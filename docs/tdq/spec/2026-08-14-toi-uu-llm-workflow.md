# SPEC — Chấm toàn bộ workflow theo hướng LLM đọc & chi phí context

<!-- doc-lint: allow R10 — spec viết trước khi có luật ranh giới module -->

Ngày: 2026-08-14 · Bản: 1.0 · Brief: ../brief/2026-08-14-toi-uu-llm-workflow.md · Lane: full
Trạng thái: CHỜ DUYỆT

## 1. Mục tiêu & phạm vi

- Mục tiêu: chấm từng phần của bộ workflow TDQ (`skills/` 28 file · `hooks/` 6 file ·
  `agents/` 3 file) theo một thang đo 6 tiêu chí có lệnh kiểm, chỉ ra chỗ phí bằng số đo
  thật, rồi giao một bộ đề xuất sửa copy dán được. Hai ràng buộc cứng: **không luật nào
  biến mất** và **mức chi tiết đủ cho model hạng thấp vẫn chạy đúng**.
- Trong phạm vi:
  - Thang chấm 6 tiêu chí, mỗi tiêu chí một lệnh đo.
  - Bảng chấm từng file của `skills/`, `hooks/`, `agents/`.
  - Danh sách chỗ phí, mỗi chỗ kèm số đo và `file:line`.
  - Đề xuất sửa: mỗi đề xuất có nguyên văn nháp, chỗ chèn `file:mục`, mức chi phí,
    lệnh kiểm, và hai cột tác động: token và độ tuân thủ của model hạng thấp.
  - Bảng đối chiếu luật trước/sau chứng minh 0 luật mất.
  - Ba gói theo chi phí cộng đúng một khuyến nghị.
  - Nháp mở rộng `scripts/context_surface.py` để lần sau tự chấm lại (chỉ nháp, không code).
- NGOÀI phạm vi (chép từ brief `### Phạm vi đã chốt`):
  - **Thực thi bản sửa** — request này dừng ở tài liệu đề xuất. Cấm sửa file trong
    `skills/`, `hooks/`, `agents/`, `scripts/`.
  - `scripts/` (4.759 dòng), `portable/` (12 file), `tests/` — không chấm.
  - Bản "chỉ báo cáo suông" (liệt kê chỗ chưa tối ưu mà không đề xuất cách sửa).
  - Mốc số bắt buộc kiểu "phải giảm ≥ 25% token" — user chốt không đặt mốc.

## 1b. Lộ trình

| Bước/phase | Chạy? | Vì sao |
|---|---|---|
| Research web | CÓ — đã xong | có ẩn số ngoài: chuẩn viết skill, cách viết cho model nhỏ |
| Interview | CÓ — 2 vòng, đã xong | scope + chi tiết, không còn câu làm đổi kết quả |
| Spec → plan → implement → report | CÓ | khung bất biến |
| QC độc lập bằng agent | BỎ | đầu ra là một file Markdown, mọi dòng DoD kiểm bằng lệnh — thêm agent là thêm vòng, không thêm bảo đảm |
| Chia sub-agent để implement | BỎ | mọi task ghi vào cùng một file, tách ra chỉ gây xung đột ghi |
| Sửa `skills/`, `hooks/`, `agents/` | BỎ | user chốt dừng ở bản đánh giá + đề xuất |
| `graphify extract` cuối turn | BỎ | không file mã nguồn nào đổi |

## 2. Đầu ra cụ thể

Đặt `F = docs/tdq/knowledge/2026-08-14-toi-uu-llm-workflow.md`.

| # | Đầu ra | Đường dẫn/vị trí | Đo "xong" bằng |
|---|---|---|---|
| 1 | Thang chấm 6 tiêu chí, mỗi tiêu chí một lệnh đo | `$F` mục `## Thang chấm` | `grep -c "^| R[1-6] " $F` = 6 |
| 2 | Bảng chấm 28 file `skills/` | `$F` mục `## Bảng chấm skills` | số dòng bảng = số file `.md` trong `skills/` |
| 3 | Bảng chấm 6 hook + 3 agent | `$F` mục `## Bảng chấm hooks & agents` | `grep -c "^| hooks/\|^| agents/" $F` = 9 |
| 4 | Danh sách chỗ phí, mỗi chỗ có số đo + `file:line` | `$F` mục `## Chỗ phí` | mỗi dòng `| F<n> |` có ít nhất một số và một `file:` |
| 5 | Đề xuất sửa, khuôn 7 trường | `$F` mục `## Đề xuất` | mỗi khối `### Đ<n>` đủ 7 trường |
| 6 | Bảng đối chiếu luật trước/sau | `$F` mục `## Đối chiếu luật` | tổng luật cột "sau" ≥ cột "trước" |
| 7 | Ba gói + 1 khuyến nghị | `$F` mục `## Gói` | `grep -c "^### Gói" $F` = 3 và `grep -c "^Khuyến nghị: " $F` = 1 |
| 8 | Nháp công cụ đo lại | `$F` mục `## Công cụ đo lại` | có khối lệnh chạy được, nêu rõ cột thêm vào |
| 9 | Nguồn | `$F` mục `## Nguồn` | ≥ 6 URL |

## 3. Cách tiếp cận & lý do

- Chọn: đo trước, chấm sau, đề xuất cuối. Mọi con số lấy bằng lệnh chạy thật
  (`scripts/context_surface.py`, `wc`, `grep`, bấm giờ hook), không ước lượng bằng cảm
  tính. Thang chấm định nghĩa trước khi nhìn kết quả để tránh chấm chiều theo ý mình.
- Vì: repo đã qua 5 vòng tối ưu trước (knowledge 2026-08-04 ×2, 2026-08-05 ×3, 2026-08-08),
  nên phần dễ đã bị cắt; chỉ có số đo mới phân biệt được "còn phí thật" với "đã cắt rồi".
  Công cụ `context_surface.py` sẵn có đã phân tầng nạp đúng theo mô hình chi phí thật của
  skill (chỉ `description` luôn nạp, thân nạp khi gọi, reference đọc khi cần).
- Xử lý xung đột hai mặt (user chốt ưu tiên tuân thủ): mỗi đề xuất phải khai **hai cột
  tác động** — token và độ tuân thủ model hạng thấp. Đề xuất làm giảm token nhưng hạ độ
  tuân thủ thì bị loại, trừ khi bù được bằng checklist hoặc định dạng đầu ra rõ hơn.
  Căn cứ: chuẩn viết skill nói mức chi tiết phải nhắm vào model yếu nhất được hỗ trợ, và
  tài liệu prompt cho model nhỏ nói model nhỏ cần chỉ dẫn **chi tiết hơn**, không ngắn hơn.
- Đã loại: chấm bằng cảm nhận đọc rồi xếp hạng — vì không tái lập được, và lần sau không
  so được tiến bộ. Đã loại: dùng jscpd quét trùng lặp trên `.md` — trùng lặp luật ở đây là
  trùng **ý**, không trùng chuỗi, jscpd không bắt được.

## 3b. Năng lực & công cụ

| Skill | Nguồn | Phán quyết | Dùng ở đâu / Lý do loại |
|---|---|---|---|
| tdq-intake, tdq-spec, tdq-plan, tdq-build, tdq-conventions, tdq-status | plugin:tdq-workflow | NỀN | vừa là khung chạy request, vừa là đối tượng bị chấm |
| tavily-search | user | DÙNG | đã chạy 2 truy vấn lấy chuẩn viết skill và cách viết cho model nhỏ, kết quả ở `docs/tdq/research/` |
| mem0-memory | user | DÙNG | cuối request ghi đúng 1 fact về thang chấm và gói khuyến nghị |
| graphify | user | KHÔNG | spec §3 đã chọn cách khác tốt hơn: số liệu lấy trực tiếp bằng `context_surface.py` và `wc`/`grep`; đồ thị không chứa `.md` |
| sonar-duplication | plugin:sonarqube | KHÔNG | spec §3 đã chọn cách khác tốt hơn: trùng lặp cần bắt là trùng ý, không trùng chuỗi |
| Đã xét 180 skill khác | user/plugin/built-in | KHÔNG | khác lĩnh vực |

## 4. Yêu cầu bắt buộc

- Log service: BỎ — request chỉ tạo một file Markdown, không có file mã nguồn chạy được.
- Không placeholder, không TODO stub. Mọi con số trong `$F` phải là kết quả một lệnh đã
  chạy thật; cấm ghi số ước lượng mà không nói rõ là ước lượng.
- Mỗi đầu ra ở §2 có ít nhất một hạng mục QC ở §6 kiểm bằng lệnh.
- Mọi đề xuất phải trích **nguyên văn dòng luật bị thay** khi nó sửa một luật đang có.

## 5. Ràng buộc & rủi ro

| Rủi ro | Ảnh hưởng | Cách giảm |
|---|---|---|
| Đề xuất cắt chữ làm mất một luật mà không ai nhận ra | Workflow đổi behavior — đúng thứ user cấm | Bảng đối chiếu luật ở §2 đầu ra 6: đếm luật trước/sau theo từng file, cột "sau" không được nhỏ hơn |
| Cắt cho gọn khiến model hạng thấp không đủ chỉ dẫn | Model rẻ chạy sai quy trình, mất chất lượng output | Mỗi đề xuất khai cột "tác động model hạng thấp"; đề xuất làm xấu cột này bị loại |
| Chấm lại chỗ 5 vòng trước đã cắt rồi | Tốn công, đề xuất trùng | Đọc 2 knowledge gần nhất trước khi viết mục `## Chỗ phí`, ghi rõ đề xuất nào là mới |
| Bảng chấm 37 dòng phình thành tài liệu không ai đọc | Đề xuất không được áp dụng | Bảng chỉ 5 cột; phần diễn giải nằm ở `## Chỗ phí`, tối đa 8 mục |
| Vô tình sửa file trong `skills/`/`hooks/`/`agents/` | Vượt phạm vi user chốt | Q11 kiểm `git status --porcelain -- skills hooks agents scripts` phải rỗng |
| Thang chấm bịa tiêu chí không đo được | Điểm số vô nghĩa | Mỗi tiêu chí R1–R6 bắt buộc có cột "lệnh đo" chạy được |

## 6. QC & Definition of Done

| # | Hạng mục kiểm | Lệnh/cách kiểm | Điều kiện PASS |
|---|---|---|---|
| Q1 | Đủ 9 mục chính | `grep -c "^## " $F` | = 9 |
| Q2 | Thang chấm đủ 6 tiêu chí có lệnh đo | `grep -c "^| R[1-6] " $F` | = 6, mỗi dòng có ô lệnh khác rỗng |
| Q3 | Bảng chấm phủ hết `skills/` | so số dòng `| skills/` với `find skills -name "*.md" | wc -l` | bằng nhau (28) |
| Q4 | Bảng chấm phủ hết hook + agent | `grep -c "^| hooks/\|^| agents/" $F` | = 9 |
| Q5 | Chỗ phí có số đo và vị trí | mỗi dòng `| F<n> |` chứa ≥ 1 chữ số và chuỗi `file:` hoặc đường dẫn | 100% dòng đạt |
| Q6 | Đề xuất đủ khuôn 7 trường | 7 lệnh `grep -c "^- <trường>:" $F` | 7 lệnh ra cùng một số = số khối `### Đ` |
| Q7 | Đối chiếu luật không mất luật | cột "luật sau" ≥ cột "luật trước" ở mọi dòng | 0 dòng vi phạm |
| Q8 | Ba gói + 1 khuyến nghị | `grep -c "^### Gói" $F` và `grep -c "^Khuyến nghị: " $F` | = 3 và = 1 |
| Q9 | Công cụ đo lại chạy được | lệnh trong mục `## Công cụ đo lại` chạy thử | exit code khác 127 |
| Q10 | Nguồn đủ | `grep -c "^- https\?://" $F` | ≥ 6 |
| Q11 | Không vượt phạm vi + test còn xanh | `git status --porcelain -- skills hooks agents scripts` và `python3 -m pytest tests/ -q` | rỗng, và không có `failed`, số test ≥ 563 |
| Q12 | Lint tài liệu | `python3 scripts/doc_lint.py $F <spec> <plan>` | exit 0 |

DoD: đủ 12 hạng mục Q1–Q12 PASS, `$F` tồn tại với đủ 9 mục, plan 100% task `[x]`, report
đã viết, và `git status` chứng minh không file nào của `skills/`, `hooks/`, `agents/`,
`scripts/` bị sửa.

## 7. Câu hỏi còn mở

(rỗng)
