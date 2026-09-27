"""Khoá 6 điểm tương thích với 3 host — yêu cầu 2026-09-03-1440.

Vì sao phải khoá bằng test: cả 6 điểm đều là thứ ĐÚNG-SAI theo host, không phải theo ý người
viết, và mỗi cái đã từng sai đúng một lần. Sai lại thì im lặng — hook không chạy, plugin không
được nạp, key không có giá trị — nên chỉ có test mới bắt được lúc ai đó dựng lại bundle.

Sáu điểm, sáu test, mỗi test chạy riêng được bằng `-k`: `plugin_agy`, `settings`, `tuyet_doi`,
`deny`, `trust`, `user_config`.
"""
import json
import ntpath
import os
import posixpath
import subprocess
import tempfile
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import build_portable  # noqa: E402
import tdq_checkportable  # noqa: E402 — chủ của phép kiểm dấu ~

# 2026-09-21: layout agy không còn nằm sẵn trong repo — nó được SINH ra lúc cài, vào đúng thư
# mục cài trên máy người dùng. Nên test sinh một bản tạm rồi soi bản đó. Bundle codex thì bỏ
# hẳn: Codex nay đọc repo qua `.agents/plugins/marketplace.json`, không còn file nào để soi.
_TMP = tempfile.TemporaryDirectory()
BAN_AGY = build_portable.sinh_agy_tai_cho(ROOT, os.path.join(_TMP.name, "tdq-workflow"))


def _doc(*phan):
    with open(os.path.join(*phan), encoding="utf-8") as f:
        return f.read()


class TuongThichAgy(unittest.TestCase):
    def test_plugin_agy(self):
        """Bundle agy PHẢI có `plugin.json` ở gốc — agy 1.1.11 chỉ coi thư mục là plugin khi
        thấy file này (`~/.gemini/config/plugins/<tên>/plugin.json`)."""
        duong = os.path.join(BAN_AGY, "plugin.json")
        self.assertTrue(os.path.isfile(duong), "thiếu plugin.json ở gốc bundle agy")
        self.assertEqual(json.loads(_doc(duong))["name"], "tdq-workflow")
        self.assertTrue(os.path.isdir(os.path.join(BAN_AGY, "skills")))
        for ten in ("hooks.json", "mcp_config.json"):
            self.assertTrue(os.path.isfile(os.path.join(BAN_AGY, ten)),
                            f"{ten} phải nằm ở gốc plugin, không nằm trong config/")

    def test_settings(self):
        """KHÔNG được ship `settings.json`: file thật của người dùng giữ model/colorScheme/
        trustedWorkspaces và không có mục permissions — copy đè là mất cấu hình, không được
        thêm hàng rào nào."""
        self.assertFalse(os.path.exists(os.path.join(BAN_AGY, "config", "settings.json")))
        self.assertFalse(os.path.exists(os.path.join(BAN_AGY, "settings.json")))

    def test_tuyet_doi(self):
        """Mọi `command` hook agy phải là đường dẫn tuyệt đối đã bung `~`: dấu `~` nằm trong
        nháy kép không được shell bung, hook chết với exit 127."""
        du_lieu = json.loads(_doc(BAN_AGY, "hooks.json"))
        lenh = [h["command"]
                for muc in du_lieu["hooks"].values()
                for nhom in muc for h in nhom["hooks"]]
        self.assertTrue(lenh, "hooks.json agy không khai lệnh nào")
        for c in lenh:
            # 2026-09-27: hỏi đúng câu "còn `~` CHƯA BUNG không", thay vì "có ký tự `~` không".
            # Runner Windows của GitHub có thư mục nhà dạng 8.3 (`C:\Users\RUNNER~1\...`) — đường
            # dẫn đó đã tuyệt đối và chạy đúng, nhưng phép kiểm cũ báo đỏ (CI run 35957834415).
            # Phép kiểm sống ở `tdq_checkportable`, dùng chung với chính sản phẩm.
            self.assertFalse(tdq_checkportable.con_dau_nga_chua_bung(c),
                             f"còn dấu ~ chưa bung: {c}")
            duong = c.split()[-1]
            # Both rule sets, not just the host's. The bundle bakes in the absolute path of the
            # machine that BUILT it, so a bundle built on macOS carries `/Users/...` — and
            # `ntpath.isabs` calls that relative, failing the case on Windows for a bundle that
            # is perfectly correct. What the invariant actually says is "absolute somewhere".
            self.assertTrue(posixpath.isabs(duong) or ntpath.isabs(duong),
                            f"đường dẫn không tuyệt đối: {duong}")

    def test_deny(self):
        """Payload deny phải mang CẢ `allow_tool: false` lẫn `decision: "deny"` — Google chưa
        công bố schema chính thức nên không được bỏ cách viết nào."""
        kich_ban = os.path.join(ROOT, "hooks", "scripts", "agy_pretooluse_gate.py")
        vao = json.dumps({"tool_name": "run_command",
                          "tool_input": {"command": "git checkout -b codex-thu"}})
        moi_truong = dict(os.environ, TDQ_LOG="0")
        ket_qua = subprocess.run([sys.executable, kich_ban], input=vao, encoding="utf-8", text=True,
                                 capture_output=True, env=moi_truong, check=True)
        payload = json.loads(ket_qua.stdout)
        self.assertIs(payload["allow_tool"], False)
        self.assertEqual(payload["decision"], "deny")
        self.assertTrue(payload["reason"])


class TuongThichCodexVaClaude(unittest.TestCase):

    def test_user_config(self):
        """`plugin.json` của Claude Code khai `displayName` và `userConfig` cho 2 key Tavily,
        cả hai đánh dấu `sensitive` để giá trị không bao giờ hiện ra."""
        du_lieu = json.loads(_doc(ROOT, ".claude-plugin", "plugin.json"))
        self.assertTrue(du_lieu.get("displayName"))
        cau_hinh = du_lieu["userConfig"]
        for khoa in ("TAVILY_API_KEY", "TAVILY_API_KEY_BACKUP"):
            self.assertIn(khoa, cau_hinh)
            self.assertIs(cau_hinh[khoa]["sensitive"], True)
            self.assertTrue(cau_hinh[khoa]["title"])


if __name__ == "__main__":
    unittest.main()
