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
| QC | file `qc/<slug>.md` | QC 3 hạng mục ghi vào mục ## QC của plan (mặc định BẬT) |
| Vòng fix khi FAIL | trần không giới hạn, ghi file qc/ | BẮT BUỘC, trần 3 vòng, ghi trong plan |

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

## QC ở quick

Mặc định **BẬT**. Đủ 3 hạng mục, làm ngay sau khi implement xong:

- **Q1 — test từng task:** chạy đúng lệnh `Test:` của từng task trong plan, tất cả pass.
- **Q2 — đối chiếu Definition of Done:** đọc TỪNG dòng DoD, mỗi dòng ghi PASS/FAIL kèm
  lệnh và output thật.
- **Q3 — biên & đường lỗi cơ bản:** input rỗng, sai kiểu, file thiếu. Không được traceback trần.

Nhẹ hơn full đúng **4 hạng mục bị bỏ** so với [qc.md](qc.md): full-suite toàn repo (quick
chỉ chạy test của từng task) · kiểm log service · kiểm không-placeholder · kiểm hợp đồng
skill `Dùng:/Kiểm/Ra`.

Bằng chứng append vào CHÍNH file plan, không tạo file `qc/`:

```markdown
## QC
- Q1 test từng task: PASS — `<lệnh>` → `<output thật>`
- Q2 đối chiếu DoD: PASS — <từng dòng DoD + bằng chứng>
- Q3 biên & đường lỗi: PASS — `<lệnh>` → `<output thật>`
```

Opt-out CHỈ khi user nói rõ, ví dụ `"duyệt quick không QC"` → chạy approve kèm `--no-qc`.
User im lặng về QC = CÓ QC. Khi đó mục `## QC` vẫn phải có, đúng 1 dòng:

```markdown
## QC
BỎ theo yêu cầu user: "<nguyên văn câu user>"
```

## Vòng fix

- BẮT BUỘC, kể cả khi user bỏ QC. Test đỏ hoặc bug đã biết thì vẫn phải fix.
- Task fix ghi vào plan dưới heading `## QC vòng N — fix`, khuôn
  `- [ ] **QCn.1** <việc> — Test: <check>`. Làm red→green, tick `[x]` ngay.
- Fix xong chạy lại **đủ 3 hạng mục** Q1/Q2/Q3, không chỉ chạy lại hạng mục vừa FAIL.
- **Trần 3 vòng.** Vượt trần → DỪNG, báo user, đề xuất chuyển lane full. Giữ
  `phase=implement`, KHÔNG chạy `set phase=idle`.
- Quick external mà engine ngoài làm FAIL → hội thoại chính tự fix. Không giao lại engine đã fail.

## Giao engine ngoài (quick external)

- Dòng máy-đọc đặt ngay dưới `Năng lực:`, đúng khuôn một dòng:
  `Thực thi external: engine=<codex|agy> · khó=<slug>`
- Model default = slug ĐẦU TIÊN (dòng 1, bỏ nhãn `(chưa xác minh)`) trong output của
  `python3 scripts/external_models.py list <engine>`.
- Luật chọn engine: [03-plan.md](../03-plan.md) mục "Chốt engine + model".
- Task dùng skill cần MCP tool (nhãn `(mcp)`) → **KHÔNG** giao external: engine ngoài
  không gọi được MCP/công cụ riêng của harness chính. Khuyên user chọn main hoặc subagent; user vẫn đòi external thì
  nêu rõ rủi ro rồi làm theo user.
