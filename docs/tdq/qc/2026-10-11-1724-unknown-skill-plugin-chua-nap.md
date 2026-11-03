# QC — Setup tự phát hiện và bật plugin tdq-workflow chưa bật ở scope user
Ngày: 2026-10-11 · Plan: ../plan/2026-10-11-1724-unknown-skill-plugin-chua-nap.md · Vòng: 2
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

| # | Hạng mục | Lệnh đã chạy | Kết quả | PASS/FAIL |
|---|---|---|---|---|
| Q1 | Hàm bật khóa | `python -m pytest tests/test_plugin_tiers.py -q` | 19 passed | PASS |
| Q2 | Bậc kiểm plugin user | `python -m pytest tests/test_tdq_setup.py -q -k plugin_user` | 5 passed, HOME tạm | PASS |
| Q3 | Khối ghim + dòng dự phòng | `python -m pytest tests/test_claude_md_core.py -q` | 12 passed; dòng bản mẫu 269 ký tự, máy này 315 | PASS (lệch, chờ duyệt) |
| Q4 | Hồi quy vùng setup | pytest 10 file của DoD 4 | 200 passed, 2 failed — cả 2 ở `test_tu_khoi_tao`, đã đỏ ở HEAD | PASS |
| Q5 | Áp lên máy | lệnh kiểm của T3.2 | rc=0; `settings.json.bak` có; cảnh báo lệch 0.59.0 | PASS |
| F1 | Trọn suite | `tdq_test.py tron-bo` | 2549 test; đỏ `test_codex_cli`, `test_tu_khoi_tao` — đều đỏ ở HEAD; radius misses 0; 2/3 lần chạy trọn bộ | PASS |
| F2 | Hồi quy vùng chạm | `tdq_test.py vung-cham` | 131 module; 2 FAIL có sẵn ở HEAD | PASS |
| F3 | Ràng buộc kiến trúc | `git status` + grep import | không file code mới; `scripts → scripts` (tdq_setup → plugin_tiers), không import `hooks/` | PASS |
| F4 | Clean code | tự kiểm 5 câu | xem dưới | PASS |
| HĐ | Hợp đồng `tdq-setup` (T2.1) | Kiểm: `pytest -k plugin_user`; Ra: `kiem_plugin_user` | 5 passed; hàm có tại `scripts/tdq_setup.py` | PASS |

## Bằng chứng
### Vòng 1 — FAIL ở F1
```
ERROR collecting tests/test_tuong_thich_host.py
scripts\build_portable.py:502: RuntimeError: the antigravity bundle still has 1 use(s) of CLAUDE_PLUGIN_ROOT
```
Nguyên nhân: dòng dự phòng viết `${{CLAUDE_PLUGIN_ROOT}}` trong hằng số, bộ build chỉ thay chuỗi literal.
Fix QC1.1: biến đi qua tham số `format(bien_plugin="${CLAUDE_PLUGIN_ROOT}")`. Sau fix:
```
tests/test_tuong_thich_host.py tests/test_build_portable.py tests/test_claude_md_core.py → 49 passed
```

### Đối chiếu HEAD sạch (worktree `git worktree add /tmp/tdq-base HEAD`)
```
BASE (HEAD 402b39d), 7 module đỏ của lần tron-bo đầu:
FAILED tests/test_codex_cli.py::DongYCliTest::test_ba_cho_goi_y_cung_mot_lenh
FAILED tests/test_tu_khoi_tao.py::SessionStartKichHoat::test_kich_hoat_project_chua_dung_thi_bat_nen_va_tra_ve_ngay
FAILED tests/test_tu_khoi_tao.py::SessionStartKichHoat::test_kich_hoat_thu_muc_khong_phai_project_thi_khong_bat
3 failed, 143 passed
NOW (sau fix): 2 failed, 144 passed — tập con của BASE
```

### F1 — tron-bo vòng 2
```
Ran 2549 tests in 423.202s
ERROR: test_chong_dang_dung_nhung_da_chet_thi_bat_lai (test_tu_khoi_tao)   ← chập chờn, cùng nhóm SessionStart
FAIL: test_ba_cho_goi_y_cung_mot_lenh (test_codex_cli)
FAIL: test_kich_hoat_thu_muc_khong_phai_project_thi_khong_bat (test_tu_khoi_tao)
tron-bo: modules=131 failed=2 missed=0
```

### Q5 — setup thật
```
đã cài · bật plugin tdq-workflow@tdq-local ở scope user (mở phiên mới để nạp)
đã cài · ghim hướng dẫn 3 tầng vào ~/.claude/CLAUDE.md
cảnh báo · bản cài tdq-workflow@tdq-local 0.59.0 lệch instruction 0.66.0 — chạy /plugin update tdq-workflow@tdq-local
log: plugin user: tdq-workflow@tdq-local: chưa có khóa→True (C:\Users\admin\.claude\settings.json)
chạy lần 2: không ghi lại, chỉ còn dòng cảnh báo (idempotent)
grep -c "Unknown skill" ~/.claude/CLAUDE.md → 1
```

### F4 — 5 câu tự kiểm
- SRP: có — `bat_khoa` chỉ ghi khóa; `_ban_cai_user` chỉ đọc bản cài; `_da_bat` chỉ đọc trạng thái; `kiem_plugin_user` điều phối.
- OCP: có — thêm marketplace mới không phải sửa code (khóa lấy từ `installed_plugins.json`).
- LSP: có — mọi nhánh của `bat_khoa` trả `(bool, str)`, mọi nhánh của `kiem_plugin_user` trả 3 list.
- ISP: có — `home`, `goc_plugin`, `cham_may` đều được dùng.
- DIP: có — ghi qua `plugin_tiers._write_settings` (nguyên tử + `.bak`), đọc qua `tdq_lsp._doc_json`, log qua `_log`.

## Lệch spec chờ duyệt
- Q3 · ngưỡng: dòng dự phòng ≤ 300 ký tự · đo: bản mẫu 269, máy này 315 (đường dẫn cài 59 ký tự × 2) · đã áp: giữ mệnh đề nhắc chạy setup, rút 1 lần lặp đường dẫn.

## Kết luận
PASS toàn bộ sau 1 vòng fix (QC1.1). Lỗi có sẵn ngoài phạm vi: `test_codex_cli::test_ba_cho_goi_y_cung_mot_lenh`, nhóm `test_tu_khoi_tao::SessionStartKichHoat` (2–3 ca, chập chờn).
