# Brief — Ví dụ & hướng dẫn thân thiện cho câu hỏi kiểu A/B/C

## Nguyên văn
User (2 lượt, cùng ý, lượt sau rõ hơn): "sau câu đó có thể thêm ví dụ và hướng dẫn
người dùng (ngắn gọn nhưng thân thiện) thêm để thân thiện người dùng, cho người dùng
biết trả lời gì để làm gì" — kèm ảnh chụp một câu hỏi lane thật (`Bạn muốn chạy lane
nào?` với option A/B) từ một session khác.

Cách hiểu đầu tiên:
- Mục tiêu: mọi câu hỏi dạng khuôn A/B/C của TDQ (chọn lane, chọn mode, hỏi commit,
  interview...) sau khi liệt kê option cần có thêm 1 đoạn ngắn, thân thiện, giúp
  người dùng lần đầu biết **gõ gì** để **được gì** — không chỉ "gõ chữ cái" mà còn ví
  dụ câu trả lời thật (vd: gõ "A" hoặc gõ nguyên câu "duyệt nhanh").
- Phạm vi đoán: đây là NÂNG CẤP của việc tầng nhỏ vừa làm ở turn trước (đã thêm 1 dòng
  hint ngắn `_Trả lời bằng chữ cái..._` vào `skills/tdq-intake/references/interview.md`).
  User chủ động nói "muốn mở request" ngay sau khi thấy bản tầng nhỏ đó — có thể vì
  muốn kỹ hơn (thêm VÍ DỤ cụ thể, không chỉ hướng dẫn chung chung) và/hoặc muốn đúng
  quy trình đầy đủ (spec/plan) cho thay đổi văn bản áp dụng xuyên suốt nhiều skill.
- Chỗ chưa rõ: nội dung ví dụ cụ thể là gì (gõ chữ cái đơn hay nguyên câu?); áp dụng
  cho TẤT CẢ câu hỏi khuôn A/B/C (interview.md dùng chung) hay chỉ câu hỏi lane; có
  cần đồng bộ với các câu hỏi không theo khuôn interview.md (vd dòng `➤ Duyệt: nhắn
  "duyệt spec"` ở tdq-spec, tdq-plan, tdq-build) hay không.

## Hiểu & kiến thức

### Năng lực dùng được
Việc thuần sửa văn bản 1 file markdown, không cần tool/skill ngoài, không cần MCP. Bỏ
qua bảng skill-inventory đầy đủ vì không có lựa chọn năng lực nào cần cân nhắc.

### Đọc code
- Vị trí đích: `skills/tdq-intake/references/interview.md`, khối "Dòng hướng dẫn trả
  lời" vừa thêm ở tầng nhỏ trước (dòng cuối file, sau khuôn "Bạn muốn bổ sung thêm gì
  không?"). Nội dung hiện tại (1 dòng, chung chung):
  `_Trả lời bằng chữ cái (vd: "A"), hoặc gõ thẳng ý bạn nếu không khớp option nào._`
- File này được nạp bởi mọi câu hỏi khuôn A/B/C trong toàn bộ TDQ: `tdq-intake` (chọn
  lane, vòng interview), `tdq-plan` (chọn mode nếu duyệt không nói rõ).
- Các dòng `➤ Duyệt:` KHÔNG dùng khuôn A/B/C — nằm riêng, in cứng trong 3 file:
  `skills/tdq-spec/SKILL.md` (`➤ Duyệt: nhắn "duyệt spec"`), `skills/tdq-plan/SKILL.md`
  (`➤ Duyệt: nhắn "duyệt plan mode <mode đề xuất>" (đổi được: main|subagent)`),
  `skills/tdq-intake/references/quick-lane.md` (`➤ Duyệt: nhắn "duyệt nhanh" (bỏ QC:
  "duyệt nhanh không QC"; "duyệt quick" vẫn chạy)`). Cả 3 đã tự mang ví dụ câu duyệt cụ
  thể — theo 2B, rà lại xem có cần thêm hướng dẫn/ví dụ phụ (vd nói rõ "trả lời đó sẽ
  làm gì tiếp theo") hay giữ nguyên vì đã đủ tự giải thích.
- Không có entry point runtime nào khác đọc các file này ngoài các skill trên (chỉ là
  tài liệu hướng dẫn Claude khi hỏi, không có code parse).

### Quyết định đã chốt
- Nội dung ví dụ (câu hỏi 1 → A): đưa cả 2 kiểu ví dụ — gõ tắt chữ cái (`"A"`) VÀ gõ
  nguyên câu tự nhiên khớp ngữ cảnh câu hỏi (vd với câu chọn lane: `"lane full"`/`"chế
  độ chuyên sâu"`; với câu duyệt: đã có sẵn ở dòng `➤ Duyệt:`, không lặp lại ở đây).
  Vì nội dung ví dụ câu tự nhiên phụ thuộc NGỮ CẢNH câu hỏi cụ thể (lane/mode/tuỳ
  chỉnh khác), dòng hướng dẫn chung trong `interview.md` chỉ nêu NGUYÊN TẮC ("gõ chữ
  cái HOẶC gõ thẳng câu trả lời tự nhiên khớp ý bạn chọn") + 1 ví dụ minh hoạ trung
  tính không gắn lane cụ thể, để không sai lệch khi áp dụng cho câu hỏi khác (mode,
  interview tuỳ chọn...).
- Phạm vi (câu hỏi 2 → B): sửa khối hướng dẫn dùng chung trong `interview.md` VÀ rà lại
  3 dòng `➤ Duyệt:` ở `tdq-spec/SKILL.md`, `tdq-plan/SKILL.md`,
  `tdq-intake/references/quick-lane.md`. Rà lại không có nghĩa chắc chắn sửa — mỗi dòng
  đã tự mang ví dụ câu duyệt cụ thể trong chính nó; chỉ thêm nếu thật sự thiếu (vd chưa
  nói rõ trả lời đó dẫn tới bước gì tiếp theo). Việc rà + kết luận từng dòng nằm ở P2
  của plan.
- Phương án loại: không tạo file/skill mới, không đụng hook — đây thuần là văn bản
  hướng dẫn cho Claude khi hỏi, không có logic máy đọc.

### Lộ trình
| Bước/phase | CÓ-BỎ | Vì sao |
|---|---|---|
| Research | BỎ | Thuần nội bộ, không có ẩn số bên ngoài (thư viện/API/phiên bản) |
| Interview | CÓ (đã xong, 2 câu, ở brief) | Có 2 điểm ảnh hưởng kết quả, đã hỏi & chốt |
| Subagent (implement) | BỎ | 1 file, việc nhỏ, làm main luôn nhanh hơn giao subagent |
| QC độc lập bằng agent (`tdq-qc-tester`) | BỎ | QC tự làm bằng đọc lại file đủ, không cần agent riêng cho việc văn bản |
| Phân tích → spec/plan → implement → report | CÓ (khung bất biến) | Giữ nguyên theo lane full |

## Hỏi đáp

1. Ví dụ trả lời nên là gì?
- A (đề xuất, USER CHỌN): Cả hai — vừa ví dụ gõ tắt (`"A"`) vừa ví dụ gõ nguyên câu tự
  nhiên — người quen gõ tắt lẫn người quen viết câu đều hiểu.
- (B, C: không chọn)

2. Áp dụng cho phạm vi nào?
- (A: không chọn)
- B (USER CHỌN): Cả khuôn A/B/C lẫn rà lại toàn bộ dòng `➤ Duyệt:` riêng lẻ ở
  tdq-spec/tdq-plan/tdq-build xem có cần thêm gì không.

Ghi chú xử lý mâu thuẫn: user chọn 2B (rà cả dòng `➤ Duyệt:`), khác đề xuất 2A ban đầu
của tôi (chỉ interview.md). Tôn trọng lựa chọn user — phạm vi thật sự = 2B, đã cập nhật
lại phần "Quyết định đã chốt" và "Đọc code" ở trên cho khớp 2B (rà cả 3 file `➤ Duyệt:`).
Ngày giờ: 2026-08-13 15:03.
