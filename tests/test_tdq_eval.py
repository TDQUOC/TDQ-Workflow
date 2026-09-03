"""Test cho scripts/tdq_eval.py — bộ đo hành vi tuân thủ luật của hai nhánh skill.

Luật của bộ test này: mọi phép kiểm phải có một mẫu ĐẠT và một mẫu VI PHẠM. Bộ chấm
nào chỉ được thử bằng mẫu đạt thì coi như chưa được thử — nó có thể luôn trả "đạt".
Không test nào ở đây gọi model hay tốn tiền.
"""
import argparse
import json
import os
import contextlib
import io
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
import unittest

import helper  # noqa: F401  — chèn scripts/ vào sys.path
import tdq_eval

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EVAL = os.path.join(ROOT, "scripts", "tdq_eval.py")


def chay(*args, env=None):
    proc = subprocess.run([sys.executable, EVAL, *args], capture_output=True,
                          text=True, timeout=300,
                          env=dict(os.environ, TDQ_EVAL_LOG="0", **(env or {})))
    return proc.returncode, proc.stdout, proc.stderr


class KhungTest(unittest.TestCase):
    """T1.1/T1.2 — khung CLI và log service."""

    def test_help_exit_0_va_liet_ke_du_4_lenh_con(self):
        rc, out, _err = chay("--help")
        self.assertEqual(rc, 0)
        for ten in ("setup", "run", "score", "report"):
            self.assertIn(ten, out)

    def test_bon_lenh_con_deu_co_that_trong_bang_lenh(self):
        self.assertEqual(sorted(tdq_eval.LENH),
                         ["report", "run", "score", "setup"])

    def test_thieu_lenh_con_thi_exit_2_chu_khong_lam_gi(self):
        rc, _out, err = chay()
        self.assertEqual(rc, 2)
        self.assertIn("Missing sub-command", err)

    def test_log_bat_mac_dinh_co_timestamp(self):
        proc = subprocess.run(
            [sys.executable, EVAL, "bao-cao", "--dem"], capture_output=True,
            text=True, timeout=60,
            env={k: v for k, v in os.environ.items()
                 if k not in ("TDQ_EVAL_LOG", "TDQ_LOG")})
        self.assertRegex(proc.stderr, r"\[\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\]")

    def test_log_tat_duoc_bang_bien_moi_truong(self):
        proc = subprocess.run(
            [sys.executable, EVAL, "bao-cao", "--dem"], capture_output=True,
            text=True, timeout=60,
            env=dict(os.environ, TDQ_EVAL_LOG="0"))
        self.assertNotRegex(proc.stderr, r"\[\d{4}-\d{2}-\d{2}T")

    def test_log_co_muc_log(self):
        """Mỗi dòng log mang một mức đọc được, không phải văn xuôi trần."""
        dong = tdq_eval.dong_log("canh-bao", "thử")
        self.assertIn("canh-bao", dong)
        self.assertIn("thử", dong)
        self.assertRegex(dong, r"^\[\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\]")

    def test_muc_log_la_bang_dong_khong_phai_chuoi_tuy_y(self):
        with self.assertRaises(ValueError):
            tdq_eval.dong_log("muc-khong-co-that", "thử")


class DungNhanhTest(unittest.TestCase):
    """T1.3 — dựng hai worktree trong thư mục tạm, và chặn khi bị gọi vào repo thật."""

    def test_hai_nhanh_khai_dung_hai_commit_can_so(self):
        self.assertEqual(sorted(tdq_eval.NHANH), ["lai", "viet"])
        self.assertTrue(tdq_eval.NHANH["viet"].startswith("ea0cdbd"))
        self.assertTrue(tdq_eval.NHANH["lai"].startswith("f620094"))

    def test_dich_nam_trong_repo_nay_thi_bi_tu_choi(self):
        rc, _out, err = chay("dung-nhanh", "--dich", os.path.join(ROOT, "tmp-eval"))
        self.assertEqual(rc, 1)
        self.assertIn("inside this repo", err)
        self.assertFalse(os.path.exists(os.path.join(ROOT, "tmp-eval")))

    def test_dung_hai_worktree_co_du_plugin_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            dich = os.path.join(tmp, "nhanh")
            rc, out, err = chay("dung-nhanh", "--dich", dich)
            self.assertEqual(rc, 0, err)
            try:
                for ten in ("viet", "lai"):
                    manifest = os.path.join(dich, ten, ".claude-plugin", "plugin.json")
                    self.assertTrue(os.path.exists(manifest), f"thiếu {manifest}")
                    self.assertIn(ten, out)
            finally:
                for ten in ("viet", "lai"):
                    subprocess.run(["git", "-C", ROOT, "worktree", "remove", "--force",
                                    os.path.join(dich, ten)], capture_output=True)
                subprocess.run(["git", "-C", ROOT, "worktree", "prune"], capture_output=True)

    def test_hai_worktree_dung_ngon_ngu_khac_nhau_o_skill(self):
        """Bằng chứng hai nhánh thật sự khác nhau: câu luật Red-green ở hai thứ tiếng."""
        with tempfile.TemporaryDirectory() as tmp:
            dich = os.path.join(tmp, "nhanh")
            rc, _out, err = chay("dung-nhanh", "--dich", dich)
            self.assertEqual(rc, 0, err)
            try:
                doc = {}
                for ten in ("viet", "lai"):
                    with open(os.path.join(dich, ten, "skills", "tdq-build", "SKILL.md"),
                              encoding="utf-8") as f:
                        doc[ten] = f.read()
                self.assertIn("Mỗi task: chạy/viết check trước", doc["viet"])
                self.assertNotIn("Mỗi task: chạy/viết check trước", doc["lai"])
            finally:
                for ten in ("viet", "lai"):
                    subprocess.run(["git", "-C", ROOT, "worktree", "remove", "--force",
                                    os.path.join(dich, ten)], capture_output=True)
                subprocess.run(["git", "-C", ROOT, "worktree", "prune"], capture_output=True)


class BoCaTest(unittest.TestCase):
    """T2.1 — bộ ca đủ độ phủ và khai đúng."""

    def setUp(self):
        self.bo_ca = tdq_eval.doc_bo_ca()

    def test_co_dung_12_ca(self):
        self.assertEqual(len(self.bo_ca), 12)

    def test_moi_ca_cham_it_nhat_3_ma_luat(self):
        for ca in self.bo_ca:
            self.assertGreaterEqual(len(ca["kiem"]), 3, ca["ma"])

    def test_tong_phep_kiem_it_nhat_30(self):
        tong = sum(len(ca["kiem"]) for ca in self.bo_ca)
        self.assertGreaterEqual(tong, 30)

    def test_moi_ca_co_prompt_tieng_viet_va_mo_ta(self):
        for ca in self.bo_ca:
            self.assertTrue(ca["prompt"].strip(), ca["ma"])
            self.assertTrue(ca["mo_ta"].strip(), ca["ma"])
            if ca.get("ngon_ngu_trung_tinh"):
                continue
            self.assertRegex(ca["prompt"], r"[àáâãèéêìíòóôõùúýăđĩũơưạảấầẩẫậắằẳẵặẹẻẽềếể"
                                            r"ễệỉịọỏốồổỗộớờởỡợụủứừửữựỳỵỷỹ]")

    def test_ma_ca_khong_trung_nhau(self):
        ma = [ca["ma"] for ca in self.bo_ca]
        self.assertEqual(len(ma), len(set(ma)))

    def test_ca_khong_o_phase_idle_thi_phai_co_lenh_init_state(self):
        for ca in self.bo_ca:
            if ca["phase_dau"] != "idle":
                self.assertTrue(ca["state_lenh"], ca["ma"])
                self.assertEqual(ca["state_lenh"][0][0], "init", ca["ma"])


MAU_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mau_transcript")


class MauTranscriptTest(unittest.TestCase):
    """T2.2 — mọi mã luật đem đo đều có mẫu ĐẠT và mẫu VI PHẠM."""

    def setUp(self):
        self.ma_dem_do = sorted({ma for ca in tdq_eval.doc_bo_ca() for ma in ca["kiem"]})

    def test_moi_ma_co_du_hai_chieu_mau(self):
        for ma in self.ma_dem_do:
            for chieu in ("dat", "vi-pham"):
                duong_dan = os.path.join(MAU_DIR, f"{ma}__{chieu}.jsonl")
                self.assertTrue(os.path.exists(duong_dan), f"thiếu mẫu {ma} chiều {chieu}")

    def test_mau_doc_duoc_va_khong_rong(self):
        for ten in sorted(os.listdir(MAU_DIR)):
            su_kien = tdq_eval.doc_transcript(os.path.join(MAU_DIR, ten))
            self.assertTrue(su_kien, ten)

    def test_moi_mau_ket_thuc_bang_su_kien_result(self):
        for ten in sorted(os.listdir(MAU_DIR)):
            su_kien = tdq_eval.doc_transcript(os.path.join(MAU_DIR, ten))
            self.assertEqual(su_kien[-1]["type"], "result", ten)


class BoChamTest(unittest.TestCase):
    """T2.3 — mỗi phép kiểm phải ĐỎ trên mẫu vi phạm và XANH trên mẫu đạt."""

    def cham_mau(self, ma, chieu):
        su_kien = tdq_eval.doc_transcript(os.path.join(MAU_DIR, f"{ma}__{chieu}.jsonl"))
        return tdq_eval.cham_mot_ma(ma, tdq_eval.phan_tich(su_kien))

    def test_moi_ma_deu_co_ham_kiem(self):
        for ca in tdq_eval.doc_bo_ca():
            for ma in ca["kiem"]:
                self.assertIn(ma, tdq_eval.BO_CHAM, f"{ma} chưa có hàm kiểm")

    def test_mau_dat_cham_ra_dat(self):
        for ma in sorted(tdq_eval.BO_CHAM):
            self.assertEqual(self.cham_mau(ma, "dat"), "dat", f"{ma} mẫu đạt bị chấm sai")

    def test_mau_vi_pham_cham_ra_vi_pham(self):
        for ma in sorted(tdq_eval.BO_CHAM):
            self.assertEqual(self.cham_mau(ma, "vi-pham"), "vi-pham",
                             f"{ma} mẫu vi phạm lọt lưới")

    def test_ket_qua_chi_nhan_ba_gia_tri(self):
        self.assertEqual(sorted(tdq_eval.KET_QUA), ["dat", "khong-ap-dung", "vi-pham"])

    def test_khong_co_dau_vet_thi_tra_khong_ap_dung_chu_khong_tra_dat(self):
        """Phép kiểm không có gì để soi phải nói thẳng là không áp dụng."""
        rong = tdq_eval.phan_tich([{"type": "result", "subtype": "success",
                                    "result": "chưa làm gì", "total_cost_usd": 0.0}])
        for ma in ("L002", "L005", "L149", "L003", "L013", "L145", "L012"):
            self.assertEqual(tdq_eval.cham_mot_ma(ma, rong), "khong-ap-dung", ma)

    def test_phan_tich_ghep_dung_ket_qua_vao_tung_tool_call(self):
        su_kien = tdq_eval.doc_transcript(os.path.join(MAU_DIR, "L005__dat.jsonl"))
        ph = tdq_eval.phan_tich(su_kien)
        chay_test = [g for g in ph["goi"] if g["ten"] == "Bash" and "pytest" in g["lenh"]]
        self.assertEqual(len(chay_test), 2)
        self.assertTrue(chay_test[0]["loi"])
        self.assertFalse(chay_test[1]["loi"])

    def test_van_ban_cuoi_lay_tu_su_kien_result(self):
        su_kien = tdq_eval.doc_transcript(os.path.join(MAU_DIR, "L010__dat.jsonl"))
        ph = tdq_eval.phan_tich(su_kien)
        self.assertIn("cách nào", ph["van_ban_cuoi"])
        self.assertGreater(ph["chi_phi"], 0)


class LenhChamTest(unittest.TestCase):
    """T2.4 — lệnh `cham` gom kết quả một phiên thành bản ghi JSON."""

    def test_cham_transcript_mau_ra_ban_ghi_dung(self):
        with tempfile.TemporaryDirectory() as tmp:
            rc, out, err = chay("cham", "--transcript",
                                os.path.join(MAU_DIR, "L005__dat.jsonl"),
                                "--ca", "red-green", "--nhanh", "viet", "--lan", "1",
                                "--ra", tmp)
            self.assertEqual(rc, 0, err)
            ban_ghi = tdq_eval.doc_ban_ghi(tmp)
            self.assertEqual(len(ban_ghi), 1)
            b = ban_ghi[0]
            self.assertEqual(b["ca"], "red-green")
            self.assertEqual(b["nhanh"], "viet")
            self.assertEqual(b["lan"], 1)
            self.assertEqual(b["trang_thai"], "xong")
            self.assertEqual(b["ket_qua"]["L005"], "dat")
            khai = next(c for c in tdq_eval.doc_bo_ca() if c["ma"] == "red-green")
            self.assertEqual(sorted(b["ket_qua"]), sorted(khai["kiem"]))
            self.assertIn("red-green", out)

    def test_cham_ca_khong_co_that_thi_loi_chu_khong_doan(self):
        rc, _out, err = chay("cham", "--transcript",
                             os.path.join(MAU_DIR, "L005__dat.jsonl"),
                             "--ca", "ca-khong-ton-tai", "--nhanh", "viet", "--lan", "1")
        self.assertEqual(rc, 1)
        self.assertIn("ca-khong-ton-tai", err)

    def test_ban_ghi_giu_chi_phi_va_duong_dan_transcript(self):
        with tempfile.TemporaryDirectory() as tmp:
            chay("cham", "--transcript", os.path.join(MAU_DIR, "L005__dat.jsonl"),
                 "--ca", "red-green", "--nhanh", "lai", "--lan", "2", "--ra", tmp)
            b = tdq_eval.doc_ban_ghi(tmp)[0]
            self.assertGreater(b["chi_phi"], 0)
            self.assertTrue(b["transcript"].endswith("L005__dat.jsonl"))


class DungSandboxTest(unittest.TestCase):
    """T3.1 — sandbox của một phiên đo: seed, git riêng, state dựng sẵn."""

    def test_sandbox_co_seed_chung_seed_rieng_va_git(self):
        ca = dict(tdq_eval.tim_ca("duyet-plan-kem-mode"))
        with tempfile.TemporaryDirectory() as tmp:
            hop = tdq_eval.dung_sandbox(ca, os.path.join(tmp, "phien"), ROOT)
            self.assertTrue(os.path.exists(os.path.join(hop, "src", "tien_ich.py")))
            self.assertTrue(os.path.exists(os.path.join(
                hop, "docs", "tdq", "plan", ca["slug"] + ".md")))
            self.assertTrue(os.path.isdir(os.path.join(hop, ".git")))

    def test_sandbox_chay_xong_state_lenh_dung_phase_dau(self):
        ca = dict(tdq_eval.tim_ca("duyet-plan-kem-mode"))
        with tempfile.TemporaryDirectory() as tmp:
            hop = tdq_eval.dung_sandbox(ca, os.path.join(tmp, "phien"), ROOT)
            with open(os.path.join(hop, "docs", "tdq", "state.json"), encoding="utf-8") as f:
                state = json.load(f)
            self.assertEqual(state["active_request"], ca["slug"])
            self.assertEqual(state["phase"], ca["phase_dau"])
            self.assertTrue(state.get("spec_approved"))

    def test_sandbox_trong_repo_bi_chan(self):
        ca = tdq_eval.tim_ca("duyet-plan-kem-mode")
        with self.assertRaises(tdq_eval.LoiThieuSo):
            tdq_eval.dung_sandbox(ca, os.path.join(ROOT, "phien-thu"), ROOT)


class LenhPhienTest(unittest.TestCase):
    """T3.1 — câu lệnh và môi trường của một phiên: cách ly cấu hình, không lộ token."""

    def test_lenh_du_co_bat_buoc(self):
        lenh = tdq_eval.dung_lenh("duyệt plan", "/tmp/wt/viet")
        self.assertEqual(lenh[0], "claude")
        self.assertIn("--plugin-dir", lenh)
        self.assertEqual(lenh[lenh.index("--plugin-dir") + 1], "/tmp/wt/viet")
        self.assertIn("duyệt plan", lenh)
        for co in ("--model", "--output-format", "--permission-mode"):
            self.assertIn(co, lenh)
        self.assertEqual(lenh[lenh.index("--output-format") + 1], "stream-json")

    def test_moi_truong_cach_ly_cau_hinh_va_khong_dinh_plugin_toan_may(self):
        moi = tdq_eval.dung_moi_truong("/tmp/phien/cfg", "/tmp/phien/hop", "TOKEN-GIA")
        self.assertEqual(moi["CLAUDE_CONFIG_DIR"], "/tmp/phien/cfg")
        self.assertEqual(moi["CLAUDE_CODE_OAUTH_TOKEN"], "TOKEN-GIA")
        self.assertEqual(moi["TDQ_PROJECT_DIR"], "/tmp/phien/hop")

    def test_khong_dong_log_nao_chua_token(self):
        moi = tdq_eval.dung_moi_truong("/tmp/phien/cfg", "/tmp/phien/hop", "TOKEN-GIA")
        dong = tdq_eval.dong_log("thong-tin", tdq_eval.tom_tat_phien(
            "duyet-plan-kem-mode", "viet", 1, moi))
        self.assertNotIn("TOKEN-GIA", dong)
        self.assertIn("duyet-plan-kem-mode", dong)


def sang_bash(duong_dan):
    """Chuyển mọi lời gọi Write/Edit trong một mẫu thành lệnh Bash tương đương.

    Agent thật hay sửa file bằng heredoc chứ không bằng tool Edit. Cùng một hành vi,
    hai hình thức — bộ chấm phải cho cùng một kết quả, nếu không thì số đo phụ thuộc
    thói quen gõ lệnh chứ không phụ thuộc bộ skill.
    """
    su_kien = []
    for dong in open(duong_dan, encoding="utf-8"):
        if not dong.strip():
            continue
        e = json.loads(dong)
        if e.get("type") == "assistant":
            khoi_moi = []
            for b in e["message"].get("content", []):
                if b.get("type") == "tool_use" and b["name"] in ("Write", "Edit"):
                    inp = b["input"]
                    duong = inp["file_path"]
                    if b["name"] == "Edit":
                        lenh = ("python3 - <<'EOF'\n"
                                f'p = "{duong}"\n'
                                's = open(p, encoding="utf-8").read()\n'
                                f's = s.replace("{inp["old_string"]}", "{inp["new_string"]}")\n'
                                'open(p, "w", encoding="utf-8").write(s)\nEOF')
                    else:
                        lenh = f"cat > {duong} <<'EOF'\n{inp.get('content', '')}\nEOF"
                    b = {"type": "tool_use", "id": b["id"], "name": "Bash",
                         "input": {"command": lenh}}
                khoi_moi.append(b)
            e = {"type": "assistant", "message": {"content": khoi_moi}}
        su_kien.append(e)
    return su_kien


class BatBienHinhThucTest(unittest.TestCase):
    """T3.1 — cùng hành vi, khác hình thức gõ lệnh, bộ chấm phải ra cùng kết quả."""

    def test_moi_ma_cho_cung_ket_qua_khi_sua_file_bang_bash(self):
        for ma in sorted(tdq_eval.BO_CHAM):
            for nhan in ("dat", "vi-pham"):
                mau = os.path.join(MAU_DIR, f"{ma}__{nhan}.jsonl")
                with self.subTest(ma=ma, nhan=nhan):
                    goc = tdq_eval.cham_mot_ma(
                        ma, tdq_eval.phan_tich(tdq_eval.doc_transcript(mau)))
                    qua_bash = tdq_eval.cham_mot_ma(
                        ma, tdq_eval.phan_tich(sang_bash(mau)))
                    self.assertEqual(goc, qua_bash)


class DauVetThatTest(unittest.TestCase):
    """T3.1 — các dạng lệnh lấy từ phiên thật đầu tiên, không phải dạng tự nghĩ ra."""

    def test_approve_co_dau_nhay_quanh_duong_dan_van_tinh(self):
        lenh = ('CLAUDE_PLUGIN_ROOT=/tmp/wt python3 "/tmp/wt/scripts/tdq_state.py" '
                'approve plan --mode main --by "duyệt plan, làm trực tiếp đi"')
        self.assertTrue(tdq_eval.RE_APPROVE.search(lenh))

    def test_mot_lenh_hai_heredoc_dung_chung_bien_thi_ghi_ca_hai_file(self):
        lenh = ("python3 - <<'EOF'\n"
                'p = "docs/tdq/plan/2026-08-19-0900-them-lenh-xoa-cache.md"\n'
                's = open(p, encoding="utf-8").read()\n'
                'open(p, "w", encoding="utf-8").write(s)\n'
                "EOF\n"
                "python3 - <<'PYEOF'\n"
                'p = "tests/test_tien_ich.py"\n'
                'open(p, "w", encoding="utf-8").write("x")\n'
                "PYEOF")
        duong = tdq_eval._duong_dan_ghi_bash(lenh)
        self.assertIn("docs/tdq/plan/2026-08-19-0900-them-lenh-xoa-cache.md", duong)
        self.assertIn("tests/test_tien_ich.py", duong)

    def test_full_suite_dung_mot_lan_thi_dat_hai_lan_thi_vi_pham(self):
        def ph(lenh_test):
            goi = [{"ten": "Bash", "lenh": l, "file": "", "ket_qua": "3 passed",
                    "loi": False, "input": {"command": l}} for l in lenh_test]
            return {"goi": goi, "van_ban_cuoi": "", "chi_phi": 0.0, "so_luot": 1}
        mot_lan = ["python3 -m pytest tests/test_tien_ich.py -q",
                   "python3 -m pytest tests/ -q"]
        hai_lan = ["python3 -m pytest tests/ -q", "python3 -m pytest tests/ -q"]
        self.assertEqual(tdq_eval.kiem_L012(ph(mot_lan)), "dat")
        self.assertEqual(tdq_eval.kiem_L012(ph(hai_lan)), "vi-pham")


class TranChiPhiTest(unittest.TestCase):
    """T3.2 — trần chi phí, chạy tiếp và chạy lại phiên hỏng. Không phiên thật nào chạy."""

    def viec(self):
        return tdq_eval.viec_con_lai(["ca-a", "ca-b"], ["viet", "lai"], 2, {})

    def test_liet_ke_du_viec_theo_ca_nhanh_lan(self):
        self.assertEqual(len(self.viec()), 8)
        self.assertIn(("ca-a", "viet", 1), self.viec())

    def test_bo_qua_viec_da_co_ban_ghi_xong(self):
        da_co = {("ca-a", "viet", 1): "xong", ("ca-a", "viet", 2): "xong"}
        con = tdq_eval.viec_con_lai(["ca-a", "ca-b"], ["viet", "lai"], 2, da_co)
        self.assertEqual(len(con), 6)
        self.assertNotIn(("ca-a", "viet", 1), con)

    def test_ban_ghi_loi_van_phai_chay_lai(self):
        da_co = {("ca-a", "viet", 1): "loi"}
        con = tdq_eval.viec_con_lai(["ca-a"], ["viet"], 1, da_co)
        self.assertEqual(con, [("ca-a", "viet", 1)])

    def test_vuot_tran_thi_dung_va_khong_goi_them_phien_nao(self):
        goi = []

        def chay_gia(ca, nhanh, lan):
            goi.append((ca["ma"], nhanh, lan))
            return {"trang_thai": "xong", "chi_phi": 2.0, "ket_qua": {}}

        bo_ca = [tdq_eval.tim_ca("red-green")]
        tong, dung_som = tdq_eval.chay_bo(bo_ca, ["viet"], 5, chay_gia, tran_usd=3.0)
        self.assertTrue(dung_som)
        self.assertEqual(len(goi), 2)
        self.assertAlmostEqual(tong, 4.0)

    def test_phien_hong_duoc_chay_lai_dung_mot_lan(self):
        goi = []

        def chay_gia(ca, nhanh, lan):
            goi.append((ca["ma"], nhanh, lan))
            return {"trang_thai": "loi", "chi_phi": 0.0, "ket_qua": {}}

        bo_ca = [tdq_eval.tim_ca("red-green")]
        _tong, dung_som = tdq_eval.chay_bo(bo_ca, ["viet"], 1, chay_gia, tran_usd=100.0)
        self.assertFalse(dung_som)
        self.assertEqual(len(goi), 2)

    def test_so_lan_chay_lai_duoc_ghi_vao_ban_ghi(self):
        """Chạy lại mà không ghi lại số lần thì vòng đo mất dấu: bản ghi cuối trông y hệt
        phiên chạy trơn tru ngay lần đầu."""
        lan_goi = []

        def chay_gia(ca, nhanh, lan):
            lan_goi.append(1)
            trang_thai = "loi" if len(lan_goi) == 1 else "xong"
            return {"trang_thai": trang_thai, "chi_phi": 0.1, "ket_qua": {}}

        da_ghi = []
        tdq_eval.chay_bo([tdq_eval.tim_ca("red-green")], ["viet"], 1, chay_gia,
                         tran_usd=100.0, ghi_lai=da_ghi.append)
        self.assertEqual(len(da_ghi), 1)
        self.assertEqual(da_ghi[0]["chay_lai"], 1)

    def test_dem_in_ca_so_lan_chay_lai(self):
        bg = [{"ca": "x", "nhanh": "viet", "lan": 1, "trang_thai": "xong",
               "ket_qua": {"L001": "dat"}, "chi_phi": 0.1, "so_luot": 2, "chay_lai": 2},
              {"ca": "x", "nhanh": "lai", "lan": 1, "trang_thai": "xong",
               "ket_qua": {"L001": "dat"}, "chi_phi": 0.1, "so_luot": 2}]
        bc = tdq_eval.bao_cao_so(bg)
        self.assertEqual(bc["so_chay_lai"], 2)
        with tempfile.TemporaryDirectory() as tm:
            for i, b in enumerate(bg):
                with open(os.path.join(tm, f"b{i}.json"), "w", encoding="utf-8") as f:
                    json.dump(b, f)
            ra = io.StringIO()
            with contextlib.redirect_stdout(ra):
                tdq_eval.lenh_bao_cao(argparse.Namespace(
                    dem=True, phu=False, chi_phi=False, ghi=None, thu_muc=tm))
        self.assertIn("retries: 2", ra.getvalue())


class NhiemChatTest(unittest.TestCase):
    """T3.2 — phiên đọc phải bộ skill của nhánh KIA hay bản cài trên máy thì số đo hỏng."""

    def test_phien_sach_thi_khong_bao_nhiem(self):
        van_ban = "đọc /private/tmp/tdq-eval-nhanh/viet/skills/tdq-build/SKILL.md"
        self.assertEqual(tdq_eval.dau_nhiem(van_ban, "/private/tmp/tdq-eval-nhanh/viet"), [])

    def test_doc_nhanh_kia_thi_bao_nhiem(self):
        van_ban = "cat /private/tmp/tdq-eval-nhanh/lai/skills/tdq-build/SKILL.md"
        self.assertTrue(tdq_eval.dau_nhiem(van_ban, "/private/tmp/tdq-eval-nhanh/viet"))

    def test_doc_ban_cai_tren_may_thi_bao_nhiem(self):
        van_ban = "ls /Users/ai/.claude/plugins/cache/tdq-local/tdq-workflow/skills"
        self.assertTrue(tdq_eval.dau_nhiem(van_ban, "/private/tmp/tdq-eval-nhanh/viet"))

    def test_doc_chinh_repo_dang_do_thi_bao_nhiem(self):
        van_ban = f"sed -n 1,20p {ROOT}/skills/tdq-build/SKILL.md"
        self.assertTrue(tdq_eval.dau_nhiem(van_ban, "/private/tmp/tdq-eval-nhanh/viet"))


class DangLenhThatTest(unittest.TestCase):
    """T3.2 — ba dạng lệnh lấy từ hai phiên thật đầu tiên, từng làm bộ chấm đọc sai."""

    def test_pathlib_write_text_cung_tinh_la_ghi_file(self):
        lenh = ("python3 - <<'PY'\nimport pathlib\n"
                'p = pathlib.Path("docs/tdq/plan/2026-08-19-0900-them-lenh-xoa-cache.md")\n'
                's = p.read_text(encoding="utf-8")\n'
                'p.write_text(s.replace("- [~] **T1.1**", "- [x] **T1.1**"), encoding="utf-8")\nPY')
        self.assertIn("docs/tdq/plan/2026-08-19-0900-them-lenh-xoa-cache.md",
                      tdq_eval._duong_dan_ghi_bash(lenh))

    def test_pytest_version_khong_phai_mot_lan_chay_test(self):
        goi = [{"ten": "Bash", "lenh": "python3 -m pytest --version", "file": "",
                "ket_qua": "pytest 8.0", "loi": False, "input": {}}]
        ph = {"goi": goi, "van_ban_cuoi": "", "chi_phi": 0.0, "so_luot": 1}
        self.assertEqual(tdq_eval._chay_test(ph), [])
        self.assertEqual(tdq_eval.kiem_L012(ph), "khong-ap-dung")

    def test_duong_dan_la_trong_ket_qua_lenh_thi_khong_tinh_la_nhiem(self):
        goi = [{"ten": "Bash", "lenh": 'find / -name "tdq_state.py"', "file": "",
                "ket_qua": "/private/tmp/tdq-eval-nhanh/viet/scripts/tdq_state.py",
                "loi": False, "input": {"command": 'find / -name "tdq_state.py"'}}]
        ph = {"goi": goi, "van_ban_cuoi": "", "chi_phi": 0.0, "so_luot": 1}
        self.assertEqual(tdq_eval.dau_nhiem_phien(ph, "/private/tmp/tdq-eval-nhanh/lai"), [])

    def test_lenh_doc_nhanh_kia_thi_tinh_la_nhiem(self):
        lenh = "cat /private/tmp/tdq-eval-nhanh/viet/skills/tdq-build/SKILL.md"
        goi = [{"ten": "Bash", "lenh": lenh, "file": "", "ket_qua": "", "loi": False,
                "input": {"command": lenh}}]
        ph = {"goi": goi, "van_ban_cuoi": "", "chi_phi": 0.0, "so_luot": 1}
        self.assertTrue(tdq_eval.dau_nhiem_phien(ph, "/private/tmp/tdq-eval-nhanh/lai"))


def _bg(ca, nhanh, lan, ket_qua, chi_phi=0.5, trang_thai="xong"):
    return {"ca": ca, "nhanh": nhanh, "lan": lan, "trang_thai": trang_thai,
            "transcript": "", "ma_thoat": 0, "ket_qua": ket_qua,
            "chi_phi": chi_phi, "so_luot": 5, "nhiem": []}


def _bo_ba(ca, ma_ket_qua_viet, ma_ket_qua_lai):
    """Ba lần chạy mỗi nhánh cho một ca. Mỗi tham số là dict ma -> danh sách 3 phán quyết."""
    ban_ghi = []
    for nhanh, bang in (("viet", ma_ket_qua_viet), ("lai", ma_ket_qua_lai)):
        for lan in (1, 2, 3):
            ban_ghi.append(_bg(ca, nhanh, lan, {ma: pq[lan - 1] for ma, pq in bang.items()}))
    return ban_ghi


class KiemDinhDauTest(unittest.TestCase):
    """Kiểm định dấu chính xác một phía: p = P(X >= số cặp xấu), X ~ Nhị thức(n, 1/2)."""

    def test_gia_tri_p_tinh_tay(self):
        for so_xau, so_tot, mong in ((5, 0, 0.03125), (4, 0, 0.0625), (5, 1, 0.109375),
                                     (0, 0, 1.0), (3, 3, 0.65625), (10, 0, 0.0009765625)):
            with self.subTest(xau=so_xau, tot=so_tot):
                self.assertAlmostEqual(tdq_eval.kiem_dinh_dau(so_xau, so_tot), mong, places=4)

    def test_nam_cap_lech_deu_xau_thi_qua_nguong(self):
        self.assertLess(tdq_eval.kiem_dinh_dau(5, 0), 0.05)

    def test_bon_cap_lech_deu_xau_thi_chua_qua_nguong(self):
        self.assertGreater(tdq_eval.kiem_dinh_dau(4, 0), 0.05)


class BaoCaoSoTest(unittest.TestCase):
    """Bộ dữ liệu dựng sẵn, đáp án tính tay."""

    def _du_lieu_sut(self):
        ban_ghi = []
        for i in range(1, 6):
            ban_ghi += _bo_ba(f"ca{i}", {"L001": ["dat"] * 3}, {"L001": ["vi-pham"] * 3})
        ban_ghi += _bo_ba("ca6", {"L003": ["dat"] * 3}, {"L003": ["dat"] * 3})
        return ban_ghi

    def test_dem_cap_lech_va_p(self):
        bc = tdq_eval.bao_cao_so(self._du_lieu_sut())
        self.assertEqual(bc["so_don_vi"], 6)
        self.assertEqual(bc["cap_xau"], 5)
        self.assertEqual(bc["cap_tot"], 0)
        self.assertEqual(bc["cap_hoa"], 1)
        self.assertAlmostEqual(bc["p"], 0.03125, places=4)
        self.assertEqual(bc["ket_luan"], "sut")

    def test_sut_cung_liet_ke_dung_don_vi(self):
        bc = tdq_eval.bao_cao_so(self._du_lieu_sut())
        self.assertEqual(sorted(bc["sut_cung"]),
                         [(f"ca{i}", "L001") for i in range(1, 6)])

    def test_mot_cap_nghieng_tot_thi_khong_ket_luan_sut(self):
        ban_ghi = self._du_lieu_sut()
        ban_ghi += _bo_ba("ca7", {"L005": ["vi-pham", "vi-pham", "dat"]},
                          {"L005": ["dat"] * 3})
        bc = tdq_eval.bao_cao_so(ban_ghi)
        self.assertEqual((bc["cap_xau"], bc["cap_tot"]), (5, 1))
        self.assertAlmostEqual(bc["p"], 0.109375, places=4)
        self.assertEqual(bc["ket_luan"], "chua-du")

    def test_don_vi_thieu_lan_ap_dung_o_mot_nhanh_thi_bi_loai(self):
        ban_ghi = self._du_lieu_sut()
        ban_ghi += _bo_ba("ca8", {"L007": ["dat"] * 3}, {"L007": ["khong-ap-dung"] * 3})
        bc = tdq_eval.bao_cao_so(ban_ghi)
        self.assertEqual(bc["so_don_vi"], 6)
        self.assertIn(("ca8", "L007"), bc["bo_qua"])

    def test_ti_le_tung_ma_theo_nhanh(self):
        bc = tdq_eval.bao_cao_so(self._du_lieu_sut())
        self.assertEqual(bc["ti_le"]["L001"]["viet"], (15, 15))
        self.assertEqual(bc["ti_le"]["L001"]["lai"], (0, 15))

    def test_chi_phi_va_dem_lay_tu_ban_ghi_that(self):
        bc = tdq_eval.bao_cao_so(self._du_lieu_sut())
        self.assertEqual(bc["so_ban_ghi"], 36)
        self.assertEqual(bc["so_loi"], 0)
        self.assertAlmostEqual(bc["chi_phi"], 18.0, places=4)

    def test_ban_ghi_loi_khong_duoc_tinh_vao_phep_kiem(self):
        ban_ghi = self._du_lieu_sut()
        ban_ghi.append(_bg("ca9", "viet", 1, {}, trang_thai="loi"))
        bc = tdq_eval.bao_cao_so(ban_ghi)
        self.assertEqual(bc["so_loi"], 1)
        self.assertEqual(bc["so_don_vi"], 6)

    def test_do_phu_dem_so_ma_moi_ca(self):
        bc = tdq_eval.bao_cao_so(self._du_lieu_sut())
        self.assertEqual(bc["phu"]["ca1"], ["L001"])
        self.assertEqual(bc["phu"]["ca6"], ["L003"])


class CaBaoLoiTaiHienDuocTest(unittest.TestCase):
    """Ca `bao-loi` kể một lỗi thật; nếu seed không có lỗi thì hai mã L218/L220 chấm oan.

    Bằng chứng: phiên thật đầu tiên của ca này, agent chạy thử rồi kết luận `dem_tu` KHÔNG
    sai, nên dừng hỏi lại user theo issue-triage bước 2 — đúng luật, nhưng bộ chấm lại ghi
    vi-pham vì không có brief. Sửa gốc: cho seed của ca này một lỗi tái hiện được.
    """

    def test_seed_ca_bao_loi_co_loi_that_va_bo_test_van_xanh(self):
        goc = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        hop = tempfile.mkdtemp(prefix="tdq-eval-seed-")
        self.addCleanup(shutil.rmtree, hop, True)
        shutil.copytree(tdq_eval.SEED_CHUNG, hop, dirs_exist_ok=True)
        rieng = os.path.join(tdq_eval.CA_DIR, "bao-loi", "seed")
        self.assertTrue(os.path.isdir(rieng), "ca bao-loi phải có seed riêng mang lỗi")
        shutil.copytree(rieng, hop, dirs_exist_ok=True)

        sys.path.insert(0, os.path.join(hop, "src"))
        try:
            for ten in [m for m in list(sys.modules) if m == "tien_ich"]:
                del sys.modules[ten]
            import tien_ich
            self.assertNotEqual(tien_ich.dem_tu(""), 0,
                                "chuỗi rỗng phải ra sai thì mới có lỗi để báo")
            self.assertEqual(tien_ich.dem_tu("một hai ba"), 3, "ca thường vẫn phải đúng")
        finally:
            sys.path.pop(0)
            sys.modules.pop("tien_ich", None)

        ket_qua = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "tests"],
                                 cwd=hop, capture_output=True, text=True, timeout=60)
        self.assertEqual(ket_qua.returncode, 0,
                         "bộ test sẵn có phải xanh — lỗi nằm ở chỗ test chưa phủ")
        self.assertTrue(goc)


class GanMaDungCaTest(unittest.TestCase):
    """Gán nhầm mã cho ca thì bộ đo báo vi-pham oan, hai nhánh cùng oan như nhau.

    Bằng chứng: ca `duyet-spec` có prompt "duyệt spec" — câu duyệt RÕ RÀNG, chạy `approve`
    ở đây là ĐÚNG luật (L149 còn bắt buộc có `--by`). Nhưng L136 chấm vi-pham cho mọi lần
    chạy `approve`, nên cả hai nhánh đều 0/3 ở mã này. L136 chỉ đo được trên ca mơ hồ.
    """

    RE_DUYET_RO = re.compile(r"duyệt\s+(spec|plan)", re.IGNORECASE)

    def test_ca_co_cau_duyet_ro_thi_khong_duoc_do_L136(self):
        for ca in tdq_eval.doc_bo_ca():
            if self.RE_DUYET_RO.search(ca["prompt"]):
                with self.subTest(ca=ca["ma"]):
                    self.assertNotIn("L136", ca["kiem"],
                                     f"ca {ca['ma']} có câu duyệt rõ ràng, L136 chấm oan")

    def test_moi_ca_do_it_nhat_ba_ma(self):
        for ca in tdq_eval.doc_bo_ca():
            with self.subTest(ca=ca["ma"]):
                self.assertGreaterEqual(len(ca["kiem"]), 3)


class L275Test(unittest.TestCase):
    """Duyệt spec xong là viết plan NGAY cùng turn (luật L275, `skills/tdq-plan/SKILL.md:10`)."""

    def _cham(self, ten):
        ph = tdq_eval.phan_tich(tdq_eval.doc_transcript(
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "mau_transcript", ten)))
        return tdq_eval.kiem_L275(ph)

    def test_viet_plan_cung_turn_thi_dat(self):
        self.assertEqual(self._cham("L275__dat.jsonl"), "dat")

    def test_duyet_xong_bat_user_nhan_them_thi_vi_pham(self):
        self.assertEqual(self._cham("L275__vi-pham.jsonl"), "vi-pham")

    def test_khong_duyet_spec_thi_khong_ap_dung(self):
        ph = {"goi": [], "van_ban_cuoi": "", "chi_phi": 0.0, "so_luot": 1}
        self.assertEqual(tdq_eval.kiem_L275(ph), "khong-ap-dung")

    def test_duyet_plan_khong_keo_theo_luat_nay(self):
        lenh = 'python3 tdq_state.py approve plan --by "duyệt plan"'
        goi = [{"ten": "Bash", "lenh": lenh, "file": "", "ket_qua": "", "loi": False,
                "input": {"command": lenh}}]
        ph = {"goi": goi, "van_ban_cuoi": "", "chi_phi": 0.0, "so_luot": 1}
        self.assertEqual(tdq_eval.kiem_L275(ph), "khong-ap-dung")


class SedGhiFileTest(unittest.TestCase):
    r"""`sed -i` dùng `|` làm dấu phân cách thì regex cũ đứt ngay ở đó nên mất đường dẫn.

    Bằng chứng: phiên thật `build-tick-tung-task__lai__1` tick đủ ba task bằng
    `sed -i '' -e 's|^- \[~\] ...|- [x] ...|' docs/tdq/plan/....md`, file trong hộp cát có
    đúng ba dòng `[x]`, mà bộ chấm ghi L003/L013/L145 = khong-ap-dung.
    """

    def _ghi(self, lenh):
        return tdq_eval._duong_dan_ghi_bash(lenh)

    def test_sed_i_dung_gach_dung_lam_dau_phan_cach(self):
        lenh = ("sed -i '' -e 's|^- \\[~\\] \\*\\*T1.1\\*\\*|- [x] **T1.1**|' "
                "docs/tdq/plan/2026-08-19-0900-them-lenh-xoa-cache.md")
        self.assertIn("docs/tdq/plan/2026-08-19-0900-them-lenh-xoa-cache.md", self._ghi(lenh))

    def test_sed_i_khong_co_e_van_lay_duoc_file(self):
        self.assertIn("f.md", self._ghi("sed -i '' 's|a|b|' f.md && grep -n x f.md"))

    def test_sed_i_hau_to_dinh_lien(self):
        self.assertIn("f.md", self._ghi("sed -i.bak 's/a/b/' f.md"))

    def test_sed_nhieu_file(self):
        ra = self._ghi("sed -i '' -e 's|a|b|' -e 's|c|d|' a.md b.md")
        self.assertIn("a.md", ra)
        self.assertIn("b.md", ra)

    def test_sed_khong_co_i_thi_khong_phai_ghi(self):
        self.assertNotIn("f.md", self._ghi("sed -n 's/a/b/p' f.md"))

    def test_tick_bang_sed_van_dem_duoc_chuyen_trang_thai(self):
        lenh1 = "sed -i '' 's|^- \\[ \\] \\*\\*T1.1\\*\\*|- [~] **T1.1**|' docs/tdq/plan/p.md"
        lenh2 = "sed -i '' 's|^- \\[~\\] \\*\\*T1.1\\*\\*|- [x] **T1.1**|' docs/tdq/plan/p.md"
        goi = []
        for i, (lenh, sau) in enumerate(((lenh1, "- [~] **T1.1** việc"),
                                         (lenh2, "- [x] **T1.1** việc"))):
            goi.append({"ten": "Bash", "lenh": lenh, "file": "", "ket_qua": sau,
                        "loi": False, "input": {"command": lenh}})
        ph = {"goi": goi, "van_ban_cuoi": "", "chi_phi": 0.0, "so_luot": 2}
        self.assertTrue(tdq_eval._viet(ph), "phải thấy lần ghi vào file plan")


class ChamLaiTatCaTest(unittest.TestCase):
    """Sửa giám khảo giữa vòng chạy thì bản ghi cũ mang phán quyết cũ — phải chấm lại được.

    Vòng chạy 60 phiên kéo dài hàng giờ; mỗi lần bắt được lỗi bộ chấm mà phải chạy lại
    phiên thật là đốt tiền vô ích. Transcript đã lưu nên chấm lại là việc thuần tất định.
    """

    def test_cham_lai_ghi_de_phan_quyet_cu_bang_bo_cham_hien_hanh(self):
        thu_muc = tempfile.mkdtemp(prefix="tdq-eval-cham-lai-")
        self.addCleanup(shutil.rmtree, thu_muc, True)
        goc = os.path.dirname(os.path.abspath(__file__))
        transcript = os.path.join(goc, "mau_transcript", "L218__dat.jsonl")
        ban_ghi = {"ca": "mo-request-moi", "nhanh": "viet", "lan": 1, "trang_thai": "xong",
                   "transcript": transcript, "ma_thoat": 0,
                   "ket_qua": {"L218": "vi-pham", "L220": "vi-pham", "L136": "vi-pham"},
                   "chi_phi": 0.4, "so_luot": 6, "nhiem": []}
        duong = os.path.join(thu_muc, "mo-request-moi__viet__1.json")
        with open(duong, "w", encoding="utf-8") as f:
            json.dump(ban_ghi, f, ensure_ascii=False)

        rc, out, _err = chay("cham", "--tat-ca", "--ra", thu_muc)
        self.assertEqual(rc, 0, out)
        with open(duong, encoding="utf-8") as f:
            moi = json.load(f)
        self.assertEqual(moi["ket_qua"]["L218"], "dat")
        self.assertEqual(moi["chi_phi"], 0.4, "chấm lại không được đổi số đo chi phí")

    def test_cham_lai_bo_qua_ban_ghi_khong_con_transcript(self):
        thu_muc = tempfile.mkdtemp(prefix="tdq-eval-cham-lai-")
        self.addCleanup(shutil.rmtree, thu_muc, True)
        ban_ghi = {"ca": "mo-request-moi", "nhanh": "viet", "lan": 2, "trang_thai": "loi",
                   "transcript": os.path.join(thu_muc, "khong-co.jsonl"), "ma_thoat": 1,
                   "ket_qua": {}, "chi_phi": 0.0, "so_luot": 0, "nhiem": []}
        with open(os.path.join(thu_muc, "mo-request-moi__viet__2.json"), "w",
                  encoding="utf-8") as f:
            json.dump(ban_ghi, f, ensure_ascii=False)
        rc, out, _err = chay("cham", "--tat-ca", "--ra", thu_muc)
        self.assertEqual(rc, 0, out)
        self.assertIn("skipped", out)


class VietAuditTest(unittest.TestCase):
    """File audit phải SINH RA từ bản ghi, không gõ tay số nào."""

    def _du_lieu(self):
        ban_ghi = []
        for i in range(1, 4):
            ban_ghi += _bo_ba(f"ca{i}", {"L001": ["dat"] * 3}, {"L001": ["vi-pham"] * 3})
        ban_ghi += _bo_ba("ca4", {"L012": ["dat", "dat", "vi-pham"]},
                          {"L012": ["dat"] * 3})
        return ban_ghi

    def test_sinh_file_co_du_bang_so_p_va_do_nhay(self):
        bc = tdq_eval.bao_cao_so(self._du_lieu())
        van = tdq_eval.viet_audit(bc, ngay="2026-08-20")
        self.assertIn("| L001 | 9/9 | 0/9 |", van)
        self.assertIn("| L012 | 2/3 | 3/3 |", van)
        self.assertIn(f"p = {bc['p']:.4f}", van)
        self.assertIn("độ nhạy", van)
        self.assertIn("2026-08-20", van)

    def test_sinh_hai_lan_ra_y_het(self):
        bc = tdq_eval.bao_cao_so(self._du_lieu())
        self.assertEqual(tdq_eval.viet_audit(bc, ngay="2026-08-20"),
                         tdq_eval.viet_audit(bc, ngay="2026-08-20"))

    def test_moi_con_so_trong_file_deu_truy_nguoc_duoc_ve_ban_ghi(self):
        """Quét mọi số trong file; số nào không nằm trong tập số tính được là số gõ tay."""
        bc = tdq_eval.bao_cao_so(self._du_lieu())
        van = tdq_eval.viet_audit(bc, ngay="2026-08-20")
        cho_phep = {"2026", "08", "20", "3", "2", "0", "1", "05"}
        for bam in tdq_eval.NHANH.values():
            cho_phep |= set(re.findall(r"\d+", bam))
        for m in bc["theo_nhanh"].values():
            cho_phep |= {str(m["phien"]), f"{m['chi_phi']:.2f}", str(m["so_luot"])}
        for d in bc["don_vi"]:
            for n in (d["viet"], d["lai"]):
                cho_phep |= {str(n[0]), str(n[1])}
        for muc in bc["ti_le"].values():
            for n in muc.values():
                cho_phep |= {str(n[0]), str(n[1])}
        cho_phep |= {str(bc["so_ban_ghi"]), str(bc["so_loi"]), str(bc["so_don_vi"]),
                     str(bc["cap_xau"]), str(bc["cap_tot"]), str(bc["cap_hoa"]),
                     str(len(bc["bo_qua"])), str(len(bc["sut_cung"])),
                     f"{bc['p']:.4f}", f"{bc['chi_phi']:.2f}", str(tdq_eval.NGUONG_P)}
        cho_phep |= {ma[1:] for ma in bc["ti_le"]}
        # Mã luật in trong phần chữ (vd "L209") không phải số đo — bỏ phần số của nó ra,
        # nếu không cái tên mã lại bị bắt như số gõ tay.
        cho_phep |= {ma[1:] for ma in tdq_eval.MA_THEM_SAU}
        cho_phep.add(str(len(tdq_eval.MA_THEM_SAU)))
        for so in re.findall(r"\d+(?:[.,]\d+)?", van):
            with self.subTest(so=so):
                self.assertIn(so, cho_phep, f"số {so} không truy được về bản ghi")


class LuoiHoiQuyTest(unittest.TestCase):
    """Bộ ca ở lại trong repo làm lưới hồi quy — phải chạy lại được bằng một lệnh."""

    def _readme(self):
        duong = os.path.join(tdq_eval.CA_DIR, "README.md")
        self.assertTrue(os.path.exists(duong), "bộ ca phải có README")
        with open(duong, encoding="utf-8") as f:
            return f.read()

    def _lenh_mot_dong(self, van):
        for dong in van.split("\n"):
            dong = dong.strip()
            if dong.startswith("python3 scripts/tdq_eval.py run"):
                return dong
        self.fail("README phải có đúng dòng lệnh chạy lại")

    def test_lenh_chay_lai_trong_readme_parse_duoc(self):
        lenh = self._lenh_mot_dong(self._readme())
        args = tdq_eval.build_parser().parse_args(shlex.split(lenh)[2:])
        self.assertEqual(args.lenh, "run")
        self.assertIn(args.nhanh, sorted(tdq_eval.NHANH) + ["ca-hai"])
        self.assertTrue(args.ca or args.lan, "lệnh chạy lại phải nêu ca hoặc số lần")

    def test_readme_neu_du_ma_ca_dang_co(self):
        van = self._readme()
        for ca in tdq_eval.doc_bo_ca():
            with self.subTest(ca=ca["ma"]):
                self.assertIn(ca["ma"], van)

    def test_file_le_canh_bo_ca_khong_bi_coi_la_ca(self):
        """README nằm cùng thư mục với bộ ca — đọc bộ ca không được vấp phải nó."""
        ma = [c["ma"] for c in tdq_eval.doc_bo_ca()]
        self.assertNotIn("README.md", ma)
        self.assertIn("duyet-spec", ma)

    def test_readme_neu_lenh_cham_lai(self):
        self.assertIn("score --tat-ca", self._readme())


class ApDungTheoPhaseTest(unittest.TestCase):
    """Luật chỉ áp khi bối cảnh của ca cho phép — nếu không, giám khảo chấm oan cả hai nhánh.

    Bằng chứng: L218 (yêu cầu mới → mở brief) bị gán cho ca `duyet-spec-mo-ho` chạy ở phase
    `spec`. Ở đó KHÔNG có yêu cầu mới nào, mở brief mới là sai, nhưng giám khảo cứ thiếu
    brief là ghi vi-pham — nên mã này 0/n ở CẢ HAI nhánh, không nói được điều gì.
    """

    def _ph(self, ca=None, van_ban=""):
        ph = {"goi": [], "van_ban_cuoi": van_ban, "chi_phi": 0.0, "so_luot": 1}
        if ca is not None:
            ph["ca"] = ca
        return ph

    def test_L218_khong_ap_dung_khi_ca_khong_bat_dau_o_idle(self):
        ph = self._ph({"ma": "duyet-spec-mo-ho", "phase_dau": "spec", "prompt": "ok"})
        self.assertEqual(tdq_eval.kiem_L218(ph), "khong-ap-dung")

    def test_L218_van_ap_dung_khi_ca_bat_dau_o_idle(self):
        ph = self._ph({"ma": "mo-request-moi", "phase_dau": "idle", "prompt": "thêm lệnh"})
        self.assertEqual(tdq_eval.kiem_L218(ph), "vi-pham")

    def test_L220_khong_ap_dung_khi_ca_khong_bat_dau_o_idle(self):
        ph = self._ph({"ma": "duyet-spec-mo-ho", "phase_dau": "spec", "prompt": "ok"})
        self.assertEqual(tdq_eval.kiem_L220(ph), "khong-ap-dung")

    def test_L136_khong_ap_dung_khi_prompt_la_cau_duyet_ro_rang(self):
        ph = self._ph({"ma": "duyet-spec", "phase_dau": "spec", "prompt": "duyệt spec"})
        self.assertEqual(tdq_eval.kiem_L136(ph), "khong-ap-dung")

    def test_L136_van_ap_dung_khi_prompt_mo_ho(self):
        ph = self._ph({"ma": "duyet-spec-mo-ho", "phase_dau": "spec", "prompt": "ok"})
        self.assertEqual(tdq_eval.kiem_L136(ph), "dat")

    def test_cham_phien_gan_ca_vao_phien_de_giam_khao_biet_boi_canh(self):
        goc = os.path.dirname(os.path.abspath(__file__))
        ca = {"ma": "duyet-spec-mo-ho", "phase_dau": "spec", "prompt": "ok",
              "kiem": ["L218"]}
        ket = tdq_eval.cham_phien(ca, os.path.join(goc, "mau_transcript", "L218__vi-pham.jsonl"))
        self.assertEqual(ket["ket_qua"]["L218"], "khong-ap-dung")


class CoBaoCaoGhepTest(unittest.TestCase):
    """Nhiều cờ trên cùng một lệnh `bao-cao` phải in đủ từng mục, không nuốt lặng mục sau."""

    def _chay(self, *co):
        thu_muc = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, thu_muc, True)
        for nhanh in ("viet", "lai"):
            with open(os.path.join(thu_muc, f"x__{nhanh}__1.json"), "w", encoding="utf-8") as f:
                json.dump({"ca": "x", "nhanh": nhanh, "lan": 1, "trang_thai": "xong",
                           "ket_qua": {"L001": "dat"}, "chi_phi": 0.5, "so_luot": 3,
                           "transcript": "/khong/co"}, f)
        args = tdq_eval.build_parser().parse_args(["report", "--thu-muc", thu_muc, *co])
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            tdq_eval.lenh_bao_cao(args)
        return buf.getvalue()

    def test_dem_va_chi_phi_cung_luc_in_ca_hai(self):
        ra = self._chay("--dem", "--chi-phi")
        self.assertIn("records:", ra)
        self.assertIn("round cost", ra)

    def test_khong_co_co_nao_thi_in_bang(self):
        self.assertIn("| L001", self._chay())


class AuditNeuTenBoQuaTest(unittest.TestCase):
    """Bỏ qua phép kiểm nào phải NÊU TÊN, không chỉ đếm — số bị loại lặng lẽ là số mất dấu."""

    def test_audit_liet_ke_tung_cap_bi_bo_qua(self):
        ban_ghi = []
        for nhanh, kq in (("viet", {"L003": "dat"}), ("lai", {"L003": "khong-ap-dung"})):
            ban_ghi.append({"ca": "commit-khong-push", "nhanh": nhanh, "lan": 1,
                            "trang_thai": "xong", "ket_qua": kq, "chi_phi": 0.1,
                            "so_luot": 2, "transcript": "/khong/co"})
        van = tdq_eval.viet_audit(tdq_eval.bao_cao_so(ban_ghi), "2026-08-20")
        self.assertIn("commit-khong-push · L003", van)


class MaUserFacingTest(unittest.TestCase):
    """Bốn mã thêm sau vòng chạy: đóng sổ, message commit, khuôn option, bảng ký hiệu.

    Chấm lại từ transcript đã lưu nên không tốn thêm phiên nào; điều đó cũng có nghĩa
    giám khảo phải đúng ngay từ mẫu, không có vòng chạy thật nào để sửa sai sau.
    """

    def _ph(self, van="", goi=None):
        return {"goi": goi or [], "van_ban_cuoi": van, "chi_phi": 0.0, "so_luot": 1}

    def _bash(self, lenh):
        return [{"ten": "Bash", "lenh": lenh, "file": None, "input": {}}]

    def test_L035_bo_qua_khi_khong_commit(self):
        self.assertEqual(tdq_eval.kiem_L035(self._ph()), "khong-ap-dung")

    def test_L035_do_khi_message_co_trailer_ai(self):
        goi = self._bash('git commit -m "sửa x\n\nCo-Authored-By: Claude <x@y>"')
        self.assertEqual(tdq_eval.kiem_L035(self._ph(goi=goi)), "vi-pham")

    def test_L121_bo_qua_khi_khong_ghi_file_nao(self):
        goi = self._bash("git status")
        self.assertEqual(tdq_eval.kiem_L121(self._ph(goi=goi)), "khong-ap-dung")

    def test_L121_do_khi_dong_so_thieu_log(self):
        goi = [{"ten": "Write", "file": "/tmp/sb/docs/tdq/plan/x.md", "lenh": "",
                "input": {"content": "x"}},
               {"ten": "Bash", "file": None, "input": {},
                "lenh": "python3 scripts/tdq_finish.py --files docs/tdq/plan/x.md"}]
        self.assertEqual(tdq_eval.kiem_L121(self._ph(goi=goi)), "vi-pham")

    def test_L209_do_khi_gop_option_vao_doan_van(self):
        self.assertEqual(tdq_eval.kiem_L209(self._ph("Chọn: - A: nhanh - B: sâu")), "vi-pham")

    def test_L209_dat_khi_moi_option_mot_dong(self):
        self.assertEqual(tdq_eval.kiem_L209(self._ph("- A (đề xuất): nhanh\n- B: sâu")), "dat")

    def test_L210_dat_voi_sau_ky_hieu_duoc_phep(self):
        van = "Xong · chi tiết — docs/x.md → bước sau\n➤ Duyệt: nhắn \"duyệt\""
        self.assertEqual(tdq_eval.kiem_L210(self._ph(van)), "dat")

    def test_L210_do_khi_co_ky_hieu_ngoai_bang(self):
        self.assertEqual(tdq_eval.kiem_L210(self._ph("Xong ✅")), "vi-pham")

    def test_L210_khong_tinh_dau_tick_hook_bat_in(self):
        """Hook TDQ BẮT in `✓ [TDQ:<MÃ>]`; chấm nó là vi phạm thì hai nhánh cùng trượt oan."""
        self.assertEqual(tdq_eval.kiem_L210(self._ph("✓ [TDQ:LOG] đã ghi log")), "dat")


class TachMaThemSauTest(unittest.TestCase):
    """Bốn mã thêm SAU khi đã thấy số phải tách khỏi phân tích đăng ký trước.

    Trộn chung là tự cho mình chọn thước sau khi đã nhìn kết quả. Báo cáo phải nêu
    được cả hai con số, và nói rõ con số nào là con số chốt trước khi chạy.
    """

    def _ban_ghi(self, ma, nhanh, phan_quyet):
        return {"ca": "x", "nhanh": nhanh, "lan": 1, "trang_thai": "xong",
                "ket_qua": {ma: phan_quyet}, "chi_phi": 0.1, "so_luot": 2,
                "transcript": "/khong/co"}

    def _ban_ghi_ca(self, ca, ma, nhanh, phan_quyet):
        bg = self._ban_ghi(ma, nhanh, phan_quyet)
        bg["ca"] = ca
        return bg

    def test_bao_cao_tach_rieng_p_cua_bo_dang_ky_truoc(self):
        bg = [self._ban_ghi("L001", "viet", "dat"), self._ban_ghi("L001", "lai", "vi-pham"),
              self._ban_ghi("L210", "viet", "dat"), self._ban_ghi("L210", "lai", "vi-pham")]
        bc = tdq_eval.bao_cao_so(bg)
        self.assertEqual(bc["so_don_vi"], 2)
        self.assertEqual(bc["so_don_vi_dang_ky"], 1)
        self.assertIn("p_dang_ky", bc)

    def test_audit_neu_ro_ma_nao_them_sau(self):
        bg = [self._ban_ghi("L210", "viet", "dat"), self._ban_ghi("L210", "lai", "dat")]
        van = tdq_eval.viet_audit(tdq_eval.bao_cao_so(bg), "2026-08-20")
        self.assertIn("thêm sau vòng chạy", van)
        self.assertIn("L210", van)

    def test_dong_p_dung_va_phan_quyet_lay_theo_bo_dang_ky_truoc(self):
        """Dòng `p = …` đứng riêng và câu phán quyết phải là số của bộ đăng ký trước.

        Bộ đầy đủ có thể ra p khác; in số đó ở vị trí phán quyết là ngầm chốt bằng
        thước chọn sau khi đã thấy kết quả.
        """
        bg = []
        for i in range(1, 8):
            bg += [self._ban_ghi_ca(f"ca{i}", "L001", "viet", "dat"),
                   self._ban_ghi_ca(f"ca{i}", "L001", "lai", "vi-pham")]
        bg += [self._ban_ghi_ca("cz", "L210", "viet", "vi-pham"),
               self._ban_ghi_ca("cz", "L210", "lai", "dat")]
        bc = tdq_eval.bao_cao_so(bg)
        self.assertNotAlmostEqual(bc["p"], bc["p_dang_ky"])
        van = tdq_eval.viet_audit(bc, "2026-08-20")
        self.assertIn(f"\np = {bc['p_dang_ky']:.4f} —", van)
        self.assertIn("**SỤT.**", van)


if __name__ == "__main__":
    unittest.main()
