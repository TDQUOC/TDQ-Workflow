"""Tests for Archify gate in approve spec/quick and set phase=idle."""
import os
import json
import tempfile
import unittest
from pathlib import Path

from helper import read_state, run_state_cli
import tdq_state
from archify_artifacts import build_manifest, bind_document

SLUG_MOI = "2026-11-09-0200-demo-moi"
SLUG_CU = "2026-11-08-1000-demo-cu"


def _make_spec_content():
    return (
        "# Spec demo\n\n"
        "## 1. Mục tiêu\n\nDemo.\n\n"
        "## 6. Định nghĩa xong\n\n"
        "| ID | Mục | Điều kiện PASS | Đo trước | Dự phòng nếu trượt |\n"
        "|---|---|---|---|---|\n"
        "| Q1 | Test | pass | yes | no |\n"
    )


def _make_report_content(missing=None):
    sections = {
        "truoc": "## Trước request\nHiện trạng A.\n\n",
        "sau": "## Sau request\nHiện trạng B.\n\n",
        "da_test": "## Đã test\nĐã test các mục.\n\n",
        "ket_qua": "## Kết quả test\nMọi thứ pass.\n\n",
    }
    out = "# Report demo\n\n"
    for k, v in sections.items():
        if missing and k in missing:
            continue
        out += v
    return out


class TestArchifyGate(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.cwd = self._tmp.name

    def tearDown(self):
        self._tmp.cleanup()

    def _setup_full(self, slug=SLUG_MOI):
        rc, _, err = run_state_cli(self.cwd, "init", slug, "full")
        self.assertEqual(rc, 0, err)
        rc, _, err = run_state_cli(self.cwd, "set", "phase=spec")
        self.assertEqual(rc, 0, err)
        rel = f"docs/tdq/spec/{slug}.md"
        spec_abs = Path(self.cwd) / rel
        spec_abs.parent.mkdir(parents=True, exist_ok=True)
        spec_abs.write_text(_make_spec_content(), encoding="utf-8")
        rc, _, err = run_state_cli(self.cwd, "set", f"spec_file={rel}")
        self.assertEqual(rc, 0, err)
        return rel

    def _render_and_bind(self, doc_rel, manifest_rel, artifact_rel):
        doc_path = Path(self.cwd) / doc_rel
        manifest_path = Path(self.cwd) / manifest_rel
        artifact_path = Path(self.cwd) / artifact_rel
        artifact_path.parent.mkdir(parents=True, exist_ok=True)
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        artifact_path.write_text("<html>artifact</html>", encoding="utf-8")
        cand_path = Path(self.cwd) / "cand.md"
        cand_path.write_text("candidate", encoding="utf-8")

        manifest = build_manifest(
            project=self.cwd,
            document=doc_path,
            candidate=cand_path,
            artifact=artifact_path,
            receipt={"ok": True},
            evidence_kind="planned",
            request="demo",
            lane="full",
            source_paths=[],
        )
        manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        bind_document(doc_path, manifest_path)

    # Q1: approve spec slug mới thiếu/stale manifest -> exit != 0, chưa duyệt
    def test_q1_approve_spec_slug_moi_thieu_manifest_bi_chan(self):
        rel = self._setup_full(SLUG_MOI)
        rc, out, err = run_state_cli(self.cwd, "approve", "spec", "--by", "user")
        self.assertNotEqual(rc, 0)
        state = read_state(self.cwd)
        self.assertFalse(state.get("spec_approved"))

    # Q2: approve spec có manifest current -> qua
    def test_q2_approve_spec_co_manifest_current_qua(self):
        rel = self._setup_full(SLUG_MOI)
        man_rel = f"docs/tdq/spec/{SLUG_MOI}-preview.manifest.json"
        art_rel = f"docs/tdq/spec/{SLUG_MOI}-preview.html"
        self._render_and_bind(rel, man_rel, art_rel)

        rc, out, err = run_state_cli(self.cwd, "approve", "spec", "--by", "user")
        self.assertEqual(rc, 0, err)
        state = read_state(self.cwd)
        self.assertTrue(state.get("spec_approved"))

    # Q3: approve quick thiếu / có flow manifest -> chặn / qua
    def test_q3_approve_quick_thieu_va_co_manifest(self):
        slug = SLUG_MOI
        rc, _, err = run_state_cli(self.cwd, "init", slug, "quick")
        self.assertEqual(rc, 0, err)
        plan_rel = f"docs/tdq/plan/{slug}.md"
        plan_abs = Path(self.cwd) / plan_rel
        plan_abs.parent.mkdir(parents=True, exist_ok=True)
        plan_abs.write_text("# Plan quick\n\nContent\n", encoding="utf-8")

        # Thieu manifest -> chan
        rc, out, err = run_state_cli(self.cwd, "approve", "quick", "--by", "user")
        self.assertNotEqual(rc, 0)
        state = read_state(self.cwd)
        self.assertFalse(state.get("quick_approved"))

        # Co manifest current -> qua
        man_rel = f"docs/tdq/plan/{slug}-flow.manifest.json"
        art_rel = f"docs/tdq/plan/{slug}-flow.html"
        self._render_and_bind(plan_rel, man_rel, art_rel)
        rc, out, err = run_state_cli(self.cwd, "approve", "quick", "--by", "user")
        self.assertEqual(rc, 0, err)
        state = read_state(self.cwd)
        self.assertTrue(state.get("quick_approved"))

    # Q4: --bo-qua-archify ghi archify_bo_qua; lý do rỗng bị từ chối
    def test_q4_bo_qua_archify(self):
        rel = self._setup_full(SLUG_MOI)
        # Ly do rong -> fail
        rc, out, err = run_state_cli(self.cwd, "approve", "spec", "--by", "user", "--bo-qua-archify", "  ")
        self.assertNotEqual(rc, 0)

        # Ly do hop le -> pass va ghi vao state
        rc, out, err = run_state_cli(self.cwd, "approve", "spec", "--by", "user", "--bo-qua-archify", "tinh huong dac biet")
        self.assertEqual(rc, 0, err)
        state = read_state(self.cwd)
        self.assertTrue(state.get("spec_approved"))
        bq = state.get("archify_bo_qua")
        self.assertIsNotNone(bq)
        self.assertEqual(bq.get("ly_do"), "tinh huong dac biet")
        self.assertEqual(bq.get("cong"), "spec")

    # Q5: idle: report thiếu mục / thiếu manifest / đủ -> chặn / chặn / qua
    def test_q5_idle_report_gate(self):
        rel = self._setup_full(SLUG_MOI)
        man_rel = f"docs/tdq/spec/{SLUG_MOI}-preview.manifest.json"
        art_rel = f"docs/tdq/spec/{SLUG_MOI}-preview.html"
        self._render_and_bind(rel, man_rel, art_rel)
        # approve spec
        run_state_cli(self.cwd, "approve", "spec", "--by", "user")

        # 1. Chưa có file report -> chan khi set phase=idle
        rc, out, err = run_state_cli(self.cwd, "set", "phase=idle")
        self.assertNotEqual(rc, 0)

        # 2. File report thiếu mục -> chan
        rep_rel = f"docs/tdq/reports/{SLUG_MOI}.md"
        rep_path = Path(self.cwd) / rep_rel
        rep_path.parent.mkdir(parents=True, exist_ok=True)
        rep_path.write_text(_make_report_content(missing=["ket_qua"]), encoding="utf-8")
        rc, out, err = run_state_cli(self.cwd, "set", "phase=idle")
        self.assertNotEqual(rc, 0)

        # 3. File report đủ 4 mục nhưng thiếu manifest -> chan
        rep_path.write_text(_make_report_content(), encoding="utf-8")
        rc, out, err = run_state_cli(self.cwd, "set", "phase=idle")
        self.assertNotEqual(rc, 0)

        # 4. Có manifest current -> qua
        rep_man_rel = f"docs/tdq/reports/{SLUG_MOI}.manifest.json"
        rep_art_rel = f"docs/tdq/reports/{SLUG_MOI}.html"
        self._render_and_bind(rep_rel, rep_man_rel, rep_art_rel)
        rc, out, err = run_state_cli(self.cwd, "set", "phase=idle")
        self.assertEqual(rc, 0, err)
        state = read_state(self.cwd)
        self.assertEqual(state.get("phase"), "idle")

    # Q5b: idle với archify_bo_qua bỏ qua kiểm tra manifest report nhưng vẫn đòi 4 mục
    def test_q5b_idle_with_archify_bo_qua(self):
        rel = self._setup_full(SLUG_MOI)
        run_state_cli(self.cwd, "approve", "spec", "--by", "user", "--bo-qua-archify", "bo qua")

        rep_rel = f"docs/tdq/reports/{SLUG_MOI}.md"
        rep_path = Path(self.cwd) / rep_rel
        rep_path.parent.mkdir(parents=True, exist_ok=True)
        # Thieu muc -> van chan
        rep_path.write_text(_make_report_content(missing=["sau"]), encoding="utf-8")
        rc, out, err = run_state_cli(self.cwd, "set", "phase=idle")
        self.assertNotEqual(rc, 0)

        # Du 4 muc, khong co manifest -> van qua nho archify_bo_qua
        rep_path.write_text(_make_report_content(), encoding="utf-8")
        rc, out, err = run_state_cli(self.cwd, "set", "phase=idle")
        self.assertEqual(rc, 0, err)
        state = read_state(self.cwd)
        self.assertEqual(state.get("phase"), "idle")

    # Q6: slug trước mốc không bị gate
    def test_q6_slug_truoc_moc_khong_gate(self):
        rel = self._setup_full(SLUG_CU)
        rc, out, err = run_state_cli(self.cwd, "approve", "spec", "--by", "user")
        self.assertEqual(rc, 0, err)
        state = read_state(self.cwd)
        self.assertTrue(state.get("spec_approved"))


if __name__ == "__main__":
    unittest.main()
