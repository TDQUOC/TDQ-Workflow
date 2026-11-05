# Trước/Sau — Chọn test TDQ theo tính năng và chứng cứ {#tong-quan}

@meta locale=vi

Thiết kế planned: chọn ít scenario cần thiết nhưng vẫn giữ một lượt full regression fresh ở cổng QC cuối. Bộ smoke chạy theo tính năng và rủi ro, không thay toàn suite. Số case nhỏ không tự chứng minh chất lượng.

## Luồng test trước và sau {#luong-test}

@workflow id=truoc-test title="Trước: test theo mức tối thiểu cố định"
| thay-doi | Sửa feature hoặc luật TDQ | backend |
| bo-case | Áp sẵn 1 happy + 2 boundary + 1 failure | backend |
| vung-cham | Chạy vùng chạm, fallback nếu không rõ | backend |
| qc-full | QC full/ultra chạy toàn suite | security |
| thay-doi > bo-case | có thể thêm ca không gắn rủi ro |
| bo-case > vung-cham | module chọn có thể rất rộng |
| vung-cham > qc-full | lặp lượt nếu không lập lịch trước |

@workflow id=sau-test title="Sau: rủi ro dẫn hướng case và lượt chạy"
| chon | Feature và rủi ro thật | backend |
| fixture | Scenario với dữ liệu mô phỏng | backend |
| chay | Smoke và vùng chạm theo kế hoạch | frontend |
| full | Full fresh khi nguồn ổn định | security |
| chon > fixture |
| fixture > chay |
| chay > full |

Hiện trạng có nguồn: `scripts/tdq_test.py:424-462` xác định bán kính, `scripts/tdq_test.py:729-748` fallback; `skills/tdq-build/references/vision-test-loop.md:40-47` quy định số scenario tối thiểu, `skills/tdq-build/references/qc.md:34-38,97-103` giữ full regression. Thiết kế sau là đề xuất, không phải kết quả runtime.

## Ngân sách & nghĩa của bằng chứng {#bang-chung}

| Điều | Hiện tại | Đề xuất |
|---|---|---|
| Số case | Receipt lịch sử 4.161 nodeid / 193 module | Không đặt hard-cap toàn repo; đo giá trị theo feature/risk |
| Smoke | Chưa có baseline tổng thời gian | Full khuyến nghị 5 phút; ultra khuyến nghị 10 phút, có lý do để nới |
| Full QC | `tron-bo` collect + execute | Vẫn một lượt fresh ở QC cuối, không dùng receipt cũ thay verdict |
| Simulation | Fixture tạm trong test liên quan | Dữ liệu cô lập, test CLI/hook thật và lỗi phục hồi |

Trượt mục tiêu smoke không được biến thành PASS bằng cách bỏ case quan trọng. CI vẫn giữ `unittest discover tests` trên ma trận hệ điều hành và Python, không nằm trong request này.
