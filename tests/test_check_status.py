"""Skill + CLI `tdq-check-status`: dò request đang dở, chấm 11 ca lệch D1–D11.

Luật khoá ở đây: đĩa là bằng chứng, `state.json` là lời khai. Lệch thì tin đĩa và
ĐỀ XUẤT lệnh vá — không tự ghi, và không bao giờ sinh lệnh làm mất dữ liệu.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

import helper
from helper import ROOT
import tdq_state

SCRIPT = os.path.join(ROOT, "scripts", "tdq_checkstatus.py")
SKILL_DIR = os.path.join(ROOT, "skills", "tdq-check-status")


def viet(path, noi_dung):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(noi_dung)
    return path


def doc(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


PLAN_MAU = """# PLAN — mẫu

## P1 — việc
- [x] **T1.1** (n3 e5m) việc xong — Test: `true`
- [ ] **T1.2** (n3 e5m) việc chưa làm — Test: `true`
"""


class TempRepo(unittest.TestCase):
    """Một project TDQ giả lập trong thư mục tạm, không đụng repo thật."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.cwd = self.tmp.name
        self.addCleanup(self.tmp.cleanup)
        os.makedirs(os.path.join(self.cwd, "docs", "tdq"), exist_ok=True)

    def chay(self, *args, env=None):
        return helper.run_checkstatus_cli(self.cwd, *args, env=env)

    def json_ra(self, *args):
        rc, out, _err = self.chay("report", "--json", *args)
        self.assertEqual(rc, 0, out)
        return json.loads(out)

    def ma_ca_lech(self, *args):
        return {c["ma"] for c in self.json_ra(*args)["ca_lech"]}

    def tai_san(self, slug, plan=PLAN_MAU, spec="# SPEC\n", brief="# BRIEF\n"):
        """Ghi brief/spec/plan của một request lên đĩa, trả về đường dẫn tương đối."""
        duong = {}
        for thu_muc, noi_dung in (("brief", brief), ("spec", spec), ("plan", plan)):
            if noi_dung is None:
                continue
            rel = os.path.join("docs", "tdq", thu_muc, f"{slug}.md")
            viet(os.path.join(self.cwd, rel), noi_dung)
            duong[thu_muc] = rel
        return duong

    def state_day_du(self, slug="2026-08-16-0900-viec", phase="implement", **thua):
        """State của một request đã duyệt spec + plan, khớp đĩa — ca sạch."""
        duong = self.tai_san(slug)
        moc = "2026-08-16T09:00:00+07:00"
        truong = dict(
            active_request=slug, lane="full", phase=phase,
            started_at=moc, phase_history=[{"phase": "spec", "at": moc}],
            spec_file=duong["spec"], spec_approved=True, spec_approved_at=moc,
            spec_approved_by="duyệt spec",
            spec_sha256=tdq_state.sha256_file(os.path.join(self.cwd, duong["spec"])),
            plan_file=duong["plan"], plan_approved=True, plan_approved_at=moc,
            plan_approved_by="duyệt plan",
            plan_sha256=tdq_state.sha256_file(os.path.join(self.cwd, duong["plan"])),
            implement_mode="main",
        )
        truong.update(thua)
        helper.write_state(self.cwd, **truong)
        return duong

    def doi_plan(self, noi_dung):
        """Thay nội dung plan rồi ghi lại `plan_sha256` cho khớp — để chỉ còn ca cần thử."""
        self.state_day_du()
        self.tai_san("2026-08-16-0900-viec", plan=noi_dung)
        rel = os.path.join("docs", "tdq", "plan", "2026-08-16-0900-viec.md")
        state = tdq_state.load(self.cwd)
        state["plan_sha256"] = tdq_state.sha256_file(os.path.join(self.cwd, rel))
        helper.write_state(self.cwd, **state)


# ------------------------------------------------------------------ P1 khung

class KhungCli(TempRepo):

    def test_khung_cli_report_chay_duoc(self):
        self.state_day_du()
        rc, out, _err = self.chay("report")
        self.assertEqual(rc, 0, out)
        self.assertIn("Request", out)

    def test_khung_cli_sai_cu_phap_thoat_2(self):
        rc, _out, err = self.chay("khong-co-lenh-nay")
        self.assertEqual(rc, 2, err)

    def test_ca_lech_d1_khong_co_request(self):
        helper.write_state(self.cwd, active_request=None)
        rc, out, _err = self.chay("report")
        self.assertEqual(rc, 0, out)
        self.assertIn("Chưa có request TDQ nào đang chạy", out)
        self.assertIn("D1", out)

    def test_gom_bang_chung_du_tai_san_va_tick(self):
        self.state_day_du()
        du_lieu = self.json_ra()
        tai_san = du_lieu["bang_chung"]["tai_san"]
        self.assertTrue(tai_san["spec"]["co"])
        self.assertTrue(tai_san["plan"]["co"])
        self.assertFalse(tai_san["qc"]["co"])
        self.assertEqual(du_lieu["bang_chung"]["tick"]["tong"], 2)
        self.assertEqual(du_lieu["bang_chung"]["tick"]["xong"], 1)

    def test_khong_git_van_chay(self):
        """Repo không phải git: nhánh git in '—', phần còn lại vẫn nguyên."""
        self.state_day_du()
        du_lieu = self.json_ra()
        self.assertEqual(du_lieu["bang_chung"]["git"]["co"], False)
        self.assertTrue(du_lieu["bang_chung"]["git"]["ly_do"])

    def test_ca_lech_d8_working_log_khong_nhac_slug(self):
        self.state_day_du()
        du_lieu = self.json_ra("--now", "2026-08-16T10:00:00+07:00")
        self.assertIn("D8", {c["ma"] for c in du_lieu["ca_lech"]})

    def test_ca_lech_d8_bao_cao_in_entry_cuoi_cua_working_log(self):
        """QC1.5 — T1.4 đòi 'mốc entry cuối', nên entry đó phải lên báo cáo."""
        self.state_day_du()
        viet(os.path.join(self.cwd, tdq_state.today_log_rel()),
             "## 09:00\n\nviệc cũ\n\n## 09:30\n\nlàm việc của 2026-08-16-0900-viec\n")
        du_lieu = self.json_ra()
        log = du_lieu["bang_chung"]["working_log"]
        self.assertEqual(log["entry_cuoi"], "## 09:30")
        self.assertTrue(log["nhac_slug_entry_cuoi"])
        _rc, out, _err = self.chay("report")
        self.assertIn("09:30", out)


class CoGit(TempRepo):
    """Ca D7: repo THẬT có git, có commit sau mốc `updated_at` của state."""

    def setUp(self):
        super().setUp()
        if shutil.which("git") is None:
            self.skipTest("máy không có git")
        for args in (("init", "-q"), ("config", "user.email", "t@t.t"),
                     ("config", "user.name", "t")):
            subprocess.run(["git", *args], cwd=self.cwd, check=True,
                           capture_output=True)

    def commit(self, message):
        subprocess.run(["git", "add", "-A"], cwd=self.cwd, check=True, capture_output=True)
        subprocess.run(["git", "commit", "-q", "-m", message], cwd=self.cwd,
                       check=True, capture_output=True)

    def test_ca_lech_d7_co_commit_sau_updated_at(self):
        self.state_day_du(updated_at="2020-01-01T00:00:00+07:00")
        viet(os.path.join(self.cwd, "them.txt"), "agent khác vừa sửa\n")
        self.commit("agent ngoài làm hộ phase implement")
        du_lieu = self.json_ra()
        self.assertTrue(du_lieu["bang_chung"]["git"]["co"])
        self.assertIn("D7", {c["ma"] for c in du_lieu["ca_lech"]})
        self.assertIn("agent ngoài làm hộ", json.dumps(du_lieu, ensure_ascii=False))


# ------------------------------------------------------- P2 chấm 11 ca lệch

class BangCaLech(TempRepo):

    def test_ca_lech_bang_du_11_ma_du_truong(self):
        sys.path.insert(0, os.path.join(ROOT, "scripts"))
        import tdq_checkstatus
        bang = tdq_checkstatus.CA_LECH
        self.assertEqual(sorted(bang, key=lambda m: int(m[1:])),
                         [f"D{i}" for i in range(1, 12)],
                         "phải đủ đúng 11 mã D1–D11")
        for ma, luat in bang.items():
            with self.subTest(ma=ma):
                for truong in ("dau_hieu", "muc", "chan_doan"):
                    self.assertTrue(luat.get(truong), f"{ma} thiếu {truong}")
                self.assertIn(luat["muc"], ("ok", "canh-bao", "chan"))
                self.assertIn("lenh_va", luat, f"{ma} thiếu khoá lenh_va")

    def test_ca_lech_sach_khong_bao_gi(self):
        """Request khớp đĩa hoàn toàn → không ca nào ngoài D8 (working log)."""
        self.state_day_du()
        viet(os.path.join(self.cwd, tdq_state.today_log_rel()),
             "## 09:30\n\nlàm việc của 2026-08-16-0900-viec\n")
        self.assertEqual(self.ma_ca_lech(), set())


class CaLechPhase(TempRepo):

    def test_ca_lech_d2_phase_spec_ma_chua_co_file(self):
        slug = "2026-08-16-0900-viec"
        helper.write_state(self.cwd, active_request=slug, lane="full", phase="spec")
        self.assertIn("D2", self.ma_ca_lech())

    def test_ca_lech_d2_implement_ma_plan_chua_tick(self):
        chua_tick = PLAN_MAU.replace("- [x] **T1.1**", "- [ ] **T1.1**")
        self.state_day_du()
        duong = self.tai_san("2026-08-16-0900-viec", plan=chua_tick)
        helper.write_state(
            self.cwd, active_request="2026-08-16-0900-viec", lane="full",
            phase="implement", plan_file=duong["plan"], plan_approved=True,
            plan_approved_at="2026-08-16T09:00:00+07:00", plan_approved_by="duyệt plan",
            plan_sha256=tdq_state.sha256_file(os.path.join(self.cwd, duong["plan"])),
            spec_file=duong["spec"], spec_approved=True,
            spec_approved_at="2026-08-16T09:00:00+07:00", spec_approved_by="duyệt spec",
            spec_sha256=tdq_state.sha256_file(os.path.join(self.cwd, duong["spec"])),
            started_at="2026-08-16T09:00:00+07:00")
        self.assertIn("D2", self.ma_ca_lech())

    def test_ca_lech_d2_moi_task_xong_ma_van_o_implement(self):
        self.doi_plan(PLAN_MAU.replace("- [ ] **T1.2**", "- [x] **T1.2**"))
        ca = self.ma_ca_lech()
        self.assertIn("D2", ca)
        self.assertNotIn("D3", ca)

    def test_ca_lech_d2_de_xuat_dung_phase_ke_tiep(self):
        self.doi_plan(PLAN_MAU.replace("- [ ] **T1.2**", "- [x] **T1.2**"))
        lenh = " ".join(self.json_ra()["lenh_va"])
        self.assertIn("set phase=qc", lenh)


class CaLechTaiSan(TempRepo):

    def test_ca_lech_d3_sha_spec_lech_sau_khi_duyet(self):
        self.state_day_du()
        viet(os.path.join(self.cwd, "docs", "tdq", "spec", "2026-08-16-0900-viec.md"),
             "# SPEC đã sửa sau khi duyệt\n")
        du_lieu = self.json_ra()
        ca = [c for c in du_lieu["ca_lech"] if c["ma"] == "D3"]
        self.assertTrue(ca, "phải bắt được sha lệch")
        self.assertEqual(ca[0]["muc"], "chan")
        self.assertEqual(du_lieu["ket_luan"], "CẦN USER QUYẾT")

    def test_ca_lech_d4_mot_task_dang_lam(self):
        self.doi_plan(PLAN_MAU.replace("- [ ] **T1.2**", "- [~] **T1.2**"))
        du_lieu = self.json_ra()
        self.assertEqual(du_lieu["bang_chung"]["tick"]["dang_lam"], ["T1.2"])
        self.assertNotIn("D4", {c["ma"] for c in du_lieu["ca_lech"]})

    def test_ca_lech_d4_nhieu_task_dang_lam_thi_canh_bao(self):
        self.doi_plan(PLAN_MAU.replace("- [x] **T1.1**", "- [~] **T1.1**")
                              .replace("- [ ] **T1.2**", "- [~] **T1.2**"))
        du_lieu = self.json_ra()
        ca = [c for c in du_lieu["ca_lech"] if c["ma"] == "D4"]
        self.assertTrue(ca)
        self.assertEqual(ca[0]["muc"], "canh-bao")
        self.assertIn("T1.1", ca[0]["chi_tiet"])
        self.assertIn("T1.2", ca[0]["chi_tiet"])

    def test_ca_lech_d5_file_dang_ky_nhung_mat_tren_dia(self):
        self.state_day_du()
        os.remove(os.path.join(self.cwd, "docs", "tdq", "plan",
                               "2026-08-16-0900-viec.md"))
        ca = [c for c in self.json_ra()["ca_lech"] if c["ma"] == "D5"]
        self.assertTrue(ca)
        self.assertEqual(ca[0]["muc"], "chan")

    def test_ca_lech_d6_co_duyet_nhung_thieu_nguoi_duyet(self):
        self.state_day_du(spec_approved_by="")
        ca = [c for c in self.json_ra()["ca_lech"] if c["ma"] == "D6"]
        self.assertTrue(ca)


class CaLechState(TempRepo):

    def test_ca_lech_d9_schema_cu(self):
        self.state_day_du()
        path = os.path.join(self.cwd, "docs", "tdq", "state.json")
        with open(path, encoding="utf-8") as f:
            tho = json.load(f)
        tho["schema_version"] = 1
        with open(path, "w", encoding="utf-8") as f:
            json.dump(tho, f, ensure_ascii=False)
        self.assertIn("D9", self.ma_ca_lech())

    def test_ca_lech_d10_thieu_moc_thoi_gian(self):
        self.state_day_du(started_at=None, phase_history=[])
        du_lieu = self.json_ra()
        ca = [c for c in du_lieu["ca_lech"] if c["ma"] == "D10"]
        self.assertTrue(ca)
        self.assertEqual(ca[0]["muc"], "canh-bao")
        self.assertIn("started_at", " ".join(du_lieu["lenh_va"]))

    def test_ca_lech_d10_chi_rong_phase_history_thi_chi_la_ok(self):
        """QC1.5 — `set started_at` không chữa được `phase_history` rỗng, đừng hứa hão."""
        self.state_day_du(phase_history=[])
        ca = [c for c in self.json_ra()["ca_lech"] if c["ma"] == "D10"]
        self.assertTrue(ca)
        self.assertEqual(ca[0]["muc"], "ok")
        self.assertIsNone(ca[0]["lenh_va"])

    def test_ca_lech_d11_state_lac_cho(self):
        self.state_day_du()
        viet(os.path.join(self.cwd, "con", "docs", "tdq", "state.json"), "{}\n")
        ca = [c for c in self.json_ra()["ca_lech"] if c["ma"] == "D11"]
        self.assertTrue(ca)
        self.assertEqual(ca[0]["muc"], "chan")


class StateDocKhongDuoc(TempRepo):
    """QC1.1 + QC1.2 — state còn trên đĩa nhưng không dùng được.

    Đây là ca nguy hiểm nhất: nếu bộ dò nói "chưa có request nào", model yếu sẽ mở
    request mới và ghi đè lên spec/plan đang có.
    """

    def lam_hong_state(self, noi_dung):
        with open(os.path.join(self.cwd, "docs", "tdq", "state.json"),
                  "w", encoding="utf-8") as f:
            f.write(noi_dung)

    def test_state_hong_khong_bao_la_chua_co_request(self):
        self.state_day_du()
        self.lam_hong_state('{ "active_request": "x",\n')
        rc, out, _err = self.chay("report")
        self.assertEqual(rc, 0, out)
        self.assertNotIn("Chưa có request TDQ nào đang chạy", out)
        du_lieu = self.json_ra()
        ca = [c for c in du_lieu["ca_lech"] if c["ma"] == "D1"]
        self.assertTrue(ca)
        self.assertEqual(ca[0]["muc"], "chan")
        self.assertEqual(du_lieu["ket_luan"], "CẦN USER QUYẾT")

    def test_state_hong_chi_ra_tai_san_con_tren_dia(self):
        self.state_day_du()
        self.lam_hong_state("{ khong-phai-json")
        du_lieu = self.json_ra()
        self.assertIn("2026-08-16-0900-viec", json.dumps(du_lieu, ensure_ascii=False))
        self.assertNotIn("tdq-intake", du_lieu["viec_ke_tiep"])

    def test_state_hong_khong_bi_script_ghi_de(self):
        """Bộ dò chỉ đọc: file hỏng phải còn NGUYÊN sau khi chạy report."""
        self.state_day_du()
        tho = "{ hỏng nhưng phải giữ lại"
        self.lam_hong_state(tho)
        self.chay("report")
        self.assertEqual(doc(os.path.join(self.cwd, "docs", "tdq", "state.json")), tho)

    def test_schema_la_chuoi_khong_lam_no_script(self):
        self.state_day_du()
        path = os.path.join(self.cwd, "docs", "tdq", "state.json")
        with open(path, encoding="utf-8") as f:
            tho = json.load(f)
        tho["schema_version"] = "1"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(tho, f, ensure_ascii=False)
        rc, out, err = self.chay("report", "--json")
        self.assertEqual(rc, 0, err)
        self.assertIn("D9", {c["ma"] for c in json.loads(out)["ca_lech"]})

    def test_schema_la_thieu_han_van_bao_d9(self):
        self.state_day_du()
        path = os.path.join(self.cwd, "docs", "tdq", "state.json")
        with open(path, encoding="utf-8") as f:
            tho = json.load(f)
        del tho["schema_version"]
        with open(path, "w", encoding="utf-8") as f:
            json.dump(tho, f, ensure_ascii=False)
        self.assertIn("D9", self.ma_ca_lech())


class BaMucKetLuan(TempRepo):

    def test_ba_muc_ket_luan_tiep_tuc_duoc(self):
        self.state_day_du()
        viet(os.path.join(self.cwd, tdq_state.today_log_rel()),
             "## 09:30\n\nlàm việc của 2026-08-16-0900-viec\n")
        self.assertEqual(self.json_ra()["ket_luan"], "TIẾP TỤC ĐƯỢC")

    def test_ba_muc_ket_luan_va_roi_tiep_tuc(self):
        self.state_day_du(started_at=None, phase_history=[])
        self.assertEqual(self.json_ra()["ket_luan"], "VÁ RỒI TIẾP TỤC")

    def test_viec_ke_tiep_khong_noi_chan_khi_khong_co_ca_chan(self):
        """QC1.4 — D7 một mình đẩy sang CẦN USER QUYẾT, nhưng không có ca `chan` nào."""
        self.state_day_du()
        du_lieu = self.json_ra()
        ca_gia = [{"ma": "D7", "muc": "canh-bao", "lenh_va": None,
                   "dau_hieu": "", "chan_doan": "", "chi_tiet": ""}]
        sys.path.insert(0, os.path.join(ROOT, "scripts"))
        import tdq_checkstatus
        muc = tdq_checkstatus.ket_luan(ca_gia)
        self.assertEqual(muc, "CẦN USER QUYẾT")
        cau = tdq_checkstatus.viec_ke_tiep(
            {"active_request": "x", "phase": "implement"},
            du_lieu["bang_chung"], muc, ca_gia)
        self.assertNotIn("chan`", cau)
        self.assertIn("D7", cau)

    def test_viec_ke_tiep_neu_dich_danh_ca_chan(self):
        self.state_day_du()
        os.remove(os.path.join(self.cwd, "docs", "tdq", "spec",
                               "2026-08-16-0900-viec.md"))
        self.assertIn("D5", self.json_ra()["viec_ke_tiep"])

    def test_ba_muc_ket_luan_can_user_quyet(self):
        self.state_day_du()
        os.remove(os.path.join(self.cwd, "docs", "tdq", "spec",
                               "2026-08-16-0900-viec.md"))
        self.assertEqual(self.json_ra()["ket_luan"], "CẦN USER QUYẾT")


# --------------------------------------------------- P3 báo cáo và lệnh vá

MUC_BAO_CAO = ("## Request", "## Bằng chứng trên đĩa", "## Ca lệch phát hiện",
               "## Kết luận", "## Lệnh vá đề xuất", "## Việc kế tiếp")


class KhuonBaoCao(TempRepo):

    def test_khuon_bao_cao_du_6_muc_dung_thu_tu(self):
        self.state_day_du()
        _rc, out, _err = self.chay("report")
        vi_tri = [out.find(m) for m in MUC_BAO_CAO]
        for muc, i in zip(MUC_BAO_CAO, vi_tri):
            self.assertGreaterEqual(i, 0, f"báo cáo thiếu mục {muc}")
        self.assertEqual(vi_tri, sorted(vi_tri), "6 mục phải đúng thứ tự")

    def test_bao_cao_json_du_khoa(self):
        self.state_day_du()
        du_lieu = self.json_ra()
        for khoa in ("slug", "phase", "ket_luan", "ca_lech", "lenh_va", "bang_chung"):
            self.assertIn(khoa, du_lieu)

    def test_khuon_bao_cao_file_reference_du_6_muc(self):
        path = os.path.join(SKILL_DIR, "references", "report-template.md")
        noi_dung = doc(path)
        for muc in MUC_BAO_CAO:
            self.assertIn(muc, noi_dung, f"khuôn thiếu mục {muc}")


class LenhVa(TempRepo):

    def test_lenh_va_chi_thuoc_hai_ho_set_va_approve(self):
        self.state_day_du(started_at=None, phase_history=[], spec_approved_by="")
        for lenh in self.json_ra()["lenh_va"]:
            self.assertIn("tdq_state.py", lenh)
            self.assertRegex(lenh, r"tdq_state\.py (set|approve) ")
            for cam in (" init ", " reset", " rm ", ">", " mv "):
                self.assertNotIn(cam, lenh, f"lệnh vá chứa từ cấm: {lenh}")

    # QC1.3: danh sách đen lọt quá nhiều. Đây là danh sách những gì PHẢI bị chặn.
    LENH_CAM = (
        "tdq_state.py init 2026-01-01-0900-x full",
        "tdq_state.py reset",
        "rm -rf docs/tdq",
        "python3 scripts/tdq_state.py set phase=qc >docs/x.md",
        "python3 scripts/tdq_state.py set phase=qc>docs/x.md",
        "python3 scripts/tdq_state.py set phase=qc;mv docs/tdq /tmp",
        "python3 scripts/tdq_state.py set phase=qc && git checkout -- docs/tdq",
        "python3 scripts/tdq_state.py set phase=qc | truncate -s 0 docs/tdq/state.json",
        "python3 scripts/tdq_state.py set phase=qc $(rm -rf docs)",
        "python3 scripts/tdq_state.py set phase=qc\nrm -rf docs",
        "python3 scripts/tdq_state.py approve spec --by \"a\" ; rm -rf docs",
        "python3 scripts/tdq_state.py phases-doc",
    )
    LENH_CHO_QUA = (
        "python3 scripts/tdq_state.py set phase=qc",
        "python3 scripts/tdq_state.py set schema_version=4",
        "python3 scripts/tdq_state.py set started_at=2026-08-16T09:00:00+07:00",
        "python3 scripts/tdq_state.py approve spec --by \"duyệt spec a\"",
        "python3 scripts/tdq_state.py approve plan --by \"duyệt plan inline mode\"",
    )

    def test_lenh_va_chan_mau_lenh_nguy_hiem(self):
        sys.path.insert(0, os.path.join(ROOT, "scripts"))
        import tdq_checkstatus
        for xau in self.LENH_CAM:
            with self.subTest(cam=xau):
                with self.assertRaises(ValueError):
                    tdq_checkstatus.kiem_lenh_va(xau)

    def test_lenh_va_khong_chan_oan_lenh_hop_le(self):
        sys.path.insert(0, os.path.join(ROOT, "scripts"))
        import tdq_checkstatus
        for xau in self.LENH_CHO_QUA:
            with self.subTest(qua=xau):
                self.assertEqual(tdq_checkstatus.kiem_lenh_va(xau), xau)

    def test_lenh_va_khong_chan_oan_gia_tri_chua_tu_khoa(self):
        """Giá trị chứa chữ "init"/"reset" là dữ liệu, không phải lệnh con."""
        sys.path.insert(0, os.path.join(ROOT, "scripts"))
        import tdq_checkstatus
        lenh = "python3 scripts/tdq_state.py approve spec --by \"duyệt, reset lại cũng ok\""
        self.assertEqual(tdq_checkstatus.kiem_lenh_va(lenh), lenh)


# ------------------------------------------------- P4/P5 skill và portable

class SkillVaPortable(unittest.TestCase):

    def test_bang_lech_khop_voi_script(self):
        sys.path.insert(0, os.path.join(ROOT, "scripts"))
        import tdq_checkstatus
        bang = doc(os.path.join(SKILL_DIR, "references", "bang-lech.md"))
        for ma, luat in tdq_checkstatus.CA_LECH.items():
            with self.subTest(ma=ma):
                self.assertIn(ma, bang, f"bảng thiếu {ma}")
                dong = [d for d in bang.splitlines() if d.strip().startswith(f"| {ma} ")]
                self.assertTrue(dong, f"bảng thiếu dòng của {ma}")
                self.assertIn(luat["muc"], dong[0], f"{ma}: mức trong bảng lệch script")

    def test_bang_lech_tro_ve_conventions(self):
        bang = doc(os.path.join(SKILL_DIR, "references", "bang-lech.md"))
        self.assertIn("tdq-conventions", bang)

    def test_status_tro_sang_check_status(self):
        noi_dung = doc(os.path.join(ROOT, "skills", "tdq-status", "SKILL.md"))
        self.assertIn("tdq-check-status", noi_dung)

    def test_khong_dung_lenh_lam_mat_du_lieu(self):
        """Luật cứng của spec §4: skill không được nhắc `init`/`reset`/`rm`."""
        for path in (os.path.join(SKILL_DIR, "SKILL.md"),
                     os.path.join(SKILL_DIR, "references", "bang-lech.md")):
            with self.subTest(path=os.path.basename(path)):
                noi_dung = doc(path)
                for cam in ("tdq_state.py init", "tdq_state.py reset", "rm -rf"):
                    self.assertNotIn(f"`{cam}", noi_dung)


class LogService(TempRepo):

    def test_log_tat_duoc_bang_bien_moi_truong(self):
        self.state_day_du()
        _rc, _out, err = self.chay("report", env={"TDQ_LOG": "0"})
        self.assertEqual(err, "")

    def test_log_bat_mac_dinh_co_timestamp(self):
        self.state_day_du()
        _rc, _out, err = self.chay("report", env={"TDQ_LOG": "1"})
        self.assertTrue(err.startswith("["), err)


if __name__ == "__main__":
    unittest.main()
