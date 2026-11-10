# Báo cáo — Nâng cấp tư duy sâu và chặn bẫy lặp tool trong TDQ Workflow

Ngày: 2026-11-11 · Request: 2026-11-10-2335-nang-cap-tu-duy-tdq-workflow · Lane: full
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md
Sơ đồ Archify: docs/tdq/reports/2026-11-10-2335-nang-cap-tu-duy-tdq-workflow.html

## 1. Trước request (trạng thái/flow)
- **Hiện trạng:** Khi khảo sát mã nguồn có `offset` và `limit`, cổng `read_gate.py` dòng 114–116 coi mọi lệnh có chỉ định dòng là "aimed read" và thoát 0 im lặng tuyệt đối.
- **Bẫy tự hồi quy:** Khi model gặp hàm phức tạp, mô hình bị khóa vào chuỗi gọi tool liên hoàn `Read -> Read` với 0 thinking token. Trong phiên làm việc mẫu tại V-Translate, model đã gọi 74 lần lệnh Read trên duy nhất file `app/main.py` qua lại giữa 2 đoạn code mà không có cảnh báo nào từ hook, buộc người dùng phải nhấn Interrupt.
- **Thiếu phản tư:** Chưa có quy chuẩn bắt buộc tư duy phản tư (Reflective Thought) giữa các lần gọi công cụ trong Soul và tài liệu quick-lane.

## 2. Sau request (trạng thái/flow)
- **Thuật toán Range Overlap (≥ 70%):** `read_gate.py` tính toán mức độ chồng lấn giữa dải dòng mới và các dải dòng đã đọc trước đó trong session.
  - Đọc file dài hợp lệ: Đọc các đoạn khác nhau (overlap < 30%) được phép hoàn toàn và im lặng tuyệt đối.
  - Bẫy lặp 1 đoạn: Khi một đoạn bị đọc lặp lại ≥ 2 lần (overlap ≥ 70%), hook phát sinh cảnh báo `[TDQ:DOC]` nhắc nhở AI rằng nội dung đã có trong ngữ cảnh và yêu cầu dừng đọc để tổng hợp viết giải pháp.
- **Củng cố quy chuẩn Soul & Quick Lane:** Bổ sung điều khoản "Reflective Thought & Hypothesis" vào Clean Code Invariants của Soul: bắt buộc nêu giả thuyết trước khi đọc mã, cấm xé vụn dải đọc (khuyến khích đọc dải rộng 100–300 dòng), và cấm đánh đổi chất lượng lấy tốc độ.

## 3. Đã test gì
- **Q1:** Đọc nhiều đoạn khác nhau trong file dài (offset=200/limit=40 và offset=500/limit=50) -> kiểm chứng hook im lặng hoàn toàn, không cảnh báo nhầm.
- **Q2:** Đọc lặp lại cùng một đoạn có overlap ≥ 70% từ lần 2 trở lên -> kiểm chứng hook kích hoạt nhắc nhở `[TDQ:DOC]`.
- **Q3:** Đọc toàn bộ file lần 2 khi file không đổi -> kiểm chứng hook kích hoạt nhắc nhở như cũ.
- **Q4:** Kiểm tra hook chạy nhẹ, không spawn tiến trình con (thời gian chạy < 5ms).
- **Q5:** Kiểm tra doc_lint trên spec, soul.md và quick-lane.md.
- **Đánh giá độc lập:** Chạy subagent `tdq-qc-tester` độc lập kiểm chứng toàn bộ DoD và test suite.

## 4. Kết quả test
- **Toàn bộ 19 test trong `tests/test_read_gate.py` PASS 100%:**
  - `test_im_vung_khac_thi_khong_nhac`: PASS (0.21s).
  - `test_nhac_khi_lap_doan_offset_limit`: PASS (0.27s).
  - `test_thong_diep_remind_ai`: PASS (0.28s).
  - `test_nhac_lan_doc_thu_hai_cua_file_khong_doi`: PASS (0.21s).
  - `test_nhe_khong_spawn_tien_trinh_con`: PASS (0.09s).
- **Doc Lint:** Spec, soul.md, quick-lane.md đều đạt 0 lỗi lint (mã thoát 0).
- **Agent tdq-qc-tester:** Đánh giá độc lập đạt `VERDICT: PASS everything` với 0 khuyết tật.

## Thời gian

Request `2026-11-10-2335-nang-cap-tu-duy-tdq-workflow` · lane full · opened at 2026-11-10T23:42:03+07:00

| Phase | Wall clock | API request | Tool wait | Background job | Observed union | Unattributed | Times entered |
|---|---|---|---|---|---|---|---|
| idle | 10s | 8s [partial] | 2s [partial] | — [unavailable] | 10s [partial] | 0s [partial] | 1 |
| analyze | 13 min | 2 min [partial] | 7s [partial] | — [unavailable] | 2 min [partial] | 11 min [partial] | 1 |
| spec | 5 min | 4 min [partial] | 41s [partial] | — [unavailable] | 4 min [partial] | 35s [partial] | 1 |
| plan | 11 min | 4 min [partial] | 20s [partial] | — [unavailable] | 4 min [partial] | 7 min [partial] | 1 |
| implement | 11 min | 9 min [partial] | 2 min [partial] | — [unavailable] | 11 min [partial] | 2s [partial] | 1 |
| qc | 9 min | 6 min [partial] | 7 min [partial] | — [unavailable] | 9 min [partial] | 1s [partial] | 1 |
| report | 27s | 19s [partial] | 8s [partial] | — [unavailable] | 26s [partial] | 0s [partial] | 1 |
| Total | 50 min | 24 min [partial] | 10 min [partial] | — [unavailable] | 31 min [partial] | 19 min [partial] |  |

Model compute time is unavailable (`model_giay=null`). API includes network/provider latency; tool time is host wait. Observed metrics may overlap; unattributed time is not assumed user/model time.
<!-- tdq-archify-binding:start -->
<!-- manifest: 2026-11-10-2335-nang-cap-tu-duy-tdq-workflow.manifest.json -->
<!-- manifest_digest: d25772c8dcef8eade698783921a43b7626ce2115c4571152775a227e72a27892 -->
<!-- tdq-archify-binding:end -->