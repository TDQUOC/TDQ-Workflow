# REPORT — Trang trí khối chat cuối trả lời user (`2026-08-14-trang-tri-khoi-chat` · lane full · mode main · 18 task tick đủ)

**Đã làm:** P0 viết `scripts/scan_block_symbols.py` và chốt whitelist 6 ký hiệu bằng bằng
chứng chạy thật · P1 viết lại khuôn gốc `user-facing-block.md` (bảng 5 thành phần, 7 luật
trang trí, bảng ký hiệu, ví dụ trước/sau) · P2-P3 trang trí 8 file skill cùng 3 file
portable, không đụng 5 chỗ mã sinh chuỗi · P4-P5 mở rộng `tests/test_user_facing_block.py`
từ 4 lên 10 test · QC 3 vòng fix 6 lỗi do chính phép kiểm và agent QC lộ ra.

**Kết quả:** test 569 → 574 (280 subtest) · test của khuôn 4 → 10 · ký hiệu ngoài
whitelist trong khối in cho user 3 → 0 · file trỏ về khuôn gốc 8/11 → 10/11 (file thứ 11
là chính khuôn).

**Kiểm:** `python3 -m pytest tests/ -q` → `574 passed, 280 subtests passed`, 0 failed ·
`doc_lint.py` exit 0 · QC PASS 10/10 hạng mục DoD, cộng một lượt độc lập bằng agent
`tdq-qc-tester` (PASS 10/10, nêu 7 phát hiện: sửa 3 lỗi thật, 1 đính chính số liệu, 3 ghi
rõ vì sao không sửa).

**Đầu ra:** `skills/tdq-conventions/references/user-facing-block.md` (khuôn gốc) ·
`scripts/scan_block_symbols.py` · `tests/test_user_facing_block.py` ·
`docs/tdq/qc/2026-08-14-trang-tri-khoi-chat.md`.

**Giới hạn:** chỉ làm được **format**, không làm màu và cỡ chữ — app và extension không
dùng chung bộ dựng với terminal, mẫu số chung là markdown terminal dựng được. Luật cấm
emoji giữ nguyên; nới đúng phần ký hiệu Unicode, giới hạn trong 6 ký tự có bằng chứng.
Ký tự `▸` user chọn ở vòng interview bị loại vì grep toàn kho ra 0 kết quả. Whitelist chỉ
áp cho nội dung khối ``` , không áp cho văn xuôi hướng dẫn quanh khối.

**Git:** chưa commit phần thành quả. Có đúng một commit `4b3eba4` "Backup phase
analyze+spec" tạo trước khi build theo yêu cầu của user, không phải commit gỡ chặn.
