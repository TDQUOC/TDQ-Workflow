# SPEC — Bỏ cổng clean code, thay bằng luật SOLID

<!-- doc-lint: allow R10 — spec viết trước khi có luật ranh giới module -->

Ngày: 2026-08-16 · Bản: 1.0 · Brief: ../brief/2026-08-16-1300-bo-cong-clean-code.md · Lane: full
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md
Trạng thái: CHỜ DUYỆT

## 1. Mục tiêu & phạm vi

- Mục tiêu: gỡ cổng hỏi "Bật clean code cho request này chứ?" khỏi khuôn spec và xoá
  `scripts/code_rule_scan.py`, thay bằng một file luật thường trực ở `tdq-conventions` —
  clean code trở thành hành vi model tự tuân theo 5 nguyên tắc SOLID, không còn là một
  cổng hỏi và một lượt chạy linter cuối request.
- Trong phạm vi:
  - Xoá lớp câu hỏi: bước 1b của `tdq-spec/SKILL.md`, mục `## Khuôn hỏi clean code` và
    dòng `Clean code: BẬT|TẮT` §4 của `spec-template.md`.
  - Xoá lớp script: `scripts/code_rule_scan.py`, `tests/test_code_rule_scan.py`,
    `tests/test_clean_code_workflow.py`.
  - Đổi lớp DoD: hạng mục QC clean code trong `tdq-build/references/qc.md` và
    `portable/workflow/references/qc.md` đổi từ lệnh scan sang checklist có/không.
  - Thêm file luật `skills/tdq-conventions/references/clean-code.md` theo khuôn 3 mục.
  - Giữ nguyên thư viện `skills/tdq-build/references/rules/`, chỉ xoá các dòng nhắc
    `code_rule_scan.py` trong `chung.md` và `index.md`.
  - Mở rộng phạm vi `doc_lint` R9 để phủ file luật mới.
- NGOÀI phạm vi (chép từ brief `### Phạm vi đã chốt`, mặt LOẠI): hiệu năng · bảo mật ·
  trải nghiệm người dùng · độ tin cậy · an toàn · chức năng. Cộng thêm: không gộp và
  không xoá 10 file thư viện `rules/` (user chốt 2a), không đụng `docs/kien-truc.md`,
  không đổi soul.

## 1b. Lộ trình

Chép từ brief mục `### Lộ trình`. User duyệt spec là duyệt luôn lộ trình này.

| Bước/phase | Chạy? | Vì sao |
|---|---|---|
| Research web | CÓ | SOLID chưa xuất hiện ở repo (grep 0 kết quả), soul đòi mọi kết luận có nguồn — đã chạy, kết quả ở `../research/2026-08-16-bo-cong-clean-code.md` |
| Interview | CÓ | đã chạy 2 vòng: scope `1abc 2a 3a 4a`, chi tiết `1a 2a 3a` |
| QC độc lập (agent) | CÓ | thay đổi có hiệu lực hồi tố lên mọi request sau; lượt kiểm độc lập ở request trước tìm ra 5 lỗ hổng mà test tại chỗ không thấy |

## 2. Đầu ra cụ thể

| # | Đầu ra | Đường dẫn/vị trí | Đo "xong" bằng |
|---|---|---|---|
| 1 | File luật clean code + SOLID, khuôn 3 mục, mỗi luật hai cột đọc | `skills/tdq-conventions/references/clean-code.md` | `doc_lint.py` exit 0 và `pytest tests/test_clean_code_rule.py -k khuon` xanh |
| 2 | Bảng 5 luật SOLID hai cột: "khi có class" và "khi chỉ có hàm/module" | mục `## Làm gì` của đầu ra 1 | `pytest -k bang_solid` — đủ 5 mã SRP/OCP/LSP/ISP/DIP, mỗi mã đủ 2 cột |
| 3 | Nhãn giới hạn của LSP + ghi rõ bản đọc hàm là suy diễn | mục `## Làm gì` của đầu ra 1 | `pytest -k lsp_gioi_han` — có cả chữ "kế thừa" lẫn chữ đánh dấu suy diễn |
| 4 | Checklist 5 câu có/không thay cho lệnh scan | mục `## Tự kiểm` của đầu ra 1 | `pytest -k checklist` — đúng 5 dòng câu hỏi, mỗi dòng kết bằng dấu hỏi |
| 5 | Dòng nạp luật mới trong thân skill conventions | `skills/tdq-conventions/SKILL.md` | `grep -c clean-code.md` ra ≥ 1 và `doc_lint` exit 0 (trần 130 dòng) |
| 6 | Cổng hỏi bị gỡ khỏi khuôn spec | `skills/tdq-spec/SKILL.md` · `references/spec-template.md` | `grep -c "Khuôn hỏi clean code"` ra 0 ở cả hai file |
| 7 | Hạng mục DoD đổi dạng, khớp nhau hai bản | `skills/tdq-build/references/qc.md` · `portable/workflow/references/qc.md` | `pytest -k qc_khop_portable` — cả hai nhắc checklist, không bản nào nhắc `code_rule_scan` |
| 8 | Script và hai test bị xoá | `scripts/code_rule_scan.py` · `tests/test_code_rule_scan.py` · `tests/test_clean_code_workflow.py` | `test -e` cả ba đều sai; `grep -rn code_rule_scan` chỉ còn `CHANGELOG.md` |
| 9 | Thư viện `rules/` sạch dấu vết script | `rules/chung.md` · `rules/index.md` | `pytest tests/test_rules_library.py` xanh và `grep -c code_rule_scan` ra 0 |
| 10 | `doc_lint` R9 phủ file luật mới | `scripts/doc_lint.py` | `pytest tests/test_doc_lint.py -k r9` — file thiếu 1 trong 3 mục thì R9 báo lỗi |
| 11 | Bộ test của luật mới | `tests/test_clean_code_rule.py` | `pytest tests/test_clean_code_rule.py -q` xanh |
| 12 | Phát hành 0.22.0 | `CHANGELOG.md` · `.claude-plugin/plugin.json` | `grep -c "0.22.0"` ra ≥ 1 ở cả hai |

## 3. Cách tiếp cận & lý do

- Chọn: viết luật SOLID theo **hai cột** — mỗi nguyên tắc có bản đọc "khi có class" và bản
  đọc "khi chỉ có hàm/module", ví dụ ĐÚNG/SAI lấy từ chính `scripts/` của repo này.
- Vì: đo được rằng repo có **4 `class` trên 280 `def`** ở 19 file `scripts/`. SOLID là bộ
  nguyên tắc hướng đối tượng, tâm điểm là class (slide CSCE 315 Texas A&M: *"with focus on
  designing the classes"*; Real Python giới hạn phạm vi ở *"object-oriented code"*). Một
  luật chỉ chép năm câu gốc sẽ để model mở `tdq_state.py` ra, không thấy class, rồi kết
  luận luật không áp — đúng thất bại mà soul nguyên tắc 3 cấm. Bản đọc theo hàm/module có
  nguồn: DEV *Do the SOLID principles apply to Functional Programming?*.
- Chọn: giữ đủ 5 luật, nhưng **LSP mang nhãn giới hạn** "chỉ áp nguyên văn khi có class con
  hoặc nhiều bản cài cùng một giao diện", kèm bản đọc mở rộng cho hàm được đánh dấu rõ là
  suy diễn của repo này.
- Vì: phát biểu gốc của Barbara Liskov nói về object và subtype (nguồn: DEV *A Pythonic
  Guide to SOLID*). Trình bày bản đọc cho hàm như trích dẫn Liskov là bịa nguồn.
- Chọn: `## Tự kiểm` gồm **checklist 5 câu có/không** cộng **mở rộng `doc_lint` R9**.
- Vì: soul nguyên tắc 3 cho phép Tự kiểm là "một lệnh HOẶC một câu hỏi có/không", nhưng
  luật phân xử #2 ưu tiên luật kiểm được bằng lệnh. Bỏ linter mà không bù gì là hạ tầng 1.
  R9 kiểm được hình dạng file luật bằng lệnh; checklist lo phần phán đoán thiết kế mà không
  lệnh nào thay được.
- Chọn: xoá thẳng `code_rule_scan.py`, không để lại wrapper báo lỗi.
- Vì: `graphify query "code_rule_scan"` trả 13 node đều là cạnh `contains` nội bộ file —
  không script nào khác gọi vào. Đây là lá, xoá không gãy ai.
- Đã loại: giữ script và chỉ bỏ câu hỏi — vì user yêu cầu xoá script, và script phụ thuộc
  linter cài sẵn: request ngay trước báo `CHƯA KIỂM ĐƯỢC — thiếu ruff` cho cả 5 file Python,
  tức cổng tốn một lượt hỏi mà không trả lại bảo đảm nào.
- Đã loại: gộp hoặc xoá thư viện `rules/` — vì user chốt 2a giữ nguyên.

## 3b. Năng lực & công cụ

Chép từ brief mục `### Năng lực dùng được`.

| Skill | Nguồn | Phán quyết | Dùng ở đâu / Lý do loại |
|---|---|---|---|
| tdq-conventions | project | NỀN | skill khung nạp mọi phase; file luật mới đặt vào `references/` của nó |
| tdq-spec | project | NỀN | chính khuôn spec của nó là thứ bị sửa |
| tdq-build | project | NỀN | `references/qc.md` và thư viện `rules/` bị sửa |
| graphify | user | DÙNG | tra hộ tiêu thụ của `code_rule_scan.py` trước khi xoá — đã chạy, xác nhận là lá |
| mem0-memory | user | DÙNG | sau khi chốt, ghi một fact ngắn: clean code đổi từ scan sang luật SOLID |
| Đã xét 34 skill khác | user/plugin/built-in | KHÔNG | khác lĩnh vực |

## 4. Yêu cầu bắt buộc

- Log service: BỎ — việc này chỉ XOÁ code và sửa tài liệu, không tạo file mã nguồn chạy
  được nào mới. Sửa `doc_lint.py` là mở rộng một hằng phạm vi, không thêm runtime.
- Không placeholder, không TODO stub, không mock trình bày như dữ liệu thật.
- Mỗi thành phần có unit test riêng, chạy được bằng một lệnh.
- Clean code: luật mới ở `skills/tdq-conventions/references/clean-code.md` áp cho chính
  request này — file luật viết ra phải qua được checklist 5 câu của chính nó.

## 5. Ràng buộc & rủi ro

Ràng buộc kiến trúc phải giữ (chép từ `docs/kien-truc.md`, trạng thái NHÁP):

- `skills/` chỉ được **nhắc tên lệnh** của `scripts/`, cấm chép nội dung script vào skill —
  việc này chạm ở `clean-code.md` và hai file `qc.md`: chỉ được nêu tên checklist, không
  chép logic linter cũ vào.
- File code MỚI bắt buộc nằm trong `scripts/` hoặc `hooks/` — việc này chỉ XOÁ code và sửa
  `scripts/doc_lint.py`, không thêm file code ngoài hai thư mục đó.
- `tests/` gọi được vào mọi tầng — `tests/test_clean_code_rule.py` đọc file luật trực tiếp.

Ràng buộc khác: `portable/` phải khớp bước với `skills/`; trần dòng `tdq-conventions` là
130 và SKILL.md hiện đúng 130 dòng, nên thêm dòng nạp luật mới thì phải nới trần hoặc bù
dòng — soul cấm nén luật cho vừa trần.

| Rủi ro | Ảnh hưởng | Cách giảm |
|---|---|---|
| Luật SOLID viết xong vẫn quá trừu tượng, Haiku đọc không làm được | Mất luôn lớp clean code: cổng cũ đã gỡ mà luật mới vô hiệu | Bắt buộc mỗi luật có ví dụ ĐÚNG/SAI lấy từ file thật trong `scripts/`; QC có hạng mục đọc thử bằng agent độc lập |
| Xoá 2 test làm tụt số test, che một hồi quy khác | Suite vẫn xanh nhưng mất độ phủ | Ghi số test trước/sau vào file qc; `test_clean_code_rule.py` phải bù ít nhất số hạng mục đã mất |
| `spec-template.md` còn sót dòng `Clean code:` ở spec cũ trong `docs/tdq/spec/` | Spec cũ đỏ lint hoặc gây hiểu nhầm | Không sửa spec cũ; chỉ khuôn mẫu đổi. QC kiểm bằng `doc_lint` trên toàn `docs/tdq/spec/` |
| Nới trần `tdq-conventions` thành thói quen, skill phình dần | Context cost tăng mỗi turn | Nới đúng số dòng cần, kèm comment lý do ngay tại `SKILL_LINE_LIMITS` như tiền lệ 0.19.0 |
| R9 mở rộng làm đỏ oan file cũ khác | Suite đỏ ngoài phạm vi | R9 chỉ thêm đúng một đường dẫn cụ thể, không thêm thư mục; `test_doc_lint.py -k r9` khoá phạm vi |

## 6. QC & Definition of Done

| # | Hạng mục kiểm | Lệnh/cách kiểm | Điều kiện PASS |
|---|---|---|---|
| Q1 | File luật mới đủ khuôn 3 mục | `python3 scripts/doc_lint.py skills/tdq-conventions/references/clean-code.md` | exit 0 |
| Q2 | Bảng 5 luật đủ mã và đủ hai cột | `pytest tests/test_clean_code_rule.py -k bang_solid` | xanh; đủ SRP, OCP, LSP, ISP, DIP |
| Q3 | Mỗi luật có ví dụ ĐÚNG/SAI từ file thật của repo | `pytest tests/test_clean_code_rule.py -k vi_du` | xanh; mọi đường dẫn nêu trong ví dụ đều tồn tại trên đĩa |
| Q4 | LSP có nhãn giới hạn và đánh dấu suy diễn | `pytest tests/test_clean_code_rule.py -k lsp_gioi_han` | xanh |
| Q5 | Checklist đúng 5 câu có/không | `pytest tests/test_clean_code_rule.py -k checklist` | xanh |
| Q6 | Conventions nạp luật mới | `pytest tests/test_clean_code_rule.py -k conventions_nap` | xanh |
| Q7 | Cổng hỏi biến mất khỏi khuôn spec | `grep -c "Khuôn hỏi clean code" skills/tdq-spec/SKILL.md skills/tdq-spec/references/spec-template.md` | cả hai ra 0 |
| Q8 | Dòng `Clean code: BẬT\|TẮT` biến mất khỏi §4 khuôn | `grep -c "Clean code: BẬT" skills/tdq-spec/references/spec-template.md` | 0 |
| Q9 | Hai bản `qc.md` khớp nhau, không bản nào nhắc script cũ | `pytest tests/test_clean_code_rule.py -k qc_khop_portable` | xanh |
| Q10 | Script và hai test đã xoá | `ls scripts/code_rule_scan.py tests/test_code_rule_scan.py tests/test_clean_code_workflow.py` | cả ba báo không tồn tại |
| Q11 | Không còn tham chiếu mồ côi | `grep -rn "code_rule_scan" --include=*.md --include=*.py . \| grep -v CHANGELOG \| grep -v docs/tdq \| grep -v docs/workinglog \| grep -v graphify-out` | chỉ còn dòng trong `tests/test_clean_code_rule.py` (chốt chặn hồi quy), không dòng nào ở `skills/`, `scripts/`, `hooks/`, `portable/` |
| Q12 | Thư viện `rules/` còn nguyên và xanh | `pytest tests/test_rules_library.py -q` | xanh; `ls skills/tdq-build/references/rules/ \| wc -l` vẫn ra 10 |
| Q13 | R9 phủ file luật mới, không đỏ oan file khác | `pytest tests/test_doc_lint.py -k r9` | xanh |
| Q14 | Toàn bộ suite | `python3 -m pytest -q` | 0 test đỏ; số test ghi rõ trước/sau vào file qc |
| Q15 | Lint mọi file đã sửa | `python3 scripts/doc_lint.py <danh sách file>` | exit 0 |
| Q16 | Lint toàn bộ spec cũ không đỏ vì thay đổi khuôn | `python3 scripts/doc_lint.py docs/tdq/spec/*.md` | exit 0 |
| Q17 | Phát hành 0.22.0 | `grep -c "0.22.0" CHANGELOG.md .claude-plugin/plugin.json` | cả hai ≥ 1 |
| Q18 | Luật mới tự soi được chính nó | chạy checklist 5 câu của `clean-code.md` lên chính file luật và lên `doc_lint.py` sau khi sửa | 5/5 câu trả lời được, ghi đáp án vào file qc |
| Q19 | Kiểm độc lập | agent `tdq-qc-tester` chạy lại Q1–Q18 và soi thêm: luật có dùng được cho model yếu không | báo cáo PASS, hoặc FAIL thì mở vòng fix trong plan |

DoD: đủ 12 đầu ra ở §2 · Q1–Q19 PASS có bằng chứng trong `docs/tdq/qc/<slug>.md` ·
`grep -rn code_rule_scan` sạch ngoài `CHANGELOG.md` và `docs/tdq/` · suite xanh ·
`doc_lint` exit 0 · phát hành 0.22.0 · report có bảng thời gian thật.

## 7. Câu hỏi còn mở

(rỗng)
