# QC — Phối hợp công cụ tự động có kiểm chứng
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md
Ngày: 2026-11-03 · Plan: ../plan/2026-11-03-1420-phoi-hop-cong-cu.md · Vòng: 4 và ACL được duyệt · Trạng thái: hồi quy và apply PASS; eval INCONCLUSIVE

| # | Hạng mục | Bằng chứng hiện có | Trạng thái |
|---|---|---|---|
| Q1 | Soul và luật thường trực | Policy coverage có internal steps/discovery/verify/permission; focused xanh | PASS contract; eval hành vi miễn `WAIVED_USER` |
| Q2 | Routing/handoff | Chrome MCP upload fixture; native Save As; SHA-256 tệp cuối khớp | PASS smoke local, không suy rộng Gemini |
| Q3 | Thiếu tool | Bỏ luật tự cài LSP, thêm official-source proposal/approval; policy test xanh | PASS contract; eval hành vi miễn |
| Q4 | Instruction | Rollback có backup path; ACL semantic fail-closed; fixture, full suite sau ACL và apply thật đạt | PASS |
| Q5 | Stamp và hook | 66 passed, 63 subtests: updater retry, stamp failure và hook main báo lỗi redacted | PASS |
| Q6 | Delivery/download | File 96 byte khớp hash; không lặp upload; destination type bị từ chối không bypass | Lệch #2 chờ duyệt |
| Q7 | Regression/eval | 32/32 CLI trials completed, observed model cc4; outcome unavailable; report offline INCONCLUSIVE | Hồi quy PASS; eval `WAIVED_USER` (không phải PASS) |
| Q8 | Apply user-level | Writer hẹp đã ghi policy; backup, bytes ngoài block, ACL/mode/settings giữ nguyên, lượt hai no-op | PASS apply |
| QC-F1 | Full suite | Sau ACL: 4138 ca, 12 skipped, 0 failures, details_complete=true; receipt ebaab9fca3284d1e93a969a284b14665 | PASS nguồn sau ACL |
| QC-F2 | Vùng chạm | Release allowlist đã sửa và suite trước ACL đạt; root ACL 51 tests/142 subtests; policy/setup/hook 109 tests/28 subtests, 2 live skips | PASS các vùng đã chạy |
| QC-F3 | Kiến trúc | Không schema/phase/hook mới; không dependency/permission/host writer mới | CHỜ review cuối |
| QC-F4 | Clean code | Ruff không cài; compileall PASS; nguồn diff --check PASS; 29 hàm evaluator kiểm AST max 50/10/15 | PASS kiểm cấu trúc; Ruff chưa kiểm |

## Bằng chứng

- T0.1 red: 6 failed/21 passed; sau sửa và bổ sung: 45 passed. Parser trace rỗng trả `incomplete/missing_terminal_response`, không PASS.
- T1.2 red policy: 8 failures gồm 2 subtest; sau sửa: 74 passed, 2 live-receipt skip, 28 subtests. Test chuỗi chỉ là coverage luật, không chứng nhận hiệu quả model.
- T2.1 red: 14 failed/16 passed; green 28 passed/28 subtests, gồm protected Windows DACL fixture.
- T2.2 red: 2 assertion stamp và 1 assertion hook main; 2 lần import fixture lỗi không tính RED. Green 66 passed/63 subtests.
- T3.1 root sau tích hợp: 34 passed, 2 skipped, 380 subtests; 329 neo audit và 62 hash được đối chiếu bởi agent.
- Hồi quy evaluator rộng: 3 failed/176 passed. Ca cũ dùng corpus ID-only và trace không có terminal, đang sửa fixture theo fail-closed.
- Runtime: `TDQ_TOOL_RUNTIME_RECEIPT=docs/tdq/artifacts/2026-11-03-1420-phoi-hop-cong-cu/runtime-receipt.json python -m pytest tests/test_tool_composition.py -q -k runtime`: 3 passed, 1 skipped, 7 deselected. Skip là receipt apply user-level chưa có.
- Chrome page 9 trong isolated context `tdq-tool-routing-fixture`; upload_file chọn fixture.txt 96 byte; Save As semantic InvokePattern.Invoke báo delivered_unverified rồi file đọc lại khớp SHA-256 `b95b954dca6a42dc1901e97f5f847b2d67daad7ae2bc8e95140838ed621caf7f`.
- Native `type` bị POLICY_DENIED/not_delivered; không bật headed hoặc sửa policy. Dùng filename và Downloads đã kiểm, Save thành công. Không screenshot native chứa dữ liệu cá nhân vào artifacts.
- CLI native preflight cô lập: READY, Claude Code 2.1.317, 0 paid model calls. Một baseline probe thật 4.605s, response/model cc4 xác minh; sau đó 32 A/B trials đầy đủ, không tool thật, chưa chấm quality.
- Các trial nằm trong artifacts/trials; `run_summary.json` ghi 32/32; response-only rubric độc lập không thay trial gốc hay tự chứng nhận gate. Rubric: baseline 6/16, candidate 14/16; forbidden recommendations 0/32. Candidate trượt 2 ca uncertain-delivery vì dừng an toàn nhưng không nêu bounded progress-based retry; không tuning theo holdout.
- QC1.1/QC1.2 sau tích hợp: 150 passed, 35 subtests; sửa scorer identity, rollback backup, staged ACL, E2E terminal/corpus và release allowlist đúng ultracode.md. Không tăng cap release.
- Chrome Archify E2E rerun 2 passed/2 subtests trong 14.23s; Codex timeout fixture rerun 2 passed trong 4.25s. Không chứng nhận full suite từ các rerun riêng.
- Token budget: 8 passed. Compileall và source diff --check PASS. LSP tự đổi pyrightconfig scope scripts đã khôi phục từ backup đối chiếu HEAD; không giữ đổi cấu hình ngoài phạm vi.

## Lệch spec chờ duyệt

- #1/Q7: bằng chứng response-only đã chạy thật, chưa có scorer chứng nhận theo identity khóa; giữ outcome unavailable, không waive.
- #2/Q6: smoke thủ công không có deadline toàn chuỗi 120 giây; chọn đích native bị chặn. Báo giới hạn, không đổi policy. Runtime hook/CLI fixture 120s riêng đã đạt, không đổi tên bằng chứng browser.
- #3/Q7: Ruff không có trên PATH/module, chưa cài; compileall/tests/AST không thay thế lint. LSP chưa chứng minh đầy đủ theo module.

## Kiểm bổ sung trước lần cuối

- Runtime hook process thật trong HOME/project tạm, deadline 120s: PASS, có NEXT và Rule, không sửa user config. Receipt: artifacts/hook-runtime-receipt.json.
- Smoke public writer trong child process/HOME tạm, deadline 120s: PASS, backup đúng byte, giữ CRLF phần riêng, lượt hai no-op. Receipt: artifacts/writer-smoke-receipt.json.
- QC độc lập vòng cuối: Q4 30 tests/31 subtests PASS; Q5 61 tests/18 subtests PASS; evaluator 89 tests/4 subtests xanh nhưng phát hiện scorer globals identity và UTF-8/schema trace lỗi. QC vòng 3 đã sửa: 149 passed/4 subtests; chặn UTF-8/schema hỏng và globals/builtin shadow, khóa cả source+bytecode+rubric. Full-suite lần hai đã dừng, không đánh PASS hoặc bỏ lỗi. Xác minh độc lập đúng hai defect hoàn tất: 117 passed/4 subtests; hai lỗi không còn tái hiện. Full-suite cuối vẫn FAIL 6 ca bên dưới.

## Full-suite nguồn cuối

Receipt: `docs/tdq/cache/test-runs/d62619eb6441fbab/68fe29e71e5d468aa341e0278c33a06e/result.json`. 4126 tests, 12 skipped, 6 failures, details_complete=true; không có source drift.

- Hai ca `test_archify_e2e.py`: `viewer/chrome-startup-timeout`, Chrome không hoàn tất DevTools handshake.
- Ba ca `test_codex_cli.py`: `test_treo_thi_qua_han_va_van_don_home`, `test_version_timeout_owns_descendants_without_creating_home`, `test_windows_cmd_descendant_timeout_is_bounded`; nhận `PermissionError` thay kết quả timeout mong đợi. Chưa xác định nguyên nhân gốc; kết quả riêng trước đó xanh không phủ nhận FAIL trong full suite.
- `test_kiem_no_marker.py::MarkerLedgerTest::test_no_argument_scans_this_repo_and_is_clean`: marker mới tại `scripts/tdq_skill_eval.py:280` không được checker nhận diện upgrade path. Đây là lỗi guard của thay đổi hiện tại, không gọi là môi trường.

Đã dừng sau ba vòng fix. User sau đó duyệt «“duyệt sửa QC tiếp», cho phép một vòng bổ sung; đã resume qua CLI. Không bỏ test, nâng timeout hoặc waive.

## Vòng bổ sung đã duyệt

- QC4.1: marker sai dấu phân cách `;` thay vì `,` theo `has_upgrade_path()`. Sửa đúng một dấu, không đổi runtime. Test đỏ trước sửa; sau sửa `python -m pytest tests/test_kiem_no_marker.py -q`: 15 passed.
- QC4.2: tái hiện nested IsolatedJob: WinError32 ở `1.err` khi TemporaryDirectory.cleanup sau timeout; handle nhả trễ 11–12ms. Retry chỉ WinError32 trong ngân sách cleanup 5s còn lại; lỗi dai dẳng vẫn ném và giữ chẩn đoán. Root 65 passed/1 POSIX skipped; reproducer nested 3 passed, hết lỗi cleanup.
- QC4.3: đối chứng xác định USERPROFILE giả làm Chrome không nhận DevTools pipe; các biến HOME/TEMP/APPDATA riêng không gây lỗi. All-private bỏ riêng USERPROFILE đạt. Đã sửa env chỉ của subprocess E2E Windows trong runner, vẫn giữ HOME/config roots và Chrome profile tạm; không đổi sandbox/timeout/quyền. Root chạy chung Chrome+Codex bên trong IsolatedJob: 43 passed/6 subtests trong 32.80s, cleanup verified. Vùng process ownership: 255 tests PASS, details_complete=true. Full-suite vòng bổ sung đang chạy trên nguồn cố định.

## Sửa ACL đã duyệt

- ACL1.1 đã tích hợp không commit; `tdq_team.py check ACL1.1` đạt, root `python -m pytest tests/test_claude_md_core.py tests/test_auto_update_setup.py -q`: 51 passed, 142 subtests. Patch đầy đủ đã giữ, worktree riêng đã dọn.
- Comparator so owner/group/control/revision/ordered ACE; chỉ bỏ offsets/padding. Native xác nhận SetFileSecurityW làm 0x8404 thành 0x8004; thêm AUTO_INHERIT_REQ vào bản copy của lời gọi giữ readback 0x8404. Protected/unprotected và khác thư mục cha đều đạt.
- Smoke child process deadline 120s dùng ACL đọc từ instruction thật trên file tạm: PASS, giữ CRLF/ACL, một backup, lượt hai no-op; không ghi file thật. Hai lỗi quoting và một lỗi console encoding của lệnh bao đã sửa, không tính là lỗi writer hoặc evidence PASS.
- Policy/setup/hook bổ sung: 109 passed, 2 live-receipt skipped, 28 subtests. Runtime receipt cũ: 3 passed, 1 instruction-receipt skipped, 7 deselected; không biến smoke cũ thành timed browser PASS.
- Compileall và diff --check đạt. LSP root tdq_setup.py không diagnostics; `pyright scripts/tdq_setup.py tests/test_claude_md_core.py` tại root: 0 errors/0 warnings/0 informations. Module `python -m pyright` không có nhưng CLI đã cài dùng được; không cài mới. Full suite sau ACL đang chạy; 4131 tests PASS phía trên chỉ chứng nhận nguồn trước ACL.
- Báo cáo offline `eval-offline-final.md` từ 32 trial gốc: cell claude:cc4, 16 cặp, INCONCLUSIVE/unavailable_metrics. Exit 0 chỉ là xuất report thành công, không phải quality PASS; không đổi trial hoặc chứng nhận nguồn ACL mới.

## Kiểm độc lập báo cáo cuối

Hai agent đọc-only đối chiếu báo cáo với bằng chứng gốc và soi lại bản sửa ACL. Xác nhận: 4.138 ca/4.126 pass/12 skip/0 fail, receipt khớp nguồn, backup `CLAUDE.md.bak.djwkvuw1` khớp `before_sha256`, target khớp `after_sha256`, HTML manifest digest khớp, HEAD/branch đúng.

Lỗi trong bản báo cáo đầu đã sửa: (1) ghi `QC Q1–Q8 PASS` → nay `Q1–Q8 đóng, Q7 WAIVED_USER`; (2) lệnh receipt chỉ đặt một biến môi trường → nay ghi đủ hai receipt và chạy lại đạt 11 passed/2 subtest; (3) lệnh `eval-waive` thiếu `--reason/--by/--scope` → nay ghi đúng; (4) tổng thời gian lệch do làm tròn → ghi rõ không sửa số; (5) `chưa release` → nêu đúng `.tdq-phat-hanh.json` chỉ đổi mốc, version vẫn 0.88.0, chưa xác định nguyên nhân; (6) push không kiểm chứng được vì branch không có upstream.

Phát hiện mới, chưa sửa: `GetFileSecurityW(..., 7, ...)` chỉ đọc `OWNER|GROUP|DACL`, không có SACL; `SetFileSecurityW` cũng dùng mask 7. Hệ quả: audit policy riêng của file đích không được bảo toàn qua `os.replace`, và khác biệt SACL giữa hai descriptor không bị phát hiện. Đã ghi vào giới hạn/rủi ro báo cáo. Người dùng được giải thích ba phương án và chọn phương án 1 — giữ nguyên, không mở rộng đọc SACL vì cần `SE_SECURITY_NAME`.


## Kết luận

Hồi quy sau ACL PASS: 4138 ca tổng cộng gồm 4126 passed/12 skipped, 2669 subtests; details_complete=true. Writer hẹp áp dụng user-level thành công; receipt kiểm backup `C:/Users/admin/.claude/CLAUDE.md.bak.djwkvuw1`, bytes ngoài block/ACL/mode/settings giữ nguyên, lượt hai no-op. Hai receipt runtime/instruction: 11 passed, 2 subtests.

Chưa có quality PASS cho eval hành vi: report offline vẫn INCONCLUSIVE/unavailable_metrics. User nhắn «auto duyệt lệch hãy chạy end to end đến hết plan đi»; ba lệch đã ghi `duyet` và miễn eval Q7 ghi `WAIVED_USER`, không đổi trial/record. Master kiến trúc còn stale. Không commit/push/release.
