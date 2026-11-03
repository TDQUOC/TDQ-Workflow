# QC — Bỏ cổng clean code, xoá script scan

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

Ngày: 2026-08-16 · Vòng: 1 · Slug: `2026-08-16-1300-bo-cong-clean-code`

## Bảng hạng mục

| # | Hạng mục | Kết quả | Bằng chứng |
|---|---|---|---|
| Q1 | File luật đủ khuôn 3 mục | PASS | `doc_lint.py skills/tdq-conventions/references/clean-code.md` exit 0 |
| Q2 | Bảng 5 luật đủ mã, đủ hai cột | PASS | `pytest -k bang_solid` xanh; SRP OCP LSP ISP DIP đều có dòng bảng |
| Q3 | Ví dụ ĐÚNG/SAI từ file thật | PASS | `pytest -k vi_du` xanh; mọi đường dẫn trong ví dụ đều `is_file()` |
| Q4 | LSP có nhãn giới hạn, đánh dấu suy diễn | PASS | `pytest -k lsp_gioi_han` xanh |
| Q5 | Checklist đúng 5 câu có/không | PASS | `pytest -k checklist` xanh (TuKiem: 5 câu, mỗi câu một dòng) |
| Q6 | Conventions nạp luật mới | PASS | `pytest -k conventions_nap` xanh; §11 SKILL.md trỏ `references/clean-code.md` |
| Q7 | Cổng hỏi biến mất khỏi khuôn spec | PASS | `grep -c "Khuôn hỏi clean code"` → SKILL.md 0 · spec-template.md 0 |
| Q8 | Dòng `Clean code: BẬT` biến mất | PASS | `grep -c "Clean code: BẬT" spec-template.md` → 0 |
| Q9 | Hai bản `qc.md` khớp nhau | PASS | `pytest -k qc_khop_portable` xanh; cả hai có QC-F4, không bản nào nhắc script cũ |
| Q10 | Script và hai test đã xoá | PASS | `ls` cả ba báo `No such file or directory` |
| Q11 | Không còn tham chiếu mồ côi | PASS sau fix QC1.2 | Lệnh spec đã sửa (thêm `grep -v docs/workinglog`) → còn 2 dòng, cả hai là chốt chặn hồi quy. Xem `## Ghi chú Q11` |
| Q12 | Thư viện `rules/` nguyên vẹn và xanh | PASS sau fix QC1.2 | `pytest tests/test_rules_library.py` 5 passed, 11 subtests; `ls skills/tdq-build/references/rules/ \| wc -l` = 10 (lệnh spec ghi `ls rules/` là sai đường dẫn, đã sửa) |
| Q13 | R9 phủ file luật mới, không đỏ oan | PASS | `pytest tests/test_doc_lint.py -k r9` 8 passed (trước: 5) |
| Q14 | Toàn bộ suite | PASS | `python3 -m pytest -q` → **703 passed, 375 subtests**. Trước: 687 (703 − 23 test mới + 7 test đã xoá) |
| Q15 | Lint mọi file đã sửa | PASS | `doc_lint.py` trên 10 file đã sửa → exit 0 |
| Q16 | Spec cũ không đỏ vì đổi khuôn | PASS | `doc_lint.py docs/tdq/spec/*.md` exit 0 |
| Q17 | Phát hành 0.22.0 | PASS | `grep -c "0.22.0"` → CHANGELOG.md 1 · plugin.json 1 |
| Q18 | Luật tự soi được chính nó | PASS | Xem mục `## Q18 — chạy checklist lên chính bản thay đổi` |
| Q19 | Kiểm độc lập | Xem mục `## Q19` | agent `tdq-qc-tester` |
| QC-F1 | Full suite | PASS | 703 passed, 0 failed |
| QC-F2 | Hồi quy vùng chạm | PASS | `test_doc_lint.py` 43 passed · `test_rules_library.py` 5 passed · `test_clean_code_rule.py` 21 passed |
| QC-F3 | Ràng buộc kiến trúc | PASS | Không thêm file code mới; `portable/` sửa khớp `skills/`; không chạm `state.json` |
| QC-F4 | Clean code | PASS | Chính là Q18 — file mã nguồn duy nhất bị sửa là `scripts/doc_lint.py` |

## Ghi chú Q11

Lệnh `grep -rn "code_rule_scan" --include=*.md --include=*.py . | grep -v CHANGELOG |
grep -v docs/tdq | grep -v graphify-out` (bản gốc trong spec) ra 4 dòng. Sau fix QC1.2
lệnh thêm `grep -v docs/workinglog` và ra 2 dòng. Xét từng dòng của bản gốc:

- `tests/test_clean_code_rule.py:196` — `assertNotIn("code_rule_scan", doc(path))`. Đây là
  chốt chặn hồi quy: xoá chuỗi này là mất luôn phép kiểm "hai bản qc.md không nhắc script
  cũ". Giữ.
- `tests/test_clean_code_rule.py:3` — docstring nói vì sao file test này tồn tại. Giữ.
- `docs/workinglog/2026-08-16.md` 2 dòng — nhật ký lịch sử ghi việc đã làm. Sửa nhật ký là
  làm sai lệch hồ sơ. Giữ.

Không dòng nào là tham chiếu mồ côi theo nghĩa "code hay tài liệu còn trỏ tới thứ đã xoá và
sẽ gãy". Đã sửa 1 chỗ thật sự thừa: comment R9 trong `scripts/doc_lint.py` đổi từ nêu tên
file đã xoá sang "script scan cũ".

## Q18 — chạy checklist lên chính bản thay đổi

File mã nguồn duy nhất bị sửa là `scripts/doc_lint.py` (mở rộng phạm vi R9 + nới trần dòng).

| Câu | `scripts/doc_lint.py` | `clean-code.md` (bản thân file luật) |
|---|---|---|
| SRP | CÓ — `_r9_in_scope()` chỉ trả lời "file này có thuộc phạm vi không", `rule_r9()` chỉ kiểm 3 mục. Thêm file vào phạm vi không phải sửa phép kiểm | CÓ — file chỉ nói một việc: clean code là gì và tự kiểm thế nào |
| OCP | CÓ — thêm `clean-code.md` chỉ là thêm một phần tử vào hằng `RULE_FILE_NAMES`, thân `_r9_in_scope()` không đổi một chữ | CÓ — thêm nguyên tắc mới là thêm một dòng bảng cộng một khối `### <MÃ>` |
| LSP | CÓ — `_r9_in_scope()` mọi nhánh trả `bool`; `rule_r9()` mọi nhánh trả `None` và chỉ append vào `out` | KHÔNG ÁP DỤNG — file tài liệu, không có nhánh `return` |
| ISP | CÓ — `_r9_in_scope(path)` nhận đúng đường dẫn, không nhận cả object `Doc` dù người gọi có sẵn | CÓ — mỗi khối ví dụ đứng độc lập, đọc một khối không phải nạp cả file |
| DIP | CÓ — vẫn đi qua điểm vào chung `RULES` + `Doc`, không tự mở file ra đọc lần nữa | CÓ — luật trỏ về `soul.md` làm luật gốc, không chép lại nội dung soul |

Câu nào cũng trả lời được, không câu nào phải sửa code sau khi trả lời.

## Q19 — lượt kiểm độc lập (agent `tdq-qc-tester`)

Agent chạy lại Q1–Q18 bằng đúng lệnh literal trong spec §6. Kết quả: Q1–Q10, Q13–Q18 PASS
khớp với bảng trên. Q11 và Q12 agent chấm FAIL vì lệnh literal trong spec không bao giờ ra
được điều kiện PASS đã ghi. Ba điểm soi thêm đều PASS: ví dụ trong file luật khớp với code
thật (agent mở `scripts/tdq_checkstatus.py` xác nhận `gom_bang_chung` chỉ đọc và
`cham_ca_lech` chỉ phán xét); không còn chỗ nào giả định cổng BẬT/TẮT ngoài hồ sơ lịch sử;
phần QC-F4 khớp 100% giữa `skills/` và `portable/`.

Bốn phát hiện, đã xử hết ở vòng fix 1:

| # | Mức | Nội dung | Xử lý |
|---|---|---|---|
| 1 | cảnh báo | Lệnh Q11 thiếu `grep -v docs/workinglog` | QC1.2 — sửa lệnh trong spec §6 |
| 2 | cảnh báo | Lệnh Q12 ghi `ls rules/`, đường dẫn thật là `skills/tdq-build/references/rules/` | QC1.2 — sửa lệnh trong spec §6 |
| 3 | cảnh báo | Câu LSP trong `## Tự kiểm` chỉ hỏi bản đọc cho hàm, không nhắc substitutability khi có kế thừa | QC1.1 — viết lại câu, phủ cả hai cột |
| 4 | cảnh báo | Câu OCP thiếu vế "thêm class con thay vì sửa class cũ" | QC1.1 — viết lại câu, phủ cả hai cột |

Phát hiện 3 và 4 là lỗi thật của luật, không phải lỗi lệnh: bảng `## Làm gì` có hai cột
nhưng `## Tự kiểm` chỉ hỏi một cột, nên model sửa một cây class sẽ không được nhắc đúng
nội dung LSP/OCP gốc.

## Vòng fix 1

- QC1.1 — hai câu LSP và OCP trong `## Tự kiểm` viết lại để phủ cả ca có class lẫn ca chỉ
  có hàm; vẫn đúng 5 câu. Test mới `test_checklist_phu_ca_hai_ban_doc` khoá lại: câu LSP
  phải chứa "kế thừa", câu OCP phải chứa "class". Chạy đỏ trước (2 subtest FAIL), xanh sau.
- QC1.2 — sửa lệnh Q11 và Q12 trong spec §6.

## Kết luận

Q1–Q19 PASS sau một vòng fix. Suite sau fix: **704 passed, 377 subtests**
(`test_clean_code_rule.py` 21 test). `doc_lint` exit 0 trên mọi file đã sửa.
