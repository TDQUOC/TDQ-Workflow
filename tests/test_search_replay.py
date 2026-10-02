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
    def test_stub_tren_fixture(self):
        kq = search_replay.phat_lai(search_replay.doc_dau_vao(FIXTURE), luat=search_replay._LuatStub)
        self.assertEqual(kq["luat"], "stub")
        self.assertEqual(kq["bat"], 0)
        self.assertGreater(kq["lot"], 0)
        self.assertIn(7, [h["luot"] for h in kq["hang"]])

    def test_cli_bang_va_json(self):
        p = _chay(FIXTURE, env={"TDQ_LOG": "0"})
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertRegex(p.stdout, r"luật: (search_rules|STUB — cho qua tất cả)")
        self.assertIn("| luot | cong cu | lenh | quyet dinh | ly do |", p.stdout)
        self.assertRegex(p.stdout, r"\| 7 \| Bash \|")
        p = _chay(FIXTURE, "--json", "--cua-so", "5", env={"TDQ_LOG": "0"})
        d = json.loads(p.stdout)
        self.assertEqual(set(d), {"bat", "bat_oan", "lot", "bi_chan", "luat"})
        self.assertIn(d["luat"], ("stub", "search_rules"))

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

    def test_doc_va_khong_phai_tim_bi_bo(self):
        luot = [h["luot"] for h in self.kq["hang"]]
        self.assertEqual(luot, [1, 3, 4, 5, 8])

    def test_dem(self):
        # luot 4 is the 3rd tim_code with window 2 -> denied; luot 5 denied loc_file.
        self.assertEqual(self.kq["bi_chan"], [4, 5])
        self.assertEqual(self.kq["bat"], 2)
        self.assertEqual(self.kq["bat_oan"], 1)
        self.assertEqual(self.kq["lot"], 2)  # luot 1 and 3, before any concept call
        self.assertEqual(self.kq["luat"], "gia")

    def test_khai_niem_dat_lai_bo_dem(self):
        tt8 = self.luat.thay[-1]
        self.assertTrue(tt8["da_goi_khai_niem"])
        self.assertEqual(tt8["so_lan_tim_tu_lan_goi"], 0)
        # Before the reset the counter climbed, denied searches included; loc_file did not count.
        self.assertEqual([t["so_lan_tim_tu_lan_goi"] for t in self.luat.thay[:4]], [0, 1, 2, 3])

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
        self.assertIn("luật: STUB — cho qua tất cả", bang)
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
        self.assertEqual([s["loai"] for s in sk], ["prompt", "tim", "doc", "khai_niem", "tim"])
        self.assertIn("fontfamily", sk[0]["token"])
        self.assertEqual([s["luot"] for s in sk], [0, 1, 2, 3, 4])

    def test_khong_import_hooks(self):
        with open(SCRIPT, encoding="utf-8") as fh:
            self.assertIsNone(re.search(r"^\s*(from|import)\s+hooks", fh.read(), re.M))


if __name__ == "__main__":
    unittest.main()
