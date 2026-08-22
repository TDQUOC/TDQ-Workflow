"""Test cho scripts/skill_tokens.py — thước đo token thật của bộ skill.

Luật của bộ test này: **cấm chấp nhận số đoán**. Test quan trọng nhất ở đây không
phải "script in ra bảng", mà "script THÀ LỖI còn hơn ước lượng ký tự chia bốn" —
vì cả request này đứng trên giả định con số đo được là con số thật.
"""
import os
import subprocess
import sys
import unittest

import helper  # noqa: F401  — chèn scripts/ vào sys.path
import skill_tokens

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT = os.path.join(ROOT, "scripts", "skill_tokens.py")
VENV = os.path.join(ROOT, ".venv-tokens", "bin", "python")


def chay(*args, env=None):
    proc = subprocess.run([sys.executable, SCRIPT, *args], capture_output=True,
                          text=True, timeout=300,
                          env=dict(os.environ, TDQ_LOG="0", **(env or {})))
    return proc.returncode, proc.stdout, proc.stderr


def co_thu_vien():
    """Venv có thư viện đếm token không — quyết định test nào chạy được thật."""
    if not os.path.exists(VENV):
        return False
    proc = subprocess.run([VENV, "-c", "import anthropic_tokenizer"],
                          capture_output=True, timeout=60)
    return proc.returncode == 0


CO_THU_VIEN = co_thu_vien()


class CamDoanTokenTest(unittest.TestCase):
    """Luật xương sống: thiếu thư viện thì LỖI, không rơi về ký tự/4."""

    def test_thieu_thu_vien_thi_thoat_ma_3_va_khong_in_bang(self):
        """Chặn đường nhảy sang venv để dựng lại đúng cảnh máy chưa cài gì."""
        rc, out, err = chay("--theo-phase", env={"TDQ_TOKENS_DA_NHAY": "1",
                                                 "TDQ_TOKENS_VENV": "khong-co"})
        if rc == 0:
            self.skipTest("python chạy test đã có sẵn anthropic-tokenizer")
        self.assertEqual(rc, skill_tokens.EXIT_THIEU_THU_VIEN)
        self.assertNotIn("| khối phase |", out)
        self.assertIn("anthropic-tokenizer", err)

    def test_nap_bo_dem_nem_loi_chu_khong_nuot_tien_trinh(self):
        """Hàm thư viện tuyệt đối không được `execv` — nó ăn mất cả test runner."""
        # Soi bytecode chứ không soi chữ: docstring của hàm có nhắc `execv` để giải
        # thích vì sao cấm, soi chữ sẽ bắt nhầm chính lời giải thích đó.
        ten_goi = skill_tokens.nap_bo_dem.__code__.co_names
        self.assertNotIn("execv", ten_goi)
        self.assertNotIn("exit", ten_goi)
        self.assertTrue(issubclass(skill_tokens.ThieuThuVienDem, Exception))

    def test_thong_bao_loi_co_lenh_cai_chay_duoc(self):
        self.assertIn("pip install", skill_tokens.CAI_DAT)
        self.assertIn("anthropic-tokenizer==0.1.0", skill_tokens.CAI_DAT)


class PhanMucTest(unittest.TestCase):
    """Phân mục là thứ quyết định nhóm nào bị đề xuất tắt — sai mục là tắt nhầm."""

    def test_moi_nguon_trong_bang_muc_deu_ra_dung_muc(self):
        for ten_muc, khoa in skill_tokens.MUC:
            for k in khoa:
                with self.subTest(nguon=k):
                    self.assertEqual(skill_tokens.phan_muc(f"plugin:{k}"), ten_muc)

    def test_nguon_la_thi_roi_vao_khac_chu_khong_vang(self):
        self.assertEqual(skill_tokens.phan_muc("plugin:khong-he-ton-tai"),
                         skill_tokens.MUC_KHAC)
        self.assertEqual(skill_tokens.phan_muc("user"), skill_tokens.MUC_KHAC)

    def test_moi_nguon_chi_thuoc_dung_mot_muc(self):
        """Một nguồn khớp hai mục thì tổng theo mục sẽ đếm trùng — phải chặn từ gốc."""
        thay = {}
        for ten_muc, khoa in skill_tokens.MUC:
            for k in khoa:
                self.assertNotIn(k, thay,
                                 f"khoá {k!r} nằm ở cả {thay.get(k)!r} và {ten_muc!r}")
                thay[k] = ten_muc


class KhungTest(unittest.TestCase):
    """CLI và log service."""

    def test_khong_co_co_nao_thi_bao_loi_cu_phap(self):
        rc, _out, err = chay()
        self.assertEqual(rc, 2)
        self.assertIn("--theo-phase", err)

    def test_hai_co_cung_luc_cung_bao_loi(self):
        rc, _out, err = chay("--theo-phase", "--mo-ta")
        self.assertEqual(rc, 2)
        self.assertIn("--mo-ta", err)

    @unittest.skipUnless(CO_THU_VIEN, "venv .venv-tokens chưa cài anthropic-tokenizer")
    def test_log_bat_mac_dinh_va_tat_duoc(self):
        moi = dict(os.environ)
        moi.pop("TDQ_LOG", None)
        proc = subprocess.run([sys.executable, SCRIPT, "--theo-phase"],
                              capture_output=True, text=True, timeout=300, env=moi)
        self.assertRegex(proc.stderr, r"\[\d{4}-\d{2}-\d{2}T")
        _rc, _out, err_tat = chay("--theo-phase")
        self.assertEqual(err_tat.strip(), "")


class DoTheoPhaseTest(unittest.TestCase):
    """`--theo-phase`: sáu khối, số dương, và nói thật rằng đó là TRẦN."""

    @unittest.skipUnless(CO_THU_VIEN, "venv .venv-tokens chưa cài anthropic-tokenizer")
    def test_in_du_sau_khoi_va_thoat_0(self):
        rc, out, _err = chay("--theo-phase")
        self.assertEqual(rc, 0)
        for ten_khoi, _ in skill_tokens.KHOI_PHASE:
            self.assertIn(f"| {ten_khoi} |", out)
        self.assertIn(skill_tokens.KHOI_LUAT_KEM, out)

    @unittest.skipUnless(CO_THU_VIEN, "venv .venv-tokens chưa cài anthropic-tokenizer")
    def test_khai_ro_la_tran_tren_chu_khong_phai_so_that(self):
        """Số gộp mọi reference cao hơn số một request thật đọc — cấm giấu chỗ này."""
        _rc, out, _err = chay("--theo-phase")
        self.assertIn("UPPER BOUND", out)

    def test_moi_khoi_deu_co_skill_ton_tai_that(self):
        for _ten_khoi, skills in skill_tokens.KHOI_PHASE:
            for skill in skills:
                with self.subTest(skill=skill):
                    self.assertIsNotNone(skill_tokens._than_skill(skill))


class DoMoTaTest(unittest.TestCase):
    """`--mo-ta`: tổng phải khớp inventory, nếu không thì đang đếm nhầm tập skill."""

    @unittest.skipUnless(CO_THU_VIEN, "venv .venv-tokens chưa cài anthropic-tokenizer")
    def test_so_skill_khop_dung_skill_inventory(self):
        import skill_inventory
        mong_doi = len(skill_inventory.inventory(ROOT))
        _rc, out, _err = chay("--mo-ta")
        self.assertIn(f"Total: {mong_doi} enabled skill(s)", out)

    @unittest.skipUnless(CO_THU_VIEN, "venv .venv-tokens chưa cài anthropic-tokenizer")
    def test_bang_co_ca_cot_token_va_cot_muc(self):
        _rc, out, _err = chay("--mo-ta")
        self.assertIn("desc tokens", out)
        self.assertIn("| group |", out)

    @unittest.skipUnless(CO_THU_VIEN, "venv .venv-tokens chưa cài anthropic-tokenizer")
    def test_token_chi_giu_ten_luon_nho_hon_token_mo_ta(self):
        """Giữ tên mà đắt hơn giữ cả mô tả thì phép đo đã sai ở đâu đó.

        Đọc qua CLI chứ không gọi hàm trong tiến trình: python chạy pytest không có
        thư viện đếm token, gọi thẳng thì test bị skip và mất luôn phép kiểm này.
        """
        _rc, out, _err = chay("--mo-ta")
        so_dong = 0
        for dong in out.splitlines():
            o = [c.strip() for c in dong.strip().strip("|").split("|")]
            if len(o) != 5 or not o[2].isdigit():
                continue
            tok, ten_tok = int(o[3].replace(".", "")), int(o[4].replace(".", ""))
            with self.subTest(nguon=o[0]):
                self.assertLess(ten_tok, tok)
            so_dong += 1
        self.assertGreater(so_dong, 10, "bảng --mo-ta hầu như rỗng — không kiểm được gì")

    def test_ban_do_skill_md_quet_mot_lan_va_co_du_skill_tdq(self):
        ban_do = skill_tokens.ban_do_skill_md()
        for skill in ("tdq-intake", "tdq-spec", "tdq-plan", "tdq-build",
                      "tdq-conventions"):
            with self.subTest(skill=skill):
                self.assertIn(skill, ban_do)


if __name__ == "__main__":
    unittest.main()


class DemDuThuMucConTest(unittest.TestCase):
    """`_references` phải đếm cả file trong thư mục con của `references/`.

    Vì sao khoá: `tdq-build/references/rules/` có 10 file (14.554 token) nằm trong thư mục
    con. Bản `glob` không đệ quy bỏ qua toàn bộ nhóm đó, nên mọi con số "trần trên" của bộ
    skill đều thấp hơn thực tế — và một thước đo sai thấp thì mọi kết luận tối ưu dựng
    trên nó đều sai theo, không ai thấy.
    """

    def test_dem_ca_file_trong_thu_muc_con(self):
        ra = skill_tokens._references("tdq-build")
        con = [p for p in ra if os.sep + "rules" + os.sep in p]
        self.assertTrue(
            con,
            "`_references('tdq-build')` không thấy file nào trong `references/rules/` — "
            "thư mục con đang bị bỏ qua, mọi số đo sẽ thấp hơn thực tế")

    def test_dem_du_moi_file_md_duoi_references(self):
        for ten in ("tdq-build", "tdq-conventions", "tdq-intake"):
            thu_muc = os.path.join(ROOT, "skills", ten, "references")
            that = sorted(os.path.join(g, f)
                          for g, _, fs in os.walk(thu_muc) for f in fs if f.endswith(".md"))
            self.assertEqual(
                that, skill_tokens._references(ten),
                f"Danh sách reference của `{ten}` lệch với file thật trên đĩa")
