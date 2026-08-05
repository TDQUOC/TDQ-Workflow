# Kiến thức chốt — audit tối ưu token/time workflow (vòng 3)

## Năng lực dùng được (B0)

Phân vân → DÙNG. Không xoá bảng này kể cả khi mọi dòng là KHÔNG.

| Skill | Nguồn | Phán quyết | Dùng ở đâu / Lý do loại |
|---|---|---|---|
| tdq-workflow:tdq-intake, tdq-conventions, tdq-spec, tdq-plan, tdq-build, tdq-status | plugin:tdq-workflow | NỀN | chính workflow đang chạy |
| graphify | user | DÙNG | map cấu trúc/dependency toàn bộ workflow khi tìm chỗ tốn token (chưa chạy trong vòng này — cân nhắc ở QC nếu cần soi dependency) |
| claude-api | built-in | DÙNG | tra cứu cơ chế prompt caching/pricing khi đánh giá đề xuất (tham chiếu ở mục 5 research) |
| claude-md-management:claude-md-improver | plugin | DÙNG | đối chiếu chuẩn audit CLAUDE.md (CLAUDE.md đã qua vòng 2, chỉ tham khảo tiêu chí) |
| tavily (tavily-primary MCP, qua agent search-scout) | plugin:tavily | DÙNG | research bên ngoài — đã chạy 4 truy vấn, 12 finding, `docs/tdq/research/2026-08-05-audit-toi-uu-workflow.md` |
| feature-dev:feature-dev, code-review:code-review, remember:doctor, remember:remember, plugin-dev:create-plugin/agent-development/command-development/hook-development/mcp-integration/plugin-settings/plugin-structure/skill-development, agent-sdk-dev:new-sdk-app, hookify:configure/help/hookify/writing-rules/list, skill-creator:skill-creator, frontend-design:frontend-design, playground:playground, mcp-server-dev:build-mcp-app/build-mcp-server/build-mcpb, dataviz, artifact-design/artifact-diagramming/artifact-capabilities, update-config, keybindings-help, simplify, run, init, review, security-review, tavily-cli/crawl/dynamic-search/extract/map/best-practices/tavily-search(skill dạy)/tavily-research(skill dạy) | built-in/plugin | KHÔNG | khác lĩnh vực — round này chỉ phân tích + viết report, không tạo plugin/hook/skill mới, không sửa code, không cần trực quan hoá |

## 1. Số liệu đo hiện tại (sau các fix vòng 2)

Đo lúc 11:04, 3 session gần nhất (`python3 scripts/token_audit.py --sessions 3 --top 12`):

- Tổng carry-cost **142.493.808 token** / 1.310 API call / cache_read 153,34M / cache_write 4,13M.
- Chi phí quy đổi (TTL 1h): 28,26M input-token tương đương — cache_read 54% · cache_write 29% · output 16%.

| nhóm | lần | carry-cost |
|---|---|---|
| Read file | 155 | 47.751.442 |
| Bash khác | 348 | 36.978.979 |
| tavily search | 19 | 16.547.726 |
| chạy test suite | 115 | 11.535.669 |
| `tdq_state.py` dump JSON | 127 | 7.366.700 |
| doc_lint | 106 | 6.320.107 |
| WebFetch | 3 | 4.994.518 |
| Edit (echo lại diff) | 251 | 4.054.785 |
| Agent | 16 | 3.056.485 |

Điểm mới so với vòng 2: **Read file** vẫn giữ #1 và còn tăng (32,96M → 47,75M). **WebFetch**
lần đầu lọt top dù chỉ 3 lần gọi — 1 lệnh WebFetch 37.206 ký tự mang carry-cost 4.483.082
token. Đây là minh chứng cơ chế "carry-cost nhân theo số lần bị đọc lại trong cache_read của
các API call sau" khi tool-result lớn xuất hiện sớm trong session dài.

## 2. Đối chiếu vòng 1 + vòng 2 (agent D)

- Vòng 1 (19 đề xuất) + vòng 2 (21 task) đã làm: A4/A5 (`tdq_state`/`doc_lint` im lặng),
  B1 (research qua search-scout, digest ≤1.500), D1/D2(v1) (gộp Bash, test theo module),
  A2 (Read theo offset/grep). Cũng đã làm: C1 (CLAUDE.md lõi ≤3.500 byte), B1(v2)
  (`tdq_finish.py`), B2/B3/C1/C2/D1/E2(v2) (6 luật context vào tdq-conventions). Và:
  D2/D3(v2) (effort + ngưỡng digest 7 agent), D4(v2) (plan >6 task → đề xuất mode
  subagent), E1(v2) (sửa lỗi đếm `token_audit.py`).
- **Deferred, chưa vòng nào đụng**: A3(v1) Bash im lặng cấm `grep -A/-B`/`cat`, A6 gộp
  sửa lặp thành script, B2(v1) đọc ≥4 file qua Explore (thành luật bắt buộc), C2 chia nhỏ
  `tdq-build/SKILL.md`, D3(v1) gộp Edit cùng file. Còn: E1(v1) gộp
  questions+research+knowledge, E2(v1) cap dòng qua `doc_lint`, E3(v1) 1 request/session
  `/clear`, E4(v1) lane quick mạnh hơn.
- **Nợ đo lường chưa đóng**: report vòng 2 tự ghi nhận đo before/after (14,73M → 20,29M).
  Số này **tăng chứ không giảm** vì đo trong 1 session đang phình — "không chứng minh cải
  thiện" (`reports/2026-08-05-toi-uu-token-vong-2.md`). Số đo 142,49M ở mục 1 (vòng này, 3
  session MỚI, sau fix) cũng không so sánh trực tiếp được với số cũ vì khác cỡ mẫu. Cần đo
  trên session sạch, cùng kịch bản mới, mới kết luận được P0-P2 có hiệu quả thật hay không.
- Cả 2 vòng đều loại trừ tường minh: sửa `~/.claude/settings.json` phần hooks/env/permissions
  — vòng này audit hook (chỉ đọc) đã bổ khuyết phần bị bỏ trống đó.

## 3. Phát hiện mới (vòng 3) — token/thời gian

**Skill (`skills/tdq-*`):**
- Mọi request mới nạp cứng `tdq-conventions` (120 dòng) + `tdq-intake` (117 dòng) ≈ 15,3KB
  trước khi biết việc gì, kể cả câu hỏi vặt rơi vào quick lane.
- Trùng lặp nội dung nhiều nơi: khuôn interview (4 nơi), luật cấm prefix tên AI (4 nơi),
  luật "chỉ sửa state qua CLI" (3 nơi). Ngưỡng digest ≤1.500 ký tự cũng bị chép tay vào
  từng agent thay vì trỏ 1 nguồn — rủi ro bảo trì khi thêm agent mới.
- `tdq-build/SKILL.md` có 3 lệnh git rời rạc (đóng worktree) không gộp bằng `&&`, không
  nhất quán với luật gộp Bash đã có ở `tdq-conventions` §10.
- 4 file references không có giới hạn kích thước (`subagent-tuning.md`, `plugin-routing.md`,
  `deep-search.md` nhánh degrade, `phases.md`) — rủi ro phình dần theo thời gian, khác các
  template đã có trần dòng rõ ràng.

**Script (`scripts/*.py`):**
- `tdq_state.py.turn_snapshot()` gọi `git status --porcelain` **2 lần trùng lặp** (qua
  `repo_status_digest` và `repo_status_paths`, cùng argument, không cache) — chạy mỗi turn
  qua `prompt_context.py`, rồi `stop_gate.py` cuối turn gọi lại lần nữa khi nghi vấn đổi repo.
- `external_task.py skill_dump` in nguyên văn SKILL.md + references ra stdout không giới
  hạn, để orchestrator dán lại nguyên văn vào packet. Nội dung tính token **2 lần** (đọc +
  viết lại) dù đích đến là engine ngoài, không phải model đọc hiểu.
- `bash_gate.py` đọc lại `turn_rows()` (parse `.tdq-turn.jsonl`) 3 lần trong 1 lần invoke,
  không cache trong process — chi phí thấp mỗi lần nhưng cộng dồn theo số lệnh Bash/turn.

**Hook:**
- `UserPromptSubmit` in `[TDQ:NEXT]`/`[TDQ:INTAKE]` mỗi turn kể cả turn không liên quan TDQ,
  nội dung LẶP Y HỆT khi state không đổi — carry-cost thuần lặp lại.
- `edit_gate.py`/`bash_gate.py` reminder `TDQ:APPROVE` chỉ dedupe trong 1 turn, KHÔNG dedupe
  cross-turn — spec/plan kéo dài nhiều turn có Edit sẽ lặp cảnh báo gần giống nhau nhiều lần.
- LSP: xác nhận không còn eager-load nào sót — vòng 2 đã fix đúng, chỉ `pyright-lsp` bật.

## 4. Phát hiện mới (vòng 3) — issue logic/an toàn (user đã chốt: đưa vào report)

1. **Mâu thuẫn luật thật**: `quick-lane.md` nói external cho task `(mcp)` là *soft-block*
   ("user vẫn đòi thì làm theo"), nhưng `tdq-build/SKILL.md` nói *hard-block* ("đã chặn từ
   lúc duyệt"). Hai văn bản đưa ra 2 hành vi khác nhau cho cùng tình huống.
2. **Định nghĩa "đã đổi repo" lệch nhau**: `reminder-codes.md` loại trừ hẳn `docs/tdq/` khỏi
   vân tay repo, còn `tdq-conventions/SKILL.md` §6 diễn đạt rộng hơn ("turn nào đổi repo").
   Chỉ đọc §6 mà không mở `reminder-codes.md` dễ hiểu sai khi nào bắt buộc ghi log.
3. **`stop_gate.py` rủi ro false-positive thật**: so `git status` toàn working tree, không
   scope theo turn/worktree/session. Worktree hoặc process khác sửa file cùng lúc có thể
   khiến turn hiện tại bị gán oan "đã đổi repo" và bị chặn đòi ghi log việc không phải mình
   làm. Code tự nhận thức rủi ro này trong docstring (từng có bug tương tự ở 0.3.1) nhưng
   chưa có biện pháp khắc phục thêm.
4. Ranh giới "chặn kỹ thuật → tự chọn, không hỏi" vs "chặn cần user gỡ → dừng hỏi" trong
   `tdq-build/SKILL.md` Luật cứng không có tiêu chí phân biệt rõ, dựa hoàn toàn vào phán
   đoán của model.

## 5. Nguyên tắc rút ra từ research ngoài (4 truy vấn tavily-primary, 12 finding)

Chi tiết + evidence_quote: `docs/tdq/research/2026-08-05-audit-toi-uu-workflow.md`.

1. Prompt caching là đòn bẩy #1 — giữ system prompt/tool-def ổn định, front-load trước
   breakpoint; cache_read rẻ hơn cache miss ~90%, hoà vốn chỉ sau ~2 lần tái dùng.
2. Lọc output TRƯỚC khi vào context (hook grep/lọc log, test output) có thể giảm một lệnh
   từ 80.000 xuống 2.000 token — khớp trực tiếp với finding WebFetch 37K ký tự / 4,48M
   carry-cost ở mục 1.
3. Subagent = context isolation thật (giảm ~67% token so với nhồi nhiều skill vào 1 hội
   thoại chính) nhưng tốn thêm lượt điều phối — parent phải scope input tường minh.
4. CLAUDE.md/skill là overhead LẶP LẠI mỗi session (20-30k token trước khi gõ chữ đầu) —
   nên giữ dưới ~500 token, đẩy luật chi tiết sang file scoped theo path/tình huống.
5. Plan mode / phân tích thuần (không sửa file) mặc định cho các round research-only có
   thể giảm ~50% token phiên đó so với round có build.

## 6. Quyết định đã chốt (interview vòng 1 lúc mở request + vòng 2 lúc 11:18)

- Phạm vi report gồm **cả issue logic/an toàn** (mục 4), không chỉ token/time thuần
  (user chọn A, câu 1 vòng 2).
- Request này **dừng ở report đề xuất** — không sửa code sản phẩm ngay. "Implement" của
  lane full = viết report + knowledge, không phải code change. Việc triển khai đề xuất nào
  sẽ là request mới do user tự mở sau khi đọc (user chọn A, câu 2 vòng 2).
- Không đo lại theo kịch bản chuẩn hoá (session sạch, cùng thao tác before/after) trong
  round này. Đây là khoảng trống đo lường tồn đọng từ vòng 2 — đề xuất cho vòng triển khai
  sau nếu muốn có bằng chứng before/after đáng tin.

## 7. Phương án đã loại

- Không mở lại `~/.claude/settings.json` để sửa hook trong round này (chỉ audit, không
  sửa) — khớp với việc dừng ở report, không implement code.
- Không chạy `graphify` để vẽ dependency graph riêng cho audit này — 5 agent đọc trực
  tiếp source đã đủ độ chi tiết cần thiết. Tránh phát sinh thêm 1 lượt review đồ thị không
  cần thiết cho một round chỉ ra report.
- Không kích hoạt deep-search hybrid (agy + scout 2 phase) — chủ đề research (best practice
  tối ưu context agentic workflow) không đạt ≥2 tín hiệu trigger ở `deep-search.md`, dùng
  1 agent `search-scout` (tavily thường) là đủ.

## 8. Nguồn

- `docs/tdq/research/2026-08-05-audit-toi-uu-workflow.md` (4 truy vấn, 12 finding có
  evidence_quote).
- `docs/tdq/{requests,knowledge,spec,plan,reports,qc}/2026-08-04-toi-uu-token-workflow*`
  và `2026-08-05-toi-uu-token-vong-2*` (đối chiếu vòng 1/2).
- Đo trực tiếp: `python3 scripts/token_audit.py --sessions 3 --top 12` (11:04, 2026-08-05).
- Đọc trực tiếp: `skills/tdq-*/**/*.md`, `agents/*.md`, `scripts/{tdq_state,tdq_finish,
  doc_lint,external_task,search_task,claude_export,plugin_tiers,external_models,
  skill_inventory}.py`, `hooks/scripts/*.py`, `.claude/settings.json`, `~/.claude/settings.json`
  (chỉ đọc, không in secret).

## 9. Đề xuất xếp ưu tiên

Gộp mục 3 (10 finding token/time) + mục 4 (4 issue logic/an toàn) + mục 2 (9 đề xuất
deferred vòng 1/2 + 1 nợ đo lường) = 24 mục. Xếp theo ma trận effort thấp/impact cao
trước → effort cao/impact cao → effort cao/impact thấp. Cột "Nguồn" trỏ về mục đã audit
ở trên để đối chiếu.

### P0 — effort thấp, impact cao (làm sớm)

| # | Đề xuất | Nguồn | Effort | Impact |
|---|---|---|---|---|
| P0-1 | Nới trần report `≤10 dòng` → khuyến nghị 10-20 dòng, không giới hạn cứng | mục "Bổ sung Bản 1.1" round này | Thấp | Giảm rủi ro report bị cắt cụt mất ý — **đã làm trong round này (P2 của plan)** |
| P0-2 | `tdq_state.py.turn_snapshot()` gộp 2 lần gọi `git status --porcelain` trùng lặp thành 1, cache trong hàm | mục 3 script (SC1) | Thấp | 1 subprocess call ít hơn mỗi turn có prompt_context + stop_gate |
| P0-3 | `bash_gate.py` cache `turn_rows()` trong 1 lần invoke thay vì parse lại 3 lần | mục 3 script (SC3) | Thấp | Cộng dồn theo số lệnh Bash/turn, effort sửa nhỏ (thêm biến cache cục bộ) |
| P0-4 | Sửa mâu thuẫn luật: `quick-lane.md` (soft-block) vs `tdq-build/SKILL.md` (hard-block) cho task `(mcp)` khi external — chọn 1 hành vi, đồng bộ 2 file | mục 4 issue #1 | Thấp | An toàn — tránh hành vi sai khi gặp task `(mcp)` lúc giao external |
| P0-5 | Hợp nhất định nghĩa "đã đổi repo" giữa `reminder-codes.md` và `tdq-conventions/SKILL.md` §6 (1 nguồn, nơi kia trỏ link) | mục 4 issue #2 | Thấp | Tránh hiểu sai khi nào bắt buộc ghi working log |
| P0-6 | Gộp `tdq-build/SKILL.md` 3 lệnh git rời rạc lúc đóng worktree external bằng `&&`, khớp luật gộp Bash đã có | mục 3 skill (S3) | Rất thấp | Vài Bash call ít hơn mỗi lần đóng worktree external |

### P1 — effort cao hơn nhưng impact vẫn đáng kể (hoặc effort thấp/impact vừa)

| # | Đề xuất | Nguồn | Effort | Impact |
|---|---|---|---|---|
| P1-1 | Xem lại kiến trúc nạp cứng `tdq-conventions` (120 dòng) + `tdq-intake` (117 dòng) ≈15,3KB mọi request, kể cả câu hỏi vặt quick lane — cân nhắc bản rút gọn cho quick | mục 3 skill (S1) | Cao | Impact cao nhất theo research #4 (CLAUDE.md/skill là overhead lặp mỗi session) |
| P1-2 | Gộp 4 loại luật trùng lặp rải rác (khuôn interview 4 nơi, cấm prefix AI 4 nơi, "chỉ sửa state qua CLI" 3 nơi, ngưỡng digest ≤1.500 ký tự chép tay mỗi agent) về 1 nguồn, nơi khác trỏ link | mục 3 skill (S2) | Trung bình | Giảm token + giảm đúng loại rủi ro round này gặp phải (sửa 1 nơi quên nơi khác — như trần report) |
| P1-3 | `stop_gate.py` scope phát hiện "đổi repo" theo turn/worktree thay vì `git status` toàn working tree | mục 4 issue #3 | Cao | An toàn — false-positive/false-negative khi có worktree hoặc process khác chạy song song |
| P1-4 | Viết tiêu chí cụ thể phân biệt "chặn kỹ thuật → tự chọn" vs "chặn cần user gỡ → dừng hỏi" trong Luật cứng `tdq-build/SKILL.md` | mục 4 issue #4 | Thấp-trung bình | Giảm rủi ro model tự quyết sai lúc build |
| P1-5 | `external_task.py skill_dump` nén/trích thay vì in nguyên văn SKILL.md (đang tính token 2 lần: đọc + dán lại packet) | mục 3 script (SC2) | Trung bình | Chỉ ảnh hưởng khi dùng mode external, nhưng packet có thể lớn |
| P1-6 | `UserPromptSubmit` rút gọn/dedupe khi `[TDQ:NEXT]` in ra Y HỆT turn trước (state không đổi) | mục 3 hook (H1) | Trung bình | Carry-cost lặp lại mỗi turn — đúng loại overhead research #4 cảnh báo |
| P1-7 | `TDQ:APPROVE` reminder dedupe cross-turn (hiện chỉ dedupe trong 1 turn) cho spec/plan kéo dài nhiều turn | mục 3 hook (H2) | Trung bình | Giảm cảnh báo lặp gần giống nhau nhiều lần |
| P1-8 | A3(v1) deferred: cấm `grep -A/-B`/`cat` không mục tiêu trong luật Bash im lặng, khuyến khích `grep -n` + `Read offset/limit` | mục 2 deferred | Thấp | Giảm output tool lớn không cần thiết |
| P1-9 | B2(v1) deferred: bắt buộc đọc ≥4 file qua Explore agent thay vì Read trực tiếp trong hội thoại chính | mục 2 deferred | Thấp | Context isolation theo research #3 (giảm ~67% khi cô lập đúng) |
| P1-10 | E3(v1) deferred: khuyến nghị `/clear` sau khi đóng 1 request/session dài | mục 2 deferred | Thấp | Giảm tích luỹ context qua nhiều request nối tiếp trong 1 phiên |
| P1-11 | C2 deferred: chia nhỏ `tdq-build/SKILL.md` (đang dài, nạp cứng mỗi lần build) | mục 2 deferred | Trung bình | Giảm token nạp mỗi lần vào phase build |
| P1-13 | Lọc output trước khi vào context cho nhóm carry-cost lớn nhất (theo nguyên tắc research #2): "chạy test suite" (11,5M) và "Bash khác" (36,98M) ở mục 1 — chỉ dán phần fail/summary, không dán log đầy đủ | mục 5 nguyên tắc #2 + mục 1 số liệu | Trung bình | Cao — đúng 2 nhóm đang đứng #2-#3 carry-cost sau Read file |
| P1-12 | Đo lại theo kịch bản chuẩn hoá (session sạch, cùng thao tác before/after) để xác nhận P0-P2 vòng 1/2 có hiệu quả thật | mục 2 "nợ đo lường" | Trung bình | Cao — xác nhận hay bác bỏ toàn bộ nỗ lực tối ưu 2 vòng trước; không có số này thì mọi kết luận "đã tối ưu" đều chưa chứng minh được |

### P2 — effort cao/impact thấp hơn, hoặc cần làm rõ thêm trước khi làm

| # | Đề xuất | Nguồn | Effort | Impact |
|---|---|---|---|---|
| P2-1 | T7: thêm trần dòng cho 4 file references chưa có giới hạn (`subagent-tuning.md`, `plugin-routing.md`, `deep-search.md` nhánh degrade, `phases.md`) | mục 3 skill (S4) | Thấp | Thấp-trung bình — chỉ ngừa phình dần, chưa phải vấn đề cấp bách |
| P2-2 | E1(v1) deferred: gộp `questions`+`research`+`knowledge` thành ít file hơn | mục 2 deferred | Cao | Trung bình — đổi cấu trúc tài liệu TDQ, rủi ro phá quy ước đang chạy ổn |
| P2-3 | A6(v1) deferred: gộp thao tác sửa lặp nhiều file giống hệt thành 1 script | mục 2 deferred | Trung bình-cao | Thấp — chỉ có lợi khi thật sự có đợt sửa lặp lại quy mô lớn |
| P2-4 | D3(v1) deferred: gộp nhiều lệnh Edit cùng file trong 1 turn | mục 2 deferred | Thấp | Thấp — Edit đã rẻ hơn nhiều so với Read/Bash theo bảng carry-cost mục 1 |
| P2-5 | E4(v1) deferred: lane quick "mạnh hơn" — ý chưa rõ, cần hỏi lại user cụ thể muốn mạnh ở khía cạnh nào trước khi ước lượng effort | mục 2 deferred | Chưa xác định | Chưa xác định — mở request mới nên hỏi lại trước |
| P2-6 | Áp research #5 (mặc định plan mode/phân tích thuần cho round research-only, không build) thành luật lane | mục 5 nguyên tắc #5 | Trung bình | Trung bình — chỉ áp dụng cho nhóm round thuần nghiên cứu, không phải mọi request |
| P2-7 | E2(v1) deferred: cap dòng report bằng `doc_lint` (máy kiểm cứng) — **đã lỗi thời**: mâu thuẫn trực tiếp với P0-1 (round này vừa bỏ trần cứng) | mục 2 deferred | — | Không nên làm — giữ nguyên quyết định P0-1 |

Ghi chú đối chiếu Q3: 24 mục nguồn (10 mục 3 + 4 mục 4 + 9 deferred + 1 nợ đo lường)
đều xuất hiện ở trên; mục 3 "S2" (4 loại trùng lặp) gộp thành 1 dòng P1-2 vì cùng một
hướng sửa (gộp 1 nguồn sự thật) — ghi rõ 4 loại trong dòng đó theo đúng luật cho phép
gộp của spec Q3.

Đối chiếu T1.2 (12 finding research, 4 truy vấn tavily-primary → 5 nguyên tắc tổng hợp
ở mục 5): #1 caching leverage → P0-1/P1-6/P1-7 (giữ nội dung hook ổn định, giảm lặp
y hệt); #2 lọc output trước context → P1-5 (skill_dump) + P1-13 (test suite/Bash log);
#3 subagent isolation → P1-9 (Explore ≥4 file); #4 CLAUDE.md/skill overhead lặp mỗi
session → P1-1 + P1-2; #5 plan mode mặc định cho round research-only → P2-6. Cả 5
nguyên tắc (đại diện cho 12 nguồn) đều có ≥1 dòng đề xuất tương ứng — không sót.

## Lộ trình

| Bước/phase | CÓ-BỎ | Vì sao |
|---|---|---|
| Phân tích (đã xong) | CÓ | bắt buộc, đã hoàn tất B0-B6 |
| Spec | CÓ | chốt phạm vi + cấu trúc report trước khi viết, dù deliverable là tài liệu |
| Plan | CÓ | chia task viết từng phần report (issue → đề xuất → ưu tiên), theo khung bất biến |
| Implement | CÓ (dạng viết tài liệu, không sửa code) | viết `docs/tdq/reports/2026-08-05-audit-toi-uu-workflow.md` + hoàn thiện knowledge này |
| QC | CÓ, rút gọn | không có test code — QC = tự rà report đủ ý theo DoD (`doc_lint`, đối chiếu mục 3+4 đã đưa hết vào report chưa) |
| Report cuối (chat) | CÓ | tóm tắt ≤10 dòng trỏ vào report chi tiết |
