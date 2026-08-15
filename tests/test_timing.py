"""Slug có giờ phút + đếm thời gian mỗi request/phase.

Khoá hành vi của request 2026-08-15-1207-gio-phut-dem-thoi-gian:
  - `parse_slug` đọc được CẢ HAI định dạng slug (cũ chỉ ngày, mới có giờ phút);
  - `init` từ chối slug ghi mới thiếu giờ phút;
  - `state.json` giữ mốc mở request và lịch sử phase;
  - `tdq_timing.py` dựng bảng thời gian hai cột và đóng sổ vào timing.jsonl.
"""
import json
import os
import tempfile
import unittest

import helper  # noqa: F401  — nạp sys.path cho scripts/
from helper import read_state, run_state_cli
import tdq_state


class TempRepo(unittest.TestCase):
    """Mỗi test một project rỗng — state thật của repo không bị đụng tới."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.cwd = self._tmp.name

    def tearDown(self):
        self._tmp.cleanup()

    def viet_state_tho(self, **fields):
        """Ghi thẳng state.json dạng THÔ (không qua default_state) — mô phỏng file
        do bản cũ sinh ra, thiếu hẳn field mới."""
        path = os.path.join(self.cwd, "docs", "tdq", "state.json")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(fields, f, ensure_ascii=False)
        return path


class ParseSlug(unittest.TestCase):
    def test_parse_slug_cu(self):
        """Slug cũ (chỉ ngày) vẫn đọc được — 269 file tài liệu cũ giữ nguyên tên."""
        got = tdq_state.parse_slug("2026-08-04-export-claude-setup")
        self.assertEqual(got, ("2026-08-04", None, "export-claude-setup"))

    def test_parse_slug_moi(self):
        got = tdq_state.parse_slug("2026-08-15-1207-gio-phut-dem-thoi-gian")
        self.assertEqual(got, ("2026-08-15", "1207", "gio-phut-dem-thoi-gian"))

    def test_parse_slug_sai(self):
        for bad in ("", "khong-co-ngay", "2026-8-15-thieu-so-0", "2026-08-15",
                    "2026-13-40-ngay-khong-co-that", None):
            with self.subTest(slug=bad):
                self.assertIsNone(tdq_state.parse_slug(bad))

    def test_parse_slug_bon_so_khong_phai_gio(self):
        """Phần chữ bắt đầu bằng 4 chữ số nhưng không phải giờ hợp lệ → coi là chữ."""
        got = tdq_state.parse_slug("2026-08-15-9999-viec-gi-do")
        self.assertEqual(got, ("2026-08-15", None, "9999-viec-gi-do"))


class InitSlug(TempRepo):
    def test_init_bat_buoc_gio_phut(self):
        """Ghi mới mà thiếu giờ phút → từ chối, và nói đúng công thức phải dùng."""
        rc, _out, err = run_state_cli(self.cwd, "init", "2026-08-15-thieu-gio", "full")
        self.assertNotEqual(rc, 0)
        self.assertIn(tdq_state.SLUG_FORMULA, err)
        self.assertIsNone(read_state(self.cwd))

    def test_init_bat_buoc_nhan_slug_moi(self):
        rc, _out, _err = run_state_cli(self.cwd, "init", "2026-08-15-1207-co-gio", "full")
        self.assertEqual(rc, 0)
        self.assertEqual(read_state(self.cwd)["active_request"], "2026-08-15-1207-co-gio")


class MocThoiGianTrongState(TempRepo):
    def test_state_cu_duoc_va_field_thieu(self):
        """State bản cũ (schema 3, không có mốc nào) vẫn đọc được, không mất dữ liệu."""
        self.viet_state_tho(schema_version=3, active_request="2026-08-04-demo",
                            lane="full", phase="spec")
        state = read_state(self.cwd)
        self.assertEqual(state["schema_version"], 4)
        self.assertEqual(state["active_request"], "2026-08-04-demo")   # slug cũ giữ nguyên
        self.assertIsNone(state["started_at"])
        self.assertEqual(state["phase_history"], [])

    def test_state_cu_phase_history_hong_thi_bo_qua(self):
        """`phase_history` sai kiểu → coi như rỗng, không làm gãy lệnh nào."""
        self.viet_state_tho(schema_version=3, phase_history="không phải list")
        self.assertEqual(read_state(self.cwd)["phase_history"], [])

    def test_init_dong_dau_started_at(self):
        rc, _out, _err = run_state_cli(self.cwd, "init", "2026-08-15-1300-viec-moi", "full")
        self.assertEqual(rc, 0)
        state = read_state(self.cwd)
        self.assertTrue(state["started_at"], "init phải đóng dấu mốc mở request")
        self.assertEqual([m["phase"] for m in state["phase_history"]], ["idle"])

    def test_phase_history_ghi_moi_lan_doi_phase(self):
        run_state_cli(self.cwd, "init", "2026-08-15-1300-viec-moi", "full")
        for phase in ("analyze", "spec", "plan"):
            run_state_cli(self.cwd, "set", f"phase={phase}")
        moc = read_state(self.cwd)["phase_history"]
        self.assertEqual([m["phase"] for m in moc], ["idle", "analyze", "spec", "plan"])
        for m in moc:
            self.assertTrue(m["at"], "mỗi mốc phải có thời điểm")
        self.assertEqual(sorted(m["at"] for m in moc), [m["at"] for m in moc])

    def test_phase_history_khong_ghi_khi_phase_khong_doi(self):
        """Set lại đúng phase đang đứng không đẻ mốc rác — nếu không, bảng thời gian
        sẽ đầy những khoảng 0 giây."""
        run_state_cli(self.cwd, "init", "2026-08-15-1300-viec-moi", "full")
        run_state_cli(self.cwd, "set", "phase=spec")
        run_state_cli(self.cwd, "set", "phase=spec")
        self.assertEqual([m["phase"] for m in read_state(self.cwd)["phase_history"]],
                         ["idle", "spec"])

    def test_phase_history_quay_lui_ghi_them_moc(self):
        """Quay lại phase cũ PHẢI đẻ mốc mới — đó là cơ sở đếm 'số lần vào'."""
        run_state_cli(self.cwd, "init", "2026-08-15-1300-viec-moi", "full")
        for phase in ("spec", "plan", "spec"):
            run_state_cli(self.cwd, "set", f"phase={phase}")
        self.assertEqual([m["phase"] for m in read_state(self.cwd)["phase_history"]],
                         ["idle", "spec", "plan", "spec"])


def moc(phase, hh, mm, ss=0):
    """Một mốc phase vào ngày 2026-08-15, giờ địa phương."""
    return {"phase": phase, "at": f"2026-08-15T{hh:02d}:{mm:02d}:{ss:02d}+07:00"}


def su_kien(hh, mm, ss=0):
    """Một bản ghi transcript của model — chỉ cần timestamp và dấu hiệu là bước model."""
    return {"type": "assistant", "message": {"usage": {"input_tokens": 1}},
            "requestId": f"r{hh}{mm}{ss}", "timestamp": f"2026-08-15T{hh:02d}:{mm:02d}:{ss:02d}+07:00"}


class BangThoiGian(TempRepo):
    """Bảng thời gian: cột treo tường, số lần vào, cột model."""

    def setUp(self):
        super().setUp()
        self.transcript = tempfile.TemporaryDirectory()
        self.addCleanup(self.transcript.cleanup)

    def viet_transcript(self, *events, ten="phien.jsonl"):
        path = os.path.join(self.transcript.name, ten)
        with open(path, "w", encoding="utf-8") as f:
            for e in events:
                f.write(json.dumps(e, ensure_ascii=False) + "\n")
        return path

    def chay(self, *args, transcript=True):
        extra = ("--transcript-dir", self.transcript.name) if transcript else ()
        return helper.run_timing_cli(self.cwd, *args, *extra)

    def test_bang_thoi_gian_co_du_cot(self):
        helper.write_state(self.cwd, active_request="2026-08-15-0900-viec",
                           lane="full", phase="plan",
                           started_at="2026-08-15T09:00:00+07:00",
                           phase_history=[moc("idle", 9, 0), moc("spec", 9, 10),
                                          moc("plan", 9, 40)])
        rc, out, _err = self.chay("show", "--now", "2026-08-15T10:00:00+07:00")
        self.assertEqual(rc, 0)
        for cot in ("Phase", "Treo tường", "Model", "Số lần"):
            self.assertIn(cot, out)
        self.assertIn("spec", out)
        self.assertIn("30 phút", out)          # spec 09:10 → 09:40
        self.assertIn("1 giờ", out)            # tổng 09:00 → 10:00

    def test_quay_lui_cong_don_va_dem_so_lan(self):
        helper.write_state(self.cwd, active_request="2026-08-15-0900-viec", lane="full",
                           phase="spec", started_at="2026-08-15T09:00:00+07:00",
                           phase_history=[moc("spec", 9, 0), moc("plan", 9, 20),
                                          moc("spec", 9, 30)])
        rc, out, _err = self.chay("show", "--now", "2026-08-15T09:34:00+07:00")
        self.assertEqual(rc, 0)
        dong = [d for d in out.splitlines() if d.strip().startswith("| spec")]
        self.assertEqual(len(dong), 1, f"spec phải gộp thành MỘT dòng, có: {dong}")
        self.assertIn("24 phút", dong[0])      # 20 phút + 4 phút
        self.assertIn("2", dong[0])            # vào 2 lần

    def test_thoi_gian_model_lay_tu_transcript(self):
        """Cột model chỉ cộng khoảng cách giữa các bước model NẰM TRONG cửa sổ phase."""
        helper.write_state(self.cwd, active_request="2026-08-15-0900-viec", lane="full",
                           phase="spec", started_at="2026-08-15T09:00:00+07:00",
                           phase_history=[moc("spec", 9, 0)])
        self.viet_transcript(su_kien(9, 0), su_kien(9, 1), su_kien(9, 3))
        rc, out, _err = self.chay("show", "--now", "2026-08-15T10:00:00+07:00", "--json")
        self.assertEqual(rc, 0)
        so_lieu = json.loads(out)
        spec = [p for p in so_lieu["phases"] if p["phase"] == "spec"][0]
        self.assertEqual(spec["treo_tuong_giay"], 3600)
        self.assertEqual(spec["model_giay"], 180)   # 1 phút + 2 phút, không tính giờ chờ

    def test_tong_model_do_tren_ca_cua_so_request(self):
        """Hai tổng phải cùng một cửa sổ: started_at → lúc chốt, kể cả khi mốc phase
        bắt đầu muộn hơn (state cũ được vá started_at về sau)."""
        helper.write_state(self.cwd, active_request="2026-08-15-0900-viec", lane="full",
                           phase="qc", started_at="2026-08-15T09:00:00+07:00",
                           phase_history=[moc("qc", 9, 30)])
        self.viet_transcript(su_kien(9, 5), su_kien(9, 7),      # ngoài mọi cửa sổ phase
                             su_kien(9, 31), su_kien(9, 32))    # trong cửa sổ qc
        rc, out, _err = self.chay("show", "--now", "2026-08-15T09:40:00+07:00", "--json")
        self.assertEqual(rc, 0)
        so_lieu = json.loads(out)
        qc = [p for p in so_lieu["phases"] if p["phase"] == "qc"][0]
        self.assertEqual(qc["model_giay"], 60)
        self.assertEqual(so_lieu["treo_tuong_giay"], 2400)      # 09:00 → 09:40
        self.assertEqual(so_lieu["model_giay"], 180)            # 120 + 60, không chỉ 60

    def test_nguong_cho_dai_khong_tinh_vao_model(self):
        helper.write_state(self.cwd, active_request="2026-08-15-0900-viec", lane="full",
                           phase="spec", started_at="2026-08-15T09:00:00+07:00",
                           phase_history=[moc("spec", 9, 0)])
        # 9:00 → 9:02 là model chạy; 9:02 → 9:30 là user đi vắng (> MAX_GAP_SECONDS)
        self.viet_transcript(su_kien(9, 0), su_kien(9, 2), su_kien(9, 30))
        rc, out, _err = self.chay("show", "--now", "2026-08-15T10:00:00+07:00", "--json")
        self.assertEqual(rc, 0)
        spec = [p for p in json.loads(out)["phases"] if p["phase"] == "spec"][0]
        self.assertEqual(spec["model_giay"], 120)

    def test_khong_transcript_thi_gach_ngang_va_van_thoat_0(self):
        helper.write_state(self.cwd, active_request="2026-08-15-0900-viec", lane="full",
                           phase="spec", started_at="2026-08-15T09:00:00+07:00",
                           phase_history=[moc("spec", 9, 0)])
        rc, out, err = helper.run_timing_cli(
            self.cwd, "show", "--now", "2026-08-15T10:00:00+07:00",
            "--transcript-dir", os.path.join(self.cwd, "khong-ton-tai"))
        self.assertEqual(rc, 0)
        self.assertIn("—", out)
        self.assertIn("transcript", (out + err).lower())

    def test_khong_co_request_thi_noi_ro_va_thoat_0(self):
        rc, out, err = self.chay("show")
        self.assertEqual(rc, 0)
        self.assertIn("request", (out + err).lower())


class DongSo(TempRepo):
    def test_dong_so_ghi_dung_mot_dong_jsonl(self):
        helper.write_state(self.cwd, active_request="2026-08-15-0900-viec", lane="full",
                           phase="report", started_at="2026-08-15T09:00:00+07:00",
                           phase_history=[moc("spec", 9, 0), moc("report", 9, 30)])
        rc, _out, _err = helper.run_timing_cli(self.cwd, "close",
                                               "--now", "2026-08-15T10:00:00+07:00")
        self.assertEqual(rc, 0)
        path = os.path.join(self.cwd, "docs", "tdq", "timing.jsonl")
        with open(path, encoding="utf-8") as f:
            dong = [d for d in f.read().splitlines() if d.strip()]
        self.assertEqual(len(dong), 1)
        ban_ghi = json.loads(dong[0])
        self.assertEqual(ban_ghi["slug"], "2026-08-15-0900-viec")
        self.assertEqual(ban_ghi["lane"], "full")
        self.assertEqual(ban_ghi["started_at"], "2026-08-15T09:00:00+07:00")
        self.assertEqual(ban_ghi["closed_at"], "2026-08-15T10:00:00+07:00")
        self.assertEqual(ban_ghi["treo_tuong_giay"], 3600)
        self.assertIn("phases", ban_ghi)

    def test_dong_so_hai_lan_khong_ghi_trung(self):
        """Đóng sổ lần hai cho cùng request không đẻ dòng thứ hai — nếu không, số liệu
        của một request bị đếm hai lần khi `init` và `tdq_finish` cùng gọi."""
        helper.write_state(self.cwd, active_request="2026-08-15-0900-viec", lane="full",
                           phase="report", started_at="2026-08-15T09:00:00+07:00",
                           phase_history=[moc("spec", 9, 0)])
        helper.run_timing_cli(self.cwd, "close", "--now", "2026-08-15T10:00:00+07:00")
        helper.run_timing_cli(self.cwd, "close", "--now", "2026-08-15T10:05:00+07:00")
        path = os.path.join(self.cwd, "docs", "tdq", "timing.jsonl")
        with open(path, encoding="utf-8") as f:
            self.assertEqual(len([d for d in f.read().splitlines() if d.strip()]), 1)

    def test_dong_so_khong_co_request_thi_im_lang(self):
        rc, _out, _err = helper.run_timing_cli(self.cwd, "close")
        self.assertEqual(rc, 0)
        self.assertFalse(os.path.exists(os.path.join(self.cwd, "docs", "tdq", "timing.jsonl")))


class NoiVaoWorkflow(TempRepo):
    """Đóng sổ phải tự xảy ra ở hai cửa: mở request mới, và đóng request cũ."""

    def doc_timing(self):
        path = os.path.join(self.cwd, "docs", "tdq", "timing.jsonl")
        if not os.path.exists(path):
            return []
        with open(path, encoding="utf-8") as f:
            return [json.loads(d) for d in f.read().splitlines() if d.strip()]

    def test_init_dong_so_request_cu_truoc_khi_reset(self):
        """`init` xoá sạch state — không đóng sổ trước thì lịch sử thời gian bay mất."""
        run_state_cli(self.cwd, "init", "2026-08-15-0900-viec-cu", "full")
        run_state_cli(self.cwd, "set", "phase=spec")
        run_state_cli(self.cwd, "init", "2026-08-15-1000-viec-moi", "quick")
        ban_ghi = self.doc_timing()
        self.assertEqual([b["slug"] for b in ban_ghi], ["2026-08-15-0900-viec-cu"])
        self.assertEqual(ban_ghi[0]["lane"], "full")

    def test_init_lan_dau_khong_ghi_gi(self):
        run_state_cli(self.cwd, "init", "2026-08-15-0900-viec-dau", "full")
        self.assertEqual(self.doc_timing(), [])

    def test_finish_dong_so_khi_ve_idle(self):
        run_state_cli(self.cwd, "init", "2026-08-15-0900-viec", "full")
        rc, out, err = helper.run_finish_cli(self.cwd, "--phase", "idle",
                                             "--skip-graphify", "--log", "thử đóng sổ")
        self.assertEqual(rc, 0, err)
        self.assertEqual([b["slug"] for b in self.doc_timing()], ["2026-08-15-0900-viec"])
        self.assertIn("thời gian", (out + err).lower())

    def test_finish_phase_khac_idle_khong_dong_so(self):
        run_state_cli(self.cwd, "init", "2026-08-15-0900-viec", "full")
        helper.run_finish_cli(self.cwd, "--phase", "qc", "--skip-graphify", "--log", "chưa xong")
        self.assertEqual(self.doc_timing(), [])


class LuatVaKhuon(unittest.TestCase):
    """Luật trong skill/tài liệu phải nói đúng chuẩn mới — người đọc luật là model."""

    def doc(self, *phan):
        with open(os.path.join(helper.ROOT, *phan), encoding="utf-8") as f:
            return f.read()

    def test_khuon_report_co_bang_thoi_gian(self):
        noi_dung = self.doc("skills", "tdq-build", "references", "report-template.md")
        self.assertIn("tdq_timing.py show", noi_dung)
        self.assertIn("Treo tường", noi_dung)

    def test_status_co_dong_dong_ho(self):
        noi_dung = self.doc("skills", "tdq-status", "SKILL.md")
        self.assertIn("tdq_timing.py status", noi_dung)

    def test_cong_thuc_slug_moi_o_moi_noi(self):
        """Mọi chỗ in công thức slug phải có HHMM — sót một chỗ là chuẩn mới trôi."""
        import subprocess
        out = subprocess.run(
            ["grep", "-rnI", "YYYY-MM-DD-", "skills", "scripts", "portable",
             os.path.join("docs", "tdq", "STATE.md")],
            cwd=helper.ROOT, capture_output=True, text=True).stdout
        thieu = [d for d in out.splitlines() if "HHMM" not in d]
        self.assertEqual(thieu, [], f"Còn {len(thieu)} chỗ in công thức slug cũ")

    def test_portable_dong_bo_voi_skill(self):
        self.assertIn("YYYY-MM-DD-HHMM-", self.doc("portable", "AGENTS.md"))
        self.assertIn("YYYY-MM-DD-HHMM-", self.doc("portable", "workflow", "01-intake.md"))


class LogService(TempRepo):
    def test_tat_log_bang_bien_moi_truong(self):
        helper.write_state(self.cwd, active_request="2026-08-15-0900-viec", lane="full",
                           phase="spec", started_at="2026-08-15T09:00:00+07:00",
                           phase_history=[moc("spec", 9, 0)])
        _rc, _out, err = helper.run_timing_cli(self.cwd, "show", env={"TDQ_LOG": "0"})
        self.assertEqual(err, "")
        _rc, _out, err_bat = helper.run_timing_cli(self.cwd, "show", env={"TDQ_LOG": "1"})
        self.assertTrue(err_bat, "log mặc định phải BẬT")


if __name__ == "__main__":
    unittest.main()
