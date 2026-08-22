# SPEC — Quốc tế hoá bộ workflow TDQ

Ngày: 2026-08-21 · Bản: 1.0 · Brief: ../brief/2026-08-21-2351-quoc-te-hoa-workflow.md · Lane: full
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md
Trạng thái: CHỜ DUYỆT

## Mục lục

- 1. Mục tiêu & phạm vi
- 1b. Lộ trình
- 2. Đầu ra cụ thể
- 2b. Ranh giới module
- 3. Cách tiếp cận & lý do
- 3b. Năng lực & công cụ
- 4. Yêu cầu bắt buộc
- 5. Ràng buộc & rủi ro
- 6. QC & Definition of Done
- 7. Câu hỏi còn mở

## 1. Mục tiêu & phạm vi

- **Mục tiêu**: bộ workflow chạy được với user nói bất kỳ ngôn ngữ nào. Ba tầng tách bạch:
  luật (model đọc) viết **tiếng Anh**; chuỗi máy in ra viết **tiếng Anh**; tài liệu request
  sinh ra (brief/spec/plan/qc/report) và mọi câu đối thoại viết bằng **ngôn ngữ của user**,
  lấy từ một giá trị ghi trong state lúc `init`. Đo được bằng §6.
- **Trong phạm vi**:
  - `skills/**/*.md` và `agents/*.md` — dịch sang tiếng Anh, giữ nguyên hành vi, mã task,
    tên lệnh, tên trường state, và các dòng "soul".
  - Comment + docstring tiếng Việt trong `hooks/**/*.py`, `scripts/**/*.py` — dịch.
  - Chuỗi máy in ra cho user từ `hooks/` và `scripts/` — dịch sang tiếng Anh cố định.
  - `hooks/scripts/prompt_context.py` — cổng duyệt nhận chữ cái `a`–`d` và từ khoá tiếng
    Anh, ở cả 4 cổng `spec`/`plan`/`quick`/`mode`.
  - `scripts/tdq_state.py` — thêm trường ngôn ngữ tài liệu, ghi lúc `init`.
  - `skills/tdq-conventions/` — luật ngôn ngữ mới, thay luật "mọi output tiếng Việt".
  - `tests/`, `evals/` — cập nhật theo chuỗi mới, thêm ca đa ngôn ngữ.
  - `portable_claude/`, `portable_codex/` — sinh lại bằng `scripts/build_portable.py`.
  - `docs/kien-truc.md` — thêm dòng `## Đã chốt` cho quyết định ngôn ngữ (thêm dòng, không
    dịch file).
- **NGOÀI phạm vi**:
  - Dịch lại tài liệu request cũ trong `docs/tdq/` (brief/spec/plan/qc/report/audit đã có)
    — quyết định `5a`, chúng là hồ sơ lịch sử.
  - Dịch thân `docs/kien-truc.md`, `CHANGELOG.md`, `docs/workinglog/` — cùng lý do.
  - Dựng cơ chế i18n tra bảng cho chuỗi máy — quyết định `3b` chọn tiếng Anh cố định.
  - Viết bộ đoán ngôn ngữ bằng Python — model tự nhận rồi khai bằng cờ (xem §3).
  - Đổi bất kỳ hành vi nào của workflow ngoài ngôn ngữ: thứ tự phase, luật duyệt, luật
    tick, luật commit đều giữ y nguyên.

## 1b. Lộ trình

Chép từ brief mục `### Lộ trình`. User duyệt spec là duyệt luôn lộ trình này.

| Bước/phase | Chạy? | Vì sao |
|---|---|---|
| Vòng scope | GỘP | request tự khai đủ 4 mặt A–D lấy từ `docs/tdq/audit/da-ngon-ngu.md`; vòng hỏi 7 câu đã phủ cả mặt lẫn bối cảnh |
| Research web | BỎ | việc nội bộ repo, không có ẩn số ngoài |
| Interview | CÓ | đã chạy 1 vòng 7 câu, không còn câu nào đổi được sản phẩm |
| Spec | CÓ | việc lớn, chạm hook + state + test |
| Plan | CÓ | phải chia đợt vì có phụ thuộc cứng giữa các tầng |
| Implement | CÓ | mode do user chốt ở cổng `mode` |
| QC độc lập (agent) | BỎ | luật phiên hiện tại cấm gọi agent khi user không yêu cầu; QC vẫn chạy đủ bằng lệnh |
| Full suite | CÓ | 1 lần ở QC, cộng 1 lần chốt sau mỗi phase đổi chuỗi máy |
| Sinh lại `portable_*` | CÓ | bản portable là bản sao của nguồn, không sinh lại là lệch |
| Report | CÓ | luật chung |

## 2. Đầu ra cụ thể

| # | Đầu ra | Đường dẫn/vị trí | Đo "xong" bằng |
|---|---|---|---|
| 1 | Trường ngôn ngữ tài liệu trong state, ghi lúc `init` qua một cờ; thiếu cờ thì mặc định tiếng Việt | `scripts/tdq_state.py` | `init` có cờ → state giữ đúng mã ngôn ngữ; `init` không cờ → state giữ mặc định tiếng Việt; request cũ đọc lên không lỗi |
| 2 | Cổng duyệt nhận chữ cái `a`–`d` ở cả 4 cổng, và nhận từ khoá tiếng Anh | `hooks/scripts/prompt_context.py` | câu duyệt tiếng Việt cũ, câu tiếng Anh, và chữ cái đơn đều được nhận; câu nhiễu và câu hỏi vẫn bị từ chối |
| 3 | Chuỗi máy in ra cho user bằng tiếng Anh | `hooks/**/*.py`, `scripts/**/*.py` | không còn chuỗi in ra chứa ký tự tiếng Việt |
| 4 | Luật ngôn ngữ mới: luật viết tiếng Anh, tài liệu viết theo ngôn ngữ user | `skills/tdq-conventions/` | luật cũ "mọi output tiếng Việt" không còn; luật mới nêu rõ 3 tầng và giá trị mặc định |
| 5 | Toàn bộ thân luật bằng tiếng Anh | `skills/**/*.md`, `agents/*.md` | không còn dòng tiếng Việt ngoài phần trích dẫn ví dụ được đánh dấu |
| 6 | Lưới test/eval cập nhật + ca đa ngôn ngữ | `tests/`, `evals/` | suite xanh ở mức mốc; có ca duyệt bằng tiếng Anh và ca duyệt bằng chữ cái |
| 7 | Bản portable sinh lại khớp nguồn | `portable_claude/`, `portable_codex/` | lệnh sinh chạy sạch và bản sinh khớp nguồn |
| 8 | Quyết định ngôn ngữ ghi vào hồ sơ kiến trúc | `docs/kien-truc.md` mục `## Đã chốt` | có dòng ngày + nội dung quyết định |

## 2b. Ranh giới module

| Module | Vùng file | Phụ thuộc module | Đầu ra §2 nào |
|---|---|---|---|
| M1 luật nền | `skills/tdq-conventions/` | không | 4 |
| M2 skill khung | `skills/tdq-intake/`, `skills/tdq-spec/`, `skills/tdq-plan/`, `skills/tdq-build/`, `skills/tdq-status/`, `agents/` | M1 | 5 |
| M3 cổng máy | `hooks/scripts/` | không | 2, 3 (phần hook) |
| M4 CLI & state | `scripts/` | không | 1, 3 (phần CLI) |
| M5 lưới | `tests/`, `evals/` | M3, M4 | 6 |
| M6 bản sinh & hồ sơ | `portable_claude/`, `portable_codex/`, `docs/kien-truc.md` | M1, M2, M3, M4 | 7, 8 |

## 3. Cách tiếp cận & lý do

- **Chọn**: tách ba tầng theo người đọc. Luật → tiếng Anh cố định (model đọc, không phải
  user). Chuỗi máy → tiếng Anh cố định (quyết định `3b`). Tài liệu + đối thoại → biến
  ngôn ngữ đọc từ state (quyết định `4a`).
- **Vì**: gộp ba tầng vào một luật ngôn ngữ duy nhất chính là gốc của ràng buộc hiện tại —
  mã K8 và K9 trong `docs/tdq/audit/da-ngon-ngu.md` chứng minh chỉ có một dòng luật cứng
  và 6 dòng nhắc lại, không có tầng nào phân biệt người đọc.
- **Nhận diện ngôn ngữ**: model tự nhận từ câu của user rồi khai bằng cờ lúc `init`; state
  lưu lại; thiếu cờ thì rơi về tiếng Việt. Đã loại: viết bộ đoán ngôn ngữ bằng Python —
  thêm phụ thuộc, và đoán kém hơn chính model đang đọc câu đó.
- **Thứ tự thi hành**: sửa máy trước (M3, M4), rồi luật (M1, M2), rồi lưới (M5), cuối cùng
  sinh lại bản portable (M6). Lý do: đổi chuỗi máy làm đỏ test, phải sửa test cùng lượt;
  còn dịch luật thì không có phép kiểm máy nào bắt được, nên phải nằm sau khi lưới đã ổn.
- **Đã loại**: dịch từng phần rồi để repo lẫn hai ngôn ngữ nhiều turn — trạng thái nửa vời
  làm model đọc luật mâu thuẫn, rủi ro cao hơn chính việc dịch.

## 3b. Năng lực & công cụ

| Skill | Nguồn | Phán quyết | Dùng ở đâu / Lý do loại |
|---|---|---|---|
| tdq-intake | plugin:tdq-workflow | NỀN | skill khung đang chạy |
| tdq-spec | plugin:tdq-workflow | DÙNG | viết spec này; cũng là đối tượng bị dịch (đầu ra 5) |
| tdq-plan | plugin:tdq-workflow | DÙNG | viết plan; cũng là đối tượng bị dịch (đầu ra 5) |
| tdq-build | plugin:tdq-workflow | DÙNG | chạy implement/QC/report (đầu ra 5) |
| tdq-conventions | plugin:tdq-workflow | DÙNG | luật gốc về ngôn ngữ (đầu ra 4) |
| tdq-status | plugin:tdq-workflow | DÙNG | khuôn `➤ Duyệt:` nằm trong đây (đầu ra 2, 5) |
| Đã xét 280 skill khác | user/plugin/built-in | KHÔNG | khác lĩnh vực |

## 4. Yêu cầu bắt buộc

- Log service bật mặc định: timestamp, đủ chi tiết debug, tắt/giảm được qua config. Việc
  này CÓ runtime (sửa `hooks/`, `scripts/`), nên dòng này áp dụng: mọi dòng log đang có
  giữ nguyên định dạng `[timestamp] …`, chỉ đổi ngôn ngữ phần chữ.
- Không placeholder, không TODO stub, không mock trình bày như dữ liệu thật.
- Mỗi thành phần có unit test riêng, chạy được bằng một lệnh.
- Code viết ra bám 5 nguyên tắc SOLID theo `skills/tdq-conventions/references/clean-code.md`,
  và bám rule ngôn ngữ trong `skills/tdq-build/references/rules/`.
- **Giữ hành vi tuyệt đối**: dịch KHÔNG được đổi tên lệnh, tên trường state, mã `[TDQ:*]`,
  mã task, tên file, thứ tự phase, hay ngưỡng số nào. Dịch là đổi chữ, không đổi luật.
- **Giữ soul**: dòng `Soul: chất lượng > runtime > context cost` và
  `references/soul.md` là luật gốc — chỉ dịch chữ, cấm đổi nội dung hay thứ tự ưu tiên.

## 5. Ràng buộc & rủi ro

Ràng buộc kiến trúc phải giữ (chép từ `docs/kien-truc.md`):

- "`hooks/` được gọi `scripts/`; `scripts/` **không** được import `hooks/`" — việc này chạm
  cả hai tầng khi đổi chuỗi máy, phải giữ nguyên chiều gọi.
- "`skills/` chỉ được **nhắc tên lệnh** của `scripts/`, cấm chép nội dung script vào skill"
  — khi dịch skill, cấm chép thêm nội dung script vào để "giải thích cho rõ".
- "Chỉ `scripts/tdq_state.py` được ghi `docs/tdq/state.json`" — trường ngôn ngữ mới (đầu ra
  1) phải nằm trong file đó, không có nơi nào khác ghi.
- "`portable_claude/`, `portable_codex/` SINH bằng `scripts/build_portable.py` … không sửa
  tay" — cấm dịch tay trong hai thư mục này.
- Hub `main()`, `cli()`, `log()` (bậc 20/17/17) nằm trong `scripts/` và sẽ bị chạm khi đổi
  chuỗi — plan phải khai `Chạm:` và thêm dòng DoD kiểm hồi quy riêng.

| Rủi ro | Ảnh hưởng | Cách giảm |
|---|---|---|
| Đổi chuỗi máy làm đỏ 19 file test đang assert chuỗi/ký hiệu tiếng Việt | suite đỏ hàng loạt, khó biết lỗi thật hay lỗi chuỗi | mỗi task đổi chuỗi đi kèm task sửa test của đúng module đó trong cùng phase; chạy test module ngay, không dồn tới QC |
| Dịch luật làm model đổi hành vi mà không phép kiểm nào bắt được | workflow chạy sai lặng lẽ | giữ nguyên mọi tên lệnh/nhãn/mã; sau khi dịch, chạy bộ `evals/tuan-thu` — đây là lưới duy nhất đo hành vi model |
| Repo lẫn hai ngôn ngữ giữa chừng | model đọc luật mâu thuẫn ngay trong lúc đang sửa chính nó | dịch trọn một module trong một phase, không để module nào dở dang qua phase sau |
| Chữ cái `a`–`d` nuốt câu thật (vd user gõ "c" nghĩa khác) | duyệt nhầm | giữ neo `^…$` và ranh giới từ như regex `LETTER` hiện tại; bộ ca âm cũ phải vẫn trượt |
| Bản `portable_*` lệch nguồn sau khi dịch | user cài bản portable nhận luật cũ | sinh lại ở phase cuối và kiểm khớp nguồn |
| User tiếng Việt thấy dòng máy đổi sang tiếng Anh | trải nghiệm đổi đột ngột | đã là quyết định `3b` của user; report nêu lại rõ ràng |

## 6. QC & Definition of Done

| # | Hạng mục kiểm | Điều kiện PASS |
|---|---|---|
| Q1 | trường ngôn ngữ trong state | `init` kèm cờ → state giữ đúng mã; `init` không cờ → giữ mặc định tiếng Việt; state của request cũ đọc lên không lỗi |
| Q2 | cổng duyệt: đường cũ | mọi câu duyệt tiếng Việt đang được nhận hôm nay vẫn được nhận, ở cả 4 cổng |
| Q3 | cổng duyệt: đường mới | câu duyệt tiếng Anh và chữ cái `a`–`d` đứng riêng đều được nhận ở cả 4 cổng |
| Q4 | cổng duyệt: đường phải chặn | câu hỏi, câu nhiễu, và câu phủ định (cả tiếng Việt lẫn tiếng Anh) vẫn bị từ chối |
| Q5 | chuỗi máy | không còn chuỗi in ra cho user chứa ký tự tiếng Việt trong `hooks/` và `scripts/` |
| Q6 | comment mã nguồn | không còn comment/docstring tiếng Việt trong `hooks/` và `scripts/` |
| Q7 | thân luật | không còn dòng tiếng Việt trong `skills/**/*.md` và `agents/*.md`, trừ phần trích dẫn ví dụ được đánh dấu rõ |
| Q8 | giữ hành vi | mọi tên lệnh, tên trường state, mã `[TDQ:*]`, tên file, thứ tự phase giữ nguyên so với trước khi dịch |
| Q9 | giữ soul | dòng `Soul:` và nội dung `references/soul.md` giữ đúng thứ tự ưu tiên, chỉ đổi ngôn ngữ |
| Q10 | luật ngôn ngữ mới | `tdq-conventions` nêu đủ 3 tầng người đọc và giá trị mặc định khi thiếu ngôn ngữ |
| Q11 | lưới | suite xanh ở mức mốc đo lúc bắt đầu; có ít nhất 1 ca eval duyệt tiếng Anh và 1 ca duyệt bằng chữ cái |
| Q12 | bản sinh | `portable_claude/` và `portable_codex/` sinh lại sạch và khớp nguồn |
| Q13 | log service | mọi dòng log giữ định dạng timestamp và vẫn tắt/giảm được qua config |
| Q14 | hồ sơ kiến trúc | `docs/kien-truc.md` có dòng `## Đã chốt` ghi quyết định ngôn ngữ kèm ngày |

DoD: 14 hạng mục trên PASS, có bằng chứng lệnh thật trong file qc; không task nào trong
plan còn `[ ]`; không file nào ngoài phạm vi §1 bị sửa.

## 7. Câu hỏi còn mở

(rỗng)
