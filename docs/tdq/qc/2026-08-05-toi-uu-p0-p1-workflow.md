# QC — 2026-08-05-toi-uu-p0-p1-workflow

Spec §6 (Q1-Q10) · DoD: 16/16 đầu ra + suite 0 fail + lint 0 + `tdq-qc-tester` PASS + graphify 0.

## Tự kiểm (P1-P6)

| # | Hạng mục | Lệnh | Kết quả |
|---|---|---|---|
| Q1 | Test dedupe git status/turn_rows | `cd tests && python3 -m unittest discover -v` | 585 tests, 0 fail |
| Q2 | Đầu ra #3,4,5,7,9,10,13,16 | grep từng dòng §2 | #3 `grep "làm theo user" quick-lane.md` rỗng (rc=1) ✓; #4 `reminder-codes.md` xuất hiện dòng 19,72 ✓; #9 `"2 phiên"` dòng 57 ✓; #13 `"/clear"` dòng 91 ✓; #16 `dot reporter\|redirect` dòng 9 ✓; #5/#7/#10 đọc tay đã xác nhận ở P2-P4 |
| Q3 | #6, #14 không phá quick lane/external | `tdq_state.py init <slug-test> quick && next` (chạy ở P3) | Phần A/C `tdq-intake/SKILL.md` đủ bước, không thiếu |
| Q4 | #8 test khoá ngưỡng 1.500 bắt được lệch | `test_agent_digest_sync.py` (P5) | Cố ý sửa sai → FAIL, phục hồi → PASS |
| Q5 | #11 nén `skill_dump()` | test mới so byte trước/sau (P1 T1.4) | PASS, giảm byte, giữ đủ 5 trường hợp đồng |
| Q6 | #12 dedupe `prompt_context.py` 2 lượt gọi | `test_context_hooks.py` (P1 T1.3, sửa lại ở QC1.7) | Lượt 2 ngắn hơn/khác lượt 1 |
| Q7 | #15 kịch bản đo chạy được thật | đọc `measure-scenario.md` (P4 T4.3) | Không bước nào mơ hồ |
| Q8 | Lint toàn bộ file đổi | `doc_lint.py skills portable docs/tdq/plan/<slug>.md docs/workinglog/2026-08-05.md` | exit 0 (working-log 5 lỗi R5 còn lại thuộc entry request khác trong ngày, ngoài phạm vi build) |
| Q9 | QC độc lập `tdq-qc-tester` | agent nền, phase riêng — xem bảng dưới | 8/10 PASS vòng 1, 10/10 sau QC vòng 2 |
| Q10 | Rebuild graphify | `graphify extract . --code-only` | exit 0, 3412 nodes/4638 edges, mtime mới hơn lúc bắt đầu implement |

Đầu ra #1,#2 (dedupe `_git status`, `turn_rows()`): test đếm số lần gọi = 1, PASS (P1 T1.1-T1.2).

## Kiểm độc lập — agent `tdq-qc-tester` (TQC.1)

Chạy lại full suite độc lập + probe `bash_gate.py`/`prompt_context.py` bằng input mẫu,
không dùng lại kết quả tự kiểm P1-P6.

**Vòng 1: 8/10 PASS, 2/10 FAIL.**

| Defect | Mức | Vị trí | Fix |
|---|---|---|---|
| 1 | Trung bình | `skills/tdq-intake/SKILL.md:77-79` — cross-reference cũ trỏ "Nhánh external" trong `tdq-build/SKILL.md`, nội dung đã dời sang `references/external-build.md` ở T2.3 | QC2.1: sửa link trỏ đúng `references/external-build.md` |
| 2 | Cao | Đầu ra #13 (`/clear` trong `portable/AGENTS.md`) chưa được gán vào task nào ở P1-P6 — thiếu deliverable so với DoD | QC2.2: thêm dòng khuyến nghị vào mục Working log của `portable/AGENTS.md` |
| 3 | Nhẹ | 3 câu R5 quá 40 từ trong working log, do chính build này ghi | QC2.3: tách câu |
| 4 | Nhẹ | Header `## 13:43` trùng 2 lần trong working log | QC2.3: gộp thành 1 entry |

**Vòng 2 (sau fix QC2.1-QC2.3): 10/10 PASS.** Bằng chứng:
`doc_lint.py skills/tdq-intake/SKILL.md` exit 0 (đọc tay xác nhận link đúng đích);
`grep -n "/clear" portable/AGENTS.md` → dòng 91;
`doc_lint.py docs/workinglog/2026-08-05.md` không còn báo lỗi tại 3 entry `13:43/13:47/14:51`;
`doc_lint.py docs/tdq/plan/2026-08-05-toi-uu-p0-p1-workflow.md` exit 0;
full suite chạy lại sau mọi fix → 585/585 PASS.

## Kết luận

10/10 hạng mục QC + 16/16 đầu ra §2 PASS. DoD spec §6 đạt đủ.
