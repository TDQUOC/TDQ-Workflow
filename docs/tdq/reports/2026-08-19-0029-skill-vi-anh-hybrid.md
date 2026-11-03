# REPORT — Hybrid skill: luật tiếng Anh, giao tiếp user tiếng Việt (`2026-08-19-0029-skill-vi-anh-hybrid` · lane full · mode main · 2 task tick đủ)

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

**Đã làm:** 5 truy vấn research (Anthropic best practices, 2 nghiên cứu đá nhau về chỉ dẫn/nội dung, nguồn giải mâu thuẫn, đối chứng skill cộng đồng) · nối mục mới vào `docs/tdq/audit/de-an-toi-uu-context.md`.

**Câu hỏi 1 — có cách dịch sang Anh mà giữ output/rule/behavior Việt không?**
Có, nhưng KHÔNG phải "dịch nguyên khối" (cách hướng A gốc định làm — đã bị cảnh báo trực tiếp là cho kết quả tệ hơn viết lại từ đầu). Pattern đúng: **tách theo loại nội dung**, không tách theo "dịch hết hay giữ hết":
- Luật lý luận/điều kiện phức tạp (gate, tick discipline, thứ tự phase) → viết tiếng Anh được, có bằng chứng còn giúp tuân thủ tốt hơn (tiếng Anh làm "mỏ neo" ổn định cho luật phức tạp).
- Khuôn user-facing (report, câu hỏi option A/B, mọi ví dụ user nhìn trực tiếp) + khai báo ngôn ngữ đầu ra → PHẢI giữ tiếng Việt, tách riêng biệt, không lẫn vào phần luật.

**Câu hỏi 2 — `superpowers` và skill tiếng Anh khác đảm bảo quality thế nào?**
Không phải vì đã giải bài toán khớp ngôn ngữ. Hai lý do: (a) tác vụ của chúng là quy trình/tool-call, ít nhạy ngôn ngữ đầu ra hơn TDQ (TDQ có yêu cầu cứng "output 100% tiếng Việt", chúng thì không); (b) không có gate nào đo lệch ngôn ngữ trong các bộ đó — lệch có xảy ra cũng không lộ ra. TDQ có `doc_lint.py`/`stop_gate.py` làm hiện lỗi ngay nếu có, nên không dùng "superpowers chạy tốt" làm bằng chứng an toàn cho TDQ được.

**Điều kiện cần trước khi patch hybrid thật (chưa có ở đây):** (a) lưới khoá hành vi rà đúng ranh giới "luật lý luận" vs "khuôn user-facing" cho từng skill, (b) một gate mới đo được "output có đúng tiếng Việt không" — khai báo tường minh ngôn ngữ đầu ra là điều kiện CẦN, không phải ĐỦ (có ca thực tế model vẫn lệch dù đã khai báo rõ).

**Khuyến nghị:** thứ tự nên làm D → C → B (từ đề án cũ) **không đổi**. Hướng A — kể cả bản hybrid vừa tìm ra — vẫn hoãn tới khi có đủ 2 điều kiện trên.

**Kiểm:** `doc_lint.py` exit 0 cả 2 file · `grep -c "Vòng 2026-08-19 (2)"` = 1 · `git status --short -- docs/tdq` chỉ liệt kê file trong `docs/tdq/`.
**Đầu ra:** `docs/tdq/audit/de-an-toi-uu-context.md` (mục mới cuối file) · `docs/tdq/reports/2026-08-19-0029-skill-vi-anh-hybrid.md` (file này).
**Giới hạn:** chưa patch bất kỳ skill nào — đúng phạm vi spec đã chốt (1A+2A), chỉ research + trình bày.
**Git:** chưa commit.

## Thời gian

| Phase | Treo tường | Model chạy | Số lần vào |
|---|---|---|---|
| idle | 0 giây | 0 giây | 1 |
| analyze | 6 phút | 6 phút | 1 |
| spec | 1 phút | 58 giây | 1 |
| plan | 1 phút | 1 phút | 1 |
| **Tổng** | **8 phút** | **8 phút** | |
