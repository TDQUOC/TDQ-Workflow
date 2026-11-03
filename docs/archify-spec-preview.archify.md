# Hiểu trước, duyệt trước, rồi mới code {#spec-ba}

**Agent hiện tại làm BA; Archify dựng sơ đồ.** Không cần endpoint riêng để thực hiện thiết kế này.

- Full xem HTML ở Spec, Quick xem flow ở mini-plan.
- Master phản ánh hiện trạng có bằng chứng; Task BA mô tả thay đổi dự kiến.
- Chỉ công bố artifact sau khi kiểm định đạt; lỗi phải hiện rõ.

@answer scope="Thiết kế đề xuất v1.0 · chờ duyệt · chưa triển khai"
@meta locale=en style=editorial

## Ai làm gì? {#roles}

@workflow id=authoring-flow title="Luồng BA trước khi viết code"
| ask | Yêu cầu | external |
| agent | Agent làm BA | backend |
| render | Archify dựng hình | backend |
| review | Dev duyệt | security |
| build | Code và QC | backend |
| ask > agent | |
| agent > render | candidate |
| render > review | HTML |
| review > build | đã duyệt | emphasis |

| Thành phần | Trách nhiệm |
| --- | --- |
| Agent đang có | Khảo sát bằng LSP, Graphify và code; viết nghiệp vụ, quy tắc, nhánh lỗi và candidate |
| Archify | Kiểm schema, dựng bố cục và giao HTML tương tác |
| TDQ | Kiểm receipt, quản lý snapshot, freshness và cổng duyệt |
| Endpoint ngoài | Chỉ xét nếu không dùng được agent hiện tại; không triển khai client riêng trong đợt này |

## Hai tầng tài liệu, không trộn ý tưởng với hiện trạng {#maps}

| Artifact | Trả lời | Thời điểm |
| --- | --- | --- |
| Task BA Full | Làm gì, vì sao, luồng nào, lỗi nào? | Spec trước duyệt; Plan liên kết lại |
| Task BA Quick | Task ảnh hưởng nhiều module hoặc refactor như thế nào? | Mini-plan trước một cổng duyệt |
| Master Map | Dự án hiện có những thành phần và quan hệ nào? | Dựng từ snapshot xác định; nguồn đổi thì stale |

Master có trang tổng quan và góc nhìn chi tiết. Không lấy 25 nút được chọn rồi gọi đó là toàn dự án. Inventory ghi phần đã khảo sát và phần chưa rõ.

## Khi mã nguồn đổi thì cập nhật ra sao? {#refresh}

@workflow id=refresh-flow title="Lifecycle cập nhật có kiểm chứng"
| source | Nguồn thay đổi | database |
| stale | Đánh dấu stale | security |
| update | Agent cập nhật | backend |
| check | Kiểm định | security |
| publish | Publish Master | frontend |
| source > stale | fingerprint |
| stale > update | đọc diff |
| update > check | candidate |
| check > publish | đạt | emphasis |

HTML là snapshot tĩnh. Thay đổi ngoài workflow được phát hiện ở lần kiểm tra tiếp theo, không có daemon theo dõi. Khi render lỗi, giữ bản tốt và báo lỗi; không lấy HTML cũ để báo thành công.

## Nghiệm thu bằng kết quả thật {#acceptance}

- [ ] Finalize lỗi không thể trả thành công.
- [ ] Sources đúng schema và đúng snapshot mã nguồn.
- [ ] Full và Quick có preview đúng lúc, không thêm cổng duyệt.
- [ ] Master HTML có coverage và phát hiện stale.
- [ ] Sửa nội dung sau duyệt phát hiện sai hash.
- [ ] Chạy bằng agent hiện tại, không cần API key ngoài.
- [ ] Kiểm tra HTML và tương tác qua trình duyệt thật.
- [ ] Phân loại lỗi nền, sửa hồi quy và có reviewer độc lập.

@callout level=warning title="Đây là bản thiết kế, không phải nghiệm thu"
| Request trước chưa đạt QC toàn bộ. Spec mới yêu cầu sửa và kiểm chứng các thiếu sót; không kế thừa kết luận PASS sai. |
