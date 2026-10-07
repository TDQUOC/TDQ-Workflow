# REPORT — Gỡ Lumen và tối ưu luật tìm kiếm 3 tầng (`2026-10-07-2041-go-lumen-toi-uu-tim-kiem` · lane full · mode main · 22 task + 1 fix tick đủ)

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

**Đã làm:** P1 gỡ lumen/ollama khỏi `tdq_lsp`·`tdq_setup`·`tdq_finish`·`setup_status`·`session_start`, thang 7 bậc · P2 cổng `TDQ:SEARCH` nhắc theo tầng sống, ghi sổ LSP ở PreToolUse · P3 tìm ra vì sao hook không chạy trong Codex, chặn `tdq_setup` ghi đè `.codex/hooks.json` của chính repo · P4 luật chữ 3 tầng (4 câu chấm oan, bảng loại câu hỏi kèm số đo mới) · P5 phát hành 0.58.0 · P6 đo trước/sau · P7 dọn máy
**Kết quả:** `tdq_lsp.py check` CHƯA ĐẠT exit 4 → **ĐẠT exit 0** (7/7 bậc, smoke 3/3) · lượt thừa của cổng 4 → **1** (2 lần đo) · sổ tìm kiếm từ phiên Codex 0 → **4 dòng** (khi đủ 2 điều kiện) · trọn suite 3 module đỏ → **0/127** · máy: bớt 85 MB plugin + 418 MB index + 639 MB model
**Kiểm:** `tdq_test.py tron-bo` 127 module 0 đỏ · `doc_lint` 0 vi phạm · `token_budget.py` khoá mới · QC PASS 9/9 DoD + F1–F4, 1 vòng fix (QC1.1 `chung.md` còn "lumen or grep")
**Đầu ra:** mã + luật trên nhánh `chore/go-lumen-toi-uu-tim-kiem` · bằng chứng `docs/tdq/bench/2026-10-07-2041-sau-khi-go/` · nguyên nhân hook Codex `docs/tdq/research/2026-10-07-2041-hook-codex.md` · Backup: `~/.claude/settings.json`, `~/.codex/config.toml`, `~/.claude/CLAUDE.md` `.truoc-tdq-20261007220249.bak`
**Giới hạn:** dữ liệu lumen và model đã xoá là không hoàn tác (user chọn 2B, 2C) · hook TDQ trong Codex trên máy này **chưa** chạy theo mặc định — cần user tự cho Codex tạo tiến trình và duyệt `/hooks` · bản plugin đang cài (cache 0.57.0) chỉ nhận mã mới sau khi push và cập nhật plugin · phiên Claude Code đang chạy mất MCP lumen (đã dừng tiến trình để xoá cache)
**Lệch spec chờ duyệt:** #1 · Q5 · hook Codex ghi sổ → mặc định 0 vì sandbox Windows + hook chưa duyệt (ngoài repo) · đã áp: TDQ in hai điều kiện mỗi lần ghi hook, đo dưới hai điều kiện được 4 dòng · #2 · Q6 · spec §1 "khối search gate trong `.codex/hooks.json` gốc repo thành chính thức" → file đó là hàng rào viết tay của `codex implement`, khối kia do ghi đè nhầm · đã áp: trả file về bản commit + chặn `khai_hook_codex` ghi vào repo plugin
**Git:** chưa commit (nhánh `chore/go-lumen-toi-uu-tim-kiem`, gộp về `main`)

## Thời gian

| Phase | Wall clock | Model time | Times entered |
|---|---|---|---|
| idle | 0s | — | 1 |
| analyze | 13 min | — | 1 |
| spec | 8 min | — | 1 |
| plan | 9 min | — | 1 |
| implement | 54 min | — | 1 |
| qc | 8 min | — | 1 |
| report | 0s | — | 1 |
| **Total** | **1h 30min** | **—** | |

Cột model là `—`: không đọc được transcript của phiên.
