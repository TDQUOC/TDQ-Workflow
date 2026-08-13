# Brief — Đổi tên lane quick/full thành "pipeline nhanh / chuyên sâu"

Ngày: 2026-08-12

## Nguyên văn

> okay hãy thử đi phan tích toàn bộ workflow này xem có thể rename lane quick/full thành
> pipeline nhanh/chuyên sâu có đucojw không, do tôi muốn đổi nó lại để nó dễ thích nghi
> với người dùng

### Cách hiểu đầu tiên

- Mục tiêu: từ vựng người dùng gặp phải dễ hiểu với người Việt — "pipeline nhanh" và
  "pipeline chuyên sâu" thay cho "lane quick" / "lane full".
- Phạm vi đoán: mọi chỗ in ra cho user (câu hỏi chọn lane, status line, thông điệp hook,
  tài liệu skill), và tuỳ quyết định — cả định danh nội bộ (giá trị `lane` trong state,
  tham số CLI, khoá `quick_*`).
- Chỗ chưa rõ: đổi cả định danh hay chỉ đổi nhãn hiển thị; tham số CLI có dấu tiếng Việt
  hay không dấu; 70 tài liệu plan/spec cũ có viết lại không; có cần đường tương thích
  ngược cho state đang tồn tại không.

### Đo sơ bộ trước khi hỏi

Số lần xuất hiện từ khoá `quick`/`full` (đếm dòng, `grep -rIn`):

| Vùng | Số dòng | Tính chất |
|---|---|---|
| `docs/` | 1078 | phần lớn là tài liệu lịch sử (70 file plan/spec/qc cũ) |
| `tests/` | 168 | khoá cứng giá trị và thông điệp |
| `skills/` | 62 | văn bản hướng dẫn — chỗ user đọc nhiều nhất |
| `scripts/` | 50 | `VALID_LANES`, `PHASE_TABLE`, khoá `quick_*`, CLI |
| `portable/` | 41 | bản tài liệu mang đi |
| `hooks/` | 16 | thông điệp nhắc/chặn |
| `.claude-plugin/` | 1 | mô tả |

49 file mã/tài liệu sống (không kể `docs/tdq/` lịch sử) có chứa từ khoá. Tên 6 skill
`tdq-*` KHÔNG chứa `quick`/`full` — đây là điểm thuận lợi lớn.

Định danh thật sự bị khoá cứng (23 dòng ở `scripts/` + `hooks/` + `.claude-plugin/`):
`VALID_LANES = {"quick", "full"}`, `PHASE_TABLE["quick"]`, `APPROVE_TARGETS`, các khoá
state `quick_approved`, `quick_approved_at`, `quick_approved_by`, `quick_qc_skipped`,
tham số CLI `init <slug> quick|full` và `approve quick`, tên file
`skills/tdq-intake/references/quick-lane.md`.

## Hiểu & kiến thức

### Chốt sau interview

| # | Điểm | Chốt |
|---|---|---|
| 1 | Cặp từ tiếng Anh | `express` (nhanh) / `deep` (chuyên sâu) |
| 2 | Định danh nội bộ | KHÔNG đổi — `lane` vẫn là `quick`/`full`, giữ nguyên 4 khoá `quick_*`, không migrate state, không đụng 168 dòng test |
| 3 | 70 tài liệu cũ trong `docs/tdq/` | Giữ nguyên, là hồ sơ lịch sử |
| 4 | Cặp từ tiếng Việt | `chế độ nhanh` / `chế độ chuyên sâu` |

Nhãn hiển thị hợp nhất: **`chế độ nhanh (express)`** và **`chế độ chuyên sâu (deep)`**.

### Vì sao chỉ đổi nhãn

Tách "nhãn người đọc" khỏi "định danh máy đọc" là cách rẻ nhất: rủi ro hồi quy gần bằng
không, không cần migrate `docs/tdq/state.json` đang tồn tại, không phá test. Tiền lệ ngành:
AWS Step Functions đặt hai loại workflow là **Standard** và **Express** — `express` đã mang
nghĩa "đường nhanh" quen thuộc với người làm kỹ thuật.

### Điểm thiết kế còn mở → giải trong spec

Câu duyệt hiện tại người dùng gõ là `duyệt quick`. Nếu nhãn dạy người dùng nói "chế độ
nhanh" mà bộ nhận vẫn chỉ hiểu `quick` thì nhãn mới phản tác dụng. Hai regex liên quan:
`hooks/scripts/prompt_context.py:26` và `hooks/scripts/bash_gate.py:42`. Hướng xử lý đề
xuất: thêm **bí danh** (`nhanh`, `express`) bên cạnh `quick`, giữ `quick` chạy như cũ.

### Lộ trình

| Bước/phase | Chạy? | Vì sao |
|---|---|---|
| Research web | BỎ | Đã có tiền lệ AWS Step Functions; việc này là đổi chữ trong repo, không phụ thuộc kiến thức ngoài |
| Interview | XONG | 4 câu, đã chốt ở bảng trên |
| QC độc lập (agent) | BỎ | Thay đổi bề mặt chữ + bí danh, QC bằng full-suite + grep là đủ và kiểm được |

## Hỏi đáp

| # | Hỏi | Đáp |
|---|---|---|
| 1 | Cặp từ tiếng Anh chuyên nghiệp hơn `quick`/`full`? | **B** — `express` / `deep` |
| 2 | Có đổi định danh nội bộ (giá trị `lane`, khoá state, tham số CLI)? | **A** — không đổi |
| 3 | Có viết lại 70 tài liệu `docs/tdq/` cũ? | **A** — giữ nguyên |
| 4 | Cặp từ tiếng Việt? | **C** — `chế độ nhanh` / `chế độ chuyên sâu` |
