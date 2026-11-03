# SPEC — Đề xuất tối ưu time/token cho TDQ workflow

<!-- doc-lint: allow R10 — spec viết trước khi có luật ranh giới module -->

Ngày: 2026-08-04 · Bản: 1.0 · Request: ../requests/2026-08-04-toi-uu-token-workflow.md · Lane: full
Trạng thái: CHỜ DUYỆT

## 1. Mục tiêu & phạm vi

- Mục tiêu: giao **một file đề xuất** chỉ ra mọi điểm đốt time/token của TDQ workflow, kèm
  giải pháp tới mức task, ước lượng tiết kiệm và thứ tự ưu tiên. Mục tiêu đo được: chỉ ra
  ≥10 nguyên nhân có số đo thật và ≥12 task khả thi, tổng tiết kiệm ước tính ≥50% token
  cache-read và ≥25 phút/request.
- Trong phạm vi: phân tích transcript, research, viết file đề xuất + plan cho request sau.
- NGOÀI phạm vi: sửa CLAUDE.md, sửa skill, sửa script, sửa hook. **Lần này chỉ đề xuất.**

## 1b. Lộ trình

| Bước/phase | Chạy? | Vì sao |
|---|---|---|
| Research web | CÓ (xong) | cần chuẩn chính thức về progressive disclosure + context management |
| Interview | CÓ (xong, 2 vòng) | đầu ra và mức đánh đổi chỉ user quyết được |
| Spec | CÓ | user duyệt phạm vi đề xuất trước |
| Plan | CÓ | user muốn plan sẵn để duyệt sau |
| Implement | CÓ — chỉ viết 1 file đề xuất | không sửa code/skill lần này |
| Sub-agent / mode external | BỎ | việc là viết 1 file, chia ra tốn hơn tiết kiệm |
| QC agent độc lập | BỎ | không có code để test độc lập |
| Full test suite | BỎ | không đụng file code, chỉ chạy doc_lint |
| graphify rebuild | BỎ | không đổi code |
| Report | CÓ | khung bất biến |

## 2. Đầu ra cụ thể

| # | Đầu ra | Đường dẫn/vị trí | Đo "xong" bằng |
|---|---|---|---|
| 1 | File đề xuất tối ưu | `docs/tdq/knowledge/2026-08-04-de-xuat-toi-uu-token.md` | có đủ 5 nhóm A–E, ≥12 task, mỗi task có cột tiết kiệm ước tính + rủi ro |
| 2 | Bảng nguyên nhân có số đo | trong đầu ra 1, mục "Nguyên nhân" | ≥10 dòng, mỗi dòng có số đo lấy từ research |
| 3 | Bảng ưu tiên | trong đầu ra 1, mục "Thứ tự làm" | mỗi task có hạng P0/P1/P2 theo tỉ lệ tiết kiệm/công sức |
| 4 | Script đo lặp lại được | `scripts/token_audit.py` | chạy `python3 scripts/token_audit.py` in bảng carry-cost, exit 0 |
| 5 | Report | `docs/tdq/reports/2026-08-04-toi-uu-token-workflow.md` | ≤50 dòng |

## 3. Cách tiếp cận & lý do

- Chọn: phân tích dựa trên **mô hình chi phí** `Σ(context size × số API call)`, đo trực tiếp
  trên transcript jsonl của chính repo này, rồi xếp giải pháp theo 3 đòn bẩy L1/L2/L3.
- Vì: số đo nội bộ mạnh hơn phỏng đoán; 70,2M/127M token cache-read là carry-cost của tool
  output nên đòn bẩy L1 phải đứng đầu. Nguồn ngoài xác nhận hướng subagent + progressive
  disclosure (platform.claude.com, claudefa.st, case study CLAUDE.md 42k→1,9k).
- Đã loại: đo bằng cảm tính hoặc chỉ theo tài liệu ngoài — vì không khớp workflow này.
- Đã loại: dùng `clear_tool_uses_20250919` của API — Claude Code chưa expose cho user config.

## 3b. Năng lực & công cụ

| Skill | Nguồn | Phán quyết | Dùng ở đâu / Lý do loại |
|---|---|---|---|
| tdq-intake | plugin:tdq-workflow | NỀN | skill khung đang chạy |
| tdq-spec | plugin:tdq-workflow | NỀN | skill khung đang chạy |
| tdq-plan | plugin:tdq-workflow | NỀN | skill khung đang chạy |
| tdq-build | plugin:tdq-workflow | NỀN | skill khung đang chạy |
| tdq-conventions | plugin:tdq-workflow | NỀN | skill khung đang chạy |
| tdq-status | plugin:tdq-workflow | KHÔNG | spec §3 đã chọn cách khác tốt hơn — state đọc thẳng bằng CLI |
| claude-md-improver | plugin:claude-md-management | DÙNG | soi CLAUDE.md để đề xuất bản cắt gọn (nhóm C) |
| update-config | built-in | KHÔNG | khác lĩnh vực — request này không sửa cấu hình |
| graphify | user | KHÔNG | khác lĩnh vực — không đổi code |
| skill-creator | plugin:skill-creator | KHÔNG | khác lĩnh vực — không tạo skill mới |
| remember | plugin:remember | KHÔNG | khác lĩnh vực |
| tavily-search | plugin:tavily | DÙNG | research đã chạy 2 truy vấn |
| tavily-research | plugin:tavily | KHÔNG | spec §3 đã chọn cách khác tốt hơn — tavily-search đã đủ |
| tavily-crawl | plugin:tavily | KHÔNG | spec §3 đã chọn cách khác tốt hơn — tavily-search đã đủ |
| tavily-map | plugin:tavily | KHÔNG | spec §3 đã chọn cách khác tốt hơn — tavily-search đã đủ |
| tavily-extract | plugin:tavily | KHÔNG | spec §3 đã chọn cách khác tốt hơn — tavily-search đã đủ |
| tavily-cli | plugin:tavily | KHÔNG | spec §3 đã chọn cách khác tốt hơn — tavily-search đã đủ |
| tavily-dynamic-search | plugin:tavily | KHÔNG | spec §3 đã chọn cách khác tốt hơn — tavily-search đã đủ |
| tavily-best-practices | plugin:tavily | KHÔNG | khác lĩnh vực |
| frontend-design | plugin:frontend-design | KHÔNG | khác lĩnh vực |
| writing-hookify-rules | plugin:hookify | KHÔNG | khác lĩnh vực |
| build-mcp-app | plugin:mcp-server-dev | KHÔNG | khác lĩnh vực |
| build-mcp-server | plugin:mcp-server-dev | KHÔNG | khác lĩnh vực |
| build-mcpb | plugin:mcp-server-dev | KHÔNG | khác lĩnh vực |
| playground | plugin:playground | KHÔNG | khác lĩnh vực |
| agent-development | plugin:plugin-dev | KHÔNG | khác lĩnh vực |
| command-development | plugin:plugin-dev | KHÔNG | khác lĩnh vực |
| hook-development | plugin:plugin-dev | KHÔNG | khác lĩnh vực |
| mcp-integration | plugin:plugin-dev | KHÔNG | khác lĩnh vực |
| plugin-settings | plugin:plugin-dev | KHÔNG | khác lĩnh vực |
| plugin-structure | plugin:plugin-dev | KHÔNG | khác lĩnh vực |
| skill-development | plugin:plugin-dev | KHÔNG | khác lĩnh vực |

## 4. Yêu cầu bắt buộc

- `scripts/token_audit.py` có log service bật mặc định: timestamp mỗi bước, tắt bằng
  biến môi trường `TDQ_AUDIT_LOG=0`.
- Không placeholder: mọi con số trong file đề xuất phải lấy từ số đo thật, ghi rõ nguồn.
- `scripts/token_audit.py` có unit test riêng chạy bằng một lệnh.

## 5. Ràng buộc & rủi ro

| Rủi ro | Ảnh hưởng | Cách giảm |
|---|---|---|
| Đề xuất cắt context làm Claude quên luật | chất lượng giảm | mỗi task ghi rõ "cắt gì / giữ gì", phần luật bất biến không đụng |
| Ước lượng tiết kiệm sai lệch | kỳ vọng sai | ghi rõ công thức và giả định của từng ước lượng |
| Chính request này lại tốn nhiều token | mâu thuẫn mục tiêu | lộ trình đã cắt QC agent, full suite, subagent; spec/plan rút gọn |
| `token_audit.py` phụ thuộc định dạng jsonl | hỏng khi Claude Code đổi schema | bắt lỗi từng dòng, bỏ qua dòng lạ, không crash |

## 6. QC & Definition of Done

| # | Hạng mục kiểm | Lệnh/cách kiểm | Điều kiện PASS |
|---|---|---|---|
| Q1 | File đề xuất tồn tại, đủ 5 nhóm | `grep -c '^## Nhóm' <file>` | = 5 |
| Q2 | ≥12 task, mỗi task có tiết kiệm + rủi ro | đếm dòng bảng task | ≥12 dòng, không ô trống |
| Q3 | ≥10 nguyên nhân có số đo | đếm dòng bảng nguyên nhân | ≥10 dòng, mỗi dòng có số |
| Q4 | Bảng ưu tiên P0/P1/P2 | `grep -c 'P0\|P1\|P2' <file>` | ≥12 |
| Q5 | `token_audit.py` chạy được | `python3 scripts/token_audit.py` | exit 0, in bảng carry-cost |
| Q6 | Test của `token_audit.py` | `cd tests && python3 -m unittest test_token_audit` | OK |
| Q7 | Log service của script | `TDQ_AUDIT_LOG=0 python3 scripts/token_audit.py` | không in dòng log nào |
| Q8 | Lint spec↔plan | `python3 scripts/doc_lint.py --pair <spec> <plan>` | exit 0 |
| Q9 | Report ≤50 dòng | `wc -l <report>` | ≤50 |
| Q10 | Không đụng file ngoài phạm vi | `git status --porcelain` | chỉ có docs/tdq, docs/workinglog, scripts/token_audit.py, tests/test_token_audit.py |

DoD: Q1–Q10 đều PASS, mọi task trong plan đã tick `[x]`.

## 7. Câu hỏi còn mở

(rỗng)
