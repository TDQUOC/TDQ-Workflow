# Brief — Sửa bộ workflow TDQ để chạy đủ tính năng trên Windows
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## Nguyên văn

Lượt 1 — "hi hãy check repo này giúp tôi".

Lượt 2 — "okay vậy hãy check xem bạn có thể fix để bộ workflow nayuf chạy được ổn định và đầy
đủ tính năng trên window ko?"

Lượt 3 — user chốt ba lựa chọn khi được hỏi:

- Phạm vi: **N1→N4 + dọn sạch test đỏ**.
- `hooks/hooks.json`: **tự nhận hệ điều hành lúc chạy** (shim), không dùng lệnh sinh lại thủ công.
- Cách làm: **đi qua workflow TDQ** của chính repo (intake → spec → plan → duyệt → implement).

### Cách hiểu đầu tiên của tôi

**Mục tiêu.** Bộ TDQ-Workflow hiện không chạy được trên Windows 11 của user. Yêu cầu là vá tới
mức "chạy ổn định và đầy đủ tính năng", không phải vá tạm cho khỏi nổ.

**Phạm vi đoán.** Bốn nhóm lỗi đã đo được ở lượt 2, cộng phần dọn test đỏ:

- N1 — encoding stdout: không script nào gọi `reconfigure`, Python 3.13 trên Windows dùng
  cp1252 nên mọi `print` chứa ký tự ngoài ASCII đều ném `UnicodeEncodeError`.
- N2 — tên lệnh `python3` không tồn tại trên Windows, gồm cả `hooks.json` lẫn các chuỗi lệnh
  sinh ra lúc chạy và chuỗi tĩnh trong `skills/*.md`.
- N3 — test harness set `HOME` mà `ntpath.expanduser` chỉ đọc `USERPROFILE`.
- N4 — dấu `\` rò vào dữ liệu xuất ra của một số script.
- Dọn test đỏ: artifact riêng máy bị commit, test phụ thuộc tool ngoài chưa cài, ba chỗ drift.

**Chỗ chưa rõ.** Còn phải chốt với user ở phase analyze:

- Shim nhận hệ cho `hooks.json` phải chạy được trên host nào (Claude Code Windows dùng shell gì
  để chạy hook), và có được phép thêm file mới vào `hooks/` không.
- 96 chuỗi `python3` tĩnh trong `skills/*.md`: sửa hết hay thêm một dòng nhắc trong header hook.
- "Dọn sạch test đỏ" tới mức nào: xanh toàn bộ trên Windows, hay chấp nhận `skip` cho các ca
  cần tool ngoài (`codex`, `graphify`, `anthropic-tokenizer`, `pytest`).
- Có phải giữ nguyên hành vi trên macOS/Linux tuyệt đối không (baseline lệch 0).

## Hiểu & kiến thức

Vòng scope: BỎ — user đã liệt kê tường minh phạm vi ở lượt 3 (N1→N4 + dọn test đỏ) và chọn sẵn
cách xử lý `hooks.json`, nên mọi mặt còn lại đều suy ra được từ code và số đo đã có.

### Năng lực dùng được

| Năng lực | Nguồn | Dùng? | Vì sao |
|---|---|---|---|
| `skill_inventory.py` (B0) | project | KHÔNG | trả về `(no skill on disk)` trên máy này — xem "Phát hiện ngoài dự kiến" |
| `tdq_lsp.py` bậc 1–7 | project | KHÔNG | 4/7 bậc THIẾU, chưa được user cho cài |
| grep + đọc file | built-in | CÓ | lớp tìm kiếm duy nhất còn dùng được, đủ cho phạm vi này |
| `claude-code-guide` (subagent) | built-in | CÓ | đã tra tài liệu hook Windows, kết quả ở `### Nghiên cứu` |
| `build_portable.py --sinh-hook-claude` | project | CÓ | đã có sẵn cơ chế viết lại `hooks.json` theo OS |
| `python -m unittest discover tests` | project | CÓ | mốc đo đỏ/xanh trước và sau |

### Số đo hiện trạng (Windows 11, Python 3.13.15, máy của user)

| Mốc | Số |
|---|---|
| Test chạy mặc định (không ép UTF-8) | 1907 ca — 670 fail, 97 error |
| Test khi ép `PYTHONUTF8=1` | 1907 ca — 357 fail, 7 error |
| Entry point có `__main__` trong `scripts/` + `hooks/scripts/` | 40 |
| Trong đó tới được qua `tdq_state.py` hoặc `hooks/scripts/_common.py` | 18 |
| Còn lại phải thêm tay một dòng import | 22 |
| `subprocess(text=True)` thiếu `encoding=` | 20 |
| `open()` không khai `encoding=` | 9 |
| Chuỗi `python3` trong `scripts/` + `hooks/scripts/` | 153 |
| Chuỗi `python3` trong `skills/**/*.md` | 96 |
| File test set `HOME` mà thiếu `USERPROFILE` | 6 file, 20 chỗ |

### Bốn nhóm lỗi

**N1 — encoding stdout.** Không file nào gọi `sys.stdout.reconfigure`. Python 3.13 trên Windows
lấy encoding theo locale (cp1252 ở máy này), nên mọi `print` chứa dấu tick, dấu chéo hay tiếng
Việt đều ném `UnicodeEncodeError`. Đã dựng lại được: hook `session_start.py` chết ngay ở dòng
`print(out)`. Hệ quả thật: cả 6 hook im lặng, workflow mất sạch phần nhắc `[TDQ:*]`.

**N2 — tên lệnh `python3`.** Bằng chứng đo tại máy user:

- `where python3` ra `...\WindowsApps\python3.exe`, tức stub Microsoft Store; chạy thử trả
  **exit 49**, khác 0 nên toán tử `||` của shell sẽ nhảy sang nhánh dự phòng.
- `where py` ra `...\Programs\Python\Launcher\py.exe` — launcher thật.
- `where python` ra `...\Python313\python.exe` đứng TRƯỚC stub, nên `python` chạy đúng ở máy này;
  nhưng `python` vắng mặt trên macOS 12.3+ và nhiều bản Linux nên không dùng làm tên chung được.
- `.py` KHÔNG có file association, `.PY` KHÔNG nằm trong `PATHEXT`. Vì vậy phương án "bỏ hẳn tên
  interpreter, trỏ `hooks.json` thẳng vào đường dẫn `.py`, dựa vào shebang" chạy trên macOS/Linux
  nhưng CHẾT trên Windows. Loại.

**N3 — test harness không chạy được trên Windows.** 6 file test set `HOME` trỏ vào thư mục tạm,
nhưng `ntpath.expanduser` KHÔNG đọc `HOME`; nó đọc `USERPROFILE`. Hệ quả: test quét nhầm
`~/.claude` thật của máy thay vì thư mục tạm, kéo theo khoảng 16 ca `skill_inventory` và các ca
liên đới.

**N4 — dấu chéo ngược rò vào dữ liệu xuất ra.** `kiem_no_marker` in `scripts\a.py:2`,
`context_surface` trả `skills\tdq-build\SKILL.md`, sổ turn ghi `src\a.py`. Đã kiểm `edit_gate` và
`stop_gate`: hai cổng chặn dùng `os.sep` nhất quán nên KHÔNG hỏng chức năng — đây là lệch ở biên
xuất, không phải lệch ở cổng. Repo đã có sẵn lối vá đúng tại `build_portable.py:1017` và
`claude_export.py:197` (`.replace(os.sep, "/")`); việc còn lại là áp cho nhất quán.

### Phần test đỏ KHÔNG phải lỗi Windows

| Nhóm | Số ca | Bản chất |
|---|---|---|
| `test_skill_router` | 285 | `docs/tdq/audit/skill-index.json` bị commit kèm 284 đường dẫn tuyệt đối của máy tác giả; fail trên mọi máy khác |
| `test_codex_cli` + `test_codex_run` | 16 | máy chưa cài `codex` CLI |
| `test_checkportable` | 11 | máy chưa cài `graphify` |
| `test_doc_dup` | 5 | máy chưa cài `anthropic-tokenizer` |
| loader error | 2 | máy chưa cài `pytest` |
| drift thật | 3 | `docs/claude-md-mau.md` 3533 vượt trần 3500 byte · `index.md` nhắc thừa `bash.md` · `setup_status` trả model khác test mong |

### Nghiên cứu

Giao cho subagent `claude-code-guide` tra tài liệu chính thức `code.claude.com/docs`
(`hooks.md`, `plugins-reference.md`, `debug-your-config.md`). Kết quả:

- Hook có HAI dạng: *exec form* (khai thêm `args`, spawn thẳng, KHÔNG qua shell) và *shell form*
  (chỉ `command`, có shell nên dùng được `|`, `&&`, `||`).
- `hooks.json` KHÔNG có trường điều kiện theo hệ điều hành (`os`, `platform`, `when`). Một chuỗi
  lệnh duy nhất phải đúng cho cả ba hệ.
- Tài liệu KHÔNG nêu: Windows dùng shell nào cho *shell form*; `${CLAUDE_PLUGIN_ROOT}` bung ra
  dạng đường dẫn nào trên Windows; encoding Claude Code dùng để đọc stdout của hook.

### Ẩn số chặn thiết kế

Claude Code trên Windows chạy *shell form* bằng shell nào. `cmd.exe` hiểu `||`; PowerShell 5.1 thì
`||` là lỗi cú pháp và hook chết ngay. Tài liệu không nói, nên chỉ chốt được bằng thực nghiệm:
cài plugin vào một project nháp rồi quan sát hook có chạy không. Việc đó thuộc phase
implement/QC, không đoán trước ở đây.

### Phát hiện ngoài dự kiến — KHÔNG phải lỗi Windows

Claude Code đã đổi layout thư mục và bộ TDQ chưa biết:

- Skill của user nằm ở `~/.claude/skills/synced/<uuid>_<uuid>/<tên>/SKILL.md`, sâu hơn khuôn
  `~/.claude/skills/<x>/SKILL.md` mà `skill_inventory.py` đang quét, nên bước B0 trả về
  `(no skill on disk)` — workflow mù hoàn toàn về năng lực sẵn có.
- `~/.claude/plugins/` không còn `installed_plugins.json`; thay vào đó là `synced/` và
  `marketplaces/`, nên `tdq_lsp.py` báo `FileNotFoundError` rồi bỏ qua bậc kiểm plugin.

Hai cái này phá "đầy đủ tính năng" trên máy user y như lỗi Windows, nhưng nguyên nhân khác hẳn,
nên phải để user quyết có gộp vào request này không.

## Hỏi đáp

Vòng 1 — 5 câu, user trả lời `1b 2b 3b 4a 5a` kèm một yêu cầu chen ngang.

**1. `hooks.json` nạp interpreter kiểu gì?** → **B: giữ cơ chế sinh lại theo OS.**
Bỏ phương án shim "tự nhận hệ" mà chính user chọn ở lượt trước. Lý do đổi ý là bằng chứng mới:
tài liệu Claude Code không nói Windows chạy *shell form* bằng shell nào, nên chuỗi có `||` là
canh bạc — PowerShell 5.1 coi `||` là lỗi cú pháp. Sinh lại theo OS thì chắc chắn chạy.
Hệ quả phải nhận: sau mỗi lần update plugin phải chạy lại một lệnh, và diff local luôn bẩn.

**2. 96 chuỗi `python3` tĩnh trong `skills/**/*.md`?** → **B: sửa hết sang placeholder do hook bung ra.**
Chạm gần hết tầng luật và bắt buộc dựng lại 3 bundle portable. Đổi lại, không còn chỗ nào
trong tài liệu chỉ cho agent một lệnh không chạy được trên máy đang ngồi.

**3. Mức "dọn sạch test đỏ" với 34 ca cần tool ngoài?** → **B: cài đủ tool rồi chạy thật.**
Phải cài `codex`, `graphify`, `anthropic-tokenizer`, `pytest`. `codex` còn cần đăng nhập, nên
bước này sẽ xin phép từng lệnh chứ không tự cài.

**4. Layout `~/.claude/skills/synced/...` mới làm B0 và `tdq_lsp.py` mù?** → **A: gộp vào request này.**

**5. Bậc thang LSP?** → **A: cài cả ba.** Kèm yêu cầu: *"tiến hành setup lsp cho user-level và
đảm bảo nó hoạt động ổn định trước khi tiến hành làm request này"*.

### Kết quả setup LSP (làm ngay trong phase analyze, mức user)

Trạng thái đầu: 2/7 bậc ĐẠT. Trạng thái cuối: **6/7 bậc ĐẠT, 1 cảnh báo không chặn.**

| Việc | Cách làm | Ghi chú |
|---|---|---|
| Bậc 1 · `agent-lsp` | tải `agent-lsp_windows_amd64.zip` v0.19.2, đối chiếu sha256 khớp checksums.txt, đặt vào `~/.local/bin` | `install.sh` chính thức CHẶN Windows (`unsupported OS`), nhưng release có sẵn bản Windows |
| Bậc 3 · language server | `npm i -g pyright vscode-langservers-extracted` | |
| Bậc 2 · MCP `lsp` | ghi tay `mcpServers.lsp` vào `~/.claude.json` | `agent-lsp init` đặt tên server là `agent-lsp`, KHÔNG khớp `MCP_SERVER_NAME = "lsp"` mà `tdq_lsp.py` đòi, nên phải ghi tay |
| Bậc 4 · quyền tool | thêm `mcp__lsp__*` vào `permissions.allow` của `~/.claude/settings.json` | |
| Ổn định | trỏ cấu hình vào `%APPDATA%\fnm\aliases\default\*.cmd` và thêm đường dẫn đó vào PATH user | npm cài vào `fnm_multishells\<pid>_<ts>` — thư mục đổi theo từng shell; `aliases\default` là symlink bền |

Đã sao lưu `~/.claude.json` và `~/.claude/settings.json` (đuôi `.bak-20260920-191811`) trước khi sửa.

`agent-lsp doctor`: **2 ok, 0 failed**; pyright đủ 12 capability gồm `referencesProvider`,
`callHierarchyProvider`, `renameProvider`, `workspaceSymbolProvider`.

### Phép kiểm hiệu ứng — ĐẠT

Ký hiệu chọn: `now_iso` (`scripts/tdq_state.py:334`).

| Cách hỏi | Kết quả |
|---|---|
| `grep -rl now_iso scripts/ hooks/` | 5 file |
| `find_references` tại chỗ ĐỊNH NGHĨA, workspace nguội | 10 hit / **1 file** |
| `find_references` từ phía NGƯỜI GỌI (`doc_dup.py:57`) | 16 hit / **6 file** |

6 >= 5 nên phép kiểm ĐẠT. `go_to_definition` từ `doc_dup.py:57` nhảy đúng `tdq_state.py:334`,
chứng minh `extraPaths` của `pyrightconfig.json` phân giải được `import tdq_state`.

Hai điều phải nhớ khi dùng, vì cả hai đều tạo ra kết luận sai:

- Hỏi tại chỗ định nghĩa khi chưa file nào gọi được mở ra chỉ thấy 1 file. Phải hỏi từ phía
  người gọi, hoặc mở file gọi trước.
- Đầu ra mặc định là GCF nén, chỉ in namespace (`TDQ-Workflow/scripts.ref_1`) chứ không in
  đường dẫn file. Đếm dòng đó như đếm file là đúng cái bẫy `kiem-lsp-hieu-ung.md` cảnh báo.
  Muốn có đường dẫn thì đặt `AGENT_LSP_OUTPUT_FORMAT=json`.

### Bậc 5 — đã cài lumen theo lựa chọn `1b` của user

Vòng 2 — user chọn **B: cài lumen rồi `ollama pull` model embedding.**

| Việc | Kết quả |
|---|---|
| Bản Windows của lumen | CÓ — release `v0.0.42` có `lumen-0.0.42-windows-amd64.exe`, đúng version repo đã đo |
| Cài plugin | `claude plugin install lumen@claude-plugins-official -y`, scope user, ghim sha `f60f9ec` |
| Model embedding | `ollama pull ordis/jina-embeddings-v2-base-code` — 323 MB, xong |
| Binary | `scripts/run.cmd` tự tải `bin/lumen-windows-amd64.exe` (35 MB) ở lần chạy đầu, `--version` chạy được |
| Bậc 5 | THIẾU → **ĐẠT** (ollama đang chạy, có model) |
| Bậc 6 | ĐẠT → **CẢNH BÁO** (xem dưới) |

Đây là bằng chứng ngoài lề nhưng đáng ghi cho N2: `hooks.json` của lumen trỏ vào
`"${CLAUDE_PLUGIN_ROOT}/scripts/run"` KHÔNG có đuôi, mà thư mục đó chỉ có `run` (bash) và
`run.cmd`. Cách đó chỉ chạy được nếu host dùng `cmd.exe` — vì `cmd.exe` tự thêm đuôi theo
`PATHEXT`, còn CreateProcess trần thì không. Một plugin chính chủ trong marketplace của Anthropic
đang đặt cược vào đúng giả định ấy. Đó là chỉ dấu mạnh cho câu hỏi "Windows chạy *shell form*
bằng shell nào", nhưng vẫn là chỉ dấu chứ chưa phải bằng chứng, nên không đổi lựa chọn `1b` cho
`hooks.json` của TDQ.

### Bậc 6 — lumen chèn hook cạnh tranh, cần user quyết

`tdq_lsp.py` bắt được: lumen đăng ký `PreToolUse` với matcher `Grep|Bash` tại
`~/.claude/plugins/cache/claude-plugins-official/lumen/0.0.42/hooks/hooks.json`, đẩy agent gọi
lumen trước. Thứ tự tìm kiếm mà workflow này đã chốt thì khác. Script KHÔNG tự sửa file của
plugin khác; gỡ hay giữ là quyết định của user, và một lần update plugin sẽ đặt nó về chỗ cũ.

### Sự cố trong lúc setup, đã xử lý

`agent-lsp init --help` không có cờ `--help`: công cụ chạy luôn init với lựa chọn mặc định và
ghi `CLAUDE.md` + `.mcp.json` vào gốc repo. Hai file đều chưa từng được commit nên đã xoá, repo
trở lại đúng trạng thái cũ (`git status` chỉ còn file của request này).

### Đo lại bảng thứ tự tìm kiếm trên máy user (vòng 3, lựa chọn `1b`)

User chọn **B: sửa `uu-tien-tim-kiem.md` để lumen là lớp đầu tiên cho mọi loại câu hỏi**, kèm
điều kiện tôi đã nêu: đo lại trên máy này trước khi ghi. Đây là luật **tầng 1 — chất lượng**
theo bảng phân tầng của `soul.md`, nên số đo quyết định chứ không phải sở thích.

Bộ đo chạy cùng một câu hỏi qua cả ba lớp. Repo lúc đo: lumen index 1488 file / 27318 chunk
(8m44s), pyright qua agent-lsp 0.19.2.

**Loại 1 — quan hệ: "ai gọi `now_iso`"**

| Lớp | Thời gian | Số file | Đúng/sai |
|---|---|---|---|
| agent-lsp | 0.39s | 6 | **6 đúng, 0 sai** |
| grep | 0.04s | 8 | 6 đúng, **2 dương tính giả** |
| lumen | 1.18s | 10 | tìm ra chỗ ĐỊNH NGHĨA, **trượt toàn bộ 5 chỗ gọi**; 4/10 là bản sao trong portable bundle |

Hai file grep thừa là dương tính giả thật, không phải lỗi đếm: `tests/test_context_hooks.py:14`
và `tests/test_edit_gate.py:10` **tự định nghĩa `now_iso()` riêng** — trùng tên, khác ký hiệu.
LSP loại đúng hai file đó.

**Loại 2 — tên chính xác đã biết: `bac6_hook_xung_dot`**

| Lớp | Thời gian | Số file | Đúng/sai |
|---|---|---|---|
| grep | 0.04s | 2 | 2 đúng |
| agent-lsp `find_symbol` | 0.08s | 1 | đúng chỗ định nghĩa |
| lumen | 1.17s | 10 | có file đúng nhưng chìm giữa 7+ file sai, 3 trong đó là bản sao portable |

lumen chậm hơn grep **29 lần** cho loại câu hỏi này.

**Loại 3 — khái niệm mơ hồ, đúng sở trường của lumen**

Mục tiêu thật: `scripts/tdq_state.py:1727` — dòng `state[f"{target}_approved_at"] = now_iso()`.
Hỏi lumen 3 cách diễn đạt khác nhau, đều viết sát nội dung code:

| Câu hỏi | `scripts/tdq_state.py` có trong top-8? |
|---|---|
| "record the timestamp when the user approves the spec" | KHÔNG |
| "set spec_approved_at when approval is recorded" | KHÔNG |
| "approval gate stores who approved and when" | KHÔNG |

Cả 3 lần lumen trả về tài liệu NÓI VỀ duyệt (`skills/tdq-conventions/references/approval.md`,
`docs/tdq/**/2026-08-04-approval-gate-bug.md`) chứ không ra dòng code đóng dấu thời gian.
Nhìn được lý do: repo có 945 file tài liệu so với khoảng 40 script, nên chunk tài liệu áp đảo
không gian embedding; cộng thêm 3 bundle portable nhân bản mọi script.

**Kết luận theo soul.** Tự kiểm của `soul.md` hỏi: *"thay đổi này có hạ chất lượng để đổi lấy
tốc độ hoặc token không?"* Đặt lumen lên đầu mọi loại câu hỏi thì loại 1 rơi từ 6/6 đúng xuống
0/6, loại 2 chậm gấp 29 lần và kém chính xác hơn, còn loại 3 — sở trường của chính nó — trượt
mục tiêu code ở cả 3 cách hỏi. Không có tầng nào được lợi. Soul nói luật mâu thuẫn với soul là
luật phải sửa, nên tôi KHÔNG tự ghi luật này; báo số và xin user ra phán quyết, rồi ghi phán
quyết vào tài liệu request theo luật hoà giải mục 2 của soul.

### Hai phát hiện phụ, đều đáng sửa thật

**1. `find_references` tệ đi khi mở sẵn nhiều file.** Ngược trực giác nhưng lặp lại được:

| Cách gọi | Số file tìm ra |
|---|---|
| chỉ mở `doc_dup.py` rồi hỏi | **6** |
| mở `doc_dup.py` + gọi `go_to_definition` trước | 6 (không đổi) |
| mở thêm 2 file gọi khác | 4 |
| mở đủ 8 file grep chỉ ra | **1** |

`go_to_definition` không liên quan. Biến thật là số document mở sẵn — mở càng nhiều càng tệ.
Vậy cách dùng đúng là **hỏi thẳng, không mở file trước**. Kết luận "6 file" của phép kiểm hiệu
ứng ở vòng 1 vì thế vẫn đứng, nhưng lý do tôi ghi lúc đó ("nhờ gọi `go_to_definition`") là SAI
và đã sửa lại ở đây.

**2. lumen nuốt cả 3 bundle portable.** `antigravity_portable/`, `portable_codex/` và
`portable_claude/` chứa bản sao của gần như mọi script, nên kết quả nào của lumen cũng có
3-4 bản trùng chiếm chỗ trong top-10. Repo đã có `.graphifyignore` cho đúng vấn đề này ở công
cụ khác. Cho lumen một danh sách bỏ qua tương tự là việc nhỏ và cải thiện thật.

### Đính chính loại 3 — lumen KHÔNG mù, nó bị bản sao chiếm chỗ

Sau khi user chọn `1a`, tôi kiểm chứng giả thuyết "bản sao portable làm bẩn kết quả" bằng cách
hỏi lại với độ sâu 25 rồi lọc bỏ ba bundle, thay vì dừng ở top-8 như vòng trước:

| Câu hỏi | Hạng của `scripts/tdq_state.py` sau khi lọc |
|---|---|
| "record the timestamp when the user approves the spec" | hạng **4** |
| "set spec_approved_at when approval is recorded" | hạng **1** |

Kết luận vòng trước — "lumen trượt mục tiêu code ở cả 3 cách hỏi" — là ĐÚNG về hiện tượng
nhưng SAI về nguyên nhân. lumen tìm được mục tiêu; ba bundle portable nhân bản mọi script đã
đẩy nó ra khỏi top-8. Bảng thứ tự hiện hành vốn đã định tuyến câu hỏi khái niệm sang lumen,
nên số đo này ỦNG HỘ giữ nguyên bảng, đúng như phán quyết `1a`.

### Phán quyết của user về thứ tự tìm kiếm (ghi theo luật hoà giải mục 2 của soul)

**Phán quyết: `1a`** — giữ bảng chọn lớp theo loại câu hỏi, cộng hai cải thiện có số đo:

1. Thêm `.lumenignore` ở gốc repo, loại `portable_claude/`, `portable_codex/`,
   `antigravity_portable/`. Cú pháp giống `.gitignore`; repo đã có tiền lệ `.graphifyignore`.
2. Thêm luật "KHÔNG mở file trước khi hỏi `find_references`" vào
   `skills/tdq-lsp-setup/references/uu-tien-tim-kiem.md`, viết theo khuôn ba mục mà soul
   nguyên tắc 3 đòi (`When it applies` / `What to do` / `Self-check`).

Không sửa thứ hạng các lớp trong bảng. Hai việc trên là sửa file trong repo nên thuộc phase
implement, và được nhập vào phạm vi request này.

### Lộ trình

| Bước/phase | CÓ-BỎ | Vì sao |
|---|---|---|
| Nghiên cứu thêm | BỎ | tài liệu hook Windows đã tra; phần còn lại là ẩn số chỉ thực nghiệm mới chốt được |
| spec | CÓ | khung bất biến, và phạm vi đụng cả 3 tầng luật/CLI/hook |
| plan | CÓ | khung bất biến; mỗi task một test |
| implement | CÓ | khung bất biến |
| Chia việc cho subagent | BỎ | các nhóm N1-N4 đụng chéo cùng tập file, chia ra là chuốc conflict |
| QC bằng agent độc lập | CÓ | mốc đỏ/xanh phải do một lượt chạy độc lập xác nhận, không tự chấm |
| Rà soát sâu | CÓ | N2 chạm gần hết tầng luật và bắt dựng lại 3 bundle portable |
| report | CÓ | khung bất biến |
