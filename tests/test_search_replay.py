"""Tests for scripts/search_replay.py (T1.3): replaying recorded searches through the rules."""
import json
import os
import re
import subprocess
import sys
import tempfile
import unittest

from helper import ROOT

sys.path.insert(0, os.path.join(ROOT, "scripts"))
import search_replay  # noqa: E402

SCRIPT = os.path.join(ROOT, "scripts", "search_replay.py")
FIXTURE = os.path.join(ROOT, "tests", "fixtures", "phien_excalidraw_tim.json")


def _chay(*args, env=None):
    return subprocess.run([sys.executable, SCRIPT, *args], capture_output=True, encoding="utf-8",
                          text=True, timeout=60, env=dict(os.environ, **(env or {})))


class LuatGia:
    """Fake rules: commands starting with 'ls' are loc_file; deny when the window is used up
    or when the command contains 'DENY'. Records every state it was handed."""
    TEN = "gia"
    CUA_SO = 2

    def __init__(self):
        self.thay = []

    def phan_loai(self, cong_cu, lenh):
        if lenh.startswith("ls"):
            loai = "loc_file"
        elif "grep" in lenh:
            loai = "tim_code"
        else:
            loai = "khong_phai_tim"
        return {"loai": loai, "tu_khoa": [], "doan_mo": False}

    def quyet_dinh(self, pl, tt):
        self.thay.append(dict(tt))
        if "DENY" in self.lenh_hien_tai:
            return False, "fake deny"
        return tt["so_lan_tim_tu_lan_goi"] < tt["cua_so"], "fake window"


def _phat(luat, su_kien, cua_so=None):
    # Wrap so the fake can see the command it is judging.
    goc = luat.phan_loai

    def pl(cong_cu, lenh):
        luat.lenh_hien_tai = lenh
        return goc(cong_cu, lenh)
    luat.phan_loai = pl
    return search_replay.phat_lai(su_kien, cua_so=cua_so, luat=luat)


class TestFixtureThat(unittest.TestCase):
    def test_luat_that_tren_fixture(self):
        """F6: luot 23 `graphify god-nodes` is a real concept query — the gate unlocks there, so
        the replay must too (the old replay skipped every "doc" event and missed it)."""
        kq = search_replay.phat_lai(search_replay.doc_dau_vao(FIXTURE))
        self.assertEqual(kq["luat"], "search_rules")
        self.assertEqual((kq["bat"], kq["bat_oan"], kq["lot"]), (11, 0, 0))
        self.assertIn(7, kq["bi_chan"])
        self.assertNotIn(28, kq["bi_chan"])

    def test_cli_bang_va_json(self):
        p = _chay(FIXTURE, env={"TDQ_LOG": "0"})
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertIn("rules: search_rules", p.stdout)
        self.assertIn("| event | tool | command | decision | reason |", p.stdout)
        self.assertRegex(p.stdout, r"\| 7 \| Bash \|")
        p = _chay(FIXTURE, "--json", "--cua-so", "5", env={"TDQ_LOG": "0"})
        d = json.loads(p.stdout)
        self.assertEqual(set(d), {"bat", "bat_oan", "lot", "bi_chan", "luat"})
        self.assertEqual(d["luat"], "search_rules")

    def test_log(self):
        self.assertEqual(_chay(FIXTURE, "--json", env={"TDQ_LOG": "0"}).stderr, "")
        err = _chay(FIXTURE, "--json", env={"TDQ_LOG": "1"}).stderr
        self.assertRegex(err, r"^\[\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d\] search_replay: ")


class TestNgunghia(unittest.TestCase):
    SK = [
        {"luot": 0, "loai": "prompt", "token": ["alpha"]},
        {"luot": 1, "loai": "tim", "cong_cu": "Bash", "lenh": "grep a"},
        {"luot": 2, "loai": "doc", "cong_cu": "Bash", "lenh": "grep in a doc event"},
        {"luot": 3, "loai": "tim", "cong_cu": "Bash", "lenh": "grep b"},
        {"luot": 4, "loai": "tim", "cong_cu": "Bash", "lenh": "grep c"},
        {"luot": 5, "loai": "tim", "cong_cu": "Bash", "lenh": "ls DENY"},
        {"luot": 6, "loai": "prompt", "token": ["beta", "gamma"]},
        {"luot": 7, "loai": "khai_niem", "cong_cu": "mcp__lsp__find_symbol"},
        {"luot": 8, "loai": "tim", "cong_cu": "Bash", "lenh": "grep d"},
        {"luot": 9, "loai": "tim", "cong_cu": "Bash", "lenh": "cat x"},
        {"luot": 10, "loai": "he_thong"},
        {"luot": 11, "loai": "skill", "cong_cu": "Skill"},
    ]

    def setUp(self):
        self.luat = LuatGia()
        self.kq = _phat(self.luat, self.SK)

    def test_moi_lenh_shell_deu_qua_luat(self):
        """F6: the gate sees every shell command, so the replay classifies "doc" events too;
        only what the rules call khong_phai_tim drops out."""
        luot = [h["luot"] for h in self.kq["hang"]]
        self.assertEqual(luot, [1, 2, 3, 4, 5, 8])

    def test_dem(self):
        # Window 2: luot 1 and 2 run; 3 and 4 are denied; luot 5 is a denied loc_file.
        self.assertEqual(self.kq["bi_chan"], [3, 4, 5])
        self.assertEqual(self.kq["bat"], 3)
        self.assertEqual(self.kq["bat_oan"], 1)
        self.assertEqual(self.kq["lot"], 2)  # luot 1 and 2, before any concept call
        self.assertEqual(self.kq["luat"], "gia")

    def test_khai_niem_dat_lai_bo_dem(self):
        tt8 = self.luat.thay[-1]
        self.assertTrue(tt8["da_goi_khai_niem"])
        self.assertEqual(tt8["so_lan_tim_tu_lan_goi"], 0)
        # A denied search never ran, so it does not eat the window (same rule as the gate).
        self.assertEqual([t["so_lan_tim_tu_lan_goi"] for t in self.luat.thay[:5]], [0, 1, 2, 2, 2])

    def test_prompt_thay_token(self):
        self.assertEqual(self.luat.thay[0]["token_prompt"], {"alpha"})
        self.assertEqual(self.luat.thay[-1]["token_prompt"], {"beta", "gamma"})

    def test_cua_so_ghi_de(self):
        luat = LuatGia()
        kq = _phat(luat, self.SK, cua_so=10)
        self.assertEqual(kq["bi_chan"], [5])
        self.assertEqual(luat.thay[0]["cua_so"], 10)

    def test_bang_cat_lenh(self):
        bang = search_replay.in_bang({"luat": "stub", "bat": 0, "bat_oan": 0, "lot": 1, "bi_chan": [],
                                      "hang": [{"luot": 1, "cong_cu": "Bash", "lenh": "grep " + "x" * 200,
                                                "cho_phep": True, "ly_do": "ok"}]})
        self.assertIn("rules: stub", bang)
        dong = [d for d in bang.splitlines() if d.startswith("| 1 |")][0]
        self.assertLessEqual(len(dong.split(" | ")[2]), 70)


class TestTranscript(unittest.TestCase):
    def test_jsonl(self):
        dong = [
            {"type": "user", "message": {"content": "find the fontFamily helper"}},
            {"type": "assistant", "message": {"content": [
                {"type": "tool_use", "name": "Bash", "input": {"command": "grep -rn fontFamily src"}},
                {"type": "tool_use", "name": "Bash", "input": {"command": "cat a.ts"}},
                {"type": "tool_use", "name": "mcp__lsp__find_symbol", "input": {}},
                {"type": "tool_use", "name": "Grep", "input": {"pattern": "foo"}}]}},
            {"type": "user", "message": {"content": [{"type": "tool_result", "content": "x"}]}},
        ]
        with tempfile.TemporaryDirectory() as d:
            duong = os.path.join(d, "t.jsonl")
            with open(duong, "w", encoding="utf-8") as fh:
                fh.write("\n".join(json.dumps(x) for x in dong))
            sk = search_replay.doc_dau_vao(duong)
        self.assertEqual([s["loai"] for s in sk], ["prompt", "tim", "tim", "khai_niem", "tim"])
        self.assertIn("fontfamily", sk[0]["token"])
        self.assertEqual([s["luot"] for s in sk], [0, 1, 2, 3, 4])

    def test_khong_import_hooks(self):
        with open(SCRIPT, encoding="utf-8") as fh:
            self.assertIsNone(re.search(r"^\s*(from|import)\s+hooks", fh.read(), re.M))


if __name__ == "__main__":
    unittest.main()
