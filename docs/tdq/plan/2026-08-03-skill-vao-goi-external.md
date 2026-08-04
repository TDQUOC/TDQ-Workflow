# PLAN — Đưa skill vào gói external (hybrid 3 nhánh)

Ngày: 2026-08-03 · Spec: ../spec/2026-08-03-skill-vao-goi-external.md (bản 1.1, ĐÃ DUYỆT) · Lane: full
Mode thực thi: main — các phase đụng chung `external_task.py` + bộ test contract, phụ thuộc chặt, không đáng chia worktree.
Trạng thái plan: HOÀN THÀNH (duyệt "duyệt plan mode main" 2026-08-03; 16/16 task xong, QC 9/9 PASS)

## Năng lực → task
| Skill | Task | Đầu ra bắt buộc |
|---|---|---|
| tdq-build | T4.3, T4.5 | `skills/tdq-build/SKILL.md` + `agents/*.md` có 6 cụm contract mới (full) + luật quick external, test xanh |
| tdq-plan | T4.4 | `skills/tdq-plan/SKILL.md` + `references/plan-template.md` có luật nhãn `(mcp)`, test xanh |
| graphify | T5.3 | `graphify-out/` rebuild sau khi code đổi, exit 0 |

## Quy tắc thi hành (áp cho mọi task)
1. Thứ tự phase là thứ tự phụ thuộc — không đảo.
2. Mỗi task: viết test trước (đỏ) → code → test xanh → tick `[x]` NGAY vào file này.
3. Sau mỗi phase: chạy toàn bộ test suite từ `tests/` (`python3 -m unittest`), phải xanh mới sang phase sau.
4. Lệnh nào chạm state của workflow phải có `TDQ_PROJECT_DIR=<thư mục tạm>` ngay trên chính lệnh đó.
5. QC FAIL → thêm task fix vào mục QC của file này (không cần duyệt lại), loop đến khi pass.
6. Không commit/push cho đến khi user yêu cầu.

## P1 — Parser dòng `Dùng:` + split-plan (spec §2 đầu ra 2)
- [x] **T1.1** Regex chuẩn + hàm `parse_dung_lines(plan_text)` trả `{task_id: [(skill, is_mcp)]}` theo cú pháp spec §1 — Test: biến thể backtick/`(mcp)`/nhiều skill một task/dòng lệch khuôn bị bỏ qua
- [x] **T1.2** `split-plan` tách task `(mcp)` thành gói riêng `{"mcp": true}` giữ nguyên vị trí. Gói thường thêm khóa `"skills"` — Test: plan có task mcp giữa phase → 3 gói đúng thứ tự, khóa đúng; có dòng log timestamp (lệnh không slug → stderr)
- [x] **T1.3** Helper chung `strip_skill_sections(text)` cắt từ dòng `## SKILL` ĐẦU TIÊN; áp đích danh cho `count_packet_tasks`, `_task_id` và `check_packet_skills` (T3.1) — Test: gói có phần SKILL chứa chuỗi `## TASK` → đếm đúng số task thật, `_task_id` không nhặt id trong phần SKILL

**Xong P1 khi**: 3 test mới xanh + suite xanh.

## P2 — Lệnh `skill-dump` (spec §2 đầu ra 1)
- [x] **T2.1** Resolver tên skill: `skills/<tên>/` repo → `~/.claude/skills/<tên>/` → thư mục skill plugin đã cài; trùng tên → nguồn trước thắng + log cảnh báo — Test: fixture giả resolve riêng tầng 2 (`~/.claude/skills/`) và tầng 3 (plugin); 2 nguồn trùng tên → chọn đúng + có cảnh báo
- [x] **T2.2** Lệnh `skill-dump <tên>...`: in body SKILL.md (bỏ frontmatter) + toàn bộ `references/*.md`, mỗi file dưới header `## SKILL <tên> — <file>`; skill ma → exit 1 + log tên thiếu — Test: skill có references dump đủ file đúng thứ tự; skill ma exit 1; log stderr có timestamp

**Xong P2 khi**: test P2 xanh + suite xanh.

## P3 — Warning máy-kiểm trong run-plan (spec §2 đầu ra 3)
- [x] **T3.1** Hàm thuần `check_packet_skills(packet_text, plan_text) -> [cảnh báo]`: thiếu `## SKILL <tên> — ` cho task trong gói → cảnh báo; task `(mcp)` lọt gói → cảnh báo leak; so khớp nguyên header — Test: 4 case (thiếu / đủ / leak mcp / `notion` không match `notion-db`)
- [x] **T3.2** `run-plan --plan-file <plan>` (flag tùy chọn) gọi hàm ở T3.1: in cảnh báo + ghi `run.log` của slug kèm số dòng gói, VẪN chạy engine. — Test: stub engine, gói thiếu skill → stderr có cảnh báo timestamp, exit theo engine; không truyền flag → không đối chiếu

**Xong P3 khi**: test P3 xanh + suite xanh.

## P4 — Khuôn + skill docs (spec §2 đầu ra 4–7)
- [x] **T4.1** Viết `skills/tdq-build/references/agents-md.md`: nội dung AGENTS.md thật trong code fence, ≤60 dòng, mệnh lệnh, tiếng Việt. Nội dung: unittest từ `tests/`, red→green, không commit, format report — Test: unit test đếm khối trong fence ≤60 dòng + đủ cụm bắt buộc
- [x] **T4.2** Khuôn gói `references/external-task.md`: thêm mục `## SKILL <tên> — <file>` đặt CUỐI gói + hướng dẫn sinh bằng `skill-dump`. Áp cho CẢ khuôn task đơn (quick) lẫn khuôn gói plan (full) — Test: contract khuôn chứa `## SKILL` ở cuối và nhắc `skill-dump` cho cả 2 khuôn
- [x] **T4.3** Nhánh external `skills/tdq-build/SKILL.md`: LUÔN `split-plan` kể cả plan ≤6 task; sinh AGENTS.md từ khuôn; `skill-dump` vào gói; gói `mcp=true` Claude tự làm. Thêm: lệnh mẫu `run-plan` kèm `--plan-file`; xóa AGENTS.md trước diff-check/merge; lệnh mẫu trong `agents/codex-runner.md` + `agents/agy-runner.md` thêm `--plan-file` — Test: contract 6 cụm trong SKILL.md + `--plan-file` trong 2 file agent
  - Dùng: `tdq-build`
  - Nạp: gọi skill `tdq-build` TRƯỚC bước đỏ của task này. Agent ngoài không có skill system: đọc `skills/tdq-build/SKILL.md` rồi làm theo.
  - Để: sửa đúng nhánh external hiện có, không phá cấu trúc bước/luật sẵn có của skill.
  - Ra: `skills/tdq-build/SKILL.md`, `agents/codex-runner.md`, `agents/agy-runner.md` bản mới.
  - Kiểm: `python3 -m unittest test_skill_docs test_external_task -v` (từ `tests/`) xanh phần contract.
  - Không dùng cho: viết khuôn AGENTS.md (T4.1) hay luật plan (T4.4).
- [x] **T4.4** `skills/tdq-plan/SKILL.md` + `references/plan-template.md`: luật bắt buộc nhãn `(mcp)` theo cú pháp chuẩn spec §1, ghi ngay trong bước lập plan — Test: contract string + `python3 scripts/doc_lint.py` trên 2 file exit 0
  - Dùng: `tdq-plan`
  - Nạp: gọi skill `tdq-plan` TRƯỚC bước đỏ của task này. Agent ngoài không có skill system: đọc `skills/tdq-plan/SKILL.md` rồi làm theo.
  - Để: đặt luật nhãn `(mcp)` đúng chỗ khối hợp đồng `Dùng:` của template, không đổi khuôn 6 trường.
  - Ra: `skills/tdq-plan/SKILL.md`, `skills/tdq-plan/references/plan-template.md` bản mới.
  - Kiểm: `python3 -m unittest test_skill_docs -v` (từ `tests/`) xanh phần contract tdq-plan.
  - Không dùng cho: sửa nhánh external của tdq-build (T4.3).
- [x] **T4.5** Quick lane external: `skills/tdq-build/SKILL.md` (nhánh external, phần task đơn) + `skills/tdq-intake/SKILL.md` Phần C: gói task đơn cũng chép skill qua `skill-dump`; task quick dùng skill `(mcp)` → không duyệt external, khuyên main/subagent — Test: contract string 2 cụm trong 2 file

**Xong P4 khi**: test contract P4 xanh + suite xanh.

## P5 — Sync, log & QC (spec §2 đầu ra 8–9, §4)
- [x] **T5.1** Sync `portable/workflow/03-plan.md` + `04-build.md` khớp T4.3–T4.4 — Test: `test_portable_sync` xanh
- [x] **T5.2** Rà log service hợp nhất: 3 đường (`skill-dump`, `split-plan`, warning `run-plan`) cùng cơ chế log sẵn có; lệnh không có slug → stderr timestamp, có slug → `run.log` — Test: unit test bắt dòng log timestamp cho cả 3 đường
- [x] **T5.3** QC chạy lệnh: toàn suite từ `tests/` + `python3 scripts/doc_lint.py docs/tdq/spec/2026-08-03-skill-vao-goi-external.md --pair docs/tdq/spec/2026-08-03-skill-vao-goi-external.md docs/tdq/plan/2026-08-03-skill-vao-goi-external.md` + graphify — Test: Q1–Q9 của spec §6 PASS, mọi lệnh exit 0
  - Dùng: `graphify`
  - Nạp: skill `graphify` đã ở user-level; agent ngoài: chạy thẳng CLI `graphify`.
  - Để: rebuild code graph sau khi `external_task.py` và tests đổi.
  - Ra: `graphify-out/` cập nhật (manifest + graph).
  - Kiểm: `graphify extract . --code-only` từ repo root exit 0.
  - Không dùng cho: phân tích/QC nội dung docs (đã có doc_lint + unittest).
- [x] **T5.4** Ghi QC evidence `docs/tdq/qc/2026-08-03-skill-vao-goi-external.md` + report `docs/tdq/reports/2026-08-03-skill-vao-goi-external.md` — Test: 2 file tồn tại, `wc -l` report ≤50

**Xong P5 khi**: DoD dưới đây PASS toàn bộ.

## Definition of Done
Trỏ về spec §6 (Q1–Q9): Q1 toàn suite `python3 -m unittest` từ `tests/` · Q2 test `skill-dump` · Q3 test `split-plan` mcp+skills · Q4 test warning `check_packet_skills` · Q5 khuôn AGENTS.md ≤60 dòng · Q6 contract skill docs · Q7 `doc_lint --pair` spec/plan exit 0 · Q8 `test_portable_sync` · Q9 `graphify extract . --code-only` exit 0.
