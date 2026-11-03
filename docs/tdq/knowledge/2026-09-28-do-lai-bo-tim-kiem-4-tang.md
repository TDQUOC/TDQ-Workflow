# KNOWLEDGE — đo lại bộ tìm kiếm 4 tầng trên MỘT repo code thật

Ngày: 2026-09-28 · Nguồn: đo trực tiếp trong phiên, hai đối tượng: repo này và
`C:\Users\admin\Documents\claudecodeui` (995 file, 468 `.ts` + 301 `.tsx`)

## 1. Vấn đề cốt lõi

Mọi số đo của luật `uu-tien-tim-kiem.md` cho tới nay đều lấy trên **chính repo TDQ-Workflow** —
một repo mà phần lớn nội dung là Markdown và skill. Đo graphify ở đây rồi kết luận về công cụ là
sai phương pháp, và tôi đã mắc đúng lỗi đó: từ chỗ đồ thị TDQ chỉ có 12% cạnh xuyên file, tôi
viết vào report rằng "graphify không làm được blast radius". Đo lại trên một project code thật
thì kết luận **đảo ngược**.

## 2. Số đo — hai repo, cùng một công cụ

| Chỉ số | TDQ-Workflow (doc/skill) | claudecodeui (TS/React) |
|---|---|---|
| node / cạnh | 2415 / 5139 | 6258 / 16121 |
| cạnh trong cùng file | 88% | 45% |
| **cạnh xuyên file** | **12%** | **54%** |
| `calls` xuyên file | 100 | **981** |
| `imports_from` | 8 | **3605** |
| `references` / `re_exports` / `dynamic_import` | 0 / 0 / 0 | 606 / 261 / 57 |
| `implements` / `inherits` | 0 / 14 | 22 / 12 |
| **`rationale_for`** | **1035** | **2** |
| cạnh `hooks/` → `scripts/` | **0** | — |
| thời gian dựng lại | — | **16.5 s / 917 file** |

Hai mặt của cùng một công cụ: repo code thật cho **bản đồ phụ thuộc**; repo tài liệu nặng cho
**liên kết code ↔ lý do**. Không repo nào cho cả hai.

## 3. Phép thử độ chính xác — `affected AppError` so với grep

| | Kết quả |
|---|---|
| graphify `affected --depth 1` | **60 file, 0 dương tính giả** |
| grep `-rl "AppError"` | 66 file |
| 6 file chênh | 2 file chỉ nhắc trong **comment**, 1 file khai `AppErrorOptions` (**tên khác**), 1 file là **nơi định nghĩa** `AppError` (không phải nơi bị ảnh hưởng) |

Tức grep nhiễu ~9% ở câu hỏi này; graphify không nhiễu. Và `--depth 2` mở từ 134 lên 207 node —
câu hỏi mà grep không trả lời được ở bất kỳ giá nào.

## 4. Chi phí token, đo bằng ký tự đầu ra

| Câu hỏi | Công cụ rẻ nhất | Chi phí |
|---|---|---|
| "file nào nhắc tới X" | `grep -rl` | ~2.5 KB — **grep thắng** |
| "ai bị ảnh hưởng, kèm quan hệ + dòng" | `graphify affected --depth 1` | **12.6 KB** so với `grep -rn` **42.9 KB** → rẻ hơn **3.4×** |
| "vỡ lan 2 bậc" | `graphify affected --depth 2` | 19.4 KB · không công cụ nào khác làm được |
| "hub kiến trúc" | `graphify god-nodes` | **251 byte** cho 8 hub |
| "kiểu trả về / diagnostics" | `mcp__lsp__*` | graphify **không có** khái niệm kiểu; node chỉ mang `label`, `source_file`, `source_location` |

## 5. Quyết định đã chốt

| # | Quyết định | Lý do |
|---|---|---|
| K1 | Không kết luận về công cụ tìm kiếm khi chỉ đo trên repo TDQ | Đo hai repo cho hai kết quả trái ngược; một mẫu là không đủ |
| K2 | Mọi số đo mới của luật tìm kiếm phải ghi **đo trên repo nào** | Thiếu dòng đó là số đo vô nghĩa với người đọc sau |
| K3 | graphify chỉ lãi token khi đồ thị MỚI | Đồ thị TDQ cũ 8 ngày, 34% node (845/2415) trỏ vào `antigravity_portable/` đã xoá; hệ quả đo được: `explain load` nhập nhằng 4 node, phải dùng id đầy đủ mới ra — mất thêm 3 lượt truy vấn |
| K4 | Bỏ thói quen `tdq_finish --skip-graphify` | Chính nó làm đồ thị cũ: hơn 10 lần skip trong một phiên |
| K5 | graphify là **bản đồ**, không phải **type checker** | Không kiểu, không diagnostics, `implements` chỉ 22 cạnh trên 16121 |

## 6. Chỗ cần nhớ khi đọc lại

`rationale_for` 1035 so với 2 là chỉ dấu rõ nhất: ở repo này graphify nối code với lý do trong
tài liệu, thứ không công cụ nào khác trong bộ làm được — nhưng ở project code thật thì nó gần như
không tồn tại. Giá trị của graphify **thay đổi theo loại repo**, nên câu "graphify có đáng không"
chỉ trả lời được khi kèm tên repo.
