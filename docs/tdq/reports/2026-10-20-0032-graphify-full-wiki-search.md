# REPORT — Nâng cấp Graphify full extraction, wiki provenance và cấu hình provider an toàn (`2026-10-20-0032-graphify-full-wiki-search` · lane full · mode main · 12 task tick đủ)

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

**Đã làm:** P1 Viết shared full extraction transaction, fail-closed khi thiếu backend/wiki, loại trừ wiki khỏi input corpus (`scripts/tdq_graphify.py`, `scripts/tdq_finish.py`) · P1b Bổ sung cấu hình provider an toàn `docs/tdq/config.json` và hướng dẫn `docs/tdq/graphify-provider.md`, không lưu secret trong repo/config/log, chỉ lấy key từ biến môi trường, tự động chuyển code-only degraded khi thiếu cấu hình · P2 Tích hợp bootstrap (`tdq_setup.py`) và rung 7 (`tdq_lsp.py`) phân biệt full fresh vs degraded, hướng dẫn fallback LSP + grep · P3 Benchmark A/B (`evals/audit_graphify_full_wiki_ab.py`) đo 3 biến thể, giữ nguyên selector tìm kiếm 3 tầng do Graphify CLI ngữ cảnh chưa vượt trội so với LSP/grep · P4 Hoàn thiện trọn bộ unit test và tài liệu.
**Kết quả:** Benchmark A/B TDQ-Workflow: code-only 2,472 nodes/5,089 links/5.08s → full 2,491/5,107/51.75s (36,938 tokens in / 2,780 out) → full+wiki 2,483/5,093/61.89s (36,938 in / 3,366 out, 149 wiki articles) · Độ chính xác Photoboth360: Static extraction F1 0.958 (imports) và 0.898 (callables); Scorer P@5 0.200, R@5 0.833, MRR@10 0.554; CLI context BFS F1 0.250 · Selector: giữ nguyên 3 tầng (exact grep → relationship/diagnostics LSP → architecture/concept Graphify + grep, then verify).
**Kiểm:** 100% test vùng chạm PASS (10 `test_tdq_graphify`, 22 `test_tdq_finish`, 37 `test_tu_khoi_tao`, 7 `test_bac_graphify`, 8 `test_luat_4_tang`, 6 `test_graphify_full_wiki_ab`) · `doc_lint` 0 lỗi · `token_budget` 54 file OK · QC PASS (lệch, chờ duyệt) 4/4 mục DoD.
**Đầu ra:** `scripts/tdq_graphify.py` · `docs/tdq/config.json` · `docs/tdq/graphify-provider.md` · `docs/tdq/bench/2026-10-20-0032-graphify-full-wiki-ab.md` · `docs/tdq/reports/graphify-danh-gia-nhanh.html` · `docs/tdq/reports/2026-10-20-worktree-subagent-access.md`.
**Giới hạn:** Request được mở với bỏ qua LSP (`lsp_bo_qua`: Người dùng cho phép bỏ qua kiểm chứng LSP cross-file cho nghiên cứu/thay đổi hook; phân tích trực tiếp source và benchmark Graphify) · Worktree sub-agent gặp lỗi handle trên Windows, đã khắc phục bằng cách chuyển mode main inline và dọn dẹp sạch · Mặc định `docs/tdq/config.json` để `enabled: false`, người dùng cần cấu hình endpoint/model và export biến môi trường chứa API key để bật trọn vẹn full semantic extraction.
**Lệch spec chờ duyệt:** #1 Q1: Full extraction thật tối đa 3 lần → đo được 3 lần trong bài đo A/B và transaction → phương án đã áp: giữ artifact hiện có, kích hoạt degraded fail-closed, không phát sinh lần gọi thứ tư ngoài ngân sách.
**Git:** Commit nền `f2a5f4e feat: add full graphify transaction contract` đã tạo trong quá trình thực thi; các thay đổi cấu hình an toàn và hoàn thiện runner hiện đang staged/unstaged tại nhánh `feature/graphify-full-wiki-search`.

## Thời gian

| Phase | Wall clock | Model time | Times entered |
|---|---|---|---|
| idle | 0s | — | 1 |
| analyze | 9 min | — | 1 |
| spec | 20 min | — | 2 |
| plan | 37 min | — | 2 |
| implement | 9h 12min | — | 2 |
| qc | 31s | — | 1 |
| report | 17s | — | 1 |
| **Total** | **10h 19min** | **—** | |
