# PLAN — Áp dụng nâng cấp triết lý và kiến trúc Andrej Karpathy vào TDQ Workflow

Ngày: 2026-10-16 · Spec: ../spec/2026-10-16-1410-nang-cap-triet-ly-karpathy.md (bản 1.0, ĐÃ DUYỆT) · Lane: full
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md
Mode thực thi: main — 4 task liên kết chặt chẽ giữa hệ thống rule, bộ lọc `luat_gon.py`, hook `edit_gate.py` và bảng neo luật; thực thi tuần tự trong main session giúp đồng bộ tức thì chỉ mục và ngân sách token.
Trạng thái plan: HOÀN THÀNH

## Mục lục

- Quy tắc thi hành (áp cho mọi task)
- P1 — Cập nhật hệ thống Rule cốt lõi (`chung.md`, `clean-code.md`, `interview.md`, `agents/tdq-implementer.md`)
- P2 — Tối ưu hóa bộ lọc `luat_gon.py` và JIT Micro-rules trong `edit_gate.py`
- P3 — Đồng bộ bảng neo luật, khóa ngân sách và kiểm định QC mức Ultra
- Cụm song song
- Definition of Done

## Quy tắc thi hành (áp cho mọi task)

1. Thứ tự phase là thứ tự phụ thuộc — không đảo.
2. Mỗi task: đánh `[~]` khi bắt đầu → viết test trước (đỏ) → code → test xanh → đổi sang `[x]` NGAY vào file này. Trạng thái checkbox: `[ ]` chưa làm · `[~]` đang làm · `[x]` xong.
3. Mỗi bước: `tdq_test.py vung-cham`; trọn bộ chỉ ở QC.
4. Lệnh nào chạm state của workflow phải có `TDQ_PROJECT_DIR=<thư mục tạm>` ngay trên chính lệnh đó.
5. QC FAIL → thêm task fix vào mục QC của file này (không cần duyệt lại), loop đến khi pass.
6. Không commit/push cho đến khi user yêu cầu.
7. Tuân thủ 6 mã cấm cơ học (ANTI-1 Fake Red, ANTI-2 Blind Assertion, ANTI-3 Dirty State Git, ANTI-4 Late Tick, ANTI-5 Raw Dump, ANTI-6 Broad Area).

## P1 — Cập nhật hệ thống Rule cốt lõi (`chung.md`, `clean-code.md`, `interview.md`, `agents/tdq-implementer.md`)

- [x] **T1.1** (e20m) Cập nhật `skills/tdq-build/references/rules/chung.md` (Surgical Changes cấm drive-by refactor + Clean Up Only Your Own Mess phân biệt dead code mới/cũ), `skills/tdq-conventions/references/clean-code.md` (YAGNI đứng trên SOLID: cấm abstraction cho code dùng 1 lần), `skills/tdq-intake/references/interview.md` (Think Before Coding — Surface Tradeoffs & Push Back), và `agents/tdq-implementer.md` (4 nguyên lý Karpathy & Goal-Driven Loop) — Test: `python scripts/doc_index.py --tat-ca && python scripts/token_budget.py && python scripts/doc_lint.py skills/tdq-build/references/rules/chung.md skills/tdq-conventions/references/clean-code.md skills/tdq-intake/references/interview.md`
  - Chạm: `skills/tdq-build/references/rules/chung.md`, `skills/tdq-conventions/references/clean-code.md`, `skills/tdq-intake/references/interview.md`, `agents/tdq-implementer.md`
  - Dùng: `token_budget.py & doc_index.py`
  - Để: đồng bộ chỉ mục dòng và khóa ngân sách token sau khi cập nhật các file rule
  - Ra: tệp khóa `docs/tdq/token-budget.json` và khối chỉ mục `<!-- muc-luc-dong -->` đã cập nhật
  - Kiểm: `python scripts/token_budget.py --kiem` đạt 0 vi phạm
  - Không dùng cho: việc sửa nội dung văn bản rule

**Xong P1 khi**: Cả 4 file tài liệu được cập nhật đầy đủ các nguyên lý Karpathy bằng tiếng Anh chuẩn mực, đạt 0 vi phạm qua `doc_lint.py`.

## P2 — Tối ưu hóa bộ lọc `luat_gon.py` và JIT Micro-rules trong `edit_gate.py`

- [x] **T2.1** (e15m) Cập nhật `hooks/scripts/luat_gon.py`, `tests/test_luat_gon.py` và `tests/test_context_hooks.py` (TDD đỏ → xanh): ở mức `full` (mặc định), cấu hình `CAT_THEO_MUC["full"] = (MUC_VI_DU, MUC_ULTRA)` để lọc bỏ 50 dòng ví dụ dài (`### RIGHT / WRONG for this law`), giảm ~500 tokens mang vác cho mọi phiên `implement` và `SubagentStart` — Test: `python -m unittest discover -s tests -p "test_luat_gon.py" && python -m unittest discover -s tests -p "test_context_hooks.py" -k "TestThanLuatKenhPhien"`
  - Chạm: `hooks/scripts/luat_gon.py`, `tests/test_luat_gon.py`, `tests/test_context_hooks.py`
  - Cần: T1.1
- [x] **T2.2** (e15m) Cập nhật `hooks/scripts/edit_gate.py` và unit test `tests/test_edit_gate.py` (TDD đỏ → xanh): tích hợp quy tắc Surgical & No Single-Use Abstraction vào `QUY_TAC_NGON_NGU` để mớm lần đầu khi sửa code trong phiên (giữ dưới trần 200 ký tự) — Test: `python -m unittest discover -s tests -p "test_edit_gate.py" -k "test_jit"`
  - Chạm: `hooks/scripts/edit_gate.py`, `tests/test_edit_gate.py`
  - Cần: T2.1

**Xong P2 khi**: `luat_gon.py` cắt gọn 50 dòng ví dụ ở mức `full`, `edit_gate.py` mớm JIT micro-rules mới thành công, toàn bộ unit test chạy xanh 100%.

## P3 — Đồng bộ bảng neo luật, khóa ngân sách và kiểm định QC mức Ultra

- [x] **T3.1** (e15m) Đồng bộ số dòng bảng neo `docs/tdq/audit/luat-hien-co.md`, kiểm tra `test_luat_skill.py`, `test_doc_index.py`, `test_token_budget.py` và phối hợp subagent `tdq-qc-tester` hoàn thành QC mức `ultra` — Test: `python -m unittest discover -s tests -p "test_luat_skill.py" && python -m unittest discover -s tests -p "test_doc_index.py" && python -m unittest discover -s tests -p "test_token_budget.py"`
  - Chạm: `docs/tdq/audit/luat-hien-co.md`, `docs/tdq/token-budget.json`, `docs/tdq/plan/2026-10-16-1410-nang-cap-triet-ly-karpathy.md`
  - Cần: T2.2
  - Dùng: `Agent`
  - Để: chạy thẩm định độc lập mức `ultra` qua `tdq-qc-tester`
  - Ra: biên bản thẩm định độc lập xác nhận đạt DoD
  - Kiểm: `VERDICT: PASS` cho toàn bộ Q1–Q5
  - Không dùng cho: việc tự ý sửa đổi code ngoài phạm vi

**Xong P3 khi**: Toàn bộ test suite của các module chạm đạt 100% PASS, `token_budget.py --kiem` đạt 0 vi phạm và subagent QC độc lập xác nhận PASS.

## Cụm song song

- **Một cụm tuần tự vì**: Các task có tính phụ thuộc trực tiếp: cập nhật văn bản luật trong `chung.md` (P1) $\to$ cấu hình bộ lọc cắt dòng `luat_gon.py` và `edit_gate.py` (P2) $\to$ đồng bộ số dòng bảng neo luật và khóa ngân sách cuối cùng (P3). Thực thi tuần tự trong `main` mode giúp tránh lệch chỉ mục dòng.

## Definition of Done

Trỏ về §6 của spec. Liệt kê lại từng hạng mục QC + lệnh kiểm, MỖI DÒNG MỘT Ô TICK:

- [x] Q1 Cập nhật `chung.md` và `clean-code.md` với quy tắc Surgical, Clean Own Mess và YAGNI > SOLID — `python scripts/doc_lint.py skills/tdq-build/references/rules/chung.md skills/tdq-conventions/references/clean-code.md`
- [x] Q2 Cập nhật `interview.md` và `agents/tdq-implementer.md` với Push Back và 4 nguyên lý Karpathy — `python scripts/doc_lint.py skills/tdq-intake/references/interview.md`
- [x] Q3 Hook `edit_gate.py` mớm thông điệp Surgical & Simplicity trong JIT micro-rules — `python -m unittest discover -s tests -p "test_edit_gate.py"`
- [x] Q4 Đồng bộ chỉ mục dòng, bảng neo luật, bộ lọc `luat_gon.py` và khóa ngân sách token — `python -m unittest discover -s tests -p "test_luat_gon.py" && python -m unittest discover -s tests -p "test_luat_skill.py" && python scripts/token_budget.py --kiem`
- [x] Q5 Kiểm thử độc lập mức `ultra` — chạy subagent `tdq-qc-tester` thẩm định độc lập và ghi biên bản QC
