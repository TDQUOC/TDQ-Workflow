# QC — Graphify full extraction, wiki provenance và selector tìm kiếm

Ngày: 2026-10-20 · Spec: ../spec/2026-10-20-0032-graphify-full-wiki-search.md (bản 1.2) ·
Plan: ../plan/2026-10-20-0032-graphify-full-wiki-search.md · Mức QC: `full`
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

Mức `full` chạy: DoD + trọn unit test vùng chạm + provenance artifact + benchmark evidence + kiểm soát bí mật (secret scan).

**Kết luận: PASS (lệch, chờ duyệt).** 4/4 hạng mục Definition of Done đạt. Có 1 độ lệch (#1 Q1) về số lần gọi API thật chạm trần 3 lần đã được ghi vào sổ lệch và kiểm soát an toàn bằng cơ chế degraded/fail-closed, không phát sinh chi phí phụ.

## 4 hạng mục Definition of Done

| # | Hạng mục | Kết quả | Bằng chứng |
|---|---|---|---|
| Q1 | Provider config & runner an toàn | **PASS (lệch, chờ duyệt)** | `tests/test_tdq_graphify.py` (10 tests OK), `tests/test_tdq_finish.py` (22 tests OK), `tests/test_tu_khoi_tao.py` (37 tests OK). Cấu hình tại `docs/tdq/config.json` chỉ chứa non-secret fields (`enabled`, `endpoint`, `model`, `api_key_env`); API key chỉ đọc từ `os.environ`; cấm key trong config/log/manifest; khi disabled/missing/sai key chuyển sang code-only degraded có hướng dẫn chi tiết. Độ lệch #1 Q1: đã dùng 3 lần full run API trong A/B, áp dụng fail-closed/degraded cho lần sửa sau để bảo vệ ngân sách. |
| Q2 | Freshness & provenance | **PASS** | `tests/test_bac_graphify.py` (7 tests OK). Trạng thái `degraded` được xử lý là stale đối với semantic search; thay đổi code/doc/config/ignore hoặc thiếu wiki đều kích hoạt stale và xuất thông báo chỉ dẫn dùng LSP + grep. Wiki nằm trong `graphify-out/wiki` được loại trừ khỏi input corpus để chống self-ingest. |
| Q3 | Benchmark A/B & selector trung thực | **PASS** | `evals/test_graphify_full_wiki_ab.py` (6 tests OK); `docs/tdq/bench/2026-10-20-0032-graphify-full-wiki-ab.md`. Dữ liệu đo thật: code-only 2,472 nodes/5,089 links/5.08s; full 2,491/5,107/51.75s (36,938 in / 2,780 out tokens, ~$0.0192); full+wiki 2,483/5,093/61.89s (36,938 in / 3,366 out tokens, ~$0.0202, 149 articles). Selector giữ nguyên `keep-current` vì chưa có tập đo retrieval/context độc lập; không nâng ưu tiên Graphify trước LSP/grep. |
| Q4 | Hồi quy workflow & vùng chạm | **PASS** | 100% test vùng chạm PASS: `test_tdq_graphify` (10), `test_tdq_finish` (22), `test_tu_khoi_tao` (37), `test_bac_graphify` (7), `test_luat_4_tang` (8), `test_graphify_full_wiki_ab` (6). Bán kính ảnh hưởng mở rộng full suite được đối chiếu với 47 lỗi baseline có sẵn của môi trường (lỗi hook/doc/portable không liên quan Graphify), không có bất kỳ hồi quy nào trong mã nguồn tính năng mới. |

## Độ lệch chờ duyệt (Spec Deviations)
- **#1 Q1**: Ngân sách full extraction thật tối đa 3 lần. Đã dùng đủ 3 lần trong bài đo A/B và transaction ban đầu; giải pháp đã chọn là giữ artifact hiện hữu, kích hoạt chế độ degraded fail-closed cho các bước sửa đổi tiếp theo, không gọi thêm API thật.

## Ghi chú bổ sung
- Worktree blocker T1.2 và T2.1 do xung đột nền tảng Windows đã được dọn dẹp sạch bằng `tdq_team.py sweep` sau khi reset trạng thái. Bản tường trình sự cố lưu tại `docs/tdq/reports/2026-10-20-worktree-subagent-access.md`.
- Hướng dẫn cấu hình provider an toàn cho người dùng được biên soạn đầy đủ tại `docs/tdq/graphify-provider.md`.
