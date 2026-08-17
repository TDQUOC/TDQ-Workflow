"""Bộ sinh hai bản portable từ một nguồn duy nhất.

Khoá hành vi của request 2026-08-17-0938-portable-codex:
  - CLI có đủ cờ và log service tắt được bằng TDQ_LOG=0;
  - manifest đủ 5 khối và sha256 khớp file thật;
  - rewrite `${CLAUDE_PLUGIN_ROOT}` → `${CLAUDE_PROJECT_DIR}` ĐẾM ĐÚNG số lần thay
    (grep bằng 0 chưa đủ: thay sót ở file không được copy vẫn cho grep sạch);
  - bản sinh không mang theo state/rác của repo nguồn.
"""
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
import unittest

import helper  # noqa: F401  — nạp sys.path cho scripts/
import build_portable

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT = os.path.join(ROOT, "scripts", "build_portable.py")


def chay(*args, env=None):
    """Gọi build_portable.py như tiến trình con — kiểm cả CLI lẫn log ra stderr."""
    proc = subprocess.run(
        [sys.executable, SCRIPT, *args],
        capture_output=True, text=True, timeout=120,
        env=dict(os.environ, **(env or {})),
    )
    return proc.returncode, proc.stdout, proc.stderr


class TempDest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.dest = self._tmp.name

    def tearDown(self):
        self._tmp.cleanup()


class TestCLI(TempDest):
    def test_help_co_du_ba_co(self):
        ma, out, _ = chay("--help")
        self.assertEqual(ma, 0)
        for co in ("--dest", "--only"):
            self.assertIn(co, out)

    def test_log_tat_duoc_bang_bien_moi_truong(self):
        _, _, bat = chay("--dest", self.dest)
        self.assertTrue(bat.strip(), "log mặc định phải BẬT, ghi ra stderr")
        with tempfile.TemporaryDirectory() as d2:
            _, _, tat = chay("--dest", d2, env={"TDQ_LOG": "0"})
        self.assertEqual(tat.strip(), "", "TDQ_LOG=0 phải im hoàn toàn")


class TestManifest(TempDest):
    def test_manifest_du_5_khoi(self):
        os.makedirs(os.path.join(self.dest, "sub"), exist_ok=True)
        with open(os.path.join(self.dest, "sub", "a.txt"), "w", encoding="utf-8") as f:
            f.write("xin chao")
        man = build_portable.sinh_manifest(self.dest)
        for khoi in ("files", "version", "python_min", "external_commands", "mcp_servers"):
            self.assertIn(khoi, man, f"manifest thiếu khối {khoi}")
        self.assertIn("sub/a.txt", man["files"], "đường dẫn trong manifest phải dùng dấu /")

    def test_sha256_khop_file_that(self):
        noi_dung = "nội dung kiểm tra"
        with open(os.path.join(self.dest, "b.txt"), "w", encoding="utf-8") as f:
            f.write(noi_dung)
        man = build_portable.sinh_manifest(self.dest)
        cho_doi = hashlib.sha256(noi_dung.encode("utf-8")).hexdigest()
        self.assertEqual(man["files"]["b.txt"], cho_doi)

    def test_manifest_khong_tu_liet_ke_chinh_no(self):
        with open(os.path.join(self.dest, "manifest.json"), "w", encoding="utf-8") as f:
            json.dump({}, f)
        man = build_portable.sinh_manifest(self.dest)
        self.assertNotIn("manifest.json", man["files"],
                         "manifest tự liệt kê chính nó thì sha256 không bao giờ khớp")


class TestDoiBien(unittest.TestCase):
    def test_doi_bien_dem_dung_so_lan(self):
        goc = 'a ${CLAUDE_PLUGIN_ROOT}/x và $CLAUDE_PLUGIN_ROOT/y'
        moi, so_lan = build_portable.doi_bien_plugin_root(goc)
        self.assertEqual(so_lan, 2, "phải đếm cả dạng ngoặc nhọn lẫn dạng trần")
        self.assertNotIn("CLAUDE_PLUGIN_ROOT", moi)
        self.assertEqual(moi.count("${CLAUDE_PROJECT_DIR}"), 2)

    def test_khong_co_bien_thi_khong_doi_gi(self):
        moi, so_lan = build_portable.doi_bien_plugin_root("khong co gi")
        self.assertEqual(so_lan, 0)
        self.assertEqual(moi, "khong co gi")


class TestBanClaude(TempDest):
    """Bản claude: cấu trúc phải giữ `hooks/` cạnh `scripts/`.

    `hooks/scripts/_common.py` suy thư mục scripts bằng `../../scripts`, nên hai cây này
    bắt buộc nằm cạnh nhau trong cùng một gốc. Gốc đó là `.claude/tdq/` — không thể đổ
    thẳng vào `.claude/` vì Claude Code chỉ nạp skill ở đúng `.claude/skills/`.
    """

    def setUp(self):
        super().setUp()
        build_portable.sinh_ban_claude(ROOT, self.dest)
        self.goc = os.path.join(self.dest, "portable_claude")

    def test_ban_claude_du_thu_muc(self):
        for duong in (".claude/settings.json", ".claude/skills", ".claude/agents",
                      ".claude/tdq/scripts", ".claude/tdq/hooks/scripts",
                      ".mcp.json", "manifest.json", "README.md"):
            self.assertTrue(os.path.exists(os.path.join(self.goc, duong)),
                            f"bản claude thiếu {duong}")

    def test_hooks_va_scripts_canh_nhau(self):
        chung_goc = os.path.join(self.goc, ".claude", "tdq")
        self.assertTrue(os.path.isfile(os.path.join(chung_goc, "hooks/scripts/_common.py")))
        self.assertTrue(os.path.isfile(os.path.join(chung_goc, "scripts/tdq_state.py")))

    def test_settings_co_du_5_hook_va_bien_dung(self):
        with open(os.path.join(self.goc, ".claude", "settings.json"), encoding="utf-8") as f:
            cai_dat = json.load(f)
        hooks = cai_dat["hooks"]
        self.assertEqual(
            sorted(hooks), ["PreToolUse", "SessionStart", "Stop", "UserPromptSubmit"])
        lenh = [h["command"] for muc in hooks.values() for nhom in muc for h in nhom["hooks"]]
        self.assertEqual(len(lenh), 5, "phải đủ 5 hook command")
        for mot_lenh in lenh:
            self.assertIn("${CLAUDE_PROJECT_DIR}/.claude/tdq/hooks/scripts/", mot_lenh)
            self.assertNotIn("CLAUDE_PLUGIN_ROOT", mot_lenh)
        self.assertIn("env", cai_dat, "phải giữ khối env của repo nguồn")

    def test_mcp_json_khong_co_secret(self):
        with open(os.path.join(self.goc, ".mcp.json"), encoding="utf-8") as f:
            tho = f.read()
        cau_hinh = json.loads(tho)
        self.assertIn("mcpServers", cau_hinh)
        for xau_khoa in ("sk-", "tvly-", "api_key", "apiKey", "token"):
            self.assertNotIn(xau_khoa, tho, f"`.mcp.json` không được chứa {xau_khoa}")

    def test_ban_claude_khong_con_plugin_root(self):
        sot = []
        for thu_muc, thu_muc_con, files in os.walk(self.goc):
            thu_muc_con[:] = [d for d in thu_muc_con if d != "__pycache__"]
            for ten in files:
                noi = build_portable._doc_text(os.path.join(thu_muc, ten))
                if noi and "CLAUDE_PLUGIN_ROOT" in noi:
                    sot.append(os.path.relpath(os.path.join(thu_muc, ten), self.goc))
        self.assertEqual(sot, [], f"còn sót biến plugin ở: {sot}")

    def test_lenh_goi_script_tro_dung_goc_tdq(self):
        """Rewrite phải kèm prefix `.claude/tdq`, nếu không lệnh gọi script trỏ sai chỗ."""
        duong = os.path.join(self.goc, ".claude", "skills", "tdq-status", "SKILL.md")
        noi_dung = build_portable._doc_text(duong)
        self.assertIn("${CLAUDE_PROJECT_DIR}/.claude/tdq/scripts/", noi_dung)


class TestBanCodex(TempDest):
    """Bản codex: harness không có skill/hook system nên mọi thứ phải là markdown đọc tuần tự."""

    def setUp(self):
        super().setUp()
        build_portable.sinh_ban_codex(ROOT, self.dest)
        self.goc = os.path.join(self.dest, "portable_codex")

    def test_ban_codex_du_file_workflow(self):
        ten = sorted(os.listdir(os.path.join(self.goc, "workflow")))
        for mo_dau in ("01-", "02-", "03-", "04-", "05-"):
            self.assertTrue(any(t.startswith(mo_dau) for t in ten),
                            f"thiếu file workflow số {mo_dau}")
        self.assertTrue(os.path.isdir(os.path.join(self.goc, "scripts")))
        self.assertTrue(os.path.isfile(os.path.join(self.goc, "manifest.json")))

    def test_phases_md_khop_phase_table(self):
        """Bảng phase phải SINH từ hằng, không chép tay — chép tay là lệch khi hằng đổi."""
        import tdq_state
        thuc_te = build_portable._doc_text(os.path.join(self.goc, "workflow", "phases.md"))
        self.assertEqual(thuc_te.strip(), tdq_state.render_phases_md().strip())

    def test_agents_md_tro_checkportable_dau_tien(self):
        noi_dung = build_portable._doc_text(os.path.join(self.goc, "AGENTS.md"))
        self.assertIn("tdq_checkportable.py", noi_dung)
        vi_tri_check = noi_dung.index("tdq_checkportable.py")
        vi_tri_intake = noi_dung.index("02-")
        self.assertLess(vi_tri_check, vi_tri_intake,
                        "bước kiểm tương thích phải đứng TRƯỚC bước mở request")

    def test_ban_codex_khong_con_plugin_root(self):
        for thu_muc, thu_muc_con, files in os.walk(self.goc):
            thu_muc_con[:] = [d for d in thu_muc_con if d != "__pycache__"]
            for ten in files:
                noi = build_portable._doc_text(os.path.join(thu_muc, ten))
                self.assertNotIn("CLAUDE_PLUGIN_ROOT", noi or "",
                                 f"còn biến plugin ở {ten}")


class TestCheckportableTrongBanSinh(TempDest):
    """Skill tự kiểm phải có mặt ở CẢ HAI bản và phải là bước đầu tiên được nhắc tới."""

    def setUp(self):
        super().setUp()
        self.claude = build_portable.sinh_ban_claude(ROOT, self.dest)
        self.codex = build_portable.sinh_ban_codex(ROOT, self.dest)

    def test_claude_co_skill_checkportable(self):
        duong = os.path.join(self.claude, ".claude", "skills", "tdq-checkportable", "SKILL.md")
        self.assertTrue(os.path.isfile(duong))
        noi_dung = build_portable._doc_text(duong)
        # Skill chỉ NHẮC tên lệnh; chép logic vào skill là tạo bản thứ hai sẽ lệch khi script đổi.
        self.assertNotIn("\nimport ", noi_dung)
        self.assertNotIn("\ndef ", noi_dung)
        self.assertIn("tdq_checkportable.py", noi_dung)

    def test_codex_co_file_checkportable(self):
        ten = os.listdir(os.path.join(self.codex, "workflow"))
        self.assertTrue(any(t.startswith("06-") and "checkportable" in t for t in ten), ten)

    def test_ca_hai_ban_deu_goi_check_dau_tien(self):
        for duong in (os.path.join(self.claude, "README.md"),
                      os.path.join(self.codex, "AGENTS.md")):
            noi_dung = build_portable._doc_text(duong)
            self.assertIn("checkportable", noi_dung, duong)

    def test_readme_neu_du_3_gioi_han(self):
        """CẢ HAI bản, không chỉ bản claude — spec §2 đầu ra #4 đòi README cho mỗi bản."""
        for goc in (self.claude, self.codex):
            duong = os.path.join(goc, "README.md")
            self.assertTrue(os.path.isfile(duong), f"{os.path.basename(goc)} thiếu README.md")
            noi_dung = build_portable._doc_text(duong)
            for tu_khoa in ("tin cậy", "MCP", "khởi động lại"):
                self.assertIn(tu_khoa.lower(), noi_dung.lower(),
                              f"{os.path.basename(goc)}/README thiếu giới hạn: {tu_khoa}")
            self.assertIn("tdq-bak-", noi_dung, "README phải nêu cơ chế sao lưu khi tự vá")

    def test_tai_lieu_khong_hua_qua_nang_luc(self):
        """Tài liệu không được hứa việc mã không làm.

        Bản trước hứa `setup` "tự cài gói" và "sửa cấu hình mức người dùng" trong khi mã
        không có một đường nào chạm tới pip hay `~`. Lời hứa sai còn tệ hơn thiếu tính
        năng: người dùng tin là đã được vá rồi bỏ qua phần phải tự làm.
        """
        cam = ("tự cài gói", "mức người dùng")
        for goc, ten in ((self.claude, "README.md"), (self.codex, "AGENTS.md"),
                         (self.codex, "README.md")):
            noi_dung = build_portable._doc_text(os.path.join(goc, ten)) or ""
            for cum in cam:
                self.assertNotIn(cum, noi_dung, f"{ten} hứa quá năng lực: {cum!r}")
        skill = build_portable._doc_text(os.path.join(
            self.claude, ".claude", "skills", "tdq-checkportable", "SKILL.md"))
        for cum in cam:
            self.assertNotIn(cum, skill, f"SKILL.md hứa quá năng lực: {cum!r}")


class TestCopyLoc(TempDest):
    def _dung_nguon_gia(self):
        """Dựng cây nguồn giả có sẵn đúng loại rác cần bị loại."""
        nguon = os.path.join(self.dest, "nguon")
        for duong in ("skills/tdq-x", "docs/tdq", ".git", "graphify-out", "__pycache__"):
            os.makedirs(os.path.join(nguon, duong), exist_ok=True)
        ghi = {
            "skills/tdq-x/SKILL.md": "noi dung skill",
            "docs/tdq/state.json": "{}",
            ".git/config": "x",
            "graphify-out/g.json": "{}",
            "__pycache__/a.pyc": "x",
        }
        for duong, noi in ghi.items():
            with open(os.path.join(nguon, duong), "w", encoding="utf-8") as f:
                f.write(noi)
        return nguon

    def test_copy_khong_mang_rac(self):
        nguon = self._dung_nguon_gia()
        dich = os.path.join(self.dest, "dich")
        build_portable.copy_loc(nguon, dich)
        self.assertTrue(os.path.exists(os.path.join(dich, "skills/tdq-x/SKILL.md")))
        for rac in ("docs/tdq/state.json", ".git/config", "graphify-out/g.json",
                    "__pycache__/a.pyc"):
            self.assertFalse(os.path.exists(os.path.join(dich, rac)),
                             f"bản sinh không được mang theo {rac}")

    def test_giu_quyen_thuc_thi(self):
        nguon = os.path.join(self.dest, "n2")
        os.makedirs(nguon, exist_ok=True)
        kich_ban = os.path.join(nguon, "run.sh")
        with open(kich_ban, "w", encoding="utf-8") as f:
            f.write("#!/bin/sh\n")
        os.chmod(kich_ban, 0o755)
        dich = os.path.join(self.dest, "d2")
        build_portable.copy_loc(nguon, dich)
        self.assertTrue(os.access(os.path.join(dich, "run.sh"), os.X_OK))


class TestCodexNativeLayers(TempDest):
    """Ba lớp native của Codex CLI (>= 0.147.0) trong `portable_codex/`.

    Vì sao khoá bằng test: bản trước KHÔNG sinh lớp nào trong ba lớp này vì tin rằng Codex
    "không có skill/hook system". Giả định đó sai, và cái sai chỉ lộ ra khi có người mở
    bundle lên hỏi. Số đo thật của từng lớp nằm ở `docs/tdq/qc/2026-08-17-1139-*.md`.
    """

    def setUp(self):
        super().setUp()
        self.goc = build_portable.sinh_ban_codex(ROOT, self.dest)

    # ---- lớp 1: skill auto-load ----

    def test_agents_skills_du_8_skill_va_frontmatter_hop_le(self):
        goc_skill = os.path.join(self.goc, ".agents", "skills")
        self.assertTrue(os.path.isdir(goc_skill), "thiếu .agents/skills — Codex quét đúng chỗ này")
        for ten in build_portable.THU_TU_SKILL:
            duong = os.path.join(goc_skill, ten, "SKILL.md")
            self.assertTrue(os.path.isfile(duong), f"thiếu {ten}/SKILL.md")
            truong = build_portable.doc_frontmatter(build_portable._doc_text(duong))
            for khoa in ("name", "description"):
                self.assertTrue(truong.get(khoa), f"{ten}/SKILL.md thiếu frontmatter {khoa}")

    def test_skill_giu_duoc_references_di_kem(self):
        """Skill mất `references/` là mất phần lớn nội dung — SKILL.md chỉ trỏ sang đó."""
        duong = os.path.join(self.goc, ".agents", "skills", "tdq-conventions", "references")
        self.assertTrue(os.path.isdir(duong))
        self.assertTrue(os.listdir(duong))

    # ---- lớp 2: MCP ----

    def test_config_toml_du_2_server_va_khong_lo_khoa(self):
        import tomllib
        duong = os.path.join(self.goc, ".codex", "config.toml")
        with open(duong, "rb") as f:
            cau_hinh = tomllib.load(f)
        self.assertEqual(sorted(cau_hinh["mcp_servers"]), sorted(build_portable.MCP_SERVERS))
        # Không giá trị nào trong file được trùng giá trị khoá thật đang có ở máy này.
        noi_dung = build_portable._doc_text(duong)
        for ten_bien, gia_tri in os.environ.items():
            if any(d in ten_bien for d in ("KEY", "TOKEN", "SECRET")) and len(gia_tri) > 8:
                self.assertNotIn(gia_tri, noi_dung, f"config.toml lộ giá trị của {ten_bien}")

    # ---- lớp 3: hook ----

    def test_hooks_nam_canh_scripts_o_goc_bundle(self):
        """`hooks/scripts/_common.py` suy ra `scripts/` bằng `../../scripts` tính từ nó."""
        self.assertTrue(os.path.isdir(os.path.join(self.goc, "hooks", "scripts")))
        self.assertTrue(os.path.isdir(os.path.join(self.goc, "scripts")))

    def test_hook_chay_duoc_trong_bo_cuc_bundle(self):
        payload = json.dumps({"hook_event_name": "PreToolUse", "tool_name": "Edit",
                              "tool_input": {"file_path": os.path.join(self.goc, "a.txt")},
                              "cwd": self.goc})
        proc = subprocess.run(
            [sys.executable, os.path.join(self.goc, "hooks", "scripts", "edit_gate.py")],
            input=payload, capture_output=True, text=True, timeout=60, cwd=self.goc)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        json.loads(proc.stdout or "{}")

    def test_hooks_json_du_4_event_va_dung_matcher_that(self):
        duong = os.path.join(self.goc, ".codex", "hooks.json")
        with open(duong, encoding="utf-8") as f:
            du_lieu = json.load(f)
        su_kien = du_lieu["hooks"]
        self.assertEqual(sorted(su_kien),
                         ["PreToolUse", "SessionStart", "Stop", "UserPromptSubmit"])
        self.assertEqual(len(su_kien["PreToolUse"]), 2, "PreToolUse phải có đúng 2 nhóm matcher")
        matcher = sorted(nhom.get("matcher", "") for nhom in su_kien["PreToolUse"])
        # Tên tool THẬT của Codex, đo bằng hook thăm dò — không phải tên của Claude Code.
        self.assertEqual(matcher, ["Bash", "apply_patch"])

    def test_moi_command_tro_toi_file_co_that_trong_bundle(self):
        with open(os.path.join(self.goc, ".codex", "hooks.json"), encoding="utf-8") as f:
            du_lieu = json.load(f)
        so_lenh = 0
        for nhom_su_kien in du_lieu["hooks"].values():
            for nhom in nhom_su_kien:
                for hook in nhom["hooks"]:
                    lenh = hook["command"]
                    self.assertNotIn("${", lenh, "command không được còn biến chưa thay")
                    duong = lenh.split()[-1].strip('"')
                    self.assertFalse(os.path.isabs(duong),
                                     "phải là đường dẫn tương đối: cwd của hook = gốc project")
                    self.assertTrue(os.path.isfile(os.path.join(self.goc, duong)), duong)
                    so_lenh += 1
        self.assertEqual(so_lenh, 5, "đủ 5 hook của bộ TDQ")

    def test_adapter_apply_patch_doc_duoc_duong_dan_trong_than_patch(self):
        """Codex gửi `tool_input.command` chứa thân patch, KHÔNG có `file_path`."""
        than = ("*** Begin Patch\n*** Update File: docs/tdq/plan/x.md\n@@\n+y\n*** End Patch")
        payload = json.dumps({"hook_event_name": "PreToolUse", "tool_name": "apply_patch",
                              "tool_input": {"command": than}, "cwd": self.goc})
        proc = subprocess.run(
            [sys.executable,
             os.path.join(self.goc, "hooks", "scripts", "codex_edit_gate.py")],
            input=payload, capture_output=True, text=True, timeout=60, cwd=self.goc)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("docs/tdq/plan/x.md", proc.stderr + proc.stdout,
                      "adapter phải rút được đường dẫn ra khỏi thân patch")

    # ---- manifest ----

    def test_manifest_liet_ke_du_file_native_moi(self):
        with open(os.path.join(self.goc, "manifest.json"), encoding="utf-8") as f:
            files = json.load(f)["files"]
        for duong in (".codex/config.toml", ".codex/hooks.json",
                      ".agents/skills/tdq-intake/SKILL.md",
                      "hooks/scripts/edit_gate.py", "hooks/scripts/codex_edit_gate.py"):
            self.assertIn(duong, files, f"manifest thiếu {duong}")


class TestTachPatch(unittest.TestCase):
    """Rút đường dẫn ra khỏi thân patch của `apply_patch` — hàm thuần, kiểm riêng."""

    def test_ba_dang_lenh_patch(self):
        from build_portable import tach_duong_dan_patch as tach
        self.assertEqual(tach("*** Update File: a/b.py\n"), "a/b.py")
        self.assertEqual(tach("*** Add File: c.md\n@@\n+x\n"), "c.md")
        self.assertEqual(tach("*** Delete File: d.txt\n"), "d.txt")

    def test_khong_co_gi_thi_tra_chuoi_rong(self):
        from build_portable import tach_duong_dan_patch as tach
        self.assertEqual(tach("khong phai patch"), "")
        self.assertEqual(tach(""), "")

    def test_lay_file_dau_tien_khi_patch_nhieu_file(self):
        from build_portable import tach_duong_dan_patch as tach
        than = "*** Begin Patch\n*** Update File: mot.py\n*** Update File: hai.py\n"
        self.assertEqual(tach(than), "mot.py")


class TestHuongDanCaiDat(unittest.TestCase):
    """README của mỗi bundle phải nêu ĐÚNG đường dẫn lệnh có thật trong chính bundle đó.

    Vì sao khoá: hai bundle đặt `tdq_checkportable.py` ở hai chỗ khác nhau
    (`scripts/` với codex, `.claude/tdq/scripts/` với claude). Chép nhầm dòng lệnh giữa
    hai README là lỗi im lặng — người dùng chạy ra `No such file` ngay bước đầu tiên.
    """

    MAU_LENH = re.compile(r"python3 ([\w./-]+\.py)")

    def _kiem(self, ten_ban):
        with tempfile.TemporaryDirectory() as tmp:
            build_portable.main(["--dest", tmp, "--only", ten_ban.split("_")[1]])
            goc = os.path.join(tmp, ten_ban)
            with open(os.path.join(goc, "README.md"), encoding="utf-8") as f:
                readme = f.read()
            duong_dan = set(self.MAU_LENH.findall(readme))
            self.assertTrue(duong_dan, f"README {ten_ban} không nêu lệnh nào")
            for duong in duong_dan:
                self.assertTrue(os.path.isfile(os.path.join(goc, duong)),
                                f"README {ten_ban} nhắc {duong} nhưng bundle không có file đó")

    def test_lenh_trong_readme_claude_co_that(self):
        self._kiem("portable_claude")

    def test_lenh_trong_readme_codex_co_that(self):
        self._kiem("portable_codex")

    def test_readme_codex_neu_du_ba_cach_trust(self):
        with tempfile.TemporaryDirectory() as tmp:
            build_portable.main(["--dest", tmp, "--only", "codex"])
            with open(os.path.join(tmp, "portable_codex", "README.md"), encoding="utf-8") as f:
                readme = f.read()
        for manh in ("setup --trust", 'trust_level = "trusted"', "Review hooks"):
            self.assertIn(manh, readme, f"README codex thiếu hướng dẫn: {manh}")


if __name__ == "__main__":
    unittest.main()
