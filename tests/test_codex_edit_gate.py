"""`hooks/scripts/codex_edit_gate.py` — lớp chặn SỚM của mode `codex`.

Ba bất biến, theo đúng thứ tự quan trọng:

1. Chỉ chặn khi đang ở trong một lượt Codex (có biến mốc `TDQ_CODEX_TASK`). Ngoài mode,
   hook này vẫn chỉ là cầu nối sang `edit_gate.py` như trước — chặn nhầm phiên người dùng
   tự chạy `codex` là hỏng thứ không phải việc của nó.
2. Trong lượt: đường ghi ngoài `VÙNG FILE` hoặc vào vùng khoá → `permissionDecision: deny`
   kèm mã `[TDQ:VUNG]`. Cả hai nhánh `apply_patch` và `Bash` đều phải chặn — Codex ghi file
   bằng shell cũng dễ như bằng patch.
3. Hook KHÔNG phải hàng rào duy nhất: thiếu khai vùng thì nó cảnh báo rồi cho đi, vì hậu
   kiểm `git diff` mới là lớp quyết định. Một hook tự ý chặn sạch khi thiếu cấu hình sẽ
   làm người ta tắt nó đi, và thế là mất luôn lớp chặn sớm.
"""
import importlib.util
import json
import os
import subprocess
import sys
import unittest

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GATE = os.path.join(GOC, "hooks", "scripts", "codex_edit_gate.py")

_spec = importlib.util.spec_from_file_location("codex_edit_gate_mod", GATE)
gate = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(gate)


def chay(payload, env_them=None, cwd=None):
    """Chạy hook như Codex chạy: payload qua stdin, quyết định qua stdout."""
    env = dict(os.environ, TDQ_LOG="0")
    env.pop("TDQ_CODEX_TASK", None)
    env.update(env_them or {})
    proc = subprocess.run([sys.executable, GATE], input=json.dumps(payload),
                          capture_output=True, text=True, timeout=60,
                          cwd=cwd or GOC, env=env)
    try:
        ra = json.loads(proc.stdout) if proc.stdout.strip() else {}
    except ValueError:
        ra = {}
    hso = ra.get("hookSpecificOutput") or {}
    return proc, hso.get("permissionDecision"), hso.get("permissionDecisionReason", "")


def moi_truong(vung, khoa=(), ma_task="T1.1"):
    return {"TDQ_CODEX_TASK": ma_task,
            "TDQ_CODEX_VUNG": json.dumps(list(vung)),
            "TDQ_CODEX_KHOA": json.dumps(list(khoa))}


def patch(duong):
    return {"tool_name": "apply_patch", "hook_event_name": "PreToolUse", "cwd": GOC,
            "tool_input": {"command": f"*** Begin Patch\n*** Update File: {duong}\n@@\n+x\n"}}


def bash(lenh):
    return {"tool_name": "Bash", "hook_event_name": "PreToolUse", "cwd": GOC,
            "tool_input": {"command": lenh}}


class TestTachDuongGhiShell(unittest.TestCase):
    """Năm dạng ghi file bằng shell — hàm thuần, kiểm riêng cho dễ đọc lỗi."""

    def test_ghi_de(self):
        self.assertIn("a.py", gate.tach_duong_ghi_shell("echo x > a.py"))

    def test_ghi_noi(self):
        self.assertIn("a.py", gate.tach_duong_ghi_shell("echo x >> a.py"))

    def test_heredoc(self):
        self.assertIn("a.py", gate.tach_duong_ghi_shell("cat <<'EOF' > a.py\nx\nEOF"))

    def test_tee(self):
        self.assertIn("a.py", gate.tach_duong_ghi_shell("echo x | tee -a a.py"))

    def test_mv_ke_ca_nguon(self):
        """`mv` đổi CẢ hai đầu: nguồn biến mất cũng là một thay đổi ngoài vùng."""
        duong = gate.tach_duong_ghi_shell("mv a.py b.py")
        self.assertIn("a.py", duong)
        self.assertIn("b.py", duong)

    def test_khong_nham_chuyen_huong_fd(self):
        """`2>&1` và `/dev/null` không phải file trong repo."""
        duong = gate.tach_duong_ghi_shell("pytest 2>&1 > /dev/null")
        self.assertNotIn("&1", duong)
        self.assertNotIn("/dev/null", duong)

    def test_lenh_chi_doc_thi_khong_co_duong_nao(self):
        for lenh in ("pytest -q", "git status", "ls scripts/"):
            with self.subTest(lenh=lenh):
                self.assertEqual(gate.tach_duong_ghi_shell(lenh), [])


class TestChanNgoaiVung(unittest.TestCase):
    def test_bash_nam_dang_deu_bi_chan(self):
        env = moi_truong(["scripts/a.py"])
        for lenh in ("echo x > ngoai/vung.py",
                     "echo x >> ngoai/vung.py",
                     "cat <<'EOF' > ngoai/vung.py\nx\nEOF",
                     "echo x | tee ngoai/vung.py",
                     "mv scripts/a.py ngoai/vung.py"):
            with self.subTest(lenh=lenh):
                _, quyet, ly_do = chay(bash(lenh), env)
                self.assertEqual(quyet, "deny", lenh)
                self.assertIn("TDQ:VUNG", ly_do)
                self.assertIn("ngoai/vung.py", ly_do)

    def test_apply_patch_ngoai_vung_bi_chan(self):
        _, quyet, ly_do = chay(patch("ngoai/vung.py"), moi_truong(["scripts/a.py"]))
        self.assertEqual(quyet, "deny")
        self.assertIn("TDQ:VUNG", ly_do)

    def test_trong_vung_thi_khong_chan(self):
        for payload in (patch("scripts/a.py"), bash("echo x > scripts/a.py")):
            with self.subTest(payload=payload["tool_name"]):
                _, quyet, _ = chay(payload, moi_truong(["scripts/a.py"]))
                self.assertNotEqual(quyet, "deny")

    def test_vung_la_thu_muc_thi_file_ben_trong_duoc_ghi(self):
        _, quyet, _ = chay(patch("scripts/con/a.py"), moi_truong(["scripts/"]))
        self.assertNotEqual(quyet, "deny")

    def test_vung_khoa_bi_chan_du_nam_trong_vung(self):
        """Vùng khoá thắng: file test nằm trong vùng vẫn cấm Codex chạm."""
        env = moi_truong(["tests/"], khoa=["tests/test_x.py"])
        _, quyet, ly_do = chay(patch("tests/test_x.py"), env)
        self.assertEqual(quyet, "deny")
        self.assertIn("TDQ:VUNG", ly_do)
        self.assertIn("tests/test_x.py", ly_do)

    def test_duong_tuyet_doi_trong_repo_quy_ve_duong_tuong_doi(self):
        _, quyet, _ = chay(patch(os.path.join(GOC, "scripts", "a.py")),
                           moi_truong(["scripts/a.py"]))
        self.assertNotEqual(quyet, "deny")


class TestNgoaiModeChiNhac(unittest.TestCase):
    def test_thieu_bien_moc_thi_khong_bao_gio_deny(self):
        """Không có biến mốc = không phải lượt của workflow → hook không phải chủ nhà."""
        _, quyet, _ = chay(bash("echo x > ngoai/vung.py"))
        self.assertNotEqual(quyet, "deny")

    def test_co_bien_moc_nhung_thieu_khai_vung_thi_canh_bao_roi_cho_di(self):
        proc, quyet, _ = chay(bash("echo x > ngoai/vung.py"),
                              {"TDQ_CODEX_TASK": "T1.1", "TDQ_LOG": "1"})
        self.assertNotEqual(quyet, "deny")
        self.assertIn("VÙNG FILE", proc.stderr)

    def test_payload_hong_khong_lam_chet_phien(self):
        proc = subprocess.run([sys.executable, GATE], input="{khong phai json",
                              capture_output=True, text=True, timeout=60, cwd=GOC,
                              env=dict(os.environ, TDQ_LOG="0"))
        self.assertEqual(proc.returncode, 0)


class TestPhepKiemKhoiDong(unittest.TestCase):
    """T6.4 — `tdq_codex.kiem_hook_ban` khẳng định hàng rào sớm CÓ hoạt động.

    Vì sao cần: hook Codex không tự chạy nếu thiếu `--dangerously-bypass-hook-trust`
    (issue #32491, còn nguyên ở 0.154.0), và độ phủ matcher `apply_patch` còn ngờ. Một
    hàng rào im lặng tệ hơn không có hàng rào, vì người ta tin nó.

    Và điều KHÔNG được làm: tự hạ cấp. Hook không bắn thì ghi ĐÚNG MỘT dòng cảnh báo
    rồi chạy tiếp — lớp quyết định là hậu kiểm `git diff`. Thêm một máy tự đổi cấu hình
    chỉ tạo thêm nhánh chưa ai chạy bao giờ.
    """

    @classmethod
    def setUpClass(cls):
        sys.path.insert(0, os.path.join(GOC, "scripts"))
        import tdq_codex
        cls.tdq_codex = tdq_codex

    def test_tren_repo_that_thi_hang_rao_ban_duoc(self):
        ban, ly_do = self.tdq_codex.kiem_hook_ban(GOC)
        self.assertTrue(ban, ly_do)
        self.assertEqual(ly_do, "")

    def test_co_bo_qua_tin_hook_nam_trong_bang_co(self):
        """Thiếu cờ này thì hook im lặng — và im lặng là ca tệ nhất."""
        lenh = self.tdq_codex.dung_lenh(goc_repo=GOC, model="m", file_schema="s",
                                        file_ket_qua="k")
        self.assertIn(self.tdq_codex.CO_EXEC["bo_qua_tin_hook"], lenh)

    def test_thieu_hooks_json_thi_bao_khong_ban(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            ban, ly_do = self.tdq_codex.kiem_hook_ban(tmp)
            self.assertFalse(ban)
            self.assertTrue(ly_do)

    def test_canh_bao_dung_mot_dong_va_khong_ha_cap(self):
        dong = self.tdq_codex.canh_bao_hook(False, "thiếu .codex/hooks.json")
        self.assertEqual(len(dong.splitlines()), 1, "cảnh báo phải gọn đúng một dòng")
        self.assertIn("audit", dong, "phải nói rõ lớp nào mới là lớp quyết định")
        self.assertEqual(self.tdq_codex.canh_bao_hook(True, ""), "")

    def test_khong_co_nhanh_tu_ha_cap_trong_nguon(self):
        with open(os.path.join(GOC, "scripts", "tdq_codex.py"), encoding="utf-8") as f:
            nguon = f.read()
        for dau in ("sandbox_gia_tri] = ", "CO_EXEC[", "read-only"):
            with self.subTest(dau=dau):
                self.assertNotIn(dau + "\n", nguon)
        self.assertFalse("ha_cap" in nguon or "hạ cấp sandbox" in nguon,
                         "không được có nhánh tự hạ cấp cấu hình")


if __name__ == "__main__":
    unittest.main()
