# REPORT — Luôn tổ chức modular, ưu tiên sub-agent song song (`2026-08-18-1744-uu-tien-subagent-song-song` · lane full · mode main · 39/39 task tick đủ)

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

**Đã làm:** tách yêu cầu làm hai vế — modular hoá TÀI LIỆU áp vô điều kiện (spec có §2b ranh giới module, plan luôn khai `Chạm:` + `## Cụm song song`, rule R10 của `doc_lint`), còn chạy song song thì có ngưỡng đo được · thay "phase làm proxy phụ thuộc" bằng đồ thị `Cần:` thật trong `tdq_team.py`: xếp đợt tô-pô, ưu tiên đường găng theo b-level, phát liên tục thay vì chờ hết đợt, trần 4 nhánh đếm cả task đang bay · gỡ khoá doctrine leader khỏi `implement_mode = subagent` (mode `main` = leader tự làm hết nhưng theo thứ tự cụm, ghi lý do giữ) · thêm `hop-dong` vào tập lý do giữ (5 nhóm, tập ĐÓNG) · cổng đề xuất mode không đoán bằng mắt nữa mà chạy `tdq_bench.py mo-phong --he-so-agent 1.5` · lane quick được sinh agent con khi có ≥3 task `Chạm:` rời nhau · vá `edit_gate` chặn nhầm file ngoài project (cả `TDQ:TICK` lẫn `TDQ:TEAM`).
**Kết quả:** số đợt của plan CÓ khai `Cần:` 18 → 10 (giảm 44%) · ba plan cũ không khai: 6→6, 13→13, 10→10 — không cải thiện, đúng thiết kế "không phá plan cũ" nhưng lợi ích chỉ đến khi khuôn mới được dùng thật · test suite 704 → 975 test.
**Kiểm:** `pytest -q` 975 passed, 1240 subtests, 0 đỏ · `doc_lint.py` exit 0 trên mọi file đã sửa, `--pair spec plan` exit 0 · QC 19/19 hạng mục DoD + 4 hạng mục hồi quy PASS; Q19 (agent `tdq-qc-tester` độc lập) vòng 1 FAIL 12 defect → kiểm lại từng cái, 10 thành QC1.1–QC1.10 và đã vá hết, vòng fix 1/3.
**Đầu ra:** `scripts/tdq_team.py` · `scripts/doc_lint.py` · `hooks/scripts/edit_gate.py` · `skills/tdq-{spec,plan,build,intake}/**` · `tests/test_uu_tien_song_song.py` + `tests/test_team_mode.py` · `docs/tdq/{spec,plan,qc}/2026-08-18-1744-*.md` · `docs/tdq/audit/luat-hien-co.md`.
**Giới hạn:** bật rule R10 làm 57 spec CŨ phải nhận dòng `<!-- doc-lint: allow R10 ... -->` — thay đổi diện rộng nằm ngoài dòng `Chạm:` của mọi task, chỉ là miễn trừ lint chứ không đổi nội dung spec · lợi ích lịch trình bằng 0 với plan không khai `Cần:` · số 1,5× (agent con chậm hơn leader) là giả định bảo thủ lấy từ smoke test cũ, chưa đo lại trên request này · T3.3 và T3.5 viết impl và test cùng bước, không đúng red→green nghiêm ngặt.
**Git:** chưa commit — không có commit gỡ chặn nào trong build này.

## Thời gian

| Phase | Treo tường | Model chạy | Số lần vào |
|---|---|---|---|
| idle | 1 giây | 0 giây | 1 |
| analyze | 13 phút | 13 phút | 1 |
| spec | 12 phút | 12 phút | 1 |
| plan | 1 giờ 27 phút | 4 phút | 1 |
| implement | 28 phút | 28 phút | 1 |
| qc | 22 phút | 22 phút | 1 |
| report | 0 giây | 0 giây | 1 |
| **Tổng** | **2 giờ 43 phút** | **1 giờ 19 phút** | |

Lệch lớn ở phase `plan` (1 giờ 27 treo tường so với 4 phút model chạy) là thời gian CHỜ user duyệt, không phải thời gian làm.
