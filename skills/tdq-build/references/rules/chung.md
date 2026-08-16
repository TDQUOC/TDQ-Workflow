# Rule chung mọi ngôn ngữ

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md
Nạp file này TRƯỚC, rồi mới nạp file rule ngôn ngữ theo bảng trong `index.md`.

## Nguồn

- SonarSource Clean Code — https://community.sonarsource.com/t/introducing-clean-code-in-our-products/98431 —
  4 thuộc tính đo được: Consistent, Intentional, Adaptable, Responsible.
- arXiv 2411.10656 — https://arxiv.org/html/2411.10656v2 — đo 1.848 issue code do LLM
  sinh: 59,6% thuộc nhóm Intentionality.
- Ngưỡng complexity — https://dev.to/optiklab/writing-self-documented-code-with-low-cognitive-complexity-3k2l
  và https://www.augmentcode.com/learn/how-to-reduce-cyclomatic-complexity — default
  SonarQube 10/15(25); ESLint để 20, Microsoft CA1502 để 25 nên phải chốt một mức.
- Bảo mật — https://www.kiuwan.com/blog/secure-coding-guidelines — OWASP Secure Coding
  Practices là checklist trung lập ngôn ngữ; CERT chỉ có cho C/C++/Java/Perl.

## Khi nào áp dụng

- Mọi lần viết hoặc sửa code, bất kể ngôn ngữ — kể cả script nhỏ và test.
- Luật này áp thường trực, không có cổng bật/tắt. Nguyên tắc SOLID và checklist 5 câu
  ở `skills/tdq-conventions/references/clean-code.md` áp cùng lúc với file này.

## Luật Intentionality

Code LLM sinh ra hỏng nhiều nhất ở nhóm Intentional (59,6%), nên soát nhóm này TRƯỚC
ba nhóm còn lại. Ba câu hỏi bắt buộc trước khi nộp code:

1. **Tên nói đúng việc chưa?** Tên hàm/biến đọc lên phải ra đúng việc nó làm.
2. **Logic đầy đủ chưa?** Không TODO bỏ lửng, không nhánh điều kiện trống, không
   nuốt lỗi im lặng.
3. **Có code chết không?** Biến không dùng, import thừa, hàm không ai gọi → xoá.

## Ngưỡng đo được

- Cyclomatic complexity ≤ 10 mỗi hàm (mọi ngôn ngữ).
- Cognitive complexity ≤ 15 mỗi hàm; riêng họ C (C, C++, Objective-C) ≤ 25.
- Hàm vượt ngưỡng → tách hàm nhỏ, KHÔNG nới ngưỡng tại chỗ.
- Cách ghi đè ngưỡng: chỉ được ghi đè bằng một dòng trong spec của request (kèm số mới
  và lý do), vì default mỗi tool mỗi khác; cấm ghi đè bằng thoả thuận miệng trong chat.

## Làm gì

1. Mở `index.md`, tra đuôi file đang sửa → nạp đúng file rule ngôn ngữ.
2. Viết code theo mục "Làm gì" của file ngôn ngữ đó; tên đặt theo chuẩn ngôn ngữ.
3. Soát checklist OWASP rút gọn: validate input tại biên, không hardcode secret/API key,
   lỗi phải được xử lý hoặc log rồi ném tiếp — cấm `catch` rỗng.
4. Chạy lệnh linter trong bảng `index.md`; máy thiếu linter thì ghi "chưa kiểm được",
   cấm ghi PASS.

## Tự kiểm

- [ ] Không hàm nào vượt cyclomatic ≤ 10, cognitive ≤ 15 (họ C ≤ 25)
- [ ] Trả lời được cả 3 câu hỏi Intentionality ở trên cho file vừa sửa
- [ ] Không secret, không code chết, không TODO bỏ lửng
- [ ] Linter đã chạy (hoặc đã ghi rõ "chưa kiểm được" khi máy thiếu linter)

## Ví dụ ĐÚNG/SAI

```python
# SAI — tên mơ hồ, nuốt lỗi, nhánh trống (cả 3 lỗi Intentionality):
def process(d):
    try:
        r = do(d)
    except Exception:
        pass  # TODO
# ĐÚNG — tên nêu việc, lỗi được log và ném tiếp:
def tach_dong_loi(log_text):
    try:
        return [d for d in log_text.splitlines() if "ERROR" in d]
    except UnicodeDecodeError as loi:
        logging.error("log_text hỏng encoding: %s", loi)
        raise
```
