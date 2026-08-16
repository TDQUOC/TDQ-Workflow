# BRIEF — Bỏ cổng clean code, xoá script scan

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## Nguyên văn

> tôi muốn mở request mới cho yêu cầu là bỏ câu hỏi Bật clean code cho request này chứ?
> và xóa script scan clean code luôn. clean code bây giờ là claude code cố gắng tổ chứ
> project, script, funtion, class clean code nhất có thể và cố gắng tuân theo 5 luật
> solid code thôi. yêu cầu update vẫn phải tuân thủ soul của workflow

Kèm ảnh chụp chính khuôn hỏi cần bỏ, nguyên văn trong ảnh:

> **Bật clean code cho request này chứ?**
> – A (đề xuất): BẬT — cuối request chạy `scripts/code_rule_scan.py`, có LỖI thì fix tới khi sạch
> – B: TẮT — bỏ bước scan và fix; code viết ra VẪN tổ chức theo rule ngôn ngữ

### Cách hiểu đầu tiên

Mục tiêu: cắt một cổng hỏi và một script khỏi workflow, đổi "clean code" từ **cơ chế kiểm
bằng linter ngoài** sang **luật hành vi mà model tự tuân**. Lý do đằng sau (suy đoán, cần
user xác nhận): cổng này hỏi mọi request chạm mã nguồn nhưng đáp án gần như luôn là A, còn
`code_rule_scan.py` phụ thuộc linter cài sẵn trên máy — chính request trước vừa báo
`CHƯA KIỂM ĐƯỢC — thiếu ruff` cho cả 5 file Python, tức cổng tốn một lượt hỏi mà không
trả lại bảo đảm nào.

Phạm vi đoán — 9 file đang nhắc tới cổng hoặc script:

| Nhóm | File |
|---|---|
| Khuôn spec | `skills/tdq-spec/SKILL.md` (bước 1b) · `skills/tdq-spec/references/spec-template.md` (§4 + khuôn hỏi cuối file) |
| QC | `skills/tdq-build/references/qc.md` · `portable/workflow/references/qc.md` |
| Thư viện rule | `skills/tdq-build/references/rules/chung.md` · `rules/index.md` (+ 8 file rule ngôn ngữ) |
| Script | `scripts/code_rule_scan.py` (138 dòng) |
| Test | `tests/test_code_rule_scan.py` (83 dòng) · `tests/test_clean_code_workflow.py` (76 dòng) |
| Khác | `CHANGELOG.md` · `.claude-plugin/plugin.json` (bump) |

Chỗ chưa rõ — phải hỏi user, không tự quyết:

1. Thư viện `skills/tdq-build/references/rules/` (10 file, có test riêng
   `tests/test_rules_library.py`) giữ hay xoá? Script scan là hộ tiêu thụ chính của nó,
   nhưng bản thân thư viện là tài liệu rule đọc được, không cần linter.
2. Luật clean code mới đặt ở đâu để mọi phase đều thấy: `tdq-conventions` (áp toàn workflow)
   hay `tdq-build` (chỉ áp lúc implement)?
3. Có cần cổng QC nào thay thế không, hay bỏ hẳn hạng mục clean code khỏi bảng DoD?

## Hiểu & kiến thức

### Phạm vi đã chốt

- Mặt CHỌN: bảo trì · tương thích (bản portable) · flexibility (thư viện `rules/`)
- Mặt LOẠI: hiệu năng · bảo mật · trải nghiệm người dùng · độ tin cậy · an toàn · chức năng
- Bối cảnh: repo chính của bộ workflow, dùng thật hằng ngày, một người giữ, chạy trên máy
  cá nhân; sửa khuôn spec là sửa luật mọi request sau phải theo
- Mức đầu tư suy ra: đầy đủ — vì đây là product chạy thật và thay đổi có hiệu lực hồi tố

### Ba lớp của cổng clean code hiện tại

| Lớp | Nằm ở đâu | Số dòng |
|---|---|---|
| Câu hỏi A/B | `skills/tdq-spec/SKILL.md` bước 1b · `references/spec-template.md` §4 + mục cuối file | — |
| Hạng mục DoD | `skills/tdq-build/references/qc.md` dòng 12, 46-47 · `portable/workflow/references/qc.md` dòng 20-21 | — |
| Script scan | `scripts/code_rule_scan.py` | 138 |
| Test khoá | `tests/test_code_rule_scan.py` · `tests/test_clean_code_workflow.py` | 83 + 76 |

### Kiến thức chốt từ research

Chi tiết và nguồn ở `../research/2026-08-16-bo-cong-clean-code.md`. Ba điều quyết định
thiết kế:

1. SOLID là bộ nguyên tắc **hướng đối tượng**, tâm điểm là class (nguồn: slide CSCE 315,
   Real Python). Repo này có **4 class trên 280 hàm** ở 19 file `scripts/` — gần như thuần
   hàm. Chép nguyên văn năm câu SOLID kiểu OOP vào đây là viết một luật không áp được.
2. 4/5 luật có bản đọc theo hàm và module. Riêng **LSP cần quan hệ kế thừa** mới áp nguyên
   văn; bản đọc cho hàm là suy diễn, phải ghi rõ là mở rộng chứ không trích Liskov.
3. Bỏ script scan = bỏ phần `## Tự kiểm` dạng **lệnh**. Soul nguyên tắc 3 cho phép Tự kiểm
   là "một lệnh HOẶC một câu hỏi có/không", nhưng luật phân xử #2 ưu tiên luật kiểm được
   bằng lệnh — nên phải bù bằng phần kiểm hình dạng chạy được (doc_lint).

### Ràng buộc kiến trúc chạm tới

- Chỉ `tdq_state.py` được ghi `state.json` — việc này không chạm.
- `portable/` phải khớp bước với `skills/` — chạm: hai file `qc.md` phải sửa cùng nhau.
- File code MỚI phải nằm trong `scripts/` hoặc `hooks/` — việc này chỉ XOÁ code, không thêm.

## Hỏi đáp

**Vòng scope** (user trả lời `1abc 2a 3a 4a`):

1. Mặt bao quanh → A+B+C: bảo trì, tương thích, flexibility. Không chọn D.
2. Thư viện `rules/` → A: GIỮ NGUYÊN, chỉ xoá các dòng nhắc `code_rule_scan.py`.
3. Chỗ đặt luật mới → A: `skills/tdq-conventions/`, để mọi phase đều thấy.
4. DoD QC → A: CÓ, đổi dạng — hạng mục tự kiểm có/không theo checklist SOLID, vẫn ghi
   bằng chứng vào file qc.

**Vòng chi tiết** (user trả lời `1a 2a 3a`):

1. Dạng luật → A: HAI CỘT — mỗi luật có bản đọc "khi có class" và "khi chỉ có hàm/module",
   ví dụ ĐÚNG/SAI lấy từ chính `scripts/` của repo.
2. LSP → A: GIỮ ĐỦ 5, gắn nhãn giới hạn "chỉ áp khi có class con hoặc nhiều bản cài cùng
   một giao diện", kèm bản đọc mở rộng cho hàm và ghi rõ đó là suy diễn.
3. Tự kiểm → A: checklist 5 câu có/không cho phần phán đoán, CỘNG mở rộng `doc_lint` R9
   phủ file luật mới để phần hình dạng vẫn kiểm được bằng lệnh.

### Năng lực dùng được

| Skill | Nguồn | Phán quyết | Dùng ở đâu / Lý do loại |
|---|---|---|---|
| `tdq-conventions` | project | NỀN | skill khung nạp mọi phase; file luật mới đặt vào đây |
| `tdq-spec` | project | NỀN | chính khuôn spec của nó là thứ bị sửa |
| `tdq-build` | project | NỀN | `references/qc.md` và thư viện `rules/` bị sửa |
| `graphify` | user | DÙNG | tra hộ tiêu thụ của `code_rule_scan.py` trước khi xoá, tránh xoá nhầm thứ còn người gọi |
| `mem0-memory` | user | DÙNG | ghi một fact ngắn sau khi chốt: clean code đổi từ scan sang luật SOLID |
| Đã xét 34 skill khác | user/plugin/built-in | KHÔNG | khác lĩnh vực |

### Lộ trình

| Bước/phase | Chạy? | Vì sao |
|---|---|---|
| Research web | CÓ | SOLID chưa có ở repo, soul đòi mọi kết luận có nguồn — đã chạy, kết quả ở `../research/2026-08-16-bo-cong-clean-code.md` |
| Interview | CÓ | đã chạy 2 vòng: scope `1abc 2a 3a 4a`, chi tiết `1a 2a 3a` |
| QC độc lập (agent) | CÓ | thay đổi có hiệu lực hồi tố lên mọi request sau; lượt kiểm độc lập ở request trước tìm ra 5 lỗ hổng mà test tại chỗ không thấy |

### Ba câu kiểm cổng

1. Làm ra cái gì? Một file luật SOLID mới ở `tdq-conventions`, ba lớp cổng clean code bị
   gỡ, `code_rule_scan.py` và hai test của nó bị xoá, `doc_lint` R9 mở rộng phạm vi.
2. Còn chỗ nào phải đoán không? Không — ba câu mở đã được user chốt ở vòng chi tiết.
3. Xong thì kiểm bằng gì? `doc_lint` exit 0 trên file luật mới · suite xanh sau khi xoá
   2 test · grep 0 kết quả cho `code_rule_scan` ngoài `CHANGELOG.md`.
