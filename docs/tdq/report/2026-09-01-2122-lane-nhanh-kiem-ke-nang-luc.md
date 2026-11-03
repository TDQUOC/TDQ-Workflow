# REPORT — giá của kiểm kê năng lực + đọc code + research trong lane nhanh

Ngày: 2026-09-01 · Plan: ../plan/2026-09-01-2122-lane-nhanh-kiem-ke-nang-luc.md · Lane: quick
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

Câu hỏi: bê ba bước nặng của pha `analyze` lane chuyên sâu — B0 kiểm kê năng lực, B1 đọc
code, B2 research nhiều hướng — sang lane nhanh thì trả giá bao nhiêu, được lại bao nhiêu.
Số thời gian dưới đây lấy từ `docs/tdq/timing.jsonl` (43 request đã đóng sổ), không ước đoán.

## 1. Ba bước đó thật ra làm gì

| Bước | Nguồn luật | Sản phẩm phải đẻ ra |
|---|---|---|
| B0 kiểm kê năng lực | `skills/tdq-intake/references/analyze-full.md:8` | Bảng phán quyết từng skill vào mục `### Năng lực dùng được` của brief; luật "nghi ngờ thì DÙNG" |
| B1 đọc code | `analyze-full.md:16` | Điểm vào, luồng dữ liệu, config, test, phiên bản; bắt buộc gọi song song LSP + lumen, grep là lớp cuối; đọc/dựng `docs/kien-truc.md` |
| B2 research nhiều hướng | `analyze-full.md:47` | 2–4 truy vấn khác góc qua `tavily-primary`, giao subagent, subagent tự ghi `docs/tdq/research/<slug>.md` và chỉ trả về digest ≤ 1.500 ký tự |

Ba bước này hiện lane nhanh KHÔNG bỏ hẳn: bước 1 của `quick-lane.md:38` vẫn buộc "đọc đúng
phần code liên quan" và vẫn buộc search khi có ẩn số ngoài. Cái lane nhanh thực sự bỏ là
**hình thức bắt buộc**: không bảng kiểm kê, không file research riêng, không `kien-truc.md`.

## 2. Số đo thật

`model_giay` = thời gian model thực sự chạy; `treo_tuong_giay` = đồng hồ treo tường, gồm cả
lúc chờ user nên không dùng để so.

| Đại lượng | n | Trung vị | Nhỏ nhất | Lớn nhất |
|---|---|---|---|---|
| Pha `analyze` lane chuyên sâu | 29 | **372 s** | 0 s | 979 s |
| Tổng một request lane nhanh | 13 | **533 s** | 155 s | 1200 s |
| Tổng một request lane chuyên sâu | 30 | **3409 s** | — | — |

Đây là con số then chốt: **372 s / 533 s ≈ +70 %**. Bê nguyên pha `analyze` vào lane nhanh
thì một request lane nhanh trung vị dài thêm khoảng hai phần ba, từ ~9 phút lên ~15 phút.

## 3. Giá theo từng bước, ba thước

Lưu ý về độ tin: `timing.jsonl` đo theo PHA, không đo theo bước, nên 372 s là số đo thật của
cả pha; cột thời gian từng bước dưới đây là ước lượng chia theo khối lượng sản phẩm mỗi bước
(bảng kiểm kê, phần đọc code, file research) — nói rõ để không nhầm là số đo.

| Bước | Thời gian (ước, trong 372 s) | Context tiêu tốn | Lượt user phải trả lời |
|---|---|---|---|
| B0 kiểm kê năng lực | ~40–60 s | 9 dòng bảng lọc (`--loc`) hoặc 223 dòng nếu `--tat-ca`; bản thân script chỉ 0,08 s | 0 |
| B1 đọc code | ~180–220 s | Nặng nhất: hai lớp LSP + lumen cùng đổ kết quả, cộng `kien-truc.md` | 0 |
| B2 research | ~80–120 s | Nhẹ nếu đúng luật (digest ≤ 1.500 ký tự); file research trung vị 69 dòng nằm trên đĩa, không vào context | 0 |

Điểm đáng chú ý ở cột thứ ba: **cả ba bước đều tốn 0 lượt trả lời của bạn.** Cái ngốn lượt
là bước B4 interview, không nằm trong ba bước bạn hỏi. Nghĩa là ba bước này không làm lane
nhanh "phiền" hơn — chúng chỉ làm nó chậm hơn và tốn context hơn.

Về context, B2 là bước có bẫy lớn nhất và đã có rào: `analyze-full.md:53` ghi rằng để kết quả
tavily thô nằm lại trong context tốn ~14 triệu token mỗi 2 phiên — đó là lý do luật bắt giao
subagent. Làm đúng luật thì B2 rẻ; làm sai luật thì B2 đắt hơn cả hai bước kia cộng lại.

## 4. Cân trọn gói cả ba bước

**Giá:** +372 s model mỗi request (+70 % thời gian), context tăng chủ yếu do B1, và lane nhanh
phải sinh thêm ít nhất hai file (`brief` có bảng kiểm kê, `research/<slug>.md`). Brief lane
chuyên sâu trung vị 107 dòng — so với mini-plan lane nhanh 52 dòng, tức tài liệu gấp đôi.

**Được:** B1 là bước trả lại giá trị rõ nhất và đo được. Chính request 2103 vừa rồi cho thấy:
nếu không đọc kỹ, sẽ không phát hiện `phase_key` nuốt pha thật của lane quick — và cả phương
án sẽ sai chỗ. Trước đó, request gỡ pha sơ đồ có một lỗ hổng cổng `plan` chỉ lộ ra vì đọc
`git show HEAD:scripts/tdq_state.py`. Đó là hai lần B1 cứu bài trong hai request gần nhất.

B0 và B2 thì khác. B0 chống được đúng một dạng lỗi: quên mất đã có sẵn skill/script làm việc
đó rồi. Với repo này — 223 skill nhưng phần lớn request chỉ đụng `tdq-*` — bảng lọc ra 9 dòng
và câu trả lời gần như luôn giống nhau. B2 chỉ có giá khi có ẩn số ngoài; các request gần đây
đều thuần nội bộ nên B2 sẽ tự bỏ theo đúng điều kiện `analyze-full.md:56`.

Nói thẳng: **bê cả ba là mua đắt.** Giá gần như toàn bộ nằm ở B1 và phần lớn giá trị cũng nằm
ở B1; B0 và B2 cộng vào ~120–180 s để chống hai dạng lỗi hiếm với repo này.

## 5. Đề xuất, kèm ngưỡng

Lấy **B1 bắt buộc, B0 và B2 có điều kiện** — chứ không lấy trọn gói:

- **B1 đọc code — LUÔN LUÔN.** Thật ra `quick-lane.md:38` đã buộc rồi; việc cần làm chỉ là
  nói rõ "đọc code" nghĩa là gọi song song LSP + lumen như lane chuyên sâu, chứ không phải
  grep một phát rồi viết. Giá thêm gần bằng 0 vì bước này vốn đã có.
- **B0 kiểm kê — chỉ khi request đụng vùng chưa có tiền lệ**, tức không có file nào trong
  `docs/tdq/report/` từng chạm cùng thư mục. Đụng lại `scripts/tdq_state.py` hay `hooks/` thì
  bỏ, vì câu trả lời đã biết.
- **B2 research — chỉ khi có ẩn số ngoài** (thư viện, API, phiên bản, hành vi công cụ bên
  thứ ba). Đây đúng là điều kiện lane nhanh đang ghi; giữ nguyên, không siết thêm.

Với ngưỡng này, request lane nhanh điển hình của repo — thuần nội bộ, đụng vùng đã quen — tốn
thêm gần như 0 s, và request lạ mới trả 372 s. Lane nhanh vẫn nhanh ở chỗ nó cần nhanh.

Nếu bạn muốn ngược lại — bắt cả ba bước không điều kiện — thì lane nhanh trung vị thành ~15
phút, tức bằng khoảng một phần tư lane chuyên sâu (3409 s), và câu hỏi thật sự sẽ là còn giữ
hai lane làm gì.
