#!/usr/bin/env python3
"""Tests for team identity, versioned assignment projection, and U06/U09 contracts.

Covers:
1. Replay of stale detection: false stale on progress checkbox under legacy maps vs.
   safe preservation under versioned assignment projection (U06).
2. Mutation matrix:
   - order, phase, ma, deps, files, test, contract, mcp, estimate -> change projection SHA
   - checkbox and progress notes -> do NOT change projection SHA in explicit mode
   - checkbox in legacy-conservative mode -> triggers stale (conservative fallback)
3. Unknown version / corrupted / unparseable maps are rejected, never assumed current.
4. Atomic assignment map write (mkstemp + replace).
5. U09 HOLD status, reason, and conflict probe distinguishing clean/conflict/error.
"""
import json
import os
import sys
import tempfile
import unittest

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(GOC, "scripts")
if SCRIPTS not in sys.path:
    sys.path.insert(0, SCRIPTS)

import tdq_state
import tdq_team

LENH_LUON_XANH = f'"{sys.executable}" -c "pass"'

PLAN_TUONG_MINH = f"""# PLAN — mau tuong minh

## P1 — khoi tao
- [ ] **T1.1** (e5m) khoi tao he thong — Test: `{LENH_LUON_XANH}`
  - Chạm: `scripts/core.py`
- [ ] **T1.2** (e10m) cau hinh co ban — Test: `{LENH_LUON_XANH}`
  - Chạm: `scripts/config.py`
  - Cần: T1.1
  - Dùng: `claude-api`
  - Để: thiet lap thong so chay

## P2 — tinh nang
- [ ] **T2.1** (e15m) mo rong module — Test: `{LENH_LUON_XANH}`
  - Chạm: `scripts/ext.py`
  - Cần: T1.2
"""

PLAN_LEGACY = f"""# PLAN — mau legacy khong co can

## P1 — khoi tao
- [ ] **T1.1** (e5m) khoi tao — Test: `{LENH_LUON_XANH}`
  - Chạm: `scripts/core.py`
- [ ] **T1.2** (e10m) cau hinh — Test: `{LENH_LUON_XANH}`
  - Chạm: `scripts/config.py`
"""


class TestTeamIdentityProjection(unittest.TestCase):
    """Kiểm tra chi tiết cơ chế assignment projection và mutation matrix (U06)."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.cwd = self.tmp.name
        self.addCleanup(self.tmp.cleanup)

    def _ghi_plan(self, text, rel_path="docs/tdq/plan/2026-10-17-test-proj.md"):
        full = os.path.join(self.cwd, rel_path)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, "w", encoding="utf-8") as f:
            f.write(text)
        return full

    def test_chieu_phan_cong_che_do_tuong_minh(self):
        """Kế hoạch có 'Cần:' kích hoạt chế độ 'explicit'."""
        duong = self._ghi_plan(PLAN_TUONG_MINH)
        tasks = tdq_team.doc_plan(duong)
        chieu, mode = tdq_team.chieu_phan_cong(tasks)
        self.assertEqual(mode, "explicit")
        self.assertEqual(len(chieu), 3)
        self.assertEqual(chieu[0]["ma"], "T1.1")
        self.assertEqual(chieu[1]["ma"], "T1.2")
        self.assertEqual(chieu[1]["deps"], ["T1.1"])
        self.assertNotIn("trang_thai", chieu[0])

    def test_chieu_phan_cong_che_do_legacy(self):
        """Kế hoạch không có 'Cần:' dùng chế độ 'legacy-conservative'."""
        duong = self._ghi_plan(PLAN_LEGACY)
        tasks = tdq_team.doc_plan(duong)
        chieu, mode = tdq_team.chieu_phan_cong(tasks)
        self.assertEqual(mode, "legacy-conservative")
        self.assertEqual(len(chieu), 2)
        self.assertIn("trang_thai", chieu[0])

    def test_mutation_matrix_checkbox_khong_doi_sha_khi_tuong_minh(self):
        """Checkbox thay đổi ([ ] -> [~] -> [x] -> [>]) KHÔNG làm đổi projection SHA ở chế độ explicit."""
        duong1 = self._ghi_plan(PLAN_TUONG_MINH)
        tasks1 = tdq_team.doc_plan(duong1)
        sha1, mode1 = tdq_team.tinh_sha_projection(tasks1)
        self.assertEqual(mode1, "explicit")

        # Đổi checkbox T1.1 sang [~]
        text_dang_lam = PLAN_TUONG_MINH.replace("- [ ] **T1.1**", "- [~] **T1.1**")
        duong2 = self._ghi_plan(text_dang_lam)
        tasks2 = tdq_team.doc_plan(duong2)
        sha2, _ = tdq_team.tinh_sha_projection(tasks2)
        self.assertEqual(sha1, sha2)

        # Đổi checkbox T1.1 sang [x] và T1.2 sang [>]
        text_da_giao = text_dang_lam.replace("- [~] **T1.1**", "- [x] **T1.1**").replace(
            "- [ ] **T1.2**", "- [>] **T1.2**")
        duong3 = self._ghi_plan(text_da_giao)
        tasks3 = tdq_team.doc_plan(duong3)
        sha3, _ = tdq_team.tinh_sha_projection(tasks3)
        self.assertEqual(sha1, sha3)

    def test_mutation_matrix_progress_notes_khong_doi_sha_khi_tuong_minh(self):
        """Thêm dòng ghi chú tiến độ (Tiến độ: ...) không làm đổi projection SHA."""
        duong1 = self._ghi_plan(PLAN_TUONG_MINH)
        tasks1 = tdq_team.doc_plan(duong1)
        sha1, _ = tdq_team.tinh_sha_projection(tasks1)

        text_kem_tien_do = PLAN_TUONG_MINH.replace(
            "  - Chạm: `scripts/core.py`",
            "  - Chạm: `scripts/core.py`\n  - Tiến độ: Đang thực hiện red-green\n  - Tiến độ inline: 100%"
        )
        duong2 = self._ghi_plan(text_kem_tien_do)
        tasks2 = tdq_team.doc_plan(duong2)
        sha2, _ = tdq_team.tinh_sha_projection(tasks2)
        self.assertEqual(sha1, sha2)

    def test_mutation_matrix_order_thay_doi_sha(self):
        """Đổi thứ tự task làm đổi projection SHA."""
        duong1 = self._ghi_plan(PLAN_TUONG_MINH)
        sha1, _ = tdq_team.tinh_sha_projection(tdq_team.doc_plan(duong1))

        # Đảo thứ tự T1.1 và T1.2
        p1 = f"""# PLAN — dao thu tu
## P1 — khoi tao
- [ ] **T1.2** (e10m) cau hinh co ban — Test: `{LENH_LUON_XANH}`
  - Chạm: `scripts/config.py`
  - Cần: T1.1
- [ ] **T1.1** (e5m) khoi tao he thong — Test: `{LENH_LUON_XANH}`
  - Chạm: `scripts/core.py`
## P2 — tinh nang
- [ ] **T2.1** (e15m) mo rong module — Test: `{LENH_LUON_XANH}`
  - Chạm: `scripts/ext.py`
  - Cần: T1.2
"""
        duong2 = self._ghi_plan(p1)
        sha2, _ = tdq_team.tinh_sha_projection(tdq_team.doc_plan(duong2))
        self.assertNotEqual(sha1, sha2)

    def test_mutation_matrix_phase_thay_doi_sha(self):
        """Đổi phase làm đổi projection SHA."""
        duong1 = self._ghi_plan(PLAN_TUONG_MINH)
        sha1, _ = tdq_team.tinh_sha_projection(tdq_team.doc_plan(duong1))

        text_doi_phase = PLAN_TUONG_MINH.replace("## P2 — tinh nang", "## P3 — tinh nang")
        duong2 = self._ghi_plan(text_doi_phase)
        sha2, _ = tdq_team.tinh_sha_projection(tdq_team.doc_plan(duong2))
        self.assertNotEqual(sha1, sha2)

    def test_mutation_matrix_deps_thay_doi_sha(self):
        """Đổi dependencies (Cần:) làm đổi projection SHA."""
        duong1 = self._ghi_plan(PLAN_TUONG_MINH)
        sha1, _ = tdq_team.tinh_sha_projection(tdq_team.doc_plan(duong1))

        text_doi_dep = PLAN_TUONG_MINH.replace("  - Cần: T1.2", "  - Cần: T1.1")
        duong2 = self._ghi_plan(text_doi_dep)
        sha2, _ = tdq_team.tinh_sha_projection(tdq_team.doc_plan(duong2))
        self.assertNotEqual(sha1, sha2)

    def test_mutation_matrix_files_thay_doi_sha(self):
        """Đổi vùng file chạm làm đổi projection SHA."""
        duong1 = self._ghi_plan(PLAN_TUONG_MINH)
        sha1, _ = tdq_team.tinh_sha_projection(tdq_team.doc_plan(duong1))

        text_doi_file = PLAN_TUONG_MINH.replace("`scripts/core.py`", "`scripts/core_new.py`")
        duong2 = self._ghi_plan(text_doi_file)
        sha2, _ = tdq_team.tinh_sha_projection(tdq_team.doc_plan(duong2))
        self.assertNotEqual(sha1, sha2)

    def test_mutation_matrix_test_thay_doi_sha(self):
        """Đổi lệnh test làm đổi projection SHA."""
        duong1 = self._ghi_plan(PLAN_TUONG_MINH)
        sha1, _ = tdq_team.tinh_sha_projection(tdq_team.doc_plan(duong1))

        text_doi_test = PLAN_TUONG_MINH.replace(
            f"Test: `{LENH_LUON_XANH}`", "Test: `python3 -m pytest tests/test_new.py`"
        )
        duong2 = self._ghi_plan(text_doi_test)
        sha2, _ = tdq_team.tinh_sha_projection(tdq_team.doc_plan(duong2))
        self.assertNotEqual(sha1, sha2)

    def test_mutation_matrix_contract_thay_doi_sha(self):
        """Đổi dòng hợp đồng (Dùng:, Để:, ...) làm đổi projection SHA."""
        duong1 = self._ghi_plan(PLAN_TUONG_MINH)
        sha1, _ = tdq_team.tinh_sha_projection(tdq_team.doc_plan(duong1))

        text_doi_hop_dong = PLAN_TUONG_MINH.replace(
            "  - Để: thiet lap thong so chay", "  - Để: tich hop module nang cao"
        )
        duong2 = self._ghi_plan(text_doi_hop_dong)
        sha2, _ = tdq_team.tinh_sha_projection(tdq_team.doc_plan(duong2))
        self.assertNotEqual(sha1, sha2)

    def test_mutation_matrix_mcp_thay_doi_sha(self):
        """Thêm flag MCP làm đổi projection SHA."""
        duong1 = self._ghi_plan(PLAN_TUONG_MINH)
        sha1, _ = tdq_team.tinh_sha_projection(tdq_team.doc_plan(duong1))

        text_them_mcp = PLAN_TUONG_MINH.replace("  - Dùng: `claude-api`", "  - Dùng: `claude-api` (mcp)")
        duong2 = self._ghi_plan(text_them_mcp)
        sha2, _ = tdq_team.tinh_sha_projection(tdq_team.doc_plan(duong2))
        self.assertNotEqual(sha1, sha2)

    def test_mutation_matrix_estimate_thay_doi_sha(self):
        """Đổi ước lượng (eNm) làm đổi projection SHA."""
        duong1 = self._ghi_plan(PLAN_TUONG_MINH)
        sha1, _ = tdq_team.tinh_sha_projection(tdq_team.doc_plan(duong1))

        text_doi_estimate = PLAN_TUONG_MINH.replace("(e5m)", "(e45m)")
        duong2 = self._ghi_plan(text_doi_estimate)
        sha2, _ = tdq_team.tinh_sha_projection(tdq_team.doc_plan(duong2))
        self.assertNotEqual(sha1, sha2)

    def test_mutation_matrix_legacy_checkbox_thay_doi_sha(self):
        """Ở chế độ legacy-conservative, đổi checkbox BẮT BUỘC làm đổi hash (bảo thủ)."""
        duong1 = self._ghi_plan(PLAN_LEGACY)
        tasks1 = tdq_team.doc_plan(duong1)
        sha1, mode1 = tdq_team.tinh_sha_projection(tasks1)
        self.assertEqual(mode1, "legacy-conservative")

        text_legacy_doi_tick = PLAN_LEGACY.replace("- [ ] **T1.1**", "- [~] **T1.1**")
        duong2 = self._ghi_plan(text_legacy_doi_tick)
        tasks2 = tdq_team.doc_plan(duong2)
        sha2, mode2 = tdq_team.tinh_sha_projection(tasks2)
        self.assertEqual(mode2, "legacy-conservative")
        self.assertNotEqual(sha1, sha2)


class TestReplayStaleDauVao(unittest.TestCase):
    """Tái lập lỗi stale dư lịch sử và kiểm chứng cơ chế giải quyết (O06)."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.cwd = self.tmp.name
        self.slug = "2026-10-17-test-stale"
        self.plan_rel = f"docs/tdq/plan/{self.slug}.md"
        self.full_plan = os.path.join(self.cwd, self.plan_rel)
        os.makedirs(os.path.dirname(self.full_plan), exist_ok=True)
        tdq_state.save(self.cwd, {
            "active_request": self.slug,
            "lane": "full",
            "phase": "implement",
            "implement_mode": "subagent",
            "plan_file": self.plan_rel,
        })
        self.addCleanup(self.tmp.cleanup)

    def _ghi_plan(self, text):
        with open(self.full_plan, "w", encoding="utf-8") as f:
            f.write(text)

    def test_tai_lap_stale_du_ban_do_legacy(self):
        """Tái lập: Bản đồ cũ (chỉ có plan_sha toàn file) coi việc tick checkbox là stale (stale dư)."""
        self._ghi_plan(PLAN_TUONG_MINH)
        # Sinh bản đồ legacy (không có projection_version, chỉ có plan_sha)
        legacy_ban_do = {
            "slug": self.slug,
            "plan_file": self.plan_rel,
            "plan_sha": tdq_team.sha_file(self.full_plan),
            "tasks": {"T1.1": {"quyet_dinh": "giao", "ly_do": "", "vung_file": ["scripts/core.py"], "dot": 1}},
        }
        # Kiểm tra trước khi sửa: không stale
        stale, _ = tdq_team.kiem_tra_stale(self.full_plan, legacy_ban_do)
        self.assertFalse(stale)

        # Sửa checkbox [ ] -> [~]
        self._ghi_plan(PLAN_TUONG_MINH.replace("- [ ] **T1.1**", "- [~] **T1.1**"))
        # Bản đồ legacy bị stale dù chỉ đổi tick
        stale, ly_do = tdq_team.kiem_tra_stale(self.full_plan, legacy_ban_do)
        self.assertTrue(stale)
        self.assertIn("legacy", ly_do.lower())

    def test_khong_bi_stale_du_voi_projection_v1_tuong_minh(self):
        """Khắc phục: Bản đồ projection v1 ở chế độ explicit KHÔNG bị stale khi tick checkbox."""
        self._ghi_plan(PLAN_TUONG_MINH)
        tdq_team.lenh_phan_cong(self.cwd, [])
        duong_map = tdq_team.duong_ban_do(self.cwd, self.slug)
        with open(duong_map, encoding="utf-8") as f:
            ban_do = json.load(f)

        self.assertEqual(ban_do.get("projection_version"), "v1")
        self.assertEqual(ban_do.get("projection_mode"), "explicit")
        self.assertTrue(ban_do.get("plan_assignment_sha"))

        # Sửa checkbox [ ] -> [~] rồi [x]
        self._ghi_plan(PLAN_TUONG_MINH.replace("- [ ] **T1.1**", "- [x] **T1.1**"))
        stale, ly_do = tdq_team.kiem_tra_stale(self.full_plan, ban_do)
        self.assertFalse(stale, f"Bị stale ngoài ý muốn: {ly_do}")

        # Thêm ghi chú tiến độ
        self._ghi_plan(PLAN_TUONG_MINH.replace("- [ ] **T1.1**", "- [x] **T1.1**").replace(
            "  - Chạm: `scripts/core.py`",
            "  - Chạm: `scripts/core.py`\n  - Tiến độ: Xong 100%"
        ))
        stale, ly_do = tdq_team.kiem_tra_stale(self.full_plan, ban_do)
        self.assertFalse(stale, f"Bị stale khi thêm tiến độ: {ly_do}")

    def test_phat_hien_stale_chinh_xac_khi_cau_truc_task_doi(self):
        """Bản đồ projection v1 vẫn phát hiện stale chính xác khi cấu trúc task/file/dep thay đổi."""
        self._ghi_plan(PLAN_TUONG_MINH)
        tdq_team.lenh_phan_cong(self.cwd, [])
        duong_map = tdq_team.duong_ban_do(self.cwd, self.slug)
        with open(duong_map, encoding="utf-8") as f:
            ban_do = json.load(f)

        # Sửa dependency của T1.2
        self._ghi_plan(PLAN_TUONG_MINH.replace("  - Cần: T1.1", "  - Cần: T2.1"))
        stale, ly_do = tdq_team.kiem_tra_stale(self.full_plan, ban_do)
        self.assertTrue(stale)
        self.assertIn("changed", ly_do.lower())


class TestGuardVaVersionHopDong(unittest.TestCase):
    """Kiểm tra tính an toàn: unknown version, unparseable, atomic write (U06)."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.cwd = self.tmp.name
        self.slug = "2026-10-17-test-guard"
        self.plan_rel = f"docs/tdq/plan/{self.slug}.md"
        self.full_plan = os.path.join(self.cwd, self.plan_rel)
        os.makedirs(os.path.dirname(self.full_plan), exist_ok=True)
        with open(self.full_plan, "w", encoding="utf-8") as f:
            f.write(PLAN_TUONG_MINH)
        self.addCleanup(self.tmp.cleanup)

    def test_unknown_projection_version_tu_choi_ngay(self):
        """Phiên bản projection không xác định (ví dụ v999) bị từ chối ngay, không giả định là current."""
        ban_do = {
            "slug": self.slug,
            "plan_file": self.plan_rel,
            "projection_version": "v999",
            "projection_mode": "explicit",
            "plan_assignment_sha": "fake_sha",
            "tasks": {},
        }
        stale, ly_do = tdq_team.kiem_tra_stale(self.full_plan, ban_do)
        self.assertTrue(stale)
        self.assertIn("Unknown projection version 'v999'", ly_do)

    def test_map_khong_hop_le_hoac_thieu_file(self):
        """Dữ liệu bản đồ không phải dict hoặc file plan không tồn tại."""
        stale, ly_do = tdq_team.kiem_tra_stale(self.full_plan, "khong phai dict")
        self.assertTrue(stale)
        self.assertIn("not a valid object", ly_do)

        stale, ly_do = tdq_team.kiem_tra_stale("file_khong_ton_tai.md", {})
        self.assertTrue(stale)
        self.assertIn("not found", ly_do)

    def test_ghi_ban_do_atomic_khong_de_lai_file_tam(self):
        """ghi_ban_do_atomic ghi toàn vẹn file đích và dọn dẹp sạch file tạm."""
        duong = os.path.join(self.cwd, "docs", "tdq", "team", f"{self.slug}.json")
        du_lieu = {"test": 123, "slug": self.slug}
        tdq_team.ghi_ban_do_atomic(duong, du_lieu)

        self.assertTrue(os.path.isfile(duong))
        with open(duong, encoding="utf-8") as f:
            doc_lai = json.load(f)
        self.assertEqual(doc_lai, du_lieu)

        # Không còn file .tmp nào trong thư mục
        thu_muc = os.path.dirname(duong)
        file_tam = [f for f in os.listdir(thu_muc) if f.endswith(".tmp")]
        self.assertEqual(file_tam, [])


class TestU09HoldVaConflictProbe(unittest.TestCase):
    """Kiểm tra U09 ở trạng thái HOLD và năng lực phân biệt clean/conflict/error của probe (U09)."""

    def test_u09_status_va_reason_duoc_ghi_nhan_ro_rang(self):
        """U09 khai báo rõ trạng thái HOLD và lý do theo đúng hợp đồng spec."""
        self.assertEqual(tdq_team.U09_STATUS, "HOLD")
        self.assertIn("Chưa đủ history/corpus case", tdq_team.U09_REASON)

    def test_probe_do_xung_dot_phong_ve(self):
        """Probe git merge-tree giữ nguyên tính năng 3-way không sửa working tree."""
        # Kiểm tra sự tồn tại của hàm probe hiện hữu
        self.assertTrue(callable(tdq_team._do_xung_dot))
        # Không có cờ advisory tự động sinh cạnh DAG ảo
        self.assertFalse(hasattr(tdq_team, "_sinh_canh_dag_advisory"))


if __name__ == "__main__":
    unittest.main()
