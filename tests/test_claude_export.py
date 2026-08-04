"""Test cho scripts/claude_export.py — bộ export cấu hình Claude Code sang máy khác.

Luật của bộ test này: KHÔNG được đọc/ghi `~/.claude`, `~/.claude.json` hay
`~/Documents` thật. Mọi ca dựng một "máy nguồn giả" trong thư mục tạm rồi tiêm
đường dẫn vào script qua tham số `--claude-home` / `--repo`.
"""
import contextlib
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile

from helper import ROOT

import claude_export  # noqa: E402

SCRIPT = os.path.join(ROOT, "scripts", "claude_export.py")
FAKE_KEY = "tvly-dev-FAKEKEY0123456789abcdefghij"


def _git(cwd, *args):
    return subprocess.run(
        ["git", "-c", "user.email=t@example.com", "-c", "user.name=tester", *args],
        cwd=cwd, capture_output=True, text=True, check=True,
    ).stdout.strip()


def make_repo(base):
    """Repo giả có `.git` thật, 1 file tracked, 1 file untracked bị gitignore."""
    repo = os.path.join(base, "srcrepo")
    os.makedirs(os.path.join(repo, ".claude-plugin"))
    with open(os.path.join(repo, ".claude-plugin", "plugin.json"), "w") as f:
        json.dump({"name": "tdq-workflow", "version": "9.9.9"}, f)
    with open(os.path.join(repo, "README.md"), "w") as f:
        f.write("repo giả\n")
    with open(os.path.join(repo, ".gitignore"), "w") as f:
        f.write("junk/\n.DS_Store\n")
    os.makedirs(os.path.join(repo, "junk"))
    with open(os.path.join(repo, "junk", "big.bin"), "w") as f:
        f.write("x" * 1000)
    os.makedirs(os.path.join(repo, ".remember", "tmp"))
    os.makedirs(os.path.join(repo, ".remember", "logs"))
    # giống repo thật: `.remember/.gitignore` = `*` nên cả thư mục là untracked
    with open(os.path.join(repo, ".remember", ".gitignore"), "w") as f:
        f.write("*\n")
    with open(os.path.join(repo, ".remember", "core-memories.md"), "w") as f:
        f.write("nhớ cái này\n")
    with open(os.path.join(repo, ".remember", "tmp", "session.pid"), "w") as f:
        f.write("12345\n")
    with open(os.path.join(repo, ".remember", "logs", "run.log"), "w") as f:
        f.write("log rác\n")
    with open(os.path.join(repo, ".DS_Store"), "w") as f:
        f.write("rác macOS\n")
    _git(repo, "init", "-q")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "khoi tao repo gia")
    return repo


def make_claude_home(base, key=FAKE_KEY):
    """`~/.claude` giả: settings.json có key thật trong `env`, cùng vài file phụ."""
    home = os.path.join(base, "claudehome")
    os.makedirs(os.path.join(home, "plugins"))
    os.makedirs(os.path.join(home, "skills", "graphify"))
    os.makedirs(os.path.join(home, "scripts"))
    settings = {
        "env": {"TAVILY_API_KEY_PRIMARY": key, "TAVILY_API_KEY_BACKUP": key + "-b"},
        "extraKnownMarketplaces": {
            "tdq-local": {"source": {"source": "directory", "path": "/duong/dan/cu"}},
        },
    }
    with open(os.path.join(home, "settings.json"), "w") as f:
        json.dump(settings, f)
    with open(os.path.join(home, "CLAUDE.md"), "w") as f:
        f.write("# quy tac\n")
    with open(os.path.join(home, "statusline.sh"), "w") as f:
        f.write("#!/bin/sh\necho hi\n")
    with open(os.path.join(home, "plugin-tiers.json"), "w") as f:
        json.dump({"tiers": {}}, f)
    with open(os.path.join(home, "skills", "graphify", "SKILL.md"), "w") as f:
        f.write("# graphify\n")
    with open(os.path.join(home, "scripts", "helper.sh"), "w") as f:
        f.write("echo helper\n")
    with open(os.path.join(home, "plugins", "installed_plugins.json"), "w") as f:
        json.dump({"plugins": {"demo@mkt": [{"scope": "user"}],
                               "local@mkt": [{"scope": "local"}]}}, f)
    with open(os.path.join(home, "plugins", "known_marketplaces.json"), "w") as f:
        json.dump({"tdq-local": {"source": {"source": "directory",
                                            "path": "/duong/dan/cu"}}}, f)
    # `~/.claude.json` nằm CẠNH `~/.claude` — script suy ra từ thư mục cha.
    with open(os.path.join(base, ".claude.json"), "w") as f:
        json.dump({"oauthAccount": {"emailAddress": "x@y.z"}, "machineID": "abc",
                   "mcpServers": {
                       "tavily-primary": {"type": "http", "url": "https://a.example",
                                          "headers": {"Authorization":
                                                      "Bearer ${TAVILY_API_KEY_PRIMARY}"}},
                       "tavily-backup": {"type": "http", "url": "https://b.example"}}}, f)
    return home


def run_cli(*args, versions=False):
    """Mặc định tắt bước dò version CLI: 8 lệnh `--version` mỗi lần build là quá chậm."""
    env = dict(os.environ, TDQ_EXPORT_CLI_VERSIONS="1" if versions else "0")
    proc = subprocess.run([sys.executable, SCRIPT, *args],
                          capture_output=True, text=True, timeout=300, env=env)
    return proc.returncode, proc.stdout, proc.stderr


class Fixture(unittest.TestCase):
    """Dựng máy nguồn giả + đích trong thư mục tạm cho mỗi ca."""

    def setUp(self):
        self.base = tempfile.mkdtemp(prefix="tdq-export-test-")
        self.addCleanup(shutil.rmtree, self.base, ignore_errors=True)
        self.repo = make_repo(self.base)
        self.home = make_claude_home(self.base)
        self.dest = os.path.join(self.base, "bundle")

    def build(self, *extra, **kwargs):
        return run_cli("build", "--dest", self.dest, "--claude-home", self.home,
                       "--repo", self.repo, *extra, **kwargs)

    def read_manifest(self):
        with open(os.path.join(self.dest, "manifest.json"), encoding="utf-8") as f:
            return json.load(f)


# ---------------------------------------------------------------- P2: khung + hàm nền

class ParseArgsTest(unittest.TestCase):
    def test_two_subcommands(self):
        self.assertEqual(claude_export.parse_args(["build", "--dest", "/x"]).cmd, "build")
        self.assertEqual(claude_export.parse_args(["check", "--dest", "/x"]).cmd, "check")

    def test_unknown_subcommand_exits(self):
        with self.assertRaises(SystemExit):
            claude_export.parse_args(["khong-co-lenh-nay"])


class LogTest(unittest.TestCase):
    def tearDown(self):
        claude_export.set_log_level()

    def _capture(self, **level):
        claude_export.set_log_level(**level)
        buf = io.StringIO()
        with contextlib.redirect_stderr(buf):
            claude_export.log("việc bình thường")
            claude_export.log("chi tiết", level="debug")
        return buf.getvalue()

    def test_log_default_on(self):
        out = self._capture()
        self.assertIn("việc bình thường", out)
        self.assertRegex(out, r"\[\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}")

    def test_quiet_silences_log(self):
        self.assertEqual(self._capture(quiet=True), "")

    def test_verbose_adds_debug(self):
        self.assertNotIn("chi tiết", self._capture())
        self.assertIn("chi tiết", self._capture(verbose=True))


class ReadMcpServersTest(Fixture):
    def test_reads_two_servers(self):
        got = claude_export.read_mcp_servers(os.path.join(self.base, ".claude.json"))
        self.assertEqual(sorted(got), ["tavily-backup", "tavily-primary"])

    def test_missing_key_gives_empty_dict(self):
        path = os.path.join(self.base, "trong.json")
        with open(path, "w") as f:
            json.dump({"machineID": "abc"}, f)
        self.assertEqual(claude_export.read_mcp_servers(path), {})

    def test_missing_file_gives_empty_dict(self):
        self.assertEqual(claude_export.read_mcp_servers(self.base + "/khong-co.json"), {})


class ScanSecretsTest(Fixture):
    def setUp(self):
        super().setUp()
        self.tree = os.path.join(self.base, "cay-quet")
        os.makedirs(self.tree)

    def test_finds_the_only_leaking_file(self):
        with open(os.path.join(self.tree, "leak.txt"), "w") as f:
            f.write("Authorization: Bearer " + FAKE_KEY + "\n")
        with open(os.path.join(self.tree, "sach.txt"), "w") as f:
            f.write("khong co gi\n")
        hits = claude_export.scan_secrets(self.tree, [FAKE_KEY])
        self.assertEqual([os.path.basename(h) for h in hits], ["leak.txt"])

    def test_clean_tree_gives_empty_list(self):
        self.assertEqual(claude_export.scan_secrets(self.repo, [FAKE_KEY]), [])

    def test_ignores_empty_and_short_values(self):
        with open(os.path.join(self.tree, "a.txt"), "w") as f:
            f.write("abc\n")
        self.assertEqual(claude_export.scan_secrets(self.tree, ["", "abc", None]), [])


class CollectConfigTest(Fixture):
    def test_sha256_changes_with_one_byte(self):
        path = os.path.join(self.base, "f.txt")
        with open(path, "w") as f:
            f.write("a")
        first = claude_export.sha256_of(path)
        with open(path, "w") as f:
            f.write("b")
        self.assertNotEqual(first, claude_export.sha256_of(path))
        self.assertEqual(len(first), 64)

    def test_collects_files_and_dirs_of_claude_home(self):
        got = claude_export.collect_config_files(self.home)
        self.assertIn("config/settings.json", got)
        self.assertIn("config/CLAUDE.md", got)
        self.assertIn("config/installed_plugins.json", got)
        self.assertIn("config/skills-graphify/SKILL.md", got)
        self.assertNotIn("config/.claude.json", got)

    def test_skips_missing_entries(self):
        os.remove(os.path.join(self.home, "plugin-tiers.json"))
        self.assertNotIn("config/plugin-tiers.json",
                         claude_export.collect_config_files(self.home))

    def test_harvest_secrets_only_takes_real_values(self):
        path = os.path.join(self.base, "s.json")
        with open(path, "w") as f:
            json.dump({"env": {"TAVILY_API_KEY_PRIMARY": FAKE_KEY,
                               "OTHER_TOKEN": "${FROM_ENV}",
                               "EDITOR": "vim"}}, f)
        got = claude_export.harvest_secrets(path)
        self.assertEqual(got, {"TAVILY_API_KEY_PRIMARY": FAKE_KEY})


# ---------------------------------------------------------------- P3: lệnh build

class BuildGuardTest(Fixture):
    def test_empty_dest_is_allowed(self):
        os.makedirs(self.dest)
        self.assertEqual(self.build()[0], 0)

    def test_own_bundle_is_overwritten(self):
        self.assertEqual(self.build()[0], 0)
        with open(os.path.join(self.dest, "dau-vet.txt"), "w") as f:
            f.write("ban cu\n")
        self.assertEqual(self.build()[0], 0)
        self.assertFalse(os.path.exists(os.path.join(self.dest, "dau-vet.txt")))

    def test_foreign_dir_refused_with_exit_2(self):
        os.makedirs(self.dest)
        with open(os.path.join(self.dest, "luan-van.docx"), "w") as f:
            f.write("du lieu cua user\n")
        code, _, err = self.build()
        self.assertEqual(code, 2)
        self.assertIn("luan-van.docx", err + _)
        self.assertTrue(os.path.exists(os.path.join(self.dest, "luan-van.docx")))


class BuildRepoTest(Fixture):
    def test_clone_keeps_git_and_drops_untracked(self):
        self.assertEqual(self.build()[0], 0)
        repo = os.path.join(self.dest, "tdqworkflow-repo")
        self.assertTrue(os.path.isdir(os.path.join(repo, ".git")))
        self.assertTrue(os.path.isfile(os.path.join(repo, "README.md")))
        self.assertFalse(os.path.exists(os.path.join(repo, "junk")))
        self.assertFalse(os.path.exists(os.path.join(repo, ".DS_Store")))

    def test_remember_copied_but_runtime_filtered(self):
        self.assertEqual(self.build()[0], 0)
        mem = os.path.join(self.dest, "tdqworkflow-repo", ".remember")
        self.assertTrue(os.path.isfile(os.path.join(mem, "core-memories.md")))
        self.assertFalse(os.path.exists(os.path.join(mem, "tmp")))
        self.assertFalse(os.path.exists(os.path.join(mem, "logs")))

    def test_clone_head_matches_source(self):
        self.assertEqual(self.build()[0], 0)
        src = _git(self.repo, "rev-parse", "HEAD")
        got = _git(os.path.join(self.dest, "tdqworkflow-repo"), "rev-parse", "HEAD")
        self.assertEqual(src, got)


class BuildConfigTest(Fixture):
    def test_config_and_mcp_written(self):
        self.assertEqual(self.build()[0], 0)
        self.assertTrue(os.path.isfile(os.path.join(self.dest, "config", "settings.json")))
        with open(os.path.join(self.dest, "config", "mcp-servers.json"), encoding="utf-8") as f:
            mcp = json.load(f)
        self.assertEqual(sorted(mcp), ["tavily-backup", "tavily-primary"])
        self.assertEqual(mcp["tavily-primary"]["headers"]["Authorization"],
                         "Bearer ${TAVILY_API_KEY_PRIMARY}")

    def test_marketplace_path_rewritten_to_dest(self):
        self.assertEqual(self.build()[0], 0)
        new_path = os.path.join(self.dest, "tdqworkflow-repo")
        with open(os.path.join(self.dest, "config", "settings.json"), encoding="utf-8") as f:
            settings = json.load(f)
        self.assertEqual(
            settings["extraKnownMarketplaces"]["tdq-local"]["source"]["path"], new_path)
        with open(os.path.join(self.dest, "config", "known_marketplaces.json"),
                  encoding="utf-8") as f:
            known = json.load(f)
        self.assertEqual(known["tdq-local"]["source"]["path"], new_path)
        self.assertEqual(known["tdq-local"]["installLocation"], new_path)

    def test_api_key_replaced_by_placeholder(self):
        self.assertEqual(self.build()[0], 0)
        with open(os.path.join(self.dest, "config", "settings.json"), encoding="utf-8") as f:
            settings = json.load(f)
        self.assertNotIn(FAKE_KEY, json.dumps(settings))
        self.assertIn("TAVILY_API_KEY_PRIMARY", settings["env"]["TAVILY_API_KEY_PRIMARY"])

    def test_readme_written_from_template(self):
        self.assertEqual(self.build()[0], 0)
        with open(os.path.join(self.dest, "README.md"), encoding="utf-8") as f:
            text = f.read()
        self.assertNotIn("{{", text)
        self.assertIn("demo", text)


class BuildManifestTest(Fixture):
    def test_exactly_eight_keys(self):
        self.assertEqual(self.build()[0], 0)
        self.assertEqual(sorted(self.read_manifest()), [
            "cli_dependencies", "exported_at", "marketplaces", "mcp_servers",
            "plugin_version", "plugins", "repo_commit", "source_files",
        ])

    def test_version_and_commit_match_source(self):
        self.assertEqual(self.build()[0], 0)
        manifest = self.read_manifest()
        self.assertEqual(manifest["plugin_version"], "9.9.9")
        self.assertEqual(manifest["repo_commit"], _git(self.repo, "rev-parse", "HEAD"))

    def test_source_files_carry_path_and_sha(self):
        self.assertEqual(self.build()[0], 0)
        entry = self.read_manifest()["source_files"]["config/settings.json"]
        self.assertEqual(entry["source"], os.path.join(self.home, "settings.json"))
        self.assertEqual(entry["sha256"],
                         claude_export.sha256_of(os.path.join(self.home, "settings.json")))

    def test_plugins_only_user_scope(self):
        self.assertEqual(self.build()[0], 0)
        self.assertEqual(sorted(self.read_manifest()["plugins"]), ["demo@mkt"])


class BuildSecretScanTest(Fixture):
    def test_leak_deletes_bundle_and_exits_3(self):
        # `echo helper` là nội dung thật của config/scripts/helper.sh trong bundle:
        # khai nó là chuỗi bí mật thì bước quét cuối phải bắt được và huỷ bundle.
        code, out, err = self.build("--extra-secret", "echo helper")
        self.assertEqual(code, 3)
        self.assertFalse(os.path.exists(self.dest))
        self.assertIn("secret", (out + err).lower())

    def test_clean_build_leaves_no_key_anywhere(self):
        self.assertEqual(self.build()[0], 0)
        self.assertEqual(claude_export.scan_secrets(self.dest, [FAKE_KEY]), [])
        self.assertEqual(claude_export.scan_secrets(self.dest, [FAKE_KEY + "-b"]), [])


class BuildZipTest(Fixture):
    def test_zip_is_valid_and_atomic(self):
        target = self.dest + ".zip"
        with open(target, "w") as f:
            f.write("ban zip cu\n")
        self.assertEqual(self.build("--zip")[0], 0)
        with zipfile.ZipFile(target) as zf:
            self.assertIsNone(zf.testzip())
            self.assertTrue(any(n.endswith("manifest.json") for n in zf.namelist()))
        self.assertFalse(os.path.exists(target + ".tmp"))

    def test_no_zip_flag_leaves_zip_untouched(self):
        target = self.dest + ".zip"
        with open(target, "w") as f:
            f.write("ban zip cu\n")
        self.assertEqual(self.build()[0], 0)
        with open(target, encoding="utf-8") as f:
            self.assertEqual(f.read(), "ban zip cu\n")


class BuildLogTest(Fixture):
    def test_default_logs_to_stderr(self):
        code, _, err = self.build()
        self.assertEqual(code, 0)
        self.assertRegex(err, r"\[\d{4}-\d{2}-\d{2}T")

    def test_quiet_flag_silences_build(self):
        code, _, err = self.build("--quiet")
        self.assertEqual(code, 0)
        self.assertEqual(err.strip(), "")


# ---------------------------------------------------------------- P4: lệnh check

class CheckTest(Fixture):
    def check(self, *extra):
        return run_cli("check", "--dest", self.dest, "--claude-home", self.home,
                       "--repo", self.repo, *extra)

    def test_clean_right_after_build(self):
        self.assertEqual(self.build()[0], 0)
        code, out, _ = self.check()
        self.assertEqual(code, 0)
        self.assertIn("0 mục lệch", out)

    def test_config_drift_named_and_exit_1(self):
        self.assertEqual(self.build()[0], 0)
        with open(os.path.join(self.home, "CLAUDE.md"), "a") as f:
            f.write("them mot dong\n")
        code, out, _ = self.check()
        self.assertEqual(code, 1)
        self.assertIn("config/CLAUDE.md", out)
        self.assertIn("1 mục lệch", out)

    def test_missing_source_file_counts_as_drift(self):
        self.assertEqual(self.build()[0], 0)
        os.remove(os.path.join(self.home, "statusline.sh"))
        code, out, _ = self.check()
        self.assertEqual(code, 1)
        self.assertIn("config/statusline.sh", out)

    def test_repo_commit_drift_shows_both_sha(self):
        self.assertEqual(self.build()[0], 0)
        old = _git(self.repo, "rev-parse", "HEAD")
        with open(os.path.join(self.repo, "README.md"), "a") as f:
            f.write("doi noi dung\n")
        _git(self.repo, "add", "-A")
        _git(self.repo, "commit", "-q", "-m", "doi repo")
        new = _git(self.repo, "rev-parse", "HEAD")
        code, out, _ = self.check()
        self.assertEqual(code, 1)
        self.assertIn(old[:8], out)
        self.assertIn(new[:8], out)

    def test_plugin_version_drift_reported(self):
        self.assertEqual(self.build()[0], 0)
        path = os.path.join(self.repo, ".claude-plugin", "plugin.json")
        with open(path, "w") as f:
            json.dump({"name": "tdq-workflow", "version": "9.9.10"}, f)
        code, out, _ = self.check()
        self.assertEqual(code, 1)
        self.assertIn("9.9.10", out)

    def test_missing_manifest_exits_2(self):
        os.makedirs(self.dest)
        self.assertEqual(self.check()[0], 2)

    def test_broken_manifest_exits_2_without_traceback(self):
        """Manifest hỏng là bundle không hợp lệ (2), không phải drift (1)."""
        self.assertEqual(self.build()[0], 0)
        with open(os.path.join(self.dest, "manifest.json"), "w") as f:
            f.write("{khong phai json")
        code, _, err = self.check()
        self.assertEqual(code, 2)
        self.assertNotIn("Traceback", err)
        self.assertIn("đọc không được", err)

    def test_unknown_old_commit_says_so_instead_of_question_mark(self):
        """SHA cũ không có trong repo thì nói thẳng, không in `(+?)`."""
        self.assertEqual(self.build()[0], 0)
        path = os.path.join(self.dest, "manifest.json")
        with open(path, encoding="utf-8") as f:
            manifest = json.load(f)
        manifest["repo_commit"] = "deadbeef" * 5
        with open(path, "w", encoding="utf-8") as f:
            json.dump(manifest, f)
        code, out, _ = self.check()
        self.assertEqual(code, 1)
        self.assertNotIn("+?", out)
        self.assertIn("không so được", out)


# ---------------------------------------------------------------- P5: tài liệu bundle

class TemplateTest(unittest.TestCase):
    """Template trong `claude-export/` là thứ script nạp thật, không phải văn bản trang trí."""

    def test_manifest_template_has_the_eight_keys(self):
        with open(os.path.join(ROOT, "claude-export", "MANIFEST.template.json"),
                  encoding="utf-8") as f:
            keys = sorted(json.load(f))
        self.assertEqual(keys, [
            "cli_dependencies", "exported_at", "marketplaces", "mcp_servers",
            "plugin_version", "plugins", "repo_commit", "source_files",
        ])

    def test_readme_template_restores_mcp_and_verifies(self):
        with open(os.path.join(ROOT, "claude-export", "README.template.md"),
                  encoding="utf-8") as f:
            text = f.read()
        self.assertIn("claude mcp add-json", text)
        self.assertIn("--scope user", text)
        self.assertIn("claude doctor", text)
        self.assertIn("config/mcp-servers.json", text)

    def test_instructions_document_the_two_commands(self):
        with open(os.path.join(ROOT, "claude-export", "INSTRUCTIONS.md"),
                  encoding="utf-8") as f:
            text = f.read()
        self.assertIn("claude_export.py build", text)
        self.assertIn("claude_export.py check", text)


if __name__ == "__main__":
    unittest.main()
