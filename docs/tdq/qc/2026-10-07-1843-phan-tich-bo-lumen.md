# QC — Phân tích: bỏ Lumen thì TDQ trên Claude Code và Codex còn chạy ổn không
Ngày: 2026-10-07 · Plan: ../plan/2026-10-07-1843-phan-tich-bo-lumen.md · Vòng: 1 · Mức QC: `full`
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

| # | Hạng mục | Lệnh đã chạy | Kết quả | PASS/FAIL |
|---|---|---|---|---|
| Q1 | Bản đồ phủ 51 file | vòng `grep -rIl -i lumen …` → `grep -qF <basename>` trong research | 51/51 (lần đầu 50/51, thiếu `uu-tien-tim-kiem-chi-tiet.md` → đã bổ sung) | PASS |
| Q2 | 12 câu/repo, 4 lần chạy đủ từng câu | `grep -c '^\| *[0-9]+ *\|'` trên 2 file câu hỏi + 4 file kết quả | 12 · 12 · 12 · 12 · 12 · 12 | PASS |
| Q3 | Kết luận theo luật định trước | `grep -c "KHÔNG giảm đáng kể" tong-hop.md` | 2 (một cho mỗi repo), kèm trúng/trượt + tỉ lệ token 0,88× và 1,06× | PASS |
| Q4 | Thử Claude Code có output thật | `grep -c "FINAL success\|claude -p" claude-code.md` | 3; phiên lần 3 `FINAL success`, 12 lượt | PASS |
| Q5 | Thử Codex có output thật | `grep -c "codex exec\|turn.completed" codex.md` | 2; `turn.completed`, đúng đích | PASS |
| Q6 | Script TDQ khi binary vắng không traceback | `grep -c Traceback script-tdq.md`; `grep exit=` | 0; exit 4 / 0 / 0 | PASS (lệch #1, chờ duyệt) |
| Q7 | Máy về như cũ | `diff sha-truoc.txt sha-sau.txt` | rỗng; `lumen@claude-plugins-official: true` | PASS |
| Q8 | Hồi quy | `tdq_test.py tron-bo` | `modules=129 failed=3` — đỏ: `test_codex_edit_gate.py test_codex_hooks_json.py test_finish_reindex.py` = đúng 3 module mốc | PASS |
| Q9 | Báo cáo đủ | đếm hàng kết luận host; đếm đề xuất thiếu liên kết | 2 hàng host (Claude Code, Codex); 0 đề xuất thiếu liên kết | PASS |
| QC-F1 | Trọn suite | `tdq_test.py tron-bo` + `tdq_test.py so` | 129 module, 3 đỏ mốc, 424 s; `full-suite runs: 2 of budget 3 · radius misses: 0` | PASS |
| QC-F2 | Hồi quy vùng chạm | plan không có dòng `Chạm:` | KHÔNG ÁP DỤNG — không task nào sửa file mã | PASS |
| QC-F3 | Ràng buộc kiến trúc | spec §5: "không chạm dòng nào" | `git status` chỉ thêm file trong `docs/tdq/` của request | PASS |
| QC-F4 | Clean code | — | KHÔNG ÁP DỤNG — không sửa file code | PASS |

Hợp đồng skill (plan): `tdq-setup` → cột luật chữ có ở research §3 · `lumen:doctor` → `chuan-bi.md` có `Status: OK` · `lumen:reindex` → `index_status` `Stale: no` cả 2 repo (ghi trong `chuan-bi.md`). `doc_lint` báo cáo + research: `0 violation(s)`.

## Bằng chứng
### Q1
```
phu: 50
thieu: ./skills/tdq-setup/references/uu-tien-tim-kiem-chi-tiet.md
(sau khi bổ sung) grep -c "uu-tien-tim-kiem-chi-tiet.md" research → 1  ⇒ 51/51
```
### Q2–Q7, Q9
```
Q2: cau-hoi-tdq-workflow.md 12 · cau-hoi-claudecodeui.md 12 · ket-qua-ccui-co.md 12 · ket-qua-ccui-khong.md 12 · ket-qua-tdq-co.md 12 · ket-qua-tdq-khong.md 12
Q3: 2
Q4: 3
Q5: 2
Q6: 0 · 31:exit=4 · 43:exit=0 · 67:exit=0
Q7: (diff rỗng)
Q9: 2 · 0
```
### Q8 / QC-F1
```
tdq_test: tron-bo modules=129 failed=3 missed=0 ok=False seconds=424.32
tron-bo: red modules: test_codex_edit_gate.py test_codex_hooks_json.py test_finish_reindex.py
full-suite runs: 2 of budget 3
radius misses: 0
```
Mốc trước khi làm (2026-10-07 18:4x, brief): cùng 3 module đỏ, cùng nguyên nhân (`.codex/hooks.json` chưa commit; test reindex phụ thuộc ollama — ollama đã được tắt lại về đúng trạng thái ban đầu trước lần chạy này).

## Lệch spec chờ duyệt
- #1 · Q6 · ngưỡng: `tdq_lsp check`, `tdq_finish`, `tdq_setup` chạy khi binary vắng · đo được: `tdq_setup.py main` KHÔNG chạy — nó cài phần thiếu, vá file hook của plugin khác và ghim khối luật vào instruction của user, vượt giới hạn "không sửa máy user" · phương án đã áp: chạy phần kiểm dùng chung (`kiem_mot_lenh`/`smoke_bon_tang` qua `tdq_lsp check`) + đọc mã phần dựng nền `lumen()` (`scripts/tdq_setup.py:676-693`).

## Kết luận
PASS toàn bộ (Q6 PASS có lệch #1 chờ user duyệt).
