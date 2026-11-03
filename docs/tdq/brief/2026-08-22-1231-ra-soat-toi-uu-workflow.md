# BRIEF — Chạy thử một route sau khi chuyển sang tiếng Anh

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## Nguyên văn

> okay bây giở tôi muốn bạn chạy lại thử 1 route xem sau convert sang tiếng anh xem có thể
> optimize hơn và vẫn tuân thủ soul không? giữ đúng behavior nũa

Cách tôi đọc yêu cầu này:

- Mục tiêu: chạy thử MỘT đường đi (route) của workflow sau đợt chuyển skill/rule/reference
  sang tiếng Anh, để trả lời ba câu: (1) còn tối ưu thêm được không, (2) có còn tuân thủ
  soul không, (3) behavior có giữ nguyên không.
- Phạm vi đoán: đọc + đo một route, ra báo cáo đề xuất; chưa chắc đã sửa code trong request này.
- Chỗ chưa rõ: "route" là gì — một kịch bản trong `evals/tuan-thu`, một chuỗi phase của
  workflow (intake → spec → plan → build), hay bảng định tuyến skill (`tests/test_skill_router.py`).
  Chưa rõ đây là việc ĐO rồi báo cáo, hay đo xong SỬA luôn.

## Hiểu & kiến thức

### Phạm vi đã chốt

- Mặt CHỌN: context cost · trùng lặp và luật chồng luật · runtime (số step) · chất lượng bản dịch tiếng Anh
- Mặt LOẠI: không mặt nào bị loại trong 4 mặt đưa ra; loại hẳn việc SỬA code trong request này (user chọn "chỉ Y")
- Bối cảnh: đề xuất chỉ được đụng CÁCH VIẾT, cấm đổi luật · đầu ra top 10 đề xuất kèm token ước tính · research ngoài CÓ, giao sub-agent
- Mức đầu tư suy ra: vừa — vì đầu ra là tài liệu phân tích có số đo, không có runtime mới, nhưng kết luận sẽ dẫn đường cho các request sửa sau

### Số đo bề mặt hiện tại (2026-08-22)

| Tầng nạp | Token |
|---|---|
| always loaded | ~1.400 (7 description + `docs/claude-md-mau.md`) |
| loaded on skill call | 10.785 (7 thân SKILL.md) |
| read on demand | 50.064 (35 reference + 3 agent) |
| Trần một request lane full | 59.486 |

Nguồn: `python3 scripts/context_surface.py --quiet` và `python3 scripts/skill_tokens.py --theo-phase`.

File nặng nhất theo thứ tự: `quick-lane.md` 2.883 · `tdq-conventions/SKILL.md` 2.702 ·
`team-mode.md` 2.644 · `plan-template.md` 2.380 · `spec-template.md` 2.058.

## Hỏi đáp

### Vòng 1 — làm rõ yêu cầu

- Hỏi: "chạy thử 1 route" là chạy một kịch bản, hay rà soát toàn bộ workflow rồi lên ý tưởng?
  Đáp: chọn B — chỉ rà soát toàn bộ và lên ý tưởng, chưa chạy, chưa sửa.
- Hỏi: pipeline nào? Đáp: A — chế độ chuyên sâu (deep).

### Vòng 2 — vòng scope

- Hỏi: rà soát bao quanh mặt nào? Đáp: 1ABCD — context cost, trùng lặp/luật chồng luật, runtime, chất lượng bản dịch.
- Hỏi: đề xuất được đụng tới đâu? Đáp: 2A — chỉ cắt/gộp cách viết, cấm đổi luật.
- Hỏi: danh sách dài bao nhiêu? Đáp: 3A — top 10, xếp theo lợi ích/rủi ro, có token ước tính.
- Hỏi: research ngoài? Đáp: 4A — CÓ, giao sub-agent chạy tavily.

### Vòng 3 — vòng chi tiết

- Hỏi: quét file nào? Đáp: 5A — `skills/**` + `agents/*.md` + `docs/claude-md-mau.md`.
- Hỏi: đầu ra đặt đâu? Đáp: 6A — file `docs/tdq/audit/...`, report chỉ tóm tắt.
- Hỏi: chốt "optimize hơn" bằng gì? Đáp: 7A — không đặt %, mỗi đề xuất kèm token tiết kiệm đo được.
- Hỏi: chứng minh behavior không đổi? Đáp: 8A — CÓ, mỗi đề xuất ghi luật bị chạm + eval bắt được.

### Năng lực dùng được

Phân vân → DÙNG. Kiểm kê ngày 2026-08-22: 286 skill trên đĩa, cộng skill built-in trong context.
Không xoá bảng này kể cả khi không có dòng DÙNG nào.

| Skill | Nguồn | Phán quyết | Dùng ở đâu / Lý do loại |
|---|---|---|---|
| tdq-intake | plugin:tdq-workflow | NỀN | skill khung đang chạy phase analyze |
| tdq-spec | plugin:tdq-workflow | NỀN | skill khung viết spec |
| tdq-plan | plugin:tdq-workflow | NỀN | skill khung viết plan |
| tdq-build | plugin:tdq-workflow | NỀN | skill khung implement/QC/report |
| tdq-conventions | plugin:tdq-workflow | NỀN | quy ước chung, nạp đầu mọi skill |
| Đã xét 281 skill khác | user/plugin/built-in | KHÔNG | khác lĩnh vực |

### Chốt kiến thức

- Chọn: rà soát tĩnh 4 mặt (context cost · trùng lặp · số step · chất lượng bản dịch), ra một
  hồ sơ audit kèm top 10 đề xuất; KHÔNG sửa một dòng luật nào trong request này.
- Vì: user chọn hướng B ("chỉ Y"); và research chỉ ra rủi ro thật của repo là nội dung trùng
  giữa các file chứ không phải tổng token — 10.785 token loaded-on-skill-call còn xa ngưỡng ~32k.
- Đã loại: hướng A (rà soát rồi chạy route đo trước/sau) — user chọn B; hướng C (chỉ chạy một
  route) — không trả lời được câu "toàn bộ workflow còn tối ưu được không".
- Nguồn: `docs/tdq/research/2026-08-22-1231-ra-soat-toi-uu-workflow.md`.
- Cảnh báo độ tin cậy: kết luận số 6 của file research ("thứ tự ưu tiên khi cắt") là suy luận
  của agent, KHÔNG có nguồn trực tiếp — không dùng để xếp hạng đề xuất.

### Lộ trình

| Bước/phase | Chạy? | Vì sao |
|---|---|---|
| Research web | CÓ (đã chạy) | user chọn 4A; cần đối chiếu hướng dẫn viết skill của Anthropic |
| Interview | CÓ (đã chạy) | yêu cầu ban đầu mơ hồ ở cả phạm vi lẫn định nghĩa "optimize" |
| Vòng scope | CÓ (đã chạy) | request bao cả hệ thống, dùng chữ mở "optimize" không kèm số |
| Spec → plan → implement → report | CÓ | khung bất biến, không cắt |
| QC độc lập (agent) | CÓ | đầu ra là con số; cần một agent đo lại độc lập để bắt số bịa hoặc sai |
| Deep review (tdq-reviewer) | BỎ | phạm vi đã chốt bằng 8 câu hỏi, không còn chỗ mơ hồ để review |
| Chia sub-agent chạy song song | BỎ | quyết ở cổng mode sau khi duyệt plan, không chốt ở đây |
