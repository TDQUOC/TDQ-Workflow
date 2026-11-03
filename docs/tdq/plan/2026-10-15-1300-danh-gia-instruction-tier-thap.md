# PLAN — Đánh giá độ chi tiết instruction TDQ Workflow cho model tier thấp và phương án tối ưu token context

Ngày: 2026-10-15 · Spec: ../spec/2026-10-15-1300-danh-gia-instruction-tier-thap.md (bản 1.0, ĐÃ DUYỆT) · Lane: full
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md
Mode thực thi: main — 4 task gắn kết chặt chẽ giữa thiết kế RFC và tinh chỉnh hook; chạy trực tiếp trong main session tiết kiệm chi phí tạo worktree và context handover.
Trạng thái plan: HOÀN THÀNH

## Mục lục

- Quy tắc thi hành (áp cho mọi task)
- P1 — Báo cáo Kiến trúc Đề xuất chi tiết (RFC / Blueprint) tối ưu instruction và lazy load context
- P2 — Cơ chế hoãn nạp luật gọn có điều kiện theo phase trong hook khởi tạo phiên
- P3 — Bộ unit test kiểm chứng nạp context có điều kiện theo phase
- P4 — Log, ngân sách token và QC Definition of Done
- Cụm song song
- Definition of Done

## Quy tắc thi hành (áp cho mọi task)

1. Thứ tự phase là thứ tự phụ thuộc — không đảo.
2. Mỗi task: đánh `[~]` khi bắt đầu → viết test trước (đỏ) → code → test xanh → đổi sang `[x]` NGAY vào file này. Trạng thái checkbox: `[ ]` chưa làm · `[~]` đang làm · `[x]` xong.
3. Mỗi bước: `tdq_test.py vung-cham`; trọn bộ chỉ ở QC.
4. Lệnh nào chạm state của workflow phải có `TDQ_PROJECT_DIR=<thư mục tạm>` ngay trên chính lệnh đó.
5. QC FAIL → thêm task fix vào mục QC của file này (không cần duyệt lại), loop đến khi pass.
6. Không commit/push cho đến khi user yêu cầu.

## P1 — Báo cáo Kiến trúc Đề xuất chi tiết (RFC / Blueprint) tối ưu instruction và lazy load context

- [x] **T1.1** (e20m) Soạn thảo Báo cáo Kiến trúc Đề xuất chi tiết `docs/kien-truc-instruction-lazy-load.md` đạt tiêu chuẩn lint và ngân sách token: bao gồm đầy đủ 5 phần lớn:
  1. Hiện trạng & Đo đạc định lượng carry-cost trên toàn bộ 45 file reference và 9 file skill (~90.242 tokens).
  2. Phân tích chi tiết 7 điểm gãy của model nhỏ khi gặp instruction cô đọng, triết lý cao (lỗi CLI, quên tick checkbox, test đỏ ảo, sai format `Chạm:`, lúng túng khi QC/Git, thiếu ví dụ ngôn ngữ).
  3. Phân tích đối chứng các bài học thành công từ `vision-test-loop.md` (Trigger table, công thức mechanical, Anti-pattern codes, bảng Symptom -> Action).
  4. Thiết kế chi tiết 4 giải pháp kiến trúc tối ưu ngữ cảnh (Kim tự tháp 3 tầng, Hook-driven JIT Micro-injection, Externalized Log & Silent CLI, State-Anchored Compaction & Session Handoff).
  5. Lộ trình triển khai cụ thể 3 giai đoạn cho TDQ Workflow.
  - Chạm: `docs/kien-truc-instruction-lazy-load.md`
  - Dùng: `Agent`
  - Để: điều phối 2 subagent chạy ngầm song song thu thập chứng cứ thực tế và cấu trúc tham chiếu
  - Ra: dữ liệu định lượng và báo cáo tổng hợp từ subagent
  - Kiểm: các phân tích từ subagent được tích hợp đầy đủ vào 5 phần của RFC
  - Không dùng cho: việc tự động sửa code ngoài phạm vi
  - Dùng: `context_surface.py & skill_tokens.py`
  - Để: đo đạc chính xác dung lượng token và bề mặt context của toàn bộ 45 file reference và 9 file skill
  - Ra: bảng số liệu định lượng chi tiết ~90.242 tokens làm căn cứ cho RFC
  - Kiểm: số liệu token trong RFC khớp với đo đạc thực tế của hai script
  - Không dùng cho: việc sửa đổi file rule trên đĩa
  - Test: `python scripts/doc_lint.py docs/kien-truc-instruction-lazy-load.md`

**Xong P1 khi**: File `docs/kien-truc-instruction-lazy-load.md` hoàn thành đầy đủ 5 phần lớn, phân tích chuyên sâu, đạt 0 vi phạm qua `doc_lint.py`.

## P2 — Cơ chế hoãn nạp luật gọn có điều kiện theo phase trong hook khởi tạo phiên

- [x] **T2.1** (e15m) Cập nhật `hooks/scripts/session_start.py` (TDD đỏ → xanh): kiểm tra `effective_phase(state)`. Khi phase là `implement` (hoặc khi không có request active), nạp toàn bộ thân luật `chung.md` như hiện tại; khi có request active ở các phase khác (`idle`, `analyze`, `spec`, `plan`, `qc`, `report`), chỉ nạp dòng tiêu đề tóm tắt trỏ đường (`[{MA_GON}] The build-less-than-asked law (muc_gat={muc}) — full ladder loads during phase implement (see skills/tdq-build/references/rules/chung.md).`), giảm 90% carry-cost ở đầu phiên. Cập nhật `turn_log_append` ghi nhận đúng `so_dong` thực tế được bơm — Test: `python -m unittest discover -s tests -p "test_context_hooks.py" -k "TestThanLuatKenhPhien"`
  - Chạm: `hooks/scripts/session_start.py`

**Xong P2 khi**: `SessionStart` chạy ở phase `spec`/`plan`/`idle` chỉ in dòng tóm tắt và ghi đúng `so_dong` nhỏ vào log; khi ở phase `implement` in đầy đủ thân luật.

## P3 — Bộ unit test kiểm chứng nạp context có điều kiện theo phase

- [x] **T3.1** (e15m) Cập nhật `tests/test_context_hooks.py` và `tests/test_log_kenh_luat.py` (TDD đỏ → xanh): bổ sung test cases kiểm chứng:
  1. `SessionStart` ở phase `idle`, `analyze`, `spec`, `plan` chỉ in dòng tóm tắt (< 200 tokens) và không chứa thân luật bậc 7 `| 7 |`.
  2. `SessionStart` ở phase `implement` nạp đầy đủ thân luật `chung.md`.
  3. `so_dong` ghi vào `.tdq-turn.jsonl` phản ánh chính xác số dòng được bơm theo từng phase.
  - Chạm: `tests/test_context_hooks.py`, `tests/test_log_kenh_luat.py`
  - Cần: T2.1
  - Test: `python -m unittest discover -s tests -p "test_context_hooks.py" -k "TestThanLuatKenhPhien"` và `python -m unittest discover -s tests -p "test_log_kenh_luat.py"`

**Xong P3 khi**: Toàn bộ unit test kiểm chứng `SessionStart` và `so_dong` chạy xanh 100%.

## P4 — Log, ngân sách token và QC Definition of Done

- [x] **T4.1** (e10m) Kiểm tra toàn diện hợp đồng tài liệu và chất lượng mã nguồn: chạy `python scripts/doc_lint.py --pair docs/tdq/spec/2026-10-15-1300-danh-gia-instruction-tier-thap.md docs/tdq/plan/2026-10-15-1300-danh-gia-instruction-tier-thap.md`, chạy `python scripts/token_budget.py --kiem`, kiểm tra log service qua `test_log_kenh_luat.py`, chạy toàn bộ test vùng chạm qua `tdq_test.py` — Test: `python scripts/token_budget.py --kiem && python scripts/doc_lint.py docs/tdq/plan/2026-10-15-1300-danh-gia-instruction-tier-thap.md`
  - Chạm: `docs/tdq/plan/2026-10-15-1300-danh-gia-instruction-tier-thap.md`
  - Cần: T1.1, T2.1, T3.1

**Xong P4 khi**: `doc_lint.py` và `token_budget.py --kiem` đạt 0 vi phạm, 100% test vùng chạm đạt PASS.

## Cụm song song

- **Một cụm tuần tự vì**: Request gồm 4 task có mối phụ thuộc chặt chẽ: T1.1 (lập tài liệu RFC), T2.1 (sửa hook), T3.1 (unit test cho hook), T4.1 (kiểm tra hợp đồng và QC) — thực thi tuần tự trong `main` mode để đảm bảo tính toàn vẹn và tối ưu token context.

## Definition of Done

1. Tài liệu `docs/kien-truc-instruction-lazy-load.md` được viết hoàn chỉnh, sâu sắc, giải quyết toàn diện bài toán của model tier thấp và tối ưu hóa context.
2. `hooks/scripts/session_start.py` được tinh chỉnh hoãn nạp `chung.md` theo phase, tiết kiệm ~2.000 tokens carry-cost ngay đầu phiên.
3. Bộ unit test trong `tests/test_context_hooks.py` và `tests/test_log_kenh_luat.py` được bổ sung và kiểm chứng xanh 100%.
4. Toàn bộ các tiêu chí kiểm thử QC mức `lite` đạt PASS, không phát sinh lỗi phụ thuộc hay vỡ hợp đồng tài liệu.
