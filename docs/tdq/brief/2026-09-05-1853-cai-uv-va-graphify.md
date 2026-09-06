# Cài uv và setup graphify vào Claude Code user-level

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## Nguyên văn

> đã clone về document/ForAgentCode/graphify hãy đọc nó và phân tích đẻ cài uv và setup graphify vào claude code userlevel giúp tôi

**Cách hiểu đầu tiên**

- **Mục tiêu:** cài `uv` lên máy, rồi cài graphify và gắn nó vào Claude Code ở phạm vi user-level (mọi project đều dùng được).
- **Phạm vi đoán:** máy local của người dùng — cài binary `uv`, cài package `graphifyy`, ghi skill + đăng ký vào `~/.claude/`. Không đụng source graphify, không đụng repo TDQ-Workflow ngoài file brief/log của workflow.
- **Nguồn phân tích:** repo đã clone tại `/Users/tdq/Documents/ForAgentCode/graphify`, bản `0.9.54`, remote `https://github.com/Graphify-Labs/graphify.git`.

**Điểm chưa rõ**

1. Cài `uv` bằng Homebrew hay script chính chủ của Astral — hai đường cho kết quả khác nhau về vị trí binary và cách update.
2. Bản thân graphify **không có** đường cài hook always-on ở user-level; chỉ skill mới ở user-level được. Cần người dùng xác nhận mức độ tích hợp mong muốn.
3. Có nên đụng `~/.claude/CLAUDE.md` hay không, khi file này vừa được thay bằng block TDQ Workflow ở request trước.

## Hiểu & kiến thức

### B1 — Đọc code (luôn chạy)

**Phía graphify** (`/Users/tdq/Documents/ForAgentCode/graphify`, bản 0.9.54):

- `pyproject.toml`: `requires-python = ">=3.10"`, package PyPI tên `graphifyy`, CLI tên `graphify`, entrypoint `graphify.__main__:main`. 30 dependency tree-sitter.
- `graphify/install.py:624` `install()` — đường **user-level**: copy skill vào `~/.claude/skills/graphify/SKILL.md`, rồi ở dòng 674 ghi đăng ký vào `Path.home()/".claude"/"CLAUDE.md"`. Tôn trọng biến môi trường `CLAUDE_CONFIG_DIR` nếu có.
- `graphify/install.py:676` — **cạm bẫy**: `if "graphify" in content` thì in "already registered (no change)" và bỏ qua. `~/.claude/CLAUDE.md` hiện tại đã chứa chuỗi `graphify` (mục "Git & Graphify" của block TDQ) nên bước đăng ký sẽ bị skip im lặng.
- `graphify/install.py:1766` `claude_install()` và `:1794` `_install_claude_hook()` — ghi cứng vào `(project_dir or Path("."))`, tức **project-scoped**, không có nhánh nào rẽ về `Path.home()`. Kết luận: hook always-on của Claude Code **không thể cài user-level**.

**Phía TDQ-Workflow:**

- `scripts/tdq_finish.py:166` dùng `shutil.which("graphify")`; hiện trả None nên bước graphify bị skip. Cài graphify xong thì bước `graphify extract . --code-only` **tự kích hoạt** ở cuối mọi turn có đổi file code — đây là thay đổi hành vi kèm theo, không phải tác dụng phụ ngoài ý muốn.
- `.graphifyignore` đã được tinh chỉnh từ trước (loại `tests/ docs/ portable_* skills/ agents/ ClaudeExport/`), `graphify-out/` đã có `GRAPH_REPORT.md` + `graph.json` + `manifest.json` sinh từ bản 0.9.28/0.9.42.

### B0 — Kiểm kê năng lực: BỎ

Đã có tiền lệ: `docs/tdq/reports/2026-08-14-graphify-chi-source.md` (lane full, QC 9/9) từng làm việc trên đúng vùng này — `.graphifyignore`, `graphify-out/`, luật đọc đồ thị. Không phải đất mới.

### B2 — Research (sub-agent, nguồn devguide.python.org + pyenv wiki + docs.astral.sh)

- **Python không có "LTS".** Tháng 9/2026: 3.14.7 là stable mới nhất (EOL 10/2030); 3.13.15 bugfix (EOL 10/2029); 3.12 security-only (EOL 10/2028); 3.10 hết hạn ngay 10/2026; **3.9 đã EOL từ 31/10/2025** — đúng bản máy đang chạy. An toàn nhất cho tooling: **3.13.x** (đã 2 năm ngoài thị trường, hầu hết package có wheel sẵn); 3.14 vẫn ổn nhưng vài thư viện C-extension còn trễ wheel.
- **pyenv trên macOS ARM** cần build dependency: `openssl@3 readline sqlite3 xz tcl-tk@8 libb2 zstd zlib pkgconfig`. Máy hiện **chưa có cái nào** (brew mới chỉ cài `nvm`). Cạm bẫy: shim phải nằm sớm trong PATH; nên dùng `tcl-tk@8` vì Tcl/Tk 9 còn experimental.
- **pyenv + uv không xung đột.** uv quét theo thứ tự: thư mục managed → PATH. Python do pyenv cài nằm trên PATH nên uv coi là "system" và dùng được. Mặc định `python-preference=managed`. Ép dùng pyenv bằng `UV_PYTHON_PREFERENCE=system` hoặc `--python 3.13`.
- **`uv tool install` đặt binary vào `~/.local/bin`** (venv ở `~/.local/share/uv/tools`). Thư mục này **đã có sẵn trên PATH** của máy (`~/.zshrc` dòng 7-8 và `~/.zprofile` dòng 7), nên nhiều khả năng không cần chạy `uv tool update-shell`.

### Hiện trạng máy (đo trực tiếp)

- Homebrew có sẵn `pyenv 2.8.5` và `uv 0.12.10`, cả hai **chưa cài**. Brew mới chỉ cài đúng `nvm`.
- Xcode Command Line Tools 26.6.0 đã có → đủ toolchain để pyenv biên dịch Python.
- Đĩa còn 420 GB.
- `~/.zshrc` 11 dòng (nvm + PATH + alias `agyp`), `~/.zprofile` có `brew shellenv`. Dòng 7 và 8 của `.zshrc` là **PATH trùng lặp y hệt nhau** — không ảnh hưởng gì, chỉ là rác.

## Hỏi đáp

<!-- điền ở phase analyze -->
