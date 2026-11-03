# Brief — gỡ Lumen và tối ưu lại luật tìm kiếm
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## Nguyên văn

> 1a commit và mở request gỡ lumen và xử lí lại luật tìm kiếm cho tối ưu
> (trả lời câu lane) 1a và sửa lại hook luôn

Đọc lần đầu:
- Mục tiêu: gỡ Lumen (máy + TDQ), viết lại luật tìm kiếm thành 3 tầng (LSP · grep · graphify) sao cho agent tìm đúng với ít lượt thừa nhất; sửa hook tìm kiếm (Claude Code và Codex) theo luật mới.
- Đầu vào: request `2026-10-07-1843-phan-tich-bo-lumen` (commit `f80464d`) — 7 đề xuất, bản đồ 51 file, số đo.
- "sửa lại hook luôn": gộp phần `.codex/hooks.json` đang dở (khối search gate do `tdq_setup` ghi lúc 14:42, có `.bak`) vào request này, và sửa hook theo luật mới.
- Chưa rõ: gỡ hẳn mã lumen khỏi TDQ hay giữ làm tầng tuỳ chọn; gỡ trên máy tới đâu (plugin, config, index, model ollama); "tối ưu" đo bằng gì; gate giữ chặn hay đổi.

## Hiểu & kiến thức

### Năng lực dùng được

| Năng lực | Nguồn | Phán | Lý do |
|---|---|---|---|
| tdq-setup (`uu-tien-tim-kiem.md`, `lumen.md`) | project | DÙNG | nguồn luật 4 tầng cần viết lại |
| mcp__lsp__* (find_references, blast_radius) | MCP | DÙNG | dựng dòng `Chạm:` |
| graphify | CLI | DÙNG | bản đồ vỡ lan |
| lumen:doctor / lumen:reindex | plugin lumen | KHÔNG | đối tượng bị gỡ |
| skill trên đĩa khác (17) | project/plugin | KHÔNG | lọc "search hook lumen setup" ra 0 |

### Hiện trạng đã đo (2026-10-07, request trước)
- 4 câu luật chấm oan: `tdq_state.py:1194,1209`, `analyze-full.md:33-39`, `quick-lane.md:42`, `tdq-build/SKILL.md:66`.
- Gate Claude Code: chặn 2 lần, `LOI_RA` mở đầu "Ask first: lumen…" → 1 `ToolSearch("lumen")` thừa; `find_symbol` lỗi "LSP client not initialized; call start_lsp first" không được tính → thêm 1 lần chặn; graphify mở khoá. ~4 lượt thừa.
- Hook TDQ KHÔNG chạy trong Codex (0 dòng sổ); `codex features list`: `hooks stable true`. Codex Windows từ chối mọi lệnh shell `CreateProcess … blocked by policy` — chưa rõ có cùng gốc với việc hook không chạy hay không.
- `.codex/hooks.json` (chưa commit) có khối search gate do `tdq_setup` ghi; `tests/test_codex_hooks_json.py`, `test_codex_edit_gate.py` còn đòi đúng 2 matcher Bash + apply_patch → 2 module đỏ.
- `tdq_setup.ghim_huong_dan_tool` ghi khối luật 4 tầng vào `~/.claude/CLAUDE.md` giữa 2 dấu mốc → sửa template rồi chạy lại là cập nhật được CLAUDE.md toàn cục.
- Chất lượng tìm không lumen: không giảm đáng kể (12 câu × 2 repo).

### Phạm vi đã chốt
- Mặt CHỌN: chức năng (luật 3 tầng, gate) · tương thích Claude Code/Codex (hook Codex chạy thật) · bảo trì (xoá mã/test/tài liệu lumen) · dọn máy user
- Mặt LOẠI: đo lại chất lượng 12 câu (user không chọn 5C) · đo token skill (không chọn 5B) · hiệu năng máy
- Bối cảnh: 1 máy Windows, 1 người giữ, plugin TDQ phát hành 0.57.0 qua marketplace git
- Mức đầu tư suy ra: vừa — công cụ nội bộ nhưng sửa hook chặn và gỡ dữ liệu trên máy (khó hoàn tác) nên phải đo trước/sau và có bản sao

### Quyết định đã chốt
- Xoá hẳn lumen khỏi mã TDQ (1A); thang kiểm còn 7 bậc, đánh số lại liên tục (bậc 6→5, 7→6, 8→7) để không còn lỗ hổng số.
- Ollama: TDQ thôi quản (xoá `wake`/`nha` cùng lumen) — ollama là của user, không phải phụ thuộc của TDQ nữa.
- Gate giữ chặn (3A): lời nhắc sinh từ tầng đang sống; ghi nhận lời gọi LSP ngay ở PreToolUse (lỗi "chưa khởi động" vẫn tính đã hỏi); ngưỡng: lượt thừa ≤ 1 trên đúng phiên thử của request trước (mốc 4).
- Codex (4A): điều tra vì sao hook không chạy, sửa, đo bằng sổ tìm kiếm; sửa 2 test cho khớp `.codex/hooks.json` có search gate.
- Máy (2ABC): gỡ plugin lumen, bỏ `[mcp_servers.lumen]` (bản sao), bỏ env `OLLAMA_HOST`/`LUMEN_EMBED_MODEL`, xoá `~/.local/share/lumen` (416 MB) + `~/.config/lumen/`, `ollama rm qwen3-embedding:0.6b` (639 MB). Làm CUỐI implement, sau khi test xanh.
- CLAUDE.md toàn cục: cập nhật qua `ghim_huong_dan_tool` (khối có dấu mốc), không sửa tay.
- Phát hành 0.58.0 (CHANGELOG + 2 plugin.json).

### Lộ trình
| Bước/phase | Chạy? | Vì sao |
|---|---|---|
| Research web | CÓ (1 câu, tự làm) | cách bật hook dự án của codex-cli 0.155 — chưa biết |
| Interview | CÓ | 2 vòng |
| spec → plan | CÓ | khung bất biến |
| QC độc lập (agent) | BỎ | mức `full` không đòi |
| Report + hỏi commit | CÓ | khung bất biến |

## Hỏi đáp
- **Vòng 1** (user: "1a 2abc 3a 4a 5a 6a"): 1A xoá hẳn mã lumen · 2ABC gỡ plugin + config + env, xoá index/config lumen, xoá model embedding · 3A gate giữ chặn, sửa lời nhắc + tính LSP lỗi khởi động · 4A sửa hook Codex chạy thật + 2 test · 5A tối ưu đo bằng số lượt thừa · 6A QC `full`.
