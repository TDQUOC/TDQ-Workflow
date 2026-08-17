# Quy trình thêm ngôn ngữ mới

Soul: chất lượng > runtime > context cost. Nạp khi gặp ngôn ngữ chưa có rule.

## Nguồn

- Khuôn 7 mục và mức ngưỡng rút từ bộ rule hiện có (`chung.md` + 7 file ngôn ngữ),
  vốn dựng từ file research của request set-soul trong `docs/tdq/research/`.
- Quy trình duyệt-trước-ghi lấy theo luật gate của TDQ: chỉ NGƯỜI DÙNG duyệt.

## Khi nào áp dụng

- Task phải viết/sửa file có đuôi KHÔNG nằm trong bảng của `index.md`, và user scope
  cũng chưa có skill `tdq-rules` cho ngôn ngữ đó.
- Chỉ chạy quy trình khi request thật sự cần code ngôn ngữ đó; ngôn ngữ chỉ bị nhắc
  qua thì bỏ.

## Luật Intentionality

1. Rule mới viết ra phải trả lời được 3 câu hỏi Intentionality của `chung.md`,
   không chép nguyên văn style guide dài dòng.
2. **Nguồn phải có thật**: mọi URL đưa vào rule phải nằm trong file research của
   request; chưa tìm được nguồn thì ghi "chưa có nguồn", cấm bịa link.
3. Rule không nói được "vi phạm thì đo bằng gì" là rule chết — mỗi luật phải gắn
   linter hoặc ngưỡng số.

## Ngưỡng đo được

- File rule mới: dưới 150 dòng, đủ khuôn 7 mục đúng thứ tự như file này.
- Tối thiểu 2 nguồn chính thức có URL kiểm chứng được trong research.
- Ngưỡng complexity lấy theo `chung.md` (10/15, họ C 25); chỉ đổi khi nguồn chính
  thức của ngôn ngữ nêu mức khác, và phải ghi rõ nguồn đó.

## Làm gì

1. Search tavily đúng 4 truy vấn cố định, lưu kết quả + URL vào file research của
   request đang chạy:
   - `<ngôn ngữ> official style guide`
   - `<ngôn ngữ> linter static analysis tool`
   - `<ngôn ngữ> code smells common mistakes`
   - `<ngôn ngữ> cyclomatic cognitive complexity threshold`
2. Viết nháp rule theo khuôn 7 mục, kèm dòng linter cho bảng `index.md`.
3. Nháp xong thì **trình nháp trong chat** cho user đọc — đủ nguyên văn, không
   tóm tắt cụt.
4. **DỪNG chờ user duyệt.** User chưa duyệt thì không ghi file rule ra bất kỳ đâu.
5. User duyệt xong mới ghi vào `~/.claude/skills/tdq-rules/` dạng skill có
   `SKILL.md` (nêu khi nào nạp, file rule nằm cạnh) để mọi project dùng lại;
   request hiện tại thì nạp rule đó như tầng theo việc.

## Tự kiểm

- [ ] Đã chạy đủ 4 truy vấn cố định; kết quả nằm trong file research
- [ ] Mọi URL trong nháp có mặt trong research; thiếu nguồn đã ghi "chưa có nguồn"
- [ ] Có câu duyệt của user trong chat TRƯỚC khi ghi ra `~/.claude`
- [ ] Skill mới có `SKILL.md`; bảng linter đã sẵn dòng cho `index.md`

## Ví dụ ĐÚNG/SAI

```text
SAI  — gặp Kotlin, viết rule từ trí nhớ, ghi thẳng ra user scope không hỏi ai.
ĐÚNG — search 4 truy vấn → lưu research → nháp khuôn 7 mục → trình trong chat
       → user gõ "duyệt" → mới ghi skill tdq-rules kèm SKILL.md.
```
