# Báo cáo nghiệm thu — Gate cứng cho sơ đồ Archify ở spec và report {#tong-quan}

@meta locale=vi

Đã bổ sung gate cứng kiểm tra manifest Archify trong `approve spec`, `approve quick` và kiểm tra 4 phần báo cáo cùng manifest report trong `set phase=idle` tại `scripts/tdq_state.py`.

## Trước: luật chỉ là chữ, không có code chặn {#truoc}

@workflow id=luong-truoc title="Trước: agent bỏ skill vẫn qua cổng"
| spec | Agent viết spec, không render Archify | backend |
| approve | approve spec: chỉ kiểm R14 | security |
| build | Build + report chữ | backend |
| idle | set phase=idle: không kiểm report | security |
| spec > approve |
| approve > build |
| build > idle |

## Sau: CLI đòi manifest current và 4 mục report {#sau}

@workflow id=luong-sau title="Sau: thiếu sơ đồ hoặc thiếu mục thì bị chặn"
| spec | Agent viết spec + render preview Archify | backend |
| approve | approve spec/quick: R14 + preview manifest current | security |
| build | Build + report đủ 4 mục + render report Archify | backend |
| idle | set phase=idle: 4 mục + report manifest current | security |
| spec > approve |
| approve > build |
| build > idle |

Tất cả các cổng đều đã được kiểm chứng bằng 7 bài test chuyên biệt trong `tests/test_archify_gate.py` và 142 bài test liên đới toàn hệ thống.
