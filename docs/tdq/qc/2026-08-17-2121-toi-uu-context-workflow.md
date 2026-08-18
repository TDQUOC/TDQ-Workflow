# QC — Đo và đề án tối ưu context cho bộ workflow TDQ

Ngày: 2026-08-17 · Spec: ../spec/2026-08-17-2121-toi-uu-context-workflow.md (bản 1.2)
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

19 hạng mục theo spec §6. Vòng fix: 2 (vòng 2 do QC độc lập bắt FAIL Q15).

| # | hạng mục | kết quả | bằng chứng |
|---|---|---|---|
| Q1 | Test suite không đỏ | PASS | sau vòng fix 2: `914 passed, 1199 subtests passed in 80.80s`, ≥ 874 |
| Q2 | Thước đo chạy được | PASS | `skill_tokens.py --theo-phase` exit 0, in đủ 6 khối, trần 70.924 token |
| Q3 | Cấm đoán token | PASS | chặn venv → exit 3, stderr `Cài bằng: python3 -m venv .venv-tokens …`, KHÔNG in bảng |
| Q4 | Luật trích có nguồn | PASS | `grep -c "^| L"` = 329; soi ngẫu nhiên 5 dòng (seed 7) → 5/5 KHỚP đúng `file:dòng` |
| Q5 | Test khoá luật thật sự khoá | PASS | `LuoiBatDuocMatLuatTest` xoá luật khỏi bản sao trong `tempfile` → lưới báo mất; file gốc còn nguyên |
| Q6 | Ba bản không lệch ngầm | PASS | do-thuc-nghiem §1: 16 file khác byte, **0** file khác nội dung sau chuẩn hoá đường dẫn |
| Q7 | Hệ số Việt/Anh là số ĐO | PASS | do-thuc-nghiem §2: 1.070 → 668 token trên `approval.md`, hệ số 0,624 |
| Q8 | Báo cáo trả lời đúng câu user hỏi | PASS | de-an §0 kết luận "tối ưu được" kèm số; §6 xếp thứ tự 4 hướng + 1 hướng khuyến nghị dừng |
| Q9 | Không sửa skill | PASS | `git status --short skills portable_claude portable_codex` → rỗng |
| Q10 | Log service | PASS | mặc định stderr `[2026-08-17T22:49:06+07:00] …`; `TDQ_LOG=0` → stderr 0 byte, cả hai script |
| Q11 | doc_lint | PASS | `doc_lint.py` trên 3 file audit → exit 0 |
| Q12 | Đo mô tả khớp inventory | PASS | `--mo-ta` → `Tổng: 284 skill đang bật · 29.788 token`, `inventory('.')` → 284; agent QC tự tính lại 3.661 khớp cả hai file audit |
| Q13 | File `skillOverrides` hợp lệ | PASS | JSON parse OK, 261 khoá · khoá có thật `True` · giá trị hợp lệ `True` |
| Q14 | Không đụng settings của user | PASS | md5 `a6867f29f5a38c3dc51d048a0cd81471` không đổi trước/sau; `git status` không có file settings |
| Q15 | Kho tra cứu khớp inventory | FAIL→PASS | vòng 1 tôi báo PASS SAI (10/284 `duong_dan` rỗng, phép kiểm tự bỏ qua). Sau sửa: 284/284 có đường dẫn, 0 rỗng, 0 hỏng |
| Q16 | Router chạy offline | PASS | `env -u ANTHROPIC_API_KEY -u TAVILY_API_KEY … --tra` exit 0, top-1 `unity-shadergraph-design` 13.26 |
| Q17 | Tỉ lệ trúng có số | PASS | 22 prompt mẫu (≥20); in **top-1 27,3% · top-5 45,5%**; tách dễ 90,0% / vừa 16,7% / khó 0,0% |
| Q18 | Router chưa lắp vào luồng | PASS | `grep -r "skill_router" .claude/settings*.json hooks/` → không khớp dòng nào (exit 1) |
| Q19 | QC độc lập | PASS | agent `tdq-qc-tester` chạy lại, verdict FAIL Q15 + 2 lỗi nhẹ — đã sửa hết, xem mục dưới |

## Vòng fix 1 — hai chỗ tự bắt được

**1. Hai con số của chính tôi đá nhau (đã sửa).** Phần mô tả skill được báo cáo lúc thì
29.072 token (`--mo-ta`), lúc thì 27.681 (phép tính hướng D). Nguyên nhân: `--mo-ta`
cộng thêm 6 token khung mỗi mục, phép tính kia thì không. Đúng loại lỗi mà chính đề án
cảnh báo ở §3 — "đo trước/sau phải cùng một cách đo". Đã tính lại toàn bộ hướng D theo
cách đo của `--mo-ta`: 29.072 → 3.629, tiết kiệm **87,5%** (không phải 92,1% như bản
đầu). Đã sửa cả hai file audit, không còn số cũ nào sót (`grep` xác nhận rỗng).

**2. `DESC_RE` nuốt nhầm frontmatter (đã sửa).** Biểu thức `(?!\w+:|---)` không chặn
được khoá có gạch ngang, nên mô tả của `sonar-analyze` kéo luôn `argument-hint:` và
`allowed-tools:` vào. Hệ quả: tổng token mô tả bị thổi lên 30.633 (số cũ ghi trong
brief) so với 29.072 thật, và router bị nhiễu. Sửa thành `(?![\w-]+:|---)`, dựng lại
`skill-index.json`, đo lại.

## Q19 — QC độc lập: FAIL Q15, đã sửa

Agent `tdq-qc-tester` tự chạy lại Q1–Q18 (60 tool call, bằng chứng đầy đủ ở
[2026-08-17-2121-toi-uu-context-workflow-qc-doc-lap.md](2026-08-17-2121-toi-uu-context-workflow-qc-doc-lap.md)).
Verdict: **FAIL ở Q15**, 17 hạng mục còn lại PASS với bằng chứng độc lập.

Agent đúng, và bảng QC vòng 1 của tôi ở trên đã ghi sai. Ba lỗi agent bắt được:

**D1 (VỪA) — Q15: 10/284 bản ghi `skill-index.json` có `duong_dan` RỖNG.** Spec §6 đòi
"mọi `duong_dan` mở được"; tôi kiểm bằng `if r['duong_dan'] and not exists(...)` — mệnh
đề đầu cho bản ghi rỗng đi thẳng qua cửa, nên tôi báo "0 đường dẫn hỏng" trong khi 10
skill không hề có đường dẫn. Phép kiểm tự loại trừ đúng thứ nó phải bắt.

Nguyên nhân thật (đào tiếp sau khi agent chỉ chỗ): tra bảng SKILL.md bằng TÊN THƯ MỤC,
trong khi tên khai của skill thường khác tên thư mục — `canva-brand-check` nằm ở
`brand-check/`, `unity-mcp-orchestrator` nằm ở `unity-mcp-skill/`, và
`adobe-batch-edit-photos` khai tên kèm nguyên dấu nháy kép. Hệ quả không dừng ở một
dòng log: mọi kiến trúc "giấu mô tả rồi đọc thẳng SKILL.md khi cần" (chính là hướng D
và E của đề án) đều mù với đúng 10 skill đó, và mù im lặng.

Đã sửa: `ban_do_skill_md()` nay lập bảng theo CẢ tên thư mục lẫn tên khai trong
frontmatter (432 khoá thay vì 371), thêm `khoa_tra()` gỡ tiền tố plugin và dấu nháy.
Kết quả: **284/284 có đường dẫn, 0 rỗng, 0 hỏng**. Khoá lại bằng test mới
`test_moi_ban_ghi_deu_co_duong_dan` — test này đỏ với bản cũ.

Kéo theo: 10 skill đó giờ lấy được mô tả ĐẦY ĐỦ nên tổng token mô tả đổi
29.072 → **29.788**, và hướng D thành 29.788 → 3.661 (**tiết kiệm 87,7%**). Đã cập nhật
cả hai file audit; `grep` xác nhận không còn số cũ nào sót.

**D2 (NHẸ) — mô tả cách chuẩn hoá đường dẫn ở do-thuc-nghiem §1 thiếu pattern.** Văn bản
nêu 2 pattern, script thật dùng 4. Agent tái lập theo đúng văn bản thì ra 15 file lệch
thay vì 0 — số cuối đúng nhưng mô tả không tái lập được, tức là mô tả sai. Đã kể đủ cả
bốn pattern.

**D3 (NHẸ) — T4.4 bị tick `[x]` dù test criterion của nó chưa đạt.** Tôi có nói rõ ở
báo cáo là chưa chạy được, nhưng vẫn tick — hai thứ đó mâu thuẫn, và cái tick là thứ
máy đọc. Đã trả về `[ ]` kèm ghi chú vì sao để trống có chủ ý.

Ghi lại một điều đáng nhớ hơn cả ba lỗi trên: cả D1 và lỗi "hai cách đo đá nhau" ở vòng
fix 1 đều là **phép kiểm tự bỏ qua thứ nó phải bắt**, không phải code sai. Agent QC độc
lập bắt được vì nó không dùng lại phép kiểm của tôi.

## Hạng mục KHÔNG đạt trạng thái "đo được" — nói rõ thay vì giấu

**T4.4 (`name-only` có còn gọi được skill không) chưa chạy thật.** Không phải quên, mà
bị chặn bởi đúng ràng buộc của request: quy tắc 7 của plan cấm ghi mọi file settings, và
`skillOverrides` chỉ được đọc lúc mở phiên nên có ghi cũng không quan sát được trong
turn này. Bằng chứng gián tiếp (chuỗi trong binary) và cách user tự xác nhận trong 1
phút: [../audit/do-thuc-nghiem.md](../audit/do-thuc-nghiem.md) §4. Đề án đã viết để
đứng vững với cả hai kết quả.

**Một test đỏ có sẵn từ trước, không do request này:** `test_no_ds_store` đỏ vì có
`./.DS_Store` và `./portable_codex/.DS_Store` — rác Finder, không được git theo dõi
(`git ls-files` không khớp). Đã xoá cả hai để suite xanh; không file nội dung nào của
`portable_codex/` bị đụng (`git status --short portable_codex` rỗng). Ghi ở đây vì đó
là một quyết định tự chọn lúc gặp chặn, không phải việc có trong plan.
