"""P1/P3 — PHASE_TABLE là nguồn sự thật duy nhất; doc phải khớp hằng trong code."""
import os
import unittest

from helper import ROOT, tdq_state

REQUIRED_KEYS = {"entry", "action", "cmd", "checklist", "done_when", "forbidden"}
DOC_FILES = [
    os.path.join(ROOT, "skills", "tdq-conventions", "references", "phases.md"),
    os.path.join(ROOT, "portable", "workflow", "phases.md"),
]


class PhaseTableTest(unittest.TestCase):
    def test_all_phases_covered(self):
        keys = set(tdq_state.PHASE_TABLE)
        self.assertTrue(tdq_state.VALID_PHASES <= keys,
                        f"thiếu phase: {tdq_state.VALID_PHASES - keys}")
        self.assertIn("no_state", keys)
        self.assertIn("quick", keys)
        self.assertEqual(len(keys), 9, sorted(keys))

    def test_every_row_complete(self):
        for name, row in tdq_state.PHASE_TABLE.items():
            with self.subTest(phase=name):
                self.assertEqual(REQUIRED_KEYS, set(row), name)
                self.assertTrue(row["checklist"], name)
                self.assertTrue(all(isinstance(i, str) and i.strip() for i in row["checklist"]))
                for key in ("entry", "action", "cmd", "done_when", "forbidden"):
                    self.assertTrue(str(row[key]).strip(), f"{name}.{key} rỗng")

    def test_phase_key_mapping(self):
        self.assertEqual(tdq_state.phase_key(None), "no_state")
        self.assertEqual(tdq_state.phase_key({}), "no_state")
        self.assertEqual(tdq_state.phase_key({"active_request": "r", "lane": "quick",
                                              "phase": "implement"}), "quick")
        self.assertEqual(tdq_state.phase_key({"active_request": "r", "lane": "full",
                                              "phase": "qc"}), "qc")
        self.assertEqual(tdq_state.phase_key({"active_request": "r", "lane": "full",
                                              "phase": "sai"}), "idle")

    def test_docs_match_constant(self):
        """Mỗi phase phải xuất hiện trong doc kèm đúng lệnh chuyển tiếp."""
        for doc in DOC_FILES:
            self.assertTrue(os.path.isfile(doc), f"thiếu {doc}")
            text = open(doc, encoding="utf-8").read()
            for name, row in tdq_state.PHASE_TABLE.items():
                with self.subTest(doc=os.path.basename(doc), phase=name):
                    self.assertIn(name, text, f"{doc}: thiếu phase {name}")
                    self.assertIn(row["cmd"], text, f"{doc}: lệnh của {name} không khớp code")


if __name__ == "__main__":
    unittest.main()
