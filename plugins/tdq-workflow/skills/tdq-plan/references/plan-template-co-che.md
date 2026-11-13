# How the plan's three conditional sections work
<!-- muc-luc-dong:
  Cụm song song — cách chia cho đúng=27-42 · Luật file nóng — nhận diện và hai cách xử=43-58 ·
  Khuôn khối hợp đồng skill — năm trường và nhãn `(mcp)`=59-79 ·
  Dòng `Chạm` — hai người đọc, và cái giá của việc thiếu nó=80-89 ·
  Dòng `Cần` — cách máy xếp đợt, và luật lùi=90
-->

The body below stays in Vietnamese ON PURPOSE. It is recorded here so it is not read as a
regression. At HEAD these sections sat INSIDE the `i18n-allow` fence of `plan-template.md`,
written in the language of the plan document they describe. This change only MOVED them.

Turning them into English belongs to the i18n workstream. That workstream locks every law it
rewrites through the `neo bản mới` column of `docs/tdq/audit/luat-hien-co.md`. Doing it here,
without that column, is how a law gets lost in translation.

Tách khỏi `plan-template.md` ngày 2026-10-02, có số đo: ba mục này cộng lại **1.831 token** trong
một file 5.067 token. Cả ba đều CÓ ĐIỀU KIỆN. `Cụm song song` chỉ cần nghĩ kỹ khi chạy mode đội;
`Luật file nóng` chỉ nổ khi một đường dẫn bị từ 2 task chạm; `Khuôn khối hợp đồng skill` chỉ dùng
khi task có gọi skill. Nạp cả ba vào mọi lần viết plan là trả tiền cho thứ phần lớn lượt không
dùng.

Khuôn mẫu (phần phải CHÉP vào plan) vẫn nằm ở `plan-template.md`; ở đây là phần GIẢI THÍCH, đọc
khi gặp đúng ca. Mỗi mục dưới đây là một mục trong khối chỉ mục dòng ở đầu file, nên lấy đúng một
mục bằng `offset/limit` được.

## Cụm song song — cách chia cho đúng

Mode `subagent` chia task thành từng đợt. Hai task cùng đợt chạy đồng thời ở hai worktree khác
nhau, nên chúng KHÔNG được đụng chung một file — git không hề cảnh báo, tới lúc merge mới vỡ. Máy
tự chia đợt từ dòng `Chạm:`, nhưng người viết plan mới là người biết ý đồ, nên hãy giúp máy chia
đúng:

- Gom task cùng chạm một file vào cùng một phase, đặt kề nhau, để thứ tự đọc ra được.
- Task phụ thuộc task khác thì nhắc mã task đó trong phần mô tả (vd "sau `T1.1`"). `assign` đọc
  mã này để giữ đúng thứ tự.
- Chia nhỏ theo FILE, đừng chia theo bước thời gian. "Viết `a.py`" + "viết test cho `a.py`" là
  một task; "viết `a.py`" + "viết `b.py`" là hai task chạy song song được.
- Ước lượng nhanh: đếm số task có `Chạm:` không giao nhau. Con số đó là trần tốc độ của mode đội.
  Đừng đoán bên nào thắng — chạy `simulate` ở bước 1 của [tdq-plan/SKILL.md](../SKILL.md) và lấy
  dòng `Winner:` làm đề xuất.

## Luật file nóng — nhận diện và hai cách xử

`assign` đếm số task khai mỗi đường dẫn ở dòng `Chạm:`; đường dẫn nào từ 2 task trở lên bị in ra
dưới nhãn `HOT FILE` kèm mã các task. Worktree KHÔNG cứu được loại file này: mọi nhánh đều phải
sửa nó, nên đợt nào cũng đụng nhau (nghiên cứu N3 của brief `2026-08-17`).

Cách nhận diện khi đang viết plan: file kiểu bảng đăng ký, `index`, `__init__`, `manifest`, bảng
hằng số — thứ mà "thêm một mục" là bước bắt buộc của nhiều task.

Hai cách xử lý, chọn một, không có cách thứ ba:

- **Nâng lên đợt sớm**: tách phần sửa chung thành MỘT task riêng, đặt ở phase trước; các task sau
  nhánh ra từ file đã ổn định. Đây là cách mặc định.
- **Một chủ ghi duy nhất**: nếu không tách được, để đúng MỘT task khai file đó ở `Chạm:`, các task
  còn lại không được chạm; ai cần thay đổi ở đó thì báo để gộp vào task chủ.

## Khuôn khối hợp đồng skill — năm trường và nhãn `(mcp)`

Khối hợp đồng đặt NGAY DƯỚI dòng task dùng skill đó, tối đa 6 dòng, đủ năm trường:

```markdown
- [ ] **T<x.y>** <việc của task> — Test: <...>
  - Dùng: `<tên skill>`
- [ ] **T<x.z>** <task mà skill cần MCP tool> — Test: <...>
  - Dùng: `<tên skill>` (mcp)
  - Để: <việc cụ thể skill lo trong task này>, nạp skill TRƯỚC bước đỏ. Agent ngoài
    không có skill system: đọc `<đường dẫn>/SKILL.md` rồi làm theo.
  - Ra: <artifact phải tồn tại sau task, có đường dẫn>
  - Kiểm: <một lệnh chạy được, PASS đo được>
  - Không dùng cho: <việc kề bên mà skill này KHÔNG được lan sang>
```

Luật nhãn `(mcp)` — BẮT BUỘC ghi ngay khi lập plan: skill nào cần MCP tool lúc chạy (gọi server
MCP, ví dụ tavily/notion) thì dòng `Dùng:` phải kết thúc bằng nhãn ` (mcp)` NGOÀI backtick, cuối
dòng, đúng cú pháp spec §1. `split-plan` đọc nhãn này để biết task nào buộc phải do Claude tự làm,
không giao cho sub-agent thiếu MCP.

## Dòng `Chạm` — hai người đọc, và cái giá của việc thiếu nó

Dòng này có HAI người đọc. Người thứ nhất là người viết plan: nó trả lời "sửa chỗ này thì vỡ chỗ
nào". Người thứ hai là máy: `scripts/tdq_team.py assign` đọc các đường dẫn trong backtick để dựng
vùng file của task, rồi xếp task đụng chung file vào hai đợt khác nhau.

Task thiếu dòng này sẽ bị `assign` xếp vào `tu_lam` với lý do `vung-khoa` — leader phải tự làm, và
mất chỗ chạy song song. Đó là lý do dòng `Chạm:` không phải thủ tục giấy tờ: thiếu nó là mất một
nhánh thi hành.

## Dòng `Cần` — cách máy xếp đợt, và luật lùi

Máy đọc dòng này để xếp đợt: task chỉ được phát khi mọi mã trong `Cần:` đã xong.

Plan KHÔNG khai `Cần:` ở bất kỳ task nào thì máy lùi về luật cũ — thứ tự phase là thứ tự phụ
thuộc. Luật lùi này giữ cho plan viết trước đây chạy y như cũ, nên không có plan nào vỡ vì cơ chế
`Cần:` ra đời sau nó.

Ví dụ phải khai: task gọi hàm mà task khác vừa viết; task sinh lại bản portable sau khi task khác
sửa skill.
