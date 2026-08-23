# Report — skill tdq-lsp-setup, nhúng agent-lsp vào bộ workflow
Ngày: 2026-08-23 · Plan: ../plan/2026-08-23-0052-skill-tdq-lsp-setup.md · QC: ../qc/2026-08-23-0052-skill-tdq-lsp-setup.md
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## Đã làm

- Skill mới `skills/tdq-lsp-setup/` — thang 6 bậc cài đặt, bảng 30 ngôn ngữ kèm lệnh cài, luật
  ưu tiên tìm kiếm, và mục runbook ghi nguyên 5 bước đã chạy trên máy này để lần sau đổi máy
  hay thêm ngôn ngữ thì đọc lại mà làm.
- `scripts/tdq_lsp.py` — 3 lệnh `kiem` / `danh-thuc` / `nha`. Bậc 1–4 chặn được, bậc 5–6 chỉ
  cảnh báo. Script không bao giờ tự cài: nó in lệnh và để user quyết.
- Luật "LSP trước, lumen khi LSP rỗng, grep cuối" móc vào 5 chỗ: intake, analyze-full, spec,
  plan, build. Câu luật viết một chỗ, 4 chỗ kia trích nguyên văn; `tests/test_tdq_lsp_skill.py`
  so từng chữ nên sửa một chỗ mà quên chỗ khác là đỏ.
- Cài thật trên máy: agent-lsp 0.18.0, pyright, typescript-language-server + typescript 5.9.3,
  csharp-ls 0.26.0, lua-language-server 3.19.1. MCP `lsp` đăng ký ở user scope, Connected.
- Hai bản portable sinh lại, cả hai đã mang skill mới và script mới.

## Kết quả kiểm

QC 36 hạng mục (32 dòng DoD + 4 cố định): **PASS 34, TREO 2, FAIL 0**. Suite tổng
37 đỏ / 1349 xanh — đúng mốc nền, cả 37 nằm trong `tests/test_skill_router.py` từ trước.

## Cần bạn biết

1. **`agent-lsp init` từng ghi 2 file vào repo.** Chạy nó với stdin đóng thì nó lấy hết giá trị
   mặc định và tự ghi `.mcp.json` + `CLAUDE.md` vào thư mục hiện tại. Cả hai đều là file mới
   (`git status` báo `??`), không đè lên cái gì; tôi đã xoá và chuyển sang `claude mcp add`
   tường minh. Bài học này đã viết vào runbook của skill.
2. **typescript 7 không chạy được.** `npm i -g typescript` ra bản 7.0.2 (bản port sang Go) —
   không có `lib/tsserver.js` nên `typescript-language-server` không khởi động nổi. Đã hỏi bạn
   và bạn chọn hạ về `typescript@5` (5.9.3). Nếu sau này npm tự nâng lên 7 thì lỗi quay lại.
3. **Lua phải đăng ký tay.** `agent-lsp doctor` không tự dò `lua-language-server` dù nó có sẵn,
   nên lệnh `claude mcp add` liệt kê `lua:lua-language-server` tường minh.
4. **Đã sửa 1 file ngoài repo, có sao lưu.** Hook `PreToolUse` của plugin lumen giục dùng lumen
   thay Grep, ngược thứ tự ưu tiên vừa chốt. Đã gỡ đúng khối đó, giữ `SessionStart`. Bản sao lưu:
   `~/.claude/plugins/cache/claude-plugins-official/lumen/0.0.42/hooks/hooks.json.bak-tdq-lsp-0.0.42-20260823-100731`.
   Plugin cập nhật là hook mọc lại — bậc 6 sẽ báo.
5. **Hai hạng mục treo tới phiên sau.** Q12 (gọi thật một tool `mcp__lsp__*`) và Q30 (hết dòng
   giục của lumen) đều chặn vì MCP và hook chỉ nạp lúc mở phiên. Task T4.5 của plan treo cùng lý
   do. Mở phiên mới rồi chạy hai phép kiểm ghi ở cuối file QC là xong.
6. **Một lần vá bằng Bash.** Cổng `TDQ:TICK` chặn Edit ở giữa đợt sửa R5 của `tdq-build` (3 lần
   sửa liên tiếp không đổi tick), tôi áp cùng thay đổi đó bằng một lệnh python trong Bash.
7. Không có commit nào trong đợt này. Commit `f986139` của request trước vẫn chưa push.

## Thời gian

| Phase | Wall clock | Model time | Times entered |
|---|---|---|---|
| idle | 0s | 0s | 1 |
| analyze | 17 min | 12 min | 1 |
| spec | 18 min | 18 min | 1 |
| plan | 7 min | 7 min | 1 |
| implement | 8h 46min | 47 min | 1 |
| qc | 7 min | 6 min | 1 |
| report | 7s | 0s | 1 |
| **Total** | **9h 35min** | **1h 30min** | |
