# REPORT — Skill tiếng Anh vs tiếng Việt + phương án tối ưu bộ workflow (`2026-08-18-2358-skill-en-vs-vi-toi-uu` · lane full · mode main · 2 task tick đủ)

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

**Đã làm:** 3 lượt research web (tokenizer, tuân thủ chỉ dẫn theo ngôn ngữ, prompt caching 2026) + thực nghiệm dịch `tdq-build/SKILL.md` sang tiếng Anh, đo token thật · đối chiếu kết quả với đề án cũ (2026-08-17) và soul.md · nối mục "Vòng 2026-08-19" vào `docs/tdq/audit/de-an-toi-uu-context.md` chốt lại hướng A.

**Kết quả:** dịch sang Anh tiết kiệm token 43,2% (6.396 ký tự/3.579 token VI → 7.701 ký tự/2.034 token EN) — khớp khoảng đã đo trước (37,6-43,2%). Phát hiện mới: lệch ngôn ngữ chỉ dẫn/nội dung giảm độ chính xác tới 50% (nghiên cứu 35 ngôn ngữ, 2025).

**Phương án patch — xếp thứ tự nên làm (không đổi so với vòng 08-17):**

| # | hướng | tiết kiệm | rủi ro | trạng thái |
|---|---|---|---|---|
| 1 | D — `skillOverrides` (settings.json) | 26.127 token (87,7%) | thấp | chưa áp dụng, khuyến nghị làm trước |
| 2 | C — tách reference ra khỏi SKILL.md chính | chưa đo hết | thấp | chưa áp dụng |
| 3 | B — cắt output tool dư thừa | chưa đo | thấp | chưa áp dụng |
| 4 | A — dịch skill sang tiếng Anh | ~40% token | **cao** | **khuyến nghị KHÔNG làm** — mới xác nhận thêm ở vòng này |
| — | E — router BM25 tự động | — | — | chưa đủ điều kiện (top-5 chỉ 45,5%) |

**Vì sao A bị loại:** soul.md xếp chất lượng > runtime > context cost. Lợi ích của A nằm ở trục thấp nhất (context cost, vốn đã giảm nhẹ do prompt caching). Rủi ro mới (lệch ngôn ngữ chỉ dẫn/nội dung) nằm ở trục cao nhất (chất lượng). Đây là khuyến nghị dựa trên bằng chứng hiện có, không phải cấm tuyệt đối.

**Kiểm:** `doc_lint.py` exit 0 cả `de-an-toi-uu-context.md` và report này · `grep -c "Vòng 2026-08-19"` = 1 · `git status --short` chỉ liệt kê file trong `docs/tdq/`.
**Đầu ra:** `docs/tdq/audit/de-an-toi-uu-context.md` (mục mới cuối file) · `docs/tdq/reports/2026-08-18-2358-skill-en-vs-vi-toi-uu.md` (file này).
**Giới hạn:** chưa thực thi patch nào (D/C/B) — theo đúng phạm vi spec, request này chỉ chốt kết luận + report, không sửa `skills/` hay `settings.json`.
**Git:** chưa commit.

## Thời gian

| Phase | Treo tường | Model chạy | Số lần vào |
|---|---|---|---|
| idle | 1 giây | 0 giây | 1 |
| analyze | 8 phút | 8 phút | 1 |
| spec | 2 phút | 2 phút | 1 |
| plan | 7 phút | 7 phút | 1 |
| **Tổng** | **17 phút** | **17 phút** | |
