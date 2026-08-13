# Brief — Fix: câu hỏi TDQ bị ẩn khi bật focus mode

## Nguyên văn
User: "duyệt report và mở request mới lên phương án fix cho issue đó" — sau khi báo cáo
`docs/tdq/reports/2026-08-13-focus-mode-an-cau-hoi.md` được duyệt, mở request mới để lên
phương án sửa (không chỉ điều tra nữa).

Cách hiểu đầu tiên: dựa trên nguyên nhân đã chốt ở report trước — `stop_gate.py` chặn
Stop mọi turn đổi-repo-mà-chưa-log, khiến câu hỏi lane/interview (in trước lúc bị chặn)
không phải "dòng cuối turn", nên focus mode gập ẩn nó. Report đã gợi ý 1 hướng: ghi
working log TRƯỚC khi in câu hỏi cần dừng chờ, để câu hỏi luôn là dòng cuối turn. Mục tiêu
request này: LÊN PHƯƠNG ÁN (thiết kế cách sửa cụ thể) — chưa chắc đã yêu cầu triển khai
ngay, cần hỏi lại phạm vi.

Phạm vi đoán: đổi thứ tự bước trong các skill có câu hỏi cần dừng chờ (`tdq-intake`,
`tdq-spec`, `tdq-plan`, quick-lane...) — ghi log trước, hỏi sau.

Chỗ chưa rõ:
1. "Lên phương án" nghĩa là chỉ THIẾT KẾ (spec mô tả cách sửa, chưa code) hay LÀM LUÔN
   (spec → plan → build luôn trong request này)?
2. Đổi thứ tự "log trước, hỏi sau" có tác dụng phụ: một số nội dung log (vd tóm tắt "đã
   hỏi gì, đang chờ gì") chỉ biết chính xác SAU khi câu hỏi đã được soạn — cần quyết định
   cách log tách 2 giai đoạn (ghi khung trước, bổ sung chi tiết sau) hay chấp nhận log hơi
   sớm/thiếu chi tiết.
3. Phạm vi áp dụng: chỉ 4 file chính (`tdq-intake`, `tdq-spec`, `tdq-plan`,
   `quick-lane.md`) hay còn chỗ khác có DỪNG-chờ-user tương tự (vd `tdq-build` khi hỏi về
   commit)?

## Hiểu & kiến thức

### Kiểm kê năng lực
`skill_inventory.py` không có skill nào khớp việc sửa văn bản quy ước nội bộ (không phải
domain code) — tất cả gom vào dòng tổng KHÔNG áp dụng.

### Đọc code
- `skills/tdq-conventions/SKILL.md` §1 "Giao thức một turn" bước 4 đã QUY ĐỊNH SẴN: "Cuối
  turn có đổi repo: chạy ĐÚNG MỘT lệnh `tdq_finish.py --files ... --log ... --phase ...`".
  Đây chính là quy ước đúng (lint → append log → set phase → graphify gộp 1 lệnh) —
  nhưng suốt cả 2 request trước (`fix-dong-giai-thich-lane`, `focus-mode-an-cau-hoi`),
  Claude KHÔNG dùng lệnh này — luôn Edit tay working log SAU khi bị `stop_gate.py` chặn,
  tức SAU khi câu hỏi/tóm tắt đã in ra chat. Đây là 2 lỗ hổng riêng biệt cộng dồn:
  (a) không tuân thủ dùng `tdq_finish.py`, (b) thứ tự log-sau-câu-hỏi thay vì trước.
- `grep "DỪNG"` liệt kê toàn bộ điểm dừng-chờ-user sau khi đổi repo, cần áp quy tắc mới:
  `tdq-intake/SKILL.md` bước 2 (câu hỏi lane) + bước 4 Phần C (duyệt nhanh); vòng interview
  Phần B (không có từ khoá DỪNG tường minh nhưng có dừng ngầm chờ trả lời); `tdq-spec/SKILL.md`
  bước 4 (duyệt spec); `tdq-plan/SKILL.md` bước 5 (duyệt plan); `tdq-intake/references/quick-lane.md`
  bước 8 (vượt trần 3 vòng fix); `tdq-build/SKILL.md` (mode thiếu → DỪNG HỎI; vượt trần 3
  vòng QC → DỪNG báo user; hỏi user có commit không ở cuối report).
- Không có ẩn số ngoài (thư viện, API, phiên bản) — việc thuần sửa quy ước nội bộ trong
  chính repo này, đã có đủ nguồn từ report request trước (docs.claude.com + GitHub Issue
  #50894). **Research: BỎ.**

### Vòng interview
1. Cách sửa: viết quy tắc **1 LẦN** trong `tdq-conventions/SKILL.md` §1 (áp dụng chung mọi
   skill, DRY) rồi các skill con chỉ cần 1 câu trỏ về, hay viết LẶP LẠI câu chữ ở TỪNG file
   DỪNG-chờ-user (rõ ràng hơn khi đọc riêng lẻ 1 skill, nhưng dễ lệch câu chữ về sau)?
2. Có nhân dịp này đổi luôn cách làm từ "Edit tay working log" sang "gọi đúng
   `tdq_finish.py` như quy ước đã ghi" không? (Sửa dứt điểm cả 2 lỗ hổng cộng dồn, nhưng
   mở rộng phạm vi thêm việc sửa cách Claude vận hành, không chỉ sửa văn bản skill.)

## Hỏi đáp
User trả lời "1A 2A": chọn viết quy tắc 1 lần trong `tdq-conventions/SKILL.md` §1 (DRY —
mọi skill đã "Nạp tdq-conventions trước" nên tự động thừa hưởng, không cần sửa thêm file
nào khác); đổi luôn sang bắt buộc gọi `tdq_finish.py`, cấm Edit tay working log.

## Chốt kiến thức
- Sửa ĐÚNG 1 file: `skills/tdq-conventions/SKILL.md` §1 bước 4. Nội dung mới: (a) bắt
  buộc dùng lệnh `tdq_finish.py`, cấm Edit tay file working log; (b) lệnh đó phải chạy
  TRƯỚC đoạn chat cuối cùng kết thúc turn (tóm tắt/câu hỏi/dòng ➤ Duyệt/báo lỗi vượt
  trần) — không gọi thêm tool nào sau khi đã in đoạn đó, để đoạn chat luôn là "final
  response" thật của turn, tương thích focus mode.
- Không sửa từng skill con riêng lẻ (`tdq-intake`, `tdq-spec`, `tdq-plan`, `quick-lane`,
  `tdq-build`) — chúng đã nạp `tdq-conventions` nên tự động thừa hưởng quy tắc mới, đúng
  lựa chọn 1A của user.
- Đã loại: viết lặp câu chữ ở từng file (phương án B bị user từ chối) — vì dễ lệch câu
  chữ giữa các file theo thời gian, đúng lý do đã nêu lúc hỏi.
- Kiểm chứng sống: từ turn viết plan trở đi trong CHÍNH request này, tự áp dụng ngay quy
  tắc mới (gọi `tdq_finish.py` trước khi in tóm tắt/câu hỏi) làm bằng chứng hoạt động —
  không chỉ sửa văn bản suông.

### Lộ trình
| Bước/phase | Chạy? | Vì sao |
|---|---|---|
| Research web | BỎ | Thuần nội bộ, đã có nguồn từ request `focus-mode-an-cau-hoi` trước |
| Interview | Đã xong (2 câu, không còn mơ hồ) | — |
| QC độc lập (agent) | BỎ | Việc thuần văn bản 1 file, tự đọc lại + doc_lint đủ; QC còn có thể tự kiểm bằng cách quan sát chính các turn build/QC/report của request này có tuân quy tắc mới không |

