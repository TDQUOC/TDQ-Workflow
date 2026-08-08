# QC — Siết QC và vòng fix cho lane quick

Slug: `2026-08-07-siet-qc-lane-quick` · Lane: full · Spec: `../spec/2026-08-07-siet-qc-lane-quick.md` (bản 1.1)
Plan: `../plan/2026-08-07-siet-qc-lane-quick.md` · Chạy lúc: 2026-08-07 17:35–17:37

Mọi lệnh `init`/`approve` dưới đây chạy trong sandbox `TDQ_PROJECT_DIR=<scratchpad>/qc-q5*`
theo luật chung §6 của spec, nên KHÔNG đụng `docs/tdq/state.json` thật.

| # | Hạng mục | Kết quả | Bằng chứng (output thật) |
|---|---|---|---|
| Q1 | Test mới cho luật QC quick | **PASS** | `cd tests && python3 -m unittest test_quick_qc -v` → `Ran 15 tests in 0.251s` · `OK` (≥ 12) |
| Q2 | Parity 5 nguồn + phase table | **PASS** | `cd tests && python3 -m unittest test_portable_sync test_phase_table -v` → `Ran 12 tests in 0.005s` · `OK` |
| Q3 | Suite không hồi quy | **PASS** | `cd tests && python3 -m unittest discover . -q` → `Ran 618 tests` · `FAILED (failures=1)`, đúng 1 failure và đúng tên đã khoanh ngoài phạm vi: `FAIL: test_d_ban_repo_trung_ban_da_cai (test_claude_md_core.CoreFileTest…)`. Mốc trước khi sửa: 603 test / 1 failure cùng tên → +15 test, 0 hồi quy |
| Q4 | Lint tài liệu | **PASS** | `python3 scripts/doc_lint.py skills portable` → không in gì, `exit=0` |
| Q5 | Cờ `--no-qc` chạy đúng và chặn đúng | **PASS** | `approve quick --no-qc --by "duyệt quick không QC"` → `approve_quick_exit=0`, stderr có `[2026-08-07T17:36:48+07:00] ℹ️ Ghi nhận user BỎ QC cho quick theo yêu cầu: "duyệt quick không QC". Vòng fix vẫn BẮT BUỘC: test đỏ hoặc bug đã biết thì vẫn phải fix.` · `get quick_qc_skipped` → `true` · `approve spec --no-qc --by x` → `exit=2`, `Cờ --no-qc chỉ dùng cho \`approve quick\`, không dùng cho spec.` |
| Q6 | 5 nguồn cùng nêu 3 hạng mục QC và trần 3 vòng | **PASS** | `grep -l "trần 3 vòng" <3 file văn bản> \| wc -l` → `3` · `grep -c "trần 3 vòng" <2 bản phases.md>` → `skills/tdq-conventions/references/phases.md:2` và `portable/workflow/phases.md:2` (mỗi file ≥ 1) |
| Q7 | Biên & đường lỗi của cờ mới | **PASS** | 3 biến thể, cả 3 `traceback=0`: `--no-qc` → `exit=2` · `Bỏ QC phải kèm --by "<nguyên văn câu user>" để còn dấu vết.` (thiếu `--by` exit ≠ 0, thông báo tiếng Việt nêu rõ `--by`) · `--no-qc lạ` → `exit=2` · `Tham số không hợp lệ: --no-qc lạ` · `--no-qc --no-qc --by x` → `exit=0`, cờ idempotent, `get quick_qc_skipped` → `true` |
| Q8 | QC độc lập bằng agent `tdq-qc-tester` | **PASS** | xem mục dưới |

## Q8 — kiểm độc lập

Agent `tdq-qc-tester` tự chạy lại Q1–Q7 trên cây làm việc thật (sandbox riêng cho mọi
lệnh ghi state). Phán quyết nguyên văn: **"PASS — Q1–Q7 đều đạt, không hạng mục nào FAIL."**
Số liệu agent đo khớp bảng trên: 15 test · 12 test · 618 test / 1 failure đúng tên · lint 0 ·
`grep -l` = 3 · 2 bản `phases.md` `diff` với `phases-doc` là IDENTICAL · `next` quick 16 dòng.

Agent probe thêm ngoài yêu cầu, đều đạt: `TDQ_LOG=0` tắt sạch dòng timestamp · `--by ""`
→ exit 2 và cờ vẫn `false` · `approve plan --no-qc` → exit 2 · không còn TODO/FIXME/stub.
State thật của repo sau mọi lệnh vẫn `lane=full phase=qc quick_qc_skipped=False`.

**Một chỗ agent đo khác tôi, agent đúng:** biến thể `--no-qc --no-qc --by x` cho `exit=0`
(cờ idempotent), không phải `exit=2`. Lần đo đầu của tôi bị vỡ argv do vòng lặp shell
không quote biến. Đã chạy lại bằng argv thật và sửa ô Q7 ở trên. Điều kiện PASS của Q7
vẫn đạt: cả 3 biến thể không traceback, và biến thể thiếu `--by` vẫn `exit=2`.

## Vòng fix

0 vòng. Không hạng mục nào FAIL nên không mở mục `## QC vòng N — fix` trong plan.

## Ghi chú (không FAIL, đã báo trong report)

- 1 failure có sẵn `test_claude_md_core.test_d_ban_repo_trung_ban_da_cai` là do
  `portable/claude-md/CLAUDE.md` lệch `~/.claude/CLAUDE.md` từ 2026-08-06, spec §1 đã ghi
  NGOÀI phạm vi. Đo trước và sau khi sửa đều thấy đúng 1 failure này.
- Agent nêu 2 mặt bẩn tiềm tàng, cả 2 là hành vi có sẵn, spec không yêu cầu chặn.
  Một: `approve quick --no-qc` khi state đang `lane=full` chỉ `⚠️` rồi vẫn set cờ (exit 0).
  Hai: `approve quick` thiếu `--by` (không có `--no-qc`) vẫn exit 0 kèm `⚠️` — đúng spec §4.
- `skills/tdq-intake/references/quick-lane.md` đúng 90 dòng, sát trần 90 của spec §2.
- Trong lúc build, 2 hook duyệt báo câu `"duyệt spec 1.1 và duyệt plan mode main"` là
  không rõ. Câu đó có động từ duyệt 2 lần, đủ đối tượng và mode nên không phải suy diễn.
  Heuristic `prompt_context.py` còn hụt ở dạng câu duyệt ghép — ngoài phạm vi request này.
