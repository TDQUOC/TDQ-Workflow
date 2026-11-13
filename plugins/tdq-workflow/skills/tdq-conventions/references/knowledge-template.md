# Chuẩn bài học tri thức (TDQ Knowledge Template)

Áp dụng cho các bài học kinh nghiệm, quy ước rút ra từ các phiên làm việc (O12).
Tuân thủ nguyên tắc: chất lượng > runtime > context cost.

## Vòng đời bài học

Mỗi bài học tri thức có đúng một trong 4 trạng thái:

1. **`candidate`**: Bài học mới ghi nhận từ thực tế, chưa qua kiểm định của con người.
   - BẮT BUỘC: `auto_policy: false` (không bao giờ được tự động kích hoạt thành policy của hệ thống).
   - Tuyệt đối không tự ý nới quyền, không tự động nạp vào system prompt nếu chưa duyệt.
2. **`reviewed`**: Bài học đã được con người (human/team) rà soát, kiểm chứng và phê duyệt.
   - BẮT BUỘC: có `nguoi_duyet`, `ngay_duyet`, `nguon.evidence`.
3. **`rejected`**: Bài học bị từ chối do không chính xác, gây tác dụng phụ hoặc không phù hợp.
4. **`superseded`**: Bài học đã lỗi thời và bị thay thế bởi bài học mới.
   - BẮT BUỘC: có `thay_the` trỏ tới bài học thay thế.
   - Thu hồi/thay thế có hiệu lực tức thì ngay khi đọc.

*Ghi chú về tài liệu cũ (legacy):* Các tài liệu chưa có frontmatter chuẩn được xếp loại `legacy_unverified`, không tự động phong cấp thành `reviewed`.

## Quy định về bảo mật

- Tuyệt đối KHÔNG lưu trữ secret, token, API key, password, private key trong file bài học.
- Quá trình kiểm tra secret tự động (secret screening) sẽ từ chối lưu bài học chứa secret.
- Mọi nhật ký lỗi không được in chuỗi secret thô (data minimization).

## Khung mẫu Markdown

```markdown
---
tieu_de: <Tiêu đề ngắn gọn của bài học>
trang_thai: candidate | reviewed | rejected | superseded
nguon:
  request: <Mã request sinh ra bài học, ví dụ 2026-10-17-1741-nang-cap-tdq-toan-dien>
  commit: <SHA commit liên quan>
  evidence: <Đường dẫn file bằng chứng hoặc test, ví dụ docs/tdq/qc/...>
pham_vi: <Phạm vi áp dụng, ví dụ skills/tdq-build, scripts/tdq_eval.py, toàn cục>
nguoi_duyet: <Người hoặc nhóm duyệt nếu reviewed>
ngay_duyet: <Thời điểm ISO nếu reviewed>
thay_the: <Đường dẫn bài học thay thế nếu superseded>
auto_policy: false
---

# <Tiêu đề bài học>

## Ngữ cảnh và vấn đề
<Mô tả ngắn gọn tình huống phát sinh và vấn đề gặp phải.>

## Nguyên nhân gốc rễ
<Lý giải tại sao vấn đề xảy ra.>

## Quy tắc áp dụng
<Quy tắc rõ ràng, cụ thể để không lặp lại lỗi.>

## Bằng chứng kiểm chứng
<Liên kết hoặc kết quả test chứng minh quy tắc này hoạt động đúng.>
```
