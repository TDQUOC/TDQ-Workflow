# QC — Bản portable_codex dùng đúng cơ chế native của Codex CLI

Ngày: 2026-08-17 · Plan: ../plan/2026-08-17-1139-codex-native-layers.md
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## Trinh sát

Phần này chốt rủi ro **R2** của spec (§5) bằng số đo từ `codex` chạy thật, không suy đoán.
Bản đã kiểm: `codex-cli 0.147.0-alpha.6.5` tại
`/Applications/ChatGPT.app/Contents/Resources/codex`. Mọi lượt chạy đều đặt
`CODEX_HOME=<thư mục tạm>` nên **không lượt nào chạm `~/.codex` thật** (quy tắc 7 của plan).

Công cụ đo: `tests/probe_codex_hook.py` — cắm vào cả 5 event, ghi mỗi lần gọi một dòng JSON
gồm `os.getcwd()` của tiến trình hook, `argv`, và nguyên payload stdin.

### K1 — Hook bị chặn bởi một cổng tin cậy THỨ HAI, ngoài `trust_level`

Ba lượt chạy đầu (hook đặt ở `~/.codex/hooks.json`, rồi `<project>/.codex/hooks.json`, rồi cả
hai) đều **không sinh một dòng nào** trong file thăm dò, dù project đã `trust_level = "trusted"`.
Đọc chuỗi trong binary tìm ra nguyên nhân: mỗi hook còn phải qua một **hash tin cậy** riêng —
`[hooks.state].<key>` giữ `enabled` + `trusted_hash`, và việc duyệt chỉ làm được trong TUI
("Review hooks" → "Trust all and continue"; sửa file rồi thì hiện "Modified since last trusted -
review required"). Không có lệnh CLI nào đặt được hash này; thử tự dựng hash (sha256 của
`hooks.json` theo 6 dạng khoá) đều trượt — đây là chốt an toàn cố ý, không phải lỗi.

Cửa thoát duy nhất là cờ `--dangerously-bypass-hook-trust` (biến `BYPASS_HOOK_TRUST`), tài liệu
của chính Codex mô tả là *"Run enabled hooks without requiring persisted hook trust for this
invocation. DANGEROUS."*. **Chỉ dùng cho phép đo ở đây, không đưa vào tài liệu bản portable như
cách dùng bình thường.** Hệ quả với sản phẩm: README phải nói người dùng cần **bốn** thao tác
tay, không phải ba — thêm bước duyệt hook trong TUI.

### K2 — cwd của tiến trình hook = gốc project

Lượt chạy với cờ bypass (`--cd <proj>`) cho kết quả trùng khít ở mọi event:

```
cwd_process = .../scratchpad/probe/proj
cwd payload = .../scratchpad/probe/proj
```

→ **Chốt nhánh đường dẫn TƯƠNG ĐỐI.** `.codex/hooks.json` viết được `command` dạng
`python3 hooks/scripts/<x>.py` và vẫn chạy đúng ở máy đích, nên file này nằm thẳng trong
`manifest.files` như mọi file tĩnh khác — **không phải sinh lúc `setup`**. R2 đóng.

### K3 — Tên tool thật (quyết định `matcher`)

Đo bằng hai lượt chạy riêng, một lượt sửa file và một lượt chạy lệnh shell:

| Việc | `tool_name` | `tool_input` thật đo được |
|---|---|---|
| chạy lệnh shell | `Bash` | `{"command": "echo xin-chao-tdq"}` |
| sửa file | `apply_patch` | `{"command": "*** Begin Patch\n*** Update File: note.txt\n@@\n+lan hai\n*** End Patch"}` |

Khoá payload `PreToolUse`: `cwd`, `hook_event_name`, `model`, `permission_mode`, `session_id`,
`tool_input`, `tool_name`, `tool_use_id`, `transcript_path`, `turn_id`. `PostToolUse` có thêm
`tool_response`.

Hai hệ quả trái ngược nhau:

- **`bash_gate.py` dùng lại nguyên xi.** `tool_name` = `Bash` và `tool_input.command` trùng
  đúng Claude Code, `bash_gate.py:75` đọc thẳng được. Matcher giữ nguyên `Bash`.
- **`edit_gate.py` KHÔNG dùng lại nguyên xi được.** Nó đọc
  `tool_input.file_path` / `tool_input.notebook_path` (`hooks/scripts/edit_gate.py:37-38`),
  mà `apply_patch` không có hai trường đó — chỉ có `command` chứa thân patch. Chạy nguyên xi
  dưới Codex thì target rỗng, gate mất tác dụng mà vẫn exit 0 (hỏng im lặng). Matcher cũng
  phải đổi từ `Edit|Write|MultiEdit|NotebookEdit` sang `apply_patch`.

### K4 — Hook cấp project chạy độc lập; hai cấp thì cộng dồn

Lượt chỉ có `<project>/.codex/hooks.json`: mỗi event nổ **đúng 1 lần**. Lượt có cả
`~/.codex/hooks.json` lẫn file project: mỗi event nổ **2 lần**. Bundle chỉ phát file cấp
project nên không có nguy cơ chạy đúp.

### Kết luận trinh sát (đặt trước phần QC vì mọi lựa chọn thiết kế dưới đây dựa vào nó)

1. `.codex/hooks.json` dùng đường dẫn tương đối, nằm trong `manifest.files`.
2. Matcher: `Bash` cho gate lệnh, `apply_patch` cho gate sửa file.
3. `edit_gate.py` cần một lớp mỏng đọc đường dẫn ra khỏi thân patch — chỗ lệch duy nhất so
   với quyết định A2 ("dùng lại nguyên `hooks/scripts/*.py`"), đã báo user.
4. README phải nêu bốn thao tác tay, trong đó có duyệt hook trong TUI.

## Q9 — Codex thật nạp được bản sinh

Hạng mục này là lý do request tồn tại: tám vòng test xanh cũng không chứng minh được Codex
đọc bundle. Chạy bằng `codex-cli 0.147.0-alpha.6.5`, `CODEX_HOME` là thư mục tạm nên
`~/.codex` thật không bị đụng.

Dựng bối cảnh: chép `portable_codex/` sang thư mục thử, `git init`, rồi

```
CODEX_HOME=<tmp> python3 scripts/tdq_checkportable.py setup --trust
→ LƯU Ý  project đã trusted trong <tmp>/config.toml
→ SẠCH   121 file khớp manifest

<tmp>/config.toml:
[projects."<đường dẫn bundle>"]
trust_level = "trusted"
```

### Q9a — mức tự động (cờ bỏ qua cổng tin cậy hook): **PASS**

Chạy `codex exec --dangerously-bypass-hook-trust`, yêu cầu liệt kê skill rồi tạo một file.

**Skill — Codex tự nạp đủ 8 skill TDQ** (trích nguyên output):

> `imagegen`, `openai-docs`, `plugin-creator`, `skill-creator`, `skill-installer`,
> `tdq-build`, `tdq-check-status`, `tdq-checkportable`, `tdq-conventions`, `tdq-intake`,
> `tdq-plan`, `tdq-spec`, `tdq-status`, `excalidraw-skill`, `graphify`, `mem0-memory`

**Hook — cả 4 event đều nổ** (đếm trên log phiên, mỗi hook một cặp `X` / `X Completed`):

```
4 × PreToolUse · 1 × SessionStart · 1 × UserPromptSubmit · 1 × Stop
```

**Hook chạy ĐÚNG, không chỉ nổ** — sổ turn `docs/tdq/.tdq-turn.jsonl` do chính hook ghi
trong project thử:

```json
{"kind": "observe", "event": "edit", "path": "thu.txt"}
{"kind": "observe", "event": "state_cli", "cmd": "get"}
```

Dòng đầu là bằng chứng quyết định cho adapter: Codex gửi `apply_patch` với thân patch, và
gate nhận được đúng `thu.txt` chứ không phải chuỗi rỗng. Dòng sau là `bash_gate.py` bắt đúng
lệnh shell.

**MCP — nạp từ `.codex/config.toml` của project:**

```
$ codex mcp list
Name            Command  Args                  Env                   Status   Auth
tavily-backup   npx      -y tavily-mcp@latest  TAVILY_API_KEY=*****  enabled  Unsupported
tavily-primary  npx      -y tavily-mcp@latest  TAVILY_API_KEY=*****  enabled  Unsupported
```

Giá trị khoá bị chính Codex che (`*****`); file trong bundle chỉ ghi TÊN biến qua `env_vars`.

### Q9b — mức thật (người dùng duyệt hook trong giao diện): **KHÔNG THỰC HIỆN ĐƯỢC**

Cổng tin cậy hook chỉ duyệt được trong TUI của Codex (mục "Review hooks"), tức cần một người
ngồi bấm. Phiên này chạy headless nên không làm được, và **không có cách nào tự động hoá mà
không phải là forge hash** — đã thử, thất bại, và đó là hành vi đúng của Codex.

Hệ quả đã được ghi vào sản phẩm chứ không để trôi: `README.md` và `AGENTS.md` của bundle nêu
đây là một trong **bốn** việc máy không tự làm được, kèm câu cảnh báo rằng chưa duyệt thì hook
im lặng không chạy, và sửa `hooks.json` thì phải duyệt lại. Cờ `--dangerously-bypass-hook-trust`
**không** được nhắc tới trong bất kỳ tài liệu nào của bundle — nó chỉ tồn tại trong file QC này.

## Q1–Q8, Q10 — QC độc lập bằng agent `tdq-qc-tester`

Agent chạy lại từ đầu mọi lệnh trong Definition of Done, không tin lời khai của phase
implement. Kết quả: **PASS toàn bộ, 0 khuyết tật.**

| # | Hạng mục | Lệnh | Output thật | Kết luận |
|---|---|---|---|---|
| Q1 | test suite không đỏ | `python3 -m pytest tests/ -q` | `764 passed, 375 subtests passed in 43.29s` | PASS |
| Q2 | 8 skill đúng chuẩn Codex | `pytest tests/test_build_portable.py -q` + soi 8 SKILL.md | `36 passed`; cả 8 file có `name` + `description` | PASS |
| Q3 | MCP đọc được, không lộ khoá | `tomllib.load()` + đối chiếu giá trị env thật | `['tavily-backup', 'tavily-primary']`; `leaked keys found in file: []` | PASS |
| Q4 | `hooks.json` đủ 4 event | `json.load(...)['hooks'].keys()` | 4 event; `PreToolUse` 2 matcher `apply_patch`+`Bash`; 5 `command` trỏ file có thật | PASS |
| Q5 | hook chạy trong bố cục bundle | bơm payload `apply_patch` vào `edit_gate.py` và `codex_edit_gate.py` | cả hai in `{"hookSpecificOutput":{…}}`, exit 0 | PASS |
| Q6 | `setup --trust` ghi thật + backup | `pytest tests/test_checkportable.py -q` | `27 passed` | PASS |
| Q7 | bundle sạch sau khi sinh | `time … check --root portable_codex` | `SẠCH 121 file khớp manifest`, `0.027 total` | PASS |
| Q8 | hết giả định sai | `grep -rn "không có skill/hook system\|hook là cơ chế riêng…"` | 0 dòng (rc=1) | PASS |
| Q10 | kiến trúc khớp thực tế | `grep -n "portable" docs/kien-truc.md` | chỉ còn dòng nhắc `portable_claude/` + `portable_codex/` | PASS |
| Hồi quy | `--only claude` không đổi byte | sha256 tổng `portable_claude/` trước/sau | `1d34ce47…` giống hệt hai lần | PASS |

Biên agent tự thăm dò thêm, ngoài phần được giao — tất cả PASS:

- `CODEX_HOME` trỏ thư mục không tồn tại → `setup --trust` tạo file mới, khai đúng đường dẫn.
- Chạy `--trust` hai lần → lần hai in `bỏ qua --trust: project đã được khai trusted từ trước`,
  không block trùng, không backup thừa.
- `config.toml` đã có `[projects."/other"]` → block đó còn nguyên, chỉ thêm block của bundle.
- `setup` trần trên `HOME` giả có sẵn config → sha256 file không đổi một byte.
- Bundle `chmod -R a-w` → `check` vẫn chạy.
- `TDQ_LOG=0` → stderr rỗng; bật log → có timestamp ISO và tên file đã ghi.
- `grep -rn "TODO\|FIXME\|XXX\|placeholder"` trên 3 file mã → 0 dòng.
- `~/.codex` THẬT không bị đụng: sha256 `config.toml` trước/sau giống hệt (`b74535c8…`),
  `find ~/.codex -maxdepth 2` trước/sau `diff` rỗng.

Ghi chú phương pháp của agent (không phải khuyết tật): lần bơm payload đầu tiên dùng lại cùng
một `session_id` nên bị cơ chế chống nhắc lặp của `_common.remind()` làm stdout rỗng — đúng
thiết kế. Đổi `session_id` mỗi lần thì cả hai gate đều in JSON hợp lệ.

## Kết luận QC

**PASS.** Q1–Q8, Q9a, Q10 và hồi quy đều có bằng chứng chạy thật. Q9b (người dùng duyệt hook
trong giao diện) không thực hiện được trong phiên headless — đã ghi rõ ở mục Q9 thay vì bỏ
qua, và hệ quả của nó đã được đưa vào README/AGENTS.md của bundle.
