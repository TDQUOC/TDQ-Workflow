# QC — 2026-08-13-ra-soat-toi-uu-llm

Chạy lúc 2026-08-13, mode `main`, trên máy đang chạy phiên Claude Code.
Report: ../reports/2026-08-13-ra-soat-toi-uu-llm.md

| # | Hạng mục | Lệnh | Kết quả | Phán quyết |
|---|---|---|---|---|
| Q1 | Báo cáo sạch lint | `python3 scripts/doc_lint.py docs/tdq/reports/2026-08-13-ra-soat-toi-uu-llm.md` | exit 0, không in lỗi | PASS |
| Q2 | Báo cáo không phình | `wc -l` báo cáo | `117` (trần 120) | PASS |
| Q3 | Bảng bề mặt đủ file | `awk '/^## Đo bề mặt/,/^## Tốc độ hook/' <report> \| grep -c "^\| "` | `36` (trần dưới 35) | PASS |
| Q4 | Script đo chạy được | `python3 scripts/context_surface.py` | exit 0, in bảng 58 dòng + 3 dòng TỔNG | PASS |
| Q5 | Test script đo | `python3 -m pytest tests/test_context_surface.py -q` | `15 passed in 1.05s` | PASS |
| Q6 | Đo đủ hook | `awk '/^## Tốc độ hook/,/^## Trùng lặp/' <report> \| grep -c "ms"` | `9` (trần dưới 6) | PASS |
| Q7 | Mọi dòng xếp hạng có cột luật bị đụng | Đếm cột 4 dòng xếp hạng | cả 4 dòng đều `NF=7`, không ô nào rỗng | PASS |
| Q8 | Không sửa file sản phẩm | `git status --short` | chỉ `scripts/context_surface.py`, `tests/test_context_surface.py`, tài liệu TDQ của request, và file sổ sách do hook sinh (`docs/tdq/STATE.md`, working log, `graphify-out/`) | PASS |
| Q9 | Toàn bộ suite xanh | `python3 -m pytest tests/ -q` | `535 passed, 206 subtests passed in 34.23s` | PASS |

## Q10 — Bằng chứng phân loại 5 nhóm (T3.2)

Gán nhóm cho từng dòng bằng luật máy, xét theo thứ tự: (1) dòng trùng nguyên văn với
một file khác trong bộ → `trùng chỗ khác`; (2) dòng trong khối ``` hoặc dòng `➤` →
`khuôn mẫu`; (3) dòng chứa "vd"/"ví dụ"/"e.g" → `ví dụ`; (4) frontmatter, tiêu đề, dòng
giải thích lý do → `nền tảng`; (5) còn lại → `luật lõi`.

| skill | luật lõi | nền tảng | ví dụ | khuôn mẫu | trùng chỗ khác | tổng | `wc -c` |
|---|---|---|---|---|---|---|---|
| tdq-build | 3.312 | 485 | 0 | 458 | 3.570 | 7.825 | 7.825 |
| tdq-conventions | 4.457 | 783 | 200 | 48 | 2.039 | 7.527 | 7.527 |
| tdq-intake | 4.189 | 331 | 0 | 95 | 2.529 | 7.144 | 7.144 |
| tdq-plan | 3.385 | 263 | 111 | 748 | 1.641 | 6.148 | 6.148 |
| tdq-spec | 1.938 | 374 | 113 | 481 | 766 | 3.672 | 3.672 |
| tdq-status | 1.618 | 255 | 0 | 143 | 0 | 2.016 | 2.016 |

Tổng khớp `wc -c` sai số 0% ở cả 6 file — trần cho phép là 2%.

## Q11 — Log service (T5.1)

`bash -c 'python3 scripts/context_surface.py --quiet 2>&1 >/dev/null | wc -l'` → `0`.
`bash -c 'python3 scripts/context_surface.py --quiet 2>/dev/null | wc -l'` → `64`.
Bỏ `--quiet` thì stderr có dòng `[2026-08-13T21:02:56+07:00] bắt đầu quét bề mặt`.
Kết luận: log bật mặc định, có timestamp ISO, ra stderr, `--quiet` chỉ tắt log chứ
không tắt bảng. PASS.

Lưu ý khi chạy lại: zsh bật MULTIOS nên `2>&1 >/dev/null` KHÔNG chặn stdout như ở bash.
Phép kiểm này phải chạy trong `bash -c`, nếu không sẽ đọc nhầm bảng thành log.

DoD: 9/9 hạng mục PASS, không hạng mục nào phải vào vòng fix.
