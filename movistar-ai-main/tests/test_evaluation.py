"""Tests for the generator-comparison evaluation harness."""

from __future__ import annotations

import unittest
from pathlib import Path

from ai_engine.demo import build_demo_service
from ai_engine.evaluation import load_evaluation_cases, run_evaluation
from ai_engine.mocks import MockRecommendationSource


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class EvaluationHarnessTests(unittest.TestCase):
    def test_deterministic_baseline_satisfies_synthetic_invariants(self) -> None:
        cases = load_evaluation_cases(
            PROJECT_ROOT / "fixtures" / "evaluation_cases_v01.json"
        )
        payload = dict(
            MockRecommendationSource(
                PROJECT_ROOT / "fixtures" / "ml_recommendation_v01.json"
            ).load()
        )

        results = run_evaluation(
            cases=cases,
            service_factory=lambda: build_demo_service(PROJECT_ROOT),
            recommendation_payload=payload,
        )

        self.assertEqual(len(results), 5)
        for evaluation in results:
            self.assertTrue(evaluation.structural_compliance, evaluation.case_id)
            self.assertTrue(evaluation.grounding_compliance, evaluation.case_id)
            self.assertTrue(evaluation.identifiers_preserved, evaluation.case_id)
            self.assertTrue(evaluation.unauthorized_claims_absent, evaluation.case_id)
            self.assertTrue(evaluation.strategy_respected, evaluation.case_id)
            self.assertTrue(evaluation.response_type_respected, evaluation.case_id)
            self.assertTrue(evaluation.context_consistent, evaluation.case_id)
            self.assertTrue(evaluation.error_handling_compliance, evaluation.case_id)
            self.assertTrue(
                evaluation.degradation_behavior_respected, evaluation.case_id
            )
            if evaluation.case_id == "missing-knowledge-abstention":
                self.assertTrue(evaluation.degraded_or_abstained)
                self.assertEqual(evaluation.generator, "controlled_response")
            else:
                self.assertGreaterEqual(evaluation.naturalness_proxy, 0.8)
                self.assertFalse(evaluation.degraded_or_abstained)
                self.assertEqual(evaluation.generator, "deterministic")
            self.assertIsNone(evaluation.total_tokens)
            self.assertGreaterEqual(evaluation.end_to_end_latency_ms, 0)


if __name__ == "__main__":
    unittest.main()
