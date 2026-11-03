# PLAN — Cập nhật đầy đủ các đề xuất kiến trúc tối ưu instruction và lazy load vào TDQ Workflow

Ngày: 2026-10-15 · Spec: ../spec/2026-10-15-1425-cap-nhat-full-de-xuat-instruction.md (bản 1.0, ĐÃ DUYỆT) · Lane: full
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md
Mode thực thi: main — các task trải dài từ tài liệu, rule, hook tới script kiểm thử; thực thi tuần tự trong main session bảo đảm tính nhất quán và kiểm soát token chặt chẽ.
Trạng thái plan: HOÀN THÀNH

## Mục lục

- Quy tắc thi hành (áp cho mọi task)
- P1 — Tích hợp bộ mã cấm cơ học tường minh `ANTI-1`..`ANTI-6`
- P2 — Xây dựng Cookbooks thực chiến Python và TypeScript/JS (Tầng 3)
- P3 — Cài đặt JIT Micro-injection và Neo Phục Hồi sau Compaction trong Hooks
- P4 — Cài đặt Silent CLI trong `tdq_test.py`
- P5 — Đồng bộ ngân sách token, log và kiểm định QC mức Full
- Cụm song song
- Definition of Done

## Quy tắc thi hành (áp cho mọi task)

1. Thứ tự phase là thứ tự phụ thuộc — không đảo.
2. Mỗi task: đánh `[~]` khi bắt đầu → viết test trước (đỏ) → code → test xanh → đổi sang `[x]` NGAY vào file này. Trạng thái checkbox: `[ ]` chưa làm · `[~]` đang làm · `[x]` xong.
3. Mỗi bước: `tdq_test.py vung-cham`; trọn bộ chỉ ở QC.
4. Lệnh nào chạm state của workflow phải có `TDQ_PROJECT_DIR=<thư mục tạm>` ngay trên chính lệnh đó.
5. QC FAIL → thêm task fix vào mục QC của file này (không cần duyệt lại), loop đến khi pass.
6. Không commit/push cho đến khi user yêu cầu.

## P1 — Tích hợp bộ mã cấm cơ học tường minh `ANTI-1`..`ANTI-6`

- [x] **T1.1** (e20m) Tích hợp bộ 6 mã cấm cơ học `ANTI-1`..`ANTI-6` kèm ví dụ đối chứng WRONG/RIGHT chuẩn hóa vào các tài liệu hướng dẫn cốt lõi: `skills/tdq-build/references/team-mode.md`, `agents/tdq-implementer.md`, `skills/tdq-build/references/qc.md`, `skills/tdq-plan/references/plan-template.md` — Test: `python scripts/doc_lint.py skills/tdq-build/references/team-mode.md skills/tdq-build/references/qc.md skills/tdq-plan/references/plan-template.md`
  - Chạm: `skills/tdq-build/references/team-mode.md`, `agents/tdq-implementer.md`, `skills/tdq-build/references/qc.md`, `skills/tdq-plan/references/plan-template.md`
  - Dùng: `Agent`
  - Để: hỗ trợ kiểm tra tính tương thích của instruction trên nhiều agent role
  - Ra: các đoạn hướng dẫn mã cấm đã được đối soát
  - Kiểm: 4 file tài liệu mang đầy đủ 6 mã cấm cơ học
  - Không dùng cho: việc tự ý viết code phá vỡ cấu trúc role

**Xong P1 khi**: Cả 4 file tài liệu đều mang bộ mã cấm tường minh `ANTI-1`..`ANTI-6`, đạt 0 vi phạm qua `doc_lint.py`.

## P2 — Xây dựng Cookbooks thực chiến Python và TypeScript/JS (Tầng 3)

- [x] **T2.1** (e25m) Soạn thảo `skills/tdq-build/references/rules/python-cookbook.md` (> 100 dòng) và `typescript-js-cookbook.md` (> 100 dòng) theo chuẩn Kim tự tháp 3 tầng: chứa các mẫu thực chiến (Async/Await, DB transaction context manager, Domain Error handling, Clean Architecture patterns, Logging chuẩn ISO). Cập nhật `skills/tdq-build/references/rules/index.md` bổ sung bảng chỉ mục Cookbooks và quy tắc nạp Tầng 3 khi gặp bế tắc — Test: `python scripts/doc_lint.py skills/tdq-build/references/rules/python-cookbook.md skills/tdq-build/references/rules/typescript-js-cookbook.md skills/tdq-build/references/rules/index.md`
  - Chạm: `skills/tdq-build/references/rules/python-cookbook.md`, `skills/tdq-build/references/rules/typescript-js-cookbook.md`, `skills/tdq-build/references/rules/index.md`
  - Cần: T1.1
  - Dùng: `context_surface.py & skill_tokens.py`
  - Để: đo lường dung lượng token của các file cookbooks mới tạo và kiểm tra bề mặt ngữ cảnh
  - Ra: số đo dung lượng token thực tế của thư mục cookbooks
  - Kiểm: dung lượng mỗi file cookbook nằm trong ngưỡng thiết kế 1.500 - 3.000 tokens
  - Không dùng cho: việc sửa đổi nội dung file trên đĩa

**Xong P2 khi**: Thư mục `rules/` có 2 file cookbook chất lượng cao đạt chuẩn lint, `index.md` có chỉ mục liên kết.

## P3 — Cài đặt JIT Micro-injection và Neo Phục Hồi sau Compaction trong Hooks

- [x] **T3.1** (e20m) Cập nhật `hooks/scripts/edit_gate.py` và unit test `tests/test_edit_gate.py` (TDD đỏ → xanh): bổ sung chức năng nhận diện đuôi file `.py` hoặc `.ts` khi gọi tool `Edit` lần đầu trong phiên, mớm đúng 3 dòng quy tắc vàng của ngôn ngữ (dedupe qua `already_reminded`) — Test: `python -m unittest discover -s tests -p "test_edit_gate.py"`
  - Chạm: `hooks/scripts/edit_gate.py`, `tests/test_edit_gate.py`
  - Cần: T2.1
- [x] **T3.2** (e20m) Cập nhật `hooks/scripts/session_start.py`, `hooks/scripts/prompt_context.py` và bộ unit test `tests/test_context_hooks.py` (TDD đỏ → xanh): bổ sung xử lý khi `source == "compact"` để reset cờ nhắc ngôn ngữ và bơm Khối Neo Phục Hồi (Compact Recovery Anchor) < 200 tokens tóm tắt state, plan và mã cấm `ANTI`; trong `prompt_context.py` tự động mớm checklist DoD và 5 câu hỏi SOLID khi phase là `qc` — Test: `python -m unittest discover -s tests -p "test_context_hooks.py"`
  - Chạm: `hooks/scripts/session_start.py`, `hooks/scripts/prompt_context.py`, `tests/test_context_hooks.py`
  - Cần: T3.1

**Xong P3 khi**: `edit_gate` mớm JIT micro-rules thành công; `session_start` bơm neo phục hồi sau compact; các unit test chạy xanh 100%.

## P4 — Cài đặt Silent CLI trong `tdq_test.py`

- [x] **T4.1** (e15m) Cập nhật `scripts/tdq_test.py` và unit test `tests/test_tdq_test.py` (TDD đỏ → xanh): bổ sung cờ `--silent` ghi log chi tiết ra `docs/tdq/.tdq-test.log`, terminal chỉ in `≤ 2` dòng tóm tắt trạng thái và dòng lỗi quyết định khi kiểm thử thất bại — Test: `python -m unittest discover -s tests -p "test_tdq_test.py"`
  - Chạm: `scripts/tdq_test.py`, `tests/test_tdq_test.py`
  - Cần: T3.2

**Xong P4 khi**: `tdq_test.py --silent` chạy đúng yêu cầu, ghi log chi tiết ra file đĩa và in tóm tắt ngắn gọn.

## P5 — Đồng bộ ngân sách token, log và kiểm định QC mức Full

- [x] **T5.1** (e15m) Đồng bộ tệp khóa ngân sách `token_budget.py`, kiểm tra hợp đồng `doc_lint.py --pair`, kiểm tra log service và chạy trọn bộ kiểm thử ở mức QC `full` — Test: `python scripts/token_budget.py && python scripts/doc_lint.py --pair docs/tdq/spec/2026-10-15-1425-cap-nhat-full-de-xuat-instruction.md docs/tdq/plan/2026-10-15-1425-cap-nhat-full-de-xuat-instruction.md && python scripts/token_budget.py --kiem`
  - Chạm: `docs/tdq/token-budget.json`, `docs/tdq/plan/2026-10-15-1425-cap-nhat-full-de-xuat-instruction.md`
  - Cần: T1.1, T2.1, T3.1, T3.2, T4.1

**Xong P5 khi**: `token_budget.py --kiem` và `doc_lint.py --pair` đạt 0 vi phạm; 100% test suite đạt PASS.

## Cụm song song

- **Một cụm tuần tự vì**: 5 phase có mối phụ thuộc dây chuyền chặt chẽ: chuẩn hóa mã cấm P1 $\to$ soạn cookbooks P2 $\to$ cài đặt hook JIT & Neo Phục Hồi P3 $\to$ cài đặt Silent CLI P4 $\to$ kiểm định trọn bộ P5. Thực thi tuần tự trong `main` mode giúp kiểm soát trạng thái tốt nhất.

## Definition of Done

1. 4 file tài liệu cốt lõi tích hợp đầy đủ bộ mã cấm tường minh `ANTI-1`..`ANTI-6`.
2. Thư viện Cookbooks thực chiến Python và TypeScript/JS (Tầng 3) được xây dựng hoàn chỉnh, chất lượng cao.
3. Cơ chế JIT Micro-injection và Neo Phục Hồi sau Compaction hoạt động ổn định và có unit test bảo chứng.
4. Chế độ Silent CLI trong `tdq_test.py` hoạt động chính xác, bảo vệ context window khỏi rác log.
5. Toàn bộ các tiêu chí kiểm thử QC mức `full` đạt 100% PASS, 0 vi phạm lint và token budget.
