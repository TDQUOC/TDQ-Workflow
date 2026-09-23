"""Kiểm tính toàn vẹn repo — manifest và changelog phải khớp bản đang phát hành.

Phần cũ soát câu chữ trong .md đã bỏ (2026-08-08): đó là test văn phong, chặn đúng
việc rút gọn skill mà không bắt được lỗi hành vi nào.
"""
import json
import os
import re
import unittest

from helper import ROOT


class RepoIntegrityTest(unittest.TestCase):
    def test_marketplace_and_plugin_agree(self):
        with open(os.path.join(ROOT, ".claude-plugin", "plugin.json"), encoding="utf-8") as f:
            plugin = json.load(f)
        with open(os.path.join(ROOT, ".claude-plugin", "marketplace.json"), encoding="utf-8") as f:
            market = json.load(f)
        self.assertEqual(plugin["name"], market["plugins"][0]["name"])
        self.assertRegex(plugin["version"], r"^\d+\.\d+\.\d+$")

    def test_changelog_documents_current_version(self):
        with open(os.path.join(ROOT, ".claude-plugin", "plugin.json"), encoding="utf-8") as f:
            version = json.load(f)["version"]
        with open(os.path.join(ROOT, "CHANGELOG.md"), encoding="utf-8") as f:
            text = f.read()
        heads = re.findall(r"^## (\d+\.\d+\.\d+)", text, re.MULTILINE)
        self.assertIn(version, heads, "changelog chưa có mục cho bản đang phát hành")
        self.assertEqual(heads[0], version, "mục đầu changelog phải là bản đang phát hành")

    def test_hai_manifest_mo_ta_giong_nhau(self):
        """Codex và Claude Code phát cùng một plugin — mô tả lệch nhau là một bản đã cũ."""
        with open(os.path.join(ROOT, ".claude-plugin", "plugin.json"), encoding="utf-8") as f:
            claude = json.load(f)
        with open(os.path.join(ROOT, ".codex-plugin", "plugin.json"), encoding="utf-8") as f:
            codex = json.load(f)
        self.assertEqual(claude["description"], codex["description"])
        self.assertEqual(claude["version"], codex["version"])

    def test_no_ds_store(self):
        junk = []
        for dirpath, dirnames, files in os.walk(ROOT):
            dirnames[:] = [d for d in dirnames if d != ".git"]
            junk += [os.path.join(dirpath, n) for n in files if n == ".DS_Store"]
        self.assertEqual(junk, [])


# 2026-09-21 (T5.1): tài liệu HIỆN HÀNH không được còn mô tả ba bundle như cách cài. Hồ sơ
# request cũ (`docs/tdq/`), working log, CHANGELOG và archive là lịch sử — được nhắc tên cũ.
TAI_LIEU_HIEN_HANH = ("README.md", "docs/kien-truc.md", "docs/notes/user-level-install.md",
                      ".opencode/INSTALL.md", ".claude-plugin/plugin.json",
                      ".codex-plugin/plugin.json", ".claude-plugin/marketplace.json")
TEN_BUNDLE = re.compile(r"portable_claude|portable_codex|antigravity_portable|bản portable")


class TaiLieuCaiDatTest(unittest.TestCase):
    def test_khong_con_bundle_trong_tai_lieu_hien_hanh(self):
        for duong in TAI_LIEU_HIEN_HANH:
            with self.subTest(duong=duong):
                with open(os.path.join(ROOT, duong), encoding="utf-8") as f:
                    trung = TEN_BUNDLE.findall(f.read())
                self.assertEqual(trung, [], f"{duong} còn nhắc bundle đã gỡ ở 0.50.0")

    def test_readme_du_bon_host_moi_host_mot_lenh_that(self):
        with open(os.path.join(ROOT, "README.md"), encoding="utf-8") as f:
            readme = f.read()
        for host, lenh in (("Claude Code", "/plugin install tdq-workflow@tdq-local"),
                           ("Codex", "codex plugin add tdq-workflow@tdq-local"),
                           ("OpenCode", ".opencode/plugins/tdq-workflow.js"),
                           ("Antigravity", "build_portable.py --sinh-agy")):
            with self.subTest(host=host):
                self.assertIn(host, readme)
                self.assertIn(lenh, readme)

    def test_bang_cau_truc_dem_dung_so_skill_agent_hook(self):
        """2026-09-23: bảng ghi `skills/ (6)` khi trên đĩa có 9, `hooks/ (5)` khi `hooks.json`
        khai 6. Số đếm trong tài liệu phải đo lại được, nếu không nó chỉ đúng vào ngày viết."""
        with open(os.path.join(ROOT, "README.md"), encoding="utf-8") as f:
            readme = f.read()
        so_skill = len([t for t in os.listdir(os.path.join(ROOT, "skills"))
                        if os.path.isfile(os.path.join(ROOT, "skills", t, "SKILL.md"))])
        so_agent = len([t for t in os.listdir(os.path.join(ROOT, "agents"))
                        if t.endswith(".md")])
        with open(os.path.join(ROOT, "hooks", "hooks.json"), encoding="utf-8") as f:
            muc = json.load(f)["hooks"]
        so_hook = sum(len(nhom["hooks"]) for danh_sach in muc.values() for nhom in danh_sach)
        for ten, so in (("skills", so_skill), ("agents", so_agent), ("hooks", so_hook)):
            with self.subTest(thu_muc=ten):
                self.assertRegex(readme, rf"`{ten}/` \({so}\b",
                                 f"bảng Cấu trúc ghi sai số {ten}, thật là {so}")

    def test_kien_truc_bo_tang_ban_ngoai_them_adapter(self):
        with open(os.path.join(ROOT, "docs", "kien-truc.md"), encoding="utf-8") as f:
            kien_truc = f.read()
        self.assertNotIn("Luật bản ngoài", kien_truc)
        self.assertIn("| Adapter |", kien_truc)
        da_chot = kien_truc.split("## Đã chốt", 1)[1]
        self.assertIn("2026-09-21", da_chot)


if __name__ == "__main__":
    unittest.main()
