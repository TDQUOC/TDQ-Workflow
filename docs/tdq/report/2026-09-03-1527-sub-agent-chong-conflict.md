# REPORT — Chống conflict khi chạy sub-agent implement (`2026-09-03-1527-sub-agent-chong-conflict` · lane full · mode main · 20/20 task tick đủ)

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

**Đã làm:** P0 — đổi 22 sub-command của 5 script CLI sang tên tiếng Anh, tên cũ thành bí danh
ẩn giải ở tầng argv nên `--help` chỉ in tên mới mà hook/bundle/tài liệu cũ vẫn chạy · P1 —
`check` chạy thật lệnh `Test:` của task trong worktree của nó, `merge` từ chối nhánh có test đỏ
· P2 — dòng `Chạm:` thành hàng rào máy: agent con ghi ra ngoài vùng đã khai thì bị chặn ngay lúc
ghi, không phải lúc merge · P3 — `merge` tự rebase lên bản tích hợp mới nhất trước, hỏng thì
`rebase --abort` trả worktree về nguyên trạng; thêm lệnh `resolve` chỉ đọc, in hai phía từng
file kẹt · P4 — `assign` phát hiện và cảnh báo file nóng trước khi mở nhánh nào · P5 — cập nhật
`team-mode.md`, `plan-template.md`, `tdq-implementer.md` và dựng lại 3 bundle portable · P6 —
4 nhánh quyết định mới đều ghi log, tắt được bằng `TDQ_LOG=0`.

**Kết quả:** năm lỗ hổng H1–H5 từ chỗ chỉ là câu chữ trong tài liệu → đều có hàng rào máy:
lời tự khai `TICK-READY` bị kiểm lại bằng chính lệnh test của task · base cũ được rebase tự động
thay vì để conflict nổ lúc merge · conflict có đường gỡ (`resolve`) thay vì chỉ bị chặn · ghi
ngoài vùng bị chặn tại chỗ · file nóng được nêu tên ở `assign`, lúc mà cách sửa còn rẻ. Bộ test
mới: 0 → 41 ca.

**Kiểm:** `pytest -q` 100 failed / 1518 passed, ĐÚNG BẰNG mốc đỏ 100 có sẵn trên HEAD sạch
(đối chiếu bằng `git stash -u`) · QC PASS 19/19 hạng mục (15 dòng DoD + QC-F1→F4), không phải mở
vòng fix nào · `tdq_checkportable.py check` CLEAN cả 3 bundle (93 / 143 / 86 file) ·
`doc_lint.py` exit 0 trên mọi `.md` đã sửa.

**Đầu ra:** `scripts/tdq_team.py` (`resolve`, `_rebase_len_tich_hop`, `_kiem_test_cua_task`,
`ngoai_vung_khai`, `_file_nong`) · `scripts/tdq_ten_lenh.py` (bảng tên, một nguồn sự thật) ·
`hooks/scripts/edit_gate.py` (khối 2c) · `scripts/tdq_worktree_registry.py` (3 lý do chặn mới) ·
`tests/test_team_chong_conflict.py` (41 ca) · `skills/tdq-build/references/team-mode.md` ·
`skills/tdq-plan/references/plan-template.md` · `agents/tdq-implementer.md` ·
`docs/tdq/qc/2026-09-03-1527-sub-agent-chong-conflict.md` · 3 bundle portable.

**Ngoài dự kiến, đã sửa tận gốc (không nới test):** `tests/test_tdq_eval.py` + `evals/tuan-thu/README.md`
còn tên cũ ở chỗ khai trực tiếp `build_parser` · `docs/tdq/audit/luat-hien-co.md` neo 4 luật
(L006, L007, L094, L096) vào câu chữ trước khi đổi tên · `scripts/tdq_bench.py` sinh plan mẫu có
`Test:` là câu chữ chứ không phải lệnh, nên bị chính hàng rào H5 từ chối — plan mẫu nay khai
`Test: \`true\``.

**Còn treo, không nằm trong request:** hai khoá Tavily lộ trong lịch sử public
(`docs/tdq/audit/settings-backup-2026-08-19.json`) vẫn chờ user tự xoay vòng · bảng `## Cấu trúc`
của README còn ghi `skills/ (6)` trong khi thực tế có 8 skill.
