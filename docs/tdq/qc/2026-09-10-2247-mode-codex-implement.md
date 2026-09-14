# QC — Mode thứ ba: `codex implement`
Ngày: 2026-09-12 · Plan: ../plan/2026-09-10-2247-mode-codex-implement.md · Vòng: 1
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

Phần này ghi hai phép kiểm CHẠY THẬT của T10.2. Chạy thật nghĩa là gọi đúng file thật với
payload thật rồi soi hiệu ứng trên đĩa — không mock, không đọc lại kết quả của test suite.

| # | Hạng mục | Lệnh đã chạy | Kết quả | PASS/FAIL |
|---|---|---|---|---|
| Q13 | Sandbox chặn ghi ra ngoài repo và ngoài `/tmp`, `$TMPDIR` | `python3 scripts/tdq_codex.py check` | `KHÔNG chạy được · có codex nhưng bạn chưa duyệt cho workflow gọi nó` → không gọi được `codex exec` thật | SKIP (có tuyên bố) |
| Q14 | Hook deny chặn thật một lượt | 3 lượt `hooks/scripts/codex_edit_gate.py` với payload `apply_patch` thật, biến mốc `TDQ_CODEX_TASK=T10.2`, `TDQ_CODEX_VUNG=["src"]`, `TDQ_CODEX_KHOA=["tests"]`; sau đó `test ! -e /tmp/qc-hook/ngoai-vung.py` | ngoài vùng → `permissionDecision: deny` kèm `[TDQ:VUNG]`; vùng khoá → `deny` kèm câu "Codex không được sửa file test"; trong vùng → không chặn, exit 0; file đích KHÔNG tồn tại | PASS |

## Q13 — vì sao SKIP, và SKIP này có giá trị gì

Cờ đồng ý mức máy (`docs/tdq/.tdq-codex.json`) đang là `false` trên máy này. Bật hộ cờ đó rồi
gọi `codex exec` là tự quyết thay người dùng đúng cái quyết định mà cả mode này được dựng để
không tự quyết — nên phép kiểm dừng ở đây thay vì đi vòng.

Mở lại phép kiểm này bằng hai lệnh, theo đúng thứ tự:

```
python3 scripts/tdq_checkportable.py setup --codex
python3 scripts/tdq_codex.py setup-model <ten-model>
```

Sau đó chạy một lượt `run` có `--vung` trỏ vào repo rồi yêu cầu ghi ra một đường ngoài repo,
ngoài `/tmp` và ngoài `$TMPDIR`; đạt khi đường đó không tồn tại sau lượt chạy.

Cho tới lúc ấy, lớp quyết định của mode KHÔNG phải sandbox mà là hậu kiểm `git diff` trong
`scripts/tdq_vungfile.py` — lớp này chạy được trên máy không có `codex`, và có test riêng.

## Q14 — nguyên văn ba lượt

```
### ngoài vùng
{"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny",
 "permissionDecisionReason": "[TDQ:VUNG] `ngoai-vung.py` nằm ngoài VÙNG FILE đã khai cho task
 — sửa đúng file trong vùng, hoặc báo leader nới vùng."}}
### vùng khoá
{"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny",
 "permissionDecisionReason": "[TDQ:VUNG] `tests/test_a.py` nằm trong VÙNG KHOÁ của task —
 Codex không được sửa file test — sửa đúng file trong vùng, hoặc báo leader nới vùng."}}
### trong vùng
(không in gì, exit 0 — không chặn)
```

Lượt thứ ba là phần quan trọng nhất của phép kiểm: một hàng rào chặn cả việc hợp lệ sẽ bị tắt,
và lúc đó mất luôn phần nó chặn đúng.

## Vòng 2 — chạy hết Definition of Done (2026-09-12 12:00)

Mọi lệnh `unittest` chạy bằng `python3 -m unittest discover tests -p "<file>.py"` (gọi thẳng
`-m unittest tests.test_X` đỏ oan vì `import helper` cần `tests/` nằm trên sys.path).

| # | Kết quả | Bằng chứng |
|---|---|---|
| Q1 | PARTIAL | `check --json` → `{"co": true, "chay_duoc": false, "ly_do": "có `codex` nhưng bạn chưa duyệt cho workflow gọi nó"}`. Máy CÓ `codex` nhưng cờ đồng ý đang false nên `chay_duoc`/`phien_ban` không đo được; `modes --json` trả đúng 3 mode, `codex` `chon_duoc=false` kèm lý do |
| Q2 | PASS | `test_codex_cli` + `test_state` OK |
| Q3 | PASS | `test_codex_cli` OK |
| Q4 | PASS | `test_checkportable` OK |
| Q5 | PASS | `test_mode_phase` + `test_state` OK |
| Q6 | PASS | `test_phase_table` OK |
| Q7 | PASS | `test_team_mode` OK |
| Q8 | PASS | `test_codex_run` OK |
| Q9 | PASS | `test_codex_run` OK |
| Q10 | PASS | `test_codex_run` OK |
| Q11 | PASS | `test_vungfile` OK |
| Q12 | PASS | `test_vungfile` OK |
| Q13 | SKIP (tuyên bố ở trên) | cờ đồng ý false — không tự bật |
| Q14 | PASS | `test_codex_edit_gate` OK + ba lượt chạy thật ở vòng 1 |
| Q14b | PASS | `test_vungfile` + `test_codex_edit_gate` OK |
| Q14c | PASS | `test_codex_run` OK (log một lượt có cả `red=` và `green=`) |
| Q14d | PASS | `test_codex_hooks_json` OK; `.codex/hooks.json` gốc repo chỉ có khoá `description` + `hooks`, hai matcher `PreToolUse` |
| Q14e | PASS | `test_build_portable` OK (so `sha256` `.codex/` trước/sau build) |
| Q15 | PASS | `test_codex_edit_gate` OK |
| Q16 | PASS | `test_codex_run` OK |
| Q17 | PASS | `test_codex_run` OK |
| Q18 | PASS | `test_codex_run` OK |
| Q19 | PASS | `test_codex_run` OK; `git check-ignore -q docs/tdq/.tdq-codex-prompt.log` exit 0, `docs/tdq/.tdq-codex.json` cũng bị ignore |
| Q20 | PASS | `test_prompt_context` OK |
| Q21 | PASS | `test_luat_mode` + `test_kien_truc` OK |
| Q21b | PARTIAL | tên biến `TDQ_CODEX_TASK/VUNG/KHOA` không chứa `KEY`/`TOKEN`/`SECRET` (kiểm được, PASS); nửa "sống qua sandbox" cần một lượt `codex exec` thật → SKIP cùng lý do Q13 |
| Q22 | PASS | `test_bench` OK |
| Q23 | PASS | `test_bench` OK |
| Q24 | FAIL (nợ có sẵn) | suite ra 290 fail / 4 error — ĐÚNG bằng danh sách đo ở HEAD trước request bằng worktree tách rời (`diff` hai danh sách rỗng). Request thêm 0 fail mới |
| Q25 | PASS | `grep -rn ADAPTER_CODEX scripts/ hooks/ skills/ portable_codex/` không ra dòng nào; bundle có `portable_codex/.codex/hooks.json` và `portable_codex/hooks/scripts/codex_edit_gate.py` |
| Q26 | PARTIAL | `doc_lint.py --pair` exit 0; `i18n_check.py` exit 1 trên 207 dòng tiếng Việt CÓ SẴN ở `scripts/hooks/agents` và 44 dòng ở `skills/` — bằng đúng số đo trước request, các file request chạm đã về 0 |
| Hồi quy Hub | PASS | `graphify extract . --code-only` (2322 node, 4939 cạnh); `affected` trên `scripts_tdq_state_cli`, `sinh_ban_codex()`, `_sinh_hooks_codex()` không có node vỡ. Ghi chú: `cmd_build()` trong plan là tên SAI — `build_portable.py` không có hàm đó |

### Ba hạng mục không PASS được bằng chính request này

1. **Q24** và nửa `i18n_check` của **Q26**: nợ có sẵn của repo, nằm ngoài `Chạm:` của request.
   Vá chúng là một request riêng — sửa lẫn vào đây thì không ai tách được lỗi mới với lỗi cũ.
2. **Q13** và nửa sau của **Q21b**: cần gọi `codex exec` thật, tức cần người dùng bật cờ đồng ý.
   Lệnh mở lại đã ghi nguyên văn ở mục Q13 phía trên.
