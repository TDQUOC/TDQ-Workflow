"""Chống bỏ sót khi rút gọn ~/.claude/CLAUDE.md (spec 2026-08-05 §2).

3 điều kiện, đo trên BẢN MẪU trong repo `docs/claude-md-mau.md`:
  (a) mọi luật bị CHUYỂN phải tìm được ở đúng file đích;
  (b) luật bất biến (git, trình bày, logging, 5 luật kích hoạt TDQ) vẫn còn trong bản mẫu;
  (c) bản mẫu ≤ 3.500 byte.

Không so với `~/.claude/CLAUDE.md`: suite phải chạy được ở máy chưa cài,
và file ngoài repo không phải thứ test của repo được phép đòi hỏi.
"""

import os
import struct
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CORE = os.path.join(REPO, "docs", "claude-md-mau.md")
sys.path.insert(0, os.path.join(REPO, "scripts"))
import tdq_setup  # noqa: E402 — chủ của khối ghim, để test và sản phẩm dùng chung một dấu mốc
# 2026-09-20: 3500 → 3800. The template stood at 3533 bytes, and every section of it is a
# tier-1 or tier-2 law (approval, git, secrets, the TDQ gates); §7 already forbids copying
# details in, so there is nothing redundant left to squeeze. `soul.md` settles which side
# gives: a size cap is a tier-3 constraint, so hitting it means RAISING THE CAP, never
# compressing a law to fit. Same ruling the repo already applied to `chung.md` (150 → 240
# lines). The cap still exists because this file is loaded every session.
# 2026-09-28: 3800 → 4300. Khối `TDQ:TOOLS` ghim luật 4 tầng vào instruction user-level, thứ một
# agent phải biết TRƯỚC khi nạp bất kỳ skill nào — chưa biết thì nó grep mọi thứ. Cùng phán quyết
# của soul.md như lần trước: trần kích thước là ràng buộc tầng 3, nên chạm trần là NÂNG TRẦN chứ
# không nén luật. Khối đo được 466 byte, trần chừa phần cho một lần sửa chữ sau này.
# 2026-10-11: 4300 → 6000. 0.65/0.66 thêm hai mục luật cứng vào khối ghim (cấm plan mode/popup,
# cấm trailer AI) và 0.67 thêm dòng dự phòng `Unknown skill` — kênh duy nhất tới model ở project
# chưa bật plugin. Bản mẫu đo 5.6 KB sau khi đồng bộ lại; cùng phán quyết soul.md: nâng trần.
# 2026-10-15: 6000 → 6500. Thêm hướng dẫn khởi tạo LSP và tra symbol vào khối ghim; cùng phán quyết.
# 2026-10-20: 6500 → 10000. Bổ sung MCP-First, LSP-Autonomy, Auto-carry dirty zone, Khảo sát 3 chiều và Ngoại lệ Refactor; cùng phán quyết soul.md.
# 2026-11-03: 10000 -> 11500. Verified completion, permission boundaries and
# tool handoff are tier-1 rules; measured template is 11181 bytes, not optional detail.
# 2026-11-05: 11500 -> 12500. Plain, visual, complete presentation and the 4-part
# Before/After + Tested/Result report contract with Archify HTML are tier-1 rules
# pinned in TDQ:TOOLS so every session and project receives them on install/update.
MAX_BYTES = 12500

# (mô tả, đường dẫn file đích tương đối repo, các chuỗi phải có mặt)
# Đích có thể là MỘT file hay MỘT CẶP file: 2026-10-02 vài file luật bị tách làm file anh + file
# em để xuống dưới trần token, và luật không rời skill — nó sang file em, vẫn được trỏ tới từ cùng
# `SKILL.md`. Đòi needle nằm đúng file anh là đòi một chi tiết sắp xếp, không phải đòi luật còn.
MOVED = [
    ("§3 failover Tavily", "skills/tdq-conventions/references/tavily.md",
     ["tavily-primary", "tavily-backup", "websearch"]),
    ("§6 quy ước working log", "skills/tdq-conventions/SKILL.md",
     ["docs/workinglog", "working log"]),
    ("§7 xử lý issue user báo", "skills/tdq-intake/references/issue-triage.md",
     ["log", "computer use", "spec"]),
    ("§8 checklist lập spec", ("skills/tdq-spec/references/spec-template.md",
                               "skills/tdq-spec/references/spec-template-huong-dan.md"),
     ["qc", "download"]),
    ("§10 bảng định tuyến plugin", "skills/tdq-conventions/references/plugin-routing.md",
     ["data-engineering", "desktop-commander", "notion", "mongodb"]),
    ("§9 chi tiết mode thực thi", "skills/tdq-plan/SKILL.md",
     ["main", "subagent"]),
]

# Luật KHÔNG được rời bản lõi — mất một dòng là mất một hàng rào an toàn.
INVARIANTS = [
    ("§2 cấm tiền tố tên branch", ["antigravity", "gemini", "codex"]),
    ("§2 cấm trailer AI trong commit", ["co-authored-by"]),
    ("§2 chỉ commit khi user yêu cầu", ["commit"]),
    ("§3 cấm lộ API key", ["api key"]),
    ("§3 không bịa thông tin", ["không được bịa"]),
    ("§4 trình bày ngắn gọn", ["ngắn gọn"]),
    ("§5 log service cho sản phẩm", ["log"]),
    ("§9①  mọi prompt mới vào intake", ["tdq-intake"]),
    ("§9② chỉ user duyệt", ["chỉ người dùng duyệt", "hỏi"]),
    ("§9③ state chỉ ghi qua script", ["tdq_state.py"]),
    ("§9④ gộp gate duyệt", ["duyệt plan"]),
    ("§9⑤ doc tiếng Việt, report ngắn gọn 10-20 dòng", ["tiếng việt", "10-20 dòng"]),
]


def _read(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


class CoreFileTest(unittest.TestCase):
    def test_ban_mau_ton_tai_trong_repo(self):
        self.assertTrue(os.path.exists(CORE), f"thiếu nguồn sự thật {CORE}")

    def test_c_kich_thuoc_khong_qua_tran(self):
        # Measured as git stores it (LF): a Windows checkout with core.autocrlf adds one byte per
        # line, and read 4314 bytes for a 4250-byte template (2026-10-08).
        with open(CORE, "rb") as fh:
            size = len(fh.read().replace(b"\r\n", b"\n"))
        self.assertLessEqual(size, MAX_BYTES, f"bản mẫu {size} byte > {MAX_BYTES}")


class MovedRulesTest(unittest.TestCase):
    """(a) Luật đã chuyển phải nằm ở file đích, nếu không là mất luật."""

    def test_moi_luat_chuyen_deu_co_o_file_dich(self):
        for label, dich, needles in MOVED:
            rels = (dich,) if isinstance(dich, str) else dich
            with self.subTest(luat=label):
                van = []
                for rel in rels:
                    path = os.path.join(REPO, rel)
                    self.assertTrue(os.path.exists(path), f"{label}: thiếu file đích {rel}")
                    van.append(_read(path).lower())
                text = chr(10).join(van)
                for needle in needles:
                    self.assertIn(needle, text,
                                  f"{label}: {' + '.join(rels)} thiếu \"{needle}\"")


class InvariantRulesTest(unittest.TestCase):
    """(b) Luật bất biến phải còn nguyên trong bản mẫu."""

    def test_luat_bat_bien_con_trong_ban_loi(self):
        text = _read(CORE).lower()
        for label, needles in INVARIANTS:
            with self.subTest(luat=label):
                for needle in needles:
                    self.assertIn(needle, text, f"{label}: bản mẫu thiếu \"{needle}\"")




class KhoiHuongDanToolTest(unittest.TestCase):
    """(d) Bản ngắn của luật 3 tầng phải được GHIM vào instruction user-level.

    Vì sao phải ghim: luật đầy đủ nằm trong `skills/`, thứ chỉ được nạp khi router gọi đúng skill.
    Một agent chưa nạp skill nào vẫn phải biết dùng công cụ nào khi nào, nếu không nó mặc định
    grep mọi thứ. Khối có dấu mốc để `scripts/tdq_setup.py` ghi lại được mà không đụng phần user
    tự viết — Claude Code không có cách tắt/ghi đè từng phần nào khác.
    """

    def test_khoi_co_dau_moc_dong_mo_va_dong_dong(self):
        text = _read(CORE)
        self.assertIn(tdq_setup.MOC_MO, text)
        self.assertIn(tdq_setup.MOC_DONG, text)
        self.assertEqual(text.count(tdq_setup.MOC_MO), 1, "khối bị nhân bản")

    def test_khoi_ke_du_ba_tang(self):
        text = _read(CORE)
        khoi = text.split(tdq_setup.MOC_MO)[1].split(tdq_setup.MOC_DONG)[0]
        for ten in ("lsp", "grep", "graphify"):
            self.assertIn(ten, khoi.lower(), f"khối ghim thiếu tầng {ten}")
        self.assertNotIn("lumen", khoi.lower(), "0.58.0: khối ghim không được dẫn tới lumen")

    def test_khoi_ghi_hai_lan_khong_nhan_ban(self):
        with tempfile.TemporaryDirectory() as tmp:
            dich = os.path.join(tmp, "CLAUDE.md")
            with open(dich, "w", encoding="utf-8") as fh:
                fh.write("# Luật của tôi\n\n- một dòng của user\n")
            tdq_setup.ghim_huong_dan_tool(dich)
            tdq_setup.ghim_huong_dan_tool(dich)
            noi_dung = _read(dich)
        self.assertEqual(noi_dung.count(tdq_setup.MOC_MO), 1)
        self.assertIn("một dòng của user", noi_dung, "không được đụng phần user tự viết")

    def test_khoi_cap_nhat_lai_dung_cho_cu(self):
        """Ghi lần hai với nội dung mới phải THAY khối cũ, không nối thêm khối thứ hai."""
        with tempfile.TemporaryDirectory() as tmp:
            dich = os.path.join(tmp, "CLAUDE.md")
            with open(dich, "w", encoding="utf-8") as fh:
                fh.write(f"# Đầu\n\n{tdq_setup.MOC_MO}\nnội dung cũ\n{tdq_setup.MOC_DONG}\n\n# Cuối\n")
            tdq_setup.ghim_huong_dan_tool(dich)
            noi_dung = _read(dich)
        self.assertNotIn("nội dung cũ", noi_dung)
        self.assertIn("# Cuối", noi_dung, "phần sau khối phải còn nguyên")

    def test_khoi_trong_ban_mau_khop_nguyen_van_voi_hang_so(self):
        """Bản mẫu và hằng số trong code là MỘT, không phải hai bản chép tay.

        Chúng đã lệch một lần trong chính request sinh ra khối này: hằng số được sửa sang đường
        dẫn khác sau khi bản mẫu đã ghi, và không phép kiểm nào thấy. Bản được GHI RA MÁY USER
        lại là bản không ai soi, nên chỗ này phải có một ca so nguyên văn.
        """
        text = _read(CORE)
        trong_mau = text.split(tdq_setup.MOC_MO)[1].split(tdq_setup.MOC_DONG)[0].strip()
        self.assertEqual(trong_mau, tdq_setup.khoi_huong_dan(tdq_setup.GOC_MAU).strip())

    def test_khoi_co_duong_du_phong_unknown_skill(self):
        """Project chưa bật plugin: hook không chạy, khối ghim là kênh duy nhất tới model."""
        goc = "/may/goc"
        dong = [d for d in tdq_setup.khoi_huong_dan(goc).splitlines() if "Unknown skill" in d]
        self.assertEqual(len(dong), 1, "cần đúng một dòng dự phòng")
        self.assertLessEqual(len(dong[0]), 300, f"dòng dự phòng {len(dong[0])} ký tự > 300")
        self.assertIn(f"{goc}/skills/tdq-intake/SKILL.md", dong[0])
        self.assertIn("setup", dong[0])

    def test_khoi_trong_ban_mau_khong_mang_duong_dan_cua_mot_may_cu_the(self):
        """Bản mẫu là tài liệu chung — đường dẫn tuyệt đối của máy người dựng không được lọt vào."""
        text = _read(CORE)
        trong_mau = text.split(tdq_setup.MOC_MO)[1].split(tdq_setup.MOC_DONG)[0]
        for dau_hieu in ("C:/Users/", "C:" + os.sep + "Users", "/home/", "/Users/"):
            self.assertNotIn(dau_hieu, trong_mau, f"bản mẫu lọt đường dẫn máy: {dau_hieu}")

    def test_byte_tran_da_duoc_nang_kem_ly_do(self):
        """soul.md: trần kích thước là ràng buộc tầng 3 — chạm trần thì NÂNG TRẦN, không nén luật."""
        nguon = _read(os.path.join(REPO, "tests", "test_claude_md_core.py"))
        self.assertGreater(MAX_BYTES, 3800, "thêm luật mà không nâng trần là sẽ phải nén luật")
        self.assertIn("2026-09-28", nguon, "mỗi lần nâng trần phải ghi lý do kèm ngày")

    def test_khoi_co_chuan_trinh_bay_va_report_de_hieu_archify(self):
        khoi = tdq_setup.khoi_huong_dan(tdq_setup.GOC_MAU)
        for cum in (
            "đơn giản, dễ hiểu, ngắn gọn",
            "trực quan, đầy đủ thông tin",
            "Archify HTML",
            "Trước request",
            "Sau request",
            "Đã test gì",
            "Kết quả test",
        ):
            self.assertIn(cum, khoi)


class AclDescriptorTest(unittest.TestCase):
    @staticmethod
    def descriptor(reverse=False, sid=18, masks=(0x1f01ff, 0x120089), control=0x8004,
                   ace_flags=(0, 0), revision=2, dacl="acl", padding=0):
        owner = bytes((1, 1)) + b"\0\0\0\0\0\5" + struct.pack("<I", sid)
        group = bytes((1, 1)) + b"\0\0\0\0\0\5" + struct.pack("<I", 32)
        aces = [struct.pack("<BBHI", 0, flag, 20, mask) + owner
                for mask, flag in zip(masks, ace_flags)]
        acl = struct.pack("<BBHHH", revision, 0, 8 + sum(map(len, aces)) + padding,
                          len(aces), 0) + b"".join(aces) + b"\0" * padding
        parts = {"owner": owner, "group": group, "dacl": acl}
        order = ("dacl", "group", "owner") if reverse else ("owner", "group", "dacl")
        data, offsets = b"", {"dacl": 0}
        for name in order:
            if name == "dacl" and dacl != "acl":
                continue
            offsets[name] = 20 + len(data)
            data += parts[name]
        if dacl == "absent":
            control &= ~4
        return struct.pack("<BBHIIII", 1, 0, control, offsets["owner"],
                           offsets["group"], 0, offsets["dacl"]) + data

    def test_equivalent_storage(self):
        first, second = self.descriptor(), self.descriptor(reverse=True, padding=8)
        self.assertNotEqual(first, second)
        self.assertTrue(tdq_setup._acl_instruction_bang_nhau(first, second))
        self.assertTrue(tdq_setup._acl_instruction_bang_nhau(None, None))
        self.assertFalse(tdq_setup._acl_instruction_bang_nhau(first, None))

    def test_changed_semantics(self):
        first = self.descriptor()
        changes = (self.descriptor(sid=19), self.descriptor(masks=(0x120089, 0x1f01ff)),
                   self.descriptor(masks=(0x1f01ff, 1)), self.descriptor(ace_flags=(16, 0)),
                   self.descriptor(control=0x9004), self.descriptor(control=0x8404),
                   self.descriptor(control=0x8005), self.descriptor(control=0x8006),
                   self.descriptor(control=0x800c), self.descriptor(revision=4))
        for change in changes:
            with self.subTest(change=change):
                self.assertFalse(tdq_setup._acl_instruction_bang_nhau(first, change))
        variants = [self.descriptor(dacl="absent"), self.descriptor(dacl="null"),
                    self.descriptor(masks=(), ace_flags=())]
        for index, left in enumerate(variants):
            for right in variants[index + 1:]:
                self.assertFalse(tdq_setup._acl_instruction_bang_nhau(left, right))

    def test_invalid_descriptors_rejected_even_when_identical(self):
        valid = self.descriptor()
        malformed = [valid[:size] for size in range(len(valid))]
        for offset, data in ((0, b"\2"), (2, b"\4\0"), (4, struct.pack("<I", 9999)),
                             (20, b"\2"), (21, b"\xff"), (44, b"\3"),
                             (46, b"\xff\xff"), (48, b"\xff\xff"), (54, b"\xff\xff")):
            bad = bytearray(valid)
            bad[offset:offset + len(data)] = data
            malformed.append(bytes(bad))
        for bad in malformed:
            with self.subTest(size=len(bad)), self.assertRaisesRegex(OSError, "ACL"):
                tdq_setup._acl_instruction_bang_nhau(bad, bad)


class SafeWriterTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / "instruction.md"
        self.log = mock.patch.object(tdq_setup, "_log")
        self.log.start()
        self.addCleanup(self.log.stop)
        self.stamp = mock.patch.object(tdq_setup, "ghi_update_stamp")
        self.stamp_mock = self.stamp.start()
        self.addCleanup(self.stamp.stop)

    def write(self, data):
        self.path.write_bytes(data)
        return data

    def run_writer(self):
        return tdq_setup.ghim_huong_dan_tool(str(self.path), "/fixture/tdq")

    def backups(self):
        return list(self.path.parent.glob(self.path.name + ".bak.*"))

    def test_invalid_utf8_unchanged(self):
        old = self.write(b"private\xff\n")
        with self.assertRaisesRegex((ValueError, OSError), "instruction.md"):
            self.run_writer()
        self.assertEqual(self.path.read_bytes(), old)
        self.assertEqual(list(self.path.parent.iterdir()), [self.path])

    def test_bad_markers_unchanged(self):
        start, end = tdq_setup.MOC_MO, tdq_setup.MOC_DONG
        for content in (start, end, end + start, start + start + end,
                        start + end + end, start + end + start + end):
            with self.subTest(content=content):
                old = self.write(content.encode())
                with self.assertRaisesRegex(ValueError, "instruction.md"):
                    self.run_writer()
                self.assertEqual(self.path.read_bytes(), old)
                self.assertEqual(self.backups(), [])

    def test_replace_preserves_bom_mixed_newlines_and_outside_bytes(self):
        before = b"\xef\xbb\xbf# private\r\n\n  "
        after = "\r\n# Cuối\n  \r".encode()
        old = self.write(before + tdq_setup.MOC_MO.encode() + b"\nold\n"
                         + tdq_setup.MOC_DONG.encode() + after)
        self.assertTrue(self.run_writer())
        block = (tdq_setup.MOC_MO + "\n" + tdq_setup.khoi_huong_dan("/fixture/tdq")
                 + "\n" + tdq_setup.MOC_DONG).replace("\n", "\r\n").encode()
        self.assertEqual(self.path.read_bytes(), before + block + after)
        self.assertEqual([p.read_bytes() for p in self.backups()], [old])
        self.stamp_mock.assert_not_called()

    def test_append_preserves_all_original_bytes(self):
        for old in (b"private  \r\n \t", b"\xef\xbb\xbf", b"\n\r\n", b"private"):
            with self.subTest(old=old):
                self.write(old)
                self.assertTrue(self.run_writer())
                data = self.path.read_bytes()
                self.assertTrue(data.startswith(old))
                newline = b"\r\n" if old == b"private  \r\n \t" else b"\n"
                self.assertIn(tdq_setup.MOC_MO.encode() + newline, data)

    def test_new_file_and_noop_without_io_changes(self):
        self.assertTrue(self.run_writer())
        self.assertEqual(self.backups(), [])
        old, info = self.path.read_bytes(), self.path.stat()
        with mock.patch.object(tdq_setup.tempfile, "mkstemp", side_effect=AssertionError("write")), \
                mock.patch.object(tdq_setup.os, "replace", side_effect=AssertionError("replace")):
            self.assertFalse(self.run_writer())
        self.assertEqual(self.path.read_bytes(), old)
        self.assertEqual(self.path.stat().st_mtime_ns, info.st_mtime_ns)
        self.assertEqual(self.path.stat().st_ino, info.st_ino)
        self.assertEqual(self.backups(), [])
        self.stamp_mock.assert_not_called()

    def test_unique_backups(self):
        old = self.write(b"private\n")
        self.run_writer()
        first = self.path.read_bytes()
        tdq_setup.ghim_huong_dan_tool(str(self.path), "/fixture/other")
        self.assertCountEqual([p.read_bytes() for p in self.backups()], [old, first])

    def test_temp_creation_failure_preserves_source(self):
        old = self.write(b"private\n")
        with mock.patch.object(tdq_setup.tempfile, "mkstemp", side_effect=OSError("temp failure")):
            with self.assertRaisesRegex(OSError, "instruction.md"):
                self.run_writer()
        self.assertEqual(self.path.read_bytes(), old)

    def test_replace_failure_preserves_source_and_backup(self):
        old = self.write(b"private\n")
        with mock.patch.object(tdq_setup.os, "replace", side_effect=OSError("replace failure")):
            with self.assertRaisesRegex(OSError, "instruction.md"):
                self.run_writer()
        self.assertEqual(self.path.read_bytes(), old)
        self.assertEqual([p.read_bytes() for p in self.backups()], [old])
        self.assertEqual(len(list(self.path.parent.iterdir())), 2)

    def test_readback_failure_restores_source(self):
        old = self.write(b"private\n")
        real_open, replaced = tdq_setup.io.open, []
        real_replace = tdq_setup.os.replace

        def replace(src, dst):
            real_replace(src, dst)
            replaced.append(dst)

        def fail_readback(path, mode="r", *args, **kwargs):
            if str(path) == str(self.path) and mode == "rb" and len(replaced) == 1:
                raise OSError("readback failure")
            return real_open(path, mode, *args, **kwargs)

        with mock.patch.object(tdq_setup.os, "replace", side_effect=replace), \
                mock.patch.object(tdq_setup.io, "open", side_effect=fail_readback):
            with self.assertRaisesRegex(OSError, "instruction.md"):
                self.run_writer()
        self.assertEqual(self.path.read_bytes(), old)
        self.assertEqual([p.read_bytes() for p in self.backups()], [old])

    def test_rollback_failures_report_existing_unique_backup(self):
        real_open = tdq_setup.io.open
        real_replace = tdq_setup.os.replace
        create = tdq_setup._tam_instruction
        for failure in ("create", "replace", "readback"):
            with self.subTest(failure=failure):
                old = self.write(b"private\n")
                existing = set(self.backups())
                replaced = []

                def replace(src, dst):
                    if replaced and failure == "replace":
                        raise OSError("restore replace failure")
                    real_replace(src, dst)
                    replaced.append(dst)

                def stage(*args):
                    if replaced and failure == "create":
                        raise OSError("restore creation failure")
                    return create(*args)

                def fail_readback(path, mode="r", *args, **kwargs):
                    if str(path) == str(self.path) and mode == "rb" and replaced:
                        raise OSError("readback failure")
                    return real_open(path, mode, *args, **kwargs)

                with mock.patch.object(tdq_setup, "_tam_instruction", side_effect=stage), \
                        mock.patch.object(tdq_setup.os, "replace", side_effect=replace), \
                        mock.patch.object(tdq_setup.io, "open", side_effect=fail_readback):
                    with self.assertRaises(OSError) as error:
                        self.run_writer()
                backups = set(self.backups()) - existing
                self.assertEqual(len(backups), 1)
                backup = backups.pop()
                self.assertEqual(backup.read_bytes(), old)
                self.assertIn(str(backup), str(error.exception))
                self.assertEqual(list(self.path.parent.glob("*.tmp.*")), [])

    def test_staged_acl_mismatch_preserves_original(self):
        old = self.write(b"private\n")
        read_acl = tdq_setup._acl_instruction

        def mismatch(path, descriptor=None):
            if descriptor is None and ".tmp." in str(path):
                return b"mismatched ACL"
            return read_acl(path, descriptor)

        with mock.patch.object(tdq_setup, "_acl_instruction", side_effect=mismatch), \
                mock.patch.object(tdq_setup.os, "replace") as replace:
            with self.assertRaisesRegex(OSError, "ACL"):
                self.run_writer()
            replace.assert_not_called()
        self.assertEqual(self.path.read_bytes(), old)
        self.assertEqual([p.read_bytes() for p in self.backups()], [old])
        self.assertEqual(list(self.path.parent.glob("*.tmp.*")), [])

    def test_concurrent_acl_change_blocks_replace(self):
        old = self.write(b"private\n")
        first = AclDescriptorTest.descriptor()
        changed = AclDescriptorTest.descriptor(ace_flags=(16, 0))
        reads = []

        def read_acl(path, descriptor=None):
            if descriptor is None:
                reads.append(path)
                return changed if len(reads) == 4 else first

        with mock.patch.object(tdq_setup, "_acl_instruction", side_effect=read_acl), \
                mock.patch.object(tdq_setup.os, "replace") as replace:
            with self.assertRaisesRegex(OSError, "ACL instruction đổi đồng thời"):
                self.run_writer()
            replace.assert_not_called()
        self.assertEqual(self.path.read_bytes(), old)

    def test_readback_acl_change_restores_original(self):
        old = self.write(b"private\n")
        first = AclDescriptorTest.descriptor()
        changed = AclDescriptorTest.descriptor(control=0x9004)
        reads = []

        def read_acl(path, descriptor=None):
            if descriptor is None:
                reads.append(path)
                return changed if len(reads) == 5 else first

        with mock.patch.object(tdq_setup, "_acl_instruction", side_effect=read_acl):
            with self.assertRaisesRegex(OSError, "ACL đọc lại instruction không khớp"):
                self.run_writer()
        self.assertEqual(self.path.read_bytes(), old)
        self.assertEqual(len(reads), 7)

    def test_backup_write_failure_preserves_source(self):
        old = self.write(b"private\n")
        with mock.patch.object(tdq_setup.os, "fsync", side_effect=OSError("backup flush")):
            with self.assertRaisesRegex(OSError, "instruction.md"):
                self.run_writer()
        self.assertEqual(self.path.read_bytes(), old)
        self.assertEqual(list(self.path.parent.iterdir()), [self.path])

    def test_temp_write_failure_preserves_source_and_backup(self):
        old = self.write(b"private\n")
        with mock.patch.object(tdq_setup.os, "fsync", side_effect=[None, OSError("temp flush")]):
            with self.assertRaisesRegex(OSError, "instruction.md"):
                self.run_writer()
        self.assertEqual(self.path.read_bytes(), old)
        self.assertEqual([p.read_bytes() for p in self.backups()], [old])
        self.assertEqual(len(list(self.path.parent.iterdir())), 2)

    def test_concurrent_source_change_not_overwritten(self):
        self.write(b"private\n")
        create = tdq_setup._tam_instruction

        def change_after_stage(*args):
            result = create(*args)
            if args[-1] == ".tmp.":
                self.path.write_bytes(b"concurrent writer\n")
            return result

        with mock.patch.object(tdq_setup, "_tam_instruction", side_effect=change_after_stage):
            with self.assertRaisesRegex(OSError, "instruction.md"):
                self.run_writer()
        self.assertEqual(self.path.read_bytes(), b"concurrent writer\n")

    def test_equivalent_descriptor_storage_during_staging_and_concurrency(self):
        self.write(b"private\n")
        descriptors = [AclDescriptorTest.descriptor(), AclDescriptorTest.descriptor(reverse=True)]
        reads = []

        def read_acl(path, descriptor=None):
            if descriptor is None:
                reads.append(path)
                return descriptors[len(reads) % 2]

        with mock.patch.object(tdq_setup, "_acl_instruction", side_effect=read_acl):
            self.assertTrue(self.run_writer())
        self.assertGreaterEqual(len(reads), 5)

    @unittest.skipUnless(os.name == "nt", "Windows security descriptor")
    def test_unprotected_inherited_native_roundtrip(self):
        parent_acl = tdq_setup._acl_instruction(str(self.path.parent))
        assert isinstance(parent_acl, bytes)
        parent = bytearray(parent_acl)
        # Cha protected (0x1000), AUTO_INHERITED (0x400), AUTO_INHERIT_REQ (0x100).
        # Chỉ cha bị protected; file con mới vẫn nhận ACE kế thừa.
        parent[2:4] = (int.from_bytes(parent[2:4], "little") | 0x1500).to_bytes(2, "little")
        dacl = int.from_bytes(parent[16:20], "little")
        cursor = dacl + 8
        for _ in range(int.from_bytes(parent[dacl + 4:dacl + 6], "little")):
            parent[cursor + 1] |= 3
            cursor += int.from_bytes(parent[cursor + 2:cursor + 4], "little")
        tdq_setup._acl_instruction(str(self.path.parent), bytes(parent))
        parent_readback = tdq_setup._acl_instruction(str(self.path.parent))
        assert isinstance(parent_readback, bytes)
        self.assertEqual(int.from_bytes(parent_readback[2:4], "little") & 0x1500, 0x1400)
        self.write(b"private\n")
        acl = tdq_setup._acl_instruction(str(self.path))
        assert isinstance(acl, bytes)
        control = int.from_bytes(acl[2:4], "little")
        self.assertFalse(control & 0x1000)
        self.assertTrue(control & 0x400)
        with tempfile.TemporaryDirectory() as other:
            target = Path(other) / "different-parent.md"
            target.write_bytes(b"fixture\n")
            before = tdq_setup._acl_instruction(str(target))
            self.assertFalse(tdq_setup._acl_instruction_bang_nhau(acl, before))
            tdq_setup._acl_instruction(str(target), acl)
            self.assertTrue(tdq_setup._acl_instruction_bang_nhau(
                acl, tdq_setup._acl_instruction(str(target))))
        dacl = int.from_bytes(acl[16:20], "little")
        self.assertGreater(int.from_bytes(acl[dacl + 4:dacl + 6], "little"), 0)
        self.assertTrue(acl[dacl + 9] & 16)
        self.assertTrue(self.run_writer())
        for path in [self.path, *self.backups()]:
            self.assertTrue(tdq_setup._acl_instruction_bang_nhau(
                acl, tdq_setup._acl_instruction(str(path))))

    def test_mode_acl_and_same_directory_replace(self):
        self.write(b"private\n")
        if os.name != "nt":
            self.path.chmod(0o640)
        mode = self.path.stat().st_mode
        acl = tdq_setup._acl_instruction(str(self.path))
        if os.name == "nt":
            assert isinstance(acl, bytes)
            protected = bytearray(acl)
            control = int.from_bytes(protected[2:4], "little") | 0x1000
            protected[2:4] = control.to_bytes(2, "little")
            tdq_setup._acl_instruction(str(self.path), bytes(protected))
            acl = tdq_setup._acl_instruction(str(self.path))
            assert isinstance(acl, bytes)
            self.assertTrue(int.from_bytes(acl[2:4], "little") & 0x1000)
        replace = tdq_setup.os.replace

        def same_directory(src, dst):
            self.assertEqual(Path(src).parent, self.path.parent)
            self.assertEqual(Path(dst), self.path)
            replace(src, dst)

        with mock.patch.object(tdq_setup.os, "replace", side_effect=same_directory):
            self.assertTrue(self.run_writer())
        self.assertEqual(self.path.stat().st_mode, mode)
        self.assertTrue(tdq_setup._acl_instruction_bang_nhau(
            tdq_setup._acl_instruction(str(self.path)), acl))
        if os.name == "nt":
            assert isinstance(acl, bytes)
            self.assertGreater(len(acl), 20)
        self.assertFalse(self.run_writer())
        self.assertTrue(tdq_setup._acl_instruction_bang_nhau(
            tdq_setup._acl_instruction(str(self.path)), acl))

    def test_symlink_or_reparse_rejected_without_read(self):
        self.write(b"private\n")
        info = mock.Mock(st_mode=0o120777, st_file_attributes=0x400)
        with mock.patch.object(tdq_setup.os, "lstat", return_value=info), \
                mock.patch.object(tdq_setup.os, "open", side_effect=AssertionError("follow link")):
            with self.assertRaisesRegex(ValueError, "instruction.md"):
                self.run_writer()
        self.assertEqual(self.path.read_bytes(), b"private\n")

    def test_readback_mismatch_restores_source(self):
        old = self.write(b"private\n")
        real_open, replaced = tdq_setup.io.open, []
        real_replace = tdq_setup.os.replace

        def replace(src, dst):
            real_replace(src, dst)
            replaced.append(dst)

        def mismatch(path, mode="r", *args, **kwargs):
            if str(path) == str(self.path) and mode == "rb" and len(replaced) == 1:
                return tdq_setup.io.BytesIO(b"wrong readback")
            return real_open(path, mode, *args, **kwargs)

        with mock.patch.object(tdq_setup.os, "replace", side_effect=replace), \
                mock.patch.object(tdq_setup.io, "open", side_effect=mismatch):
            with self.assertRaisesRegex(OSError, "instruction.md"):
                self.run_writer()
        self.assertEqual(self.path.read_bytes(), old)
        self.assertEqual([p.read_bytes() for p in self.backups()], [old])

    def test_nonregular_rejected(self):
        self.path.mkdir()
        with self.assertRaisesRegex((ValueError, OSError), "instruction.md"):
            self.run_writer()
        self.assertTrue(self.path.is_dir())
        self.assertEqual(self.backups(), [])


if __name__ == "__main__":
    unittest.main()
