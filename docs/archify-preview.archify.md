# TDQ × Archify: hiểu luồng trước khi code {#tdq-archify}

Một trang tổng quan cho dự án, một bản BA riêng cho từng request. **Thiết kế đã chốt; tích hợp chưa được nghiệm thu đầy đủ.**

- Graphify cung cấp dữ liệu quan hệ; Archify trình bày sơ đồ để dev khám phá.
- Bản BA mô tả thay đổi dự kiến, không được coi là hiện trạng đã triển khai.
- HTML là ảnh chụp tại lúc sinh; muốn cập nhật phải chạy lại quy trình dựng.
- Unit test adapter đã xanh, nhưng kiểm thử toàn bộ và vùng chạm đã báo lỗi.

@answer scope="Thiết kế và tiến độ · 24/10/2026 · chưa nghiệm thu"
@meta locale=en style=editorial

## Hai tầng giúp dev đọc từ tổng thể đến chi tiết {#two-levels}

@architecture id=architecture-view title="Mô hình đích: tổng quan và BA theo request"
| evidence | Mã nguồn | database |
| analysis | Phân tích | backend |
| master | Bản đồ dự án | frontend |
| request | Yêu cầu mới | external |
| design | Thiết kế BA | backend |
| task | Preview task | frontend |
| evidence > analysis | khảo sát |
| analysis > master | hiện trạng |
| request > design | nghiệp vụ |
| master > design | bối cảnh |
| design > task | dự kiến | emphasis |

| Góc nhìn | Dành cho | Nội dung | Cập nhật |
| --- | --- | --- | --- |
| Master Map | Dev mới, người rà kiến trúc | Module, trách nhiệm, ranh giới, quan hệ chính | Dự kiến dựng lại từ nguồn đã kiểm chứng sau merge hoặc khi quét |
| Task BA | Dev nhận task, người duyệt | Mục tiêu, luồng chính, ngoại lệ, thay đổi trước và sau | Khi sửa thiết kế của request; lưu phiên bản đã duyệt |

Đích dự kiến: `docs/architecture/index.html` cho toàn dự án và `docs/tdq/spec/<slug>-preview.html` cho từng request chuyên sâu. Không nhồi mọi hàm vào một sơ đồ duy nhất.

## BA xuất hiện trước cổng duyệt ở cả hai pipeline {#pipelines}

@workflow id=ba-flow title="Luồng đích: từ yêu cầu đến kiểm chứng"
| ask | Nhận yêu cầu | external |
| study | Khảo sát | backend |
| ba | Dựng BA | backend |
| approve | Duyệt thiết kế | security |
| code | Viết code | backend |
| verify | Kiểm chứng | security |
| ask > study | |
| study > ba | |
| ba > approve | preview |
| approve > code | đã duyệt | emphasis |
| code > verify | |

| Pipeline | Khi nào có preview? | Độ chi tiết | Cổng duyệt giữ nguyên |
| --- | --- | --- | --- |
| Full | Trong bước spec khi môi trường sẵn sàng | Kiến trúc, flow nghiệp vụ, ngoại lệ và thay đổi | Duyệt spec, rồi duyệt plan |
| Quick | Task chạm từ hai module hoặc refactor | Workflow gọn, ưu tiên luồng cần sửa | Một cổng duyệt mini-plan |
| Việc nhỏ | Không ép tạo HTML | Text hoặc Mermaid đủ rõ | Không thêm cổng chỉ để duyệt hình |

Một bản BA chỉ rõ người khởi tạo, đầu vào và quy tắc quyết định nhánh. Nó mô tả thành phần xử lý, đầu ra và lỗi. Hình đẹp không thay thế tiêu chí nghiệm thu.

## Thành phần nào đã có, phần nào chưa được chứng minh? {#delivery-status}

| Thành phần | Bằng chứng hiện có | Giới hạn cần biết |
| --- | --- | --- |
| Blueprint | `docs/kien-truc-tich-hop-archify.md` đã tạo, doc_lint đạt | Tài liệu thiết kế không chứng minh runtime hoạt động |
| Adapter | `scripts/tdq_archify.py`: check, render, open, bridge, sync-master | Check môi trường không tương đương render thành công |
| Graphify bridge | Chuyển nodes và links sang JSON, tự kiểm BRIDGE OK | Mặc định chọn tối đa 25 nút; không phải bản đồ đầy đủ toàn repo |
| Master sync | Hàm sync_master ghi master.architecture.json | Hiện chưa tự render index.html; chưa có bằng chứng đồng bộ tự động sau merge |
| Skills | Đã bổ sung chỉ dẫn preview trong spec, quick và plan | Cú pháp render trong chỉ dẫn cần đối soát với CLI dùng cờ |
| Endpoint AI | Đã khai báo biến trong .env.example | Chưa có bằng chứng scanner gọi endpoint; khai báo biến không tạo ra năng lực này |

@callout level=warning title="Đính chính kết luận nghiệm thu trước đó"
| Không thể giữ kết luận QC ultra PASS toàn bộ. Hai lệnh nền kiểm thử toàn bộ và vùng chạm đã kết thúc với mã lỗi 1. |
| Lần chạy riêng ba module adapter, setup và doc_lint đạt 143 tests. Kết quả này không thay thế toàn bộ suite. |

## Graphify, agent và Archify chia việc như thế nào? {#responsibilities}

| Thành phần | Trách nhiệm | Không được suy diễn |
| --- | --- | --- |
| Graphify cùng LSP và đọc code | Thu thập quan hệ và vị trí nguồn | Đồ thị cũ hoặc cạnh thiếu hướng không chứng minh luồng runtime |
| Agent đang làm việc | Hiểu nghiệp vụ, chọn mức trừu tượng, viết candidate | Quan hệ suy đoán phải được ghi rõ, không giả thành bằng chứng |
| Archify CLI | Kiểm schema, dựng sơ đồ, xuất HTML tương tác | Không tự thực thi nghiệp vụ; chuyển động trên sơ đồ không phải trace thật |
| TDQ adapter | Điều phối CLI và quản lý đầu vào, đầu ra | Thành công một bước không được coi là toàn bộ finalize đã đạt |
| Endpoint ngoài | Hướng mở rộng đã chọn cho phân tích độc lập | Cần triển khai client, quyền gửi dữ liệu và ngân sách trước khi vận hành |

Mặc định, agent hiện tại viết candidate và Node.js dựng HTML. Việc này vẫn dùng context của phiên agent, không phải AI miễn phí. Endpoint riêng là lựa chọn mở rộng, không phải điều kiện để tạo trang này.

## Điều kiện để gọi bản đồ là hiện trạng đáng tin {#next-checks}

- [ ] Gắn bản đồ với revision hoặc fingerprint của nguồn đã đọc.
- [ ] Tách phần đã triển khai khỏi phần dự kiến và phần chưa rõ.
- [ ] Ghi phạm vi bị lọc khi giới hạn node; không gọi lát cắt là toàn repo.
- [ ] Render candidate bằng Archify thật và kiểm tra HTML trong trình duyệt.
- [ ] Xác minh lỗi finalize không bị báo thành công, cùng cách mở file an toàn.
- [ ] Kiểm chứng luồng dựng Master HTML và cập nhật sau thay đổi mã nguồn.
- [ ] Xác định lỗi của các suite nền, sửa và chạy lại trước khi nghiệm thu.

Trang này là bản tổng hợp để duyệt cách tổ chức và hiểu tiến độ. Nó không phải bản đồ trực tiếp của toàn bộ codebase, cũng không tự cập nhật khi file nguồn thay đổi.
