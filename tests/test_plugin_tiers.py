"""Test cho scripts/plugin_tiers.py — HOME giả trong tmpdir."""
import json
import os
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT = os.path.join(ROOT, "scripts", "plugin_tiers.py")

ALWAYS_OFF = [
    "firecrawl", "chrome-devtools-mcp", "lumen", "greptile", "sonarqube",
    "learning-output-style",
]
ON_DEMAND = [
    "data-engineering", "huggingface-skills", "hyperframes",
    "datarobot-agent-skills", "figma", "qt-development-skills", "cloudflare",
    "canva", "adobe-for-creativity", "mongodb", "postman", "desktop-commander",
    "base44", "unreal-engine-skills-for-claude-code", "notion",
    "redis-development",
]
MK = "@claude-plugins-official"


class TierBase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.home = self.tmp.name
        self.claude = os.path.join(self.home, ".claude")
        os.makedirs(self.claude)
        self.settings_path = os.path.join(self.claude, "settings.json")
        self.tiers_path = os.path.join(self.claude, "plugin-tiers.json")
        self.write_tiers({"always_off": ALWAYS_OFF, "on_demand": ON_DEMAND})
        enabled = {name + MK: True for name in ALWAYS_OFF + ON_DEMAND}
        enabled["tdq-workflow@tdq-local"] = True
        enabled["tavily" + MK] = True
        self.base_settings = {
            "model": "opus",
            "permissions": {"allow": ["Bash(ls:*)"]},
            "env": {"FOO": "bar"},
            "hooks": {"PreToolUse": [{"hooks": [{"type": "command",
                                                 "command": "echo hi"}]}]},
            "enabledPlugins": enabled,
        }
        self.write_settings(self.base_settings)

    def write_tiers(self, data):
        with open(self.tiers_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def write_settings(self, data):
        with open(self.settings_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            f.write("\n")

    def read_settings(self):
        with open(self.settings_path, encoding="utf-8") as f:
            return json.load(f)

    def run_cli(self, *args, env_extra=None):
        env = dict(os.environ, HOME=self.home)
        env.pop("PLUGIN_TIERS_LOG", None)
        if env_extra:
            env.update(env_extra)
        return subprocess.run([sys.executable, SCRIPT, *args],
                              capture_output=True, text=True, env=env)


class StatusTest(TierBase):
    def test_status_lists_all_tiers(self):
        proc = self.run_cli("status")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        lines = [l for l in proc.stdout.splitlines() if " | " in l]
        self.assertEqual(len(lines), len(ALWAYS_OFF) + len(ON_DEMAND))
        self.assertIn("firecrawl | always_off | True", proc.stdout)
        self.assertIn("figma | on_demand | True", proc.stdout)

    def test_bad_usage_exit_2(self):
        for args in ([], ["nosuch"], ["enable"], ["reset", "extra"]):
            proc = self.run_cli(*args)
            self.assertEqual(proc.returncode, 2, f"args={args}: {proc.stderr}")


class ResetTest(TierBase):
    def test_reset_sets_22_false(self):
        proc = self.run_cli("reset")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        enabled = self.read_settings()["enabledPlugins"]
        for name in ALWAYS_OFF + ON_DEMAND:
            self.assertIs(enabled[name + MK], False, name)
        self.assertIs(enabled["tdq-workflow@tdq-local"], True)
        self.assertIs(enabled["tavily" + MK], True)

    def test_backup_bak(self):
        with open(self.settings_path, encoding="utf-8") as f:
            before = f.read()
        self.run_cli("reset")
        bak = self.settings_path + ".bak"
        self.assertTrue(os.path.exists(bak))
        with open(bak, encoding="utf-8") as f:
            self.assertEqual(f.read(), before)

    def test_preserves_other_keys(self):
        before = self.read_settings()
        proc = self.run_cli("reset")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        after = self.read_settings()
        tier_keys = {n + MK for n in ALWAYS_OFF + ON_DEMAND}
        strip = lambda d: {k: v for k, v in d.items() if k != "enabledPlugins"}
        self.assertEqual(strip(before), strip(after))
        ep_before = {k: v for k, v in before["enabledPlugins"].items()
                     if k not in tier_keys}
        ep_after = {k: v for k, v in after["enabledPlugins"].items()
                    if k not in tier_keys}
        self.assertEqual(ep_before, ep_after)


class EnableTest(TierBase):
    def test_enable_on_demand(self):
        proc = self.run_cli("enable", "figma")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.run_cli("reset")
        proc = self.run_cli("enable", "figma")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIs(self.read_settings()["enabledPlugins"]["figma" + MK], True)

    def test_enable_always_off_refused(self):
        self.run_cli("reset")
        proc = self.run_cli("enable", "lumen")
        self.assertEqual(proc.returncode, 0)
        self.assertIn("⚠️", proc.stderr)
        self.assertIs(self.read_settings()["enabledPlugins"]["lumen" + MK], False)

    def test_enable_unknown_refused(self):
        before = self.read_settings()
        proc = self.run_cli("enable", "khong-ton-tai")
        self.assertEqual(proc.returncode, 0)
        self.assertIn("⚠️", proc.stderr)
        self.assertEqual(self.read_settings(), before)


class BrokenInputTest(TierBase):
    def check_no_touch(self, path):
        with open(path, encoding="utf-8") as f:
            before = f.read()
        for cmd in (["reset"], ["enable", "figma"]):
            proc = self.run_cli(*cmd)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertIn("⚠️", proc.stderr)
            self.assertNotIn("Traceback", proc.stderr)
        with open(path, encoding="utf-8") as f:
            self.assertEqual(f.read(), before)

    def test_settings_broken(self):
        with open(self.settings_path, "w", encoding="utf-8") as f:
            f.write("{hỏng")
        self.check_no_touch(self.settings_path)

    def test_settings_missing(self):
        os.unlink(self.settings_path)
        proc = self.run_cli("reset")
        self.assertEqual(proc.returncode, 0)
        self.assertIn("⚠️", proc.stderr)
        self.assertFalse(os.path.exists(self.settings_path))

    def test_tiers_broken(self):
        with open(self.tiers_path, "w", encoding="utf-8") as f:
            f.write("[[[")
        self.check_no_touch(self.settings_path)

    def test_tiers_missing(self):
        os.unlink(self.tiers_path)
        with open(self.settings_path, encoding="utf-8") as f:
            before = f.read()
        proc = self.run_cli("reset")
        self.assertEqual(proc.returncode, 0)
        self.assertIn("⚠️", proc.stderr)
        with open(self.settings_path, encoding="utf-8") as f:
            self.assertEqual(f.read(), before)


class LogTest(TierBase):
    @property
    def log_path(self):
        return os.path.join(self.claude, "logs", "plugin-tiers.log")

    def test_log_written_with_timestamp(self):
        self.run_cli("reset")
        self.run_cli("enable", "figma")
        with open(self.log_path, encoding="utf-8") as f:
            body = f.read()
        self.assertRegex(body, r"\[\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}")
        self.assertIn("reset:", body)
        self.assertIn("enable figma" + MK + ": False→True", body)

    def test_log_off(self):
        proc = self.run_cli("reset", env_extra={"PLUGIN_TIERS_LOG": "0"})
        self.assertEqual(proc.returncode, 0)
        self.assertFalse(os.path.exists(self.log_path))


class IdempotentTest(TierBase):
    def test_idempotent(self):
        self.run_cli("reset")
        with open(self.settings_path, encoding="utf-8") as f:
            first = f.read()
        proc = self.run_cli("reset")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        with open(self.settings_path, encoding="utf-8") as f:
            self.assertEqual(f.read(), first)
        log = os.path.join(self.claude, "logs", "plugin-tiers.log")
        with open(log, encoding="utf-8") as f:
            self.assertIn("0 changes", f.read())


if __name__ == "__main__":
    unittest.main()
