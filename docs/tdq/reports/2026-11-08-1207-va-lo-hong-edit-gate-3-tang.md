# REPORT — Vá lỗ hổng gate 3 tầng (`2026-11-08-1207-va-lo-hong-edit-gate-3-tang` · lane full · mode main)

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

**Trước request (trạng thái/flow):** Ở play3clone, user nhắn `1a` khi chưa có cổng chờ duyệt. Agent tự chạy `approve spec`, `approve plan` rồi sửa `server/index.js` trong cùng một lượt. Hệ thống lọt vì: `edit_gate` chỉ nhắc (allow) khi còn cổng chờ; `bash_gate` bỏ qua khi không có dòng `signal`, và có lệch cũng chỉ nhắc; `quick-lane.md` bước 2 và `PHASE_TABLE["quick_analyze"]` bảo `set phase=implement` trước cổng duyệt quick. Lỗi có từ bản 0.3.0, không phải do đợt tối ưu runtime (`hooks/` không đổi từ `540004ff`).

**Sau request (trạng thái/flow):**
- `edit_gate.py`: còn cổng chờ → **deny** sửa file trong project ngoài `docs/`. File `docs/**` và file ngoài project vẫn như cũ.
- `bash_gate.py`: `approve X` / `set phase=plan|implement` bị **deny** nếu lượt này hook prompt đã chạy (`turn_start`) mà không có `signal` duyệt khớp cổng X. Một prompt mở đúng một cổng. Host không có hook prompt vẫn chỉ nhắc. `set phase=implement` khi plan đã duyệt (vòng fix QC) không bị chặn.
- `quick_analyze`: lệnh kế là `approve quick`; `quick-lane.md` bước 2 giữ `phase=analyze`.

**Đã test gì:** test đỏ→xanh cho từng tầng (ca play3clone, một-prompt-một-cổng, host thiếu hook, vòng fix QC, docs không bị chặn); vùng chạm hook 274 test, bảng phase/quick 59 test; full fresh `tron-bo --workers 1 --fresh --reuse off`; `doc_lint` các tài liệu sửa.

**Kết quả test:** full fresh trước bump **PASS: 4202 case gồm 4192 passed, 10 skipped, 926 s**, `details_complete=True` (`docs/tdq/cache/test-runs/3df348232a8e68c3/3ad8dab13edb4d1c91efcf5f18af95b3/result.json`). QC Q1–Q5 PASS (`docs/tdq/qc/2026-11-08-1207-va-lo-hong-edit-gate-3-tang.md`). Vòng fix 1 sửa 4 test khóa hành vi cũ (`test_e2e_chain` ×2, `test_doc_index`, `test_luat_skill`).

**Đầu ra:** `hooks/scripts/edit_gate.py`, `hooks/scripts/bash_gate.py`, `scripts/tdq_state.py`, `skills/tdq-intake/references/quick-lane.md`, `skills/tdq-conventions/references/phases.md`, `docs/tdq/audit/luat-hien-co.md`, `docs/tdq/token-budget.json`; test `test_edit_gate`, `test_bash_gate`, `test_compliance_protocol`, `test_phase_table`, `test_e2e_chain`.

**Giới hạn:**
- Đã bump hai manifest lên 0.95.0; chưa cập nhật plugin cài trên máy/play3clone. Phiên đang dùng cache 0.94.0 không tự nhận bản vá chỉ vì repository đã push.
- Main agent ghi file qua shell (`node -e`, `Set-Content`) không đi qua `edit_gate` — ghi `ponytail:` trong code.
- `looks_like_approval` hiểu sai câu duyệt thật sẽ bị chặn; user gõ lại câu mẫu (`duyệt spec`).
- 16/329 neo luật lệch dòng ở `skills/tdq-build/SKILL.md` có sẵn từ HEAD (4,9%), chưa xử lý.

**Lệch spec chờ duyệt:** Không có.

**Git / phát hành:** Bản vá commit `d6116f2c`, merge vào `dev` tại `093a2e0c`, bump 0.95.0 tại `9bde4e13`, đính chính số test tại `b3480d0c`. Đã push `dev` và snapshot sạch `main@6f03655c`; tag `v0.95.0` trỏ đúng snapshot này. [GitHub Release 0.95.0](https://github.com/TDQUOC/TDQ-Workflow/releases/tag/v0.95.0) đã xuất bản, không draft/prerelease, có ZIP 175 file và `SHA256SUMS.txt`. Digest ZIP do GitHub trả về khớp checksum local `8311df3d953136b17db9fda0b20ebb160b7f6cecb56d8ceca74f746d06c9e4a4`. Sau bump, kiểm đóng gói/host/version đạt **225 passed, 55 subtests passed (48,43 s)**; không chạy lại full suite cho riêng thay đổi version. [Bằng chứng phát hành](../artifacts/2026-11-08-1207-va-lo-hong-edit-gate-3-tang/release-0.95.0.json).

## Thời gian

Request `2026-11-08-1207-va-lo-hong-edit-gate-3-tang` · lane full · opened at 2026-11-08T12:07:32+07:00

| Phase | Wall clock | API request | Tool wait | Background job | Observed union | Unattributed | Times entered |
|---|---|---|---|---|---|---|---|
| idle | 14s | 12s [partial] | 2s [partial] | — [unavailable] | 14s [partial] | 0s [partial] | 1 |
| analyze | 23s | 13s [partial] | 10s [partial] | — [unavailable] | 23s [partial] | 0s [partial] | 1 |
| spec | 12 min | 6 min [partial] | 15s [partial] | — [unavailable] | 7 min [partial] | 5 min [partial] | 1 |
| plan | 19 min | 7 min [partial] | 3 min [partial] | — [unavailable] | 11 min [partial] | 8 min [partial] | 1 |
| qc | 33 min | 3 min [partial] | 25s [partial] | — [unavailable] | 4 min [partial] | 29 min [partial] | 2 |
| implement | 2 min | 1 min [partial] | 24s [partial] | — [unavailable] | 2 min [partial] | 0s [partial] | 1 |
| report | 14s | 8s [partial] | 4s [partial] | — [unavailable] | 13s [partial] | 1s [partial] | 1 |
| Total | 1h 05min | 19 min [partial] | 5 min [partial] | — [unavailable] | 24 min [partial] | 42 min [partial] |  |

Model compute time is unavailable (`model_giay=null`). Phần lớn thời gian `qc` là 2 lần full fresh (~15 phút mỗi lần).
<!-- tdq-archify-binding:start -->
<!-- manifest: 2026-11-08-1207-va-lo-hong-edit-gate-3-tang.manifest.json -->
<!-- manifest_digest: 145721e86a309318eddda92d44da26012d231f3f6a9f479bf428584c16ca11d0 -->
<!-- tdq-archify-binding:end -->