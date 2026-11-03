# Report — bundle portable cho Antigravity CLI (agy)
Ngày: 2026-08-27 · Plan: ../plan/2026-08-27-1112-antigravity-portable-skill.md · QC: ../qc/2026-08-27-1112-antigravity-portable-skill.md
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## Đã làm
- Thêm target thứ 3 `antigravity_portable/` cho `scripts/build_portable.py`: skill (9 skill theo
  đúng thứ tự đọc), `scripts/`, 2 hook agy, `config/hooks.json` + `config/settings.json` +
  `config/mcp_config.json`, README hướng dẫn cài user-level và `manifest.json` (83 file).
- 2 hook thật, mạnh hơn hẳn bản `portable_codex/` chỉ-markdown: `PreToolUse` trả `deny` CHẶN CỨNG
  đúng 2 luật cố định (tên branch/worktree cấm; ghi thẳng `state.json`/`STATE.md` qua shell), và
  `Stop` trả `continue` ép không kết lượt khi plan còn việc — port nguyên 3 điều kiện của
  `stop_gate.py`, có `MAX_STREAK=3` để không nhốt phiên bị kẹt.
- Vì path cấu hình global của agy chưa nhất quán giữa các nguồn, README bắt copy trùng lặp vào
  MỌI path ứng viên (3 chỗ skill, 2 chỗ hooks.json, 2 chỗ mcp_config.json) + bước tự kiểm
  `/skills` `/mcp` `/permissions`. Riêng CORE của bundle nằm ở đúng 1 path cố định
  `~/.gemini/antigravity-cli/tdq`, nên đường dẫn trong hook/skill là absolute, không có biến.
- Log service cho cả 2 hook: 1 dòng stderr có timestamp nêu case đã khớp, tắt bằng `TDQ_LOG=0`.
- Dọn 3 chỗ trong `build_portable.py` còn mô tả Antigravity là "harness chỉ đọc markdown".

## Kết quả kiểm
11 hạng mục QC (7 DoD + 4 cố định) PASS. Test của việc này: 15 (PreToolUse) + 10 (Stop) + 11
(bundle) xanh; vùng `Chạm:` 248 passed. `--only claude` / `--only codex` vẫn exit 0 và 2 cây
bundle cũ không đổi 1 byte (so sha).

## Cần biết
- **Chưa test end-to-end trên agy thật** (spec §5, rủi ro 4). Toàn bộ test là mô phỏng schema
  JSON; schema `PreToolUse`/`Stop` của agy chưa được tài liệu công khai chốt, nên hook thử 4
  dạng field-path và luôn fail-open khi không parse được. README có checklist smoke-test tay.
- `pytest tests/ -q` còn **5 lỗi có từ trước request này**, đã chứng minh bằng worktree sạch tại
  HEAD hoặc `git diff` rỗng trên file bị flag: `test_bench` (worktree cũ còn sót),
  `test_luat_skill`, `test_skill_router`, `test_doc_lint` (2 câu > 40 từ ở `tdq-build/SKILL.md`
  và `tdq-lsp-setup/`), `test_rules_library` (sửa đổi chưa commit sẵn có ở
  `rules/index.md` thêm dòng `bash.md` chưa có file rule). Nợ kỹ thuật của repo, ngoài phạm vi.
- Đã nới 1 bất biến test: `test_compliance_protocol` cấm hook tự dựng JSON `deny`. Luật đó là
  của harness Claude Code; deny cứng là mục tiêu của bundle agy — nới đúng 2 file agy-only,
  kèm comment. Không commit nào được tạo tự động trong lượt này.

## Thời gian

| Phase | Wall clock | Model time | Times entered |
|---|---|---|---|
| idle | 4s | 0s | 1 |
| analyze | 14 min | 14 min | 1 |
| spec | 7 min | 7 min | 1 |
| diagram | 5 min | 5 min | 1 |
| plan | 22 min | 13 min | 1 |
| implement | 1h 47min | 44 min | 1 |
| qc | 2 min | 2 min | 1 |
| report | 4s | 3s | 1 |
| **Total** | **2h 38min** | **1h 24min** | |
