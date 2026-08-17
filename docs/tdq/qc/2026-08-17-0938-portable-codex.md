# QC — Bộ portable tự sinh cho hai harness

Request: `2026-08-17-0938-portable-codex` · Ngày kiểm: 2026-08-17
Người kiểm: agent `tdq-qc-tester` (độc lập, không viết code này)
Spec: `../spec/2026-08-17-0938-portable-codex.md` §6 · Plan: `../plan/2026-08-17-0938-portable-codex.md`

Thư mục tạm dùng chung cho mọi hạng mục:
`SP=/private/tmp/claude-501/-Users-truongdinhquoc-Documents-TDQWorkflow/d64f9bf9-f202-411c-9230-8b9835cbf4ee/scratchpad`

## Bảng phán quyết

| # | Hạng mục DoD | Lệnh | Output thật | Kết quả |
|---|---|---|---|---|
| Q1 | Test tự động toàn bộ | `python3 -m pytest tests/ -q` | `733 passed, 375 subtests passed in 39.52s` · `EXIT=0` | PASS |
| Q2 | Sinh được cả hai bản | `python3 scripts/build_portable.py --dest $SP/tdqp` | `EXIT=0`; `ls -d` thấy cả `portable_claude` và `portable_codex` | PASS |
| Q3 | Không sót biến plugin | `grep -rI "CLAUDE_PLUGIN_ROOT" $SP/tdqp/portable_claude \| wc -l` | `0` (bản codex cũng `0`; grep kể cả binary trên cả cây: `0`) | PASS |
| Q4 | Manifest khớp thực tế | `python3 scripts/tdq_checkportable.py check --root $SP/tdqp/portable_claude` | `SẠCH   77 file khớp manifest` · `EXIT=0` (codex: `SẠCH 66 file`, `EXIT=0`) | PASS |
| Q5 | Phát hiện được hỏng | `printf '#' >> <root>/.claude/tdq/scripts/tdq_state.py` rồi chạy lại Q4 | `LỆCH   .claude/tdq/scripts/tdq_state.py` · `EXIT=1` — đúng 1 tên file, không báo thừa | PASS |
| Q6 | Phát hiện thiếu lệnh ngoài | `PATH=$SP/emptybin /usr/bin/python3 scripts/tdq_checkportable.py check --root ...` | `THIẾU  lệnh ngoài \`git\` chưa có trong PATH` · `EXIT=1`, không traceback | PASS |
| Q7 | Bản sinh không chứa rác | `find $SP/fresh -name state.json -o -name ".git" -o -name "graphify-out"` | (rỗng) — quét thêm `__pycache__/.pytest_cache/*.pyc/.DS_Store/.venv` cũng rỗng | PASS |
| Q8 | Skill không chép logic | `grep -c "def \|import " portable_claude/.claude/skills/tdq-checkportable/SKILL.md` | `0` (bản sinh tạm cũng `0`; nguồn `portable_src/...` cũng `0`) | PASS |
| Q9 | Bản cũ đã bỏ | `test -d portable && echo VAN CON \|\| echo DA XOA` | `DA XOA (false)` | PASS |
| Q10 | Log service hoạt động | xem mục "Log service" bên dưới | bật: 6 dòng có timestamp ISO; `TDQ_LOG=0`: `stderr 0 dòng, stdout 0 dòng` | PASS |
| Q11 | DoD dòng cuối: **README mỗi bản** nêu 3 giới hạn cứng + cảnh báo quyền setup | `find portable_codex -iname "README*"` | (rỗng) — `portable_codex/` **không có README.md**; spec §2 đầu ra #4 liệt kê `README.md` là bắt buộc | **FAIL** |

## Bốn hạng mục cố định

| # | Hạng mục | Bằng chứng | Kết quả |
|---|---|---|---|
| QC-F1 | Full suite đúng lệnh plan | `python3 -m pytest tests/ -q` → `733 passed, 375 subtests passed`, `EXIT=0` | PASS |
| QC-F2 | Hồi quy vùng chạm | `hooks/hooks.json` (đọc văn bản), `scripts/tdq_state.py` (chỉ đọc `PHASE_TABLE`), `portable/` (đã xoá) — toàn bộ suite gồm test của các node này đều xanh | PASS |
| QC-F3 | Ràng buộc kiến trúc spec §5 | `grep -n "import.*hooks\|from hooks" scripts/build_portable.py scripts/tdq_checkportable.py` → rỗng; hai file code mới đều nằm trong `scripts/`; không script nào ghi `state.json` (chuỗi duy nhất xuất hiện là mục EXCLUDE, dòng 55); skill chỉ nhắc lệnh (Q8=0) | PASS |
| QC-F4 | Clean code | Có vi phạm: `to_ten_khoa` là dead code + ternary hai nhánh giống hệt nhau (D5). Xem mục Khuyết tật. | **FAIL** |

## Bằng chứng chi tiết

### Q1 — full suite
```
$ python3 -m pytest tests/ -q ; echo "EXIT=$?"
733 passed, 375 subtests passed in 39.52s
EXIT=0
$ python3 -m pytest tests/test_build_portable.py tests/test_checkportable.py -q
32 passed in 0.89s
```

### Q2/Q3 — sinh bản + rewrite biến
```
$ python3 scripts/build_portable.py --dest $SP/tdqp ; echo "EXIT=$?"
[2026-08-17T10:44:45+07:00] manifest: 77 file trong portable_claude
[2026-08-17T10:44:45+07:00] portable_codex: 8 file workflow, còn sót 0 biến plugin
[2026-08-17T10:44:45+07:00] manifest: 66 file trong portable_codex
EXIT=0
$ grep -rI "CLAUDE_PLUGIN_ROOT" $SP/tdqp/portable_claude | wc -l   → 0
$ grep -rI "CLAUDE_PLUGIN_ROOT" $SP/tdqp/portable_codex  | wc -l   → 0
```
Rewrite là thật, không phải do loại file: nguồn `skills hooks agents .claude` có **56** chỗ
`CLAUDE_PLUGIN_ROOT`; log build ghi `đổi 64 chỗ dùng biến plugin, còn sót 0`; bản sinh có
**64** chỗ `CLAUDE_PROJECT_DIR`.

### Đường dẫn hook trong `.claude/settings.json` (yêu cầu số 4)
```
so su kien hook: 4 ['PreToolUse', 'SessionStart', 'Stop', 'UserPromptSubmit']
OK    .claude/tdq/hooks/scripts/bash_gate.py
OK    .claude/tdq/hooks/scripts/edit_gate.py
OK    .claude/tdq/hooks/scripts/prompt_context.py
OK    .claude/tdq/hooks/scripts/session_start.py
OK    .claude/tdq/hooks/scripts/stop_gate.py
```
Cả 5 script đều mang tiền tố `${CLAUDE_PROJECT_DIR}/.claude/tdq/hooks/scripts/` và **tồn tại
thật** trong bản sinh. PASS.

### Hook chạy được, import `tdq_state` không lỗi (yêu cầu số 5)
```
$ echo '{}' | TDQ_PROJECT_DIR=$SP/proj CLAUDE_PROJECT_DIR=$R python3 $R/.claude/tdq/hooks/scripts/session_start.py
EXIT=0   (không ImportError; 5/5 hook session_start, prompt_context, stop_gate, bash_gate, edit_gate đều EXIT=0)
```
Không phải fail-open: `_common.py` import ở top-level **không có try/except**
(`sys.path.insert(0, _SCRIPTS_DIR)` rồi `import tdq_state`), và stdout ra nội dung suy từ
state thật: `[TDQ:NEXT] chưa có request · phase idle · Project: ...`. PASS.

### `.mcp.json` không lộ giá trị khoá (yêu cầu số 3)
```
"env": { "TAVILY_API_KEY": "${TAVILY_API_KEY}" }   ← chỉ TÊN biến
gia tri secret bi lo: KHONG CO
```
Quét cả cây bản sinh `grep -rIn "tvly-\|sk-ant\|ghp_\|AKIA..."` → không kết quả. PASS.

### Log service (Q10, yêu cầu số 8)
```
$ python3 scripts/build_portable.py --dest $SP/lg1          → stderr 6 dòng
[2026-08-17T10:46:53+07:00] bắt đầu · repo=... · dest=... · version=0.23.0
[2026-08-17T10:46:53+07:00] portable_claude: đổi 64 chỗ dùng biến plugin, còn sót 0
$ TDQ_LOG=0 python3 scripts/build_portable.py --dest $SP/lg2 → stderr 0 dòng | stdout 0 dòng
$ python3 scripts/tdq_checkportable.py check --root ...      → stderr 1 dòng
[2026-08-17T10:46:53+07:00] check · root=...
$ TDQ_LOG=0 python3 scripts/tdq_checkportable.py check ...   → stderr 0 dòng
```
Cả hai script: bật mặc định, timestamp ISO kèm offset, ra stderr, `TDQ_LOG=0` im hoàn toàn. PASS.

### Không placeholder (yêu cầu số 10)
```
$ grep -n "TODO\|FIXME\|XXX\|HACK\|placeholder\|NotImplemented\|stub" scripts/build_portable.py scripts/tdq_checkportable.py
(rỗng)
$ grep -n "^\s*pass\s*$\|raise NotImplementedError" ...   (rỗng)
$ python3 -m py_compile scripts/build_portable.py scripts/tdq_checkportable.py   → COMPILE OK
```
Không có chuỗi placeholder. PASS về mặt từ khoá — nhưng xem D3/D5: `setup` và `to_ten_khoa`
là stub *về hành vi* dù không mang chữ TODO.

### Kiểm ngoài happy path
| Tình huống | Lệnh | Kết quả | Đánh giá |
|---|---|---|---|
| Thiếu `manifest.json` | `check --root <thư mục rỗng>` | `LỖI  không thấy manifest.json trong ...` `EXIT=1` | Tốt |
| `manifest.json` hỏng JSON | `check --root $SP/bad1` | `LỖI  Expecting property name enclosed in double quotes...` `EXIT=1` | Tốt |
| Root không tồn tại | `check --root $SP/khong-co-that` | `LỖI  không thấy manifest.json` `EXIT=1` | Tốt |
| Lệnh sai / thiếu lệnh | `tdq_checkportable.py linhtinh` | `invalid choice` `EXIT=2` — đúng docstring | Tốt |
| `--only linhtinh` | `build_portable.py --only linhtinh` | `EXIT=2` | Tốt |
| `--only claude` / `--only codex` | | `EXIT=0`, chỉ sinh đúng 1 thư mục | Tốt |
| `manifest` rỗng khối `files` | `check --root $SP/e5` | `SẠCH  0 file khớp manifest` `EXIT=0` | D6 — báo sạch với manifest vô nghĩa |
| Sinh lại 2 lần | `diff -r $SP/rep1 $SP/rep2` | `0 dòng khác` | Tái lập được |
| Trôi so với bản trong repo | `diff -r portable_claude $SP/fresh/portable_claude` | `0 dòng` (codex cũng `0`) | Không trôi |

### Manifest 5 khối
```
portable_claude khoa: ['external_commands','files','mcp_servers','python_min','version'] | du 5 khoi: True | version: 0.23.0 | python_min: 3.8
portable_codex  khoa: (như trên) | du 5 khoi: True
```
PASS.

## Khuyết tật phát hiện

### D1 — NGHIÊM TRỌNG: lệnh "Bước 0" mà bản claude tự hướng dẫn thì chạy FAIL
`tdq_checkportable.py` suy root mặc định bằng `dirname(dirname(__file__))` (dòng 177). Trong
bản claude script nằm ở `.claude/tdq/scripts/`, nên root mặc định ra `.claude/tdq` — trong khi
`manifest.json` nằm ở **gốc bundle**. Mọi tài liệu của bản claude đều bảo chạy KHÔNG có `--root`:
- `portable_claude/.claude/skills/tdq-checkportable/SKILL.md:15` và `:24`
- `portable_claude/README.md:17`

Repro (trên bản sinh hoàn toàn sạch, vừa PASS Q4):
```
$ cd $SP/fresh/portable_claude
$ python3 .claude/tdq/scripts/tdq_checkportable.py check
LỖI    không thấy manifest.json trong .../portable_claude/.claude/tdq
EXIT=1
```
Bản codex không dính (script ở `scripts/`, root suy ra đúng gốc bundle → `SẠCH 66 file`, `EXIT=0`).
Đây đúng là rủi ro R1 của spec: người dùng ở máy khác chạy bước đầu tiên là thấy lỗi trên một
bộ hoàn toàn lành lặn. Nghi ở: `scripts/tdq_checkportable.py:177` (hoặc SKILL.md/README thiếu `--root`).

### D2 — CAO: `portable_codex/` thiếu hẳn `README.md`
Spec §2 đầu ra #4 đo "xong" bằng: có `AGENTS.md`, `workflow/`, `scripts/`, `manifest.json`,
**`README.md`**; DoD cuối spec: "README **mỗi bản** nêu rõ ba giới hạn cứng ... và cảnh báo
quyền tự setup".
```
$ ls -a portable_codex        → AGENTS.md  manifest.json  scripts  workflow   (không có README.md)
$ find portable_codex $SP/fresh/portable_codex -iname "README*"   → (rỗng)
```
Nội dung ba giới hạn có tồn tại nhưng nằm trong `AGENTS.md:32-34`, không phải README.
Test canh cửa `tests/test_build_portable.py:228 test_readme_neu_du_3_gioi_han` chỉ đọc
`self.claude`, nên lỗ hổng này không bị suite bắt. Nghi ở: `scripts/build_portable.py`
(hàm sinh bản codex) + `tests/test_build_portable.py:228`.

### D3 — CAO: `setup` không vá gì, vẫn exit 0 trên bundle hỏng; nhánh backup không bao giờ chạy
`chay_setup` (`scripts/tdq_checkportable.py:138-147`) chỉ `os.makedirs` cho thư mục cha của file
thiếu, rồi dừng. Không chép lại file, không cài gói, không đụng cấu hình user-level.
```
$ rm <root>/.claude/tdq/scripts/tdq_state.py ; printf 'X' >> <root>/README.md
$ python3 scripts/tdq_checkportable.py setup --root $SP/setuptest
ĐÃ LÀM (không có gì cần vá)          ← mâu thuẫn với 2 dòng ngay dưới
THIẾU  .claude/tdq/scripts/tdq_state.py
LỆCH   README.md
EXIT=0                                ← bundle hỏng nhưng vẫn báo thành công
$ find $SP/setuptest -name "*.tdq-bak-*"   → (rỗng)
$ test -f <root>/.claude/tdq/scripts/tdq_state.py → VAN THIEU
```
Khi thiếu cả thư mục thì `setup` tạo **thư mục rỗng** rồi vẫn `EXIT=0`:
`ĐÃ LÀM tạo thư mục .claude/tdq/hooks` + `THIẾU .claude/tdq/hooks/hooks.json`.
Hệ quả nặng hơn: `ghi_de_co_backup` (dòng 121) — thứ hiện thực yêu cầu bắt buộc §4(b) của spec —
**không có caller nào trong mã sản phẩm**:
```
$ grep -rn "ghi_de_co_backup" scripts/ tests/
scripts/tdq_checkportable.py:121:def ghi_de_co_backup(...)
tests/test_checkportable.py:85:  tdq_checkportable.ghi_de_co_backup(...)   ← chỉ test gọi
```
Nên `test_setup_backup_truoc_khi_ghi_de` kiểm hàm trợ giúp chứ không kiểm lệnh `setup`;
yêu cầu "backup trước khi ghi đè" đúng một cách rỗng vì `setup` chẳng bao giờ ghi đè.
Nghi ở: `scripts/tdq_checkportable.py:138-147` và `:186-192`.

### D4 — TRUNG BÌNH: tài liệu bản sinh tuyên bố năng lực `setup` không hề tồn tại
Bốn chỗ hứa `setup` tự cài gói / sửa cấu hình mức người dùng / luôn sao lưu:
`portable_claude/README.md:15-16`, `portable_claude/.claude/skills/tdq-checkportable/SKILL.md:27`,
`portable_codex/workflow/06-checkportable.md:27`, `portable_codex/AGENTS.md:14-15`.
Trong khi mã không có bất kỳ đường nào làm việc đó:
```
$ grep -n "pip\|subprocess\|install\|expanduser\|~/.claude" scripts/tdq_checkportable.py
(rỗng)
```
Người dùng được cảnh báo về một quyền mà công cụ không dùng, và tin vào một cơ chế tự vá không có.

### D5 — THẤP (QC-F4 clean code): dead code + nhánh rẽ vô nghĩa
`to_ten_khoa` (`scripts/tdq_checkportable.py:56-63`) không được mã sản phẩm nào gọi (chỉ
`tests/test_checkportable.py:101`), tức T4.4 "mọi đường in ra chỉ in TÊN khoá" chưa được nối vào
đường in thật. Trong chính hàm đó, dòng 62 có ternary hai nhánh **giống hệt nhau**:
```python
dong.append(f"{ten}: {co}" if nhay_cam else f"{ten}: {co}")
```
→ `nhay_cam` (dòng 60) tính xong bị bỏ, `DAU_HIEU_BI_MAT` trở nên vô dụng.

### D6 — THẤP: manifest rỗng vẫn được báo "SẠCH"
`check` với `{"files":{}, ...}` in `SẠCH 0 file khớp manifest`, `EXIT=0`. Manifest cụt/rỗng lẽ ra
phải bị coi là bất thường. Nghi ở: `scripts/tdq_checkportable.py:163-166`.

## Kết luận

10 hạng mục Q1–Q10 của spec §6 đều PASS trên máy kiểm. Nhưng **DoD chưa đạt trọn**: dòng cuối
DoD (README mỗi bản) FAIL vì `portable_codex/README.md` không tồn tại (D2), QC-F4 FAIL (D5), và
nghiêm trọng nhất là D1 — lệnh khởi đầu mà chính bản claude hướng dẫn thì chạy lỗi trên bộ sạch,
đúng kịch bản rủi ro R1 mà spec đặt ra để QC phải bắt.

**VERDICT: FAIL** — Q11 (README bản codex), QC-F4, cộng khuyết tật D1 và D3 nằm ngoài bảng Q
nhưng phá đúng mục tiêu "copy một thư mục là dùng được" của spec §1.

---

## Vòng 2 — kiểm lại sau vòng fix (2026-08-17, agent `tdq-qc-tester`, độc lập)

Phạm vi: xác minh 5 khuyết tật D1/D2/D3/D4/D6 đã hết + hồi quy. Lịch sử vòng 1 giữ nguyên ở trên.
`SP=/private/tmp/claude-501/-Users-truongdinhquoc-Documents-TDQWorkflow/d64f9bf9-f202-411c-9230-8b9835cbf4ee/scratchpad`
Bundle kiểm: sinh mới vào `$SP/r2` (`build_portable.py --dest $SP/r2`, EXIT=0) — `diff -r` với
`portable_claude/`+`portable_codex/` trong repo = 0 dòng, nên kết quả áp cho cả hai.

### Bảng khuyết tật vòng 1

| # | Khuyết tật vòng 1 | Lệnh đã chạy | Output thật | Kết quả |
|---|---|---|---|---|
| R2-1 | D1 — "Bước 0" chạy được không cần `--root` | `cd portable_claude && python3 .claude/tdq/scripts/tdq_checkportable.py check` | `SẠCH   77 file khớp manifest` · `EXIT=0` | ĐÃ SỬA |
| R2-1b | D1 bản codex | `cd portable_codex && python3 scripts/tdq_checkportable.py check` | `SẠCH   67 file khớp manifest` · `EXIT=0` | ĐÃ SỬA |
| R2-1c | D1 với cwd ngoài bundle (`cd /`) | `python3 $SP/r2/portable_claude/.claude/tdq/scripts/tdq_checkportable.py check` | `SẠCH   77 file khớp manifest` · `EXIT=0` | ĐÃ SỬA |
| R2-2 | D2 — `portable_codex/README.md` + 3 giới hạn cứng | `find $SP/r2 -iname "README*"` ; đọc file | Có `portable_codex/README.md`; mục "Ba việc máy KHÔNG tự làm được": `1. Tin cậy thư mục` / `2. Duyệt MCP server` / `3. Khởi động lại` | ĐÃ SỬA |
| R2-3a | D3 — xoá `.mcp.json` rồi `setup` | `rm $R/.mcp.json; … setup --root $R` | `ĐÃ LÀM sinh lại .mcp.json` · `SẠCH 77 file` · `EXIT=0`; `check` ngay sau: `SẠCH 77 file` `EXIT=0` | ĐÃ SỬA |
| R2-3b | D3 — xoá `tdq_state.py` rồi `setup` phải nói thật | `rm $R/.claude/tdq/scripts/tdq_state.py; … setup --root $R` | `CÒN    .claude/tdq/scripts/tdq_state.py (chép lại từ bản gốc)` · `EXIT=1` | ĐÃ SỬA |
| R2-3c | D3 — file LỆCH 1 byte rồi `setup` | `printf 'X' >> $R/README.md; … setup --root $R` | `CÒN    README.md (chép lại từ bản gốc)` · `EXIT=1` | ĐÃ SỬA |
| R2-3d | D3 — ghi đè `settings.json` để lại `.tdq-bak-` | hỏng khối `hooks` rồi `setup --root $R`; `find $R -name "*.tdq-bak-*"` | log `sao lưu settings.json → settings.json.tdq-bak-20260817-105800`; file backup tồn tại thật | ĐÃ SỬA |
| R2-3e | D3 — `ghi_de_co_backup` có caller sản phẩm | `grep -rn "ghi_de_co_backup" scripts/` | `scripts/tdq_checkportable.py:198:    ghi_de_co_backup(duong, noi_dung)` (trong `_ghi_json_co_backup`) | ĐÃ SỬA |
| R2-4 | D4 — tài liệu bản sinh không hứa quá năng lực | `grep -rn "tự cài\|cài gói\|mức người dùng\|user-level\|~/.claude\|install\|pip " <4 file tài liệu>` | không kết quả (`GREP_EXIT=1`) | ĐÃ SỬA (còn sót ở docstring — xem D7) |
| R2-5 | D6 — `manifest.files` rỗng | `check --root <manifest files rỗng>` | `LỖI   manifest không liệt kê file nào — bản portable hỏng, chép lại từ gốc` · `EXIT=1` | ĐÃ SỬA |
| R2-5b | D6 — manifest thiếu hẳn khoá `files` | `check --root $SP/e_nofiles` | cùng thông điệp trên · `EXIT=1` | ĐÃ SỬA |

### Bảng hồi quy

| # | Hạng mục | Lệnh đã chạy | Output thật | Kết quả |
|---|---|---|---|---|
| H1 | Toàn bộ test suite | `python3 -m pytest tests/ -q` | `738 passed, 375 subtests passed in 38.14s` · `EXIT=0` | PASS |
| H1b | Hai file test của request | `python3 -m pytest tests/test_build_portable.py tests/test_checkportable.py -q` | `37 passed in 1.18s` · `EXIT=0` | PASS |
| H2 | Q2 sinh hai bản | `python3 scripts/build_portable.py --dest $SP/r2` | `EXIT=0`; có `portable_claude` + `portable_codex` | PASS |
| H3 | Q3 không sót biến plugin | `grep -rI CLAUDE_PLUGIN_ROOT $SP/r2/portable_{claude,codex} \| wc -l` | `0` và `0` | PASS |
| H4 | Q4 manifest khớp | `check --root $SP/r2/portable_claude` | `SẠCH 77` `EXIT=0` (codex `SẠCH 67` `EXIT=0`) | PASS |
| H5 | Q5 phát hiện sửa 1 byte | `printf '#' >> …/tdq_state.py` rồi `check` | `LỆCH   .claude/tdq/scripts/tdq_state.py` · `EXIT=1`, đúng 1 tên | PASS |
| H6 | Q6 thiếu lệnh ngoài | `PATH=$SP/emptybin /usr/bin/python3 … check` | `THIẾU  lệnh ngoài \`git\` chưa có trong PATH` · `EXIT=1`, không traceback | PASS |
| H7 | Q7 không mang rác | `find $SP/r2 \( -name state.json -o -name .git -o -name graphify-out -o -name __pycache__ -o -name "*.pyc" \) \| wc -l` | `0` | PASS |
| H8 | Q8 skill không chép logic | `grep -c "def \|import " portable_claude/.claude/skills/tdq-checkportable/SKILL.md` | `0` | PASS |
| H9 | Q9 bản cũ đã bỏ | `test -d portable` | `DA XOA` | PASS |
| H10 | Q10 log service | `build_portable.py` mặc định vs `TDQ_LOG=0` | mặc định `6` dòng stderr, dòng đầu `[2026-08-17T11:01:01+07:00] bắt đầu · repo=… · version=0.23.0`; `TDQ_LOG=0`: `stderr=0 stdout=0` (check cũng `stderr=0`) | PASS |
| H11 | 5 hook bản claude chạy được | `echo '{}' \| TDQ_PROJECT_DIR=… CLAUDE_PROJECT_DIR=$R python3 $R/.claude/tdq/hooks/scripts/<h>.py` | `session_start/prompt_context/stop_gate/bash_gate/edit_gate` đều `EXIT=0  ImportError=0` | PASS |
| H12 | `.mcp.json` chỉ tên biến | `cat $SP/r2/portable_claude/.mcp.json` ; `grep -rIn "tvly-\|sk-ant\|ghp_\|AKIA[0-9A-Z]" $SP/r2 \| wc -l` | `"TAVILY_API_KEY": "${TAVILY_API_KEY}"` ; quét secret = `0` | PASS |
| H13 | Không import vòng | `import tdq_checkportable, build_portable` (và ngược lại) | `order A ok True` / `order B ok True`; `grep "import build_portable" scripts/tdq_checkportable.py` → rỗng | PASS |
| H14 | Build vs setup khớp byte-for-byte | xoá `.mcp.json` + hỏng `hooks` trong `settings.json` → `setup` → `cmp` với bản build | `.mcp.json IDENTICAL`; `settings.json IDENTICAL` khi khối `env` còn nguyên → `SẠCH 77` `EXIT=0` | PASS (có ngoại lệ D8) |
| H15 | `setup` trên bundle sạch (idempotent) | `setup --root $SP/s7` rồi `check` | `ĐÃ LÀM (không có gì cần vá)` · `SẠCH 77` · cả hai `EXIT=0`; `find -name "*.tdq-bak-*"` = `0` | PASS |
| H16 | Không placeholder/TODO/stub | `grep -nE "TODO\|FIXME\|XXX\|HACK\|placeholder\|NotImplemented\|^\s*pass\s*$" scripts/{build_portable,tdq_checkportable}.py` | chỉ `tdq_checkportable.py:238: pass` — nằm trong `except ValueError:` (bắt lỗi thật, không phải stub); `py_compile` → `COMPILE OK` | PASS |
| H17 | Không trôi so với bản trong repo | `diff -r portable_claude $SP/r2/portable_claude` ; codex tương tự | `0` dòng cả hai | PASS |

### Kiểm ngoài happy path (vòng 2)

| Tình huống | Lệnh | Kết quả | Đánh giá |
|---|---|---|---|
| `--root` trỏ vào FILE | `check --root …/README.md` | `LỖI    không thấy manifest.json trong …/README.md` `EXIT=1` | Tốt |
| `--root ""` | `check --root ""` | rơi về cwd, `LỖI … trong /Users/…/TDQWorkflow` `EXIT=1` | Chấp nhận |
| sha256 trong manifest sai KIỂU (số) | `check --root $SP/bad9` | `LỆCH   a.txt` `EXIT=1`, không traceback | Tốt |
| `setup` trên manifest rỗng | `setup --root $SP/e_empty` | `LỖI   manifest không liệt kê file nào` `EXIT=1` | Tốt |
| `setup` trên thư mục CHỈ ĐỌC (`chmod 555`) | `setup --root $SP/ro` | `PermissionError: [Errno 13] … '.mcp.json'` + traceback | **D9** |
| `setup` trên bundle **codex** sạch | `setup --root $SP/s8` | `ĐÃ LÀM sinh lại .mcp.json` — tạo file không có trong manifest codex | **D10** |

### Khuyết tật còn lại / mới phát hiện ở vòng 2

- **D5 (vòng 1, CHƯA SỬA — THẤP)** `to_ten_khoa` vẫn là dead code (`grep -rn to_ten_khoa scripts/` chỉ
  ra định nghĩa dòng 63; caller duy nhất là `tests/test_checkportable.py:151`) và dòng 69 vẫn là
  ternary hai nhánh giống hệt nhau: `dong.append(f"{ten}: {co}" if nhay_cam else f"{ten}: {co}")`
  → `nhay_cam` (dòng 67) và hằng `DAU_HIEU_BI_MAT` (dòng 41) vô dụng. QC-F4 (clean code) vẫn FAIL.
- **D7 (mới, THẤP)** Docstring của chính script được ship vẫn hứa quá năng lực — đúng thứ D4 đi sửa:
  `scripts/tdq_checkportable.py:11` "tạo file/thư mục thiếu, **cài gói, sửa cả cấu hình mức người dùng**"
  và `:180` "được trao quyền sửa cả cấu hình mức người dùng". Mã không có đường nào:
  `grep -n "pip\|subprocess\|expanduser\|os.system" scripts/tdq_checkportable.py` → rỗng. File này
  đi theo cả hai bundle (`portable_claude/.claude/tdq/scripts/`, `portable_codex/scripts/`).
- **D8 (mới, THẤP)** Mất trắng `.claude/settings.json` thì `setup` KHÔNG dựng lại được khối `env`
  (nguồn `env` chỉ có ở repo gốc, không đi theo bundle) → in đồng thời `ĐÃ LÀM sinh lại
  .claude/settings.json` và `CÒN .claude/settings.json (chép lại từ bản gốc)`, `EXIT=1`, `cmp` với
  bản build báo `differ: char 6, line 2`. Exit code trung thực nên không chặn DoD, nhưng hai dòng
  thông điệp mâu thuẫn nhau.
- **D9 (mới, TRUNG BÌNH)** `setup` ném traceback `PermissionError` khi gốc bundle không ghi được,
  trái với chính nguyên tắc ghi trong docstring `kiem_moi_truong` ("một traceback ở đây nghĩa là
  người dùng mất luôn đường tự vá"). Repro: `chmod 555 <bundle>; python3 scripts/tdq_checkportable.py
  setup --root <bundle>`. Nghi ở `scripts/tdq_checkportable.py:189` (`ghi_de_co_backup`) — không
  bọc `OSError`.
- **D10 (mới, THẤP)** `chay_setup` ghi `.mcp.json` vô điều kiện, kể cả với bản codex vốn không có
  file đó trong manifest và harness codex không đọc `.mcp.json` → `setup` tạo rác ngoài manifest ở
  gốc project người dùng. Nghi ở `scripts/tdq_checkportable.py:225-227`.

### Kết luận vòng 2

Cả 5 khuyết tật được giao kiểm lại (D1, D2, D3, D4, D6) đều ĐÃ SỬA và xác minh bằng lệnh chạy thật.
Hồi quy H1–H17 PASS toàn bộ, không có hồi quy mới trên DoD Q1–Q10.
Còn D5 từ vòng 1 chưa sửa (QC-F4 clean code) và 4 khuyết tật nhỏ mới lộ ra khi dò ngoài happy path.

**VERDICT vòng 2: PASS có điều kiện** — DoD Q1–Q10 + 5 khuyết tật vòng 1 đều PASS; FAIL còn lại
duy nhất là QC-F4 (D5, dead code + ternary trùng nhánh), cộng D7–D10 mức THẤP/TRUNG BÌNH không
chạm DoD.

---

## Vòng 3 — kiểm lại sau vòng fix 2 (2026-08-17, agent `tdq-qc-tester`, độc lập)

Phạm vi: 5 điểm còn lại từ vòng 2 (D5, D9, D7, D8, D10) + hồi quy. Vòng 1 và 2 giữ nguyên ở trên.
Bundle kiểm: sinh mới `python3 scripts/build_portable.py --dest $SP/r3` (`BUILD_EXIT=0`);
`diff -r` với `portable_claude/`+`portable_codex/` trong repo = 0 → kết quả áp cho cả hai.

### Bảng 5 khuyết tật vòng 2

| # | Khuyết tật | Lệnh đã chạy | Output thật | Kết quả |
|---|---|---|---|---|
| V3-1a | D5 — `to_ten_khoa` có caller sản phẩm | `grep -n "to_ten_khoa\|bien_moi_truong_mcp" scripts/tdq_checkportable.py` | `:81 return to_ten_khoa(…)` trong `bien_moi_truong_mcp`; `:278 for dong in bien_moi_truong_mcp(manifest)` (trong `_in_ket_qua`) — caller sản phẩm thật, không chỉ test | ĐÃ SỬA |
| V3-1b | D5 — ternary hai nhánh trùng đã hết | `grep -n "if nhay_cam else" scripts/tdq_checkportable.py` | không kết quả (`GREP=1`); hàm nay là list-comprehension một nhánh, dòng 64-70 | ĐÃ SỬA |
| V3-1c | D5 — `check` in tên biến, KHÔNG lộ giá trị | `TAVILY_API_KEY='tvly-FAKE-SECRET-9z9z9z' python3 scripts/tdq_checkportable.py check --root $SP/r3/portable_claude` | `LƯU Ý  biến TAVILY_API_KEY: đã đặt` · grep giá trị giả trong stdout = `0`, trong stderr = `0` | ĐÃ SỬA |
| V3-1d | D5 — phân biệt đã/chưa đặt | `env -u TAVILY_API_KEY … check` | `LƯU Ý  biến TAVILY_API_KEY: CHƯA đặt` | ĐÃ SỬA |
| V3-1e | D5 — `setup` cũng không lộ giá trị | `TAVILY_SECRET_X='tvly-LEAKME-1234' … setup --root $SP/g4` | `LƯU Ý  biến TAVILY_SECRET_X: đã đặt`; grep giá trị = `0` | ĐÃ SỬA |
| V3-2a | D9 — `setup` trên bundle chỉ đọc, có việc phải ghi | `rm $RO/.mcp.json; chmod -R 555 $RO; setup --root $RO` | `LỖI   không ghi được vào bundle: [Errno 13] Permission denied: …/.mcp.json` + `sửa quyền thư mục (chmod -R u+w) rồi chạy lại setup` · `Traceback=0` · `EXIT=1` | ĐÃ SỬA |
| V3-2b | D9 — nhánh ghi đè (backup) trên bundle chỉ đọc | hỏng khối `hooks` rồi `chmod -R 555`; `setup` | `LỖI   không ghi được vào bundle: … settings.json.tdq-bak-20260817-110651` · `Traceback=0` · `EXIT=1` | ĐÃ SỬA |
| V3-2c | D9 — chỉ đọc nhưng bundle sạch | `chmod -R 555 $SP/ro3; setup` | `ĐÃ LÀM (không có gì cần vá)` · `Traceback=0` · `EXIT=0` (đúng: không có việc ghi nào) | ĐÃ SỬA |
| V3-3 | D7 — docstring không còn hứa quá năng lực | `grep -n "cài gói\|mức người dùng\|user-level\|tự cài" scripts/tdq_checkportable.py` | không kết quả (`GREP_EXIT=1`); quét cả bundle sinh mới `grep -rIn "cài gói\|mức người dùng" $SP/r3/` cũng rỗng. Docstring module nay ghi `vá phần vá được…`; `ghi_de_co_backup` ghi `file bị ghi đè có thể mang thứ người dùng tự thêm (khối env…)` | ĐÃ SỬA |
| V3-4 | D8 — xoá hẳn `.claude/settings.json` rồi `setup` | `rm $R/.claude/settings.json; setup --root $R` | `ĐÃ LÀM sinh lại .claude/settings.json (phần hook; khối \`env\` không tái tạo được — chép lại từ bản gốc nếu bạn từng thêm biến ở đó)` + `CÒN .claude/settings.json` · `EXIT=1` — không còn đọc như tự mâu thuẫn | ĐÃ SỬA |
| V3-5 | D10 — `setup` trên bản codex không tạo `.mcp.json` | `setup --root $SP/d10` rồi `ls -a`, rồi `check` | `ĐÃ LÀM (không có gì cần vá)` · `SETUP_EXIT=0`; đếm `.mcp.json` = `0`; `check` → `SẠCH 67 file khớp manifest` `CHECK_EXIT=0` | ĐÃ SỬA |

### Bảng hồi quy vòng 3

| # | Hạng mục | Lệnh đã chạy | Output thật | Kết quả |
|---|---|---|---|---|
| G1 | Toàn bộ suite | `python3 -m pytest tests/ -q` | `743 passed, 375 subtests passed in 37.86s` · `EXIT=0` | PASS |
| G1b | Hai file test của request | `python3 -m pytest tests/test_build_portable.py tests/test_checkportable.py -q` | `42 passed in 1.43s` · `EXIT=0` | PASS |
| G2 | `check` không cần `--root`, CẢ HAI bản (repo) | `cd portable_claude && python3 .claude/tdq/scripts/tdq_checkportable.py check` / codex tương tự | `claude EXIT=0` · `codex EXIT=0` | PASS |
| G2b | như trên, trên bản sinh mới `$SP/r3` | cùng lệnh | `SẠCH 77 file khớp manifest` · `SẠCH 67 file khớp manifest` | PASS |
| G3 | 0 `CLAUDE_PLUGIN_ROOT` hai bản | `grep -rI CLAUDE_PLUGIN_ROOT $SP/r3/portable_{claude,codex} \| wc -l` | `0` và `0` | PASS |
| G4 | Không trôi so với repo | `diff -r portable_claude $SP/r3/portable_claude` (và codex) | `claude diff=0` · `codex diff=0` | PASS |
| G5 | D3 vẫn đúng — xoá `.mcp.json` rồi `setup` | `rm $R/.mcp.json; setup; check; cmp` | `ĐÃ LÀM sinh lại .mcp.json` · `CHECK_EXIT=0` · `mcp IDENTICAL` (byte-for-byte với đường build) | PASS |
| G6 | D6 vẫn đúng — manifest `files` rỗng | `check --root $SP/g2` | `LỖI   manifest không liệt kê file nào…` · `EXIT=1` | PASS |
| G7 | Q5 phát hiện sửa 1 byte | `printf '#' >> …/tdq_state.py; check` | `LỆCH   .claude/tdq/scripts/tdq_state.py` · `EXIT=1` | PASS |
| G8 | Q6 thiếu lệnh ngoài | `PATH=$SP/emptybin /usr/bin/python3 … check` | `THIẾU  lệnh ngoài \`git\` chưa có trong PATH` · `EXIT=1`, không traceback | PASS |
| G9 | 5 hook bản claude | chạy từng hook bản sinh mới | cả 5 `EXIT=0 ImportErr=0` | PASS |
| G10 | Log service | `check` mặc định vs `TDQ_LOG=0` | mặc định: `[2026-08-17T11:08:11+07:00] check · root=…`; `TDQ_LOG=0`: `stderr=0` | PASS |
| G11 | Không placeholder/TODO | `grep -nE "TODO\|FIXME\|NotImplemented\|placeholder" scripts/tdq_checkportable.py scripts/build_portable.py` | không kết quả (`GREP=1`) | PASS |
| G12 | Không import vòng | `import` hai chiều | `A ok True` · `B ok True` | PASS |

### Kết luận vòng 3

Cả 5 điểm còn lại từ vòng 2 (D5, D7, D8, D9, D10) đều ĐÃ SỬA, xác minh bằng lệnh chạy thật.
QC-F4 (clean code) — điểm FAIL duy nhất còn lại của vòng 2 — nay PASS: `to_ten_khoa` có caller
sản phẩm qua `bien_moi_truong_mcp`, ternary trùng nhánh đã hết, và đường in mới được kiểm là
KHÔNG lộ giá trị khoá (grep giá trị giả trong stdout/stderr = 0).
Hồi quy G1–G12 PASS toàn bộ; không phát sinh khuyết tật mới.

**VERDICT vòng 3: PASS toàn bộ** — không còn hạng mục FAIL.
