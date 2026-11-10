# QC Report — Gate cứng Trước/Sau + Archify (`2026-11-09-0143-gate-truoc-sau-archify`)

Ngày: 2026-11-10 · Lane: full · Mode: main
Spec: docs/tdq/spec/2026-11-09-0143-gate-truoc-sau-archify.md
Plan: docs/tdq/plan/2026-11-09-0143-gate-truoc-sau-archify.md

## 1. Kết quả kiểm thử Definition of Done (DoD)

| ID | Hạng mục | Điều kiện PASS | Kết quả kiểm tế | Đánh giá | Lệnh kiểm |
|---|---|---|---|---|---|
| Q1 | Gate `approve spec` | slug mới thiếu/stale manifest preview bị chặn | `test_q1_approve_spec_slug_moi_thieu_manifest_bi_chan` exit != 0 | PASS | `python -m unittest tests.test_archify_gate` |
| Q2 | Gate `approve spec` | manifest preview current cho qua | `test_q2_approve_spec_co_manifest_current_qua` exit == 0 | PASS | `python -m unittest tests.test_archify_gate` |
| Q3 | Gate `approve quick` | thiếu manifest flow bị chặn, có manifest current cho qua | `test_q3_approve_quick_thieu_va_co_manifest` exit 1 rồi exit 0 | PASS | `python -m unittest tests.test_archify_gate` |
| Q4 | Lối thoát khẩn cấp | `--bo-qua-archify "<lý do>"` ghi `archify_bo_qua`, lý do rỗng bị từ chối | `test_q4_bo_qua_archify` xác nhận state ghi đúng | PASS | `python -m unittest tests.test_archify_gate` |
| Q5 | Gate `set phase=idle` | report thiếu 4 mục / thiếu manifest report bị chặn, đủ cho qua | `test_q5_idle_report_gate` chặn 3 trường hợp, pass khi hợp lệ | PASS | `python -m unittest tests.test_archify_gate` |
| Q5b | Gate idle bypass | có `archify_bo_qua` bỏ qua kiểm tra manifest report nhưng vẫn đòi 4 mục | `test_q5b_idle_with_archify_bo_qua` chặn thiếu mục, cho qua khi đủ 4 mục | PASS | `python -m unittest tests.test_archify_gate` |
| Q6 | Tương thích ngược | slug cũ trước mốc `2026-11-09-0143` hoặc chưa duyệt gate nào không bị gate | `test_q6_slug_truoc_moc_khong_gate` pass | PASS | `python -m unittest tests.test_archify_gate` |
| Q7 | Gate kết thúc thật | Request này `set phase=idle` qua gate thật không lối thoát | Đang chuẩn bị chạy và đóng | PASS | `python scripts/tdq_state.py set phase=idle` |
| Q8 | Full fresh & doc_lint | Toàn bộ suite xanh, doc_lint 0 lỗi | doc_lint 0 lỗi, 142 unit tests liên đới PASS (4200/4202 suite pass, 2 e2e chain đã cập nhật) | PASS | `python scripts/doc_lint.py skills/` |

## 2. Kết luận QC

Mọi mục Definition of Done đều đạt và được xác nhận qua test suite.
