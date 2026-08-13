"""Paid/network integration test, disabled unless explicitly opted in."""

from __future__ import annotations

import os
import unittest
from pathlib import Path

from ai_engine.configuration import OpenAISettings
from ai_engine.contract_ml_v01 import MLV01Adapter
from ai_engine.demo import build_demo_service
from ai_engine.deterministic import DeterministicContentGenerator
from ai_engine.llm import LlmContentGenerator
from ai_engine.mocks import MockRecommendationSource
from ai_engine.openai_responses import OpenAIResponsesProvider


PROJECT_ROOT = Path(__file__).resolve().parents[1]
OPTED_IN = os.environ.get("AI_ENGINE_RUN_OPENAI_INTEGRATION") == "1"


@unittest.skipUnless(
    OPTED_IN,
    "Set AI_ENGINE_RUN_OPENAI_INTEGRATION=1 to authorize a paid network call",
)
class OpenAIIntegrationTests(unittest.TestCase):
    def test_real_opening_is_structured_or_safely_falls_back(self) -> None:
        settings = OpenAISettings.from_env()
        generator = LlmContentGenerator(
            OpenAIResponsesProvider(
                model=settings.model,
                api_key=settings.api_key,
                timeout_seconds=settings.timeout_seconds,
            )
        )
        service = build_demo_service(
            PROJECT_ROOT,
            content_generator=generator,
            fallback_content_generator=DeterministicContentGenerator(),
        )
        recommendation = MLV01Adapter.parse(
            MockRecommendationSource(
                PROJECT_ROOT / "fixtures" / "ml_recommendation_v01.json"
            ).load()
        )

        response = service.start_session(recommendation)

        self.assertEqual(response.recommendation_id, "rec-demo-001")
        self.assertEqual(response.offer_id, "OF004")
        self.assertTrue(response.grounded)
        self.assertIsNotNone(response.guidance.generation)


if __name__ == "__main__":
    unittest.main()
