# Brief — phân tích bỏ Lumen khỏi TDQ workflow
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## Nguyên văn

> Okay mở request phân tích nếu như tôi bỏ lumen thì claude code và codex dùng tdq workflow có còn hoạt động ổn được không?

Đọc lần đầu:
- Mục tiêu: trả lời có/không kèm bằng chứng — gỡ Lumen thì TDQ trên Claude Code và trên Codex còn chạy ổn không; chỗ nào gãy, chỗ nào chỉ ồn, cần sửa gì.
- Phạm vi đoán: hook (search_gate, search_observe, session_start), script (tdq_lsp, tdq_setup, tdq_finish, tdq_codex_mcp, search_rules, setup_status), luật chữ (skill, CLAUDE.md, tdq_state PHASE_TABLE), test.
- Chưa rõ: "bỏ" là tắt ollama, gỡ plugin + binary, hay gỡ luôn Lumen khỏi mã/luật TDQ; đầu ra chỉ báo cáo hay kèm đề xuất sửa; có đo thật trên Codex không.

## Hiểu & kiến thức

### Năng lực dùng được

| Năng lực | Nguồn | Phán | Lý do |
|---|---|---|---|
| skill trên đĩa (17) | project/plugin | BỎ | lọc "lumen search tim kiem" ra 0 skill khớp |
| tdq-setup (tham chiếu lumen.md, uu-tien-tim-kiem.md) | project | DÙNG | luật 4 tầng và cấu hình lumen nằm đây |
| lumen:doctor | plugin lumen | DÙNG | đo sức khoẻ Lumen hiện tại |
| mcp__lsp__*, graphify | MCP/CLI | DÙNG | hai tầng khái niệm còn lại khi bỏ Lumen |
| code-review, simplify, các skill tài liệu | built-in | BỎ | không liên quan phân tích |

### Phát hiện sơ bộ (đọc mã 2026-10-07)

1. **Lumen đang chết sẵn trên máy này**: `tdq_lsp.py check` → bậc 5 CẢNH BÁO (ollama chưa chạy), smoke lumen TRƯỢT `all embedding servers are unhealthy`; các bậc còn lại ĐẠT. Workflow trong phiên này vẫn chạy → bằng chứng thực địa đầu tiên.
2. **Search gate** (`hooks/scripts/search_gate.py`, `scripts/search_rules.py`): tầng khái niệm = lumen | LSP | graphify, MỘT tầng là đủ mở khoá grep. Không tầng nào sống theo dấu mốc sẵn sàng → gate tự đứng xuống; không có dấu mốc → đứng xuống sau `BREAKER_CHAN` lần chặn.
3. **Codex**: `scripts/tdq_codex_mcp.py` khai báo cả lumen lẫn lsp; thiếu lumen thì "báo và bỏ qua". `.codex/hooks.json` matcher `.*lumen.*|.*lsp.*` — cần kiểm graphify qua Bash có được ghi sổ trên Codex không.
4. **tdq_finish reindex**: không có binary → `skip`; có binary mà chết → ghi nợ mỗi turn (ồn).
5. **Luật chữ bắt buộc Lumen**: CLAUDE.md toàn cục, `analyze-full.md` ("LSP and lumen together", grep thiếu LSP+lumen là lỗi QC), `tdq_state.py` PHASE_TABLE dòng 1194/1209, `uu-tien-tim-kiem.md`, `quick-lane.md`. Gỡ Lumen mà không sửa → agent bị chấm lỗi QC vì không gọi được thứ đã gỡ.
6. ~22 file test nhắc lumen — cần biết test nào gãy khi binary vắng.

### Phạm vi đã chốt
- Mặt CHỌN: chức năng · tương thích Claude Code/Codex · chất lượng tìm kiếm (có đo) · bảo trì (test, luật chữ, tài liệu)
- Mặt LOẠI: hiệu năng máy (RAM/CPU của ollama — ollama được giữ) · bảo mật · sửa mã thật (để request sau)
- Bối cảnh: 1 máy Windows cá nhân · 2 host (Claude Code, Codex qua 9router) · 1 người dùng/bảo trì · repo đo: TDQ-Workflow + 1 repo mã thật
- Mức đầu tư suy ra: vừa — công cụ nội bộ một người giữ, nhưng kết luận quyết định gỡ một tầng của luật bắt buộc nên phải có số đo, không suy đoán

### Quyết định đã chốt
- Phương pháp đo chất lượng: 2 nhánh agent cùng bộ câu hỏi — nhánh CÓ lumen và nhánh KHÔNG lumen (chỉ grep/LSP/graphify); chấm trúng/trượt theo đáp án, đếm lượt tool và token. Mỗi repo × mỗi nhánh = 1 agent → 4 agent.
- Đã loại: so lumen top-k thô với grep thô — không phản ánh cách agent thật làm việc; một agent cho mỗi câu (48 agent) — tốn ~10× mà không thêm thông tin.
- Thử 2 host bằng ghi đè theo lần chạy, binary vắng giả lập bằng `USERPROFILE` tạm cho các script TDQ.

### Lộ trình
| Bước/phase | Chạy? | Vì sao |
|---|---|---|
| Research web | BỎ | câu hỏi nội bộ; hành vi Codex khi MCP hỏng đo trực tiếp rẻ hơn tra |
| Interview | CÓ | đã chạy 2 vòng |
| spec → plan | CÓ | khung bất biến |
| Implement bằng subagent | CÓ | 4 agent đo chất lượng chạy song song |
| QC độc lập (agent) | BỎ | mức QC `full` không đòi; đầu ra là báo cáo, không có mã |
| Report + hỏi commit | CÓ | khung bất biến |

## Hỏi đáp

- **User hỏi trước vòng 1:** thiếu lumen thì chất lượng có giảm không?
  **Trả lời (từ số đo có sẵn):** cơ chế workflow không giảm (gate nhận LSP/graphify). Chất lượng tìm chỉ có thể giảm ở loại "khái niệm mơ hồ, không có tên" — LSP xếp đích hạng 13/62 (report 2026-09-03-0017). NHƯNG repo chưa có số đo trực tiếp lumen đúng hơn grep/LSP bao nhiêu; dòng lumen trong bảng uu-tien-tim-kiem.md dựa trên điểm yếu của LSP, không dựa trên lumen được đo. Dùng thật ít: lumen 22,5k ký tự output so với Bash 2,29M (do-noi-bo 2026-10-03). Hook SessionStart/PreToolUse của plugin lumen tốn ~13,5k token qua 299 lần chèn.
- **Vòng 1** (user: "1a giữ ollama 2abcd 3a đã chạy đc với api 9router 4a 5a 6a"):
  1. Bỏ = gỡ plugin lumen + binary, **GIỮ ollama**; phân tích mã/luật TDQ phải sửa gì.
  2. Mặt chọn: chức năng, tương thích 2 host, chất lượng tìm (đo), bảo trì.
  3. Đo thật trên Codex — Codex chạy được qua provider 9router (`~/.codex/config.toml`, codex-cli 0.155.1).
  4. Đầu ra: báo cáo + danh sách đề xuất sửa; sửa thật để request sau.
  5. QC `full` (đã ghi `muc_qc=full`).
  6. Loại `docs`; user tự commit/dọn thay đổi đang dở rồi mới mở nhánh `docs/phan-tich-bo-lumen`.
- Phát hiện thêm sau vòng 1: `~/.codex/config.toml` khai `[mcp_servers.lumen]` trỏ thẳng vào binary trong cache plugin Claude Code (`.../plugins/cache/.../lumen/0.0.42/bin/...exe`) → gỡ plugin bên Claude Code làm Codex trỏ vào file không còn. Repo mẫu có sẵn: `C:/Users/admin/Documents/claudecodeui`, `C:/Users/admin/Documents/excalidraw`.
- **Vòng 2** (user: "7a 8a 9a"): 7A giả lập gỡ rồi trả lại như cũ · 8A đo trên `claudecodeui` (kèm TDQ-Workflow) · 9A agent soạn ~12 câu/repo + đáp án, user xem trong plan.
- Cách giả lập ít xâm lấn hơn 7A mà vẫn đúng ý: `claude -p --settings '<json tắt plugin lumen>'` và `codex exec -c mcp_servers.lumen...=...` — ghi đè theo từng lần chạy, KHÔNG sửa file cấu hình của user; chỉ khi ghi đè không ăn mới rơi về 7A (sửa file có bản sao rồi khôi phục).
- **Mốc test trước khi làm gì** (`tdq_test.py tron-bo`, 7 phút 5 giây): 3 module đỏ SẴN — `test_codex_edit_gate.py`, `test_codex_hooks_json.py` (do `.codex/hooks.json` chưa commit đã thêm khối search gate mà test còn đòi đúng 2 matcher Bash + apply_patch), `test_finish_reindex.py` (test không mock `_ollama_dang_chay` → đỏ khi ollama tắt: test phụ thuộc trạng thái máy, chính là một điểm phụ thuộc lumen/ollama).
