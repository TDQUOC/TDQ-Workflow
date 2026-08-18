# BRIEF — Spec không giữ lệnh kiểm, băm bỏ vùng sổ sách

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## Nguyên văn

> vậy có cần fix ko? … A
>
> (A = mở request mới lane quick làm Đ2 + Đ1 trong report
> `docs/tdq/reports/2026-08-18-2050-spec-doi-sau-khi-duyet.md`, và commit hai file phân tích)

### Cách hiểu đầu tiên

Vá hai nguyên nhân gốc đông ca nhất của lỗi "spec đổi sau khi duyệt":

- **Đ2** — spec không ghi tên file test và cờ lệnh cụ thể nữa; §6 chỉ giữ ĐIỀU KIỆN PASS,
  còn lệnh kiểm do plan giữ. Plan không bị niêm phong sha nên sửa thoải mái.
- **Đ1** — `spec_sha256` băm phần NỘI DUNG, bỏ vùng sổ sách đầu file (Ngày/Bản/Trạng thái).

NGOÀI phạm vi user đã chốt: Đ3 (nới quyền tự duyệt) và Đ4 (dời cổng duyệt) — không làm.

## Hiểu & kiến thức

- Băm hiện tại: `sha256_file` trong `scripts/tdq_state.py` (băm cả file) · hook so lại ở
  `hooks/scripts/prompt_context.py` chạy mỗi `UserPromptSubmit`. Hai chỗ phải dùng CHUNG
  một hàm, không được chép luật băm ra hai nơi.
- 42/58 spec cũ có nêu `tests/test_*` — luật mới chỉ áp cho spec viết từ mốc ra luật trở
  đi, tra bằng ngày trong slug. Cố ý KHÔNG sửa 42 file cũ: request trước đã bị chê vì rải
  dòng miễn trừ lint vào 57 spec cũ, không lặp lại.
- `skills/tdq-build/references/qc.md` hiện dặn "sửa spec ở đây làm sha256 lệch → xin duyệt
  lại" — phải cập nhật cho khớp cơ chế mới.

Vòng scope: **BỎ** — phạm vi, mặt cần đạt và hai đề xuất đã chốt xong ở request phân tích
liền trước; không còn ẩn số làm đổi kết quả.

## Hỏi đáp

**Vòng chốt (2026-08-18)**

1. Fix hay không: **có**, nhưng chỉ Đ2 + Đ1.
2. Đ3/Đ4: **không làm** — Đ3 nới quyền tự duyệt (trái luật "chỉ NGƯỜI DÙNG duyệt"), Đ4 đổi thứ tự gate, lớn hơn phần nó cứu.
3. Spec cũ: **giữ nguyên**, luật mới chỉ áp cho spec mới.
