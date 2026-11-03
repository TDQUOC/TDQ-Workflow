# Nghiệm thu Phối hợp công cụ {#tong-quan}

@meta locale=vi

Kết quả thực tế cho request `2026-11-03-1420-phoi-hop-cong-cu` (lane full, mode subagent, 19/19 task). Luật tự chủ phối hợp công cụ đã vào soul/routing và vào managed instruction thật trên máy; writer instruction giữ nguyên dữ liệu riêng của người dùng. Bằng chứng cuối: 4.126 test passed, 12 skipped, 0 failures; apply user-level có backup `CLAUDE.md.bak.djwkvuw1`. Eval hành vi **không** được chứng nhận chất lượng — người dùng miễn (`WAIVED_USER`).

## Vòng làm việc của agent {#vong-lam-viec}

@workflow id=vong-lap title="Lập kế hoạch"
| goal | Mục tiêu, đích, quyền | backend |
| inventory | Công cụ có thật | database |
| steps | Bước nội bộ ngắn | backend |
| preflight | Kiểm kết nối | security |
| goal > inventory | phạm vi |
| inventory > steps | khả năng thật |
| steps > preflight | chốt tool |

@workflow id=vong-chay title="Thực thi và kiểm"
| preflight2 | Đã kiểm điểm cuối | security |
| execute | Một tool đủ thì thôi | backend |
| verify | Kiểm kết quả thật | security |
| handoff | Page/process/file mới | external |
| preflight2 > execute | chỉ gọi khi đã kiểm |
| execute > verify | mọi đường giao việc |
| verify > handoff | identity mới |

Ví dụ đã kiểm bằng fixture local: Chrome MCP mở trang, `upload_file` chọn tệp 96 byte, nhập prompt, tải về; file cuối đọc lại khớp SHA-256 `b95b954d…caf7f`. Nhánh native Save As bị `POLICY_DENIED` nên không bypass; ghi rõ là smoke khám phá, không phải timed PASS toàn chuỗi.

## Bảo toàn instruction người dùng {#writer}

@workflow id=writer-vao title="Đọc và dựng file tạm"
| doc | Đọc byte, chặn symlink | security |
| validate | Marker, UTF-8 strict | backend |
| stage | Tạm cùng thư mục, fsync | backend |
| readback | So byte và ACL | security |
| doc > validate | cấu trúc |
| validate > stage | không ghi đè lạ |
| stage > readback | so trước khi thay |

@workflow id=writer-ra title="Thay và khôi phục"
| readback2 | Đã so xong | security |
| replace | os.replace nguyên tử | backend |
| restore | Khôi phục backup | security |
| noop | Lượt hai không ghi | backend |
| readback2 > replace | cùng inode |
| replace > restore | chỉ khi lỗi |
| restore > noop | báo đường backup |

Ca kiểm: file mới, marker thiếu/đảo/lặp, UTF-8 hỏng, CRLF/BOM hỗn hợp, đổi ACL đồng thời, đọc lại lỗi. Lượt hai là no-op: không tạo backup, không ghi.

## ACL Windows — lỗi thật đã sửa {#acl}

@workflow id=acl-doc title="Đọc descriptor"
| raw | GetFileSecurityW | external |
| parse | Biên, SID, ACE | backend |
| semantic | owner/group/control | backend |
| raw > parse | descriptor lỗi phải ném |
| parse > semantic | dữ liệu hỏng bị từ chối |

@workflow id=acl-ghi title="Đặt và so lại"
| setcopy | Request bit trên bản copy | security |
| compare | Bỏ offsets, giữ nghĩa | backend |
| native | Readback control | external |
| setcopy > compare | chỉ đặt khi đọc được |
| compare > native | kiểm lại quyền |

Số đo native: `SetFileSecurityW` đưa control `0x8404` thành `0x8004` (mất `AUTO_INHERITED`); thêm request bit vào bản copy của lời gọi thì readback giữ `0x8404` với SID và thứ tự ACE nguyên. Fixture gồm DACL protected, DACL kế thừa unprotected và vòng lặp khác thư mục cha.

## Kết quả kiểm và giới hạn {#ket-qua}

@workflow id=ket-qua-flow title="Bằng chứng cuối"
| suite | 4.138 ca | backend |
| focused | 51 passed, 142 subtest | backend |
| policy | 109 passed, 28 subtest | backend |
| receipts | 11 passed, 2 subtest | security |
| suite > focused | sau ACL |
| focused > policy | fixture và hook |
| policy > receipts | apply thật |

Pyright hai file ACL: 0 errors, 0 warnings. Giới hạn phải nói rõ: eval chỉ chấm nội dung câu trả lời trên mẫu nhỏ, dùng nguồn trước lần sửa rollback/ACL cuối; không chứng minh thao tác browser/native, không đo tốc độ hay chi phí. Ruff chưa cài nên lint Python chưa chạy; thay bằng compileall, test và Pyright. Master kiến trúc chưa cập nhật theo diff này.
