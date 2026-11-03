# Knowledge — 2026-08-03-skill-vao-goi-external

## Năng lực dùng được
| Skill | Nguồn | Phán quyết | Lý do |
|---|---|---|---|
| tdq-conventions / tdq-spec / tdq-plan / tdq-build | plugin tdq-workflow | DÙNG | Chính là các file sẽ sửa + luồng đang theo |
| graphify | user | DÙNG | Cuối turn có thay đổi code phải extract |
| tavily-search (MCP tavily-primary) | plugin tavily | ĐÃ DÙNG | Research phase analyze (4 truy vấn) |
| skill-creator, plugin-dev:* | plugin | KHÔNG | Không tạo skill/plugin mới, chỉ sửa nội dung sẵn có |
| Còn lại (frontend-design, playground, mcp-server-dev, hookify, remember, claude-md-improver, tavily-*, tdq-intake/status) | plugin | KHÔNG | Ngoài phạm vi request |

## Quyết định đã chốt (interview 2 vòng — xem questions/<slug>.md)
1. **Nhánh 2 (skill hướng dẫn per-task)**: chép **nguyên văn SKILL.md + toàn bộ references** của skill trong khối `Dùng:` vào gói task/plan. Máy-chép (script), không chắt lọc. User chấp nhận rủi ro context phình với model thấp (đã cảnh báo bằng số liệu ~3k token).
2. **Nhánh 3 (skill MCP-tool)**: plan đánh nhãn trong khối `Dùng:` — cú pháp `Dùng: <skill> (mcp)`. `split-plan` đọc nhãn bằng máy → task đó KHÔNG vào gói external, Claude tự làm. tdq-plan bắt buộc ghi nhãn khi skill cần MCP tool.
3. **Nhánh 1 (quy ước xuyên task)**: orchestrator sinh `AGENTS.md` ≤60 dòng ở ROOT worktree lúc chuẩn bị (codex auto-load qua `--cd`; agy auto-parse ở workspace root); **xóa trước diff-check/merge**. KHÔNG dùng `.agents/skills/`.
4. **Enforcement**: `run-plan` in **CẢNH BÁO + ghi log** (không chặn cứng) khi gói thiếu mục skill so với khối `Dùng:` của plan; kèm unit test.

## Ràng buộc
- Hoạt động đúng kể cả model cấp thấp: AGENTS.md ngắn-mệnh-lệnh (≤60 dòng), luật phân nhánh máy-kiểm (nhãn `(mcp)`, warning script), lưới cuối = verify 3 tầng + trường `Kiểm` của QC — không dựa vào engine "hiểu ý".
- AGENTS.md và mọi file skill chép vào worktree không được lọt vào diff merge về repo.
- Portable (03-plan/04-build) phải sync cùng thay đổi skill; test `test_portable_sync` sẽ bắt.
- Repo test: `python3 -m unittest` chạy từ `tests/`; doc_lint R2 (lệnh trong code block).

## Phương án đã loại + lý do
- Mục chuẩn "External notes" trong SKILL.md / orchestrator chắt lọc ad-hoc → user chọn chép nguyên văn (không sót thông tin).
- Danh sách cứng skill MCP trong script → user chọn nhãn trong plan (không phải bảo trì list; kết hợp cũng bị loại).
- `.agents/skills/` cho agy → thêm bề mặt bảo trì, agy đã đọc AGENTS.md root.
- Chặn cứng khi thiếu skill trong gói → user chọn warning (không chặn flow).

## Nguồn
- `docs/tdq/research/2026-08-03-skill-vao-goi-external.md` (4 truy vấn Tavily: cơ chế nạp codex/agy, AGENTS.md best practices, instruction-following model yếu).
- Evidence code: `scripts/external_task.py:266` (prompt = nguyên văn file gói, chưa có skill injection), `skills/tdq-build/SKILL.md:39` (luật NẠP skill chỉ ở nhánh main), khuôn gói `references/external-task.md` (0 nhắc skill/Dùng).
