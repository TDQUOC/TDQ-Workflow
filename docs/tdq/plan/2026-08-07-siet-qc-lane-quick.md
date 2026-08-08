# PLAN — Siết QC và vòng fix cho lane quick

Ngày: 2026-08-07 · Spec: ../spec/2026-08-07-siet-qc-lane-quick.md (bản 1.1, ĐÃ DUYỆT) · Lane: full
Mode thực thi: main — 5 nguồn sự thật phải khớp nhau TỪNG CHỮ và ba phase đụng chung `scripts/tdq_state.py`; chia subagent/worktree sẽ tạo đúng loại lệch mà việc này đang đi sửa. (user CHỐT mode main lúc 17:21)
Trạng thái plan: HOÀN THÀNH 2026-08-07 (duyệt 17:21 · 18/18 task tick · Q1-Q8 PASS)

## Năng lực → task

(Mỗi dòng DÙNG ở spec §3b phải có mặt ở đây VÀ có khối hợp đồng 6 trường trong task.)

| Skill | Task | Đầu ra bắt buộc |
|---|---|---|
| test-driven-development | T1.1 | `tests/test_quick_qc.py` chạy thấy ĐỎ trước khi sửa 4 nguồn, log đỏ dán vào working log |
| skill-creator | T3.3 | `skills/tdq-intake/SKILL.md` + `references/quick-lane.md` qua `doc_lint.py` exit 0 |
| verification-before-completion | T6.1 | `docs/tdq/qc/2026-08-07-siet-qc-lane-quick.md` có output thật cho Q1–Q7 |

## Quy tắc thi hành (áp cho mọi task)

1. Thứ tự phase là thứ tự phụ thuộc — không đảo.
2. Mỗi task: viết test trước (đỏ) → code → test xanh → tick `[x]` NGAY vào file này.
3. Sau mỗi phase: chạy toàn bộ test suite, phải xanh mới sang phase sau (mốc: 1 failure
   có sẵn `test_claude_md_core.test_d_ban_repo_trung_ban_da_cai`, ngoài phạm vi theo spec §1).
4. Lệnh `init`/`set`/`approve` phải có `TDQ_PROJECT_DIR=<thư mục tạm>` ngay trên chính lệnh
   đó — thiếu là ghi đè `docs/tdq/state.json` thật của chính request này.
5. QC FAIL → thêm task fix vào mục `## QC vòng N — fix` của file này (không cần duyệt lại),
   loop đến khi pass. Đây là lane **full**, không có trần vòng fix (`tdq-build/references/qc.md`
   dòng 54) — trần 3 vòng là luật đang được VIẾT RA cho lane quick, không áp cho request này.
6. `scripts/tdq_state.py` đổi `PHASE_TABLE` → phải sinh lại 2 bản `phases.md` bằng lệnh
   `phases-doc` trong cùng phase, không sửa tay.
7. Không commit/push cho đến khi user yêu cầu.

## P1 — Test đỏ trước (khoá hành vi bằng máy)

- [x] **T1.1** (xong: 15 test, 14 đỏ — 2 `ERROR` là `KeyError: quick_qc_skipped`, đỏ vì thiếu hành vi) · Viết `tests/test_quick_qc.py` với 12 test, tên test phải khớp bộ lọc dùng ở P4 (4 test parity portable đặt tiền tố `test_portable_`): (1) `quick-lane.md` có mục `## QC ở quick`; (2) `quick-lane.md` nêu đủ 3 hạng mục Q1/Q2/Q3; (3) cả 3 file văn bản (2 bản quick-lane + `tdq-intake/SKILL.md`) đều chứa cụm `trần 3 vòng`; (4) cả 3 file đó đều chứa cụm `QC vòng N — fix`; (5) `PHASE_TABLE["quick"]["checklist"]` có ≥ 2 mục chứa "QC"; (6) `PHASE_TABLE["quick"]["cmd"]` chứa `[--no-qc]`; (7) `default_state()` có `quick_qc_skipped` = False (và KHÔNG có key `quick_qc_skipped_by`); (8) `approve quick --no-qc --by "…"` set `quick_qc_skipped` = True và `quick_approved_by` = nguyên văn; (9) `approve spec --no-qc` exit ≠ 0; (10) `approve quick --no-qc` thiếu `--by` exit ≠ 0; (11) `test_portable_quick_lane_parity` — 2 bản `quick-lane.md` cùng phát biểu 3 hạng mục và trần 3 vòng, và `test_portable_phases_doc_regenerated` — 2 bản `phases.md` khớp đúng `render_phases_md()`; (12) `_common.APPROVE_HINTS["quick"]` chứa `không QC` và `prompt_context.looks_like_approval("duyệt quick không QC", "quick")` là True — Test: `cd tests && python3 -m unittest test_quick_qc -v` → 12 test, ĐỎ ít nhất 10 (chỉ test nào tình cờ pass mới xanh), dán số liệu vào working log
  - Dùng: `test-driven-development`
  - Nạp: gọi skill `superpowers:test-driven-development` TRƯỚC khi viết file test. Agent ngoài không có skill system: đọc `~/.claude/plugins/…/superpowers/skills/test-driven-development/SKILL.md` rồi làm theo.
  - Để: bảo đảm 7 test này ĐỎ vì thiếu hành vi, không đỏ vì lỗi cú pháp/import sai.
  - Ra: `tests/test_quick_qc.py` (mới) + log đỏ trong `docs/workinglog/2026-08-07.md`.
  - Kiểm: `cd tests && python3 -m unittest test_quick_qc -v 2>&1 | grep -cE "^(FAIL|ERROR):"` ≥ 10.
  - Không dùng cho: không viết lại/không sửa test sẵn có trong `tests/` — chỉ file mới này.

**Xong P1 khi**: `tests/test_quick_qc.py` tồn tại, có 12 test, ≥ 10 test đỏ và lý do đỏ là thiếu hành vi.

## P2 — `scripts/tdq_state.py` (nguồn sự thật N3 + cờ opt-out)

- [x] **T2.1** (xong: `False False`) · Thêm ĐÚNG 1 field vào `default_state()`: `"quick_qc_skipped": False`. KHÔNG thêm `quick_qc_skipped_by` — `quick_approved_by` (dòng 63) đã giữ nguyên văn cùng câu duyệt đó, thêm nữa là field trùng — Test: `python3 -c "import sys;sys.path.insert(0,'scripts');import tdq_state as t;s=t.default_state();print(s['quick_qc_skipped'], 'quick_qc_skipped_by' in s)"` in `False False`
- [x] **T2.2** (xong: `approve spec --no-qc` exit 2 nêu tên cờ; thiếu `--by` exit 2) · Thêm cờ `--no-qc` vào `_parse_approve_args()`: chỉ hợp lệ với target `quick`, target khác → `_fail` nêu rõ `--no-qc` chỉ dùng cho quick; `--no-qc` mà thiếu `--by` cũng `_fail` (hiện chỉ `_warn` rồi exit 0 → mất nguyên văn, trái quyết định 9); cập nhật `USAGE` — Test: `TDQ_PROJECT_DIR=/tmp/tdq-t22 python3 scripts/tdq_state.py approve spec --no-qc` exit ≠ 0 và stderr chứa "quick"; `TDQ_PROJECT_DIR=/tmp/tdq-t22 python3 scripts/tdq_state.py approve quick --no-qc` exit ≠ 0 và stderr chứa `--by`
- [x] **T2.3** (xong: `_info` in dòng có timestamp ra stderr, `get quick_qc_skipped` → `true`) · `_cli_approve` khi có `--no-qc`: set `quick_qc_skipped` = True và log 1 dòng qua `_info()` (đường duy nhất có timestamp, ra **stderr**, tôn trọng `TDQ_LOG=0`) — KHÔNG in vào dòng `✅` stdout vì dòng đó không có timestamp — Test: `TDQ_PROJECT_DIR=/tmp/tdq-t23 python3 scripts/tdq_state.py init 2026-08-07-x quick && TDQ_PROJECT_DIR=/tmp/tdq-t23 python3 scripts/tdq_state.py approve quick --no-qc --by "duyệt quick không QC" 2>&1 | grep -cE "^\[[0-9]{4}-"` ≥ 1, rồi `TDQ_PROJECT_DIR=/tmp/tdq-t23 python3 scripts/tdq_state.py get quick_qc_skipped` in đúng `true`
- [x] **T2.4** (xong: 18 test test_phase_table+test_next xanh; checklist 3 mục QC, `[--no-qc]` True; `next` quick 16 dòng ≤ 20) · Cập nhật `PHASE_TABLE["quick"]`: `action` nêu QC mặc định bật; `cmd` thêm `[--no-qc]` (thành `approve quick [--mode external] [--no-qc] --by "<nguyên văn câu user>"`); `checklist` thay mục "Implement + validate" bằng 3 mục — implement red→green; QC 3 hạng mục ghi vào mục `## QC` của plan (hoặc 1 dòng `BỎ theo yêu cầu user: "<nguyên văn>"` khi `quick_qc_skipped`); FAIL → `## QC vòng N — fix`, trần 3 vòng, vượt thì DỪNG báo user; dòng `➤ Duyệt` thêm biến thể `"duyệt quick không QC"`; `done_when` thêm điều kiện mục `## QC` tồn tại; `forbidden` thêm "Đóng việc khi còn test đỏ / còn bug đã biết" và "Chạy `set phase=idle` khi đã vượt trần 3 vòng fix mà chưa báo user" — Test: `cd tests && python3 -m unittest test_phase_table test_next -v` xanh và `python3 -c "import sys;sys.path.insert(0,'scripts');import tdq_state as t;r=t.PHASE_TABLE['quick'];print(len([c for c in r['checklist'] if 'QC' in c]), '[--no-qc]' in r['cmd'])"` in số ≥ 2 và `True`
- [x] **T2.5** (xong: sinh lại 2 bản `phases.md` bằng `phases-doc`, `test_phase_table` xanh) · Sinh lại nguồn sự thật N5 bằng máy — `python3 scripts/tdq_state.py phases-doc --plugin-root > skills/tdq-conventions/references/phases.md` và `python3 scripts/tdq_state.py phases-doc > portable/workflow/phases.md`; KHÔNG sửa tay hai file này (`render_phases_md()` đổ cả checklist quick ra đây) — Test: `cd tests && python3 -m unittest test_phase_table -v` xanh và `git diff --stat skills/tdq-conventions/references/phases.md portable/workflow/phases.md` cho thấy cả 2 file đổi

**Xong P2 khi**: 5 task tick, `cd tests && python3 -m unittest test_state test_state_file test_phase_table test_next -q` xanh.

## P3 — `skills/tdq-intake` (nguồn sự thật N1 + N2)

- [x] **T3.1** (xong: 2 dòng bảng mới, `grep -c "mục ## QC"` = 1) · `references/quick-lane.md`: dòng 14 bảng đổi cột Quick thành `QC 3 hạng mục ghi vào mục ## QC của plan (mặc định BẬT)`, thêm dòng bảng `| Vòng fix khi FAIL | trần không giới hạn, ghi file qc/ | BẮT BUỘC, trần 3 vòng, ghi trong plan |` — Test: `grep -c "mục ## QC" skills/tdq-intake/references/quick-lane.md` ≥ 1
- [x] **T3.2** (xong: `## QC ở quick` + `## Vòng fix`, doc_lint exit 0, 90 dòng ≤ 90) · `references/quick-lane.md`: thêm mục `## QC ở quick` gồm 3 hạng mục (Q1 test từng task pass · Q2 đối chiếu từng dòng DoD · Q3 biên & đường lỗi: input rỗng, sai kiểu, file thiếu), câu nêu rõ **4 hạng mục bị bỏ** so với `tdq-build/references/qc.md` (full-suite toàn repo — thay bằng test của từng task · log service · không-placeholder · hợp đồng skill `Dùng:/Kiểm/Ra`), khuôn mục `## QC` append vào plan, luật opt-out (`"duyệt quick không QC"` → ghi 1 dòng `BỎ theo yêu cầu user: "<nguyên văn>"`), và mục `## Vòng fix` (bắt buộc kể cả khi bỏ QC · khuôn `## QC vòng N — fix` · **fix xong chạy lại đủ 3 hạng mục QC**, không chỉ chạy lại hạng mục vừa FAIL · trần 3 vòng · vượt trần → DỪNG báo user + đề xuất chuyển full, GIỮ `phase=implement` và không được `set phase=idle` · quick external FAIL thì hội thoại chính tự fix, không giao lại engine đã fail). Câu ngắn, dùng gạch đầu dòng — `doc_lint.py` R5 chặn câu quá 40 từ — Test: `python3 scripts/doc_lint.py skills/tdq-intake/references/quick-lane.md` exit 0 và `wc -l < skills/tdq-intake/references/quick-lane.md` ≤ 90
- [x] **T3.3** (xong: nạp `skill-creator` trước, bước 4/5/7 sửa + bước 8 vòng fix, +6 dòng → 91 ≤ 120, lint 0) · `SKILL.md` Phần C: bước 4 thêm biến thể `"duyệt quick không QC"` vào dòng `➤ Duyệt`; bước 5 thêm `[--no-qc]` vào lệnh approve; bước 7 thay "chạy validate" bằng "chạy QC 3 hạng mục theo quick-lane.md (mặc định BẬT), ghi mục `## QC` vào plan"; thêm bước 7b vòng fix bắt buộc trần 3 vòng — tổng thêm ≤ 12 dòng — Test: `python3 scripts/doc_lint.py skills/tdq-intake/SKILL.md` exit 0 và `wc -l < skills/tdq-intake/SKILL.md` ≤ 120
  - Dùng: `skill-creator`
  - Nạp: gọi skill `skill-creator` TRƯỚC bước đỏ của task này. Agent ngoài không có skill system: đọc `~/.claude/plugins/…/skill-creator/SKILL.md` rồi làm theo.
  - Để: soi lại shape + description của `tdq-intake` sau khi thêm luật, giữ trần dòng R6 và không làm loãng description.
  - Ra: `skills/tdq-intake/SKILL.md` sửa xong, ≤ 120 dòng.
  - Kiểm: `cd tests && python3 -m unittest test_skill_shape test_skill_docs -q` xanh.
  - Không dùng cho: không tạo skill mới, không sửa skill tdq-* nào khác.
- [x] **T3.4** (xong: `test_quick_qc -k hint` xanh; `test_context_hooks test_hook_resilience` 28 test OK) · `hooks/scripts/_common.py`: `APPROVE_HINTS["quick"]` thêm biến thể → `nhắn "duyệt quick" (bỏ QC: "duyệt quick không QC")`. Đã xác minh `prompt_context.QUESTION` neo `\bkhông\b\s*$` ở cuối câu nên câu này KHÔNG bị lọc thành câu hỏi — chỉ cần sửa gợi ý, không sửa regex — Test: `cd tests && python3 -m unittest test_quick_qc -k hint -v` xanh và `cd tests && python3 -m unittest test_context_hooks test_hook_resilience -q` xanh

**Xong P3 khi**: 4 task tick, `python3 scripts/doc_lint.py skills` exit 0.

## P4 — Bản portable (nguồn sự thật N4)

- [x] **T4.1** (xong: doc_lint exit 0; `-k test_portable` chạy 2 test OK — không phải xanh giả) · Đồng bộ `portable/workflow/references/quick-lane.md` với T3.1+T3.2 · giữ đúng khác biệt sẵn có · đường dẫn `scripts/` thay `${CLAUDE_PLUGIN_ROOT}/scripts/` · link `03-plan.md` · đoạn external không hard-block MCP — Test: `python3 scripts/doc_lint.py portable/workflow/references/quick-lane.md` exit 0 và `cd tests && python3 -m unittest test_quick_qc -k test_portable -v` chạy ≥ 2 test và OK (bộ lọc phải khớp tên test đặt ở T1.1 — `-k` không khớp gì thì in "Ran 0 tests" rồi exit 0, tức xanh giả)
- [x] **T4.2** (xong: bước 4/5/7 + bước 8 vòng fix; `test_portable_sync test_phase_table` 12 test OK, doc_lint portable exit 0) · Đồng bộ `portable/workflow/01-intake.md` (Phần C bước 4/5/7/7b) với T3.3. `portable/workflow/phases.md` KHÔNG sửa ở đây — đã sinh bằng máy ở T2.5 — Test: `cd tests && python3 -m unittest test_portable_sync test_phase_table -v` xanh

**Xong P4 khi**: 2 task tick, `python3 scripts/doc_lint.py skills portable` exit 0.

## P5 — Log & test bắt buộc

- [x] **T5.1** (xong: log ON in 1 dòng có timestamp ra stderr, `TDQ_LOG=0` in 0, `get quick_qc_skipped` → `true`) · Log service: cờ `--no-qc` log đúng 1 dòng qua `_info()` — `[<ISO timestamp>] ℹ️ Ghi nhận user BỎ QC cho quick theo yêu cầu: "<nguyên văn>"` — ra stderr, tắt được bằng `TDQ_LOG=0` sẵn có (không thêm cơ chế mới) — Test: `TDQ_PROJECT_DIR=/tmp/tdq-t51 python3 scripts/tdq_state.py init 2026-08-07-x quick && TDQ_PROJECT_DIR=/tmp/tdq-t51 python3 scripts/tdq_state.py approve quick --no-qc --by "bỏ QC" 2>&1 | grep -cE "^\[[0-9]{4}-[0-9]{2}-[0-9]{2}T"` ≥ 1, và cùng lệnh với `TDQ_LOG=0` in `0`
- [x] **T5.2** (xong: `test_quick_qc` 15 test OK — sửa DOC cho khớp test, không sửa test để lách: 2 chỗ ngắt dòng làm vỡ cụm `trần 3 vòng`) · Cả 12 test của `tests/test_quick_qc.py` chuyển XANH, không sửa test để lách — Test: `cd tests && python3 -m unittest test_quick_qc -v` → `OK`, 12 test
- [x] **T5.3** (xong: 3 biến thể đều 0 traceback, exit 2; thiếu `--by` báo đúng "Bỏ QC phải kèm --by") · Biên & đường lỗi của cờ mới không traceback trần: thiếu `--by` (phải exit ≠ 0 theo T2.2), tham số lạ sau `--no-qc`, `--no-qc` lặp 2 lần — Test: `for a in "--no-qc" "--no-qc lạ" "--no-qc --no-qc --by x"; do TDQ_PROJECT_DIR=/tmp/tdq-t53 python3 scripts/tdq_state.py approve quick $a 2>&1 | grep -c Traceback; done` in `0` ba lần; riêng biến thể thiếu `--by` kiểm thêm exit ≠ 0
- [x] **T5.4** (xong: plugin.json 0.8.0 → 0.9.0, CHANGELOG mục 0.9.0; lệnh kiểm khớp version exit 0) · `CHANGELOG.md` thêm mục phiên bản mới (mô tả 4 nguồn + cờ `--no-qc`) và `.claude-plugin/plugin.json` bump version khớp — Test: `python3 -c "import json,re,sys;v=json.load(open('.claude-plugin/plugin.json'))['version'];sys.exit(0 if v in open('CHANGELOG.md').read() else 1)"` exit 0

**Xong P5 khi**: 4 task tick và toàn suite chỉ còn 1 failure có sẵn.

## P6 — QC

- [x] **T6.1** (xong: nạp `verification-before-completion` trước · Q1-Q7 PASS có output thật trong `docs/tdq/qc/2026-08-07-siet-qc-lane-quick.md`) Chạy đủ Q1–Q7 của spec §6 · ghi `docs/tdq/qc/2026-08-07-siet-qc-lane-quick.md` với lệnh + output thật cho từng hạng mục — Test: file tồn tại, có ≥ 7 dòng bảng và mỗi dòng có PASS/FAIL kèm bằng chứng
  - Dùng: `verification-before-completion`
  - Nạp: gọi skill `superpowers:verification-before-completion` TRƯỚC khi ghi kết luận QC. Agent ngoài không có skill system: đọc `~/.claude/plugins/…/verification-before-completion/SKILL.md` rồi làm theo.
  - Để: chặn việc khai PASS cho hạng mục chưa chạy; mỗi dòng PASS phải có output kèm.
  - Ra: `docs/tdq/qc/2026-08-07-siet-qc-lane-quick.md`.
  - Kiểm: `grep -c "PASS\|FAIL" docs/tdq/qc/2026-08-07-siet-qc-lane-quick.md` ≥ 7.
  - Không dùng cho: không dùng để tự ý mở rộng phạm vi QC sang lane full.
- [x] **T6.2** (xong: agent `tdq-qc-tester` phán quyết PASS Q1-Q7 · agent sửa lại 1 số liệu Q7 của tôi, đã ghi rõ trong file qc) Gọi agent `tdq-qc-tester` kiểm độc lập spec §6 (Q8) — Test: agent trả PASS kèm bằng chứng cho Q1–Q7, hoặc FAIL kèm hạng mục cụ thể

**Xong P6 khi**: Q1–Q8 PASS có bằng chứng.

## Definition of Done

Trỏ về spec §6:

| # | Hạng mục | Lệnh kiểm |
|---|---|---|
| Q1 | test mới xanh | `cd tests && python3 -m unittest test_quick_qc -v` → 12 test OK |
| Q2 | parity 5 nguồn | `cd tests && python3 -m unittest test_portable_sync test_phase_table -v` |
| Q3 | không hồi quy | `cd tests && python3 -m unittest discover . -q` → ≥ 615 test, đúng 1 failure `test_claude_md_core.test_d_ban_repo_trung_ban_da_cai` (mốc đã đo: 603 test / 1 failure) |
| Q4 | lint tài liệu | `python3 scripts/doc_lint.py skills portable` exit 0 |
| Q5 | cờ `--no-qc` | trong sandbox `TDQ_PROJECT_DIR`: approve quick `--no-qc` → `get quick_qc_skipped` in `true`; `approve spec --no-qc` exit ≠ 0; thiếu `--by` exit ≠ 0 |
| Q6 | 5 nguồn cùng luật | `grep -l "trần 3 vòng" <3 file văn bản> \| wc -l` = 3, `grep -c` ở 2 bản `phases.md` ≥ 1, và `PHASE_TABLE['quick']['checklist']` ≥ 2 mục "QC" |
| Q7 | biên đường lỗi | 3 biến thể tham số sai → 0 traceback, thiếu `--by` exit ≠ 0 |
| Q8 | QC độc lập | agent `tdq-qc-tester` PASS |

Thêm: 7 đầu ra spec §2 tồn tại · mọi task tick `[x]` · report đã viết · working log 2026-08-07 có mục cho từng turn build.
