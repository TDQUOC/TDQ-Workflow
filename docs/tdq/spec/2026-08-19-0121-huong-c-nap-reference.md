# SPEC — Hướng C: nạp reference theo nhu cầu

Ngày: 2026-08-19 · Bản: 1.0 · Brief: ../brief/2026-08-19-0121-huong-c-nap-reference.md · Lane: full
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md
Trạng thái: CHỜ DUYỆT

## 1. Mục tiêu & phạm vi
- Mục tiêu: đưa mọi file reference về **đúng một tầng** từ `SKILL.md` (trục chất lượng),
  sửa công cụ đo đang đếm thiếu (trục bảo trì), và cắt phần đọc thừa bằng mục lục (trục
  context) — không đổi một chữ nào của nội dung luật.
- Trong phạm vi: sửa link + thêm mục lục trong `skills/`; sửa `scripts/skill_tokens.py`
  đếm đệ quy; 3 test khoá mới; chạy lại `build_portable.py` cho hai bản portable; đính
  chính số hướng C trong đề án; report.
- NGOÀI phạm vi (chép từ "Mặt LOẠI" của brief): bảo mật · hiệu năng runtime của
  hook/script · trải nghiệm người dùng cuối · tương thích harness ngoài Claude/Codex.
  Cũng ngoài phạm vi: **viết lại nội dung luật**, gộp/tách skill, hướng B, A(hybrid), E.

## 1b. Lộ trình
Chép từ brief mục `### Lộ trình`.

| Bước/phase | Chạy? | Vì sao |
|---|---|---|
| Kiểm kê năng lực (B0) | CÓ (xong ở analyze) | 6/284 skill liên quan |
| Đọc code | CÓ (xong ở analyze) | đã dựng đồ thị link + đo token từng file |
| Research web | CÓ (xong, 1 truy vấn) | kiểm tiền đề "tách sâu thêm" — tiền đề sai |
| Vòng scope | CÓ (xong) | user chốt 1ABC 2A 3A |
| Interview chi tiết thêm | BỎ | ba câu scope đã khoá hết chỗ đổi kết quả |
| QC độc lập (agent) | BỎ | test khoá tự động là bằng chứng mạnh hơn agent đọc lại |
| Chia subagent | BỎ | 5 nhóm task tuyến tính qua cùng bộ file |

## 2. Đầu ra cụ thể
| # | Đầu ra | Đường dẫn/vị trí | Đo "xong" bằng |
|---|---|---|---|
| 1 | Mọi reference tới được thẳng từ một `SKILL.md` | `skills/*/SKILL.md` | đồ thị link: 37/37 file ở tầng 1, 0 file mồ côi |
| 2 | Test khoá luật một tầng | bộ test của repo | test đỏ trên cây hiện tại, xanh sau khi sửa |
| 3 | `skill_tokens.py` đếm đệ quy | `scripts/skill_tokens.py` | `--theo-phase` báo 35 file reference (thay vì 25) và trần ≥ 89.000 token |
| 4 | Test khoá công cụ đo không sót thư mục con | bộ test của repo | test đỏ với bản đếm cũ, xanh với bản đệ quy |
| 5 | Mục lục cho 8 file reference > 100 dòng | `skills/*/references/*.md` | mỗi file có `## Mục lục` ngay dưới dòng mở đầu, liệt kê đủ các `##` của chính nó |
| 6 | Test khoá mục lục | bộ test của repo | file > 100 dòng mà thiếu mục lục → đỏ |
| 7 | Hai bản portable sinh lại từ nguồn mới | `portable_claude/`, `portable_codex/` | `build_portable.py` chạy exit 0; `manifest.json` khớp sha256 file thật |
| 8 | Test khoá reference có đủ ở cả hai bản portable | bộ test của repo | thiếu 1 file reference ở bất kỳ bản nào → đỏ |
| 9 | Đính chính hướng C trong đề án | `docs/tdq/audit/de-an-toi-uu-context.md` | có mục "Đính chính hướng C 2026-08-19", nêu số 55.719 thiếu 14.554 |
| 10 | Report | `docs/tdq/reports/2026-08-19-0121-huong-c-nap-reference.md` | file tồn tại, `doc_lint` exit 0 |

## 2b. Ranh giới module
| Module | Vùng file | Phụ thuộc module | Đầu ra §2 nào |
|---|---|---|---|
| M1 — cấu trúc link skill | `skills/*/SKILL.md` + test đi kèm | không | 1, 2, 5, 6 |
| M2 — công cụ đo | `scripts/skill_tokens.py` + test đi kèm | không | 3, 4 |
| M3 — portable | `portable_*/` + test đi kèm | M1 | 7, 8 |
| M4 — tài liệu | `docs/tdq/audit/`, `docs/tdq/reports/` | M1, M2, M3 | 9, 10 |

M1 và M2 độc lập nhau, chạm hai vùng file rời nhau → chạy song song được. M3 phải đợi M1
(sinh lại từ nguồn đã sửa). M4 đợi cả ba vì phải ghi số đo sau.

## 3. Cách tiếp cận & lý do
- **Phẳng hoá bằng cách thêm link ở `SKILL.md`, KHÔNG bằng cách gộp nội dung vào thân
  skill.** 14 file đang ở tầng ≥ 2 chỉ cần thân skill tương ứng có đúng một dòng trỏ tới
  nó; link chéo giữa các reference giữ nguyên vì lúc đó chúng chỉ còn là đường tắt, không
  còn là đường DUY NHẤT. Cách này thêm ~14 dòng vào các `SKILL.md` (chi phí context gần
  như 0) mà xoá hẳn rủi ro "model chỉ đọc một phần luật".
- **Chuỗi `rules/` rút từ tầng 4 xuống tầng 1** bằng cách cho `tdq-build/SKILL.md` trỏ
  thẳng `rules/index.md`, và `index.md` trỏ tới đủ 10 file ngôn ngữ. Giữ nguyên cơ chế
  "nạp `chung.md` + đúng một file ngôn ngữ" — đây là progressive disclosure đúng, chỉ sai
  ở chỗ cửa vào bị chôn quá sâu.
- **Mục lục thay vì tách file.** Hướng dẫn chính thức khuyên mục lục cho file > 100 dòng
  và cấm tách sâu thêm; mục lục tốn ~40 token/file nhưng cho model đọc chọn lọc.
- Đã loại: tách tiếp file reference lớn — đi ngược hướng dẫn chính thức, đẩy luật xuống
  tầng model có thể đọc thiếu (brief, Phát hiện 1).
- Đã loại: cắt trùng lặp nội dung giữa các reference ở vòng này — muốn cắt trùng phải đọc
  và viết lại chữ của luật, mà "viết lại nội dung luật" nằm ngoài phạm vi user đã chốt.
  Ghi lại thành việc của request sau.
- Đã loại: sửa tay hai bản portable — chúng được SINH ra; sửa tay là tái lập đúng lỗi mà
  `build_portable.py` sinh ra để dập.

## 3b. Năng lực & công cụ
| Skill | Nguồn | Phán quyết | Dùng ở đâu / Lý do loại |
|---|---|---|---|
| `tdq-spec`, `tdq-plan`, `tdq-build` | plugin:tdq-workflow | DÙNG | chạy phase tương ứng |
| `tdq-conventions` | plugin:tdq-workflow | NỀN | skill khung |
| `scripts/skill_tokens.py` | project | DÙNG | đo token trước/sau, và chính nó là đối tượng sửa |
| `scripts/build_portable.py` | project | DÙNG | sinh lại hai bản portable |
| Đã xét 278 skill khác | plugin/built-in | KHÔNG | khác lĩnh vực |

## 4. Yêu cầu bắt buộc
- Log service: `skill_tokens.py` đã có log service sẵn — giữ nguyên, không tắt.
- **Không đổi một chữ nào của nội dung luật.** Chỉ được thêm link, thêm mục lục, sửa mã
  công cụ đo. Sửa câu chữ luật là dấu hiệu đã ra ngoài phạm vi.
- Không placeholder, không TODO stub.
- Mọi test mới phải ĐỎ trên cây hiện tại trước khi sửa — test xanh ngay từ đầu là test không khoá gì.
- Sửa `skills/` xong BẮT BUỘC chạy `build_portable.py`; cấm sửa tay `portable_*`.

## 5. Ràng buộc & rủi ro
Ràng buộc kiến trúc phải giữ: `portable_claude/` và `portable_codex/` là sản phẩm SINH ra
từ `skills/` — một nguồn, hai đích. Không được có đường sửa nào khác.

| Rủi ro | Ảnh hưởng | Cách giảm |
|---|---|---|
| Thêm link vào `SKILL.md` làm thân skill phình, đội chi phí "luôn nạp" | tốn context mọi request | mỗi file thêm đúng 1 dòng trỏ; đo lại thân skill sau khi sửa, chấp nhận trần +300 token, vượt thì gộp dòng |
| Sửa link làm hỏng link cũ, tài liệu trỏ vào hư không | luật mất đường tới, tệ hơn hiện tại | test khoá kiểm MỌI link `.md` trong `skills/` trỏ tới file có thật |
| Mục lục lệch khỏi tiêu đề thật sau này | model đọc theo mục lục sai | test khoá so mục lục với danh sách `##` của chính file |
| `skill_tokens.py` đổi cách đếm làm số trước/sau không so được | tạo ra mức "tiết kiệm" ảo, đúng lỗi đã mắc ở hướng D | report ghi CẢ hai số theo cách đếm mới cho cả trước lẫn sau; cấm so số cũ với số mới |
| Sinh lại portable làm lệch `manifest.json` | máy đích tự vá sai | chạy bộ test portable và test tự kiểm máy đích sau khi sinh |

## 6. QC & Definition of Done
| # | Hạng mục kiểm | Điều kiện PASS |
|---|---|---|
| Q1 | Luật một tầng | đồ thị link: 37/37 reference được ít nhất một `SKILL.md` trỏ thẳng; 0 file mồ côi |
| Q2 | Không link chết | mọi link `.md` trong `skills/` trỏ tới file tồn tại |
| Q3 | Công cụ đo đếm đủ | `skill_tokens.py --theo-phase` liệt kê 35 file reference, trần ≥ 89.000 token |
| Q4 | Mục lục | 8 file > 100 dòng đều có `## Mục lục` khớp danh sách `##` của chính nó |
| Q5 | Nội dung luật không đổi | `git diff` trên `skills/` chỉ gồm dòng link và khối mục lục — không dòng luật nào bị sửa chữ |
| Q6 | Portable đồng bộ | lệnh sinh portable exit 0; bộ test portable và test tự kiểm máy đích đều xanh; mọi reference của `skills/` có mặt ở cả hai bản |
| Q7 | Test khoá thật sự khoá | 3 test mới đều ĐỎ khi hoàn tác thay đổi tương ứng |
| Q8 | Full suite | toàn bộ test suite của repo xanh |
| Q9 | Số trước/sau cùng một cách đếm | report ghi rõ cả hai số đo bằng bản `skill_tokens.py` mới |

DoD: 10 đầu ra §2 tồn tại, đạt Q1-Q9, và một người đọc report biết chính xác việc này đổi
gì về chất lượng (tầng luật) và đổi gì về token, không lẫn hai thứ.

## 7. Câu hỏi còn mở
(rỗng)
