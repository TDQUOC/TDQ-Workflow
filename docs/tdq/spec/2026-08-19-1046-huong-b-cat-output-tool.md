# SPEC — Hướng B: cắt output tool

Ngày: 2026-08-19 · Bản: 1.0 · Brief: ../brief/2026-08-19-1046-huong-b-cat-output-tool.md · Lane: full
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

- Mục tiêu: cắt phần token do **output tool** chiếm giữa một request, bằng ba việc tách
  bạch — (a) làm thước đo `token_audit.py` đếm đúng thay vì ước lượng ký tự/4, (b) thêm
  luật + hook nhắc cho đúng chỗ số đo chỉ ra, (c) áp một khoá cấu hình nền tảng chạm
  được nhóm output khổng lồ của tool bên thứ ba. Đo lại trước/sau trên cùng bộ session.
- Trong phạm vi: sửa `scripts/token_audit.py`; thêm luật vào `skills/tdq-conventions/`;
  thêm phần nhắc vào `hooks/scripts/bash_gate.py`; ghi `MAX_MCP_OUTPUT_TOKENS` vào
  `~/.claude/settings.json` (có backup); sinh lại hai bản portable; test khoá cho mọi
  thay đổi; đính chính đề án; report.
- NGOÀI phạm vi (chép từ brief `### Phạm vi đã chốt`, dòng "Mặt LOẠI"): bảo mật · trải
  nghiệm người dùng · an toàn dữ liệu. Ngoài ra: KHÔNG đụng `BASH_MAX_OUTPUT_LENGTH`
  (số đo bác bỏ, xem §3); KHÔNG sửa hành vi chặn của hook (chỉ nhắc, không `deny`);
  KHÔNG đụng hướng A/E — mỗi hướng một request riêng.

## 1b. Lộ trình

Chép từ brief mục `### Lộ trình`. User duyệt spec là duyệt luôn lộ trình này.

| Bước/phase | Chạy? | Vì sao |
|---|---|---|
| Research web | CÓ (xong ở analyze) | phải tra biến môi trường trần output, không đoán |
| Đo bằng số thật | CÓ (xong ở analyze) | đề án không có số nào cho hướng B |
| Vòng scope | CÓ (xong ở chat) | user chốt 1ABCD · 2A · 3A |
| Interview chi tiết thêm | BỎ | mọi câu còn lại đã trả lời được bằng số vừa đo |
| Chia subagent | BỎ | phiên hiện tại cấm gọi AgentTool khi user không yêu cầu |
| QC độc lập (agent) | BỎ | cùng lý do trên; QC chạy bằng lệnh đo lại được |
| Sinh lại portable + test khoá | CÓ | user chốt 3A |

## 2. Đầu ra cụ thể

| # | Đầu ra | Đường dẫn/vị trí | Đo "xong" bằng |
|---|---|---|---|
| 1 | `token_audit.py` đếm bằng `anthropic_tokenizer`, có cache, thiếu venv thì LỖI rõ ràng | `scripts/token_audit.py` | chạy được, không còn hằng số ký tự/4 trên đường tính chính; thiếu venv thì thoát khác 0 kèm câu hướng dẫn |
| 2 | Bảng phân rã hành vi mới trong cùng script | `scripts/token_audit.py` | in được: mỗi tool có n · trung vị · p90 · p99 · max; và tỉ lệ `Read` có `offset`/`limit`, tỉ lệ `Read` đọc lại trong cùng session |
| 3 | Test khoá cho hai đầu ra trên | bộ test của repo | test mới đỏ trước khi sửa, xanh sau khi sửa |
| 4 | Luật mới: phân biệt "đọc lại vì luật" và "đọc lại vì quên" | `skills/tdq-conventions/references/context-budget.md` | mục mới nêu đủ 5 ca bắt buộc cũ + tiêu chí nhận diện lần đọc lại KHÔNG thuộc 5 ca đó |
| 5 | Luật mới: trần output cho tool ngoài (MCP) | `skills/tdq-conventions/references/context-budget.md` | có dòng luật nêu ngưỡng số cụ thể và việc phải làm khi vượt |
| 6 | Hook nhắc khi lệnh Bash đọc file lớn mà không giới hạn | `hooks/scripts/bash_gate.py` | nhắc đúng mã `[TDQ:*]`, KHÔNG trả `deny`; lệnh đã có giới hạn thì im lặng |
| 7 | Test khoá cho hook | bộ test của repo | test mới đỏ trước, xanh sau; ca "đã có giới hạn" phải không bị nhắc |
| 8 | Backup settings trước khi ghi | `docs/tdq/audit/settings-backup-2026-08-19-huong-b.json` | file tồn tại, parse được JSON, khớp md5 bản gốc |
| 9 | `~/.claude/settings.json` có `MAX_MCP_OUTPUT_TOKENS` | `~/.claude/settings.json` | parse lại được; khoá mới có mặt; mọi khoá cấp cao sẵn có còn nguyên |
| 10 | Hai bản portable sinh lại | `portable_claude/`, `portable_codex/` | lệnh sinh thoát 0; nội dung luật và script mới có đủ ở cả hai bản |
| 11 | Bảng đo trước/sau trên cùng bộ session | `docs/tdq/audit/de-an-toi-uu-context.md` | mục đính chính mới có bảng số trước/sau, nêu rõ phần nào đo được và phần nào chỉ kiểm chứng được ở phiên mới |
| 12 | Report | `docs/tdq/reports/2026-08-19-1046-huong-b-cat-output-tool.md` | file tồn tại, máy kiểm tài liệu thoát 0 |

## 2b. Ranh giới module

| Module | Vùng file | Phụ thuộc module | Đầu ra §2 nào |
|---|---|---|---|
| M1 thước đo | `scripts/token_audit.py` | không | 1, 2, 3 |
| M2 luật | `skills/tdq-conventions/references/context-budget.md`, `skills/tdq-conventions/SKILL.md` | không | 4, 5 |
| M3 hook | `hooks/scripts/bash_gate.py` | M2 (mã nhắc phải khớp luật) | 6, 7 |
| M4 cấu hình | `~/.claude/settings.json`, `docs/tdq/audit/settings-backup-2026-08-19-huong-b.json` | không | 8, 9 |
| M5 portable + sổ sách | `portable_claude/`, `portable_codex/`, `docs/tdq/audit/de-an-toi-uu-context.md`, `docs/tdq/reports/` | M1, M2, M3, M4 | 10, 11, 12 |

Test của M1/M3 nằm trong vùng file của chính module đó về mặt trách nhiệm; đường dẫn cụ
thể do plan chỉ định.

## 3. Cách tiếp cận & lý do

- **Chọn: sửa thước đo TRƯỚC khi cắt.** `token_audit.py` đang dùng ước lượng ký tự/4.
  Hai vòng trước (hướng D, hướng C) đều sai vì tin dụng cụ đo chưa kiểm; vòng này không
  lặp lại. Mọi con số "tiết kiệm" chỉ được tuyên bố sau khi thước đo đã chuẩn.
- **Chọn: KHÔNG đụng `BASH_MAX_OUTPUT_LENGTH`.** Đo 3.067 lệnh Bash trong 5 session:
  trung vị 399 ký tự, p99 7.854, max 25.654 — **0 lệnh** chạm trần mặc định 30.000. Hạ
  trần chỉ cắt mất output thật chứ không cắt lãng phí. Đây là đính chính cho chính đề
  xuất ban đầu của tôi ở vòng scope.
- **Chọn: `MAX_MCP_OUTPUT_TOKENS` là đòn bẩy cấu hình duy nhất.** Nhóm tốn 18,1%
  carry-cost là output của một tool MCP bên thứ ba với 13 lần gọi; không luật văn bản
  nào của TDQ với tới tool ngoài, chỉ trần của nền tảng chạm được.
- **Chọn: hook chỉ NHẮC, không chặn.** Bám quyết định kiến trúc 2026-07-29 ("hook chỉ
  nhắc và kiểm bằng hiệu ứng thật"). Chặn một lệnh đọc file lớn có thể chặn đúng lần đọc
  cần cho chất lượng — trái soul.
- **Chọn: tách "đọc lại vì luật" khỏi "đọc lại vì quên".** 64,2% lần `Read` là đọc lại,
  nhưng phần lớn do chính luật TDQ bắt buộc ("cấm làm theo trí nhớ", 5 ca bắt buộc đọc
  lại). Cắt mù vào con số này là cắt vào chất lượng. Luật mới phải nêu tiêu chí nhận
  diện, không nêu chỉ tiêu giảm.
- **Đã loại: đặt chỉ tiêu giảm % carry-cost** — vì phần lớn carry-cost đến từ việc đọc
  đúng thứ cần đọc; đặt chỉ tiêu là thưởng cho việc đọc thiếu.
- **Đã loại: viết công cụ đo mới** — `token_audit.py` đã tồn tại và đúng mô hình
  carry-cost; dựng mới là bỏ phí phần đúng.

## 3b. Năng lực & công cụ

| Skill | Nguồn | Phán quyết | Dùng ở đâu / Lý do loại |
|---|---|---|---|
| `tdq-spec`, `tdq-plan`, `tdq-build` | plugin:tdq-workflow | DÙNG | chạy phase tương ứng |
| `tdq-conventions` | plugin:tdq-workflow | NỀN | skill khung; §10 và `context-budget.md` là chỗ sửa của M2 |
| `scripts/token_audit.py` | project | DÙNG | đầu ra 1, 2, 11 |
| `scripts/build_portable.py` | project | DÙNG | đầu ra 10 |
| `scripts/doc_lint.py` | project | DÙNG | kiểm tài liệu ở mọi phase |
| `tdq-status`, `tdq-check-status` | plugin:tdq-workflow | KHÔNG | khác lĩnh vực — không hỏi trạng thái, không khôi phục phiên |
| Đã xét 278 skill khác | plugin/built-in | KHÔNG | khác lĩnh vực |

## 4. Yêu cầu bắt buộc

- Log service bật mặc định: `token_audit.py` và `bash_gate.py` đều có runtime; log ra
  stderr kèm timestamp ISO, tắt được bằng biến môi trường sẵn có của từng file, giữ
  nguyên hợp đồng log hiện tại.
- Không placeholder, không TODO stub, không số liệu bịa.
- Mỗi thay đổi có test riêng, chạy được bằng một lệnh; test phải đỏ trước khi sửa.
- Code bám SOLID theo `skills/tdq-conventions/references/clean-code.md` và rule ngôn ngữ
  trong `skills/tdq-build/references/rules/`.
- **Backup `~/.claude/settings.json` trước khi ghi** — không có backup thì cấm ghi. Ghi
  bằng `json.load` → sửa dict → `json.dump`, cấm sửa chuỗi thô, ghi xong parse lại.
- **Cấm sửa tay** `portable_claude/` và `portable_codex/` — chỉ sinh lại bằng script.
- Cấm tuyên bố mức tiết kiệm khi chưa đo bằng thước đo đã sửa.

## 5. Ràng buộc & rủi ro

Ràng buộc kiến trúc phải giữ (chép từ `docs/kien-truc.md`, chỉ dòng việc này chạm):

- "`hooks/` được gọi `scripts/`; `scripts/` **không** được import `hooks/`" — việc này
  chạm ở `hooks/scripts/bash_gate.py` và `scripts/token_audit.py`.
- "hook chỉ nhắc và kiểm bằng hiệu ứng thật, không trả `deny`" — chạm ở đầu ra 6.
- "Luật bản ngoài `portable_claude/`, `portable_codex/` SINH bằng
  `scripts/build_portable.py`, không sửa tay" — chạm ở đầu ra 10.

| Rủi ro | Ảnh hưởng | Cách giảm |
|---|---|---|
| Đổi cách đếm token làm số mới không so được với số cũ | bảng trước/sau vô nghĩa | đo lại CẢ hai mốc bằng thước đo mới trên cùng bộ session, không so số mới với số cũ |
| `anthropic_tokenizer` chạy trên hàng triệu ký tự quá chậm | công cụ đo thành không dùng được | đo thời gian chạy, thêm cache theo nội dung; ngưỡng PASS ở §6 |
| Hook nhắc quá nhiều thành nhiễu, bị bỏ qua | luật mất tác dụng, giống lỗi đã có ở các hook khác | chỉ nhắc khi lệnh KHÔNG có giới hạn nào; có `head`/`tail`/`-c`/`-n` thì im lặng — khoá bằng test |
| Ghi hỏng `~/.claude/settings.json` | chặn toàn bộ công việc của user trên mọi project | backup trước; ghi qua dict; parse lại sau khi ghi |
| `MAX_MCP_OUTPUT_TOKENS` không có tác dụng thật | tưởng đã cắt mà chưa | nguồn hiện là deepwiki + issue, chưa phải tài liệu chính thức đầy đủ; report phải ghi rõ cần kiểm chứng ở PHIÊN MỚI |
| Luật mới bị hiểu thành "hạn chế đọc lại" | cắt vào chất lượng, trái soul | luật viết dạng tiêu chí nhận diện, giữ nguyên 5 ca bắt buộc đọc lại, nêu thẳng câu "nghi ngờ thì đọc lại" |

## 6. QC & Definition of Done

| # | Hạng mục kiểm | Điều kiện PASS |
|---|---|---|
| Q1 | Thước đo đếm đúng | không còn đường tính chính dựa trên ước lượng ký tự/4; thiếu venv tokenizer thì thoát khác 0 kèm hướng dẫn, không âm thầm ước lượng |
| Q2 | Bảng phân rã hành vi có đủ cột | in ra n, trung vị, p90, p99, max cho từng tool; có tỉ lệ `Read` giới hạn và tỉ lệ `Read` đọc lại |
| Q3 | Thước đo còn chạy đủ nhanh để dùng | đo 5 session xong dưới 60 giây trên máy này |
| Q4 | Test mới thật sự khoá được hành vi | mỗi test mới đỏ trước khi sửa, xanh sau khi sửa, có dán kết quả cả hai lần |
| Q5 | Hook nhắc đúng chỗ | lệnh đọc file lớn không giới hạn → có nhắc; lệnh đã có giới hạn → không nhắc; không ca nào trả `deny` |
| Q6 | Luật mới không cắt vào chất lượng | mục mới giữ nguyên 5 ca bắt buộc đọc lại và câu "nghi ngờ thì đọc lại"; không có chỉ tiêu giảm % nào được đặt ra |
| Q7 | Backup hợp lệ trước khi ghi settings | backup parse được JSON và khớp md5 bản gốc tại thời điểm backup |
| Q8 | Settings sau khi ghi vẫn hợp lệ | parse được; có khoá mới; mọi khoá cấp cao sẵn có còn nguyên |
| Q9 | Ba bản đồng bộ | lệnh sinh portable thoát 0; luật mới và script mới có mặt ở cả hai bản portable |
| Q10 | Toàn bộ test suite | không có test đỏ mới so với trước request; test đỏ sẵn có phải chứng minh là có sẵn |
| Q11 | Số trước/sau trung thực | bảng đo lấy từ thước đo đã sửa cho cả hai mốc; phần chưa kiểm chứng được ghi rõ là chưa kiểm chứng |
| Q12 | Đề án được đính chính | mục đính chính mới nêu rõ tiền đề "thước đo chưa tồn tại" là sai và vì sao |

DoD: 12 đầu ra ở §2 tồn tại, đạt Q1–Q12, user biết chính xác phần nào đã đo được và
phần nào phải mở phiên mới mới xác nhận, và biết cách đảo ngược thay đổi cấu hình.

## 7. Câu hỏi còn mở

(rỗng)
