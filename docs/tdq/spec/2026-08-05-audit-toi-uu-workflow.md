# SPEC — Audit toàn bộ workflow TDQ, đề xuất tối ưu token/thời gian (vòng 3)

<!-- doc-lint: allow R10 — spec viết trước khi có luật ranh giới module -->

Ngày: 2026-08-05 · Bản: 1.1 · Request: ../requests/2026-08-05-audit-toi-uu-workflow.md · Lane: full
Trạng thái: CHỜ DUYỆT

## 1. Mục tiêu & phạm vi
- Mục tiêu: có một bản report đề xuất đầy đủ — liệt kê MỌI issue tốn token/thời gian
  (và issue logic/an toàn liên quan) đang tồn tại trong workflow TDQ, kèm hướng optimize
  cụ thể, xếp ưu tiên — để user tự quyết mở request triển khai phần nào.
- Trong phạm vi: `skills/tdq-*` (SKILL.md + references), `scripts/*.py` dùng bởi TDQ,
  `agents/*.md`, hook (`hooks/scripts/*.py`, `.claude/settings.json`, phần hook của
  `~/.claude/settings.json`), đối chiếu với đề xuất/nợ còn treo của vòng 1
  (`2026-08-04-toi-uu-token-workflow`) và vòng 2 (`2026-08-05-toi-uu-token-vong-2`).
- **Bổ sung (Bản 1.1, theo yêu cầu user giữa lúc chờ duyệt spec):** nới lỏng convention
  chung "report `docs/tdq/reports/<slug>.md` ≤10 dòng" trên TOÀN workflow (áp dụng mọi
  request TDQ sau này, không chỉ report của round này) — bỏ trần cứng, thay bằng khuyến
  nghị "ngắn gọn nhất có thể, khoảng 10-20 dòng là ổn". Đây là 1 thay đổi nhỏ, độc lập,
  làm luôn trong round này (không mở request riêng). KHÔNG đụng tới convention khác
  ("tóm tắt ≤10 dòng trong chat" của quick-lane/status) — giữ nguyên.
- NGOÀI phạm vi: sửa code/skill/script/hook khác ngoài việc nới trần report ở trên
  (round này KHÔNG implement các đề xuất tối ưu tìm được, chỉ report — user đã chốt câu 2
  vòng interview 2); đo lại before/after theo kịch bản chuẩn hoá (ghi nhận là khoảng
  trống, không tự bổ sung trong round này); các plugin/skill không thuộc `tdq-workflow`
  (ngoài phạm vi audit hiệu năng workflow này).

## 1b. Lộ trình
Chép từ `knowledge/2026-08-05-audit-toi-uu-workflow.md` mục "Lộ trình".

| Bước/phase | Chạy? | Vì sao |
|---|---|---|
| Phân tích | CÓ | đã hoàn tất — 5 agent song song (đối chiếu vòng 1/2, skill, script, hook, research ngoài) + tự đo `token_audit.py` |
| Research web | CÓ | 4 truy vấn tavily-primary qua agent `search-scout`, 12 finding có nguồn |
| Interview | CÓ | 2 vòng — chốt phạm vi report (gồm issue logic) và điểm dừng (report, không implement) |
| QC độc lập (agent) | BỎ | deliverable là tài liệu, không có test code chạy được — QC = tự đối chiếu DoD + `doc_lint`, không cần agent riêng cho việc này |
| Implement (dạng viết tài liệu) | CÓ | viết report + hoàn thiện knowledge, không sửa code sản phẩm |

## 2. Đầu ra cụ thể
| # | Đầu ra | Đường dẫn/vị trí | Đo "xong" bằng |
|---|---|---|---|
| 1 | Report tổng hợp (chuẩn TDQ, ngắn gọn ~10-20 dòng, trỏ vào knowledge) | `docs/tdq/reports/2026-08-05-audit-toi-uu-workflow.md` | `doc_lint.py` exit 0 (không còn kiểm `wc -l` ≤10) |
| 2 | Danh sách đầy đủ issue + đề xuất optimize, xếp ưu tiên P0/P1/P2 kèm effort ước lượng | trình bày trong chat cuối turn build (nội dung "report đề xuất" chính user yêu cầu) + lưu trong `knowledge/2026-08-05-audit-toi-uu-workflow.md` mục mới "## 9. Đề xuất xếp ưu tiên" | mọi finding ở knowledge mục 3+4 đều xuất hiện trong bảng ưu tiên (đối chiếu tay khi QC) |
| 3 | Knowledge đã hoàn thiện (đã có phần lớn từ phase analyze) | `docs/tdq/knowledge/2026-08-05-audit-toi-uu-workflow.md` | file tồn tại, đủ 9 mục |
| 4 | Nới trần report thành convention chung (không giới hạn cứng, khuyến nghị 10-20 dòng) | `skills/tdq-build/references/report-template.md`, `skills/tdq-build/SKILL.md` (dòng 136,142), `portable/workflow/references/report-template.md`, `portable/workflow/04-build.md` (dòng 125,132), `scripts/tdq_state.py` (`PHASE_TABLE`, action ~499 + checklist ~502), `skills/tdq-conventions/references/phases.md` + `portable/workflow/phases.md` (sinh lại qua `phases-doc`, KHÔNG sửa tay), `portable/claude-md/CLAUDE.md` dòng 41 (cài lại `~/.claude/CLAUDE.md`, backup có timestamp), `portable/AGENTS.md` dòng 13 (sơ đồ) | `tests/test_phase_table.py` + `tests/test_claude_md_core.py` PASS, `doc_lint.py` exit 0 trên mọi file .md đã sửa, `grep -rn "≤ *10 dòng"` trên các file này không còn khớp (trừ convention "tóm tắt trong chat" cố tình giữ nguyên) |

## 3. Cách tiếp cận & lý do
- Chọn: gộp toàn bộ finding đã có ở knowledge (mục 2-4: token/time + logic/an toàn) và
  9 đề xuất deferred từ vòng 1/2 thành MỘT danh sách duy nhất, xếp ưu tiên theo ma trận
  effort thấp/impact cao trước, effort cao/impact cao sau, effort cao/impact thấp cuối
  cùng (không tạo danh sách rời rạc theo nguồn).
- Vì: user cần một bản để đọc và tự quyết mở request tiếp theo — danh sách rời theo
  nguồn (vòng 1 riêng, vòng 3 riêng) sẽ buộc user phải tự gộp, đi ngược mục tiêu "report
  đề xuất" gọn để quyết định.
- Đã loại: viết luôn spec/plan/build cho từng đề xuất riêng lẻ trong round này — vì user
  đã chọn dừng ở report (câu 2 vòng interview 2); triển khai để request mới tự chọn phạm
  vi, tránh gộp quá nhiều thay đổi không liên quan vào 1 lần duyệt.
- Việc nới trần report (mục bổ sung 1.1) là NGOẠI LỆ được user chốt tường minh khi
  góp ý spec ("thêm vào spec là update report... không có max limit line... khoảng
  10-20 line là okay") + xác nhận qua câu hỏi phạm vi ("convention chung, toàn
  workflow") — không mâu thuẫn với quyết định "dừng ở report" vì đây là 1 thay đổi
  nhỏ độc lập (đổi 1 con số trong luật), không phải triển khai đề xuất tối ưu nào
  trong danh sách audit.

## 3b. Năng lực & công cụ
Chép từ `knowledge/2026-08-05-audit-toi-uu-workflow.md` mục "Năng lực dùng được".

| Skill | Nguồn | Phán quyết | Dùng ở đâu / Lý do loại |
|---|---|---|---|
| tdq-workflow:tdq-intake, tdq-conventions, tdq-spec, tdq-plan, tdq-build, tdq-status | plugin:tdq-workflow | NỀN | chính workflow đang chạy |
| graphify | user | DÙNG | map cấu trúc/dependency toàn bộ workflow khi tìm chỗ tốn token (đã cân nhắc, không cần chạy thêm ở bước build vì 5 agent đã đọc trực tiếp source đủ chi tiết) |
| claude-api | built-in | DÙNG | tra cứu cơ chế prompt caching/pricing khi đánh giá đề xuất (đã dùng ở mục 5 knowledge) |
| claude-md-management:claude-md-improver | plugin | DÙNG | đối chiếu chuẩn audit CLAUDE.md (tham khảo tiêu chí, không sửa) |
| tavily (tavily-primary MCP, qua agent search-scout) | plugin:tavily | DÙNG | research bên ngoài — đã chạy 4 truy vấn, 12 finding |
| feature-dev:feature-dev, code-review:code-review, remember:doctor, remember:remember, plugin-dev:create-plugin/agent-development/command-development/hook-development/mcp-integration/plugin-settings/plugin-structure/skill-development, agent-sdk-dev:new-sdk-app, hookify:configure/help/hookify/writing-rules/list, skill-creator:skill-creator, frontend-design:frontend-design, playground:playground, mcp-server-dev:build-mcp-app/build-mcp-server/build-mcpb, dataviz, artifact-design/artifact-diagramming/artifact-capabilities, update-config, keybindings-help, simplify, run, init, review, security-review, tavily-cli/crawl/dynamic-search/extract/map/best-practices/tavily-search/tavily-research (skill dạy, không phải MCP tool) | built-in/plugin | KHÔNG | khác lĩnh vực — round chỉ phân tích + viết report, không tạo plugin/hook/skill mới, không sửa code, không cần trực quan hoá |

## 4. Yêu cầu bắt buộc
- Log service bật mặc định: working log ghi timestamp mỗi turn có đổi repo (đã áp dụng
  từ phase analyze, tiếp tục ở phase build).
- Không placeholder: mọi finding trong report phải trỏ file:dòng thật đã audit, không
  suy đoán số liệu chưa đo.
- Đơn vị "test" cho deliverable tài liệu: `doc_lint.py` PASS + checklist đối chiếu DoD
  (không có unit test code vì không sửa code).

## 5. Ràng buộc & rủi ro
| Rủi ro | Ảnh hưởng | Cách giảm |
|---|---|---|
| Danh sách đề xuất quá dài (16 token/time + 5 logic + 9 deferred cũ ≈ 30 mục) khiến report khó đọc | User khó ưu tiên, dễ bỏ sót | Xếp theo ma trận effort/impact, nhóm P0/P1/P2, mỗi mục 1-2 dòng, chi tiết đầy đủ nằm ở knowledge |
| Số đo carry-cost 142,49M (vòng này) không so sánh trực tiếp được với số vòng 1/2 (khác cỡ mẫu session) | Dễ đọc nhầm là "tệ hơn" trong khi chỉ là khác mẫu đo | Ghi rõ trong report đây là số hiện trạng, không phải so sánh before/after; nêu rõ nợ đo lường ở mục 5 knowledge |
| 2 mâu thuẫn luật (G1, G2) chưa có quyết định đúng — nêu ra nhưng chưa chọn hướng sửa | User đọc report thấy vấn đề nhưng chưa có đáp án sẵn để duyệt ngay | Mỗi mâu thuẫn kèm 1 đề xuất hướng sửa cụ thể (không chỉ nêu vấn đề), user quyết ở request triển khai sau |
| `portable/claude-md/CLAUDE.md` chỉ còn ~155 byte trống trước trần `MAX_BYTES=3500` (`tests/test_claude_md_core.py`) | Sửa dòng 41 quá dài → vỡ test, chặn cài lại `~/.claude/CLAUDE.md` | Viết câu thay thế ngắn hơn hoặc bằng câu cũ; đo `wc -c` trước khi cài lại, không cài nếu vượt trần |
| Trần "≤10 dòng" nằm rải ở ≥9 vị trí (2 template, 2 SKILL/04-build, PHASE_TABLE, 2 phases.md sinh tự động, CLAUDE.md, AGENTS.md) — dễ sót 1 chỗ | Convention mới không nhất quán, chỗ còn chỗ mất | Dùng lại đúng danh sách đã `grep` được (mục Đầu ra #4), kiểm lại bằng `grep -rn "≤ *10 dòng"` sau khi sửa xong |

## 6. QC & Definition of Done
| # | Hạng mục kiểm | Lệnh/cách kiểm | Điều kiện PASS |
|---|---|---|---|
| Q1 | Report ngắn gọn, đúng khuôn TDQ | đọc lại bằng mắt (không còn ngưỡng máy đếm dòng) | súc tích, khuyến nghị ~10-20 dòng, không bắt buộc cắt nếu cần thêm để đủ ý |
| Q2 | Report + knowledge qua lint | `python3 scripts/doc_lint.py docs/tdq/reports/2026-08-05-audit-toi-uu-workflow.md docs/tdq/knowledge/2026-08-05-audit-toi-uu-workflow.md docs/tdq/spec/2026-08-05-audit-toi-uu-workflow.md` | exit 0 |
| Q3 | Mọi finding ở knowledge mục 2-4 xuất hiện trong bảng ưu tiên | đối chiếu tay: đếm mục knowledge mục 2-4 (16 token/time + 4 logic + 9 deferred = 29) so với số dòng bảng ưu tiên | không thiếu mục nào (cho phép gộp 2 mục liên quan thành 1 dòng nếu ghi rõ) |
| Q4 | Số liệu trong report khớp số đã đo | đối chiếu report với `knowledge` mục 1 (142.493.808 token, top nhóm) | khớp nguyên văn, không làm tròn sai |
| Q5 | Convention report đã nới đồng bộ, không vỡ test | `python3 -m pytest tests/test_phase_table.py tests/test_claude_md_core.py -q` + `grep -rn "≤ *10 dòng" skills/ portable/ scripts/tdq_state.py` | 2 file test PASS · grep chỉ còn khớp ở chỗ "tóm tắt trong chat" cố tình giữ nguyên (không còn khớp ở report-file) |

DoD: report file tồn tại, ngắn gọn, PASS lint · bảng đề xuất ưu tiên đầy đủ (Q3) xuất
hiện trong chat cuối turn build · convention report đã nới trên mọi vị trí liệt kê ở
mục 2 #4 và Q5 PASS · `spec_file`/`plan_file` đã đăng ký vào state · working log đã
ghi turn build.

## 7. Câu hỏi còn mở
(rỗng)
