# PLAN — Quốc tế hoá bộ workflow TDQ

Ngày: 2026-08-22 · Spec: ../spec/2026-08-21-2351-quoc-te-hoa-workflow.md (bản 1.0, ĐÃ DUYỆT) · Lane: full
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md
Mode thực thi: main — mô phỏng trên chính plan này cho "đội" thắng 20.3 phút (25 task, 4 đợt, hệ số agent 1.5), nhưng luật phiên hiện tại cấm gọi sub-agent nên đề xuất main; user chốt ở cổng mode.
Trạng thái plan: HOÀN THÀNH (T7.2 hoãn — chờ user duyệt chi phí eval) — mode main (user chọn "A" lúc 2026-08-22T00:22)

## Quy tắc thi hành (áp cho mọi task)
1. Thứ tự phase là thứ tự phụ thuộc — không đảo.
2. Mỗi task: `[~]` khi bắt đầu → check đỏ → sửa → check xanh → `[x]` NGAY vào file này.
3. Sau mỗi phase: chạy test của các module vừa chạm, phải xanh mới sang phase sau.
4. **Task dịch nào đổi chuỗi máy in ra thì sửa test của chính module đó TRONG CÙNG TASK** —
   không để test đỏ trôi sang task sau (rủi ro số 1 ở spec §5).
5. Dịch là đổi chữ: cấm đổi tên lệnh, tên trường state, mã `[TDQ:*]`, tên file, thứ tự phase,
   ngưỡng số. Thấy luật viết sai trong lúc dịch → ghi lại, KHÔNG sửa trong request này.
6. QC FAIL → thêm task fix vào mục QC của file này (không cần duyệt lại), loop đến khi pass.
7. Không commit/push cho đến khi user yêu cầu.

## P1 — Mốc & công cụ đo

- [x] **T1.1** (e8m) Ghi mốc: full suite + bảng đếm dòng tiếng Việt của 6 tầng file vào `docs/tdq/bench/i18n/moc.md` — Test: file có đủ 6 dòng đếm và số pass/fail thật của suite
- [x] **T1.2** (e25m) Viết `scripts/i18n_check.py`: quét một vùng đường dẫn, đếm dòng chứa ký tự tiếng Việt, tách 3 loại (comment · chuỗi · thân), bỏ qua dòng có nhãn trích dẫn cố ý, exit 1 khi còn sót — Test: `python3 -m pytest tests/test_i18n_check.py -q` xanh
  - Chạm: `scripts/i18n_check.py`, `tests/test_i18n_check.py` → file mới, chưa node nào phụ thuộc

**Xong P1 khi**: có mốc số và có đúng một lệnh dùng lại được cho mọi hạng mục đếm ngôn ngữ.

## P2 — M4a: state & trường ngôn ngữ

- [x] **T2.1** (e20m) Thêm trường ngôn ngữ tài liệu vào state + cờ khai lúc `init`; thiếu cờ → mặc định tiếng Việt; state cũ thiếu trường đọc lên không lỗi — Test: `python3 -m pytest tests/ -q -k "state and lang"` xanh, và `tdq_state.py get` trên state cũ không lỗi
  - Chạm: `scripts/tdq_state.py`, `tests/test_state_lang.py` → node `cli()`, `main()` (Hub, bậc 17/20)
- [x] **T2.2** (e35m) Dịch 439 dòng tiếng Việt của `scripts/tdq_state.py` (comment + chuỗi in ra) và sửa mọi test đang assert chuỗi cũ — Test: `python3 scripts/i18n_check.py scripts/tdq_state.py` = 0 và `python3 -m pytest tests/ -q -k state` xanh
  - Chạm: `scripts/tdq_state.py`, `tests/test_state*.py` → node `cli()`, `main()`, `log()` (Hub)
  - Cần: T1.2, T2.1
- [x] **T2.3** (e20m) Dịch `scripts/tdq_finish.py` (41) + `scripts/doc_lint.py` (153) và sửa test của hai module đó — Test: `python3 scripts/i18n_check.py scripts/tdq_finish.py scripts/doc_lint.py` = 0 và `pytest -q -k "finish or doc_lint"` xanh
  - Chạm: `scripts/tdq_finish.py`, `scripts/doc_lint.py`, `tests/test_doc_lint.py`, `tests/test_tdq_finish.py` → node `main()` (Hub)
  - Cần: T1.2

**Xong P2 khi**: 3 script lõi sạch tiếng Việt, state giữ được ngôn ngữ, test của chúng xanh.

## P3 — M3: cổng máy (hook)

- [x] **T3.1** (e25m) Thêm nhận diện chữ cái `a`–`d` đứng riêng và từ khoá duyệt tiếng Anh, đấu vào CẢ 4 cổng `spec`/`plan`/`quick`/`mode`; giữ nguyên mọi đường tiếng Việt cũ — Test: `pytest tests/test_prompt_context.py -q` xanh, có ca mới cho `"A"` ở cổng `spec`/`plan`/`quick` và ca cũ `"Ai làm cũng được"` vẫn trượt
  - Chạm: `hooks/scripts/prompt_context.py`, `tests/test_prompt_context.py` → node đọc bởi `hooks/scripts/bash_gate.py`
  - Cần: T1.2
- [x] **T3.2** (e15m) Mở rộng bộ chặn câu hỏi/phủ định sang tiếng Anh (`not yet`, `no`, `?`), thêm ca âm `"ok but not yet"`, `"approve? not sure"` — Test: `pytest tests/test_prompt_context.py -q -k reject` xanh
  - Chạm: `hooks/scripts/prompt_context.py`, `tests/test_prompt_context.py` → cùng node T3.1
  - Cần: T3.1
- [x] **T3.3** (e10m) Đổi khuôn dòng mời thành hai lối (câu chữ + chữ cái) tại nguồn máy duy nhất `APPROVE_HINTS`, và sửa test khoá nguyên văn dòng đó — Test: `pytest tests/ -q -k "approve_hint or common"` xanh
  - Chạm: `hooks/scripts/_common.py`, `tests/test_common.py` → node dùng bởi 5 hook
  - Cần: T3.1
- [x] **T3.4** (e30m) Dịch comment + chuỗi in ra của 6 file trong `hooks/scripts/` (331 dòng) và sửa test hook tương ứng — Test: `python3 scripts/i18n_check.py hooks/` = 0 và `pytest tests/ -q -k hook` xanh
  - Chạm: `hooks/scripts/*.py`, `tests/test_*hook*.py`, `tests/test_bash_gate.py`, `tests/test_stop_gate.py`, `tests/test_edit_gate.py` → 5 hook cắm vào Claude Code
  - Cần: T3.1, T3.2, T3.3

**Xong P3 khi**: 4 cổng nhận cả ba dạng trả lời (Việt · Anh · chữ cái), `hooks/` sạch tiếng Việt, test hook xanh.

## P4 — M4b: các script còn lại

- [x] **T4.1** (e40m) Dịch nhóm workflow: `tdq_eval.py` (276), `tdq_team.py` (205), `tdq_checkstatus.py` (182), `tdq_bench.py` (173) + sửa test của chúng — Test: `python3 scripts/i18n_check.py` trên 4 file = 0 và `pytest -q -k "eval or team or checkstatus or bench"` xanh
  - Chạm: `scripts/tdq_eval.py`, `scripts/tdq_team.py`, `scripts/tdq_checkstatus.py`, `scripts/tdq_bench.py`, `tests/test_tdq_eval.py`, `tests/test_tdq_team.py`, `tests/test_tdq_checkstatus.py`, `tests/test_tdq_bench.py` → node `main()`, `cli()` (Hub)
  - Cần: T2.2
- [x] **T4.2** (e35m) Dịch nhóm build & skill: `build_portable.py` (240), `tdq_checkportable.py` (117), `skill_inventory.py` (65), `skill_router.py` (54), `skill_tokens.py` (98), `plugin_tiers.py` (25), `luat_phan_loai.py` (48) + sửa test — Test: `i18n_check` trên 7 file = 0 và `pytest -q -k "portable or skill or plugin or phan_loai"` xanh
  - Chạm: `scripts/build_portable.py`, `scripts/tdq_checkportable.py`, `scripts/skill_inventory.py`, `scripts/skill_router.py`, `scripts/skill_tokens.py`, `scripts/plugin_tiers.py`, `scripts/luat_phan_loai.py`, `tests/test_build_portable.py`, `tests/test_skill_router.py`, `tests/test_skill_tokens.py` → node `cmd_build()` (Hub, bậc 17)
  - Cần: T2.2
- [x] **T4.3** (e30m) Dịch nhóm đo & phụ trợ: `token_audit.py`, `claude_export.py`, `context_surface.py`, `tdq_timing.py`, `step_audit.py`, `scan_block_symbols.py`, 5 file `canvas_*.py`, `check_canvas_layout.py` + sửa test — Test: `python3 scripts/i18n_check.py scripts/` = 0 và `pytest tests/ -q` không có lỗi mới so với mốc
  - Chạm: `scripts/token_audit.py`, `scripts/claude_export.py`, `scripts/context_surface.py`, `scripts/tdq_timing.py`, `scripts/step_audit.py`, `scripts/scan_block_symbols.py`, `scripts/canvas_*.py`, `scripts/check_canvas_layout.py`, `tests/test_token_audit.py`, `tests/test_tdq_timing.py` → node `log()` (Hub, bậc 17)
  - Cần: T4.1, T4.2

**Xong P4 khi**: `python3 scripts/i18n_check.py scripts/ hooks/` báo 0 dòng còn lại.

## P5 — M1: luật nền

- [x] **T5.1** (e20m) Viết lại luật ngôn ngữ trong `skills/tdq-conventions/SKILL.md`: 3 tầng người đọc (luật → tiếng Anh · chuỗi máy → tiếng Anh · tài liệu và đối thoại → ngôn ngữ user đọc từ state), mặc định tiếng Việt khi thiếu; dịch phần thân còn lại — Test: `python3 scripts/i18n_check.py skills/tdq-conventions/SKILL.md` = 0 và `grep -c "tiếng Việt" ` trên file = 0 ngoài dòng nói về giá trị mặc định
  - Dùng: `tdq-conventions`
  - Để: giữ đúng thứ tự ưu tiên của soul và cấu trúc mục hiện có khi viết lại luật ngôn ngữ; nạp skill TRƯỚC bước đỏ. Agent ngoài không có skill system: đọc `skills/tdq-conventions/SKILL.md` rồi làm theo.
  - Ra: `skills/tdq-conventions/SKILL.md` bản tiếng Anh có mục luật ngôn ngữ 3 tầng
  - Kiểm: `python3 scripts/i18n_check.py skills/tdq-conventions/SKILL.md` = 0
  - Không dùng cho: đổi bất kỳ luật nào ngoài luật ngôn ngữ
  - Cần: T1.2
- [x] **T5.2** (e30m) Dịch 12 file `skills/tdq-conventions/references/` (gồm `soul.md` — chỉ đổi ngôn ngữ, cấm đổi thứ tự ưu tiên) — Test: `python3 scripts/i18n_check.py skills/tdq-conventions/` = 0
  - Cần: T5.1

**Xong P5 khi**: luật gốc bằng tiếng Anh, và luật ngôn ngữ mới đã nói rõ 3 tầng.

## P6 — M2: skill khung & agent

- [x] **T6.1** (e30m) Dịch `skills/tdq-intake/` (8 file, 279 dòng) — Test: `python3 scripts/i18n_check.py skills/tdq-intake/` = 0
  - Cần: T5.1
- [x] **T6.2** (e30m) Dịch `skills/tdq-build/` (14 file, 281 dòng) — Test: `python3 scripts/i18n_check.py skills/tdq-build/` = 0
  - Dùng: `tdq-build`
  - Để: giữ nguyên 3 phase implement/qc/report và luật cứng khi dịch; nạp skill TRƯỚC bước đỏ. Agent ngoài: đọc `skills/tdq-build/SKILL.md` rồi làm theo.
  - Ra: `skills/tdq-build/**/*.md` bản tiếng Anh
  - Kiểm: `python3 scripts/i18n_check.py skills/tdq-build/` = 0
  - Không dùng cho: đổi luật tick, luật commit, hay số vòng fix của QC
  - Cần: T5.1
- [x] **T6.3** (e15m) Dịch `skills/tdq-plan/` (3 file, 157 dòng) — Test: `python3 scripts/i18n_check.py skills/tdq-plan/` = 0
  - Dùng: `tdq-plan`
  - Để: giữ nguyên khuôn plan, luật `Chạm:`/`Cần:`/`(eNm)` khi dịch; nạp skill TRƯỚC bước đỏ. Agent ngoài: đọc `skills/tdq-plan/SKILL.md` rồi làm theo.
  - Ra: `skills/tdq-plan/**/*.md` bản tiếng Anh
  - Kiểm: `python3 scripts/i18n_check.py skills/tdq-plan/` = 0
  - Không dùng cho: đổi khuôn task hay luật đo mode
  - Cần: T5.1
- [x] **T6.4** (e15m) Dịch `skills/tdq-spec/` (2 file, 115 dòng) — Test: `python3 scripts/i18n_check.py skills/tdq-spec/` = 0
  - Dùng: `tdq-spec`
  - Để: giữ nguyên khuôn spec và luật R11 (spec giữ điều kiện, plan giữ lệnh) khi dịch; nạp skill TRƯỚC bước đỏ. Agent ngoài: đọc `skills/tdq-spec/SKILL.md` rồi làm theo.
  - Ra: `skills/tdq-spec/**/*.md` bản tiếng Anh
  - Kiểm: `python3 scripts/i18n_check.py skills/tdq-spec/` = 0
  - Không dùng cho: đổi danh sách mục bắt buộc của spec
  - Cần: T5.1
- [x] **T6.5** (e12m) Dịch `skills/tdq-status/`, `skills/tdq-check-status/` và 3 file `agents/*.md` — Test: `python3 scripts/i18n_check.py skills/ agents/` = 0
  - Dùng: `tdq-status`
  - Để: giữ nguyên khuôn dòng trạng thái và dòng `➤ Duyệt:` đã đổi ở T3.3; nạp skill TRƯỚC bước đỏ. Agent ngoài: đọc `skills/tdq-status/SKILL.md` rồi làm theo.
  - Ra: `skills/tdq-status/SKILL.md`, `skills/tdq-check-status/**`, `agents/*.md` bản tiếng Anh
  - Kiểm: `python3 scripts/i18n_check.py skills/ agents/` = 0
  - Không dùng cho: đổi nội dung báo cáo trạng thái
  - Cần: T3.3, T5.1

**Xong P6 khi**: `python3 scripts/i18n_check.py skills/ agents/` = 0.

## P7 — M5: lưới đo hành vi

- [x] **T7.1** (e20m) Thêm 2 ca vào `evals/tuan-thu/`: một ca user viết tiếng Anh duyệt spec, một ca trả lời đúng một chữ cái — Test: `python3 scripts/tdq_eval.py` chạy được 2 ca mới, không sửa `ca.json` của 7 ca cũ
  - Chạm: `evals/tuan-thu/duyet-spec-tieng-anh/`, `evals/tuan-thu/duyet-bang-chu-cai/` → thư mục mới
  - Cần: T3.1, T4.1
- [ ] **T7.2** (e15m) Chạy trọn bộ `evals/tuan-thu` sau khi luật đã dịch, đối chiếu 7 ca cũ giữ nguyên kết quả — Test: bảng kết quả eval có 9 ca, 7 ca cũ giữ đúng phán quyết như trước khi dịch
  - HOÃN (quyết định lúc build): transcript của 60 bản ghi cũ nằm ở `/private/tmp` đã bị xoá nên không chấm lại được; chạy lại trực tiếp = 72 phiên `claude -p` opus (~70 USD, vài giờ) và `NHANH` đang ghim 2 commit cũ, chưa có nhánh cho cây đã dịch. Đã chạy 1 phiên khói trên cây đã dịch (ca `duyet-spec-tieng-anh`): L149/L275/L012/L210 ĐẠT, L121 vi-phạm — nằm trong dải nhiễu của 6 bản ghi `duyet-spec` cũ. Lệnh chạy đầy đủ để user tự quyết: `python3 scripts/tdq_eval.py chay --nhanh ca-hai --lan 3 --wt /private/tmp/tdq-eval-nhanh --tran-usd 70 --tiep-tuc`.
  - Cần: T6.5, T7.1

**Xong P7 khi**: lưới eval phủ cả 3 dạng trả lời và 7 ca cũ không đổi kết quả.

## P8 — M6: bản sinh & hồ sơ

- [x] **T8.1** (e10m) Sinh lại `portable_claude/` và `portable_codex/` từ nguồn đã dịch — Test: `python3 scripts/build_portable.py` chạy sạch và `python3 scripts/tdq_checkportable.py` báo khớp
  - Chạm: `portable_claude/**`, `portable_codex/**` → sinh lại toàn bộ, không sửa tay
  - Cần: T6.5
- [x] **T8.2** (e5m) Thêm dòng `## Đã chốt` vào `docs/kien-truc.md` ghi quyết định 3 tầng ngôn ngữ kèm ngày — Test: `grep "2026-08-22" docs/kien-truc.md` có dòng quyết định ngôn ngữ
  - Cần: T5.1

## P9 — Log & test bắt buộc

- [x] **T9.1** (e10m) Kiểm log service sau khi dịch: mọi dòng log giữ định dạng `[timestamp]`, mức log và cách tắt qua config không đổi — Test: chạy 3 lệnh CLI bất kỳ, output có timestamp; bật cờ tắt log thì im
  - Cần: T4.3
- [x] **T9.2** (e10m) Chạy full suite đúng một lần, so với mốc T1.1 — Test: `python3 -m pytest tests/ -q` không có lỗi mới ngoài 37 lỗi `test_skill_router.py` đã có ở mốc
  - Cần: T8.1

## Cụm song song

Sáu module của spec §2b là sáu vùng file rời nhau, nhưng **không phải sáu cụm chạy song song
được**, vì có ba ràng buộc thật:

- `tests/` bị chạm bởi gần như mọi task dịch (mỗi task sửa test của chính module mình) → các
  task dịch KHÔNG được xếp cùng đợt dù khác thư mục nguồn.
- P5 phải xong trước P6: luật nền định nghĩa luật ngôn ngữ mà các skill khung dẫn về.
- P8 phải cuối cùng: bản portable là bản sao của cả `skills/`, `hooks/`, `scripts/`, `agents/`.

Chạy song song được thật sự: **T6.1 · T6.2 · T6.3 · T6.4** (bốn thư mục skill rời nhau, không
đụng `tests/`, chỉ cần T5.1 xong trước) và **T4.1 · T4.2** (hai nhóm script rời nhau, nhưng
đụng `tests/` khác file nên vẫn tách được). Đó là trần tốc độ của mode đội: 2 đợt.

## Definition of Done

Mỗi dòng kiểm được bằng một lệnh; QC đếm hạng mục theo đúng số dòng này (spec §6 Q1–Q14).

- [x] Q1 · state giữ ngôn ngữ: `TDQ_PROJECT_DIR=<tmp> python3 scripts/tdq_state.py init x full` → state có giá trị mặc định; init kèm cờ ngôn ngữ → state giữ đúng mã
- [x] Q2 · đường cũ còn sống: `python3 -m pytest tests/test_prompt_context.py -q` xanh, gồm mọi ca duyệt tiếng Việt hiện có
- [x] Q3 · đường mới: `pytest tests/test_prompt_context.py -q -k "english or letter"` xanh cho cả 4 cổng
- [x] Q4 · đường phải chặn: `pytest tests/test_prompt_context.py -q -k reject` xanh, gồm ca `"ok but not yet"`
- [x] Q5 · chuỗi máy: `python3 scripts/i18n_check.py --kind string hooks/ scripts/` = 0
- [x] Q6 · comment mã nguồn: `python3 scripts/i18n_check.py --kind comment hooks/ scripts/` = 0
- [x] Q7 · thân luật: `python3 scripts/i18n_check.py skills/ agents/` = 0
- [x] Q8 · giữ hành vi: `git diff --stat` + `grep -c "TDQ:" hooks/scripts/*.py` bằng số ở mốc T1.1; danh sách lệnh con của `tdq_state.py` không đổi
- [x] Q9 · giữ soul: `git diff skills/tdq-conventions/references/soul.md` chỉ đổi ngôn ngữ, thứ tự 3 vế giữ nguyên
- [x] Q10 · luật ngôn ngữ mới: `grep -c "" ` trên mục luật ngôn ngữ của `tdq-conventions/SKILL.md` cho thấy đủ 3 tầng và dòng mặc định
- [ ] Q11 · lưới: `python3 -m pytest tests/ -q` không lỗi mới so với mốc, và `python3 scripts/tdq_eval.py` có 9 ca với 7 ca cũ giữ phán quyết
- [x] Q12 · bản sinh: `python3 scripts/tdq_checkportable.py` báo khớp
- [x] Q13 · log service: 3 lệnh CLI in dòng có `[timestamp]`, cờ tắt log làm im output
- [x] Q14 · hồ sơ kiến trúc: `grep "2026-08-22" docs/kien-truc.md` có dòng quyết định ngôn ngữ

## QC vòng 1 — fix

- [x] **QC1.1** Dịch chú thích tiếng Việt còn sót ở `scripts/doc_lint.py` (khối `HTML_COMMENT`) — Test: `python3 scripts/i18n_check.py --kind comment hooks/ scripts/` = 0 và `python3 -m pytest tests/test_doc_lint.py -q` xanh
  - Chạm: `scripts/doc_lint.py` → node `main()` (Hub)
