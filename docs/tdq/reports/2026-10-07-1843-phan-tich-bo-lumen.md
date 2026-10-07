# REPORT — Phân tích bỏ Lumen (`2026-10-07-1843-phan-tich-bo-lumen` · lane full · mode main · 15 task tick đủ)

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

**Đã làm:** bản đồ 51 file phụ thuộc lumen · đo 12 câu × 2 repo × có/không lumen (4 agent) · chạy thử Claude Code (`--settings` tắt lumen) và Codex (`-c` lumen trỏ binary không tồn tại) trên bản sao tạm · chạy script TDQ với bộ dò binary vá rỗng · báo cáo kết luận + 7 đề xuất sửa
**Kết quả:** Claude Code CÓ chạy ổn (thừa ~4 lượt ở lần tìm đầu) · Codex CÓ chạy ổn (không lỗi khởi động) · chất lượng tìm KHÔNG giảm đáng kể: trượt chênh 1/12, token 0,88× (TDQ) và 1,06× (claudecodeui) · 4 câu luật GÃY (chấm oan), 9 điểm ỒN, 0 traceback
**Kiểm:** `tdq_test.py tron-bo` 129 module, 3 đỏ = đúng 3 module mốc · `doc_lint` 0 vi phạm · QC PASS 9/9 DoD + F1–F4
**Đầu ra:** `docs/tdq/report/2026-10-07-1843-phan-tich-bo-lumen.md` (kết luận + đề xuất) · `docs/tdq/research/2026-10-07-1843-phan-tich-bo-lumen.md` · `docs/tdq/bench/2026-10-07-1843-*/`
**Giới hạn:** bộ câu do agent soạn bằng grep (thiên về grep) · hook TDQ không chạy trong Codex nên search gate Codex chưa được thử · Codex Windows chặn mọi lệnh shell (`blocked by policy`) — cả hai là tình trạng sẵn có, không do lumen
**Lệch spec chờ duyệt:** #1 · Q6 · `tdq_setup` chạy khi vắng binary → không chạy `main` (cài/vá file plugin khác) · đã chạy phần kiểm dùng chung + đọc mã phần dựng nền
**Git:** chưa commit · chưa mở nhánh request (cây git bẩn từ trước, chờ user dọn)

## Thời gian

| Phase | Wall clock | Model time | Times entered |
|---|---|---|---|
| idle | 7s | — | 1 |
| analyze | 50 min | — | 1 |
| spec | 2 min | — | 1 |
| plan | 22 min | — | 1 |
| implement | 20 min | — | 1 |
| qc | 50s | — | 1 |
| report | 6s | — | 1 |
| **Total** | **1h 33min** | **—** | |

Cột model là `—`: không đọc được transcript của phiên.
