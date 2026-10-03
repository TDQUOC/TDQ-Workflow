"""R14: hàng §6 có ngưỡng số phải mang cột `Đo trước` và `Dự phòng nếu trượt` không rỗng."""
import contextlib
import io
import os
import shutil
import sys
import tempfile
import unittest

from helper import ROOT

sys.path.insert(0, os.path.join(ROOT, "scripts"))
import doc_lint  # noqa: E402

TEN_MOI = "2026-10-03-0732-thu.md"
TEN_CU = "2026-09-01-1200-thu.md"

DAU_THIEU = "| # | Hạng mục | Điều kiện PASS |\n|---|---|---|\n"
DAU_DU = ("| # | Hạng mục | Điều kiện PASS | Đo trước | Dự phòng nếu trượt |\n"
          "|---|---|---|---|---|\n")


def _spec(bang):
    return ("# SPEC — thử\n\n## 5. Ràng buộc\n\n| Q1 | ngoài §6 | ≤ 200 MB |\n\n"
            "## 6. QC & Definition of Done\n\n" + bang + "\n## 7. Câu hỏi còn mở\n\nkhông\n")


class TestR14Bat(unittest.TestCase):
    """Hàng có ngưỡng mà thiếu cột / ô rỗng → lỗi."""

    def test_bat_thieu_hai_cot(self):
        loi = doc_lint.r14_loi(_spec(DAU_THIEU + "| Q9 | Installer | ≤ 200 MB |\n"), TEN_MOI)
        self.assertEqual(len(loi), 1)
        so_dong, thong_bao = loi[0]
        self.assertEqual(_spec(DAU_THIEU + "| Q9 | Installer | ≤ 200 MB |\n")
                         .splitlines()[so_dong - 1], "| Q9 | Installer | ≤ 200 MB |")
        self.assertIn("Q9", thong_bao)

    def test_bat_khong_co_dau_bang(self):
        loi = doc_lint.r14_loi(_spec("| Q9 | Installer | ≤ 200 MB |\n"), TEN_MOI)
        self.assertEqual(len(loi), 1)

    def test_bat_o_rong_va_gach(self):
        for do, du in (("—", "giảm gói"), ("212 MB", "—"), ("", "giảm gói"), ("212 MB", "-")):
            bang = DAU_DU + f"| Q9 | Installer | ≤ 200 MB | {do} | {du} |\n"
            self.assertEqual(len(doc_lint.r14_loi(_spec(bang), TEN_MOI)), 1, (do, du))

    def test_bat_do_truoc_khong_co_so(self):
        bang = DAU_DU + "| Q9 | Installer | ≤ 200 MB | ước lượng: ổn | giảm gói |\n"
        self.assertEqual(len(doc_lint.r14_loi(_spec(bang), TEN_MOI)), 1)

    def test_bat_so_kem_don_vi(self):
        for dk in ("tải xong trong 30 giây", "phủ 80%", "tối đa ~5 phút", "không quá 2 lần",
                   "ít nhất 9", "≥ 9 trên 10 hàng", "<= 500 ms", "dưới 3 s"):
            bang = DAU_THIEU + f"| Q2 | thử | {dk} |\n"
            self.assertEqual(len(doc_lint.r14_loi(_spec(bang), TEN_MOI)), 1, dk)


class TestR14DuCot(unittest.TestCase):
    """Đủ hai cột, có số đo → không lỗi."""

    def test_du_cot_khong_loi(self):
        bang = DAU_DU + ("| Q9 | Installer | ≤ 200 MB | 212 MB + ~20 MB | "
                         "bỏ bộ font phụ, ghi lệch |\n")
        self.assertEqual(doc_lint.r14_loi(_spec(bang), TEN_MOI), [])

    def test_du_cot_bang_khong_co_cot_pass_dung_cot_3(self):
        bang = ("| # | Mục | Ngưỡng | Đo trước | Dự phòng nếu trượt |\n|---|---|---|---|---|\n"
                "| Q9 | Installer | ≤ 200 MB | 212 MB | giảm gói |\n"
                "| Q10 | Installer | ≤ 200 MB | — | — |\n")
        loi = doc_lint.r14_loi(_spec(bang), TEN_MOI)
        self.assertEqual(len(loi), 1)
        self.assertIn("Q10", loi[0][1])


class TestR14TonTai(unittest.TestCase):
    """Phép tồn tại / vắng mặt, số phiên bản, mã Q → không phải ngưỡng."""

    def test_ton_tai_khong_phai_nguong(self):
        for dk in ("≥ 1 test", "0 failure", "= 0 dòng", "bản 0.56.0", "Q3 và Q4 xanh",
                   "exit ≠ 0", "4 loại được nhận",
                   "trên 103 spec cũ → 0 lỗi R14", "a -> 5 b", "1 dòng", "đối chiếu §2 dòng 1"):
            bang = DAU_THIEU + f"| Q3 | thử | {dk} |\n"
            self.assertEqual(doc_lint.r14_loi(_spec(bang), TEN_MOI), [], dk)

    def test_ton_tai_ngoai_muc_6_khong_xet(self):
        self.assertEqual(doc_lint.r14_loi(_spec(DAU_THIEU), TEN_MOI), [])


class TestR14Moc(unittest.TestCase):
    """Spec trước mốc slug → im; spec hiện tại → qua."""

    def test_moc_slug_cu_im(self):
        van = _spec(DAU_THIEU + "| Q9 | Installer | ≤ 200 MB |\n")
        self.assertEqual(doc_lint.r14_loi(van, TEN_CU), [])
        self.assertEqual(doc_lint.r14_loi(van, "2026-10-03-0731-thu.md"), [])
        self.assertEqual(len(doc_lint.r14_loi(van, "docs/tdq/spec/" + TEN_MOI)), 1)

    def test_moc_spec_hien_tai_qua(self):
        """Spec hiện tại: hàng nào R14 bắt thì chỉ thiếu ô đo/dự phòng — điền vào BẢN SAO là qua.

        Từ T1.2, ngưỡng trong inline code cũng tính, nên Q1/Q2 của spec bị bắt cho tới khi
        leader điền hai ô ở spec. Test không sửa spec: nó điền trên bản sao trong bộ nhớ.
        """
        duong = os.path.join(ROOT, "docs", "tdq", "spec",
                             "2026-10-03-0732-do-truoc-lam-mot-turn.md")
        with open(duong, encoding="utf-8") as f:
            dong = f.read().splitlines()
        for so_dong, _ in doc_lint.r14_loi("\n".join(dong), duong):
            o = doc_lint._r14_o(dong[so_dong - 1])
            self.assertEqual(len(o), 5, dong[so_dong - 1])
            dong[so_dong - 1] = "| " + " | ".join(o[:3] + ["đo: 212 MB", "ghi lệch"]) + " |"
        self.assertEqual(doc_lint.r14_loi("\n".join(dong), duong), [])

    def test_moc_chi_nhanh_spec(self):
        tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, tmp, True)
        van = _spec(DAU_THIEU + "| Q9 | Installer | ≤ 200 MB |\n")
        for nhanh, mong in (("spec", 1), ("plan", 0)):
            thu_muc = os.path.join(tmp, "docs", "tdq", nhanh)
            os.makedirs(thu_muc)
            duong = os.path.join(thu_muc, TEN_MOI)
            with open(duong, "w", encoding="utf-8") as f:
                f.write(van)
            with contextlib.redirect_stderr(io.StringIO()):
                loi = [d for d in doc_lint.lint_file(duong) if "[R14]" in d]
            self.assertEqual(len(loi), mong, nhanh)


THU_MUC_SPEC = os.path.join(ROOT, "docs", "tdq", "spec")
H3 = "| # | Hạng mục kiểm | Điều kiện PASS |\n|---|---|---|\n"
H4 = ("| # | Hạng mục kiểm | Lệnh/cách kiểm | Điều kiện PASS |\n"
      "|---|---|---|---|\n")

# (đầu tên spec cũ, đầu bảng của spec đó, hàng chép nguyên văn) — 10 hàng CÓ ngưỡng số.
MAU_CO_NGUONG = [
    ("2026-08-19-1046", H3, "| Q3 | Thước đo còn chạy đủ nhanh để dùng | đo 5 session xong "
                            "dưới 60 giây trên máy này |"),
    ("2026-08-19-1616", H3, "| Q7 | Tiết kiệm token | tổng token bộ skill giảm ít nhất 30%, "
                            "đo bằng tokenizer thật |"),
    ("2026-08-22-1033", H3, "| Q10 | Ngưỡng disk | Tổng > 500 MB hoặc tuổi > 7 ngày → in cảnh "
                            "báo có kèm con số thật |"),
    ("2026-08-23-1125", H3, "| Q13 | Báo cáo không quá dài | file báo cáo không quá 250 dòng |"),
    ("2026-08-24-1427", H3, "| Q2 | Mã và lời chặn | Payload chặn chứa `[TDQ:UNFINISHED]`, nêu "
                            "số task còn hở, dài không quá 300 ký tự |"),
    ("2026-09-28-2324", H3, "| Q12 | Ba file về dưới trần | cả ba ≤ 3.500 token |"),
    ("2026-08-19-0121", H3, "| Q3 | Công cụ đo đếm đủ | `skill_tokens.py --theo-phase` liệt kê "
                            "35 file reference, trần ≥ 89.000 token |"),
    ("2026-09-23-1148", H3, "| Q6 | Luật chạm trần thời gian | tài liệu QC ghi trần 120 giây mỗi "
                            "phép, hành vi khi chạm trần, và luật cấm tự nâng trần khi chưa "
                            "hỏi user |"),
    ("2026-07-29-skill", H4, "| Q6 | Trần token | `python3 -m unittest test_token_budget "
                             "test_skill_shape` | Xanh; `tdq-intake` ≤120 dòng, reference mới "
                             "≤200 dòng, `next` ≤20 dòng |"),
    ("2026-08-07-siet", H4, "| Q3 | Toàn bộ suite không hồi quy | `cd tests && python3 -m unittest "
                            "discover . -q` | ≥ 615 test, đúng 1 failure và là "
                            "`test_claude_md_core.test_d_ban_repo_trung_ban_da_cai` (mốc đã đo "
                            "trước khi sửa: 603 test / 1 failure cùng tên) |"),
]

# 10 hàng KHÔNG có ngưỡng: exit 0, ≥ 1, = 0, mã Qn, ngày, số phiên bản, đường dẫn có số.
MAU_KHONG_NGUONG = [
    ("2026-08-19-0029", H3, "| Q3 | doc_lint sạch trên cả 2 file đầu ra | `doc_lint.py <file>` "
                            "exit 0 từng file |"),
    ("2026-08-22-1033", H3, "| Q19 | Khối gợi ý đủ và đúng | Mỗi lý do chặn trong tập đóng cho ra "
                            "≥ 1 phương án, mỗi phương án có một lệnh chạy được; lý do ngoài "
                            "tập → máy báo lỗi, không in khối rỗng |"),
    ("2026-09-16-1447", H3, "| Q3 | Mọi trích dẫn code kiểm được bằng máy | Số trích dẫn "
                            "`đường-dẫn:dòng` sai = 0 khi mở từng file và so với số dòng thật |"),
    ("2026-09-07-0905", H3, "| Q11 | QC độc lập | agent `tdq-qc-tester` chấm lại Q1–Q10 và kết "
                            "luận PASS kèm bằng chứng |"),
    ("2026-10-03-0015", H3, "| Q17 | Quyết định kiến trúc | `kien-truc.md` có dòng chốt "
                            "2026-10-03; `TDQ:SEARCH` có trong danh sách đóng và bảng mã |"),
    ("2026-09-27-1905", H3, "| Q9 | Suite trên macOS thật | 0 fail, 0 error, đo ở bản 3.13 |"),
    ("2026-08-05-bump", H4, "| Q1 | Version + changelog | `cd tests && python3 -m unittest "
                            "test_docs_consistency` | xanh, `plugin.json` = `0.7.0` |"),
    ("2026-07-29-skill", H4, "| Q11 | Đóng gói | `claude plugin validate . --strict` | PASS, "
                             "version 0.3.3 |"),
    ("2026-09-20-1823", H3, "| Q11 | Bộ test đầy đủ trên Windows | 0 fail, 0 error |"),
    ("2026-09-14-1252", H3, "| Q10 | Lượt thật — làm được | `run` với `ag/gemini-3.8-flash-medium` "
                            "trên task scratch làm được → JSON in ra có `trang_thai` = `xong`, "
                            "lệnh exit 0 |"),
]


def _spec_cu(dau):
    for ten in sorted(os.listdir(THU_MUC_SPEC)):
        if ten.startswith(dau) and ten.endswith(".md"):
            with open(os.path.join(THU_MUC_SPEC, ten), encoding="utf-8") as f:
                return f.read()
    return ""


def _bi_bat(dau_bang, hang):
    return bool(doc_lint.r14_loi(_spec(dau_bang + hang + "\n"), TEN_MOI))


class ChinhXac(unittest.TestCase):
    """Độ chính xác trên spec thật: ≥ 9/10 hàng có ngưỡng bị bắt, 0/10 hàng không ngưỡng."""

    def test_chinh_xac_mau_la_nguyen_van(self):
        for dau, _, hang in MAU_CO_NGUONG + MAU_KHONG_NGUONG:
            self.assertIn(hang, _spec_cu(dau).splitlines(), dau)

    def test_chinh_xac_bat_hang_co_nguong(self):
        trung = [hang for _, dau_bang, hang in MAU_CO_NGUONG if _bi_bat(dau_bang, hang)]
        self.assertEqual(len(MAU_CO_NGUONG), 10)
        self.assertGreaterEqual(len(trung), 9, [h for _, _, h in MAU_CO_NGUONG if h not in trung])

    def test_chinh_xac_khong_bat_oan(self):
        self.assertEqual(len(MAU_KHONG_NGUONG), 10)
        oan = [hang for _, dau_bang, hang in MAU_KHONG_NGUONG if _bi_bat(dau_bang, hang)]
        self.assertEqual(oan, [])

    def test_chinh_xac_inline_code_khong_con_mien(self):
        """Ngưỡng bọc backtick vẫn là ngưỡng — không còn lối né R14."""
        for dk in ("`≤ 200 MB`", "hàng `Installer ≤ 200 MB` thiếu 2 cột", "`wc -l` ≤ 120"):
            self.assertTrue(_bi_bat(DAU_THIEU, f"| Q1 | thử | {dk} |"), dk)

    def test_chinh_xac_dau_muc_khong_phai_so_kem_don_vi(self):
        """`§2 dòng 1` là trỏ tới mục, không phải `2 dòng`."""
        self.assertFalse(_bi_bat(H3, "| Q1 | x | đối chiếu §2 dòng 1, §12 dòng 4 |"))

    def test_chinh_xac_spec_cu_khong_loi_r14(self):
        """`doc_lint docs/tdq/spec` → 0 lỗi R14 trên mọi spec trước mốc."""
        loi = []
        for ten in sorted(os.listdir(THU_MUC_SPEC)):
            if not ten.endswith(".md") or ten[:15] >= doc_lint.R14_MOC:
                continue
            with contextlib.redirect_stderr(io.StringIO()):
                loi += [d for d in doc_lint.lint_file(os.path.join(THU_MUC_SPEC, ten))
                        if "[R14]" in d]
        self.assertEqual(loi, [])


class TestR14Log(unittest.TestCase):
    """R14 ghi một dòng log có giờ ISO; TDQ_LOG=0 tắt."""

    def setUp(self):
        tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, tmp, True)
        thu_muc = os.path.join(tmp, "docs", "tdq", "spec")
        os.makedirs(thu_muc)
        self.duong = os.path.join(thu_muc, TEN_MOI)
        with open(self.duong, "w", encoding="utf-8") as f:
            f.write(_spec(DAU_THIEU + "| Q9 | Installer | ≤ 200 MB |\n"))
        cu = os.environ.get("TDQ_LOG")
        self.addCleanup(lambda: os.environ.__setitem__("TDQ_LOG", cu) if cu is not None
                        else os.environ.pop("TDQ_LOG", None))

    def _chay(self):
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            doc_lint.lint_file(self.duong)
        return [d for d in err.getvalue().splitlines() if "R14" in d]

    def test_log_mot_dong_iso(self):
        os.environ["TDQ_LOG"] = "1"
        dong = self._chay()
        self.assertEqual(len(dong), 1)
        self.assertRegex(dong[0], r"^\[\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\] doc_lint: R14")

    def test_log_tat(self):
        os.environ["TDQ_LOG"] = "0"
        self.assertEqual(self._chay(), [])


if __name__ == "__main__":
    unittest.main()
