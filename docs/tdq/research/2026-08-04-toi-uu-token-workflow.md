# RESEARCH — Tối ưu token/time cho TDQ workflow

## Phần 1 — Đo trên chính transcript của repo này (nguồn nội bộ, đáng tin nhất)

Nguồn: `~/.claude/projects/-Users-truongdinhquoc-Documents-TDQWorkflow/*.jsonl`, 2 session
gần nhất (request `export-claude-setup` + `approval-gate` và `workflow-linh-hoat`).

| Chỉ số | Session A (740 msg) | Session B (331 msg) |
|---|---|---|
| output tokens | 562,883 | 166,977 |
| cache_write | 3,314,123 | 1,012,876 |
| **cache_read** | **91,328,363** | **35,659,037** |
| context TB mỗi API call | ~123k | ~108k |

→ **Mô hình chi phí thật:** `tổng token ≈ Σ (kích thước context) qua từng API call`.
Mỗi tool call = 1 API call = đọc lại TOÀN BỘ context. 1.071 API call cho ~3 request.

### Carry-cost: mỗi output của tool bị mang vác lại ở mọi call sau đó

Công thức: `ký tự/4 × số API call còn lại`. Tổng 70,2M token cache-read đến từ tool output:

| Nhóm | Số lần | Carry-cost (token) |
|---|---|---|
| Read file | 90 | 29,159,282 |
| tavily search (raw result nằm lại context) | 14 | 13,987,211 |
| Bash khác | 157 | 11,990,518 |
| Agent (report subagent) | 6 | 4,520,122 |
| doc_lint | 33 | 2,543,692 |
| `tdq_state.py` (in nguyên JSON 17 trường) | 62 | 2,169,705 |
| Edit (echo lại đoạn diff) | 148 | 2,034,624 |
| chạy full test suite | 42 | 1,819,605 |
| graphify | 12 | 754,972 |
| Write / AskUserQuestion / khác | 64 | 1,259,207 |

Top 5 tool result đắt nhất đều là **đọc lại spec/plan của chính request** (12–16k ký tự
mỗi lần, đọc 3–5 lần) và **kết quả tavily thô** (9–12k ký tự/lần, ở lại đến hết session).

### Chi phí luôn-nạp

| Thứ | Ký tự | ≈ token | × 1.071 call |
|---|---|---|---|
| `~/.claude/CLAUDE.md` | 12,245 | ~3,060 | ~3,28M |
| `tdq-conventions/SKILL.md` | 5,792 | ~1,450 | (khi nạp) |
| `tdq-build/SKILL.md` | 10,936 | ~2,730 | (khi nạp) |
| 16 file references | 50,483 | ~12,600 | (nạp lười, OK) |

### Chi phí THỜI GIAN

- Full test suite: 462 test ≈ 42s/lần × **42 lần** ≈ **29 phút** chỉ chờ test.
- doc_lint 33 lần, graphify 12 lần, mỗi lần vài giây.
- Mỗi gate duyệt = 1 lần chờ người + 1 lần nạp lại context.

## Phần 2 — Research bên ngoài (tavily-primary, 2 truy vấn, 2026-08-04)

| Nguồn | Điều rút ra |
|---|---|
| platform.claude.com — Skill authoring best practices | Chỉ `name`+`description` của skill là luôn nạp (~30–50 token/skill); SKILL.md nạp khi trigger; references nạp khi cần. Giữ SKILL.md < 500 dòng. **Script chạy qua bash không tốn context — chỉ output mới tốn.** |
| medium.com/@cem.karaca (case study) | CLAUDE.md 1.207 dòng = ~42.200 token/hội thoại → đẩy chi tiết sang skill/references còn ~1.900 token: **giảm 94%** phần luôn-nạp. |
| claudefa.st — Context Management | "Context rẻ nhất là context không bao giờ nạp". Giao việc đọc nhiều file cho **subagent** — subagent có context window riêng, chỉ trả về summary. Hay bị compact = task quá to, nên chia nhỏ task chứ không phải cần context lớn hơn. |
| primeline.cc — Stop Wasting Tokens 2026 | Ngưỡng context: <60% chạy bình thường; 60–80% nạp bản tóm tắt thay vì full doc, ưu tiên delegate; >80% dừng nạp, chuẩn bị handoff. Ưu tiên `/compact` hơn `/clear` (giữ prompt cache). |
| institute.sfeir.com | Sub-agent (Task) có context window riêng → context chính nhẹ. PreCompact hook giảm 30% mất mát thông tin khi compact. |
| platform.claude.com cookbook — Context engineering | API có `clear_tool_uses_20250919` (xoá tool result cũ) + `compact_20260112`. Là tính năng tầng API, Claude Code chưa expose cho user config → **không dùng được trực tiếp**, chỉ để tham khảo hướng đi. |

## Phần 3 — Đối chiếu: nguyên nhân gốc trong TDQ workflow

1. **Doc quá nặng và bị đọc lại nhiều lần.** Spec 13,5k + plan 17k ký tự/request; workflow
   bắt đọc lại ở mỗi phase (spec→plan→implement→qc→report).
2. **Mọi thứ chạy trong main context.** Lane full mặc định mode `main`; research, đọc code,
   QC đều nằm trong hội thoại chính thay vì subagent có context riêng.
3. **Kết quả tavily thô ở lại vĩnh viễn** trong context (14M token carry).
4. **CLI ồn:** `tdq_state.py` in nguyên JSON 17 trường ở mọi lệnh (62 lần).
5. **Nghi thức lặp:** full test suite 42 lần thay vì test theo module rồi full 1 lần ở QC.
6. **CLAUDE.md global 12k ký tự** nạp ở mọi turn của MỌI project, kể cả việc không liên quan TDQ.

## Phần 1b — Số đo lặp lại được (`scripts/token_audit.py`)

Lệnh: `python3 scripts/token_audit.py --sessions 2 --top 8` (2026-08-04 22:10). Output thật:

```
# Token audit — 2 session · ~/.claude/projects/-Users-truongdinhquoc-Documents-TDQWorkflow

API call: 1,123 · output: 795,298 · cache_read: 132,613,613 · cache_write: 4,426,599

nhóm                            lần    carry-cost (token)
---------------------------------------------------------
Read file                        92            30,204,230
tavily search                    14            14,270,344
Bash khác                       159            12,709,429
Agent                             6             3,553,132
doc_lint                         37             2,595,470
tdq_state.py (dump JSON)         68             2,286,630
Edit (echo lại diff)            149             2,116,707
chạy test suite                  44             1,991,365
graphify                         12               764,046
Write                            42               577,258
AskUserQuestion                  11               466,766
WebFetch                          1               180,880
ToolSearch                        7                52,553
Skill                            11                48,066
---------------------------------------------------------
TỔNG                            656            72,209,476

# Top 8 tool output đắt nhất
     2,352,350 tok |   13,160 ký tự | Agent          Survey full Claude Code config for export spec
     2,144,880 tok |   15,891 ký tự | Read file      docs/tdq/spec/2026-08-…  (đọc lại spec)
     2,117,367 tok |   12,852 ký tự | Read file      docs/tdq/spec/2026-08-…  (đọc lại spec)
     2,037,666 tok |   11,496 ký tự | tavily search  "Claude Code MCP server configuration…"
     1,973,088 tok |   11,904 ký tự | tavily search  "Claude Code Windows support native…"
     1,944,078 tok |   10,970 ký tự | tavily search  "Claude Code settings.json global v…"
     1,694,510 tok |    9,563 ký tự | tavily search  "Claude Code backup restore migrate…"
     1,617,938 tok |    9,130 ký tự | tavily search  "Claude Code plugin marketplace add…"
```

Đọc bảng: **1 tool output ~12k ký tự phát sinh sớm trong session tốn ~2 TRIỆU token**, vì nó
bị mang vác lại ở mọi API call sau đó. Đây là căn cứ số học cho mọi đề xuất ở nhóm A và B.

## Phần 4 — Xác minh 3 khẳng định bằng nguồn chính thức

Truy vấn qua `tavily-primary`, giới hạn domain `docs.claude.com|platform.claude.com|anthropic.com`.

| # | Khẳng định | Nguồn chính thức | Trích |
|---|---|---|---|
| 1 | Skill nạp theo tầng (progressive disclosure) | https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices | "At startup, the name and description from all Skills' YAML frontmatter are loaded into the system prompt… Files read on-demand… Scripts executed efficiently: only the script's output consumes tokens." |
| 2 | Subagent có context window RIÊNG, chỉ trả summary | https://docs.anthropic.com/en/docs/claude-code/sub-agents | "Each subagent starts with a fresh, isolated context window… Use one when a side task would flood your main conversation with search results, logs, or file contents you won't reference again: the subagent does that work in its own context and returns only the summary." |
| 3 | Thứ gì luôn nằm trong MỌI request | https://docs.anthropic.com/en/docs/claude-code/features-overview | "CLAUDE.md loads at session start and **stays in every request**. MCP tool names load at start with full schemas deferred until use. Skills load descriptions at start, full content on invocation. Subagents get isolated context." |

Hệ quả trực tiếp cho đề xuất:
- Khẳng định 3 xác nhận `CLAUDE.md` là chi phí nhân với MỌI API call → nhóm C có căn cứ.
- Khẳng định 2 xác nhận subagent là công cụ đúng để cắt 30,2M (Read) + 14,3M (tavily) → nhóm B.
- Khẳng định 1 xác nhận **output của script mới tốn token, thân script thì không** → nên đẩy
  logic nặng vào script chạy qua bash và in ít, thay vì để model đọc file rồi tự tính.
