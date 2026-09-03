# PLAN — Sửa tương thích 3 host (Claude Code 2.x / Codex 0.149 / agy 1.1.11)

Trạng thái plan: HOÀN THÀNH · mode: main (user chốt "a" lúc 14:57) · Spec: ../spec/2026-09-03-1440-kiem-tuong-thich-3-host.md

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

Mode thực thi: main — 14 task nhưng 9 task cùng chạm đúng một file `scripts/build_portable.py`,
không cắt sóng song song được mà không tranh file.

## P1 — Bundle agy về đúng layout agy 1.1.11

- [x] **T1.1** (e10m) Đổi hằng đường dẫn agy trong bộ sinh: bỏ `GOC_AGY`, `AGY_SKILL_PATHS`,
  `AGY_HOOKS_CONFIG_PATHS`, `AGY_SETTINGS_PATHS`, `AGY_MCP_PATHS`; thay bằng một hằng gốc plugin
  `~/.gemini/config/plugins/tdq-workflow` — Test: `grep -c "antigravity-cli/tdq" scripts/build_portable.py` = 0
  Chạm: `scripts/build_portable.py`
- [x] **T1.2** (e8m) Sinh `antigravity_portable/plugin.json` đúng khuôn agy (`{"name": "tdq-workflow"}`
  cộng `description`), đặt ở gốc bundle — Test: `python3 -c "import json;d=json.load(open('antigravity_portable/plugin.json'));assert d['name']=='tdq-workflow'"`
  Chạm: `scripts/build_portable.py`, `antigravity_portable/plugin.json`
- [x] **T1.3** (e6m) Bỏ hàm `_sinh_settings_agy` và mọi lối gọi nó; bundle không còn
  `config/settings.json` — Test: `test -e antigravity_portable/config/settings.json` trả về sai
  Chạm: `scripts/build_portable.py`
- [x] **T1.4** (e6m) Chuyển `hooks.json` và `mcp_config.json` vào gốc bundle theo chuẩn plugin agy,
  bỏ thư mục `config/` — Test: `ls antigravity_portable/hooks.json antigravity_portable/mcp_config.json` exit 0
  Chạm: `scripts/build_portable.py`
- [x] **T1.5** (e12m) Viết lại `README_AGY`: 3 bước thật (đặt thư mục plugin · bật trong
  `~/.gemini/config/config.json` khoá `plugins.tdq-workflow.enabled` · thêm đường skill vào
  `~/.gemini/config/skills.json`), kèm cách tự kiểm `agy plugin list` — Test: `grep -c "config/plugins" antigravity_portable/README.md` ≥ 1 và `grep -c "antigravity-cli/skills" antigravity_portable/README.md` = 0
  Chạm: `scripts/build_portable.py`, `antigravity_portable/README.md`

## P2 — Hợp đồng hook agy

- [x] **T2.1** (e8m) `command` trong `hooks.json` agy sinh ra bằng đường dẫn TUYỆT ĐỐI đã bung `~`
  (dùng `os.path.expanduser`), không còn dấu `~` trong chuỗi — Test: `grep -c '"~' antigravity_portable/hooks.json` = 0
  Chạm: `scripts/build_portable.py`
- [x] **T2.2** (e8m) Payload deny của `agy_pretooluse_gate.py` phát cả `allow_tool: false` lẫn
  `decision: "deny"` trong cùng một JSON, kèm ghi chú nguồn — Test: gọi hàm deny, khẳng định JSON có đủ 2 khoá
  Chạm: `hooks/scripts/agy_pretooluse_gate.py`
- [x] **T2.3** (e5m) Cập nhật docstring 2 hook agy: bỏ câu "schema chưa xác nhận 2026-08", thay
  bằng nguồn đã tra và ngày — Test: `grep -c "2026-08" hooks/scripts/agy_*.py` = 0
  Chạm: `hooks/scripts/agy_pretooluse_gate.py`, `hooks/scripts/agy_stop_gate.py`

## P3 — Codex: trust hook + biến môi trường

- [x] **T3.1** (e10m) Thêm mục `## Trust hook` vào README codex: giải thích `trusted_hash` ghim nội
  dung, nên dựng lại bundle là phải duyệt lại bằng `/hooks` — Test: `grep -c "trusted_hash" portable_codex/README.md` ≥ 1
  Chạm: `scripts/build_portable.py`, `portable_codex/README.md`
- [x] **T3.2** (e6m) Thêm mục export biến môi trường: nêu rõ `env_vars` chỉ khai TÊN biến nên người
  dùng phải tự `export` trước khi mở codex — Test: `grep -c "export TAVILY_API_KEY" portable_codex/README.md` ≥ 1
  Chạm: `scripts/build_portable.py`, `portable_codex/README.md`

## P4 — Kê khai plugin Claude Code

- [x] **T4.1** (e8m) Thêm `displayName` và `userConfig` (2 biến Tavily, `sensitive: true`) vào
  `.claude-plugin/plugin.json` — Test: `claude plugin validate .` exit 0
  Chạm: `.claude-plugin/plugin.json`
- [x] **T4.2** (e5m) Sửa mô tả marketplace: bỏ chữ "Local marketplace" nay repo đã công khai — Test: `grep -c "Local marketplace" .claude-plugin/marketplace.json` = 0
  Chạm: `.claude-plugin/marketplace.json`

## P5 — Bộ kiểm và test

- [x] **T5.1** (e10m) `tdq_checkportable.py` hiểu layout agy mới: kiểm `plugin.json` ở gốc thay vì
  `config/` — Test: `python3 scripts/tdq_checkportable.py check --root antigravity_portable` in `CLEAN`
  Chạm: `scripts/tdq_checkportable.py`
- [x] **T5.2** (e15m) `tests/test_tuong_thich_host.py` — khoá 6 điểm: plugin.json agy, không còn
  settings.json, không còn `~` trong hooks agy, payload 2 khoá, README codex có trust, plugin.json
  Claude có userConfig — Test: `pytest tests/test_tuong_thich_host.py -q` xanh
  Chạm: `tests/test_tuong_thich_host.py`
- [x] **T5.3** (e10m) Dựng lại 3 bundle rồi kiểm bằng hiệu ứng trên host thật: `agy plugin list` và
  `codex --version`, chỉ lệnh ĐỌC — Test: `agy plugin validate antigravity_portable` exit 0 (thay cho `agy plugin list` — xem quyết định trong working log)
  Chạm: `antigravity_portable/`, `portable_codex/`, `portable_claude/`

## Hợp đồng công cụ

- Dùng: Sinh bundle portable
  - Để: dựng lại 3 thư mục bundle sau mỗi lần đổi hằng đường dẫn hoặc README
  - Ra: `portable_claude/`, `portable_codex/`, `antigravity_portable/` kèm `manifest.json`
  - Kiểm: lệnh exit 0 và in đủ 3 dòng số file
  - Không dùng cho: sửa tay file bên trong bundle

- Dùng: Kiểm bundle
  - Để: đối chiếu cây file thật với manifest sau khi dựng
  - Ra: dòng `CLEAN`/`MISSING`/`DRIFT`/`NOTE` cho từng bundle
  - Kiểm: cả 3 bundle ra `CLEAN`
  - Không dùng cho: ghi ra ngoài repo — chỉ nhánh `--trust` được phép, và task này không dùng nhánh đó

- Dùng: Kiểm bằng hiệu ứng trên host thật
  - Để: xác nhận agy nhận plugin và codex còn đúng version đã khảo sát
  - Ra: dòng `tdq-workflow` trong `agy plugin list`, chuỗi version của `codex --version`
  - Kiểm: hai lệnh exit 0 và có chuỗi mong đợi
  - Không dùng cho: mọi lệnh GHI vào `~/.gemini` hay `~/.codex`

- Dùng: Kê khai plugin Claude
  - Để: xác nhận `plugin.json` sau khi thêm `displayName` và `userConfig` vẫn hợp lệ
  - Ra: kết quả validate của Claude Code
  - Kiểm: exit 0
  - Không dùng cho: cài hay bật plugin trên máy người dùng

- Dùng: Lint tài liệu
  - Để: giữ mọi `.md` sửa trong luật R5/R6/R11
  - Ra: số phát hiện và mã thoát
  - Kiểm: exit 0
  - Không dùng cho: file trong `docs/archive/`

## Cụm song song

Không cắt sóng: T1.1–T1.5, T2.1, T3.1, T3.2 cùng ghi `scripts/build_portable.py`.

## Definition of Done

- [x] `antigravity_portable/plugin.json` hợp lệ, cây `skills/` đúng chuẩn agy.
- [x] README agy hướng dẫn đúng 3 đường thật, không còn đường `antigravity-cli/skills`.
- [x] Bundle agy không còn `config/settings.json`.
- [x] Payload deny agy chứa cả `allow_tool` và `decision`.
- [x] Không còn dấu `~` chưa bung trong `hooks.json` agy.
- [x] README codex có mục trust hook và mục export biến môi trường.
- [x] `plugin.json` có `displayName` + `userConfig`; `claude plugin validate .` exit 0.
- [x] `tdq_checkportable.py check` ra `CLEAN` trên cả 3 bundle.
- [x] `pytest tests/test_tuong_thich_host.py -q` xanh.
- [x] `pytest -q` không quá 100 đỏ.
- [x] `doc_lint.py` exit 0 trên mọi `.md` đã sửa.
