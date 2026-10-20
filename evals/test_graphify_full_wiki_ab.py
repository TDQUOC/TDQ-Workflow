"""Contract tests for the three-way Graphify selector benchmark."""
import unittest

from audit_graphify_full_wiki_ab import choose_selector, run_cap, usage_or_none


class BenchmarkContractTests(unittest.TestCase):
    def test_cap_allows_only_three_real_full_runs(self):
        self.assertEqual(run_cap(["full", "full_wiki", "full"]), 3)
        with self.assertRaises(ValueError):
            run_cap(["full", "full_wiki", "full", "full"])

    def test_missing_usage_is_not_invented(self):
        self.assertIsNone(usage_or_none({}))
        self.assertEqual(usage_or_none({"usage": {"input_tokens": 4}}), {"input_tokens": 4})

    def test_artifact_lives_under_graphify_out(self):
        from tempfile import TemporaryDirectory
        from pathlib import Path
        from audit_graphify_full_wiki_ab import artifact_status
        with TemporaryDirectory() as temp:
            output = Path(temp) / "run" / "graphify-out"
            output.mkdir(parents=True)
            (output / "graph.json").write_text('{"nodes": [], "links": []}', encoding="utf-8")
            status = artifact_status(output.parent)
        self.assertEqual(status["status"], "OK")

    def test_selector_stays_current_without_complete_evidence(self):
        result = choose_selector({"code_only": {"status": "OK"},
                                  "full": {"status": "MISSING"},
                                  "full_wiki": {"status": "MISSING"}})
        self.assertEqual(result["decision"], "keep-current")
        self.assertIn("evidence", result["reason"])

    def test_artifact_only_evidence_keeps_selector_current(self):
        result = choose_selector({name: {"status": "OK"}
                                  for name in ("code_only", "full", "full_wiki")})
        self.assertEqual(result["decision"], "keep-current")

    def test_selector_does_not_replace_lsp_or_grep(self):
        result = choose_selector({name: {"status": "OK", "metrics": {"f1": .9}}
                                  for name in ("code_only", "full", "full_wiki")})
        self.assertEqual(result["exact_name"], "grep")
        self.assertEqual(result["relation_type_rename"], "LSP")
        self.assertEqual(result["concept_architecture"], "Graphify + grep, then verify")


if __name__ == "__main__":
    unittest.main()
