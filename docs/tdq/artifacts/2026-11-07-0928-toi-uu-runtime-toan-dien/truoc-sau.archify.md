# Trước/Sau — Tối ưu runtime TDQ Workflow {#tong-quan}

@meta locale=vi

Bản thiết kế planned: giữ search, approval và QC; chỉ promote từng tối ưu sau phép đo tương đương. Đầu vào: source 0.94.0, receipt và benchmark cùng fingerprint. Đầu ra: runtime có fallback, evidence và report.

## Trước: đường nóng {#truoc}

@workflow id=runtime-truoc title="Trước: thao tác đồng bộ và đo chưa đủ"
| start | SessionStart và LSP readiness | backend |
| change | Sửa mã trong request | backend |
| finish | tdq_finish rebuild Graphify | backend |
| test | Full fresh cuối, nguy cơ vô hiệu khi source đổi | security |
| end | Report chưa có cohort đủ | backend |
| start > change |
| change > finish |
| finish > test |
| test > end |

## Sau: đo, kiểm, rồi bật {#sau}

@workflow id=runtime-sau title="Sau: baseline → thí điểm → parity → promote hoặc rollback"
| baseline | Đo critical path theo cohort | backend |
| pilot | LSP, Graphify, test, hook thí điểm | backend |
| guard | QC + parity + freshness | security |
| enable | Promote từng phần đạt ngưỡng | frontend |
| fallback | Không đạt: giữ đường cũ | security |
| baseline > pilot |
| pilot > guard |
| guard > enable |
| guard > fallback |

Trigger là request/turn có thay đổi code hoặc hook khởi động. Lỗi timeout, metadata sai, graph stale, receipt invalid hoặc benchmark lệch parity phải trở về đường cũ; không gán unknown timing cho model/người dùng. `workers=2` và cache chỉ đủ điều kiện mới opt-in. Nguồn hiện trạng: `scripts/tdq_finish.py:198-207,300-323`, `hooks/scripts/session_start.py:154-186,208-272`, `skills/tdq-build/references/runtime-speed.md:27-68`. Không phải bằng chứng tốc độ sau triển khai.
