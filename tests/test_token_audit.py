"""Test cho scripts/token_audit.py — đo carry-cost của tool output trong transcript."""

import json
import os
import subprocess
import sys
import tempfile
import unittest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "scripts"))

import token_audit  # noqa: E402


def _assistant(tool_id, name, inp, usage=True):
    msg = {"role": "assistant", "content": [
        {"type": "tool_use", "id": tool_id, "name": name, "input": inp}]}
    if usage:
        msg["usage"] = {"input_tokens": 1, "output_tokens": 1,
                        "cache_read_input_tokens": 100}
    return {"type": "assistant", "message": msg}


def _result(tool_id, text):
    return {"type": "user", "message": {"role": "user", "content": [
        {"type": "tool_result", "tool_use_id": tool_id, "content": text}]}}


def _write(path, records):
    with open(path, "w", encoding="utf-8") as fh:
        for r in records:
            fh.write(json.dumps(r) + "\n")


class IterEventsTest(unittest.TestCase):
    def test_bo_qua_dong_hong_khong_crash(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "s.jsonl")
            with open(p, "w", encoding="utf-8") as fh:
                fh.write(json.dumps({"ok": 1}) + "\n")
                fh.write("{ dòng hỏng không phải json\n")
                fh.write("\n")
                fh.write(json.dumps({"ok": 2}) + "\n")
            events = list(token_audit.iter_events(p))
        self.assertEqual([e.get("ok") for e in events], [1, 2])

    def test_file_khong_ton_tai_tra_rong(self):
        self.assertEqual(list(token_audit.iter_events("/khong/co/that.jsonl")), [])


class CarryCostTest(unittest.TestCase):
    def test_cong_thuc_chars_chia_4_nhan_so_call_con_lai(self):
        # 3 API call; tool_result của call 1 nằm trước call 2 và 3.
        text = "x" * 400          # 400 ký tự → 100 token
        records = [
            _assistant("t1", "Read", {"file_path": "/a.md"}),   # api call 1
            _result("t1", text),
            _assistant("t2", "Read", {"file_path": "/b.md"}),   # api call 2
            _result("t2", text),
            _assistant("t3", "Read", {"file_path": "/c.md"}),   # api call 3
        ]
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "s.jsonl")
            _write(p, records)
            rows = token_audit.carry_cost([p])
        by = {r.group: r for r in rows}
        # result 1 còn 2 call phía sau (call 2, 3) → 100*2 = 200
        # result 2 còn 1 call phía sau (call 3)    → 100*1 = 100
        self.assertEqual(by["Read file"].tokens, 300)
        self.assertEqual(by["Read file"].count, 2)

    def test_gom_nhom_theo_loai_lenh_bash(self):
        records = [
            _assistant("t1", "Bash", {"command": "python3 scripts/tdq_state.py next"}),
            _result("t1", "y" * 40),
            _assistant("t2", "Bash", {"command": "cd tests && python3 -m unittest discover"}),
            _result("t2", "y" * 40),
            _assistant("t3", "Bash", {"command": "ls"}),
            _result("t3", "y" * 40),
            _assistant("t4", "Edit", {"file_path": "/a.md"}),
        ]
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "s.jsonl")
            _write(p, records)
            groups = {r.group for r in token_audit.carry_cost([p])}
        self.assertIn("tdq_state.py (dump JSON)", groups)
        self.assertIn("chạy test suite", groups)
        self.assertIn("Bash khác", groups)

    def test_khong_co_session_tra_bang_rong(self):
        self.assertEqual(token_audit.carry_cost([]), [])


class UsageTotalsTest(unittest.TestCase):
    def test_cong_don_usage_va_dem_api_call(self):
        records = [
            _assistant("t1", "Read", {"file_path": "/a.md"}),
            _result("t1", "z" * 8),
            _assistant("t2", "Read", {"file_path": "/b.md"}),
        ]
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "s.jsonl")
            _write(p, records)
            tot = token_audit.usage_totals([p])
        self.assertEqual(tot["api_calls"], 2)
        self.assertEqual(tot["cache_read"], 200)
        self.assertEqual(tot["output"], 2)


def _assistant_line(mid, blocks, usage=None):
    """Một DÒNG jsonl của message `mid` — Claude Code tách 1 message ra nhiều dòng."""
    msg = {"role": "assistant", "id": mid, "content": blocks}
    msg["usage"] = usage or {"input_tokens": 10, "output_tokens": 5,
                             "cache_read_input_tokens": 100,
                             "cache_creation_input_tokens": 20}
    return {"type": "assistant", "message": msg}


class MessageIdTest(unittest.TestCase):
    """Một message nằm nhiều dòng jsonl → chỉ được tính LÀ MỘT API call."""

    def _records(self):
        return [
            _assistant_line("msg_1", [{"type": "thinking", "thinking": "..."}]),
            _assistant_line("msg_1", [{"type": "text", "text": "làm thôi"}]),
            _assistant_line("msg_1", [{"type": "tool_use", "id": "t1",
                                       "name": "Read", "input": {"file_path": "/a.md"}}]),
            _assistant_line("msg_1", [{"type": "tool_use", "id": "t1",
                                       "name": "Read", "input": {"file_path": "/a.md"}}]),
        ]

    def test_ba_dong_cung_message_id_dem_mot_api_call(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "s.jsonl")
            _write(p, self._records())
            tot = token_audit.usage_totals([p])
        self.assertEqual(tot["api_calls"], 1)

    def test_usage_cong_mot_lan_cho_moi_message(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "s.jsonl")
            _write(p, self._records())
            tot = token_audit.usage_totals([p])
        self.assertEqual(tot["cache_read"], 100)
        self.assertEqual(tot["cache_write"], 20)
        self.assertEqual(tot["input"], 10)
        self.assertEqual(tot["output"], 5)

    def test_dedup_tool_use_theo_id(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "s.jsonl")
            _write(p, self._records())
            tot = token_audit.usage_totals([p])
        self.assertEqual(tot["tool_calls"], 1)

    def test_message_khong_co_id_van_dem_tung_dong(self):
        # transcript cũ/không có `message.id` → giữ nguyên cách đếm cũ, không mất số
        records = [
            _assistant("t1", "Read", {"file_path": "/a.md"}),
            _assistant("t2", "Read", {"file_path": "/b.md"}),
        ]
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "s.jsonl")
            _write(p, records)
            tot = token_audit.usage_totals([p])
        self.assertEqual(tot["api_calls"], 2)
        self.assertEqual(tot["tool_calls"], 2)


class CostEquivalentTest(unittest.TestCase):
    """Quy hóa đơn về input-token tương đương theo hệ số của trang giá chính thức."""

    TOTALS = {"cache_read": 1000, "cache_write": 100, "input": 10, "output": 20}

    def test_ttl_1h_dung_he_so_2(self):
        # 1000*0,1 + 100*2 + 10*1 + 20*5 = 410
        equiv, parts = token_audit.cost_equivalent(self.TOTALS, "1h")
        self.assertEqual(equiv, 410)
        self.assertEqual(parts["cache_write"], 200)

    def test_ttl_5m_dung_he_so_1_25(self):
        # 1000*0,1 + 100*1,25 + 10*1 + 20*5 = 335
        equiv, _ = token_audit.cost_equivalent(self.TOTALS, "5m")
        self.assertEqual(equiv, 335)

    def test_mac_dinh_la_ttl_1h(self):
        self.assertEqual(token_audit.cost_equivalent(self.TOTALS)[0], 410)

    def test_totals_rong_tra_0(self):
        self.assertEqual(token_audit.cost_equivalent({})[0], 0)


class CliTest(unittest.TestCase):
    def _run(self, args, env=None):
        e = dict(os.environ)
        if env:
            e.update(env)
        return subprocess.run(
            [sys.executable, os.path.join(REPO, "scripts", "token_audit.py")] + args,
            capture_output=True, text=True, env=e)

    def test_khong_co_session_van_exit_0(self):
        with tempfile.TemporaryDirectory() as d:
            r = self._run(["--transcript-dir", d])
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_in_bang_carry_cost(self):
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "s.jsonl"), [
                _assistant("t1", "Read", {"file_path": "/a.md"}),
                _result("t1", "q" * 400),
                _assistant("t2", "Read", {"file_path": "/b.md"}),
            ])
            r = self._run(["--transcript-dir", d])
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("carry-cost", r.stdout)
        self.assertIn("Read file", r.stdout)

    def test_log_bat_mac_dinh_ra_stderr(self):
        with tempfile.TemporaryDirectory() as d:
            r = self._run(["--transcript-dir", d])
        self.assertTrue(r.stderr.strip(), "log phải bật mặc định")

    def test_tat_log_bang_bien_moi_truong(self):
        with tempfile.TemporaryDirectory() as d:
            r = self._run(["--transcript-dir", d], env={"TDQ_AUDIT_LOG": "0"})
        self.assertEqual(r.stderr.strip(), "")


if __name__ == "__main__":
    unittest.main()
