# Phối hợp công cụ {#tong-quan}

@meta locale=en

Thiết kế đề xuất: agent tự lập bước và phối hợp đúng công cụ để hoàn tất task; setup ghim luật vào Claude Code user-level, giữ dữ liệu riêng và quyền hiện có. Công cụ thiếu chỉ được research rồi đề xuất cài user-level, chờ người dùng duyệt.

## Thực thi hiện tại {#task-truoc}

@workflow id=task-truoc-flow title="Trước: routing rời rạc"
| user | User giao task | external |
| pick | Tra bảng plugin | backend |
| tool | Dùng tool đã chọn | cloud |
| block | Lỗi hoặc thiếu tool | security |
| result | Kết quả từng thao tác | database |
| user > pick | mục tiêu |
| pick > tool | lựa chọn tĩnh |
| tool > block | gián đoạn |
| tool > result | chưa contract chung |

Nguồn: `plugin-routing.md` và `mcp-first-guide.md`. Đã có MCP-first, chưa có vòng handoff và kiểm kết quả cuối thống nhất.

## Thực thi đề xuất {#task-sau}

@workflow id=task-sau-flow title="Sau: lập bước, phối hợp, kiểm chứng"
| user | Task và phạm vi quyền | external |
| plan | Lập bước nội bộ | backend |
| probe | Inventory và pre-flight | security |
| web | Chrome MCP cho web | cloud |
| native | Desktop cho dialog native | backend |
| verify | Kiểm trạng thái và file đích | database |
| missing | Research và đề xuất cài | external |
| done | Hoàn tất có bằng chứng | backend |
| user > plan | input và output |
| plan > probe | chọn đường ngắn đúng |
| probe > web | tool có sẵn |
| probe > missing | thiếu tool |
| web > native | bước tùy chọn khi cần native |
| native > verify | quay lại browser đối chiếu |
| verify > done | đủ điều kiện |

Không ép nhiều tool; upload_file trực tiếp được thì bỏ file picker. Không retry gửi/upload chưa rõ đã xảy ra. Không tự sửa quyền để vượt chặn.

## Setup hiện tại {#setup-truoc}

@workflow id=setup-truoc-flow title="Trước: ghi trực tiếp và stamp có thể lệch"
| entry | CLI hoặc SessionStart | external |
| render | Sinh khối TDQ:TOOLS | backend |
| write | Ghi CLAUDE.md trực tiếp | database |
| stamp | Ghi stamp phiên bản | backend |
| entry > render | setup/update |
| render > write | thay khối |
| write > stamp | lỗi có thể bị bắt và bỏ qua |

Nguồn: `tdq_setup.py` writer và setup bù. Thiếu backup/atomic write; marker lỗi chưa fail-closed.

## Setup đề xuất {#setup-sau}

@workflow id=setup-sau-flow title="Sau: giữ nội dung riêng, ghi và kiểm an toàn"
| entry | CLI hoặc SessionStart | external |
| validate | Đọc UTF-8 và kiểm marker | security |
| compare | So khối instruction | backend |
| backup | Backup bản gốc | database |
| write | File tạm rồi replace | backend |
| verify | Đọc lại xác minh | security |
| stamp | Stamp thành công | backend |
| failure | Giữ gốc, báo lỗi, retry lần sau | external |
| entry > validate | chỉ Claude user-level |
| validate > compare | hợp lệ |
| compare > backup | cần cập nhật |
| backup > write | backup thành công |
| write > verify | thay nguyên tử |
| verify > stamp | nội dung đúng |
| verify > failure | xác minh trượt |

Không đổi nội dung thì no-op, không ghi hay backup. Lỗi ở bất kỳ bước nào giữ nguyên bản gốc và không tiến stamp; đường lỗi ở view thể hiện bằng nhánh xác minh. Bảo toàn phần user ngoài managed block; không sửa host khác, không thêm state/hook/planner engine. QC ultra kiểm fixture trước áp dụng máy thật.
