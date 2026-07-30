# KNOWLEDGE — Tối ưu plugin user-level + lazy-load

Ngày: 2026-07-30 · Trạng thái: analyze XONG (interview vòng 1 đóng) → chờ spec

## Năng lực dùng được

Phân vân → DÙNG. Không xoá bảng này kể cả khi mọi dòng là KHÔNG.

| Skill | Nguồn | Phán quyết | Dùng ở đâu / Lý do loại |
|---|---|---|---|
| tdq-intake, tdq-spec, tdq-plan, tdq-build, tdq-status, tdq-conventions | plugin:tdq-workflow | NỀN | skill khung đang chạy |
| update-config | built-in | DÙNG | bước sửa `~/.claude/settings.json` (enabledPlugins) — skill chuyên trị settings, giảm rủi ro sai schema |
| claude-md-improver (claude-md-management) | plugin | DÙNG | validate chất lượng mục mới trong `~/.claude/CLAUDE.md` sau khi viết (phân vân → DÙNG) |
| hook-development (plugin-dev) | plugin | DÙNG | viết đúng hook SessionEnd/SessionStart user-level cho cơ chế tự-tắt tier 2 |
| tavily-search (MCP tavily-primary) | MCP | NỀN | lớp research của workflow, đã dùng ở analyze |
| graphify | user | KHÔNG | khác lĩnh vực (task sửa config, không hỏi codebase; hook post-commit tự lo) |
| ~215 skill còn lại (data-engineering, huggingface, hyperframes, datarobot, figma, qt, cloudflare, canva, adobe, mongodb, postman, base44, unreal, desktop-commander, firecrawl, chrome-devtools, lumen, sonarqube, playwright, notion, hookify, remember, …) | plugin/built-in | KHÔNG | khác lĩnh vực — chúng là ĐỐI TƯỢNG bị cấu hình, không phải công cụ làm task này |

(Bảng nén theo luật >20 skill: các dòng KHÔNG cùng lý do gộp 1 dòng.)

## Sự thật đã chốt (từ research + đo máy)

1. Lazy-load thật không tồn tại trong harness: catalog skill nhét vào mọi message
   (~50 token/skill); cách duy nhất giảm = tắt plugin. Bật lại nhanh:
   `claude plugin enable <tên>@claude-plugins-official` + user gõ `/reload-plugins`.
2. Chỉ tắt được cả plugin, không tắt riêng agent/skill con → feature-dev:code-reviewer
   theo số phận plugin feature-dev (nhóm 5: giữ).
3. Mọi plugin ở máy đều scope user → sửa `~/.claude/settings.json` là đủ, không đụng
   bug #27247.
4. Phán quyết user đã chốt: tắt hẳn firecrawl, chrome-devtools-mcp, lumen, greptile,
   sonarqube; giữ tavily, playwright, graphify, review built-in; nhóm còn lại giữ
   nhưng giảm nhẹ context.

## Quyết định đã chốt (interview vòng 1 — xem ../questions/ cùng slug)

1. **Tắt hẳn 6 plugin**: firecrawl, chrome-devtools-mcp, lumen, greptile, sonarqube
   (thua ranking) + learning-output-style (xung đột luật 1-turn).
2. **Tier 2 — tắt mặc định 16 plugin domain** (~145/225 skill, tiết kiệm ~5–7k
   token/message): data-engineering, huggingface-skills, hyperframes,
   datarobot-agent-skills, figma, qt-development-skills, cloudflare, canva,
   adobe-for-creativity, mongodb, postman, desktop-commander, base44,
   unreal-engine-skills-for-claude-code, notion, redis-development.
3. **Tier 1 — luôn bật**: tdq-workflow, tavily, playwright, feature-dev, code-review,
   code-simplifier, plugin-dev, skill-creator, claude-md-management, frontend-design,
   playground, remember, hookify, agent-sdk-dev, mcp-server-dev, context7, LSP.
4. **Cơ chế bật lại**: việc khớp plugin tier 2 → Claude ĐỀ XUẤT + HỎI user (trong
   TDQ: tại vòng interview/B0); user đồng ý → Claude chạy
   `claude plugin enable <tên>@claude-plugins-official --scope user` + in 1 dòng nhắc
   gõ `/reload-plugins`. KHÔNG tự bật khi chưa hỏi.
5. **Tự tắt lại**: hook SessionEnd user-level chạy script reset mọi plugin tier 2 về
   `false` (idempotent); bù trường hợp crash bằng reset ở SessionStart matcher
   `startup`. Danh sách tier nằm trong file cấu hình riêng để script + CLAUDE.md
   cùng đọc một nguồn.
6. **CLAUDE.md**: thêm mục "Năng lực & plugin (lazy-load)" (bảng định tuyến việc→plugin,
   enum đóng cho model thấp) VÀ viết lại §10 TDQ (gộp T7.2: tên skill mới
   tdq-intake/spec/plan/build, bỏ tham chiếu tdq-start/tdq-analyze cũ).
7. Phương án đã loại: "giữ bật + luật chỉ-dùng-khi-khớp" (không giảm context thật —
   catalog vẫn bị nhét, issue #42650); tắt riêng agent trong plugin (harness không hỗ trợ).

## Kiểm cổng

- Phạm vi cuối: rõ — sửa `~/.claude/settings.json` (enabledPlugins), thêm script
  `plugin_tiers.py` (nguồn trong repo này, copy sang `~/.claude/scripts/`), đăng ký
  2 hook user-level, viết 2 mục CLAUDE.md. Không cần model/download/cài thêm.
- QC/validate: test unit cho script (danh sách tier, idempotent, JSON hỏng), chạy
  thật lệnh enable/disable + kiểm `claude plugin list --disabled`, đo lại số skill
  trên đĩa sau khi áp, doc_lint cho mục CLAUDE.md mới nếu áp được.
