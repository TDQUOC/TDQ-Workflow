# BRIEF — Tối ưu thời gian xử lý các phase của workflow

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## Nguyên văn

> hiện tại sau khi chạy thử version mới của workflow tôi gặp một hiện trạng là thời gian
> process, implement request có vẻ hơi lâu cho tất cả các phase như ở project
> Heineken_Appketnoi tôi muốn bạn check lại workflow xem có cách nào giữ soul, rule,
> behavior nhưng tối ưu hơn thời gian để claude code xử lí các phase của request mà vẫn
> giữ đầy đủ chất lượng output không?

**Cách hiểu đầu tiên**

- Mục tiêu: giảm thời gian thực (wall-clock) từ lúc user nhắn tới lúc có kết quả, ở MỌI
  phase của request — không chỉ implement.
- Ràng buộc cứng user nêu: giữ nguyên soul (3 tầng ưu tiên), giữ nguyên rule, giữ nguyên
  behavior, giữ nguyên chất lượng output. Tức là cắt chi phí thi hành, KHÔNG cắt luật.
- Bối cảnh quan sát: chạy bản 0.18.0 ở project ngoài `Heineken_Appketnoi` — không phải ở
  chính kho workflow này. Vậy mọi phép đo phải làm ở điều kiện project ngoài.

**Phạm vi đoán (chưa xác nhận)**

- Nguồn tốn thời gian nghi ngờ, xếp theo mức nghi: số vòng gate chờ user · lượng token
  phải nạp mỗi turn (6 SKILL.md = 27.462 ký tự, cộng file reference nạp thêm) · 5 hook
  chạy mỗi lần (SessionStart, UserPromptSubmit, 2 PreToolUse, Stop) · graphify chạy cuối
  turn trên kho lớn · số lần chạy full test suite.
- Chưa rõ user thấy chậm ở khâu nào nhất: chờ Claude "nghĩ", chờ lệnh chạy, hay chờ
  chính mình phải trả lời gate.

**Chỗ chưa rõ (phải hỏi)**

1. Phase nào chậm nhất theo cảm nhận, và mức chấp nhận được là bao nhiêu?
2. Có được phép giảm số gate chờ user không, hay gate là phần "behavior" phải giữ nguyên?
3. Có được đo trực tiếp trên `Heineken_Appketnoi` không (đọc log/transcript ở đó)?

## Hiểu & kiến thức

### Năng lực dùng được

| Năng lực | Nguồn | Phán quyết | Vì sao |
|---|---|---|---|
| `tdq-conventions` | plugin:tdq-workflow | DÙNG | chứa `context-budget.md` — chính là chỗ phải sửa |
| `tdq-intake` / `tdq-spec` / `tdq-plan` / `tdq-build` | plugin:tdq-workflow | DÙNG | mỗi skill là một phase cần cắt bước |
| `tdq-status` | plugin:tdq-workflow | BỎ | chỉ báo trạng thái, không nằm trên đường đi của request |
| `scripts/token_audit.py` | project | DÙNG | đã dùng để đo carry-cost thật ở Heineken |
| `superpowers:*`, `code-simplifier`, `graphify` | plugin ngoài | BỎ | việc này là sửa luật văn bản, không phải refactor code |

### Đo thật — nguồn: transcript phiên `0a2b58a3` của `Heineken_AppKetNoi` (131,5 MB)

| Chỉ số | Giá trị đo được |
|---|---|
| Số bước model (API call có usage) | 4.809 |
| Độ trễ mỗi bước | trung vị **3,3 s** · p90 12,3 s |
| Tổng thời gian model chạy | **7,6 giờ** trong một phiên kéo dài 2 ngày 14 giờ |
| Context mỗi turn | trung vị 129.709 token · p90 163k · max 267k |
| Tool call / assistant message | **1,00** (3.095 lượt, không lượt nào gộp) |
| Read lặp lại cùng file | 103 / 278 lượt (20 lần cho `RfidUdpReceiver.cs`) |
| Ảnh base64 trong tool result | 136 tấm = 44,4 MB = **93%** khối lượng tool result |
| Chi phí 6 SKILL.md nạp mỗi turn | 27.462 ký tự ≈ 6.900 token ≈ **5%** context một turn |

**Đính chính 2026-08-15 (phase implement).** Hai dòng in đậm ở trên đếm theo BẢN GHI
jsonl. Claude Code tách một câu trả lời thành nhiều bản ghi và chép `usage` vào từng bản,
nên cách đếm này thổi phồng số bước và luôn ra đúng 1,00 tool call mỗi lượt bất kể model
có gộp hay không. Đo lại cùng transcript bằng `scripts/step_audit.py` (gom theo
`requestId`): **3.234 bước · 1,03 tool call mỗi lượt trên 3.085 lượt · 114 Read lặp**.
Hướng kết luận không đổi — 1,03 nghĩa là ~97% số lượt chỉ phát một tool call — nhưng con
số đúng là 1,03, không phải 1,00 tuyệt đối.

### Kết luận nhân quả (thứ tự theo mức đóng góp)

1. **Số bước là biến chính, không phải kích thước context.** Độ trễ theo bậc context:
   80k → 3,0 s · 120k → 3,4 s · 160k → 3,9 s · 240k → 5,1 s. Context tăng 3 lần chỉ làm
   chậm thêm ~70%, trong khi tổng thời gian tỉ lệ THẲNG với 4.809 bước. Cắt 30% số bước
   tiết kiệm nhiều gấp bội cắt 30% context.
2. **Không có lượt gọi tool song song nào.** Tỉ lệ 1,00 tool/message trên 3.095 lượt là
   bằng chứng luật gộp hiện có không được thi hành lần nào. Mỗi tool call = một vòng
   round-trip ≈ 3,3 s.
3. **Vì sao luật gộp bị bỏ:** nó nằm ở `context-budget.md` — file reference ít khi nạp —
   và được đóng khung là "tiết kiệm context", mà soul xếp context cost ở tầng THẤP NHẤT.
   Đọc đúng soul thì bỏ qua luật này là hợp lệ. Đây là lỗi phân tầng, không phải lỗi ý
   thức: gộp tool call thực chất là **runtime** (tầng 2), phải nói ở tầng đó.
4. **Ảnh chiếm 93% tool result** nhưng ảnh hưởng gián tiếp (đẩy context lên 130k), nên
   theo mục 1 thì đây là ưu tiên sau, không phải trước.
5. **Chi phí luật TDQ chỉ ~5% context/turn.** Cắt chữ trong SKILL.md gần như không đổi
   được gì về thời gian — đây là lý do KHÔNG nên cắt luật, đúng ý ràng buộc của user.
6. Lỗi phụ phát hiện khi đo: `token_audit.py` suy thư mục transcript sai khi tên project
   có dấu `_` (Claude Code đổi `_` thành `-`), phải truyền tay `--transcript-dir`.

### Phạm vi đã chốt

- Mặt CHỌN: hiệu năng · bảo trì · độ tin cậy
- Mặt LOẠI: "chỉ cần chạy được" (làm nhanh cho xong) — chép sang spec §1 NGOÀI phạm vi
- Bối cảnh: áp cho MỌI project dùng workflow, Heineken chỉ là ca đo mẫu; không đặt
  ngưỡng phần trăm, đích là sửa đúng chỗ hở đã đo được
- Mức đầu tư suy ra: **vừa** — vì bộ luật này cả nhóm dùng hằng ngày (cần test biên và
  đường lỗi), nhưng user đã bỏ mốc số nên không dựng hạng mục QC theo ngưỡng %

### Quyết định đã chốt (và vì sao)

1. **Không cắt một chữ luật nào.** Đo cho thấy 6 SKILL.md chỉ chiếm ~5% context/turn và
   độ trễ gần như không theo context — cắt luật tốn công mà không đổi thời gian, lại phá
   đúng thứ user muốn giữ.
2. **Đòn bẩy chính: nâng luật gộp tool call từ tầng 3 lên tầng 2.** Soul giữ nguyên ba
   tầng; chỉ nói rõ gộp tool call thuộc **runtime**, không phải context cost. Đây là sửa
   chỗ phân loại sai, không phải sửa soul.
3. **Chuyển luật ra tầng luôn nạp.** Luật nằm ở `context-budget.md` (reference ít nạp) là
   lý do kỹ thuật khiến nó vô hình; đưa bản rút gọn vào thân `tdq-conventions/SKILL.md`.
4. **Trả thêm context để mua lại số bước là ĐÚNG soul.** Trần "+200 token" chỉ là một dòng
   DoD của request 2026-08-14, không phải luật thường trực (không test nào khoá) — nên
   không coi nó là ràng buộc ở đây, nhưng vẫn viết ngắn nhất có thể.
5. **Hàng rào chất lượng (mặt độ tin cậy).** Luật gộp phải kèm danh sách chỗ CẤM gộp:
   bước đỏ→xanh phải chạy riêng để thấy đỏ thật, lệnh cần khoanh vùng lỗi, lệnh phá hủy,
   và không được bỏ bất kỳ phép kiểm nào để lấy tốc độ.
6. **Đo được thì mới nói là nhanh hơn.** Thêm `scripts/step_audit.py` đo từ transcript:
   số bước, tool/message, số Read lặp, độ trễ trung vị — dùng chính nó làm bằng chứng QC.
7. **Sửa luôn lỗi đo sai đường dẫn** của `token_audit.py` với tên project có dấu `_`,
   vì nếu không thì chính công cụ đo của workflow không dùng được ở Heineken.
8. **Không thêm hook chặn.** Máy không phân biệt được hai tool call độc lập với hai tool
   call phụ thuộc nhau, hook sẽ báo oan và làm chậm thêm; chọn đo + luật ở tầng luôn nạp.

### Phương án đã loại

- Cắt bớt gate duyệt: user chọn 3C (giữ nguyên behavior), và gate là thứ giữ chất lượng.
- Nén/cắt SKILL.md: đo cho thấy vô ích (mục 1).
- Chặn ảnh base64 vào context: ảnh chiếm 93% tool result nhưng chỉ tác động gián tiếp qua
  context, mà context lại gần như không đổi độ trễ — ưu tiên thấp, để lần sau.

### Lộ trình

| Bước/phase | CÓ-BỎ | Vì sao |
|---|---|---|
| Research web | BỎ | thuần nội bộ, kết luận lấy từ transcript thật, không có ẩn số ngoài |
| Vòng scope | CÓ | đã chạy, user chốt 1ABC · 2A · 3C · 4A |
| Spec + plan | CÓ | khung bất biến |
| Chia subagent | BỎ | 6 file nhỏ, phụ thuộc lẫn nhau, chia ra tốn thêm bước — trái mục tiêu |
| QC độc lập bằng agent | BỎ | mọi hạng mục kiểm được bằng lệnh; gọi agent tốn thêm bước |
| Implement | CÓ | khung bất biến |
| QC chính + report | CÓ | khung bất biến |

## Hỏi đáp

**Vòng scope — 2026-08-15 10:43**

1. Mặt bao quanh → user: **"1abc"** = hiệu năng + bảo trì + độ tin cậy (loại D).
2. Bối cảnh → user: **"2a"** = mọi project dùng workflow, Heineken là ca đo mẫu.
3. Mốc số bước → user: **"3c"** = không đặt mốc số, chỉ sửa đúng chỗ hở đã tìm ra.
   Hệ quả: QC không có hạng mục ngưỡng %, thay bằng bằng chứng đo trước/sau.
4. Bổ sung thêm → user: **"4a"** = không, làm tiếp.

Vòng chi tiết: BỎ — sau vòng scope không còn câu nào mà đáp án khác nhau làm đổi sản
phẩm; các quyết định còn lại là việc chuyên môn của tôi, đã ghi ở mục trên.
