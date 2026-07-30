"""P1 (0.3.3) — scripts/skill_inventory.py: kiểm kê skill trên đĩa.

Script là nửa "kiểm chứng được" của bước kiểm kê năng lực: quét đúng 3 nguồn
(user, project, plugin đang bật), cấm quét cache, và luôn nhắc model chép thêm
skill built-in (thứ không tồn tại trên đĩa).
"""
import json
import os
import subprocess
import sys
import tempfile
import unittest

from helper import ROOT

SCRIPT = os.path.join(ROOT, "scripts", "skill_inventory.py")

REMINDER_1 = "— Bảng trên chỉ gồm skill trên đĩa."
REMINDER_2 = ("— CHÉP THÊM các skill built-in đang thấy trong context "
              "vào bảng kiểm kê rồi phán quyết từng dòng.")


def skill_md(name, desc="mô tả ngắn"):
    return f"---\nname: {name}\ndescription: {desc}\n---\n\n# {name}\n"


class InventoryBase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.home = os.path.join(self.tmp.name, "home")
        self.project = os.path.join(self.tmp.name, "proj")
        os.makedirs(self.home)
        os.makedirs(self.project)

    def write(self, rel, text):
        path = os.path.join(self.tmp.name, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
        return path

    def run_inv(self, *args, env_extra=None):
        env = dict(os.environ, HOME=self.home)
        env.pop("TDQ_LOG", None)
        if env_extra:
            env.update(env_extra)
        proc = subprocess.run(
            [sys.executable, SCRIPT, "--project", self.project, *args],
            capture_output=True, text=True, env=env, timeout=30)
        return proc.returncode, proc.stdout, proc.stderr

    def settings(self, layer, enabled):
        rel = {
            "user": "home/.claude/settings.json",
            "project": "proj/.claude/settings.json",
            "local": "proj/.claude/settings.local.json",
        }[layer]
        self.write(rel, json.dumps({"enabledPlugins": enabled}))

    def installed(self, plugins):
        self.write("home/.claude/plugins/installed_plugins.json",
                   json.dumps({"version": 2, "plugins": plugins}))

    def plugin_cache(self, name, version, skills):
        root = os.path.join(self.home, ".claude", "plugins", "cache", "mk", name, version)
        for skill in skills:
            path = os.path.join(root, "skills", skill, "SKILL.md")
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                f.write(skill_md(skill))
        return root


class CliTest(InventoryBase):
    def test_cli_exit_codes(self):
        """HOME rỗng → bảng rỗng nhưng exit 0; cờ lạ → exit 2 (sai cú pháp)."""
        rc, out, _ = self.run_inv()
        self.assertEqual(rc, 0, out)
        rc, _, err = self.run_inv("--gi-do-la")
        self.assertEqual(rc, 2, err)

    def test_builtin_reminder_lines(self):
        """2 dòng nhắc built-in phải in NGUYÊN VĂN, kể cả khi bảng rỗng."""
        _, out, _ = self.run_inv()
        lines = out.strip().splitlines()
        self.assertIn(REMINDER_1, lines)
        self.assertIn(REMINDER_2, lines)


class ScanDirsTest(InventoryBase):
    def test_scans_user_and_project_dirs(self):
        self.write("home/.claude/skills/alpha/SKILL.md", skill_md("alpha"))
        self.write("home/.claude/skills/beta/SKILL.md", skill_md("beta"))
        self.write("proj/.claude/skills/gamma/SKILL.md", skill_md("gamma"))
        _, out, _ = self.run_inv()
        self.assertIn("alpha", out)
        self.assertIn("beta", out)
        self.assertIn("gamma", out)
        self.assertIn("| user", out)
        self.assertIn("| project", out)


class PluginTest(InventoryBase):
    def enable_and_install(self, key, entry):
        self.settings("user", {key: True})
        self.installed({key: [entry]})

    def test_settings_three_layers(self):
        """Tầng project đè tầng user: user bật + project tắt → không liệt kê."""
        root = self.plugin_cache("pl", "1.0.0", ["sk-a"])
        self.settings("user", {"pl@mk": True})
        self.settings("project", {"pl@mk": False})
        self.installed({"pl@mk": [{"scope": "user", "installPath": root}]})
        _, out, _ = self.run_inv()
        self.assertNotIn("sk-a", out)

    def test_local_layer_enables(self):
        """settings.local.json bật được plugin mà tầng user không nhắc tới."""
        root = self.plugin_cache("pl", "1.0.0", ["sk-a"])
        self.settings("local", {"pl@mk": True})
        self.installed({"pl@mk": [{"scope": "user", "installPath": root}]})
        _, out, _ = self.run_inv()
        self.assertIn("sk-a", out)

    def test_project_scope_filtered(self):
        """Entry scope=project của PROJECT KHÁC không được lọt vào bảng."""
        root = self.plugin_cache("pl", "1.0.0", ["sk-a"])
        self.enable_and_install("pl@mk", {
            "scope": "project",
            "projectPath": os.path.join(self.tmp.name, "khac"),
            "installPath": root,
        })
        _, out, _ = self.run_inv()
        self.assertNotIn("sk-a", out)

    def test_project_scope_matching_included(self):
        root = self.plugin_cache("pl", "1.0.0", ["sk-a"])
        self.enable_and_install("pl@mk", {
            "scope": "project", "projectPath": self.project, "installPath": root,
        })
        _, out, _ = self.run_inv()
        self.assertIn("sk-a", out)

    def test_reads_installpath_only(self):
        """Cache giữ nhiều version — chỉ version trong installed_plugins được đọc."""
        self.plugin_cache("pl", "0.9.0", ["sk-cu"])
        root_new = self.plugin_cache("pl", "1.0.0", ["sk-moi"])
        self.enable_and_install("pl@mk", {"scope": "user", "installPath": root_new})
        _, out, _ = self.run_inv()
        self.assertIn("sk-moi", out)
        self.assertNotIn("sk-cu", out)
        self.assertEqual(out.count("sk-moi"), 1, "không được liệt kê trùng")


class LogServiceTest(InventoryBase):
    def test_warn_on_broken_json(self):
        """settings.json hỏng → ⚠️ kèm timestamp ra stderr, exit vẫn 0."""
        self.write("home/.claude/settings.json", "{hong json")
        rc, _, err = self.run_inv()
        self.assertEqual(rc, 0)
        self.assertIn("⚠️", err)
        self.assertIn("settings.json", err)

    def test_tdq_log_0_silences(self):
        self.write("home/.claude/settings.json", "{hong json")
        rc, _, err = self.run_inv(env_extra={"TDQ_LOG": "0"})
        self.assertEqual(rc, 0)
        self.assertEqual(err.strip(), "")

class SanitizeTest(InventoryBase):
    def test_control_chars_stripped(self):
        """QC1.1 (Q9) — SKILL.md xấu không được điều khiển terminal của user."""
        self.write("home/.claude/skills/xau/SKILL.md",
                   "---\nname: xau\ndescription: \x1b[2Jxoá\x07màn hình\n---\n")
        rc, out, _ = self.run_inv()
        self.assertEqual(rc, 0)
        self.assertIn("xau", out)
        self.assertNotIn("\x1b", out)
        self.assertNotIn("\x07", out)


if __name__ == "__main__":
    unittest.main()
