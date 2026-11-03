# QC — Báo cáo đề xuất 10 issue

Ngày: 2026-10-25 · Plan: ../plan/2026-10-25-1113-phan-tich-muoi-issue.md
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

Trạng thái cuối: kiểm chứng đầu ra TÀI LIỆU hoàn tất; toàn repo FAIL (9failures,2errors). Chỉ đề xuất, chưa fix. Không còn tác vụ kiểm nền; lifecycle vẫn paused do6worktrees Archify cũ, không giả đã qua gate qc/report.

## Mốc nguồn

T1.1: đã tạo và đọc lại snapshot 356 file nguồn/test/skill + .env.example trong `docs/tdq/2026-10-25-1113-phan-tich-muoi-issue.source-before.json`, chứa timestamp và HEAD. Bao gồm file chưa tracked, bỏ pycache/pyc/pyo. Đây là mốc đầu implement; không có sửa source được thực hiện trong analyze.

## Inventory và baseline kế thừa

Nguồn chung: `docs/tdq/archify-qc-after-fix-stderr.log`, QC Archify và đối chứng a03d698/5d6570d đã lưu. Lượt đó: 2974 tests,9 failures,1 error,10 skipped; KHÔNG tính là full suite của request mới.

| ID | Test ID |
|---|---|
| I01 | test_luat_gate_chat.NextStepTest.test_next_step_moi_dong_neu_duoc_pha_ke |
| I02 | test_reference_mot_tang.MotTang.test_moi_reference_duoc_skill_md_tro_thang |
| I03 | test_reference_mot_tang.KhongLinkChet.test_khong_link_nao_tro_vao_hu_khong |
| I04 | test_skill_shape.SkillShapeTest.test_exactly_six_skills |
| I05 | test_token_budget.TokenBudgetTest.test_skill_descriptions_total |
| I06 | test_utf8_io.EntryPointTest.test_entrypoint_moi_file_deu_toi_duoc_utf8_io |
| I07 | test_vision_test_loop_doc.TestVisionTestLoopDoc.test_tier1_wiring_across_skills |
| I08 | test_reminder_contract.SearchGateDenialRepeatTest.test_search_gate_repeat_denial_shorter_and_preserves_recovery |
| I09 | test_tdq_test.CaDaDoTest.test_ban_kinh_ca_da_do_ask_gate_nho |
| I10 | test_tuong_thich_host.TuongThichAgy.test_tuyet_doi |

Analyze mới đã tái hiện I08/I09/I10: 3 failed trong1.65s. Probe search_rules: analyze allow=True, implement allow=False. Probe naive path split: mất prefix khi có khoảng trắng dù actual path là absolute. Đây là chẩn đoán, không chứng minh patch đã chạy.

## Bảo toàn Archify

Snapshot `docs/tdq/2026-10-24-2348-hoan-thien-archify.resume.json` và hướng dẫn resume đã tồn tại. Không sửa snapshot, không phục hồi active request, không dọn worktree. T1.1 hoàn tất khóa mốc và inventory.

## Kiểm thực hiện trong request này

- T1.2: C1 xác nhận đủ10 hồ sơ và8 trường/mục; C2 xác nhận path/line tồn tại. Đối chiếu thủ công assertions với policy/producer: I08 phase analyze được allow, I09 textual dependency có cả docstring, I10 generator quote nhưng consumer split sai. Không sửa code để chứng minh giả thuyết.
- T2.1: C1/C2/C3/C5 đều exit0; lint report/QC0violations. Nội dung có phương án chọn/loại, âm/dương, ảnh hưởng và rollback cho mỗi issue; Mermaid kèm bảng tương đương, chưa render/browser audit và không dùng làm bằng chứng UI.
- I05: đo4 câu ứng viên đúng nội dung báo cáo:134/126/137/138 ký tự; tổng11 descriptions nếu thay=1709, giữ7 câu còn lại. Source thực vẫn2051. Không ghi ứng viên vào SKILL.md hoặc tuyên bố router sau patch PASS.
- T3.1 targeted: `python -m pytest tests/test_luat_gate_chat.py tests/test_reference_mot_tang.py tests/test_skill_shape.py tests/test_token_budget.py tests/test_utf8_io.py tests/test_vision_test_loop_doc.py tests/test_reminder_contract.py tests/test_tdq_test.py tests/test_tuong_thich_host.py -q --tb=short` → **10 failed,116 passed,2 subtests passed in15.18s**, exit1. Log `docs/tdq/2026-10-25-1113-phan-tich-muoi-issue-tests.log`; đúng10 IDs inventory, không phát sinh ID mới ở nhóm này.
- Full suite đã khởi chạy non-elevated, chưa có kết quả. Stdout/stderr/status riêng: `docs/tdq/2026-10-25-1113-full-stdout.log`, `docs/tdq/2026-10-25-1113-full-stderr.log`, `docs/tdq/2026-10-25-1113-full-status.log`. Không ghi đè log Archify, không chạy suite thứ hai đồng thời.

## Kết quả cuối bổ sung

Full suite đã kết thúc: `Ran 2974 tests in 637.997s`, `FAILED (failures=9, errors=2, skipped=10)`, exit1, Elevated=False.10 lỗi khớp inventory; thêm error ở `tests/test_tu_khoi_tao.py:482`: WinError32 khi os.remove da-chay.txt, process khác còn giữ file. Rerun riêng đúng test đạt kết quả1failed trong0.57s, chưa có đối chứng baseline cho lỗi bổ sung; không suy là regression từ tài liệu hoặc lỗi nền đã chứng minh. Giữ ngoài phạm vi10issue, ghi phát hiện chứ không fix.

C1/C2/C3/C5 sau full suite exit0;356file nguồn giữ nguyên. Snapshot và hướng dẫn resume còn nguyên. Ledger1tron-bo/0radius misses; không có vung-cham được ghi nên0misses không là bảo đảm coverage, QC-F2 có targeted9modules độc lập.

Review nội dung: mỗi issue có cơ chế lỗi và8 trường, không chỉ đo đủ heading; I08 giữ miễn gate exploratory, I09 không loại caller để giảm số, I10 không bỏ quoting producer; descriptions ứng viên giữ trigger quan trọng nhưng chưa tuyên bố routing hậu sửa đạt. Phát hiện ngoài scope được ghi rõ, không thay inventory.

## Bảng QC cuối

| Mục | Trạng thái | Bằng chứng |
|---|---|---|
| Q1 | PASS nội dung | C1 đủ10×8 trường, review từng issue |
| Q2 | PASS nội dung | C2 path/line thật; facts tách proposals/uncertainty |
| Q3 | PASS nội dung | Không tăng cap/bỏ assert; I09 đề xuất thay bằng fixture coverage tương đương, chưa áp dụng; có thứ tự và ca âm/dương |
| Q4 | PASS về tính đầy đủ bằng chứng, sản phẩm FAIL | Full/targeted đã kết thúc; lưu exit1,10issue và lỗi WinError32 bổ sung, không giả PASS |
| Q5 | PASS | C5 sau suite so hash356file bằng snapshot; resume đủ descriptor |
| Q6 | PASS sau lint cuối | Tài liệu phân biệt hiện trạng/đề xuất, có links và glossary trong spec |
| QC-F1 | FAIL | 2974tests,9failures,2errors,10skipped; không sửa trong request docs |
| QC-F2 | FAIL sản phẩm / đủ evidence chẩn đoán | Targeted10failed116passed2subtests, IDs khớp baseline |
| QC-F3 | PASS tại mốc13:19 | Chỉ tài liệu; nguồn giữ nguyên; state qua CLI |
| QC-F4 | KHÔNG ÁP DỤNG với source | Không code mới; tài liệu đã review không lặp kết luận thiếu căn cứ |

## Điểm chặn quy trình

Lệnh chuyển phase qc ngày2026-10-25 13:21 trả exit2 vì6worktrees Archify cũ còn mở. Không phải task của request tài liệu; không tự xóa/commit và không sửa state thẳng để vượt gate. Có thể hoàn tất nội dung/bằng chứng nhưng lifecycle chưa đóng cho tới khi giải quyết gate an toàn. Full suite vẫn được theo dõi đến kết quả cuối, không coi im lặng là PASS.
