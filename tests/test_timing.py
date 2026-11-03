"""Slug có giờ phút + đếm thời gian mỗi request/phase.

Khoá hành vi của request 2026-08-15-1207-gio-phut-dem-thoi-gian:
  - `parse_slug` đọc được CẢ HAI định dạng slug (cũ chỉ ngày, mới có giờ phút);
  - `init` từ chối slug ghi mới thiếu giờ phút;
  - `state.json` giữ mốc mở request và lịch sử phase;
  - `tdq_timing.py` dựng bảng thời gian hai cột và đóng sổ vào timing.jsonl.
"""
import contextlib
import datetime
import io
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import helper  # noqa: F401  — nạp sys.path cho scripts/
from helper import read_state, run_state_cli
import tdq_state
import tdq_timing


def duyet_spec(cwd):
    """Cổng vào pha `plan` đòi spec đã duyệt — mở sẵn để test đo được mốc thời gian."""
    run_state_cli(cwd, "set", "spec_file=docs/tdq/spec/x.md")
    run_state_cli(cwd, "approve", "spec", "--by", "duyệt spec")


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
        # Số hiệu schema lấy từ chính default_state() — mỗi lần nâng schema không
        # phải sửa lại ca test này, mà vẫn khoá đúng lời hứa "nạp là nâng".
        self.assertEqual(state["schema_version"],
                         tdq_state.default_state()["schema_version"])
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
        duyet_spec(self.cwd)
        for phase in ("analyze", "spec", "plan"):
            run_state_cli(self.cwd, "set", f"phase={phase}")
        moc = read_state(self.cwd)["phase_history"]
        self.assertEqual([m["phase"] for m in moc],
                         ["idle", "analyze", "spec", "plan"])
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
        duyet_spec(self.cwd)
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
        for cot in ("Phase", "Wall clock", "Model", "Times entered"):
            self.assertIn(cot, out)
        self.assertIn("spec", out)
        self.assertIn("30 min", out)           # spec 09:10 → 09:40
        self.assertIn("1h", out)               # tổng 09:00 → 10:00

    def test_quay_lui_cong_don_va_dem_so_lan(self):
        helper.write_state(self.cwd, active_request="2026-08-15-0900-viec", lane="full",
                           phase="spec", started_at="2026-08-15T09:00:00+07:00",
                           phase_history=[moc("spec", 9, 0), moc("plan", 9, 20),
                                          moc("spec", 9, 30)])
        rc, out, _err = self.chay("show", "--now", "2026-08-15T09:34:00+07:00")
        self.assertEqual(rc, 0)
        dong = [d for d in out.splitlines() if d.strip().startswith("| spec")]
        self.assertEqual(len(dong), 1, f"spec phải gộp thành MỘT dòng, có: {dong}")
        self.assertIn("24 min", dong[0])       # 20 phút + 4 phút
        self.assertIn("2", dong[0])            # vào 2 lần

    def test_assistant_gap_cannot_be_presented_as_model(self):
        """Assistant timestamps alone do not establish model compute time."""
        helper.write_state(self.cwd, active_request="2026-08-15-0900-viec", lane="full",
                           phase="spec", started_at="2026-08-15T09:00:00+07:00",
                           phase_history=[moc("spec", 9, 0)])
        self.viet_transcript(su_kien(9, 0), su_kien(9, 1), su_kien(9, 3))
        rc, out, _err = self.chay("show", "--now", "2026-08-15T10:00:00+07:00", "--json")
        self.assertEqual(rc, 0)
        so_lieu = json.loads(out)
        spec = [p for p in so_lieu["phases"] if p["phase"] == "spec"][0]
        self.assertEqual(spec["treo_tuong_giay"], 3600)
        self.assertIsNone(spec["model_giay"])

    def test_request_wall_window_does_not_infer_model(self):
        """The whole request retains wall time even with incomplete phase coverage."""
        helper.write_state(self.cwd, active_request="2026-08-15-0900-viec", lane="full",
                           phase="qc", started_at="2026-08-15T09:00:00+07:00",
                           phase_history=[moc("qc", 9, 30)])
        self.viet_transcript(su_kien(9, 5), su_kien(9, 7),      # ngoài mọi cửa sổ phase
                             su_kien(9, 31), su_kien(9, 32))    # trong cửa sổ qc
        rc, out, _err = self.chay("show", "--now", "2026-08-15T09:40:00+07:00", "--json")
        self.assertEqual(rc, 0)
        so_lieu = json.loads(out)
        qc = [p for p in so_lieu["phases"] if p["phase"] == "qc"][0]
        self.assertIsNone(qc["model_giay"])
        self.assertEqual(so_lieu["treo_tuong_giay"], 2400)      # 09:00 → 09:40
        self.assertIsNone(so_lieu["model_giay"])

    def test_long_gap_does_not_identify_user_absence(self):
        helper.write_state(self.cwd, active_request="2026-08-15-0900-viec", lane="full",
                           phase="spec", started_at="2026-08-15T09:00:00+07:00",
                           phase_history=[moc("spec", 9, 0)])
        # Neither short nor long gaps prove model compute time or user absence.
        self.viet_transcript(su_kien(9, 0), su_kien(9, 2), su_kien(9, 30))
        rc, out, _err = self.chay("show", "--now", "2026-08-15T10:00:00+07:00", "--json")
        self.assertEqual(rc, 0)
        spec = [p for p in json.loads(out)["phases"] if p["phase"] == "spec"][0]
        self.assertIsNone(spec["model_giay"])

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
        # 2026-09-28: cờ `--skip-graphify` bị gỡ hẳn — chính nó làm đồ thị cũ 8 ngày. Hai ca này
        # chạy trên thư mục tạm không có file code nào, nên bước graphify tự `skip`.
        rc, out, err = helper.run_finish_cli(self.cwd, "--phase", "idle",
                                             "--log", "thử đóng sổ")
        self.assertEqual(rc, 0, err)
        self.assertEqual([b["slug"] for b in self.doc_timing()], ["2026-08-15-0900-viec"])
        self.assertIn("timing", (out + err).lower())

    def test_finish_phase_khac_idle_khong_dong_so(self):
        run_state_cli(self.cwd, "init", "2026-08-15-0900-viec", "full")
        helper.run_finish_cli(self.cwd, "--phase", "qc", "--log", "chưa xong")
        self.assertEqual(self.doc_timing(), [])


class LuatVaKhuon(unittest.TestCase):
    """Luật trong skill/tài liệu phải nói đúng chuẩn mới — người đọc luật là model."""

    def doc(self, *phan):
        with open(os.path.join(helper.ROOT, *phan), encoding="utf-8") as f:
            return f.read()

    def test_khuon_report_co_bang_thoi_gian(self):
        noi_dung = self.doc("skills", "tdq-build", "references", "report-template.md")
        self.assertIn("tdq_timing.py show", noi_dung)
        self.assertIn("Wall clock", noi_dung)

    def test_status_co_dong_dong_ho(self):
        noi_dung = self.doc("skills", "tdq-status", "SKILL.md")
        self.assertIn("tdq_timing.py status", noi_dung)

    def test_cong_thuc_slug_moi_o_moi_noi(self):
        """Mọi chỗ in công thức slug phải có HHMM — sót một chỗ là chuẩn mới trôi."""
        # Tương đương `grep -rnI YYYY-MM-DD- …` viết bằng Python: `grep` chỉ có trong PATH của
        # Git Bash, gọi từ cmd/PowerShell thì ca này vỡ vì lý do sai.
        def cac_file(goc):
            if os.path.isfile(goc):
                yield goc
            for thu_muc, _con, ten_file in os.walk(goc):
                for ten in ten_file:
                    yield os.path.join(thu_muc, ten)

        out = []
        for goc in ("skills", "scripts", "portable_src", os.path.join("docs", "tdq", "STATE.md")):
            for duong in cac_file(os.path.join(helper.ROOT, goc)):
                with open(duong, "rb") as f:
                    du_lieu = f.read()
                if b"\0" in du_lieu:  # -I: bỏ file nhị phân
                    continue
                for so, dong in enumerate(du_lieu.decode("utf-8", "replace").splitlines(), 1):
                    if "YYYY-MM-DD-" in dong:
                        out.append(f"{os.path.relpath(duong, helper.ROOT)}:{so}:{dong}")
        thieu = [d for d in out if "HHMM" not in d]
        self.assertEqual(thieu, [], f"Còn {len(thieu)} chỗ in công thức slug cũ")


class LogService(TempRepo):
    def test_tat_log_bang_bien_moi_truong(self):
        helper.write_state(self.cwd, active_request="2026-08-15-0900-viec", lane="full",
                           phase="spec", started_at="2026-08-15T09:00:00+07:00",
                           phase_history=[moc("spec", 9, 0)])
        _rc, _out, err = helper.run_timing_cli(self.cwd, "show", env={"TDQ_LOG": "0"})
        self.assertEqual(err, "")
        _rc, _out, err_bat = helper.run_timing_cli(self.cwd, "show", env={"TDQ_LOG": "1"})
        self.assertTrue(err_bat, "log mặc định phải BẬT")


BASE = datetime.datetime(2026, 10, 27, tzinfo=datetime.timezone.utc)


def at_second(seconds):
    return (BASE + datetime.timedelta(seconds=seconds)).isoformat()


class TimingV2(TempRepo):
    def setUp(self):
        super().setUp()
        self.logs = Path(self.cwd) / "logs"
        self.logs.mkdir()
        self.state = {"active_request": "2026-10-27-0000-fixture", "lane": "full",
                      "phase": "implement", "started_at": at_second(0),
                      "phase_history": [{"phase": "analyze", "at": at_second(0)},
                                        {"phase": "implement", "at": at_second(10)}]}
        self.quiet = patch.dict(os.environ, {"TDQ_LOG": "0"})
        self.quiet.start()
        self.addCleanup(self.quiet.stop)

    def event(self, event_type, seconds, **fields):
        return {"type": event_type, "timestamp": at_second(seconds),
                "cwd": self.cwd, "sessionId": "session", **fields}

    def api(self, start, end, identity="request", final=True):
        return [self.event("api-request", start, id=identity),
                self.event("assistant", end, requestRef=identity, uuid=identity + "-reply",
                           message={"content": [], "stop_reason": "end_turn" if final else None})]

    def tool(self, start, end, identity="tool", output="synthetic"):
        return [self.event("assistant", start, message={"content": [
            {"type": "tool_use", "id": identity, "name": "Read", "input": {}}]}),
            self.event("user", end, message={"content": [
                {"type": "tool_result", "tool_use_id": identity, "content": output}]})]

    def write(self, records, name="session.jsonl"):
        path = self.logs / name
        path.write_text("".join(json.dumps(record) + "\n" for record in records), encoding="utf-8")
        return path

    def measure(self, records, end=20, **kwargs):
        self.write(records)
        return tdq_timing.tong_hop(self.state, BASE + datetime.timedelta(seconds=end),
                                  self.logs, project_dir=self.cwd, **kwargs)

    def number(self, data, metric):
        return data["metrics"][metric]["seconds"]

    def test_known_overlap_and_phase_clipping(self):
        data = self.measure(self.api(0, 10) + self.tool(5, 15))
        self.assertEqual(data["schema_version"], 2)
        self.assertEqual(data["treo_tuong_giay"], 20)
        expected = {"api_request_seconds": 10, "tool_call_seconds": 10,
                    "background_job_seconds": None, "observed_union_seconds": 15,
                    "unattributed_seconds": 5}
        self.assertEqual({key: value["seconds"] for key, value in data["metrics"].items()}, expected)
        self.assertIsNone(data["model_giay"])
        analyze, implement = data["phases"]
        self.assertEqual(self.number(analyze, "tool_call_seconds"), 5)
        self.assertEqual(self.number(implement, "tool_call_seconds"), 5)
        self.assertEqual(self.number(analyze, "observed_union_seconds"), 10)
        self.assertEqual(self.number(implement, "observed_union_seconds"), 5)
        self.assertEqual(self.number(implement, "api_request_seconds"), 0)
        self.assertIsNone(analyze["model_giay"])
        self.assertEqual(data["metrics"]["observed_union_seconds"]["quality"], "complete")

    def test_same_kind_overlap_is_merged_before_cross_kind_union(self):
        data = self.measure(self.api(0, 10, "one") + self.api(8, 12, "two") + self.tool(10, 20), end=30)
        self.assertEqual(self.number(data, "api_request_seconds"), 12)
        self.assertEqual(self.number(data, "tool_call_seconds"), 10)
        self.assertEqual(self.number(data, "observed_union_seconds"), 20)
        self.assertEqual(self.number(data, "unattributed_seconds"), 10)

    def test_long_span_is_retained_without_300_second_threshold(self):
        data = self.measure(self.api(0, 600), end=620)
        self.assertEqual(self.number(data, "api_request_seconds"), 600)
        self.assertEqual(self.number(data, "unattributed_seconds"), 20)
        self.assertIsNone(data["model_giay"])

    def test_spans_are_clipped_at_both_request_boundaries(self):
        data = self.measure(self.api(-5, 25))
        self.assertEqual(self.number(data, "api_request_seconds"), 20)
        self.assertEqual([self.number(row, "api_request_seconds") for row in data["phases"]], [10, 10])

    def test_half_open_window_excludes_boundary_only_intervals(self):
        data = self.measure(self.api(-5, 0) + self.tool(20, 30))
        self.assertEqual(self.number(data, "observed_union_seconds"), 0)
        self.assertEqual(self.number(data, "unattributed_seconds"), 20)

    def test_repeated_phase_accumulates_duration_and_entry_count(self):
        self.state["phase_history"] = [{"phase": phase, "at": at_second(at)}
                                       for phase, at in [("analyze", 0), ("implement", 5), ("analyze", 10)]]
        data = self.measure(self.api(0, 20))
        analyze = data["phases"][0]
        self.assertEqual(analyze["so_lan"], 2)
        self.assertEqual(analyze["treo_tuong_giay"], 15)
        self.assertEqual(self.number(analyze, "api_request_seconds"), 15)
        self.assertEqual(data["current_phase"], "analyze")
        self.assertTrue(tdq_timing.dong_ho_ngan(data).startswith("⏱ analyze"))

    def test_total_uses_request_window_even_before_first_phase(self):
        self.state["phase_history"] = [{"phase": "qc", "at": at_second(10)}]
        data = self.measure(self.api(1, 4) + self.tool(12, 15))
        self.assertEqual(self.number(data, "observed_union_seconds"), 6)
        self.assertEqual(self.number(data["phases"][0], "observed_union_seconds"), 3)

    def test_phases_before_request_are_clipped(self):
        self.state["started_at"] = at_second(5)
        data = self.measure(self.api(0, 20))
        self.assertEqual(data["treo_tuong_giay"], 15)
        self.assertEqual([row["treo_tuong_giay"] for row in data["phases"]], [5, 10])
        self.assertEqual(self.number(data, "observed_union_seconds"), 15)

    def test_phase_ending_at_request_start_is_not_an_entry_inside_window(self):
        self.state["started_at"] = at_second(10)
        data = self.measure(self.api(0, 20))
        self.assertEqual([row["phase"] for row in data["phases"]], ["implement"])
        self.assertEqual(data["phases"][0]["so_lan"], 1)

    def test_fractional_seconds_are_not_rounded_before_aggregation(self):
        self.state["phase_history"] = [{"phase": "analyze", "at": at_second(0)},
                                       {"phase": "implement", "at": at_second(0.4)}]
        data = self.measure(self.api(0.1, 0.8), end=1)
        self.assertAlmostEqual(self.number(data, "api_request_seconds"), 0.7)
        self.assertAlmostEqual(self.number(data["phases"][0], "api_request_seconds"), 0.3)
        self.assertAlmostEqual(self.number(data["phases"][1], "api_request_seconds"), 0.4)
        self.assertAlmostEqual(self.number(data, "unattributed_seconds"), 0.3)

    def test_many_repeated_phases_conserve_observed_time(self):
        self.state["phase_history"] = [{"phase": ("analyze", "implement")[index % 2],
                                        "at": at_second(index)} for index in range(200)]
        data = self.measure(self.api(-1, 201), end=200)
        self.assertEqual(sum(row["so_lan"] for row in data["phases"]), 200)
        self.assertEqual(sum(self.number(row, "api_request_seconds") for row in data["phases"]), 200)

    def test_incomplete_stream_preserves_confirmed_partial_time(self):
        data = self.measure(self.api(0, 5, "complete") + self.api(6, 8, "pending", final=False))
        self.assertEqual(self.number(data, "api_request_seconds"), 5)
        self.assertEqual(data["metrics"]["api_request_seconds"]["quality"], "partial")
        self.assertEqual(data["metrics"]["observed_union_seconds"]["quality"], "partial")
        self.assertEqual(self.number(data, "unattributed_seconds"), 15)

    def test_incomplete_stream_without_valid_spans_does_not_claim_zero(self):
        data = self.measure(self.api(0, 5, final=False))
        self.assertIsNone(self.number(data, "api_request_seconds"))
        self.assertIsNone(self.number(data, "observed_union_seconds"))
        self.assertIsNone(self.number(data, "unattributed_seconds"))
        self.assertEqual(data["metrics"]["api_request_seconds"]["quality"], "partial")

    def test_missing_sources_keep_wall_but_not_fake_zero(self):
        data = self.measure([])
        self.assertEqual(data["treo_tuong_giay"], 20)
        self.assertEqual({value["quality"] for value in data["metrics"].values()}, {"unavailable"})
        self.assertEqual({value["seconds"] for value in data["metrics"].values()}, {None})

    def test_malformed_log_reduces_quality_without_losing_known_span(self):
        path = self.write(self.tool(0, 5))
        with path.open("a", encoding="utf-8") as stream:
            stream.write("{broken\n")
        data = tdq_timing.tong_hop(self.state, BASE + datetime.timedelta(seconds=20),
                                  self.logs, project_dir=self.cwd)
        self.assertEqual(self.number(data, "tool_call_seconds"), 5)
        self.assertEqual(data["metrics"]["tool_call_seconds"]["quality"], "partial")

    def test_background_tool_return_does_not_infer_job_duration(self):
        data = self.measure(self.tool(0, 1, output="Script running with cell ID 12"))
        self.assertEqual(self.number(data, "tool_call_seconds"), 1)
        self.assertIsNone(self.number(data, "background_job_seconds"))
        self.assertEqual(self.number(data, "unattributed_seconds"), 19)

    def test_codex_task_wall_is_not_an_api_span(self):
        records = [{"type": "session_meta", "payload": {"id": "codex", "cwd": self.cwd}},
                   {"type": "event_msg", "timestamp": at_second(0), "payload": {"type": "task_started"}},
                   {"type": "event_msg", "timestamp": at_second(15), "payload": {"type": "task_complete"}}]
        data = self.measure(records)
        self.assertIsNone(self.number(data, "api_request_seconds"))
        self.assertEqual(self.number(data, "tool_call_seconds"), 0)
        self.assertEqual(self.number(data, "observed_union_seconds"), 0)
        self.assertIsNone(data["model_giay"])

    def test_session_filter_controls_attribution(self):
        foreign = [{**record, "sessionId": "other"} for record in self.tool(0, 20)]
        self.write(foreign, "other.jsonl")
        data = self.measure(self.tool(0, 5), session_ids=["session"])
        self.assertEqual(self.number(data, "tool_call_seconds"), 5)
        self.assertEqual(data["attribution"], "session")

    def test_out_of_order_phase_marks_cannot_double_count(self):
        self.state["phase_history"].append({"phase": "qc", "at": at_second(5)})
        data = self.measure(self.api(0, 20))
        self.assertIn("phase_out_of_order", data["diagnostics"])
        self.assertEqual(sum(row["treo_tuong_giay"] for row in data["phases"]), 20)
        self.assertEqual(sum(self.number(row, "api_request_seconds") for row in data["phases"]), 20)
        self.assertEqual(data["phases"][0]["metrics"]["api_request_seconds"]["quality"], "partial")

    def test_bad_phase_mark_types_are_diagnosed(self):
        self.state["phase_history"].extend([None, {"phase": [], "at": at_second(12)},
                                            {"phase": "qc", "at": "2026-10-27T00:00:13"}])
        data = self.measure(self.tool(0, 20))
        self.assertIn("invalid_phase_mark", data["diagnostics"])
        self.assertEqual(len(data["phases"]), 2)

    def test_duplicate_phase_mark_does_not_add_an_entry(self):
        self.state["phase_history"].insert(0, dict(self.state["phase_history"][0]))
        data = self.measure(self.api(0, 20))
        self.assertEqual(data["phases"][0]["so_lan"], 1)
        self.assertIn("duplicate_phase_mark", data["diagnostics"])

    def test_simultaneous_phase_transitions_remain_disjoint(self):
        self.state["phase_history"][1]["at"] = at_second(0)
        data = self.measure(self.api(0, 20))
        self.assertEqual([row["treo_tuong_giay"] for row in data["phases"]], [0, 20])
        self.assertEqual([self.number(row, "api_request_seconds") for row in data["phases"]], [0, 20])

    def test_missing_request_start_does_not_fall_back_to_phase(self):
        self.state["started_at"] = None
        data = self.measure(self.api(0, 20))
        self.assertIsNone(data["treo_tuong_giay"])
        self.assertIsNone(self.number(data, "observed_union_seconds"))
        self.assertIn("invalid_request_window", data["diagnostics"])

    def test_naive_end_or_end_before_start_is_unavailable(self):
        self.write(self.api(0, 20))
        for end in (BASE.replace(tzinfo=None), BASE - datetime.timedelta(seconds=1), None):
            with self.subTest(end=end):
                data = tdq_timing.tong_hop(self.state, end, self.logs, project_dir=self.cwd)
                self.assertIsNone(data["treo_tuong_giay"])
                self.assertIsNone(self.number(data, "unattributed_seconds"))

    def test_invalid_history_is_reported_without_changing_request_measurement(self):
        self.state["phase_history"] = "invalid"
        data = self.measure(self.api(0, 20))
        self.assertEqual(data["phases"], [])
        self.assertIn("invalid_phase_history", data["diagnostics"])
        self.assertEqual(self.number(data, "api_request_seconds"), 20)

    def test_json_markdown_status_preserve_quality_and_meaning(self):
        data = self.measure(self.api(0, 10) + self.tool(5, 15))
        decoded = json.loads(json.dumps(data))
        markdown, status = tdq_timing.bang_markdown(decoded), tdq_timing.dong_ho_ngan(decoded)
        for label in ("API request", "Tool wait", "Background job", "Observed union", "Unattributed"):
            self.assertIn(label, markdown)
            self.assertIn(label, status)
        self.assertIn("15s [complete]", markdown)
        self.assertIn("15s [complete]", status)
        self.assertIn("— [unavailable]", markdown)
        self.assertIn("model_giay=null", markdown)
        self.assertNotIn("\n", status)

    def test_status_includes_current_phase_wall_and_observed_quality(self):
        data = self.measure(self.api(0, 10) + self.tool(5, 15))
        row = data["phases"][1]
        status = tdq_timing.dong_ho_ngan(data)
        self.assertIn("implement (all entries) wall " + tdq_timing.dinh_dang(row["treo_tuong_giay"]), status)
        self.assertIn("phase observed 5s [complete]", status)
        self.assertIn("whole request 20s", status)

    def test_v1_formatter_uses_legacy_label_without_mutating_history(self):
        legacy = {"slug": "old", "lane": "full", "started_at": at_second(0),
                  "treo_tuong_giay": 600, "model_giay": 120,
                  "phases": [{"phase": "spec", "treo_tuong_giay": 600, "model_giay": 120, "so_lan": 1}]}
        before = json.dumps(legacy)
        self.assertIn("legacy assistant-gap estimate", tdq_timing.bang_markdown(legacy))
        self.assertIn("legacy assistant-gap estimate", tdq_timing.dong_ho_ngan(legacy))
        self.assertEqual(json.dumps(legacy), before)

    def test_close_preserves_history_and_uses_request_start_pair(self):
        data = self.measure(self.api(0, 10))
        history = Path(self.cwd) / tdq_timing.TIMING_REL
        history.parent.mkdir(parents=True)
        old = b'{"slug":"old","started_at":"old","model_giay":120}\n[]\n{broken\n'
        history.write_bytes(old)
        self.assertTrue(tdq_timing.dong_so(self.cwd, data))
        first = history.read_bytes()
        self.assertTrue(first.startswith(old))
        self.assertFalse(tdq_timing.dong_so(self.cwd, dict(data, closed_at=at_second(30))))
        self.assertEqual(history.read_bytes(), first)
        self.assertTrue(tdq_timing.dong_so(self.cwd, dict(data, started_at=at_second(1))))

    def init_cli_state(self):
        result = run_state_cli(self.cwd, "init", self.state["active_request"], "full")
        self.assertEqual(result[0], 0, result[2])
        result = run_state_cli(self.cwd, "set", "started_at=" + self.state["started_at"],
                               "phase_history=" + json.dumps(self.state["phase_history"]))
        self.assertEqual(result[0], 0, result[2])

    def test_cli_host_repeatable_sessions_and_status_json(self):
        self.init_cli_state()
        self.write(self.tool(0, 5))
        self.write([{**record, "sessionId": "other"} for record in self.tool(10, 15)], "other.jsonl")
        common = ("--transcript-dir", str(self.logs), "--now", at_second(20), "--host", "claude",
                  "--session-id", "session", "--session-id", "other", "--json")
        show = helper.run_timing_cli(self.cwd, "show", *common)
        status = helper.run_timing_cli(self.cwd, "status", *common)
        self.assertEqual(show[0], 0, show[2])
        self.assertEqual(status[0], 0, status[2])
        self.assertEqual(json.loads(show[1]), json.loads(status[1]))
        self.assertEqual(self.number(json.loads(show[1]), "tool_call_seconds"), 10)
        self.assertEqual(json.loads(show[1])["attribution"], "session")

    def test_cli_auto_resolves_codex_without_claude_default(self):
        self.init_cli_state()
        home = Path(self.cwd) / "home"
        sessions = home / ".codex" / "sessions" / "2020" / "01" / "01"
        sessions.mkdir(parents=True)
        records = [{"type": "session_meta", "payload": {"id": "codex", "cwd": self.cwd}},
                   {"type": "response_item", "timestamp": at_second(1),
                    "payload": {"type": "function_call", "call_id": "call"}},
                   {"type": "response_item", "timestamp": at_second(4),
                    "payload": {"type": "function_call_output", "call_id": "call"}}]
        (sessions / "session.jsonl").write_text("".join(json.dumps(row) + "\n" for row in records), encoding="utf-8")
        result = helper.run_timing_cli(self.cwd, "show", "--json", "--now", at_second(20),
                                       env={"HOME": str(home), "USERPROFILE": str(home)})
        self.assertEqual(result[0], 0, result[2])
        data = json.loads(result[1])
        self.assertEqual(self.number(data, "tool_call_seconds"), 3)
        self.assertIsNone(self.number(data, "api_request_seconds"))

    def test_cli_naive_now_rejected_and_json_empty_state_is_null(self):
        result = helper.run_timing_cli(self.cwd, "show", "--now", "2026-10-27T00:00:00")
        self.assertEqual(result[0], tdq_timing.EXIT_SYNTAX)
        result = helper.run_timing_cli(self.cwd, "show", "--json")
        self.assertEqual(result[0], 0)
        self.assertIsNone(json.loads(result[1]))

    def test_public_aggregation_logs_diagnostics_to_stderr_only(self):
        self.state["phase_history"] = [None]
        stdout, stderr = io.StringIO(), io.StringIO()
        with patch.dict(os.environ, {"TDQ_LOG": "1"}), contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            data = self.measure(self.tool(0, 5))
        self.assertEqual(stdout.getvalue(), "")
        self.assertRegex(stderr.getvalue(), r"\[\d{4}-\d{2}-\d{2}T")
        self.assertIn("invalid_phase_mark", stderr.getvalue())
        self.assertEqual(self.number(data, "tool_call_seconds"), 5)


if __name__ == "__main__":
    unittest.main()
