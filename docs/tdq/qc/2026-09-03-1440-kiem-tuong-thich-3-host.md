# QC — Sửa tương thích 3 host (Claude Code / Codex 0.149 / agy 1.1.11)
Ngày: 2026-09-03 · Plan: ../plan/2026-09-03-1440-kiem-tuong-thich-3-host.md · Vòng: 1
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

11 dòng DoD → Q1–Q11, cộng 4 hạng mục cố định QC-F1→F4.

| # | Hạng mục | Lệnh đã chạy | Kết quả | PASS/FAIL |
|---|---|---|---|---|
| Q1 | `plugin.json` hợp lệ, cây `skills/` đúng chuẩn agy | `agy plugin validate antigravity_portable` | `[ok]` · 9 skills, 2 mcpServers, 2 hooks processed | PASS |
| Q2 | README agy đúng 3 đường thật, không còn `antigravity-cli/skills` | `grep -c "config/plugins"` · `grep -c "antigravity-cli/skills"` | 2 · 0 | PASS |
| Q3 | Bundle agy không còn `config/settings.json` | `test -e antigravity_portable/config/settings.json` | không tồn tại | PASS |
| Q4 | Payload deny agy có cả `allow_tool` và `decision` | `pytest tests/test_tuong_thich_host.py -k deny` | 1 passed | PASS |
| Q5 | Không còn `~` chưa bung trong `hooks.json` agy | `grep -c '"~' antigravity_portable/hooks.json` | 0 | PASS |
| Q6 | README codex có mục trust hook + export biến | `grep -c trusted_hash` · `grep -c "export TAVILY_API_KEY"` | 1 · 1 | PASS |
| Q7 | `plugin.json` có `displayName` + `userConfig`, validate exit 0 | `claude plugin validate .` | `✔ Validation passed` | PASS |
| Q8 | `tdq_checkportable.py check` ra `CLEAN` cả 3 bundle | `check --root <3 bundle>` | CLEAN 85 · 142 · 92 | PASS |
| Q9 | Bộ test tương thích host xanh | `pytest tests/test_tuong_thich_host.py -q` | 6 passed | PASS |
| Q10 | `pytest -q` không quá 100 đỏ | `pytest -q` | 100 failed, 1478 passed | PASS |
| Q11 | `doc_lint.py` exit 0 trên mọi `.md` đã sửa | `doc_lint.py <plan> <spec>` | 0 violation, exit 0 | PASS |
| QC-F1 | Toàn bộ test suite | `pytest -q` | 100 failed / 1478 passed / 1423 subtests, 96.7 s | PASS |
| QC-F2 | Regression vùng `Chạm:` | `pytest` trên 5 file test của vùng chạm | 128 passed | PASS |
| QC-F3 | Ràng buộc kiến trúc spec §5 | xem `## Bằng chứng` | 2/2 giữ nguyên | PASS |
| QC-F4 | Clean code — 5 câu tự kiểm | xem `## Bằng chứng` | 5/5 yes | PASS |

## Bằng chứng

### Q1
```
  [ok]    antigravity_portable
          ✔ skills      : 9 processed
          - agents      : skipped (not found)
          - commands    : skipped (not found)
          ✔ mcpServers  : 2 processed
          ✔ hooks       : 2 processed
```
Chính agy 1.1.11 đọc được bundle: nó nhận cả `hooks.json` lẫn `mcp_config.json` ở gốc plugin —
bằng chứng mạnh hơn `agy plugin list` (lệnh đó chỉ liệt kê plugin ĐÃ import).

### Q5
```
python3 /Users/truongdinhquoc/.gemini/config/plugins/tdq-workflow/hooks/scripts/agy_pretooluse_gate.py
```

### Q7
```
Validating marketplace manifest: .claude-plugin/marketplace.json
✔ Validation passed
```
Vòng đầu FAIL: validator đòi trường `title` cho mỗi mục `userConfig` — tài liệu không nêu.
Đã thêm `title` cho cả 2 khoá rồi validate lại.

### Q8
```
CLEAN    85 file(s) match the manifest      (antigravity_portable)
CLEAN    142 file(s) match the manifest     (portable_codex)
CLEAN    92 file(s) match the manifest      (portable_claude)
```

### Q10 / QC-F1
```
100 failed, 1478 passed, 1423 subtests passed in 96.86s
```
Mốc đỏ có sẵn là 100 — không tăng. Trong vòng chạy đầu số đỏ lên 106 vì 6 test cũ đang khoá
LAYOUT CŨ của bundle agy (`config/hooks.json`, `config/settings.json`) và 1 test đòi mọi lệnh
`python3 <file>.py` nêu trong README phải có thật trong chính bundle đó. Đã sửa: 5 test agy
viết lại theo layout plugin mới (thêm `test_plugin_json_dung_khuon_agy`,
`test_khong_ship_settings_json`), và bỏ chuỗi `python3 scripts/build_portable.py` khỏi README
codex/agy vì `build_portable.py` cố tình KHÔNG ship trong bundle.

### QC-F2
```
tests/test_build_portable.py tests/test_tuong_thich_host.py tests/test_checkportable.py → 87 passed
tests/test_agy_hooks.py tests/test_plugin_tiers.py                                      → 41 passed
```
Không có nút nào trong vùng chạm thiếu test.

### QC-F3
- Ràng buộc 1 — không sửa tay file trong 3 bundle: mọi thay đổi làm ở `scripts/build_portable.py`
  rồi dựng lại; `check` ra CLEAN trên cả 3 (Q8) chứng minh cây file khớp manifest do bộ sinh ghi.
- Ràng buộc 2 — không ghi ra ngoài repo: không chạy lệnh GHI nào vào `~/.gemini` hay `~/.codex`.
  Chỉ dùng lệnh ĐỌC `codex --version`, `agy --version`, `agy plugin list`, `agy plugin validate`,
  `ls ~/.gemini/config/plugins`. Lệnh cài agy chỉ được IN trong README cho người dùng tự chạy.

### QC-F4
1. Tên nói đúng việc? — yes (`goc_agy_tuyet_doi`, `kiem_layout_agy`, `_sinh_plugin_json_agy`).
2. Hàm làm đúng một việc? — yes; `_sinh_settings_agy` bị bỏ hẳn thay vì để chết.
3. Không lặp? — yes; hằng `GOC_AGY`/`TEN_PLUGIN_AGY` là nguồn duy nhất, README và hooks.json
   cùng đọc từ đó.
4. Comment giải thích VÌ SAO? — yes; mỗi chỗ sửa ghi rõ bằng chứng khảo sát máy thật và ngày.
5. Không placeholder/TODO? — yes.

## Kết luận
PASS toàn bộ — 15/15 hạng mục, không có vòng fix nào phải để lại.
