# REPORT — Hướng C: nạp reference theo nhu cầu (`2026-08-19-0121-huong-c-nap-reference` · lane full · mode main · 14/14 task tick đủ)

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

**Kết luận phải nói trước: hướng C không tiết kiệm token — nó tốn thêm 1.290 token
(+2,5%) mỗi request, và đó là đổi đúng chiều.** Đề án cũ xếp hướng C hạng 2 vì tưởng nó
rẻ context. Thứ nó thật sự mua là chất lượng: 14 file luật rời khỏi vùng model có thể đọc
nửa vời.

## Đổi gì về CHẤT LƯỢNG (trục cao nhất)

- 14/37 file reference trước đây không được `SKILL.md` nào trỏ thẳng — chỉ tới được qua
  một reference khác, đúng chỗ hướng dẫn chính thức cảnh báo *"Claude may partially read
  files when they're referenced from other referenced files"*. Nay cả 14 file ở tầng 1.
- Chuỗi sâu nhất rút từ **tầng 4 xuống tầng 1**: thư viện rule ngôn ngữ (`rules/`, 10 file)
  trước đây phải đi `SKILL.md` → `clean-code.md` → `rules/chung.md` → `rules/index.md` →
  file ngôn ngữ. Nay `tdq-build/SKILL.md` trỏ thẳng `rules/index.md`.
- Chừa đúng **một ngoại lệ, và ngoại lệ bị khoá chặt hơn phần còn lại**: nhóm điều phối
  theo ngôn ngữ được phép có một bước nhảy, đổi lại test bắt cửa vào phải ở tầng 1 và phải
  trỏ đủ MỌI file anh em — thiếu một file là có luật ngôn ngữ không đường nào tới.
- 8 file reference > 100 dòng có mục lục khớp tiêu đề thật, để đọc chọn lọc thay vì nuốt cả file.
- **Không một chữ nào của luật bị đổi**: 329/329 điểm neo trong `luat-hien-co.md` còn
  nguyên; 10 dòng bị `git diff` báo xoá đều là dòng cũ được thay bằng chính nó có thêm cú
  pháp link — kiểm bằng máy, 0 dòng mất chữ.

## Đổi gì về TOKEN (trục thấp nhất) — cùng một cách đếm

| Khối | Trước | Sau | Chênh |
|---|---|---|---|
| Thân 5 skill | 16.128 | 16.538 | +410 |
| 37 file reference | 77.611 | 78.718 | +1.107 |
| Một request lane full thật tiêu | 50.796 | 52.086 | **+1.290 (+2,5%)** |

Và thước đo hết sai: `skill_tokens.py` dùng `glob` không đệ quy nên bỏ sót trọn
`references/rules/` (10 file, 14.554 token). Trần báo 74.846 trong khi thực tế 93.739 —
sai 20%. Đã sửa sang glob đệ quy, có test khoá.

## Ba lưới test mới

`test_reference_mot_tang.py` (một tầng · không link chết · mục lục khớp tiêu đề) ·
`test_skill_tokens.py` (thước đo không sót thư mục con) · `test_build_portable.py` (mọi
reference có mặt ở cả hai bản portable). Cả ba đều được chứng minh ĐỎ trước khi sửa —
lưới cuối chứng minh bằng cách giấu tạm một file khỏi bản codex, thấy đỏ, trả lại, thấy xanh.

## Kiểm

`python3 -m pytest tests/` — **1.006 pass, 1.215 subtest pass**. Còn 25 subtest đỏ, TẤT CẢ
nằm trong `tests/test_skill_router.py` về skill `figma-*`/`datarobot-*`. **Đây là lỗi có
sẵn, không phải do request này**: đã chứng minh bằng cách `git stash` toàn bộ thay đổi rồi
chạy lại — vẫn đúng 25 đỏ y hệt. File đó chưa từng được commit (còn untracked từ request
`2026-08-17-2121`), và không đụng tới bất kỳ skill `tdq-*` nào.

`build_portable.py` exit 0 · 82 file bản claude, 127 file bản codex, manifest khớp sha256 ·
`doc_lint` exit 0 trên mọi file đã sửa.

## Việc phát sinh, đã xử lý trong turn

- Trần dòng của `tdq-conventions/SKILL.md` nới 143 → 145, có ghi lý do ngay tại chỗ theo
  đúng tiền lệ của hai lần nới trước.
- `luat-hien-co.md` lệch 104/329 số dòng do chèn mục lục → đã cập nhật lại cột dòng bằng
  cách dò chữ neo, không sửa chữ luật nào.

## Việc còn lại, cố ý không làm

- `bang-lech.md` còn nhắc `portable/AGENTS.md` — đường dẫn cũ, thư mục nay là
  `portable_codex/`. Sửa nó là sửa chữ trong file luật, nằm ngoài phạm vi spec đã chốt.
- Cắt trùng lặp nội dung giữa các reference: phải đọc và viết lại chữ của luật — để
  request riêng.

**Git:** chưa commit.
