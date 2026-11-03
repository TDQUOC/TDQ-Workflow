# SPEC — Tối ưu bộ plugin user-level: tier hoá, lazy-load, viết lại §10 (v1.0)

<!-- doc-lint: allow R10 — spec viết trước khi có luật ranh giới module -->

Ngày: 2026-07-30 · Request: `../requests/2026-07-30-plugin-lazy-load.md` ·
Knowledge: `../knowledge/2026-07-30-plugin-lazy-load.md`

## 1. Mục tiêu & phạm vi

**Mục tiêu:** giảm nhẹ context (catalog skill ~50 token/skill/message) và loại xung đột
hành vi giữa các plugin, ở mức **user-level** (`~/.claude/`), theo phán quyết ranking
user đã chốt; instruction viết đủ chi tiết để model cấp thấp làm đúng.

**In scope:**
1. Tắt hẳn 6 plugin: `firecrawl`, `chrome-devtools-mcp`, `lumen`, `greptile`,
   `sonarqube`, `learning-output-style` (đều `@claude-plugins-official`).
2. Tier hoá phần còn lại: 16 plugin domain tắt mặc định (on-demand):
   `data-engineering`, `huggingface-skills`, `hyperframes`, `datarobot-agent-skills`,
   `figma`, `qt-development-skills`, `cloudflare`, `canva`, `adobe-for-creativity`,
   `mongodb`, `postman`, `desktop-commander`, `base44`,
   `unreal-engine-skills-for-claude-code`, `notion`, `redis-development`.
   Tier luôn-bật: mọi plugin còn lại (tdq-workflow, tavily, playwright, feature-dev,
   code-review, code-simplifier, plugin-dev, skill-creator, claude-md-management,
   frontend-design, playground, remember, hookify, agent-sdk-dev, mcp-server-dev,
   context7 và các plugin LSP) — giữ nguyên `true`, không ghi thêm gì.
3. Cơ chế on-demand: file cấu hình `~/.claude/plugin-tiers.json` (nguồn sự thật duy
   nhất) + script `~/.claude/scripts/plugin_tiers.py` (nguồn trong repo:
   `scripts/plugin_tiers.py`) + 2 hook user-level trong `~/.claude/settings.json`:
   - `SessionEnd` → `plugin_tiers.py reset` — ép `false` CẢ `always_off` LẪN
     `on_demand` (chống drift), idempotent.
   - `SessionStart` matcher `startup` → `plugin_tiers.py reset` (bù trường hợp crash).
   - Bật lại đi qua đúng MỘT lệnh duy nhất:
     `python3 ~/.claude/scripts/plugin_tiers.py enable <tên-plugin>` — chỉ nhận
     plugin thuộc `on_demand`, cũng atomic write + log như reset. Không dùng
     `claude plugin enable` trong bảng định tuyến để mọi đường ghi settings đều
     qua một chỗ.
4. Sửa `~/.claude/CLAUDE.md`:
   - Thêm mục **"Năng lực & plugin (lazy-load)"**: luật đề-xuất-và-hỏi + bảng định
     tuyến việc→plugin (enum đóng, model thấp theo được).
   - **Viết lại §10** (gộp T7.2 treo từ 0.3.0): tên skill 0.3.3
     (tdq-intake/spec/plan/build/status), bỏ tham chiếu `tdq-start`/`tdq-analyze`
     VÀ bỏ lệnh `/tdq-workflow:tdq-approve` (0.3.3 đã xoá skill đó — duyệt bằng
     chat thường theo tdq-conventions §4, ví dụ "duyệt spec"/"duyệt plan mode main").

**Out of scope:** không gỡ cài đặt (`uninstall`) plugin nào; không đổi code plugin
tdq-workflow (không tăng version); không đụng scope project của repo khác
(superpowers giữ nguyên); không tối ưu MCP server ngoài việc tắt plugin chứa nó.

## 2. Đầu ra đo đếm được

| # | Đầu ra | Đo bằng |
|---|---|---|
| 1 | `~/.claude/settings.json`: 22 key `enabledPlugins` = `false` (6 tắt hẳn + 16 on-demand) | `claude plugin list --disabled` chứa **đúng đủ 22 tên** trong danh sách §1, VÀ không plugin tier luôn-bật nào xuất hiện trong đó |
| 2 | `~/.claude/plugin-tiers.json`: `{"always_off": [6], "on_demand": [16]}` | JSON parse + đúng 6/16 phần tử |
| 3 | `scripts/plugin_tiers.py` (repo) + bản copy `~/.claude/scripts/plugin_tiers.py` | `python3 ~/.claude/scripts/plugin_tiers.py status` chạy được, exit 0 |
| 4 | 2 hook đăng ký trong `~/.claude/settings.json` (SessionEnd, SessionStart:startup) | đọc settings thấy đúng 2 entry trỏ script |
| 5 | `tests/test_plugin_tiers.py` ≥ 8 test, đi kèm suite hiện có | `python3 -m unittest discover tests` OK |
| 6 | `~/.claude/CLAUDE.md`: mục "Năng lực & plugin (lazy-load)" + §10 mới | grep hết `tdq-start` = 0 kết quả; bảng định tuyến đủ 16 dòng on-demand |
| 7 | Catalog nhẹ đi: skill trên đĩa từ ~225 → ≤ 85 | `scripts/skill_inventory.py` đếm sau khi áp + `/reload-plugins` |

## 3. Cách tiếp cận + lý do

- **Tắt-mặc-định + bật-khi-cần** là cách duy nhất giảm context thật: harness nhét
  catalog skill vào mọi message, chưa có deferred discovery (issue #42650); tắt plugin
  là cơ chế duy nhất gỡ catalog. Phương án "giữ bật + luật chỉ-dùng-khi-khớp" bị loại
  vì không giảm token.
- **Script + file tier riêng** thay vì hardcode danh sách vào hook command: một nguồn
  sự thật, sửa danh sách không phải sửa hook; script sửa `enabledPlugins` bằng
  atomic write (đọc → đổi → ghi file tạm → rename), có backup `.bak` một bản.
- **Đề-xuất-và-hỏi trước khi bật** (quyết định user, interview vòng 1): Claude không
  bao giờ tự bật; chỉ chạy lệnh enable sau khi user đồng ý, rồi in đúng 1 dòng nhắc
  gõ `/reload-plugins`.
- **Reset ở cả SessionEnd lẫn SessionStart(startup)**: SessionEnd không bắn khi crash.
  Lưu ý giới hạn: hook SessionStart chạy SAU khi phiên đã nạp catalog — reset lúc
  startup chỉ dọn settings cho lần nạp kế tiếp (phiên hiện tại muốn áp ngay phải gõ
  `/reload-plugins`). Idempotent — chạy lặp vô hại.
- **§10 viết lại cùng lượt** vì mục lazy-load mới và §10 cùng nằm một file, sửa một
  lần tránh hai request đụng cùng file.

## 3b. Năng lực & công cụ

Phân vân → DÙNG. Không xoá mục này kể cả khi mọi dòng là KHÔNG.

| Skill | Nguồn | Phán quyết | Dùng ở đâu / Lý do loại |
|---|---|---|---|
| tdq-intake, tdq-spec, tdq-plan, tdq-build, tdq-status, tdq-conventions | plugin:tdq-workflow | NỀN | skill khung đang chạy |
| update-config | built-in | DÙNG | task sửa `~/.claude/settings.json` (enabledPlugins + hooks) — nạp trước khi ghi để đúng schema settings |
| hook-development (plugin-dev) | plugin | DÙNG | viết đúng 2 hook SessionEnd/SessionStart user-level (matcher, event, exit code) |
| claude-md-improver (claude-md-management) | plugin | DÙNG | audit `~/.claude/CLAUDE.md` sau khi thêm mục mới + §10 |
| tavily-search (tavily-primary MCP) | MCP | NỀN | lớp research của workflow (đã dùng ở analyze) |
| graphify | user | KHÔNG | khác lĩnh vực |
| ~215 skill còn lại (bảng nén — danh sách nhóm trong knowledge cùng slug) | plugin/built-in | KHÔNG | khác lĩnh vực |

## 4. Yêu cầu bắt buộc

1. **Log service bật mặc định**: `plugin_tiers.py` ghi log timestamp ISO vào
   `~/.claude/logs/plugin-tiers.log` (mỗi lần reset/enable: plugin nào đổi, giá trị
   cũ→mới); tắt bằng env `PLUGIN_TIERS_LOG=0`; lỗi JSON/IO → cảnh báo 1 dòng stderr
   + exit 0 (hook không được chặn phiên), exit 2 chỉ khi sai cú pháp lệnh.
2. Không placeholder — mọi lệnh, tên plugin, đường dẫn trong CLAUDE.md là giá trị thật.
3. Test cho từng phần (script: tier list, atomic write, idempotent, log on/off, và
   BẮT BUỘC 3 case an toàn: (a) trước/sau `reset`, settings.json chỉ khác đúng các
   key thuộc 2 danh sách tier — mọi key khác giữ nguyên từng byte; (b) settings.json
   hỏng/thiếu → 1 dòng ⚠️ stderr, exit 0, KHÔNG ghi đè file; (c) plugin-tiers.json
   hỏng → như (b); xem §6).
4. Instruction cho model thấp: bảng định tuyến enum đóng dạng
   `| Việc chạm tới … | Bật plugin … |`, kèm đúng 2 bước hành động (hỏi user → chạy
   lệnh + nhắc `/reload-plugins`), không có bước tự suy diễn.
5. Script không chứa API key, không gọi mạng.

## 5. Ràng buộc & rủi ro

| Rủi ro | Mức | Xử lý |
|---|---|---|
| Nhiều session song song: session A kết thúc HOẶC phiên mới khởi động (reset startup) → tắt plugin session B đang dùng | TB | Chấp nhận (ghi rõ trong CLAUDE.md: bật lại nhanh bằng 1 lệnh); mitigation phức tạp hơn nằm ngoài scope |
| SessionEnd không bắn khi crash/kill | TB | Reset bù ở SessionStart matcher `startup`; giới hạn: chỉ dọn settings cho lần nạp kế tiếp, phiên hiện tại cần `/reload-plugins` |
| Ghi `settings.json` khi app đang chạy | TB | Atomic write (tmp + rename) + backup `.bak`; chỉ đổi key trong `enabledPlugins` |
| `/reload-plugins` phải do user gõ — Claude không tự áp được thay đổi | Thấp | Instruction in đúng 1 dòng nhắc; nghiệm thu cuối cần user gõ 1 lần |
| feature-dev vẫn bật → agent code-reviewer của nó còn hiện | Thấp | Bảng định tuyến ghi rõ: review dùng built-in `/code-review` |
| CLAUDE.md toàn cục đổi ảnh hưởng mọi project | Thấp | Mục mới ngắn (≤ 45 dòng), enum đóng, không mâu thuẫn luật cũ |
| Bug #27247 (local scope) | Không áp dụng | Chỉ ghi user settings, key `enabledPlugins` đã tồn tại |

## 6. Phạm vi QC & Definition of Done

1. `python3 -m unittest discover tests` OK — toàn bộ suite hiện có xanh + ≥ 8 test mới.
2. Chạy thật trên máy: `plugin_tiers.py reset` → `claude plugin list --disabled`
   đúng đủ 22 tên, không lẫn tier luôn-bật; `plugin_tiers.py enable <1 plugin
   on-demand>` → `true`, rồi `reset` → về `false` (mô phỏng SessionEnd).
3. Log: file log có dòng timestamp cho lần reset/enable (plugin nào, cũ→mới);
   `PLUGIN_TIERS_LOG=0` → không ghi.
4. 3 case an toàn §4.3 (settings nguyên vẹn ngoài key tier · settings hỏng không ghi
   đè · tier hỏng không ghi đè) pass bằng unit test + chạy tay 1 lần.
5. `~/.claude/CLAUDE.md`: grep `tdq-start|tdq-analyze|tdq-approve` = 0; mục lazy-load
   đủ 16 dòng định tuyến; chạy audit bằng skill claude-md-improver, áp góp ý hợp lý.
6. `doc_lint.py docs/tdq/spec` exit 0 (R8); sau plan: `doc_lint.py --pair` exit 0.
7. Đo lại: `skill_inventory.py` ≤ 85 skill sau khi user gõ `/reload-plugins`
   (nghiệm thu cuối cùng cần 1 thao tác user này).
8. Bản copy `~/.claude/scripts/plugin_tiers.py` trùng hash (sha256) với
   `scripts/plugin_tiers.py` trong repo sau bước cài.
9. Working log + report ≤ 50 dòng theo chuẩn TDQ.

## 7. Câu hỏi còn mở

(rỗng)
