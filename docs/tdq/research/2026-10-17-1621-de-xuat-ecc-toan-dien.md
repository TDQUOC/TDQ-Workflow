# RESEARCH — Hồ sơ bằng chứng nâng cấp ECC → TDQ toàn diện hơn
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

Ngày: 2026-10-17 · Request: `2026-10-17-1621-de-xuat-ecc-toan-dien` · O1
Phạm vi: nghiên cứu chỉ đọc, kiểm cô lập TDQ; không triển khai nâng cấp.

## 1. Snapshot và cách đọc chứng cứ

| Thành phần | Giá trị |
|---|---|
| TDQ chính | `C:/Users/admin/Documents/Projects/ForAgentCode/TDQ-Workflow` |
| TDQ HEAD | `1d78ca86ca5b0710f357d8436ec7d9d2d7562b54` |
| ECC chỉ đọc | `C:/Users/admin/Documents/ECC` |
| ECC HEAD | `76aaa77df6adc5b889e689007bf99b9a4f74af34` |
| Nhánh request | `docs/de-xuat-ecc-toan-dien`, gốc `docs/deep-research-kien-truc-ecc` |
| Môi trường đo mới | Windows 11 build 26100; Python 3.13.15, `sys.platform=win32`; Bash làm driver, tiến trình con Python Windows; không phải smoke toàn bộ PowerShell host |
| Thời điểm smoke mới | 2026-10-17T16:53:18+07:00 |
| Quyền | full/main/ultra đã được duyệt; không quyền sửa runtime, eval trả phí, commit/push |

Nhãn: **S** = đọc nguồn/manifest; **T** = thấy test có oracle, chưa đồng nghĩa test chạy ở request này; **X** = thực thi TDQ thật có input/output mới; **H** = kết quả lịch sử có snapshot; **M** = mô hình/ước lượng; **?** = chưa xác minh/định lượng. Không có phép thực thi ECC trong request này. Code tồn tại và được nối entry point không chứng minh tính năng đã được người dùng triển khai hoặc hiệu quả production.

Nguồn cũ: `docs/tdq/research/2026-10-17-1442-de-xuat-nang-cap-tu-ecc.md` (H1), report và QC cùng slug. H1 đo TDQ `5c8a9c22a42a59c5a2e0f2941ed92bced36e9df3`, ECC cùng HEAD hiện tại. Lệnh `git diff 5c8a9c22a42a59c5a2e0f2941ed92bced36e9df3..HEAD --name-only -- hooks scripts tests skills agents` trả rỗng; không có source diff trong vùng đó. Đây là lý do tái sử dụng source/đo nền, **không** đổi timestamp benchmark cũ thành mới.

Hash SHA-256 mới của nguồn quyết định:

| File TDQ | SHA-256 |
|---|---|
| `hooks/hooks.json` | `4e1bfc6757fdd47925c969c7e09a1c964b82e5435548da530b59137bc3ef90b3` |
| `hooks/scripts/prompt_context.py` | `f738bd7fd4941d930f8161e877f687666c137fba283509b815f6833d603d4bbc` |
| `hooks/scripts/session_start.py` | `349779cf85f5d10fdd6253d608bee5980bf45eceabc1185217ab4dbc5eac5c32` |
| `scripts/tdq_eval.py` | `8adf95b9d795fbcacf6ad4bf2adb269f2ae789128eb3e17dbb59cbd9b0d873ee` |

LSP Python đã khởi động; `cham_phien` có references source/test. Markdown bị LSP nhận prose thành symbol nên blast-radius tài liệu không dùng làm quan hệ runtime. Setup và kiểm hiệu ứng tìm kiếm đã làm trong analyze; graph được refresh, không chạy lại mỗi bước. Graph không thay source/manifest. Hai digest khảo sát độc lập theo nhóm được dùng làm chỉ mục, leader kiểm các claim quyết định và loại claim sai tại §4.

Đầu request đã có thay đổi `.tdq-phat-hanh.json`, `STATE.md`, `timing.jsonl`, working log. Refresh tạo thay đổi `graphify-out/graph.json`, `manifest.json`; không coi là sản phẩm nâng cấp hoặc tự đưa vào commit. LSP từng sửa pyrightconfig ngoài ý muốn, đã phục hồi nguyên byte và gỡ backup do tool tạo. Hai lời gọi khảo sát từng truyền isolation thừa trái hợp đồng; đã yêu cầu chỉ đọc absolute repo chính. `git worktree list` sau chúng chỉ còn repo chính. Không che sai thao tác này bằng kết luận tuân thủ tuyệt đối; không dùng worktree snapshot làm evidence. Tại QC, ba lời gọi reviewer lại truyền isolation thừa và override opus trái inherit. Reviewer thiết kế quan sát worktree ở HEAD `6ddd1a408197db87ea675942362558fd34f76375`, khác repo chính; họ xác nhận đọc absolute repo chính. O3 giữ FAIL lịch sử và deviation #1 CLI Q10 ánh xạ Q-J; lời gọi kiểm cuối cũng lặp sai isolation/model và được ghi vào cùng lệch. Một reviewer khởi LSP nhầm worktree tạo untracked pyrightconfig; worktree đó được giữ công khai không force cleanup. Kết quả sản phẩm không xóa vi phạm thao tác.

## 2. Năm trụ cột và D01–D10: bằng chứng còn hiện hành

Nguồn ECC trong các bảng tương đối với root ECC; TDQ tương đối root TDQ. H1 §4 có chi tiết nguồn/cơ chế; leader đọc lại recognizer, matcher, đối chiếu source delta và nguồn quyết định. Những phần không chạy mới giữ nhãn S/H.

| Cũ | TDQ đã có / khoảng thiếu | Cơ chế ECC và quan hệ | Trạng thái, quyết định |
|---|---|---|---|
| D01 approval | `hooks/scripts/prompt_context.py:40-83,91-117`: recognizer từ text, LETTER chỉ chữ; không có provenance trong hàm | `workflows/orch-review.workflow.js:64-108,245-287` outcome/evidence có cấu trúc; **không** phải bản vá host approval sẵn | S/H1-M7: `1a` false, notification chứa spec approved có thể true; CLI hiện vẫn là nơi ghi duyệt. Giữ ưu tiên nguồn tin, không auto-grant regex |
| D02 artifact | `tests/test_report_kien_truc_ecc.py:211-225`: fixture fallback khi artifact vắng | `workflows/orch-review.workflow.js:248-255,280-283`: null/lỗi verifier không được approve | S/H: tách unit validator/acceptance; không diễn giải suite xanh là sản phẩm tồn tại |
| D03 Windows/host | `hooks/hooks.json:58-71,104-110`; search gate match PowerShell nhưng post observer không; `search_rules.py:646-668` recognition có PowerShell | `scripts/lib/windows-bash.js:19-46,57-85`; `pre-bash-commit-quality.js:263-307` có đường Node Windows riêng | S/H1-M2/M4: coverage không đồng nhất, không phải TDQ hoàn toàn không biết PowerShell; không kết luận CVE tương đương |
| D04 review | `skills/tdq-build/references/qc.md:34-40,73-84,97-110`: ultra reviewer độc lập/evidence đã có | `workflows/orch-review.workflow.js:220-287`: dedup/skeptic, uncertain/unverified | S: học outcome/giới hạn phản biện, không thêm reviewer thứ hai như tính năng mới; confidence .8 không là 80% accuracy |
| D05 parser | `scripts/search_rules.py:159-242`: depth cap/recognition, chưa thấy work budget tổng trên đường khảo sát | `scripts/hooks/lib/shell-scan.js:6-12`: `24*(L+1)+4096` | S/H: kiểm input type/length/work/output, unknown theo caller. Không coi scanner là sandbox hoặc bảo đảm mọi helper tuyến tính |
| D06 identity | `scripts/tdq_state.py:569-589` hash thân approval; `tdq_team.py:345-350,375-377,396` hash plan team | `scripts/lib/context-carriers.js:146-170`: descriptor proposed/inactive có các digest và yêu cầu revalidate; enforcement ở `scripts/lib/context-profile-store.js:181-198,225-238` kiểm file và dựng/so carrier trước apply/materialization | S: assignment/progress projection là đề xuất TDQ; chỉ bỏ header không bỏ tick; ưu tiên theo replay stale thực |
| D07 noise | `hooks/scripts/search_gate.py:43-44,126-129` breaker missing readiness; gate/task/team vẫn riêng | `gateguard-fact-force.js:1613-1634` denial rút ngắn, `gateguard-code-lexer.js:307-315` signature | S: học format/dedupe, không nhập trivial bypass hay hạ block sau N lần |
| D08 latency | `hooks/hooks.json:38-112`: Bash pre 2 command, Edit pre 1; observer pre/post LSP chủ đích chịu lỗi | `scripts/hooks/bash-hook-dispatcher.js:22-52,123-174` gọi `.run(rawInput)` nội trình | S/H1-M1/M2: chỉ thử cùng event sau đo critical path; chưa có dispatcher TDQ chạy |
| D09 dependency/lifecycle | `tdq_team.py:215-312,662-744,804-898`: DAG, same-file exclusion, lifecycle, conflict probe | `scripts/lib/agent-proximity/distance.js:1-315`, `scripts/lib/worktree-lifecycle/git.js:125-144` noisy-OR / merge-tree | S/H1-M6: giữ DAG và file lock; advisory/probe chỉ khi có conflict lịch sử/case cụ thể |
| D10 cache | `tdq_team.py:698-700,931-951`: dọn rác/runtime host không phải dependency cache | `ecc2/src/worktree/mod.rs:1200-1405` hash manifest/lock + directory link | S: shared writable link không an toàn mặc định; chưa có consumer nặng/measurement, hoãn feasibility |

## 3. Tám nhóm bổ sung: không phải tám tính năng mới

### G1 — Ngữ cảnh và bàn giao

- TDQ S/T/X: `hooks/scripts/session_start.py:192-198,224-257` đọc state → render → law theo phase → compact anchor → cap → rewrite lệnh. `hooks/hooks.json` nối SessionStart. `tests/test_context_hooks.py:145-169` có oracle lazy load/compact. X1 dưới đây chạy entry point thật.
- ECC S/T: `hooks/hooks.json` nối `suggest-compact` tại PreToolUse Edit|Write và `pre-compact` tại PreCompact. `scripts/hooks/suggest-compact.js:15-80` dùng usage/tool-count; `pre-compact.js:59-90` chọn session cùng worktree, `:141,154-172` thực gọi `generateSessionSummary` và ghi summary qua `scripts/lib/llm-summary.js`. Test `tests/hooks/pre-compact.test.js` có kiểm cô lập session, chưa chạy tại đây.
- Khoảng học: handoff gọn, có provenance và task đang làm/blocker/next-check. Anchor hiện có request/phase/plan, không phải full working context. Chưa đủ bằng chứng để kết luận cần hook đếm tool call hay tự summary LLM. Ngưỡng tool count không đồng nghĩa token window.
- Tối thiểu: thử checkpoint dẫn xuất từ state/plan đã có, không đọc transcript cá nhân, không viết state thứ hai. Giữ nguyên nếu replay compact không cho thấy thiếu thông tin; không thêm pre-tool hook mặc định.

### G2 — Bài học và memory

- TDQ S: `docs/tdq/knowledge/` có tài liệu; rules/reminder là tri thức được biên soạn. Đây không phải bằng chứng TDQ đã có vault/auto-learning. Memory của host bên ngoài repo không được đồng nhất thành runtime TDQ.
- ECC S/T: `scripts/memory.js:51,60-77` CLI/handoff và unreviewed context; `scripts/lib/memory-vault-format.js:5-18,31-60` schema/scopes/unreviewed/status/secret patterns. Test `tests/lib/memory-vault.test.js`, `tests/scripts/memory.test.js` tồn tại theo khảo sát. `skills/continuous-learning-v2/scripts/instinct-cli.py:128-133,1592-1684,2158-2202` có promotion/prune; **đây là module khác memory-vault**, không gộp chúng thành một trust pipeline đã chứng minh end-to-end.
- Giới hạn Windows S: `instinct-cli.py:44-48,415-428` bỏ `fcntl` trên Windows ở helper được đọc; chưa chứng minh mọi ghi đều không khóa hoặc đã xảy ra corruption. .8 là heuristic, TTL là chính sách chứ không phải độ đúng.
- Học tối thiểu: bài học ứng viên có nguồn/điều kiện/duyệt/thu hồi; không tự tiến hóa thành luật, không quét transcript nền. Secret regex chỉ giảm rò rỉ mẫu đã biết, không bảo đảm sạch dữ liệu.

### G3 — Đánh giá lặp

- TDQ S/X: `evals/tuan-thu/README.md:5-47` mô tả 12 ca; `scripts/tdq_eval.py:44-57,93-111,624-677,717-745` có setup/run/score/report và subprocess model thật; `NHANH` hardcode hai commit lịch sử, `MODEL` cấu hình trong source. Không chạy setup/run trong request này. **Gap Windows đã xác minh tĩnh:** `lenh_chay` gọi `lay_token()` vô điều kiện (`tdq_eval.py:883-899`); `lay_token:679-689` chạy `security find-generic-password` đọc macOS Keychain, `chay_phien:717-730` cũng fallback helper đó. Offline scorer/rescore được smoke không chứng minh real-run CLI dùng được trên Windows. U03 phải xác định auth/launcher contract không lộ secret, U11 mới tích hợp trước một live eval được duyệt; không đọc credential hoặc gọi helper này ở đây. Phần auth Windows chưa nằm estimate scorer/manifest U11 hay coverage P0 U03, phải scope/ước lượng riêng khi được giao. `cham_phien` dùng chung parser/scorer, X1 kiểm 4 trace synthetic, không phải eval chất lượng model.
- ECC S: `scripts/eval-harness.js:1-60` capsule/receipt/gate; `ecc2/src/harness_eval.rs:185-200,488-530` candidate identity/paired sample/promotion policy. Nguồn Rust là subsystem riêng, không chứng minh plugin mặc định dùng nó.
- Học tối thiểu: manifest thí nghiệm bất biến (candidate/base commit, corpus/check-set version, host/model/quyền, missing/skip), CLI generic khi cần; giữ engine Python. Sign test một phía có giả định, nhiều metric/post-hoc cần tách; p<.05 không tự bảo đảm agent tốt.

### G4 — Hậu kiểm trace

- TDQ S/X: `scripts/tdq_eval.py:182-217,325-389,408-421,624-631` lưu thứ tự và **đã** kiểm temporal L003/L005/L013. `scripts/step_audit.py:1-43` phân tích chi phí/bước/đọc lặp, không đồng nghĩa validator tuân thủ đầy đủ.
- ECC S: `skills/skill-comply/scripts/grader.py:28-76,79-116,119-140` phân loại LLM rồi kiểm before/after và hạ kết quả phụ thuộc prerequisite thất bại. `runner.py:17-60` dùng sandbox POSIX theo khảo sát; chưa kiểm portability Windows. Skill có supportive/neutral/competing prompts, đó là thiết kế bộ ca.
- Khoảng học: trace identity/task/tool-result/unknown rõ và phụ thuộc chứng cứ; **không** thiếu hoàn toàn thứ tự. Chưa chứng minh TDQ cần DSL tổng quát. X1 cho thấy missing là N/A, không được cộng PASS; null/[] chưa type-validate. Nên mở rộng oracle theo lỗi thật, tái dùng scorer, không LLM judge mặc định.

### G5 — Định cỡ/rủi ro

- TDQ S: `skills/tdq-intake/SKILL.md:17-32` bốn điều kiện tier nhỏ; `references/lane-decision.md:20-31` có sáu tiêu chí và **đã** có data/security/public API/money; bất kỳ ô deep nào → đề xuất deep. CLI `tdq_state.py` ghi lane/gate, không tự xác minh agent phân loại rủi ro đúng.
- ECC S: `skills/orch-pipeline/SKILL.md:1-80` hướng dẫn bốn cỡ và tie-breaker security/public contract. Không từ việc đây là guideline suy rằng toàn ECC không có state machine.
- Kết luận: giữ nhỏ + quick/full; không thêm Standard lane hoặc risk engine. Chỉ cần ví dụ calibration nếu hồi quy intake chỉ ra lỗi; không đề xuất lại security tie-breaker đã có. Không tự hạ QC/lane.

### G6 — Skill chuyên ngành và tìm đúng năng lực

- TDQ S: `scripts/skill_inventory.py:210-236,239-274` quét nguồn được cài, substring casefold, giữ nguồn protected; `skills/tdq-intake/references/skill-inventory.md:1-60` DÙNG/NỀN/KHÔNG; `skills/tdq-build/references/rules/index.md:33-55` lazy load ngôn ngữ. Inventory trên đĩa không cấp quyền gọi skill không user-invocable.
- ECC S: `scripts/lib/context-retrieval.js:3-15,17-33,38-101` BM25F + hashed character n-gram/RRF, deterministic/offline; `scripts/dev/generate-skill-triggers.js:1-76` sinh trigger dev-time có model; `scripts/hooks/context-routing-index.js:1-26` là module cần phân biệt với registry/manifest nối thật ở host. Không thấy tên module này trực tiếp trong manifest được đếm nên không tuyên bố luôn tự chạy.
- Khoảng học: chuẩn hóa identifier và corpus truy vấn có nhãn; giữ protected source và quyền dùng. Tokenizer ECC `/[^a-z0-9]+/` không thể chép mù cho tiếng Việt. n-gram giúp hình thái, **không** suy ra true synonyms (source tự nói rõ). Chỉ thêm retrieval phức tạp khi baseline misses được chứng minh.

### G7 — Nhiều phiên/harness

- TDQ S/T: `tests/test_adapter_host.py:1-60` mô tả/kiểm adapter mỏng đa host; `agents/tdq-implementer.md` cùng `scripts/tdq_team.py` sử dụng worktree và host lifecycle; SessionStart phục hồi state. Có hỗ trợ nhiều host không đồng nghĩa mọi hook có parity hoặc concurrent writes đã an toàn.
- ECC S: `ecc2/src/session/manager.rs:1-140`, `ecc2/src/session/daemon.rs:1-60` có session manager/daemon trong subsystem Rust. Không chạy daemon, không xác minh vận hành Windows.
- Kết luận: không xem thiếu daemon là defect. Nếu cần, metadata handoff gộp G1, host parity gộp D03, concurrent ownership vào D06; không xây SQLite/control plane/cron. Không tuyên bố hoãn là tiết kiệm 3–4 tuần đã đo.

### G8 — Model theo vai trò

- TDQ S: `agents/tdq-implementer.md:1-6`, `tdq-qc-tester.md:1-7`, `tdq-reviewer.md:1-6`: inherit/high; `skills/tdq-conventions/references/subagent-tuning.md:6-37` đã có override theo task.
- ECC S: ba mẫu code-architect/code-reviewer/tdd-guide dùng sonnet, **nhưng** `agents/architect.md:5` opus và `agents/conversation-analyzer.md:4`, `comment-analyzer.md:4`, `doc-updater.md:5` haiku. Vì thế ECC cũng phân model theo role, không phải toàn sonnet.
- Giới hạn tài liệu TDQ S: tuning dòng 11/57 nói Agent không có effort param; schema công cụ phiên hiện tại **có** effort. Đây là lệch tài liệu/harness cần ghi trong parity inventory D03, không sửa source/skill ở đây. High không đồng nghĩa mức tối đa, inherit không bảo đảm model mạnh nhất. Chưa có eval để kết luận cấu hình nào chất lượng hơn.
- Kết luận: giữ inherit/override hiện có, kiểm đúng capability theo host; không thêm model router/tự downgrade hoặc gán savings token.

## 4. Các claim khảo sát bị sửa, không chuyển tiếp thành kết luận

| Claim ban đầu | Xử lý và nguồn |
|---|---|
| TDQ chưa phát hiện compact | Bác: `session_start.py:239-245`, X1 |
| TDQ chưa kiểm trước/sau | Bác: L003/L005/L013, X1; chỉ cân nhắc phủ oracle/trace thiếu |
| TDQ chủ yếu phân lane theo file/time, thiếu security tie-breaker | Bác: lane-decision:27,31 đã có |
| ECC tất cả agent sonnet, TDQ vì high/inherit nên vượt trội | Bác bằng architect/haiku và semantics tuning; không có eval chất lượng |
| ECC retrieval khắc phục đồng nghĩa tổng quát | Bác: context-retrieval:9-11; tokenizer ASCII cần điều chỉnh tiếng Việt |
| TDQ không có mọi memory động / ECC vault+instinct là một pipeline | Thu hẹp: vùng khảo sát không chứng minh auto-learning TDQ; hai subsystem ECC không gộp proof |
| Hoãn daemon tiết kiệm ít nhất vài tuần | Loại: không có estimate phạm vi/baseline, không phải tiền/thời gian thực tiết kiệm |
| Không có rủi ro kỹ thuật khi sửa guideline | Loại: có rủi ro drift, phân loại quá mức, nới quyền gián tiếp |

## 5. X1 — Smoke mới trên entry point TDQ thật

Trước viết O1, `doc_lint.py <O1>` trả exit 2 `not found`: thiếu sản phẩm thật, không dựng test đỏ. Smoke stdlib có oracle công khai trước; Python `-I` import source TDQ được phép vào memory, không chạy ECC. Không gọi `dung_sandbox`, `chay_phien`, token/API hoặc transcript riêng. Driver ở stdin; bytecode off. Temp state chỉ qua **CLI tdq_state.py**. Cwd/TDQ_PROJECT_DIR của mọi con là temp; không `.git` nên SessionStart không tự update project; thêm hai cờ tắt setup và chạm máy. Mỗi con timeout 30s, toàn driver 120s, không nâng trần.

Input scorer: tool-use/result synthetic, Write/Edit plan tick T1.1, Bash `python -m pytest tests/test_demo.py` **chỉ là chuỗi trong transcript, không được thực thi**. Oracle: đúng ~→đỏ→xanh→x là đạt L003/L005; đảo thứ tự vi phạm; thiếu trace N/A; chỉ xanh vi phạm L005. Compact oracle: startup không anchor; compact có request/phase/plan/ANTI-6. Đây không đo chất lượng của agent thật.

Output thô mới (2026-10-17T16:53:18+07:00):

```text
SCORER ordered {'L003': 'dat', 'L005': 'dat'} MATCH True
SCORER reversed {'L003': 'vi-pham', 'L005': 'vi-pham'} MATCH True
SCORER missing {'L003': 'khong-ap-dung', 'L005': 'khong-ap-dung'} MATCH True
SCORER green-only {'L003': 'khong-ap-dung', 'L005': 'vi-pham'} MATCH True
SCORER_BOUNDARY empty LoiThieuSo
SCORER_BOUNDARY malformed LoiThieuSo
SCORER_BOUNDARY null AttributeError
SCORER_BOUNDARY array AttributeError
TEMP_STATE_CLI 0
HOOK startup exit 0 anchor False details False chars 788 lines 11
HOOK compact exit 0 anchor True details True chars 1085 lines 14
```

Rỗng/lỗi JSON có lỗi chủ đích, null/[] là giới hạn schema có thật, **chưa vá**. Hook valid sau các input scorer lỗi vẫn đạt ở đường riêng; không suy hai module dùng chung recovery. Scorer tiếp tục qua malformed tới hook vì driver bắt ngoại lệ để quan sát. Không coi mọi missing là PASS, không chấm chất lượng nhờ synthetic nhỏ. Smoke phase analyze không chứng minh anchor không bị cắt trong mọi tổ hợp ultra/long-path/law; request sau cần boundary đó. Số chars bao gồm đường dẫn tuyệt đối sau cap nên không so mù với budget nội dung.

### Driver tái lập đầy đủ

Chạy Bash từ repo chính; không tạo code file trong repo. Source ECC không được import/thực thi.

```bash
python3 -I - <<'PY'
import sys, os, json, tempfile, subprocess, importlib.util, pathlib, datetime
root=pathlib.Path('C:/Users/admin/Documents/Projects/ForAgentCode/TDQ-Workflow')
os.environ['PYTHONDONTWRITEBYTECODE']='1'; sys.dont_write_bytecode=True
spec=importlib.util.spec_from_file_location('scorer',root/'scripts/tdq_eval.py'); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
def trace(items):
 out=[]
 for i,(name,inp,res,err) in enumerate(items):
  out += [{'type':'assistant','message':{'content':[{'type':'tool_use','id':str(i),'name':name,'input':inp}]}},{'type':'user','message':{'content':[{'type':'tool_result','tool_use_id':str(i),'content':res,'is_error':err}]}}]
 return out
red=('Bash',{'command':'python -m pytest tests/test_demo.py'},'1 failed',True)
green=('Bash',{'command':'python -m pytest tests/test_demo.py'},'1 passed',False)
tick=lambda x:('Edit',{'file_path':'docs/tdq/plan/demo.md','new_string':f'- [{x}] **T1.1** demo'},'',False)
rows=[('ordered',[tick('~'),red,green,tick('x')],{'L003':'dat','L005':'dat'}),('reversed',[tick('x'),green,red,tick('~')],{'L003':'vi-pham','L005':'vi-pham'}),('missing',[],{'L003':'khong-ap-dung','L005':'khong-ap-dung'}),('green-only',[green],{'L003':'khong-ap-dung','L005':'vi-pham'})]
print('STAMP',datetime.datetime.now().astimezone().isoformat(timespec='seconds'),'PYTHON',sys.version.split()[0],sys.platform)
with tempfile.TemporaryDirectory(prefix='tdq-ecc-evidence-') as td:
 p=pathlib.Path(td); env=dict(os.environ,TDQ_PROJECT_DIR=td,TDQ_KHOI_TAO_NEN='0',TDQ_KHONG_CHAM_MAY='1',PYTHONDONTWRITEBYTECODE='1')
 for name,items,want in rows:
  f=p/(name+'.jsonl'); ev=trace(items) or [{'type':'result','result':''}]; f.write_text('\n'.join(json.dumps(x) for x in ev),encoding='utf-8')
  got=m.cham_phien({'kiem':['L003','L005']},str(f))['ket_qua']; print('SCORER',name,got,'MATCH',got==want); assert got==want
 for name,content in [('empty',''),('malformed','{'),('null','null'),('array','[]')]:
  f=p/(name+'.jsonl'); f.write_text(content,encoding='utf-8')
  try: m.cham_phien({'kiem':['L003']},str(f)); result='accepted'
  except Exception as exc: result=type(exc).__name__
  print('SCORER_BOUNDARY',name,result)
 cp=subprocess.run([sys.executable,str(root/'scripts/tdq_state.py'),'set','active_request=2026-10-17-0000-synthetic','lane=full','phase=analyze','plan_file=docs/tdq/plan/demo.md'],cwd=td,env=env,capture_output=True,text=True,encoding='utf-8',timeout=30)
 print('TEMP_STATE_CLI',cp.returncode); assert cp.returncode==0,(cp.stdout,cp.stderr)
 for source in ['startup','compact']:
  q=subprocess.run([sys.executable,str(root/'hooks/scripts/session_start.py')],input=json.dumps({'cwd':td,'session_id':source,'source':source}),cwd=td,env=env,capture_output=True,text=True,encoding='utf-8',timeout=30)
  present='[TDQ:ANCHOR]' in q.stdout; details=all(x in q.stdout for x in ['2026-10-17-0000-synthetic','phase=analyze','docs/tdq/plan/demo.md','ANTI-6'])
  print('HOOK',source,'exit',q.returncode,'anchor',present,'details',details,'chars',len(q.stdout),'lines',len(q.stdout.splitlines())); assert q.returncode==0 and present==(source=='compact'); assert source!='compact' or details
PY
```

## 6. Định lượng: lịch sử, mô hình và dữ liệu còn thiếu

H1 §2 giữ toàn bộ dữ liệu thô/lệnh M1: Python noop median **21.346ms**, observer nonconcept **54.825ms**, LSP **55.887ms**, n=12/case; p95 nearest-rank tương ứng 22.459/56.006/57.134ms, với n=12 là max. Không dùng làm SLA hoặc tiết kiệm toàn bộ observer; host scheduling chưa đo. Tái tính mẫu noop ở H1: median của 21.329 và 21.364 =21.3465, biểu diễn Python round từ dữ liệu gốc làm tròn 3 số là 21.346 theo kết quả lịch sử; không suy độ chính xác microsecond từ số đã làm tròn.

Mô hình thành phần đơn giản: `saving_ms = N * k * 21.346 - overhead_ms`; với k=1, N=20/50/100 và overhead=0 → 426.920/1067.300/2134.600ms. Đây là **mô hình đơn giản mới từ median đã làm tròn**, không thay bảng scenario H1/report cũ dùng input overhead/count khác; không cộng hai bảng. Critical-path có thể không tăng hoặc âm. Không lượng hóa token/tiền hoặc tốc độ cả phiên từ phép nhân này.

Không có corpus độc lập để tính precision/recall cải thiện, tần suất compact lỗi, stale dư, conflict, skill misses hoặc memory hữu ích. Các thông số .8, p<.05, TTL, số module/test đều không thay dữ liệu tác động. Công sức O2 là giờ người ước lượng, không thời gian máy/subagent. G3/G4 dùng chung parser/corpus nên gộp một phiếu, không cộng lợi ích như hai engine; G1/G7 cùng handoff, G5/G8 chủ yếu giữ nguyên.

Thiết kế thu tiếp: cùng task/quyền/host/model và corpus đóng băng, trước/sau theo cặp, đổi thứ tự randomized/counterbalanced; ground truth do người kiểm độc lập, giữ lỗi/timeout/missing/skip ở mẫu số phù hợp. Tách training/holdout theo họ task, tránh lặp một task được tính độc lập; ghi correlation theo session/repo. Preregister primary metric, guardrail chất lượng và ngân sách được người dùng duyệt trước model run; không chạy eval thật trong request này. Chi tiết go/no-go theo phiếu O2, chưa có baseline thì dùng thí điểm chứ không đặt % thắng giả.
