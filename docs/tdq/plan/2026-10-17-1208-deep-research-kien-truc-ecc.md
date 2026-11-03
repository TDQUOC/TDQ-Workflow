# PLAN — Xuất bản Báo cáo Nghiên cứu Chuyên sâu Toàn diện Kiến trúc, Tính năng & Giải thuật của ECC (`ecc-universal` `v2.2.3`)

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

- **Request**: `2026-10-17-1208-deep-research-kien-truc-ecc`
- **Spec**: `docs/tdq/spec/2026-10-17-1208-deep-research-kien-truc-ecc.md`
- **Trạng thái**: ĐÃ DUYỆT

Mode thực thi: subagent — theo đo đạc thực nghiệm từ `tdq_bench.py simulate --he-so-agent 1.5`, mode `subagent` (3.1 phút) thắng `main` (6.1 phút) với chênh lệch 3.0 phút.

## Cụm song song

- **Wave 1 (Song song độc lập vùng file)**:
  - Cụm A (`T1.1`): Biên soạn Báo cáo Kỹ thuật Markdown chuyên sâu 11 chương (`docs/tdq/reports/2026-10-17-1208-deep-research-kien-truc-ecc.md`).
  - Cụm B (`T1.2`): Xây dựng Standalone HTML Dashboard Report tương tác 100% offline (`docs/tdq/reports/2026-10-17-1208-deep-research-kien-truc-ecc.html`).
  - Cụm C (`T2.1`): Viết bộ kiểm thử tự động xác thực cấu trúc và nội dung của cả 2 báo cáo (`tests/test_report_kien_truc_ecc.py`).

## Phase 1 — Biên soạn Báo cáo Markdown & Standalone HTML Dashboard Report

- [x] **T1.1** (e8m) Biên soạn Báo cáo Kỹ thuật Markdown chuyên sâu 11 chương tại `docs/tdq/reports/2026-10-17-1208-deep-research-kien-truc-ecc.md` (gồm 10 chương phân tích 10 phân hệ SA1–SA10 của ECC `v2.2.3` + Chương 11 Bảng đối chiếu ECC vs TDQ Workflow `v0.71.0` trên 10 trục kiến trúc và Top 10 giải thuật tinh hoa có thể học hỏi) — Test: `python3 -c "import pathlib; p=pathlib.Path('docs/tdq/reports/2026-10-17-1208-deep-research-kien-truc-ecc.md'); s=p.read_text('utf-8'); assert len(s.splitlines())>=450 and all(k in s for k in ['SA1','SA2','SA3','SA4','SA5','SA6','SA7','SA8','SA9','SA10','TCAS','Szymkiewicz-Simpson','GateGuard','scanShell','ecc2','orch-review','TDQ Workflow'])"`
  - Chạm: `docs/tdq/reports/2026-10-17-1208-deep-research-kien-truc-ecc.md`
  - Dùng: `Agent`
  - Để: Tổng hợp chính xác toàn bộ kết quả khảo sát từ 10 subagents (SA1–SA10) trên kho mã nguồn `C:\Users\admin\Documents\ECC` và phục vụ thẩm định độc lập qua `tdq-qc-tester` ở pha QC
  - Ra: Nội dung 11 chương chuyên sâu trong `docs/tdq/reports/2026-10-17-1208-deep-research-kien-truc-ecc.md` kèm biên bản thẩm định ở pha QC
  - Kiểm: Đủ 11 chương, đầy đủ công thức toán học và dẫn chứng đường dẫn tuyệt đối tới `C:\Users\admin\Documents\ECC`
  - Không dùng cho: Không spawn lại subagent đọc lặp những file đã có đủ bằng chứng trong Brief

- [x] **T1.2** (e10m) Xây dựng Standalone HTML Dashboard Report tương tác 100% offline tại `docs/tdq/reports/2026-10-17-1208-deep-research-kien-truc-ecc.html` (áp dụng nguyên tắc trực quan hóa của `dataviz`: Dark/Light mode toggle, sticky sidebar navigation, live search & section filter, KPI stat tiles, tối thiểu 4 sơ đồ kiến trúc/giải thuật SVG inline, hộp công thức toán học TCAS/ECC2/Instincts/GAN/EDD và bảng ma trận đối chiếu ECC vs TDQ Workflow) — Test: `python3 -c "import pathlib, html.parser; p=pathlib.Path('docs/tdq/reports/2026-10-17-1208-deep-research-kien-truc-ecc.html'); s=p.read_text('utf-8'); parser=html.parser.HTMLParser(); parser.feed(s); assert s.count('<svg')>=4 and len(s.splitlines())>=700 and all(k in s for k in ['TCAS','Szymkiewicz-Simpson','GateGuard','ecc2','orch-review','TDQ Workflow'])"`
  - Chạm: `docs/tdq/reports/2026-10-17-1208-deep-research-kien-truc-ecc.html`
  - Dùng: `dataviz`
  - Để: Thiết kế hệ thống bảng màu chuẩn tương phản Dark/Light, stat tiles KPI, sơ đồ kiến trúc SVG inline và bảng dữ liệu so sánh giữa ECC và TDQ Workflow
  - Ra: File `docs/tdq/reports/2026-10-17-1208-deep-research-kien-truc-ecc.html` hoạt động độc lập không cần CDN ngoài, có >= 4 sơ đồ SVG và bộ lọc tương tác
  - Kiểm: Mở trực tiếp trên trình duyệt không lỗi console, có nút chuyển Dark/Light mode, ô tìm kiếm lọc tức thời và >= 4 thẻ `<svg>`
  - Không dùng cho: Không nhúng thư viện JS/CSS qua mạng ngoài (Chart.js, D3 CDN, Tailwind CDN) làm mất tính độc lập offline

## Phase 2 — Kiểm thử Tự động & Nhật ký

- [x] **T2.1** (e5m) Viết bộ kiểm thử tự động `tests/test_report_kien_truc_ecc.py` kiểm tra toàn diện cả 2 báo cáo (`.md` và `.html`): kiểm tra tồn tại file, tính hợp lệ DOM HTML, không phụ thuộc CDN ngoài, có >= 4 biểu đồ `<svg>`, độ phủ đủ 10 phân hệ SA1–SA10 + Chương 11 đối chiếu TDQ Workflow, kiểm chứng các hằng số/công thức giải thuật (`TCAS`, `Szymkiewicz-Simpson`, `GateGuard`, `scanShell`, `ecc2`, `orch-review`, `Cryptographic Digest Chain`), và giữ sạch cơ chế log chuẩn của dự án — Test: `python3 -m unittest tests/test_report_kien_truc_ecc.py`
  - Chạm: `tests/test_report_kien_truc_ecc.py`

## Definition of Done

- [x] **DoD-1**: Tệp Báo cáo Markdown `docs/tdq/reports/2026-10-17-1208-deep-research-kien-truc-ecc.md` tồn tại, đủ 11 chương (SA1–SA10 + Đối chiếu TDQ Workflow) và không chứa placeholder — Check: `python3 -c "import pathlib; s=pathlib.Path('docs/tdq/reports/2026-10-17-1208-deep-research-kien-truc-ecc.md').read_text('utf-8'); assert len(s.splitlines())>=450 and all(k in s for k in ['SA1','SA2','SA3','SA4','SA5','SA6','SA7','SA8','SA9','SA10','TCAS','Szymkiewicz-Simpson','GateGuard','scanShell','ecc2','orch-review','TDQ Workflow'])"`
- [x] **DoD-2**: Tệp Standalone HTML Dashboard Report `docs/tdq/reports/2026-10-17-1208-deep-research-kien-truc-ecc.html` tồn tại, tự thân 100% offline, có Dark/Light mode, live search và >= 4 sơ đồ SVG — Check: `python3 -c "import pathlib; s=pathlib.Path('docs/tdq/reports/2026-10-17-1208-deep-research-kien-truc-ecc.html').read_text('utf-8'); assert s.count('<svg')>=4 and len(s.splitlines())>=700 and 'cdn.' not in s.lower()"`
- [x] **DoD-3**: Bộ kiểm thử `tests/test_report_kien_truc_ecc.py` và toàn bộ test suite của dự án chạy xanh 100% — Check: `python3 -m unittest tests/test_report_kien_truc_ecc.py`
- [x] **DoD-4**: Tài liệu spec và plan đạt chuẩn `doc_lint.py --pair` — Check: `python3 scripts/doc_lint.py --pair docs/tdq/spec/2026-10-17-1208-deep-research-kien-truc-ecc.md docs/tdq/plan/2026-10-17-1208-deep-research-kien-truc-ecc.md`
