"""Test cho scripts/tdq_bench.py — bộ cân đo mode main với mode đội.

Luật của bộ test này: không hằng số nào được đặt tay trong code sản phẩm. Test tự
dựng file thực đo giả để kiểm công thức, và kiểm luôn rằng thiếu file thì lệnh LỖI.
"""
import json
import os
import subprocess
import sys
import unittest

import helper  # noqa: F401  — chèn scripts/ vào sys.path
import tdq_bench

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BENCH = os.path.join(ROOT, "scripts", "tdq_bench.py")


def chay(*args, env=None):
    proc = subprocess.run([sys.executable, BENCH, *args], capture_output=True,
                          text=True, timeout=300,
                          env=dict(os.environ, TDQ_LOG="0", **(env or {})))
    return proc.returncode, proc.stdout, proc.stderr


class KhungTest(unittest.TestCase):
    """T1.1/T1.2 — khung CLI và log service."""

    def test_help_exit_0_va_liet_ke_du_4_lenh_con(self):
        rc, out, _err = chay("--help")
        self.assertEqual(rc, 0)
        for ten in ("gen-plan", "calibrate", "simulate", "scan"):
            self.assertIn(ten, out)

    def test_bon_lenh_con_deu_co_that_trong_bang_lenh(self):
        self.assertEqual(sorted(tdq_bench.LENH),
                         ["calibrate", "gen-plan", "scan", "simulate"])

    def test_thieu_lenh_con_thi_exit_2_chu_khong_lam_gi(self):
        rc, _out, err = chay()
        self.assertEqual(rc, 2)
        self.assertIn("Missing sub-command", err)

    def test_log_service_bat_mac_dinh_va_tat_bang_bien_moi_truong(self):
        proc = subprocess.run(
            [sys.executable, BENCH, "gen-plan", "--task", "2"],
            capture_output=True, text=True, timeout=60,
            env={k: v for k, v in os.environ.items() if k != "TDQ_LOG"})
        self.assertNotEqual(proc.stderr.strip(), "")
        self.assertIn("gen-plan", proc.stderr)
        # timestamp ISO: [YYYY-MM-DDTHH:MM:SS]
        self.assertRegex(proc.stderr, r"\[\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\]")
        rc, _out, err = chay("gen-plan", "--task", "2")
        self.assertEqual(rc, 0)
        self.assertEqual(err.strip(), "")


class DungPlanTest(unittest.TestCase):
    """T2.1 — plan mẫu phải là plan TDQ hợp lệ, không phải chuỗi trang trí."""

    def _sinh(self, **kw):
        van_ban, so_cap = tdq_bench.sinh_plan(**kw)
        return van_ban, so_cap, tdq_bench._tasks_tu_van_ban(van_ban)

    def test_dung_so_task_va_dung_so_cap_chong_file(self):
        for so_task, chong in ((12, 0.25), (12, 0.0), (8, 1.0), (10, 0.5)):
            with self.subTest(so_task=so_task, chong=chong):
                _vb, so_cap, tasks = self._sinh(so_task=so_task, chong=chong)
                self.assertEqual(len(tasks), so_task)
                m = round(chong * so_task)
                self.assertEqual(so_cap, m * (m - 1) // 2)
                self.assertEqual(tdq_bench.dem_cap_chong(tasks), so_cap)

    def test_moi_task_khai_vung_file_nen_khong_roi_vao_vung_khoa(self):
        _vb, _cap, tasks = self._sinh(so_task=6, chong=0.0)
        for t in tasks:
            self.assertTrue(t.vung_file, f"{t.ma} không khai Chạm:")

    def test_phu_thuoc_lam_task_bi_giu_lai_cho_leader(self):
        _vb, _cap, tasks = self._sinh(so_task=6, chong=0.0, phu_thuoc=2)
        giu = [t.ma for t in tasks
               if tdq_bench.tdq_team.quyet_dinh_task(t, tasks) == ("tu_lam", "phu-thuoc")]
        self.assertEqual(len(giu), 2, f"giữ lại {giu}")

    def test_plan_sinh_ra_qua_duoc_doc_lint(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            duong = os.path.join(tmp, "plan-mau.md")
            rc, out, err = chay("gen-plan", "--task", "12", "--chong", "0.25",
                                "--ra", duong)
            self.assertEqual(rc, 0, err)
            self.assertIn("12 task", out)
            lint = subprocess.run(
                [sys.executable, os.path.join(ROOT, "scripts", "doc_lint.py"), duong],
                capture_output=True, text=True, timeout=60)
            self.assertEqual(lint.returncode, 0, lint.stdout + lint.stderr)

    def test_tham_so_vo_ly_thi_loi_chu_khong_sinh_plan_rac(self):
        for args in (("--task", "0"), ("--chong", "1.5"), ("--phu-thuoc", "99")):
            with self.subTest(args=args):
                rc, _out, err = chay("gen-plan", *args)
                self.assertEqual(rc, 1)
                self.assertTrue(err.strip())


class PlanMauChayThatTest(unittest.TestCase):
    """T2.2 — plan mẫu phải chạy được với ĐÚNG công cụ thật, không phải bản mô phỏng."""

    def test_phan_cong_va_kiem_ke_chay_sach_tren_plan_mau(self):
        import tempfile
        goc = tempfile.mkdtemp(prefix="tdq-bench-test-")
        try:
            slug = "2026-01-01-0000-plan-mau-bench"
            repo, _rel = tdq_bench._dung_repo_tam(goc, slug, 5)
            wt = os.path.join(goc, "worktrees")
            _giay, rc, ra = tdq_bench._team(repo, "assign", wt=wt)
            self.assertEqual(rc, 0, ra)
            _giay, rc, ra = tdq_bench._team(repo, "audit", wt=wt)
            self.assertEqual(rc, 0, ra)
            duong = os.path.join(repo, "docs", "tdq", "team", f"{slug}.json")
            with open(duong, encoding="utf-8") as f:
                ban_do = json.load(f)
            self.assertEqual(len(ban_do["tasks"]), 5)
            for ma, rec in ban_do["tasks"].items():
                self.assertEqual(sorted(rec), ["dot", "ly_do", "quyet_dinh", "vung_file"],
                                 f"{ma} thiếu trường")
                self.assertEqual(rec["quyet_dinh"], "giao", f"{ma} bị giữ lại vô cớ")
        finally:
            import shutil
            shutil.rmtree(goc, ignore_errors=True)


# Hằng số đặt sẵn CHỈ dùng trong test, để kiểm tay công thức. Code sản phẩm không có
# số nào như thế này — nó bắt buộc đọc từ file thực đo.
HS_KIEM_TAY = {"t_task": 100.0, "t_tick": 10.0, "t_phat": 20.0,
               "t_kiem": 5.0, "t_hop": 5.0, "t_don": 15.0}


def _file_thuc_do(thu_muc, hang_so=None, bo=(), so_mau=3):
    hang_so = dict(hang_so or HS_KIEM_TAY)
    du_lieu = {"slug": "test", "ngay": "2026-01-01", "hang_so": {
        ten: {"giay": giay, "so_mau": so_mau, "do_tan": 0.0, "nguon": "stub",
              "mau": [giay] * so_mau}
        for ten, giay in hang_so.items() if ten not in bo}}
    duong = os.path.join(thu_muc, "thuc-do.json")
    with open(duong, "w", encoding="utf-8") as f:
        json.dump(du_lieu, f, ensure_ascii=False)
    return duong


class HangSoTest(unittest.TestCase):
    """T3.1 — cấm bịa hằng số. Thiếu số thật thì lệnh phải chết, không đoán."""

    def test_thieu_file_thuc_do_thi_loi_va_khong_in_bang(self):
        rc, out, err = chay("simulate", "--task", "4")
        self.assertEqual(rc, 1)
        self.assertNotIn("| Metric |", out)
        self.assertIn("--thuc-do", err)

    def test_file_thuc_do_khong_ton_tai_thi_neu_ten_file_phai_co(self):
        rc, out, err = chay("simulate", "--thuc-do", "/khong/co/that.json")
        self.assertEqual(rc, 1)
        self.assertEqual(out.strip(), "")
        self.assertIn("/khong/co/that.json", err)
        self.assertIn("calibrate", err)

    def test_thieu_mot_hang_so_thi_goi_ten_hang_so_do(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            duong = _file_thuc_do(tmp, bo=("t_hop",))
            rc, out, err = chay("simulate", "--thuc-do", duong, "--task", "4")
            self.assertEqual(rc, 1)
            self.assertNotIn("| Metric |", out)
            self.assertIn("t_hop", err)

    def test_hang_so_ghi_0_mau_bi_tu_choi(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            duong = _file_thuc_do(tmp, so_mau=0)
            with self.assertRaises(tdq_bench.LoiThieuSo) as bat:
                tdq_bench.nap_hang_so(duong)
            self.assertIn("so_mau", str(bat.exception))

    def test_file_thuc_do_hong_thi_bao_do_lai_chu_khong_van_traceback(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            duong = os.path.join(tmp, "hong.json")
            with open(duong, "w", encoding="utf-8") as f:
                f.write("{khong-phai-json")
            rc, _out, err = chay("simulate", "--thuc-do", duong)
            self.assertEqual(rc, 1)
            self.assertNotIn("Traceback", err)
            self.assertIn("Measure again", err)


class CongThucTest(unittest.TestCase):
    """T3.2 — số máy in ra phải khớp số tính tay ghi ngay trong test."""

    def test_vi_du_4_task_2_dot_khop_so_tinh_tay(self):
        van_ban, _cap = tdq_bench.sinh_plan(4, chong=0.5)
        kq = tdq_bench.mo_phong_van_ban(van_ban, HS_KIEM_TAY)
        # Tính tay: T1.1 và T1.2 cùng `src/chung.py` nên phải nằm hai đợt khác nhau.
        # Đợt 1 = {T1.1, T1.3, T1.4}, đợt 2 = {T1.2}.
        self.assertEqual((kq.so_task, kq.so_giao, kq.so_tu_lam, kq.so_dot), (4, 4, 0, 2))
        # T_main = 4×100 + 4×10 = 440
        self.assertAlmostEqual(kq.t_main, 440.0)
        # T_đội = 2×(20+5+5) + 2×100 + 15 + max(0, 0−200) = 60 + 200 + 15 = 275
        self.assertAlmostEqual(kq.t_doi, 275.0)
        self.assertEqual(kq.thang, "đội")
        # Biến thể kèm tick: 275 + 4×10 = 315
        self.assertAlmostEqual(kq.t_doi_kem_tick, 315.0)

    def test_leader_lam_chen_duoc_cong_dung_phan_vuot(self):
        # 4 task, 2 task cuối phụ thuộc → leader giữ 2, giao 2 (rời nhau → 1 đợt).
        van_ban, _cap = tdq_bench.sinh_plan(4, chong=0.0, phu_thuoc=2)
        kq = tdq_bench.mo_phong_van_ban(van_ban, HS_KIEM_TAY)
        self.assertEqual((kq.so_giao, kq.so_tu_lam, kq.so_dot), (2, 2, 1))
        # chen = max(0, 2×100 − 1×100) = 100
        self.assertAlmostEqual(kq.chen, 100.0)
        # T_đội = 1×30 + 100 + 15 + 100 = 245 ; T_main = 4×100 + 4×10 = 440
        self.assertAlmostEqual(kq.t_doi, 245.0)
        self.assertAlmostEqual(kq.t_main, 440.0)

    def test_bang_in_ra_co_du_dong_va_cau_ket_luan_thang(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            duong = _file_thuc_do(tmp)
            rc, out, _err = chay("simulate", "--thuc-do", duong, "--task", "4",
                                 "--chong", "0.5")
            self.assertEqual(rc, 0)
            self.assertIn("| Metric | main | team |", out)
            self.assertIn("Winner: đội", out)
            self.assertIn("4 task", out)


class QuetTest(unittest.TestCase):
    """T3.3 — quét dải tỉ lệ tách được, phải chỉ ra ngưỡng đổi chiều."""

    def test_quet_in_bang_va_neu_ro_nguong_doi_chieu(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            duong = _file_thuc_do(tmp)
            rc, out, _err = chay("scan", "--thuc-do", duong, "--task", "12",
                                 "--buoc", "10")
            self.assertEqual(rc, 0)
            self.assertIn("| Splittable | Waves |", out)
            self.assertIn("THRESHOLD:", out)
            dong = [d for d in out.splitlines() if d.startswith("| ") and "%" in d]
            self.assertEqual(len(dong), 11)      # 0,10,…,100
            thang = [d.rsplit("|", 2)[1].strip() for d in dong]
            self.assertIn("main", thang)
            self.assertIn("đội", thang)

    def test_quet_khong_dung_hang_so_bia_khi_thieu_file(self):
        rc, out, err = chay("scan", "--task", "6")
        self.assertEqual(rc, 1)
        self.assertNotIn("| Splittable |", out)
        self.assertIn("--thuc-do", err)


class BienTest(unittest.TestCase):
    """T3.4 — plan không tách được thì mode đội KHÔNG được thắng."""

    def test_bien_6_task_cung_mot_file_thi_doi_khong_nhanh_hon(self):
        van_ban, so_cap = tdq_bench.sinh_plan(6, chong=1.0)
        self.assertEqual(so_cap, 15)             # C(6,2)
        kq = tdq_bench.mo_phong_van_ban(van_ban, HS_KIEM_TAY)
        self.assertEqual(kq.so_dot, 6)           # mỗi task một đợt
        # T_main = 6×100 + 6×10 = 660 ; T_đội = 6×30 + 6×100 + 15 = 795
        self.assertAlmostEqual(kq.t_main, 660.0)
        self.assertAlmostEqual(kq.t_doi, 795.0)
        self.assertGreaterEqual(kq.t_doi, kq.t_main)
        self.assertEqual(kq.thang, "main")

    def test_bien_giu_dung_voi_moi_bo_hang_so_duong(self):
        for t_task in (30.0, 100.0, 600.0):
            with self.subTest(t_task=t_task):
                hs = dict(HS_KIEM_TAY, t_task=t_task)
                van_ban, _cap = tdq_bench.sinh_plan(6, chong=1.0)
                kq = tdq_bench.mo_phong_van_ban(van_ban, hs)
                self.assertGreaterEqual(kq.t_doi, kq.t_main)


class ThucDoTest(unittest.TestCase):
    """T4.1 — lượt đo phải chạy vòng đội THẬT rồi ghi số, và dọn sạch sau lưng."""

    def test_thuc_do_ghi_du_6_hang_so_kem_so_mau_va_do_tan(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            ra = os.path.join(tmp, "thuc-do.json")
            rc, out, err = chay("calibrate", "--ra", ra, "--task", "3", "--lap", "3")
            self.assertEqual(rc, 0, err)
            with open(ra, encoding="utf-8") as f:
                du_lieu = json.load(f)
            self.assertEqual(sorted(du_lieu["hang_so"]), sorted(tdq_bench.HANG_SO))
            for ten, rec in du_lieu["hang_so"].items():
                self.assertGreaterEqual(rec["so_mau"], 3, ten)
                self.assertIn("do_tan", rec)
                self.assertIn(rec["nguon"], tdq_bench.NGUON_HOP_LE)
                self.assertEqual(len(rec["mau"]), rec["so_mau"], ten)
            self.assertIn("t_task", out)

    def test_thuc_do_khong_de_lai_worktree_hay_thu_muc_tam(self):
        import glob
        import tempfile
        # So TRƯỚC-SAU chứ không đòi thư mục tạm rỗng tuyệt đối: máy có thể đang chạy
        # một lượt đo khác, và test này chỉ chịu trách nhiệm cho rác của chính nó.
        khuon = os.path.join(tempfile.gettempdir(), "tdq-bench-*")
        truoc = set(glob.glob(khuon))
        with tempfile.TemporaryDirectory() as tmp:
            ra = os.path.join(tmp, "thuc-do.json")
            rc, _out, err = chay("calibrate", "--ra", ra, "--task", "3", "--lap", "1",
                                 "--cho-it-mau")
            self.assertEqual(rc, 0, err)
        self.assertEqual(set(glob.glob(khuon)) - truoc, set())

    def test_mau_that_thay_han_so_stub_va_danh_dau_nguon(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            ra = os.path.join(tmp, "thuc-do.json")
            rc, _out, err = chay("calibrate", "--ra", ra, "--task", "3", "--lap", "1",
                                 "--cho-it-mau",
                                 "--mau-that", "t_task=91.2,t_task=104.7,t_task=88.0")
            self.assertEqual(rc, 0, err)
            with open(ra, encoding="utf-8") as f:
                rec = json.load(f)["hang_so"]["t_task"]
            self.assertEqual(rec["nguon"], "that")
            self.assertEqual(rec["so_mau"], 3)
            self.assertAlmostEqual(rec["giay"], (91.2 + 104.7 + 88.0) / 3, places=3)
            self.assertGreater(rec["do_tan"], 0)

    def test_mau_that_sai_khuon_thi_loi_ro_rang(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            ra = os.path.join(tmp, "thuc-do.json")
            for chuoi in ("t_task", "t_khong_co=1", "t_task=nhanh"):
                with self.subTest(chuoi=chuoi):
                    rc, _out, err = chay("calibrate", "--ra", ra, "--task", "2",
                                         "--lap", "1", "--cho-it-mau",
                                         "--mau-that", chuoi)
                    self.assertEqual(rc, 1)
                    self.assertNotIn("Traceback", err)

    def test_khong_du_3_mau_thi_tu_choi_ghi_file(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            ra = os.path.join(tmp, "thuc-do.json")
            rc, _out, err = chay("calibrate", "--ra", ra, "--task", "1", "--lap", "1")
            self.assertEqual(rc, 1)
            self.assertFalse(os.path.exists(ra))
            self.assertIn("samples", err)

    def test_repo_that_khong_moc_nhanh_hay_worktree_nao(self):
        import tempfile
        truoc = subprocess.run(["git", "-C", ROOT, "worktree", "list"],
                               capture_output=True, text=True, timeout=60).stdout
        with tempfile.TemporaryDirectory() as tmp:
            chay("calibrate", "--ra", os.path.join(tmp, "t.json"), "--task", "3",
                 "--lap", "1", "--cho-it-mau")
        sau = subprocess.run(["git", "-C", ROOT, "worktree", "list"],
                             capture_output=True, text=True, timeout=60).stdout
        self.assertEqual(truoc, sau)
        nhanh = subprocess.run(["git", "-C", ROOT, "branch", "--list", "tdq/*"],
                               capture_output=True, text=True, timeout=60).stdout
        self.assertEqual(nhanh.strip(), "")


class VongFix1Test(unittest.TestCase):
    """Vòng fix 1 — mọi ca agent QC độc lập bới ra. Đỏ trước khi vá, xanh sau khi vá."""

    def test_lap_0_bi_tu_choi(self):
        """`--lap 0` + `--mau-that` = bịa trọn 6 hằng số mà file vẫn ghi nguon=that."""
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            ra = os.path.join(tmp, "bia.json")
            chuoi = ",".join(f"{ten}=1.0" for ten in tdq_bench.HANG_SO for _ in range(3))
            rc, _out, err = chay("calibrate", "--ra", ra, "--lap", "0", "--mau-that", chuoi)
            self.assertEqual(rc, 1)
            self.assertFalse(os.path.exists(ra))
            self.assertIn("--lap", err)
            self.assertNotIn("Traceback", err)

    def test_mau_that_ghi_ro_la_nhap_tay(self):
        """Số người nhập phải mang cach_do=nhap-tay, và mẫu máy đo phải còn ở mau_may."""
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            ra = os.path.join(tmp, "thuc-do.json")
            chuoi = "t_task=90.0,t_task=100.0,t_task=110.0"
            rc, _out, _err = chay("calibrate", "--ra", ra, "--task", "3", "--lap", "1",
                                  "--cho-it-mau", "--mau-that", chuoi)
            self.assertEqual(rc, 0)
            with open(ra, encoding="utf-8") as f:
                bang = json.load(f)["hang_so"]
            self.assertEqual(bang["t_task"]["cach_do"], "nhap-tay")
            self.assertIn("mau_may", bang["t_task"])
            self.assertEqual(bang["t_phat"]["cach_do"], "may")
            self.assertNotIn("mau_may", bang["t_phat"])

    def test_so_mau_duoi_nguong_bi_tu_choi_luc_doc(self):
        """Cửa so_mau phải khoá ở chỗ ĐỌC: file có thể bị sửa tay sau khi ghi."""
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            duong = _file_thuc_do(tmp, so_mau=1)
            rc, out, err = chay("simulate", "--thuc-do", duong, "--task", "4")
            self.assertEqual(rc, 1)
            self.assertNotIn("| Metric |", out)
            self.assertIn("so_mau", err)
            self.assertNotIn("Traceback", err)

    def test_hang_so_am_hoac_vo_cuc_bi_tu_choi(self):
        import tempfile
        for xau in (-5.0, 0.0, float("inf")):
            with self.subTest(giay=xau), tempfile.TemporaryDirectory() as tmp:
                hs = dict(HS_KIEM_TAY, t_task=xau)
                duong = _file_thuc_do(tmp, hang_so=hs)
                rc, out, err = chay("simulate", "--thuc-do", duong, "--task", "4")
                self.assertEqual(rc, 1)
                self.assertNotIn("| Metric |", out)
                self.assertIn("t_task", err)
                self.assertNotIn("Traceback", err)

    def test_moi_ca_hong_deu_bao_loi_co_lenh_sua(self):
        """5 ca hỏng agent QC tìm được: không ca nào được văng traceback thô."""
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            tot = _file_thuc_do(tmp)
            chu = _file_thuc_do(os.path.join(tmp, ""), hang_so=dict(
                HS_KIEM_TAY, t_task="nhanh"))
            khong_so = os.path.join(tmp, "null.json")
            with open(tot, encoding="utf-8") as f:
                du_lieu = json.load(f)
            du_lieu["hang_so"]["t_task"]["giay"] = None
            with open(khong_so, "w", encoding="utf-8") as f:
                json.dump(du_lieu, f)
            ca = [
                ("plan không có", ("simulate", "--thuc-do", tot,
                                   "--plan", os.path.join(tmp, "khong-co.md"))),
                ("thư mục ra không có", ("gen-plan", "--task", "2", "--ra",
                                         os.path.join(tmp, "khong/co/plan.md"))),
                ("giay không phải số", ("simulate", "--thuc-do", chu, "--task", "4")),
                ("giay null", ("simulate", "--thuc-do", khong_so, "--task", "4")),
                ("buoc 0", ("scan", "--thuc-do", tot, "--buoc", "0")),
                ("buoc âm", ("scan", "--thuc-do", tot, "--buoc", "-10")),
            ]
            for ten, lenh in ca:
                with self.subTest(ca=ten):
                    rc, out, err = chay(*lenh)
                    self.assertEqual(rc, 1)
                    self.assertNotIn("Traceback", err)
                    self.assertIn("tdq_bench.py", err)   # lỗi phải kèm câu lệnh sửa
                    self.assertNotIn("| Splittable |", out)

    def test_he_so_agent_lam_doi_thua_khi_agent_con_cham_hon(self):
        """Trục độ nhạy agent QC chỉ ra: agent con chậm gấp đôi thì lợi thế bốc hơi."""
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            duong = _file_thuc_do(tmp)
            rc, nhanh, _err = chay("simulate", "--thuc-do", duong, "--task", "12",
                                   "--chong", "0.5", "--he-so-agent", "1")
            self.assertEqual(rc, 0)
            self.assertIn("agent factor 1.0", nhanh)
            rc, cham, _err = chay("simulate", "--thuc-do", duong, "--task", "12",
                                  "--chong", "0.5", "--he-so-agent", "3")
            self.assertEqual(rc, 0)
            self.assertIn("agent factor 3.0", cham)
            self.assertIn("Winner: đội", nhanh)
            self.assertIn("Winner: main", cham)
            rc, quet, _err = chay("scan", "--thuc-do", duong, "--task", "12",
                                  "--buoc", "50", "--he-so-agent", "2")
            self.assertEqual(rc, 0)
            self.assertIn("agent factor 2.0", quet)


if __name__ == "__main__":
    unittest.main()
