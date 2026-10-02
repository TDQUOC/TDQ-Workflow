# BRIEF — Tối ưu lượng context TDQ-Workflow nạp vào phiên

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

Ngày: 2026-09-28 · Slug: 2026-09-28-2324-toi-uu-context-workflow

## Nguyên văn

> và bây giờ tôi muốn bạn làm một deep analysis để lên phương án tối ưu tdq-workflow và đưa cho
> tôi giải pháp cho vấn đề hiện tại tôi có cảm giác vẫn đang nạp quá nhiều context vào session mà
> tdq-workflow chạy, tôi muốn phương án như optimize làm ngắn text hoặc lazy load đúng đoan để nạp
> ít text vào nhưng hiệu quả vẫn cao, nhằm tiết kiệm token và thời gian xử lí hạn chế nạp quá
> nhiều đoạn ko có giá trị hoặc chưa cần dùng hãy chia nhiều agent ra phân tích và nghiên cứu và
> cho tôi đề xuất

**Cách tôi đọc yêu cầu này**

- **Mục tiêu:** cắt lượng token workflow nạp vào phiên, mà KHÔNG hạ chất lượng đầu ra. Soul xếp
  `chất lượng > runtime > context cost`, nên mọi đề xuất phải chứng minh nó không đổi chất lượng
  lấy token — thứ tự đó là luật gốc, không thương lượng.
- **Hai hướng user chỉ đích danh:** (a) làm ngắn text; (b) **nạp lười đúng đoạn** — nạp mục cần
  thay vì cả file.
- **Đầu ra của request này là ĐỀ XUẤT**, không phải bản sửa. User muốn "cho tôi đề xuất".
- **Cách làm user chỉ định:** chia nhiều agent phân tích song song.

**Ranh giới tôi tự đặt ra, chờ user bác nếu sai:** "cảm giác nạp quá nhiều" phải được đổi thành
SỐ ĐO trước khi đề xuất bất cứ thứ gì. Repo đã có tokenizer thật (`.venv-tokens/`) và ba công cụ
đo — `skill_tokens.py`, `doc_dup.py`, `context_surface.py` — nên không có lý do gì để đoán.

## Hiểu & kiến thức

### Năm hướng đo đang chạy song song

| # | Agent đo gì | Trả lời câu hỏi nào |
|---|---|---|
| 1 | Bề mặt LUÔN-NẠP: description skill, đầu ra thật của từng hook, `~/.claude/CLAUDE.md`, thân luật `[TDQ:GON]` theo từng `muc_gat` | Mỗi phiên và mỗi lượt tốn bao nhiêu token TRƯỚC khi làm việc gì |
| 2 | Chi phí THEO PHASE: `skill_tokens.py --theo-phase`, mọi câu "MUST read", token từng file `references/` | Một request lane `full` phải nạp bao nhiêu nếu tuân thủ đúng luật |
| 3 | TRÙNG LẶP: `doc_dup.py` trên `skills/`, `agents/`, bản mẫu | Bao nhiêu token bị trả hai lần cho cùng một câu |
| 4 | CƠ CHẾ nạp lười đang có và bị vô hiệu ở đâu, cộng các quyết định tối ưu ĐÃ chốt trước đây | Đề xuất nào là mới, đề xuất nào đã bị bác rồi |
| 5 | Phiên THẬT: đếm trong transcript xem file nào bị đọc mấy lần, quy ra token, so với tổng input token | Lý thuyết có khớp thực tế không |

### Vì sao phải đo trước khi đề xuất

Đây là request thứ ba trong hai tháng động vào cùng chủ đề (`2026-08-09-cat-token-thua-workflow`,
`2026-08-22-toi-uu-workflow`). Không đọc kết quả hai lần trước là chắc chắn đề xuất lại thứ đã bị
bác, hoặc cắt lại thứ đã cắt. Agent 4 có nhiệm vụ đó.

Và một cái bẫy đã gặp thật trong repo này: trần kích thước là ràng buộc **tầng 3** theo `soul.md`,
nên chạm trần thì NÂNG TRẦN chứ không nén luật (tiền lệ ở `tests/test_claude_md_core.py`, áp hai
lần: `chung.md` 150→240 dòng, bản mẫu 3800→4300 byte). Nghĩa là "làm ngắn text" KHÔNG được phép
trở thành "cắt luật cho vừa ngân sách". Phần cắt được phải là phần **lặp lại, chưa cần, hoặc
không ai đọc** — không phải phần mang luật.

### Số đo 1 — bề mặt LUÔN-NẠP (tokenizer thật)

| Nguồn | Token | Nạp khi nào |
|---|---|---|
| `session_start.py` | **2.024** | mỗi phiên — 1.807 trong đó (89%) là thân luật `[TDQ:GON]` |
| `subagent_start.py` | **1.842** | **mỗi sub-agent** — chép lại đúng thân luật đó |
| Description toàn bộ skill | 532 | mỗi lời gọi API (nằm trong system prompt) |
| `~/.claude/CLAUDE.md` | 328 | mỗi phiên |
| `prompt_context.py` + các gate | 78 → ≤163 | mỗi lượt — đã bị trần cứng chặn |

Tổng luôn-nạp: **2.884 token/phiên**, **1.842/sub-agent**.

### Số đo 2 — chi phí ĐỌC LUẬT của một request lane `full`

| Phase | Token phải nạp nếu tuân thủ đúng mọi câu "MUST read" |
|---|---|
| intake/analyze | 18.728 |
| spec | 6.167 |
| plan | 16.487 |
| implement | 8.179 |
| qc | 2.877 |
| report | 1.860 |
| luôn nạp (`tdq-conventions`) | 3.414 |
| **Tổng** | **57.712** |

Thân skill chỉ 16.2k; **38 file `references/` chiếm 65k — tức 78% chi phí**. Bề mặt luôn-nạp
(2.884) chỉ bằng **5%** của con số này: tối ưu hook là tối ưu nhầm chỗ.

Tỉ lệ "thực sự cần / tổng" của 5 file nặng nhất, đo theo một lần dùng điển hình:

| File | Token | Cần | Phần thừa là gì |
|---|---|---|---|
| `plan-template.md` | 5.067 | **38%** | cụm song song, luật file nóng, khuôn hợp đồng skill — đều CÓ ĐIỀU KIỆN mà nạp vô điều kiện |
| `quick-lane.md` | 4.356 | 47% | luật tick, 3 mục QC, vòng fix — cần ở bước sau, không phải bước 1 |
| `team-mode.md` | 3.652 | 50% | ví dụ ĐÚNG/SAI, sổ worktree — tra cứu |
| `uu-tien-tim-kiem.md` | 3.449 | **27%** | vòng đời Ollama, bảng phụ thuộc, luật hook — hạ tầng, không cần lúc đang tìm |
| `spec-template.md` | 3.394 | 77% | mục lục song ngữ |

### Số đo 3 — trùng lặp (`doc_dup.py`)

Cắt được **~1.400–1.500 token**, trong đó **1.125 là câu luật tìm kiếm bị chép nguyên văn ở 6
file**. Khối trùng chủ yếu dài 3–5 dòng; chỉ 1 khối dài hơn 6 dòng.

### Số đo 4 — phiên THẬT (transcript 22,76 MB, 10.495 dòng, 1.554 tool-call)

| Chỉ số | Giá trị |
|---|---|
| Lượt đọc file | 367 lượt / **191 file duy nhất** |
| Token nội dung đọc vào | **1.769.960** |
| `cache_read_input_tokens` | 1.476.638.858 — **98,2% tổng input** |
| `cache_creation_input_tokens` | 27.419.319 |
| `input_tokens` (chưa cache) | 6.348 |
| `output_tokens` | 3.220.649 |

Top file tốn nhất **đều vì ĐỌC LẠI**, không vì file to:

| File | Lần đọc | Token/lần | Tổng |
|---|---|---|---|
| `scripts/tdq_state.py` | **12** | 26.961 | 323.532 |
| `scripts/build_portable.py` | **19** | 9.436 | 179.284 |
| `scripts/tdq_codex.py` | 7 | 11.900 | 83.300 |
| `CHANGELOG.md` | 4 | 17.537 | 70.148 |
| `tests/test_check_status.py` | 6 | 10.366 | 62.196 |

### Chẩn đoán — ba điều số đo nói, mà cảm giác không nói

1. **Chi phí thật không phải "file to bao nhiêu", mà là "nội dung ở lại trong context bao lâu".**
   98,2% input của phiên là đọc lại context đã có. Mỗi token nạp vào sớm sẽ bị nhân với số lời
   gọi API còn lại của phiên. Nên một file 5.000 token nạp ở đầu phase `plan` đắt hơn nhiều lần
   con số 5.000.
2. **Đọc lại cùng một file là khoản lãng phí lớn nhất đo được.** `tdq_state.py` bị đọc 12 lần,
   `build_portable.py` 19 lần — riêng hai file này 502.816 token, bằng 28% toàn bộ nội dung đọc
   vào của phiên. Repo ĐÃ CÓ luật chống việc này (`context-budget.md`, 5 ca re-read) nhưng nó nằm
   trong một file reference, tức muốn biết luật thì phải nạp thêm — và không cổng nào cưỡng chế.
3. **Cơ chế nạp lười đã dựng sẵn nhưng bị chính tài liệu vô hiệu hoá.** 17 file có mục lục, nhưng
   4 câu "MUST open and read" (`tdq-build/SKILL.md:88,100,157`, `tdq-intake/SKILL.md:129`) cộng 7
   lần "working from memory is banned" ép đọc trọn file. Mục lục có mà không ai được phép dùng.

### Những phương án ĐÃ bị đo và bác — không đề xuất lại

| Phương án | Kết luận cũ |
|---|---|
| Tách `references/` sâu hơn | **Ngược kỳ vọng**: phải làm NÔNG đi (14 file kéo lên tầng 1), và việc đó TỐN thêm 1.290 token |
| Dịch toàn bộ sang tiếng Anh | KHÔNG — rủi ro lệch ngôn ngữ nằm ở trục chất lượng, trục cao hơn token |
| Router BM25 chọn skill | KHÔNG — top-5 chỉ đúng 45,5%, dưới ngưỡng 90% |
| Cắt output tool / `BASH_MAX_OUTPUT_LENGTH` | Bị loại có bằng chứng; MCP chỉ chiếm 1,9% |
| `skillOverrides` name-only | ĐÃ ÁP — cắt 12.446 token (41,8%) |

## Hỏi đáp

**Năm câu chốt ở cuối phase analyze** (nguyên văn user: `1b và cho agent tự quyết định có nên đọc
lại ko 2a 3b 4b 5a`).

| # | Câu hỏi | Chốt | Hệ quả |
|---|---|---|---|
| 1 | Cổng chống đọc lại: nhắc hay chặn | **Chỉ NHẮC**, agent tự quyết có đọc lại hay không | Giữ đúng tinh thần `kien-truc.md` 2026-07-29: hook nhắc, không chặn. Đổi lại: hiệu quả phụ thuộc agent có nghe hay không — phải đo sau |
| 2 | Chỉ mục dòng | **Sinh tự động** bằng script + test khoá | Chỉ mục không bao giờ lệch với nội dung |
| 3 | Trần token cho references | **3.500/file NGAY** | Buộc cắt 3 file trong request này: `plan-template` 5.067, `quick-lane` 4.356, `team-mode` 3.652 |
| 4 | Cổng CI | **Chỉ in**, không làm đỏ | Bề mặt luôn-nạp được theo dõi nhưng không bị cưỡng chế |
| 5 | Mức QC | **`full`** | Đã ghi `muc_qc=full` vào state |

### Hai vướng kỹ thuật của câu 3, và cách giải

**(a) CI không có tokenizer.** `doc_lint` chạy ở CI, nơi repo cố ý không cài công cụ ngoài; mà
`skill_tokens.py` thoát 3 khi thiếu `anthropic-tokenizer`. Đo thử đại lượng thay thế trên cả 43
file reference:

| Đại lượng | Khoảng dao động | Kết luận |
|---|---|---|
| token/dòng | 11,6 → 47,2 | lệch **4,1 lần** — đếm dòng vô dụng để đoán token |
| byte/token | 2,20 → 3,98 | lệch **1,81 lần** — tốt hơn 2,3 lần nhưng vẫn không cưỡng chế được một trần chính xác |

Nên dùng **tệp khoá token**: một script có tokenizer ghi `token-budget.json` gồm `{đường dẫn:
{token, sha256}}`. CI chỉ việc so `sha256` của file với bản ghi — khớp thì con số token còn đúng và
đem so với trần được, không khớp thì báo "số đo đã cũ, chạy lại script". Cưỡng chế CHÍNH XÁC mà
không cần tokenizer ở CI. Cùng cơ chế lockfile của npm/pip.

**(b) Cắt 3 file xuống 3.500 mà không được nén luật.** `soul.md` xếp trần kích thước ở tầng 3, nên
không được cắt luật cho vừa ngân sách. Phần cắt được, theo số đo của phase này:

| File | Hiện | Cắt gì | Còn |
|---|---|---|---|
| `plan-template` | 5.067 | mục lục song ngữ trùng 519 + dời 2 mục CÓ ĐIỀU KIỆN (cụm song song 755, luật file nóng 554) sang file em | ~3.240 |
| `quick-lane` | 4.356 | 3 mục QC + vòng fix (548+190) chỉ cần ở bước sau, dời sang file em | ~3.600 → cắt thêm mục lục trùng |
| `team-mode` | 3.652 | ví dụ ĐÚNG/SAI 390 + sổ worktree 575 là tra cứu, dời sang file em | ~2.690 |

**Và đây là chỗ nghịch với kết luận cũ, nên phải nói rõ.** Request `2026-08-22` đã đo và BÁC việc
tách reference sâu hơn: nó tốn thêm 1.290 token. Nhưng phép đo đó chạy khi KHÔNG có chỉ mục dòng
và KHÔNG có luật đọc-theo-đoạn — chi phí điều hướng lúc đó là "mở thêm một file và đọc trọn".
Với Đ2 trong tay, chi phí điều hướng là "đọc 20 dòng chỉ mục rồi lấy đúng một mục". Nên tôi làm
lại việc đã bị bác, có lý do, và lý do đó phải được kiểm bằng số đo trước/sau ở phase QC — nếu
tổng token của một request lane `full` không giảm, kết luận cũ thắng và phải hoàn tác.

### Lộ trình

| Bước/phase | CÓ-BỎ | Vì sao |
|---|---|---|
| analyze | **CÓ** (đã chạy) | 5 agent đo song song: bề mặt luôn-nạp, chi phí theo phase, trùng lặp, cơ chế nạp lười, phiên thật |
| research web | **BỎ** | agent 4 đã tra cách Claude Code nạp skill/hook; phần còn lại là đo trên chính repo |
| vòng hỏi phạm vi | **BỎ** | user đã chốt đúng 4 đề xuất trong 6, và 5 câu thiết kế |
| spec | **CÓ** | thêm một hook mới, một script mới, một tệp khoá, và sửa hàng chục file luật |
| plan | **CÓ** | thứ tự bắt buộc: sinh chỉ mục trước, rồi mới dời mục, rồi mới chốt trần |
| implement | **CÓ** | — |
| chia cho sub-agent | **BỎ** | các việc dồn vào cùng vài file luật; chia ra là tự tạo xung đột |
| qc | **CÓ**, mức `full` | có phép đo trước/sau quyết định giữ hay hoàn tác |
| QC độc lập (agent) | **BỎ** | mức `full` không gọi |
| **đo lại tổng token trước/sau** | **CÓ — bắt buộc** | đây là tiêu chí sống còn của request: không giảm thì hoàn tác |
| report | **CÓ** | — |

Bốn luồng tính năng: (1) cổng nhắc đọc lại; (2) chỉ mục dòng sinh tự động + luật đọc-theo-đoạn;
(3) tệp khoá token + trần 3.500; (4) bảng bề mặt luôn-nạp in ra ở CI.


