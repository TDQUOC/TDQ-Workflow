# SPEC — Đưa skill vào gói external (hybrid 3 nhánh)

<!-- doc-lint: allow R10 — spec viết trước khi có luật ranh giới module -->

Ngày: 2026-08-03 · Bản: 1.1 (sau review, 11 finding đã áp) · Request: ../requests/2026-08-03-skill-vao-goi-external.md · Lane: full
Trạng thái: CHỜ DUYỆT

## 1. Mục tiêu & phạm vi
- Mục tiêu: mode external giao được skill mà plan khai báo (khối `Dùng:`) tới engine ngoài theo 3 nhánh đã chốt. Hoạt động đúng kể cả model cấp thấp: luật phân nhánh máy-kiểm, không dựa vào engine suy luận.
- Trong phạm vi:
  - Nhánh 2: lệnh mới `skill-dump` chép nguyên văn SKILL.md + toàn bộ references vào gói.
  - Nhánh 3: nhãn `(mcp)` trong dòng `Dùng:` của plan; `split-plan` tách task đó thành gói riêng cho Claude tự làm, giữ nguyên thứ tự.
  - Nhánh 1: khuôn AGENTS.md ≤60 dòng, sinh ở root worktree lúc chuẩn bị, xóa trước diff-check/merge.
  - Warning máy-kiểm trong `run-plan` khi gói thiếu mục skill so với plan.
  - Cập nhật skill tdq-plan/tdq-build, khuôn gói, lệnh mẫu trong runner agents (`--plan-file`), portable sync, unit test.
  - Quick lane external: áp dụng tương tự — gói task đơn cũng chép skill qua `skill-dump`; task quick dùng skill `(mcp)` → không duyệt external, Claude khuyên mode main/subagent.
- NGOÀI phạm vi: `.agents/skills/` cho agy (đã loại ở interview); chắt lọc/tóm tắt nội dung skill (user chốt chép nguyên văn); thay đổi logic verify 3 tầng và fix-rounds; chặn cứng khi thiếu skill (chỉ warning).

### Cú pháp máy-đọc dòng `Dùng:` (chuẩn duy nhất, mọi parser dùng chung)
- Khuôn: `- Dùng: \`<tên-skill>\`` hoặc `- Dùng: \`<tên-skill>\` (mcp)` — nhãn `(mcp)` nằm NGOÀI backtick, cuối dòng.
- Mỗi dòng `Dùng:` đúng 1 skill; task dùng nhiều skill → nhiều khối hợp đồng, mỗi khối 1 dòng `Dùng:`.
- Task có ≥1 dòng `Dùng:` gắn `(mcp)` → task là task MCP (Claude tự làm toàn bộ task).
- Regex chuẩn (ghi vào code + test): `^\s*-\s*Dùng:\s*` + backtick + tên `[A-Za-z0-9_-]+` + backtick + tùy chọn ` (mcp)`.

## 2. Đầu ra cụ thể
| # | Đầu ra | Đường dẫn/vị trí | Đo "xong" bằng |
|---|---|---|---|
| 1 | Lệnh `skill-dump <tên>...` — resolve theo thứ tự: `skills/<tên>/` trong repo → `~/.claude/skills/<tên>/` → thư mục skill của plugin đã cài (nguồn như `skill_inventory.py`); trùng tên → nguồn đứng trước thắng + log cảnh báo. In nguyên văn body SKILL.md (bỏ frontmatter) + toàn bộ `references/*.md`, mỗi file dưới header `## SKILL <tên> — <file>`, toàn khối nội dung nằm SAU heading (xem luật parser ở #2). Không tìm thấy → exit 1, log rõ tên thiếu | `scripts/external_task.py` | Unit test: skill repo có references dump đủ file đúng thứ tự; skill ngoài repo (fixture giả `~/.claude/skills/`) resolve được; trùng tên chọn đúng nguồn; skill ma → exit 1 |
| 2 | `split-plan` parse dòng `Dùng:` theo regex chuẩn §1; task `(mcp)` tách thành gói riêng `{"mcp": true}` giữ nguyên vị trí trong dãy gói; gói thường thêm khóa `"skills": [tên...]`. Luật parser gói (dùng chung cho `count_packet_tasks` và warning): mọi nội dung từ dòng `## SKILL` ĐẦU TIÊN trở đi không được đếm là TASK — mục SKILL luôn đặt CUỐI gói | `scripts/external_task.py` | Unit test: plan có task mcp giữa phase → 3 gói đúng thứ tự, gói giữa `mcp=true`; khóa `skills` đúng; `count_packet_tasks` không đếm `## TASK` nằm trong phần SKILL dump |
| 3 | Hàm thuần `check_packet_skills(packet_text, plan_text) -> [cảnh báo]` + `run-plan --plan-file <plan>` (flag tùy chọn) gọi nó: (a) chỉ xét task CÓ MẶT trong gói; thiếu mục `## SKILL <tên> — ` (so khớp nguyên chuỗi header, không match tiền tố tên) → cảnh báo; (b) task gắn `(mcp)` xuất hiện trong gói engine → cảnh báo leak. In cảnh báo + ghi log, VẪN chạy; log thêm số dòng gói | `scripts/external_task.py` | Unit test hàm thuần (không cần engine): gói thiếu skill → cảnh báo; đủ → rỗng; leak mcp → cảnh báo; tên gần giống (`notion` vs `notion-db`) không match nhầm |
| 4 | Khuôn AGENTS.md cho worktree external: nội dung thật nằm trong code fence của file khuôn, ≤60 dòng (đếm khối trong fence, không đếm phần giải thích), mệnh lệnh, tiếng Việt, chứa quy ước xuyên task (unittest từ `tests/`, red→green, không commit, format report) | `skills/tdq-build/references/agents-md.md` | Unit test: khối trong fence ≤60 dòng + có các cụm bắt buộc |
| 5 | Khuôn gói external có mục `## SKILL <tên> — <file>` đặt CUỐI gói + hướng dẫn sinh bằng `skill-dump` | `skills/tdq-build/references/external-task.md` | Test contract: khuôn chứa `## SKILL` ở cuối và nhắc `skill-dump` |
| 6 | Nhánh external của tdq-build: LUÔN chạy `split-plan` kể cả plan ≤6 task (để nhãn mcp được tách máy); bước sinh AGENTS.md từ khuôn; bước `skill-dump` vào gói; gói `mcp=true` Claude tự làm; lệnh mẫu `run-plan` PHẢI kèm `--plan-file`; bước xóa AGENTS.md trước diff-check/merge. Lệnh mẫu trong `agents/codex-runner.md`, `agents/agy-runner.md` thêm `--plan-file` | `skills/tdq-build/SKILL.md` + `agents/*.md` | Test contract string: 6 cụm bắt buộc có mặt (split-plan luôn chạy, AGENTS.md, skill-dump, mcp, --plan-file, xóa AGENTS.md) |
| 7 | Luật nhãn: skill cần MCP tool → dòng `Dùng:` PHẢI ghi `(mcp)` theo cú pháp chuẩn §1; ghi trong bước lập plan | `skills/tdq-plan/SKILL.md` + `references/plan-template.md` | Test contract string + `doc_lint` pass |
| 8 | Portable sync: `portable/workflow/03-plan.md`, `04-build.md` khớp thay đổi 6–7 | `portable/workflow/` | `python3 -m unittest` (test_portable_sync) xanh |
| 9 | Unit test mới cho đầu ra 1–7 (đầu ra 8 kiểm bằng `test_portable_sync` sẵn có) | `tests/test_external_task.py`, `tests/test_skill_docs.py` (hoặc file test hiện có tương ứng) | Toàn suite xanh từ `tests/` |

## 3. Cách tiếp cận & lý do
- Chọn: 3 nhánh máy-thực-thi — chép nguyên văn bằng script (không chắt lọc bằng model), tách task MCP bằng nhãn máy-đọc ngay ở `split-plan`, quy ước xuyên task qua AGENTS.md root worktree mà codex (`--cd`) và agy (workspace root) đều tự nạp.
- Vì: research chốt — prompt-following không bảo đảm ở model thấp, phải dựa luật deterministic + verify ngoài prompt (nguồn: `../research/2026-08-03-skill-vao-goi-external.md`). Verify 3 tầng + trường `Kiểm` của QC giữ vai trò lưới cuối, không đổi.
- Gói `mcp=true` giữ nguyên vị trí trong dãy gói để bảo toàn thứ tự phụ thuộc giữa task Claude làm và task engine làm.
- Đã loại: mục chuẩn "External notes"/chắt lọc ad-hoc — user chốt chép nguyên văn; danh sách cứng skill MCP trong script — user chọn nhãn trong plan; `.agents/skills/` — thêm bề mặt bảo trì; chặn cứng — user chọn warning.

## 3b. Năng lực & công cụ
| Skill | Nguồn | Phán quyết | Dùng ở đâu / Lý do loại |
|---|---|---|---|
| tdq-conventions | plugin:tdq-workflow | NỀN | khung workflow đang chạy |
| tdq-intake | plugin:tdq-workflow | NỀN | đã dùng ở phase analyze |
| tdq-spec | plugin:tdq-workflow | NỀN | skill đang thi hành spec này |
| tdq-plan | plugin:tdq-workflow | DÙNG | đầu ra 7 — sửa luật nhãn `(mcp)` |
| tdq-build | plugin:tdq-workflow | DÙNG | đầu ra 4–6 — sửa nhánh external |
| tdq-status | plugin:tdq-workflow | KHÔNG | khác lĩnh vực — chỉ báo trạng thái |
| graphify | user | DÙNG | cuối turn build: `graphify extract . --code-only` |
| tavily-search | plugin:tavily | KHÔNG | spec §3 đã chọn cách khác tốt hơn — research đã xong ở analyze |
| tavily-best-practices | plugin:tavily | KHÔNG | khác lĩnh vực |
| tavily-cli | plugin:tavily | KHÔNG | khác lĩnh vực |
| tavily-crawl | plugin:tavily | KHÔNG | khác lĩnh vực |
| tavily-dynamic-search | plugin:tavily | KHÔNG | khác lĩnh vực |
| tavily-extract | plugin:tavily | KHÔNG | khác lĩnh vực |
| tavily-map | plugin:tavily | KHÔNG | khác lĩnh vực |
| tavily-research | plugin:tavily | KHÔNG | khác lĩnh vực |
| skill-creator | plugin:skill-creator | KHÔNG | spec §3 đã chọn cách khác tốt hơn — sửa skill sẵn có, không tạo mới |
| skill-development | plugin:plugin-dev | KHÔNG | spec §3 đã chọn cách khác tốt hơn — sửa trực tiếp theo khuôn repo |
| agent-development | plugin:plugin-dev | KHÔNG | khác lĩnh vực — không tạo agent mới |
| command-development | plugin:plugin-dev | KHÔNG | khác lĩnh vực |
| hook-development | plugin:plugin-dev | KHÔNG | khác lĩnh vực |
| mcp-integration | plugin:plugin-dev | KHÔNG | khác lĩnh vực |
| plugin-settings | plugin:plugin-dev | KHÔNG | khác lĩnh vực |
| plugin-structure | plugin:plugin-dev | KHÔNG | khác lĩnh vực |
| claude-md-improver | plugin:claude-md-management | KHÔNG | khác lĩnh vực |
| frontend-design | plugin:frontend-design | KHÔNG | khác lĩnh vực |
| writing-hookify-rules | plugin:hookify | KHÔNG | khác lĩnh vực |
| build-mcp-app | plugin:mcp-server-dev | KHÔNG | khác lĩnh vực |
| build-mcp-server | plugin:mcp-server-dev | KHÔNG | khác lĩnh vực |
| build-mcpb | plugin:mcp-server-dev | KHÔNG | khác lĩnh vực |
| playground | plugin:playground | KHÔNG | khác lĩnh vực |
| remember | plugin:remember | KHÔNG | khác lĩnh vực |

## 4. Yêu cầu bắt buộc
- Log service bật mặc định: `skill-dump`, `split-plan`, warning của `run-plan` ghi qua cơ chế log sẵn có của `external_task.py` (timestamp, tắt/giảm được qua config hiện hành).
- Không placeholder, không TODO stub; khuôn AGENTS.md là nội dung dùng được ngay.
- Đầu ra 1–7 có unit test mới riêng; đầu ra 8 kiểm bằng `test_portable_sync` sẵn có. Tất cả chạy bằng `python3 -m unittest` từ thư mục `tests/`.

## 5. Ràng buộc & rủi ro
| Rủi ro | Ảnh hưởng | Cách giảm |
|---|---|---|
| Gói phình do chép nguyên SKILL.md + references (user chấp nhận) | Model thấp bám lệnh kém hơn khi gói dài | `run-plan` log số dòng gói; verify tầng 2/3 + `Kiểm` bắt sai sót; timeout đã scale theo số task |
| Plan quên nhãn `(mcp)` | Task MCP rơi vào gói engine, chắc chắn fail | Luật bắt buộc trong tdq-plan + tdq-reviewer soát plan; cảnh báo leak của `check_packet_skills`; engine fail → fix loop → Claude fallback vẫn cứu |
| AGENTS.md lọt vào merge | File rác vào repo | Bước xóa bắt buộc trước diff-check; diff-check sẵn có chặn "file lạ" |
| Skill trong plan không resolve được tên | `skill-dump` fail giữa chừng | Exit 1 + log rõ tên thiếu; orchestrator sửa gói trước khi dispatch |
| Portable lệch skill | `test_portable_sync` đỏ | Sync trong cùng phase, chạy suite trước khi xong |

## 6. QC & Definition of Done
| # | Hạng mục kiểm | Lệnh/cách kiểm | Điều kiện PASS |
|---|---|---|---|
| Q1 | Toàn bộ suite | `python3 -m unittest` (từ `tests/`) | Exit 0, không skip mới |
| Q2 | `skill-dump` | Unit test đầu ra 1 | Nguyên văn + references, skill ma exit 1 |
| Q3 | `split-plan` nhãn mcp + khóa skills | Unit test đầu ra 2 | Gói mcp riêng, đúng thứ tự |
| Q4 | Warning `run-plan` | Unit test đầu ra 3 | Cảnh báo khi thiếu, im lặng khi đủ |
| Q5 | Khuôn AGENTS.md | Unit test đầu ra 4 | ≤60 dòng, đủ cụm bắt buộc |
| Q6 | Contract skill docs (tdq-build, tdq-plan, khuôn gói) | Unit test đầu ra 5–7 | Đủ cụm bắt buộc |
| Q7 | doc_lint spec + plan | `python3 scripts/doc_lint.py docs/tdq/spec/<slug>.md --pair docs/tdq/spec/<slug>.md docs/tdq/plan/<slug>.md` | Exit 0 |
| Q8 | Portable sync | Q1 bao gồm `test_portable_sync` | Xanh |
| Q9 | Graph | `graphify extract . --code-only` cuối turn build | Exit 0 |

DoD: Q1–Q9 PASS; 9 đầu ra ở §2 tồn tại đúng vị trí; report ≤50 dòng tiếng Việt trong `docs/tdq/reports/`.

## 7. Câu hỏi còn mở
(Rỗng — 6 câu hỏi đã chốt ở `../questions/2026-08-03-skill-vao-goi-external.md`.)
