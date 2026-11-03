# KNOWLEDGE — Siết QC và vòng fix cho lane quick

Ngày: 2026-08-07 · Request: ../requests/2026-08-07-siet-qc-lane-quick.md · Lane: full
Hỏi–đáp: ../questions/2026-08-07-siet-qc-lane-quick.md (2 vòng, 12 câu, hết chỗ đoán)

## Năng lực dùng được

Phân vân → DÙNG. Không xoá bảng này kể cả khi mọi dòng là KHÔNG.

| Skill | Nguồn | Phán quyết | Dùng ở đâu / Lý do loại |
|---|---|---|---|
| tdq-intake, tdq-spec, tdq-plan, tdq-build, tdq-conventions, tdq-status | plugin:tdq-workflow | NỀN | chính workflow đang chạy — và cũng là đối tượng bị sửa |
| test-driven-development | plugin:superpowers | DÙNG | task sửa `tdq_state.py` + luật red→green: viết test parity thấy đỏ trước khi sửa văn bản |
| verification-before-completion | plugin:superpowers | DÙNG | trước khi khai QC PASS: chạy thật `python3 -m unittest` và dán số liệu |
| skill-creator | plugin:skill-creator | DÙNG | sửa `skills/tdq-intake/**` — soi lại shape/description sau khi thêm luật QC |
| graphify | user | NỀN | `tdq_finish.py` tự chạy `graphify extract . --code-only` cuối turn |
| 34 skill data-engineering, 25 huggingface-skills, 19 hyperframes, 13 datarobot, 12 qt-development, 12 figma, 11 postman, 11 cloudflare, 10 firecrawl, 9 sonarqube, 8 tavily, 7 mongodb, 7 adobe, 6 desktop-commander, 6 chrome-devtools-mcp, 6 canva, 5 base44, 3 unreal, 3 mcp-server-dev, 2 lumen, 1 playground, 1 remember, 1 hookify, 1 frontend-design, 1 claude-md-management, figma-implement, mem0-memory, unity-mcp-orchestrator | nhiều nguồn | KHÔNG | khác lĩnh vực |
| 11 skill plugin-dev + 8 skill superpowers còn lại (brainstorming, writing-plans, executing-plans, systematic-debugging, requesting/receiving-code-review, dispatching-parallel-agents, using-git-worktrees…) | plugin:plugin-dev, plugin:superpowers | KHÔNG | spec §3 đã chọn cách khác tốt hơn — TDQ workflow tự lo phần plan/review/worktree tương ứng |

Tổng kiểm kê: 248 skill trên đĩa (`scripts/skill_inventory.py`), 32 nguồn.

## Quyết định đã chốt (12/12 câu, không còn chỗ đoán)

1. **QC quick = 3 hạng mục** (nhẹ hơn 6 hạng mục của `tdq-build/references/qc.md`):
   - Q1: test của TỪNG task pass (đã chạy thật, có output)
   - Q2: đối chiếu TỪNG dòng Definition of Done → PASS/FAIL kèm bằng chứng
   - Q3: biên & đường lỗi cơ bản — input rỗng, input sai kiểu, file thiếu
   Bỏ khỏi quick: full suite toàn repo · log service · không-placeholder · hợp đồng skill
   `Dùng:/Kiểm/Ra`.
2. **Bằng chứng ghi vào chính `docs/tdq/plan/<slug>.md`**, mục `## QC` append ở cuối.
   KHÔNG tạo `docs/tdq/qc/<slug>.md` — quick vẫn là "gộp 1 file".
3. **Ép red → green** ở quick giống full: check phải FAIL trước, rồi code, rồi pass.
4. **Vòng fix: trần 3 vòng.** FAIL → thêm task fix vào chính plan dưới `## QC vòng N — fix`
   theo khuôn `- [ ] **QCn.1** <việc> — Test: <check>`, không cần duyệt lại. Vượt 3 vòng →
   DỪNG, báo user kèm chẩn đoán và đề xuất chuyển lane full.
5. **Quick external FAIL** → vòng fix do hội thoại chính tự làm, KHÔNG giao lại engine đã fail.
6. **Ép bằng máy** chỉ ở 4 nguồn sự thật văn bản + test parity. KHÔNG thêm rule
   `doc_lint.py`, KHÔNG chạm `hooks/scripts/stop_gate.py`.
7. **QC mặc định BẬT, user opt-out có chủ đích:** gate duyệt quick có thêm biến thể
   `"duyệt quick không QC"`. Nhắn `"duyệt quick"` trơn (hoặc im lặng về QC) = CÓ QC.
8. **Vòng fix KHÔNG opt-out được:** kể cả khi user bỏ QC, test đỏ hoặc bug phát hiện được
   thì vẫn bắt buộc fix, vẫn trần 3 vòng.
9. **Bỏ QC vẫn để lại dấu vết:** mục `## QC` trong plan có đúng 1 dòng
   `BỎ theo yêu cầu user: "<nguyên văn câu user>"`.

## Ràng buộc kỹ thuật (đã xác minh bằng đọc code)

**4 nguồn sự thật phải sửa đồng bộ — lệch một chỗ là hỏng âm thầm:**

| # | File | Chỗ hiện tại |
|---|---|---|
| N1 | `skills/tdq-intake/references/quick-lane.md:14` | bảng: `| QC | file qc/<slug>.md | validate ngay trong turn implement |` |
| N2 | `skills/tdq-intake/SKILL.md` Phần C bước 4 + 7 | dòng `➤ Duyệt` (thêm biến thể) và "chạy validate" |
| N3 | `scripts/tdq_state.py` `PHASE_TABLE["quick"]` (~dòng 529-551) | checklist "Implement + validate", `done_when`, `forbidden` |
| N4 | `portable/workflow/references/quick-lane.md` + `portable/workflow/phases.md` | bản mirror cho agent chạy ngoài Claude Code |

**Test đang canh, phải giữ xanh:**
- `tests/test_portable_sync.py` — parity từng bước skills↔portable sau chuẩn hoá; sửa N1/N2
  mà không sửa N4 là đỏ ngay.
- `tests/test_phase_table.py` — `PHASE_TABLE` là nguồn sự thật duy nhất, doc `phases.md`
  (cả 2 bản) phải khớp; mọi row phải đủ 6 key.
- `tests/test_state.py`, `tests/test_next.py` — `approve quick` và output `next`.
- `scripts/doc_lint.py` R6: trần dòng `tdq-intake/SKILL.md` = 120 (hiện **84**, còn dư 36).
  R4 cấm từ mơ hồ → câu luật mới phải nêu điều kiện cụ thể, không được viết "nếu cần".
- `quick-lane.md` không có trần R6 riêng (chỉ `MAX_LINES_ANY = 500`, hiện 49 dòng).

**Ràng buộc CLI:** `scripts/tdq_state.py` đã có `approve quick --mode external`. Biến thể
"không QC" cần một cách lưu state — hiện `state.json` không có field nào cho nó (xem
phương án ở spec §3).

## Cách tiếp cận đã chọn

Sửa văn bản luật ở 4 nguồn + thêm field state cho opt-out + test parity khẳng định 4 nguồn
khớp nhau. Không thêm rule lint, không thêm hook — theo đúng đáp câu 6.

## Phương án đã loại

- **Thêm rule `doc_lint.py` soi plan quick phải có `## QC`** — loại: chỉ soi được SAU khi
  implement xong, không chặn được hành vi "quên QC" đúng lúc; user chọn A câu 6.
- **Chặn ở `stop_gate.py`** — loại: cùng lý do; thêm nữa stop_gate đang là chỗ nhiều luật,
  thêm điều kiện lane-quick làm nó khó bảo trì.
- **Nạp thẳng `tdq-build/references/qc.md` cho quick** — loại: 6 hạng mục quá nặng, mất
  tính "nhẹ hơn full" mà user yêu cầu (đáp 1A loại thẳng phương án D).
- **Tạo file `docs/tdq/qc/<slug>.md` rút gọn cho quick** — loại: phá nguyên tắc "quick gộp
  1 file" (đáp 2A loại phương án C).

## Lộ trình

Khung bất biến: phân tích → spec/plan → implement → report.

| Bước/phase | CÓ-BỎ | Vì sao |
|---|---|---|
| Phân tích (B0-B6) | CÓ | đã xong: kiểm kê 248 skill, đọc 4 nguồn sự thật + 5 file test, 2 vòng interview |
| Research web (B3) | BỎ | thuần nội bộ — không có ẩn số thư viện/API/phiên bản bên ngoài |
| Deep search | BỎ | không đạt tiêu chí (không có ẩn số ngoài nào) |
| Spec + duyệt | CÓ | sửa luật lõi của workflow, sai là lan ra mọi request quick sau này |
| Plan + duyệt kèm mode | CÓ | khung bất biến |
| Implement | CÓ | khung bất biến |
| Chia subagent | BỎ | 6-8 file, sửa liên đới chặt (4 nguồn phải khớp từng chữ) — chia ra dễ lệch hơn là làm tuần tự |
| QC file `qc/<slug>.md` | CÓ | lane full, và chính request này nói về QC nên phải làm mẫu mực |
| QC độc lập bằng agent `tdq-qc-tester` | CÓ | rẻ, và đây là loại thay đổi mà tự-kiểm dễ thiên vị (tự viết luật rồi tự bảo đã khớp) |
| Review sâu bằng `tdq-reviewer` | CÓ | review spec+plan trước khi build — sửa luật workflow, mâu thuẫn nội bộ là rủi ro lớn nhất |
| Report | CÓ | khung bất biến |

## Kiểm cổng

1. **Phạm vi cuối đã rõ chưa?** Rõ. Ra: 4 nguồn sự thật văn bản được sửa (N1-N4) + field
   state cho opt-out QC + test parity mới. Cái mới: lane quick có QC 3 hạng mục mặc định
   bật + vòng fix bắt buộc trần 3 vòng + biến thể duyệt `"duyệt quick không QC"`.
2. **Có cần model / download / cài đặt gì không?** Không. Chỉ Python 3.12 sẵn có và
   `unittest` trong repo.
3. **Phạm vi QC/test/validate đã có chưa?** Có: `python3 -m unittest discover tests` toàn
   bộ phải xanh (mốc hiện tại cần đo lại trước khi sửa), `python3 scripts/doc_lint.py
   skills portable` exit 0, cộng test parity mới cho 4 nguồn.
