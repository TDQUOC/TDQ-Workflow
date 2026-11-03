# PLAN — Tối ưu token/time workflow (vòng 2)

Ngày: 2026-08-05 · Spec: ../spec/2026-08-05-toi-uu-token-vong-2.md (ĐÃ DUYỆT) · Lane: full
Mode thực thi: subagent — plan 21 task, các phase đã chia theo cụm file rời nhau nên giao được; P2 và P4 vẫn do main làm vì chạm `~/.claude/*` ngoài repo và cần nguyên văn spec §2 (ĐỀ XUẤT, user chốt lúc duyệt)
Trạng thái plan: CHỜ DUYỆT

## Giao việc theo phase (khi user chốt mode `subagent`)

| Phase | Ai làm | Vì sao |
|---|---|---|
| P1 | subagent `sonnet-high_ sua token audit` | code + test khép kín trong 2 file |
| P2 | main | sửa `~/.claude/CLAUDE.md` ngoài repo, worktree không phủ; rủi ro mất luật cao nhất |
| P3 | subagent `sonnet-high_ viet tdq finish` | script mới, không đụng file phase khác |
| P4 | main | chốt nguyên văn luật workflow, cần cả spec §2 và §4 trong context |
| P5 | subagent `sonnet-low_ khoa effort digest` | sửa frontmatter 7 agent, cơ học |
| P6 | main + agent `tdq-qc-tester` | tổng hợp số đo và QC độc lập |

## Năng lực → task

| Skill | Task | Đầu ra bắt buộc |
|---|---|---|
| `search-scout` | T1.1 | mục "Đơn giá xác nhận" trong `docs/tdq/research/2026-08-05-toi-uu-token-vong-2.md` |
| `scripts/token_audit.py` | T1.3, T1.5 | `tests/test_token_audit.py` xanh + số before trong knowledge |
| `skill-creator` | T2.2 | 2 file `references/` mới + checklist §8 trong `spec-template.md` |
| `claude-md-management` (claude-md-improver) | T2.3 | `portable/claude-md/CLAUDE.md` ≤ 3.500 byte |
| `scripts/plugin_tiers.py` | T2.5 | 10 LSP ở tier `on_demand`, `pyright-lsp` giữ nguyên |
| `tdq-conventions`, `tdq-spec`, `tdq-plan`, `tdq-build` | T4.1 | 4 SKILL.md mang đủ 8 luật mới |
| `scripts/doc_lint.py` | T4.5 | `doc_lint.py skills portable` exit 0 |
| `tdq-qc-tester` | T6.3 | báo cáo PASS/FAIL 10 mục DoD kèm bằng chứng |
| `graphify` | T6.4 | `graphify-out/graph.json` mới hơn commit cuối |

## Quy tắc thi hành (áp cho mọi task)

1. Thứ tự phase là thứ tự phụ thuộc — không đảo.
2. Mỗi task: viết test trước (đỏ) → code → test xanh → tick `[x]` NGAY vào file này.
3. Sau mỗi phase: chạy toàn bộ test suite, phải xanh mới sang phase sau.
4. Lệnh nào chạm state của workflow phải có `TDQ_PROJECT_DIR=<thư mục tạm>` ngay trên chính lệnh đó.
5. Mọi thay đổi trong `~/.claude/` phải backup trước, ghi đường dẫn backup vào report.
6. QC FAIL → thêm task fix vào mục QC của file này (không cần duyệt lại), loop đến khi pass.
7. Không commit/push cho đến khi user yêu cầu.
8. Ràng buộc chặn: task nào làm giảm độ tin cậy của workflow thì bỏ, không đánh đổi.

## P1 — Đo cho đúng trước đã (spec §4 nhóm E)

- [x] **T1.1** Xác nhận đơn giá 4 loại token trước khi hardcode hệ số quy đổi — Test: file research có mục `## Đơn giá xác nhận (2026-08-05)` với 4 hệ số + URL nguồn
  - Dùng: `search-scout` (mcp)
  - Nạp: gọi Agent với `description` = `sonnet-low_ xac nhan don gia token`; agent tự nạp skill của nó.
  - Để: tra giá cache read, cache write, input, output hiện hành của Opus/Sonnet trên trang giá chính thức; trả 4 hệ số + URL.
  - Ra: mục `## Đơn giá xác nhận (2026-08-05)` trong `docs/tdq/research/2026-08-05-toi-uu-token-vong-2.md`.
  - Kiểm: `grep -c "Đơn giá xác nhận" docs/tdq/research/2026-08-05-toi-uu-token-vong-2.md` trả 1.
  - Không dùng cho: chốt hệ số cuối và sửa code — main làm; agent chỉ trả số kèm nguồn, digest ≤ 1.500 ký tự.
- [x] **T1.2** Viết `tests/test_token_audit.py` đỏ: transcript giả 3 dòng JSONL cùng một `message.id`, trong đó 2 dòng lặp lại cùng `tool_use.id` — Test: `cd tests && python3 -m unittest test_token_audit -v` fail vì đếm 3 API call
- [x] **T1.3** Sửa `scripts/token_audit.py`: gom block theo `message.id`, dedup `tool_use.id` — Test: T1.2 xanh, đếm đúng 1 API call và 1 tool call
  - Dùng: `scripts/token_audit.py`
  - Nạp: script chạy trực tiếp, không cần nạp skill.
  - Để: sửa vòng đọc JSONL để một message nằm nhiều dòng chỉ tính một lần.
  - Ra: `scripts/token_audit.py` bản đã sửa + `tests/test_token_audit.py`.
  - Kiểm: `cd tests && python3 -m unittest test_token_audit -v` exit 0.
  - Không dùng cho: đổi định dạng bảng in ra hay thêm chỉ số ngoài spec §4 E1.
- [x] **T1.4** Thêm cột chi phí quy đổi `cache_read×0,1 + cache_write×1,25 + input + output×5` theo hệ số T1.1 — Test: unittest cho 1 bản ghi usage biết trước ra đúng con số
- [x] **T1.5** Đo BEFORE bằng công cụ đã sửa, ghi vào knowledge — Test: `docs/tdq/knowledge/2026-08-05-toi-uu-token-vong-2.md` có mục `## Đo before (công cụ đã sửa)` đủ 4 số

**Xong P1 khi**: `test_token_audit` xanh và số before đã nằm trong knowledge.

## P2 — Cắt context nền (spec §4 nhóm A)

- [x] **T2.1** Viết `tests/test_claude_md_core.py` đỏ với 4 điều kiện của spec §2 · kích thước ≤ 3.500 byte · 5 luật bất biến còn nguyên · mỗi luật CHUYỂN tìm thấy ở file đích · bản repo trùng bản đã cài — Test: chạy test, fail vì chưa có `portable/claude-md/CLAUDE.md`
- [x] **T2.2** Tạo `skills/tdq-intake/references/issue-triage.md` (§7 cũ) và `skills/tdq-conventions/references/plugin-routing.md` (bảng định tuyến §10 cũ); bổ sung checklist §8 vào `skills/tdq-spec/references/spec-template.md` — Test: 3 file tồn tại, `doc_lint.py` trên chúng exit 0
  - Dùng: `skill-creator`
  - Nạp: gọi skill `skill-creator` TRƯỚC bước đỏ của task này.
  - Để: dựng 2 file `references/` đúng chuẩn progressive disclosure, chỉ nạp khi cần.
  - Ra: `skills/tdq-intake/references/issue-triage.md`, `skills/tdq-conventions/references/plugin-routing.md`.
  - Kiểm: `python3 scripts/doc_lint.py skills/tdq-intake skills/tdq-conventions` exit 0.
  - Không dùng cho: viết lại thân SKILL.md hay tạo skill mới ngoài 2 file trên.
- [x] **T2.3** Viết bản lõi `portable/claude-md/CLAUDE.md` theo đúng 11 dòng phán quyết của spec §2 — Test: `wc -c portable/claude-md/CLAUDE.md` ≤ 3.500
  - Dùng: `claude-md-management` (claude-md-improver)
  - Nạp: gọi skill `claude-md-improver` TRƯỚC khi viết, dùng rubric của nó chấm bản nháp.
  - Để: chấm bản lõi theo 6 tiêu chí, chỉ ra chỗ mất luật hoặc chỗ còn dài.
  - Ra: `portable/claude-md/CLAUDE.md` (nguồn sự thật trong repo).
  - Kiểm: `cd tests && python3 -m unittest test_claude_md_core -v` exit 0.
  - Không dùng cho: tự ghi đè `~/.claude/CLAUDE.md` — việc cài là T2.4, có backup.
- [x] **T2.4** Backup rồi cài bản lõi — Test: `~/.claude/CLAUDE.md.bak-<YYYYMMDD-HHMM>` tồn tại, `diff` bản repo và bản cài trả rỗng, `test_claude_md_core` xanh cả 4 điều kiện
- [x] **T2.5** Chuyển 10 LSP (clangd, csharp, gopls, jdtls, kotlin, lua, php, ruby, rust-analyzer, swift) sang tier `on_demand`, giữ `pyright-lsp` — Test: chạy reset rồi kiểm 10 plugin `false` và `pyright-lsp` `true` trong settings
  - Dùng: `scripts/plugin_tiers.py`
  - Nạp: script chạy trực tiếp, không cần nạp skill.
  - Để: sửa `~/.claude/plugin-tiers.json` rồi `reset` để tắt nhóm on_demand.
  - Ra: `~/.claude/plugin-tiers.json` có 10 slug LSP trong nhóm `on_demand`.
  - Kiểm: `python3 ~/.claude/scripts/plugin_tiers.py reset` exit 0, sau đó `grep` 11 slug trong settings cho kết quả đúng bảng trên.
  - Không dùng cho: bật/tắt plugin ngoài danh sách 10 LSP này.

**Xong P2 khi**: `test_claude_md_core` xanh và `plugin_tiers.py reset` cho đúng 10 slug tắt.

## P3 — Một lệnh cuối turn (spec §4 nhóm B, task B1)

- [x] **T3.1** Viết `tests/test_tdq_finish.py` đỏ: `--dry-run` in đúng 1 dòng và exit 0 — Test: `cd tests && python3 -m unittest test_tdq_finish -v` fail vì thiếu file
- [x] **T3.2** Viết `scripts/tdq_finish.py` chạy 4 bước theo thứ tự: doc_lint file vừa sửa → append working log → set phase → graphify · chạy hết mọi bước kể cả khi một bước fail · exit code tổng hợp — Test: giả lập doc_lint fail, khẳng định 3 bước còn lại vẫn chạy và exit khác 0
- [x] **T3.3** Log service bật mặc định: timestamp, tên bước, kết quả từng bước; tắt bằng `TDQ_LOG=0` — Test: chạy 2 lần, có biến môi trường và không, so số dòng log
- [x] **T3.4** Output ngắn: ≤ 200 ký tự khi mọi bước pass, chi tiết chỉ khi có `--verbose` — Test: unittest đo độ dài stdout
- [x] **T3.5** Chạy thật trên project tạm — Test: `TDQ_PROJECT_DIR=<thư mục tạm> python3 scripts/tdq_finish.py --phase implement` tạo đúng entry working log và đổi phase

**Xong P3 khi**: `test_tdq_finish` xanh và một lần chạy thật thay được chuỗi 4 lệnh cũ.

## P4 — Đưa luật vào skill và portable (spec §4 nhóm B, C, D, E)

- [x] **T4.1** Ghi 6 luật vào `skills/tdq-conventions/SKILL.md`: không chạy `tdq_state.py next` khi hook đã in `[TDQ:NEXT]` (B3); phát 2–5 tool call độc lập trong cùng một lượt (B2); append working log bằng `tdq_finish.py`, cấm Read lại file để append (C1); file trên 200 dòng thì `grep -n` rồi Read theo `offset`/`limit` (C2); `description` của Agent theo dạng `<model>-<effort>_ <mô tả>` (D1); không đổi model hay effort giữa chừng một phase build (E2) — Test: 6 lần `grep` trên SKILL.md đều trúng
  - Dùng: `tdq-conventions`, `tdq-spec`, `tdq-plan`, `tdq-build`
  - Nạp: đọc `skills/tdq-conventions/SKILL.md` cùng 3 SKILL.md kia trước bước đỏ của task.
  - Để: đặt mỗi luật đúng mục của nó và giữ trần dòng của từng SKILL.md.
  - Ra: 4 file `skills/tdq-*/SKILL.md` đã cập nhật.
  - Kiểm: `cd tests && python3 -m unittest test_skill_docs -v` exit 0.
  - Không dùng cho: đổi khung phase, đổi cổng duyệt hay rút số vòng verify.
- [x] **T4.2** Ghi luật D4 vào `skills/tdq-plan/SKILL.md`: plan trên 6 task thì mặc định ĐỀ XUẤT mode subagent, giao theo phase, user vẫn là người chốt — Test: `grep` trúng câu luật và trần 100 dòng còn nguyên
- [x] **T4.3** Thay chuỗi bookkeeping cuối turn trong `skills/tdq-build/SKILL.md` bằng một lệnh `tdq_finish.py` — Test: `grep -c "tdq_finish.py"` ≥ 1 và không còn chuỗi 4 lệnh cũ
- [x] **T4.4** Đồng bộ `portable/workflow/*` với 4 SKILL.md vừa sửa — Test: `cd tests && python3 -m unittest test_portable_sync -v`
- [x] **T4.5** Lint toàn bộ doc hướng dẫn — Test: `python3 scripts/doc_lint.py skills portable` exit 0
  - Dùng: `scripts/doc_lint.py`
  - Nạp: script chạy trực tiếp, không cần nạp skill.
  - Để: bắt bước nhảy số, lệnh ngoài code block, từ mơ hồ, quá trần dòng.
  - Ra: exit code 0 trên `skills` và `portable`.
  - Kiểm: `python3 scripts/doc_lint.py skills portable` exit 0.
  - Không dùng cho: kiểm nội dung nghiệp vụ của spec/plan — việc đó là `--pair`.

**Xong P4 khi**: 8 luật đều `grep` trúng, `test_portable_sync` xanh, `doc_lint` exit 0.

## P5 — Sub-agent nói đúng sự thật (spec §4 nhóm D)

- [x] **T5.1** Viết `tests/test_agent_frontmatter.py` đỏ: cả 7 agent phải có `model` và `effort` tường minh, và thân agent phải có ngưỡng digest ≤ 1.500 ký tự — Test: chạy test, fail ở phần ngưỡng digest
- [x] **T5.2** Thêm ngưỡng digest ≤ 1.500 ký tự và câu cấm dán kết quả tool thô vào 7 file `agents/*.md` — Test: T5.1 xanh cả hai điều kiện

**Xong P5 khi**: `test_agent_frontmatter` xanh trên đủ 7 agent.

## P6 — Log, test bắt buộc, đo lại và QC

- [x] **T6.1** Chạy toàn bộ test suite — Test: `cd tests && python3 -m unittest discover -s . -p "test_*.py"` xanh, tổng số test ≥ 482 cộng số test mới
- [x] **T6.2** Đo AFTER và viết bảng before/after vào report — Test: `docs/tdq/reports/2026-08-05-toi-uu-token-vong-2.md` có bảng kèm id session thật của cả hai lần đo
- [x] **T6.3** QC độc lập theo 10 mục DoD của spec §7 — Test: agent trả PASS cho cả 10 mục, mỗi mục kèm lệnh và output
  - Dùng: `tdq-qc-tester`
  - Nạp: gọi Agent với `description` = `sonnet-high_ qc toi uu token vong 2`, truyền plan và spec.
  - Để: chạy lại test, dò cạnh, đối chiếu từng mục DoD, báo PASS/FAIL kèm bằng chứng.
  - Ra: digest PASS/FAIL 10 mục, ≤ 1.500 ký tự.
  - Kiểm: mọi mục FAIL đều sinh task fix trong mục QC của file này.
  - Không dùng cho: tự sửa code — agent này chỉ đọc và báo.
- [x] **T6.4** Rebuild code graph sau khi sửa `scripts/*.py` — Test: `graphify-out/graph.json` có mtime mới hơn lúc bắt đầu P1
  - Dùng: `graphify`
  - Nạp: kiểm `graphify --version` trước; thiếu thì báo user, không tự cài.
  - Để: dựng lại graph cho `scripts/` sau khi thêm `tdq_finish.py` và sửa `token_audit.py`.
  - Ra: `graphify-out/graph.json` và `graphify-out/GRAPH_REPORT.md` mới.
  - Kiểm: `graphify extract . --code-only` exit 0.
  - Không dùng cho: phân tích doc trong `docs/` hay `skills/`.

**Xong P6 khi**: suite xanh, bảng before/after có số thật, QC PASS 10/10.

## Mục QC (thêm task fix ở đây khi FAIL)

QC 2026-08-05 báo PASS 10/10 DoD, kèm 2 defect nhẹ ngoài bảng DoD:

- [x] **Q1** Rút report về ≤ 50 dòng (đang 53) — Test: `wc -l docs/tdq/reports/2026-08-05-toi-uu-token-vong-2.md` ≤ 50
- [x] **Q2** Append entry working log cho turn build P1–P6 (đang thiếu) — Test: `docs/workinglog/2026-08-05.md` có entry sau 01:25 nêu P1–P6

## Definition of Done

Trỏ về spec §6 và §7. Từng hạng mục và lệnh kiểm:

| # | Hạng mục | Lệnh kiểm |
|---|---|---|
| 1 | Toàn bộ test suite xanh | `cd tests && python3 -m unittest discover -s . -p "test_*.py"` |
| 2 | CLAUDE.md lõi ≤ 3.500 byte | `wc -c ~/.claude/CLAUDE.md` |
| 3 | Bản repo trùng bản đã cài | `diff portable/claude-md/CLAUDE.md ~/.claude/CLAUDE.md` |
| 4 | Có backup CLAUDE.md cũ | `ls ~/.claude/CLAUDE.md.bak-*` |
| 5 | Mỗi luật CHUYỂN có mặt ở file đích | `cd tests && python3 -m unittest test_claude_md_core` |
| 6 | `tdq_finish.py` chạy thật, có nhánh fail | `TDQ_PROJECT_DIR=<thư mục tạm> python3 scripts/tdq_finish.py --dry-run` |
| 7 | `token_audit.py` đếm đúng transcript giả | `cd tests && python3 -m unittest test_token_audit` |
| 8 | 10 LSP ở tier on_demand | `python3 ~/.claude/scripts/plugin_tiers.py reset` |
| 9 | 7 agent có effort tường minh và ngưỡng digest | `cd tests && python3 -m unittest test_agent_frontmatter` |
| 10 | Doc hướng dẫn sạch lint và spec/plan khớp | `python3 scripts/doc_lint.py skills portable` |
