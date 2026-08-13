# RESEARCH — Tối ưu skill cho LLM mà giữ nguyên hành vi

Ngày: 2026-08-13 · Lớp search: `tavily-primary` (2 truy vấn) + `WebFetch` 1 bài

## Truy vấn 1 — cách Anthropic khuyến nghị tổ chức skill

Nguồn: <https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills>

- Progressive disclosure có 3 tầng: metadata (`name` + `description`) luôn nằm trong
  system prompt · thân `SKILL.md` chỉ nạp khi skill được chọn · file trong `references/`
  chỉ đọc khi thân file trỏ tới.
- Metadata mỗi skill tốn khoảng 30–50 token, nên `description` là chỗ đắt nhất tính theo
  tần suất: nó nằm trong MỌI phiên, kể cả phiên không dùng skill đó.
- Khi `SKILL.md` phình to hoặc chứa phần chỉ đúng trong vài tình huống → tách sang file
  phụ và trỏ tên file từ thân chính.

## Truy vấn 2 — chi phí của file chỉ dẫn và cách nén

Nguồn: <https://www.augmentcode.com/guides/how-to-build-agents-md> (dẫn nghiên cứu ETH Zurich)

- File chỉ dẫn kiểu `AGENTS.md`/`CLAUDE.md` làm tăng chi phí suy luận 19–23%; bản do
  người viết tay chỉ đem lại lợi ích khoảng 4%. Bài học: mỗi dòng phải đáng giá.
- Ngưỡng thực dụng được nêu: quá 150–200 dòng thì tách file theo thư mục.

Nguồn: <https://arxiv.org/html/2603.29919v1> — *SkillReducer* (đọc qua `WebFetch`)

Quy trình 2 tầng, đúng bài toán của request này:

1. **Tầng định tuyến** — nén `description` bằng delta debugging (thuật toán `ddmin`):
   cắt từng mệnh đề, giữ tập nhỏ nhất mà vẫn định tuyến đúng, có bước phục hồi chọn lọc.
2. **Tầng thân file** — phân loại nội dung thành 5 nhóm: luật lõi, nền tảng, ví dụ,
   khuôn mẫu, phần thừa. CHỈ luật lõi nằm thường trực; bốn nhóm còn lại chuyển thành
   module đọc theo yêu cầu. Kèm khử trùng lặp chéo file và gắn metadata định tuyến cho
   từng file tham chiếu.

Số đo họ báo: `description` giảm 48% · thân file giảm 39% · bộ skill ngoài đời giảm tới
77,5% ở tài liệu dài · chi phí mỗi lần gọi skill giảm 26,8%.

Hai cổng an toàn — đây là phần đáng chép nhất cho việc của ta:

- **Cổng 1 (trung thực)**: kiểm bản nén còn giữ đủ mọi khái niệm vận hành của bản gốc,
  thiếu thì trả lại nguyên phần đó.
- **Cổng 2 (chất lượng chức năng)**: chạy tác vụ thật ở 3 điều kiện (không skill, skill
  gốc, skill nén) rồi so điểm; có vòng phản hồi đẩy mục bị hụt trở lại nhóm lõi, tối đa
  2 vòng. Họ đạt 86% pass, không hồi quy.

## Điều rút ra cho tdq-workflow

- Hướng tối ưu đúng là **đổi tầng nạp**, không phải xoá luật: luật vẫn còn nguyên chữ,
  chỉ chuyển từ "luôn nạp" sang "đọc khi cần".
- `description` của 6 skill đáng soi riêng vì nằm trong mọi phiên; repo đã có trần 900
  ký tự nhưng chưa từng nén theo kiểu cắt-thử-đo.
- Trùng lặp chéo file là hạng mục có tên trong nghiên cứu, khớp với giả thuyết 1–3 ở brief.
- Mọi khuyến nghị phải đi kèm cách chứng minh "không mất luật" — bắt chước cổng 1 bằng
  bảng đối chiếu luật, cổng 2 bằng chính bộ test sẵn có của repo.
