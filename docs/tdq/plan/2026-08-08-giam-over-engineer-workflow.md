# PLAN — Giảm over-engineer & over-test cho TDQ workflow

Ngày: 2026-08-08 · Spec: ../spec/2026-08-08-giam-over-engineer-workflow.md (bản 1.0, ĐÃ DUYỆT) · Lane: full
Mode thực thi: main — 8 đầu ra đụng chung một nhóm file (`tdq_state.py`, `skills/`, `tests/`) và phụ thuộc chặt theo thứ tự xoá rồi mới rút gọn; chạy song song trong worktree riêng sẽ đụng độ nhiều hơn phần tiết kiệm được (ĐỀ XUẤT, user chốt lúc duyệt)
Trạng thái plan: CHỜ DUYỆT

## Năng lực → task

| Skill | Task | Đầu ra bắt buộc |
|---|---|---|
| superpowers:test-driven-development | T1.1 | `tests/test_doc_lint.py` có test đỏ trước khi sửa `rule_r5`, xanh sau |
| mem0-memory | T8.4 | 1 fact trong mem0 project `TDQWorkflow` về quyết định kiến trúc, đọc lại được bằng `search_memories` |

## Quy tắc thi hành (áp cho mọi task)

1. Thứ tự phase là thứ tự phụ thuộc — không đảo.
2. Mỗi task: viết test trước (đỏ) → code → test xanh → tick `[x]` NGAY vào file này.
3. Sau mỗi phase: chạy toàn bộ test suite, phải xanh mới sang phase sau.
4. Lệnh nào chạm state của workflow phải có `TDQ_PROJECT_DIR=<thư mục tạm>` ngay trên chính lệnh đó.
5. QC FAIL → thêm task fix vào mục QC của file này (không cần duyệt lại), loop đến khi pass.
6. Không commit/push cho đến khi user yêu cầu. Ngoại lệ duy nhất: P2 xoá external cần
   một commit riêng để `git revert` khôi phục được (giả định G3 của spec) — commit,
   KHÔNG push, liệt kê trong report.
7. Theo nguyên tắc minimal của spec §4: chỉ P1, P4, P5, P7 có test. Các task xoá file
   và sửa tài liệu kiểm bằng `grep`/`ls`, không viết test mới.

## P1 — Sửa `doc_lint` (D7)

Làm trước tiên: mọi tài liệu sinh ra ở các phase sau đều đi qua `doc_lint`.

- [x] **T1.1** Thêm test đỏ vào `tests/test_doc_lint.py`: đoạn văn >40 từ có
      `<!-- doc-lint: allow R5 -->` ngay dòng trên thì R5 phải im — Test: test mới FAIL trước khi sửa `rule_r5`
  - Dùng: `superpowers:test-driven-development`
  - Nạp: gọi skill `superpowers:test-driven-development` TRƯỚC bước đỏ của task này.
  - Để: dựng đúng chu trình đỏ → xanh cho hai bug của `doc_lint`, không cho sửa code trước khi có test đỏ.
  - Ra: `tests/test_doc_lint.py` có test `test_allow_r5_ngay_tren_doan` (đỏ ở T1.1, xanh ở T1.2).
  - Kiểm: `python3 -m unittest tests.test_doc_lint -v` — đỏ tại T1.1, xanh tại T1.2.
  - Không dùng cho: các task xoá file ở P2, P3 — chúng không có hành vi để test.
- [x] **T1.2** Sửa `rule_r5` trong `scripts/doc_lint.py`: khi gom buffer thì bỏ qua dòng
      `<!-- doc-lint: ... -->` và không cho nó thành `state["start"]` — Test: `python3 -m unittest tests.test_doc_lint` xanh
- [x] **T1.3** Thêm test đỏ: file bất kỳ dưới `docs/tdq/` chỉ chịu R8, không chịu R1–R7 — Test: test mới FAIL trước khi sửa `lint_file`
- [x] **T1.4** Sửa `lint_file`: đổi điều kiện `in_spec_dir` thành "đường dẫn nằm trong
      `docs/tdq/`"; R8 vẫn chỉ soi thư mục `spec/` — Test: `python3 scripts/doc_lint.py docs/tdq/requests/2026-08-08-giam-over-engineer-workflow.md` exit 0

**Xong P1 khi**: `python3 -m unittest tests.test_doc_lint` xanh và `python3 scripts/doc_lint.py docs/tdq` exit 0.

## P2 — Xoá nhánh external và deep search (D3)

- [x] **T2.1** Xoá `scripts/external_task.py`, `external_models.py`, `external_report_schema.json`,
      `search_task.py`, `search_report_schema.json`, `samples/e2e_agy.py`, `samples/e2e_codex.py` — Test: `ls scripts/external* scripts/search*` báo không tồn tại
- [x] **T2.2** Xoá `agents/agy-runner.md`, `codex-runner.md`, `search-runner.md`, `search-scout.md` — Test: `ls agents` còn đúng 3 file
- [x] **T2.3** Xoá `skills/tdq-build/references/external-build.md`, `external-task.md`,
      `skills/tdq-conventions/references/deep-search.md` — Test: `ls` báo không tồn tại
- [x] **T2.4** Dọn `scripts/tdq_state.py`: `VALID_MODES` còn `("main", "subagent")`, bỏ
      `--mode external` khỏi `approve quick`, gỡ mọi câu external trong `PHASE_TABLE` — Test: `python3 -m unittest tests.test_state tests.test_phase_table` xanh
- [x] **T2.5** Dọn `hooks/scripts/_common.py`, `edit_gate.py`, `prompt_context.py` — Test: `python3 -m unittest tests.test_edit_gate tests.test_context_hooks` xanh
- [x] **T2.6** Dọn 9 file skill còn nhắc external (`tdq-build/SKILL.md`, `agents-md.md`,
      `tdq-conventions/SKILL.md`, `approval.md`, `subagent-tuning.md`, `tdq-intake/SKILL.md`,
      `quick-lane.md`, `tdq-plan/SKILL.md`, `plan-template.md`) — Test: `grep -ril external skills` rỗng
- [x] **T2.7** Xoá `tests/test_external_task.py`, `test_external_models.py`,
      `test_search_task.py`, `test_e2e_agy.py`, `test_e2e_codex.py` — Test: `python3 -m unittest discover -s tests -t tests -q` xanh
- [x] **T2.8** Commit riêng cho P2 với message mô tả việc xoá, KHÔNG push — Test: `git log -1 --oneline` in đúng commit đó

**Xong P2 khi**: `grep -ril external skills hooks agents scripts tests` không ra kết quả và suite xanh.

## P3 — Xoá `portable/` (D4)

- [x] **T3.1** Chuyển `portable/claude-md/CLAUDE.md` thành `docs/claude-md-mau.md`,
      gỡ phần nói về external/deep search — Test: `ls docs/claude-md-mau.md` tồn tại, `grep -i external` rỗng
- [x] **T3.2** Xoá thư mục `portable/` và `tests/test_portable_sync.py` — Test: `ls portable` báo không tồn tại; suite xanh

**Xong P3 khi**: `portable/` không còn và `python3 -m unittest discover -s tests -t tests -q` xanh.

## P4 — Gộp output thành `brief/` (D5)

- [x] **T4.1** Đổi `PHASE_TABLE` trong `scripts/tdq_state.py`: mọi câu nhắc
      `requests/`, `knowledge/`, `questions/` chuyển thành `brief/<slug>.md` — Test: `python3 -m unittest tests.test_phase_table` xanh
- [x] **T4.2** Đổi `skills/tdq-intake/SKILL.md`, `references/analyze-full.md`,
      `skills/tdq-conventions/SKILL.md` §5 (cây tài liệu), `tdq-spec/references/spec-template.md`
      sang khuôn brief 3 mục: `## Nguyên văn`, `## Hiểu & kiến thức`, `## Hỏi đáp` — Test: `grep -rn "requests/" skills` chỉ còn trong ghi chú lịch sử hoặc rỗng
- [x] **T4.3** Chạy thử một request giả để xác nhận khuôn mới chạy được — Test: `TDQ_PROJECT_DIR=<thư mục tạm> python3 scripts/tdq_state.py init test-brief full && ... next` in ra đường dẫn `brief/`

**Xong P4 khi**: T4.3 in đúng `brief/` và suite xanh.

## P5 — Tầng `nhỏ` và QC bám DoD (D1, D2)

- [x] **T5.1** Viết mục "Tầng nhỏ" vào `skills/tdq-intake/SKILL.md`: 4 điều kiện vào,
      việc được làm, luật thoát bắt buộc khi vi phạm giữa chừng — Test: `grep -c "Tầng nhỏ" skills/tdq-intake/SKILL.md` ≥ 1 và mục có đủ 4 điều kiện
- [x] **T5.2** Thêm luật in dòng `Cỡ: <nhỏ|quick|full> · Cần: <...>` vào
      `skills/tdq-intake/SKILL.md` và `references/lane-decision.md` — Test: `grep -n "Cỡ:" skills/tdq-intake/references/lane-decision.md` ra kết quả
- [x] **T5.3** Đổi định nghĩa QC trong `skills/tdq-build/references/qc.md`,
      `skills/tdq-intake/references/quick-lane.md`, `PHASE_TABLE`: số hạng mục QC bằng số
      dòng DoD; vòng fix chỉ chạy lại hạng mục FAIL cộng hạng mục có thể bị bản fix làm
      hỏng; bỏ luật vòng fix bắt buộc khi user tắt QC; giữ trần 3 vòng — Test: `grep -rn "3 hạng mục" skills` rỗng
- [x] **T5.4** Sửa `tests/test_quick_qc.py` theo luật QC mới, giữ nguyên phần kiểm
      `--no-qc` và `quick_qc_skipped` — Test: `python3 -m unittest tests.test_quick_qc` xanh

**Xong P5 khi**: `grep -rn "3 hạng mục" skills` rỗng và suite xanh.

## P6 — Rút gọn skill nặng (D6)

- [x] **T6.1** Tách mục 10 của `skills/tdq-conventions/SKILL.md` sang
      `references/context-budget.md`, chỗ cũ để lại 2 dòng và một link — Test: `wc -c skills/tdq-conventions/SKILL.md` giảm so với 7.345, số đo ghi lại
- [x] **T6.2** Rút mục 7 (git), 8 (research), 9 (sub-agent), 11 (chất lượng) của
      `tdq-conventions/SKILL.md` còn phần không suy ra được từ chỗ khác — Test: `python3 -m unittest discover -s tests -t tests -q` xanh
- [x] **T6.3** Rút `tdq-intake/SKILL.md`, `tdq-plan/SKILL.md`, `tdq-build/SKILL.md` sau
      khi P2 đã gỡ external — Test: `wc -c skills/*/SKILL.md` ghi lại, và `python3 scripts/doc_lint.py skills` exit 0

**Xong P6 khi**: `doc_lint` trên `skills/` exit 0 và tổng byte skill đã ghi lại để so ở P8.

## P7 — Dọn bộ test (D8)

- [x] **T7.1** Xoá test chỉ assert chuỗi trong .md: `tests/test_skill_docs.py`,
      `test_docs_consistency.py`, `test_agent_digest_sync.py`, và các test cùng loại trong
      `test_compliance_protocol.py` — Test: `python3 -m unittest discover -s tests -t tests -q` xanh
- [x] **T7.2** Làm `tests/test_claude_md_core.py` hermetic: bỏ so sánh với
      `~/.claude/CLAUDE.md`, chỉ kiểm `docs/claude-md-mau.md` trong repo — Test: `HOME=/nonexistent python3 -m unittest tests.test_claude_md_core` xanh
- [x] **T7.3** Giảm test hook: bỏ test assert nguyên văn thông điệp, giữ test hành vi
      chặn/không chặn của `stop_gate`, `edit_gate`, `bash_gate` — Test: `python3 -m unittest tests.test_stop_gate tests.test_edit_gate tests.test_bash_gate` xanh
- [x] **T7.4** Chạy suite hai lần để xác nhận hermetic — Test: `python3 -m unittest discover -s tests -t tests -q` và `HOME=/nonexistent python3 -m unittest discover -s tests -t tests -q` cùng exit 0

**Xong P7 khi**: cả hai lần chạy ở T7.4 exit 0.

## P8 — Đo, QC, ghi nhớ

- [x] **T8.1** Đo lại 4 số bằng đúng cách đã đo ở knowledge: byte skill nạp mỗi vòng
      full, số file output mỗi request, số test, giây chạy suite — Test: 4 cặp số trước/sau có mặt trong `docs/tdq/reports/<slug>.md`
- [x] **T8.2** Chạy đủ Q1–Q10 của spec §6, ghi bằng chứng vào `docs/tdq/qc/<slug>.md`;
      Q1 phân loại lại 5 request cũ trong `docs/tdq/requests/` theo tầng mới — Test: `qc/<slug>.md` có đủ 10 dòng kết quả kèm lệnh và output
- [x] **T8.3** Gọi agent `tdq-qc-tester` chạy độc lập một lượt — Test: agent trả PASS, kết quả dán vào `qc/<slug>.md`
- [x] **T8.4** Ghi 1 fact vào mem0 về quyết định kiến trúc của request này — Test: `search_memories` với project `TDQWorkflow` trả về đúng fact vừa ghi
  - Dùng: `mem0-memory` (mcp)
  - Nạp: gọi skill `mem0-memory` TRƯỚC khi ghi. Agent ngoài không có skill system: đọc `~/.claude/skills/mem0-memory/SKILL.md` rồi làm theo.
  - Để: ghi đúng một fact ngắn về "TDQ bỏ external, thêm tầng nhỏ, QC bám DoD", không ghi nhật ký phiên.
  - Ra: một memory trong mem0 project `TDQWorkflow`, lấy lại được bằng `search_memories`.
  - Kiểm: `mcp__mem0__search_memories` với truy vấn "tầng nhỏ TDQ" trả về fact đó.
  - Không dùng cho: ghi số đo hay nội dung report — những thứ đó nằm trong repo.

**Xong P8 khi**: Q1–Q10 PASS và `tdq-qc-tester` trả PASS.

## Px — Log & test bắt buộc

- [x] **Tx.1** Log service: KHÔNG áp dụng — request này không viết service mới, chỉ xoá
      và rút gọn. Các script bị sửa giữ nguyên cách log hiện có (cảnh báo stderr, exit
      code, `tdq_finish.py` ghi working log có timestamp) — Test: `python3 scripts/tdq_finish.py --help` chạy được và working log của turn build có timestamp
- [x] **Tx.2** Unit test chạy bằng một lệnh — Test: `python3 -m unittest discover -s tests -t tests -q` exit 0

## Definition of Done

Trỏ về §6 của spec. Từng hạng mục kèm lệnh kiểm:

| # | Hạng mục | Lệnh kiểm |
|---|---|---|
| Q1 | Tầng `nhỏ` dùng được | đọc `skills/tdq-intake/SKILL.md` + phân loại 5 request cũ |
| Q2 | QC bám DoD | `grep -rn "3 hạng mục" skills/` |
| Q3 | External sạch | `grep -ril external skills hooks agents scripts tests` |
| Q4 | `portable/` đã xoá | `ls portable` và `ls docs/claude-md-mau.md` |
| Q5 | Gộp brief chạy được | chạy request giả với `TDQ_PROJECT_DIR` tạm |
| Q6 | `doc_lint` đúng phạm vi | `python3 scripts/doc_lint.py docs/tdq/brief/<slug>.md` |
| Q7 | Cửa thoát `allow R5` | `python3 -m unittest tests.test_doc_lint` |
| Q8 | Suite xanh và hermetic | `python3 -m unittest discover -s tests -t tests -q` và bản `HOME=/nonexistent` |
| Q9 | 6 rào an toàn còn nguyên | chạy từng hook với state giả trong thư mục tạm |
| Q10 | Số đo trước/sau | 4 cặp số trong `reports/<slug>.md`, không có ngưỡng chặn |

## QC vòng 1 — fix

Nguồn: agent `tdq-qc-tester` chạy độc lập (T8.3) trả FAIL, 5 khiếm khuyết đã đối chiếu
lại và xác nhận đúng. Chi tiết ở `../qc/2026-08-08-giam-over-engineer-workflow.md`.

- [x] **F1** Sửa lệnh DoD sai trong spec và plan: `python3 -m unittest discover -s tests -t tests -q`
      (exit 5, NO TESTS RAN) thành `python3 -m unittest discover -s tests -t tests -q` —
      Test: chạy đúng lệnh mới ở gốc repo trả exit 0; `grep -c "discover -q\`" ` trên 2
      file trả 0
- [x] **F2** Làm nốt D2: bỏ luật "vòng fix bắt buộc kể cả khi user tắt QC" ở
      `quick-lane.md`, `tdq-intake/SKILL.md`, `PHASE_TABLE`; sinh lại `phases.md` —
      Test: `grep -rn "kể cả khi user" skills/ scripts/` rỗng; `test_quick_qc.py` xanh
- [x] **F3** Sửa mâu thuẫn trần vòng fix ở `quick-lane.md` dòng 15 (lane full ghi "trần
      không giới hạn") cho khớp `qc.md` — Test: `grep -n "không giới hạn" skills/` rỗng
- [x] **F4** `agents/tdq-reviewer.md`: `knowledge/requests` thành `brief` — Test:
      `grep -n "knowledge\|requests" agents/tdq-reviewer.md` rỗng
- [x] **F5** Chạy lại hạng mục FAIL và hạng mục bản fix có thể làm hỏng: Q2, Q5, Q7, Q8
      cộng `doc_lint skills` — Test: cả 5 phép kiểm PASS

**Xong vòng 1 khi**: F1-F5 tick và suite xanh. Trần 3 vòng.
