# QC — Trang trí khối chat cuối trả lời user

Spec: ../spec/2026-08-14-trang-tri-khoi-chat.md (bản 1.0) · Plan: ../plan/2026-08-14-trang-tri-khoi-chat.md

## Quét ký tự trước khi siết

Lệnh: `python3 scripts/scan_block_symbols.py --lieu-ke` (toàn file) và
`python3 scripts/scan_block_symbols.py --chi-khoi --lieu-ke` (chỉ nội dung khối ```).

**Toàn file — 11 ký hiệu, 8 ký tự ngoài whitelist ban đầu:**

| Ký tự | Codepoint | Tên | Số lần | Trong khối mẫu? |
|---|---|---|---|---|
| `—` | U+2014 | EM DASH | 108 | có (24) |
| `→` | U+2192 | RIGHTWARDS ARROW | 78 | có (8) |
| `·` | U+00B7 | MIDDLE DOT | 64 | có (26) |
| `–` | U+2013 | EN DASH | 17 | có (7) |
| `➤` | U+27A4 | BLACK RIGHTWARDS ARROWHEAD | 17 | có (11) |
| `§` | U+00A7 | SECTION SIGN | 12 | không |
| `≤` | U+2264 | LESS-THAN OR EQUAL TO | 9 | không |
| `…` | U+2026 | HORIZONTAL ELLIPSIS | 7 | có (3) |
| `≥` | U+2265 | GREATER-THAN OR EQUAL TO | 4 | không |
| `⏳` | U+23F3 | HOURGLASS WITH FLOWING SAND | 1 | không (nhưng VẪN in ra user) |
| `✔` | U+2714 | HEAVY CHECK MARK | 1 | không (nhưng VẪN in ra user) |

### Quyết định (T0.2)

**Quyết định nền — phạm vi của whitelist là nội dung các khối ```, không phải cả file.**
Lý do: văn xuôi hướng dẫn quanh khối không bao giờ tới mắt user, siết cả file sẽ buộc thay
`→ § ≤ ≥` trong hàng trăm chỗ tài liệu — mà thay ký tự trong câu là **sửa chữ**, đúng thứ
đáp án 3A của user cấm. Đây là chỗ lệch so với chữ nghĩa của spec §6 Q5 ("trong 12 file"),
ghi ra đây thay vì nới âm thầm; hiệu lực thật không giảm vì có thêm quyết định 4 bên dưới.

| # | Ký tự | Quyết định | Căn cứ |
|---|---|---|---|
| 1 | `→` U+2192 | **VÀO whitelist** | nguồn: đang chạy thật — 8 lần trong khối mẫu của `report-template.md`, `quick-lane.md`, `portable/workflow/02-spec.md`; in ra cho user hằng ngày, chưa từng có báo lỗi hiển thị. Đúng chuẩn bằng chứng của luật 2A |
| 2 | `–` U+2013 | **VÀO whitelist** | nguồn: 7 lần trong khối mẫu của 7 file, gồm chính khuôn gốc; cùng lớp bằng chứng với `—` |
| 3 | `…` U+2026 | **VÀO whitelist** | nguồn: 3 lần trong khối mẫu `report-template.md`; cùng lớp bằng chứng |
| 4 | `⏳` U+23F3 và `✔` U+2714 | **LOẠI — phải thay** | `skills/tdq-status/SKILL.md:26` dạy Claude in `✔ đã duyệt / ⏳ chờ duyệt` cho user. `⏳` là emoji thật (khối Miscellaneous Technical, hiển thị dạng emoji trên đa số nền), vi phạm luật "Không emoji" của khuôn. Test emoji hiện tại KHÔNG bắt được vì dải `[\U0001F300-\U0001FAFF☀-⛿✅❌⚠]` không phủ U+23F3 và U+2714, lại chỉ quét mỗi file khuôn |
| 5 | `▸` U+25B8 | **LOẠI** | `grep -c '▸' -r skills/ scripts/ hooks/ portable/` → 0 kết quả. Ký tự mới, không có bằng chứng render (luật 2A) |
| 6 | `§ ≤ ≥` | **ngoài phạm vi** | chỉ nằm trong văn xuôi tài liệu, không in ra user |

**Whitelist chốt (áp cho nội dung khối ``` trong 12 file): `➤` `·` `—` `→` `–` `…` — đúng 6
ký tự, tất cả đều có bằng chứng đang chạy thật.**

**Quyết định 4 sinh thêm việc, không nằm trong plan gốc:** phải mở rộng phép cấm emoji ra
cả 12 file (không chỉ file khuôn) và vá dải regex để bắt `⏳` `✔`. Đây là lỗi thật do chính
request này lộ ra, nằm đúng trong mặt C (chống trôi khuôn) user đã chọn, nên xử lý ngay
thay vì để lại — thêm task QC0.1 vào plan.

### Ghi chú về hợp đồng skill của T0.2

Plan giao T0.2 hai skill: `tavily-search (mcp)` để tra nguồn render cho ký tự lạ, và
`claude-code-guide` để đối chiếu. **Không gọi cả hai** — vì luật 2A user chốt là "chỉ dùng
thứ đã có bằng chứng chạy thật trong repo", mà cả 3 ký tự lạ (`→ – …`) đều đã có bằng chứng
đó bằng lệnh grep ở bảng trên, nên câu hỏi mà research định trả lời đã tự tắt. Gọi tavily
lúc này là tra một thứ đã biết đáp án. Ghi ra đây để người đọc plan không tưởng là bỏ sót.

## Kết quả QC — 10 hạng mục DoD

| # | Hạng mục | Kết quả | Bằng chứng |
|---|---|---|---|
| Q1 | Bảng cấu trúc đủ 5 thành phần | PASS | `grep -A9 'Thành phần' <khuôn> \| grep -c '^| '` → `6` (1 tiêu đề + 1 kẻ + 5 dòng, đếm gộp = 6 ≥ 6) |
| Q2 | Đủ 7 luật đánh số | PASS | Lệnh thô `grep -cE '^[1-7]\. '` → `12` vì nó đếm gộp cả 5 dòng mục "Năm thành phần". Phép đếm đúng phạm vi nằm ở `test_rules_table_and_seven_rules`: cắt theo mục `## Bảy luật trang trí` rồi so `['1'..'7']` — xanh |
| Q3 | Có khối mẫu trước/sau | PASS | `grep -c '### Trước\|### Sau' <khuôn>` → `2` |
| Q4 | Không cấu trúc rủi ro trong khối mẫu | PASS | Lệnh thô quét cả file ra 12 dòng, **không dòng nào nằm trong khối mẫu**: 10 dòng là tiêu đề `#`/`##` của chính tài liệu, 1 dòng là câu liệt kê ký tự kẻ khung bị cấm. Phép kiểm đúng phạm vi (`CAM` áp lên nội dung khối) nằm trong `test_sample_blocks_follow_rules` — xanh trên 9 khối của 11 file |
| Q5 | Whitelist ký hiệu | PASS | `python3 -m pytest tests/test_user_facing_block.py -q` → `10 passed, 58 subtests passed`; có `test_symbol_whitelist`, và chèn thử `▸` vào khuôn thì test ĐỎ đúng chỗ (`{'▸': {...: 1}}`) rồi hoàn tác |
| Q6 | Chuỗi máy bắt còn nguyên | PASS | `grep -c '· Góp ý: nhắn trực tiếp' hooks/scripts/_common.py` → `2`; `grep -c 'plan đề xuất {mode}'` → `2` (1 dòng chuỗi thật + 1 dòng chú thích). `test_code_generated_blocks_conform` so nguyên văn `➤ Duyệt: nhắn "duyệt spec" · Góp ý: nhắn trực tiếp` |
| Q7 | Test cũ không đỏ, số test không giảm | PASS | `python3 -m pytest tests/ -q` → `574 passed, 280 subtests passed`, 0 failed (mốc cũ 569) |
| Q8 | File nói với user đều trỏ về khuôn | PASS sau vòng 1 | Lượt đầu FAIL 8/11 → thêm dòng trỏ ở `skills/tdq-status/SKILL.md` và `portable/workflow/02-spec.md` (QC1.1). Nay 10/11; file thứ 11 là chính khuôn gốc, không tự trỏ về mình |
| Q9 | Portable khớp khuôn gốc | PASS | `pytest -k portable` xanh; bản portable được sinh từ khuôn gốc bằng đúng 4 phép thay chữ cố ý (xem mục dưới) |
| Q10 | 0 từ nội dung bị mất | PASS | Diff từng từ trên 10 file `.md` đã sửa → `0` với mọi file, trừ `skills/tdq-status/SKILL.md` mất đúng 2 "từ" là `✔` và `⏳` — đây là việc QC0.1 cố ý làm, không phải mất chữ |

Full suite chạy đúng một lần ở cuối implement và một lần ở QC: `574 passed`, 0 failed.

### Bốn chỗ bản portable cố ý khác khuôn gốc

`workflow` thay cho `TDQ` ở câu mở · `cổng chọn cách chạy (mode)` thay cho `cổng chọn mode` ·
bỏ tham chiếu `[SKILL.md](../SKILL.md)` ở luật in lại nguyên văn · câu cuối mục ký hiệu
nói "kho gốc kiểm hộ bằng một test whitelist" thay vì trỏ tên script chỉ có trong kho này.

### Ghi chú T3.2 — 5 chỗ mã sinh chuỗi

Không chỗ nào phải sửa. `hooks/scripts/_common.py:176-183` (`approve_hint`) đã đúng luật 7
và chỉ dùng ký tự whitelist; `scripts/tdq_state.py:586` và `:689-690` là chuỗi hướng dẫn
Claude in dòng `➤`, đúng khuôn sẵn; `hooks/scripts/stop_gate.py:153` chỉ nhắc in lại
nguyên văn dòng `➤ Duyệt`. Ba chuỗi máy đang bắt giữ nguyên từng byte.

### Ba thứ cố ý KHÔNG đụng

1. `✓` (U+2713) trong `tdq-conventions/SKILL.md` và `reminder-codes.md`: là giao ước
   `✓ [TDQ:<MÃ>]` của workflow, không phải emoji, và hai file đó ngoài 12 file phạm vi.
2. Bốn vi phạm `doc_lint` ở `portable/AGENTS.md`, `portable/workflow/02-spec.md`,
   `portable/workflow/references/quick-lane.md`: có sẵn từ trước request này — kiểm bằng
   cách lint lại đúng bản `HEAD` của ba file, ra y hệt 4 dòng đó.
3. `§ ≤ ≥` trong văn xuôi tài liệu: ngoài phạm vi whitelist theo quyết định nền của T0.2.

### Một cái bẫy gặp thật, ghi lại để lần sau tránh

Hai lần suýt mất việc vì `git checkout <file>`: lần một dùng để hoàn tác một phép thử,
nó xoá luôn phần T1.2 vừa viết trong cùng file (khôi phục được nhờ dựng ngược từ bản
portable). Và `__pycache__` giữ bản `.pyc` cũ khi file mới có cùng kích thước và mtime
sát nhau, làm test đọc nhầm mã cũ — phải xoá `__pycache__` mới thấy kết quả thật.

## Vòng QC độc lập — agent `tdq-qc-tester`

Agent chạy lại cả 10 hạng mục DoD cộng 4 điểm rủi ro. Phán quyết: PASS cả 10 hạng mục.
Nó nêu 7 phát hiện. Xử lý từng cái:

| # | Phát hiện | Xử lý |
|---|---|---|
| 1 | `lane-decision.md` dòng 56-57 vỡ markdown: `**_chế độ nhanh (express):**` sinh ra chữ `_` trần và mất phần in nghiêng | SỬA — QC2.1. Đoạn đó là câu giải thích in nghiêng nguyên khối, không phải nhãn trường, nên trả về dạng cũ |
| 2 | Test xanh giả: chèn `**Mục tiêu**: ` (dấu hai chấm ngoài cặp sao) mà suite vẫn xanh | SỬA — QC2.2. Thêm `NHAN_SAI`, đã chứng minh đỏ bằng phép chèn thật rồi hoàn tác |
| 3 | `test_sample_blocks_follow_rules` chạy rỗng với `interview.md` và `tdq-status/SKILL.md` | SỬA — QC2.3. Hai file đó thật sự có 0 khối ```; nay số khối từng file bị chốt trong `SO_KHOI` nên xoá khối là đỏ |
| 4 | Số liệu Q4 và Q10 trong file này ghi thiếu | SỬA — xem hai dòng đính chính ngay dưới bảng |
| 5 | Q8 buộc thêm câu trỏ khuôn, nghịch với luật 3A "chỉ đổi trang trí" | KHÔNG SỬA — ghi rõ: luật 3A bảo vệ chữ trong khối mẫu in cho user. Câu thêm nằm ở văn xuôi hướng dẫn, ngoài khối, và Q8 đòi phải có |
| 6 | `scan_block_symbols.py` không có log timestamp; số liệu T0.1 trong plan đã cũ | KHÔNG SỬA phần log — script là công cụ chạy một phát, in bảng ra stdout, không có runtime để bật log service (spec §4 miễn trừ). Số liệu T0.1: đã ghi thêm một câu trong plan nói rõ đó là số đo tại thời điểm đó |
| 7 | Thiếu file report | ĐÃ LÀM — `docs/tdq/reports/2026-08-14-trang-tri-khoi-chat.md`, viết ở bước report ngay sau QC |

Đính chính Q4: lệnh thô quét cả 9 file skill ra 50 dòng, không phải 12. Toàn bộ 50 dòng
là tiêu đề `#` của chính tài liệu, nằm ngoài khối mẫu. Quét trong khối ra 0.

Đính chính Q10: đo lại sau QC vòng 2 trên 10 file `.md` đã sửa, kết quả 0 từ bị mất ở
9 file. File còn lại là `skills/tdq-status/SKILL.md` mất đúng 2 ký tự `✔` và `⏳`, đúng
việc QC0.1 cố ý làm.

Sau QC vòng 2: `python3 -m pytest tests/ -q` → `574 passed, 280 subtests passed`, 0 failed.

