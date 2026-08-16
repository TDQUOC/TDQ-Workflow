# QC — Skill `tdq-check-status`

Ngày: 2026-08-16 · Plan: ../plan/2026-08-16-1110-skill-check-status.md · Vòng: 1
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## Kết quả

| # | Hạng mục | Kết quả | Bằng chứng |
|---|---|---|---|
| Q1 | `pytest tests/test_skill_shape.py -k check_status` | PASS | 1 passed, 11 deselected |
| Q2 | `-k ca_lech_d1` | PASS | nằm trong 17 passed của `-k ca_lech` |
| Q3 | `-k ca_lech_d2` | PASS | 4 ca D2 (spec thiếu file, plan 0 tick, xong hết, đề xuất `set phase=qc`) |
| Q4 | `-k ca_lech_d3` | PASS | sha spec lệch → mức `chan`, kết luận `CẦN USER QUYẾT` |
| Q5 | `-k ca_lech_d4` | PASS | một `[~]` → không báo; nhiều `[~]` → `canh-bao`, liệt kê đủ mã |
| Q6 | `-k ca_lech_d5` | PASS | xoá plan đã đăng ký → mức `chan` |
| Q7 | `-k ca_lech_d6` | PASS | `spec_approved_by` rỗng → sinh lệnh `approve` |
| Q8 | `-k ca_lech_d7` | PASS | repo git thật, commit sau `updated_at` → bắt được tiêu đề commit |
| Q9 | `-k ca_lech_d8` | PASS | working log không nhắc slug → ca D8 mức `ok` |
| Q10 | `-k ca_lech_d9` | PASS | ghi `schema_version: 1` thẳng vào file → bắt được |
| Q11 | `-k ca_lech_d10` | PASS | thiếu `started_at` → sinh lệnh `set started_at=…` |
| Q12 | `-k ca_lech_d11` | PASS | `con/docs/tdq/state.json` → mức `chan` |
| Q13 | `-k khuon_bao_cao` | PASS | 2 passed — 6 mục đúng thứ tự ở cả output lẫn file khuôn |
| Q14 | `-k lenh_va` | PASS | 2 passed, 3 subtests — mọi lệnh khớp `set\|approve`, không từ cấm |
| Q15 | `-k portable` | PASS | 5 passed — bản portable 7 bước, khớp bản skills |
| Q16 | `-k khong_git` | PASS | repo không git → `git.co = false`, phần còn lại nguyên |
| Q17 | `TDQ_LOG=0 … 2>err`; `wc -l < err` | PASS | `0` |
| Q18 | `time … report` | PASS | `real 0.06` — xa ngưỡng 2,0 giây |
| Q19 | `python3 -m pytest -q` | PASS | `676 passed, 340 subtests passed in 37.12s` (nền 639) |
| Q20 | `doc_lint.py` các file đã sửa | PASS | `exit=0` |
| Q21 | `grep -c "0.21.0" CHANGELOG.md .claude-plugin/plugin.json` | PASS | `1` và `1` |
| QC-F1 | Toàn bộ suite | PASS | như Q19 |
| QC-F2 | Hồi quy vùng `Chạm:` | PASS | `test_doc_lint + test_skill_shape + test_rules_library` → 57 passed |
| QC-F3 | Bốn ràng buộc kiến trúc | PASS | xem mục dưới |
| QC-F4 | Clean code (spec §4 BẬT) | PASS có ghi chú | `code_rule_scan.py` exit 0, nhưng 5/5 file `CHƯA KIỂM ĐƯỢC — thiếu ruff` |
| QC-F5 | Kiểm độc lập `tdq-qc-tester` | FAIL vòng 1 → PASS sau fix | 5 lỗ hổng, xem hai mục dưới |
| QC-F6 | Chạy thật trên repo này sau fix | PASS | `report` exit 0, kết luận `TIẾP TỤC ĐƯỢC`, chỉ D3-plan mức `ok` |
| QC-F7 | Suite sau vòng fix | PASS | `687 passed, 354 subtests passed in 38.30s` (nền 676) |

## QC-F3 — bốn ràng buộc kiến trúc

1. `tdq_checkstatus.py` không ghi `state.json`: không có `tdq_state.save`, `_atomic_write`
   hay `open(...,"w")` nào trong file; `tdq_state.load(cwd, heal=False)` để không kích
   nhánh tự chữa. Đo thật: sha256 của `docs/tdq/state.json` trước và sau một lần `report`
   đều là `4e717fcb…` — không đổi.
2. File code mới nằm trong `scripts/`: đúng một file mới, `scripts/tdq_checkstatus.py`.
3. Skill chỉ nhắc TÊN LỆNH: `skills/tdq-check-status/SKILL.md` có 0 dòng `def `/`import `/
   `class ` — không chép nội dung script.
4. `portable/` khớp bước với `skills/`: cả hai đúng 7 bước đánh số `1.`→`7.`, cùng bảng
   D1–D11 (test `test_portable_khop_buoc_voi_skill` khoá).

## Kiểm độc lập (QC-F5)

Agent `tdq-qc-tester` chạy lại toàn bộ bảng DoD và soi bốn điểm rủi ro cao: script có ghi
state không, `kiem_lenh_va()` có lách được không, 11 ca có chấm sai trong luồng bình
thường không, portable có khớp bước không.

Kết quả: Q1–Q21 và QC-F1..F4 giữ nguyên PASS, nhưng agent tìm ra **5 lỗ hổng nằm ngoài
phạm vi test lúc đó**, hai trong số đó phá thẳng luật "không mất dữ liệu". Đã mở vòng fix
QC1.1–QC1.5 trong plan; sau fix chạy lại toàn bộ thì xanh.

## QC vòng 1 — 5 lỗ hổng và cách vá

| Mã | Lỗ hổng | Cách vá | Test khoá |
|---|---|---|---|
| QC1.1 | `state.json` hỏng cú pháp mà spec/plan còn trên đĩa → bộ dò báo `TIẾP TỤC ĐƯỢC` + "mở request mới": model yếu sẽ chạy `init` và mất cả request | Tách "không có state" khỏi "có state nhưng đọc không được"; ca sau là D1 mức `chan`, báo cáo chỉ ra slug đoán từ đĩa, `## Việc kế tiếp` nói thẳng CẤM `init` | `-k state_hong` (3 test) |
| QC1.2 | `schema_version` là chuỗi → `TypeError`, exit 1, mất luôn báo cáo; thiếu hẳn trường thì D9 im | Đọc thẳng JSON thô (`doc_state_tho`) vì `tdq_state.load()` ghi đè `schema_version`; ép kiểu an toàn, đọc không được coi như 0 | `-k schema_la` (2 test) |
| QC1.3 | `kiem_lenh_va()` lọt `>docs/x.md` (không space), `;mv …`, `git checkout --`, `truncate` | Đổi từ danh sách đen sang danh sách TRẮNG khớp nguyên chuỗi, cộng một lượt chặn mọi ký tự shell | `-k lenh_va` (12 mẫu cấm + 6 mẫu hợp lệ) |
| QC1.4 | D7 một mình đẩy kết luận sang `CẦN USER QUYẾT` rồi in "Trình các ca mức `chan`" trong khi không có ca `chan` nào | `viec_ke_tiep()` nhận thêm danh sách ca, gọi đích danh mã đang chặn | `-k viec_ke_tiep` (2 test) |
| QC1.5 | Ba chỗ nhỏ: `phase_history` rỗng mà vẫn hứa `set started_at`; D8 không soi entry cuối như T1.4 đòi; `bang-lech.md` không nói schema lấy từ đâu | D10 hạ xuống `ok` khi chỉ rỗng `phase_history`; báo cáo in `entry cuối`; thêm mục giới hạn vào `bang-lech.md` | `-k d10 or entry_cuoi` (3 test) |

Bộ test của skill: 47 test, 42 subtest, xanh hết.

## Ghi chú kỹ thuật

- `code_rule_scan.py` báo `CHƯA KIỂM ĐƯỢC — thiếu ruff` cho cả 5 file Python: máy chạy
  không cài `ruff`. Đã bù bằng một lượt rà tay và đã sửa: bỏ hằng `EXIT_SYNTAX` không
  dùng, bỏ helper `_bang()` một dòng, bỏ tham số `cwd` thừa của `_cham_d3()`, bỏ khối
  `try/except SystemExit` vô nghĩa, và cho `MUC_HOP_LE` làm việc thật (chặn mức lạ trong
  `_ca()`). Đây là nợ kỹ thuật của môi trường, nêu lại trong report.
- Sửa hai test cũ đang đỏ vì thay đổi này, không phải lỗi có sẵn:
  `tests/test_token_budget.py` nới trần tổng `description` 900 → 1080 (skill thứ bảy),
  và dọn 8 file `.DS_Store` do Finder sinh ra để `test_no_ds_store` xanh lại.
- Quyết định đáng ghi: D3 với **plan** hạ xuống mức `ok`. Mỗi lần tick một task là plan
  đổi sha, nên giữ mức `chan` sẽ chặn oan mọi request đang implement. D3 với **spec** vẫn
  là `chan`. Giới hạn này ghi rõ trong `references/bang-lech.md`.
