# SPEC — cổng chặn kết lượt khi plan chưa chạy hết

Ngày: 2026-08-24 · Bản: 1.0 · Brief: ../brief/2026-08-24-1427-implement-chay-het-plan.md · Lane: full
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md
Trạng thái: CHỜ DUYỆT

## Mục lục

- 1. Mục tiêu & phạm vi
- 1b. Lộ trình
- 2. Đầu ra cụ thể
- 2b. Ranh giới module
- 3. Cách tiếp cận & lý do
- 3b. Năng lực & công cụ
- 4. Yêu cầu bắt buộc
- 5. Ràng buộc & rủi ro
- 6. QC & Definition of Done
- 7. Câu hỏi còn mở

## 1. Mục tiêu & phạm vi

- Mục tiêu: khi phase là `implement` và plan còn task chưa `[x]`, `Stop` hook TỪ CHỐI kết
  lượt và đẩy model chạy tiếp. Đường dừng duy nhất là khai báo lý do; không còn đường dừng
  im lặng.
- Trong phạm vi: điểm chặn thứ ba trong `hooks/scripts/stop_gate.py` · lệnh khai báo tạm
  hoãn trong `scripts/tdq_state.py` · sửa luật ở `skills/tdq-build/SKILL.md` và
  `skills/tdq-conventions/references/phases.md` · test · sinh lại hai bản portable.
- NGOÀI phạm vi: phase `qc` và `report` (chỉ chặn `implement`) · hai điểm chặn cũ
  `[TDQ:LOG]` và `[TDQ:TICK]` giữ nguyên hành vi · không đụng `edit_gate.py`,
  `bash_gate.py`, `prompt_context.py` · không sửa 38 test đỏ có sẵn.

## 1b. Lộ trình

| Bước/phase | Chạy? | Vì sao |
|---|---|---|
| Research web | BỎ | Nguyên nhân nằm trong code repo, tài liệu hook đã tra ở analyze |
| Interview | CÓ (xong) | 4 câu đã chốt 1a/2a/3a/4a |
| diagram | CÓ | Bắt buộc ở lane full — một luồng: nhánh quyết định của `Stop` hook |
| QC độc lập (agent) | BỎ | Chạm một file hook và một script, QC leader tự chạy đủ |
| Chia sub-agent | CÓ | Chốt ở gate mode sau khi duyệt plan |

## 2. Đầu ra cụ thể

| # | Đầu ra | Đường dẫn/vị trí | Đo "xong" bằng |
|---|---|---|---|
| 1 | Điểm chặn thứ ba `[TDQ:UNFINISHED]` | `hooks/scripts/stop_gate.py` | Phase `implement`, plan còn task hở, không khai tạm hoãn → payload trả `decision: block` |
| 2 | Chặn lặp được | `hooks/scripts/stop_gate.py` | Payload chặn có `stop_hook_active: false`; cờ vào bằng `true` vẫn chặn lại được |
| 3 | Trần an toàn chống kẹt | `hooks/scripts/stop_gate.py` | Ba lần chặn liên tiếp mà checkbox không nhúc nhích → hạ xuống nhắc, không chặn nữa |
| 4 | Lệnh khai báo tạm hoãn | `scripts/tdq_state.py` | `tam-hoan --ly-do "<lý do>"` ghi khoá `implement_pause`; `tiep-tuc` xoá khoá đó |
| 5 | Miễn trừ sub-agent đang chạy | `hooks/scripts/stop_gate.py` | Plan còn task `[>]` → không chặn |
| 6 | Luật đã sửa | `skills/tdq-build/SKILL.md`, `skills/tdq-conventions/references/phases.md` | Cả hai file nêu đích danh `[TDQ:UNFINISHED]` và lệnh `tam-hoan` |
| 7 | Test khoá hành vi cổng mới | vùng test của repo | Chạy một lệnh, xanh, phủ đủ 6 nhánh quyết định |
| 8 | Hai bản portable | `portable_claude/`, `portable_codex/` | `build_portable.py` chạy lại, hai manifest mang hook và script mới |

## 2b. Ranh giới module

| Module | Vùng file | Phụ thuộc module | Đầu ra §2 nào |
|---|---|---|---|
| cong-dung | `hooks/scripts/stop_gate.py` | khai-bao | 1, 2, 3, 5 |
| khai-bao | `scripts/tdq_state.py` | không | 4 |
| luat | `skills/tdq-build/SKILL.md`, `skills/tdq-conventions/references/phases.md` | không | 6 |
| kiem | vùng test của repo | cong-dung, khai-bao | 7 |
| ban-ngoai | `portable_claude/`, `portable_codex/` | cong-dung, khai-bao, luat | 8 |

Ranh giới lấy từ LSP: `stop_gate.py` import `plan_tick_state`, `task_open_count`,
`effective_phase`, `load` từ `tdq_state.py` — chiều phụ thuộc một hướng, đúng luật gọi ở
`docs/kien-truc.md`. Không module nào khai chung đường dẫn.

## 3. Cách tiếp cận & lý do

- Chọn: thêm điểm chặn thứ ba vào `main()` của `stop_gate.py`, đặt SAU `[TDQ:LOG]` và
  `[TDQ:TICK]`. Điều kiện chặn: `effective_phase == "implement"` VÀ
  `plan_tick_state` có `exists`, `total > 0`, `not all_done` VÀ không có khoá
  `implement_pause` VÀ không có task `[>]` đang giao.
- Vì: `Stop` là sự kiện DUY NHẤT có quyền từ chối kết lượt. Luật trong skill đã nói đúng
  điều này từ lâu mà vẫn hỏng, chứng tỏ chữ không đủ, phải có cổng.
- Vì (điều kiện chặn không đòi có sửa file): đúng ca người dùng báo. Nhịp cuối thường
  không sửa gì, nên ràng buộc `culprit` của hai cổng cũ chính là lỗ lọt.
- Vì (khai báo thay vì đoán): hook không thể tự biết một lỗi có tự fix được hay không.
  Bắt bên muốn dừng ghi lý do ra state là cách duy nhất để câu "tôi bị kẹt" kiểm chứng
  được, và chính dòng lý do đó là thứ in cho user.
- Đã loại: chặn ở `PreToolUse` — sai tầng, kết lượt không phải một tool call.
- Đã loại: chỉ thêm dòng nhắc — user đã bác ở câu 1, nhắc suông chính là hiện trạng.
- Đã loại: chặn lặp vô hạn không trần — một phiên kẹt sẽ không có đường thoát nào ngoài
  giết tiến trình.

## 3b. Năng lực & công cụ

| Skill | Nguồn | Phán quyết | Dùng ở đâu / Lý do loại |
|---|---|---|---|
| tdq-build | plugin:tdq-workflow | DÙNG | Đầu ra 6 — sửa Hard rules |
| tdq-conventions | plugin:tdq-workflow | NỀN | Khung luật đang chạy |
| tdq-diagram | plugin:tdq-workflow | DÙNG | Phase `diagram` trước plan |
| tdq-plan | plugin:tdq-workflow | DÙNG | Viết plan sau khi duyệt spec |
| tdq-spec | plugin:tdq-workflow | NỀN | Skill đang chạy |
| tdq-lsp-setup | plugin:tdq-workflow | DÙNG | Đã kiểm 6/6 bậc trước khi phân tích |
| WebFetch | built-in | DÙNG | Tra tài liệu `Stop` hook, kiểm lại ở đầu ra 2 |
| Đã xét 213 skill khác | user/plugin/built-in | KHÔNG | khác lĩnh vực |

## 4. Yêu cầu bắt buộc

- Log service bật mặc định: timestamp, đủ chi tiết debug, tắt/giảm được qua config. Mọi
  quyết định chặn phải in một dòng `_info` nêu nguồn bằng chứng, theo đúng nếp hai cổng cũ.
- Không placeholder, không TODO stub, không mock trình bày như dữ liệu thật.
- Mỗi thành phần có unit test riêng, chạy được bằng một lệnh.
- Code viết ra bám 5 nguyên tắc SOLID theo
  `skills/tdq-conventions/references/clean-code.md`, và bám rule ngôn ngữ trong
  `skills/tdq-build/references/rules/`.

## 5. Ràng buộc & rủi ro

Ràng buộc kiến trúc phải giữ:

- `2026-07-29: hook chỉ nhắc và kiểm bằng hiệu ứng thật, không trả deny vì lý do "chưa
  duyệt".` — việc này chạm ở `stop_gate.py`. Cổng mới hợp luật: nó kiểm HIỆU ỨNG THẬT
  (checkbox trên đĩa), và `Stop` không phải `deny` của `PreToolUse`.
- `hooks/ được gọi scripts/; scripts/ không được import hooks/.` — chạm ở
  `stop_gate.py` import `tdq_state.py`, đúng chiều cho phép.
- `2026-08-22: chú thích/docstring của hooks/ + scripts/ và chuỗi máy in ra viết TIẾNG
  ANH.` — chạm ở cả hai file code, gác bằng `i18n_check.py`.

| Rủi ro | Ảnh hưởng | Cách giảm |
|---|---|---|
| Chặn oan → mọi lượt của mọi request đều kẹt | Rất nặng, hook chạy ở user scope | Bốn điều kiện phải cùng đúng mới chặn; thiếu state, thiếu plan, sai phase đều im lặng đi qua |
| Chặn lặp thành vòng vô tận | Phiên không thoát được | Trần ba lần chặn liên tiếp không có tiến triển, sau đó hạ xuống nhắc |
| `stop_hook_active: false` không đúng như tài liệu | Chặn lặp không hoạt động | Đầu ra 2 phải kiểm bằng chạy thật, không tin mỗi tài liệu |
| Model khai tạm hoãn dối để thoát | Mất tác dụng cổng | Lý do nằm trong state và bị in cho user; report phải liệt kê mọi lần tạm hoãn |
| Test cũ của `stop_gate` đỏ theo | Hồi quy | Chạy `tests/test_stop_gate*.py` trước khi đóng task |

## 6. QC & Definition of Done

| # | Hạng mục kiểm | Điều kiện PASS |
|---|---|---|
| Q1 | Chặn đúng ca chính | Phase `implement`, plan còn task hở, không tạm hoãn, lượt KHÔNG sửa file → vẫn trả `decision: block` |
| Q2 | Mã và lời chặn | Payload chặn chứa `[TDQ:UNFINISHED]`, nêu số task còn hở, dài không quá 300 ký tự |
| Q3 | Chặn lặp | Payload chặn có `stop_hook_active: false`; vào lại với cờ `true` vẫn chặn |
| Q4 | Trần chống kẹt | Ba lần chặn liên tiếp mà checkbox không đổi → lần thứ tư chỉ nhắc, không chặn |
| Q5 | Miễn khi đã khai tạm hoãn | Có khoá `implement_pause` → không chặn, và lý do được in ra |
| Q6 | Miễn khi sub-agent đang chạy | Plan còn task `[>]` → không chặn |
| Q7 | Không chặn ngoài phase implement | Phase `qc`, `report`, `spec`, `plan`, `idle` → không chặn |
| Q8 | Không chặn khi plan xong | Mọi task `[x]` → không chặn |
| Q9 | Im lặng khi thiếu bằng chứng | Không state, không `active_request`, hoặc plan không đọc được → không chặn |
| Q10 | Lệnh tạm hoãn | `tam-hoan --ly-do "<lý do>"` ghi được, `tiep-tuc` xoá được, thiếu `--ly-do` thì thoát khác 0 |
| Q11 | Hai cổng cũ nguyên vẹn | `tests/test_stop_gate*.py` cũ xanh hết |
| Q12 | Luật đã sửa | Hai file luật nêu đích danh `[TDQ:UNFINISHED]` và `tam-hoan` |
| Q13 | Log quyết định | Mỗi lần chặn in một dòng `_info` nêu phase, số task hở, đường dẫn plan |
| Q14 | i18n | `i18n_check.py` trên hai file code đã sửa → 0 dòng |
| Q15 | Bản portable | `build_portable.py` chạy lại, hai manifest có hook và script mới |

DoD: 15 hạng mục trên PASS · `pytest tests/ -q` không có test đỏ MỚI so mốc `22fa2eb` ·
`doc_lint.py` và `i18n_check.py` thoát 0 · mọi task trong plan `[x]`.

## 7. Câu hỏi còn mở

(Rỗng.)
