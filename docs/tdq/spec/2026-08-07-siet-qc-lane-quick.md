# SPEC — Siết QC và vòng fix cho lane quick

<!-- doc-lint: allow R10 — spec viết trước khi có luật ranh giới module -->

Ngày: 2026-08-07 · Bản: 1.1 · Request: ../requests/2026-08-07-siet-qc-lane-quick.md · Lane: full
Trạng thái: ĐÃ DUYỆT 2026-08-07T17:21 (bản 1.0 duyệt 16:56; bản 1.1 sửa theo 17 finding của `tdq-reviewer`, user duyệt lại)
Knowledge: ../knowledge/2026-08-07-siet-qc-lane-quick.md · Hỏi–đáp: ../questions/2026-08-07-siet-qc-lane-quick.md

## 1. Mục tiêu & phạm vi

- **Mục tiêu:** lane quick hiện nói "chạy validate" (không định nghĩa) và không có luật nào
  cho tình huống gặp bug. Thay bằng hai luật đo được: (a) QC 3 hạng mục **mặc định bật**,
  user opt-out có chủ đích qua gate duyệt; (b) vòng fix **bắt buộc, không opt-out được**,
  trần 3 vòng. Đo xong bằng: 4 nguồn sự thật cùng phát biểu một luật, test parity xanh.

- **Trong phạm vi:**
  - Sửa luật QC + vòng fix ở **5 nguồn sự thật** (N1–N5 mục §5).
  - Thêm biến thể duyệt `"duyệt quick không QC"` + cờ CLI `--no-qc` + 1 field state
    `quick_qc_skipped` + gợi ý duyệt trong `hooks/scripts/_common.py`.
  - Thêm test parity khẳng định 5 nguồn khớp nhau và cờ `--no-qc` hoạt động.
  - Cập nhật `CHANGELOG.md` và bump version plugin.

- **NGOÀI phạm vi:**
  - Thêm rule mới cho `scripts/doc_lint.py` (đáp câu 6 = A đã loại).
  - Chạm `hooks/scripts/stop_gate.py` (cùng lý do).
  - Sửa QC của lane full (`skills/tdq-build/references/qc.md` giữ nguyên 6 hạng mục).
  - Sửa `tests/test_claude_md_core.py::test_d_ban_repo_trung_ban_da_cai` — test này **đang
    đỏ từ trước** (bản `portable/claude-md/CLAUDE.md` lệch `~/.claude/CLAUDE.md` do mục
    plugin đổi ngày 2026-08-06). Không thuộc việc này. Mốc đã đo thật lúc 16:52:
    **603 test, 602 pass, 1 failure** đúng tên trên; DoD ở §6 tính từ mốc đó.

## 1b. Lộ trình

Chép từ knowledge. User duyệt spec là duyệt luôn lộ trình này.

| Bước/phase | Chạy? | Vì sao |
|---|---|---|
| Phân tích (B0–B6) | CÓ (xong) | kiểm kê 248 skill, đọc 4 nguồn sự thật + 5 file test, 2 vòng interview 12 câu |
| Research web | BỎ | thuần nội bộ — không có ẩn số thư viện/API/phiên bản bên ngoài |
| Deep search | BỎ | không đạt tiêu chí (không có ẩn số ngoài) |
| Interview | CÓ (xong) | 2 vòng, đã giải xung đột "QC bắt buộc" vs "hỏi user" |
| Spec + duyệt | CÓ | sửa luật lõi workflow, sai là lan ra mọi request quick sau này |
| Review sâu (`tdq-reviewer`) | CÓ | review spec + plan trước build; mâu thuẫn nội bộ là rủi ro lớn nhất của việc này |
| Plan + duyệt kèm mode | CÓ | khung bất biến |
| Implement | CÓ | khung bất biến |
| Chia subagent | BỎ | 4 nguồn phải khớp từng chữ — chia ra dễ lệch hơn làm tuần tự |
| QC file `qc/<slug>.md` | CÓ | lane full; và request này nói về QC nên phải làm mẫu mực |
| QC độc lập (`tdq-qc-tester`) | CÓ | tự viết luật rồi tự bảo đã khớp là thiên vị điển hình |
| Report | CÓ | khung bất biến |

## 2. Đầu ra cụ thể

| # | Đầu ra | Đường dẫn/vị trí | Đo "xong" bằng |
|---|---|---|---|
| 1 | Bảng so sánh quick/full có dòng QC + dòng "Vòng fix" mới; mục `## QC ở quick` (3 hạng mục, trần 3 vòng, khuôn mục `## QC` trong plan, luật chạy lại đủ 3 hạng mục sau mỗi vòng fix) | `skills/tdq-intake/references/quick-lane.md` | `grep -c "QC vòng N — fix" skills/tdq-intake/references/quick-lane.md` ≥ 1 và file ≤ 90 dòng |
| 2 | Phần C bước 4 có biến thể `"duyệt quick không QC"`; bước 7 thay "chạy validate" bằng luật QC 3 hạng mục + vòng fix bắt buộc | `skills/tdq-intake/SKILL.md` | `python3 scripts/doc_lint.py skills/tdq-intake/SKILL.md` exit 0 (R6 trần 120 dòng, R4 cấm từ mơ hồ) |
| 3 | `PHASE_TABLE["quick"]`: checklist có bước QC + bước vòng fix; `cmd` thêm `[--no-qc]`; `done_when`, `forbidden` cập nhật | `scripts/tdq_state.py` (~dòng 529-551) | `cd tests && python3 -m unittest test_phase_table -v` xanh |
| 4 | Cờ `--no-qc` cho `approve quick` + 1 field state `quick_qc_skipped` (người bỏ QC lấy từ `quick_approved_by` sẵn có, không thêm field trùng) + biến thể duyệt trong `APPROVE_HINTS` | `scripts/tdq_state.py` (`_parse_approve_args`, `_cli_approve`, `default_state`, `USAGE`), `hooks/scripts/_common.py` | trong sandbox `TDQ_PROJECT_DIR`: `approve quick --no-qc --by "x"` exit 0 và `get quick_qc_skipped` in `true`; `approve spec --no-qc` exit ≠ 0; `approve quick --no-qc` thiếu `--by` exit ≠ 0 |
| 5 | Hai bản `phases.md` **sinh lại bằng máy** (không sửa tay) + bản portable đồng bộ đầu ra 1 + 2 | `skills/tdq-conventions/references/phases.md`, `portable/workflow/phases.md`, `portable/workflow/references/quick-lane.md`, `portable/workflow/01-intake.md` | `cd tests && python3 -m unittest test_portable_sync test_phase_table` xanh |
| 6 | Test mới: parity 5 nguồn + hành vi cờ `--no-qc` + gợi ý duyệt | `tests/test_quick_qc.py` (mới) | file có ≥ 12 test, `cd tests && python3 -m unittest test_quick_qc -v` xanh |
| 7 | CHANGELOG + bump version | `CHANGELOG.md`, `.claude-plugin/plugin.json` | version trong plugin.json khớp mục mới nhất của CHANGELOG |

## 3. Cách tiếp cận & lý do

- **Chọn:** sửa văn bản luật ở 4 nguồn sự thật + thêm 2 field state cho opt-out + 1 file
  test parity mới. Không thêm rule lint, không thêm hook.
- **Vì:** `scripts/tdq_state.py` `PHASE_TABLE` đã là nguồn sự thật máy-đọc được và
  `tests/test_phase_table.py` + `tests/test_portable_sync.py` đã canh parity sẵn — chỉ cần
  mở rộng đúng chỗ là luật mới tự được ép, không phải dựng cơ chế mới. Đây là kết luận từ
  đọc code, không có nguồn ngoài (research đã BỎ, xem §1b).
- **Cái mới so với hiện trạng:** hiện tại lane quick không có định nghĩa QC nào và 0 dòng
  luật về bug (grep `FAIL|fix|bug` trong `quick-lane.md` → 0 kết quả). Sau việc này quick có
  3 hạng mục QC đo được, có khuôn ghi bằng chứng, có vòng fix trần 3, và có đường opt-out
  tường minh để lại dấu vết trong plan.
- **Đã loại:**
  - Rule `doc_lint.py` soi plan quick phải có `## QC` — vì chỉ soi được SAU implement, không
    chặn được hành vi "quên QC" đúng lúc (user chọn 6A).
  - Chặn ở `stop_gate.py` — cùng lý do, thêm nữa stop_gate đang gánh nhiều luật.
  - Nạp thẳng `qc.md` 6 hạng mục cho quick — mất tính "nhẹ hơn full" (user loại phương án 1D).
  - File `docs/tdq/qc/<slug>.md` rút gọn cho quick — phá nguyên tắc "quick gộp 1 file" (loại 2C).

## 3b. Năng lực & công cụ

Chép từ knowledge. Phân vân → DÙNG.

| Skill | Nguồn | Phán quyết | Dùng ở đâu / Lý do loại |
|---|---|---|---|
| tdq-intake, tdq-spec, tdq-plan, tdq-build, tdq-conventions, tdq-status | plugin:tdq-workflow | NỀN | chính workflow đang chạy — và cũng là đối tượng bị sửa |
| test-driven-development | plugin:superpowers | DÙNG | đầu ra 6: viết `tests/test_quick_qc.py` thấy đỏ TRƯỚC khi sửa 4 nguồn |
| verification-before-completion | plugin:superpowers | DÙNG | §6 Q1-Q5: chạy thật rồi mới khai PASS, dán số liệu |
| skill-creator | plugin:skill-creator | DÙNG | đầu ra 1+2: soi lại shape/description `skills/tdq-intake` sau khi thêm luật |
| graphify | user | NỀN | `tdq_finish.py` tự chạy `graphify extract . --code-only` cuối turn |
| 34 data-engineering, 25 huggingface-skills, 19 hyperframes, 13 datarobot, 12 qt-development, 12 figma, 11 postman, 11 cloudflare, 10 firecrawl, 9 sonarqube, 8 tavily, 7 mongodb, 7 adobe, 6 desktop-commander, 6 chrome-devtools-mcp, 6 canva, 5 base44, 3 unreal, 3 mcp-server-dev, 2 lumen, playground, remember, hookify, frontend-design, claude-md-management, figma-implement, mem0-memory, unity-mcp-orchestrator | nhiều nguồn | KHÔNG | khác lĩnh vực |
| 11 skill plugin-dev, 8 skill superpowers còn lại (brainstorming, writing-plans, executing-plans, systematic-debugging, requesting-code-review, receiving-code-review, dispatching-parallel-agents, using-git-worktrees) | plugin:plugin-dev, plugin:superpowers | KHÔNG | spec §3 đã chọn cách khác tốt hơn — TDQ tự lo plan/review/worktree tương ứng |

## 4. Yêu cầu bắt buộc

- **Log service:** việc này không sinh service mới. `tdq_state.py` đã tách hai đường ra:
  dòng `✅` tổng kết đi **stdout không timestamp** (`_cli_approve`), còn dòng có timestamp
  chỉ ra từ `_info`/`_warn` sang **stderr**, tắt được bằng `TDQ_LOG=0`. Dòng log của
  `--no-qc` phải đi qua `_info` để có timestamp và tôn trọng `TDQ_LOG=0`; mọi lệnh kiểm
  dòng đó phải hứng `2>&1`.
- **`--by` bắt buộc khi có `--no-qc`:** hiện thiếu `--by` chỉ `_warn` rồi exit 0, sẽ mất
  nguyên văn câu user. Quyết định 9 đòi để lại dấu vết, nên `--no-qc` mà không có `--by`
  phải `_fail` (exit ≠ 0).
- **Không placeholder:** không để `TODO`/`FIXME` trong luật mới; câu luật phải nêu ngưỡng
  cụ thể (R4 của `doc_lint.py` chặn từ mơ hồ như "nếu cần", "phù hợp").
- **Test cho từng phần:** mỗi đầu ra §2 có ít nhất 1 test trong `tests/test_quick_qc.py`
  hoặc test sẵn có (`test_phase_table`, `test_portable_sync`), chạy được bằng một lệnh.

## 5. Ràng buộc & rủi ro

**5 nguồn sự thật (N1–N5) — lệch một chỗ là hỏng âm thầm:**

| # | File | Chỗ sửa |
|---|---|---|
| N1 | `skills/tdq-intake/references/quick-lane.md` | dòng 14 bảng so sánh + mục mới `## QC ở quick` |
| N2 | `skills/tdq-intake/SKILL.md` | Phần C bước 4 (gate duyệt) và bước 7 (implement/validate) |
| N3 | `scripts/tdq_state.py` | `PHASE_TABLE["quick"]`, `default_state()`, `_parse_approve_args()`, `_cli_approve()`, `USAGE` |
| N4 | `portable/workflow/references/quick-lane.md`, `01-intake.md` | mirror cho agent ngoài Claude Code |
| N5 | `skills/tdq-conventions/references/phases.md` + `portable/workflow/phases.md` | **doc tự sinh** — `render_phases_md()` đổ cả `action`/`done_when`/`forbidden`/`cmd` và mục `## quick` checklist ra đây; sửa N3 mà không sinh lại là để lại luật cũ |

Sinh lại N5 bằng đúng hai lệnh (không sửa tay, `render_phases_md()` dòng 565):
`python3 scripts/tdq_state.py phases-doc --plugin-root > skills/tdq-conventions/references/phases.md`
và `python3 scripts/tdq_state.py phases-doc > portable/workflow/phases.md`.

| Rủi ro | Ảnh hưởng | Cách giảm |
|---|---|---|
| Sửa N1/N2 mà quên N4 | agent ngoài Claude Code chạy luật cũ, không ai biết | `tests/test_portable_sync.py` đang canh parity từng bước; đầu ra 6 thêm test so từng luật QC giữa 2 bản |
| Sửa N3 mà quên sinh lại N5 | `phases.md` (2 bản) còn phát biểu luật quick cũ; `test_phase_table` chỉ khoá cứng cột `cmd` nên phần checklist/`done_when` lệch **âm thầm** | đầu ra 5 chạy đúng 2 lệnh `phases-doc`; `cmd` có thêm `[--no-qc]` nên `test_phase_table::test_docs_match_constant` sẽ đỏ nếu quên |
| Lệnh kiểm chạy `approve` mà thiếu `TDQ_PROJECT_DIR` | **ghi đè `docs/tdq/state.json` thật của chính request này** — mất phase/duyệt đang chạy | mọi lệnh `init`/`set`/`approve` trong §6 và trong plan phải có `TDQ_PROJECT_DIR=<thư mục tạm>` đặt ngay trên chính lệnh đó |
| Nhồi luật vào `quick-lane.md` làm câu dài quá 40 từ | `doc_lint.py` R5 exit 1, chặn `tdq_finish.py` | viết câu ngắn, dùng gạch đầu dòng thay câu ghép; chạy `doc_lint.py` sau mỗi task P3 |
| Checklist quick dài thêm làm `next` vượt trần 20 dòng | `tests/test_next.py:36` đỏ | đã đo: quick hiện 8 mục → `next` in **14 dòng**, thêm 3 mục thành 17, còn dư 3 dòng |
| `tdq-intake/SKILL.md` vượt trần R6 = 120 dòng | `doc_lint.py` exit 1, chặn `tdq_finish.py` | hiện 84 dòng, còn dư 36; luật mới ở SKILL.md giữ ≤ 12 dòng, chi tiết đẩy hết vào `quick-lane.md` |
| Thêm field state làm vỡ test đọc `default_state()` | test đỏ hàng loạt | `tests/test_state_file.py` đã có `test_backfill_and_preserve_unknown_keys` — backfill sẵn có; vẫn phải chạy `test_state*` để xác nhận |
| `--no-qc` bị dùng sai target (`approve spec --no-qc`) | state bẩn, luật QC bị lách | `_parse_approve_args` phải `_fail` khi `--no-qc` đi với target khác `quick`; có test riêng |
| Trần 3 vòng fix bị hiểu là "hết 3 vòng thì thôi" | bug bị bỏ lại, trái ý user | câu luật phải ghi rõ: vượt 3 vòng → **DỪNG và báo user**, KHÔNG được đóng việc như đã xong |
| Test `test_claude_md_core` đang đỏ từ trước | tưởng do việc này gây ra | §1 đã loại khỏi phạm vi; DoD tính mốc đã đo 603 test / 602 pass / 1 fail-có-sẵn |
| Không cần model / không cần download | — | việc này chỉ dùng Python 3.12 sẵn có + `unittest` trong repo; không cài gói nào |

## 6. QC & Definition of Done

| # | Hạng mục kiểm | Lệnh/cách kiểm | Điều kiện PASS |
|---|---|---|---|
**Luật chung cho §6:** mọi lệnh `init`/`set`/`approve` phải chạy trong sandbox —
đặt `TDQ_PROJECT_DIR=/tmp/tdq-qc-<mã>` ngay trên chính lệnh đó. Không có biến này thì
lệnh sẽ ghi đè `docs/tdq/state.json` thật của request đang chạy.

| # | Hạng mục kiểm | Lệnh/cách kiểm | Điều kiện PASS |
|---|---|---|---|
| Q1 | Test mới cho luật QC quick | `cd tests && python3 -m unittest test_quick_qc -v` | ≥ 12 test, tất cả OK |
| Q2 | Parity 5 nguồn + phase table | `cd tests && python3 -m unittest test_portable_sync test_phase_table -v` | tất cả OK |
| Q3 | Toàn bộ suite không hồi quy | `cd tests && python3 -m unittest discover . -q` | ≥ 615 test, đúng 1 failure và là `test_claude_md_core.test_d_ban_repo_trung_ban_da_cai` (mốc đã đo trước khi sửa: 603 test / 1 failure cùng tên) |
| Q4 | Lint tài liệu | `python3 scripts/doc_lint.py skills portable` | exit 0 |
| Q5 | Cờ `--no-qc` hoạt động và chặn đúng | trong sandbox: `init q quick`, rồi `approve quick --no-qc --by "duyệt quick không QC" 2>&1`, rồi `get quick_qc_skipped`, rồi `approve spec --no-qc` | lệnh approve exit 0 và có 1 dòng khớp `^\[.*\] ℹ️`; `get` in đúng `true` (JSON, chữ thường); `approve spec --no-qc` exit ≠ 0, thông báo nêu rõ `--no-qc` chỉ dùng cho quick |
| Q6 | 5 nguồn cùng phát biểu 3 hạng mục QC và trần 3 vòng | `grep -l "trần 3 vòng" skills/tdq-intake/references/quick-lane.md skills/tdq-intake/SKILL.md portable/workflow/references/quick-lane.md \| wc -l` và `grep -c "trần 3 vòng" skills/tdq-conventions/references/phases.md portable/workflow/phases.md` | lệnh 1 in đúng `3` (đếm file khớp, không nhận exit code thay); lệnh 2 mỗi file ≥ 1 |
| Q7 | Biên & đường lỗi của cờ mới | trong sandbox, 3 biến thể: `approve quick --no-qc` (thiếu `--by`), `approve quick --no-qc lạ`, `approve quick --no-qc --no-qc --by "x"` | cả 3 không có `Traceback`; thiếu `--by` exit ≠ 0 kèm thông báo tiếng Việt nêu rõ phải có `--by` |
| Q8 | QC độc lập | gọi agent `tdq-qc-tester` với plan + spec này | trả PASS kèm bằng chứng cho Q1–Q7 |

**DoD:** đủ 7 đầu ra §2 tồn tại · Q1–Q8 PASS có bằng chứng trong `docs/tdq/qc/2026-08-07-siet-qc-lane-quick.md` · mọi task trong plan tick `[x]` · `docs/tdq/reports/2026-08-07-siet-qc-lane-quick.md` đã viết · working log 2026-08-07 có mục cho từng turn build.

## 7. Câu hỏi còn mở

(RỖNG — 12/12 câu interview đã có đáp, xem `questions/2026-08-07-siet-qc-lane-quick.md`.)
