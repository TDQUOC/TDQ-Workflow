# REPORT — Hướng D: cắt token mô tả skill (`2026-08-19-0046-huong-d-skill-overrides` · lane full · mode main · 5/5 task tick đủ)

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

**Phát hiện quan trọng nhất: con số 87,7% của đề án cũ là SAI.** Đề án 2026-08-17 giả định
`skillOverrides` áp cho mọi skill. Tài liệu chính thức nói ngược lại — *"Plugin skills are
not affected by `skillOverrides`"*. Đo lại: chỉ 33/284 skill (2.981/29.788 token = 10%)
nằm trong tầm với của cơ chế này, tiết kiệm tối đa **8,8%** chứ không phải 87,7%.

**Đã làm:**
- Backup `~/.claude/settings.json` → `docs/tdq/audit/settings-backup-2026-08-19.json` (khớp md5).
- Sinh lại `skill-overrides-de-xuat.json`: 261 khoá → **33 khoá** (bỏ 228 khoá plugin no-op).
- Ghi `~/.claude/settings.json`: D1 — 33 khoá `name-only`, giữ nguyên `unity-skills:
  user-invocable-only` user tự đặt; D2 — thêm `skillListingMaxDescChars: 300` (đòn bẩy MỚI,
  đề án cũ chưa biết, áp được cho CẢ plugin skill nên chạm tới đúng 90% token kia).
- Thêm mục "Đính chính 2026-08-19" vào `de-an-toi-uu-context.md`, giữ nguyên mục cũ để
  thấy sai ở đâu.

**Mức tiết kiệm dự kiến:** D1 −2.632 token (8,8%) + D2 −9.814 token (32,9%) ≈ **−12.446
token (41,8%)** trên 29.788 token mô tả skill.

**⚠️ CHƯA XÁC NHẬN — bạn cần làm 1 việc:** cấu hình skill chỉ được đọc lúc MỞ PHIÊN. Số
41,8% ở trên là đo trước, không phải đo sau. Phải **mở một phiên Claude Code mới** rồi mới
biết có ăn thật không. Cơ chế này có tiền sử hỏng âm thầm (issue #50631: `skillOverrides`
là stub luôn trả `"on"` ở v2.1.114, tới v2.1.129 mới có behavior thật — máy đang chạy
v2.1.234 nên về lý là đã qua, nhưng đây đúng kiểu lỗi không phát tín hiệu).

**Cách đảo ngược (10 giây):** `cp docs/tdq/audit/settings-backup-2026-08-19.json
~/.claude/settings.json` rồi mở phiên mới. Chỉ muốn bỏ phần cắt mô tả thì xoá đúng dòng
`skillListingMaxDescChars`.

**Cái giá đã cân nhắc:** trần 300 ký tự cắt đuôi mô tả của 47 skill. 6 skill `tdq-*` dài
138-155 ký tự nên không bị chạm; đường search thật đi qua MCP tool `mcp__tavily-primary__*`
chứ không qua skill listing nên CLAUDE.md §3 không ảnh hưởng; 45/47 skill bị cắt thuộc
lĩnh vực không dùng trong dự án này.

**Kiểm:** Q1-Q6 PASS (bảng ở plan) · `doc_lint` exit 0 · settings parse lại được, 17 khoá
cấp cao, không mất khoá nào của bản backup.
**Đầu ra:** `settings-backup-2026-08-19.json` · `skill-overrides-de-xuat.json` (33 khoá) ·
`~/.claude/settings.json` · mục đính chính trong `de-an-toi-uu-context.md` · report này.
**Giới hạn:** D3 (tắt hẳn plugin qua `/plugin`) ngoài phạm vi — đây mới là đường duy nhất
cắt sâu hơn vào 90% token plugin, top tốn: `data-engineering` 3.698, `huggingface-skills`
3.224, `hyperframes` 2.423. Hướng C, B, A(hybrid), E: mỗi hướng một request riêng.
**Git:** chưa commit.
