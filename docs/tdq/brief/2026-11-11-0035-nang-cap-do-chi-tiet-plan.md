# Brief: Báo cáo nghiên cứu chuyên sâu về nâng cấp độ chi tiết của Plan cho Model Tier thấp

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## Nguyên văn

- **Lời người dùng:**
  - "okay bây giời tôi muốn bạn resreach sâu và cho tôi đề xuất tôi ưu nhất cho plan, bây giờ plan đang sơ sài quá, tôi muốn plan thể hiện chi tiết đầy đủ hơn, để bước implement có thể dùng model tier thấp vẫn có thể hiểu và làm đúng plan và yêu cầu của spec hãy resreach vaf phân tiichs hiện tại có gì và đề xuất gì?"
  - "11a output này trông đợi là report sâu chi tiết"
  - "1B và có selft review và recheck baaso cáo"
- **Mục tiêu:** Nghiên cứu sâu toàn diện và xuất bản một Báo cáo nghiên cứu & đề xuất kiến trúc chi tiết, phân tích hiện trạng mẫu Plan hiện tại của TDQ Workflow, bóc tách nguyên nhân khiến model tier thấp (Haiku, Claude 3.5 Haiku, model local) bị ảo giác/đoán mò khi thi công task 1 dòng, đề xuất chuẩn hóa cấu trúc "Self-Contained Task Block", kèm quy trình Self-review và Recheck độc lập để đảm bảo báo cáo đạt chất lượng tối đa.
- **Phạm vi:**
  - Tập trung 100% vào báo cáo nghiên cứu, phân tích và đề xuất kiến trúc (không sửa đổi trực tiếp mã nguồn `scripts/doc_lint.py` hay template hệ thống trong request này).
  - Xuất bản Báo cáo nghiên cứu chuyên sâu (`docs/tdq/research/...` và `docs/tdq/reports/...`).
  - Xuất bản Sơ đồ trực quan Hiện trạng vs Đề xuất mới qua Archify HTML.
  - Thực hiện Self-review và Recheck đa góc độ (kiến trúc, kinh tế học token, tính khả thi, độ rõ ràng cho fresher).

## Hiểu & kiến thức

### Năng lực dùng được

| Skill / Công cụ | Nguồn | Quyết định | Lý do |
|---|---|---|---|
| `tdq-spec` | plugin:tdq-workflow | NỀN | Soạn spec báo cáo nghiên cứu và chuẩn hóa |
| `tdq-plan` | plugin:tdq-workflow | NỀN | Lập kế hoạch chi tiết cho các bước thẩm định |
| `tdq-build` | plugin:tdq-workflow | NỀN | Thực thi và QC báo cáo |
| `Archify CLI` (`tdq_archify.py`) | project | DÙNG | Render sơ đồ trực quan Hiện tại vs Đề xuất |
| `doc_lint.py` | scripts/ | DÙNG | Kiểm tra chất lượng và format văn bản |
| Đã xét 25 skill khác | user/plugin/built-in | KHÔNG | khác lĩnh vực |

### Lộ trình

| Bước/phase | Chạy? | Vì sao |
|---|---|---|
| `spec` | CÓ | Thiết kế chi tiết đặc tả cấu trúc báo cáo, self-review và recheck |
| `plan` | CÓ | Lập kế hoạch chi tiết cho các task nghiên cứu và kiểm chứng |
| `implement` | CÓ | Hoàn thiện báo cáo nghiên cứu, biên bản self-review và sơ đồ Archify |
| `qc` (ultra) | CÓ | Kiểm tra chất lượng báo cáo, recheck độc lập bằng agent |
| `report` | CÓ | Xuất báo cáo nghiên cứu chuyên sâu đa chiều kèm sơ đồ Archify Trước/Sau |

## Hỏi đáp

- Người dùng chốt phương án: **1B** — Báo cáo nghiên cứu sâu, phân tích và đề xuất kiến trúc, có quy trình Self-review và Recheck độc lập, không can thiệp code/template hệ thống.
- Mức QC: `ultra`.
