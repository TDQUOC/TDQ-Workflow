# REPORT — Chế độ `_tdq_direct` tự động phân tích và chỉ 1 cổng duyệt mini-plan (`2026-10-14-1022-che-do-tdq-direct` · lane full · mode subagent · 6 task hoàn tất)

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

**Đã làm:**
- P1 (`prompt_context.py` & `test_prompt_context.py`): Nhận diện từ khóa `_tdq_direct` (không phân biệt hoa thường) qua regex `RE_DIRECT` khi chưa có request mở hoặc phase idle, phát câu nhắc `[TDQ:INTAKE]` direct (186 ký tự ≤ 240); bổ sung 8 unit tests kiểm thử toàn diện.
- P2 (`SKILL.md` & `quick-lane.md`): Quy định luồng tiếp nhận bỏ qua hỏi chọn pipeline & phỏng vấn, tự động `init <slug> quick`, mở branch git và chuyển thẳng Part C; chạy tìm kiếm mã nguồn 3 tầng (LSP, graphify, grep), lập mini-plan ≤ 40 dòng trong `docs/tdq/plan/<slug>.md`, chỉ dừng đúng 1 cổng duyệt `quick_approved` rồi implement.
- P3 (`tdq_setup.py` & `claude-md-mau.md`): Bổ sung gạch đầu dòng nguyên tắc `_tdq_direct` vào `KHOI_HUONG_DAN` (164 ký tự ≤ 300) và đồng bộ nguyên văn sang bản mẫu `docs/claude-md-mau.md`.
- P4 & QC: Kiểm thử đơn vị và hồi quy vùng chạm 100% pass, cập nhật chỉ mục `doc_index.py` và ngân sách `token_budget.json`.

**Kết quả:**
- Definition of Done Q1–Q5: 5/5 PASS.
- Test hồi quy vùng chạm: 235 passed, 146 subtests passed (100% xanh).
- Hợp đồng tài liệu: `doc_lint` 0 vi phạm; `quick-lane.md` 3493 tokens (≤ trần 3500); `SKILL.md` 147 dòng (≤ trần 148); chỉ mục khớp tuyệt đối (`doc_index --kiem` exit 0).

**Giới hạn:**
- Từ khóa `_tdq_direct` có hiệu lực khi bắt đầu một request mới (chưa có active request hoặc đang ở `phase=idle`). Nếu đang có một request chạy dở dang, prompt vẫn tuân thủ theo phase và gate của request hiện hành.

**Lệch spec:** 0 mục lệch spec.

**Git:** Chưa commit, hiện nằm trên branch `feature/che-do-tdq-direct`.

## Thời gian

| Phase | Wall clock | Model time | Times entered |
|---|---|---|---|
| idle | 0s | — | 1 |
| analyze | 24 min | — | 1 |
| spec | 6 min | — | 1 |
| plan | 1h | — | 1 |
| qc | 12 min | — | 1 |
| report | 1 min | — | 1 |
| **Total** | **1h 43min** | **—** | |
