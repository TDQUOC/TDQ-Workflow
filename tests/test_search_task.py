"""Test search_task.py — deep search điều phối multi-call agy (stub binary, không mạng)."""
import json
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT = os.path.join(ROOT, "scripts", "search_task.py")
SCHEMA = os.path.join(ROOT, "scripts", "search_report_schema.json")
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import search_task  # noqa: E402


def good_finding(**overrides):
    finding = {
        "route": "docs chính thức",
        "claim": "typescript mới nhất là 7.0.2",
        "source_url": "https://www.npmjs.com/package/typescript",
        "evidence_quote": "7.0.2 • Public • Published",
        "score": 8,
    }
    finding.update(overrides)
    return finding


def good_report(**overrides):
    report = {
        "findings": [good_finding()],
        "not_found": False,
        "queries_used": ["typescript latest version npm"],
    }
    report.update(overrides)
    return report


class SchemaTest(unittest.TestCase):
    """T1.1 — schema all-required, URL bắt buộc có path."""

    def test_schema_file_exists_all_required(self):
        with open(SCHEMA, encoding="utf-8") as f:
            schema = json.load(f)
        self.assertEqual(schema["type"], "object")
        self.assertEqual(sorted(schema["required"]),
                         ["findings", "not_found", "queries_used"])
        item = schema["properties"]["findings"]["items"]
        self.assertEqual(sorted(item["required"]),
                         ["claim", "evidence_quote", "route", "score", "source_url"])
        self.assertEqual(item["properties"]["source_url"]["pattern"],
                         r"^https?://[^/]+/\S+$")

    def test_valid_report_passes(self):
        self.assertEqual(search_task.validate_report(good_report()), [])

    def test_bare_domain_url_fails(self):
        for url in ("https://npmjs.com", "https://npmjs.com/", "http://x.y",
                    "ftp://a.b/c", "npmjs.com/package/typescript"):
            report = good_report(findings=[good_finding(source_url=url)])
            self.assertNotEqual(search_task.validate_report(report), [], url)

    def test_missing_key_fails(self):
        report = good_report()
        del report["not_found"]
        self.assertNotEqual(search_task.validate_report(report), [])
        finding = good_finding()
        del finding["evidence_quote"]
        self.assertNotEqual(
            search_task.validate_report(good_report(findings=[finding])), [])

    def test_score_out_of_range_fails(self):
        for score in (-1, 11, "8"):
            report = good_report(findings=[good_finding(score=score)])
            self.assertNotEqual(search_task.validate_report(report), [], score)


class EnvTest(unittest.TestCase):
    """T1.2 — env default 3/5/3/540, giá trị rác → default + warn stderr."""

    def _read_env(self, **env):
        import contextlib
        import io
        from unittest import mock
        stderr = io.StringIO()
        clean = {k: v for k, v in os.environ.items()
                 if not k.startswith("TDQ_SEARCH_")}
        clean.update(env)
        with mock.patch.dict(os.environ, clean, clear=True), \
                contextlib.redirect_stderr(stderr):
            return search_task.read_env(), stderr.getvalue()

    def test_defaults_when_unset(self):
        cfg, err = self._read_env()
        self.assertEqual(cfg, {"TDQ_SEARCH_MAX_AGENTS": 3,
                               "TDQ_SEARCH_MAX_ROUTES": 5,
                               "TDQ_SEARCH_URLS_PER_ROUTE": 3,
                               "TDQ_SEARCH_TIMEOUT": 540})
        self.assertEqual(err, "")

    def test_valid_override(self):
        cfg, err = self._read_env(TDQ_SEARCH_MAX_AGENTS="1",
                                  TDQ_SEARCH_TIMEOUT="60")
        self.assertEqual(cfg["TDQ_SEARCH_MAX_AGENTS"], 1)
        self.assertEqual(cfg["TDQ_SEARCH_TIMEOUT"], 60)
        self.assertEqual(err, "")

    def test_garbage_falls_back_with_warn(self):
        for bad in ("abc", "0", "-2", "3.5"):
            cfg, err = self._read_env(TDQ_SEARCH_MAX_AGENTS=bad)
            self.assertEqual(cfg["TDQ_SEARCH_MAX_AGENTS"], 3, bad)
            self.assertIn("TDQ_SEARCH_MAX_AGENTS", err, bad)


class DefaultModelTest(unittest.TestCase):
    """T1.1 (0.6.0) — default flash-medium, escalation flash-high, docs đồng bộ."""

    def test_default_model_is_flash_medium(self):
        self.assertEqual(search_task.DEFAULT_MODEL, "gemini-3.6-flash-medium")

    def test_escalation_model_stays_flash_high(self):
        self.assertEqual(search_task.ESCALATION_MODEL, "gemini-3.6-flash-high")

    def test_no_stale_flash_low_anywhere_in_script(self):
        with open(SCRIPT, encoding="utf-8") as f:
            self.assertNotIn("flash-low", f.read())


class SplitTest(unittest.TestCase):
    """T2.1 — cap agent enforce bằng code, chia đều route, cắt route thừa + warn."""

    def _split(self, routes, extra_args=(), **env):
        import subprocess
        clean = {k: v for k, v in os.environ.items()
                 if not k.startswith("TDQ_SEARCH_")}
        clean.update(env)
        proc = subprocess.run(
            [sys.executable, SCRIPT, "split", "--routes", ",".join(routes),
             *extra_args],
            capture_output=True, text=True, timeout=30, env=clean)
        return proc.returncode, proc.stdout, proc.stderr

    def test_env_1_single_agent_gets_all(self):
        code, out, _ = self._split(["a", "b", "c"], TDQ_SEARCH_MAX_AGENTS="1")
        self.assertEqual(code, 0)
        data = json.loads(out)
        self.assertEqual(len(data["assignments"]), 1)
        self.assertEqual(data["assignments"][0], {"agent": 1, "routes": ["a", "b", "c"]})

    def test_env_3_five_routes_no_dup_no_loss(self):
        code, out, _ = self._split(["a", "b", "c", "d", "e"],
                                   TDQ_SEARCH_MAX_AGENTS="3")
        self.assertEqual(code, 0)
        data = json.loads(out)
        self.assertLessEqual(len(data["assignments"]), 3)
        got = [r for a in data["assignments"] for r in a["routes"]]
        self.assertEqual(sorted(got), ["a", "b", "c", "d", "e"])
        self.assertEqual(len(got), len(set(got)))

    def test_seven_routes_cut_to_five_with_warn(self):
        code, out, err = self._split(["a", "b", "c", "d", "e", "f", "g"])
        self.assertEqual(code, 0)
        got = [r for a in json.loads(out)["assignments"] for r in a["routes"]]
        self.assertEqual(sorted(got), ["a", "b", "c", "d", "e"])
        self.assertIn("f", err)
        self.assertIn("g", err)

    def test_garbage_env_defaults_with_warn(self):
        code, out, err = self._split(["a", "b", "c", "d"],
                                     TDQ_SEARCH_MAX_AGENTS="rác")
        self.assertEqual(code, 0)
        self.assertLessEqual(len(json.loads(out)["assignments"]), 3)
        self.assertIn("TDQ_SEARCH_MAX_AGENTS", err)

    def test_agents_never_exceed_routes(self):
        code, out, _ = self._split(["a", "b"], TDQ_SEARCH_MAX_AGENTS="3")
        self.assertEqual(code, 0)
        self.assertEqual(len(json.loads(out)["assignments"]), 2)

    def test_max_agents_flag_overrides_env(self):
        code, out, _ = self._split(["a", "b", "c"], ("--max-agents", "2"),
                                   TDQ_SEARCH_MAX_AGENTS="3")
        self.assertEqual(code, 0)
        self.assertEqual(len(json.loads(out)["assignments"]), 2)

    def test_start_agent_3_numbers_from_3(self):
        code, out, _ = self._split(["a", "b", "c"], ("--start-agent", "3"),
                                   TDQ_SEARCH_MAX_AGENTS="3")
        self.assertEqual(code, 0)
        agents = [a["agent"] for a in json.loads(out)["assignments"]]
        self.assertEqual(agents, [3, 4, 5])

    def test_start_agent_default_is_1(self):
        code, out, _ = self._split(["a", "b", "c"], TDQ_SEARCH_MAX_AGENTS="3")
        self.assertEqual(code, 0)
        agents = [a["agent"] for a in json.loads(out)["assignments"]]
        self.assertEqual(agents, [1, 2, 3])

    def test_start_agent_garbage_exit_2(self):
        code, _, err = self._split(["a", "b"], ("--start-agent", "rác"))
        self.assertEqual(code, 2)
        self.assertIn("start-agent", err)


class BuildCommandTest(unittest.TestCase):
    """T3.1 — lệnh agy đúng flags; prompt khuôn grounded đủ 3 luật.
    Effort nằm trong model slug (flash-low/flash-high), không có flag riêng."""

    def test_command_flags(self):
        argv = search_task.build_command("gemini-3.6-flash-low", "PROMPT", 540)
        self.assertEqual(argv[0], "agy")
        for flag, value in (("-p", "PROMPT"), ("--model", "gemini-3.6-flash-low"),
                            ("--json-schema", SCHEMA),
                            ("--output-format", "json"),
                            ("--print-timeout", "540s")):
            idx = argv.index(flag)
            self.assertEqual(argv[idx + 1], value)
        self.assertIn("--dangerously-skip-permissions", argv)
        self.assertNotIn("--effort", argv)

    def _assert_grounded(self, prompt):
        self.assertIn("not_found", prompt)          # luật 1: evidence-only
        self.assertIn("chỉ dẫn", prompt)            # luật 2: chống injection
        self.assertIn("URL đầy đủ", prompt)         # luật 3: full URL từ tool

    def test_search_prompt_grounded(self):
        prompt = search_task.build_search_prompt("BRIEF-đầy-đủ", "route-A")
        self.assertIn("BRIEF-đầy-đủ", prompt)
        self.assertIn("route-A", prompt)
        self._assert_grounded(prompt)

    def test_url_prompt_grounded(self):
        prompt = search_task.build_url_prompt("BRIEF-đầy-đủ", "route-A",
                                              "https://x.y/z")
        self.assertIn("https://x.y/z", prompt)
        self._assert_grounded(prompt)


class StubBase(unittest.TestCase):
    """Dựng stub binary agy trong PATH + run-dir tạm. Không mạng, không binary thật."""

    MODELS = "gemini-3.6-flash-medium\ngemini-3.6-flash-high\n"

    def setUp(self):
        import shutil
        import stat
        import tempfile
        self.tmp = tempfile.mkdtemp(prefix="tdq-search-")
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.bin_dir = os.path.join(self.tmp, "bin")
        self.resp_dir = os.path.join(self.tmp, "resp")
        self.project = os.path.join(self.tmp, "project")
        for d in (self.bin_dir, self.resp_dir, self.project):
            os.makedirs(d)
        self.run_dir = os.path.join(self.project, "docs", "tdq", "research",
                                    "search", "2026-07-31-demo-run")
        self.capture = os.path.join(self.tmp, "capture.txt")
        self.count = os.path.join(self.tmp, "count.txt")
        self.brief = os.path.join(self.tmp, "brief.md")
        with open(self.brief, "w", encoding="utf-8") as f:
            f.write("# BRIEF\nCâu hỏi demo.\n")
        self.set_models(self.MODELS)
        path = os.path.join(self.bin_dir, "agy")
        with open(path, "w", encoding="utf-8") as f:
            f.write(
                '#!/bin/sh\n'
                'PATH=/bin:/usr/bin\n'
                'case "$1" in\n'
                '  --version) echo "agy 1.1.8"; exit 0;;\n'
                f'  models) cat "{self.resp_dir}/models.txt"; '
                f'exit $(cat "{self.resp_dir}/models_exit" 2>/dev/null || echo 0);;\n'
                'esac\n'
                f'n=$(cat "{self.count}" 2>/dev/null || echo 0)\n'
                'n=$((n+1))\n'
                f'echo $n > "{self.count}"\n'
                f'printf \'CALL%s: %s\\n\' "$n" "$*" >> "{self.capture}"\n'
                f'if [ -f "{self.resp_dir}/sleep$n" ]; then sleep 5; fi\n'
                f'cat "{self.resp_dir}/resp$n.json" 2>/dev/null\n'
                f'exit $(cat "{self.resp_dir}/exit$n" 2>/dev/null || echo 0)\n')
        import stat as _stat
        os.chmod(path, os.stat(path).st_mode | _stat.S_IEXEC)

    def set_models(self, text):
        with open(os.path.join(self.resp_dir, "models.txt"), "w",
                  encoding="utf-8") as f:
            f.write(text)

    def set_response(self, n, data, exit_code=0):
        """Response cho call agy -p thứ n. agy bọc structured_output trong JSON vỏ."""
        if isinstance(data, dict) and "structured_output" not in data:
            data = {"response": "ok", "structured_output": data}
        with open(os.path.join(self.resp_dir, f"resp{n}.json"), "w",
                  encoding="utf-8") as f:
            f.write(data if isinstance(data, str) else json.dumps(data))
        with open(os.path.join(self.resp_dir, f"exit{n}"), "w") as f:
            f.write(str(exit_code))

    def run_cli(self, *args, env=None, alive=True):
        """Chạy search_task.main IN-PROCESS: PATH → stub, HTTP → mock."""
        import contextlib
        import io
        from unittest import mock
        clean = {k: v for k, v in os.environ.items()
                 if not k.startswith("TDQ_SEARCH_")}
        clean["PATH"] = self.bin_dir
        clean.update(env or {})
        stdout, stderr = io.StringIO(), io.StringIO()
        cwd = os.getcwd()
        os.chdir(self.project)
        try:
            with mock.patch.dict(os.environ, clean, clear=True), \
                    mock.patch.object(search_task, "_http_status",
                                      self._http_status(alive)), \
                    contextlib.redirect_stdout(stdout), \
                    contextlib.redirect_stderr(stderr):
                code = search_task.main(list(args))
        finally:
            os.chdir(cwd)
        return code, stdout.getvalue(), stderr.getvalue()

    @staticmethod
    def _http_status(alive):
        def fake(url, method):
            if alive is True:
                return 200
            if alive is False:
                return None
            return alive(url, method)
        return fake

    def calls(self):
        import re as _re
        try:
            with open(self.capture, encoding="utf-8") as f:
                text = f.read()
        except OSError:
            return []
        return _re.split(r"(?m)^CALL\d+: ", text)[1:]

    def agent_json(self, k=1):
        return os.path.join(self.run_dir, f"agent-{k}.json")

    def agent_log(self, k=1):
        return os.path.join(self.run_dir, f"agent-{k}.log")

    def run_agent(self, routes="route-A", agent="1", env=None, alive=True,
                  run_dir=None):
        return self.run_cli("run", "--brief", self.brief,
                            "--run-dir", run_dir or self.run_dir,
                            "--agent", agent, "--routes", routes,
                            env=env, alive=alive)


class PreflightTest(StubBase):
    """T3.2 — validate agy CLI + CẢ hai model slug qua external_models.py."""

    def test_missing_slug_engine_failed_exit_3(self):
        self.set_models("gemini-3.6-flash-low\n")   # thiếu slug escalation
        code, _, err = self.run_agent()
        self.assertEqual(code, 3)
        self.assertIn("engine-failed", err)
        self.assertIn("gemini-3.6-flash-high", err)
        self.assertEqual(self.calls(), [])          # không call -p nào được chạy

    def test_wrong_default_slug_engine_failed(self):
        code, _, err = self.run_cli(
            "run", "--brief", self.brief, "--run-dir", self.run_dir,
            "--agent", "1", "--routes", "r", "--model", "slug-không-tồn-tại")
        self.assertEqual(code, 3)
        self.assertIn("engine-failed", err)

    def test_agy_models_broken_engine_failed(self):
        with open(os.path.join(self.resp_dir, "models_exit"), "w") as f:
            f.write("1")
        code, _, err = self.run_agent()
        self.assertEqual(code, 3)
        self.assertIn("engine-failed", err)


class RunRouteTest(StubBase):
    """T3.3 — 1 call search + ≤N call đọc URL; parse structured_output; gộp finding."""

    def test_search_plus_url_reads_capped(self):
        urls = [f"https://site{i}.com/page{i}" for i in range(5)]
        self.set_response(1, good_report(findings=[
            good_finding(source_url=u, claim=f"claim {i}")
            for i, u in enumerate(urls)]))
        for n in (2, 3):
            self.set_response(n, good_report(findings=[good_finding(
                source_url=urls[n - 2], claim=f"enriched {n}")]))
        code, _, _ = self.run_agent(env={"TDQ_SEARCH_URLS_PER_ROUTE": "2"})
        self.assertEqual(code, 0)
        self.assertEqual(len(self.calls()), 3)      # 1 search + 2 đọc URL (cap)
        with open(self.agent_json(), encoding="utf-8") as f:
            data = json.load(f)
        self.assertEqual(data["agent"], 1)
        claims = {fnd["claim"] for fnd in data["findings"]}
        self.assertIn("claim 0", claims)
        self.assertIn("enriched 2", claims)
        for fnd in data["findings"]:
            self.assertIn("url_alive", fnd)

    def test_not_found_route_accepted(self):
        self.set_response(1, good_report(findings=[], not_found=True))
        code, _, _ = self.run_agent()
        self.assertEqual(code, 0)
        with open(self.agent_json(), encoding="utf-8") as f:
            data = json.load(f)
        self.assertEqual(data["findings"], [])
        self.assertTrue(data["not_found"])


class RetryEscalationTest(StubBase):
    """T3.4 — retry ≤2 kèm lỗi cũ, retry dùng slug escalation."""

    def test_bad_json_then_escalated_retry(self):
        self.set_response(1, "not json at all")
        self.set_response(2, good_report())
        code, _, _ = self.run_agent(env={"TDQ_SEARCH_URLS_PER_ROUTE": "0"})
        self.assertEqual(code, 0)
        calls = self.calls()
        self.assertEqual(len(calls), 2)
        self.assertIn("gemini-3.6-flash-medium", calls[0])
        self.assertIn("gemini-3.6-flash-high", calls[1])
        self.assertIn("LỖI LẦN TRƯỚC", calls[1])
        self.assertIn("JSON", calls[1])

    def test_three_bad_attempts_route_fails(self):
        for n in (1, 2, 3):
            self.set_response(n, "garbage")
        code, _, err = self.run_agent()
        self.assertEqual(code, 1)
        self.assertEqual(len(self.calls()), 3)
        self.assertIn("engine-failed", err)


class UrlAliveTest(StubBase):
    """T3.5 — HEAD → GET; 2xx/3xx sống; 403/405 sau GET sống; chết → loại."""

    def _run_with(self, statuses):
        log = []

        def fake(url, method):
            log.append((url, method))
            return statuses.get((url, method), statuses.get(url))

        self.set_response(1, good_report(findings=[
            good_finding(source_url="https://a.com/x", claim="c1"),
            good_finding(source_url="https://b.com/x", claim="c2")]))
        code, _, _ = self.run_agent(env={"TDQ_SEARCH_URLS_PER_ROUTE": "0"},
                                    alive=fake)
        with open(self.agent_json(), encoding="utf-8") as f:
            return code, json.load(f), log

    def test_head_2xx_alive(self):
        code, data, log = self._run_with({"https://a.com/x": 200,
                                          "https://b.com/x": 301})
        self.assertEqual(code, 0)
        self.assertEqual(len(data["findings"]), 2)
        self.assertTrue(all(f["url_alive"] for f in data["findings"]))

    def test_head_fail_get_2xx_alive(self):
        code, data, log = self._run_with({
            ("https://a.com/x", "HEAD"): 500, ("https://a.com/x", "GET"): 200,
            "https://b.com/x": 200})
        self.assertEqual(len(data["findings"]), 2)
        self.assertIn(("https://a.com/x", "GET"), log)

    def test_get_403_405_still_alive(self):
        code, data, _ = self._run_with({
            ("https://a.com/x", "HEAD"): 403, ("https://a.com/x", "GET"): 403,
            ("https://b.com/x", "HEAD"): 405, ("https://b.com/x", "GET"): 405})
        self.assertEqual(len(data["findings"]), 2)

    def test_dead_url_dropped(self):
        code, data, _ = self._run_with({
            ("https://a.com/x", "HEAD"): 404, ("https://a.com/x", "GET"): 404,
            "https://b.com/x": 200})
        urls = [f["source_url"] for f in data["findings"]]
        self.assertEqual(urls, ["https://b.com/x"])

    def test_timeout_none_dropped(self):
        code, data, _ = self._run_with({
            ("https://a.com/x", "HEAD"): None, ("https://a.com/x", "GET"): None,
            "https://b.com/x": 200})
        urls = [f["source_url"] for f in data["findings"]]
        self.assertEqual(urls, ["https://b.com/x"])


class CallTimeoutTest(StubBase):
    """T3.6 — call quá TDQ_SEARCH_TIMEOUT bị kill, tính 1 lần fail → retry."""

    def test_hung_call_killed_and_retried(self):
        import time
        with open(os.path.join(self.resp_dir, "sleep1"), "w") as f:
            f.write("1")
        self.set_response(2, good_report())
        start = time.monotonic()
        code, _, _ = self.run_agent(env={"TDQ_SEARCH_TIMEOUT": "1",
                                         "TDQ_SEARCH_URLS_PER_ROUTE": "0"})
        self.assertEqual(code, 0)
        self.assertLess(time.monotonic() - start, 5)
        self.assertEqual(len(self.calls()), 2)
        with open(self.agent_log(), encoding="utf-8") as f:
            self.assertIn("timeout", f.read())


class RunLayoutLogTest(StubBase):
    """T3.7 — run-dir đúng run-id, brief.md copy vào, log per-agent ISO, LOG=0 tắt."""

    def test_layout_and_log_fields(self):
        self.set_response(1, good_report())
        code, _, _ = self.run_agent()
        self.assertEqual(code, 0)
        self.assertTrue(os.path.isfile(os.path.join(self.run_dir, "brief.md")))
        self.assertTrue(os.path.isfile(self.agent_json()))
        with open(self.agent_log(), encoding="utf-8") as f:
            log = f.read()
        self.assertRegex(log, r"\[\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}")
        for field in ("model=", "agy=", "route=", "exit=", "findings=", "secs="):
            self.assertIn(field, log)

    def test_bad_run_id_exit_2(self):
        bad = os.path.join(self.project, "docs", "tdq", "research", "search",
                           "Không_Hợp_Lệ")
        code, _, err = self.run_agent(run_dir=bad)
        self.assertEqual(code, 2)
        self.assertIn("run-id", err)
        self.assertFalse(os.path.isdir(bad))

    def test_log_disabled(self):
        self.set_response(1, good_report())
        code, _, _ = self.run_agent(env={"TDQ_SEARCH_LOG": "0"})
        self.assertEqual(code, 0)
        self.assertFalse(os.path.exists(self.agent_log()))


class MergeTest(StubBase):
    """T4.1 + T4.2 — dedup URL, rank tất định 5 khóa; merged.json + report ≤50 dòng
    + run.log gộp."""

    def _write_agent(self, k, findings, routes, log_lines=("call ok",)):
        os.makedirs(self.run_dir, exist_ok=True)
        with open(self.agent_json(k), "w", encoding="utf-8") as f:
            json.dump({"agent": k, "routes": routes, "routes_failed": [],
                       "findings": findings, "not_found": not findings,
                       "queries_used": [f"q{k}"]}, f, ensure_ascii=False)
        with open(self.agent_log(k), "w", encoding="utf-8") as f:
            for line in log_lines:
                f.write(f"[2026-07-31T15:00:00+07:00] agent={k} {line}\n")

    def _fixture(self):
        def fnd(route, claim, url, score, alive=True):
            return {"route": route, "claim": claim, "source_url": url,
                    "evidence_quote": f"quote {claim}", "score": score,
                    "url_alive": alive}
        # claim X: 2 route độc lập xác nhận, score thấp — phải đứng TRÊN claim Y
        # (1 route, score cao). Trùng URL giữa agent 1 và 2 → dedup còn 1.
        self._write_agent(1, [fnd("r1", "claim X", "https://a.com/x", 3)], ["r1"])
        self._write_agent(2, [fnd("r2", "claim X", "https://a.com/x", 2),
                              fnd("r2", "claim Y", "https://b.com/y", 9)], ["r2"])
        self._write_agent(3, [fnd("r3", "claim Z", "https://c.com/z", 9,
                                  alive=False)], ["r3"])

    def test_merge_dedup_and_deterministic_rank(self):
        self._fixture()
        code, _, _ = self.run_cli("merge", self.run_dir)
        self.assertEqual(code, 0)
        with open(os.path.join(self.run_dir, "merged.json"),
                  encoding="utf-8") as f:
            merged = json.load(f)
        urls = [fnd["source_url"] for fnd in merged["findings"]]
        self.assertEqual(len(urls), len(set(urls)))          # dedup URL
        self.assertEqual(urls[0], "https://a.com/x")         # 2 route thắng score 9
        # url_alive=False xếp sau url sống dù score cao
        self.assertLess(urls.index("https://b.com/y"), urls.index("https://c.com/z"))
        self.assertEqual(sorted(merged["queries_used"]), ["q1", "q2", "q3"])

    def test_report_le_50_lines_and_runlog_merged(self):
        self._fixture()
        code, _, _ = self.run_cli("merge", self.run_dir)
        self.assertEqual(code, 0)
        with open(os.path.join(self.run_dir, "report.md"), encoding="utf-8") as f:
            report = f.read()
        self.assertLessEqual(len(report.splitlines()), 50)
        self.assertIn("https://a.com/x", report)
        with open(os.path.join(self.run_dir, "run.log"), encoding="utf-8") as f:
            runlog = f.read()
        for k in (1, 2, 3):
            self.assertIn(f"agent={k}", runlog)

    def test_merge_accepts_empty_agents(self):
        self._write_agent(1, [], ["r1"])
        code, _, _ = self.run_cli("merge", self.run_dir)
        self.assertEqual(code, 0)
        with open(os.path.join(self.run_dir, "merged.json"),
                  encoding="utf-8") as f:
            merged = json.load(f)
        self.assertTrue(merged["not_found"])
        with open(os.path.join(self.run_dir, "report.md"), encoding="utf-8") as f:
            self.assertIn("r1", f.read())                    # route rỗng ghi rõ


class SearchRunnerAgentTest(unittest.TestCase):
    """T5.1 — agent vỏ mỏng đúng khuôn runner (như RunnerAgentsTest bên external)."""

    PATH = os.path.join(ROOT, "agents", "search-runner.md")

    def test_frontmatter(self):
        with open(self.PATH, encoding="utf-8") as f:
            text = f.read()
        self.assertTrue(text.startswith("---\n"))
        head = text.split("---", 2)[1]
        self.assertRegex(head, r"name:\s*search-runner")
        self.assertIn("description:", head)
        # QC1.1 (0.6.0): wrapper chỉ cần Bash + Read — tool schemas khác là token thừa
        self.assertRegex(head, r"tools:\s*Bash,\s*Read")

    def test_return_contract_summary_not_verbatim(self):
        # QC1.1 (0.6.0): trả tóm tắt, KHÔNG dán JSON nguyên văn (đếm đôi token)
        with open(self.PATH, encoding="utf-8") as f:
            text = f.read()
        self.assertNotIn("verbatim", text.lower())
        low = text.lower()
        self.assertTrue("tóm tắt" in low or "summary" in low)
        for part in ("findings", "not_found", "agent-<k>.json"):
            self.assertIn(part, text)

    def test_core_command_and_rules(self):
        with open(self.PATH, encoding="utf-8") as f:
            text = f.read()
        self.assertIn("search_task.py run", text)
        for part in ("--brief", "--run-dir", "--agent", "--routes",
                     "run_in_background", "engine-failed"):
            self.assertIn(part, text)
        low = text.lower()
        self.assertIn("orchestrator", low)          # không tự quyết fallback
        self.assertIn("synchronous", low)           # luật sync
        self.assertIn("không commit", low)


class SearchScoutAgentTest(unittest.TestCase):
    """0.6.0 — agent scout Claude+Tavily: vỏ mỏng, slot 2 phase 1 của flow hybrid."""

    PATH = os.path.join(ROOT, "agents", "search-scout.md")

    def _text(self):
        with open(self.PATH, encoding="utf-8") as f:
            return f.read()

    def test_frontmatter(self):
        text = self._text()
        self.assertTrue(text.startswith("---\n"))
        head = text.split("---", 2)[1]
        self.assertRegex(head, r"name:\s*search-scout")
        self.assertIn("description:", head)

    def test_slot_and_output_format(self):
        text = self._text()
        self.assertIn("scout:", text)               # prefix route slot 2
        self.assertIn("agent-2.json", text)         # format file agent, đúng slot
        for field in ("url_alive", "not_found", "queries_used",
                      "routes_failed", "evidence_quote"):
            self.assertIn(field, text, field)

    def test_route_suggestions_and_tavily_rules(self):
        text = self._text()
        self.assertIn("3–5 route", text)            # final message gợi ý route
        self.assertIn("tavily-primary", text)
        self.assertIn("tavily-extract", text)       # lấy quote khi cần
        self.assertIn("curl", text)                 # tự check URL sống

    def test_log_service_and_boundaries(self):
        text = self._text()
        self.assertIn("agent-2.log", text)
        self.assertIn("TDQ_SEARCH_LOG", text)       # =0 thì tắt log
        low = text.lower()
        self.assertIn("orchestrator", low)
        self.assertIn("không commit", low)
        self.assertIn("merge", low)                 # cấm tự merge


class DeepSearchDocTest(unittest.TestCase):
    """T5.2 — deep-search.md đủ 8 mục; T6.1 — tavily.md nêu tầng search."""

    DEEP = os.path.join(ROOT, "skills", "tdq-conventions", "references",
                        "deep-search.md")
    TAVILY = os.path.join(ROOT, "skills", "tdq-conventions", "references",
                          "tavily.md")

    def test_deep_search_eight_sections(self):
        with open(self.DEEP, encoding="utf-8") as f:
            text = f.read()
        for needle in ("≥2 dấu hiệu",              # 1. tiêu chí trigger
                       "FULL",                      # 2. brief full data
                       "not_found",                 # 3. evidence-only trong brief
                       "chỉ dẫn",                   # 3. chống injection
                       "split",                     # 4. Claude không tự chia
                       "TDQ_SEARCH_MAX_AGENTS",     # 5. cap qua env
                       "restart",                   # 5. note restart phiên
                       "settings.json",             # 6. hướng dẫn đặt env
                       "spot-check",                # 7. verify nguồn top
                       "engine-failed",             # 8. fallback Tavily
                       "Tavily"):
            self.assertIn(needle, text, needle)

    def test_hybrid_flow_needles(self):
        with open(self.DEEP, encoding="utf-8") as f:
            text = f.read()
        for needle in ("Phase 1",                   # flow 2 phase, luôn đủ
                       "Phase 2",
                       "tổng quát:",                # prefix slot 1 (agy rộng)
                       "scout:",                    # prefix slot 2 (Claude)
                       "search-scout",              # agent scout
                       "--start-agent 3",           # phase 2 đánh số từ 3
                       "brief-phase2.md",           # brief nối route đã chốt
                       "Hướng từ phase 1",          # mục nối vào brief
                       "ngoại lệ",                  # slot cố định ≠ luật split
                       "scout-failed",              # định nghĩa degrade (b)
                       "cả hai hỏng",               # degrade (c)
                       "SAU merge",                 # dòng degrade ghi sau merge
                       "gemini-3.6-flash-medium"):  # default model mới
            self.assertIn(needle, text, needle)

    def test_tavily_md_layering(self):
        with open(self.TAVILY, encoding="utf-8") as f:
            text = f.read()
        self.assertIn("search-runner", text)
        self.assertIn("deep-search.md", text)

    def test_doc_lint_clean(self):
        import subprocess
        proc = subprocess.run(
            [sys.executable, os.path.join(ROOT, "scripts", "doc_lint.py"),
             self.DEEP, self.TAVILY],
            capture_output=True, text=True, timeout=30)
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)


if __name__ == "__main__":
    unittest.main()
