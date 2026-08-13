"""Thin HTTP transport for Dashboard integration."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

import uvicorn
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from ai_engine import __version__
from ai_engine.composition import EngineRuntime, build_runtime
from ai_engine.configuration import ApiServerSettings
from ai_engine.contract_dashboard_v01 import (
    DashboardContractError,
    DashboardV01Formatter,
    DashboardV01TurnAdapter,
)
from ai_engine.contract_ml_v01 import MLContractError, MLV01Adapter
from ai_engine.http_schemas import (
    DashboardResponseV01,
    DashboardTurnV01,
    HealthResponse,
    MLRecommendationV01,
    TransportErrorDetail,
    TransportErrorResponse,
)
from ai_engine.state_machine import InvalidTransitionError


def _error_response(
    *,
    status_code: int,
    code: str,
    message: str,
    details: Sequence[dict[str, str]] | None = None,
) -> JSONResponse:
    body = TransportErrorResponse(
        error={
            "code": code,
            "message": message,
            "details": [TransportErrorDetail(**detail) for detail in details or ()],
        }
    )
    return JSONResponse(status_code=status_code, content=body.model_dump(mode="json"))


def _validation_details(exc: RequestValidationError) -> list[dict[str, str]]:
    details: list[dict[str, str]] = []
    for error in exc.errors():
        location = ".".join(str(part) for part in error.get("loc", ()) if part != "body")
        details.append(
            {
                "field": location or "body",
                "message": str(error.get("msg", "Invalid value")),
            }
        )
    return details


def create_app(
    runtime: EngineRuntime | None = None,
    server_settings: ApiServerSettings | None = None,
) -> FastAPI:
    """Build an application around an injected or environment-configured runtime."""
    resolved_runtime = runtime or build_runtime()
    settings = server_settings or ApiServerSettings.from_env()

    app = FastAPI(
        title="Sales Copilot AI Engine",
        version=__version__,
        description=(
            "Local transport for starting Sales Copilot conversations and obtaining "
            "structured Dashboard 0.1 guidance."
        ),
    )
    app.state.runtime = resolved_runtime

    if settings.cors_origins:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=list(settings.cors_origins),
            allow_credentials=False,
            allow_methods=["GET", "POST"],
            allow_headers=["Content-Type"],
        )

    @app.exception_handler(RequestValidationError)
    async def request_validation_handler(
        request: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        is_ml_request = request.url.path == "/v1/conversations"
        return _error_response(
            status_code=422,
            code="ML_CONTRACT_INVALID" if is_ml_request else "DASHBOARD_CONTRACT_INVALID",
            message=(
                "The ML 0.1 recommendation is invalid."
                if is_ml_request
                else "The Dashboard 0.1 turn is invalid."
            ),
            details=_validation_details(exc),
        )

    @app.exception_handler(Exception)
    async def unhandled_error_handler(
        _request: Request,
        _exc: Exception,
    ) -> JSONResponse:
        return _error_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            code="AI_ENGINE_UNAVAILABLE",
            message="The AI Engine could not process the request.",
        )

    @app.get(
        "/health",
        response_model=HealthResponse,
        tags=["service"],
        summary="Check service availability",
    )
    def health() -> HealthResponse:
        return HealthResponse(
            status="ok",
            service="ai-engine-sales-copilot",
            version=__version__,
            generator_mode=resolved_runtime.generator_mode.value,
            ml_contract_version="0.1",
            dashboard_contract_version="0.1",
        )

    @app.post(
        "/v1/conversations",
        response_model=DashboardResponseV01,
        response_model_exclude_none=True,
        status_code=status.HTTP_201_CREATED,
        responses={
            409: {"model": TransportErrorResponse},
            422: {"model": TransportErrorResponse},
        },
        tags=["conversations"],
        summary="Start a conversation from an ML 0.1 recommendation",
    )
    def start_conversation(request_body: MLRecommendationV01) -> dict[str, Any] | JSONResponse:
        try:
            recommendation = MLV01Adapter.parse(
                request_body.model_dump(mode="json", exclude_none=True)
            )
            result = resolved_runtime.service.start_session(recommendation)
        except MLContractError as exc:
            return _error_response(
                status_code=422,
                code="ML_CONTRACT_INVALID",
                message=str(exc),
            )
        except ValueError as exc:
            if not str(exc).startswith("Session already exists:"):
                return _error_response(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    code="AI_ENGINE_UNAVAILABLE",
                    message="The AI Engine could not start the conversation.",
                )
            return _error_response(
                status_code=status.HTTP_409_CONFLICT,
                code="CONVERSATION_ALREADY_EXISTS",
                message=str(exc),
            )
        return DashboardV01Formatter().format(result)

    @app.post(
        "/v1/turns",
        response_model=DashboardResponseV01,
        response_model_exclude_none=True,
        responses={
            404: {"model": TransportErrorResponse},
            409: {"model": TransportErrorResponse},
            422: {"model": TransportErrorResponse},
        },
        tags=["conversations"],
        summary="Process a Dashboard 0.1 customer turn",
    )
    def process_turn(request_body: DashboardTurnV01) -> dict[str, Any] | JSONResponse:
        try:
            turn = DashboardV01TurnAdapter.parse(
                request_body.model_dump(mode="json", exclude_none=True)
            )
            result = resolved_runtime.service.handle_customer_turn(turn)
        except DashboardContractError as exc:
            return _error_response(
                status_code=422,
                code="DASHBOARD_CONTRACT_INVALID",
                message=str(exc),
            )
        except KeyError:
            return _error_response(
                status_code=status.HTTP_404_NOT_FOUND,
                code="CONVERSATION_NOT_FOUND",
                message=f"Conversation '{request_body.conversation_id}' does not exist.",
            )
        except InvalidTransitionError as exc:
            return _error_response(
                status_code=status.HTTP_409_CONFLICT,
                code="INVALID_CONVERSATION_STATE",
                message=str(exc),
            )
        except ValueError as exc:
            if not str(exc).startswith("Turn already processed:"):
                return _error_response(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    code="AI_ENGINE_UNAVAILABLE",
                    message="The AI Engine could not process the turn.",
                )
            return _error_response(
                status_code=status.HTTP_409_CONFLICT,
                code="TURN_ALREADY_PROCESSED",
                message=str(exc),
            )
        return DashboardV01Formatter().format(result)

    return app


app = create_app()


def main() -> None:
    """Run the local integration server using environment configuration."""
    settings = ApiServerSettings.from_env()
    uvicorn.run(app, host=settings.host, port=settings.port)


if __name__ == "__main__":
    main()
