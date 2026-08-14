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


class ProjectDirResolveTest(InventoryBase):
    """A23 — không có --project thì neo theo TDQ_PROJECT_DIR, không lấy cwd mù."""

    def test_env_project_dir_used_when_no_flag(self):
        self.write("proj/.claude/skills/demo-skill/SKILL.md",
                   skill_md("demo-skill"))
        elsewhere = os.path.join(self.tmp.name, "elsewhere")
        os.makedirs(elsewhere)
        env = dict(os.environ, HOME=self.home, TDQ_PROJECT_DIR=self.project)
        proc = subprocess.run(
            [sys.executable, SCRIPT], capture_output=True, text=True,
            env=env, timeout=30, cwd=elsewhere)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("demo-skill", proc.stdout)


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


class DescriptionTest(InventoryBase):
    """Mô tả phải mang đủ tín hiệu định tuyến và không phá số cột của bảng."""

    def row(self, out, name):
        for line in out.splitlines():
            if line.startswith(f"{name} |"):
                return line
        self.fail(f"không thấy dòng của skill {name} trong:\n{out}")

    def test_block_scalar_description_read(self):
        """`description: |` nhiều dòng → nối thành một dòng, không còn ô rỗng."""
        self.write("home/.claude/skills/blocky/SKILL.md",
                   "---\nname: blocky\ndescription: |\n  Dòng một của mô tả.\n"
                   "  Dòng hai nói thêm.\nallowed-tools:\n  - Bash(ls)\n---\n\n# blocky\n")
        _, out, _ = self.run_inv()
        row = self.row(out, "blocky")
        self.assertIn("Dòng một của mô tả.", row)
        self.assertIn("Dòng hai nói thêm.", row)
        self.assertNotIn("Bash(ls)", row)

    def test_pipe_in_description_keeps_three_columns(self):
        """Ký tự `|` trong mô tả đổi thành `/` — bảng vẫn đúng 3 cột."""
        self.write("home/.claude/skills/piped/SKILL.md",
                   skill_md("piped", "chạy a | b rồi c"))
        _, out, _ = self.run_inv()
        row = self.row(out, "piped")
        self.assertEqual(len(row.split("|")), 3, row)
        self.assertIn("chạy a / b rồi c", row)

    def test_trigger_beyond_cutoff_kept(self):
        """Cụm trigger nằm sau ký tự thứ 60 vẫn phải xuất hiện trong ô mô tả."""
        desc = "A" * 200 + " Use when the caller needs the widget rebuilt."
        self.write("home/.claude/skills/faraway/SKILL.md", skill_md("faraway", desc))
        _, out, _ = self.run_inv()
        row = self.row(out, "faraway")
        self.assertIn("Use when", row)
        self.assertIn(" … ", row)

    def test_trigger_straddling_cutoff_kept(self):
        """Trigger bắt đầu ngay TRƯỚC ngưỡng 60 (ca `huggingface-trackio`) vẫn phải đủ."""
        desc = "C" * 58 + "Use when người gọi cần dựng lại widget cho màn hình chính."
        self.write("home/.claude/skills/straddle/SKILL.md", skill_md("straddle", desc))
        _, out, _ = self.run_inv()
        row = self.row(out, "straddle")
        self.assertIn("Use when người gọi cần", row)
        self.assertEqual(row.lower().count("use when"), 1, f"lặp cụm trigger: {row}")

    def test_vietnamese_trigger_beyond_cutoff_kept(self):
        """Mô tả tiếng Việt: cụm `Dùng khi` sau ký tự 60 cũng phải giữ như cụm tiếng Anh."""
        desc = ("Đọc cấu hình rồi dựng lại toàn bộ bảng điều khiển cho người vận hành. "
                "Dùng khi người gọi cần làm mới bảng sau khi đổi cấu hình.")
        self.write("home/.claude/skills/vi-skill/SKILL.md", skill_md("vi-skill", desc))
        _, out, _ = self.run_inv()
        row = self.row(out, "vi-skill")
        self.assertIn("Dùng khi người gọi cần", row)
        self.assertIn(" … ", row)

    def test_short_description_untouched(self):
        """Mô tả ngắn hơn ngưỡng → giữ nguyên, không chèn dấu nối."""
        self.write("home/.claude/skills/tiny/SKILL.md", skill_md("tiny", "mô tả rất ngắn"))
        _, out, _ = self.run_inv()
        row = self.row(out, "tiny")
        self.assertIn("| mô tả rất ngắn |", row)
        self.assertNotIn(" … ", row)

    def test_long_description_without_trigger_cut(self):
        """Không có cụm trigger → vẫn cắt ở ngưỡng cũ, không phình bảng."""
        self.write("home/.claude/skills/plain/SKILL.md", skill_md("plain", "B" * 300))
        _, out, _ = self.run_inv()
        row = self.row(out, "plain")
        self.assertEqual(row.split("|")[1].strip(), "B" * 60)


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


class FilterFlagTest(InventoryBase):
    """Đ1 (0.16.0) — cờ `--loc` cắt output kiểm kê mà không giấu nguồn quan trọng.

    Luật: bảng đầy đủ ≈ 39.7KB mỗi lần chạy B0. `--loc <từ khoá>` giữ dòng khớp từ khoá
    CỘNG mọi dòng nguồn `project` và `plugin:tdq-workflow` (hai nguồn không được phép ẩn),
    và BẮT BUỘC in một dòng cuối nói đã ẩn bao nhiêu skill + đúng lệnh xem đủ.
    """

    def scene(self):
        """6 skill: 1 khớp từ khoá, 3 không khớp, 1 nguồn project, 1 plugin tdq-workflow.

        Ba dòng không khớp (chứ không phải một) để phép so "ít dòng hơn" còn đúng sau khi
        bản lọc cộng thêm dòng nhắc cuối — đúng tỉ lệ thật: ẩn nhiều, nhắc một dòng.
        """
        self.write("home/.claude/skills/alpha-workflow/SKILL.md",
                   skill_md("alpha-workflow", "chạy workflow nội bộ"))
        for i in ("", "-2", "-3"):
            self.write(f"home/.claude/skills/zeta-khac{i}/SKILL.md",
                       skill_md(f"zeta-khac{i}", "việc hoàn toàn khác"))
        self.write("proj/.claude/skills/gamma-du-an/SKILL.md",
                   skill_md("gamma-du-an", "việc hoàn toàn khác"))
        root = self.plugin_cache("tdq-workflow", "0.16.0", ["tdq-build"])
        self.settings("user", {"tdq-workflow@mk": True})
        self.installed({"tdq-workflow@mk": [{"installPath": root, "scope": "user"}]})

    def test_loc_prints_fewer_lines_than_default(self):
        self.scene()
        _, full, _ = self.run_inv()
        rc, small, _ = self.run_inv("--loc", "workflow")
        self.assertEqual(rc, 0, small)
        self.assertLess(len(small.splitlines()), len(full.splitlines()), small)

    def test_loc_keeps_project_and_tdq_workflow_sources(self):
        self.scene()
        _, out, _ = self.run_inv("--loc", "workflow")
        self.assertIn("alpha-workflow", out)      # khớp từ khoá
        self.assertIn("gamma-du-an", out)         # nguồn project — cấm ẩn
        self.assertIn("tdq-build", out)           # plugin:tdq-workflow — cấm ẩn
        self.assertNotIn("zeta-khac", out)        # không khớp, nguồn user → ẩn

    def test_loc_last_line_reports_hidden_count_and_full_command(self):
        self.scene()
        _, out, _ = self.run_inv("--loc", "workflow")
        last = out.strip().splitlines()[-1]
        self.assertIn("3", last, last)            # đúng 3 skill bị ẩn
        self.assertIn("--tat-ca", last, last)


class FullOutputUnchangedTest(InventoryBase):
    """Đ1 — hành vi mặc định phải y hệt bản trước khi thêm cờ; `--tat-ca` = mặc định."""

    def scene(self):
        self.write("home/.claude/skills/alpha-workflow/SKILL.md",
                   skill_md("alpha-workflow", "chạy workflow nội bộ"))
        self.write("home/.claude/skills/zeta-khac/SKILL.md",
                   skill_md("zeta-khac", "việc hoàn toàn khác"))
        self.write("proj/.claude/skills/gamma-du-an/SKILL.md", skill_md("gamma-du-an"))

    def test_tat_ca_equals_default_byte_for_byte(self):
        self.scene()
        rc_a, default, _ = self.run_inv()
        rc_b, tat_ca, _ = self.run_inv("--tat-ca")
        self.assertEqual(rc_a, 0)
        self.assertEqual(rc_b, 0, tat_ca)
        self.assertEqual(default, tat_ca)

    def test_default_has_no_hidden_notice(self):
        self.scene()
        _, out, _ = self.run_inv()
        self.assertIn("zeta-khac", out)
        self.assertNotIn("--tat-ca", out)
        self.assertEqual(out.strip().splitlines()[-1], REMINDER_2)


if __name__ == "__main__":
    unittest.main()
