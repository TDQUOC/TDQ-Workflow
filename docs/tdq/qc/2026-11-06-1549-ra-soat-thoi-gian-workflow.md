# QC — Rà soát thời gian TDQ Workflow
Ngày: 2026-11-06 · Plan: ../plan/2026-11-06-1549-ra-soat-thoi-gian-workflow.md · Vòng: 1
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

| # | Hạng mục | Lệnh đã chạy | Kết quả | PASS/FAIL |
|---|---|---|---|---|
| Q1 | Timing 2 record, phép chia, mẫu lịch sử/hiện hành | `python -c "import pathlib; p=pathlib.Path('C:/Users/admin/Documents/Projects/ForAgentCode/Review-TDQWorkflow/docs/tdq/timing.jsonl'); assert len(p.read_text(encoding='utf-8').splitlines())==2; assert round(4494.8/14116*100,2)==31.84"` | exit 0; 2 record; 31,84%; report `:14-18` tách mẫu 857,25s và 800,34s | PASS |
| Q2 | P0/P1/P2, đo/rollback, timeout khác duration | `python scripts/doc_lint.py docs/tdq/reports/2026-11-06-1549-ra-soat-thoi-gian-workflow.md` | `0 violation(s) total, exit 0`; report `:20-31` | PASS |
| Q3 | Optional đúng contract, không sửa runtime | `git diff --name-only -- scripts hooks skills tests` | output rỗng; report `:33-40` giữ HTML, gate, QC | PASS |
| Q4 | Ba phản biện, MD/HTML và binding | `python scripts/tdq_archify.py verify --document docs/tdq/reports/2026-11-06-1549-ra-soat-thoi-gian-workflow.md --manifest docs/tdq/reports/2026-11-06-1549-ra-soat-thoi-gian-workflow.manifest.json` | `status=current`, `binding.valid=true`, `manifest.status=current`; render gates validate/deliver/check pass, browser-check not-run | PASS |
| QC-F1 | Full fresh | Không chạy, vì spec §1 ngoài phạm vi và §6 xác định QC full tài liệu read-only | **KHÔNG CHẠY**; 0 full-run trong request, không có verdict hồi quy runtime | Ngoại lệ phạm vi đã duyệt |
| QC-F2 | Vùng chạm code | `python scripts/tdq_test.py vung-cham --plan-only --files docs/tdq/reports/2026-11-06-1549-ra-soat-thoi-gian-workflow.md` | `scope=none selected=0/193 selectors=(none) modules=(none) reason=no fallback` | KHÔNG ÁP DỤNG |
| QC-F3 | Ràng buộc kiến trúc spec §5 | `git diff --name-only -- scripts hooks skills tests`; `python scripts/tdq_archify.py verify ...` | Không đổi runtime/luật; HTML bound current; `docs/kien-truc.md` vẫn NHÁP | PASS |
| QC-F4 | Clean code | Kiểm vùng chạm bằng Git và task plan | KHÔNG ÁP DỤNG — không sửa file code | KHÔNG ÁP DỤNG |

## Bằng chứng và giới hạn

- `python scripts/tdq_lsp.py check`: bậc 1–6 và 8 ĐẠT, bậc 7 Graphify THIẾU; LSP reference dùng được, không lấy graph làm bằng chứng mới. Không cài/sửa môi trường.
- `Review-TDQWorkflow/docs/tdq/timing.jsonl:1-2` còn hai record; claim quick n=3 không thể tái dựng. `Review-TDQWorkflow/docs/tdq/reports/2026-11-05-1949-tdq-runtime-audit.md:24-40` chứa số LSP và full suite lịch sử; `docs/tdq/reports/2026-11-06-1250-han-che-ngat-giua-plan.md:9-15` chứa run gần hơn trước 0.94.0.
- `scripts/tdq_finish.py:198-207,300-323` xác nhận gọi extract đồng bộ với timeout ceiling. `skills/tdq-build/references/report-template.md:31-34` và `qc.md:91-100` là rào bắt buộc.
- Archify render exit 0: `gates.validate/deliver/check=pass`, `browser-check=not-run`; static verify sau render `status=current`. Browser native chưa chạy, không gọi là PASS browser.
- Team map: 1/4 task giao nhưng agent bị chặn vì report MD chưa có trong worktree; leader hoàn tất render ở root. Ba Explore subagents đã thực hiện analyze. Không có merge task con hay chứng cứ task con hoàn thành. Worktree T3.1 đã rỗng, được dọn và đóng ledger ngày 2026-11-07; `sweep` báo 0 open.
- `tdq_timing.py show` snapshot trong report là thời điểm 22:21, không phải đóng request; API/tool partial và background unavailable; không gán unattributed cho user/model.

## Lệch spec chờ duyệt

Không có. Spec đã được duyệt lại đúng digest nội dung ở 22:32:50+07:00.

## Kết luận

PASS 4/4 DoD tài liệu; Archify static current. Full fresh runtime và browser native **không chạy** theo phạm vi read-only đã duyệt; không đưa chúng vào số PASS. `eval: chưa kích hoạt (opt-in)`.
