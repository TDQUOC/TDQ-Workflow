# Brief — Tối ưu thời gian xử lý TDQ Workflow
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## Nguyên văn

> vậy có thể mở request handle cả p0+p1+p2 không?

Đọc lần đầu: người dùng muốn mở request triển khai cả ba nhóm P0/P1/P2 đã đề xuất trong `docs/tdq/reports/2026-11-06-1549-ra-soat-thoi-gian-workflow.md:20-40`. Phạm vi dự kiến gồm đo SessionStart/LSP, Graphify close-out, tránh full-suite rerun vô hiệu, thử workers/cache trên scope đủ điều kiện, đo hook I/O, batch thao tác đọc và lane routing phù hợp. Phân kỳ theo baseline, kiểm parity và rollback; không coi giả thuyết là speedup đo được. Không tự tắt search/approval/HTML/QC, không tự cài dependency hoặc bật workers/cache toàn cục. Lane full, QC full, benchmark đủ mẫu và rollout từng phần đã được chốt qua chat; chưa sửa runtime.

## Hiểu & kiến thức

### Năng lực và nguồn

| Công cụ | Phán quyết | Vai trò |
|---|---|---|
| `tdq-intake`, `tdq-spec`, `tdq-plan`, `tdq-build` | NỀN | Pipeline full, hai cổng duyệt, DoD và report. |
| LSP + Graphify + Grep | DÙNG | Symbol/caller, vỡ lan hai bước, quét rộng. `tdq_lsp.py check`: 7/8 bậc; Graphify CLI `affected step_graphify --depth 2` vẫn cho caller `main()`. |
| `tdq_runtime_bench.py`, `tdq_test.py`, receipts | DÙNG có kiểm soát | Baseline, parity, fresh QC; benchmark tốn thời gian chỉ khi scope/giới hạn được duyệt. |
| Archify | DÙNG | Spec preview và report MD/HTML có binding. |
| Setup tự cài / eval model | KHÔNG tự động | Cần đồng ý riêng khi cài hoặc bật eval; không thuộc phép đo mặc định. |

### Bảng đối chiếu vùng chạm

| Vùng file chạm | Phát hiện qua lớp nào | Tác động & quan hệ |
|---|---|---|
| `scripts/tdq_finish.py:198-207,300-323` | LSP `find_symbol/find_references`, Graphify `affected step_graphify --depth 2`, Grep | `main()` gọi rebuild Graphify đồng bộ sau code change; thay đổi freshness phải kiểm query/QC và fallback. |
| `hooks/scripts/session_start.py:154-186,208-272`, `scripts/tdq_lsp.py`, `scripts/tdq_readiness.py` | Grep + LSP workspace | Khởi động/readiness nối vòng cache/doctor; không bỏ proof kết nối hay module gate. |
| `scripts/tdq_test.py`, `scripts/tdq_test_receipt.py`, `scripts/tdq_runtime_bench.py` | Grep + report đã duyệt | Workers, reuse và receipt cùng ràng buộc parity/fresh; phải đo cùng inventory/source. |
| `hooks/scripts/search_observe.py`, `hooks/scripts/read_gate.py`, `hooks/scripts/search_gate.py` | Grep + policy | Ledger I/O hot path nhưng gate phải semantic-equivalent; không tắt theo lane tùy tiện. |
| `skills/tdq-intake/references/quick-lane.md`, `skills/tdq-build/references/qc.md`, `report-template.md` | Grep + báo cáo 2026-11-06 | B1 ba chiều, full fresh và HTML report có contract; không optional mặc định. |

`docs/kien-truc.md` còn NHÁP: chỉ dùng gợi ý về ranh giới `hooks/` → `scripts/`, không tự nhận mọi dòng là policy chốt. Source baseline: `docs/tdq/reports/2026-11-06-1549-ra-soat-thoi-gian-workflow.md:20-40`; claim LSP outlier và target 50% còn thiếu raw đủ để chứng nhận.

### Phạm vi đã chốt

- Mặt CHỌN: hiệu năng runtime, độ tin cậy chứng cứ/QC, bảo toàn gate bảo mật, maintainability tối thiểu cho phép đo.
- Mặt LOẠI: UI/UX sản phẩm, thay đổi dữ liệu người dùng, API public mới, thay đổi model/provider hoặc cài dependency mới.
- Bối cảnh: plugin TDQ nội bộ trên máy Windows 11, baseline ở repo hiện hành; benchmark đủ mẫu được duyệt, không đặt trần 30 phút; số tiết kiệm chưa đo.
- Mức đầu tư suy ra: đầy đủ — vì P0/P1/P2 chạm nhiều module runtime, hook, test và chính sách; rollout chỉ khi parity + hiệu năng đạt.

### Lộ trình

| Bước/phase | CÓ/BỎ | Vì sao |
|---|---|---|
| Analyze → spec → plan → implement → QC → report | CÓ | Request full, hai gate duyệt; QC full theo lựa chọn. |
| Baseline, benchmark đủ mẫu và rollout từng phần | CÓ | Người dùng chọn `1a 2a`; số chưa đủ chứng cứ không bật mặc định. |
| Research web ngoài | BỎ | Chỉ sửa hành vi nội bộ; chưa có dependency/API mới cần tra nguồn ngoài. |
| Model eval / auto-install / thay chính sách mandatory | BỎ | Không yêu cầu và không có đồng ý riêng; giữ HTML, approval, search, full fresh. |
| Browser UI test | BỎ | Không thay UI; Archify HTML verify tĩnh và công khai browser fallback. |

Một request bao trùm nhưng nhiều wave độc lập: (1) instrument + baseline, (2) P0 LSP/SessionStart/Graphify/full-suite invalidation, (3) P1 workers/cache/hook I/O, (4) P2 batch read/lane routing. Không tự bật tính năng có parity thất bại; báo fallback thay vì tuyên bố tiết kiệm.

## Hỏi đáp

1. Pipeline `1a` — full/deep.
2. Benchmark `1a` — đủ mẫu theo tiêu chí báo cáo; full-suite có thể chạy nhiều lượt trong phép đo, không đặt trần 30 phút.
3. Rollout `2a` — bật từng phần **đạt parity và hiệu năng**, workers/cache chỉ với scope đủ điều kiện; không bật mọi nơi.
4. QC `3a` — `full`, đã ghi `muc_qc=full`; trọn suite một lần ở cổng QC sau source edit, các lượt benchmark là thí nghiệm riêng không được nhận thay QC fresh.
5. Vòng scope không hỏi lại: người dùng đã chỉ đích cả P0/P1/P2 trong report đã duyệt, host/repo và guardrail cũng có trong code; không cần mở rộng sang lĩnh vực mới.
