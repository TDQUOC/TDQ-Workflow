# QC — skill tdq-lsp-setup, nhúng agent-lsp vào bộ workflow
Ngày: 2026-08-23 · Plan: ../plan/2026-08-23-0052-skill-tdq-lsp-setup.md · Vòng: 1
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

32 dòng DoD (Q1–Q32) cộng 4 hạng mục cố định QC-F1→F4 = 36 hạng mục.

| # | Hạng mục | Lệnh đã chạy | Kết quả | PASS/FAIL |
|---|---|---|---|---|
| Q1 | Skill tồn tại, đúng luật | `grep -c "github.com/blackwell-systems/agent-lsp" …/SKILL.md`; `grep -c '```python' …` | 1 và 0 | PASS |
| Q2 | Bảng ngôn ngữ đủ 30 | `grep -cE "^\| " …/references/languages.md` | 31 = 1 tiêu đề + 30 ngôn ngữ | PASS |
| Q3 | Script in đủ 6 bậc | `.venv/bin/python scripts/tdq_lsp.py kiem \| grep -cE "^Bậc [1-6]"` | 6 | PASS |
| Q4 | Script không tự cài | `grep -nE "npm i\|brew install\|dotnet tool install" scripts/tdq_lsp.py` | 16 dòng, đều là dữ liệu bảng hoặc `print`; không dòng nào nằm trong `subprocess` | PASS |
| Q5 | Log timestamp, tắt được | `kiem` và `TDQ_LOG=0 … kiem` | có dòng `[2026-08-23T10:30:34]`; với `TDQ_LOG=0` không còn dòng nào | PASS |
| Q6 | Test script xanh | `.venv/bin/python -m pytest tests/test_tdq_lsp.py -q` | 30 passed | PASS |
| Q7 | Móc intake | `grep -n "tdq_lsp.py" skills/tdq-intake/SKILL.md` | dòng 48 (bước 1b) kèm câu xin phép ở dòng 50 | PASS |
| Q8 | Luật mềm ở build | `grep -n "LSP" skills/tdq-build/SKILL.md` | dòng 38–43, nằm trong `## Hard rules` | PASS |
| Q9 | Luật được khoá thật | `pytest tests/test_tdq_lsp_skill.py -q` + chu trình xoá dòng luật ở 5 file (chạy ở P3) | 4 passed, 10 subtests; mỗi lần xoá đều ĐỎ đúng file | PASS |
| Q10 | MCP đăng ký thật | `claude mcp list \| grep -i lsp` | `lsp: agent-lsp … - ✔ Connected` | PASS |
| Q11 | Language server cài thật | `agent-lsp doctor`; `which lua-language-server` | c/cpp/csharp/javascript/python/typescript đều `Status: ok`; `/opt/homebrew/bin/lua-language-server` | PASS |
| Q12 | Gọi thật tool `mcp__lsp__*` | — | CHẶN: MCP đăng ký trong phiên này nên tool chỉ nạp từ phiên sau | TREO |
| Q13 | Quyền tool | `grep -n "mcp__lsp__" ~/.claude/settings.json` | dòng 15: `"mcp__lsp__*"` | PASS |
| Q14 | Portable đủ | `ls` skill và script trong hai bản | `portable_claude/.claude/skills/tdq-lsp-setup`, `portable_codex/.agents/skills/tdq-lsp-setup`, `portable_claude/.claude/tdq/scripts/tdq_lsp.py`, `portable_codex/scripts/tdq_lsp.py` — cả 4 tồn tại | PASS |
| Q15 | Lint tài liệu | `doc_lint.py` 5 file và `--pair` cặp spec–plan | 0 violation, exit 0 cả hai | PASS |
| Q16 | Suite tổng giữ mốc | `.venv/bin/python -m pytest tests/ -q` | 37 failed, 1349 passed — đúng mốc nền, toàn bộ trong `test_skill_router.py` | PASS |
| Q17 | Móc bước đọc code | `grep -n "LSP" …/analyze-full.md` | dòng 19–24 ở bước 2 | PASS |
| Q18 | Móc spec và plan | `grep -c "uu-tien-tim-kiem.md"` hai file | mỗi file 1 | PASS |
| Q19 | Móc tìm-trước-khi-tạo | `grep -n` trong `tdq-build/SKILL.md` | `mcp__lsp__find_symbol` dòng 82 < `graphify query` dòng 84 | PASS |
| Q20 | 4 chỗ móc không lệch | `pytest tests/test_tdq_lsp_skill.py -q -k khop` | 1 passed | PASS |
| Q21 | Thứ tự ưu tiên ghi rõ | `grep -n "agent-lsp" …/uu-tien-tim-kiem.md` | dòng 9 nêu thứ tự, dòng 57 nêu nhánh lumen hỏng | PASS |
| Q22 | Bậc lumen không chặn | chạy `kiem` với PATH không có `ollama` | bậc 5 CẢNH BÁO, 5/6 bậc ĐẠT, `rc=0` | PASS |
| Q23 | Hook plugin là gợi ý | `grep -in "hook" …/uu-tien-tim-kiem.md` | dòng 66: hook plugin là SUGGESTION, không phải luật | PASS |
| Q24 | Lumen chỉ chạy khi LSP rỗng | `grep -in "rỗng" …/uu-tien-tim-kiem.md` | dòng 14 trong câu luật gốc | PASS |
| Q25 | Đánh thức chạy thật | `cmd_danh_thuc` trên cổng phụ 11999 (không đụng daemon user) | "Ollama đã dậy ở cổng 11999 (pid 34584)", `curl` trả `models` | PASS |
| Q26 | Nhả model chạy thật | `scripts/tdq_lsp.py nha`; `ollama ps` | bảng `ollama ps` rỗng sau khi nhả | PASS |
| Q27 | Không tắt nhầm của user | `nha` khi daemon do lumen/user bật | "không có dấu sở hữu, giữ daemon"; `curl localhost:11434` vẫn trả lời | PASS |
| Q28 | Quá hạn không chặn | `cmd_danh_thuc(han_cho=2)` với shim `ollama` không lên cổng | "Ollama không dậy trong 2s — … tìm tiếp bằng grep", `rc=0` | PASS |
| Q29 | Hook lumen đã gỡ thật | `grep -c` trên `hooks.json` của plugin | `PreToolUse`=0, `SessionStart`=1, có `hooks.json.bak-tdq-lsp-0.0.42-20260823-100731` | PASS |
| Q30 | Hết chèn dòng giục | — | CHẶN: hook nạp lúc mở phiên, dòng giục còn tới hết phiên này | TREO |
| Q31 | Bậc 6 bắt được hook | dựng lại khối `PreToolUse` từ bản sao lưu → `kiem` → gỡ lại → `kiem` | CẢNH BÁO kèm đúng đường dẫn, rồi ĐẠT | PASS |
| Q32 | Bậc 6 không tự sửa | `grep -nE "open\(.*w\|write_text\|unlink\|rename" scripts/tdq_lsp.py` | 1 dòng duy nhất (344) ghi dấu sở hữu trong thư mục tạm, không dòng nào nhắm cache plugin | PASS |
| QC-F1 | Suite tổng | `.venv/bin/python -m pytest tests/ -q` | 37 failed, 1349 passed, 1458 subtests passed | PASS |
| QC-F2 | Hồi quy vùng chạm | pytest 9 file test của mọi vùng `Chạm:` | 191 passed, 421 subtests passed | PASS |
| QC-F3 | Ràng buộc kiến trúc | xem mục bằng chứng | 3/3 dòng ràng buộc còn nguyên | PASS |
| QC-F4 | Clean code | 5 câu self-check | 5/5 "có" | PASS |

## Bằng chứng

### Q16 / QC-F1
```
37 failed, 1349 passed, 1458 subtests passed in 259.60s (0:04:19)
```
Cả 37 đỏ nằm trong `tests/test_skill_router.py` — đúng mốc nền ghi ở plan. Đợt này có 11 test
đỏ thêm rồi được sửa hết: 4 neo luật `tdq-plan` trong `luat-hien-co.md` (chép câu đã nén),
42 số dòng lệch trong cùng bảng, trần ký tự description (1450 → 1620 vì skill thứ 8),
`SKILL_LINE_LIMITS` thiếu `tdq-lsp-setup`, hai test hard-code số thứ tự file portable
(`03-spec.md`/`06-checkportable`), và một dòng `tdq-plan` bị chú thích `i18n-allow` chen vào
giữa cụm "sub-agent implement … in parallel".

### Q22
```
Bậc 5 · sức khoẻ lumen → CẢNH BÁO (thiếu ollama — lumen không chạy được)
Tổng: 5/6 bậc ĐẠT · 1 cảnh báo không chặn
rc=0
```

### Q25 → Q26 → Q27
```
Ollama đã dậy ở cổng 11999 (pid 34584). Tìm xong nhớ chạy `nha`.
Đã tắt daemon Ollama do script bật (pid 34584).
--- cổng user 11434 vẫn sống ---  {"models":[{"name":"ordis/jina-embeddings-v2-base-code:lates
```
Cổng phụ dùng để không đụng daemon 11434 của user; `nha` tắt đúng daemon nó bật, để nguyên
daemon còn lại.

### Q31
```
Bậc 6 · hook plugin ngoài xung đột → CẢNH BÁO (lumen@claude-plugins-official (matcher Grep|Bash)
  tại ~/.claude/plugins/cache/claude-plugins-official/lumen/0.0.42/hooks/hooks.json)
  Xử lý: BÁO cho user và XIN PHÉP trước khi gỡ khối PreToolUse; script không tự sửa file plugin
Bậc 6 · hook plugin ngoài xung đột → ĐẠT (không plugin nào chèn thứ tự tìm kiếm khác)
```

### QC-F3 — ràng buộc kiến trúc
- "skills chỉ nhắc tên lệnh": `grep -cE '^import |^def ' skills/tdq-lsp-setup/SKILL.md` ra 0,
  `grep -c 'tdq_lsp.py'` ra 4 → skill gọi tên lệnh, không chép nội dung script.
- "file code mới nằm trong scripts/ hoặc hooks/": `scripts/tdq_lsp.py` tồn tại; `.graphifyignore`
  loại `skills/` nên đặt ở đó là sai — đã đặt đúng.
- "portable là sinh, không sửa tay": cả hai bản sinh lại bằng `python3 scripts/build_portable.py`
  ở T6.1; không file nào trong hai thư mục được sửa tay.
- Rủi ro "agent-lsp init ghi đè MCP config" KHÔNG xảy ra: `~/.claude.json` còn đủ 6 server user
  scope (5 cũ + `lsp`), `claude mcp list` báo 14 server Connected, không server nào lỗi.

### QC-F4 — clean code (`scripts/tdq_lsp.py`, `scripts/build_portable.py`)
- SRP — có: mỗi bậc là một hàm `_bac_N` chỉ dò một điều kiện; `cmd_kiem/danh-thuc/nha` mỗi lệnh
  một việc.
- OCP — có: thêm ngôn ngữ là thêm một dòng vào `NGON_NGU`; thêm skill vào bản portable là thêm
  một dòng vào `THU_TU_SKILL`, không mở thân hàm nào.
- LSP — có: mọi bậc trả cùng kiểu `(dat, chi_tiet, cach_sua, chi_canh_bao)`; mọi `cmd_*` trả
  `EXIT_OK` hoặc `EXIT_THIEU`, không nhánh nào ném ra ngoài.
- ISP — có: không hàm nào nhận tham số rồi bỏ không dùng; `cmd_nha(args)` giữ `args` vì khuôn
  dispatch của `argparse` đòi, đây là ràng buộc thư viện chứ không phải tham số thừa.
- DIP — có: log đi qua `_log` chung, chạy tiến trình con đi qua `_run` chung; không nơi nào tự
  gọi `subprocess` với khuôn riêng.

### Q12 và Q30 — hai hạng mục TREO
Cả hai chặn vì cùng một lý do kỹ thuật, không phải vì thiếu việc:
- Q12: MCP server `lsp` được đăng ký trong chính phiên này. Claude Code nạp danh sách MCP lúc mở
  phiên, nên tool `mcp__lsp__*` chỉ xuất hiện từ phiên sau. `ToolSearch` trong phiên này không
  tìm thấy tool nào. Bậc 2 và `claude mcp list` đã chứng minh server sống và Connected.
- Q30: hook `PreToolUse` của lumen đã bị gỡ khỏi `hooks.json` (Q29), nhưng hook đã nạp vào phiên
  từ lúc mở, nên dòng giục còn chèn tới hết phiên này.

Cách kiểm sau khi mở phiên mới: gọi `mcp__lsp__go_to_definition` trên một hàm có thật của repo
(ví dụ `cmd_kiem` trong `scripts/tdq_lsp.py`) và đối chiếu file + dòng; chạy một lệnh Bash bất kỳ
và xem đầu ra còn dòng giục dùng lumen thay Grep không.

## Kết luận
PASS 34/36. Hai hạng mục TREO (Q12, Q30) chờ mở phiên mới; không hạng mục nào FAIL. Task T4.5
của plan cũng treo vì cùng lý do với Q12.
