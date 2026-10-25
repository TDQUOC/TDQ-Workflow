# Sinh Master Map 4 góc nhìn và nâng cấp README chuẩn Flagship {#spec-ba}

**Xuất bản Portal kiến trúc tương tác 4 góc nhìn tại `docs/architecture/index.html` và tái thiết kế `README.md` chuyên nghiệp kèm cẩm nang Setup & Dependencies A–Z.**

- Nâng cấp `_generate_index_html` trong `scripts/tdq_archify.py` lên giao diện Dashboard hiện đại.
- Dựng 4 góc nhìn thực tế của `TDQ-Workflow`: `overview`, `pipeline-lifecycle`, `search-and-archify`, `hooks-and-gates`.
- Viết lại `README.md` chuẩn Flagship: 6 trụ cột bất biến, Setup 8 bậc (`tdq_setup.py`), cài đặt 4 host.

@answer scope="Thiết kế v1.0 · chờ duyệt · Mức QC full"
@meta locale=en style=editorial

## Luồng xuất bản Master Map & nâng cấp README {#flow}

@workflow id=mastermap-readme-flow title="Quy trình thực thi 3 bước"
| portal | 1. Nâng cấp Portal | backend |
| master | 2. Sinh 4 Views | backend |
| readme | 3. Nâng cấp README | frontend |
| verify | 4. Kiểm định & QC | security |
| portal > master | giao diện |
| master > readme | liên kết |
| readme > verify | 0 lỗi | emphasis |

| Đầu ra | Vị trí | Nội dung chính |
| --- | --- | --- |
| Portal Generator | `scripts/tdq_archify.py` | Giao diện Dashboard cho `index.html`, giữ nguyên hợp đồng kiểm thử |
| Master Map 4 Views | `docs/architecture/` | `index.html`, `overview.html`, `pipeline-lifecycle.html`, `search-and-archify.html`, `hooks-and-gates.html`, `manifest.json` |
| Flagship README | `README.md` | Tuyên ngôn giá trị, kiến trúc 6 trụ cột, Setup & Dependencies 8 bậc, 4 Host |
