# {{BUNDLE_NAME}} — Claude Code setup export

## 1. Giới thiệu bundle

Bundle này là bản export cấu hình Claude Code từ máy nguồn (`{{SOURCE_MACHINE_NOTE}}`),
sinh lúc `{{EXPORT_DATE}}` theo `claude-export/INSTRUCTIONS.md` của repo TDQWorkflow.
Mục tiêu: dựng lại một máy Claude Code chạy **y hệt** máy nguồn — cùng plugin, cùng
marketplace, cùng MCP server, cùng file cấu hình cá nhân (`CLAUDE.md`, `plugin-tiers.json`,
skill/script global, memory `.remember/`) và cùng repo `TDQWorkflow`.

Không có `keybindings.json` tuỳ chỉnh trên máy nguồn tại thời điểm export — máy đích
dùng nguyên phím tắt mặc định của Claude Code, không cần copy/điền thêm gì ở mục này.

Cấu trúc bundle sau khi export xong:
```
{{EXPORT_DEST}}/
├── manifest.json          # danh sách plugin/marketplace/mcp/CLI dependency/excluded — dữ liệu thật
├── README.md               # chính file này, đã điền
├── config/                 # file cấu hình global đã lọc secret
│   ├── settings.json
│   ├── CLAUDE.md
│   ├── plugin-tiers.json
│   ├── skills-graphify/
│   ├── remember/
│   ├── statusline.sh
│   ├── scripts/
│   ├── installed_plugins.json
│   └── known_marketplaces.json
└── tdqworkflow-repo/        # copy toàn bộ repo TDQWorkflow (không có .git theo mặc định)
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

`config/settings.json` đã được `INSTRUCTIONS.md` Bước 4 rewrite sẵn đường dẫn
`extraKnownMarketplaces.tdq-local` trỏ đúng vị trí `tdqworkflow-repo/` BÊN TRONG bundle
này — nếu bạn copy repo sang vị trí KHÁC vị trí gốc trong bundle (ví dụ dòng lệnh trên),
phải sửa lại đường dẫn đó (và trường tương ứng trong `known_marketplaces.json`) cho khớp
vị trí thật trên máy đích, nếu không plugin `tdq-workflow` sẽ không load được.

Điền lại 2 API key đã bị lọc khỏi bundle (giá trị thật KHÔNG có trong bundle theo chủ đích):
mở `~/.claude/settings.json`, thay 2 placeholder sau bằng key thật của bạn (xin key mới tại
nhà cung cấp — Tavily — nếu bạn dùng chung MCP server này):
- `TAVILY_API_KEY_PRIMARY`
- `TAVILY_API_KEY_BACKUP`

## 6. Verify

```bash
claude --version
claude plugin list       # đối chiếu số lượng + tên plugin khớp manifest.json.plugins
```
Cả 2 lệnh chạy được không lỗi, và danh sách plugin ở lệnh thứ 2 khớp `manifest.json` là
setup hoàn tất.
