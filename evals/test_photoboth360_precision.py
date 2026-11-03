"""Offline contract tests for the source-reviewed Graphify benchmark."""
import unittest
from unittest.mock import patch
from types import SimpleNamespace

from audit_photoboth360_precision import (
    classify, dedup_files, parse_cli, rank_metrics, checked_output,
    aggregate, run_cli,
)


class PrecisionTests(unittest.TestCase):
    def test_confusion_sets(self):
        result = classify(["a", "b", "x"], ["a", "c"], {"a", "b", "c"})
        self.assertEqual(result["tp"], ["a"])
        self.assertEqual(result["fp"], ["b"])
        self.assertEqual(result["fn"], ["c"])
        self.assertEqual(result["unjudged"], ["x"])
        self.assertEqual(result["precision"], .5)
        self.assertEqual(result["recall"], .5)
        self.assertEqual(result["f1"], .5)

    def test_empty_denominators(self):
        result = classify([], [], set())
        self.assertIsNone(result["precision"])
        self.assertIsNone(result["recall"])
        self.assertIsNone(result["f1"])
        self.assertEqual(classify([], ["a"], {"a"})["recall"], 0)

    def test_zero_overlap(self):
        self.assertEqual(classify(["b"], ["a"], {"a", "b"})["f1"], 0)

    def test_ranking_fixed_denominator(self):
        result = rank_metrics(["b", "a", "c"], {"a", "c"})
        self.assertEqual(result["p_at_5"], 2 / 5)
        self.assertEqual(result["r_at_5"], 1)
        self.assertEqual(result["hit_at_5"], 1)
        self.assertEqual(result["rr_at_10"], .5)

    def test_ranking_miss(self):
        self.assertEqual(rank_metrics(["b"], {"a"})["rr_at_10"], 0)

    def test_dedup_preserves_scorer_tie_order(self):
        nodes = {"1": {"source_file": "a"}, "2": {"source_file": "a"},
                 "3": {"source_file": "b"}}
        self.assertEqual(dedup_files([(1, "3"), (1, "1"), (.5, "2")], nodes),
                         [{"file": "b", "score": 1, "node": "3"},
                          {"file": "a", "score": 1, "node": "1"}])

    def test_cli_node_lines_only(self):
        text = "Graph: test\nNODE f() [src=a.js loc=L1 community=0]\nEDGE x [src=bad]\n"
        self.assertEqual(parse_cli(text), ["a.js"])
        self.assertEqual(parse_cli("No matching nodes found."), [])

    def test_malformed_output(self):
        with self.assertRaises(ValueError):
            parse_cli("Graph: missing node records")

    def test_nonzero_exit_not_empty(self):
        with self.assertRaises(RuntimeError):
            checked_output(1, "No matching nodes found.", "crashed")

    def test_aggregate_micro_and_macro(self):
        records = [classify(["a", "b"], ["a"], {"a", "b"}),
                   classify([], ["c"], {"c"})]
        result = aggregate(records)
        self.assertEqual(result["tp"], 1)
        self.assertEqual(result["fp"], 1)
        self.assertEqual(result["fn"], 1)
        self.assertEqual(result["precision"], .5)
        self.assertEqual(result["macro_precision_n"], 1)
        self.assertEqual(result["macro_recall"], .5)

    def test_raw_output_survives_parse_error(self):
        response = SimpleNamespace(returncode=0, stdout="invalid raw", stderr="warning")
        with patch("audit_photoboth360_precision.subprocess.run", return_value=response):
            result = run_cli({"target": ".", "graph": "test.json"}, "test")
        self.assertEqual(result["status"], "ERROR")
        self.assertEqual(result["stdout"], "invalid raw")
        self.assertEqual(result["stderr"], "warning")
        self.assertNotIn("tp", result)

    def test_rank_dedup(self):
        self.assertEqual(rank_metrics(["a", "a"], {"a"})["p_at_5"], .2)


if __name__ == "__main__":
    unittest.main()
