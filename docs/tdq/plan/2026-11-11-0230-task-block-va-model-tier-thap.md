# PLAN — Hiện thực Task Block chi tiết và Tự động gọi Model Tier thấp ở Implement

Ngày: 2026-11-11 · Spec: ../spec/2026-11-11-0230-task-block-va-model-tier-thap.md (bản 1.0, ĐÃ DUYỆT) · Lane: full
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md
Mode thực thi: subagent — tdq_bench đo nhanh hơn 10.2 phút qua 2 wave (ĐỀ XUẤT, user chốt lúc duyệt)
Trạng thái plan: ĐÃ DUYỆT

## Mục lục

- Quy tắc thi hành (áp cho mọi task)
- Thiết kế Trước vs Sau
- P1 — Hiện thực Rule R15 trong doc_lint.py và bộ Unit Test (TDD)
- P2 — Cập nhật Plan Template, Hướng dẫn và Tài liệu Team Mode
- P3 — Cập nhật cấu hình Model cho subagent tdq-implementer
- P4 — Log & test bắt buộc
- Definition of Done
- Cụm song song
- Luật file nóng (một file, nhiều task chạm)

## Quy tắc thi hành (áp cho mọi task)

1. Thứ tự phase là thứ tự phụ thuộc — không đảo.
2. Mỗi task: đánh `[~]` khi bắt đầu → viết test trước (đỏ) → code → test xanh → đổi sang `[x]` NGAY vào file này. Trạng thái checkbox: `[ ]` chưa làm · `[~]` đang làm · `[x]` xong.
3. Mỗi bước: `pytest tests/test_doc_lint_r15.py` đảm bảo không gây hồi quy.
4. Lệnh nào chạm state của workflow phải có `TDQ_PROJECT_DIR=<thư mục tạm>` ngay trên chính lệnh đó.
5. QC FAIL → thêm task fix vào mục QC của file này (không cần duyệt lại), loop đến khi pass.
6. Không commit/push cho đến khi user yêu cầu.
7. Tuân thủ 6 mã cấm cơ học (ANTI-1 Fake Red, ANTI-2 Blind Assertion, ANTI-3 Dirty State Git, ANTI-4 Late Tick, ANTI-5 Raw Dump, ANTI-6 Broad Area).

## Thiết kế Trước vs Sau

| Khía cạnh | Hiện trạng (Trước) | Thiết kế mới (Sau) |
|---|---|---|
| Cấu trúc task Plan | 1 dòng tóm tắt duy nhất, không có chi tiết kỹ thuật | Khối Self-Contained Task Block 8 trường + 4 chốt an toàn |
| Cưỡng chế Linter | Chỉ kiểm tra định dạng dòng `- [ ]` và dòng `Chạm:` | Rule R15 chặn cứng (exit 1) nếu task code thiếu logic |
| Model của Subagent | Kế thừa model lớn của parent (`inherit` - Sonnet/Opus) | Cố định `model: haiku` rẻ hơn 15x, tốc độ vượt trội |
| Giao tiếp Subagent | Subagent chỉ nhận 1 dòng, không đọc Spec, phải đoán mò | Subagent nhận trọn vẹn đặc tả hàm, giải thuật từng bước |

*Đối chiếu sơ đồ kiến trúc:* Tham chiếu bản xem trước [docs/tdq/spec/2026-11-11-0230-task-block-va-model-tier-thap-preview.html](../spec/2026-11-11-0230-task-block-va-model-tier-thap-preview.html) và manifest `2026-11-11-0230-task-block-va-model-tier-thap-preview.manifest.json` đã duyệt.

## P1 — Hiện thực Rule R15 trong doc_lint.py và bộ Unit Test (TDD)

- [x] **T1.1** (e5m) Viết test suite đỏ cho Rule R15 kiểm chứng bắt plan sơ sài và chấp thuận plan chi tiết — Test: `pytest tests/test_doc_lint_r15.py`
  - Chạm: `tests/test_doc_lint_r15.py`
  - Mục tiêu: Thiết lập tiêu chí kiểm thử cho Rule R15: task sửa code không có logic -> báo lỗi exit 1; task sửa code có logic -> pass exit 0; task docs 1 dòng -> pass exit 0.
  - Vị trí neo: Tạo mới file `tests/test_doc_lint_r15.py`.
  - Công cụ: Dùng `Write` tạo mới test file.
  - Ràng buộc: Thuần unittest / pytest, test assertion chặt chẽ (ANTI-2 guard).
  - Đặc tả kỹ thuật:
    Test cases: `test_r15_fails_on_single_line_code_task`, `test_r15_passes_on_detailed_code_task`, `test_r15_passes_on_doc_only_task`.
  - Logic cốt lõi:
    1. Tạo plan tạm có task chạm file `.py` chỉ có 1 dòng -> chạy `doc_lint.py` -> mong đợi vi phạm R15.
    2. Tạo plan tạm có task chạm file `.py` có dòng `- Đặc tả:` hoặc `- Logic:` -> chạy `doc_lint.py` -> mong đợi 0 vi phạm.
    3. Tạo plan tạm có task chạm file `.md` 1 dòng -> chạy `doc_lint.py` -> mong đợi 0 vi phạm.
  - Ca góc hiểm & TDD:
    - RED: Lệnh `pytest tests/test_doc_lint_r15.py` phải fail vì doc_lint chưa có hàm `rule_r15`.
- [x] **T1.2** (e8m) Hiện thực hàm `rule_r15` trong `scripts/doc_lint.py` và tích hợp vào danh sách RULES — Test: `pytest tests/test_doc_lint_r15.py`
  - Chạm: `scripts/doc_lint.py`
  - Cần: T1.1
  - Mục tiêu: Bổ sung logic kiểm tra độ sâu kỹ thuật cho các task can thiệp mã nguồn trong Plan.
  - Vị trí neo: Trong `scripts/doc_lint.py`, đặt ngay sau hàm `rule_r14` và trước `RULES`.
  - Công cụ: Dùng `Edit`. CẤM dùng `Write` trên `doc_lint.py`.
  - Ràng buộc: Thuần stdlib, hàm dưới 40 dòng, complexity <= 10.
  - Đặc tả kỹ thuật:
    `EXT_MA_NGUON = (".py", ".ts", ".tsx", ".js", ".jsx", ".go", ".rs", ".c", ".cpp", ".cs", ".rb", ".php", ".java")`
    `TU_KHOA_LOGIC = ("đặc tả", "logic", "giải thuật", "thuật toán", "pseudo-code")`
    `def rule_r15(doc, out):`
  - Logic cốt lõi:
    1. Kiểm tra nếu thư mục cha của doc không phải `"plan"` thì return.
    2. Duyệt qua từng task trong doc. Nếu task có khai báo `Chạm:` chứa file thuộc `EXT_MA_NGUON`:
    3. Quét các dòng con thụt lề bên dưới. Kiểm tra xem có dòng nào chứa từ khóa trong `TU_KHOA_LOGIC` không.
    4. Nếu không có dòng nào: gọi `_report(out, doc, line_idx, "R15", "task can thiệp mã nguồn nhưng thiếu khối đặc tả kỹ thuật/pseudo-code (Rule R15: Self-Contained Task Block)")`.
    5. Thêm `rule_r15` vào danh sách `RULES`.
  - Ca góc hiểm & TDD:
    - Task không có `Chạm:` hoặc chỉ chạm `.md`/`.json`: bỏ qua, không báo lỗi.
    - GREEN: `pytest tests/test_doc_lint_r15.py` chuyển xanh 100%.

**Xong P1 khi**: Rule R15 hoạt động chính xác và toàn bộ unit test của nó đều xanh.

## P2 — Cập nhật Plan Template, Hướng dẫn và Tài liệu Team Mode

- [x] **T2.1** (e5m) Cập nhật `plan-template.md` với cú pháp Task Block 8 trường và 4 chốt an toàn — Test: `python scripts/doc_lint.py skills/tdq-plan/references/plan-template.md`
  - Chạm: `skills/tdq-plan/references/plan-template.md`
  - Cần: T1.2
  - Mục tiêu: Cung cấp bản mẫu chuẩn của Self-Contained Task Block và các ví dụ thi công trực quan.
  - Vị trí neo: Mục `## P1 — <tên phase>` và mục hướng dẫn dòng `Chạm:`.
  - Công cụ: Dùng `Edit`.
  - Ràng buộc: Giữ nguyên cấu trúc template và chú thích i18n-allow.
  - Đặc tả kỹ thuật:
    Bổ sung các trường con: `Mục tiêu:`, `Vị trí neo:`, `Công cụ:`, `Ràng buộc:`, `Đặc tả kỹ thuật:`, `Logic cốt lõi:`, `Ca góc hiểm & TDD:`.
  - Logic cốt lõi:
    1. Cập nhật phần mẫu task P1 với đầy đủ 8 trường con.
    2. Bổ sung mục giải thích 4 chốt an toàn cơ học cho model 30B/Haiku.
  - Ca góc hiểm & TDD:
    - Kiểm tra `doc_lint.py` trên `plan-template.md` đạt 0 lỗi.
- [x] **T2.2** (e4m) Cập nhật `plan-template-huong-dan.md` bổ sung quy tắc phân tầng thích ứng (Adaptive) — Test: `python scripts/doc_lint.py skills/tdq-plan/references/plan-template-huong-dan.md`
  - Chạm: `skills/tdq-plan/references/plan-template-huong-dan.md`
  - Cần: T2.1
  - Mục tiêu: Hướng dẫn người viết plan khi nào dùng Full Block (bắt buộc cho code), khi nào dùng Compact (cho docs).
  - Vị trí neo: Thêm mục `## Phân tầng thích ứng (Adaptive Granularity)`.
  - Công cụ: Dùng `Edit`.
  - Ràng buộc: Ngắn gọn, súc tích, dễ hiểu cho mọi model.
  - Logic cốt lõi:
    Quy định rõ: Task sửa code -> Bắt buộc Full Block (Rule R15 kiểm soát); Task docs -> Dạng 1 dòng.
- [x] **T2.3** (e4m) Cập nhật `skills/tdq-build/references/team-mode.md` với mẫu prompt delegation nạp đủ Task Block và cơ chế model override linh hoạt — Test: `python scripts/doc_lint.py skills/tdq-build/references/team-mode.md`
  - Chạm: `skills/tdq-build/references/team-mode.md`
  - Cần: T2.1
  - Mục tiêu: Hướng dẫn Leader sao chép trọn vẹn Task Block vào prompt chuyển giao cho subagent, và cho phép override model tier cao khi task phức tạp.
  - Vị trí neo: Mục `### The delegation prompt template` và phần hướng dẫn điều phối model.
  - Công cụ: Dùng `Edit`.
  - Logic cốt lõi:
    1. Cập nhật trường `TASK:` trong template delegation: chép nguyên văn cả dòng task lẫn các dòng thụt lề đặc tả logic bên dưới.
    2. Bổ sung nguyên tắc điều phối: Mặc định subagent chạy `model: haiku`; khi task phức tạp (thuật toán nặng, bảo mật, core module), Leader chủ động override `model: "sonnet"` hoặc `model: "opus"` qua tham số gọi Agent. Không bó cứng.
- [x] **T2.4** (e3m) Đồng bộ sơ đồ Trước/Sau và bản xem trước Archify HTML — Test: `python scripts/tdq_archify.py verify --document docs/tdq/spec/2026-11-11-0230-task-block-va-model-tier-thap.md --manifest docs/tdq/spec/2026-11-11-0230-task-block-va-model-tier-thap-preview.manifest.json --project C:/Users/admin/Documents/Projects/ForAgentCode/TDQ-Workflow`
  - Chạm: `docs/tdq/artifacts/2026-11-11-0230-task-block-va-model-tier-thap/truoc-sau.archify.md`
  - Dùng: Archify CLI (`tdq_archify.py`)
  - Để: Render và verify preview HTML cho spec và report
  - Ra: `docs/tdq/spec/2026-11-11-0230-task-block-va-model-tier-thap-preview.html`
  - Kiểm: `python scripts/tdq_archify.py verify --document docs/tdq/spec/2026-11-11-0230-task-block-va-model-tier-thap.md --manifest docs/tdq/spec/2026-11-11-0230-task-block-va-model-tier-thap-preview.manifest.json --project C:/Users/admin/Documents/Projects/ForAgentCode/TDQ-Workflow`
  - Không dùng cho: Sửa đổi code linter

**Xong P2 khi**: Toàn bộ tài liệu quy chuẩn Plan và Team Mode đều cập nhật xong, đạt 0 vi phạm doc_lint.

## P3 — Cập nhật cấu hình Model cho subagent tdq-implementer

- [x] **T3.1** (e3m) Cập nhật cấu hình frontmatter trong `agents/tdq-implementer.md` sang `model: haiku` (hỗ trợ override tier cao) — Test: `grep -E "^model:\s*haiku" agents/tdq-implementer.md`
  - Chạm: `agents/tdq-implementer.md`
  - Mục tiêu: Cấu hình subagent thực thi tự động chạy trên model Haiku làm mặc định để tiết kiệm chi phí, đồng thời tài liệu hóa khả năng ghi đè model tier cao.
  - Vị trí neo: Dòng 4 của `agents/tdq-implementer.md`.
  - Công cụ: Dùng `Edit`.
  - Đặc tả kỹ thuật:
    Đổi `model: inherit` thành `model: haiku`.
    Đổi `effort: high` thành `effort: medium`.
  - Logic cốt lõi:
    Khi task đã có Micro-Spec chi tiết từng bước, model Haiku ở effort medium hoàn toàn đủ năng lực code chính xác 100% mà không lãng phí token suy luận sâu không cần thiết. Với task phức tạp, Leader ghi đè `model: sonnet / opus` khi gọi tool Agent.

**Xong P3 khi**: Frontmatter của `agents/tdq-implementer.md` khai báo đúng `model: haiku`.

## P4 — Log & test bắt buộc

- [x] **T4.1** (e3m) Log service bật mặc định kiểm chứng log stderr qua `TDQ_LOG` — Test: `pytest tests/test_doc_lint_r15.py`
  - Chạm: `scripts/doc_lint.py`
  - Cần: T1.2
  - Đặc tả kỹ thuật:
    Hàm `_log(message)` ghi log ra stderr khi `TDQ_LOG != "0"`.
  - Logic cốt lõi:
    Kiểm tra cơ chế log service trong `doc_lint.py` xuất stderr kèm timestamp chuẩn ISO.
- [x] **T4.2** (e5m) Chạy toàn bộ test suite kiểm tra không có hồi quy — Test: `pytest tests/test_doc_lint.py tests/test_doc_lint_r15.py`
  - Chạm: `tests/test_doc_lint_r15.py`
  - Dùng: `tdq-build`
  - Để: Thực thi build và QC mức ultra
  - Ra: `docs/tdq/qc/2026-11-11-0230-task-block-va-model-tier-thap.md`
  - Kiểm: `pytest tests/test_doc_lint.py tests/test_doc_lint_r15.py`
  - Không dùng cho: Sửa đổi file ngoài phạm vi
  - Đặc tả kỹ thuật:
    Chạy toàn bộ 68 test case trong các tệp kiểm thử doc_lint.
  - Logic cốt lõi:
    Thực thi pytest trên `tests/test_doc_lint.py` và `tests/test_doc_lint_r15.py`, xác nhận 100% green.

**Xong P4 khi**: Toàn bộ unit tests linter và hệ thống chạy qua 100% green.

## Definition of Done

- [ ] Q1 Mẫu Plan Template 8 trường: `plan-template.md` chứa cấu trúc Task Block 8 trường và 4 chốt an toàn — `python scripts/doc_lint.py skills/tdq-plan/references/plan-template.md`
- [ ] Q2 Hướng dẫn phân tầng thích ứng: `plan-template-huong-dan.md` có hướng dẫn Adaptive Granularity — `python scripts/doc_lint.py skills/tdq-plan/references/plan-template-huong-dan.md`
- [ ] Q3 Linter Rule R15 bắt đúng lỗi: `doc_lint.py` bắt đúng lỗi exit 1 khi task code viết 1 dòng sơ sài — `pytest tests/test_doc_lint_r15.py -k test_r15_fails_on_single_line_code_task`
- [ ] Q4 Linter Rule R15 cho qua plan chi tiết: `doc_lint.py` thoát mã 0 với task có đặc tả logic hoặc task docs — `pytest tests/test_doc_lint_r15.py -k test_r15_passes_on_detailed_code_task`
- [ ] Q5 Cấu hình subagent `tdq-implementer`: `agents/tdq-implementer.md` có `model: haiku` — `grep -E "^model:\s*haiku" agents/tdq-implementer.md`
- [ ] Q6 Hướng dẫn delegation trong team-mode: `team-mode.md` có hướng dẫn nạp trọn vẹn Task Block — `python scripts/doc_lint.py skills/tdq-build/references/team-mode.md`
- [ ] Q7 Test suite kiểm thử Rule R15: Unit tests trong `tests/` chạy qua 100% green — `pytest tests/test_doc_lint_r15.py`
- [ ] Q8 Bản xem trước Archify HTML: Render thành công, manifest digest khớp tài liệu — `python scripts/tdq_archify.py verify --document docs/tdq/spec/2026-11-11-0230-task-block-va-model-tier-thap.md --manifest docs/tdq/spec/2026-11-11-0230-task-block-va-model-tier-thap-preview.manifest.json --project C:/Users/admin/Documents/Projects/ForAgentCode/TDQ-Workflow`

## Cụm song song

Một cụm tuần tự duy nhất (`main` mode) do các task P1, P2, P3 phụ thuộc lẫn nhau trực tiếp giữa linter `doc_lint.py`, template `plan-template.md` và agent `tdq-implementer.md`.

## Luật file nóng (một file, nhiều task chạm)

- `scripts/doc_lint.py`: T1.2, T4.1 chạm. Áp dụng phương thức: **một chủ ghi duy nhất** tuần tự theo chu trình T1.2 -> T4.1.
- `tests/test_doc_lint_r15.py`: T1.1, T4.2 chạm. Áp dụng phương thức: **một chủ ghi duy nhất** tuần tự theo chu trình T1.1 -> T4.2.
