# KNOWLEDGE — Tối ưu token/time cho TDQ workflow

Request: ../requests/2026-08-04-toi-uu-token-workflow.md · Research: ../research/2026-08-04-toi-uu-token-workflow.md

## Quyết định đã chốt

1. Đầu ra = **1 file đề xuất** (báo cáo phân tích + danh sách giải pháp tới mức task, có ước
   lượng tiết kiệm và thứ tự ưu tiên). **Không sửa code/skill trong request này.**
2. Được phép đề xuất cắt gọn `~/.claude/CLAUDE.md` xuống phần lõi, đẩy chi tiết vào skill.
3. Được phép đề xuất cả 4 hướng nới nghi thức: test theo module, gộp doc, đẩy việc đọc nặng
   sang subagent, CLI im lặng.
4. Không hy sinh: 2 gate duyệt, red→green, tick ngay, bằng chứng QC, working log.

## Mô hình chi phí (nền tảng mọi đề xuất)

```
tổng token ≈ Σ (kích thước context tại mỗi API call)
           = (số API call) × (context nền + Σ tool output đã tích luỹ)
```

Hệ quả: một output tool 10k ký tự ở đầu session không tốn 2,5k token — nó tốn
`2,5k × số API call còn lại`. Đo thật: 70,2M / 127M token cache-read là carry-cost của
tool output. Vậy có ba đòn bẩy, theo đúng thứ tự hiệu quả:

| Đòn bẩy | Cách | Ảnh hưởng đo được |
|---|---|---|
| L1. Giảm thứ ở lại context | subagent, CLI im lặng, đọc từng phần | ~70M |
| L2. Giảm số API call | gộp lệnh Bash, gộp Edit, bớt lần chạy test | nhân tử của mọi thứ |
| L3. Giảm context nền | CLAUDE.md gọn, skill/references nạp lười | ~3k token × mọi call |

## Nguyên nhân gốc đã xác định (kèm số đo)

| # | Nguyên nhân | Số đo |
|---|---|---|
| N1 | Đọc lại spec/plan ở mỗi phase (12–17k ký tự/lần) | 29,2M carry |
| N2 | Kết quả tavily thô nằm lại context vĩnh viễn | 14,0M carry |
| N3 | Bash ồn (`grep -A5 -B5`, `wc` cả cây, cat file) | 12,0M carry |
| N4 | `tdq_state.py` in nguyên JSON 17 trường mỗi lệnh, 62 lệnh | 2,2M carry |
| N5 | Full test suite 462 test chạy 42 lần | 1,8M carry + **~29 phút** |
| N6 | `doc_lint` in cả khi pass, 33 lần | 2,5M carry |
| N7 | CLAUDE.md 12.245 ký tự nạp mọi turn của MỌI project | ~3k token/call |
| N8 | 8 file doc/request, spec 112 dòng + plan 121 dòng | output token đắt nhất/đơn vị |
| N9 | Mode `main` mặc định: research + đọc code đều trong context chính | gốc của N1–N3 |
| N10 | Compaction giữa request → đọc lại file đã đọc | lặp lại N1 |

## Năng lực dùng được

| Skill | Nguồn | Phán quyết | Dùng ở đâu / Lý do loại |
|---|---|---|---|
| tdq-intake | plugin:tdq-workflow | NỀN | skill khung đang chạy |
| tdq-spec | plugin:tdq-workflow | NỀN | skill khung đang chạy |
| tdq-plan | plugin:tdq-workflow | NỀN | skill khung đang chạy |
| tdq-build | plugin:tdq-workflow | NỀN | skill khung đang chạy |
| tdq-conventions | plugin:tdq-workflow | NỀN | skill khung đang chạy |
| tdq-status | plugin:tdq-workflow | KHÔNG | trùng chức năng |
| claude-md-improver | plugin:claude-md-management | DÙNG | soi CLAUDE.md để đề xuất bản cắt gọn (đề xuất N7) |
| update-config | built-in | KHÔNG | request này không sửa cấu hình |
| graphify | user | KHÔNG | không đổi code |
| skill-creator | plugin:skill-creator | KHÔNG | không tạo skill mới lần này |
| remember | plugin:remember | KHÔNG | khác lĩnh vực |
| tavily-search | plugin:tavily | DÙNG | research đã chạy 2 truy vấn |
| tavily-research / crawl / map / extract / cli / dynamic-search / best-practices | plugin:tavily | KHÔNG | trùng chức năng |
| claude-code-guide (agent) | built-in | KHÔNG | đã có nguồn doc chính thức từ research |
| các skill còn lại (frontend-design, hookify, mcp-server-dev ×3, playground, plugin-dev ×6, datarobot…) | plugin | KHÔNG | khác lĩnh vực |

## Lộ trình

| Bước/phase | Chạy? | Vì sao |
|---|---|---|
| Research web | **CÓ** (đã xong) | cần chuẩn chính thức về progressive disclosure + context management |
| Interview | **CÓ** (đã xong, 2 vòng) | đầu ra và mức đánh đổi chỉ user quyết được |
| Spec | **CÓ** (rút gọn ≤80 dòng) | user cần duyệt phạm vi đề xuất trước khi tôi viết |
| Plan | **CÓ** (rút gọn) | user muốn "plan sẵn để duyệt sau" |
| Implement | **CÓ** — nhưng chỉ viết 1 file đề xuất | không sửa code/skill lần này |
| Sub-agent / mode external | **BỎ** | việc là viết 1 file, chia ra tốn hơn tiết kiệm |
| QC agent độc lập (`tdq-qc-tester`) | **BỎ** | không có code để test độc lập |
| Full test suite 462 test | **BỎ** | không đụng file code; chỉ chạy `doc_lint` |
| graphify rebuild | **BỎ** | không đổi code |
| Report | **CÓ** (≤50 dòng) | khung bất biến |

## Cách tiếp cận đã chọn

Đề xuất chia **5 nhóm** theo đúng 3 đòn bẩy, mỗi nhóm có task cụ thể + ước lượng tiết kiệm
+ rủi ro. Xếp ưu tiên theo `tiết kiệm / công sức`, để user chọn làm nhóm nào trước.

**Đã loại:** viết công cụ đo token tự động (over-engineering — script phân tích jsonl đã
chạy được ad-hoc); dùng `clear_tool_uses` của API (Claude Code chưa expose cho user).

## Nguồn

- Transcript nội bộ `~/.claude/projects/-Users-truongdinhquoc-Documents-TDQWorkflow/*.jsonl`
- platform.claude.com — Skill authoring best practices; cookbook Context engineering
- medium.com/@cem.karaca — case study CLAUDE.md 42k→1,9k token
- claudefa.st, primeline.cc, institute.sfeir.com — context management 2026
