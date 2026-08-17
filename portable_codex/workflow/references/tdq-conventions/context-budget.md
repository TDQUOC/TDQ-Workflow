# Chi phí bước & chi phí context

Hai loại chi phí khác nhau, nằm ở hai tầng khác nhau của [soul.md](soul.md). Xếp sai tầng
là lý do luật bị bỏ qua hợp lệ, nên phần nào ra phần nấy.

Đo bằng hai lệnh:

```
python3 "./scripts/step_audit.py" --sessions 2
python3 "./scripts/token_audit.py" --sessions 2 --top 8
```

## Chi phí bước (tầng 2 — runtime)

Một tool call = một vòng round-trip. Đo trên phiên thật: trung vị **3,3 s** mỗi bước,
p90 12,3 s. Tổng thời gian tỉ lệ THẲNG với số bước, nên đây là tầng runtime, không phải
context cost.

- **Gộp tool call.** Biết trước 2–5 tool call độc lập (Bash, Read, Grep) → phát hết
  trong CÙNG MỘT LƯỢT; nhiều lệnh Bash độc lập thì gộp bằng `&&`. Tách khi cần khoanh vùng lỗi.
- **Gộp lệnh Bash.** Nhiều lệnh shell độc lập trong cùng một việc → một lệnh nối bằng
  `&&`, hoặc `;` khi muốn chạy hết dù có lệnh lỗi. Cấm tách thành nhiều lượt chỉ để
  nhìn kết quả từng lệnh cho dễ.
- **Đọc lại có điều kiện (luật MỀM).** Thông tin còn đủ và còn nguyên trong context thì
  đừng đọc lại file. Nhưng BẮT BUỘC đọc lại khi gặp một trong năm ca dưới đây. Luật này
  không bao giờ được viết thành lệnh chặn.
- **Chờ việc dài.** Lệnh chạy lâu (build, test suite lớn, server) → chạy nền rồi chờ theo
  điều kiện. Cấm vòng `sleep` thăm dò: mỗi vòng là một bước tròn mà không thêm thông tin.

### Năm ca BẮT BUỘC đọc lại

1. Context đã bị nén — thứ còn lại là bản tóm tắt, không phải nội dung file.
2. Lần trước chỉ đọc một phần (`offset`/`limit`), không đọc trọn file.
3. File có thể đã đổi từ lần đọc: mình vừa sửa, lệnh vừa sinh lại, sub-agent hoặc user chạm vào.
4. Sắp sửa chính file đó — trước khi Edit phải có nội dung mới nhất.
5. Nhớ không chắc, hoặc cần chi tiết mà lần đọc trước không để ý.

**Nghi ngờ thì đọc lại: chất lượng đứng trên runtime.** Đọc thừa một lần tốn 3,3 giây;
suy luận trên nội dung cũ tốn cả một vòng fix sai. Luật này không bắc qua sub-agent —
agent có context riêng, nó phải tự đọc.

### Cấm gộp

Bốn ca dưới đây tách ra là ĐÚNG, gộp lại là SAI, kể cả khi gộp được về mặt kỹ thuật.

| Ca | Vì sao cấm gộp |
|---|---|
| Bước đỏ → bước xanh của TDD | gộp thì không còn bằng chứng test đỏ thật, red-green thành hình thức |
| Đang khoanh vùng lỗi | gộp 5 lệnh rồi lỗi ở đâu không biết, phải chạy lại từng lệnh, tốn nhiều bước hơn |
| Lệnh phá hủy hoặc khó đảo | xoá, ghi đè, `git reset` — phải xem kết quả lệnh trước rồi mới chạy lệnh sau |
| Lệnh sau cần kết quả lệnh trước | gộp thì lệnh sau chạy trên giả định, ra kết quả sai mà không ai biết |

Ví dụ ĐÚNG: một lượt phát `Read a.py`, `Read b.py`, `grep -n "foo" c.py` — ba việc không
liên quan nhau, đọc xong mới suy luận.
Ví dụ SAI: một lượt chạy `pytest` (kỳ vọng đỏ) rồi `Edit` file rồi `pytest` lại — bước
đỏ mất bằng chứng, và lần chạy đầu vô nghĩa vì file chưa sửa.

## Chi phí context (tầng 3)

Mỗi tool call = 1 API call = model đọc lại TOÀN BỘ context: output `n` ký tự tốn
`n/4 × số API call còn lại` — **carry-cost**.

- **Lint đúng file.** Chạy `doc_lint.py` trên ĐÚNG file vừa sửa, cấm truyền cả thư mục
  (`docs/tdq`): lint thư mục in ~8.000 ký tự lỗi của file cũ, không liên quan.
- **CLI im lặng.** `tdq_state.py init|set|reset` mặc định in 1 dòng; chỉ thêm `--json`
  khi thật sự cần soi state. `next --brief` thay cho `next` trừ khi cần checklist đầy đủ.
- **Đọc vừa đủ.** File trên 200 dòng: `grep -n` định vị rồi Read theo `offset`/`limit`.
  Cấm `cat` (dùng Read), cấm `grep -A5 -B5` khi `-c`/`-l` đã đủ trả lời.
- **Việc nặng giao subagent.** Research web và đọc ≥4 file giao agent riêng — agent có
  context window riêng, chỉ trả digest về hội thoại chính.
- **Soul phân xử.** Mọi luật trên đây chỉ cắt chi phí khi đầu ra không đổi. Việc đòi đọc
  TRỌN nhiều file hay chạy đủ phép kiểm thì cứ làm đủ: chất lượng đứng trên context cost
  theo [soul.md](soul.md).
