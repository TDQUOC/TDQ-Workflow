# Trước vs Sau — Chuẩn hóa Report dễ hiểu kèm Archify HTML, Soul & User-Instruction {#tong-quan}

@meta locale=vi

Bản thiết kế Trước/Sau cho request `2026-11-05-1140-report-de-hieu-soul-instruction` (lane `quick`). Chuẩn hóa phase `report` luôn đơn giản, dễ hiểu cho mọi người đọc nhưng trực quan và đầy đủ 4 phần (Trước request, Sau request, Đã test gì, Kết quả test), đồng thời đưa nguyên tắc trình bày ngắn gọn, dễ hiểu, trực quan, đầy đủ thông tin vào `soul.md` và tự động ghim vào `~/.claude/CLAUDE.md` khi cài mới hoặc update TDQ-Workflow.

## Luồng Trước và Sau khi Cập nhật {#truoc-sau}

@workflow id=truoc-cap-nhat title="Trước khi cập nhật (Hiện trạng)"
| report | Khuôn report nén ký hiệu kỹ thuật | backend |
| soul | Soul chưa khóa luật trình bày dễ hiểu | security |
| setup | Khối TDQ:TOOLS thiếu chuẩn trình bày/report | database |
| nen | Chạy nền --nen chưa ghim lại CLAUDE.md | backend |
| report > soul | người đọc ngoài kỹ thuật khó nắm Trước/Sau |
| soul > setup | thiếu quy tắc trực quan + đầy đủ thông tin |
| setup > nen | cài mới qua hook nền chưa tự điền instruction |

@workflow id=sau-cap-nhat title="Sau khi cập nhật (Planned)"
| report2 | Report MD + Archify HTML dễ hiểu, trực quan | frontend |
| bonmuc | Bắt buộc: Trước -> Sau -> Đã test -> Kết quả | backend |
| soul2 | Soul khóa chuẩn đơn giản, trực quan, đủ ý | security |
| autopin | Setup/Update/Nền tự ghim vào CLAUDE.md | database |
| report2 > bonmuc | ai đọc cũng hiểu trạng thái và bằng chứng |
| bonmuc > soul2 | áp dụng thống nhất cho chat và tài liệu |
| soul2 > autopin | giữ nguyên nội dung riêng ngoài TDQ:TOOLS |

Hiện trạng có chứng cứ trong mã nguồn:
- `skills/tdq-build/references/report-template.md:89` và `scripts/tdq_state.py:1290`: khuôn report hiện ưu tiên nén dòng bằng dấu `·`, chưa tách tường minh 4 mục dễ hiểu cho mọi độc giả (**Trước request trạng thái/flow thế nào**, **Sau request thế nào**, **Đã test gì**, **Kết quả test ra sao**).
- `skills/tdq-conventions/references/soul.md:21`: có 4 nguyên tắc gốc nhưng chưa khóa rõ chuẩn trình bày **đơn giản, dễ hiểu, ngắn gọn nhưng trực quan, đầy đủ thông tin**.
- `scripts/tdq_setup.py:993` (`KHOI_HUONG_DAN`) và `scripts/tdq_setup.py:1647` (`khoi_tao_nen`): khối ghim `<!-- TDQ:TOOLS -->` chưa có mục trình bày & report dễ hiểu, và nhánh chạy nền `--nen` khi mới cài chưa gọi `ghim_huong_dan_tool`.
