# PLAN — Nâng cấp tư duy sâu và chặn bẫy lặp tool trong TDQ Workflow

Ngày: 2026-11-11 · Spec: ../spec/2026-11-10-2335-nang-cap-tu-duy-tdq-workflow.md (bản 1.0, ĐÃ DUYỆT) · Lane: full
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md
Mode thực thi: subagent — tdq_bench đo nhanh hơn 6.1 phút qua 2 wave (ĐỀ XUẤT, user chốt lúc duyệt)
Trạng thái plan: HOÀN THÀNH

## Mục lục

- Quy tắc thi hành (áp cho mọi task)
- Thiết kế Trước vs Sau
- P1 — Hiện thực thuật toán Range Overlap trong read_gate.py (TDD)
- P2 — Cập nhật quy chuẩn tư duy phản tư trong Soul và Quick Lane
- P3 — Log & test bắt buộc
- Definition of Done
- Cụm song song
- Luật file nóng (một file, nhiều task chạm)

## Quy tắc thi hành (áp cho mọi task)

1. Thứ tự phase là thứ tự phụ thuộc — không đảo.
2. Mỗi task: đánh `[~]` khi bắt đầu → viết test trước (đỏ) → code → test xanh → đổi sang `[x]` NGAY vào file này. Trạng thái checkbox: `[ ]` chưa làm · `[~]` đang làm · `[x]` xong.
3. Mỗi bước: `pytest tests/test_read_gate.py` đảm bảo không gây hồi quy.
4. Lệnh nào chạm state của workflow phải có `TDQ_PROJECT_DIR=<thư mục tạm>` ngay trên chính lệnh đó.
5. QC FAIL → thêm task fix vào mục QC của file này (không cần duyệt lại), loop đến khi pass.
6. Không commit/push cho đến khi user yêu cầu.
7. Tuân thủ 6 mã cấm cơ học (ANTI-1 Fake Red, ANTI-2 Blind Assertion, ANTI-3 Dirty State Git, ANTI-4 Late Tick, ANTI-5 Raw Dump, ANTI-6 Broad Area).

## Thiết kế Trước vs Sau

| Khía cạnh | Hiện trạng (Trước) | Thiết kế mới (Sau) |
|---|---|---|
| Kiểm tra `offset/limit` | Có `offset/limit` là bỏ qua kiểm tra, `sys.exit(0)` im lặng | Tính toán Range Overlap giữa dải mới và các dải cũ |
| Hỗ trợ file dài | Bị model xé nhỏ thành các lượt đọc 40 dòng lặp vô tận | Cho phép đọc các đoạn khác nhau; chỉ cảnh báo khi đọc lặp 1 đoạn |
| Nhắc nhở AI | Nhắc 1 lần rồi im lặng vĩnh viễn | Nhắc nhở rõ ràng kèm số dòng và số lần lặp khi vượt ngưỡng lặp |
| Nguyên tắc Soul | Chưa có điều khoản về phản tư sau khi đọc mã | Bổ sung quy chuẩn "Reflective Thought", cấm đọc mù mờ |

*Đối chiếu sơ đồ kiến trúc:* Tham chiếu bản xem trước [docs/tdq/spec/2026-11-10-2335-nang-cap-tu-duy-tdq-workflow-preview.html](../spec/2026-11-10-2335-nang-cap-tu-duy-tdq-workflow-preview.html) và manifest `2026-11-10-2335-nang-cap-tu-duy-tdq-workflow-preview.manifest.json` đã duyệt.

## P1 — Hiện thực thuật toán Range Overlap trong read_gate.py (TDD)

- [x] **T1.1** (e5m) Viết test case đỏ kiểm chứng hành vi Range Overlap và đọc file dài — Test: `pytest tests/test_read_gate.py -k "test_im_vung_khac_thi_khong_nhac or test_nhac_khi_lap_doan_offset_limit"`
  - Chạm: `tests/test_read_gate.py` → cập nhật test suite với các ca kiểm thử mới
- [x] **T1.2** (e8m) Cập nhật hàm `_vung`, bổ sung hàm tính độ trùng lặp `_tinh_overlap_ratio` và phát hiện đọc lặp đoạn trong `read_gate.py` — Test: `pytest tests/test_read_gate.py -k test_nhac_khi_lap_doan_offset_limit`
  - Chạm: `hooks/scripts/read_gate.py` → hàm `_tinh_overlap_ratio`, `_dem_lap_doan`, `main`
  - Cần: T1.1
- [x] **T1.3** (e4m) Định dạng thông điệp nhắc nhở `[TDQ:DOC]` trực diện cho AI thoát bẫy lặp — Test: `pytest tests/test_read_gate.py -k test_thong_diep_remind_ai`
  - Chạm: `hooks/scripts/read_gate.py` → chuỗi format nhắc nhở trong `main`
  - Cần: T1.2

**Xong P1 khi**: Toàn bộ unit tests của `read_gate.py` đều chuyển xanh.

## P2 — Cập nhật quy chuẩn tư duy phản tư trong Soul và Quick Lane

- [x] **T2.1** (e4m) Bổ sung quy tắc "Reflective Thought & Hypothesis" vào `soul.md` — Test: `python scripts/doc_lint.py skills/tdq-conventions/references/soul.md`
  - Chạm: `skills/tdq-conventions/references/soul.md` → bổ sung mục Reflective Thought
- [x] **T2.2** (e4m) Cập nhật hướng dẫn khảo sát mã nguồn trong `quick-lane.md` (đọc dải rộng trọn vẹn, cấm xé vụn) — Test: `python scripts/doc_lint.py skills/tdq-intake/references/quick-lane.md`
  - Chạm: `skills/tdq-intake/references/quick-lane.md` → bổ sung lưu ý đọc dải rộng
- [x] **T2.3** (e3m) Đồng bộ sơ đồ Trước/Sau và bản xem trước Archify HTML — Test: `python scripts/tdq_archify.py verify --document docs/tdq/spec/2026-11-10-2335-nang-cap-tu-duy-tdq-workflow.md --manifest docs/tdq/spec/2026-11-10-2335-nang-cap-tu-duy-tdq-workflow-preview.manifest.json`
  - Chạm: `docs/tdq/artifacts/2026-11-10-2335-nang-cap-tu-duy-tdq-workflow/truoc-sau.archify.md`
  - Dùng: Archify CLI (`tdq_archify.py`)
  - Để: Render và verify preview HTML cho spec và report
  - Ra: `docs/tdq/spec/2026-11-10-2335-nang-cap-tu-duy-tdq-workflow-preview.html`
  - Kiểm: `python scripts/tdq_archify.py verify --document docs/tdq/spec/2026-11-10-2335-nang-cap-tu-duy-tdq-workflow.md --manifest docs/tdq/spec/2026-11-10-2335-nang-cap-tu-duy-tdq-workflow-preview.manifest.json`
  - Không dùng cho: Sửa đổi logic hook

**Xong P2 khi**: Cả hai tài liệu quy chuẩn đều tuân thủ doc_lint và Archify binding hợp lệ.

## P3 — Log & test bắt buộc

- [x] **T3.1** (e3m) Log service bật mặc định kiểm chứng log stderr qua `TDQ_LOG` — Test: `pytest tests/test_read_gate.py -k test_log_bat_mac_dinh_co_timestamp`
  - Chạm: `hooks/scripts/read_gate.py` → hàm `_log`
- [x] **T3.2** (e5m) Chạy toàn bộ test suite và kiểm chứng không có hồi quy — Test: `pytest tests/test_read_gate.py`
  - Chạm: `tests/test_read_gate.py`

**Xong P3 khi**: Test suite `tests/test_read_gate.py` hoàn toàn xanh 100%.

## Definition of Done

- [x] Q1 Đọc nhiều đoạn khác nhau file dài: Hook im lặng hoàn toàn (`dang_nhac = False`) — `pytest tests/test_read_gate.py -k test_im_vung_khac_thi_khong_nhac`
- [x] Q2 Đọc lặp lại cùng 1 đoạn ≥ 2 lần: Hook kích hoạt nhắc nhở `[TDQ:DOC]` — `pytest tests/test_read_gate.py -k test_nhac_khi_lap_doan_offset_limit`
- [x] Q3 Đọc toàn bộ file lần 2: Hook kích hoạt nhắc nhở như cũ — `pytest tests/test_read_gate.py -k test_nhac_lan_doc_thu_hai_cua_file_khong_doi`
- [x] Q4 Thời gian chạy của hook: Dưới 10ms mỗi lần gọi — `pytest tests/test_read_gate.py -k test_nhe_khong_spawn_tien_trinh_con`
- [x] Q5 Lint tài liệu và format: `doc_lint.py` thoát mã 0 — `python scripts/doc_lint.py docs/tdq/spec/2026-11-10-2335-nang-cap-tu-duy-tdq-workflow.md`

## Cụm song song

Một cụm tuần tự duy nhất (`main` mode) do các task P1 và P3 phụ thuộc lẫn nhau trực tiếp trên file `hooks/scripts/read_gate.py` và `tests/test_read_gate.py` theo quy trình TDD.

## Luật file nóng (một file, nhiều task chạm)

- `hooks/scripts/read_gate.py`: T1.2, T1.3, T3.1 chạm. Áp dụng phương thức: **một chủ ghi duy nhất** tuần tự theo chu trình T1.2 -> T1.3 -> T3.1.
- `tests/test_read_gate.py`: T1.1, T3.2 chạm. Áp dụng phương thức: **một chủ ghi duy nhất** tuần tự theo chu trình T1.1 -> T3.2.
