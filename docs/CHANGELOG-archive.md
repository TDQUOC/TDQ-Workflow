# Changelog — bản lưu trữ

Các bản 0.17.0 trở về trước, tách khỏi `CHANGELOG.md`
để file chính nằm dưới trần R6 500 dòng. Mới nhất trên cùng.

## 0.18.0 — 2026-08-14

Set "soul" cho bộ workflow: chất lượng code agent > runtime > context cost. Ba tầng ưu
tiên này thành luật gốc, mọi khuôn tài liệu khai nó ra, và luật cũ được rà lại theo nó.
Kèm theo là thư viện rule ngôn ngữ để model yếu cũng viết code sạch, cùng năm cơ chế
chặn nợ kiến trúc do quick-fix.

- `skills/tdq-conventions/references/soul.md` (mới): ba tầng ưu tiên kèm luật phân xử khi
  hai tầng đụng nhau. Skill nền và bản portable trỏ về đây, mỗi file đúng một dòng.
- Rà 28 file luật theo soul, biên bản ở `docs/tdq/knowledge/2026-08-14-ra-soat-luat-theo-soul.md`.
  Hai chỗ SỬA: khoá cứng phạm vi QC trong `qc.md`, và ngưỡng context trong `context-budget.md`.
- `skills/tdq-build/references/rules/` (mới, 10 file): chỉ mục + 7 file ngôn ngữ, mỗi file
  cùng một khuôn (Intentionality, mùi code, công cụ lint, nguồn chính thức có URL thật).
- `scripts/code_rule_scan.py` (mới): quét file đã đổi theo bảng rule, ba trạng thái PASS /
  LỖI / CHƯA KIỂM ĐƯỢC — thiếu công cụ lint thì báo đúng trạng thái, không PASS khống.
  Log stderr có timestamp, tắt bằng `--im`, chi tiết bằng `--chi-tiet`. Không tự cài gói.
- Cổng clean code ở phase spec: việc chạm mã nguồn thì hỏi user BẬT/TẮT, đáp án ghi vào
  spec §4. TẮT vẫn tổ chức code theo rule ngôn ngữ, chỉ bỏ bước scan cuối request.
- Năm cơ chế chống nợ kiến trúc: M1 hồ sơ `docs/kien-truc.md` sinh một lần mỗi project ·
  M2 khối "Ràng buộc kiến trúc phải giữ" trong spec §5 · M3 luật "Tìm rồi mới tạo" ở bước
  code · M4 dòng `Chạm:` trong plan lấy từ `graphify affected` · M5 ba hạng mục QC cố định
  QC-F1→F3, đồng bộ nguyên văn giữa bản skill và bản portable.
- Năm khuôn tài liệu (brief, spec, plan, qc, report) đều có dòng Soul.
- Test: 574 → 596 (306 subtest). Nghiệm thu thật bằng agent Haiku đọc rule soát file mẫu
  5 lỗi cố ý — nêu đúng 5/5, không hỏi lại câu nào.

## 0.17.0 — 2026-08-14

Trang trí khối chat cuối trả lời user: dùng markdown mà cả ba mặt (terminal, app,
extension) đều dựng được, tách nhãn khỏi nội dung, và chốt bằng test thay vì bằng trí nhớ.
Màu và cỡ chữ không làm được — ba mặt không dùng chung bộ dựng, mẫu số chung là markdown
terminal dựng được. Nguyên tắc xuyên suốt: **chỉ thêm dấu đánh dấu, không đổi một từ nào**
của nội dung đang chạy.

- `skills/tdq-conventions/references/user-facing-block.md`: viết lại. Thêm bảng 5 thành
  phần kèm cấu trúc trình bày dùng cho từng thành phần, mục `## Bảy luật trang trí`, bảng
  6 ký hiệu ngoài ASCII được phép, và ví dụ đối chiếu `### Trước` / `### Sau`.
- Luật cấm emoji giữ nguyên; chỗ nới đúng một điểm là ký hiệu Unicode, giới hạn trong sáu
  ký tự `➤ · — → – …`. Cả sáu đều có bằng chứng đang in ra cho user trong kho. Ký tự `▸`
  bị loại vì grep toàn kho ra 0 kết quả. Ký tự kẻ khung bị cấm vì đòi canh cột.
- Trang trí khối mẫu trong 8 file skill và 3 file bản portable: nhãn trường in đậm với dấu
  hai chấm nằm TRONG cặp sao, đường dẫn và tên lệnh bọc nháy ngược. Năm chỗ mã sinh chuỗi
  giữ nguyên từng byte để hook và test cũ không lệch.
- `skills/tdq-status/SKILL.md`: bỏ `✔` và `⏳` ở dòng báo trạng thái duyệt, thay bằng chữ
  in đậm. Đây là chỗ duy nhất trong kho còn dạy Claude in emoji ra cho user.
- `scripts/scan_block_symbols.py` (mới): quét ký tự Unicode loại `P*`/`S*` ngoài ASCII
  trong 12 file phạm vi, có chế độ `--chi-khoi` chỉ quét nội dung khối in cho user.
- `tests/test_user_facing_block.py`: 4 → 10 test (58 subtest). Thêm phép kiểm whitelist ký
  hiệu, phép kiểm khối mẫu theo luật 1/3/7, phép kiểm chuỗi do mã sinh, phép kiểm bản
  portable khớp khuôn gốc, và bảng `SO_KHOI` chặn trường hợp phép kiểm chạy rỗng mà vẫn
  xanh. Toàn bộ suite: 569 → 574 test.
