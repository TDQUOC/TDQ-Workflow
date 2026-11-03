# PLAN — TDQ 0.3.0 (instruction-hardening-7b)

Ngày: 2026-07-29 · Spec: [2026-07-28-instruction-hardening-7b.md](../spec/2026-07-28-instruction-hardening-7b.md) (bản 1.2, ĐÃ DUYỆT) · Lane: full
Mode thực thi: **main** (tôi tự làm tuần tự, không spawn subagent) · Độ mịn: **mỗi task 1 test, red → green**
Trạng thái plan: **HOÀN THÀNH** (QC PASS 15/15, còn T7.2 chờ user)
Bản duyệt: **ĐÃ DUYỆT** (user nhắn "duyệt plan", mode main)

## Quy tắc thi hành (áp cho mọi task)

1. Thứ tự phase là thứ tự phụ thuộc — **không đảo**. Trong một phase, task chạy tuần tự theo số.
2. Mỗi task: viết test trước (đỏ) → code → test xanh → **tick `[x]` ngay** vào file này.
3. Sau mỗi phase: chạy `cd tests && python3 -m unittest discover .` — phải xanh toàn bộ trước khi sang phase sau.
4. Mọi lệnh thử nghiệm chạm state **bắt buộc** có `TDQ_PROJECT_DIR=<thư mục tạm>` ngay trên chính lệnh đó. Cấm `||` fallback. (Sự cố 2026-07-28.)
5. QC FAIL → thêm task fix vào §P8 của file này (không cần duyệt lại) và loop đến khi pass.
6. Không commit/push cho đến khi user yêu cầu.

Ước lượng: 34 task / 7 phase + QC.

---

## P1 — CLI `scripts/tdq_state.py`: state file, mirror, PHASE_TABLE, next, get

> Nền của mọi thứ còn lại. Hook và skill đều gọi về đây.

- [x] **T1.1** Ghi nguyên tử (spec S1): `save()` ghi `state.json.tmp` cùng thư mục → `os.replace()`. — Test `tests/test_state_file.py::test_atomic_write_keeps_old_on_failure` (mock `os.replace` raise → file cũ nguyên vẹn, nội dung không đổi).
- [x] **T1.2** Tự phục hồi file hỏng (S2): JSON lỗi → đổi tên `state.json.corrupt-<ts>`, dựng lại từ `default_state()`, cảnh báo stderr, exit 0. — Test `::test_corrupt_state_recovers` (ghi rác → `get` exit 0, tồn tại đúng 1 file `state.json.corrupt-*`).
- [x] **T1.3** Backfill + giữ khoá lạ (S3): thiếu khoá → bù; khoá lạ → giữ nguyên qua vòng load/save. — Test `::test_backfill_and_preserve_unknown_keys`.
- [x] **T1.4** Enum sai không làm chết (S4): `lane`/`phase`/`implement_mode` ngoài danh sách → cảnh báo stderr, coi như `None`/`idle`, vẫn chạy. — Test `::test_invalid_enum_tolerated` (`phase=xyz` → `next` exit 0 và in hướng dẫn khôi phục).
- [x] **T1.5** Hằng `PHASE_TABLE` (spec §2.3.4): dict 9 dòng, mỗi entry = `{entry, only_action, next_cmd, forbidden, checklist, done_when}`; mọi giá trị trong `VALID_PHASES` phải có entry. — Test `tests/test_phase_table.py::test_all_phases_covered`.
- [x] **T1.6** `render_state_md(state)` → chuỗi markdown đúng khuôn spec §2.3.1, ≤ 30 dòng, có dòng `Project: <tuyệt đối>`. — Test `tests/test_state_file.py::test_state_md_shape` (đủ 3 heading, bảng 6 hàng, ≤30 dòng).
- [x] **T1.7** `save()` sinh luôn `docs/tdq/STATE.md` (nguyên tử như T1.1); mọi lệnh ghi đều kéo theo. — Test `::test_save_writes_mirror` (sau `init` + `set` + `approve`, `STATE.md` khớp `state.json`).
- [x] **T1.8** In `Project: <đường dẫn tuyệt đối>` ở mọi output `next`/`get`/`STATE.md` (S5). — Test `::test_project_path_printed` (`TDQ_PROJECT_DIR` khác cwd → in đúng đường dẫn đó).
- [x] **T1.9** Mở rộng `find_shadow_states()` (S6): cảnh báo cả khi có `STATE.md` mà thiếu `state.json`. — Test `::test_shadow_and_orphan_warning`.
- [x] **T1.10** Phát hiện xung đột 2 session (S7): `set`/`approve` thấy `updated_at` trên đĩa mới hơn giá trị đã đọc → cảnh báo stderr rồi **vẫn ghi**. — Test `::test_concurrent_write_warns_but_writes`.
- [x] **T1.11** Chuẩn hoá exit code (S8, spec §2.9.4): mọi lỗi trạng thái → exit 0 + cảnh báo; chỉ sai cú pháp → exit 2 + usage tiếng Việt. — Test `::test_exit_codes_matrix` (quét mọi lệnh × 4 trạng thái xấu).
- [x] **T1.12** Lệnh `next` (spec §2.2): in khối 5 phần ≤ 20 dòng, lấy nội dung từ `PHASE_TABLE`; không state → hướng dẫn `init` + công thức slug. — Test `tests/test_next.py::test_next_all_phases` (mọi phase đủ 5 nhãn) + `::test_next_no_state`.
- [x] **T1.13** `next --brief` → đúng 1 dòng (dòng `[TDQ:NEXT] …`). — Test `::test_next_brief_single_line`.
- [x] **T1.14** `get <key>` (spec §2.2): in giá trị trần; khoá lạ → in rỗng + cảnh báo stderr, exit 0; `get` không tham số giữ hành vi cũ. — Test `::test_get_key`.
- [x] **T1.15** Log service (spec §4.1): cảnh báo stderr có timestamp ISO; `TDQ_LOG=0` tắt; mặc định bật; không log nội dung file. — Test `tests/test_state_file.py::test_log_toggle`.

**Xong P1 khi**: `cd tests && python3 -m unittest discover .` xanh; `TDQ_PROJECT_DIR=/tmp/tdq-smoke python3 scripts/tdq_state.py next` in đúng khối 5 phần.

---

## P2 — Hook: sổ turn, mã nhắc, đối chiếu bằng hiệu ứng

> Không thêm hook mới. Không đọc transcript ở bất kỳ đâu.

- [x] **T2.1** `hooks/scripts/_common.py`: thêm `turn_log_append(kind, **fields)` và `turn_log_read(session_id)` cho `docs/tdq/.tdq-turn.jsonl`; lỗi I/O → nuốt im lặng; bỏ qua dòng cũ hơn 6 giờ (RR12). — Test `tests/test_turn_ledger.py::test_append_read_and_stale_skip`.
- [x] **T2.2** `prompt_context.py` xoá mọi dòng của session hiện tại ở đầu turn. — Test `::test_prompt_clears_session_rows` (dòng session khác còn nguyên).
- [x] **T2.3** Bảng 5 mã + hàm `remind(code, lines)` sinh đúng khuôn 3 dòng ≤ 200 ký tự, dedupe **1 lần/mã/turn** qua sổ. — Test `tests/test_compliance_protocol.py::test_remind_format_and_dedupe`.
- [x] **T2.4** `edit_gate.py` ghi `observe`: `edit:<path>` cho mọi Edit/Write/MultiEdit/NotebookEdit; `log_written` khi path là `docs/workinglog/<hôm nay>.md`. — Test `::test_edit_gate_observes`.
- [x] **T2.5** `edit_gate.py` phát `TDQ:LOG` (repo đổi mà log hôm nay chưa cập nhật) và `TDQ:STATE` (định sửa `state.json`/`STATE.md`); **luôn** `permissionDecision: "allow"`. — Test `::test_edit_gate_reminders`.
- [x] **T2.6** `bash_gate.py` ghi `observe`: `state_cli` khi lệnh chứa `tdq_state.py`, `next_run` khi chứa `tdq_state.py next`. — Test `::test_bash_gate_observes`.
- [x] **T2.7** `bash_gate.py` phát `TDQ:STATE` (lệnh shell ghi thẳng state) và `TDQ:GIT` (branch/worktree phạm tiền tố, commit message có dấu vết AI, commit/push chưa được yêu cầu); luôn `allow`. — Test `::test_bash_gate_reminders`.
- [x] **T2.8** `prompt_context.py` phát `TDQ:APPROVE` khi đang chờ duyệt và prompt khớp dấu hiệu duyệt (spec §2.9.2), kèm 4 phản ví dụ không được phát. — Test `::test_approve_signal_and_counterexamples`.
- [x] **T2.9** `session_start.py` + `prompt_context.py` gọi lại hàm `next` của CLI (`--brief` cho prompt), không viết lại chữ. — Test `::test_hooks_reuse_next` (output hook chứa nguyên dòng `next --brief`).
- [x] **T2.10** `stop_gate.py` viết lại theo bảng đối chiếu spec §2.1: block **chỉ** khi có `edit:` ngoài `docs/workinglog/` và không có `log_written` và log cũ hơn file vừa sửa; các mã khác → `additionalContext`; `stop_hook_active` → im lặng. — Test `::test_stop_gate_decision_matrix` (6 tình huống).
- [x] **T2.11** Xoá sạch mọi dấu vết đọc transcript trong `hooks/`. — Test `::test_no_transcript_no_deny` (grep `transcript_path` và `"deny"` trong `hooks/`, `scripts/` → rỗng).
- [x] **T2.12** Hook không bao giờ làm hỏng tool call (spec §4.7): state hỏng / thư mục chỉ đọc / payload thiếu khoá → exit 0, không stack trace. — Test `tests/test_hook_resilience.py` (3 case × 5 hook).

**Xong P2 khi**: toàn bộ suite xanh; grep Q6 rỗng.

---

## P3 — Skills 9 → 5 (+ conventions)

- [x] **T3.1** Tạo `skills/tdq-intake/` (gộp start + analyze, ≤ 120 dòng) + `references/{lane-decision.md,interview.md}`. — Test `tests/test_doc_lint.py` (sau P5) + kiểm dòng thủ công; tạm kiểm bằng `tests/test_skill_shape.py::test_intake_shape` (có `Xong khi:`, `Bước kế tiếp:`, bước đánh số).
- [x] **T3.2** Viết lại `skills/tdq-spec/SKILL.md` ≤ 100 dòng + `references/spec-template.md`. — Test `::test_spec_shape`.
- [x] **T3.3** Viết lại `skills/tdq-plan/SKILL.md` ≤ 100 dòng + `references/plan-template.md`. — Test `::test_plan_shape`.
- [x] **T3.4** Tạo `skills/tdq-build/` (gộp implement + qc + report, ≤ 150 dòng) + `references/{qc.md,report-template.md}`. — Test `::test_build_shape`.
- [x] **T3.5** Viết lại `skills/tdq-status/SKILL.md` ≤ 60 dòng, hiện thêm `implement_mode` + `*_approved_by` (C5). — Test `::test_status_shape`.
- [x] **T3.6** Viết lại `skills/tdq-conventions/SKILL.md` ≤ 120 dòng: nhúng **giao thức một turn** (§2.8), quy tắc đọc/ghi state (§2.3.2), **bảng quyết định phase** trích từ `PHASE_TABLE`; thêm `references/{approval.md,reminder-codes.md}`; giữ `references/tavily.md`. — Test `tests/test_phase_table.py::test_conventions_matches_constant`.
- [x] **T3.7** Xoá `skills/{tdq-approve,tdq-start,tdq-analyze,tdq-implement,tdq-qc,tdq-report}/`; cập nhật 3 file `agents/*.md` trỏ tên skill mới. — Test `::test_no_stale_skill_refs` (grep tên skill cũ trong `skills/`, `agents/`, `hooks/`, `README.md` → rỗng).

**Xong P3 khi**: đúng 6 thư mục skill; grep tên cũ rỗng; suite xanh.

---

## P4 — Bản portable

- [x] **T4.1** `portable/AGENTS.md` ≤ 200 dòng: đủ luật + pipeline, mở đầu ghi rõ "harness này không có hook → tự chạy `python3 scripts/tdq_state.py next` sau mỗi bước". — Test `tests/test_portable_sync.py::test_agents_md_shape`.
- [x] **T4.2** `portable/workflow/{01-intake,02-spec,03-plan,04-build}.md`, mỗi file ≤ 200 dòng. — Test `::test_workflow_files_exist_and_bounded`.
- [x] **T4.3** `portable/README.md` ≤ 10 dòng (cách copy, yêu cầu Python 3, cách chạy). — Test `::test_readme_bounded`.
- [x] **T4.4** Test chống lệch: danh sách bước (dòng bắt đầu bằng số) của skill ↔ file portable tương ứng phải khớp. — Test `::test_steps_match_skills`.

---

## P5 — Lint + test ngân sách token

- [x] **T5.1** `scripts/doc_lint.py` khung chạy: nhận nhiều path, in `file:line: [RULE] mô tả`, exit 1 khi có vi phạm, hỗ trợ `<!-- doc-lint: allow R4 -->`. — Test `tests/test_doc_lint.py::test_runner_and_allow_comment`.
- [x] **T5.2** R1 (bước đánh số liên tục) + R3 (`Xong khi:` / `Bước kế tiếp:`). — Test `::test_r1`, `::test_r3` (mỗi rule 1 fixture bẩn + 1 sạch).
- [x] **T5.3** R2 (lệnh copy-paste được, **chấp nhận** inline-code và bảng markdown). — Test `::test_r2_table_and_inline_ok`.
- [x] **T5.4** R4 (từ mơ hồ, chỉ soát mục bước/bắt buộc, bỏ qua nếu 3 dòng sau có bảng hoặc `→`). — Test `::test_r4_scoped`.
- [x] **T5.5** R5 (câu > 40 từ) + R6 (ngưỡng dòng theo spec §2.4, mọi file ≤ 500 dòng). — Test `::test_r5`, `::test_r6`.
- [x] **T5.6** R7 (`tdq-spec`/`tdq-plan`/`tdq-build` phải link ≥ 1 `references/*template*.md`). — Test `::test_r7`.
- [x] **T5.7** Lint sạch trên `skills/**` và `portable/**`. — Test `::test_repo_docs_clean`.
- [x] **T5.8** `tests/test_token_budget.py` đo đủ 8 mục bảng spec §2.7 (4 hook, STATE.md, next, tổng description 6 skill ≤ 900 ký tự, mỗi `references/*.md` ≤ 200 dòng). — Test: chính file đó, mỗi mục 1 assert.

---

## P6 — Dọn dẹp

- [x] **T6.1** T2: viết lại `docs/notes/user-level-install.md` §3 + "Lưu ý an toàn" theo 0.3.0. — Kiểm: grep "chặn"/"gate cứng" trong file → rỗng.
- [x] **T6.2** T3: bỏ `docs/tdq/state.json` khỏi `.gitignore`, thêm `docs/tdq/.tdq-turn.jsonl`. — Kiểm: `git check-ignore -v docs/tdq/state.json` rỗng, `… .tdq-turn.jsonl` có kết quả.
- [x] **T6.3** T4: tạo `CHANGELOG.md` (mới nhất trên cùng: 0.3.0 → 0.2.0 → 0.1.x) + bảng ánh xạ tên skill cũ→mới. — Kiểm thủ công.
- [x] **T6.4** C1–C4: xoá câu chữ "the hook confirms" / "hooks enforce" / "gate duyệt cứng"; viết lại `README.md` theo 0.3.0. — Test `tests/test_docs_consistency.py::test_no_hard_gate_language` (trừ `docs/archive`, `docs/tdq`, `docs/workinglog`).
- [x] **T6.5** D1: chuyển `idea.md` + 7 file `docs/{spec,plan,qc,reports}/` v0.1 → `docs/archive/v0.1/` + README 3 dòng. D2: xoá `docs/.DS_Store`. — Kiểm: `ls docs/archive/v0.1` đủ 8 mục; `find docs -name .DS_Store` rỗng.

---

## P7 — Đóng gói 0.3.0

- [x] **T7.1** `.claude-plugin/plugin.json` → `0.3.0`; `marketplace.json` bỏ "gate duyệt cứng" (C3). — Kiểm: `claude plugin validate . --strict` PASS.
- [ ] **T7.2** Trình nguyên văn `~/.claude/CLAUDE.md` §10 bản mới (≤ 20 dòng) trong chat → **chờ user đồng ý** → mới ghi đè. — Kiểm: user xác nhận.
- [x] **T7.3** Cập nhật bản cài user-level: `claude plugin marketplace update tdq-local` + `claude plugin update tdq-workflow@tdq-local`; kiểm cache hiện 0.3.0, có `skills/tdq-intake`, `skills/tdq-build`, `portable/`, **không** còn `skills/tdq-approve`.

---

## P8 — QC (Q1–Q15 của spec) + Report

- [x] **T8.1** Chạy Q1–Q8, Q10–Q15 (tự động) → ghi kết quả vào `docs/tdq/qc/2026-07-28-instruction-hardening-7b.md`.
- [x] **T8.2** Q9 smoke bản cài, 4 kịch bản (a–d), **mỗi lệnh đặt `TDQ_PROJECT_DIR`** → dán output vào QC doc.
- [x] **T8.3** FAIL bất kỳ → thêm task fix vào ngay dưới đây, làm tiếp, không cần duyệt lại.
- [x] **T8.4** Report ≤ 50 dòng `docs/tdq/reports/2026-07-28-instruction-hardening-7b.md`: kết quả, **giới hạn RR7** (lint không chứng minh 7B thật chạy đúng), bảng ánh xạ tên skill cũ→mới, hướng dẫn nâng cấp.
- [x] **T8.5** `set phase=report` → hỏi user có commit không.

### Task fix phát sinh

## QC vòng 1 — fix
- [x] **QC1.1** Dòng tiêu đề của `next` in `phase idle` trong khi thân bài dùng row `quick` (lane quick) — làm model hiểu sai đang ở phase nào. Sửa `next_headline` dùng `phase_key`. — Test `tests/test_next.py::test_headline_shows_quick_for_quick_lane`

---

## Definition of Done

Q1–Q15 của spec PASS · `~/.claude/CLAUDE.md` §10 cập nhật sau khi user đồng ý nội dung · report ≤ 50 dòng có ghi giới hạn RR7 và bảng ánh xạ skill · working log ngày được append · chưa commit (chờ user).
