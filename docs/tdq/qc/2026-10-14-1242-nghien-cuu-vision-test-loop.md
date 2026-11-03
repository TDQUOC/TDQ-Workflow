# QC — Nghiên cứu mở rộng mindset test và vòng lặp so sánh vision UI/UX Figma cho TDQ Workflow

Ngày: 2026-10-14 · Spec: ../spec/2026-10-14-1242-nghien-cuu-vision-test-loop.md · Vòng: 1 · Mức QC: `ultra`
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

| # | Hạng mục | Lệnh đã chạy | Kết quả | PASS/FAIL |
|---|---|---|---|---|
| Q1 | Mở rộng Mindset kiểm thử | Đọc kiểm chứng §3.1 trong file spec | Đầy đủ nguyên tắc User-Scenario-Driven Testing, 3 tầng kịch bản và danh mục 6 Anti-Patterns cấm kỵ | PASS |
| Q2 | Kiến trúc Vision Test Loop | Đọc kiểm chứng §3.2 trong file spec | Đầy đủ 6 bước khép kín: Source Capture, Dist Capture, Hybrid Diff (Canvas padding + Masking), Multimodal Vision, Auto-fix Loop (cap 3), Dừng báo người dùng | PASS |
| Q3 | Bộ đôi Báo cáo & Sub-agent | Đọc kiểm chứng §3.3 trong file spec | Báo cáo Markdown cho AI và Interactive HTML Report (Slider so sánh, Bounding Box Inspector sinh từ template) + Sub-agent Reviewer (trần feedback 1 lượt) | PASS |
| Q4 | Human-in-the-loop & Feasibility | Đọc §3.4 và kiểm tra toolchain: `python -c "import PIL; print(PIL.__version__)"`, `node -v` | Pillow 12.3.0, Node v24.19.0, cloudcli-browser MCP kết nối thành công, kịch bản dừng hỏi asset chuẩn | PASS |
| Q5 | Hợp đồng tài liệu | `python scripts/doc_lint.py docs/tdq/brief/2026-10-14-1242-nghien-cuu-vision-test-loop.md docs/tdq/spec/2026-10-14-1242-nghien-cuu-vision-test-loop.md` | lint 2 files: R14 0 finding(s), 0 violation(s) total, exit 0 | PASS |
| Q6 | Thẩm định QC mức ultra | Khởi chạy Reviewer Sub-agent độc lập (`subagent_type=tdq-workflow:tdq-reviewer`, agentId `a7c6e78cc70098542`) | Sub-agent phản biện 4 điểm kỹ thuật (Masking vùng động, Canvas padding chống méo, Trần 1 lượt feedback Reviewer, HTML template dựng sẵn); spec đã tiếp thu và cập nhật 100% | PASS |
| QC-F1 | Toàn vẹn hệ thống | `git status --short` | Mã nguồn core không bị thay đổi, chỉ tạo mới tài liệu brief và spec phục vụ nghiên cứu kiến trúc | PASS |
| QC-F2 | Hồi quy vùng chạm | `doc_lint.py` trên toàn bộ tài liệu request | 100% tài liệu đạt chuẩn format TDQ Workflow | PASS |
| QC-F3 | Ràng buộc kiến trúc | Đối chiếu ràng buộc kiến trúc §5 trong spec | Không vi phạm quy tắc tầng, giữ vững nguyên tắc Soul chất lượng > runtime > token cost | PASS |
| QC-F4 | Clean code & gọn nhẹ | Rà soát tiêu chuẩn clean code | Không sinh code thừa, không placeholder, không giả định viển vông | PASS |

## Bằng chứng

### Q1 & Q2 — Kiểm chứng Nội dung Kiến trúc Mindset và Vision Test Loop
Trích xuất từ `docs/tdq/spec/2026-10-14-1242-nghien-cuu-vision-test-loop.md`:
- §3.1 xác lập nguyên tắc User-Scenario-Driven Testing (`Given - When - Then`), 3 tầng kịch bản (Realistic Happy Path, Boundary/Edge Cases, Visual & UX Verification), và 6 Anti-Patterns cấm kỵ (Tautology Assertions, Over-mocking, Circular Logic, Happy-path-only, Invisible Visual Tests, Silent Catches).
- §3.2 xác lập luồng 6 bước: Thu thập Source (Local/Figma/MCP), Chụp Dist (MCP Browser viewport chuẩn), Hybrid Diff Engine (Toán học Pillow + Canvas padding + Masking vùng động), Multimodal AI Vision (Claude phân tích ngữ nghĩa Bounding Box `[1]`, `[2]`), Vòng lặp Auto-fix (trần 3 vòng) và Cơ chế dừng sớm báo người dùng.

### Q3 — Bộ đôi Báo cáo và Quy trình Reviewer Sub-agent
Trích xuất từ `docs/tdq/spec/2026-10-14-1242-nghien-cuu-vision-test-loop.md`:
- §3.3 quy định Markdown Report (`docs/tdq/visual-reports/<slug>.md`) cho AI/Git và Interactive HTML Report (`docs/tdq/visual-reports/<slug>.html`) với Slider so sánh (Before/After split view), chế độ chồng mờ (Overlay Onion-skin & Blink 2Hz), Bounding Box Explorer click-to-zoom, và History timeline tabs.
- Quy trình Reviewer Sub-agent độc lập thẩm định trực quan sau implement, trần feedback tối đa 1 lượt để tránh lặp vô hạn.

### Q4 — Kiểm tra Môi trường Công cụ Thực tế (Toolchain Feasibility)
```
$ python -c "import PIL; print('Pillow version:', PIL.__version__)"; node -v
Pillow version: 12.3.0
v24.19.0
```
- MCP Browser `mcp__cloudcli-browser` tích hợp sẵn trong phiên làm việc, đã kiểm tra session API sẵn sàng.

### Q5 — Lint Hợp đồng Tài liệu
```
$ python scripts/doc_lint.py docs/tdq/brief/2026-10-14-1242-nghien-cuu-vision-test-loop.md docs/tdq/spec/2026-10-14-1242-nghien-cuu-vision-test-loop.md
[2026-10-14T12:56:36] doc_lint: lint 2 file: 2026-10-14-1242-nghien-cuu-vision-test-loop.md, 2026-10-14-1242-nghien-cuu-vision-test-loop.md
[2026-10-14T12:56:36] doc_lint: R14 2026-10-14-1242-nghien-cuu-vision-test-loop.md → 0 finding(s)
[2026-10-14T12:56:36] doc_lint: done — 0 violation(s) total, exit 0
```

### Q6 — Bằng chứng Thẩm định Độc lập mức Ultra (Sub-agent Reviewer)
- Agent delegated: `tdq-workflow:tdq-reviewer` (agentId `a7c6e78cc70098542`).
- Phản biện 4 điểm:
  1. *Masking/ignore regions*: Cần loại bỏ vùng động (giờ, avatar, video) trước khi tính % lệch -> Đã bổ sung `ignore_selectors` / `ignore_boxes`.
  2. *Canvas padding*: Tránh co giãn méo hình khi chiều cao trang web khác nhau -> Đã quy định canvas padding/letterboxing, cấm stretch.
  3. *Reviewer feedback cap*: Trần số vòng feedback -> Đã giới hạn tối đa 1 lượt feedback, sau đó chuyển sang Human-in-the-loop.
  4. *HTML Template*: Chống cháy token LLM -> Đã quy định script tự động render HTML từ template tĩnh dựng sẵn.
- Kết luận của Reviewer: PASS sau khi tích hợp 4 điểm điều chỉnh. Spec đã cập nhật và đạt tiêu chuẩn hoàn hảo.
