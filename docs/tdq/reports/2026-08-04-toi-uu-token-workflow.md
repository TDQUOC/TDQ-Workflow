# REPORT — Tối ưu time/token cho TDQ workflow

Ngày: 2026-08-04 · Lane full · Mode main · QC 10/10 PASS · 472 test OK

## Đã làm gì

Đo chi phí token thật của workflow trên transcript của chính repo này, đối chiếu
nguồn chính thức, rồi viết bản đề xuất tối ưu xuống mức task. **Chưa sửa gì trong
workflow** — đúng phạm vi user chốt ("báo cáo + plan sẵn để duyệt sau").

## Phát hiện cốt lõi

Mỗi tool call = 1 API call = model đọc lại TOÀN BỘ context. Nên một tool output
`n` ký tự không tốn `n/4` token mà tốn `n/4 × số API call còn lại` — gọi là **carry-cost**.

Đo 2 session gần nhất: **1.123 API call · 132,6M cache_read · 72,2M carry-cost**.
Một kết quả tavily ~12k ký tự xuất hiện sớm trong session tốn **~2 TRIỆU token**.
5 chỗ đốt nhiều nhất: Read file 30,2M · tavily 14,3M · Bash ồn 12,7M ·
subagent report 3,6M · doc_lint 2,6M. Thời gian: full suite 44 lần ≈ **31 phút chờ**.

## Sản phẩm

| File | Nội dung |
|---|---|
| `scripts/token_audit.py` | Công cụ đo carry-cost từ transcript, có log service, 10 unit test |
| `docs/tdq/knowledge/2026-08-04-de-xuat-toi-uu-token.md` | **Bản đề xuất** — 12 nguyên nhân có số, 19 task chia 5 nhóm, bảng ưu tiên P0/P1/P2, mục giả định |
| `docs/tdq/research/…` | Số đo thật + 3 khẳng định đã xác minh bằng docs chính thức |
| `docs/tdq/qc/…` | Bằng chứng Q1–Q10 |

## Đề xuất — 5 nhóm, 19 task

- **A** cắt carry-cost đọc/CLI (6 task) — hợp đồng gọn thay đọc lại spec/plan, Read theo `offset`, Bash im lặng, `tdq_state.py`/`doc_lint` im khi PASS.
- **B** đẩy việc nặng sang subagent (3) — research/đọc code/QC trả digest ≤1,5k ký tự.
- **C** cắt context nền (2) — CLAUDE.md 10.307 → ~2.600 ký tự (§9 TDQ chiếm 4.701, cắt còn ~900); chia `tdq-build/SKILL.md`.
- **D** giảm số API call (4) — gộp Bash/Edit, test theo module, graphify cuối request.
- **E** giảm output token & vệ sinh session (4) — gộp doc, cap dòng spec/plan/log, 1 request 1 session.

**Ước tính nếu làm hết:** carry-cost 72,2M → ~28M (**−61%**); API call 1.123 → ~750
(**−33%**); context nền −2.500 token mỗi call; **−25 phút/request**.
Chỉ 5 task **P0** (A4, A5, D1, D2, B1) đã cắt ~37M (**≈51%**) với ~4–5 giờ công.

## Điều cần user quyết

1. Có mở request mới để **thực thi** đề xuất không, và bắt đầu từ nhóm nào (khuyên: đúng 5 task P0).
2. Commit đợt này? Chưa commit gì. Ngoài 9 file mới của request này, `graphify-out/*` vẫn còn dư từ request trước.

## Cảnh báo trung thực

Mọi con số tiết kiệm là **ước lượng** (4 ký tự/token). Tiếng Việt có dấu tốn nhiều
token hơn nên đây là ước lượng **thấp**. Kiểm lại bằng `token_audit.py` trước/sau mỗi nhóm.
