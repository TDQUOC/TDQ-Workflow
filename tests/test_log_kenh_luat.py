"""T5.1 — khoá log service của ba kênh nạp luật gọn.

Mỗi kênh (`SessionStart`, `UserPromptSubmit`, `SubagentStart`) mỗi lần chạy ghi ĐÚNG MỘT
dòng vào sổ lượt CÓ SẴN `docs/tdq/.tdq-turn.jsonl` qua `tdq_state.turn_log_append`, với
timestamp (do `turn_log_append` tự đóng dấu), tên kênh (`event`) và mức gắt (`muc_gat`);
`muc_gat=off` thì không kênh nào ghi. Không có sổ log thứ hai.

Việc GHI thuộc T3.1–T3.3 (luật file nóng), file này chỉ là phép kiểm — không sửa mã hook.

GHI CHÚ ĐỎ cho người đọc plan: plan T5.1 còn đòi dòng log ghi **số dòng luật đã chèn**.
Đọc `session_start.py`, `prompt_context.py` (`_nhac_gon`) và `subagent_start.py` ngày
2026-09-17: trường đó CHƯA có trong mã — ba kênh chỉ ghi `event`, `muc_gat` (+ `source` /
`agent`). Test ở đây đo đúng những trường THẬT đang có, cố ý không giả vờ đạt và cũng cố ý
không khoá "vắng mặt" (khoá vắng mặt sẽ thành bẫy cho task sửa sau). Cần một task sửa mã
để thêm trường đó rồi mở rộng file này.

Mọi test đặt TDQ_PROJECT_DIR = thư mục tạm của chính nó: `resolve_project_dir` cho env
thắng payload `cwd`, nên không ghim env thì lệnh chạy test có sẵn biến đó sẽ đẩy hook đi
ghi sang project khác.
"""
import json
import os
import tempfile
import unittest
from datetime import datetime, timezone

from helper import run_hook, tdq_state, write_state

MA = "TDQ:GON"
SO_LUOT = os.path.join("docs", "tdq", ".tdq-turn.jsonl")


class LogBaKenhLuat(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.cwd = self._tmp.name
        self.addCleanup(self._tmp.cleanup)

    def state(self, **thay):
        write_state(self.cwd, active_request="2026-09-16-2234-cong-sinh-ponytail-tdq",
                    lane="full", phase="implement", spec_approved=True, plan_approved=True,
                    implement_mode="subagent", spec_file="docs/tdq/spec/x.md",
                    plan_file="docs/tdq/plan/x.md", **thay)

    def chay(self, kenh, session):
        """Chạy một kênh, trả về (rc, stdout). Kênh = tên sự kiện hook."""
        goi = {"hook_event_name": kenh, "cwd": self.cwd, "session_id": session}
        if kenh == "SessionStart":
            script, goi["source"] = "session_start.py", "startup"
        elif kenh == "UserPromptSubmit":
            script, goi["prompt"] = "prompt_context.py", "làm tiếp task sau giúp tôi"
        else:
            script, goi["agent_type"] = "subagent_start.py", "tdq-implementer"
        rc, out, _err = run_hook(script, goi, env={"TDQ_PROJECT_DIR": self.cwd})
        self.assertEqual(rc, 0, out)
        return rc, out

    def dong_luat(self, session=None):
        """Các dòng log của luật gọn trong sổ lượt, đọc thô từ file."""
        path = os.path.join(self.cwd, SO_LUOT)
        if not os.path.exists(path):
            return []
        with open(path, encoding="utf-8") as f:
            rows = [json.loads(l) for l in f if l.strip()]
        return [r for r in rows
                if r.get("code") == MA and (session is None or r.get("session") == session)]

    # -------------------------------------------------- mỗi kênh đúng một dòng

    def test_moi_kenh_ghi_dung_mot_dong_dung_ten_kenh(self):
        for kenh in ("SessionStart", "UserPromptSubmit", "SubagentStart"):
            with self.subTest(kenh=kenh):
                self.state()
                session = f"s-{kenh}"
                self.chay(kenh, session)
                dong = self.dong_luat(session)
                self.assertEqual(len(dong), 1, f"{kenh} phải ghi đúng một dòng: {dong}")
                self.assertEqual(dong[0].get("event"), kenh)
                self.assertEqual(dong[0].get("kind"), "remind")
                self.assertEqual(dong[0].get("session"), session)

    def test_ba_kenh_dung_chung_mot_so_ba_dong(self):
        """Ba kênh, ba session khác nhau → ba dòng trong CÙNG một sổ."""
        self.state()
        for kenh in ("SessionStart", "UserPromptSubmit", "SubagentStart"):
            self.chay(kenh, f"s-{kenh}")
        dong = self.dong_luat()
        self.assertEqual(len(dong), 3, dong)
        self.assertEqual(sorted(r.get("event") for r in dong),
                         ["SessionStart", "SubagentStart", "UserPromptSubmit"])

    # -------------------------------------------------- timestamp

    def test_moi_dong_co_timestamp_tu_dong_dong_dau(self):
        """`turn_log_append` tự đóng dấu `ts` — kênh không tự ghi timestamp."""
        truoc = datetime.now(timezone.utc)
        for kenh in ("SessionStart", "UserPromptSubmit", "SubagentStart"):
            with self.subTest(kenh=kenh):
                self.state()
                self.chay(kenh, f"t-{kenh}")
                row = self.dong_luat(f"t-{kenh}")[0]
                ts = datetime.fromisoformat(row["ts"])
                self.assertIsNotNone(ts.tzinfo, f"ts phải có múi giờ: {row['ts']}")
                lech = (ts.astimezone(timezone.utc) - truoc).total_seconds()
                self.assertGreaterEqual(lech, -2, row["ts"])
                self.assertLessEqual(lech, 300, row["ts"])

    # -------------------------------------------------- mức gắt

    def test_dong_log_ghi_dung_muc_gat_dang_hieu_luc(self):
        for muc in ("lite", "full", "ultra"):
            for kenh in ("SessionStart", "UserPromptSubmit", "SubagentStart"):
                with self.subTest(muc=muc, kenh=kenh):
                    self.state(muc_gat=muc)
                    session = f"m-{muc}-{kenh}"
                    self.chay(kenh, session)
                    dong = self.dong_luat(session)
                    self.assertEqual(len(dong), 1, dong)
                    self.assertEqual(dong[0].get("muc_gat"), muc)

    def test_muc_off_thi_khong_kenh_nao_ghi_dong_nao(self):
        self.state(muc_gat="off")
        for kenh in ("SessionStart", "UserPromptSubmit", "SubagentStart"):
            self.chay(kenh, f"off-{kenh}")
        self.assertEqual(self.dong_luat(), [], "muc_gat=off thì sổ không được có dòng luật")

    # -------------------------------------------------- một sổ duy nhất

    def test_khong_dung_so_log_thu_hai(self):
        """Chỉ `.tdq-turn.jsonl` của `turn_log_path`, không file log nào khác sinh ra."""
        self.state()
        for kenh in ("SessionStart", "UserPromptSubmit", "SubagentStart"):
            self.chay(kenh, f"so-{kenh}")
        self.assertEqual(tdq_state.turn_log_path(self.cwd),
                         os.path.join(self.cwd, SO_LUOT))
        thay = []
        for goc, _dirs, files in os.walk(self.cwd):
            for ten in files:
                if ten.endswith((".jsonl", ".log")):
                    thay.append(os.path.relpath(os.path.join(goc, ten), self.cwd))
        self.assertEqual(sorted(thay), [SO_LUOT], f"mọc thêm sổ log: {thay}")

    def test_bo_doc_co_san_thay_dong_cua_tung_kenh(self):
        """Đọc bằng `turn_log_read` có sẵn — cùng một sổ, không cần bộ đọc riêng."""
        self.state()
        for kenh in ("SessionStart", "UserPromptSubmit", "SubagentStart"):
            with self.subTest(kenh=kenh):
                session = f"r-{kenh}"
                self.chay(kenh, session)
                rows = [r for r in tdq_state.turn_log_read(self.cwd, session=session)
                        if r.get("code") == MA]
                self.assertEqual(len(rows), 1, rows)
                self.assertEqual(rows[0].get("event"), kenh)


if __name__ == "__main__":
    unittest.main()
