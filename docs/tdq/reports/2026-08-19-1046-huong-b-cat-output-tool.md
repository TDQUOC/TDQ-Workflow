# REPORT — Hướng B: cắt output tool (`2026-08-19-1046-huong-b-cat-output-tool` · lane full · mode main · 20/20 task tick đủ)

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

**Đã làm:** P1 `token_audit.py` đếm bằng tokenizer thật (dùng chung bộ đếm với `skill_tokens.py`, cache theo nội dung), đếm ảnh theo patch 28×28 px, thêm bảng phân rã n/trung vị/p90/p99/lớn nhất + tỉ lệ `Read` có `offset|limit` và tỉ lệ đọc lại · P2 `context-budget.md` thêm mục phân biệt đọc lại vì LUẬT / vì QUÊN và luật trần output cho tool MCP, §10 SKILL.md trỏ sang · P3 hook `bash_gate.py` thêm nhắc `TDQ:OUTPUT` (nhắc, không chặn) · P4 `~/.claude/settings.json` thêm `MAX_MCP_OUTPUT_TOKENS=25000` · P5 sinh lại 2 bản portable + đính chính đề án · P6 log service giữ nguyên hợp đồng.
**Kết quả:** không tuyên bố mức tiết kiệm — luật mới chỉ ăn vào PHIÊN MỚI. Cái đo được là thước đo: cùng 5 phiên, tổng carry-cost 2.609.256.040 (ký tự/4) → 3.844.300.565 (token thật, +47,3%) · cụm MCP 18,4% → **1,9%** · `Read file` 35,2% → 45,7% · thời gian chạy 30,6s nguội / 5,2s nóng (trần 60s).
**Defect tự phát hiện giữa build (T1.6, thêm sau khi duyệt plan):** khối `image` bị tính bằng độ dài chuỗi base64 — ảnh 960×1605 px tốn 2.030 token thật nhưng bị đếm 378.014, **sai ~186 lần**. Cái sai đó chỉ ra đúng một kết luận "cắt năng lực chụp màn hình đi", tức cắt nhầm. Đã sửa + khoá bằng test.
**Kiểm:** `pytest tests -q` → 1025 passed; đỏ duy nhất `test_skill_router` (25 subtest skill `figma-*`) đã đỏ trước request, chứng minh bằng `git stash --include-untracked` · `doc_lint` exit 0 trên 6 file · QC PASS 16/16 (12 DoD + F1–F4), 0 vòng fix.
**Đầu ra:** `scripts/token_audit.py` · `scripts/skill_tokens.py` · `hooks/scripts/bash_gate.py` · `skills/tdq-conventions/references/context-budget.md` · `docs/tdq/audit/de-an-toi-uu-context.md` (mục đính chính) · QC: `docs/tdq/qc/2026-08-19-1046-huong-b-cat-output-tool.md`.
**Backup + cách đảo ngược cấu hình:** bản nguyên byte của settings ở `~/.claude/settings-backup-2026-08-19-huong-b.json` (md5 `df7ed9ce…`). Đảo ngược: `cp ~/.claude/settings-backup-2026-08-19-huong-b.json ~/.claude/settings.json`, hoặc xoá đúng khoá `env.MAX_MCP_OUTPUT_TOKENS`.
**Đổi cách làm khi thi hành (tự quyết):** plan T4.1 định chép nguyên byte settings vào `docs/tdq/audit/`, nhưng file đó chứa API key thật — chép vào repo là commit thẳng credential lên git. Bản trong repo giữ đủ tên khoá, che giá trị mọi khoá có KEY/TOKEN/SECRET/PASSWORD; bản nguyên byte để ngoài repo.
**Giới hạn — phần CHƯA kiểm chứng được:** (1) luật mới + hook `TDQ:OUTPUT` chỉ tác động lên phiên mới, muốn biết có ăn hay không thì chạy `token_audit.py --sessions 5` sau vài phiên rồi so tỉ lệ đọc lại và token/lần của `Read`; (2) `MAX_MCP_OUTPUT_TOKENS` có hiệu lực thật hay không cũng phải kiểm ở phiên mới — nguồn hiện là deepwiki + issue #7732, chưa phải tài liệu chính thức; (3) đo trên 1 project của 1 người dùng, chưa phải mẫu chung.
**Nợ kỹ thuật đã báo, không sửa (ngoài phạm vi spec):** `tdq_team.py doc_plan()` mất `Chạm:`/`Cần:` khi mô tả task xuống dòng · đường dẫn `portable/AGENTS.md` cũ trong `bang-lech.md`.
**Git:** chưa commit. Không có commit gỡ chặn nào trong build.

## Thời gian

| Phase | Treo tường | Model chạy | Số lần vào |
|---|---|---|---|
| idle | 0 giây | 0 giây | 1 |
| analyze | 3 giờ 24 phút | 6 phút | 1 |
| spec | 5 phút | 2 phút | 1 |
| plan | 4 phút | 4 phút | 1 |
| implement | 17 phút | 17 phút | 1 |
| qc | 16 phút | 16 phút | 1 |
| report | 6 giây | 0 giây | 1 |
| **Tổng** | **4 giờ 07 phút** | **49 phút** | |
