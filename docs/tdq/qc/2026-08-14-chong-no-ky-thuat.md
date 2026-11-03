# QC — Đề xuất cơ chế chống quick-fix phá kiến trúc

Ngày: 2026-08-14 · Plan: ../plan/2026-08-14-chong-no-ky-thuat.md · Vòng 1 · 11/11 PASS

`F=docs/tdq/knowledge/2026-08-14-chong-no-ky-thuat.md`

| # | Hạng mục | Lệnh | Kết quả thật | Kết luận |
|---|---|---|---|---|
| Q1 | File đề xuất đủ 6 mục | `grep -c "^## " $F` | `6` | PASS |
| Q2 | Bảng khoảng trống 4 dòng có số đo | `grep -c "^| K[1-4] " $F` | `4` | PASS |
| Q3 | Mỗi khối cơ chế đủ 5 trường | 5 lệnh `grep -c` (`^### M`, `^- Chặn:`, `^- Chèn vào:`, `^- Nội dung nháp:`, `^- Cách kiểm:`) | `6 6 6 6 6` — bằng nhau và ≥ 6 | PASS |
| Q4 | Mọi đường dẫn trong `Chèn vào` có thật | trích 5 đường dẫn rồi `test -f` từng cái | 5/5 tồn tại, 0 dòng `MISS` | PASS |
| Q5 | Không cơ chế nào vượt trần B | `grep -c "^- Mức: C" $F` | `0` | PASS |
| Q6 | Có đúng 3 gói | `grep -c "^### Gói" $F` | `3` | PASS |
| Q7 | Đúng một dòng khuyến nghị | `grep -c "^Khuyến nghị: " $F` | `1` | PASS |
| Q8 | Có bản rút gọn express | `grep -c "^## Express" $F` | `1` và mục này gọi tên đủ M1–M6 (mỗi mã 1 dòng) | PASS |
| Q9 | Phủ đủ 4 mặt user chọn | `grep -ci` 4 từ khoá | `ràng buộc kiến trúc`=6 · `dùng lại`=3 · `bán kính ảnh hưởng`=2 · `hồi quy`=4 | PASS |
| Q10 | `doc_lint` sạch | `python3 scripts/doc_lint.py $F <spec> <plan>` | `exit 0`; thêm `--pair <spec> <plan>` cũng `exit 0` | PASS |
| Q11 | Không đụng mã nguồn, workflow còn nguyên | `git status --porcelain -- skills scripts hooks`; `python3 -m pytest tests/ -q` | git rỗng; `563 passed, 244 subtests passed in 35.72s`, 0 `failed` | PASS |

## Kiểm thêm ngoài DoD (bằng chứng cho nội dung nháp, không tính là hạng mục QC)

- `graphify god-nodes` → `Changelog - 28 edges`, `main() - 20`, `cli() - 17`, `log() - 17`,
  `cmd_build() - 17` — đúng danh sách ví dụ trong khối M1.
- `graphify affected "payload_cwd" --depth 2` → 5 hook phụ thuộc, đúng ví dụ trong M4.
- `npx --yes jscpd --min-lines 8 --threshold 3 --reporters console .` → `EXIT=0`,
  574 file, 72 cặp trùng, 1.82% token trùng — đúng số nêu trong M6.
- `npx --yes jscpd --help` xác nhận ba cờ `--min-lines`, `--threshold`, `--reporters`
  có thật ở bản 5.0.15; `jscpd --list` trả 224 định dạng.
