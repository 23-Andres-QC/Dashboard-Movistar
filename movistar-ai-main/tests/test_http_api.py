from __future__ import annotations

import json
import os
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient

from ai_engine.api import create_app
from ai_engine.composition import build_runtime
from ai_engine.configuration import ApiServerSettings, GeneratorMode, RuntimeSettings


PROJECT_ROOT = Path(__file__).resolve().parents[1]
ML_FIXTURE_PATH = PROJECT_ROOT / "fixtures" / "ml_recommendation_v01.json"
TURN_FIXTURE_PATH = PROJECT_ROOT / "fixtures" / "dashboard_turn_v01.json"


def load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_client() -> TestClient:
    runtime = build_runtime(
        RuntimeSettings(generator_mode=GeneratorMode.DETERMINISTIC),
        root=PROJECT_ROOT,
    )
    app = create_app(
        runtime=runtime,
        server_settings=ApiServerSettings(cors_origins=("*",)),
    )
    return TestClient(app)


class HttpApiTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = build_client()

    def tearDown(self) -> None:
        self.client.close()

    def start_conversation(self) -> dict[str, object]:
        response = self.client.post("/v1/conversations", json=load_json(ML_FIXTURE_PATH))
        self.assertEqual(response.status_code, 201, response.text)
        return response.json()

    def test_health_check_reports_deterministic_mode_without_api_key(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            runtime = build_runtime(root=PROJECT_ROOT)
            client = TestClient(
                create_app(
                    runtime=runtime,
                    server_settings=ApiServerSettings(cors_origins=("*",)),
                )
            )
            try:
                response = client.get("/health")
            finally:
                client.close()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")
        self.assertEqual(response.json()["generator_mode"], "deterministic")
        self.assertEqual(response.json()["ml_contract_version"], "0.1")

    def test_start_conversation_returns_structured_opening(self) -> None:
        body = self.start_conversation()

        self.assertEqual(body["contract_version"], "0.1")
        self.assertEqual(body["conversation_id"], "conv-rec-demo-001")
        self.assertEqual(body["conversation_stage"], "opening")
        self.assertEqual(body["trace"]["recommendation_id"], "rec-demo-001")
        self.assertEqual(body["grounding"]["offer_id"], "OF004")
        self.assertTrue(body["advisor_guidance"]["suggested_customer_response"])
        self.assertTrue(body["safety"]["grounded"])
        self.assertNotIn("objection", body)
        self.assertNotIn("error", body)

    def test_customer_turn_returns_grounded_price_guidance(self) -> None:
        self.start_conversation()

        response = self.client.post("/v1/turns", json=load_json(TURN_FIXTURE_PATH))

        self.assertEqual(response.status_code, 200, response.text)
        body = response.json()
        self.assertEqual(body["objection"]["category"], "precio")
        self.assertEqual(
            body["advisor_guidance"]["recommended_action"], "REFRAME_VALUE"
        )
        self.assertEqual(body["trace"]["recommendation_id"], "rec-demo-001")
        self.assertEqual(body["grounding"]["offer_id"], "OF004")
        self.assertTrue(body["safety"]["grounded"])
        self.assertNotIn("error", body)

    def test_invalid_ml_contract_returns_structured_error(self) -> None:
        payload = load_json(ML_FIXTURE_PATH)
        payload.pop("recommendation_id")

        response = self.client.post("/v1/conversations", json=payload)

        self.assertEqual(response.status_code, 422)
        body = response.json()
        self.assertEqual(body["error"]["code"], "ML_CONTRACT_INVALID")
        self.assertTrue(
            any(
                item["field"] == "recommendation_id"
                for item in body["error"]["details"]
            )
        )

    def test_unknown_conversation_returns_structured_error(self) -> None:
        payload = load_json(TURN_FIXTURE_PATH)
        payload["conversation_id"] = "conv-missing"

        response = self.client.post("/v1/turns", json=payload)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["error"]["code"], "CONVERSATION_NOT_FOUND")

    def test_invalid_dashboard_turn_returns_structured_error(self) -> None:
        payload = load_json(TURN_FIXTURE_PATH)
        payload.pop("text")

        response = self.client.post("/v1/turns", json=payload)

        self.assertEqual(response.status_code, 422)
        self.assertEqual(
            response.json()["error"]["code"], "DASHBOARD_CONTRACT_INVALID"
        )

    def test_openapi_exposes_only_handoff_operations(self) -> None:
        response = self.client.get("/openapi.json")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            set(response.json()["paths"]),
            {"/health", "/v1/conversations", "/v1/turns"},
        )


if __name__ == "__main__":
    unittest.main()
