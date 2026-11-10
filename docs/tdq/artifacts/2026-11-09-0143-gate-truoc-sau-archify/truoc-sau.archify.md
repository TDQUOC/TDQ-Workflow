# Trước/Sau — Gate cứng cho sơ đồ Archify ở spec và report {#tong-quan}

@meta locale=vi

Play3clone: 6 spec + 11 report đến 2026-11-07 đủ sơ đồ Trước/Sau; 6 spec + 18 report từ 2026-11-08 mất hết vì luật chỉ nằm trong skill, CLI không kiểm. Bản thiết kế đưa kiểm manifest Archify vào chính lệnh `approve` và `set phase=idle`.

## Trước: luật chỉ là chữ {#truoc}

@workflow id=luong-truoc title="Trước: agent bỏ skill vẫn qua cổng"
| spec | Agent viết spec, không render Archify | backend |
| approve | approve spec: chỉ kiểm R14 | security |
| build | Build + report chữ, HTML tự viết | backend |
| idle | set phase=idle: không kiểm report | security |
| spec > approve |
| approve > build |
| build > idle |

## Sau: CLI đòi manifest current {#sau}

@workflow id=luong-sau title="Sau: thiếu sơ đồ thì không qua cổng"
| spec | Agent viết spec + render preview Archify | backend |
| approve | approve spec/quick: R14 + preview manifest current | security |
| build | Build + report 4 mục + render report Archify | backend |
| idle | set phase=idle: 4 mục + report manifest current | security |
| spec > approve |
| approve > build |
| build > idle |

Máy thiếu Node: `approve … --bo-qua-archify "<lý do>"` ghi `archify_bo_qua`; gate idle bỏ phần manifest nhưng vẫn đòi 4 mục. Request mở trước mốc `2026-11-09-0143` không bị gate. Nguồn: `scripts/tdq_state.py` (`_cli_approve`, `_r14_gate`, nhánh `set`), `scripts/tdq_archify.py` (`verify_document_and_manifest`).
