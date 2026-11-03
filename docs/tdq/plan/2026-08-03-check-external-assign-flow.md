# PLAN — Đổi thiết kế mode external: giao cả plan 1 lần + phase + verify 3 tầng

Ngày: 2026-08-03 · Spec: ../spec/2026-08-03-check-external-assign-flow.md (bản 1.2, ĐÃ DUYỆT) · Lane: full
Mode thực thi: main — sửa chính cơ chế external (script + schema + skill đan nhau, phụ thuộc chặt), không dùng external để tự sửa nó.
Trạng thái plan: HOÀN THÀNH

## Năng lực → task
| Skill | Task | Đầu ra bắt buộc |
|---|---|---|
| graphify | T5.3 | code graph rebuild sau khi đổi code, kiểm bằng lệnh graphify |

## Quy tắc thi hành (áp cho mọi task)
1. Thứ tự phase là thứ tự phụ thuộc — không đảo.
2. Mỗi task: viết test trước (đỏ) → code → test xanh → tick `[x]` NGAY vào file này.
3. Sau mỗi phase: chạy toàn bộ test suite (`python3 -m pytest tests/ -q`), phải xanh mới sang phase sau.
4. Lệnh nào chạm state của workflow phải có `TDQ_PROJECT_DIR=<thư mục tạm>` ngay trên chính lệnh đó.
5. QC FAIL → thêm task fix vào mục QC của file này (không cần duyệt lại), loop đến khi pass.
6. Không commit/push cho đến khi user yêu cầu.

## P1 — Script: schema + run-plan (spec §2 #1, #2)
- [x] **T1.1** Mở rộng `validate_report` + `external_report_schema.json`: discriminator `kind: task|plan` (vắng = task, giữ hồi quy); plan-report có `tasks: [per-task report]`, `status` tổng; RÀ VÀ CẬP NHẬT test schema cũ bị ảnh hưởng (unknown key, missing key) — Test: `python3 -m pytest tests/test_external_task.py -q` (test mới: report cũ không kind pass, plan-report pass, plan-report thiếu tasks fail; test cũ đã cập nhật vẫn xanh)
- [x] **T1.2** Hàm tính timeout theo gói: `540 × n_task`, trần 3600, override `TDQ_EXTERNAL_TIMEOUT`; đếm task từ gói (`# TASK` con hoặc danh sách task trong gói plan) — Test: unit test timeout: n=3→1620, n=7→3600, gói fix m=2→1080, env override thắng (Q7)
- [x] **T1.3** Subcommand `run-plan --engine --model --task-file --worktree --slug`: 2 attempt (theo spec §3 — override câu "giữ retry 3 attempt" ở spec §1, spec 1.2 chưa sửa dòng đó; 3 attempt chỉ còn cho `run` quick lane), report tổng ghi `docs/tdq/external/<slug>/plan-round-<n>.json`, engine phải ghi `test_result` thật từng task (thiếu/rỗng → validate fail → retry), log run.log từng attempt — Test: `python3 -m pytest tests/test_external_task.py -q -k run_plan` với mock binary (Q2, Q9)
- [x] **T1.4** `parse-plan` giữ tương thích: dòng 1 model (`khó=`) và 3 model đều exit 0 — Test: unit test 2 dạng dòng máy-đọc (Q3)

**Xong P1 khi**: test_external_task.py xanh toàn bộ.

## P2 — Luật chia phase + fix-rounds (spec §2 #8, một phần #3)
- [x] **T2.1** Helper chia gói trong `external_task.py` (hoặc module cùng chỗ): plan >6 task → cắt theo phase sẵn có của plan, phase nào >6 task cắt tuần tự ≤6; in JSON danh sách gói — Test: unit test 2 case: (a) plan 7 task không phase → 2 gói ≤6 đúng thứ tự; (b) plan có heading phase 4+3 task → ranh giới gói trùng ranh giới phase (Q8)
- [x] **T2.2** Format `fix-rounds.json` (`{"rounds":[{"n":1,"tasks":[…],"result":"pass|fail"}]}`) + helper đọc/ghi/luật dừng sau round 2 — Test: unit test: ghi 2 round fail → helper báo `fallback`; không cho round 3 (Q6)

**Xong P2 khi**: unit test chia gói + fix-rounds xanh.

## P3 — Skill & khuôn gói (spec §2 #3, #4, #5)
- [x] **T3.1** Viết lại "Nhánh external" trong `skills/tdq-build/SKILL.md`: giao cả plan 1 lần qua runner (main không tự chạy lệnh), chia phase >6 task (mỗi phase 1 gói/1 turn, phase sau chờ phase trước pass verify), verify 3 tầng (engine tự verify → Claude verify phase: chạy lại test từng task + diff-check → Claude verify tổng: toàn suite + diff-check + `status --porcelain`), fix loop ≤2 vòng qua `fix-rounds.json` → fallback Claude, giữ nguyên bước đóng worktree — Test: `python3 scripts/doc_lint.py skills/tdq-build/SKILL.md` exit 0 + grep đủ từ khóa: `run-plan`, `fix-rounds.json`, `3 tầng`, `≤6 task` (Q4)
- [x] **T3.2** `skills/tdq-build/references/external-task.md`: SỬA câu mở đầu "Mỗi lần gọi engine = MỘT task" cho khớp flow mới; thêm khuôn GÓI PLAN/PHASE (bắt buộc mục "tự verify: chạy lệnh test từng task, ghi test_result thật") + khuôn GÓI FIX (thêm "task đã PASS — không làm lại", "file cấm sửa") — Test: doc_lint exit 0 + grep 3 mục bắt buộc + grep không còn "MỘT task" trái flow
- [x] **T3.3** `skills/tdq-plan/SKILL.md` mục "Chốt engine + model": lane full chỉ chốt 1 model (mức khó); bỏ hướng dẫn map TB/dễ cho lane full (giữ ghi chú tương thích dòng cũ) — Test: doc_lint exit 0 + grep không còn yêu cầu 3 mức cho lane full

**Xong P3 khi**: doc_lint 3 file exit 0, test_docs_consistency + test_skill_shape xanh.

## P4 — Agents + đồng bộ doc (spec §2 #6, #9)
- [x] **T4.1** Cập nhật `agents/codex-runner.md` + `agents/agy-runner.md`: nhận gói plan/phase/fix, chạy `external_task.py run-plan …` Bash nền + poll, trần 2×timeout gói, report đường dẫn plan-round JSON — Test: grep 2 file có `run-plan`, không còn ràng buộc "MỘT task" lane full; test_skill_shape/test agents hiện có xanh
- [x] **T4.2** Đồng bộ mô tả: `~/.claude/CLAUDE.md` mục 9 (CHỈ sửa câu "giao TỪNG task cho engine ngoài", không đụng phần khác) + skill tdq-intake/tdq-status nếu còn mô tả trái flow mới — Test: `grep -rn "TỪNG task\|MỘT task" skills/ ~/.claude/CLAUDE.md` không còn chỗ mô tả trái thiết kế mới (đầu ra #9)

**Xong P4 khi**: grep sạch + suite xanh.

## P5 — Log & test bắt buộc + QC
- [x] **T5.1** Log service: mọi lần gọi `run-plan` (plan/phase/fix round) ghi run.log timestamp, `TDQ_EXTERNAL_LOG=0` tắt — Test: unit test log có dòng attempt run-plan; env=0 → không ghi
- [x] **T5.2** Chạy toàn suite + E2E mock 2 phase Ở TẦNG SCRIPT (test đóng vai orchestrator: helper chia 7 task → 2 gói, gọi `run-plan` mock binary tuần tự, gói 2 chỉ gọi khi report gói 1 status pass; luật "Claude verify phase" ở tầng skill kiểm bằng grep/doc_lint T3.1) — Test: `python3 -m pytest tests/ -q` exit 0 (Q1, Q8)
- [x] **T5.3** Rebuild code graph — Test: `graphify extract . --code-only` exit 0
  - Dùng: `graphify`
  - Nạp: gọi skill `graphify` TRƯỚC bước chạy lệnh của task này. Agent ngoài: đọc README graphify.
  - Để: cập nhật code graph sau khi đổi scripts/skills.
  - Ra: graph artifact của graphify trong project (thư mục graph hiện có).
  - Kiểm: `graphify extract . --code-only` exit 0.
  - Không dùng cho: viết test hoặc sửa code các task khác.

**Xong P5 khi**: suite xanh, QC ghi `docs/tdq/qc/2026-08-03-check-external-assign-flow.md` với Q1–Q9 PASS kèm bằng chứng.

## Definition of Done
Theo spec §6: Q1 toàn suite · Q2 E2E run-plan mock · Q3 parse-plan 2 dạng · Q4 doc_lint · Q5 hồi quy quick (`python3 -m pytest tests/test_external_task.py tests/test_e2e_codex.py tests/test_e2e_agy.py -q` pass nguyên trạng — subcommand `run` không đổi hành vi) · Q6 fix loop 2 vòng → fallback · Q7 timeout scale theo gói · Q8 chia phase ≤6 · Q9 engine tự verify (test_result bắt buộc). 9 đầu ra spec §2 đạt điều kiện đo.
