# PLAN — Triển khai 16 đề xuất P0+P1 tối ưu workflow TDQ & user-level Claude Code

Ngày: 2026-08-05 · Spec: ../spec/2026-08-05-toi-uu-p0-p1-workflow.md (bản 1.0, ĐÃ DUYỆT) · Lane: full
Mode thực thi: subagent — 16 đầu ra chia thành 5 cụm file KHÔNG chồng lấp
(`scripts/`+`hooks/scripts/`, `skills/tdq-build/`, `skills/tdq-intake/`,
`skills/tdq-conventions/`, `tests/`) + 1 phase đóng sổ tuần tự sau khi merge hết.
Khác round audit trước (mode main vì phụ thuộc chặt 1 nguồn sự thật dùng chung), round
này không có phụ thuộc chéo giữa các cụm nên chạy song song được. (ĐỀ XUẤT, user chốt lúc duyệt)
Trạng thái plan: HOÀN THÀNH (mode main, user duyệt lúc 13:58)

## Năng lực → task

| Skill | Task | Đầu ra bắt buộc |
|---|---|---|
| `graphify` | T6.2 | `graphify-out/graph.json` mtime mới hơn lúc bắt đầu implement |

- Dùng: `tdq-plan`
  - Nạp: đang dùng ngay lúc viết file plan này (phase `plan`), không nạp lại.
  - Để: viết `docs/tdq/plan/2026-08-05-toi-uu-p0-p1-workflow.md` từ spec đã duyệt.
  - Ra: chính file plan này.
  - Kiểm: `python3 scripts/tdq_state.py next` báo `plan_file` đã set.
  - Không dùng cho: sửa lại spec.
- Dùng: `tdq-build`
  - Nạp: nạp ở đầu phase `implement` (turn sau khi plan được duyệt), không nạp ở turn viết plan.
  - Để: chạy toàn bộ P1-P6 + QC + report của request này.
  - Ra: 16 đầu ra spec §2 + `docs/tdq/qc/<slug>.md` + `docs/tdq/reports/<slug>.md`.
  - Kiểm: `python3 scripts/tdq_state.py next` báo phase lần lượt `implement` → `qc` → `report`.
  - Không dùng cho: viết spec/plan — hai việc đó đã xong ở skill khác.
- Dùng: Explore agent
  - Nạp: đã dùng ở phase analyze (1 lần, bao toàn bộ 19 đề xuất), không gọi lại ở build.
  - Để: có ground-truth file:line cho toàn bộ 16 đầu ra §2 trước khi chia task.
  - Ra: mục "Rà soát code chi tiết" trong `docs/tdq/knowledge/2026-08-05-toi-uu-p0-p1-workflow.md`.
  - Kiểm: `grep -c "Rà soát code chi tiết" docs/tdq/knowledge/2026-08-05-toi-uu-p0-p1-workflow.md` trả ≥1.
  - Không dùng cho: đọc code lúc implement — task nào cần đọc thêm thì tự đọc bằng Read/Grep.

## Quy tắc thi hành (áp cho mọi task)
1. Thứ tự phase là thứ tự phụ thuộc — P1-P5 độc lập, chạy song song được; P6 (đóng sổ) chỉ chạy sau khi P1-P5 đã merge.
2. Mỗi task: viết test trước (đỏ) → code → test xanh → tick `[x]` NGAY vào file này.
3. Sau mỗi phase: chạy test của module đang sửa; full suite để dành đúng 1 lần ở P6.
4. Lệnh nào chạm state của workflow phải có `TDQ_PROJECT_DIR=<thư mục tạm>` ngay trên chính lệnh đó.
5. QC FAIL → thêm task fix vào mục QC của file này (không cần duyệt lại), loop đến khi pass.
6. Không commit/push cho đến khi user yêu cầu.

## P1 — Cụm script/hook lõi (`scripts/`, `hooks/scripts/`) — đầu ra #1, #2, #11, #12 spec §2
- [x] **T1.1** `scripts/tdq_state.py turn_snapshot()`: gộp 2 lần gọi `git status --porcelain`
  trùng lặp (qua `repo_status_digest`/`repo_status_paths`) thành 1 lần, truyền tham số
  `status=None` xuống 2 hàm — Test: test mới đếm số lần `_git(cwd, "status", ...)` được
  gọi trong 1 lần `turn_snapshot()` bằng mock/monkeypatch = 1
- [x] **T1.2** `hooks/scripts/bash_gate.py` + `hooks/scripts/_common.py`: đọc
  `turn_rows()` đúng 1 lần trong `main()`, truyền list xuống `_check_signal_mismatch`/
  `already_reminded(cwd, payload, code, rows=None)` — Test: test mới đếm số lần đọc
  `.tdq-turn.jsonl` trong 1 lần `main()` = 1
- [x] **T1.3** `hooks/scripts/prompt_context.py`: lưu digest nội dung `[TDQ:NEXT]`/
  `[TDQ:APPROVE]` đã in (không dùng turn log — bị xoá đầu mỗi turn), so khớp turn sau.
  In gọn hơn nếu state + nội dung không đổi — Test: test mới gọi hook 2 lần liên tiếp
  cùng state, xác nhận output lần 2 ngắn hơn/khác lần 1 đúng quy tắc dedupe
- [x] **T1.4** `scripts/external_task.py skill_dump()`: chỉ chép khối hợp đồng
  (Dùng/Nạp/Để/Ra/Kiểm) + lệnh CLI cụ thể, bỏ phần diễn giải dài trong SKILL.md/references.
  Test: test mới dump skill `tdq-build`, xác nhận output còn đủ 5 trường hợp đồng VÀ
  giảm số byte so với bản dump nguyên văn hiện tại

**Xong P1 khi**: 4 test mới PASS, module test của `tdq_state.py`/`bash_gate.py`/
`external_task.py` xanh.

## P2 — Cụm skill `tdq-build` (`skills/tdq-build/`) — đầu ra #5, #10, #14, #16 spec §2
- [x] **T2.1** `skills/tdq-build/SKILL.md` mục "Đóng worktree": gộp 3 lệnh git rời rạc
  (xoá AGENTS.md, kiểm commit lạ, diff-check + status) bằng `&&`. Test: đọc lại bằng
  mắt, đúng 1 dòng lệnh gộp thay 3 dòng rời, khớp luật gộp Bash ở `tdq-conventions/SKILL.md`
- [x] **T2.2** `skills/tdq-build/SKILL.md` mục "Luật cứng": thêm 3 ví dụ cụ thể (đổi
  schema DB, xoá data, đổi API contract công khai) vào nhóm "cần dừng hỏi" — Test:
  `grep -c "schema DB\|xoá data\|API contract" skills/tdq-build/SKILL.md` trả ≥1 mỗi cụm từ
- [x] **T2.3** Tách mục "Nhánh external" (62 dòng) từ `skills/tdq-build/SKILL.md` sang
  `skills/tdq-build/references/external-build.md` mới, thêm câu trỏ nạp file này khi
  `implement_mode=external` ở Phần A bước 1 — Test: `wc -l skills/tdq-build/SKILL.md` < 150
  (dòng gốc); `grep -n "external-build.md" skills/tdq-build/SKILL.md` trả ≥1
- [x] **T2.4** `skills/tdq-build/references/qc.md`: thêm hướng dẫn chạy test suite ở
  chế độ tóm tắt (cờ `-q`/dot reporter hoặc redirect + `tail`/`grep` phần fail), không
  dán log dài vào chat — Test: `grep -in "\-q\|dot reporter\|redirect"
  skills/tdq-build/references/qc.md` trả ≥1

**Xong P2 khi**: `doc_lint.py` trên `skills/tdq-build/` exit 0, `wc -l SKILL.md` giảm
đúng như T2.3 yêu cầu.

## P3 — Cụm skill `tdq-intake` (`skills/tdq-intake/`) — đầu ra #3, #6, #7 spec §2
- [x] **T3.1** Tách Phần B "Phân tích (phase `analyze`, chỉ lane full)" từ
  `skills/tdq-intake/SKILL.md` sang `skills/tdq-intake/references/analyze-full.md` mới,
  quick lane (Phần C) không nạp file này — Test: `wc -l skills/tdq-intake/SKILL.md` < 117
  (dòng gốc); nội dung Phần C không chứa nội dung Phần B
- [x] **T3.2** `skills/tdq-intake/references/lane-decision.md`: sửa mục "Khuôn câu hỏi"
  tự định nghĩa riêng, đổi thành theo đúng khuôn `interview.md` (option mỗi dòng, khuôn
  `- A (đề xuất): ...`) — Test: đọc lại bằng mắt khớp khuôn `interview.md`; `doc_lint.py`
  trên file exit 0
- [x] **T3.3** `skills/tdq-intake/references/quick-lane.md`: bỏ câu cho user override
  soft-block khi task `(mcp)` + mode external, chốt hard-block khớp
  `tdq-build/SKILL.md:60` — Test: `grep -n "làm theo user" skills/tdq-intake/references/quick-lane.md`
  trả rỗng; `doc_lint.py --pair skills/tdq-intake/references/quick-lane.md skills/tdq-build/SKILL.md` exit 0
  (ghi chú build: `--pair` chỉ áp cho cặp spec/plan §3b, không áp cho 2 file skill —
  đổi sang `doc_lint.py` đơn file quick-lane.md, exit 0; nội dung hard-block đối chiếu
  tay khớp `tdq-build/references/external-build.md` sau khi T2.3 tách file)

**Xong P3 khi**: `doc_lint.py` trên `skills/tdq-intake/` exit 0, kiểm tay 1 lượt
`tdq_state.py init <slug-test> quick` (project tạm) rồi `next` — đủ nội dung Phần A/C
so với trước khi tách.

## P4 — Cụm skill `tdq-conventions` (`skills/tdq-conventions/`) — đầu ra #4, #9, #15 spec §2
- [x] **T4.1** `skills/tdq-conventions/SKILL.md` §6: thay đoạn diễn giải "đã đổi repo"
  bằng câu trỏ link `[reminder-codes.md](references/reminder-codes.md#...)` — Test:
  `grep -n "reminder-codes.md" skills/tdq-conventions/SKILL.md` trả ≥1
- [x] **T4.2** `skills/tdq-conventions/references/reminder-codes.md`: thêm ghi chú rủi ro
  — 2 phiên Claude Code cùng chạy trên 1 worktree chính có thể khiến `stop_gate.py` tính
  oan "đã đổi repo" (không đổi code) — Test: `grep -n "2 phiên"
  skills/tdq-conventions/references/reminder-codes.md` trả ≥1
- [x] **T4.3** Viết mới `skills/tdq-conventions/references/measure-scenario.md`: kịch bản
  đo carry-cost before/after chuẩn hoá — danh sách thao tác cố định (vd: mở request quick
  mẫu → duyệt → implement 1 task giả) + lệnh `token_audit.py --transcript-dir <dir>` mẫu
  cho 2 session before/after. Test: file tồn tại, `doc_lint.py` exit 0, có ≥1 lệnh CLI
  cụ thể copy-paste được (không chỉ mô tả suông)

**Xong P4 khi**: `doc_lint.py` trên `skills/tdq-conventions/` exit 0.

## P5 — Cụm test khoá đồng bộ (`tests/`) — đầu ra #8 spec §2
- [x] **T5.1** Viết `tests/test_agent_digest_sync.py`: đọc ngưỡng "≤1.500 ký tự" (hoặc
  số tương đương) từ 7 file `agents/*.md` + `skills/tdq-intake/SKILL.md:58`, assert tất
  cả khớp nhau. Test: `cd tests && python3 -m unittest test_agent_digest_sync -v` PASS;
  kiểm tay 1 lần bằng cách cố ý sửa sai số ở 1 file rồi chạy lại → phải FAIL, sửa đúng
  lại → PASS.
  (Ghi chú build: nguồn thứ 8 đổi từ `SKILL.md:58` sang
  `skills/tdq-intake/references/analyze-full.md`. T3.1 trong chính plan này đã tách
  Phần B ra khỏi SKILL.md nên con số "1.500 ký tự" không còn nằm ở dòng 58 cũ; test viết
  theo vị trí thật hiện tại. Đã kiểm tay: sửa sai `tdq-reviewer.md` → 2.000 → FAIL đúng
  như mong đợi, phục hồi lại → PASS, diff sạch.)

**Xong P5 khi**: `test_agent_digest_sync.py` PASS và đã xác nhận bắt được lệch số (red→green thật).

## P6 — Đóng sổ (chạy SAU khi P1-P5 đã merge về nhánh chính)
- [x] **T6.1** Chạy toàn bộ test suite — Test: `cd tests && python3 -m unittest discover -v` 0 fail

### QC vòng 1 — fix
Lần chạy đầu suite ra 7 fail, đều là test cũ scan sai vị trí sau khi T2.3/T3.1 dời nội
dung sang `references/*.md`, cộng 1 lỗi thật do T1.3 (nén nhầm cảnh báo an toàn).
- [x] **QC1.1** `test_approve_signal_and_counterexamples` (×3 subtest) fail vì T1.3
  nén luôn nhánh "chờ duyệt mơ hồ". Fix: thêm tham số `critical` vào `_emit()` trong
  `prompt_context.py`, đánh dấu `critical=True` cho nhánh mode-conflict, nhánh
  chờ duyệt (cả matched lẫn ambiguous) và nhánh spec-drift — Test:
  `python3 -m unittest test_compliance_protocol -v` 16/16 PASS
- [x] **QC1.2** `test_steps_match_skills` (portable_sync, `01-intake.md`) fail vì
  Phần B còn để nguyên văn thay vì trỏ pointer như `SKILL.md` — rút gọn Phần B
  trong `portable/workflow/01-intake.md` thành pointer, tạo
  `portable/workflow/references/analyze-full.md` chứa nội dung đầy đủ — Test:
  `python3 -m unittest test_portable_sync -v` PASS
- [x] **QC1.3** `test_tdq_build_quick_packet_gets_skill_dump` fail vì đọc
  `SKILL.md` thay vì `references/external-build.md` (đã dời ở T2.3) — sửa test
  trỏ đúng file mới — Test: `python3 -m unittest test_skill_docs -v` PASS
- [x] **QC1.4** `test_six_contract_phrases` fail cùng nguyên nhân QC1.3. Phát hiện
  thêm lỗi thật: bản R5 rút gọn câu ở segment trước đã làm rớt cụm "TRƯỚC khi
  diff-check" và gõ sai dấu "Xoá"→"Xóa" trong `external-build.md`. Sửa test trỏ
  `references/external-build.md`, khôi phục cụm bị rớt, sửa dấu, tách câu 46 từ
  thành 2 câu cho R5 (≤40 từ) — Test: `python3 -m unittest test_skill_docs -v`
  PASS + `python3 scripts/doc_lint.py skills/tdq-build/references/external-build.md`
  exit 0
- [x] **QC1.5** `test_intake_giao_research_cho_search_scout` fail vì đọc
  `SKILL.md` thay vì `references/analyze-full.md` (đã dời ở T3.1) — sửa test trỏ
  đúng file — Test: `python3 -m unittest test_skill_docs -v` PASS
- [x] **QC1.6** Fix QC1.2 kéo theo 2 fail mới ngoài danh sách gốc:
  `test_portable_mang_cung_luat` và `test_cam_gop_option_vao_doan_van` còn scan
  `01-intake.md` trực tiếp — trỏ cả hai sang
  `portable/workflow/references/analyze-full.md` — Test:
  `python3 -m unittest test_skill_docs -v` PASS
- [x] **QC1.7** Fix QC1.1 làm lộ mâu thuẫn thiết kế. Bài test
  `test_context_hooks.py::test_repeated_identical_pending_state_shrinks_on_second_turn`
  (viết ở T1.3, cùng session) đòi nhánh chờ duyệt mơ hồ PHẢI nén lặp. Ngược với
  QC1.1: nhánh này không bao giờ được nén, theo `test_compliance_protocol` — luật
  an toàn có trước. Sửa bài test T1.3: đổi kịch bản sang state KHÔNG có gì chờ duyệt (phase
  implement, spec/plan đã duyệt) để kiểm đúng hành vi nén NEXT thường, không đụng
  nhánh an toàn. Đổi tên thành
  `test_repeated_identical_next_only_shrinks_on_second_turn` — Test:
  `python3 -m unittest test_context_hooks test_compliance_protocol -v` cả 2 PASS
- [x] **QC1.8** Chạy lại toàn bộ suite sau QC1.1-QC1.7 — Test:
  `cd tests && python3 -m unittest discover` → 585 tests, 0 fail (log
  `/tmp/full-suite-3.log`)

- [x] **T6.2** Rebuild code graph (đã đổi nhiều file `.py`) — Test:
  `graphify extract . --code-only` exit 0, `graphify-out/graph.json` mtime mới hơn lúc
  bắt đầu implement
  - Dùng: `graphify`
  - Nạp: kiểm `graphify --version` trước; thiếu thì báo user, không tự cài.
  - Để: dựng lại graph sau khi sửa nhiều script/hook.
  - Ra: `graphify-out/graph.json` và `graphify-out/GRAPH_REPORT.md` mới.
  - Kiểm: `graphify extract . --code-only` exit 0.
  - Không dùng cho: phân tích doc trong `docs/` hay `skills/`.
- [x] **T6.3** Lint toàn bộ file đã sửa/tạo — Test:
  `python3 scripts/doc_lint.py skills portable tests/test_agent_digest_sync.py` (phần
  `.py` không lint bằng doc_lint, chỉ liệt kê để nhắc) exit 0 trên phần `.md`
- [x] **T6.4** Append working log tổng kết implement (P1-P5 + merge + P6) qua
  `scripts/tdq_finish.py` — Test: `docs/workinglog/2026-08-05.md` có entry mới với
  timestamp turn build

**Xong P6 khi**: suite xanh, `doc_lint` exit 0, graphify mtime mới, working log có entry.

## QC — kiểm độc lập (spec Lộ trình yêu cầu `tdq-qc-tester`)
- [x] **TQC.1** Gọi agent `tdq-qc-tester`: chạy lại full suite độc lập + probe
  `bash_gate.py`/`prompt_context.py` bằng input mẫu. Không dùng lại kết quả tự kiểm của
  P1-P6 — Test: báo cáo PASS, không phát hiện lệch so với tự kiểm

### QC vòng 2 — fix
Agent `tdq-qc-tester` báo 8/10 mục PASS, 2/10 FAIL (không lệch với tự kiểm P1-P6, đây là
2 lỗi mới đội tự kiểm bỏ sót) + 2 lỗi nhẹ trong working log.
- [x] **QC2.1** `skills/tdq-intake/SKILL.md:77-79` trỏ cross-reference cũ tới mục
  "Nhánh external" trong `tdq-build/SKILL.md` — T2.3 đã dời mục này sang
  `references/external-build.md`. Sửa link trỏ đúng file mới — Test:
  `python3 scripts/doc_lint.py skills/tdq-intake/SKILL.md` exit 0, đọc tay xác nhận
  link đúng đích
- [x] **QC2.2** Đầu ra #13 (spec §2: khuyến nghị `/clear` sau khi đóng 1 request/session
  dài) chưa từng được gán vào task nào ở P1-P6 — thiếu deliverable so với DoD "16/16 đầu
  ra". Thêm dòng khuyến nghị vào `portable/AGENTS.md` mục Working log. Test:
  `grep -n "/clear" portable/AGENTS.md` trả ≥1 dòng và `doc_lint.py portable/AGENTS.md`
  exit 0
- [x] **QC2.3** (nhẹ, không chặn) 3 câu R5 quá 40 từ trong entry `13:43`/`13:47`/`14:51`
  của `docs/workinglog/2026-08-05.md`, do chính build này ghi. Tách câu, gộp luôn 2 entry
  trùng header `## 13:43` thành 1. Test: `doc_lint.py docs/workinglog/2026-08-05.md`
  không còn báo lỗi tại 3 entry này (5 lỗi R5 còn lại thuộc entry request khác trong
  ngày, ngoài phạm vi build này)

**Xong QC khi**: `docs/tdq/qc/2026-08-05-toi-uu-p0-p1-workflow.md` ghi đủ 16 đầu ra +
kết quả `tdq-qc-tester`, tất cả PASS.

## Definition of Done
Trỏ spec §6:
- Q1 T1.1-T1.2 test riêng pass — full suite T6.1.
- Q2 T2.1/T2.2/T3.3/T4.1/T4.2/T2.4 grep/đọc tay — mỗi task tự kiểm khi tick.
- Q3 T2.3/T3.1 không phá quick lane/mode external — kiểm tay P3.
- Q4 T5.1 tự bắt được lệch số — P5.
- Q5 T1.4 giảm byte, giữ khối hợp đồng — P1.
- Q6 T1.3 dedupe đúng 2 lượt — P1.
- Q7 T4.3 kịch bản đo chạy được thật — P4.
- Q8 T6.3 lint toàn bộ file đổi — P6.
- Q9 TQC.1 QC độc lập PASS — mục QC.
- Q10 T6.2 graphify — P6.
