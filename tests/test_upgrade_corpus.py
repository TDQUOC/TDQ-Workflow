"""Validate the locked offline upgrade oracle, not candidate-derived labels."""
import hashlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "evals" / "tdq-upgrade-offline.json"


class UpgradeCorpusTest(unittest.TestCase):
    def setUp(self):
        self.assertTrue(CORPUS.is_file(), "Missing locked offline upgrade corpus")
        self.corpus = json.loads(CORPUS.read_text(encoding="utf-8"))

    def test_version_and_provenance_are_explicit(self):
        self.assertEqual(self.corpus["schema_version"], 1)
        self.assertEqual(self.corpus["oracle"], "manual-before-candidate")
        self.assertFalse(self.corpus["live_execution"])
        self.assertEqual(len(self.corpus["base_commit"]), 40)

    def test_cases_have_unique_ids_split_and_oracle(self):
        seen = set()
        groups = {}
        for case in self.corpus["cases"]:
            with self.subTest(case=case.get("id")):
                self.assertNotIn(case["id"], seen)
                seen.add(case["id"])
                self.assertIn(case["split"], ("dev", "holdout"))
                self.assertTrue(case["input"])
                self.assertTrue(case["expected"])
                self.assertTrue(case["reason"])
                self.assertTrue(case["applicability"])
                groups.setdefault(case["group"], set()).add(case["split"])
        for group in ("parser", "identity", "eval", "retrieval", "hooks"):
            self.assertEqual(groups[group], {"dev", "holdout"}, group)

    def test_measurement_protocol_does_not_turn_driver_into_host(self):
        protocol = self.corpus["dispatcher_protocol"]
        self.assertEqual(protocol["primary_metric"], "host_critical_path_ms")
        self.assertEqual(protocol["order"], ["AB", "BA"])
        self.assertGreaterEqual(protocol["baseline_repeats"], 2)
        self.assertGreater(protocol["batches"], 1)
        self.assertGreater(protocol["samples_per_batch"], 1)
        self.assertEqual(protocol["aggregation"], ["p50", "p95"])
        self.assertEqual(protocol["missing_host_trace"], "NO-GO")
        self.assertEqual(protocol["decision_effect_differences_allowed"], 0)
        self.assertTrue(protocol["guardrails"])

    def test_parser_limits_and_retrieval_guardrails_are_locked(self):
        budget = self.corpus["parser_budget"]
        commands = [case["input"]["command"] for case in self.corpus["cases"]
                    if case["group"] == "parser"]
        ordinary_max = max(len(command) for command in commands)
        self.assertGreaterEqual(budget["input_chars"], ordinary_max)
        self.assertLessEqual(budget["nesting"], 8)
        self.assertTrue(budget["cumulative"])
        self.assertEqual(budget["on_exhaustion"], "unknown")
        self.assertEqual(self.corpus["retrieval_protocol"]["label_changes"],
                         "new-version-not-original-holdout")
        self.assertEqual(self.corpus["retrieval_protocol"]["unit"], "bytes-not-tokens")

    def test_corpus_hash_covers_exact_bytes(self):
        digest = hashlib.sha256(CORPUS.read_bytes()).hexdigest()
        self.assertEqual(len(digest), 64)
        changed = hashlib.sha256(CORPUS.read_bytes() + b"\n").hexdigest()
        self.assertNotEqual(digest, changed)


if __name__ == "__main__":
    unittest.main()
