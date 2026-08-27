# QC — mind-map HTML trình bày dạng sơ đồ luồng
Ngày: 2026-08-27 · Plan: ../plan/2026-08-27-1628-mindmap-html-dang-so-do.md · Vòng: 1
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

| # | Hạng mục | Lệnh đã chạy | Kết quả | PASS/FAIL |
|---|---|---|---|---|
| Q1 | Tầng mô hình trả dữ liệu thuần, cặp `B<n>`/`B<n>!` ra 1 node quyết định + 1 node nhánh lỗi + 1 cạnh nhãn `lỗi` | `pytest tests/test_mindmap_render.py -q -k flow_model` | 10 passed | PASS |
| Q2 | Hộp cao theo chữ, không mất chữ, không chồng lấn | `pytest ... -k "wrap_label or layout"` | 11 passed | PASS |
| Q3 | Đúng hình dạng theo vai, nhãn cạnh `ok`/`lỗi` | `pytest ... -k render_flow_svg` | 7 passed | PASS |
| Q4 | Trang feature đủ 2 khối, sơ đồ đứng trước danh sách | `pytest ... -k business_layer` | 4 passed | PASS |
| Q5 | Lớp chi tiết không đổi hành vi | `pytest tests/test_mindmap_render.py tests/test_mindmap_nhan_doc.py -q` | 187 passed, 21 subtests | PASS |
| Q6 | Trang tổng: cây nhánh SVG mỗi feature một link, lưới phụ thuộc phong cách mới, danh sách link cũ còn | `pytest ... -k "cay_nhanh_svg or luoi_phu_thuoc"` | 11 passed | PASS |
| Q7 | Không phụ thuộc ngoài, không thẻ trỏ ra ngoài | `pytest ... -k so_do_that` | 5 passed, 7 subtests | PASS |
| Q8 | Không mã màu cứng trong sơ đồ mới | `pytest ... -k svg_helper` | 7 passed | PASS |
| Q9 | Mọi file sơ đồ thật render lại được, không mất bước | `pytest ... -k so_do_that` | 5 passed, 7 subtests (7 sơ đồ thật) | PASS |
| Q10 | Ca biên không vỡ | `pytest ... -k "flow_model_bien or layout_khong_chong_lan"` | 7 passed | PASS |
| Q11 | Log service có timestamp, `TDQ_LOG=0` thì im | `pytest ... -k log_service` | 3 passed | PASS |
| Q12 | Ngôn ngữ đúng tầng, không placeholder | `python3 scripts/i18n_check.py scripts/mindmap_render.py` + `grep -rn "TODO\|FIXME" scripts/mindmap_render.py` | 0 dòng tiếng Việt, exit 0; grep exit 1 (không khớp) | PASS |
| Q13 | Bộ test toàn repo không có lỗi MỚI so với trước request | `python3 -m pytest tests/ -q` | 61 failed, 1642 passed — y hệt số trước khi sửa (đối chứng bằng `git stash`) | PASS |
| F1 | Toàn bộ test suite | `python3 -m pytest tests/ -q` | 61 failed, 1642 passed, 1494 subtests | PASS (không lỗi mới) |
| F2 | Hồi quy vùng `Chạm:` | `pytest tests/test_mindmap_render.py tests/test_mindmap_nhan_doc.py tests/test_doc_lint_mindmap.py -q` | 196 passed, 21 subtests | PASS |
| F3 | Ràng buộc kiến trúc spec §5 | xem mục bằng chứng | 5/5 dòng còn giữ | PASS |
| F4 | Clean code self-check | 5 câu hỏi `clean-code.md` | 5/5 "có" | PASS |

## Bằng chứng

### Q1–Q4
```
=== -k flow_model ===              10 passed, 78 deselected in 0.04s
=== -k wrap_label or layout ===    11 passed, 77 deselected in 0.02s
=== -k render_flow_svg ===          7 passed, 81 deselected in 0.03s
=== -k business_layer ===           4 passed, 84 deselected in 0.02s
```

### Q5–Q11
```
=== Q5 ===                                              187 passed, 21 subtests passed in 3.14s
=== -k cay_nhanh_svg or luoi_phu_thuoc ===              11 passed, 77 deselected in 0.02s
=== -k so_do_that ===                                    5 passed, 83 deselected, 7 subtests passed
=== -k svg_helper ===                                    7 passed, 81 deselected in 0.02s
=== -k flow_model_bien or layout_khong_chong_lan ===     7 passed, 81 deselected in 0.02s
=== -k log_service ===                                   3 passed, 85 deselected in 0.12s
```

### Q12
Lệnh trong plan viết `python3 scripts/i18n_check.py` không tham số — chạy như vậy script exit 2
kèm dòng usage (nó bắt buộc có đường dẫn). Đã chạy đúng ý định của hạng mục, trên file đã sửa:
```
$ python3 scripts/i18n_check.py scripts/mindmap_render.py
[2026-08-27T21:23:39] i18n_check: scan 1 file(s), kind=all
[2026-08-27T21:23:39] i18n_check: done — 0 line(s), exit 0
0 Vietnamese line(s) in 1 file(s)
exit=0
$ grep -rn "TODO\|FIXME" scripts/mindmap_render.py
exit=1   (không dòng nào khớp)
```

### Q13 / F1 — toàn repo
```
61 failed, 1642 passed, 1494 subtests passed in 102.48s
```
Đối chứng: `git stash push -- scripts/mindmap_render.py tests/test_mindmap_render.py` rồi chạy lại
5 file fail (`test_skill_router.py`, `test_rules_library.py`, `test_luat_skill.py`, `test_doc_lint.py`,
`test_bench.py`) → đúng 61 fail y hệt, sau đó `git stash pop`. Kết luận: 61 lỗi có sẵn từ trước
request, không liên quan bộ render mind-map (doc-lint câu dài trong `skills/tdq-build/SKILL.md`,
assert worktree của `test_bench.py`, số bản ghi skill-inventory).

### F3 — ràng buộc kiến trúc spec §5
```
$ grep -n "^import\|^from" scripts/mindmap_render.py
22:import argparse · 23:import ast · 24:import html · 25:import itertools
26:import os · 27:import re · 28:import sys · 30:from tdq_mindmap import (...)
```
- "CLI | `scripts/` | mọi hành vi chạy được" — mọi thay đổi nằm trong `scripts/mindmap_render.py`, CLI `tdq_mindmap.py xem` vẫn exit 0 (test `so_do_that`).
- "`scripts/` không import `hooks/`" — GIỮ: chỉ thư viện chuẩn + `tdq_mindmap`.
- "File code MỚI phải nằm trong `scripts/`/`hooks/`" — GIỮ: `git status --porcelain` không file code untracked nào, chỉ tài liệu và HTML.
- "Ngôn ngữ 3 tầng (2026-08-22)" — GIỮ: i18n_check 0 dòng, mọi hằng `TEXT_*` mới có `i18n-allow`.
- "`tests/` gọi được vào mọi tầng" — GIỮ: test gọi thẳng `build_flow_model`, `layout_flow`, `render_flow_svg`, `build_branch_model`.

### F4 — clean code self-check
- SRP — có: `build_flow_model` chỉ dựng mô hình, `layout_flow`/`layout_branch_tree` chỉ tính toạ độ, `render_*_svg` chỉ sinh chuỗi; ba lý do đổi tách hẳn nhau.
- OCP — có: thêm một vai node mới chỉ cần thêm một dòng dữ liệu vào bảng hình dạng, không mở thân hàm nào.
- LSP — có: không kế thừa; mọi nhánh `return` của từng hàm trả đúng một kiểu (`dict` mô hình / `dict` layout / `str` SVG, rỗng là `""` chứ không `None`).
- ISP — có: mọi tham số truyền vào đều được dùng; `marker_suffix` có mặt vì hai sơ đồ cùng trang không được trùng id `<marker>`.
- DIP — có: cây nhánh và lưới phụ thuộc đều đi qua bộ helper chung `_svg_hop`/`_svg_mui_ten`/`_svg_nhan_nhieu_dong` của T3.1, không dựng lại chi tiết hình học.

### Việc phát sinh ngoài DoD — bản portable
Sửa `scripts/mindmap_render.py` làm 3 bản sao portable lệch khỏi bản gốc (trước request chúng
khớp HEAD). Đã chạy `python3 scripts/build_portable.py` (exit 0) → cả 3 bản khớp lại, và bộ test
toàn repo sau đó vẫn đúng 61 fail / 1642 pass, không lỗi mới.

## Kết luận
PASS toàn bộ — 13 hạng mục DoD và 4 hạng mục cố định đều PASS, không mở vòng fix nào.
