"""P5 — mỗi rule của scripts/doc_lint.py có 1 fixture bẩn + 1 fixture sạch.

Lint là thứ duy nhất chặn doc trôi về dạng văn xuôi mà model nhỏ đọc sai, nên
chính nó phải được kiểm: rule bắt đúng cái cần bắt và KHÔNG báo nhầm cái sạch.
"""
import os
import subprocess
import sys
import tempfile
import unittest

from helper import ROOT

LINT = os.path.join(ROOT, "scripts", "doc_lint.py")

sys.path.insert(0, os.path.join(ROOT, "scripts"))
import doc_lint  # noqa: E402  — đọc hằng CONTRACT_FIELDS trực tiếp


class LintBase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)

    def write(self, name, text, skill=None):
        """Ghi fixture. `skill` → đặt vào skills/<skill>/SKILL.md giả để R6/R7 soi."""
        path = os.path.join(self.tmp.name, *( [skill] if skill else [] ), name)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
        return path

    def lint(self, *paths):
        proc = subprocess.run([sys.executable, LINT, *paths],
                              capture_output=True, text=True)
        return proc.returncode, proc.stdout

    def assert_hits(self, path, rule):
        code, out = self.lint(path)
        self.assertEqual(code, 1, f"phải báo vi phạm:\n{out}")
        self.assertIn(f"[{rule}]", out, out)

    def assert_clean(self, path):
        code, out = self.lint(path)
        self.assertEqual(code, 0, f"fixture sạch mà vẫn báo:\n{out}")


class MissingPathTest(LintBase):
    """A19/A20 — path không tồn tại phải báo lỗi tử tế + exit ≠0."""

    def _lint_err(self, *paths):
        proc = subprocess.run([sys.executable, LINT, *paths],
                              capture_output=True, text=True)
        return proc.returncode, proc.stdout, proc.stderr

    def test_missing_path_no_md_suffix_exit_nonzero(self):
        # A19: trước đây collect() bỏ lặng path ma không đuôi .md → exit 0
        code, _, err = self._lint_err("/duong/dan/khong/ton/tai")
        self.assertNotEqual(code, 0)
        self.assertIn("không tìm thấy", err)

    def test_missing_md_file_friendly_message(self):
        # A20: path ma đuôi .md phải ra message, không traceback thô
        code, _, err = self._lint_err("/duong/dan/khong/ton/tai.md")
        self.assertNotEqual(code, 0)
        self.assertNotIn("Traceback", err)
        self.assertIn("không tìm thấy", err)

    def test_mixed_missing_and_real_still_reports_missing(self):
        real = self.write("ok.md", "# Doc\n\nNội dung ngắn.\n")
        code, _, err = self._lint_err(real, "/duong/dan/ma.md")
        self.assertNotEqual(code, 0)
        self.assertIn("không tìm thấy", err)


class DocLintTest(LintBase):
    # ------------------------------------------------------------ khung chạy
    def test_runner_and_allow_comment(self):
        self.assertEqual(self.lint()[0], 2, "không có đối số → exit 2")
        dirty = "# T\n\n## Các bước\n\n1. Một\n3. Ba\n"
        self.assert_hits(self.write("dirty.md", dirty), "R1")
        allowed = "# T\n\n## Các bước\n\n1. Một\n<!-- doc-lint: allow R1 -->\n3. Ba\n"
        self.assert_clean(self.write("allowed.md", allowed))
        # allow sai mã thì không tắt được rule
        wrong = "# T\n\n## Các bước\n\n1. Một\n<!-- doc-lint: allow R4 -->\n3. Ba\n"
        self.assert_hits(self.write("wrong.md", wrong), "R1")

    # ------------------------------------------------------------------- R1
    def test_r1(self):
        self.assert_hits(self.write("a.md", "# T\n\n## Các bước\n\n1. Một\n1. Lại một\n"), "R1")
        self.assert_clean(self.write("b.md", "# T\n\n## Các bước\n\n1. Một\n2. Hai\n3. Ba\n"))
        # ngoài mục "Các bước" thì số bước tự do
        self.assert_clean(self.write("c.md", "# T\n\n## Ghi chú\n\n1. Một\n5. Năm\n"))

    # ------------------------------------------------------------------- R2
    def test_r2(self):
        self.assert_hits(self.write("a.md", "# T\n\nChạy python3 scripts/tdq_state.py next.\n"), "R2")
        self.assert_clean(self.write("b.md", "# T\n\n```\npython3 scripts/tdq_state.py next\n```\n"))

    def test_r2_table_and_inline_ok(self):
        table = "# T\n\n| phase | lệnh |\n|---|---|\n| spec | python3 scripts/tdq_state.py next |\n"
        self.assert_clean(self.write("t.md", table))
        inline = "# T\n\nChạy `python3 scripts/tdq_state.py next` rồi làm theo.\n"
        self.assert_clean(self.write("i.md", inline))

    # ------------------------------------------------------------------- R3
    def test_r3(self):
        body = "---\nname: tdq-spec\n---\n\n# S\n\n## Các bước\n\n1. Làm gì đó.\n"
        self.assert_hits(self.write("SKILL.md", body + "\nreferences/spec-template.md\n",
                                    skill="tdq-spec"), "R3")
        ok = body + "\nreferences/spec-template.md\n\nXong khi: xong.\nBước kế tiếp: sang plan.\n"
        self.assert_clean(self.write("SKILL.md", ok, skill="tdq-spec"))

    # ------------------------------------------------------------------- R4
    def test_r4_scoped(self):
        self.assert_hits(self.write("a.md", "# T\n\n## Các bước\n\n1. Làm nếu cần.\n"), "R4")
        # ngoài mục bước/luật → không soát
        self.assert_clean(self.write("b.md", "# T\n\n## Ghi chú\n\nLàm nếu cần.\n"))
        # có `→` làm rõ ngay sau → tha
        self.assert_clean(self.write("c.md",
                                     "# T\n\n## Các bước\n\n1. Làm nếu cần.\n   Rỗng → bỏ qua.\n"))

    # ------------------------------------------------------------------- R5
    def test_r5(self):
        long_sentence = "một hai ba bốn năm " * 10 + "kết."
        self.assert_hits(self.write("a.md", f"# T\n\n{long_sentence}\n"), "R5")
        self.assert_clean(self.write("b.md", "# T\n\nCâu ngắn. Câu ngắn nữa.\n"))

    def test_allow_r5_ngay_tren_doan(self):
        """Cửa thoát chuẩn phải im được R5.

        Bug cũ: rule_r5 gom dòng liền nhau thành một buffer nên nuốt luôn dòng
        comment. `state["start"]` trỏ vào comment, `allowed()` soi lên dòng TRÊN
        comment và không thấy gì — cửa thoát vô hiệu, câu còn dài thêm.
        """
        long_sentence = "một hai ba bốn năm " * 10 + "kết."
        text = f"# T\n\n<!-- doc-lint: allow R5 -->\n{long_sentence}\n"
        self.assert_clean(self.write("allow5.md", text))

    def test_allow_r5_khong_lan_sang_doan_khac(self):
        """Miễn trừ chỉ cho đúng đoạn ngay dưới, không miễn cả file."""
        long_sentence = "một hai ba bốn năm " * 10 + "kết."
        text = (f"# T\n\n<!-- doc-lint: allow R5 -->\n{long_sentence}\n\n"
                f"{long_sentence}\n")
        self.assert_hits(self.write("allow5b.md", text), "R5")

    # ------------------------------------------------------------------- R6
    def test_r6(self):
        self.assert_hits(self.write("big.md", "# T\n" + "dòng\n" * 600), "R6")
        head = "---\nname: tdq-status\n---\n\nXong khi: x.\nBước kế tiếp: y.\n"
        over = head + "ghi chú\n" * 100
        self.assert_hits(self.write("SKILL.md", over, skill="tdq-status"), "R6")
        self.assert_clean(self.write("SKILL.md", head, skill="tdq-status"))

    # ------------------------------------------------------------------- R7
    def test_r7(self):
        body = "---\nname: tdq-plan\n---\n\nXong khi: x.\nBước kế tiếp: y.\n"
        self.assert_hits(self.write("SKILL.md", body, skill="tdq-plan"), "R7")
        ok = body + "\nKhuôn: [references/plan-template.md](references/plan-template.md)\n"
        self.assert_clean(self.write("SKILL.md", ok, skill="tdq-plan"))
        # skill không sinh file cho user thì không đòi template
        self.assert_clean(self.write("SKILL.md", body, skill="tdq-status"))

    # ------------------------------------------------------------- repo thật
    def test_repo_docs_clean(self):
        code, out = self.lint(os.path.join(ROOT, "skills"))
        self.assertEqual(code, 0, f"doc trong repo còn vi phạm lint:\n{out}")


if __name__ == "__main__":
    unittest.main()


SPEC_3B_OK = """# SPEC — X

## 3b. Năng lực & công cụ

| Skill | Nguồn | Phán quyết | Dùng ở đâu / Lý do loại |
|---|---|---|---|
| `dataviz` | built-in | DÙNG | vẽ biểu đồ đầu ra #2 |
| `graphify` | user | KHÔNG | khác lĩnh vực |
| `tdq-intake` | plugin:tdq-workflow | NỀN | workflow đang chạy |
"""

PLAN_CONTRACT_OK = """# PLAN — X

- [ ] **T1.1** Vẽ biểu đồ — Test: chạy lệnh Kiểm
  - Dùng: `dataviz`
  - Để: chọn dạng biểu đồ, nạp skill TRƯỚC bước đỏ.
  - Ra: `src/chart.tsx`.
  - Kiểm: `test -f src/chart.tsx`
  - Không dùng cho: layout trang.

## Cụm song song

Một cụm vì chỉ có một task.
"""

# Bản KHÔNG có mục cụm song song — dùng cho ca đỏ của luật mới (2026-08-18).
PLAN_THIEU_CUM = PLAN_CONTRACT_OK.split("## Cụm song song")[0]


class ContractFieldsTest(unittest.TestCase):
    """Hợp đồng skill còn 5 trường: `Dùng` + 4 trường bắt buộc (bỏ `Nạp` 2026-08-09)."""

    def test_nap_khong_con_bat_buoc(self):
        self.assertNotIn("Nạp", doc_lint.CONTRACT_FIELDS)

    def test_dung_bon_truong_bat_buoc(self):
        self.assertEqual(("Để", "Ra", "Kiểm", "Không dùng cho"),
                         doc_lint.CONTRACT_FIELDS)


class R8Test(LintBase):
    """R8 chỉ soi file nằm trong thư mục tên `spec/`."""

    def test_r8_missing_3b(self):
        self.assert_hits(self.write(os.path.join("spec", "a.md"), "# SPEC\n\n## 1. X\n"), "R8")

    def test_r8_outside_spec_dir_ignored(self):
        self.assert_clean(self.write("a.md", "# SPEC\n\n## 1. X\n"))

    def test_r8_empty_table(self):
        text = "# S\n\n## 3b. Năng lực & công cụ\n\n| Skill | Nguồn | Phán quyết | Ghi chú |\n|---|---|---|---|\n"
        self.assert_hits(self.write(os.path.join("spec", "b.md"), text), "R8")

    def test_r8_bad_decision(self):
        text = SPEC_3B_OK.replace("| built-in | DÙNG |", "| built-in | CÓ THỂ |")
        self.assert_hits(self.write(os.path.join("spec", "c.md"), text), "R8")

    def test_r8_custom_reason(self):
        text = SPEC_3B_OK.replace("khác lĩnh vực", "thấy không thích")
        self.assert_hits(self.write(os.path.join("spec", "d.md"), text), "R8")

    def test_r8_clean(self):
        self.assert_clean(self.write(os.path.join("spec", "e.md"), SPEC_3B_OK))

    def test_r8_file_level_allow(self):
        """Spec viết trước 0.3.3: 1 dòng allow ở bất kỳ đâu miễn cả rule cho file đó."""
        text = "# SPEC cũ\n<!-- doc-lint: allow R8 -->\n\n## 1. X\n"
        self.assert_clean(self.write(os.path.join("spec", "f.md"), text))


class TdqDocsScopeTest(LintBase):
    """R1–R7 viết cho doc HƯỚNG DẪN. Output của workflow chỉ chịu R8."""

    def test_output_workflow_khong_chiu_r5(self):
        long_sentence = "một hai ba bốn năm " * 10 + "kết."
        path = self.write(os.path.join("docs", "tdq", "brief", "x.md"),
                          f"# Brief\n\n{long_sentence}\n")
        self.assert_clean(path)

    def test_output_workflow_khong_chiu_r2(self):
        # lệnh trần giữa văn bản: R2 bắt ở skills/, nhưng brief là biên bản
        path = self.write(os.path.join("docs", "tdq", "brief", "y.md"),
                          "# Brief\n\nĐã chạy python3 scripts/tdq_state.py next.\n")
        self.assert_clean(path)

    def test_spec_van_chiu_r8(self):
        path = self.write(os.path.join("docs", "tdq", "spec", "z.md"),
                          "# SPEC\n\n## 1. X\n")
        self.assert_hits(path, "R8")

    def test_working_log_khong_chiu_r2(self):
        # working log trích nguyên văn lệnh đã chạy — sửa để chiều R2 là làm sai biên bản
        path = self.write(os.path.join("docs", "workinglog", "2026-08-08.md"),
                          "# Log\n\nĐã chạy python3 -m unittest discover -q.\n")
        self.assert_clean(path)

    def test_ngoai_docs_tdq_van_chiu_r5(self):
        long_sentence = "một hai ba bốn năm " * 10 + "kết."
        path = self.write(os.path.join("skills", "x", "note.md"),
                          f"# T\n\n{long_sentence}\n")
        self.assert_hits(path, "R5")


class PairTest(LintBase):
    """--pair <spec> <plan>: mỗi DÙNG ở §3b phải có khối hợp đồng đủ 6 trường."""

    def pair(self, spec_text, plan_text):
        spec = self.write(os.path.join("spec", "s.md"), spec_text)
        plan = self.write(os.path.join("plan", "p.md"), plan_text)
        proc = subprocess.run([sys.executable, LINT, "--pair", spec, plan],
                              capture_output=True, text=True)
        return proc.returncode, proc.stdout

    def test_pair_ok(self):
        code, out = self.pair(SPEC_3B_OK, PLAN_CONTRACT_OK)
        self.assertEqual(code, 0, out)

    def test_pair_missing_field_named(self):
        plan = PLAN_CONTRACT_OK.replace("  - Kiểm: `test -f src/chart.tsx`\n", "")
        code, out = self.pair(SPEC_3B_OK, plan)
        self.assertEqual(code, 1)
        self.assertIn("Kiểm", out)
        self.assertIn("dataviz", out)

    def test_pair_dung_without_block(self):
        code, out = self.pair(SPEC_3B_OK, "# PLAN — X\n\n- [ ] **T1.1** Không hợp đồng gì\n")
        self.assertEqual(code, 1)
        self.assertIn("dataviz", out)

    def test_pair_nen_khong_need_no_block(self):
        """NỀN và KHÔNG không đòi hợp đồng — chỉ DÙNG mới đòi."""
        spec = SPEC_3B_OK.replace("| built-in | DÙNG | vẽ biểu đồ đầu ra #2 |",
                                  "| built-in | KHÔNG | khác lĩnh vực |")
        code, out = self.pair(spec, "# PLAN — X\n\n- [ ] **T1.1** Trơn\n\n## Cụm song song\n\nMột cụm.\n")
        self.assertEqual(code, 0, out)

    def test_pair_bad_argc(self):
        proc = subprocess.run([sys.executable, LINT, "--pair", "mot-file"],
                              capture_output=True, text=True)
        self.assertEqual(proc.returncode, 2)

    def test_pair_ok_with_mcp_label(self):
        """Nhãn `(mcp)` cuối dòng `- Dùng:` (cú pháp chuẩn) không được làm sai tên skill."""
        plan = PLAN_CONTRACT_OK.replace("  - Dùng: `dataviz`\n", "  - Dùng: `dataviz` (mcp)\n")
        code, out = self.pair(SPEC_3B_OK, plan)
        self.assertEqual(code, 0, out)


RULE_3_MUC_OK = """# Luật mẫu

## Khi nào áp dụng

- Thấy file đuôi `.py` trong danh sách file đổi.

## Làm gì

1. Chạy `ruff check <file>`.
2. Sửa từng dòng ruff báo, chạy lại đến khi sạch.

## Tự kiểm

- `ruff check <file>` exit 0.
"""
RULE_THIEU_MUC = RULE_3_MUC_OK.replace("## Tự kiểm", "## Ghi chú")


SPEC_LANE_FULL_CO_2B = SPEC_3B_OK.replace(
    "# SPEC — X\n",
    "# SPEC — X\n\nNgày: 2026-08-18 · Bản: 1.0 · Lane: full\n\n## 2b. Ranh giới module\n\n"
    "| Module | Vùng file | Phụ thuộc module | Đầu ra §2 nào |\n|---|---|---|---|\n"
    "| lõi | `a.py` | không | 1 |\n")

SPEC_LANE_FULL_THIEU_2B = SPEC_3B_OK.replace(
    "# SPEC — X\n", "# SPEC — X\n\nNgày: 2026-08-18 · Bản: 1.0 · Lane: full\n")

SPEC_LANE_QUICK_THIEU_2B = SPEC_3B_OK.replace(
    "# SPEC — X\n", "# SPEC — X\n\nNgày: 2026-08-18 · Bản: 1.0 · Lane: quick\n")


class R10Test(LintBase):
    """R10 — spec lane full phải có mục ranh giới module, để plan có sẵn đường cắt."""

    def test_r10_lane_full_thieu_2b(self):
        path = os.path.join("spec", "full-thieu.md")
        self.assert_hits(self.write(path, SPEC_LANE_FULL_THIEU_2B), "R10")

    def test_r10_lane_full_co_2b_sach(self):
        path = os.path.join("spec", "full-du.md")
        self.assert_clean(self.write(path, SPEC_LANE_FULL_CO_2B))

    def test_r10_lane_quick_khong_soi(self):
        """Lane quick cố ý bỏ mục này — báo ở đây là báo nhầm."""
        path = os.path.join("spec", "quick.md")
        self.assert_clean(self.write(path, SPEC_LANE_QUICK_THIEU_2B))

    def test_r10_allow_muc_file_cho_spec_cu(self):
        """Spec viết trước khi có R10 dán 1 dòng allow là qua — y hệt cơ chế của R8.

        Dòng allow dùng mã hai chữ số, nên regex ALLOW phải nhận `R\\d+` chứ không
        phải `R\\d`; đây là chỗ dễ vỡ nhất của luật này.
        """
        text = SPEC_LANE_FULL_THIEU_2B.replace(
            "# SPEC — X\n", "# SPEC — X\n\n<!-- doc-lint: allow R10 -->\n")
        self.assert_clean(self.write(os.path.join("spec", "cu.md"), text))

    def test_r10_allow_kem_ly_do_van_duoc(self):
        """Dòng allow được ghi kèm lý do; không cho thì người ta dán allow trần, mất vết."""
        text = SPEC_LANE_FULL_THIEU_2B.replace(
            "# SPEC — X\n",
            "# SPEC — X\n\n<!-- doc-lint: allow R10 — spec viết trước luật này -->\n")
        self.assert_clean(self.write(os.path.join("spec", "cu-ly-do.md"), text))

    def test_r10_ngoai_thu_muc_spec_khong_soi(self):
        self.assert_clean(self.write("ngoai.md", SPEC_LANE_FULL_THIEU_2B))


class PairCumSongSongTest(LintBase):
    """Plan phải luôn có mục `## Cụm song song` — modular là thuộc tính của tài liệu."""

    def _pair(self, plan_text):
        spec = self.write(os.path.join("spec", "s.md"), SPEC_3B_OK)
        plan = self.write("p.md", plan_text)
        proc = subprocess.run([sys.executable, LINT, "--pair", spec, plan],
                              capture_output=True, text=True)
        return proc.returncode, proc.stdout

    def test_pair_plan_thieu_cum_song_song(self):
        code, out = self._pair(PLAN_THIEU_CUM)
        self.assertEqual(code, 1, out)
        self.assertIn("Cụm song song", out)

    def test_pair_plan_du_cum_song_song(self):
        code, out = self._pair(PLAN_CONTRACT_OK)
        self.assertEqual(code, 0, out)


class R9Test(LintBase):
    """R9 chỉ soi soul.md + references/rules/ — khuôn 3 mục cho model yếu nhất."""

    def test_r9_soul_thieu_muc(self):
        self.assert_hits(self.write("soul.md", RULE_THIEU_MUC), "R9")

    def test_r9_rules_dir_thieu_muc(self):
        path = os.path.join("references", "rules", "python.md")
        self.assert_hits(self.write(path, RULE_THIEU_MUC), "R9")

    def test_r9_du_muc_sach(self):
        self.assert_clean(self.write("soul.md", RULE_3_MUC_OK))
        self.assert_clean(
            self.write(os.path.join("references", "rules", "go.md"), RULE_3_MUC_OK))

    def test_r9_ngoai_pham_vi_khong_soi(self):
        self.assert_clean(self.write("huong-dan.md", RULE_THIEU_MUC))

    def test_r9_clean_code_thieu_muc(self):
        """Luật clean code mất phần kiểm bằng lệnh (script scan đã xoá) — R9 gánh hình dạng."""
        path = os.path.join("references", "clean-code.md")
        self.assert_hits(self.write(path, RULE_THIEU_MUC), "R9")

    def test_r9_clean_code_du_muc_sach(self):
        self.assert_clean(
            self.write(os.path.join("references", "clean-code.md"), RULE_3_MUC_OK))

    def test_r9_chi_dung_ten_file_clean_code(self):
        """Đóng đinh ĐÚNG tên file, không mở cả thư mục `references/`."""
        self.assert_clean(
            self.write(os.path.join("references", "interview.md"), RULE_THIEU_MUC))

    def test_r9_heading_trong_fence_khong_tinh(self):
        gia = "# Luật\n\n```\n## Khi nào áp dụng\n## Làm gì\n## Tự kiểm\n```\n"
        self.assert_hits(self.write("soul.md", gia), "R9")


class LogServiceTest(LintBase):
    """Spec §4: mọi script của TDQ có log service bật mặc định, tắt được bằng TDQ_LOG=0."""

    def chay(self, path, env_them=None):
        env = dict(os.environ)
        env.update(env_them or {})
        return subprocess.run([sys.executable, LINT, path], capture_output=True,
                              text=True, env=env)

    def test_log_bat_mac_dinh_ra_stderr(self):
        sach = self.write("sach.md", "# Tiêu đề\n\nMột dòng.\n")
        r = self.chay(sach)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("doc_lint", r.stderr)
        self.assertIn("sach.md", r.stderr)
        # timestamp ISO trong ngoặc vuông ở đầu dòng log
        self.assertRegex(r.stderr, r"\[\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\]")

    def test_log_tat_duoc_bang_bien_moi_truong(self):
        sach = self.write("sach.md", "# Tiêu đề\n\nMột dòng.\n")
        self.assertEqual(self.chay(sach, {"TDQ_LOG": "0"}).stderr, "")

    def test_log_khong_lam_ban_stdout(self):
        """stdout là kênh của vi phạm lint; log lẫn vào đó là hỏng hợp đồng máy đọc."""
        sach = self.write("sach.md", "# Tiêu đề\n\nMột dòng.\n")
        self.assertEqual(self.chay(sach).stdout, "")
