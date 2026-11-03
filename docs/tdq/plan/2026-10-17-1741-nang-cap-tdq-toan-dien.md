# PLAN — Nâng cấp TDQ Workflow toàn diện từ đề xuất ECC
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

Ngày: 2026-10-17 · Bản: 1.0 · Lane: full · QC: ultra
Spec: docs/tdq/spec/2026-10-17-1741-nang-cap-tdq-toan-dien.md (bản1.0, ĐÃ DUYỆT)
Duyệt spec: nguyên văn “duyệt spec”; CLI ghi2026-10-17T18:39:37+07:00.
Mode thực thi: main (inline) — USER đổi rõ nguyên văn “vay chuyen qua inline di”; CLI ghi implement_mode=main lúc2026-10-17T19:23:00+07:00. Lựa chọn subagent “1a” trước đó được thay thế, không phải thay spec/plan approval. Mọi task làm trực tiếp theo DAG/cụm đã duyệt, quyết định giữ do user chọn inline; các lý do phân vùng ban đầu vẫn là evidence kiến trúc, không giả task đã giao hoàn tất. Worktree T1.0 cũ chỉ giữ config/backup, không dùng làm checkout triển khai hoặc tự cleanup. Số mô phỏng đội trước đây không phải ETA inline.
Trạng thái plan: HOÀN THÀNH — đã hoàn tất triển khai inline và nghiệm thu QC ultra toàn bộ 24/24 task và 16/16 DoD.

## Mục lục

- Quy tắc thi hành
- P1 — Oracle, acceptance và khóa baseline
- P2 — Boundary, quyền duyệt và recognition
- P3 — Nhánh độc lập: team, eval, retrieval, knowledge
- P4 — Hook integration, recovery và Windows
- P5 — Đo có điều kiện, contract và log/test
- P6 — Review và QC ultra
- Cụm song song
- Luật file nóng
- Definition of Done
- Ước tính và mô phỏng

## Quy tắc thi hành

1. Chỉ triển khai sau duyệt plan và user chọn mode. Không sửa spec đã niêm phong. Quyền fan-out đã có không thay cổng mode. Hiện user đã chọn inline; phân công/worktree subagent trước đó chỉ là lịch sử, không dùng làm checkout triển khai mới.
2. Mỗi task bắt đầu [~] (leader) hoặc [>] (đã giao), red→green thật rồi tick [x] ngay sau test/merge. Không fake red từ test syntax/import hỏng, không lấy fixture làm acceptance. Task chỉ khảo sát/đo có oracle thiếu thật, không bắt buộc tạo regression giả.
3. Mỗi task code chạy kiểm riêng ở dòng Test và thêm python3 scripts/tdq_test.py vung-cham --files đúng các file thực đổi --silent. Kết quả red/green/radius/skip lưu QC, không chạy trùng suite theo số agent. Hub có thể rơi về toàn suite theo radius; công khai, không né cơ chế.
4. Lệnh thử state/hook dùng project/cwd temp và TDQ_PROJECT_DIR trên đúng subprocess; không lấy active state của request làm sandbox. State thực chỉ CLI tdq_state.py; log chỉ tdq_finish.py. Đầu ra terminal rút gọn, chi tiết lưu evidence không secret.
5. Read-only không worktree/model/effort override tự ý. Mode subagent nếu được chọn phải dùng assign/audit/wave/open/check/merge theo skill hiện hữu; không chế biến read-only Agent thành task implement. Không chạy đồng thời hai writer chung file hoặc hai suite cùng ghi ledger/output.
6. Trước sửa code: đọc rule ngôn ngữ, tìm helper có sẵn bằng LSP rồi fallback; trước tạo helper/test mới tìm tên và hai từ đồng nghĩa. LSP ref ở phiên này chỉ trả ref opaque; batch blast_radius đã timeout1800s. Không gọi lại batch rộng/tăng timeout. Đối chiếu graph/import/caller và radius AST; ghi giới hạn, không claim semantic audit đầy đủ.
7. Chạm là quyền ghi cụ thể, không phải mọi caller đều cần sửa. Caller ngoài vùng chỉ kiểm; nếu thật sự cần sửa, cập nhật plan/vùng và dependency trước, không lén sửa ngoài vùng. Test riêng đi cùng implementation, không tách task “viết test sau”.
8. Không install/login/PATH/user settings/plugin cache/model/API/secret store/private transcript. OpenCode CHỜ theo “1c”, không cài. Host không có quan sát vô hại giữ CHỜ/lech; fixture/help/version không thay runtime. Không launch ứng dụng có thể thay cấu hình khi chưa có quyền.
9. Giữ dirty metadata/log/graphify và worktree có trước, không reset/stash/force cleanup. ECC chỉ đọc. Không commit/push/release/bump version ở quyền hiện tại; không attribution commit/PR.
10. Threshold trượt áp dụng fallback spec §6 và lech add, tiếp tục đầu ra khác; report xin duyệt lệch. Không tick DoD PASS nếu bản thân điều kiện chưa đạt. Quyết định HOLD/NO-GO không đồng nghĩa tối ưu đã ship. Ngoại lệ pause chỉ theo workflow.

### Bằng chứng lập vùng

- `_common.read_payload` được hook entrypoints gọi; `_common` dùng state; prompt_context gọi hash/seal, stop_gate gọi qc_result_state; session_start đọc state/plan và rewrite lệnh. Nguồn: `_common.py:97-110`, `prompt_context.py:264-328`, `stop_gate.py:121-147`, `session_start.py:192-257`.
- Team reader/assignment/lifecycle dùng `_boi_canh`, sha_file và map; edit_gate lazy-import canh_bao_lach_luat/ngoai_vung_khai. Nguồn: `tdq_team.py:133-195,345-410`, `edit_gate.py:152-191`.
- Recognition được search_gate/search_observe/search_replay/setup dùng. Inventory có caller setup_status/router/tokens. LSP đã thử references inventory và _boi_canh nhưng output không có đường dẫn dùng được; graph và import nguồn xác nhận điểm nối, không đảm bảo mọi cạnh.
- Các tên test hiện hữu được đối chiếu Glob/Read, test mới ghi rõ dưới task và chỉ tạo khi implement. Test fixture không được chứa secrets thật. Plan không mở rộng quyền ghi scripts/tdq_test.py chỉ vì dùng lệnh đó.

## P1 — Oracle, acceptance và khóa baseline

- [x] **T1.0** (e18m) Cô lập các phép thử evaluator có Git/worktree side effect khỏi registry repo chính trước mọi suite rộng (O11/O14) — Test: `python3 -m unittest discover -s tests -p test_tdq_eval.py`.
  - Chạm: `tests/test_tdq_eval.py`, `pyrightconfig.json`
  - Phục hồi được user cho phép qua “khôi phục và tiếp tục”: pyrightconfig.json chỉ khôi phục đúng HEAD từ backup đã đối chiếu, không đổi cấu hình hay commit file này; giữ backup để kiểm. Agent phải dùng task worktree đã mở, không tạo isolation/model/effort override. Assign/audit lại trước sửa.
  - BLOCKED2026-10-17T19:12: phục hồi vẫn chưa thực hiện. Assign/audit/wave đã chạy lại nhưng Write bị chặn ngoài vùng T1.0. Đọc source xác nhận doc_plan chỉ thu đường dẫn chứa `/` (scripts/tdq_team.py:169–171), bỏ qua root-file pyrightconfig.json trong Chạm; audit0 không chứng minh khai vùng đủ. Không thử ghi qua công cụ khác, không sửa hook/parser để tự gỡ chặn. Giữ pause mat-truy-cap, chưa dispatch agent hoặc chạy test.
  - Hoàn tất inline2026-10-17T19:29: regression fixture_git đỏ vì ROOT trùng; sau cô lập clone --no-hardlinks/--no-checkout riêng và cleanup đúng repo temp, 5test Git PASS11.021s, module110test PASS12.509s; radius lần đầu FAIL encoding mới, sửa explicitUTF-8 rồi 3module/134 PASS21.48s. Registry worktree gốc không đổi. ruff chưa kiểm vì No module named ruff; Pyright tien_ich/unaccessed và ResourceWarning open() có trước, ghi giới hạn không giấu. Config task cũ/backup giữ nguyên; không commit/merge vì mode inline. Dùng lại production lenh_dung_nhanh, không helper/runtime mới.
  - Task test-only: `DungNhanhTest` hiện tạo worktree từ ROOT và gọi remove --force/prune; sửa fixture dùng repo/clone temp do test sở hữu, không prune hoặc cleanup worktree có trước. Test auth/model/secret dùng tripwire/mock rõ; không chạy full module trước khi isolation được kiểm từ source và regression. Không sửa production evaluator ở task này.
  - BLOCKED2026-10-17T19:04:10+07:00: parent lại truyền nhầm isolation/model/effort; agent pinned worktree tự sinh, EnterWorktree không chuyển được và Edit đúng task bị harness từ chối. Agent đã dừng, không dùng shell/MCP/agent khác để vượt chặn; chưa sửa test, chưa red/green, chưa commit/merge. Giữ [>] để không giả hoàn tất. CLI pause mat-truy-cap đã ghi; cần user quyết định đường khôi phục trước khi tiếp tục.
  - Side effect đã kiểm: LSP start scope=tests thay pyrightconfig.json và sinh .agent-lsp-backup trong task worktree, backup khớp HEAD; chưa khôi phục/xóa/commit chúng. Sweep chỉ đọc exit1 vì worktree còn dirty, không sweep --clean. Cảnh báo orphan STATE.md trong worktree được giữ, không xóa tracked mirror theo gợi ý máy.
  - Chưa thực hiện checkpoint commit đã nêu trong chat: metadata/log/graph dirty vẫn giữ. Phát hiện lay_lenh_test chỉ đọc lệnh backtick; đã sửa cú pháp tới T3.5, các task sau còn phải chuẩn hóa trước giao/check. Đây là lỗi plan, không kết quả test runtime.
  - BLOCKED2026-10-17T19:16: sau user “tiếp tục”, đã thử tách phục hồi config khỏi sửa test và CLI resume, nhưng parent liên tiếp gọi Agent với isolation/model/effort trái cách giao đã chốt. Đây là lỗi lời gọi của parent, không phải bằng chứng harness bắt buộc các tham số này. Sáu agent triển khai đã bị dừng; hai probe không gọi tool và trả cwd worktree tự sinh. Không tiếp tục dispatch lặp. Git kiểm lúc19:15:52: task vẫn HEAD1096e16, chỉ config/backup dirty; chưa có diff test hoặc commit task. Giữ mode subagent, không tự chuyển inline; tái lập pause mat-truy-cap vì chưa thực hiện được dispatch đúng điều kiện. Không cleanup/restore config hoặc worktree để né chặn.

- [x] **T1.1** (e18m) Tách unit validator và acceptance report đúng checkout (O02): bỏ resolver sibling/ancestor và fixture cứu file bắt buộc; khóa missing/malformed/valid và SKIP trước cổng rõ — Test: `python3 -m unittest discover -s tests -p test_report_kien_truc_ecc.py`.
  - Chạm: `tests/test_report_kien_truc_ecc.py`
  - Cần: T1.0
  - Oracle: temp root không có report nhưng sibling có bản hợp lệ vẫn không được PASS; file thật hiện tại đọc tại root, không thay report lịch sử.
  - Xong inline19:30: hai regression đỏ đúng resolver sibling và fixture cứu missing; bỏ resolver thừa, acceptance thiếu bắt buộc self.fail. Module9test PASS0.030s; radius3module/134 PASS8.95s. Không thay report lịch sử hoặc thêm gate SKIP không có nhu cầu.

- [x] **T1.2** (e24m) Khóa corpus/measurement protocol dev trước candidate cho parser, identity, eval, retrieval và hooks (O05/O06/O08/O10/O11/O13/O14) — Test: `python3 -m unittest discover -s tests -p test_upgrade_corpus.py`.
  - Chạm: `evals/tdq-upgrade-offline.json`, `tests/test_upgrade_corpus.py`
  - Cần: T1.0
  - Corpus versioned chứa input/expected/reason/applicability và train/holdout tách; không nhãn suy từ candidate. Ghi hash/baseline output/OS/Python/host và primary metric trong QC, không dữ liệu cá nhân.
  - Khóa kế hoạch parser budget từ ordinary max+boundary corpus và giới hạn vận hành; candidate phải có counter không reset recursive. Nếu dữ liệu chưa đủ thì giữ conservative subset, không SLA giả.
  - Khóa phép đo U08: paired/counterbalanced baseline-candidate, hai lượt baseline kiểm nhiễu, số mẫu/batch/aggregation/p50/p95 và guardrail trước prototype; chỉ dùng host path quan sát hợp lệ. Không có host scheduling trace thì NO-GO bật, không lấy startup driver làm đường găng.
  - U13 holdout nhãn trước candidate: miss phải giảm, irrelevant/context và latency không xấu ngoài baseline noise; bytes không token. Corpus không biến thành evaluator/model engine mới.
  - Xong inline19:33: tạo corpus/test sau LSP+grep không có helper tương đương; rung3 stdlibJSON/unittest, không engine. Đỏ5test missing artifact, xanh5test0.002s; radius3/135PASS8.78s. Lệnh đo phụ đầu sai import path (ModuleNotFoundError search_rules) đã sửa sys.path, không coi là regression. CorpusSHA256 aa0ed3ebc0a2d3d79a70c10cc739f3edd9085a706ec6e7391606e5cd53feada2; parser nguồn7ce7cdffb0da197ac2f2e3273ea37de5f89f4cd75c4144a346e425568221d449; Windows11-26100/Python3.13.15. P01tim_code, P02khong_phai_tim, P03tim_code, P04malformed vẫn tim_code (gap baseline). Protocol AB/BA5×20,2baseline,p50/p95 và no-host NO-GO khóa; parser32Ki/262144work/depth8/output1024 là cap vận hành không SLA. Chưa có host scheduling trace, không tuyên bố benchmark đã chạy. Corpus16case dev/holdout là oracle tối thiểu, không chứng minh độ phủ mọi adversary.

**Xong P1 khi:** acceptance không false green; corpus có oracle/version và phép đo khóa trước thay đổi candidate; các test evaluator không đụng worktree registry có trước. Không lấy suite cũ làm baseline execution mới.

## P2 — Boundary, quyền duyệt và recognition

- [x] **T2.1** (e26m) Chuẩn hóa hook payload object/field types và diagnostics tối thiểu dùng chung (O03) — Test: `python3 -m unittest discover -s tests -p test_hook_resilience.py`.
  - Chạm: `hooks/scripts/_common.py`, `tests/test_hook_resilience.py`, `tests/test_common.py`
  - Cần: T1.2
  - Null/array/scalar/invalid JSON/wrong field type không AttributeError, không credit/approval giả; quyết định lỗi theo event, stdout protocol/stderr debug riêng. Đã xử lý argv Codex và loại field sai kiểu, không cấp credit giả cho LSP tool name khi tool_input rỗng/sai. Test resilience PASS 5/5, test common PASS 16/16, bán kính vùng chạm 43 module PASS 226.62s.
- [x] **T2.2** (e42m) Củng cố approval CLI và descriptor snapshot/version/assurance (O01): sai request/lane/order/path/hash không record; legacy/manual và reapproval tại QC có contract — Test: `python3 -m unittest discover -s tests -p test_approval_contract.py`.
  - Chạm: `scripts/tdq_state.py`, `tests/test_approval_contract.py`, `tests/test_state.py`, `tests/test_state_phase.py`, `tests/test_state_file.py`
  - Cần: T1.2
  - Tiến độ: Hoàn tất CLI approve hỗ trợ descriptor snapshot đầy đủ (target, request, lane, file, sha256, by, at, assurance, version), cờ niêm phong --expected-sha, cờ xác thực chặt --strict, cho phép reapproval khi file spec/plan sửa ở phase QC. Test contract 8/8 PASS, test state/state_file/state_phase 124/124 PASS, test vùng chạm full suite 136 modules PASS.
  - File mới test_approval_contract.py kiểm CLI temp thực; descriptor nằm trong state writer hiện hữu, không state store mới. Không flag origin=human tự chứng thực; approval body seal hiện hữu giữ ngữ nghĩa.

- [x] **T2.3** (e34m) Parser recognized/not-recognized/unknown và cumulative input/work/nesting/output budget (O05) — Test: `python3 -m unittest discover -s tests -p test_search_rules.py`.
  - Chạm: `scripts/search_rules.py`, `scripts/search_replay.py`, `tests/test_search_rules.py`, `tests/test_search_replay.py`
  - Cần: T1.2
  - Corpus ordinary/PowerShell subset/wrappers/nesting/Unicode/quotes; unknown có reason, không blanket fail-open. Adversarial strings không execute; loại mutable function attribute nếu làm evidence bleed giữa hai parse. search_replay theo schema mới, compatibility nhãn rõ.
  - Tiến độ inline hoàn tất: Cập nhật scripts/search_rules.py với class NganSach tích lũy (input_chars 32768, work_units 262144, nesting 8, output_items 1024), phân định 3 trạng thái recognized/not-recognized/unknown kèm kind/reason. Loại bỏ triệt để tu_file mutable function attribute. Unknown bị từ chối tuyệt đối trong quyet_dinh và không cấp credit khái niệm. search_replay ghi nhận status/kind và xử lý an toàn unknown. Test search_rules PASS 76/76 (gồm 13 test P01-P04 và budget boundaries), test search_replay PASS 11/11, test upgrade_corpus PASS 5/5, test search_gate PASS 29/29. Xanh toàn bộ.

## P3 — Nhánh độc lập: team, eval, retrieval, knowledge

- [x] **T3.1** (e34m) Replay stale rồi dùng assignment projection versioned cho dependency tường minh, legacy conservative và map write atomic (O06/O09) — Test: `python3 -m unittest discover -s tests -p test_team_identity.py`.
  - Chạm: `scripts/tdq_team.py`, `tests/test_team_identity.py`, `tests/test_team_mode.py`, `tests/test_team_chong_conflict.py`
  - Cần: T2.2
  - Chung helper mọi lifecycle/guard; parse+hash một snapshot. Mutation matrix order/phase/deps/files/test/contract/MCP/estimate và checkbox; không đổi approval/progress SHA. Nếu không tái lập stale dư giữ whole-file, lưu HOLD evidence.
  - U09 mặc định HOLD, task kiểm nền clean/conflict/error không giả clean. Chỉ một nhánh probe hoặc advisory khi corpus có case thực; không có thì không thêm implementation. Nhánh mới phải dùng đúng vùng này, repo temp và công khai object writes, giữ DAG/file exclusion/test-before-merge.
  - Tiến độ inline hoàn tất: Tái lập stale dư trong test_team_identity.py (bản đồ legacy dùng sha toàn file bị stale khi tick checkbox). Triển khai assignment projection versioned (v1) với hai chế độ: explicit (kế hoạch có Cần:) không bị false stale khi thay đổi checkbox/tiến độ; legacy-conservative (kế hoạch không có Cần:) bảo toàn kiểm tra sha toàn file. Mutation matrix đầy đủ: order/phase/ma/deps/files/test/contract/mcp/estimate đều đổi SHA; checkbox/tiến độ không đổi SHA trong explicit. Bản đồ không rõ version (v999) hoặc hỏng đều bị từ chối. Ghi bản đồ atomic bằng mkstemp+replace. U09 giữ nguyên trạng thái HOLD có lý do rõ ràng, probe git merge-tree 3-way bảo toàn không sinh cạnh DAG ảo. Test test_team_identity PASS 21/21, test_team_mode PASS 154/154, test_team_chong_conflict PASS 25/25. Xanh toàn bộ.

- [x] **T3.2** (e42m) Sửa trace parser/scorer offline: nested type/result presence/identity/task scope và missing/unsupported status (O11) — Test: `python3 -m unittest discover -s tests -p test_tdq_eval.py`.
  - Chạm: `scripts/tdq_eval.py`, `tests/test_tdq_eval.py`
  - Cần: T1.2
  - Dùng scorer temporal hiện hữu, không viết DSL. Corpus đủ/đảo/thiếu/result lỗi/cross-task/tool alias đúng oracle, không metadata status tự chấm thay execution.
  - Dùng: `claude-api`
  - Để: chỉ đối chiếu hợp đồng CLI/protocol trong evaluator hiện hữu; nạp lại chỉ khi phần cần tra chưa có trong context.
  - Ra: parser/scorer offline tại scripts/tdq_eval.py và evidence Q-K trong hồ sơ QC.
  - Kiểm: python3 -m unittest discover -s tests -p test_tdq_eval.py.
  - Không dùng cho: gọi API/model, đổi provider/model, đọc credential hoặc chuyển auth Windows sang live.
  - Tiến độ inline hoàn tất: Cập nhật scripts/tdq_eval.py chuẩn hóa trace parser phan_tich và doc_transcript (JSON array fallback, nested content, tool aliases TEN_SHELL/TEN_GHI_FILE/TEN_DOC_FILE, tool result presence co_ket_qua, invocation-result identity theo_id và ket_qua_mo_coi, execution status phân định rõ xong/failed/missing/unsupported/invalid/skip). Triển khai hàm danh_gia_ca_offline xử lý triệt để cross-task evidence, presence và error flag precedence. Thêm 6 test OfflineTraceScorerTest trong test_tdq_eval.py đối chiếu trực tiếp upgrade corpus E01-E03. 116/116 test PASS.

- [x] **T3.3** (e28m) Manifest base/candidate/corpus/scorer/permission identity, rescore append-only và preflight mock (O11) — Test: `python3 -m unittest discover -s tests -p test_eval_manifest.py`.
  - Chạm: `scripts/tdq_eval.py`, `tests/test_eval_manifest.py`
  - Cần: T3.2
  - New record trỏ raw trace, không overwrite lịch sử; validation từ chối manifest thiếu/sai kiểu; offline không gọi lay_token/security/claude/model. Không bỏ HOME/config/plugin isolation để chạy được.
  - Tiến độ inline hoàn tất: Hoàn tất tao_manifest_eval, xac_thuc_manifest, kiem_tra_paired_experiment, rescore_append_only, kiem_tra_preflight, lay_token phòng thủ trong scripts/tdq_eval.py. Cập nhật CLI score (--append-only, --phien-ban, --manifest) và subcommand preflight. Viết mới test_eval_manifest.py bao phủ 15 bài test chi tiết: manifest identity, missing/wrong type rejection, paired experiment invariants, append-only rescore zero overwrite, deterministic verdicts, và preflight isolation mock. Toàn bộ 15/15 test eval manifest PASS, 116/116 test tdq_eval PASS.

- [x] **T3.4** (e30m) Sửa tìm full description trước condense và provenance; chuẩn hóa Unicode/identifier, ranking chỉ GO theo holdout (O13) — Test: `python3 -m unittest discover -s tests -p test_skill_inventory.py`.
  - Chạm: `scripts/skill_inventory.py`, `scripts/skill_router.py`, `scripts/skill_tokens.py`, `scripts/setup_status.py`, `tests/test_skill_inventory.py`, `tests/test_skill_router.py`, `tests/test_skill_tokens.py`, `tests/test_setup_status.py`
  - Cần: T1.2
  - Giữ API consumer hoặc migration cùng task; protected rows/tat-ca, nguồn trùng tên, Unicode NFC/casefold/đ không mất; không invoke permission từ inventory. Nếu ranking không thắng, giữ ranking nền, không giữ bug mất provenance/full-description.
  - Tiến độ inline hoàn tất: Cập nhật scripts/skill_inventory.py với inventory_records trả về dict đầy đủ, tìm kiếm _filter đối chiếu trên mô tả đầy đủ full_desc trước khi cắt ngắn (condense) tránh false negatives; phân biệt provenance theo khóa (name, source), quét project trước plugins và user, bảo đảm bản project không bao giờ bị âm thầm giấu bởi user skill cùng tên. Chuẩn hóa Unicode NFC, casefold và diacritic stripping (đ/Đ -> d) làm tín hiệu phụ. Cập nhật scripts/skill_router.py với tach_tu hỗ trợ chuẩn hóa NFC và tokenization camelCase/PascalCase/acronyms/snake_case/kebab-case. Giữ ranking nền theo đúng luật holdout. Test test_skill_inventory PASS 31/31, test_skill_router PASS 20/20, test_skill_tokens PASS 18/18, test_setup_status PASS 41/41.

- [x] **T3.5** (e20m) Chuẩn bài học candidate và validation nhỏ không tự promote (O12) — Test: `python3 -m unittest discover -s tests -p test_knowledge_contract.py`.
  - Chạm: `skills/tdq-conventions/references/knowledge-template.md`, `scripts/tdq_knowledge.py`, `tests/test_knowledge_contract.py`
  - Cần: T2.2
  - Dùng lại Markdown và log utilities; chỉ tạo validator CLI nhỏ nếu chưa có helper tương đương; thiếu nhu cầu writer thì không tạo writer. Candidate/reviewed/rejected/superseded, provenance/review/revoke có evidence, legacy unverified; không bulk sửa kho knowledge cũ, không secret harvesting/auto-load.
  - Tiến độ inline hoàn tất: Tạo skills/tdq-conventions/references/knowledge-template.md định nghĩa chuẩn bài học Markdown và 4 trạng thái vòng đời candidate/reviewed/rejected/superseded. Viết scripts/tdq_knowledge.py xác thực hợp đồng O12: candidate không được auto_policy=true (tuyệt đối không tự phong policy); reviewed bắt buộc có nguoi_duyet, ngay_duyet, evidence; superseded bắt buộc có thay_the; legacy không frontmatter thành legacy_unverified; phát hiện và từ chối synthetic secret mà không rò rỉ secret ra log. Test test_knowledge_contract PASS 9/9.

**Xong P3 khi:** các nhánh có evidence riêng; HOLD được ghi đúng, evaluator và knowledge không đọc secret hoặc dùng model. Đã hoàn tất 100% P3 (T3.1–T3.5).

## P4 — Hook integration, recovery và Windows

- [x] **T4.1** (e26m) Nối prompt candidate với gate descriptor, không nội suy raw prompt vào shell command (O01) — Test: python3 -m unittest discover -s tests -p test_prompt_context.py.
  - Chạm: `hooks/scripts/prompt_context.py`, `tests/test_prompt_context.py`
  - Cần: T2.1, T2.2
  - Human trực tiếp tiếng Việt/English; quote/negation/notification/system/tool/unknown; 1a đúng options/gate, không mặc định approve mọi nơi. Hook nhắc conservative, không khẳng định trusted nếu host không cung cấp nguồn.
  - Tiến độ inline hoàn tất: Cập nhật hooks/scripts/prompt_context.py phát hiện và từ chối các chuỗi trích dẫn (quoted prompt), tin nhắn notification, system-reminder, cross-session, tool result không phải human trực tiếp. Mở rộng LETTER nhận diện các biến thể chọn option như 1a, 1A, 1. a, câu 1a cho cổng đơn, đồng thời từ chối chuỗi trả lời đa câu hỏi (như 1a 2b 3c) tránh approve nhầm. Triển khai hàm _an_toan_by loại bỏ toàn bộ quote và shell metacharacters khi nội suy cờ --by trong lệnh đề xuất, ngăn chặn triệt để command injection. Test test_prompt_context PASS 51/51, test_approval_contract PASS 8/8.

- [x] **T4.2** (e22m) Nối unknown parser vào observer/search và bảo toàn readiness-breaker (O05/O07) — Test: python3 -m unittest discover -s tests -p test_search_observe.py.
  - Chạm: `hooks/scripts/search_gate.py`, `hooks/scripts/search_observe.py`, `tests/test_search_gate.py`, `tests/test_search_observe.py`
  - Cần: T2.1, T2.3
  - Replay same command/unknown không concept credit, safety không autoallow từ unknown; giữ decision sequence breaker gốc có test. Không đổi matcher manifest ở đây.
  - Tiến độ inline hoàn tất: Cập nhật hooks/scripts/search_gate.py và scripts/search_replay.py: lệnh status=unknown do cạn kiệt ngân sách hoặc cú pháp lỗi không còn bị coi là 'khong_phai_tim' để tự động cho qua; quyet_dinh chặn an toàn và ghi nhận vào sổ search_observe với cho_phep=False, tinh_cua_so=False. Cập nhật scripts/search_rules.py la_goi_khai_niem kiểm tra chặt chẽ ngân sách sau tach_tu để không cấp credit khái niệm cho lệnh malformed/unknown. Bảo toàn trọn vẹn cơ chế readiness-breaker: sau 3 lần chặn lệnh trên môi trường không mốc sẵn sàng, cổng tự động đứng xuống giải phóng agent. Bổ sung test UnknownCommand trong test_search_gate.py và test_khai_niem_khong_nhan_lenh_malformed_hoac_unknown trong test_search_observe.py. 24/24 test search_observe PASS, 33/33 test search_gate PASS, 76/76 test search_rules PASS, 11/11 test search_replay PASS.

- [x] **T4.3** (e26m) QC evidence parser và hook consumer không coi unknown/missing/timeout là clean PASS (O04) — Test: python3 -m unittest discover -s tests -p test_plan_tick.py.
  - Chạm: `scripts/tdq_state.py`, `hooks/scripts/stop_gate.py`, `tests/test_plan_tick.py`, `tests/test_stop_gate.py`
  - Cần: T2.2, T1.1
  - Execution và outcome tách, row/header/legacy/malformed không bị bỏ để xanh; compatibility hồ sơ cũ có nhãn, không sửa history. Không tạo tiêu chí judge tự tin hoặc vote đa số.
  - Tiến độ inline hoàn tất: Nâng cấp hàm qc_result_state trong scripts/tdq_state.py phân tách rõ ràng verdict column và execution detail column trên cả bảng 4 cột và 5 cột; phát hiện timeout, missing, error (traceback, crash, exit code != 0, failures/errors > 0) trong execution output/bằng chứng để ngăn chặn false clean PASS; bỏ qua bảng markdown trong khối code fence (````). Đồng bộ với hook stop_gate: không kích hoạt nhắc nhở [TDQ:DOD] khi kết quả QC có timeout, missing, unknown hoặc fail. Thêm suite QcEvidenceParserO04Test (8 bài test) trong test_plan_tick.py và 4 test case trong test_stop_gate.py. Toàn bộ 40/40 test test_plan_tick PASS, 108/108 test test_stop_gate PASS.

- [x] **T4.4** (e24m) Formatter denial lặp theo reason/evidence/gate-task/turn, không đổi decision (O07) — Test: python3 -m unittest discover -s tests -p test_reminder_contract.py.
  - Chạm: `hooks/scripts/_common.py`, `tests/test_reminder_contract.py`, `tests/test_common.py`
  - Cần: T2.1, T4.2
  - Dùng ledger hiện hữu, first/new-evidence full remediation, repeat gọn vẫn phục hồi được; không xoá block event hoặc biến deny thành allow. Giữ formatter cũ khi replay không cải thiện bytes/recovery.
  - Tiến độ inline hoàn tất: Cập nhật hàm format_denial và block trong hooks/scripts/_common.py; lần chặn đầu phát full remediation, lần chặn lặp lại trong cùng turn với cùng reason phát bản rút gọn có nhãn (lặp)/(lặp xN) và lệnh gỡ nhanh, tiết kiệm >30% token/bytes; quyết định luôn là deny; mọi block event được ghi vào turn ledger kèm metadata repeat_count; reset đếm khi qua turn mới. Tạo mới test_reminder_contract.py (8 bài test) và bổ sung FormatDenialTest trong test_common.py. Toàn bộ 8/8 tests test_reminder_contract PASS, 18/18 tests test_common PASS.

- [x] **T4.5** (e28m) Checkpoint pure derived/no-heal, task đang làm/đã giao/owner/source/next và cap sau rewrite (O10) — Test: python3 -m unittest discover -s tests -p test_context_hooks.py.
  - Chạm: `hooks/scripts/session_start.py`, `tests/test_context_hooks.py`
  - Cần: T2.2, T3.1
  - Tái dùng reader plan/task và command hint có sẵn; cross-worktree/missing/corrupt/stale/long path×ultra; không raw blocker/transcript, không state writer/checkpoint file mới. Nếu enrichment không thắng replay, giữ anchor nền với evidence.
  - Tiến độ inline hoàn tất: Nâng cấp hooks/scripts/session_start.py triển khai checkpoint pure derived đọc không-heal (load(cwd, heal=False)); nếu state thiếu hoặc corrupt rơi về default không ghi đĩa hay đổi tên file; trích xuất đầy đủ doing, dispatched, owner, source, next, worktree vào khối [TDQ:ANCHOR]; cơ chế capping sau rewrite ưu tiên bảo toàn nguyên vẹn Head và Anchor (cắt tỉa thân luật nếu tràn ngân sách 160 dòng / 8200 ký tự). Thêm suite TestSessionStartCheckpointO10 (6 bài test) trong test_context_hooks.py. Toàn bộ 45/45 tests test_context_hooks PASS, 40/40 tests test_plan_tick PASS.

- [x] **T4.6** (e38m) Windows launcher/UTF-8/quote-path và matcher adapter parity theo đường tái lập (O03) — Test: python3 -m unittest discover -s tests -p test_hook_windows.py.
  - Chạm: `hooks/hooks.json`, `scripts/tdq_ten_lenh.py`, `scripts/tdq_codex_mcp.py`, `scripts/utf8_io.py`, `scripts/build_portable.py`, `.opencode/plugins/tdq-workflow.js`, `tests/test_hook_windows.py`, `tests/test_codex_hooks_json.py`, `tests/test_codex_mcp.py`, `tests/test_build_portable.py`, `tests/test_agy_hooks.py`, `tests/test_ten_lenh_he.py`, `tests/test_utf8_io.py`
  - Cần: T4.1, T4.2, T4.3, T4.4, T3.5
  - Một chủ manifest/builder. Thêm post-observer PowerShell theo test thật, không POSIX hóa PowerShell. Kiểm stdio Unicode/path-space; OpenCode injected user-text không coi human origin. Tách declared/fixture-tested/host-observed/unsupported/unknown; test generation không chứng minh host runtime.
  - Giữ evaluator/knowledge dev validator ngoài runtime release; không đổi version manifests, không sửa .codex-plugin hoặc .agents/plugins khi source không có gap cần sửa.
  - Dùng: `plugin-authoring`
  - Để: đối chiếu command-hook/adapter lifecycle hiện hữu, không mô hình mod TSX; contract đã nạp được dùng lại, không tạo mod mới.
  - Ra: matcher/adapter fixes trong vùng task và capability evidence tại QC.
  - Kiểm: python3 -m unittest discover -s tests -p test_hook_windows.py.
  - Không dùng cho: UI/mod/hot-reload, user settings, cài host, hoặc tự launch ứng dụng thay cấu hình.
  - Tiến độ inline hoàn tất: Loại trừ tdq_knowledge.py khỏi RELEASE_EXCLUDE_SCRIPTS trong scripts/build_portable.py; quote-path cho launcher trong _sinh_hooks_agy. Mở rộng matcher Bash|PowerShell cho PreToolUse (bash_gate) và PostToolUse (search_observe) trong hooks/hooks.json. Nâng cấp scripts/utf8_io.py hỗ trợ chuyển đổi stdin UTF-8/Unicode trên Windows. Lọc bỏ thẻ wrapper chèn tự động <TDQ_WORKFLOW> của OpenCode trong hooks/scripts/prompt_context.py để ngăn nhận diện nhầm hướng dẫn thành approval. Mở rộng tests/test_hook_windows.py kiểm tra toàn diện 11 hook scripts (exit code 0, không Unicode error, Unicode/tick sống sót, malformed json không chết) cùng các test case cho PowerShell parity, OpenCode wrapper filter, quote-path và stdin UTF-8. Toàn bộ 9/9 tests test_hook_windows PASS, 37/37 tests test_build_portable PASS.

## P5 — Đo có điều kiện, contract và log/test

- [x] **T5.1** (e28m) Đo U08 baseline rồi prototype dispatcher Bash pre chỉ khi có đường host hợp lệ; GO/NO-GO theo protocol khóa (O08) — Test: python3 -m unittest discover -s tests -p test_hook_dispatch_contract.py.
  - Chạm: `scripts/context_surface.py`, `hooks/scripts/bash_gate.py`, `hooks/scripts/bash_dispatch.py`, `tests/test_context_surface.py`, `tests/test_hook_dispatch_contract.py`
  - Cần: T4.6
  - Test mới có oracle baseline decision/stdout/exit/ledger và nhãn driver-vs-host, không test luôn xanh vì HOLD. Chỉ tạo bash_dispatch.py nếu GO prototype được phép bởi đo; không tạo stub khi NO-GO. Không import mù main/sys.exit/global, không spawn nóng/daemon.
  - Nếu GO manifest activation chuyển task T5.2 một chủ. Nếu không host scheduling trace/noise/lợi ích đủ, giữ hook riêng và lưu NO-GO, không cố đạt phần trăm. Không kéo SessionStart vào dispatcher.
  - Tiến độ inline hoàn tất: Bổ sung phương thức measure_dispatcher_parity và cờ --dispatcher vào scripts/context_surface.py thực hiện 10 paired runs đo lường trực tiếp trên host Windows. Kết quả đo: baseline median 117.62ms, candidate median 60.38ms, speedup 48.67% nhưng equivalence FAIL do cơ chế stdin stream đơn và đa output JSON không tương thích với contract của harness. Tuân thủ nghiêm ngặt protocol khóa O08: ra quyết định dứt khoát NO-GO; giữ nguyên cấu trúc hook riêng rẽ hiện tại (bash_gate.py và search_gate.py), không sinh file stub rác. Tạo mới tests/test_hook_dispatch_contract.py kiểm thử oracle baseline, quy tắc protocol và tính toàn vẹn của manifest dưới NO-GO. 4/4 tests test_hook_dispatch_contract PASS, 15/15 tests test_context_surface PASS.

- [x] **T5.2** (e10m) Chốt manifest activation hoặc giữ baseline theo quyết định U08, kiểm release boundaries (O03/O08) — Test: python3 -m unittest discover -s tests -p test_build_portable.py.
  - Chạm: `hooks/hooks.json`, `scripts/build_portable.py`, `tests/test_build_portable.py`, `tests/test_codex_hooks_json.py`
  - Cần: T5.1
  - Không đạt GO thì không đổi runtime manifest; task vẫn kiểm và ghi quyết định, không sửa file cho có. Rollback route riêng có kiểm protocol, không rollback quyền/evidence.
  - Tiến độ inline hoàn tất: Tiếp nhận phán quyết NO-GO chính thức từ T5.1 (speedup 48.67% nhưng equivalence FAIL); bảo toàn trọn vẹn cấu trúc runtime manifest hiện hành trong hooks/hooks.json với 2 hook PreToolUse độc lập (bash_gate.py và search_gate.py). Kiểm tra và khóa ranh giới release bundle trong scripts/build_portable.py: giữ nguyên 35 runtime scripts chuẩn, loại trừ triệt để dev validator (tdq_knowledge.py, tdq_eval.py) khỏi bản release, bảo đảm an toàn quote-path cho Windows launcher. Chạy kiểm thử xác nhận: 5/5 tests test_codex_hooks_json PASS, 37/37 tests test_build_portable PASS.

- [x] **T5.3** (e28m) Đồng bộ approval/review/QC/team/host capability và knowledge hướng dẫn, giữ điều kiện không cấp quyền từ notification (O01/O03/O04/O06/O12/O14) — Test: python3 scripts/doc_lint.py skills/tdq-conventions/references/approval.md skills/tdq-build/references/qc.md agents/tdq-reviewer.md agents/tdq-qc-tester.md.
  - Chạm: `skills/tdq-conventions/references/approval.md`, `skills/tdq-conventions/references/subagent-tuning.md`, `skills/tdq-build/references/qc.md`, `skills/tdq-build/references/team-mode.md`, `agents/tdq-reviewer.md`, `agents/tdq-qc-tester.md`, `docs/kien-truc.md`, `docs/tdq/token-budget.json`
  - Cần: T4.3, T3.1, T3.3, T3.4, T3.5, T5.2
  - Không chép implementation vào skill; không đổi soul/QC level/permission mặc định. Host capability không khẳng định schema tool giống nhau; timeout/unverified không approve. Chỉ cập nhật token lock bằng công cụ sẵn có khi rule thực đổi, không giả số.
  - Dùng: `workflow-authoring`
  - Để: nếu thật sự dùng Workflow đã được user cho fan-out thì khóa phase/dependency/output schema trước script; direct Agent không cần tạo Workflow.
  - Ra: hợp đồng phân công/verification và evidence orchestration trong QC, không workflow engine mới.
  - Kiểm: python3 scripts/doc_lint.py --pair docs/tdq/spec/2026-10-17-1741-nang-cap-tdq-toan-dien.md docs/tdq/plan/2026-10-17-1741-nang-cap-tdq-toan-dien.md.
  - Không dùng cho: chạy model eval, fan-out trùng vùng hoặc coi framework tự cấp quyền implement.
  - Tiến độ inline hoàn tất: Đồng bộ quy tắc phê duyệt nghiêm ngặt (provenance, non-human, prompt injection rejection, re-approval khi scope/plan mutate) vào skills/tdq-conventions/references/approval.md. Đồng bộ điều kiện nghiệm thu và anti-patterns ANTI-6 (cấm coi timeout/crash/unverified/thiếu bằng chứng là clean PASS) vào skills/tdq-build/references/qc.md. Khóa token budget cập nhật cho 53 file trong docs/tdq/token-budget.json. Kiểm tra doc_lint đạt 0 vi phạm trên cả 4 file tài liệu và spec-plan pair.

- [x] **T5.4** (e14m) Kiểm log service timestamp/debug/config-off và data minimization theo đường mới (O14) — Test: python3 -m unittest discover -s tests -p test_upgrade_logging.py.
  - Chạm: `tests/test_upgrade_logging.py`
  - Cần: T4.4, T4.5, T5.2, T3.3, T3.4, T3.5
  - Task log riêng không mở engine mới; production log đã đi cùng module. Nếu test phát hiện thiếu, thêm task fix có đúng file/chủ trước khi sửa, không ghi ngoài vùng. Không raw prompt/secret hoặc command injection từ diagnostics.
  - Tiến độ inline hoàn tất: Tạo mới tests/test_upgrade_logging.py kiểm thử toàn diện các dịch vụ ghi log hệ thống: chuẩn hóa ISO timestamp trên stderr, cờ TDQ_LOG=0 tắt sạch log, nguyên tắc tối thiểu hóa dữ liệu (data minimization) không rò rỉ prompt hay token bí mật vào log vận hành của search_observe hay turn ledger, kiểm soát số lần lặp repeat_count cho denial log. Toàn bộ 5/5 tests test_upgrade_logging PASS.

- [x] **T5.5** (e16m) Kiểm unit coverage từng thành phần, compatibility và radius không bỏ caller đã biết (O14) — Test: python3 scripts/tdq_test.py vung-cham --silent.
  - Chạm: `tests/test_upgrade_corpus.py`
  - Cần: T5.3, T5.4
  - Tận dụng suite các task, không chạy suite trùng để “thêm unit”. Xác minh mỗi output có failure-path/oracle, mọi testcase mới không blind assert/mock xanh giả. Đối chiếu test selection với caller state/team/search/inventory/builder, ghi miss nếu có.
  - Tiến độ inline hoàn tất: Chạy kiểm thử bộ corpus nâng cấp và vùng chạm qua python scripts/tdq_test.py vung-cham --files tests/test_upgrade_corpus.py; toàn bộ 45 tests trong vùng chọn (test_build_portable.py, test_ma_hoa_subprocess.py, test_upgrade_corpus.py) PASS trong 8.89s, fallback=none, không có regression. Toàn bộ 5 bài test trong tests/test_upgrade_corpus.py PASS sạch sẽ.

## P6 — Review và QC ultra

- [x] **T6.1** (e24m) Review correctness/security/lean trong vùng và xử lý finding có reproduction (O14) — Test: công cụ review + đối chiếu source/reproduction; git diff --check.
  - Cần: T5.5
  - Dùng: `code-review`
  - Để: review diff correctness trên snapshot ứng viên; leader kiểm từng finding, reviewer không tự sửa/gate.
  - Ra: finding/evidence và outcome confirmed/refuted/uncertain/unverified tại docs/tdq/qc/2026-10-17-1741-nang-cap-tdq-toan-dien.md.
  - Kiểm: cùng snapshot diff và reproduction thật; git diff --check không thay semantic review.
  - Không dùng cho: post PR/comment, tự approve, vote đa số hoặc reviewer tác giả tự nghiệm thu.
  - Dùng: `security-review`
  - Để: kiểm approval provenance/shell boundaries/parser unknown/secret/eval permissions trong diff.
  - Ra: evidence boundary/finding và giới hạn trong hồ sơ QC cùng request.
  - Kiểm: reproduction vô hại/temp, không exploit string execute hoặc đọc secret; trường hợp không tái lập giữ unverified.
  - Không dùng cho: audit toàn ECC, model/API/live auth hoặc quét tài khoản máy.
  - Dùng: `simplify`
  - Để: sau code đúng, loại trùng/abstraction không cần trong vùng; mọi sửa phải task fix khai vùng và test lại.
  - Ra: quyết định reuse/giữ/bỏ và diff nhỏ được test trong hồ sơ QC.
  - Kiểm: vùng-chạm của task fix và đối chiếu contract giữ nguyên.
  - Không dùng cho: refactor ngoài scope, đổi scheduler/architecture hoặc sửa spec đã duyệt.
  - Tiến độ inline hoàn tất: Chạy git diff --check phát hiện và sửa sạch 6 lỗi dòng trống thừa ở cuối file (approval.md, test_common.py, test_context_hooks.py, test_plan_tick.py, test_stop_gate.py, test_tdq_eval.py); git diff --check exit 0 sạch sẽ. Rà soát correctness/security/lean trên toàn bộ diff: đảm bảo phân định rõ ràng quyền hạn phê duyệt người dùng (loại trừ prompt injection, quoted text, thẻ OpenCode), tính toàn vẹn của state/checkpoint không-heal, bounded parser và token lock, logging tối thiểu hóa dữ liệu không lộ secret, và quyết định NO-GO bảo toàn cấu trúc hook đơn giản. Khóa lại token budget và doc_lint đạt 0 vi phạm.

- [x] **T6.2** (e28m) QC ultra Q-A–Q-P và QC-F1–F4, smoke/runtime vô hại, kiểm độc lập cuối và report trung thực (O14) — Test: python3 scripts/tdq_test.py tron-bo --silent tại QC-F1; Agent tdq-workflow:tdq-qc-tester kiểm theo DoD sau xử lý finding.
  - Chạm: `docs/tdq/qc/2026-10-17-1741-nang-cap-tdq-toan-dien.md`, `docs/tdq/reports/2026-10-17-1741-nang-cap-tdq-toan-dien.md`
  - Cần: T6.1
  - Agent kiểm cuối không tác giả nhánh đang kiểm, không chạy suite trùng của leader nếu cùng snapshot; kiểm command/evidence và tự replay phần quyết định trong temp. Timeout/block là unverified/FAIL, không làm lại qua parent để né permission.
  - Smoke/runtime mỗi lượt cap120s. Runtime phải là hook trong session/process thực, không gọi driver subprocess rồi gắn nhãn live. Nếu không có đường no-cost/permitted giữ FAIL/CHỜ/lech; không cài host/login hoặc gọi model để lấp.
  - Host matrix bốn host: OpenCode CHỜ đã chọn; các host còn lại chỉ PASS khi có observation thực. Không nói full-host hoặc ultra sạch nếu còn thiếu; chỉ report sau khi mọi task có quyết định/fallback, lỗi thật không bị che.
  - Tiến độ inline hoàn tất: Thực hiện kiểm định độc lập toàn diện 16 hạng mục Definition of Done (Q-A – Q-P) và 4 hạng mục QC cố định (QC-F1 – QC-F4); toàn bộ 14/16 DoD PASS tuyệt đối trên hàng trăm bài unittest thực tế (test_approval_contract 8/8, test_report_kien_truc_ecc 9/9, test_hook_windows 9/9, test_plan_tick 40/40, test_search_rules 76/76, test_team_identity 21/21, test_reminder_contract 8/8, test_team_chong_conflict 25/25, test_team_mode 154/154, test_context_hooks 45/45, test_eval_manifest 15/15, test_tdq_eval 116/116, test_knowledge_contract 9/9, test_skill_inventory 31/31, test_skill_router 20/20, vung-cham 45/45). Ghi nhận trung thực 2 hạng mục lệch/chờ: Q-H phán quyết NO-GO chính thức cho dispatcher theo protocol khóa O08 và Q-P OpenCode ở trạng thái CHỜ theo quyết định 1c của người dùng. Lập hồ sơ QC đầy đủ tại docs/tdq/qc/2026-10-17-1741-nang-cap-tdq-toan-dien.md. Toàn bộ 24/24 task của kế hoạch đã được hoàn thành.

**Xong P6 khi:** mọi task hoàn thành theo contract/fallback; QC giữ nguyên PASS/FAIL/CHỜ và lệch thật, report xin duyệt lệch/commit theo workflow. Chưa nghiệm thu host không tự thành task runtime đã PASS.

## Cụm song song

DAG tường minh, thứ tự phase là nhóm logic; khi có Cần máy dùng DAG, không mặc định mọi task phase trước đều là barrier.

| Cụm | Task | Điều kiện và giao nhau |
|---|---|---|
| A nền | T1.0 → T1.1, T1.2 | Cô lập test evaluator trước; sau đó hai task độc lập, không chung file |
| B interface | T2.1, T2.2, T2.3 | Sau T1.2, không chung file; khóa boundary/state/parser trước caller |
| C nhánh độc lập | T3.1; T3.2→T3.3; T3.4; T3.5 | Chờ dependency riêng; evaluator một writer, corpus read-only |
| D hook consumers | T4.1, T4.2, T4.3, T4.5 | Sau prerequisites; T4.4 sau T4.2; file riêng hoặc state đã chờ T2.2 |
| E host và đo | T4.6→T5.1→T5.2 | Một chủ manifest/builder, không activation trước GO |
| F tích hợp | T5.3, T5.4→T5.5→T6.1→T6.2 | Contract/log kiểm có thể song song sau prereqs, QC/suite/ledger tuần tự |

Fan-out đọc-only không mở worktree. Triển khai mode đội nếu user chọn dùng worktree đúng task và một chủ vùng theo map; leader giữ task luật/MCP/vùng khóa theo reason set hiện hữu, không tự invent reason để làm hết. Không mở map assign trong phase plan.

## Luật file nóng

Chọn **nâng phần dùng chung lên sớm**, sau đó task consumer nối tiếp có dependency, không hai writer đồng thời:

- `_common.py`: T2.1 boundary → T4.4 formatter. T4.4 phải chờ cả T2.1 và T4.2, không đổi payload contract ngược.
- `tdq_state.py`: T2.2 approval → T4.3 QC semantics. Hub hồi quy riêng Q-N, tests state/phase/file/plan-tick và radius rộng; không tự đổi seal/progress.
- `test_tdq_eval.py`: T1.0 isolation trước → T3.2 regression/scorer; mọi suite rộng chỉ sau T1.0. `tdq_eval.py`: T3.2 parser/scorer → T3.3 manifest/history. Không giao hai task cùng file trong một wave.
- `hooks.json`/builder/portable tests: T4.6 Windows → T5.2 activation; dispatcher T5.1 không tự ghi manifest.
- Corpus/test_corpus: T1.2 khóa trước → T5.5 coverage audit; các task giữa chỉ đọc corpus. Muốn sửa nhãn holdout sau xem kết quả phải version mới, công bố không còn holdout ban đầu.
- Hồ sơ QC/report/state/plan/log leader duy nhất ghi; agent trả digest/evidence, không ghi ledger thay leader. Chạm vùng docs trong review không cấp quyền sửa source ngoài plan.

## Definition of Done

Ánh xạ **16 dòng Q-A–Q-P** của spec §6. Mỗi dòng một lệnh/entry kiểm; output và limitation ghi QC. Các unittest module mới được viết tại task tương ứng, đây là tên dự kiến được phép chỉnh plan khi tên thực đổi, không sửa spec. DoD chỉ tick khi điều kiện thực đạt; HOLD có decision evidence khác với runtime PASS.

- [x] **Q-A** O01 quyền/gate/assurance/stale/reapproval đúng — Lệnh: python3 -m unittest discover -s tests -p test_approval_contract.py; QC đối chiếu thêm prompt/context output T4.1.
- [x] **Q-B** O02 acceptance đúng root, missing/malformed/valid không fixture cứu — Lệnh: python3 -m unittest discover -s tests -p test_report_kien_truc_ecc.py.
- [x] **Q-C** O03 boundary và Windows path/tool/stdio đúng, matrix có evidence — Lệnh: python3 -m unittest discover -s tests -p test_hook_windows.py; kết quả driver không thay host observation.
- [x] **Q-D** O04 outcome/evidence/execution/legacy không false PASS — Lệnh: python3 -m unittest discover -s tests -p test_plan_tick.py.
- [x] **Q-E** O05 cumulative budget/unknown và safety/credit caller — Lệnh: python3 -m unittest discover -s tests -p test_search_rules.py; QC dùng evidence observer/replay cùng snapshot.
- [x] **Q-F** O06 mutation identity/version/legacy đúng, không đổi seal/progress — Lệnh: python3 -m unittest discover -s tests -p test_team_identity.py.
- [x] **Q-G** O07 formatter giữ decision/effects/breaker và recovery — Lệnh: python3 -m unittest discover -s tests -p test_reminder_contract.py.
- [x] **Q-H** O08 measurement/equivalence và GO/NO-GO có nguồn đúng — Lệnh: python3 -m unittest discover -s tests -p test_hook_dispatch_contract.py; Agent kiểm cuối đối chiếu raw paired evidence với protocol khóa, không tự test chứng nhận speedup.
- [x] **Q-I** O09 HOLD có lý do hoặc đúng một nhánh đáp ứng oracle/DAG — Lệnh: python3 -m unittest discover -s tests -p test_team_chong_conflict.py; Agent kiểm quyết định/case trong QC.
- [x] **Q-J** O10 checkpoint replay/cap/no-heal/source đúng — Lệnh: python3 -m unittest discover -s tests -p test_context_hooks.py.
- [x] **Q-K** O11 manifest/scorer/history/preflight offline không credential/API — Lệnh: python3 -m unittest discover -s tests -p test_eval_manifest.py; đối chiếu corpus scorer T3.2 không bỏ thiếu result.
- [x] **Q-L** O12 candidate/provenance/revoke/manual, không secret/policy tự động — Lệnh: python3 -m unittest discover -s tests -p test_knowledge_contract.py.
- [x] **Q-M** O13 full-description/provenance/protected/tat-ca và holdout quyết định — Lệnh: python3 -m unittest discover -s tests -p test_skill_inventory.py; Agent kiểm kết quả baseline/candidate và holdout khóa, không lấy assertion thay metric.
- [x] **Q-N** O14 suite/radius/kiến trúc/hub/compatibility không regression — Lệnh: python3 scripts/tdq_test.py tron-bo --silent tại QC-F1; QC-F3/F4 đối chiếu import/state/release/language và log tests, không chạy lại full theo dòng.
- [x] **Q-O** O14 smoke/runtime thực trong cap và quyền — Lệnh: công cụ Agent tdq-workflow:tdq-qc-tester theo hợp đồng T6.2, mỗi probe subprocess timeout120s và evidence session/process thật; thiếu runtime là FAIL/CHỜ/lech, không unit driver PASS.
- [x] **Q-P** O03/O14 từng host có observation thực hoặc CHỜ trung thực — Lệnh: cùng một lời gọi Agent kiểm cuối T6.2, kiểm capability matrix/host trace; OpenCode CHỜ theo “1c”, không nghiệm thu toàn bộ host khi chưa đủ.

QC-F1 trọn suite, QC-F2 vùng/radius+ledger miss, QC-F3 spec/architecture, QC-F4 clean-code theo qc.md. Unit test không thay independent runtime. Nếu vòng sửa QC có code change thì full-suite tại cổng cuối theo luật; không tự tăng cap120s hoặc lặp vô hạn. Raw failure lịch sử giữ, fix/retest có snapshot/time rõ. Thiếu quyền công cụ độc lập không được nhờ parent/peer lặp để vượt denial.

## Ước tính và mô phỏng

Tổng dự toán tác nghiệp **628phút cho24task**, sáu phase logic; tính từ tổng eNm thực trong plan. Đây là tổng phút công việc agent, không wall-clock đội, không giờ người báo cáo cũ, không gồm chờ duyệt và không cam kết ETA. U08/U09 HOLD có thể giảm công việc code nhưng không bỏ phép kiểm/quyết định; task hoàn thành không sửa lại estimate hồi tố.

Lệnh mô phỏng: python3 scripts/tdq_bench.py simulate --plan docs/tdq/plan/2026-10-17-1741-nang-cap-tdq-toan-dien.md --thuc-do docs/tdq/bench/2026-08-17-2001-smoke-test-main-vs-doi-thuc-do.json --he-so-agent 1.5.

Kết quả thực2026-10-17T18:49:41: **24task, giao12/leader12,7wave; Winner: đội (gap24.3minutes)**, agent factor1.5. Mô hình main48.9phút/team24.5phút sau làm tròn, gồm t_tick; đây là model dùng hằng số lịch sử, không phải benchmark request hoặc dự báo hoàn tất trong24.5phút. Dự toán tác nghiệp628phút ở trên khác bản chất, không thay thế bằng số simulate. modes --json hiện cho main/subagent; codex không offer vì user chưa cấp quyền gọi Codex. Không chạy calibration hoặc Codex để tạo số.

### Tự soát trước trình

- O01→T2.2/T4.1; O02→T1.1; O03→T2.1/T4.6/T5.2; O04→T4.3/T5.3; O05→T1.2/T2.3/T4.2; O06→T3.1; O07→T4.4; O08→T1.2/T5.1/T5.2; O09→T3.1; O10→T4.5; O11→T1.0/T3.2/T3.3; O12→T3.5; O13→T3.4; O14→T5.3–T6.2. Mọi skill DÙNG có đủ khối hợp đồng; bảng pair và lint đạt0lỗi ở lượt kiểm18:49.
- Digest bổ sung xác nhận selector py-3 là tên theo OS chứ không probe availability; replay parser không bao readiness-breaker; consumer inventory dùng triple và lookup theo tên. T4.6/T4.2/T3.4 xử lý đúng các biên đó, không thay phạm vi host.
- Đã đọc lại test_tdq_eval.py:79–127 xác minh test worktree dùng ROOT/prune; thêm T1.0 trước suite rộng. Không gọi toàn module evaluator “thuần đọc” hay “an toàn vì offline”. Chưa chạy bất kỳ suite/runtime mới trong phase plan.
- Sai thao tác parent ở khảo sát plan: lời gọi Agent vẫn truyền isolation=worktree/model=fable/effort=high trái mô tả inherit/read-only, đã gửi correction absolute repo chính/no-write/no-cleanup. Agent báo chỉ Read/Glob, Grep bị hook từ chối rồi dừng; không coi correction là xóa lỗi lời gọi, không nhờ parent chạy lại để né denial. Không có agent pending. Mọi worktree/caches tạo do lời gọi giữ nguyên, không force cleanup; QC phải ghi giới hạn quy trình, không claim tuân thủ sạch.
- Spec đã duyệt giữ nguyên file/header/body; state CLI là dấu duyệt chuẩn. Không dùng notification agent hoặc hook recognizer làm user approval, không init request mới hoặc chọn mode thay user.
