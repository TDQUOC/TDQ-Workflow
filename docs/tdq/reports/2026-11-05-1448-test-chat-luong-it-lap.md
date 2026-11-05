# Báo cáo — Test ít hơn khi hợp lý, không bỏ sót lỗi quan trọng

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

**Tóm tắt:** Cách *chọn và viết* test đã đổi. Toàn bộ test trên mã mới chạy xanh. Bạn đã duyệt ba lệch và miễn bước đánh giá hiệu quả cho request này; kết quả đánh giá vẫn ghi **INCONCLUSIVE** (0 lượt chạy thực). Trạng thái Git ghi tại lúc lập báo cáo; kiểm lịch sử commit để biết mới nhất.

## 1. Trước request: test được tạo và chạy ra sao?

Mỗi tính năng bị yêu cầu ít nhất **1 ca thường + 2 ca biên + 1 ca lỗi**, kể cả khi vài ca không bảo vệ rủi ro thực. Khi chạy, công cụ mới chọn test liên quan; bạn chưa xem được danh sách sẽ chạy từ trước. Số **4.161** trong kết quả lịch sử là số test riêng lẻ, không phải số tính năng hay bằng chứng test nào cũng cần thiết.

## 2. Sau request: thay đổi gì?

- **Viết test:** Chỉ thêm ca có hành vi/rủi ro và kết quả kiểm tra rõ ràng; dùng dữ liệu giả trong thư mục tạm. Không thêm ca chỉ để đủ chỉ tiêu; vẫn giữ ca lỗi, bảo mật và mất dữ liệu khi có rủi ro.
- **Chọn test:** `vung-cham --plan-only` cho xem trước phạm vi, danh sách module, số lượng và lý do **mà không chạy test hoặc ghi kết quả test**. Không xác định chắc test liên quan thì chọn rộng hơn, có thể chạy toàn bộ.
- **Giữ an toàn:** Không xóa test cũ vì chưa chứng minh ca nào thừa. Không đổi CI. Cuối đợt vẫn chạy lại toàn bộ test trên mã hiện tại.

**Điều này chưa chứng minh số test toàn repo đã giảm.** Đã đổi luật tránh sinh ca vô ích và thêm bước xem trước; sẽ chỉ xóa/gộp ca cũ khi có bằng chứng chúng trùng nhau.

## 3. Đã test gì?

| Phép kiểm | Mục đích | Kết quả |
|---|---|---|
| Dữ liệu TDQ giả lập | Xem trước khi file đổi, không có file đổi, thiếu liên kết test; kiểm thư mục test lồng nhau | 2 ca kiểm nhanh đạt trong 0,72 giây |
| Bộ kiểm quy tắc và báo cáo | Giữ đường chạy cũ, kết quả và chứng cứ | 41 ca đạt, 27 kiểm tra con đạt trong 9,13 giây |
| Toàn bộ repo, chạy mới | Phát hiện lỗi hồi quy ngoài vùng vừa sửa | 4.162 đạt, 7 bỏ qua theo cấu hình; không còn ca lỗi |

## 4. Kết quả và việc còn mở

**Test toàn repo: ĐẠT.** Lượt chạy cuối có **4.169 mã ca test**: 4.162 đạt + 7 bỏ qua; **2.724 kiểm tra con** nằm trong các ca trên, không cộng thêm vào 4.169. Chạy mới, không dùng kết quả cũ; kết quả gắn với cùng mã nguồn trước/sau và đủ danh sách ca. Mất **857,25 giây (~14 phút 17 giây)** — đây là *toàn bộ bộ test*, không phải thời gian smoke. [Chi tiết QC](../qc/2026-11-05-1448-test-chat-luong-it-lap.md) · [Bản HTML trực quan](2026-11-05-1448-test-chat-luong-it-lap.html).

**Yêu cầu tổng thể: HOÀN TẤT, kèm ba lệch đã được bạn duyệt (2026-11-05) và eval được miễn.** Hiệu quả quy tắc mới trên model vẫn **INCONCLUSIVE**. Ba điểm:

1. **Đánh giá hiệu quả quy tắc mới:** Kế hoạch đánh giá hợp lệ, nhưng môi trường chạy thử chưa cô lập và chưa có bộ chấm kết quả. **0 lượt đánh giá thực tế**; chưa thể nói quy tắc mới làm AI chọn test tốt hơn. Bạn đã miễn cổng này cho request; kết quả vẫn INCONCLUSIVE. Đây là lệch **#1/Q6** (đã duyệt).
2. **Chạy toàn bộ nhiều hơn dự kiến:** **5 lượt có kết quả so với ngân sách 3**; các lượt trước gặp lỗi cần sửa, một lượt test xanh nhưng chứng cứ mất hiệu lực vì sơ đồ kiến trúc được cập nhật cùng lúc. Chỉ lượt cuối được tính đạt. Đây là lệch **#2/Q3** (đã duyệt).
3. **Mốc tốc độ smoke:** Hai ca xem trước mất 0,72 giây, **không đại diện** cho smoke đầy đủ ở mức full/ultra. Vì chưa đo tổng thời gian tương ứng, chưa kết luận đạt mốc khuyến nghị 5/10 phút. Giữ giới hạn 120 giây cho từng phép kiểm. Đây là lệch **#3/Q5** (đã duyệt; đo smoke đại diện để request sau).

**Lưu ý:** Báo cáo bỏ sót cho biết `bo_sot=0`, nhưng phép đo bán kính chưa đầy đủ (`radius_complete=false`); không hiểu số 0 là chứng nhận không bỏ sót test. Bản xem trước thiết kế đã cũ sau khi sửa mã; HTML đính kèm dùng nguồn đang làm việc, đã xác minh. Kiểm tra trình duyệt gốc có fallback Windows, không gọi đó là PASS trình duyệt native.

**Bằng chứng kỹ thuật:** [Receipt đầy đủ của lượt chạy cuối](../cache/test-runs/50bfcfb1b6d39502/340a3e2fad5044f8b116c074e7813579/result.json), SHA256 `71dd2a235402dbff0236922e540611e45d4e45e0ea8de41cd030b8aae1df8e44`. Log gốc `docs/tdq/artifacts/2026-11-05-1448-test-chat-luong-it-lap/qc-full-stable.log` bị Git ignore, vẫn còn trên máy. Ba lệch và miễn eval do bạn duyệt ngày 2026-11-05.

**Git:** Commit `054266b0` trên nhánh request; theo yêu cầu của bạn, merge vào `dev` rồi cập nhật `main` (chưa push).

**Archify HTML:** [Mở báo cáo trực quan](2026-11-05-1448-test-chat-luong-it-lap.html).

<!-- Báo cáo dưới đây giữ nguyên số liệu thô do tdq_timing.py show đo, có nhiều trường partial/unavailable. -->

## Thời gian

Request `2026-11-05-1448-test-chat-luong-it-lap` · lane full · opened at 2026-11-05T14:53:38+07:00

| Phase | Wall clock | API request | Tool wait | Background job | Observed union | Unattributed | Times entered |
|---|---|---|---|---|---|---|---|
| idle | 0s | — [partial] | — [partial] | — [unavailable] | — [partial] | — [partial] | 1 |
| analyze | 59 min | 14 min [partial] | 2 min [partial] | — [unavailable] | 14 min [partial] | 45 min [partial] | 1 |
| spec | 8 min | 7 min [partial] | 22s [partial] | — [unavailable] | 7 min [partial] | 1 min [partial] | 1 |
| plan | 1h 27min | 41 min [partial] | 9 min [partial] | — [unavailable] | 49 min [partial] | 39 min [partial] | 1 |
| qc | 1h 09min | 1h 02min [partial] | 6 min [partial] | — [unavailable] | 1h 08min [partial] | 1 min [partial] | 1 |
| Total | 3h 43min | 2h 03min [partial] | 18 min [partial] | — [unavailable] | 2h 17min [partial] | 1h 25min [partial] |  |

Model compute time is unavailable (`model_giay=null`). API includes network/provider latency; tool time is host wait. Observed metrics may overlap; unattributed time is not assumed user/model time.
Transcript attribution: project_window. Complete covers selected supported observations only.
- api_request_seconds: missing_pairs,unknown_events,unreadable_or_uncertain_source,unsupported_source_schema
- tool_call_seconds: conflicts,missing_pairs,unknown_events,unreadable_or_uncertain_source
- background_job_seconds: schema_has_no_confirmed_lifecycle
- observed_union_seconds: conflicts,missing_pairs,unknown_events,unreadable_or_uncertain_source;missing_pairs,unknown_events,unreadable_or_uncertain_source,unsupported_source_schema
- unattributed_seconds: wall_minus_observed_union;conflicts,missing_pairs,unknown_events,unreadable_or_uncertain_source;missing_pairs,unknown_events,unreadable_or_uncertain_source,unsupported_source_schema

## Thân PR (soạn sẵn)

**Tóm tắt:** Chọn test theo feature/rủi ro, thêm `--plan-only` và giữ full fresh cuối. Không thay CI hoặc xóa case thiếu bằng chứng.
**Trước/Sau:** Preview planned `../spec/2026-11-05-1448-test-chat-luong-it-lap-preview.html`; manifest source stale sau implement, không dùng làm bằng chứng nghiệm thu.
**Đã kiểm:** Full fresh 4.162 passed, 7 skipped; smoke 2 passed; runtime/report contract 41 passed.
**Rủi ro hồi quy:** Mapping thiếu fallback full; nested module được tính đúng mẫu số; Q3/Q5/Q6 lệch đã duyệt; eval INCONCLUSIVE.
<!-- tdq-archify-binding:start -->
<!-- manifest: 2026-11-05-1448-test-chat-luong-it-lap.manifest.json -->
<!-- manifest_digest: 6b9bf7b3f42bd0aae6fce7f8301bb15980ba9d50c8cb8a62bd625732df8fee1b -->
<!-- tdq-archify-binding:end -->