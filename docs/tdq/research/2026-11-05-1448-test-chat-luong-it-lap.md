# Research — Test theo tính năng, chọn ít nhưng đủ chứng cứ
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## Câu hỏi và bằng chứng

| Câu hỏi | Nguồn | Kết luận có giới hạn |
|---|---|---|
| TDQ hiện chọn case như thế nào? | [`scripts/tdq_test.py:424`](../../../scripts/tdq_test.py), [`scripts/tdq_test.py:729`](../../../scripts/tdq_test.py), [`scripts/tdq_test.py:999`](../../../scripts/tdq_test.py) | Tìm từ file đổi, nội dung test, reverse import và quét thư mục; chọn module. `implement` chọn trực tiếp, QC có bán kính và fallback full. Pytest collect nodeid trước execute. |
| Vì sao vài nghìn? | Receipt `docs/tdq/artifacts/2026-11-03-2055-master-archify-va-trinh-bay/full-suite-result.json`, `tests/` | Receipt lịch sử ghi 4.161 nodeid duy nhất trong 193 module, 10 skipped; không phải 4.161 scenario nghiệp vụ. Một test có thể có subtest/parameterized case. Không lấy AST count làm số node thực. |
| Cần giữ bằng chứng gì? | [`scripts/tdq_test_manifest.py:45`](../../../scripts/tdq_test_manifest.py), [`scripts/tdq_test_manifest.py:161`](../../../scripts/tdq_test_manifest.py), [`scripts/tdq_test_receipt.py:27`](../../../scripts/tdq_test_receipt.py) | Manifest đối chiếu ID; thiếu/trùng/lệch là incomplete. Reuse mặc định off, policy khai dependency chưa có trong repo. Chạy lại chỉ khi evidence hợp lệ; không dùng cache xanh thay QC nếu luật còn yêu cầu fresh. |
| Những luật nào đang tốn test? | [`skills/tdq-build/references/vision-test-loop.md:38`](../../../skills/tdq-build/references/vision-test-loop.md), [`skills/tdq-build/references/qc.md:22`](../../../skills/tdq-build/references/qc.md), [`skills/tdq-build/references/runtime-speed.md:12`](../../../skills/tdq-build/references/runtime-speed.md) | Tối thiểu ba tier tình huống; deep full/ultra yêu cầu full QC; express chỉ task/DoD. Full hai cổng là chính sách, không phải chứng cứ đạt ngân sách. Smoke/runtime ultra 120 giây mỗi kiểm, không phải ngân sách cho cả smoke suite. |
| Có nên dùng marker và fixture? | [pytest markers](https://docs.pytest.org/en/stable/how-to/mark.html), [pytest cache](https://docs.pytest.org/en/stable/how-to/cache.html), [pytest fixtures](https://docs.pytest.org/en/stable/how-to/fixtures.html), [Test Pyramid](https://martinfowler.com/articles/practical-test-pyramid.html) | Marker chọn nhóm, factory fixture tạo dữ liệu mô phỏng cô lập. `--lf` chạy lỗi cũ, `--ff` ưu tiên lỗi cũ rồi chạy tất cả; không thay full. Pyramid ưu tiên nhiều unit nhanh và ít E2E nhưng chưa chứng minh hiệu quả trong TDQ. |
| CI chạy gì? | [`.github/workflows/test.yml:9`](../../../.github/workflows/test.yml) | 3 OS × 2 Python chạy `unittest discover tests` cho mỗi push/PR. Không đồng nhất với pytest runner; cần baseline/đối chiếu nếu thay CI. |

## Những gì chưa chứng minh

- Tỷ lệ test trùng/ít giá trị, số scenario nghiệp vụ độc lập, độ nhạy bắt lỗi của tập 100–200, độ flake và thời gian smoke: chưa có baseline tương đương.
- Root `pytest --collect-only -q` thấy 25 lỗi vì quét `docs/` backup; đó không phải phép thu thập hợp lệ của TDQ runner chọn `tests/`. Không xóa artifact trong pha phân tích.
- Không có login product trong repo TDQ; test simulation phải mô phỏng workflow thật (state, hook, test runner, Archify, setup), không dựng user/login giả để có số case.
