# PLAN — Phối hợp công cụ tự động có kiểm chứng
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md
Ngày: 2026-11-03 · Spec: ../spec/2026-11-03-1420-phoi-hop-cong-cu.md (1.0, ĐÃ DUYỆT) · Lane: full
Mode thực thi: subagent — mô phỏng với hệ số agent 1.5: main 18.3 phút, đội 14.3 phút; Winner: đội, chênh 4.0 phút (ĐỀ XUẤT, user chốt tại gate mode). Đây là mô hình chi phí, không phải thời gian thực đã đo của request.
Trạng thái plan: HOÀN THÀNH — 19/19 task và Q1–Q8 tick; Q7 là miễn eval `WAIVED_USER` theo lời user «auto duyệt lệch hãy chạy end to end đến hết plan đi», không phải quality PASS

## Quy tắc thi hành

- Chỉ làm O1–O5/Q1–Q8 đã duyệt. Task đỏ → code → xanh → tick ngay; không tick trước bằng chứng.
- Lệnh state phục vụ fixture phải chạy trên thư mục tạm, không dùng state request thật làm mẫu thử.
- Không thêm state, phase, hook, dependency, planner engine, permission bypass hoặc writer cho host khác.
- User chỉ cho tự phục hồi tool đã cài. Công cụ thiếu được research và đề xuất user-level; chờ duyệt trước cài.
- Không gửi/upload dữ liệu thật lên Gemini/Zalo để thử. Không commit, push hoặc release khi chưa được yêu cầu.
- Workflow phân tích/QC chỉ đọc, không state/Git writer; thiếu kết quả phải ghi incomplete, không giả PASS.

## Thiết kế Trước vs Sau

| Vùng | Trước | Sau |
|---|---|---|
| Routing | Plugin tĩnh, chuyển tool rời rạc | Inventory thực, bước nội bộ, handoff có identity và kiểm kết quả |
| Thiếu tool | Hướng dẫn rời rạc | Research nguồn chính thức, đề xuất user-level, chờ duyệt |
| Instruction | Ghi trực tiếp, marker lỗi thiếu kiểm | Backup, kiểm marker/UTF-8, atomic replace và no-op |
| Update | Lỗi writer có thể bị che bởi stamp | Lỗi không báo thành công, không tiến stamp; retry lần sau |

Preview đã duyệt: `docs/tdq/spec/2026-11-03-1420-phoi-hop-cong-cu-preview.html` cùng manifest. Kiểm binding trước code; giữ snapshot phê duyệt, không rebind thiết kế đã duyệt để che thay đổi. Task T1.2 khớp view task-sau; T2.1/T2.2 khớp view setup-sau.

## Tiền điều kiện evaluator — đã duyệt bổ sung

User duyệt nguyên văn «duyệt sửa evaluator» ngày 2026-11-03. Mở rộng O4 để sửa evaluator hiện có; không bỏ O1–O5, không thêm framework, không waive eval. Giữ snapshot spec/preview đã duyệt cùng bổ sung này.

- [x] **T0.1** (e25m) Sửa evaluator fail-closed, gắn case/model/A-B snapshot và chấm kết quả thật — Test: `python -m pytest tests/test_tdq_eval_hosts.py tests/test_tdq_skill_eval.py -q`
  - Chạm: `scripts/tdq_eval_hosts.py`, `scripts/tdq_skill_eval.py`, `tests/test_tdq_eval_hosts.py`, `tests/test_tdq_skill_eval.py`
  - Ra: trace rỗng/lỗi/thiếu terminal không được PASS; CLI dùng prompt/model/source đúng; corpus hash và source identity kiểm trước run; outcome thiếu oracle ghi unavailable, không suy từ exit code; regression local không gọi model thật.
  - Quyền: agent làm trong worktree TDQ, không commit/push; leader kiểm rồi chuyển diff chưa commit về root, không dùng merge tạo commit khi chưa được user yêu cầu.

## P1 — Khóa phép đo và luật

- [x] **T1.1** (e8m) Lập và đăng ký eval-plan trước implement, khóa corpus và baseline — Test: `python scripts/tdq_skill_eval.py plan --plan docs/tdq/artifacts/2026-11-03-1420-phoi-hop-cong-cu/eval-plan.json`
  - Ra: eval-plan, corpus và snapshot nguồn baseline trong artifacts request; ghi `eval_plan_file` qua CLI sau plan approval, trước `set phase=implement`.
  - Bằng chứng T1.1: `eval-plan.json` valid=true, experiment `e93cb4c85fffa1a28b1ea1313b16749d61d5b8fc76885126726174abf757478b`; 8 ca corpus, baseline 7 file, chưa chạy live trial. CLI approve mode tự chuyển phase implement; đăng ký eval trước mọi sửa nguồn, không phải trước chuyển phase tự động.
  - BLOCKER trước T1.2: `eval-preflight.json` tái hiện trace rỗng được chấm passed=true/score=1.0. Runner chưa đáp ứng eval hành vi theo spec. Không dùng PASS giả hoặc waiver; cần duyệt mở rộng tiền điều kiện sửa evaluator ngoài vùng Chạm hiện tại. Spec preview đã kiểm current, cảnh báo stale thuộc Master.
  - Corpus: web một tool đủ; upload trực tiếp; picker native; download chưa hoàn tất; thiếu tool; kết nối hỏng; permission denied; delivery không rõ. Kiểm đúng route, không gửi trùng, không cài/đổi quyền trái phép; ghi hiệu quả chưa đo được thay vì giả PASS.
  - Dùng: `workflow-authoring`
  - Để: tổ chức đánh giá/read-only QC hữu hạn theo corpus đã khóa.
  - Ra: accounting expected/completed/errors và verdict theo trường hợp.
  - Kiểm: mọi trường hợp có bằng chứng, thiếu nhánh thì incomplete; không đặt token ceiling.
  - Không dùng cho: sửa state/Git, thực thi cài đặt hoặc thao tác dịch vụ thật.
- [x] **T1.2** (e15m) Red→green contract soul, routing và hướng dẫn thiếu tool — Test: `python -m pytest tests/test_tool_composition.py tests/test_soul_rules.py tests/test_claude_md_core.py -q`
  - Chạm: `skills/tdq-conventions/SKILL.md`, `skills/tdq-conventions/references/soul.md`, `skills/tdq-conventions/references/plugin-routing.md`, `skills/tdq-setup/SKILL.md`, `skills/tdq-setup/references/mcp-first-guide.md`, `scripts/tdq_setup.py`, `tests/test_tool_composition.py`, `tests/test_soul_rules.py`, `tests/test_claude_md_core.py`, `tests/test_tdq_setup.py`, `docs/claude-md-mau.md`
  - Cần: T1.1
  - T0.1 chạy song song vùng evaluator riêng; T1.2 dùng eval-plan/baseline đã khóa, không cần code runner mới để viết luật. T3.2 phải đợi cả T0.1 hoàn tất mới chạy eval.
  - Tiến độ T1.2: test policy đỏ thật (8 failures gồm 2 subtest); đã sửa thân conventions, soul và routing. Chưa tick xanh; guide và setup body đã sửa, đang đồng bộ managed block/mẫu và hồi quy. Đã bỏ tự cài LSP và setup toàn phần không kiểm quyền khỏi instruction. Policy tests đã xanh; mẫu đã đồng bộ. Hồi quy còn 2 fail: trần mẫu 11181>10000 byte (nâng 11500 theo soul, có lý do) và tên nền tảng/pre-flight trong guide (khôi phục nhãn chuẩn). Sau sửa: 40 passed, 28 subtests; hồi quy vùng chạm đang chạy. Ruff chưa cài (module và PATH đều thiếu), không tự cài. Receipt validator thêm vào test hiện có: missing/wrong/partial file bị từ chối; live receipt opt-in, không đọc user-home mặc định. Focused 26 passed/2 skipped (live chưa chạy)/28 subtests. Bậc 2 tái dùng rules/writer, bậc 3 hashlib/pathlib cho fixture; không tạo runtime orchestration engine.
  - Thay luật tự cài dependency LSP cũ trong managed block, không nối thêm luật mâu thuẫn; đồng bộ mẫu instruction theo test so nguyên văn.
  - Tạo `test_tool_composition.py` vì chưa có corpus chung cho handoff browser/native; bậc 2 tái dùng các luật/writer hiện có, không tạo framework. Chuẩn bị luôn fixture runtime và kiểm receipt user-level trước QC trọn bộ. Kiểm riêng behavior fixtures và policy coverage, không đánh đồng keyword test với hiệu quả model. Test receipt thiếu evidence phải fail ở lệnh nghiệm thu tường minh, không đọc user-home thật trong unit suite.

## P2 — Bảo toàn instruction và lifecycle

- [x] **T2.1** (e18m) Red→green writer validate/backup/atomic/no-op, giữ nội dung riêng và newline/BOM — Test: `python -m pytest tests/test_claude_md_core.py -q`
  - Chạm: `scripts/tdq_setup.py`, `tests/test_claude_md_core.py`
  - Cần: T1.2
  - Ca kiểm: file mới; một block; không đổi; marker thiếu/đảo/lặp; UTF-8 lỗi; CRLF/BOM/newline hỗn hợp; backup lỗi; ghi tạm/replace/readback lỗi. Ngoài block giữ nguyên byte; block mới dùng newline đầu tiên trong file (mặc định LF). No-op không tạo backup.
  - Không mặc định `os.replace` giữ ACL Windows: dùng API nền tảng qua stdlib để giữ/đối chiếu ACL, không thêm package; không chứng minh giữ được quyền thì dừng trước ghi. Readback lỗi sau replace phải khôi phục backup an toàn và kiểm lại; rollback lỗi báo rõ đường backup, không tiến stamp. Test failure injection cho cả nhánh rollback.
  - Fixture cô lập HOME/USERPROFILE và đường instruction; chặn subprocess, shim, Codex, Chrome và dọn process ngoài phạm vi.
- [x] **T2.2** (e12m) Red→green caller không tiến stamp khi instruction lỗi, hook không báo thành công giả — Test: `python -m pytest tests/test_auto_update_setup.py tests/test_context_hooks.py -q`
  - Chạm: `scripts/tdq_setup.py`, `hooks/scripts/session_start.py`, `tests/test_auto_update_setup.py`, `tests/test_context_hooks.py`
  - Cần: T2.1
  - Tiến độ: 2 test mới đỏ thật (writer lỗi vẫn tiến stamp, ghi stamp lỗi vẫn báo True). Đã bỏ catch nuốt lỗi instruction; 2 test stamp đã xanh; đang thêm kiểm hook entrypoint báo lỗi thật, không lộ nội dung exception. Test hook lần đầu lỗi import fixture (không tính RED), sửa load module trước xác nhận assertion đỏ. Đã xác nhận assertion thiếu `[TDQ:SETUP] Update failed` khi gọi main thật với lỗi updater; không tính hai lỗi import là RED.
  - Caller map đã xác minh bởi LSP/Graphify: CLI và setup bù gọi writer; SessionStart gọi auto-update. Chỉ sửa hook nếu trả kết quả hiện tại không đủ. Kiểm hook entrypoint thật với phụ thuộc mock, không chỉ helper.

## P3 — QC ultra và áp dụng

- [x] **T3.1** (e7m) Khóa index/budget/logging và mapping luật sau sửa — Test: `python -m pytest tests/test_luat_skill.py tests/test_reference_mot_tang.py tests/test_user_facing_block.py tests/test_tool_composition.py -q`
  - Chạm: `docs/tdq/audit/luat-hien-co.md`, `docs/tdq/token-budget.json`
  - Cần: T2.2
  - Log: tái dùng logger có timestamp và TDQ_LOG; tests ở T2.1/T2.2 phải kiểm log lỗi không lộ nội dung user. Cập nhật doc_index và token lock cho đúng file, không nén mất luật.
- [x] **T3.2** (e20m) Chạy QC trọn bộ, eval đối chứng và QC độc lập trên đúng diff — Test: `python scripts/tdq_test.py tron-bo`
  - Cần: T3.1, T0.1
  - Sau ACL đã duyệt: full-suite 4138 ca (4126 passed/12 skipped), 0 failures, details_complete=true; receipt ebaab9fca3284d1e93a969a284b14665. Kiểm độc lập khớp source_before/source_after với writer/test hiện tại và 8/8 evidence hash. Hồi quy hoàn tất; chứng nhận eval Q7 vẫn INCONCLUSIVE/unavailable_metrics, không tick toàn task. T3.4 đã áp dụng hẹp thành công; không coi đây là miễn gate report.
  - Ra: QC Q1–Q8, full receipt, eval records/report. Không dùng worktree HEAD rỗng để review diff chưa commit; reviewer nhận root/path chính xác. Nếu lỗi sửa rồi rerun vùng chạm và full suite sau fix cuối theo ngân sách QC.
- [x] **T3.3** (e10m) Smoke chuỗi browser/file/native trên fixture local, không dịch vụ thật — Test: `python -m pytest tests/test_tool_composition.py -q -k runtime`
  - Cần: T3.2
  - Dùng fixture đã tạo ở T1.2, không thêm mã sau full suite; nếu phải sửa thì quay lại QC theo ngân sách.
  - Dùng: `tdq-browser-test` (mcp)
  - Để: kiểm Chrome MCP pre-flight, upload/download dữ liệu mẫu và xác minh file; native dialog chỉ khi có và cần.
  - Ra: runtime receipt trong artifacts request, ảnh fixture không chứa dữ liệu cá nhân.
  - Kiểm: lệnh runtime chạy assertions fixture; receipt MCP ghi tool/kết quả thật riêng, không giả pytest thay kiểm browser. Nhánh native không khả dụng ghi UNSUPPORTED và xử lý theo spec.
  - Không dùng cho: Gmail/Zalo/Gemini thật, OAuth, clipboard cá nhân hoặc upload video của user.
- [x] **T3.4** (e8m) Áp dụng instruction thật trên Claude user-level sau fixture đạt và đối chiếu backup — Test: kiểm digest phần ngoài managed block trước/sau, no-op lượt hai và tồn tại backup bằng lệnh Python được ghi trong receipt.
  - Hoàn tất sau full suite nguồn ACL: 4138 ca/12 skipped/0 failures, details_complete=true. Apply writer hẹp đạt; backup `C:/Users/admin/.claude/CLAUDE.md.bak.djwkvuw1`, bytes ngoài block/owner/group/DACL/mode/settings giữ nguyên, lượt hai no-op. Receipt `artifacts/2026-11-03-1420-phoi-hop-cong-cu/instruction-receipt.json`; kiểm hai live receipt: 11 passed/2 subtests. Không miễn eval/report gate.
  - Cần: T3.3
  - Dùng: `tdq-setup`
  - Để: gọi riêng `ghim_huong_dan_tool()` qua Python với đường user-level đã xác nhận, không chạy setup CLI toàn phần vì có tác dụng phụ cài MCP/permission/host khác.
  - Ra: `~/.claude/CLAUDE.md` và backup; receipt chỉ lưu hash/trạng thái, không nội dung riêng.
  - Kiểm: file ngoài block nguyên vẹn, luật mới đúng và không đổi permission/host khác.
  - Không dùng cho: cài MCP/plugin mới hoặc nâng quyền admin.
  - Dùng: `update-config`
  - Để: kiểm ranh giới CLAUDE.md và permission của harness trước áp dụng user-level.
  - Ra: checklist không đổi settings.json/permission mode trong receipt.
  - Kiểm: so hash cấu hình liên quan trước/sau, không lưu secret vào log.
  - Không dùng cho: mở quyền hoặc tắt sandbox.

## P4 — Báo cáo nghiệm thu

- [x] **T4.1** (e5m) Báo cáo Markdown + HTML nghiệm thu và hỏi commit — Test: `python scripts/tdq_archify.py verify --document docs/tdq/reports/2026-11-03-1420-phoi-hop-cong-cu.md --manifest docs/tdq/reports/2026-11-03-1420-phoi-hop-cong-cu.manifest.json`
  - Cần: T3.4
  - Ra: report có timing thật, kết quả QC/eval, giới hạn, backup path; không công bố instruction riêng hoặc dữ liệu desktop.

## Cụm song song & file nóng

Một chuỗi triển khai: T1.1 → T1.2 → T2.1 → T2.2 → T3.1 → T3.2 → T3.3 → T3.4 → T4.1. `tdq_setup.py` và tests writer là file nóng: một chủ ghi, không chia writer/caller sang worktree đồng thời. QC độc lập read-only có thể chạy khi diff ổn định. Không mode nào được tự ý commit/merge trong plan này.

## Ánh xạ đầu ra

O1/O2: T1.2; O3: T2.1/T2.2; O4: T1.1/T3.1/T3.2/T3.3; O5: T3.4/T4.1. Không có đầu ra ngoài spec.

## QC vòng 1 — fix

- [x] **QC1.1** (e12m) Khóa scorer thực, báo backup khi rollback lỗi, giữ ACL fail-closed và sửa fixture evaluator cũ — Test: `python -m pytest tests/test_tdq_skill_eval.py tests/test_tdq_eval_hosts.py tests/test_eval_contracts_e2e.py tests/test_claude_md_core.py -q`
  - Chạm: `scripts/tdq_skill_eval.py`, `scripts/tdq_setup.py`, `tests/test_tdq_skill_eval.py`, `tests/test_claude_md_core.py`, `tests/test_eval_contracts_e2e.py`
  - Cần: T0.1, T2.1
  - Review độc lập: scorer callable chưa bind với phiên bản; rollback lỗi thiếu backup path; ACL cần readback. E2E cũ dùng corpus ID-only và trace thiếu terminal: phải sửa fixture hoặc kỳ vọng incomplete, không mở lại false PASS.
- [x] **QC1.2** (e3m) Sửa budget release cũ theo tập file HEAD thật — Test: `python -m pytest tests/test_build_portable.py -q -k release_budget`
  - Chạm: `tests/test_build_portable.py`
  - Cần: T1.2
  - Baseline HEAD đã có 162 file nhưng cap 161; đây là lỗi tồn từ release trước, không do writer. Ghi rõ tệp được duyệt mới, không tăng trần mù.

## QC vòng 2 — clean code evaluator

- [x] **QC2.1** (e10m) Tách phần validate/parse/execute của evaluator đang vượt 50 dòng, giữ hành vi fail-closed — Test: `python -m pytest tests/test_tdq_eval_hosts.py tests/test_tdq_skill_eval.py tests/test_eval_contracts_e2e.py -q`
  - Chạm: `scripts/tdq_skill_eval.py`, `scripts/tdq_eval_hosts.py`, `tests/test_tdq_skill_eval.py`, `tests/test_tdq_eval_hosts.py`
  - Cần: QC1.1
  - Đo AST: run_eval 135+, parse_trace_stream 147, run_host_trial 86 dòng; baseline cũng dài nhưng phần mở rộng phải giữ giới hạn. Không class/framework; helper chỉ cho trách nhiệm thật. Không ghi latency=0 khi chưa đo, không báo quota được thực thi khi chưa có cost.

- [x] **QC2.2** (e2m) Đồng bộ cap dòng tier-1 theo soul và marker nâng cấp — Test: `python -m pytest tests/test_doc_lint.py tests/test_skill_shape.py tests/test_kiem_no_marker.py -q`
  - Chạm: `scripts/doc_lint.py`, `scripts/tdq_skill_eval.py`
  - Cần: QC2.1
  - Full suite đỏ R6: conventions 209>192, setup132>130. Nâng cap đúng số đo để giữ luật chất lượng/quyền thường trực, không nén mất luật. Marker phải nêu upgrade path rõ.

## QC vòng 3 — fail-closed trace/scorer

- [x] **QC3.1** (e8m) Từ chối UTF-8/schema trace hỏng và scorer có globals thay đổi — Test: `python -m pytest tests/test_tdq_eval_hosts.py tests/test_tdq_skill_eval.py tests/test_eval_contracts_e2e.py -q`
  - Chạm: `scripts/tdq_eval_hosts.py`, `scripts/tdq_skill_eval.py`, `tests/test_tdq_eval_hosts.py`, `tests/test_tdq_skill_eval.py`
  - Cần: QC2.1
  - QC độc lập tái hiện scorer FunctionType đổi globals nhưng identity không đổi; bytes UTF-8 lỗi bị replace vẫn completed; content=None gây TypeError. Fail-closed đúng trust boundary, không cơ chế scorer mới. Full-suite thứ hai đã dừng vì phát hiện lỗi trước khi sửa nguồn, không coi PASS.

## QC vòng 4 — user duyệt bổ sung

User duyệt nguyên văn «“duyệt sửa QC tiếp»; cho một vòng sửa bổ sung, không bỏ test/nâng timeout/miễn eval. Đã resume qua CLI.

- [x] **QC4.1** (e1m) Sửa dấu phân cách marker theo contract checker hiện có — Test: `python -m pytest tests/test_kiem_no_marker.py -q`
  - Chạm: `scripts/tdq_skill_eval.py`
  - Leader giữ sửa comment contract một dòng; không đổi runtime/scorer.
- [x] **QC4.2** (e12m) Sửa cleanup job giữ file sau timeout và xác minh Chrome handshake trong runner — Test: `python -m pytest tests/test_tdq_test_process.py tests/test_codex_cli.py tests/test_archify_e2e.py -q`
  - Chạm: `scripts/tdq_test_process.py`, `tests/test_tdq_test_process.py`
  - Bằng chứng: diagnose-process-qc.py tái hiện 3 lỗi trong IsolatedJob; __exit__ rmtree nhận WinError32 tại 1.err sau timeout đã báo cleanup_complete=True. Giữ ownership và deadline, không bỏ cleanup, đổi quyền hoặc tăng timeout. Chrome cần reproducer riêng trước kết luận cùng nguyên nhân.

- [x] **QC4.3** (e3m) Bỏ USERPROFILE giả chỉ trong subprocess browser E2E Windows, giữ HOME/config và profile Chrome tạm — Test: `python -m pytest tests/test_archify_e2e.py -q`
  - Chạm: `tests/test_archify_e2e.py`
  - Cần: QC4.2
  - Đối chứng thực: USERPROFILE-only gây CDP timeout; HOME/TEMP/APPDATA/LOCALAPPDATA riêng đều đạt; all-private bỏ USERPROFILE đạt 0.625s. Không đổi sandbox, user profile thật hoặc timeout. Chạy test trong IsolatedJob để chứng minh fix.

## Sửa ACL — user duyệt bổ sung

User duyệt nguyên văn «duyệt sửa ACL». Giữ kiểm quyền fail-closed; không nâng quyền hoặc đổi ACL file gốc để ép ghi.

- [x] **ACL1.1** (e12m) So quyền descriptor Windows theo semantics và kiểm native roundtrip — Test: `python -m pytest tests/test_claude_md_core.py tests/test_auto_update_setup.py -q`
  - Chạm: `scripts/tdq_setup.py`, `tests/test_claude_md_core.py`
  - Đối chiếu owner/group, control/defaulted flags, DACL absent/null/empty, revision và từng ACE đúng thứ tự; chỉ bỏ khác biệt storage offsets/padding. Validate descriptor trước đọc pointer. Test layout tương đương và quyền/control thay đổi phải bị từ chối. Apply máy thật do leader sau test; không agent nào sửa user instruction.

## Definition of Done

- [x] Q1 Luật tự chủ đủ bước và giữ chất lượng/quyền — `python -m pytest tests/test_tool_composition.py tests/test_soul_rules.py -q`
- [x] Q2 Routing/handoff đúng lớp, không ép nhiều tool — `python -m pytest tests/test_tool_composition.py -q -k routing`
- [x] Q3 Thiếu tool chỉ research/đề xuất user-level trước duyệt — `python -m pytest tests/test_tool_composition.py -q -k missing`
- [x] Q4 Instruction riêng/encoding giữ nguyên, backup và no-op đúng — `python -m pytest tests/test_claude_md_core.py -q`
- [x] Q5 Lỗi writer không tiến stamp và retry được — `python -m pytest tests/test_auto_update_setup.py tests/test_context_hooks.py -q`
- [x] Q6 Không lặp delivery mơ hồ, kiểm file cuối và retry có tiến triển — `python -m pytest tests/test_tool_composition.py -q -k "delivery or download or retry"`
- [x] Q7 Tương thích và eval đủ chứng cứ — `python scripts/tdq_test.py tron-bo` cùng eval report đã khóa, không chạy trọn bộ lần thừa chỉ để tick.
- [x] Q8 Setup thật và báo cáo có evidence — kiểm receipt T3.4 và `python scripts/tdq_archify.py verify --document docs/tdq/reports/2026-11-03-1420-phoi-hop-cong-cu.md --manifest docs/tdq/reports/2026-11-03-1420-phoi-hop-cong-cu.manifest.json`.

Các test selector mới phải collect được ca kiểm, không dùng exit xanh khi không chạy test. Live behavior và mock/unit evidence ghi tách biệt. Dự kiến tổng công sức 103 phút, không tính thời gian chờ user. Mô phỏng dùng dữ liệu hiệu chuẩn lịch sử, trả đội 14.3 phút/main 18.3 phút; không thay tổng eNm bằng số mô hình và không hứa mức tăng tốc này cho chuỗi phụ thuộc hiện tại.

Khảo sát plan độc lập hoàn tất 1/1 nhánh, không lỗi/thiếu. Đã đưa vào plan: mẫu instruction đồng bộ, xung đột luật tự cài LSP, ACL/newline/readback-rollback, fixture chặn tác dụng phụ và chỉ gọi writer hẹp trên máy thật. Tái dùng tests writer/update hiện hữu, không tạo thêm test_instruction_sync.py. QC hồi quy thêm `tests/test_mcp_first_auto_setup.py`, `tests/test_hook_resilience.py`, `tests/test_uiux_routing.py`, `tests/test_checkportable.py`, `tests/test_codex_search_gate.py`; chỉ mở rộng Chạm nếu failure chứng minh cần sửa.
