# PLAN — cổng chặn kết lượt khi plan chưa chạy hết

Ngày: 2026-08-24 · Spec: ../spec/2026-08-24-1427-implement-chay-het-plan.md (bản 1.0, ĐÃ DUYỆT) · Lane: full
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md
Sơ đồ: ../mind-map/cong-stop-ket-luot.md (ĐÃ DUYỆT)
Mode thực thi: main — user chốt "inline" lúc duyệt plan
Trạng thái plan: HOÀN THÀNH

## Mục lục

- Quy tắc thi hành (áp cho mọi task)
- P1 — Khai báo tạm hoãn trong state
- P2 — Cổng chặn thứ ba trong Stop hook
- P3 — Sửa luật trong skill
- P4 — Log & test bắt buộc
- P5 — Bản portable
- Cụm song song
- Definition of Done

## Quy tắc thi hành (áp cho mọi task)
1. Thứ tự phase là thứ tự phụ thuộc — không đảo.
2. Mỗi task: đánh `[~]` khi bắt đầu → viết test trước (đỏ) → code → test xanh → đổi sang
   `[x]` NGAY vào file này. Trạng thái checkbox: `[ ]` chưa làm · `[~]` đang làm · `[x]` xong.
3. Sau mỗi phase: chạy toàn bộ test suite, phải xanh mới sang phase sau.
4. Lệnh nào chạm state của workflow phải có `TDQ_PROJECT_DIR=<thư mục tạm>` ngay trên chính lệnh đó.
5. QC FAIL → thêm task fix vào mục QC của file này (không cần duyệt lại), loop đến khi pass.
6. Không commit/push cho đến khi user yêu cầu.
7. Chú thích, docstring và chuỗi máy in ra trong `hooks/` và `scripts/` viết TIẾNG ANH.

## P1 — Khai báo tạm hoãn trong state

- [x] **T1.1** (e10m) Thêm khoá `implement_pause` vào state mặc định của `tdq_state.py`, dạng `None` hoặc `{"ly_do", "at", "by"}`, kèm chú thích nêu vì sao khoá này là đường dừng hợp lệ duy nhất — Test: `TDQ_PROJECT_DIR=$T .venv/bin/pytest tests/test_implement_pause.py -q` xanh và `get implement_pause` trả rỗng trên state mới
  - Chạm: `scripts/tdq_state.py` → nguồn của mọi hook đọc state
- [x] **T1.2** (e14m) Thêm hai lệnh CLI `tam-hoan --ly-do "<lý do>"` và `tiep-tuc` vào `cli()`: ghi và xoá khoá `implement_pause`, thiếu `--ly-do` thì in usage và thoát khác 0 — Test: một lệnh pytest chạy đủ ba ca ghi, xoá, thiếu lý do
  - Chạm: `scripts/tdq_state.py`, `tests/test_implement_pause.py`
  - Cần: T1.1

**Xong P1 khi**: `tam-hoan` ghi được khoá, `tiep-tuc` xoá được, thiếu `--ly-do` thoát khác 0.

## P2 — Cổng chặn thứ ba trong Stop hook

- [x] **T2.1** (e12m) Viết hàm quyết định thuần trong `stop_gate.py` nhận state và kết quả `plan_tick_state`, trả lý do chặn hoặc `None`, phủ đúng sáu nhánh B6–B12 của sơ đồ — Test: pytest gọi thẳng hàm này với sáu bộ đầu vào, không cần payload thật
  - Chạm: `hooks/scripts/stop_gate.py`, `tests/test_stop_gate.py`
  - Cần: T1.1
  - Dùng: `tdq-lsp-setup`
  - Để: tra mọi nơi gọi `plan_tick_state` và `effective_phase` trước khi sửa, nạp skill TRƯỚC bước đỏ. Agent ngoài không có skill system: đọc `skills/tdq-lsp-setup/SKILL.md` rồi làm theo.
  - Ra: danh sách nơi gọi ghi vào phần ghi chú của task trong file này
  - Kiểm: `mcp__lsp__find_references` chạy trên hai ký hiệu trên, kết quả khác rỗng
  - Không dùng cho: sửa code hộ, skill này chỉ lo lớp tìm kiếm
- [x] **T2.2** (e10m) Nối hàm quyết định vào `main()`, đặt SAU hai cổng cũ, in payload `decision: block` mang mã `[TDQ:UNFINISHED]`, số task còn hở và `stop_hook_active: false`, dài không quá 300 ký tự — Test: pytest bơm payload không sửa file, phase `implement`, plan còn task hở → nhận đúng payload chặn
  - Chạm: `hooks/scripts/stop_gate.py`, `tests/test_stop_gate.py`
  - Cần: T2.1
- [x] **T2.3** (e12m) Trần chống kẹt: đếm số lần chặn liên tiếp mà chữ ký checkbox của plan không đổi, đủ ba lần thì hạ xuống nhắc và thôi chặn; bộ đếm reset khi checkbox nhúc nhích — Test: pytest chạy bốn vòng chặn liên tiếp, vòng bốn không còn `decision: block`
  - Chạm: `hooks/scripts/stop_gate.py`, `tests/test_stop_gate.py`
  - Cần: T2.2
- [x] **T2.4** (e8m) Đường im lặng đi qua: thiếu state, thiếu `active_request`, plan không đọc được, phase ngoài `implement`, mọi task `[x]`, còn task `[>]`, có khoá tạm hoãn — bảy ca đều không chặn, ca tạm hoãn in kèm lý do đã khai — Test: pytest bảy ca, không ca nào trả `decision`
  - Chạm: `hooks/scripts/stop_gate.py`, `tests/test_stop_gate.py`
  - Cần: T2.2
- [x] **T2.5** (e6m) Kiểm bằng chạy thật rằng `stop_hook_active: false` cho phép chặn lặp, ghi kết quả quan sát vào file QC của request — Test: một lượt thật bị chặn hai lần liên tiếp, hoặc ghi rõ hành vi khác nếu tài liệu sai
  - Cần: T2.2
  - Dùng: `WebFetch`
  - Để: đối chiếu lại tài liệu `Stop` hook chính thức nếu quan sát thật lệch với tài liệu
  - Ra: một dòng nguồn kèm URL trong file QC của request
  - Kiểm: file QC có dòng nguồn đó
  - Không dùng cho: tra cứu ngoài phạm vi hợp đồng hook

**Xong P2 khi**: sáu nhánh quyết định có test riêng, hai cổng cũ vẫn xanh.

## P3 — Sửa luật trong skill

- [x] **T3.1** (e8m) Nêu đích danh cổng `[TDQ:UNFINISHED]` và lệnh `tam-hoan` trong Hard rules của `skills/tdq-build/SKILL.md` và trong hàng `implement` của `skills/tdq-conventions/references/phases.md` — Test: `grep -l "TDQ:UNFINISHED" skills/tdq-build/SKILL.md skills/tdq-conventions/references/phases.md` trả cả hai file
  - Cần: T2.2
  - Dùng: `tdq-build`
  - Để: sửa đúng mục Hard rules mà không phá cấu trúc skill đang chạy
  - Ra: hai file luật đã sửa
  - Kiểm: `grep -l "TDQ:UNFINISHED" skills/tdq-build/SKILL.md skills/tdq-conventions/references/phases.md`
  - Không dùng cho: đổi luồng phase hay đổi gate khác

## P4 — Log & test bắt buộc

- [x] **T4.1** (e6m) Mỗi quyết định chặn in một dòng `_info` nêu phase, số task còn hở và đường dẫn plan; `TDQ_LOG=0` tắt được như nếp sẵn có — Test: pytest bắt stderr thấy đúng dòng log, và im khi `TDQ_LOG=0`
  - Chạm: `hooks/scripts/stop_gate.py`, `tests/test_stop_gate.py`
  - Cần: T2.2
- [x] **T4.2** (e10m) Chạy trọn bộ test và hai bộ gác ngôn ngữ, so mốc `22fa2eb` không có test đỏ MỚI — Test: `.venv/bin/pytest tests/ -q`, `python3 scripts/i18n_check.py hooks/scripts/stop_gate.py scripts/tdq_state.py`, `python3 scripts/doc_lint.py docs/tdq`
  - Cần: T2.3, T2.4, T3.1, T4.1
  - Dùng: `tdq-plan`
  - Để: QC FAIL thì thêm task fix vào chính file plan này theo đúng khuôn, không cần duyệt lại
  - Ra: task fix mới trong plan nếu có FAIL
  - Kiểm: `python3 scripts/doc_lint.py --pair docs/tdq/spec/2026-08-24-1427-implement-chay-het-plan.md docs/tdq/plan/2026-08-24-1427-implement-chay-het-plan.md`
  - Không dùng cho: sửa spec đã duyệt

- [x] **T4.3** (e6m) Cập nhật sơ đồ `cong-stop-ket-luot`: bốn bước còn `(?)` thay bằng cặp `file::hàm` thật vừa viết — Test: `python3 scripts/tdq_mindmap.py doi-chieu docs/tdq/mind-map/cong-stop-ket-luot.md` thoát 0 và file không còn `(?)`
  - Dùng: `tdq-diagram`
  - Để: giữ sơ đồ khớp code sau khi implement, đúng luật một feature một file sống
  - Ra: `docs/tdq/mind-map/cong-stop-ket-luot.md` và trang HTML dựng lại
  - Kiểm: `python3 scripts/tdq_mindmap.py kiem docs/tdq/mind-map/cong-stop-ket-luot.md`
  - Không dùng cho: vẽ thêm feature mới ngoài phạm vi request
  - Cần: T2.3, T2.4

## P5 — Bản portable

- [x] **T5.1** (e6m) Sinh lại hai bản portable để hook và script mới có mặt ngoài Claude Code — Test: `python3 scripts/build_portable.py` thoát 0 và `grep -c "TDQ:UNFINISHED" portable_claude/.claude/tdq/hooks/scripts/stop_gate.py` lớn hơn 0
  - Chạm: `portable_claude/`, `portable_codex/`
  - Cần: T4.2

## Cụm song song

Ba cụm không giao file: cụm state (`scripts/tdq_state.py` — T1.1, T1.2), cụm hook
(`hooks/scripts/stop_gate.py` — T2.1 đến T2.4, T4.1), cụm tài liệu (T3.1). Cụm hook phụ
thuộc T1.1 nên chỉ chạy sau, và mọi task trong cụm hook đụng chung một file nên phải nối
tiếp nhau, không tách đợt được. T3.1 chạy song song với cả hai cụm kia. T4.2 và T5.1 là
cổng gộp cuối, chạy một mình.

## Definition of Done

- [x] Q1 Phase `implement`, plan còn task hở, không tạm hoãn, lượt không sửa file → trả `decision: block` — `.venv/bin/pytest tests/test_stop_gate.py -q -k unfinished_chan_ca_chinh`
- [x] Q2 Payload chặn chứa `[TDQ:UNFINISHED]`, nêu số task còn hở, không quá 300 ký tự — `.venv/bin/pytest tests/test_stop_gate.py -q -k unfinished_noi_dung`
- [x] Q3 Payload chặn có `stop_hook_active: false`, vào lại với cờ `true` vẫn chặn — `.venv/bin/pytest tests/test_stop_gate.py -q -k unfinished_chan_lap`
- [x] Q4 Ba lần chặn liên tiếp không tiến triển → lần thứ tư chỉ nhắc — `.venv/bin/pytest tests/test_stop_gate.py -q -k unfinished_tran`
- [x] Q5 Có khoá `implement_pause` → không chặn và lý do được in — `.venv/bin/pytest tests/test_stop_gate.py -q -k unfinished_tam_hoan`
- [x] Q6 Plan còn task `[>]` → không chặn — `.venv/bin/pytest tests/test_stop_gate.py -q -k unfinished_subagent`
- [x] Q7 Phase ngoài `implement` → không chặn — `.venv/bin/pytest tests/test_stop_gate.py -q -k unfinished_ngoai_phase`
- [x] Q8 Mọi task `[x]` → không chặn — `.venv/bin/pytest tests/test_stop_gate.py -q -k unfinished_plan_xong`
- [x] Q9 Thiếu state hoặc plan không đọc được → không chặn — `.venv/bin/pytest tests/test_stop_gate.py -q -k unfinished_thieu_bang_chung`
- [x] Q10 `tam-hoan --ly-do` ghi được, `tiep-tuc` xoá được, thiếu lý do thoát khác 0 — `.venv/bin/pytest tests/test_implement_pause.py -q -k tam_hoan`
- [x] Q11 Hai cổng cũ nguyên vẹn — `.venv/bin/pytest tests/test_stop_gate.py -q`
- [x] Q12 Hai file luật nêu đích danh cổng mới và lệnh tạm hoãn — `grep -l "TDQ:UNFINISHED" skills/tdq-build/SKILL.md skills/tdq-conventions/references/phases.md`
- [x] Q13 Mỗi lần chặn in một dòng `_info` đủ ba dữ kiện — `.venv/bin/pytest tests/test_stop_gate.py -q -k unfinished_log`
- [x] Q14 Hai file mã đã sửa sạch lỗi ngôn ngữ — `python3 scripts/i18n_check.py hooks/scripts/stop_gate.py scripts/tdq_state.py`
- [x] Q15 Hai bản portable mang hook và script mới — `python3 scripts/build_portable.py && grep -c "TDQ:UNFINISHED" portable_claude/.claude/tdq/hooks/scripts/stop_gate.py`
- [x] Q16 Không có test đỏ MỚI so mốc `22fa2eb` — `.venv/bin/pytest tests/ -q`
