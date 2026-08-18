# SPEC — TDQ workflow là default tuyệt đối + bỏ mục superpower (mục 5 cũ)

<!-- doc-lint: allow R10 — spec viết trước khi có luật ranh giới module -->

Ngày: 2026-08-02 · Bản: 1.1 · Request: ../requests/2026-08-02-tdq-default-cleanup.md · Lane: full
Trạng thái: CHỜ DUYỆT

## 1. Mục tiêu & phạm vi
- Mục tiêu: mọi prompt mới (kể cả câu hỏi thuần giải đáp) đều đi qua tdq-intake, bằng 3 tầng: instruction user-level, description skill, hook deterministic. Đồng thời xóa trọn §5 "superpower" khỏi CLAUDE.md user-level.
- Trong phạm vi:
  - Sửa `~/.claude/CLAUDE.md`: xóa §5, viết lại đầu §10 thành luật "MỌI prompt mới", đánh số lại các mục.
  - Sửa `skills/tdq-intake/SKILL.md`: description + mở đầu Phần A nêu rõ áp cho cả câu hỏi/check/việc nhỏ.
  - Sửa `hooks/scripts/prompt_context.py`: in nhắc `[TDQ:INTAKE]` khi KHÔNG có request mở. Định nghĩa đóng: request mở = có `active_request` VÀ `phase != idle`; 3 case bắn nhắc = state None / thiếu active_request / phase idle (kể cả khi còn active_request).
  - Test mới cho nhánh hook + cập nhật test shape nếu đụng.
- NGOÀI phạm vi: không đổi stop_gate, không đổi lane-decision, không đổi các skill tdq khác, không sửa CLAUDE.md project, không bump version (chờ user quyết khi commit).

### 1b. Mapping số mục CLAUDE.md (cũ → mới, sau khi xóa §5)
| Cũ | Mới | Tên mục |
|---|---|---|
| 1–4 | 1–4 | giữ nguyên |
| 5 (superpower) | — | xóa trọn |
| 6 | 5 | Logging khi phát triển |
| 7 | 6 | Working log theo ngày |
| 8 | 7 | Xử lý issue/lỗi |
| 9 | 8 | Checklist khi lập spec |
| 10 | 9 | TDQ Workflow |
| 11 | 10 | Năng lực & plugin |

Tham chiếu phải quét sửa: "§10"/"mục 10" (repo: skills, docs; ngoài repo: ~/.claude/CLAUDE.md tự trỏ), "§5". Docs lịch sử trong docs/tdq/{qc,reports,spec,plan} của request cũ giữ nguyên (bản ghi thời điểm), chỉ sửa file đang sống: skills/, portable/, CLAUDE.md, knowledge/spec của request này.

## 2. Đầu ra cụ thể
| # | Đầu ra | Đường dẫn/vị trí | Đo "xong" bằng |
|---|---|---|---|
| 1 | CLAUDE.md không còn §5, §10 (số mới) mở đầu bằng luật "MỌI prompt mới → tdq-intake" | ~/.claude/CLAUDE.md | `grep -c superpower` = 0; grep thấy cụm "MỌI prompt mới"; đánh số mục liên tục |
| 2 | Description tdq-intake liệt kê trigger cả câu hỏi/check nhỏ | skills/tdq-intake/SKILL.md | grep thấy "kể cả câu hỏi" trong frontmatter; doc_lint exit 0 |
| 3 | Hook in `[TDQ:INTAKE]` khi chưa có request mở | hooks/scripts/prompt_context.py | unit test 4 case (no state / no active / idle-còn-active / phase khác idle không bắn) pass; chạy tay hook với state idle thấy [TDQ:INTAKE] |
| 4 | Test mới red→green | tests/test_prompt_context.py (file chốt duy nhất, 4 case) | `python3 -m unittest discover -s tests` toàn suite pass |

## 3. Cách tiếp cận & lý do
- Chọn: 3 tầng instruction + description + hook; hook là tầng bắt buộc vì UserPromptSubmit chạy trước model mỗi prompt.
- Vì: research xác nhận instruction/description là xác suất, model có thể bỏ qua khi context dài; hook deterministic ("skill makes competent, hook makes accountable") — nguồn trong research/2026-08-02-tdq-default-cleanup.md.
- Đã loại: chỉ instruction (không hook) — không đảm bảo; giữ một phần §5 — trùng plugin, user chốt bỏ trọn.

## 3b. Năng lực & công cụ
| Skill | Nguồn | Phán quyết | Dùng ở đâu / Lý do loại |
|---|---|---|---|
| tdq-intake | plugin:tdq-workflow | NỀN | skill khung của request này, đồng thời là file bị sửa |
| tdq-spec | plugin:tdq-workflow | NỀN | đang chạy để viết spec này |
| tdq-plan | plugin:tdq-workflow | NỀN | phase kế tiếp |
| tdq-build | plugin:tdq-workflow | NỀN | phase thực thi |
| tdq-conventions | plugin:tdq-workflow | NỀN | quy ước chung |
| tdq-status | plugin:tdq-workflow | KHÔNG | khác lĩnh vực |
| doc_lint (script) | project | DÙNG | validate SKILL.md, spec, plan sau sửa |
| unittest suite | project | DÙNG | test hook mới + toàn suite 367 |
| tavily-search | plugin:tavily | DÙNG | đã dùng ở analyze (2 truy vấn), không cần thêm |
| tavily-best-practices | plugin:tavily | KHÔNG | khác lĩnh vực |
| tavily-cli | plugin:tavily | KHÔNG | khác lĩnh vực |
| tavily-crawl | plugin:tavily | KHÔNG | khác lĩnh vực |
| tavily-dynamic-search | plugin:tavily | KHÔNG | khác lĩnh vực |
| tavily-extract | plugin:tavily | KHÔNG | khác lĩnh vực |
| tavily-map | plugin:tavily | KHÔNG | khác lĩnh vực |
| tavily-research | plugin:tavily | KHÔNG | khác lĩnh vực |
| graphify | user | DÙNG | cuối turn build chạy `graphify extract . --code-only` theo mục TDQ Workflow của CLAUDE.md |
| claude-md-improver | plugin:claude-md-management | KHÔNG | spec §3 đã chọn cách khác tốt hơn — sửa theo quyết định đã chốt, không audit tổng |
| revise-claude-md | plugin:claude-md-management | KHÔNG | spec §3 đã chọn cách khác tốt hơn — sửa trực tiếp theo quyết định |
| skill-creator | plugin:skill-creator | KHÔNG | spec §3 đã chọn cách khác tốt hơn — sửa tay theo chuẩn từ research |
| skill-development | plugin:plugin-dev | KHÔNG | spec §3 đã chọn cách khác tốt hơn — sửa tay theo chuẩn từ research |
| hook-development | plugin:plugin-dev | KHÔNG | spec §3 đã chọn cách khác tốt hơn — hook có sẵn, chỉ thêm nhánh nhỏ |
| agent-development | plugin:plugin-dev | KHÔNG | khác lĩnh vực |
| command-development | plugin:plugin-dev | KHÔNG | khác lĩnh vực |
| mcp-integration | plugin:plugin-dev | KHÔNG | khác lĩnh vực |
| plugin-settings | plugin:plugin-dev | KHÔNG | khác lĩnh vực |
| plugin-structure | plugin:plugin-dev | KHÔNG | khác lĩnh vực |
| create-plugin | plugin:plugin-dev | KHÔNG | khác lĩnh vực |
| frontend-design | plugin:frontend-design | KHÔNG | khác lĩnh vực |
| playground | plugin:playground | KHÔNG | khác lĩnh vực |
| build-mcp-app | plugin:mcp-server-dev | KHÔNG | khác lĩnh vực |
| build-mcp-server | plugin:mcp-server-dev | KHÔNG | khác lĩnh vực |
| build-mcpb | plugin:mcp-server-dev | KHÔNG | khác lĩnh vực |
| writing-hookify-rules | plugin:hookify | KHÔNG | spec §3 đã chọn cách khác tốt hơn — hook plugin tự quản, không qua hookify |
| remember | plugin:remember | KHÔNG | khác lĩnh vực — chạy nền tự động, không gọi chủ động |

## 4. Yêu cầu bắt buộc
- Hook giữ nguyên log/sổ turn hiện có; dòng mới đi qua `_emit` (tôn trọng MAX_CHARS).
- Không placeholder; dòng `[TDQ:INTAKE]` wording dạng: "chưa có request mở — nếu prompt KHÔNG thuộc vòng intake đang dở thì mở tdq-intake trước khi làm gì khác" (tránh mở request lồng khi user đang trả lời câu hỏi lane/interview lúc state chưa init).
- Dòng `[TDQ:INTAKE]` ≤ 160 ký tự, có unit test độ dài — vì `_truncate` cắt toàn output ở MAX_CHARS, không được để cụt câu lệnh nhắc.
- Nhánh hook mới có unit test riêng, chạy bằng `python3 -m unittest discover -s tests`.

## 5. Ràng buộc & rủi ro
| Rủi ro | Ảnh hưởng | Cách giảm |
|---|---|---|
| Nhắc [TDQ:INTAKE] bắn cả với prompt trong luồng đang mở | vòng intake thừa | chỉ bắn khi state None / không active_request / phase idle |
| Xóa §5 làm mất luật chưa có trong plugin | hành vi tụt chuẩn | đã đối chiếu: mọi ý §5 đều có trong tdq-plan/tdq-build/§10; ghi đối chiếu vào QC |
| CLAUDE.md đánh số lại làm lệch tham chiếu "§10" ở nơi khác | tham chiếu gãy | grep toàn repo + CLAUDE.md tìm "§10"/"§5" và sửa theo số mới |
| Sửa nhầm làm hook crash → mất luôn [TDQ:NEXT] | workflow mù state | test 4 case + chạy tay hook trước khi kết thúc build |
| ~/.claude/CLAUDE.md nằm NGOÀI repo, không có git để rollback | mất nội dung nếu sửa hỏng | backup nguyên văn vào docs/tdq/qc/claude-md-backup-2026-08-02.md TRƯỚC khi sửa; dán đối chiếu §5→plugin vào file QC |

## 6. QC & Definition of Done
| # | Hạng mục kiểm | Lệnh/cách kiểm | Điều kiện PASS |
|---|---|---|---|
| Q1 | Toàn suite test | `python3 -m unittest discover -s tests` | OK, 0 fail; có test mới cho [TDQ:INTAKE] |
| Q2 | Lint docs | `doc_lint.py` trên SKILL.md intake + spec + plan (`--pair`) | exit 0 |
| Q3 | CLAUDE.md sạch §5 | `grep -ci superpower ~/.claude/CLAUDE.md` | 0 |
| Q4 | Luật MỌI prompt | grep "MỌI prompt mới" ~/.claude/CLAUDE.md + frontmatter intake có "kể cả câu hỏi" | cả hai khớp |
| Q5 | Hook chạy thật | echo payload từng case vào `prompt_context.py` | state None hoặc thiếu active_request: chỉ [TDQ:INTAKE]; phase idle: [TDQ:NEXT] + [TDQ:INTAKE]; phase khác idle (request mở): KHÔNG có [TDQ:INTAKE] |
| Q6 | Tham chiếu số mục + đánh số liên tục | grep từng tham chiếu cũ theo bảng mapping §1b (repo + ~/.claude/CLAUDE.md + docs của request này) và `grep -E '^## [0-9]+\.' ~/.claude/CLAUDE.md` | mỗi tham chiếu cũ = 0 kết quả; dãy số mục là 1..10 liên tục |

DoD: Q1–Q6 PASS; working log ghi đủ; đối chiếu §5→plugin nằm trong file QC.

## 7. Câu hỏi còn mở
(RỖNG)
