# PLAN — Tích Hợp Archify Vào TDQ-Workflow: Trực Quan Hóa BA & Kiến Trúc Dự Án

Ngày: 2026-10-24 · Spec: ../spec/2026-10-24-2145-nghien-cuu-tich-hop-archify.md (bản 1.0, ĐÃ DUYỆT) · Lane: full
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md
Mode thực thi: subagent — mô phỏng đo được đội (subagent) nhanh hơn 10.1 phút (12.3 vs 22.4 phút) nhờ phân tách cụm tài liệu/skill song song với module adapter (ĐÃ CHỐT)
Trạng thái plan: ĐÃ DUYỆT

## Mục lục

- Quy tắc thi hành (áp cho mọi task)
- Thiết kế Trước vs Sau (áp dụng khi Refactor hoặc bổ sung tính năng)
- P1 — Đặc tả kiến trúc hệ thống (Blueprint RFC) & Cấu hình môi trường
- P2 — Module điều phối TDQ-Archify Adapter (Python CLI)
- P3 — Tích hợp quy chuẩn BA vào Spec & Quick Lane và Setup Pre-flight
- P4 — Kiểm thử tự động & Thẩm định QC Độc lập (Ultra)
- Dòng `Chạm:` (đặt NGAY DƯỚI mọi task TẠO hoặc SỬA file mã nguồn)
- Dòng `Cần:` (khai phụ thuộc giữa các task)
- Cụm song song
- Luật file nóng (một file, nhiều task chạm)
- Khuôn khối hợp đồng skill (đặt NGAY DƯỚI dòng task dùng skill đó, ≤6 dòng)
- Px — Log & test bắt buộc
- Definition of Done

## Quy tắc thi hành (áp cho mọi task)
1. Thứ tự phase là thứ tự phụ thuộc — không đảo.
2. Mỗi task: đánh `[~]` khi bắt đầu → viết test trước (đỏ) → code → test xanh → đổi sang `[x]` NGAY vào file này. Trạng thái checkbox: `[ ]` chưa làm · `[~]` đang làm · `[x]` xong.
3. Mỗi bước: `tdq_test.py vung-cham`; trọn bộ chỉ ở QC.
4. Lệnh nào chạm state của workflow phải có `TDQ_PROJECT_DIR=<thư mục tạm>` ngay trên chính lệnh đó.
5. QC FAIL → thêm task fix vào mục QC của file này (không cần duyệt lại), loop đến khi pass.
6. Không commit/push cho đến khi user yêu cầu.
7. Tuân thủ 6 mã cấm cơ học (ANTI-1 Fake Red, ANTI-2 Blind Assertion, ANTI-3 Dirty State Git, ANTI-4 Late Tick, ANTI-5 Raw Dump, ANTI-6 Broad Area).

## Thiết kế Trước vs Sau (áp dụng khi Refactor hoặc bổ sung tính năng)

| Khía cạnh | Hiện trạng (Trước) | Thiết kế mới (Sau) |
|---|---|---|
| Hiển thị luồng trong Spec | Khối Mermaid code text thô sơ trong Markdown, dev khó hình dung toàn cảnh | File HTML tương tác độc lập (`<slug>-preview.html`), có zoom đa tầng, Semantic Passport và motion dòng chảy |
| Khảo sát kiến trúc Graphify | Xuất `CALLFLOW.html` phụ thuộc CDN internet Mermaid.js, sơ đồ tĩnh dễ rối | Chuyển đổi sang Archify viewer offline 100%, hỗ trợ Route-probe tìm đường gọi ngắn nhất và Upstream/Downstream reachability |
| Vai trò BA cho Fresher | Fresher phải tự đọc text và tự hình dung luồng dữ liệu | Có sơ đồ "Personal BA" phân làn UI $\rightarrow$ Core $\rightarrow$ Storage $\rightarrow$ External rõ ràng trước khi code |
| Khả năng mở rộng AI | Phụ thuộc hoàn toàn vào context của Agent trong phiên | Hỗ trợ cơ chế Hybrid: dùng agent hiện tại hoặc cắm Endpoint AI ngoài khi quét toàn bộ repo |

## P1 — Đặc tả kiến trúc hệ thống (Blueprint RFC) & Cấu hình môi trường

- [x] **T1.1** (e15m) Soạn thảo tài liệu đặc tả kiến trúc tích hợp `docs/kien-truc-tich-hop-archify.md` chi tiết 8 phân hệ, mô hình 2 tầng, data contract và cơ chế endpoint — Test: `python3 scripts/doc_lint.py docs/kien-truc-tich-hop-archify.md`
  - Dùng: `archify`
  - Để: Đối chiếu schema JSON-IR và viewer runtime của Archify, nạp skill TRƯỚC bước đỏ
  - Ra: `docs/kien-truc-tich-hop-archify.md`
  - Kiểm: `python3 scripts/doc_lint.py docs/kien-truc-tich-hop-archify.md`
  - Không dùng cho: Sửa mã nguồn gốc trong thư mục archify ngoài

- [x] **T1.2** (e5m) Bổ sung cấu hình biến môi trường AI Endpoint và tài liệu hướng dẫn trong `.env.example` — Test: `.env.example` có đầy đủ biến `ARCHIFY_AI_ENDPOINT`, `ARCHIFY_API_KEY`, `ARCHIFY_MODEL`
  - Dùng: `claude-api`
  - Để: Chuẩn hóa tham số cấu hình endpoint LLM cho adapter, nạp skill TRƯỚC bước đỏ
  - Ra: `.env.example`
  - Kiểm: `git diff .env.example`
  - Không dùng cho: Lưu trữ API key thật (chỉ lưu placeholder)

**Xong P1 khi**: Tài liệu Blueprint và cấu hình `.env.example` hoàn thiện đầy đủ.

## P2 — Module điều phối TDQ-Archify Adapter (Python CLI)

- [x] **T2.1** (e20m) Xây dựng module `scripts/tdq_archify.py` với các hàm cốt lõi (find root, pre-flight kiểm tra Node/Archify, build CLI command, execute finalize, atomic delivery, open file) — Test: `python3 scripts/tdq_archify.py check` chạy thành công
  - Chạm: `scripts/tdq_archify.py`

- [x] **T2.2** (e15m) Bổ sung cầu nối trích xuất và chuyển đổi đồ thị Graphify sang Archify JSON-IR (`graphify_to_archify`) trong `scripts/tdq_archify.py` — Test: `python3 scripts/tdq_archify.py test-bridge`
  - Chạm: `scripts/tdq_archify.py`
  - Cần: T2.1

**Xong P2 khi**: `scripts/tdq_archify.py` thực thi độc lập bằng Python stdlib, cú pháp hợp lệ.

## P3 — Tích hợp quy chuẩn BA vào Spec & Quick Lane và Setup Pre-flight

- [x] **T3.1** (e10m) Cập nhật `skills/tdq-spec/SKILL.md` và `references/spec-template.md` chuẩn hóa việc sinh `<slug>-preview.html` tại §2c — Test: File template phản ánh đúng cú pháp HTML preview và khối duyệt spec
  - Dùng: `tdq-spec`
  - Để: Bổ sung chỉ dẫn sinh sơ đồ BA tương tác vào quy trình spec, nạp skill TRƯỚC bước đỏ
  - Ra: `skills/tdq-spec/SKILL.md`, `skills/tdq-spec/references/spec-template.md`
  - Kiểm: `git diff skills/tdq-spec/`
  - Không dùng cho: Thay đổi các section khác ngoài §2c

- [x] **T3.2** (e8m) Cập nhật `skills/tdq-intake/references/quick-lane.md` bổ sung hướng dẫn sinh mini-workflow cho các task chạm $\ge 2$ module hoặc refactor — Test: `quick-lane.md` có điều kiện kích hoạt rõ ràng
  - Dùng: `tdq-intake`
  - Để: Tích hợp BA preview tinh gọn vào express pipeline, nạp skill TRƯỚC bước đỏ
  - Ra: `skills/tdq-intake/references/quick-lane.md`
  - Kiểm: `git diff skills/tdq-intake/references/quick-lane.md`
  - Không dùng cho: Ép buộc sinh HTML cho task siêu nhỏ

- [x] **T3.3** (e8m) Cập nhật `skills/tdq-plan/references/plan-template.md` hướng dẫn đối chiếu node/boundary kiến trúc từ Archify khi lập WBS — Test: `plan-template.md` có hướng dẫn đối chiếu
  - Dùng: `tdq-plan`
  - Để: Đồng bộ liên kết giữa sơ đồ kiến trúc và kế hoạch task, nạp skill TRƯỚC bước đỏ
  - Ra: `skills/tdq-plan/references/plan-template.md`
  - Kiểm: `git diff skills/tdq-plan/references/plan-template.md`
  - Không dùng cho: Sửa đổi các rule cơ học của plan

- [x] **T3.4** (e10m) Bổ sung bậc kiểm tra Node.js $\ge 18$ và đường dẫn Archify trong `scripts/tdq_setup.py` — Test: `python3 scripts/tdq_setup.py --kiem-archify` chạy không lỗi
  - Chạm: `scripts/tdq_setup.py`
  - Dùng: `tdq-setup`
  - Để: Tự động hóa kiểm tra môi trường chạy của Archify, nạp skill TRƯỚC bước đỏ
  - Ra: `scripts/tdq_setup.py`
  - Kiểm: `python3 scripts/tdq_setup.py`
  - Không dùng cho: Chặn cứng nếu máy chưa có Archify (chỉ cảnh báo)

**Xong P3 khi**: Toàn bộ chỉ dẫn skill và script setup được cập nhật nhất quán.

## P4 — Kiểm thử tự động & Thẩm định QC Độc lập (Ultra)

- [>] **T4.1** (e15m) Xây dựng bộ test suite `tests/test_tdq_archify.py` bao phủ các trường hợp: phát hiện root, build command, kiểm tra lỗi thiếu Node, và parser graphify — Test: `pytest tests/test_tdq_archify.py` đạt 100% PASS
  - Chạm: `tests/test_tdq_archify.py`
  - Cần: T2.1, T2.2

- [ ] **T4.2** (e10m) Chạy kiểm thử tự động toàn diện và thẩm định độc lập theo chuẩn Definition of Done mức `ultra` — Test: Tất cả điều kiện DoD đạt trạng thái PASS
  - Cần: T4.1, T1.1, T3.1, T3.4

**Xong P4 khi**: 100% test PASS và thẩm định QC độc lập hoàn tất.

## Dòng `Chạm:` (đặt NGAY DƯỚI mọi task TẠO hoặc SỬA file mã nguồn)

- `T2.1`: `scripts/tdq_archify.py` → file mới, chưa node nào phụ thuộc
- `T2.2`: `scripts/tdq_archify.py` → mở rộng hàm parse_graphify
- `T3.4`: `scripts/tdq_setup.py` → thêm hàm kiểm tra môi trường Archify
- `T4.1`: `tests/test_tdq_archify.py` → file test mới

## Dòng `Cần:` (khai phụ thuộc giữa các task)

- `T2.2`: Cần T2.1
- `T4.1`: Cần T2.1, T2.2
- `T4.2`: Cần T4.1, T1.1, T3.1, T3.4

## Cụm song song

Plan này được tổ chức thành 2 cụm:
- **Cụm 1 (Tài liệu & Cấu hình):** T1.1, T1.2, T3.1, T3.2, T3.3 có thể chuẩn bị song song vì không phụ thuộc file mã nguồn của nhau.
- **Cụm 2 (Mã nguồn Adapter & Test):** T2.1 $\rightarrow$ T2.2 $\rightarrow$ T3.4 $\rightarrow$ T4.1 $\rightarrow$ T4.2 thực thi tuần tự theo chuỗi phụ thuộc logic.

## Luật file nóng (một file, nhiều task chạm)

File `scripts/tdq_archify.py` bị 2 task chạm (T2.1 và T2.2). Áp dụng luật **một chủ ghi duy nhất**: thực hiện tuần tự T2.1 xong mới chuyển sang T2.2.

## Khuôn khối hợp đồng skill (đặt NGAY DƯỚI dòng task dùng skill đó, ≤6 dòng)

Đã khai báo chi tiết dưới các task T1.1 (`archify`), T1.2 (`claude-api`), T3.1 (`tdq-spec`), T3.2 (`tdq-intake`), T3.3 (`tdq-plan`), T3.4 (`tdq-setup`).

## Px — Log & test bắt buộc

Log: BỎ — Module adapter là CLI utility chạy theo lệnh yêu cầu, không phải service chạy nền daemon.

- [ ] **Tx.1** Unit test cho từng thành phần trong `scripts/tdq_archify.py`, chạy bằng một lệnh — Test: `pytest tests/test_tdq_archify.py`

## Definition of Done

Trỏ về §6 của spec:

- [ ] Q1 Tài liệu Blueprint RFC `docs/kien-truc-tich-hop-archify.md` được soạn thảo đầy đủ 8 phân hệ kiến trúc, mô hình 2 tầng, contract CLI và data schema — `python3 scripts/doc_lint.py docs/kien-truc-tich-hop-archify.md`
- [ ] Q2 Module CLI Adapter `scripts/tdq_archify.py` thực thi độc lập bằng Python stdlib, vượt qua kiểm tra cú pháp và hỗ trợ đầy đủ các lệnh `check`, `render`, `open`, `sync-master` — `python3 scripts/tdq_archify.py check`
- [ ] Q3 Cập nhật Spec Template & Quick Lane: `skills/tdq-spec/SKILL.md`, `spec-template.md` và `quick-lane.md` có hướng dẫn rõ ràng về việc sinh `<slug>-preview.html` — `git diff skills/tdq-spec/ skills/tdq-intake/`
- [ ] Q4 Cấu hình biến môi trường AI Endpoint: `.env.example` khai báo đầy đủ các biến `ARCHIFY_AI_ENDPOINT`, `ARCHIFY_API_KEY`, `ARCHIFY_MODEL` kèm hướng dẫn chi tiết — `git diff .env.example`
- [ ] Q5 Cập nhật Setup & Pre-flight: `scripts/tdq_setup.py` có hàm kiểm tra sự hiện diện của Node.js và gói Archify — `python3 scripts/tdq_setup.py`
- [ ] Q6 Bộ kiểm thử tự động: File `tests/test_tdq_archify.py` có tối thiểu 5 unit tests bao phủ các case: dò đường dẫn, kiểm tra lỗi thiếu node, build CLI command, parse graphify — `pytest tests/test_tdq_archify.py`
- [ ] Q7 Thẩm định QC Độc lập (Ultra): Agent QC độc lập đối soát tài liệu thiết kế và chạy toàn bộ test suite, xác nhận 100% test PASS và không có vi phạm kiến trúc — `python3 scripts/tdq_qc.py danh-gia`
