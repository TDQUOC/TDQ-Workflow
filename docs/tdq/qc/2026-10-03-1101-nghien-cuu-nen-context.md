# QC — Báo cáo nghiên cứu: nén context và rút thời gian máy của workflow

Ngày: 2026-10-03 · Plan: ../plan/2026-10-03-1101-nghien-cuu-nen-context.md · Vòng: 2 · Mức QC: `full`
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

**Kết luận: PASS ở vòng 2.** Vòng 1 trượt Q4 (số của T2.1 không chạy lại được); task sửa QC1.1
viết lại script đo ngay trong báo cáo, chạy lại và đối chiếu. Không có lệch spec nào.

`R` = `docs/tdq/reports/2026-10-03-1101-nghien-cuu-nen-context.md`.

| # | Hạng mục | Lệnh đã chạy | Kết quả | PASS/FAIL |
|---|---|---|---|---|
| Q1 | Đủ số hướng | `grep -c "^| H[0-9]" R` + cột nhóm | 11 hướng H1–H11; nhóm a, b, c đều có | PASS |
| Q2 | Mỗi hướng có số | ô tiết kiệm context/thời gian trống trong các dòng `H` | 0 ô trống | PASS |
| Q3 | Số bên ngoài đã kiểm chéo | `grep -c "^| N[0-9]" R` | 38 số: 28 khớp · 3 lệch (ghi số đúng) · 7 không xác minh được, không dùng làm căn cứ | PASS |
| Q4 | Thử nghiệm chạy lại được | khối script / lệnh trong từng tiểu mục | T2.1: script trong báo cáo (vòng 2) · T2.2: 4 lệnh `discover` · T2.3: script trong báo cáo | PASS (vòng 2) |
| Q5 | Workflow không bị sửa | `git diff main -- skills hooks scripts tests agents` | 0 dòng | PASS |
| Q6 | Có khuyến nghị | `grep -n "## Thứ tự đề xuất" R` | có; request tiếp theo `test-vung-cham-buoc-trung-gian` (H5) | PASS |
| Q7 | Lint | `doc_lint.py R spec plan` | exit 0 | PASS |

## Vòng 1 → vòng 2

- **Q4 trượt ở vòng 1:** mục T2.1 trỏ tới năm script đã xoá, chỉ mô tả bằng lời.
- **QC1.1:** viết lại một script tự chứa ngay trong mục T2.1, chạy lại trên bản sao tạm.
  - Khớp chính xác: mốc gốc 50.893 / 18.631, phép (1), (1b), (2), số token dấu không đụng được
    3.419 / 1.233.
  - Lệch: phép (3) −583 so với −556 (+4,9%) ở lane full, −86 so với −59 (+45,8%) ở lane quick.
    Lý do: ranh giới câu — lần chạy lại gộp thêm một câu 57 token trong `nhanh-request.md`. Báo
    cáo giữ số cũ, ghi rõ phép (3) không tái hiện chính xác.
  - Phép (4) gộp: −10.682 so với −10.655 (+0,3%) và −1.730 so với −1.703 (+1,6%).
- **Lỗi lệnh kiểm của chính plan:** lệnh kiểm QC1.1 chứa ```` ``` ```` trong khối code inline,
  làm `tdq_team.py check` cắt mất phần sau (SyntaxError). Đổi sang `chr(96)*3`, kiểm lại xanh.

## Một chỗ sửa số đã báo user

Tóm tắt spec gửi user ghi "trọn bộ test chiếm 31% thời gian máy". T1.2 chạy lại cho thấy trọn bộ
test là **26%**; 31% là phần của mọi lần chạy test cộng lại. Báo cáo ghi tách hai số và nêu chỗ sửa.

## Thư mục tạm

Mọi thử nghiệm chạy trên bản sao trong `%TEMP%` (`tdqt12`, `tdq-thu-nghiem\t21`, `\t22`, `tdqt23`,
`\qc11`); đã xoá hết, kể cả thư mục cha rỗng `tdq-thu-nghiem`.

## Nợ khai ra, không giấu

1. Phép (3) của T2.1 (gộp câu gần trùng) phụ thuộc cách cắt câu, không tái hiện chính xác ở lane
   quick — số nhỏ (−59 / −86 token), không đổi kết luận nhóm (c).
2. Danh sách 23 / 9 file bắt buộc đọc chưa từng được ghi thành dữ liệu trong repo; QC1.1 dựng lại
   bằng cách khớp mốc gốc. Request tiếp theo nên ghi danh sách này cạnh công cụ đo.
3. Chạy test song song chưa dùng được (test git dùng chung trạng thái); 27 test đỏ khi chạy từ
   PowerShell vì gọi `true` — cả hai thuộc hướng H5/H6, chưa sửa ở request này.
