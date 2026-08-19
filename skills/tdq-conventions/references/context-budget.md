# Chi phí bước & chi phí context

Hai loại chi phí khác nhau, nằm ở hai tầng khác nhau của [soul.md](soul.md). Xếp sai tầng
là lý do luật bị bỏ qua hợp lệ, nên phần nào ra phần nấy.

Đo bằng hai lệnh:

```
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/step_audit.py" --sessions 2
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/token_audit.py" --sessions 2 --top 8
```

## Mục lục

- [Chi phí bước (tầng 2 — runtime)](#Chi phí bước (tầng 2 — runtime))
- [Chi phí context (tầng 3)](#Chi phí context (tầng 3))

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

### Đọc lại vì LUẬT hay vì QUÊN

Đo trên 5 phiên thật (`token_audit.py --sessions 5`): `Read` gọi 451 lần, **64,1% là
đọc lại file đã đọc trong cùng phiên**, trung vị 1.786 token mỗi lần. Con số đó KHÔNG
phải bằng chứng lãng phí: năm ca trên bắt buộc đọc lại, và phần lớn lần đọc lại rơi
đúng vào đó. Nó chỉ có nghĩa là chỗ này đáng phân biệt cho rõ.

Một lần đọc lại thuộc diện "vì QUÊN" khi **cả năm** điều dưới đây đúng — tức không
rơi vào ca nào trong năm ca bắt buộc:

- Context chưa bị nén kể từ lần đọc trước.
- Lần trước đã đọc TRỌN file, không `offset`/`limit`.
- Từ lần đọc đó tới giờ không ai chạm file: mình chưa sửa, không lệnh nào sinh lại nó,
  không sub-agent hay user nào đụng vào.
- Không sắp Edit chính file đó.
- Vẫn nhớ rõ đoạn cần, không cần chi tiết nào mà lần trước bỏ qua.

Ba dấu hiệu nhận ra nhanh nhất, cả ba đều là đọc lại vì quen tay:

- Đọc lại nguyên file chỉ để xác nhận MỘT dòng → `grep -n` trả lời đúng câu hỏi đó.
- Đọc lại ngay sau khi `Edit` báo thành công → `Edit` đã lỗi nếu không khớp, đọc lại
  không thêm thông tin nào.
- Đọc lại file mình vừa `Write` nguyên văn trong cùng phiên.

Sai số hai phía không cân nhau: bỏ một lần đọc CẦN thì suy luận trên nội dung cũ,
mất cả một vòng fix; đọc thừa một lần chỉ tốn 3,3 giây và một lần carry. Nên khi năm
điều kiện trên không chắc chắn đúng hết — **nghi ngờ thì đọc lại**.

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

Mỗi tool call = 1 API call = model đọc lại TOÀN BỘ context: một output tốn
`số token của nó × số API call còn lại sau nó` — **carry-cost**. Đo bằng
`token_audit.py` (đếm bằng tokenizer thật; ước lượng ký tự/4 lệch mạnh đúng ở nhóm
tốn nhất). Ảnh không tính theo độ dài base64 mà theo patch 28×28 px.

- **Lint đúng file.** Chạy `doc_lint.py` trên ĐÚNG file vừa sửa, cấm truyền cả thư mục
  (`docs/tdq`): lint thư mục in ~8.000 ký tự lỗi của file cũ, không liên quan.
- **CLI im lặng.** `tdq_state.py init|set|reset` mặc định in 1 dòng; chỉ thêm `--json`
  khi thật sự cần soi state. `next --brief` thay cho `next` trừ khi cần checklist đầy đủ.
- **Đọc vừa đủ.** File trên 200 dòng: `grep -n` định vị rồi Read theo `offset`/`limit`.
  Cấm `cat` (dùng Read), cấm `grep -A5 -B5` khi `-c`/`-l` đã đủ trả lời.
- **Việc nặng giao subagent.** Research web và đọc ≥4 file giao agent riêng — agent có
  context window riêng, chỉ trả digest về hội thoại chính.
- **Trần output cho tool ngoài (MCP).** Tool MCP là mã của bên thứ ba: TDQ không sửa
  được nội dung nó trả về, chỉ chặn được ở trần. Đặt `MAX_MCP_OUTPUT_TOKENS` trong
  `~/.claude/settings.json` (mặc định của Claude Code là 50.000, cảnh báo từ 10.000).
  Đo trên 5 phiên thật: mọi nhóm MCP hiện có đều dưới 8.800 token mỗi lần, cả cụm MCP
  chỉ chiếm **1,9%** tổng carry-cost. Trần này KHÔNG cắt chi phí đang có. Nó chặn ca
  hiếm khổng lồ trong tương lai — một lần gọi cũng đủ đội cả phiên.
  Vượt trần thì output bị cắt kèm dấu: thấy dấu cắt → gọi lại với tham số hẹp hơn
  (lọc, phân trang, chọn trường), cấm coi phần đọc được là đủ rồi kết luận.
- **Soul phân xử.** Mọi luật trên đây chỉ cắt chi phí khi đầu ra không đổi. Việc đòi đọc
  TRỌN nhiều file hay chạy đủ phép kiểm thì cứ làm đủ: chất lượng đứng trên context cost
  theo [soul.md](soul.md).
