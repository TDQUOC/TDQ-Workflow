# PLAN — Rà soát đề xuất rút ngắn thời gian TDQ Workflow

Ngày: 2026-11-06 · Spec: ../spec/2026-11-06-1549-ra-soat-thoi-gian-workflow.md (bản 1.0, ĐÃ DUYỆT) · Lane: full
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md
Mode thực thi: subagent — mô phỏng 4 task main 8,1 phút, đội 6,1 phút (`Winner: đội`, chênh 2,0 phút); 3 subagent đã fanout ở analyze, các task tổng hợp/QC nối tiếp và chung file report nên leader giữ một chủ ghi.
Trạng thái plan: HOÀN THÀNH.

## Quy tắc thi hành

- Chỉ ghi docs request, không sửa runtime/luật, không cài/setup hay chạy full suite. Tick `[~]` trước task, `[x]` sau khi chứng cứ/test tài liệu đạt; DoD tick riêng khi QC xác nhận.
- Số partial/unknown không gán thành user/model; trích source theo file:line; chưa đủ raw → UNCERTAIN. Optional không trái user instruction. Eval chưa kích hoạt.
- Preview planned đã duyệt: `../spec/2026-11-06-1549-ra-soat-thoi-gian-workflow-preview.html`, verify binding trước lúc ghi report.

## Thiết kế Trước vs Sau

| Trước | Sau |
|---|---|
| Hai report Review nêu số cũ và giả thuyết cạnh nhau | Bảng claim → chứng cứ → verdict, nêu giới hạn rõ |
| Một số mục optional trái contract HTML/search/QC | Bảng giữ bắt buộc, conditional, cần duyệt, bác bỏ |

## P1 — Kiểm claim và số liệu

- [x] **T1.1** (e8m) Tổng hợp 3/3 phản biện, kiểm timing record, công thức 31,84%, full suite lịch sử và mới, LSP/Graphify metadata — Test: `python -c "import json,pathlib; p=pathlib.Path('C:/Users/admin/Documents/Projects/ForAgentCode/Review-TDQWorkflow/docs/tdq/timing.jsonl'); assert len(p.read_text(encoding='utf-8').splitlines())==2; assert round(4494.8/14116*100,2)==31.84"`
  - Dùng: `3 `Explore` subagents`
  - Để: đọc độc lập ba góc runtime, policy optional, benchmark trước tổng hợp; 3/3 đã hoàn tất ở analyze.
  - Ra: ba digest có claim, source path:line và nhãn CONFIRMED/UNCERTAIN/CONFLICT; bảng O1.
  - Kiểm: `python -c "import pathlib; p=pathlib.Path('C:/Users/admin/Documents/Projects/ForAgentCode/Review-TDQWorkflow/docs/tdq/timing.jsonl'); assert len(p.read_text(encoding='utf-8').splitlines())==2"`
  - Không dùng cho: tự sửa runtime hoặc tạo benchmark tốn phút.

- [x] **T1.2** (e2m) Kiểm truy vết liên kết runtime và policy từ LSP/Graphify/Grep đã có — Test: `python scripts/tdq_lsp.py check`
  - Dùng: `LSP, Graphify, Grep` (mcp)
  - Để: đối chiếu caller `step_graphify`, vùng vỡ lan hai bước và nguồn policy.
  - Ra: bảng vùng chạm trong brief và claim runtime gắn file:line tại report.
  - Kiểm: `python scripts/tdq_lsp.py check`
  - Không dùng cho: coi graph stale hoặc LSP timeout là bằng chứng tốc độ.
  - Cần: T1.1

## P2 — Phân loại ưu tiên và optional

- [x] **T2.1** (e11m) Viết danh sách P0/P1/P2 có phép đo/promote/rollback và bảng mandatory/conditional/optional-chờ duyệt/reject; phản biện mâu thuẫn HTML/search/approval/QC/setup — Test: `python scripts/doc_lint.py docs/tdq/reports/2026-11-06-1549-ra-soat-thoi-gian-workflow.md`
  - Cần: T1.2
  - Ra: O2/O3 kèm path:line, không sửa code.

## P3 — QC và report

- [x] **T3.1** (e8m) QC full cho report read-only: so claim với source hiện hành, lint, render và verify HTML, ghi giới hạn chưa test/benchmark, chốt cặp QC/report — Test: `python scripts/tdq_archify.py verify --document docs/tdq/reports/2026-11-06-1549-ra-soat-thoi-gian-workflow.md --manifest docs/tdq/reports/2026-11-06-1549-ra-soat-thoi-gian-workflow.manifest.json`
  - Cần: T2.1
  - Dùng: `Archify`
  - Để: render HTML Trước/Sau và ràng buộc báo cáo với nguồn working-tree.
  - Ra: `docs/tdq/reports/2026-11-06-1549-ra-soat-thoi-gian-workflow.html`, manifest và QC Markdown.
  - Kiểm: `python scripts/tdq_archify.py verify --document docs/tdq/reports/2026-11-06-1549-ra-soat-thoi-gian-workflow.md --manifest docs/tdq/reports/2026-11-06-1549-ra-soat-thoi-gian-workflow.manifest.json`
  - Không dùng cho: suy giá trị hiệu năng hay browser UI test.

## Cụm song song & file nóng

- 3 Explore subagents đã fanout ở analyze (runtime, optional, benchmark). Bốn task T1.1 → T1.2 → T2.1 → T3.1 đọc đầu ra nối tiếp, `reports/<slug>.md` là file nóng: một chủ ghi, không thêm agent sửa song song.

## Px — Log & test bắt buộc

Log: BỎ — chỉ đọc source và viết docs, `tdq_finish --log` vẫn ghi nhật ký request; không thêm runtime/log service. Chạy các assert nguồn/ratio và lint/render/verify, không chạy full suite không liên quan.

## Definition of Done

- [x] Q1 Hai nguồn Review/timing hiện còn và phép tính 31,84% được kiểm; đánh nhãn lịch sử/current đúng — `python -c "import pathlib; p=pathlib.Path('C:/Users/admin/Documents/Projects/ForAgentCode/Review-TDQWorkflow/docs/tdq/timing.jsonl'); assert len(p.read_text(encoding='utf-8').splitlines())==2; assert round(4494.8/14116*100,2)==31.84"`
- [x] Q2 P0/P1/P2 kèm phép đo/rollback, không coi timeout là thời gian thực — `python scripts/doc_lint.py docs/tdq/reports/2026-11-06-1549-ra-soat-thoi-gian-workflow.md`
- [x] Q3 Bảng optional không trái luật user, runtime không sửa — `git diff --name-only -- scripts hooks skills tests`
- [x] Q4 3/3 phản biện, report Markdown + HTML verify, link nguồn chính xác — `python scripts/tdq_archify.py verify --document docs/tdq/reports/2026-11-06-1549-ra-soat-thoi-gian-workflow.md --manifest docs/tdq/reports/2026-11-06-1549-ra-soat-thoi-gian-workflow.manifest.json`

Ước tính 29 phút tác vụ, không gồm chờ duyệt. Không dùng một số tiền tiết kiệm dự báo làm verdict QC.
