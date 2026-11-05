# Nghiệm thu Chuẩn hóa Report Dễ hiểu kèm Archify HTML, Soul & User-Instruction (`2026-11-05-1140-report-de-hieu-soul-instruction`) {#tong-quan}

@meta locale=vi

Báo cáo thực tế cho request `2026-11-05-1140-report-de-hieu-soul-instruction` (lane `quick`, mức QC `ultra`, 3/3 task hoàn tất). Toàn bộ hệ thống báo cáo của TDQ-Workflow, luật gốc `soul.md` và khối hướng dẫn tự động ghim vào `~/.claude/CLAUDE.md` đã được đồng bộ theo chuẩn: **đơn giản, dễ hiểu, ngắn gọn nhưng trực quan và đầy đủ thông tin**.

## 1. Trước và Sau Request (Trạng thái & Luồng) {#truoc-sau}

@workflow id=truoc-request title="Trước Request (Trạng thái & Flow cũ)"
| reportcu | Report nén ký hiệu kỹ thuật | backend |
| soulcu | Soul chưa khóa luật trình bày dễ hiểu | security |
| setupcu | Khối TDQ:TOOLS thiếu chuẩn report 4 mục | database |
| nencu | Chạy nền --nen chưa ghim lại CLAUDE.md | backend |
| reportcu > soulcu | người đọc ngoài kỹ thuật khó nắm Trước/Sau |
| soulcu > setupcu | thiếu quy tắc trực quan, đầy đủ thông tin |
| setupcu > nencu | cài mới qua hook nền chưa tự điền instruction |

@workflow id=sau-request title="Sau Request (Trạng thái & Flow mới)"
| reportmoi | Report MD + Archify HTML dễ hiểu, trực quan | frontend |
| bonmuc | Bắt buộc: Trước -> Sau -> Đã test -> Kết quả | backend |
| soulmoi | Soul & Conventions khóa chuẩn trình bày | security |
| autopin | Setup, Update và --nen tự ghim CLAUDE.md | database |
| reportmoi > bonmuc | mọi người đọc đều hiểu rõ thay đổi và kết quả |
| bonmuc > soulmoi | áp dụng thống nhất cho chat và tài liệu |
| soulmoi > autopin | bảo toàn nguyên vẹn phần riêng của người dùng |

- **Trước request:** Khuôn `report-template.md` chỉ yêu cầu nén dòng bằng dấu `·`, chưa tách riêng 4 phần dễ hiểu cho mọi độc giả; `soul.md` chưa khóa chuẩn trình bày dễ hiểu + trực quan + đầy đủ thông tin; khối `KHOI_HUONG_DAN` chưa có mục chuẩn trình bày/report và nhánh chạy nền `khoi_tao_nen` (`--nen`) chưa gọi `ghim_huong_dan_tool`.
- **Sau request (Report & Archify HTML):** `skills/tdq-build/references/report-template.md`, `skills/tdq-build/references/archify-lifecycle.md`, `scripts/tdq_state.py` (`phases.md`) bắt buộc mọi report có cặp `docs/tdq/reports/<slug>.md` + `docs/tdq/reports/<slug>.html` trình bày rõ 4 phần: **(1) Trước request (trạng thái/flow)**, **(2) Sau request (trạng thái/flow)**, **(3) Đã test gì**, **(4) Kết quả test**.
- **Sau request (Soul & Conventions):** `skills/tdq-conventions/references/soul.md` và `skills/tdq-conventions/SKILL.md` khóa nguyên tắc luôn trình bày **đơn giản, dễ hiểu, ngắn gọn nhưng trực quan, đầy đủ thông tin**.
- **Sau request (Auto-pin User-Instruction):** `scripts/tdq_setup.py` (`KHOI_HUONG_DAN`, `khoi_tao_nen`) và `docs/claude-md-mau.md` bổ sung mục `## Chuẩn Trình bày & Báo cáo (Soul & Report)` và tự động ghim vào `~/.claude/CLAUDE.md` cả khi cài mới (`tdq_setup.py` trực tiếp hoặc `--nen`) lẫn khi update phiên bản (`tu_dong_cap_nhat_khi_doi_phien_ban`).

## 2. Đã Test Gì & Kết Quả Test Thực Tế {#kiem-thu}

@workflow id=luong-test title="Chuỗi Kiểm thử & Kết quả"
| t1 | Test khuôn Report + Archify HTML | backend |
| t2 | Test luật gốc Soul & Conventions | security |
| t3 | Test CLAUDE.md, Auto-Update & Token Budget | database |
| smoke | Smoke ghim thật CLAUDE.md + Master current | frontend |
| t1 > t2 | 4 passed trong test_report_visual.py |
| t2 > t3 | 6 passed, 7 subtests trong test_soul_rules.py |
| t3 > smoke | 61 passed, 142 subtests + master status=current |

- **Đã test T1:** Kiểm thử hợp đồng Report & Archify HTML (`tests/test_report_visual.py`).
- **Đã test T2:** Kiểm thử luật gốc Soul (< 150 dòng) và Conventions (`tests/test_soul_rules.py`).
- **Đã test T3:** Kiểm thử đồng bộ nguyên văn `KHOI_HUONG_DAN` với `docs/claude-md-mau.md`, tự động ghim khi chạy nền `--nen`/update version và trần token (`tests/test_claude_md_core.py`, `tests/test_auto_update_setup.py`, `tests/test_token_budget.py`, `tests/test_docs_consistency.py`, `tests/test_skill_shape.py`).
- **Đã test Smoke & QC Ultra:** Smoke test thực tế ghim vào file `~/.claude/CLAUDE.md` trên máy, đồng bộ lại `docs/architecture/index.html` (`tdq_archify.py status`) và chạy subagent QC độc lập (`tdq-qc-tester`).
- **Kết quả test tổng hợp:** Toàn bộ **94 passed, 170 subtests passed, 0 failed** trong `6.69s`; subagent QC độc lập (`ad05e87ce0f2a12e4`) xác nhận `VERDICT: PASS everything (71 passed, 149 subtests passed, 0 defects)`.
- **Kết quả Smoke & Master:** Smoke runtime `ghim_huong_dan_tool` PASS (`8.285 bytes`, bảo toàn nguyên vẹn phần riêng của user ngoài `<!-- TDQ:TOOLS -->`); Master architecture `docs/architecture/index.html`: `status="current"`, `reasons=[]`.
