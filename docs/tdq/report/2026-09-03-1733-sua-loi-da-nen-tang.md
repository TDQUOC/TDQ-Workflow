# BÁO CÁO — Sửa bốn lỗi đa nền tảng P1–P4
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md
Spec: ../spec/2026-09-03-1733-sua-loi-da-nen-tang.md · Plan: ../plan/2026-09-03-1733-sua-loi-da-nen-tang.md · QC: ../qc/2026-09-03-1733-sua-loi-da-nen-tang.md

Bốn lỗi mà request 2026-09-03-1648 tìm ra và cố ý để lại đã được sửa hết. 8/8 task, 13/13 DoD,
17/17 hạng mục QC PASS. Không có máy Windows, nên mức khẳng định cao nhất ở đây là "hàm cho ra
đúng tên lệnh mong đợi khi truyền hệ điều hành Windows vào" — không phải "đã chạy trên Windows".

## P1 — Hook gọi thẳng tên lệnh `python3`

Điều quyết định cách sửa, tìm ra ở phase analyze: **`hooks/hooks.json` là file NGUỒN viết tay**,
commit sẵn và dùng chung mọi máy, trong khi hai file hook kia do `build_portable.py` sinh. Nên
P1 phải sửa bằng hai cách khác nhau.

- **Codex và agy** — thêm `tien_to_python(nen_tang)` trong `scripts/build_portable.py`: `win32`
  ra `py -3`, còn lại ra `python3`. Hai chỗ sinh `command` gọi qua hàm đó và nhận thêm tham số
  hệ điều hành. Lệnh build chạy TẠI máy đích nên bundle luôn mang đúng tên lệnh của máy đó.
- **Claude Code** — thêm lệnh `build_portable.py --sinh-hook-claude [--he-dich win32]` viết lại
  tiền tố tên lệnh trong `hooks/hooks.json`, giữ nguyên `${CLAUDE_PLUGIN_ROOT}` và thứ tự sự
  kiện. File trong repo vẫn giữ `python3` vì đó là giá trị đúng cho macOS/Linux; người dùng
  Windows chạy lệnh này một lần.

Chọn `py -3` chứ không `python`: `py` là trình khởi chạy chính thức của bản cài Python trên
Windows, còn `python` vắng mặt trên nhiều bản Linux và trên Windows có thể là stub Microsoft
Store. Lệnh sinh lại là **bất biến** — chạy lần hai in `already correct` và không đụng file, nên
không làm bẩn git của người dùng.

## P2 — Cảnh báo "bundle dựng ở máy khác" là mã chết

`kiem_layout_agy` giờ parse `hooks.json` bằng JSON, gom mọi giá trị `command` ở mọi độ sâu, và
chỉ soi dấu `~` cùng thư mục nhà trong các giá trị đó. Lỗi cũ quét văn bản thô cả file, mà phần
mô tả của chính file nhắc `~/.gemini/config/config.json` — nên vế `if` luôn đúng và nhánh cảnh
báo "máy khác" không bao giờ chạy tới.

Chạy thật trên bundle agy: dòng NOTE sai đã biến mất. Bù lại có hai ca test đối xứng — một ca
đòi cổng gác IM khi `~` chỉ nằm trong mô tả, một ca đòi nó NỔ khi `command` trỏ vào
`/Users/nguoikhac/...`. Thêm một ca nữa cho `hooks.json` hỏng cú pháp JSON: trước đây im lặng,
giờ báo rõ.

## P3 — Bundle agy nướng cứng thư mục nhà mà README không nói

Cách nướng `$HOME` giữ nguyên vì nó đúng. Thêm vào hằng `README_AGY` một mục nói ba điều: đừng
copy bundle dựng sẵn từ máy khác; tên lệnh Python khác nhau giữa Windows và nơi khác; và lệnh
kiểm lại sau khi copy. Cộng với P2 đã sửa, người ở máy khác giờ có cả cảnh báo bằng chữ lẫn cổng
gác bằng máy.

## P4 — `check`/`merge` chạy dòng `Test:` qua `shell=True`

Thêm `chuan_hoa_lenh_test` trong `scripts/tdq_team.py`: token ĐẦU TIÊN đúng là `python3` thì đổi
sang `sys.executable` (bọc nháy nếu đường dẫn có dấu cách — rất thường gặp trên Windows), mọi
dạng khác giữ nguyên. `shell=True` được GIỮ: bỏ nó sẽ làm hỏng mọi plan cũ đang dùng toán tử
shell. Thay vào đó, dòng `Test:` chứa `&&`/`||`/`|`/`>`/`<` sinh cảnh báo mà vẫn chạy, vì cú
pháp đó khác nhau giữa `cmd.exe` và `sh`.

## Kiểm chứng

- Bộ test riêng: 17 ca, 15 subtest, xanh toàn bộ.
- `pytest -q` toàn repo: 100 đỏ — đúng mốc đỏ có sẵn, không tăng; xanh tăng 1531 → 1548.
- Ba bundle dựng lại, `tdq_checkportable.py check` in CLEAN cho cả ba (93 / 143 / 86 file).
- `doc_lint.py` exit 0 trên brief, spec, plan, QC và README bundle agy.
- `hooks/hooks.json` và `hooks/scripts/*.py` không bị đụng — đúng ranh giới spec §2b.

## Một chỗ tự sửa giữa chừng

Lần đầu tôi sửa thẳng `antigravity_portable/README.md`, rồi lệnh build kế tiếp ghi đè mất — file
đó SINH RA từ hằng `README_AGY`. Đã sửa lại đúng chỗ là hằng nguồn rồi dựng lại. Ghi ra đây vì
đó là cái bẫy sẽ lặp lại với bất kỳ ai sửa README của bundle.

## Vẫn còn mở, không nằm trong request này

Ba điểm "chưa chốt được" của báo cáo 1648 giữ nguyên, vì cả ba đều cần máy thật mới trả lời:
console encoding trên Windows khi stdout là pipe (C1), đường dẫn plugin của agy (C2), hook Codex
trên Windows native (C3). Danh sách lệnh để tự kiểm nằm ở
`2026-09-03-1648-kiem-da-nen-tang-host-lenh-kiem.md`.
