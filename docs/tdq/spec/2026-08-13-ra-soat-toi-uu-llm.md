# SPEC — Rà soát mức tối ưu cho LLM của tdq-workflow

Ngày: 2026-08-13 · Bản: 1.0 · Brief: ../brief/2026-08-13-ra-soat-toi-uu-llm.md · Lane: full
Trạng thái: CHỜ DUYỆT

## 1. Mục tiêu & phạm vi

- Mục tiêu: đo và chấm toàn bộ bề mặt `tdq-workflow` theo tiêu chí "viết cho LLM đọc",
  rồi ra một báo cáo xếp hạng cơ hội tiết kiệm kèm số đo thật. Mọi khuyến nghị phải giữ
  nguyên 100% hành vi và 100% luật hiện có.
- Trong phạm vi: 6 `SKILL.md`, 20 file `references/`, 3 agent, 6 hook script,
  `portable/workflow/`, `docs/claude-md-mau.md`, `.claude-plugin/plugin.json`,
  thời gian chạy của từng hook.
- NGOÀI phạm vi: sửa file thật theo khuyến nghị (user chốt "chỉ báo cáo") · đổi hành vi
  workflow · bỏ hay nới bất kỳ luật nào · tối ưu mã Python không nằm trên đường context ·
  chi phí của MCP ngoài workflow (Excalidraw, Figma…).

## 1b. Lộ trình

| Bước/phase | Chạy? | Vì sao |
|---|---|---|
| Research web | CÓ (xong) | Đã có `docs/tdq/research/2026-08-13-ra-soat-toi-uu-llm.md` |
| Interview | CÓ (xong) | Vòng 1 đã chốt 3 câu, không còn câu làm đổi kết quả |
| Spec + plan | CÓ | Khung bất biến |
| Implement | CÓ | Việc "làm" ở đây là đo đạc và viết báo cáo, không sửa file sản phẩm |
| QC độc lập (agent) | BỎ | Đầu ra là báo cáo; DoD tự kiểm được bằng lệnh |
| Chia subagent | BỎ | Đọc tài liệu tập trung, chia ra tốn context hơn |

## 2. Đầu ra cụ thể

| # | Đầu ra | Đường dẫn/vị trí | Đo "xong" bằng |
|---|---|---|---|
| 1 | Báo cáo rà soát, xếp hạng cơ hội theo mức tiết kiệm và rủi ro | `docs/tdq/reports/2026-08-13-ra-soat-toi-uu-llm.md` | File tồn tại, `doc_lint` exit 0, có bảng xếp hạng |
| 2 | Bảng đo bề mặt: từng file, số ký tự, tầng nạp, tần suất vào context | mục `## Đo bề mặt` của đầu ra 1 | Đủ 35 file trong phạm vi, không dòng nào thiếu cột |
| 3 | Bảng đo tốc độ hook: mỗi hook một con số mili-giây | mục `## Tốc độ hook` của đầu ra 1 | Đủ 6 hook, mỗi hook đo ≥ 5 lần lấy trung vị |
| 4 | Danh sách trùng lặp chéo file, kèm vị trí cả hai bản | mục `## Trùng lặp` của đầu ra 1 | Mỗi mục có ≥ 2 đường dẫn kèm số dòng |
| 5 | Bản vá mẫu cho 2–3 cơ hội nặng nhất, dạng khối trích trong báo cáo | mục `## Bản vá mẫu` của đầu ra 1 | Có 2–3 khối, mỗi khối nêu rõ trước/sau và luật nào được giữ |
| 6 | Script đo lặp lại được, để lần sau đo cùng cách | `scripts/context_surface.py` | Chạy một lệnh in ra bảng đầu ra 2, exit 0 |
| 7 | Test cho script đo | `tests/test_context_surface.py` | `python3 -m pytest tests/test_context_surface.py -q` exit 0 |

## 3. Cách tiếp cận & lý do

- Chọn: bắt chước quy trình 2 tầng của *SkillReducer* nhưng dừng ở bước **chẩn đoán**.
  Tầng 1 soi `description` (nằm trong mọi phiên). Tầng 2 phân loại nội dung thân file
  thành 5 nhóm (luật lõi · nền tảng · ví dụ · khuôn mẫu · phần thừa) rồi chỉ ra nhóm nào
  đáng chuyển sang đọc-khi-cần.
- Vì: nghiên cứu đó báo giảm 39% thân file và 26,8% chi phí mỗi lần gọi skill, và quan
  trọng hơn, nó có sẵn hai cổng chứng minh "không mất luật" — đúng ràng buộc user đặt ra.
  Nguồn: `docs/tdq/research/2026-08-13-ra-soat-toi-uu-llm.md`.
- Đã loại: nén thẳng bằng model rồi so kết quả — vì không chứng minh được luật nào mất.
- Đã loại: chỉ dựa vào `token_audit.py` — vì công cụ đó đo tool output đã xảy ra, không
  đo được phần tài liệu nằm sẵn trong context.

## 3b. Năng lực & công cụ

| Skill | Nguồn | Phán quyết | Dùng ở đâu / Lý do loại |
|---|---|---|---|
| `tavily-primary` | plugin:tavily | DÙNG | Research đã chạy, kết quả ở file research (mcp) |
| `graphify` | user | DÙNG | Hỏi quan hệ file khi lập bảng trùng lặp (đầu ra 4) |
| `mem0-memory` | user | DÙNG | Ghi lại kết luận kiến trúc sau khi chốt báo cáo (mcp) |
| `tdq-intake` | plugin:tdq-workflow | NỀN | Khung đang chạy request này |
| `tdq-spec` | plugin:tdq-workflow | NỀN | Khung đang chạy request này |
| Đã xét 40 skill khác | user/plugin/built-in | KHÔNG | khác lĩnh vực |

## 4. Yêu cầu bắt buộc

- Log service: có runtime (đầu ra 6 là script mới) → `scripts/context_surface.py` phải
  dùng đúng lớp log sẵn có của repo: timestamp, in ra stderr, tắt được bằng cờ.
- Không placeholder: mọi con số trong báo cáo phải là số đo thật, kèm lệnh tái lập được.
- Mỗi thành phần có unit test riêng, chạy bằng một lệnh (đầu ra 7).

## 5. Ràng buộc & rủi ro

| Rủi ro | Ảnh hưởng | Cách giảm |
|---|---|---|
| Ước lượng token theo ký tự sai lệch với tokenizer thật, nhất là tiếng Việt có dấu | Xếp hạng cơ hội lệch | Báo cáo ghi rõ là ước lượng, dùng cùng một hệ số cho mọi file để so sánh vẫn công bằng |
| Đo tốc độ hook trên máy đang chạy việc khác | Số nhiễu | Đo ≥ 5 lần, lấy trung vị, ghi kèm điều kiện đo |
| Khuyến nghị nghe hay nhưng làm mất luật | Vỡ ràng buộc cứng của user | Mỗi khuyến nghị phải kèm cột "luật bị đụng" và cách chứng minh giữ nguyên |
| Báo cáo phình dài, chính nó tốn context | Tự mâu thuẫn với mục tiêu | Trần 120 dòng cho báo cáo, chi tiết dài đẩy sang bảng |

## 6. QC & Definition of Done

| # | Hạng mục kiểm | Lệnh/cách kiểm | Điều kiện PASS |
|---|---|---|---|
| Q1 | Báo cáo tồn tại và sạch lint | `python3 scripts/doc_lint.py docs/tdq/reports/2026-08-13-ra-soat-toi-uu-llm.md` | exit 0 |
| Q2 | Báo cáo không tự phình | `wc -l docs/tdq/reports/2026-08-13-ra-soat-toi-uu-llm.md` | ≤ 120 dòng |
| Q3 | Bảng đo bề mặt đủ file | `grep -c "^| " ` mục `## Đo bề mặt` | ≥ 35 dòng dữ liệu |
| Q4 | Script đo chạy được | `python3 scripts/context_surface.py` | exit 0, in bảng |
| Q5 | Test script đo | `python3 -m pytest tests/test_context_surface.py -q` | exit 0 |
| Q6 | Đo tốc độ đủ 6 hook | `grep -c "ms" ` mục `## Tốc độ hook` | ≥ 6 dòng |
| Q7 | Mỗi khuyến nghị có cột luật bị đụng | Đọc bảng xếp hạng | Không dòng nào để trống cột đó |
| Q8 | Không sửa file sản phẩm ngoài đầu ra đã nêu | `git status --short` | Chỉ có file ở §2 và tài liệu TDQ của request này |
| Q9 | Toàn bộ suite còn xanh | `python3 -m pytest tests/ -q` | exit 0 |

DoD: 9 hạng mục trên PASS, có bằng chứng lệnh + output thật trong `docs/tdq/qc/<slug>.md`.

## 7. Câu hỏi còn mở

(RỖNG)
