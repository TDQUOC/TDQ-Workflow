# REPORT — Bỏ Lumen thì TDQ trên Claude Code và Codex còn chạy ổn không

Ngày: 2026-10-07 · Spec: ../spec/2026-10-07-1843-phan-tich-bo-lumen.md · Plan: ../plan/2026-10-07-1843-phan-tich-bo-lumen.md · Lane: full · Mode: main
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## Trả lời ngắn

| Host | Còn chạy ổn? | Vì sao |
|---|---|---|
| **Claude Code** | **CÓ** — chạy hết việc, ra đúng kết quả; tốn thêm ~4 lượt thừa mỗi lần tìm đầu tiên | gate mở khoá qua graphify/LSP; nhưng lời nhắc của gate và 3 câu luật vẫn đòi lumen ([claude-code.md](../bench/2026-10-07-1843-hai-host-khong-lumen/claude-code.md)) |
| **Codex** | **CÓ** — khởi động bình thường dù cấu hình còn trỏ vào binary lumen đã mất; ra đúng kết quả bằng LSP | server lumen lặng lẽ vắng, không lỗi ([codex.md](../bench/2026-10-07-1843-hai-host-khong-lumen/codex.md)) |
| **Chất lượng tìm** | **KHÔNG giảm đáng kể** theo luật định trước (2 repo) | trượt chênh 1 câu/12 (ngưỡng 2), token 0,88× và 1,06× (ngưỡng 1,5×) ([tong-hop.md](../bench/2026-10-07-1843-chat-luong-lumen/tong-hop.md)) |

Không điểm nào làm workflow dừng hay traceback. Thứ "gãy" là **luật chữ**: 4 chỗ chấm agent theo một tầng không còn tồn tại.

## Số đo chất lượng (12 câu khái niệm/repo, 4 agent)

| Repo | CÓ lumen (đủ/một phần/trượt · token) | KHÔNG lumen | Kết luận |
|---|---|---|---|
| TDQ-Workflow | 12/0/0 · 48.220 | 11/1/0 · 42.571 | không giảm đáng kể |
| claudecodeui | 11/1/0 · 53.246 | 10/2/0 · 56.643 | không giảm đáng kể |

Đọc kèm giới hạn ([tong-hop.md](../bench/2026-10-07-1843-chat-luong-lumen/tong-hop.md) §Giới hạn): bộ câu do agent soạn bằng grep nên mọi đích đều grep tìm được — câu mơ hồ hơn ngoài đời có thể cho lumen lợi thế lớn hơn; 12 câu/repo, 1 lần chạy. Phép đo này **bác bỏ** "thiếu lumen là tìm kém hẳn", **chưa chứng minh** "lumen vô dụng".

## Bản đồ phụ thuộc (đủ 51 file — [research](../research/2026-10-07-1843-phan-tich-bo-lumen.md))

- **GÃY (chấm oan) — 4**: `scripts/tdq_state.py:1194,1209`, `skills/tdq-intake/references/analyze-full.md:33-39`, `skills/tdq-intake/references/quick-lane.md:42`, `skills/tdq-build/SKILL.md:66`.
- **ỒN — 9**: lời nhắc gate (`search_rules.py:79`), `session_start` dựng lại nền mỗi 6 giờ, `tdq_lsp.py check` CHƯA ĐẠT vĩnh viễn (exit 4), bậc 5 gợi ý sai lệnh, `wake`, `kiem_cau_hinh_lumen`, khối ghim instruction, `uu-tien-tim-kiem*.md`, `khai_mcp_codex` để mục chết.
- **ỔN**: gate (cơ chế), `tdq_finish` reindex (skip êm), `setup_status`, bộ dò binary, toàn bộ test (447 xanh cả khi vắng binary).

## Đề xuất sửa (cho request sau, nếu quyết gỡ)

| # | Sửa | File | Bằng chứng |
|---|---|---|---|
| 1 | Đổi 3 câu luật "LSP + lumen together" thành "LSP + một tầng khái niệm đang sống (lumen nếu có, graphify nếu không)", thêm lối thoát khi lumen vắng như đã có cho LSP | `analyze-full.md:33-39`, `quick-lane.md:42`, `tdq-build/SKILL.md:66`, `tdq_state.py:1194,1209` (+ sinh lại `phases.md`) | [research §2–3](../research/2026-10-07-1843-phan-tich-bo-lumen.md) |
| 2 | `LOI_RA` chỉ gợi ý tầng đang sống theo dấu mốc sẵn sàng (đừng mở đầu bằng lumen khi `lumen.san_sang=false`) | `scripts/search_rules.py:79`, `hooks/scripts/search_gate.py` | [claude-code.md](../bench/2026-10-07-1843-hai-host-khong-lumen/claude-code.md): 1 `ToolSearch("lumen")` thừa |
| 3 | Lời gọi LSP trả "LSP client not initialized" → lời nhắc nói rõ `start_lsp` trước, hoặc gate tự coi `start_lsp` thành công là đủ | `scripts/search_rules.py` (`LSP_HOI`), `LOI_RA` | [claude-code.md](../bench/2026-10-07-1843-hai-host-khong-lumen/claude-code.md): agent kết luận "LSP chết" |
| 4 | Thêm cách tắt hẳn tầng lumen (vd biến/cấu hình "lumen: tắt"): `session_start` không dựng lại mỗi 6 giờ, smoke không tính tầng lumen vào dòng tổng, bậc 5 báo "đã tắt" | `hooks/scripts/session_start.py:119-121`, `scripts/tdq_lsp.py:452,788`, `scripts/tdq_setup.py:273` | [script-tdq.md](../bench/2026-10-07-1843-hai-host-khong-lumen/script-tdq.md): exit 4 vĩnh viễn |
| 5 | Bậc 5 kiểm binary TRƯỚC index để không gợi ý `lumen index` cho binary đã mất | `scripts/tdq_lsp.py:452-483` | [script-tdq.md](../bench/2026-10-07-1843-hai-host-khong-lumen/script-tdq.md) |
| 6 | `khai_mcp_codex` gỡ/cảnh báo mục `[mcp_servers.lumen]` trỏ vào file không tồn tại | `scripts/tdq_codex_mcp.py:115-140` | [codex.md](../bench/2026-10-07-1843-hai-host-khong-lumen/codex.md) |
| 7 | Sửa hàng "khái niệm mơ hồ → lumen" trong luật 4 tầng và CLAUDE.md toàn cục (ghi rõ dự phòng); sửa kèm 3 test ghim chữ luật | `skills/tdq-setup/references/uu-tien-tim-kiem.md`, `C:/Users/admin/.claude/CLAUDE.md`, `tests/test_claude_md_core.py`, `tests/test_luat_4_tang.py`, `tests/test_tdq_setup_skill.py` | [research §3–4](../research/2026-10-07-1843-phan-tich-bo-lumen.md) |

## Phát hiện ngoài phạm vi (không do lumen, nên xử lý riêng)

1. **Hook TDQ không chạy trong Codex trên máy này**: 0 dòng sổ tìm kiếm từ phiên Codex; search gate Codex chưa từng thật sự chặn ([codex.md](../bench/2026-10-07-1843-hai-host-khong-lumen/codex.md)).
2. **Codex trên Windows từ chối mọi lệnh shell** (`CreateProcess … rejected: blocked by policy`) ở cả `read-only` lẫn `workspace-write` ([codex.md](../bench/2026-10-07-1843-hai-host-khong-lumen/codex.md)).
3. `tests/test_finish_reindex.py` đỏ/xanh theo ollama tắt/bật — test thiếu mock `_ollama_dang_chay` ([research §4](../research/2026-10-07-1843-phan-tich-bo-lumen.md)).
4. `scripts/setup_status.py:331` ném `TypeError` khi dự án chưa có `state.json` ([script-tdq.md](../bench/2026-10-07-1843-hai-host-khong-lumen/script-tdq.md)).
5. `test_codex_edit_gate.py`, `test_codex_hooks_json.py` đỏ vì `.codex/hooks.json` chưa commit đã thêm khối search gate mà test còn đòi đúng 2 matcher.
6. `plugin-routing.md:42` xếp lumen vào "Log / trace observability" — sai nghĩa.
7. lumen 0.0.42: `semantic_search` với `path` là thư mục con báo `k value in knn query too large`.

## Máy sau khi đo
`~/.codex/config.toml`, `~/.claude/settings.json` cùng `sha256` trước/sau; plugin lumen vẫn bật; hai file đáp án đã trả về chỗ cũ; bản sao thử nằm ở `%TEMP%` (`tdq-thu-host`, `tdq-thu-script`).
