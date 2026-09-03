# QC — Chống conflict khi chạy sub-agent implement
Ngày: 2026-09-03 · Plan: ../plan/2026-09-03-1527-sub-agent-chong-conflict.md · Vòng: 1
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

15 dòng DoD → Q1–Q15, cộng 4 hạng mục cố định QC-F1→F4.

| # | Hạng mục | Lệnh đã chạy | Kết quả | PASS/FAIL |
|---|---|---|---|---|
| Q1 | Cổng vùng file chặn ghi ngoài `Chạm:` | `pytest tests/test_team_chong_conflict.py -k gate_chan_ngoai_vung` | 2 passed | PASS |
| Q2 | Cổng vùng file KHÔNG chặn ghi trong vùng | `pytest ... -k ngoai_vung` | 9 passed | PASS |
| Q3 | Mode `main` không đổi hành vi | `pytest tests/test_edit_gate.py -q` | 32 passed | PASS |
| Q4 | `check` chạy thật lệnh kiểm và nêu tên lệnh | `pytest ... -k kiem_chay_test` | 2 passed | PASS |
| Q5 | `merge` chặn khi test task đỏ | `pytest ... -k hop_chan_test_do` | 1 passed | PASS |
| Q6 | `merge` tự rebase khi base đã cũ | `pytest ... -k rebase` | 3 passed | PASS |
| Q7 | Rebase hỏng thì worktree về nguyên trạng | `pytest ... -k rebase_hong` | 1 passed | PASS |
| Q8 | Lệnh `resolve` nêu đủ thông tin để gỡ | `pytest ... -k lenh_resolve` | 3 passed | PASS |
| Q9 | `assign` cảnh báo file nóng | `pytest ... -k file_nong` | 3 passed | PASS |
| Q10 | Ba file luật khớp code | `doc_lint.py team-mode.md plan-template.md tdq-implementer.md` | 0 violation, exit 0 | PASS |
| Q11 | Bộ test đội hình cũ không thêm ca đỏ | `pytest tests/test_team_mode.py tests/test_edit_gate.py -q` | 176 passed | PASS |
| Q12 | Mốc đỏ toàn bộ không vượt 100 | `pytest -q` | 100 failed, 1518 passed — đúng bằng mốc nền HEAD | PASS |
| Q13 | Tên lệnh tiếng Anh chạy đúng ở cả 5 script | `pytest ... -k doi_ten` | 12 passed, 1 skipped | PASS |
| Q14 | Mọi tên cũ vẫn chạy qua bí danh | `pytest tests/test_team_mode.py -q` | 144 passed | PASS |
| Q15 | Không còn tên cũ trong `skills/`+`hooks/`+`agents/` | `grep -rn "phan-cong\|kiem-ke\|mo-phong" skills hooks agents \| grep -v ten-lenh` | 2 dòng, cả hai KHÔNG phải tên lệnh — xem Bằng chứng | PASS |
| QC-F1 | Toàn bộ test suite | `pytest -q` | 100 failed / 1518 passed / 1432 subtests, 123 s | PASS |
| QC-F2 | Regression vùng `Chạm:` | `pytest` trên 5 file test của vùng chạm | 295 passed, 1 skipped | PASS |
| QC-F3 | Ràng buộc kiến trúc spec §5 | xem `## Bằng chứng` | 3/3 giữ nguyên | PASS |
| QC-F4 | Clean code — 5 câu tự kiểm | xem `## Bằng chứng` | 5/5 yes | PASS |

## Bằng chứng

**Q12 — mốc đỏ.** Chạy `pytest -q` trên HEAD sạch (`git stash -u`) ra đúng 100 đỏ với 4 ca:
`test_bench.py::ThucDoTest::test_repo_that_khong_moc_nhanh_hay_worktree_nao` (nhánh thừa
`tdq/2026-08-23-1623-mindmap-html-hai-lop/tich-hop` còn sót trong repo thật),
`test_luat_skill.py::test_so_dong_ghi_trong_bang_van_tro_dung_cho`,
`test_rules_library.py::ChiMuc::test_chi_muc`,
`test_skill_router.py::test_so_ban_ghi_khop_skill_inventory`. Sau request vẫn đúng 4 ca đó,
không thêm ca nào — request này không sinh ca đỏ mới.

**Q15 — hai dòng còn lại là gì.**
`skills/tdq-intake/references/quick-lane.md:46` là TÊN FILE báo cáo
(`2026-09-01-2122-lane-nhanh-kiem-ke-nang-luc.md`), không phải lệnh.
`hooks/scripts/edit_gate.py:123` là MÃ LÝ DO `chua-phan-cong` trong tập lý do đóng, không phải
tên sub-command. Cùng luật với `mo`/`dong` của sổ worktree và `vung-khoa`: giá trị dữ liệu giữ
tiếng Việt, chỉ tên lệnh đổi sang tiếng Anh.

**Ba hồi quy phát sinh giữa chừng, đã sửa tận gốc (không nới test):**
1. `tests/test_tdq_eval.py` còn giữ tên cũ trong 6 chỗ khai trực tiếp `build_parser` — sửa
   literal sang `setup/run/score/report`, và sửa `evals/tuan-thu/README.md` dùng tên mới.
2. `docs/tdq/audit/luat-hien-co.md` neo 4 luật (L006, L007, L094, L096) vào câu chữ cũ của
   `tdq-build/SKILL.md` và `team-mode.md` — cập nhật cột neo bản mới cho khớp file thật.
3. `scripts/tdq_bench.py` sinh plan mẫu với `Test:` là câu chữ chứ không phải lệnh, nên
   `check` mới (H5) từ chối đúng luật và làm hỏng 5 ca `ThucDoTest`. Sửa plan mẫu thành
   `Test: \`true\`` — plan mẫu phải khai được lệnh kiểm như mọi plan thật.

**QC-F3 — ràng buộc kiến trúc spec §5.**
- Tập lý do chặn vẫn ĐÓNG: 3 lý do mới (`rebase-hong`, `test-code`, `test-plan`) đăng ký trong
  `LY_DO_CHAN` kèm ít nhất một option chạy được.
- `ngoai_vung_khai` nuốt mọi exception và trả `None` ngoài worktree task → hook không bao giờ
  chết vì nó, mode `main` không đổi hành vi (Q3).
- `resolve` chỉ đọc: in hai phía của từng file kẹt, không đụng repo.

**QC-F4 — 5 câu tự kiểm.**
1. Có hàm nào >60 dòng không? Không — hàm dài nhất mới thêm là `lenh_hop` (đã có sẵn, thêm 12 dòng).
2. Có logic lặp copy-paste không? Không — `_kiem_test_cua_task` dùng chung cho `check` và `merge`.
3. Có tên biến mơ hồ không? Không — theo đúng lối đặt tên đang có của `tdq_team.py`.
4. Có magic number không? Không.
5. Có nhánh nào không test không? Không — mỗi hành vi máy §2 có ≥1 ca, tổng 41 ca trong file test mới.
