# REPORT — Nâng Cấp Khảo Sát Code 3 Chiều & Bảo Toàn Chủ Đích Refactor (`2026-10-20-1355-nang-cap-khao-sat-3-chieu-refactor` · lane full · mode main · 8 task tick đủ)

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

**Đã làm:**
- Tinh chỉnh `hooks/scripts/search_gate.py` và `scripts/search_rules.py`: Mở khóa cho phép Grep diện rộng tự do (không áp quota 10 lượt, không deny) trong các phase khảo sát (`analyze`, `quick_analyze`, `spec`). Duy trì nghiêm ngặt kỷ luật cổng 3 tầng khi chuyển sang phase `implement`.
- Thêm cơ chế nhận diện tam giác khảo sát 3 chiều (`tam_giac_khao_sat`) trong `scripts/search_rules.py` để hỗ trợ kiểm tra và đánh giá chất lượng phân tích mã nguồn.
- Chuẩn hóa quy trình Tam Giác Khảo Sát 3 Chiều (Grep quét rộng → LSP đào sâu cấu trúc → Graphify quét vỡ lan) và đưa bảng đối chiếu vùng chạm bắt buộc vào `skills/tdq-intake/SKILL.md`, `references/analyze-full.md` và `references/quick-lane.md`.
- Bổ sung ngoại lệ Refactor & Mở rộng Kiến trúc vào Rung 1 của luật tinh gọn trong `skills/tdq-build/references/rules/chung.md`: Khi người dùng yêu cầu Refactor hoặc Clean Architecture/SOLID, cấu trúc sạch và tính mở rộng module đứng TRÊN luật phẫu thuật 1 dòng tối thiểu. Nghiêm cấm tự ý ép gộp các tầng/lớp hợp lý thành hàm phẳng.
- Bổ sung bảng so sánh Hiện trạng (Trước) vs Thiết kế mới (Sau) vào `skills/tdq-spec/references/spec-template.md` và `skills/tdq-plan/references/plan-template.md`.
- Đồng bộ nguyên tắc khảo sát 3 chiều và ngoại lệ refactor vào `KHOI_HUONG_DAN` của `scripts/tdq_setup.py`, cập nhật `docs/claude-md-mau.md` và ghim vào `~/.claude/CLAUDE.md`.
- Xây dựng bộ test suite `tests/test_khao_sat_3_chieu.py` kiểm chứng toàn diện 100%.

**Kết quả:**
- Triệt tiêu hoàn toàn rào cản quota Grep trong giai đoạn phân tích & lập kế hoạch, giúp agent quét trọn vẹn context codebase mà không bị phạt hay từ chối công cụ.
- Bảo toàn tuyệt đối chủ đích thiết kế kiến trúc sạch của người dùng, ngăn chặn tình trạng agent "ép phẳng" mã nguồn thành một hàm một dòng gây thoái hóa cấu trúc.
- Bộ instruction toàn cục và các mẫu tài liệu cốt lõi được đồng bộ nhất quán.

**Kiểm:**
- Unit test `test_khao_sat_3_chieu.py`: 6/6 PASS 100%.
- Cụm gate tìm kiếm: `test_search_gate.py` (34/34 PASS), `test_search_rules.py` (76/76 PASS), `test_search_observe.py` (24/24 PASS), `test_search_replay.py` (11/11 PASS), `test_codex_search_gate.py` (16/16 PASS).
- Kiểm tra hệ thống: `test_tdq_setup.py` (43/43 PASS), `test_build_portable.py` (37/37 PASS), `test_claude_md_core.py` (12/12 PASS), `test_doc_index.py` (26/26 PASS), `test_docs_consistency.py` (8/8 PASS).
- Linter: `doc_lint.py` 0 violations trên toàn bộ tài liệu (tuân thủ nghiêm ngặt R5 câu ≤ 40 từ, R6 độ dài dòng, R13 token budget ≤ 3.500).
- QC PASS 4/4 tiêu chí Definition of Done (Q1–Q4).

**Đầu ra:**
- `hooks/scripts/search_gate.py`, `scripts/search_rules.py`, `scripts/tdq_setup.py`
- `skills/tdq-build/references/rules/chung.md`
- `skills/tdq-intake/SKILL.md`, `skills/tdq-intake/references/analyze-full.md`, `skills/tdq-intake/references/quick-lane.md`
- `skills/tdq-spec/references/spec-template.md`, `skills/tdq-plan/references/plan-template.md`
- `docs/claude-md-mau.md`, `README.md`
- `tests/test_khao_sat_3_chieu.py`, `tests/test_search_gate.py`, `tests/test_tdq_setup.py`, `tests/test_build_portable.py`, `tests/test_claude_md_core.py`
- `docs/tdq/qc/2026-10-20-1355-nang-cap-khao-sat-3-chieu-refactor.md`
- `docs/tdq/reports/2026-10-20-1355-nang-cap-khao-sat-3-chieu-refactor.md`

**Giới hạn:** Không có.
**Lệch spec chờ duyệt:** Không có.
**Git:** Chưa commit (nhánh `feature/khao-sat-3-chieu-refactor`).

## Thời gian

| Phase | Wall clock | Model time | Times entered |
|---|---|---|---|
| idle | 20s | — | 1 |
| analyze | 50s | — | 1 |
| spec | 2 min | — | 1 |
| plan | 1 min | — | 1 |
| implement | 45 min | — | 1 |
| qc | 1 min | — | 1 |
| report | 17s | — | 1 |
| **Total** | **50 min** | **—** | |
