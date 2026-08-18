# REPORT — Đo và đề án tối ưu context cho bộ workflow TDQ (`2026-08-17-2121-toi-uu-context-workflow` · lane full · mode main · 20/21 task tick đủ)

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

**Đã làm:** P1 dựng thước đo token offline (`skill_tokens.py`, venv riêng, cấm đoán số) · P2 trích 329 neo luật ra `audit/luat-hien-co.md` và khoá bằng test nội dung · P3 bốn thí nghiệm đo thật (3 bản portable, dịch Anh, `skillOverrides`, `name-only`) · P4 nguyên mẫu router BM25 offline + bộ 22 prompt mẫu để trả lời ý tưởng "vector DB cho skill" bằng SỐ · P5 viết `audit/de-an-toi-uu-context.md` (5 hướng A–E) · P6 QC 19 hạng mục + QC độc lập bằng agent.

**Kết quả:** mô tả 284 skill đang bật = **29.788 token**, hạ còn **3.661** nếu dùng `skillOverrides` → tiết kiệm **87,7%** · trần context bộ workflow **70.924 token** (luôn nạp 4.477 + luật kèm 55.719 + thân phase) · hệ số dịch Việt→Anh **0,624** (1.070 → 668 token trên `approval.md`) · 3 bản portable lệch 16 file theo byte nhưng **0 file lệch nội dung** → chi phí bảo trì ×1, không phải ×3 · router BM25 **top-1 27,3% · top-5 45,5%** (dễ 90% / vừa 16,7% / khó 0%).

**Kết luận đáng giá nhất — trả lời trực tiếp ý tưởng vector DB của bạn:** ĐỪNG xây router lúc này. Không phải vì BM25 yếu mà vì nguyên nhân trượt nằm ở **khoảng cách ngôn ngữ**: cùng một ý hỏi, tiếng Việt trúng 0/4, tiếng Anh trúng 2/4 — kho skill gần như toàn tiếng Anh. Vector DB cũng dính đúng lỗi đó. Và hệ quả ngược đời: dịch workflow sang tiếng Anh sẽ **nới rộng** khoảng cách này chứ không thu hẹp. Hướng D (`skillOverrides` 3 tầng) cho 87,7% tiết kiệm mà không cần đoán skill nào liên quan — nên làm trước, và làm xong thì router gần như hết lý do tồn tại.

**Kiểm:** `python3 -m pytest` → **914 passed, 1199 subtests passed** · `doc_lint.py` trên spec/plan/3 file audit/file qc → exit 0 · QC **19/19 PASS**, trong đó Q15 là **FAIL→PASS** sau khi agent QC độc lập bắt được lỗi, 3 defect (D1 vừa, D2+D3 nhẹ) đã sửa hết trong 2 vòng fix.

**Đầu ra:** `docs/tdq/audit/de-an-toi-uu-context.md` (đề án chính) · `do-thuc-nghiem.md` · `luat-hien-co.md` · `skill-overrides-de-xuat.json` (261 khoá) · `skill-index.json` (284 bản ghi, 284/284 có đường dẫn) · `scripts/skill_tokens.py`, `scripts/skill_router.py` · `tests/test_luat_skill.py`, `tests/test_skill_router.py`. Không sửa file nào trong `skills/`, `portable_claude/`, `portable_codex/`, không đụng settings của bạn.

**Giới hạn:** T4.4 (chạy thật để xem skill mức `name-only` còn gọi được không) **để trống `[ ]` có chủ ý** — quy tắc 7 của plan cấm ghi settings, mà `skillOverrides` chỉ đọc lúc mở phiên nên có ghi cũng không quan sát được trong turn này; bằng chứng gián tiếp (chuỗi lỗi trong binary) và cách bạn tự xác nhận trong 1 phút ở `do-thuc-nghiem.md` §4, đề án đứng vững với cả hai kết quả · 329 neo luật là **trần trên**, có dương tính giả (vd L166 là dòng tiêu đề bảng) · router mới là nguyên mẫu, **chưa lắp vào hook nào** đúng như spec Q18 · phần dịch toàn bộ workflow sang tiếng Anh vẫn để lại request sau theo đúng câu 2a bạn chốt.

**Ngoài plan:** xoá 2 file `.DS_Store` (rác Finder, không được git theo dõi) để gỡ test đỏ có sẵn từ trước — quyết định tự chọn lúc gặp chặn, đã ghi ở file qc.

**Git:** chưa commit gì. Không có commit gỡ chặn nào trong build này.

## Thời gian

| Phase | Treo tường | Model chạy | Số lần vào |
|---|---|---|---|
| idle | 0 giây | 0 giây | 1 |
| analyze | 14 phút | 14 phút | 1 |
| spec | 41 phút | 11 phút | 1 |
| plan | 4 phút | 3 phút | 1 |
| implement | 35 phút | 35 phút | 1 |
| qc | 13 phút | 5 phút | 1 |
| report | 2 phút | 2 phút | 1 |
| **Tổng** | **1 giờ 48 phút** | **1 giờ 13 phút** | |
