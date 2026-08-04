# {{BUNDLE_NAME}} — Claude Code setup export

## 1. Giới thiệu bundle

Bundle này là bản export cấu hình Claude Code từ máy nguồn (`{{SOURCE_MACHINE_NOTE}}`),
sinh lúc `{{EXPORT_DATE}}` bằng `scripts/claude_export.py build` của repo TDQWorkflow,
tại commit `{{REPO_COMMIT}}`. Mục tiêu: dựng lại một máy Claude Code chạy **y hệt** máy
nguồn · cùng plugin, cùng marketplace, cùng MCP server, cùng file cấu hình cá nhân
(`CLAUDE.md`, `plugin-tiers.json`, skill/script global, memory `.remember/`) và cùng
repo `TDQWorkflow` kèm nguyên lịch sử git.

Không có `keybindings.json` tuỳ chỉnh trên máy nguồn tại thời điểm export — máy đích
dùng nguyên phím tắt mặc định của Claude Code, không cần copy/điền thêm gì ở mục này.

Thứ tự làm: mục 2 → 3 → 4 → 5 → 6 → 7. Bỏ mục 6 thì Tavily và mọi MCP server khác
sẽ không có trên máy đích.

Cấu trúc bundle:
```
{{EXPORT_DEST}}/
├── manifest.json           # plugin/marketplace/mcp/CLI + version plugin + commit SHA + sha256 file nguồn
├── README.md               # chính file này, đã điền
├── config/                 # file cấu hình global đã lọc secret
│   ├── settings.json
│   ├── CLAUDE.md
│   ├── plugin-tiers.json
│   ├── mcp-servers.json    # khối mcpServers tách từ ~/.claude.json của máy nguồn
│   ├── skills-graphify/
│   ├── remember/
│   ├── statusline.sh
│   ├── scripts/
│   ├── installed_plugins.json
│   └── known_marketplaces.json
└── tdqworkflow-repo/       # repo TDQWorkflow lấy bằng `git clone` — có `.git`, chỉ file tracked
```

## 2. CLI dependency cần cài

| Dependency | macOS | Linux | Windows |
|---|---|---|---|
| Claude Code CLI | `npm install -g @anthropic-ai/claude-code` | `npm install -g @anthropic-ai/claude-code` | **Native**: `winget install Anthropic.ClaudeCode` (hoặc npm) — không cần WSL, không hỗ trợ sandbox. **WSL2** (khuyến nghị khi cần sandbox): bật WSL2 rồi cài như nhánh Linux bên trong |
| Node.js | `brew install node` (hoặc installer trên nodejs.org) | Trình quản lý gói của distro (`apt install nodejs npm`, v.v.) hoặc nodejs.org | **Native**: `winget install OpenJS.NodeJS` hoặc installer nodejs.org. **WSL2**: như nhánh Linux |
| Python 3 | `brew install python3` | Trình quản lý gói của distro (thường có sẵn) hoặc python.org | **Native**: `winget install Python.Python.3` hoặc installer python.org. **WSL2**: như nhánh Linux |
| Git | `brew install git` (hoặc Xcode Command Line Tools) | Trình quản lý gói của distro (`apt install git`) | **Native**: `winget install Git.Git` hoặc Git for Windows. **WSL2**: như nhánh Linux |
| uv | macOS/Linux: `curl -LsSf https://astral.sh/uv/install.sh \| sh` (chuẩn, không cần Python cài sẵn) | như macOS | **Native**: `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 \| iex"`. **WSL2**: như nhánh Linux |
| graphify | `uv tool install graphifyy` rồi `graphify install` (gói PyPI tên `graphifyy`, lệnh CLI vẫn là `graphify`) | như macOS | **Native**: như macOS/Linux qua `uv`/`pipx`; nếu lệnh `graphify` không nhận diện sau khi cài, thêm thư mục Scripts của Python vào `PATH` (vấn đề PATH đã biết trên Windows) hoặc chạy `py -m graphify install`. **WSL2**: như nhánh Linux |
| Codex CLI (tuỳ chọn) | npm: `npm install -g @openai/codex` (đã có Node ở trên); hoặc standalone installer `curl -fsSL <link cài từ trang chính thức> \| sh` (không cần Node) | như macOS | npm: `npm install -g @openai/codex`, hoặc tải binary từ GitHub Releases chính thức. **WSL2**: như nhánh Linux |
| agy — Antigravity CLI (tuỳ chọn) | theo hướng dẫn cài chính thức của Antigravity CLI tại thời điểm setup máy đích | như macOS | như macOS, hoặc qua WSL2 |

Ghi chú: lệnh nhánh macOS đã test trực tiếp trên máy nguồn (macOS, kiến trúc Apple Silicon);
lệnh nhánh Linux/Windows đối chiếu theo tài liệu chính thức (Claude Code docs, astral-sh/uv
GitHub, Graphify-Labs/graphify GitHub), chưa test trực tiếp trên 2 OS đó.

Version thật đã ghi nhận trên máy nguồn lúc export: xem `cli_dependencies` trong `manifest.json`.

## 3. Cài Claude Code CLI

```bash
npm install -g @anthropic-ai/claude-code   # hoặc lệnh OS tương ứng ở mục 2
claude --version                            # xác nhận cài xong
```
Lần chạy đầu tiên, `claude` sẽ dẫn qua bước đăng nhập (`claude login` hoặc onboarding
trong ứng dụng) — máy đích tự đăng nhập tài khoản mới, KHÔNG copy `oauthAccount` từ
máy nguồn (bundle này không chứa giá trị đó theo chủ đích).

## 4. Add marketplace + cài từng plugin

```bash
# 1) Add marketplace — lặp cho từng marketplace trong manifest.json.marketplaces
claude plugin marketplace add <source-của-từng-marketplace>

# 2) Cài từng plugin — lặp cho TỪNG plugin trong manifest.json.plugins
#    (chưa có lệnh bulk-install-all ở thời điểm viết bundle này — phải cài từng dòng)
claude plugin install <plugin-name>@<marketplace-name>

# 3) Nạp lại plugin trong phiên đang mở (nếu Claude Code đang chạy)
/reload-plugins
```
Danh sách marketplace + plugin thật (đọc trực tiếp từ `installed_plugins.json` /
`known_marketplaces.json` của máy nguồn lúc export, KHÔNG hardcode số lượng ở template
này — đối chiếu số lượng plugin cài được với `manifest.json` bằng QC Q6):

{{PLUGIN_MARKETPLACE_LIST}}

## 5. Copy file cấu hình + rewrite path `tdq-local` + điền lại API key

```bash
mkdir -p ~/.claude
cp {{EXPORT_DEST}}/config/settings.json ~/.claude/settings.json
cp {{EXPORT_DEST}}/config/CLAUDE.md ~/.claude/CLAUDE.md
cp {{EXPORT_DEST}}/config/plugin-tiers.json ~/.claude/plugin-tiers.json
cp -R {{EXPORT_DEST}}/config/skills-graphify ~/.claude/skills/graphify
cp -R {{EXPORT_DEST}}/config/remember ~/.claude/.remember
cp {{EXPORT_DEST}}/config/statusline.sh ~/.claude/statusline.sh
cp -R {{EXPORT_DEST}}/config/scripts ~/.claude/scripts
cp -R {{EXPORT_DEST}}/tdqworkflow-repo ~/Documents/TDQWorkflow   # hoặc vị trí bạn muốn giữ repo
```

`config/settings.json` đã được `claude_export.py build` rewrite sẵn đường dẫn
`extraKnownMarketplaces.tdq-local` trỏ đúng vị trí `tdqworkflow-repo/` BÊN TRONG bundle
này. Copy repo sang vị trí KHÁC vị trí gốc trong bundle (ví dụ dòng lệnh trên) thì phải
sửa lại đường dẫn đó (và trường tương ứng trong `known_marketplaces.json`) cho khớp vị
trí thật trên máy đích · không sửa thì plugin `tdq-workflow` sẽ không load được.

Điền lại API key đã bị lọc khỏi bundle (giá trị thật KHÔNG có trong bundle theo chủ đích):
mở `~/.claude/settings.json`, thay mọi placeholder dạng `<TÊN_BIẾN — điền lại>` bằng key
thật của bạn. Với bộ này là 2 biến (xin key mới tại Tavily nếu bạn dùng chung MCP server):
- `TAVILY_API_KEY_PRIMARY`
- `TAVILY_API_KEY_BACKUP`

## 6. Khôi phục MCP server

MCP scope `user` KHÔNG nằm trong `settings.json` mà nằm ở `~/.claude.json`, cùng file với
`oauthAccount`/`machineID` của máy đích. Vì vậy bundle này **không** chứa `~/.claude.json`
và bạn **không** được copy đè file đó — hỏng đăng nhập máy đích.

Cách đúng là add lại từng server bằng CLI, đọc từ `config/mcp-servers.json`:

```bash
python3 -c 'import json,sys
for n, c in json.load(open(sys.argv[1])).items():
    print(n + "\t" + json.dumps(c))' "{{EXPORT_DEST}}/config/mcp-servers.json" |
while IFS=$'\t' read -r name conf; do
  claude mcp add-json "$name" "$conf" --scope user
done
claude mcp list          # đối chiếu tên server khớp config/mcp-servers.json
```

Header xác thực trong file đó là tham chiếu biến môi trường (`Bearer ${TAVILY_API_KEY_PRIMARY}`),
không phải key thật — server chỉ chạy được sau khi bạn đã điền key ở mục 5.

## 7. Verify

```bash
claude --version
claude doctor            # kiểm tra bản cài, quyền, cấu hình
claude plugin list       # đối chiếu số lượng + tên plugin khớp manifest.json.plugins
claude mcp list          # đối chiếu số lượng + tên server khớp manifest.json.mcp_servers
git -C ~/Documents/TDQWorkflow log --oneline -1   # phải ra commit {{REPO_COMMIT}}
```
Cả 5 lệnh chạy được không lỗi, danh sách plugin và MCP khớp `manifest.json`, commit của
repo khớp `{{REPO_COMMIT}}` là setup hoàn tất.
