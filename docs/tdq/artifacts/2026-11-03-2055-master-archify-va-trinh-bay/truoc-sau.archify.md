# Master kiến trúc có luồng con {#tong-quan}

@meta locale=en

Thiết kế đề xuất: giữ master Archify ở một điểm vào. Thẻ cạnh sơ đồ tổng mở modal chứa sơ đồ con có nguồn. Mỗi lượt kết việc kiểm stale; master chỉ trở lại current sau khi dựng và verify. Sơ đồ sau là planned, không phải chứng nhận code chạy.

## Master hiện tại {#master-truoc}

@architecture id=truoc-portal title="Trước: index liên kết view rời"
| source | Source đổi | backend |
| finish | tdq_finish | backend |
| stale | status stale | security |
| portal | index tĩnh | frontend |
| views | Sáu HTML view rời | cloud |
| source > finish | kết turn |
| finish > stale | fingerprint lệch |
| portal > views | liên kết file |

Nguồn: `scripts/tdq_finish.py:210-259` chỉ mark stale; `scripts/tdq_archify.py:259-347` sinh index link tới view; master status hiện stale. Node trong native viewer chỉ focus/Passport.

## Master đề xuất {#master-sau}

@architecture id=sau-portal title="Sau: overview + thẻ flow mở detail"
| source2 | Source hiện tại | backend |
| check | Kiểm freshness | security |
| model | Model có chứng cứ | database |
| master | Master explainer | frontend |
| card | Thẻ flow cạnh overview | frontend |
| detail | Modal sơ đồ con | cloud |
| source2 > check | kết turn |
| check > model | stale, cần đọc source |
| model > master | sync + verify |
| master > card | flow có nguồn |
| card > detail | click/mở |

Thẻ link mở modal trong cùng HTML, không sửa handler của node native. Chi tiết chỉ có bước đã chứng minh từ code/test; còn thiếu ghi “chưa xác minh”.

## Cổng cập nhật {#cong-cap-nhat}

@workflow id=cong-flow title="Trước report hoặc merge"
| source3 | Code đổi | backend |
| status | Check master status | security |
| author | Agent cập nhật flow | backend |
| sync | Sync trong staging | cloud |
| verify | Verify manifest | security |
| current | Master current | frontend |
| fallback | Giữ last-good, báo stale | external |
| source3 > status | fingerprint |
| status > author | stale |
| author > sync | nguồn thật |
| sync > verify | render xong |
| verify > current | đạt |
| verify > fallback | lỗi |

Không refresh trong hook mỗi tool/SessionStart. Nếu engine lỗi, giữ bundle cũ; report nêu stale, không giả current.
