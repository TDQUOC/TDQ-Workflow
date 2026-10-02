# SPEC — Nạp lười đúng đoạn: cắt token workflow nạp vào phiên

Ngày: 2026-10-02 · Bản: 1.0 · Brief: ../brief/2026-09-28-2324-toi-uu-context-workflow.md · Lane: full
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

- **Mục tiêu:** cắt lượng token workflow nạp vào phiên bằng cách nạp **đúng đoạn cần** thay vì
  trọn file, mà không hạ chất lượng. Đo được bằng hai con số: sàn tuân thủ của một request lane
  `full` giảm từ **57.712** xuống **≤ 52.500 token**, và **không file nào** trong
  `skills/**/references/` vượt **3.500 token** (hiện 3 file vượt).
- **Trong phạm vi:**
  - Cổng `PreToolUse` mới trên `Read`: **chỉ NHẮC** khi đọc trọn một file đã đọc trong phiên mà
    chưa đổi; agent tự quyết có đọc lại hay không.
  - Script sinh **chỉ mục dòng** (`§ → dòng x-y`) vào đầu mọi file luật dài, cộng test khoá cho
    chỉ mục không lệch nội dung.
  - Gỡ 4 câu "MUST open and read" ép đọc trọn file, thay bằng luật đọc-theo-đoạn.
  - Dời các mục CÓ ĐIỀU KIỆN của 3 file vượt trần sang file em; cắt mục lục song ngữ trùng.
  - Câu luật tìm kiếm: 6 bản chép nguyên văn → 1 bản + con trỏ.
  - **Tệp khoá token** `docs/tdq/token-budget.json` + một rule mới của `doc_lint` cưỡng chế trần.
  - CI **in** bảng bề mặt luôn-nạp (không làm đỏ build).
- **NGOÀI phạm vi:**
  - Hạ `muc_gat` mặc định hay bỏ bơm thân luật cho sub-agent (đề xuất Đ3 của phase analyze) —
    user chưa chọn; phải đo chuyện prune `additionalContext` trước, là request riêng.
  - Bốn phương án đã bị đo và bác ở hai request trước: tách reference sâu hơn **theo cách cũ**
    (không có chỉ mục dòng), dịch toàn bộ sang tiếng Anh, router BM25, cắt output tool.
  - Sửa `~/.claude/CLAUDE.md` của user ngoài khối `TDQ:TOOLS` đã có.
  - Cắt vào phần MANG LUẬT để đổi lấy token — `soul.md` xếp trần kích thước ở tầng 3.
  - Đổi `doc_lint` R6 (trần 500 dòng) — nó không phải thứ đang chặn, và không liên quan.

## 1b. Lộ trình

Chép từ brief mục `### Lộ trình`. User duyệt spec là duyệt luôn lộ trình này.

| Bước/phase | Chạy? | Vì sao |
|---|---|---|
| Research web | BỎ | đã tra ở analyze (cách Claude Code nạp skill/hook); phần còn lại là đo trên repo |
| Interview | BỎ | 5 câu thiết kế đã chốt |
| Vòng hỏi phạm vi | BỎ | user chốt đúng 4 trong 6 đề xuất |
| spec | CÓ | thêm hook mới, script mới, tệp khoá, và sửa hàng chục file luật |
| plan | CÓ | thứ tự bắt buộc: dời mục trước, sinh chỉ mục sau, chốt trần cuối |
| implement | CÓ | — |
| Chia cho sub-agent | BỎ | các việc dồn vào cùng vài file luật |
| qc | CÓ, mức `full` | — |
| QC độc lập (agent) | BỎ | mức `full` không gọi |
| **Đo lại tổng token trước/sau** | **CÓ — bắt buộc** | tiêu chí sống còn: không giảm thì hoàn tác |
| report | CÓ | — |

## 2. Đầu ra cụ thể

| # | Đầu ra | Đường dẫn/vị trí | Đo "xong" bằng |
|---|---|---|---|
| 1 | Cổng nhắc đọc lại | `hooks/scripts/read_gate.py` | đọc trọn một file đã đọc trong phiên, chưa đổi → in nhắc đúng MỘT lần cho file đó |
| 2 | Cổng im lặng khi đọc vùng khác | nt | gọi lại cùng file với `offset`/`limit` nhắm vùng chưa đọc → không nhắc gì |
| 3 | Cổng im lặng khi file đã đổi | nt | `mtime` hoặc kích thước đổi → không nhắc gì |
| 4 | Cổng được cắm vào Claude Code | `hooks/hooks.json` | khai `PreToolUse` matcher `Read`, và bản dựng cho host khác sinh ra cũng có nó |
| 5 | Script sinh chỉ mục dòng | `scripts/doc_index.py` | chạy hai lần cho cùng một file không sinh hai khối |
| 6 | Chỉ mục có ở mọi file luật dài | `skills/**/*.md` | mọi file ≥ 2.000 token có khối chỉ mục, mỗi mục `###`/`##` kèm khoảng dòng đúng |
| 7 | Tệp khoá token | `docs/tdq/token-budget.json` | mỗi file reference có một bản ghi `{token, sha256}`; sinh lại hai lần cho cùng cây file ra cùng nội dung |
| 8 | Trần token được cưỡng chế | `scripts/doc_lint.py` | file vượt 3.500 token → `doc_lint` báo lỗi và thoát khác 0, **không cần tokenizer** |
| 9 | Tệp khoá không được cũ | nt | sửa một file reference mà không sinh lại khoá → `doc_lint` báo "số đo đã cũ" |
| 10 | Ba file vượt trần về dưới trần | `plan-template.md`, `quick-lane.md`, `team-mode.md` | cả ba ≤ 3.500 token, và không mục luật nào bị xoá — chỉ dời sang file em |
| 11 | Bốn câu ép đọc trọn file biến mất | `skills/tdq-build/SKILL.md`, `skills/tdq-intake/SKILL.md` | không còn chuỗi "MUST open" hay "working from memory is banned" ép đọc trọn file; thay bằng luật đọc-theo-đoạn |
| 12 | Câu luật tìm kiếm còn một bản | 6 file hiện mang nó | đúng 1 bản nguyên văn + 5 con trỏ một dòng |
| 13 | Mục lục song ngữ trùng bị cắt | `plan-template.md`, `spec-template.md` | không file nào có hai mục lục cùng nội dung hai ngôn ngữ |
| 14 | Sàn tuân thủ giảm | — | đo lại tổng token các file bắt buộc đọc của lane `full`: ≤ 52.500 |
| 15 | CI in bảng bề mặt luôn-nạp | `.github/workflows/test.yml` | log của CI chứa bảng của `context_surface.py`; build KHÔNG đỏ vì bảng đó |

## 2b. Ranh giới module

| Module | Vùng file | Phụ thuộc module | Đầu ra §2 nào |
|---|---|---|---|
| M1 cổng đọc lại | `hooks/scripts/read_gate.py`, `hooks/hooks.json`, `scripts/build_portable.py` + unit test của module này | không | 1, 2, 3, 4 |
| M2 sinh chỉ mục | `scripts/doc_index.py` + unit test của module này | không | 5 |
| M3 trần token | `scripts/token_budget.py`, `docs/tdq/token-budget.json`, `scripts/doc_lint.py` + unit test của module này | M4 — khoá phải sinh SAU khi nội dung đã chốt | 7, 8, 9 |
| M4 cắt & dời nội dung | `skills/**/*.md` (toàn bộ vùng tài liệu luật) | M2 — chỉ mục sinh sau khi dời xong | 6, 10, 11, 12, 13, 14 |
| M5 bảng ở CI | `.github/workflows/test.yml` | không | 15 |

Vùng `skills/**/*.md` do **một** module duy nhất (M4) giữ, kể cả việc chèn khối chỉ mục vào các
file đó — M2 chỉ sở hữu script sinh. Hai module không khai chung một đường dẫn.

## 3. Cách tiếp cận & lý do

- **Chọn:** nạp lười bằng **chỉ mục dòng + đọc theo `offset/limit`**, cộng một cổng **chỉ nhắc**
  khi đọc lại, cộng một **tệp khoá token** để trần không trôi.
- **Vì:**
  - Số đo của phase analyze: `references/` chiếm **78%** chi phí đọc luật, còn bề mặt luôn-nạp chỉ
    **5%** — nên tối ưu hook là tối ưu nhầm chỗ.
  - 5 file nặng nhất chỉ dùng **27–77%** nội dung cho một lần dùng điển hình; phần còn lại là mục
    có điều kiện hoặc tra cứu hạ tầng.
  - 17 file **đã có mục lục** nhưng 4 câu "MUST open and read" ép đọc trọn file — cơ chế nạp lười
    đã dựng sẵn mà bị chính tài liệu vô hiệu hoá.
  - Đọc lại là khoản lãng phí lớn nhất đo được: `tdq_state.py` 12 lần, `build_portable.py` 19 lần,
    riêng hai file này **28%** toàn bộ nội dung đọc vào của một phiên thật.
  - Tệp khoá token là cách duy nhất cưỡng chế một trần token **chính xác** ở CI, nơi không có
    tokenizer: byte/token lệch 1,81 lần và token/dòng lệch 4,1 lần, nên không đại lượng thay thế
    nào đủ tin. Khoá hash là cơ chế của npm/pip, không phải phát minh mới.
- **Đã loại:**
  - **Chặn cứng** khi đọc lại — user chọn chỉ nhắc, và nó đúng với `kien-truc.md` 2026-07-29
    ("hook chỉ nhắc và kiểm bằng hiệu ứng thật"). Đổi lại: hiệu quả phụ thuộc agent có nghe.
  - **Trần byte** thay cho trần token — đo ra lệch 1,81 lần, không cưỡng chế được trần chính xác.
  - **Trần dòng** — `doc_lint` R6 đã có trần 500 dòng mà file nặng nhất chỉ 193 dòng, nên nó không
    phải thứ đang chặn; và token/dòng lệch 4,1 lần.
  - **Làm đỏ CI theo bề mặt luôn-nạp** — user chọn chỉ in.
  - **Cắt chữ trong phần mang luật** — `soul.md` xếp trần kích thước ở tầng 3; phần cắt chỉ được
    là mục lục trùng, mục có điều kiện, và câu chép lại.

## 3b. Năng lực & công cụ

| Skill | Nguồn | Phán quyết | Dùng ở đâu / Lý do loại |
|---|---|---|---|
| `code-review` | built-in | DÙNG | phase qc, phần clean code của mức `full` |
| `simplify` | built-in | DÙNG | phase qc, sau khi 5 module xong |
| Đã xét 24 skill khác | user/plugin/built-in | KHÔNG | khác lĩnh vực |

## 4. Yêu cầu bắt buộc

- Log service bật mặc định: timestamp, đủ chi tiết debug, tắt được qua config — request này có
  runtime (`read_gate.py`, `doc_index.py`, `token_budget.py`), nên dòng này áp dụng.
- Không placeholder, không TODO stub, không mock trình bày như dữ liệu thật.
- Mỗi thành phần có unit test riêng, chạy được bằng một lệnh.
- Code viết ra bám 5 nguyên tắc SOLID theo `skills/tdq-conventions/references/clean-code.md`, và
  bám rule ngôn ngữ trong `skills/tdq-build/references/rules/`.

## 5. Ràng buộc & rủi ro

Ràng buộc kiến trúc phải giữ (chép từ `docs/kien-truc.md`, chỉ dòng việc này chạm tới):

- *"`hooks/` được gọi `scripts/`; `scripts/` **không** được import `hooks/`"* — chạm ở
  `read_gate.py`: nó được phép dùng `scripts/`, và `doc_lint.py` không được import nó.
- *"File code MỚI bắt buộc nằm trong `scripts/` hoặc `hooks/`"* — chạm ở ba file mới.
- *"`skills/` chỉ được **nhắc tên lệnh** của `scripts/`, cấm chép nội dung script vào skill"* —
  chạm ở luật đọc-theo-đoạn mới trong các `SKILL.md`.
- *"hook chỉ nhắc và kiểm bằng hiệu ứng thật, không trả `deny` vì lý do 'chưa duyệt'"* (2026-07-29)
  — chạm ở `read_gate.py`, và đây chính là lý do nó CHỈ NHẮC.
- *"Chỉ `scripts/tdq_state.py` được ghi `docs/tdq/state.json`"* — `token-budget.json` là file
  riêng, không phải state.

| Rủi ro | Ảnh hưởng | Cách giảm |
|---|---|---|
| **Tách file làm TĂNG token** — kết luận cũ 2026-08-22 đã đo ra +1.290 khi tách sâu hơn | cả request thành vô nghĩa | đo lại sàn tuân thủ trước/sau ở QC; không giảm xuống ≤52.500 thì **hoàn tác phần dời**, giữ lại phần dedup + chỉ mục |
| Cổng chỉ nhắc nên có thể bị bỏ qua | tiết kiệm thật thấp hơn con số đo được | nhắc mang số liệu cụ thể ("file này bạn đã đọc ở lượt N, 27k token"); đo lại số lần đọc lại ở request sau |
| Chỉ mục dòng lệch sau mỗi lần sửa file | agent đọc sai đoạn, tệ hơn không có chỉ mục | test khoá so chỉ mục với nội dung thật; sinh lại là một bước của `tdq_finish` |
| Tệp khoá token thành cửa ải phiền | mỗi lần sửa docs phải chạy thêm một lệnh | `tdq_finish` tự sinh lại khoá khi có file `.md` đổi; `doc_lint` chỉ báo khi khoá cũ |
| Dời mục làm mất luật | mất hàng rào chất lượng | QC đếm số mục trước/sau: tổng số mục `##`/`###` của vùng tài liệu không được giảm |
| Hook mới làm chậm mỗi lần `Read` | chậm mọi tool-call | cổng chỉ đọc sổ lượt (đã có sẵn, dùng `_common.turn_rows`) và `os.stat`; không spawn tiến trình, không đọc nội dung file |

## 6. QC & Definition of Done

| # | Hạng mục kiểm | Điều kiện PASS |
|---|---|---|
| Q1 | Cổng nhắc khi đọc lại | đọc trọn một file đã đọc trong phiên và chưa đổi → nhắc đúng một lần |
| Q2 | Cổng im lặng khi đọc vùng khác | cùng file, `offset/limit` nhắm vùng chưa đọc → không nhắc |
| Q3 | Cổng im lặng khi file đã đổi | `mtime` hoặc kích thước đổi → không nhắc |
| Q4 | Cổng không làm chậm | không spawn tiến trình con, không đọc nội dung file được hỏi |
| Q5 | Cổng được cắm đủ mọi host | `hooks.json` khai `PreToolUse` trên `Read`, và bản dựng cho host khác cũng có |
| Q6 | Sinh chỉ mục idempotent | chạy hai lần không sinh hai khối, không đổi nội dung khác |
| Q7 | Chỉ mục đúng khoảng dòng | mỗi mục trong chỉ mục trỏ đúng dòng mở đầu của mục đó trong file |
| Q8 | Chỉ mục có mặt đủ | mọi file luật ≥ 2.000 token đều có khối chỉ mục |
| Q9 | Tệp khoá sinh lại được | sinh hai lần trên cùng cây file ra nội dung giống nhau |
| Q10 | Trần token cưỡng chế được | file vượt 3.500 token → `doc_lint` thoát khác 0, và chạy được khi KHÔNG có tokenizer |
| Q11 | Khoá cũ bị bắt | sửa một file reference mà chưa sinh lại khoá → `doc_lint` báo số đo đã cũ |
| Q12 | Ba file về dưới trần | cả ba ≤ 3.500 token |
| Q13 | Không mục luật nào bị mất | tổng số mục `##` + `###` của vùng tài liệu sau ≥ trước |
| Q14 | Bốn câu ép đọc trọn file đã gỡ | không còn câu nào buộc đọc trọn một file reference |
| Q15 | Câu luật tìm kiếm một bản | đúng một bản nguyên văn, năm chỗ còn lại là con trỏ một dòng |
| Q16 | Mục lục trùng đã cắt | không file nào mang hai mục lục cùng nội dung hai ngôn ngữ |
| Q17 | **Sàn tuân thủ giảm** | tổng token các file bắt buộc đọc của lane `full` ≤ **52.500** (trước: 57.712) |
| Q18 | CI in bảng | log CI có bảng bề mặt luôn-nạp, và build không đỏ vì nó |
| Q19 | Ràng buộc kiến trúc | `scripts/` không import `hooks/`; file code mới nằm đúng thư mục; hook chỉ nhắc, không `deny` |
| Q20 | Ba hệ | trọn bộ test xanh trên Windows, Linux thật và macOS thật |

DoD: 15 đầu ra ở §2 có thật và đo được · 20 hạng mục Q1–Q20 PASS · trọn bộ test xanh trên 3 hệ ·
`doc_lint` và phép kiểm i18n xanh · sàn tuân thủ ≤ 52.500 token · tổng số mục luật không giảm ·
working log của mọi turn đã ghi · CHANGELOG có mục cho bản này.

## 7. Câu hỏi còn mở

Không còn câu nào — 5 câu thiết kế đã chốt ở cuối phase analyze, ghi trong brief mục `## Hỏi đáp`.
