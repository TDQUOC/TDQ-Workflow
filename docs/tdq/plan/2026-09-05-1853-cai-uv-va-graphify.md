# QUICK — Cài pyenv + Python 3.13, uv, và graphify vào Claude Code user-level

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

**Ngày:** 2026-09-05 · Brief: ../brief/2026-09-05-1853-cai-uv-va-graphify.md · Lane: quick
**Trạng thái:** CHỜ DUYỆT
**Ước tính sẽ dùng skill:** không có

## Phạm vi
- Trong: cài pyenv + build deps qua brew; Python **3.13.x** (Python KHÔNG có LTS — 3.13 là bản bugfix an toàn nhất cho tooling, EOL 10/2029); cài uv qua brew; `uv tool install graphifyy`; đăng ký skill graphify ở user-level.
- NGOÀI: hook graphify project-level (`graphify claude install`) — cấu trúc của nó chỉ ghi vào `<project>/.claude/settings.json`, không có nhánh user-level; để bạn quyết sau.
- Trong: **cách ly tuyệt đối với Python gốc của máy.** Python mới nằm hẳn trong `~/.pyenv/versions/`, không ghi đè `/usr/bin/python3` và không chạm `/Library/Frameworks`. Không lệnh nào dùng `sudo`. Shim pyenv chỉ được nạp qua `~/.zshrc` (shell tương tác của user) → macOS và mọi script hệ thống gọi `/usr/bin/python3` bằng đường dẫn tuyệt đối vẫn chạy Python 3.9.6 y như cũ. Python 3.13 là mặc định cho **project/app mới của user**.
- NGOÀI: đổi Python mặc định của hệ thống; dọn dòng PATH trùng ở `~/.zshrc`.
- Bỏ B0: đã có tiền lệ `docs/tdq/reports/2026-08-14-graphify-chi-source.md` chạm cùng vùng.

## Task
- [x] **T1** `brew install pyenv openssl@3 readline sqlite3 xz tcl-tk@8 libb2 zstd zlib pkgconfig` — Test: `pyenv --version` in ra `pyenv 2.8.x`
- [x] **T2** Thêm 3 dòng `PYENV_ROOT` / `PATH` / `eval "$(pyenv init - zsh)"` vào `~/.zshrc` (idempotent: grep trước, có rồi thì bỏ qua) — Chạm: `~/.zshrc` — Test: `zsh -lic 'type pyenv'` in ra `pyenv is a shell function`
- [x] **T3** `pyenv install 3.13.15` rồi `pyenv global 3.13.15` — Test: `zsh -lic 'python3 -V'` in ra `Python 3.13.15`
- [x] **T4** `brew install uv` — Test: `uv --version` in ra `uv 0.12.x`
- [x] **T5** `uv tool install graphifyy` (uv tự lấy Python managed ≥3.10; không đụng pyenv global) — Test: `graphify --version` chạy được từ `~/.local/bin`
- [x] **T6** `graphify install` để tạo skill user-level, rồi **vá tay** khối đăng ký vào `~/.claude/CLAUDE.md` — Chạm: `~/.claude/skills/graphify/SKILL.md`, `~/.claude/CLAUDE.md` — Test: file SKILL.md tồn tại VÀ `~/.claude/CLAUDE.md` chứa dòng trigger `/graphify`
  - Lý do vá tay: `install.py:676` kiểm `if "graphify" in content` → `~/.claude/CLAUDE.md` đã có chữ "graphify" ở mục *Git & Graphify*, nên nó sẽ **im lặng bỏ qua** phần đăng ký. Backup `.bak-<timestamp>` trước khi sửa.

- [x] **T7** Nghiệm thu cách ly: xác nhận Python gốc không suy suyển sau khi cài xong — Test: 4 dòng DoD nhóm "cách ly" bên dưới đều xanh
  - Chạm: không sửa gì, chỉ đo.

## Definition of Done

**Nhóm cách ly (quan trọng nhất — Python gốc phải nguyên vẹn)**
- `/usr/bin/python3 -V` vẫn in `Python 3.9.6` và `/usr/bin/python3 -c 'import ssl,sqlite3;print("ok")'` in `ok`
- `ls -la /usr/bin/python3` không phải symlink trỏ vào `~/.pyenv` (vẫn trỏ `../../Library/Developer/CommandLineTools/usr/bin/python3`)
- `env -i /bin/zsh -c 'command -v python3'` (shell KHÔNG nạp `~/.zshrc`) vẫn ra `/usr/bin/python3` — chứng minh script hệ thống không bị đổi
- Không có file nào được tạo ngoài `~/.pyenv`, `~/.local`, `~/.zshrc`, `~/.claude`, và cây Homebrew; không lệnh nào chạy `sudo`

**Nhóm chức năng**
- `zsh -lic 'python3 -V'` → `Python 3.13.15`, và `zsh -lic 'command -v python3'` trỏ vào `~/.pyenv/shims/python3` (Python mới là mặc định cho project mới của user)
- `uv --version` và `pyenv --version` cùng chạy được trong shell login mới
- `graphify --version` chạy được; `graphify extract . --code-only` trong repo này chạy không lỗi
- `~/.claude/skills/graphify/SKILL.md` tồn tại và `~/.claude/CLAUDE.md` có khối đăng ký graphify kèm trigger `/graphify`

## QC

**Q1 — test của từng task: PASS**
- T1 `pyenv --version` → `pyenv 2.8.5`; `brew list` có đủ `libb2 openssl@3 pkgconf pyenv readline sqlite tcl-tk@8 xz zlib zstd`
- T2 `zsh -lic 'type pyenv'` → `pyenv is a shell function from /Users/tdq/.zshrc`
- T3 `zsh -lic 'python3 -V'` → `Python 3.13.15`
- T4 `uv --version` → `uv 0.12.10 (Homebrew 2026-09-04 aarch64-apple-darwin)`
- T5 `graphify --version` → `graphify 0.9.55`, binary tại `/Users/tdq/.local/bin/graphify`
- T6 `~/.claude/skills/graphify/SKILL.md` 41.276 byte; `grep -c '/graphify' ~/.claude/CLAUDE.md` → `3`
- T7 xem Q2–Q5

**Q2 — DoD "`/usr/bin/python3 -V` vẫn in `Python 3.9.6` và stdlib import `ok`": PASS**
`/usr/bin/python3 -V` → `Python 3.9.6`; `import ssl,sqlite3,ctypes` → `ok`

**Q3 — DoD "`ls -la /usr/bin/python3` không phải symlink trỏ vào `~/.pyenv`": PASS**
`-rwxr-xr-x  78 root  wheel  118928 Jun 25 09:29 /usr/bin/python3` — **y hệt baseline đo trước khi cài** (cùng size, cùng mtime, cùng số hardlink 78, không phải symlink).

**Q4 — DoD "`env -i /bin/zsh -c 'command -v python3'` vẫn ra `/usr/bin/python3`": PASS**
→ `/usr/bin/python3`. Chứng minh script hệ thống / cron / launchd (không nạp `~/.zshrc`) vẫn dùng Python gốc.

**Q5 — DoD "không tạo file ngoài vùng cho phép, không dùng `sudo`": PASS**
Ghi vào đúng `~/.pyenv/versions/3.13.15`, `~/.local/{bin,share/uv}`, `~/.zshrc`, `~/.claude/`, và cây Homebrew `/opt/homebrew`. `/Library/Frameworks/Python.framework` **không tồn tại** (không cài Python bản python.org). Toàn bộ 6 task không lệnh nào chạy `sudo`.

**Q6 — DoD "shell login: `python3` → 3.13.15 tại shims": PASS**
`zsh -lic` → `Python 3.13.15` và `command -v python3` → `/Users/tdq/.pyenv/shims/python3`

**Q7 — DoD "`uv` và `pyenv` cùng chạy trong shell login mới": PASS**
`uv 0.12.10` · `pyenv 2.8.5`

**Q8 — DoD "`graphify extract . --code-only` chạy không lỗi": PASS**
`51 code files → graph.json: 2016 nodes, 4285 edges, 78 communities`. Có 1 WARNING về prune entry `.claude/settings.local.json` — **lỗi cấu hình có sẵn của repo**, không do lần cài này, không chặn extract.

**Q9 — DoD "`~/.claude/skills/graphify/SKILL.md` tồn tại + CLAUDE.md có trigger `/graphify`": PASS**
`graphify install --platform claude` in ra `CLAUDE.md -> already registered (no change)` đúng như cảnh báo trong plan → đã **vá tay** khối đăng ký. Backup: `~/.claude/CLAUDE.md.bak-20260906-100617`.

## Ghi chú vận hành
- graphify chạy trong venv riêng với Python **3.10.21 do uv quản lý** (`~/.local/share/uv/python/cpython-3.10.21-...`), độc lập cả với pyenv global lẫn Python hệ thống — nâng/hạ Python của user không làm hỏng graphify.
- `~/.zshrc` chỉ nạp pyenv khi `command -v pyenv` thành công, nên xoá pyenv sau này cũng không làm shell lỗi. Backup: `~/.zshrc.bak-20260906-100326`.
