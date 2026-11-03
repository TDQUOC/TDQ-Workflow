# REPORT — Tự động setup & chứng minh LSP theo module (`2026-10-07-2225-tu-dong-setup-lsp` · lane full · mode main · 21 task + 9 DoD tick đủ)

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

**Đã làm:** `lsp_module.py` dò module (ngôn ngữ, gốc), bảng `.tdq-lsp-module.json` có vân tay + hạn 24 h, kịch bản MCP `start_lsp → open_document → find_references`, dọn broker mồ côi, cảnh báo commit < 4 GB · `tdq_lsp.py` bậc 8 + lệnh `module`/`kich-ban`/`ghi-kiem`, bậc 3 cổng 3 (ngôn ngữ chưa khai trong MCP `lsp`) · cổng LSP ở `init` + `--bo-qua-lsp` · hook `lsp_gate.py` chặn `start_lsp` thiếu `language_id`/sai cặp · `tdq_setup.py` cài agent-lsp từ release (SHA256, không shell), tự khai server ngôn ngữ mới vào MCP `lsp` · SessionStart dựng nền lại khi có ngôn ngữ mới · skill/docs + bản 0.59.0
**Kết quả:** dò module TDQ_Monitor_Online 0,04 s (ngưỡng 1 s) · hook 82–85 ms (ngưỡng 200 ms) · claudecodeui 2 module TS ĐẠT qua MCP thật · ca gốc trên bản sao: `init` rc=2 khi chưa kiểm → MCP thật 7 tham chiếu → ĐẠT → `init` rc=0
**Kiểm:** `tdq_test.py tron-bo` Ran 2531, OK (skipped=9), radius misses 0 · `doc_lint` 0 vi phạm · `tdq_lsp.py check` Tổng ĐẠT ở TDQ-Workflow và claudecodeui · QC PASS 9/9 DoD + 4/4 mục cố định
**Sửa khi soát diff:** `cai_thieu` ghi nợ giả với lệnh workflow đã viết lại đường dẫn plugin (thêm test đỏ→xanh) · report chưa đọc `lsp_bo_qua` (thêm dòng kiểm vào report-template) · 2 test giòn (dấu nháy đường dẫn; CRLF làm bản mẫu 4250 → 4314 byte) · tham số thừa `_ghi_args_mcp`
**Đầu ra:** `scripts/lsp_module.py` · `hooks/scripts/lsp_gate.py` · QC: `docs/tdq/qc/2026-10-07-2225-tu-dong-setup-lsp.md`
**Giới hạn:** bậc 7 graphify đang cảnh báo đồ thị cũ ở cả hai repo (không chặn) · bậc 8 so số tham chiếu chứ không so số file (lệch #1) · các file cũ chưa về 0 dòng i18n (lệch #2, cần request dọn riêng) · cột model time trống vì không đọc được transcript
**Lệch spec (user đã duyệt 2026-10-08 "Duyệt 1 2"):** #1 Q6 · "số file LSP ≥ số file grep" → GCF chỉ trả namespace, không có file · áp: ĐẠT khi tham chiếu LSP > số lần trong file định nghĩa — #2 Q8 · "i18n_check exit 0" → file cũ vốn chưa bao giờ 0 · áp: file mới 0 dòng, file luật không tăng
**Git:** commit trên `feature/tu-dong-setup-lsp`, merge `--no-ff` về `main`, không push

## Thời gian

| Phase | Wall clock | Model time | Times entered |
|---|---|---|---|
| idle | 0s | — | 1 |
| analyze | 4h 12min | — | 1 |
| spec | 15 min | — | 1 |
| plan | 5 min | — | 1 |
| implement | 5h 39min | — | 1 |
| qc | 8 min | — | 1 |
| report | 0s | — | 1 |
| **Total** | **10h 19min** | **—** | |
