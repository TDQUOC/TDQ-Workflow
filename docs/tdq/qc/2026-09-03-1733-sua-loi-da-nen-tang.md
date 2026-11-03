# QC — Sửa bốn lỗi đa nền tảng P1–P4
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md
Plan: ../plan/2026-09-03-1733-sua-loi-da-nen-tang.md · 13 hạng mục DoD + 4 hạng mục tự thêm

Không có máy Windows. Mọi hạng mục nói về Windows đều nghiệm thu bằng THAM SỐ giả lập, và câu
chữ dừng ở mức "hàm cho ra đúng tên lệnh mong đợi" — không hạng mục nào nói phần mềm đã chạy
được trên Windows.

| # | Hạng mục | Lệnh | Kết quả |
|---|---|---|---|
| Q1 | Hàm chọn tên lệnh đúng ba hệ | `pytest -k tien_to` | PASS — `win32`→`py -3`, `darwin`/`linux`→`python3` |
| Q2 | Codex + agy không còn `python3` viết cứng | `pytest -k sinh_command` | PASS — kể cả ca quét mã nguồn tìm dòng `"command"` mang `python3` |
| Q3 | Sinh lại `hooks/hooks.json` bất biến | `pytest -k bat_bien` | PASS — lần hai báo `already correct`, file không đổi |
| Q4 | Hệ đích Windows ra `py -3` | `build_portable.py --sinh-hook-claude --he-dich win32` | PASS — `"py -3 \"${CLAUDE_PLUGIN_ROOT}/hooks/scripts/session_start.py\""` |
| Q5 | Cổng gác hết dương tính giả | `pytest -k cong_gac_khong_no_sai` | PASS — và chạy thật trên bundle agy không còn dòng NOTE `unexpanded` |
| Q6 | Cổng gác nổ đúng ca máy khác | `pytest -k cong_gac_no_dung` | PASS — bundle giả với `/Users/nguoikhac/...` sinh cảnh báo `another home folder` |
| Q7 | Chuẩn hoá dòng `Test:` | `pytest -k chuan_hoa` | PASS — `python3 …` đổi, `pytest`/`mypython3 x`/`python -m` giữ nguyên |
| Q8 | Toán tử shell cảnh báo mà vẫn chạy | `pytest -k canh_bao_shell` | PASS — trả cảnh báo, lệnh vẫn nguyên vẹn |
| Q9 | README agy có cảnh báo gắn máy dựng | `pytest -k readme_agy` | PASS |
| Q10 | Ba bundle CLEAN | `tdq_checkportable.py check --root <từng bundle>` | PASS — 93 / 143 / 86 file khớp manifest |
| Q11 | Bộ test riêng xanh toàn bộ | `pytest tests/test_sua_da_nen_tang.py -q` | PASS — 17 ca, 15 subtest |
| Q12 | `doc_lint` sạch | `doc_lint.py <brief, spec, plan, README agy>` | PASS — 0 violation |
| Q13 | Suite không vượt mốc đỏ | `pytest -q` | PASS — 100 đỏ, đúng mốc cũ; xanh tăng 1531 → 1548 |

## Hạng mục tự thêm

| # | Hạng mục | Kết quả |
|---|---|---|
| QC-F1 | `hooks/hooks.json` trong repo KHÔNG bị bẩn sau mọi thao tác | PASS — `git status hooks/hooks.json` rỗng; lệnh sinh lại là no-op trên POSIX |
| QC-F2 | Bundle agy dựng trên máy này vẫn mang `python3` (không tự đổi sang `py -3` sai chỗ) | PASS — `command` bắt đầu `python3 /Users/truongdinhquoc/...` |
| QC-F3 | Cổng gác báo được `hooks.json` hỏng cú pháp JSON thay vì im lặng | PASS — ca `hong_cu_phap` xanh |
| QC-F4 | Không đụng `hooks/scripts/*.py` như spec §2b cấm | PASS — `git status` không liệt kê file nào trong đó |

## Ghi chú

`antigravity_portable/README.md` là file SINH RA từ hằng `README_AGY` trong `build_portable.py`.
Lần sửa đầu tôi sửa thẳng file sinh ra và lệnh build kế tiếp ghi đè mất — đã sửa lại đúng chỗ là
hằng nguồn, rồi dựng lại. Đây là lý do Q9 phải kiểm sau khi dựng lại chứ không kiểm ngay sau khi
sửa.
