# PLAN — Audit toàn bộ workflow TDQ, đề xuất tối ưu token/thời gian (vòng 3)

Ngày: 2026-08-05 · Spec: ../spec/2026-08-05-audit-toi-uu-workflow.md (bản 1.1, ĐÃ DUYỆT) · Lane: full
Mode thực thi: main — 14 task nhưng phụ thuộc chặt vào 2 nguồn sự thật dùng chung
(`PHASE_TABLE` trong `tdq_state.py` sinh ra 2 file `phases.md`; ngân sách byte
`portable/claude-md/CLAUDE.md` chỉ còn ~155 byte) và vào cùng bộ finding vừa audit —
chia cho subagent sẽ phải đồng bộ lại 2 nguồn này, tốn hơn là làm tuần tự.
(ĐỀ XUẤT, user chốt lúc duyệt)
Trạng thái plan: HOÀN THÀNH (mode main)

## Năng lực → task
(Mỗi dòng DÙNG ở spec §3b phải có mặt ở đây VÀ có khối hợp đồng 6 trường trong task.)

| Skill | Task | Đầu ra bắt buộc |
|---|---|---|
| `claude-api` | T1.1 | mục "## 9. Đề xuất xếp ưu tiên" trong knowledge, có dùng số đơn giá đã tra |
| `tavily (tavily-primary MCP, qua agent search-scout)` | T1.2 | bảng ưu tiên có tham chiếu tới 12 finding research |
| `claude-md-management:claude-md-improver` | T2.4 | `portable/claude-md/CLAUDE.md` dòng 41 đã chấm rubric trước khi cài |
| `graphify` | T3.3 | `graphify-out/graph.json` mtime mới hơn lúc bắt đầu P2 |

## Quy tắc thi hành (áp cho mọi task)
1. Thứ tự phase là thứ tự phụ thuộc — không đảo.
2. Mỗi task: viết test trước (đỏ) → code → test xanh → tick `[x]` NGAY vào file này.
3. Sau mỗi phase: chạy toàn bộ test suite, phải xanh mới sang phase sau.
4. Lệnh nào chạm state của workflow phải có `TDQ_PROJECT_DIR=<thư mục tạm>` ngay trên chính lệnh đó.
5. QC FAIL → thêm task fix vào mục QC của file này (không cần duyệt lại), loop đến khi pass.
6. Không commit/push cho đến khi user yêu cầu.

## P1 — Hoàn thiện report & knowledge (đầu ra #1, #2, #3 spec §2)
- [x] **T1.1** Viết mục `## 9. Đề xuất xếp ưu tiên` vào knowledge: gộp 16 finding
  token/time + 4 issue logic + 9 đề xuất deferred vòng 1/2 (≈29 mục) thành bảng P0/P1/P2.
  Kèm effort ước lượng, dùng ma trận effort/impact đã chốt ở spec §3 —
  Test: `grep -c "## 9. Đề xuất xếp ưu tiên" docs/tdq/knowledge/2026-08-05-audit-toi-uu-workflow.md` trả 1
  - Dùng: `claude-api`
  - Nạp: đã tra cứu ở phase analyze (knowledge mục 5), dùng lại kết quả, không gọi lại.
  - Để: dùng cơ chế/đơn giá prompt caching đã tra để đánh giá impact thực của từng đề xuất.
  - Ra: mục "## 9. Đề xuất xếp ưu tiên" trong `docs/tdq/knowledge/2026-08-05-audit-toi-uu-workflow.md`.
  - Kiểm: `grep -c "## 9. Đề xuất xếp ưu tiên" docs/tdq/knowledge/2026-08-05-audit-toi-uu-workflow.md` trả 1.
  - Không dùng cho: tra cứu giá mới — chỉ dùng lại số đã có ở mục 5.
- [x] **T1.2** Đối chiếu bảng ưu tiên (T1.1) với 12 finding trong
  `docs/tdq/research/2026-08-05-audit-toi-uu-workflow.md`. Đảm bảo mỗi finding research
  có ít nhất 1 dòng tương ứng — Test: đối chiếu tay 12/12 finding có mặt (ghi số finding
  cạnh dòng bảng ưu tiên tương ứng)
  - Dùng: `tavily (tavily-primary MCP, qua agent search-scout)` (mcp)
  - Nạp: đã chạy ở phase analyze qua agent `search-scout`, không gọi lại agent/MCP.
  - Để: đảm bảo 12 finding research ngoài (caching, subagent isolation, sizing…) được
    phản ánh trong đề xuất ưu tiên, không bị bỏ sót.
  - Ra: bảng ưu tiên (T1.1) có cột/ghi chú tham chiếu tới finding research liên quan.
  - Kiểm: đối chiếu tay — 12/12 finding research có mặt trong bảng ưu tiên hoặc knowledge mục 5.
  - Không dùng cho: chạy thêm truy vấn tavily mới trong round này.
- [x] **T1.3** Viết `docs/tdq/reports/2026-08-05-audit-toi-uu-workflow.md`: khuyến nghị
  10-20 dòng (không giới hạn cứng), tóm việc đã làm + số liệu chính + trỏ vào knowledge
  mục 9 — Test: `python3 scripts/doc_lint.py docs/tdq/reports/2026-08-05-audit-toi-uu-workflow.md` exit 0
- [x] **T1.4** Trình bày bảng ưu tiên đầy đủ (T1.1) trong chat cuối turn build — Test:
  đối chiếu tay Q3 spec (đủ 29 mục hoặc bản gộp có ghi rõ)

**Xong P1 khi**: report + mục 9 knowledge tồn tại, `doc_lint.py` PASS trên cả hai.

## P2 — Nới trần report thành convention chung (đầu ra #4 spec §2)
- [x] **T2.1** Sửa `skills/tdq-build/references/report-template.md` và
  `portable/workflow/references/report-template.md`: bỏ câu "≤10 dòng" cứng, thay bằng
  khuyến nghị ngắn gọn ~10-20 dòng — Test: `grep -n "≤10 dòng\|≤ 10 dòng"` trên 2 file
  trả rỗng, `doc_lint.py` trên 2 file exit 0
- [x] **T2.2** Sửa `skills/tdq-build/SKILL.md` (dòng 136, 142) và
  `portable/workflow/04-build.md` (dòng 125, 132) theo cùng câu khuyến nghị — Test:
  `grep -n "≤10 dòng\|≤ 10 dòng"` trên 2 file trả rỗng, `doc_lint.py` trên 2 file exit 0
- [x] **T2.3** Sửa `PHASE_TABLE` trong `scripts/tdq_state.py` (action ~dòng 499 +
  checklist ~dòng 502): đổi mô tả report từ "≤10 dòng" sang "ngắn gọn, khuyến nghị
  10-20 dòng, không giới hạn cứng"; sinh lại `skills/tdq-conventions/references/phases.md`
  (thêm `--plugin-root`) và `portable/workflow/phases.md` bằng lệnh
  `python3 scripts/tdq_state.py phases-doc [--plugin-root] > <file>` — Test:
  `cd tests && python3 -m unittest test_phase_table -v` exit 0
- [x] **T2.4** Sửa `portable/claude-md/CLAUDE.md` dòng 41 (thay "report ≤ 10 dòng" bằng
  câu khuyến nghị, đo `wc -c` không vượt 3500), backup rồi cài `~/.claude/CLAUDE.md` —
  Test: `cd tests && python3 -m unittest test_claude_md_core -v` exit 0, `diff` bản repo
  và bản cài trả rỗng
  - Dùng: `claude-md-management:claude-md-improver`
  - Nạp: gọi skill `claude-md-improver` TRƯỚC khi ghi đè, dùng rubric của nó chấm câu thay thế.
  - Để: đảm bảo câu thay thế không phá cấu trúc/tiêu chí CLAUDE.md và vẫn nằm trong 3.500 byte.
  - Ra: `portable/claude-md/CLAUDE.md` dòng 41 đã sửa + `~/.claude/CLAUDE.md` đã cài,
    backup `~/.claude/CLAUDE.md.bak-<YYYYMMDD-HHMM>`.
  - Kiểm: `cd tests && python3 -m unittest test_claude_md_core -v` exit 0; `wc -c portable/claude-md/CLAUDE.md` ≤ 3500.
  - Không dùng cho: sửa mục nào khác của CLAUDE.md ngoài dòng 41.
- [x] **T2.5** Sửa `portable/AGENTS.md` dòng 13 (sơ đồ pipeline): bỏ `(≤10 dòng)` dưới cột
  Report, thay bằng chú thích ngắn khớp convention mới — Test: `grep -n "≤10 dòng"
  portable/AGENTS.md` trả rỗng

**Xong P2 khi**: `test_phase_table.py` + `test_claude_md_core.py` PASS. Lệnh kiểm gộp:
`grep -rn "≤ *10 dòng" skills/ portable/ scripts/tdq_state.py` — chỉ còn khớp ở
convention "tóm tắt ≤10 dòng trong chat" (quick-lane/status), không còn khớp report-file.

## P3 — Log & test bắt buộc
- [x] **T3.1** Append working log (`docs/workinglog/2026-08-05.md`) cho turn build này
  qua `scripts/tdq_finish.py` — Test: file có entry mới với timestamp turn build
- [x] **T3.2** Chạy toàn bộ unit test suite —
  Test: `cd tests && python3 -m unittest discover -v` 0 fail
- [x] **T3.3** Rebuild code graph (đã đổi `scripts/tdq_state.py` +
  `portable/claude-md/CLAUDE.md`) — Test: `graphify extract . --code-only` exit 0,
  `graphify-out/graph.json` mtime mới hơn lúc bắt đầu P2
  - Dùng: `graphify`
  - Nạp: kiểm `graphify --version` trước; thiếu thì báo user, không tự cài.
  - Để: dựng lại graph sau khi sửa `tdq_state.py` và cấu trúc CLAUDE.md.
  - Ra: `graphify-out/graph.json` và `graphify-out/GRAPH_REPORT.md` mới.
  - Kiểm: `graphify extract . --code-only` exit 0.
  - Không dùng cho: phân tích doc trong `docs/` hay `skills/`.
- [x] **T3.4** Lint toàn bộ file đã sửa/tạo — Test: `python3 scripts/doc_lint.py docs/tdq/reports/2026-08-05-audit-toi-uu-workflow.md docs/tdq/knowledge/2026-08-05-audit-toi-uu-workflow.md docs/tdq/spec/2026-08-05-audit-toi-uu-workflow.md skills portable` exit 0
- [x] **T3.5** Xác nhận không sót vị trí trần cũ —
  Test: `grep -rn "≤ *10 dòng" skills/ portable/ scripts/tdq_state.py` chỉ khớp ở
  convention "tóm tắt trong chat" cố tình giữ

**Xong P3 khi**: suite xanh, `doc_lint` exit 0 trên mọi file đã sửa, grep xác nhận Q5 spec PASS.

## Definition of Done
Trỏ spec §6:
- Q1 report ngắn gọn, đúng khuôn — đọc lại bằng mắt sau T1.3.
- Q2 report + knowledge + spec qua lint — T3.4.
- Q3 mọi finding ở knowledge mục 2-4 xuất hiện trong bảng ưu tiên — T1.1/T1.2/T1.4.
- Q4 số liệu report khớp số đã đo (142.493.808 token, top nhóm) — đối chiếu tay khi viết T1.3.
- Q5 convention report đã nới đồng bộ, không vỡ test — T2.3/T2.4/T3.2/T3.5.
