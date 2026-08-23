"""P1/P3 — PHASE_TABLE là nguồn sự thật duy nhất; doc phải khớp hằng trong code."""
import os
import re
import unittest

from helper import ROOT, tdq_state

REQUIRED_KEYS = {"entry", "action", "cmd", "checklist", "done_when", "forbidden"}
DOC_FILES = [
    os.path.join(ROOT, "skills", "tdq-conventions", "references", "phases.md"),
]


class PhaseTableTest(unittest.TestCase):
    def test_all_phases_covered(self):
        keys = set(tdq_state.PHASE_TABLE)
        self.assertTrue(tdq_state.VALID_PHASES <= keys,
                        f"thiếu phase: {tdq_state.VALID_PHASES - keys}")
        self.assertIn("no_state", keys)
        self.assertIn("quick", keys)
        self.assertEqual(len(keys), 11, sorted(keys))

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

    def test_phase_key_quick_terminal(self):
        """A6: lane quick phải có terminal — quick_approved + phase=idle là đã xong."""
        base = {"active_request": "r", "lane": "quick"}
        self.assertEqual(tdq_state.phase_key({**base, "phase": "idle"}), "quick")
        self.assertEqual(tdq_state.phase_key({**base, "phase": "implement",
                                              "quick_approved": True}), "quick")
        self.assertEqual(tdq_state.phase_key({**base, "phase": "idle",
                                              "quick_approved": True}), "idle")

    def test_render_no_regex_escape_artifact(self):
        """Bug A1: escape sai trong re.sub → literal `\\1` thay vì lệnh thật."""
        doc = tdq_state.render_phases_md()
        self.assertNotIn("`\\1`", doc, "phases-doc chứa literal `\\1` — lệnh bị nuốt")
        for line in doc.splitlines():
            if re.match(r"^\d+\. ", line):
                self.assertNotIn("``", line, f"wrap đôi hỏng inline-code: {line}")
        # Từ 2026-08-09 phases-doc không sinh mục chi tiết từng phase nữa; lệnh thật
        # nằm ở khối "Lệnh nguyên văn" và ở cột lệnh của bảng.
        self.assertNotIn("\n## analyze", doc, "phases-doc còn sinh mục chi tiết phase")
        block = doc.split("The commands verbatim", 1)[1]
        for section in ("analyze", "spec", "plan"):
            self.assertIn(f"{section}: python3 scripts/", block,
                          f"khối lệnh nguyên văn mất lệnh của {section}")
        for section in ("spec", "plan"):
            self.assertIn(f"{section}: python3 scripts/tdq_state.py", block,
                          f"khối lệnh nguyên văn mất lệnh tdq_state.py của {section}")

    def test_quick_row_no_qc_variant_and_terminal(self):
        """A26: dòng duyệt quick khớp intake (biến thể bỏ QC); A6: có bước đóng."""
        row = tdq_state.PHASE_TABLE["quick"]
        self.assertIn("--no-qc", row["cmd"])
        joined = " ".join(row["checklist"])
        self.assertIn("--no-qc ONLY when the user says so", joined)
        self.assertIn("set phase=idle", joined)

    def test_render_plugin_root_variant(self):
        """A40: bản chạy trong ngữ cảnh plugin phải in path plugin-root."""
        doc = tdq_state.render_phases_md(plugin_root=True)
        self.assertIn('python3 "${CLAUDE_PLUGIN_ROOT}/scripts/tdq_state.py"', doc)
        self.assertNotIn("python3 scripts/", doc)

    def test_docs_match_constant(self):
        """Mỗi phase phải xuất hiện trong doc kèm đúng lệnh chuyển tiếp.

        A40: bản conventions chạy trong ngữ cảnh plugin → lệnh dạng plugin-root.
        """
        for doc in DOC_FILES:
            self.assertTrue(os.path.isfile(doc), f"thiếu {doc}")
            with open(doc, encoding="utf-8") as fh:
                text = fh.read()
            for name, row in tdq_state.PHASE_TABLE.items():
                with self.subTest(doc=os.path.basename(doc), phase=name):
                    self.assertIn(name, text, f"{doc}: thiếu phase {name}")
                    cmd = tdq_state.plugin_root_cmd(row["cmd"])
                    self.assertIn(cmd, text, f"{doc}: lệnh của {name} không khớp code")


if __name__ == "__main__":
    unittest.main()
