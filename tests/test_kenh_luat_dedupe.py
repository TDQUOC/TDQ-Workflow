"""T3.4 (2026-09-17) — chống chèn hai lần: ba kênh luật gọn dedupe theo LƯỢT.

Bug #10871 chạy một hook plugin hai lần với hai PID, nên mỗi kênh phải hỏi cùng một
cái sổ lượt (`already_reminded`) chứ không tự giữ cờ riêng. File này khoá ba chuyện:
1. Kênh phiên (`SessionStart`) và kênh sub-agent (`SubagentStart`) dedupe THẬT qua hai
   tiến trình: gọi hook hai lần cùng `session_id` thì thân luật ra đúng một lần.
2. Kênh lượt (`UserPromptSubmit`) chỉ dedupe TRONG MỘT tiến trình — `main()` mở đầu
   bằng `turn_log_clear` nên hai lần chạy hook là hai LƯỢT khác nhau và nhắc lại là
   đúng (số đo T3.2, ghi trong plan). Nên kênh này đo ở mức hàm `_nhac_gon`.
3. Chỉ có MỘT cơ chế: cả ba kênh dùng `already_reminded` của `_common`, không kênh nào
   tự định nghĩa cơ chế thứ hai. Và dedupe là theo lượt chứ không câm vĩnh viễn — sổ
   lượt mới thì luật nhắc lại.
"""
import contextlib
import importlib.util
import io
import os
import sys
import tempfile
import unittest

from helper import run_hook, write_state, tdq_state

MOC = "[TDQ:GON]"
MA = "TDQ:GON"
# Một dòng thật của thân luật (bậc 1 của bậc thang) — để đếm THÂN LUẬT, không chỉ cái mốc.
# Phải lấy cả phần chữ: thân luật có HAI bảng, nên chuỗi "| 1 |" trơ xuất hiện 2 lần trong
# MỘT lần chèn (đo 2026-09-17) và đếm nó sẽ báo trùng lặp không có thật. Chuỗi dưới đây duy
# nhất ở cả ba mức lite/full/ultra.
DONG_THAN_LUAT = "| 1 | Does this need to exist at all?"

HOOKS = os.path.normpath(os.path.join(tdq_state.__file__, "..", "..", "hooks", "scripts"))
if HOOKS not in sys.path:
    sys.path.insert(0, HOOKS)
_spec = importlib.util.spec_from_file_location(
    "pc_dedupe", os.path.join(HOOKS, "prompt_context.py"))
pc = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(pc)


class GocDedupe(unittest.TestCase):
    """Nền chung: một project tạm có request mở ở phase implement."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.cwd = self._tmp.name
        self.addCleanup(self._tmp.cleanup)

    def state(self, **thay):
        write_state(self.cwd, active_request="2026-09-16-2234-cong-sinh-ponytail-tdq",
                    lane="full", phase="implement", spec_approved=True, plan_approved=True,
                    implement_mode="subagent", spec_file="docs/tdq/spec/x.md",
                    plan_file="docs/tdq/plan/x.md", **thay)

    def dong_log_gon(self, session):
        rows = tdq_state.turn_log_read(self.cwd, session=session)
        return [r for r in rows if r.get("kind") == "remind" and r.get("code") == MA]


class TestKenhPhien(GocDedupe):
    """`SessionStart`: không có `turn_log_clear` nên dedupe qua hai tiến trình là thật."""

    def chay(self, session="p-dedupe"):
        rc, out, _err = run_hook("session_start.py", {
            "hook_event_name": "SessionStart", "cwd": self.cwd,
            "session_id": session, "source": "startup"})
        self.assertEqual(rc, 0)
        return out

    def test_chay_hai_lan_cung_luot_thi_than_luat_dung_mot_lan(self):
        self.state()
        lan1, lan2 = self.chay(), self.chay()
        ca_hai = lan1 + "\n" + lan2
        self.assertEqual(ca_hai.count(MOC), 1, ca_hai)
        self.assertEqual(ca_hai.count(DONG_THAN_LUAT), 1, ca_hai)
        # Lần hai vẫn phải in khối đầu (dòng luật + next): im lặng hẳn là một lỗi khác.
        self.assertIn("[TDQ]", lan2, lan2)

    def test_hai_lan_chay_chi_ghi_mot_dong_log(self):
        self.state()
        self.chay()
        self.chay()
        self.assertEqual(len(self.dong_log_gon("p-dedupe")), 1,
                         tdq_state.turn_log_read(self.cwd, session="p-dedupe"))

    def test_luot_moi_thi_nhac_lai(self):
        """Dedupe theo LƯỢT, không phải câm vĩnh viễn: xoá sổ lượt thì luật quay lại."""
        self.state()
        self.assertIn(MOC, self.chay())
        tdq_state.turn_log_clear(self.cwd, "p-dedupe")
        self.assertIn(MOC, self.chay())

    def test_phien_khac_khong_bi_dedupe_lay(self):
        """Sổ lượt tách theo `session_id`: phiên B không được im vì phiên A đã nhắc."""
        self.state()
        self.assertIn(MOC, self.chay(session="p-A"))
        self.assertIn(MOC, self.chay(session="p-B"))


class TestKenhSubagent(GocDedupe):
    """`SubagentStart`: cũng dedupe thật qua hai tiến trình."""

    def chay(self, session="sa-dedupe"):
        rc, out, _err = run_hook("subagent_start.py", {
            "hook_event_name": "SubagentStart", "cwd": self.cwd,
            "session_id": session, "agent_type": "tdq-implementer"})
        self.assertEqual(rc, 0)
        return out

    def test_chay_hai_lan_cung_luot_thi_than_luat_dung_mot_lan(self):
        self.state()
        ca_hai = self.chay() + "\n" + self.chay()
        self.assertEqual(ca_hai.count(MOC), 1, ca_hai)
        self.assertEqual(ca_hai.count(DONG_THAN_LUAT), 1, ca_hai)

    def test_hai_lan_chay_chi_ghi_mot_dong_log(self):
        self.state()
        self.chay()
        self.chay()
        self.assertEqual(len(self.dong_log_gon("sa-dedupe")), 1,
                         tdq_state.turn_log_read(self.cwd, session="sa-dedupe"))

    def test_luot_moi_thi_nhac_lai(self):
        self.state()
        self.assertIn(MOC, self.chay())
        tdq_state.turn_log_clear(self.cwd, "sa-dedupe")
        self.assertIn(MOC, self.chay())


class TestKenhLuot(GocDedupe):
    """`UserPromptSubmit`: đo ở mức HÀM, vì `main()` xoá sổ lượt lúc vào (số đo T3.2)."""

    def goi_nhac(self, session="l-dedupe"):
        payload = {"hook_event_name": "UserPromptSubmit", "cwd": self.cwd,
                   "session_id": session, "prompt": "làm tiếp"}
        bat = io.StringIO()
        with contextlib.redirect_stdout(bat):
            pc._nhac_gon(self.cwd, tdq_state.load(self.cwd), payload, session)
        return bat.getvalue()

    def test_goi_hai_lan_trong_mot_luot_thi_lan_hai_im_lang(self):
        self.state()
        self.assertIn(MOC, self.goi_nhac())
        self.assertEqual(self.goi_nhac(), "")

    def test_hai_lan_goi_chi_ghi_mot_dong_log(self):
        self.state()
        self.goi_nhac()
        self.goi_nhac()
        self.assertEqual(len(self.dong_log_gon("l-dedupe")), 1,
                         tdq_state.turn_log_read(self.cwd, session="l-dedupe"))

    def test_luot_moi_thi_nhac_lai(self):
        self.state()
        self.assertIn(MOC, self.goi_nhac())
        tdq_state.turn_log_clear(self.cwd, "l-dedupe")
        self.assertIn(MOC, self.goi_nhac())


class TestMotCoCheDuyNhat(GocDedupe):
    """Ba kênh chia MỘT cái sổ, không kênh nào có cơ chế riêng."""

    KENH = ("session_start.py", "subagent_start.py", "prompt_context.py")

    def nguon(self, ten):
        with open(os.path.join(HOOKS, ten), encoding="utf-8") as f:
            return f.read()

    def test_ba_kenh_deu_hoi_already_reminded_cua_common(self):
        for ten in self.KENH:
            with self.subTest(kenh=ten):
                src = self.nguon(ten)
                self.assertIn("already_reminded", src)
                self.assertIn("from _common import", src)

    def test_khong_kenh_nao_tu_viet_co_che_thu_hai(self):
        """Cấm định nghĩa lại dedupe hay dựng file cờ riêng bên cạnh sổ lượt."""
        for ten in self.KENH:
            with self.subTest(kenh=ten):
                src = self.nguon(ten)
                self.assertNotIn("def already_reminded", src)
                self.assertNotIn(".tdq-gon", src)

    def test_hai_kenh_khac_nhau_cung_luot_cung_chi_chen_mot_lan(self):
        """Cùng một lượt của cùng một phiên: kênh nào tới trước thì kênh sau im."""
        self.state()
        rc, phien, _err = run_hook("session_start.py", {
            "hook_event_name": "SessionStart", "cwd": self.cwd,
            "session_id": "chung", "source": "startup"})
        self.assertEqual(rc, 0)
        rc, sub, _err = run_hook("subagent_start.py", {
            "hook_event_name": "SubagentStart", "cwd": self.cwd,
            "session_id": "chung", "agent_type": "tdq-implementer"})
        self.assertEqual(rc, 0)
        self.assertIn(MOC, phien)
        self.assertNotIn(MOC, sub)
        self.assertEqual(len(self.dong_log_gon("chung")), 1)

    def test_muc_off_thi_khong_kenh_nao_in_va_khong_dong_log_nao(self):
        self.state(muc_gat="off")
        rc, phien, _err = run_hook("session_start.py", {
            "hook_event_name": "SessionStart", "cwd": self.cwd,
            "session_id": "off", "source": "startup"})
        self.assertEqual(rc, 0)
        rc, sub, _err = run_hook("subagent_start.py", {
            "hook_event_name": "SubagentStart", "cwd": self.cwd,
            "session_id": "off", "agent_type": "tdq-implementer"})
        self.assertEqual(rc, 0)
        self.assertNotIn(MOC, phien)
        self.assertNotIn(MOC, sub)
        self.assertEqual(self.dong_log_gon("off"), [])


if __name__ == "__main__":
    unittest.main()
