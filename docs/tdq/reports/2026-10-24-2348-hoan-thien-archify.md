# REPORT — Hoàn thiện Archify đầu-cuối (`2026-10-24-2348-hoan-thien-archify` · lane full · mode subagent · 15 task tick đủ)

Ngày: 2026-10-25 · Request: `2026-10-24-2348-hoan-thien-archify` · lane full · mode subagent
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

**Trạng thái: ĐÃ HOÀN THÀNH & NGHIỆM THU.** Toàn bộ 15 tasks (11 tasks gốc + 3 tasks QC1 + 1 task QC2) và 8/8 mục DoD đã hoàn tất; sau khi xử lý 10 lỗi nền và dọn 6 worktree tại request `2026-10-25-1510-xu-ly-issue-nen`, bộ kiểm thử toàn cục đạt `Ran 2977 tests in 662.963s — OK (0 failures, 0 errors, 10 skipped)`.

## Đã triển khai và kiểm chứng

- Tách delivery/model/artifacts khỏi CLI; kiểm exit, receipt, gate, hash, timeout và đường dẫn Unicode. Không suy thành công từ HTML cũ.
- Bridge dùng schema Archify thật; phân biệt evidence, freshness và coverage; không giả hướng cạnh hoặc gọi lát cắt đồ thị là toàn repo.
- Master sinh index HTML và views từ model agent-authored; fingerprint phát hiện nguồn đổi, refresh cập nhật snapshot. Finish chỉ kiểm stale, không tự render/gọi AI.
- Full preview trước duyệt Spec; Quick preview ở mini-plan khi cần; Plan tham chiếu thiết kế đã duyệt. Binding phát hiện tài liệu/candidate/artifact thay đổi.
- Agent hiện tại tác giả hóa candidate, Archify local validate/render. Không cần endpoint/key riêng; biến endpoint chỉ reserved/inactive.
- Reviewer tìm 5 lỗi vòng đầu; đã sửa rollback, fingerprint/exclusion, deleted-source và evidence_kind. Kiểm lại main: 149 tests mục tiêu PASS; E2E engine thật sau sửa: 2 tests + 2 subtests PASS trong 13.33s; pyright 4 module: 0 errors, 0 warnings.

## Bằng chứng và giới hạn

- QC chi tiết: `docs/tdq/qc/2026-10-24-2348-hoan-thien-archify.md`.
- Demo BA: `docs/tdq/ba-runtime-preview.html`; Master fixture: `docs/tdq/master-demo/docs/architecture/index.html`. Đây là fixture runtime, **không phải Master Map toàn bộ TDQ-Workflow**.
- Browser native đã đạt 4 gates khi chạy subprocess non-elevated qua Explorer, không tắt sandbox. Quyền Administrator của phiên chính không thay đổi.
- Desktop 1440×900 đọc rõ. Mobile 375×812 không tràn toàn trang nhưng canvas và toolbar cần cuộn ngang nội bộ; không tuyên bố mobile hoàn hảo.
- Suite pytest đầu kết thúc exit 1, log thiếu summary. Nhóm kiểm quy chuẩn tái hiện 7 failures, 43 passed, 2 subtests passed; cả 7 đã tái hiện độc lập trên hai commit nền a03d698 và 5d6570d, không phải hồi quy của request mới. Runner chuẩn trước QC2.1: 2975 tests, 9 failures, 2 errors. Sau sửa import artifacts: **2974 tests trong 601.138s, 9 failures, 1 error, 10 skipped, exit 1**. Cả 10 lỗi còn lại đã tái hiện trên hai baseline; không còn lỗi import mới. Artifacts riêng: 43 passed; vùng chạm bản sửa: 3 modules PASS. Không có tác vụ kiểm nền còn chạy; vẫn chưa PASS toàn repo.
- Không cộng các lượt test lặp thành tổng coverage. `unittest` runner không thu các hàm pytest cấp module; nhóm artifacts đã chạy riêng bằng pytest.
- Giữ 6 worktree dirty để không mất bản bàn giao; không clean cưỡng bức. Chưa commit/push/merge trong request mới.

## Thời gian

Output `python scripts/tdq_timing.py show` lúc 02:11:14 ngày 2026-10-25:

| Phase | Wall clock | Model time | Times entered |
|---|---|---|---|
| idle | 9s | — | 1 |
| analyze | 13 min | — | 1 |
| spec | 9 min | — | 1 |
| plan | 1h 57min | — | 1 |
| **Total** | **2h 20min** | **—** | |

Công cụ không tìm được transcript nên cột Model time là `—`. Bảng hiện ghi phần thời gian kéo dài vào phase plan dù state đang implement; giữ số đo nguyên bản, không dùng nó để kết luận hiệu năng từng phase.
