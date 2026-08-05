# Lane quick — chi tiết

Quick khác full ở chỗ **gộp tài liệu và gộp gate**, không phải ở chỗ bỏ suy nghĩ:
phân tích, web search khi có ẩn số ngoài, và interview khi còn câu hỏi làm đổi kết quả
đều GIỮ. Chỉ bỏ khi việc thuần nội bộ hoặc đã rõ hết — và phải nói rõ vì sao bỏ.

| Bước | Full | Quick |
|---|---|---|
| Phân tích + đọc code | có | có |
| Web search | có (2–4 truy vấn) | có khi có ẩn số bên ngoài |
| Interview | lặp đến hết mơ hồ | khi còn câu làm đổi kết quả |
| Tài liệu | knowledge + spec + plan | **1 file** `docs/tdq/plan/<slug>.md` |
| Gate duyệt | 2 (spec, plan) | **1** ("duyệt quick") |
| QC | file `qc/<slug>.md` | validate ngay trong turn implement |

## Khuôn mini-spec/plan (≤ 40 dòng)

```markdown
# QUICK — <tên việc>

Ngày: YYYY-MM-DD · Request: ../requests/<slug>.md · Lane: quick
Trạng thái: CHỜ DUYỆT
Năng lực: <skill sẽ DÙNG, hoặc "không có">

## Phạm vi
- Trong: <gạch đầu dòng>
- NGOÀI: <gạch đầu dòng>

## Task
- [ ] **T1** <việc cụ thể> — Test: <lệnh hoặc tiêu chí pass>
- [ ] **T2** <việc cụ thể> — Test: <lệnh>

## Definition of Done
- <điều kiện đo được, có lệnh kiểm>
```

Quá 40 dòng nghĩa là việc này không còn "quick" — nói với user và đề xuất chuyển full.

## Giao engine ngoài (quick external)

- Dòng máy-đọc đặt ngay dưới `Năng lực:`, đúng khuôn một dòng:
  `Thực thi external: engine=<codex|agy> · khó=<slug>`
- Model default = slug ĐẦU TIÊN (dòng 1, bỏ nhãn `(chưa xác minh)`) trong output của
  `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/external_models.py" list <engine>`.
- Luật chọn engine: [tdq-plan](../../tdq-plan/SKILL.md) mục "Chốt engine + model".
- Task dùng skill cần MCP tool (nhãn `(mcp)`) → **KHÔNG** giao external: engine ngoài
  không gọi được MCP. Hard-block — không có đường override, khớp luật ở
  `tdq-build/references/external-build.md`: gói `"mcp": true` luôn tự làm, không giao
  engine. Khuyên user chọn main hoặc subagent cho task này.
