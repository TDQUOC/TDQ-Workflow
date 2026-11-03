# REPORT — Phối hợp công cụ tự động có kiểm chứng (`2026-11-03-1420-phoi-hop-cong-cu` · lane full · mode subagent · 19/19 task)

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

**Đã làm:** Luật soul/routing có vòng hoàn tất công cụ (inventory thực → bước nội bộ → preflight → thực thi → kiểm đầu ra, handoff và delivery không lặp) · writer instruction validate marker/UTF-8, backup, atomic replace, rollback có đường backup, no-op không ghi · caller và hook không tiến version stamp khi writer lỗi · ACL Windows so theo semantics (owner/group/control/thứ tự ACE), giữ `AUTO_INHERITED` bằng request bit chỉ trên bản copy.
**Kết quả:** 3/3 lệch spec được duyệt · eval Q7 miễn theo lời user `WAIVED_USER` (không phải quality PASS) · apply user-level thật thành công với backup `C:\Users\admin\.claude\CLAUDE.md.bak.djwkvuw1`.
**Kiểm:** full suite nguồn cuối **4.126 passed, 12 skipped, 0 failures**, 4.138 ca/2.669 subtest, `details_complete=true` · ACL focused 51 passed/142 subtest · policy/setup/hook 109 passed/28 subtest · Pyright 0 lỗi · hai receipt live (đặt cả `TDQ_TOOL_RUNTIME_RECEIPT` và `TDQ_INSTRUCTION_RECEIPT`) **11 passed, 2 subtest** · QC đã đóng Q1–Q8, trong đó **Q7 là `WAIVED_USER`, không phải PASS**.
**Đầu ra:** `C:\Users\admin\.claude\CLAUDE.md` (managed block mới) · báo cáo `docs/tdq/reports/2026-11-03-1420-phoi-hop-cong-cu.md` + `.html` · receipt `docs/tdq/artifacts/2026-11-03-1420-phoi-hop-cong-cu/instruction-receipt.json`.
**Giới hạn:** eval hành vi `INCONCLUSIVE`/`unavailable_metrics`, trial dùng nguồn trước sửa rollback/ACL nên không chứng nhận nguồn cuối, không chứng minh browser/native hay tốc độ · smoke browser thủ công không có deadline toàn chuỗi 120 giây và chọn đích native bị `POLICY_DENIED` · Ruff chưa cài · **ACL adapter chỉ đọc `OWNER|GROUP|DACL` (mask 7), không đọc/ghi/so SACL**: audit policy riêng của file đích không được bảo toàn qua replace, và thay đổi SACL không bị phát hiện; chưa sửa vì đọc SACL cần `SE_SECURITY_NAME` — **người dùng đã được giải thích và chọn giữ nguyên (phương án 1)** sau khi request kết thúc · Master kiến trúc còn stale · POSIX chưa chạy trên máy Windows này.
**Lệch spec chờ duyệt:** không còn — #1 (Q7 eval), #2 (Q6 smoke 120s), #3 (Q7 Ruff) đều đã duyệt bằng lời người dùng «auto duyệt lệch hãy chạy end to end đến hết plan đi».
**Git:** chưa commit, chưa push; **chưa bump version/phát hành**, HEAD vẫn `24a8c15`; branch `feature/phoi-hop-cong-cu`. Lưu ý: `docs/tdq/.tdq-phat-hanh.json` chỉ đổi mốc `cap_nhat` sang `2026-11-03T18:58:36`, `phien_ban` vẫn `0.88.0`; nguyên nhân đổi mốc chưa xác định trong phiên. Branch không có upstream nên không kiểm chứng được push từ máy này.

## Thời gian

| Phase | Wall clock | API request | Tool wait | Background job | Observed union | Unattributed | Times entered |
|---|---|---|---|---|---|---|---|
| idle | 1s | — [partial] | — [partial] | — [unavailable] | — [partial] | — [partial] | 1 |
| analyze | 38 min | 3 min [partial] | 25s [partial] | — [unavailable] | 3 min [partial] | 35 min [partial] | 1 |
| spec | 8 min | — [partial] | — [partial] | — [unavailable] | — [partial] | — [partial] | 1 |
| plan | 1h 33min | 48 min [partial] | 7 min [partial] | — [unavailable] | 52 min [partial] | 41 min [partial] | 1 |
| qc | 1h 55min | 7 min [partial] | 33s [partial] | — [unavailable] | 7 min [partial] | 1h 48min [partial] | 4 |
| implement | 51 min | 28 min [partial] | 5 min [partial] | — [unavailable] | 33 min [partial] | 17 min [partial] | 3 |
| report | 4s | — [partial] | — [partial] | — [unavailable] | — [partial] | — [partial] | 1 |
| Total | 5h 05min | 1h 24min [partial] | 13 min [partial] | — [unavailable] | 1h 35min [partial] | 3h 30min [partial] |  |

Model compute time is unavailable (`model_giay=null`). API includes network/provider latency; tool time is host wait. Observed metrics may overlap; unattributed time is not assumed user/model time. Bảng trên là nguyên văn `tdq_timing.py show`; dòng Total do công cụ tính từ dữ liệu chưa làm tròn nên lệch 2 phút ở cột API (86 phút khi cộng các dòng) và 9 phút ở cột Unattributed (201 phút khi cộng các dòng) — không sửa số, mọi ô đều `[partial]`.

## Thân PR (soạn sẵn)

**Tóm tắt:** Bổ sung luật tự chủ phối hợp công cụ có kiểm chứng vào soul/routing và managed instruction; writer instruction an toàn theo byte/ACL; evaluator fail-closed trước khi chấp nhận bằng chứng.
**Trước/Sau:** Preview đã duyệt `docs/tdq/spec/2026-11-03-1420-phoi-hop-cong-cu-preview.html` là bản thiết kế; HTML nghiệm thu `docs/tdq/reports/2026-11-03-1420-phoi-hop-cong-cu.html` phản ánh kết quả thực tế.
**Đã kiểm:** `python scripts/tdq_test.py tron-bo` → 4.126 passed/12 skipped/0 failures (receipt `ebaab9fca3284d1e93a969a284b14665`) · `python -m pytest tests/test_claude_md_core.py tests/test_auto_update_setup.py -q` → 51 passed/142 subtest · `pyright scripts/tdq_setup.py tests/test_claude_md_core.py` → 0 errors · `TDQ_TOOL_RUNTIME_RECEIPT=<runtime-receipt.json> TDQ_INSTRUCTION_RECEIPT=<instruction-receipt.json> python -m pytest tests/test_tool_composition.py -q` → 11 passed/2 subtest · `python scripts/tdq_state.py eval-waive --reason "<lý do>" --by "auto duyệt lệch hãy chạy end to end đến hết plan đi" --scope "Q7 behavioral eval"` → `WAIVED_USER`.
**Rủi ro hồi quy:** writer chạm mọi luồng ghim instruction (setup CLI, auto-update, SessionStart hook); tests `test_claude_md_core.py`, `test_auto_update_setup.py`, `test_context_hooks.py` giữ byte ngoài block, backup, stamp và báo lỗi hook. Evaluator đổi hành vi fail-closed; `test_tdq_eval_hosts.py`, `test_tdq_skill_eval.py`, `test_eval_contracts_e2e.py` giữ. **Rủi ro còn mở:** SACL của file instruction không được đọc/ghi/so, nên audit policy riêng (nếu có) không được bảo toàn khi replace; chưa sửa vì cần `SE_SECURITY_NAME`.
<!-- tdq-archify-binding:start -->
<!-- manifest: 2026-11-03-1420-phoi-hop-cong-cu.manifest.json -->
<!-- manifest_digest: 64c176f8b6ff1e4676c1f4b4df858395998d341c79a1a84f844a23378d768d83 -->
<!-- tdq-archify-binding:end -->