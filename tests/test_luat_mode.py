#!/usr/bin/env python3
"""Tầng luật không được kể mode dưới dạng cặp nhị phân `main`/`subagent`.

Vì sao có phép kiểm này: thêm mode thứ ba vào code là việc một dòng bảng, còn
thứ làm người đọc (và model nhỏ) chọn sai lại là câu luật cũ vẫn nói "hai lựa
chọn". Code đúng mà luật sai thì luật thắng — nên chỗ kể mode phải kể ĐỦ.

Luật: một dòng nêu từ HAI mode trở lên phải nêu ĐỦ mọi mode trong `VALID_MODES`.
Nêu đúng một mode thì không sao — đó là mô tả riêng mode đó, không phải liệt kê.

Lối thoát có chủ đích: `<!-- luat-mode-allow: <lý do> -->` ngay TRÊN dòng, hoặc
ngay trên khối ``` chứa dòng đó. Mẫu khối chat "2 lựa chọn" là ca đúng của lối
thoát này: nó cố tình chỉ có hai, vì máy đó không chọn được mode thứ ba.
"""
import os
import re
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

from tdq_state import MODE_ALIASES, VALID_MODES  # noqa: E402

# Tám file luật của đầu ra 14 (spec §M7). Danh sách viết thẳng ở đây chứ không quét
# cả `skills/`: phép kiểm phải đỏ khi MỘT trong tám file này lùi về lối kể cũ, và
# không được đỏ vì một file khác vô can.
FILE_LUAT = (
    "skills/tdq-build/references/codex-mode.md",
    "skills/tdq-build/SKILL.md",
    "skills/tdq-build/references/team-mode.md",
    "skills/tdq-plan/SKILL.md",
    "skills/tdq-plan/references/mode-gate.md",
    "skills/tdq-plan/references/plan-template.md",
    "skills/tdq-conventions/references/approval.md",
    "skills/tdq-conventions/references/phases.md",
)

MOC_THOAT = "luat-mode-allow"
# Tách token theo mọi dấu ngăn hay gặp: `|`, `\|` trong ô bảng, `/`, dấu phẩy, khoảng trắng.
NGAN = re.compile(r"(?:\\\|)|[|/,\s]+")
MA_INLINE = re.compile(r"`([^`]+)`")
MA_NGOAC = re.compile(r"<([^<>]+)>")


def _mode_trong(chuoi):
    ra = set()
    for phan in NGAN.split(chuoi or ""):
        phan = phan.strip().strip("<>`'\"().:—-")
        ma = MODE_ALIASES.get(phan.lower())
        if ma:
            ra.add(ma)
    return ra


def mode_tren_dong(dong):
    """Tập mode mà MỘT dòng nêu ra — chỉ tính chỗ viết như định danh máy.

    Chỉ soi phần trong dấu nháy ngược và trong `<...>`: chữ "main" trong văn xuôi
    ("the main conversation") không phải một lần kể mode, và tính nó vào là tạo
    ra phép kiểm kêu oan mà người ta sẽ tắt đi.
    """
    ra = set()
    for token in MA_INLINE.findall(dong):
        ra |= _mode_trong(token)
    for token in MA_NGOAC.findall(dong):
        ra |= _mode_trong(token)
    return ra


def _duoc_tha(lines, i):
    """Dòng này có mốc thoát không: trên chính nó, ngay trên nó, hoặc trên khối ``` của nó."""
    if MOC_THOAT in lines[i]:
        return True
    if i and MOC_THOAT in lines[i - 1]:
        return True
    for j in range(i - 1, -1, -1):
        if lines[j].lstrip().startswith("```"):
            return j > 0 and MOC_THOAT in lines[j - 1]
    return False


def quet(duong):
    """[(số dòng, tập mode, nội dung)] cho mọi dòng kể thiếu mode."""
    with open(duong, encoding="utf-8") as f:
        lines = f.read().split("\n")
    loi = []
    for i, dong in enumerate(lines):
        tim = mode_tren_dong(dong)
        if len(tim) >= 2 and tim != set(VALID_MODES) and not _duoc_tha(lines, i):
            loi.append((i + 1, tim, dong.strip()))
    return loi


class TangLuatKeDuMode(unittest.TestCase):

    def test_khong_con_cap_nhi_phan(self):
        for rel in FILE_LUAT:
            with self.subTest(file=rel):
                duong = os.path.join(ROOT, rel)
                self.assertTrue(os.path.exists(duong), f"thiếu file luật {rel}")
                loi = quet(duong)
                mo_ta = "\n".join(f"  {rel}:{so}: kể {sorted(mode)} — {noi[:90]}"
                                  for so, mode, noi in loi)
                self.assertFalse(loi, f"dòng kể mode thiếu {sorted(VALID_MODES)}:\n{mo_ta}")

    def test_moi_file_luat_nhac_mode_codex(self):
        """Tám file đều phải biết mode thứ ba tồn tại — im lặng cũng là kể thiếu."""
        for rel in FILE_LUAT:
            with self.subTest(file=rel):
                with open(os.path.join(ROOT, rel), encoding="utf-8") as f:
                    self.assertIn("codex", f.read().lower(), f"{rel} chưa nhắc mode `codex`")

    def test_phep_quet_bat_duoc_cap_nhi_phan(self):
        """Phép kiểm tự chứng minh nó biết đỏ — nếu không thì `assertFalse` rỗng vô nghĩa."""
        self.assertEqual(mode_tren_dong("chạy `--mode <main|subagent>` rồi build"),
                         {"main", "subagent"})
        self.assertEqual(mode_tren_dong("nhắn `inline` hoặc `sub-agent`"),
                         {"main", "subagent"})
        self.assertEqual(mode_tren_dong("mode `main` làm tuần tự"), {"main"})
        self.assertEqual(mode_tren_dong("the main conversation stays open"), set())

    def test_moc_thoat_tha_dung_khoi(self):
        lines = ["<!-- luat-mode-allow: mẫu 2 lựa chọn -->", "```", "`main` / `subagent`",
                 "```", "`main` / `subagent`"]
        self.assertTrue(_duoc_tha(lines, 2))
        self.assertFalse(_duoc_tha(lines, 4))


if __name__ == "__main__":
    unittest.main()
