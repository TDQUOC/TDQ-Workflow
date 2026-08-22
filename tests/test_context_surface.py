"""P1 — scripts/context_surface.py: đo bề mặt vào context và tốc độ hook.

Script trả lời đúng hai câu: (1) mỗi file tài liệu của plugin nặng bao nhiêu và
nằm ở TẦNG NẠP nào (luôn nạp · nạp khi gọi skill · đọc khi cần), (2) mỗi hook
tốn bao nhiêu mili-giây mỗi lượt. Số đo phải tái lập được bằng một lệnh.
"""
import os
import subprocess
import sys
import unittest

from helper import ROOT

SCRIPT = os.path.join(ROOT, "scripts", "context_surface.py")

TIERS = ("always loaded", "loaded on skill call", "read on demand")


def run(*args, env=None):
    proc = subprocess.run(
        [sys.executable, SCRIPT, *args], capture_output=True, text=True,
        timeout=300, env=dict(os.environ, **(env or {})),
    )
    return proc.returncode, proc.stdout, proc.stderr


def data_rows(stdout):
    """Dòng dữ liệu của bảng markdown: có `|` mở đầu, bỏ dòng gạch ngăn."""
    rows = []
    for line in stdout.splitlines():
        line = line.strip()
        if line.startswith("|") and set(line) - set("|-: "):
            rows.append([c.strip() for c in line.strip("|").split("|")])
    return rows


class SurfaceTable(unittest.TestCase):
    """Bảng bề mặt: mọi file tài liệu vào context đều phải có mặt và đủ cột."""

    @classmethod
    def setUpClass(cls):
        cls.code, cls.out, cls.err = run()
        cls.rows = data_rows(cls.out)

    def test_exit_0(self):
        self.assertEqual(self.code, 0, self.err)

    def test_du_35_file(self):
        body = [r for r in self.rows if r[0] != "file"]
        self.assertGreaterEqual(len(body), 35, f"chỉ có {len(body)} dòng")

    def test_moi_dong_du_5_cot(self):
        for row in self.rows:
            self.assertEqual(len(row), 5, row)

    def test_du_ba_tang_nap(self):
        tiers = {r[1] for r in self.rows if r[0] != "file"}
        for tier in TIERS:
            self.assertIn(tier, tiers)

    def test_description_va_than_skill_tach_dong(self):
        """`description` nằm trong MỌI phiên, thân SKILL.md thì không — hai
        dòng riêng, nếu gộp thì bảng nói dối về tần suất."""
        names = [r[0] for r in self.rows]
        self.assertIn("skills/tdq-plan/SKILL.md (description)", names)
        self.assertIn("skills/tdq-plan/SKILL.md (body)", names)

    def test_co_hook_va_agent(self):
        names = " ".join(r[0] for r in self.rows)
        self.assertIn("hooks/scripts/prompt_context.py", names)
        self.assertIn("agents/tdq-implementer.md", names)

    def test_ky_tu_khop_wc(self):
        """Tách description khỏi thân file thì hai nửa cộng lại phải bằng `wc -c`
        của file gốc — nếu không, bảng đang làm rơi hoặc đếm đúp ký tự."""
        parts = [r for r in self.rows if r[0].startswith("agents/tdq-implementer.md")]
        self.assertEqual(len(parts), 2, parts)
        total = sum(int(r[2].replace(".", "")) for r in parts)
        real = os.path.getsize(os.path.join(ROOT, "agents", "tdq-implementer.md"))
        self.assertEqual(total, real)

    def test_co_dong_tong(self):
        self.assertIn("TOTAL", self.out)


class HooksTiming(unittest.TestCase):
    """Chế độ `--hooks`: mỗi hook một con số mili-giây, đo nhiều lần lấy trung vị."""

    @classmethod
    def setUpClass(cls):
        cls.code, cls.out, cls.err = run("--hooks", "--runs", "3")

    def test_exit_0(self):
        self.assertEqual(self.code, 0, self.err)

    def test_du_6_dong_ms(self):
        rows = [r for r in data_rows(self.out) if "ms" in " ".join(r)]
        self.assertGreaterEqual(len(rows), 6, self.out)

    def test_so_ms_la_so_thuc(self):
        for row in data_rows(self.out):
            for cell in row:
                if cell.endswith("ms"):
                    self.assertGreater(float(cell[:-2].replace(",", ".")), 0)

    def test_ghi_dieu_kien_do(self):
        self.assertIn("3 time(s)", self.out)


class LogService(unittest.TestCase):
    """Log service: timestamp, ra stderr, tắt bằng `--quiet`."""

    def test_mac_dinh_co_log_stderr(self):
        _, out, err = run()
        self.assertTrue(err.strip(), "log service phải in ra stderr")
        self.assertRegex(err, r"\[\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}")

    def test_quiet_khong_in_gi_ra_stderr(self):
        _, out, err = run("--quiet")
        self.assertEqual(err.strip(), "")
        self.assertTrue(out.strip(), "--quiet chỉ tắt log, không tắt bảng")

    def test_sai_cu_phap_exit_2(self):
        code, _, _ = run("--khong-co-co-nay")
        self.assertEqual(code, 2)


if __name__ == "__main__":
    unittest.main()
