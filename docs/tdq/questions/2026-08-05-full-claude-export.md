# Câu hỏi — 2026-08-05-full-claude-export

## Vòng 1

**Q1 — Có đưa `mem0R&D` vào bundle như local repo dependency thứ 2 không?**
(Phát hiện: MCP server `mem0` trong `~/.claude.json` trỏ `http://127.0.0.1:8765`, do
LaunchAgent `com.mem0.gateway.plist` khởi động từ venv đã cài — venv đó dựng từ repo
`~/Documents/mem0R&D` (1 commit, không remote). Tool export hiện chỉ biết `TDQWorkflow`.)
- A (đề xuất): Có — clone full `.git` giống TDQWorkflow.
- B: Không — chỉ export TDQWorkflow.
→ **Trả lời: A**

**Q2 — Cách tool nhận diện "repo local dependency" để mở rộng?**
(Đã kiểm chứng: không auto-detect được từ MCP config — plist trỏ vào venv ĐÃ CÀI, không
trỏ ngược lại repo nguồn, không có back-reference nào.)
- A (đề xuất): Danh sách tường minh trong 1 file config nhỏ ở `claude-export/`.
- B: Auto-detect qua heuristic — phức tạp, rủi ro sai/sót.
→ **Trả lời: A**

**Q3 — Có mang theo `~/Library/LaunchAgents/com.mem0.gateway.plist` vào bundle để tham
khảo cách mem0 tự khởi động không?**
- A (đề xuất): Có, copy vào `config/launch-agents/` chỉ để THAM KHẢO (không tự restore).
- B: Không cần.
→ **Trả lời: A**

**Bổ sung của user (cùng vòng 1):** "và có đầy đủ instruction, setting, config, rule
,... (all of claude user level)" — yêu cầu rà soát lại `CONFIG_FILES`/`CONFIG_DIRS`
của `claude_export.py` cho đủ, không chỉ 2 repo.

## Rà soát theo yêu cầu bổ sung (không cần hỏi thêm — đọc trực tiếp `~/.claude`)

- Liệt kê toàn bộ `~/.claude/` (42 mục) so với `CONFIG_FILES`/`CONFIG_DIRS` hiện tại.
- **Gap tìm thấy:** `CONFIG_DIRS` hard-code `skills/graphify` — bỏ sót
  `skills/mem0-memory` (skill user-level thật, do installer của `mem0R&D` cài, đã xác
  nhận nội dung khớp bản gốc trong repo `mem0R&D/.claude/skills/mem0-memory`, không
  phải cache). → cần TỔNG QUÁT HOÁ: copy toàn bộ thư mục con của `skills/`, không
  hard-code từng tên, để tự nhặt mọi skill user-level tương lai.
- Kiểm `plugins/data/*`: toàn bộ đang RỖNG (0 file) trên máy hiện tại → không cần đổi,
  nhưng cấu trúc copy hiện tại (`CONFIG_DIRS`) đã đủ tổng quát nếu sau này có dữ liệu
  (đi qua cùng cơ chế walk thư mục).
- Kiểm `settings.json`: statusline đã trỏ `statusline.sh` (đã copy); `hooks` định nghĩa
  inline trong chính `settings.json` (đã copy nguyên file, secret đã redact) → không
  còn phụ thuộc file ngoài nào chưa được mang theo.
- `~/.claude.json` KHÔNG mang theo nguyên file (chỉ tách `mcpServers`) — giữ nguyên,
  vì chứa `oauthAccount`/`machineID`/`userID` (bảo mật, đã ghi rõ trong
  `INSTRUCTIONS.md` "Điều script KHÔNG làm"); không hỏi lại vì đây là ràng buộc bảo
  mật đã có sẵn, không phải điểm user vừa nêu.
- `specs/`, `plans/`, cache files (`plugin-catalog-cache.json`,
  `mcp-needs-auth-cache.json`, `.last-cleanup`...) — không phải instruction/setting/rule,
  là output/cache runtime → loại, giữ nguyên phạm vi hiện tại của tool.
