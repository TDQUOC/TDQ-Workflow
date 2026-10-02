"""Header `SessionStart` không được phụ thuộc độ dài đường dẫn project (yêu cầu 2026-09-27-1905).

Lỗi thật, đo trên CI: trần 600 ký tự của khối đầu (spec §2.7) tính cả dòng `Project: <đường dẫn>`.
Thư mục tạm của macOS runner là `/var/folders/36/tjdph2t965j8snz9_vkdnw0r0000gn/T/tmpXXXXXXXX`,
đủ dài để đẩy khối đầu vượt trần, nên `cap()` cắt đuôi và để lại dấu `…` — tức mất chữ của dòng
lệnh. Đường dẫn project là dữ liệu của user: không ai chọn được độ dài của nó, nên thứ phải nhường
là phần HIỂN THỊ đường dẫn, không phải trần.

Luật chốt ở đây: header in đường dẫn RÚT NGỌN với trần ký tự cố định; `STATE.md` — nơi không có
trần — giữ đường dẫn tuyệt đối đầy đủ.

Hai nhóm chạy riêng được bằng `-k`: `header`, `state_md`.
"""
import os
import sys
import tempfile
import unittest

from helper import ROOT, bo_duong_dan_plugin, run_hook, write_state

sys.path.insert(0, os.path.join(ROOT, "scripts"))
import tdq_state  # noqa: E402

MOC_LUAT = "[TDQ:GON]"
TRAN_KHOI_DAU = 600


def khoi_dau(out):
    """Đoạn văn đầu tiên — chỗ duy nhất trần 12 dòng / 600 ký tự áp vào (2026-09-21)."""
    # 2026-10-03: hook in đường dẫn TUYỆT ĐỐI ở project không có `scripts/` — đúng ca thư mục tạm
    # của test. Trần đo NỘI DUNG khối đầu; tiền tố đường dẫn là cơ học, đổi sau bước cắt.
    out = bo_duong_dan_plugin(out)
    return out.split(MOC_LUAT, 1)[0].split("\n\n", 1)[0].rstrip()


# 190 chứ không 240: Windows chặn ở MAX_PATH 260, mà test còn phải tạo `docs/tdq/state.json`
# bên trong thư mục đó (thêm ~20 ký tự) — dựng sâu hơn là đỏ vì WinError 206, một lý do chẳng
# liên quan gì tới thứ đang kiểm.
DAI_MAC_DINH = 190


def duong_dan_dai(goc, so_ky_tu=DAI_MAC_DINH):
    """Dựng một thư mục thật có đường dẫn dài ít nhất `so_ky_tu` ký tự."""
    duong = goc
    while len(duong) < so_ky_tu:
        duong = os.path.join(duong, "thu-muc-long-mot-cai-ten-dai")
    os.makedirs(duong, exist_ok=True)
    return duong


class HeaderTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)

    def test_header_duong_dan_dai_khong_lam_tran_khoi_dau(self):
        cwd = duong_dan_dai(self._tmp.name)
        write_state(cwd, active_request="2026-07-27-0900-mot-request-ten-kha-dai", lane="full",
                    phase="spec", spec_approved=True, plan_approved=True,
                    spec_file="docs/tdq/spec/x.md", plan_file="docs/tdq/plan/x.md")
        rc, out, err = run_hook("session_start.py", {"cwd": cwd, "session_id": "s-dai"})
        self.assertEqual(rc, 0, err)
        dau = khoi_dau(out)
        self.assertLessEqual(len(dau), TRAN_KHOI_DAU,
                             f"khối đầu {len(dau)} ký tự với đường dẫn {len(cwd)} ký tự")
        # Phân biệt hai dấu `…` khác nhau: một là dấu RÚT GỌN đường dẫn (hợp lệ, do
        # `duong_hien_thi` đặt), một là dấu BỊ CẮT TRẦN của `cap()` (lỗi). Dấu cắt trần luôn nằm
        # ở CUỐI khối, và nó cắt mất những dòng cuối — nên đo bằng "dòng cuối còn không".
        self.assertFalse(dau.endswith("…"), "khối đầu bị cắt trần")
        self.assertIn("Command:", dau, "dòng lệnh phải còn nguyên")
        self.assertIn("Done when:", dau, "dòng cuối của khối đầu bị cắt mất")

    def test_header_do_dai_khong_tang_theo_duong_dan(self):
        """Đo hai lần, đường dẫn ngắn và đường dẫn dài: chênh lệch phải bị chặn, không tuyến tính."""
        do = {}
        for ten, so in (("ngan", 0), ("dai", DAI_MAC_DINH)):
            cwd = self._tmp.name if so == 0 else duong_dan_dai(self._tmp.name, so)
            write_state(cwd, active_request="2026-07-27-0900-demo", lane="full", phase="plan",
                        spec_approved=True, spec_file="docs/tdq/spec/x.md")
            _, out, _ = run_hook("session_start.py", {"cwd": cwd, "session_id": f"s-{ten}"})
            do[ten] = len(khoi_dau(out))
        self.assertLess(do["dai"] - do["ngan"], 60,
                        f"header dài thêm {do['dai'] - do['ngan']} ký tự khi đường dẫn dài thêm")

    def test_header_duong_dan_ngan_thi_in_nguyen(self):
        """Rút gọn chỉ được ra tay khi cần: đường dẫn ngắn phải hiện đủ, không cắt vô cớ."""
        cwd = self._tmp.name
        write_state(cwd, active_request="2026-07-27-0900-demo", lane="full", phase="spec")
        _, out, _ = run_hook("session_start.py", {"cwd": cwd, "session_id": "s-ngan"})
        self.assertIn(os.path.basename(cwd), out)

    def test_header_giu_ten_thu_muc_cuoi(self):
        """Rút gọn kiểu nào cũng phải giữ tên thư mục cuối — đó là thứ user nhận ra project."""
        cwd = duong_dan_dai(self._tmp.name)
        write_state(cwd, active_request="2026-07-27-0900-demo", lane="full", phase="spec")
        _, out, _ = run_hook("session_start.py", {"cwd": cwd, "session_id": "s-cuoi"})
        self.assertIn(os.path.basename(cwd), khoi_dau(out))


class StateMdTest(unittest.TestCase):
    """`STATE.md` không có trần, nên nó là nơi giữ đường dẫn đầy đủ."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)

    def test_state_md_giu_duong_dan_tuyet_doi_day_du(self):
        cwd = duong_dan_dai(self._tmp.name)
        state = write_state(cwd, active_request="2026-07-27-0900-demo", lane="full", phase="spec")
        noi_dung = tdq_state.render_state_md(cwd, state)
        self.assertIn(os.path.abspath(cwd), noi_dung,
                      "STATE.md phải giữ đường dẫn đầy đủ, nó không có trần nào")


if __name__ == "__main__":
    unittest.main()
