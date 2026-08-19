# Khuôn spec

Copy the whole block below into `docs/tdq/spec/<slug>.md` and fill it in. Drop a section
that does not apply, but say **vì sao** it does not apply.

```markdown
# SPEC — <tên việc>

Ngày: YYYY-MM-DD · Bản: 1.0 · Brief: ../brief/<slug>.md · Lane: full
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
- §6 giữ điều kiện, KHÔNG giữ lệnh kiểm
- Kiểm trước khi trình
- Checklist scope — trả lời được hết mới trình

## 1. Mục tiêu & phạm vi
- Mục tiêu: <1–3 câu, đo được>
- Trong phạm vi: <gạch đầu dòng>
- NGOÀI phạm vi: <gạch đầu dòng — nêu rõ để khỏi trôi việc. Có chạy vòng scope thì
  BẮT BUỘC chép các mặt bị loại ở brief `### Phạm vi đã chốt` vào đây>

## 1b. Lộ trình
Chép từ brief mục `### Lộ trình`. User duyệt spec là duyệt luôn lộ trình này.

| Bước/phase | Chạy? | Vì sao |
|---|---|---|
| Research web | CÓ/BỎ | <lý do> |
| Interview | CÓ/BỎ | <lý do> |
| QC độc lập (agent) | CÓ/BỎ | <lý do> |

## 2. Đầu ra cụ thể
| # | Đầu ra | Đường dẫn/vị trí | Đo "xong" bằng |
|---|---|---|---|
| 1 | | | |

## 2b. Ranh giới module

Chia việc thành các module tách rời được, để phase `plan` có sẵn đường cắt. Một module =
một vùng file không giao với module khác. Bắt buộc với lane full; lane quick BỎ mục này.

| Module | Vùng file | Phụ thuộc module | Đầu ra §2 nào |
|---|---|---|---|
| <tên ngắn> | `<đường/dẫn>`, `<đường/dẫn>` | <tên module khác, hoặc "không"> | <số thứ tự ở §2> |

Hai module không được khai chung một đường dẫn. Trùng nghĩa là chưa tách xong — gộp lại
thành một module, hoặc tách file ra trước.

## 3. Cách tiếp cận & lý do
- Chọn: <cách làm>
- Vì: <lý do, kèm nguồn research nếu có>
- Đã loại: <phương án> — vì <lý do>

## 3b. Năng lực & công cụ
Chép từ brief mục `### Năng lực dùng được`. Phân vân → DÙNG.
Một dòng cho mỗi skill DÙNG hoặc NỀN, cộng đúng một dòng tổng cho phần còn lại.
Không xoá mục này kể cả khi không có dòng DÙNG nào.
Phán quyết chỉ nhận: DÙNG / KHÔNG (+ 1 trong 4 lý do đóng) / NỀN (skill khung đang chạy).

| Skill | Nguồn | Phán quyết | Dùng ở đâu / Lý do loại |
|---|---|---|---|
| <tên> | <user\|project\|plugin:x\|built-in> | DÙNG | <đầu ra hoặc task nào> |
| Đã xét <N> skill khác | user/plugin/built-in | KHÔNG | khác lĩnh vực |

## 4. Yêu cầu bắt buộc
- Log service bật mặc định: timestamp, đủ chi tiết debug, tắt/giảm được qua config.
  Dòng này bắt buộc **chỉ khi việc này có runtime** — tức plan sẽ có ít nhất một task tạo
  hoặc sửa file mã nguồn chạy được. Không có runtime (chỉ sửa tài liệu, khuôn mẫu, cấu
  hình) → thay dòng này bằng `Log service: BỎ — <lý do một câu>`.
- Không placeholder, không TODO stub, không mock trình bày như dữ liệu thật.
- Mỗi thành phần có unit test riêng, chạy được bằng một lệnh.
- Code viết ra bám 5 nguyên tắc SOLID theo
  `skills/tdq-conventions/references/clean-code.md`, và bám rule ngôn ngữ trong
  `skills/tdq-build/references/rules/`. Luật này luôn áp, không có cổng bật/tắt.

## 5. Ràng buộc & rủi ro
Ràng buộc kiến trúc phải giữ (chép từ `docs/kien-truc.md` — chỉ những dòng việc này
chạm tới, không chép cả file):
- <nguyên văn dòng luật gọi / đã chốt> — việc này chạm ở <file/hàm>

Không chạm dòng nào → ghi `Ràng buộc kiến trúc phải giữ: không chạm dòng nào — <lý do
một câu>`. Chưa có `docs/kien-truc.md` → quay lại analyze sinh theo luật hồ sơ kiến
trúc, không bỏ trống khối này.

| Rủi ro | Ảnh hưởng | Cách giảm |
|---|---|---|

## 6. QC & Definition of Done
| # | Hạng mục kiểm | Điều kiện PASS |
|---|---|---|
| Q1 | | |

DoD: <liệt kê điều kiện đủ để tuyên bố xong>

## 7. Câu hỏi còn mở
(Phải RỖNG. Còn câu hỏi → quay lại phase analyze.)
```

## §6 giữ điều kiện, KHÔNG giữ lệnh kiểm

The spec is sealed with a sha256 when the user approves it, while **a concrete check
command is only correct AFTER the code exists** — test file name, selection flag, function
name. Write those into the spec and a wrong name found at QC time forces a re-approval,
even though the intent did not change by a single word. Measured in 2 of 7 cases in
`docs/tdq/reports/2026-08-18-2050-spec-doi-sau-khi-duyet.md`.

So: **the spec carries the PASS CONDITION, the plan carries the CHECK COMMAND.** The plan
is not sealed, so renaming a test file there is everyday work and touches no approval gate.

| Viết ở spec (ĐÚNG) | Viết ở spec (SAI — chuyển sang plan) |
|---|---|
| sửa dòng sổ sách không làm đổi sha, sửa mục đánh số thì đổi | `pytest tests/test_state.py -q -k sha` xanh |
| spec mới ghi lệnh kiểm thì linter chặn, spec cũ vẫn qua | `pytest tests/test_doc_lint.py -q -k r11` xanh |

Rule **R11** of `doc_lint.py` guards exactly this, and applies only to specs from
2026-08-19 onward.

## Kiểm trước khi trình

- Every output in §2 has at least one QC item in §6.
- §6 holds no `tests/...` path and no `-k` flag — the check command lives in the plan.
- §1b is present: every workflow step/phase says CÓ or BỎ, with the reason.
- §2b is present in lane full: one row per module, no two modules declaring one path.
- §3b is present: one row per skill marked DÙNG or NỀN, everything else merged into the
  summary row `Đã xét <N> skill khác` — machine-checked by `doc_lint.py` rule R8.
- A PASS condition in §6 is measurable by a command, not by feel.
- §7 is empty.
- No sentence uses a vague word ("phù hợp", "tối ưu", "nếu cần") without a concrete
  threshold beside it.

## Checklist scope — trả lời được hết mới trình

| Câu hỏi | Trả lời phải nằm ở |
|---|---|
| What does this work PRODUCE? | §1 mục tiêu + §2 bảng đầu ra |
| Are the areas dropped at the scope round written down? | §1 mục NGOÀI phạm vi |
| What is NEW compared with what exists today? | §3 cách tiếp cận |
| Which file/command/screen exactly is the output? | §2 cột đường dẫn/vị trí |
| Is a model needed (name, where it runs, cost)? | §1 phạm vi + §5 ràng buộc |
| Is any download/install needed? | §5 ràng buộc — ghi rõ tên gói và bản |
| How is QC/test/validate done? | §6 bảng QC + DoD |

One box still unanswered → the spec is not ready to present, go back to phase analyze.
