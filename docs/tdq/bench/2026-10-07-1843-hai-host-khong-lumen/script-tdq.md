# Script TDQ khi binary lumen vắng — 2026-10-07

Cách giả lập: bản sao repo `git clone --local` ở `%TEMP%/tdq-thu-script` (`TDQ_PROJECT_DIR` trỏ vào đó), chạy qua wrapper `%TEMP%/tdq-gia-lap/khong_lumen.py` vá đúng bộ dò duy nhất của TDQ: `tdq_lsp._binary_lumen = lambda: ''` và `tdq_lsp._lumen_thieu_binary_windows = lambda: ('', '')` — đúng như sau khi thư mục `~/.claude/plugins/cache/*/lumen` biến mất. Ollama vẫn chạy (user giữ ollama).

Lần thử đầu bằng `USERPROFILE` tạm bị LOẠI: nó che luôn `~/.claude.json`, `settings.json`, model ollama → bậc 2, 4, model báo THIẾU oan (nhiễu giả lập, không phải do lumen). Lần thử đó còn lộ một lỗi KHÔNG liên quan lumen: `setup_status.py` ném `TypeError: 'NoneType' object is not iterable` (`thu_workflow`, dòng 331) khi dự án chưa có `docs/tdq/state.json`.

```
=================== $ khong_lumen.py tdq_lsp check
[2026-10-07T20:02:27] bậc 5 sức khoẻ lumen → THIẾU
[2026-10-07T20:02:27] bậc 6 hook plugin ngoài xung đột → ĐẠT
[2026-10-07T20:02:27] bậc 7 cấu hình gốc import theo ngôn ngữ → ĐẠT
[2026-10-07T20:02:27] bậc 8 đồ thị graphify → ĐẠT
[2026-10-07T20:02:29] done · 0 bậc thiếu · 1 cảnh báo · 1 tầng trượt
Bậc 1 · binary agent-lsp → ĐẠT (0.19.2)
Bậc 2 · MCP `lsp` → ĐẠT (2 server đã đăng ký)
Bậc 3 · language server theo project → ĐẠT (đủ cho 2 ngôn ngữ: HTML, Python, khởi động thử ok)
Bậc 4 · quyền tool `mcp__lsp__*` → ĐẠT (1 mục trong allow)
Bậc 5 · sức khoẻ lumen → CẢNH BÁO (index chưa có nội dung mới nhất — chưa có lần dựng index nào của workflow)
  Xử lý: lumen index C:\Users\admin\AppData\Local\Temp\tdq-thu-script
Bậc 6 · hook plugin ngoài xung đột → ĐẠT (không plugin nào chèn thứ tự tìm kiếm khác)
Bậc 7 · cấu hình gốc import theo ngôn ngữ → ĐẠT (2 ngôn ngữ đều có file mốc ở gốc dự án)
Bậc 8 · đồ thị graphify → ĐẠT (đồ thị mới hơn mọi file mã nguồn)

Smoke test bốn tầng:
  grep      ĐẠT  · tìm ra định nghĩa trong antigravity-portable.html
  LSP       ĐẠT  · trả lời được
  graphify  ĐẠT  · trả lời được
  lumen     TRƯỢT · không tìm thấy binary lumen

Tổng: CHƯA ĐẠT · 7/8 bậc ĐẠT · smoke 3/4 tầng trả lời được · 1 cảnh báo không chặn · 1 tầng trượt: lumen
exit=4
=================== $ khong_lumen.py tdq_finish
[2026-10-07T20:02:29] start · project=C:\Users\admin\AppData\Local\Temp\tdq-thu-script · 5 file(s) changed
[2026-10-07T20:02:29] khoa-token → skip (no rule file changed)
[2026-10-07T20:02:29] lint → ok (1 file)
[2026-10-07T20:02:29] worklog → skip (no --log)
[2026-10-07T20:02:29] timing → skip (books close only on idle)
[2026-10-07T20:02:29] phase → skip (no --phase)
[2026-10-07T20:02:29] graphify → skip (no code file changed)
[2026-10-07T20:02:29] reindex → skip (lumen not installed)
[2026-10-07T20:02:29] done · 0 step(s) failed
✓ tdq_finish: khoa-token=skip · lint=ok · worklog=skip · timing=skip · phase=skip · graphify=skip · reindex=skip
exit=0
=================== $ khong_lumen.py setup_status
[2026-10-07T20:02:31+07:00] bash_gate.py · running a command: median 53.4ms
[2026-10-07T20:02:31+07:00] stop_gate.py · ending a turn: median 52.4ms
[2026-10-07T20:02:31] kiem · project=C:\Users\admin\AppData\Local\Temp\tdq-thu-script
[2026-10-07T20:02:32] bậc 1 binary agent-lsp → ĐẠT
[2026-10-07T20:02:32] bậc 2 MCP `lsp` → ĐẠT
[2026-10-07T20:02:32] bậc 3 language server theo project → ĐẠT
[2026-10-07T20:02:32] bậc 4 quyền tool `mcp__lsp__*` → ĐẠT
[2026-10-07T20:02:32] bậc 5 sức khoẻ lumen → THIẾU
[2026-10-07T20:02:32] bậc 6 hook plugin ngoài xung đột → ĐẠT
[2026-10-07T20:02:32] bậc 7 cấu hình gốc import theo ngôn ngữ → ĐẠT
[2026-10-07T20:02:32] bậc 8 đồ thị graphify → ĐẠT
[2026-10-07T20:02:32+07:00] setup_status: workflow: 17 skill · 81 doc row · 8 rung
[2026-10-07T20:02:32+07:00] setup_status: graphify --version: rc=0 in 0.1s
[2026-10-07T20:02:32+07:00] setup_status: lumen: not installed
[2026-10-07T20:02:32+07:00] setup_status: agent-lsp --version: rc=0 in 0.0s
[2026-10-07T20:02:32+07:00] setup_status: ollama --version: rc=0 in 0.0s
[2026-10-07T20:02:36+07:00] setup_status: claude mcp list: rc=0 in 4.4s
[2026-10-07T20:02:37+07:00] setup_status: received: 5 MCP server · 4/4 LSP answered
[2026-10-07T20:02:37+07:00] setup_status: lumen: model=qwen3-embedding:0.6b endpoints=1
[2026-10-07T20:02:37+07:00] setup_status_render: rendered 4 block(s)
[2026-10-07T20:02:37+07:00] setup_status: wrote C:\Users\admin\AppData\Local\Temp\tdq-thu-script\setup_status.html in 8.3s
C:\Users\admin\AppData\Local\Temp\tdq-thu-script\setup_status.html
exit=0
```

## Đọc kết quả
- `tdq_lsp.py check`: không traceback; **exit 4** (EXIT_SMOKE), dòng tổng **CHƯA ĐẠT vĩnh viễn** vì smoke luôn trượt tầng lumen. Bậc 5 chỉ CẢNH BÁO nhưng gợi ý sai: `lumen index <dự án>` — lệnh của binary không còn (bậc 5 kiểm index trước, chưa từng hỏi binary có tồn tại không).
- `tdq_finish.py`: không traceback, exit 0, `reindex → skip (lumen not installed)` — rơi êm.
- `setup_status.py`: không traceback, exit 0, ghi `lumen: not installed`; vẫn in model/endpoint lumen từ cấu hình còn sót.
- `tdq_setup.py`: KHÔNG chạy `main` vì nó cài/vá file plugin khác và ghim hướng dẫn vào file của user (ngoài giới hạn giả lập). Phần kiểm của nó là chính `kiem_mot_lenh` ở trên; phần dựng nền `khoi_tao_nen` đọc mã: thiếu binary → log `nền: không thấy lumen — bỏ index` (`scripts/tdq_setup.py:678-680`).

Ngoại lệ Python do lumen vắng: **0**.
