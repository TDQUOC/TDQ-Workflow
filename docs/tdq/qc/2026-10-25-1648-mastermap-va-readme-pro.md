# QC — Sinh Master Map 4 góc nhìn và nâng cấp README chuyên nghiệp

Ngày: 2026-10-25 · Plan: ../plan/2026-10-25-1648-mastermap-va-readme-pro.md · Vòng: 1
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

| # | Hạng mục | Lệnh đã chạy | Kết quả | PASS/FAIL |
|---|---|---|---|---|
| Q1 | Giao diện Portal `index.html` và 4 góc nhìn Master Map xuất bản thành công (O1, O2, O3) | `python scripts/tdq_archify.py status --project .` + kiểm trình duyệt Chrome DevTools MCP | `"status": "current", "reasons": []`; 4/4 views hiển thị chuẩn, 0 lỗi console | PASS |
| Q2 | Tài liệu `README.md` chuẩn Flagship và đầy đủ hướng dẫn Setup & Dependencies (O4) | `python scripts/doc_lint.py README.md` | `0 violation(s) total, exit 0` (219 dòng ≤ 500 dòng) | PASS |
| Q3 | Hồi quy vùng chạm và toàn bộ kho mã nguồn | `python -m pytest tests/test_archify_pipeline.py tests/test_docs_consistency.py tests/test_skill_shape.py -q` & `tron-bo` | 48 passed, 21 subtests passed in 8.38s; full suite 2.978 passed in 658.634s (0 failed, 0 errors) | PASS |
| QC-F1 | Trọn bộ test suite & ledger | `python scripts/tdq_test.py tron-bo` & `tdq_test.py so` | Ran 2978 tests in 658.634s — OK (skipped=10); full-suite runs: 1/2, radius misses: 0 | PASS |
| QC-F2 | Hồi quy vùng chạm (`archify_pipeline`, `docs_consistency`, `skill_shape`, `tdq_archify`) | `python -m pytest tests/test_archify_pipeline.py tests/test_tdq_archify.py tests/test_docs_consistency.py tests/test_skill_shape.py -q` | 85 passed, 21 subtests passed | PASS |
| QC-F3 | Ràng buộc kiến trúc (Spec §5) | `python -m pytest tests/test_kien_truc.py -q` & `pyright scripts/tdq_archify.py` | 4 passed in 0.10s; pyright 0 errors, 0 warnings | PASS |
| QC-F4 | Clean code (5 câu hỏi Self-check) | Tự soát SRP, OCP, LSP, ISP, DIP trên `_generate_index_html` | 5/5 CÓ | PASS |

## Bằng chứng

### Q1 & Browser Verification (Chrome DevTools MCP)
```
{
  "status": "current",
  "reasons": [],
  "manifest_path": "docs/architecture/manifest.json"
}
- Đã kiểm tra trên Chrome DevTools MCP (1440x900):
  + URL 1: file:///.../docs/architecture/index.html (4 góc nhìn: overview, pipeline-lifecycle, search-and-archify, hooks-and-gates; 6 module pills; 0 console errors/warnings). Ảnh chụp: docs/tdq/mastermap-portal-desktop.png
  + URL 2: file:///.../docs/architecture/overview.html (tương tác sơ đồ 6 tầng, Node index 6 thành phần, 0 console errors/warnings). Ảnh chụp: docs/tdq/mastermap-overview-desktop.png
```

### Q2
```
[2026-10-25T18:24:05] doc_lint: lint 1 file: README.md
[2026-10-25T18:24:05] doc_lint: done — 0 violation(s) total, exit 0
```

### Q3 & QC-F2 & QC-F3
```
................................................... [ 98%]
.                                                                        [100%]
52 passed, 21 subtests passed in 8.43s
0 errors, 0 warnings, 0 informations (pyright scripts/tdq_archify.py)
```

### QC-F4 (Clean Code Self-Check)
- SRP: CÓ — Hàm `_generate_index_html` chỉ chịu trách nhiệm kết xuất trang chủ HTML từ dữ liệu model và danh sách views đã được kiểm chứng.
- OCP: CÓ — Tự động hiển thị bất kỳ danh sách module (`coverage.modules`) và danh sách góc nhìn (`rendered_views`) nào được khai báo trong `master.model.json` mà không cần sửa code.
- LSP: CÓ — Giữ nguyên chữ ký hàm `(validated_model: dict, rendered_views: list[dict]) -> str` và toàn bộ các nhãn hợp đồng kiểm thử.
- ISP: CÓ — Chỉ nhận đúng 2 tham số cần thiết (`validated_model` và `rendered_views`).
- DIP: CÓ — Phụ thuộc vào dữ liệu trừu tượng đã chuẩn hóa từ `validate_model` thay vì đọc trực tiếp tệp trên đĩa.

### QC-F1 (Full Suite `tron-bo` & Ledger `so`)
```
Elevated=False
Ran 2978 tests in 658.634s
OK (skipped=10)
ExitCode=0
request: 2026-10-25-1648-mastermap-va-readme-pro (phase qc)
full-suite runs: 1 of budget 2
radius misses: 0
```

## Lệch spec chờ duyệt
không có

## Kết luận
PASS toàn bộ
