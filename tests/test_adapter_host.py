"""Adapter cho từng host — một nguồn, nhiều manifest mỏng.

Vì sao có file này: trước bản này repo chép toàn bộ `skills/`, `hooks/`, `agents/` và `scripts/`
vào ba thư mục bundle, tổng 357 file nhân bản trên 4.2 MB trong khi nguồn chỉ 672 KB. Bốn hệ quả
đã gặp thật: lumen index cả bản sao và bản sao chiếm hết top-10; bundle lệch nguồn sau mỗi lần
sửa; bundle nướng cứng thư mục nhà của máy dựng nên không commit được từ Windows; và
`portable_codex.zip` đứng yên suốt 24 bản vì không script nào dựng nó.

Khoá của mô hình mới nằm ở đúng một dòng lặp lại trong mọi manifest: adapter TRỎ vào nguồn chung
thay vì chép nó. Test ở đây khoá đúng tính chất đó — một manifest trỏ sai chỗ vẫn là JSON hợp lệ
và vẫn cài được, nó chỉ lặng lẽ nạp nhầm skill.
"""
import json
import os
import re
import subprocess
import unittest

from helper import ROOT, co_lenh

MARKETPLACE_CODEX = os.path.join(ROOT, ".agents", "plugins", "marketplace.json")
PLUGIN_CODEX = os.path.join(ROOT, ".codex-plugin", "plugin.json")
PLUGIN_CLAUDE = os.path.join(ROOT, ".claude-plugin", "plugin.json")
ADAPTER_OPENCODE = os.path.join(ROOT, ".opencode", "plugins", "tdq-workflow.js")

TEN_PLUGIN = "tdq-workflow"
# Ba thư mục bundle của mô hình cũ. Không được quay lại.
BUNDLE_CU = ("portable_claude", "portable_codex", "antigravity_portable")


def doc_van_ban(duong):
    with open(duong, encoding="utf-8") as f:
        return f.read()


def doc_json(duong):
    return json.loads(doc_van_ban(duong))


def ban_plugin():
    return doc_json(PLUGIN_CLAUDE)["version"]


class CodexAdapterTest(unittest.TestCase):
    """Codex CLI >= 0.155.1 nhận marketplace từ một đường dẫn local, `owner/repo` hoặc Git URL.

    Đã đo: thêm chính repo làm marketplace thì `codex plugin list` in ra plugin với nguồn trỏ
    vào thư mục repo. Nên adapter chỉ cần hai file manifest, không cần bundle 157 file.
    """

    def test_codex_co_du_hai_manifest(self):
        for duong in (MARKETPLACE_CODEX, PLUGIN_CODEX):
            with self.subTest(duong=os.path.basename(duong)):
                self.assertTrue(os.path.isfile(duong), f"thiếu {duong}")

    def test_codex_marketplace_tro_vao_chinh_repo(self):
        """`"url": "./"` là cả mô hình. Trỏ đi chỗ khác là quay lại việc chép."""
        muc = doc_json(MARKETPLACE_CODEX)["plugins"]
        ten = [p["name"] for p in muc]
        self.assertIn(TEN_PLUGIN, ten)
        plugin = next(p for p in muc if p["name"] == TEN_PLUGIN)
        self.assertEqual(plugin["source"]["url"], "./")

    def test_codex_plugin_tro_vao_skills_dung_chung(self):
        du_lieu = doc_json(PLUGIN_CODEX)
        self.assertEqual(du_lieu["name"], TEN_PLUGIN)
        self.assertEqual(du_lieu["skills"], "./skills/")

    def test_codex_ban_khop_plugin_claude(self):
        """Hai manifest lệch bản là hai plugin khác nhau dưới mắt hai host."""
        self.assertEqual(doc_json(PLUGIN_CODEX)["version"], ban_plugin())

    def test_codex_khong_tro_vao_bundle_nao(self):
        van_ban = doc_van_ban(MARKETPLACE_CODEX) + doc_van_ban(PLUGIN_CODEX)
        for ten in BUNDLE_CU:
            with self.subTest(bundle=ten):
                self.assertNotIn(ten, van_ban)

    def test_codex_policy_dung_gia_tri_cli_nhan(self):
        """Tập giá trị ĐÓNG, đọc từ thông báo lỗi của chính CLI.

        Bản đầu viết `"authentication": "NONE"` — JSON hợp lệ, test cũ xanh, nhưng
        `codex plugin marketplace add` bác thẳng: `unknown variant NONE, expected ON_INSTALL or
        ON_USE`. Một manifest sai schema vẫn nằm yên trên đĩa như manifest đúng, nên tập giá trị
        phải bị khoá ở đây chứ không đợi tới lúc người dùng cài.
        """
        plugin = next(p for p in doc_json(MARKETPLACE_CODEX)["plugins"]
                      if p["name"] == TEN_PLUGIN)
        self.assertIn(plugin["policy"]["authentication"], ("ON_INSTALL", "ON_USE"))
        self.assertIn(plugin["policy"]["installation"], ("AVAILABLE", "BLOCKED"))


# `import()` của ESM chỉ nhận specifier hoặc URL. Một đường dẫn Windows tuyệt đối (`C:\...`)
# bị hiểu là specifier và ném ERR_UNSUPPORTED_ESM_URL_SCHEME, nên mọi ca dưới đây phải đổi nó
# sang `file://` trước. Trên macOS và Linux đường dẫn tuyệt đối tình cờ chạy được, nên đây đúng
# là loại bẫy chỉ lộ ra trên Windows.
NAP_URL = "const { pathToFileURL } = require('node:url'); "


class OpenCodeAdapterTest(unittest.TestCase):
    """OpenCode có API lập trình nên adapter phải là JavaScript — không có đường khai báo."""

    def setUp(self):
        if not os.path.isfile(ADAPTER_OPENCODE):
            self.skipTest("adapter OpenCode chưa được viết")

    @unittest.skipUnless(co_lenh("node"), "chưa cài node")
    def test_opencode_node_nap_duoc(self):
        """Nạp thật bằng node. Một file JS sai cú pháp vẫn nằm yên trên đĩa như file đúng."""
        ma = ("import(pathToFileURL(process.argv[1]).href).then(m => "
              "{ if (!m.default && !m.TdqWorkflowPlugin) { console.error('thiếu export'); "
              "process.exit(1); } console.log('OK'); })")
        proc = subprocess.run(["node", "-e", NAP_URL + ma, ADAPTER_OPENCODE],
                              capture_output=True, text=True, encoding="utf-8",
                              errors="replace", timeout=120)
        self.assertEqual(proc.returncode, 0, proc.stderr[-600:])
        self.assertIn("OK", proc.stdout)

    @unittest.skipUnless(co_lenh("node"), "chưa cài node")
    def test_opencode_doc_dung_so_skill(self):
        """Adapter phải thấy ĐÚNG số skill trong nguồn chung, không phải một bản sao nào."""
        that = len([t for t in os.listdir(os.path.join(ROOT, "skills"))
                    if os.path.isfile(os.path.join(ROOT, "skills", t, "SKILL.md"))])
        ma = ("import(pathToFileURL(process.argv[1]).href).then(async m => "
              "{ const ds = await (m.docSkill || m.default.docSkill)(); "
              "console.log(ds.length); })")
        proc = subprocess.run(["node", "-e", NAP_URL + ma, ADAPTER_OPENCODE],
                              capture_output=True, text=True, encoding="utf-8",
                              errors="replace", timeout=120)
        self.assertEqual(proc.returncode, 0, proc.stderr[-600:])
        self.assertEqual(int(proc.stdout.strip()), that)

    def _chay_setup(self, tdq_log):
        """Gọi `setup` với một host giả: nhận skill qua `transform`, có `session.hook`."""
        ma = ("import(pathToFileURL(process.argv[1]).href).then(async m => { "
              "const ctx = { skill: { transform: async f => f({ add() {} }) }, "
              "session: { hook: async () => {} } }; await m.setup(ctx); })")
        return subprocess.run(["node", "-e", NAP_URL + ma, ADAPTER_OPENCODE],
                              capture_output=True, encoding="utf-8", errors="replace",
                              env=dict(os.environ, TDQ_LOG=tdq_log), timeout=120)

    @unittest.skipUnless(co_lenh("node"), "chưa cài node")
    def test_opencode_log_bat_mac_dinh_co_timestamp(self):
        proc = self._chay_setup("1")
        self.assertEqual(proc.returncode, 0, proc.stderr[-600:])
        self.assertRegex(proc.stderr, r"\[\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\] tdq-workflow: "
                                      r"đăng ký \d+/\d+ skill")

    @unittest.skipUnless(co_lenh("node"), "chưa cài node")
    def test_opencode_log_tat_duoc(self):
        proc = self._chay_setup("0")
        self.assertEqual(proc.returncode, 0, proc.stderr[-600:])
        self.assertEqual(proc.stderr.strip(), "")

    def test_opencode_phu_thuoc_chi_thu_vien_chuan(self):
        """Giới hạn user chốt ở vòng chi tiết: cấm package npm, đúng kỷ luật của superpowers."""
        chuan = {"path", "fs", "url", "os", "node:path", "node:fs", "node:url", "node:os"}
        van_ban = doc_van_ban(ADAPTER_OPENCODE)
        nguon = re.findall(r"""(?:from|require\()\s*['"]([^'"]+)['"]""", van_ban)
        ngoai = [n for n in nguon if n not in chuan and not n.startswith(".")]
        self.assertEqual(ngoai, [], f"adapter kéo theo package ngoài: {ngoai}")


class KhongConBundleTest(unittest.TestCase):
    """Mô hình cũ không được quay lại bằng đường nào."""

    def setUp(self):
        proc = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True,
                              text=True, encoding="utf-8", errors="replace", timeout=120)
        if proc.returncode != 0:
            self.skipTest("không phải git repo")
        self.theo_doi = proc.stdout.splitlines()

    def test_khong_con_bundle_trong_git(self):
        con = sorted({d.split("/")[0] for d in self.theo_doi
                      if d.split("/")[0] in BUNDLE_CU})
        self.assertEqual(con, [], f"ba bundle vẫn còn trong git: {con}")

    def test_khong_con_zip_ban_sao(self):
        self.assertNotIn("portable_codex.zip", self.theo_doi)


if __name__ == "__main__":
    unittest.main()
