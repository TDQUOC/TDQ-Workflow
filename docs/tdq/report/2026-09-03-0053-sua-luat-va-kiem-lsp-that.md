# Báo cáo — Sửa luật thứ tự tìm kiếm và bắt kiểm LSP hoạt động thật

**Ngày:** 2026-09-03 · Lane: full · Plan: ../plan/2026-09-03-0053-sua-luat-va-kiem-lsp-that.md
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

Request này đóng lại lỗ hổng mà ba request trước phơi ra: thang `tdq_lsp.py kiem` báo **6/6 ĐẠT**
trong cả trạng thái độ phủ 7 % lẫn 100 %. Nó kiểm sự **tồn tại**, không kiểm **hiệu quả**.

## 1. Vấn đề — bằng chứng cụ thể

| Trạng thái | Thang báo | Độ phủ truy vấn quan hệ | Test |
|---|---|---|---|
| Trước khi có `pyrightconfig.json` | **6/6 ĐẠT**, thoát 0 | **1/15 file (7 %)** | xanh |
| Sau khi có `pyrightconfig.json` | **6/6 ĐẠT**, thoát 0 | **15/15 file (100 %)** | xanh |

Thang không phân biệt được hai cột. Không phép kiểm nào trong repo phân biệt được. Số đo lấy từ
báo cáo `2026-09-03-0017-them-pyrightconfig-do-lai.md`.

## 2. Luật thứ tự tìm kiếm — cũ và mới, đặt cạnh nhau

**Cũ:**

> Đối tượng tìm là ký hiệu code (hàm, class, biến, kiểu) → BẮT BUỘC gọi song song cả
> `mcp__lsp__*` và lumen, gộp kết quả hai lớp trước khi đọc; grep là lớp cuối.

**Mới:**

> Đối tượng tìm là ký hiệu code (hàm, class, biến, kiểu) → chọn lớp theo LOẠI truy vấn: quan
> hệ và đổi tên dùng `mcp__lsp__*`; tên chính xác đã biết dùng grep; khái niệm mơ hồ dùng
> lumen; chưa chắc thuộc loại nào thì gọi song song rồi gộp.

Bảng §2 của file luật gốc giờ mang số đo thật cho từng dòng, không còn dòng nào là ước lượng:

| Loại truy vấn | Lớp đầu tiên | Số đo |
|---|---|---|
| quan hệ, blast radius, đổi tên | `mcp__lsp__*` | LSP phủ 15/15 và 0 dương tính giả; grep cũng đủ 15 nhưng kéo thêm 6 file thừa — precision 67 % |
| tên chính xác đã biết token | grep | ~0,1 s so với 3–6 s của LSP, cả hai đều đủ 6/6 vị trí |
| khái niệm mơ hồ | lumen | LSP xếp đích hạng **13/62** — nó là chỉ mục TÊN, không hiểu khái niệm |
| chưa phân loại được | gọi song song, gộp | rẻ hơn chọn sai rồi tìm lại |

Đổi luật kéo theo 3 việc bắt buộc, đã làm đủ: 5 chỗ móc chép lại nguyên văn (test khớp-từng-chữ
khoá); §3 vòng đời Ollama sửa theo (lumen chỉ còn thức dậy ở truy vấn khái niệm mơ hồ hoặc chưa
phân loại được, không còn ở **mọi** truy vấn ký hiệu); và test khoá luật viết lại.

Test cũ `test_cau_goc_du_ba_lop` khoá **thứ tự chữ** `mcp__lsp__` < `lumen` < `grep`. Luật mới
không còn một thứ tự tuyến tính duy nhất nên test đó đỏ đúng như dự báo ở plan. Thay bằng phép
kiểm ánh xạ: đủ 3 lớp, và mỗi lớp phải nằm trong 60 ký tự quanh loại truy vấn nó phục vụ — cộng
một test mới khẳng định chuỗi "BẮT BUỘC gọi song song" đã biến mất.

## 3. Bậc 7 — kiểm cấu hình gốc import

Nền research (`docs/tdq/research/2026-09-03-0053-*.md`): mọi client LSP tìm gốc dự án bằng một
**root marker**, và các ngôn ngữ chia hai nhóm với mức nguy hiểm khác hẳn nhau.

| Nhóm | Ngôn ngữ | File mốc | Thiếu thì sao | Bậc 7 xử |
|---|---|---|---|---|
| **B** | Python, TS/JS, Lua, C/C++ | `pyrightconfig.json`, `tsconfig.json`, `.luarc.json`, `compile_commands.json` | dự án vẫn chạy, test vẫn xanh, chỉ mục liên file **chết âm thầm** | **CHẶN**, thoát 3 |
| **A** | Go, Rust, Java, Ruby, PHP, C#, Swift… | manifest build (`go.mod`, `Cargo.toml`…) | dự án **không build được**, tự lộ ngay | cảnh báo, thoát 0 |

Repo này sập đúng ở nhóm B. Ngoài ra CSS/HTML/YAML/JSON được khai danh sách mốc **rỗng** — chúng
không có đồ thị import nên không có gốc để cấu hình; rỗng nghĩa là "không áp dụng", không phải
"thiếu". Không có điều này, bậc 7 báo nhiễu "HTML thiếu package.json" trên chính repo này.

### Kịch bản quyết định — bậc 7 có bắt được lỗi thật không

Đây là phép kiểm duy nhất chứng minh bậc mới không lặp lại bệnh của 6 bậc cũ:

```
mv pyrightconfig.json /tmp/    → Tổng: 6/7 bậc ĐẠT · 1 bậc cần bạn cho phép cài   · thoát 3
mv /tmp/... trở lại            → Tổng: 7/7 bậc ĐẠT                                · thoát 0
```

Khi thiếu, bậc 7 in nội dung file cần tạo kèm câu xin phép và **không tự ghi file** — có test
riêng so danh sách file trong thư mục trước và sau lời gọi.

## 4. Bước kiểm bằng hiệu ứng thật

Bậc 7 bắt **nguyên nhân** đã biết. Nó không bắt được nguyên nhân chưa biết, nên intake có thêm
một bước kiểm **triệu chứng**, tài liệu ở `skills/tdq-intake/references/kiem-lsp-hieu-ung.md`:
chọn một hàm bất kỳ đang có trong repo và được gọi từ nhiều file, so `find_references` với `grep`
theo số **file phân biệt**, ĐẠT khi LSP ≥ grep. Không neo file/dòng cố định — neo cứng thì code
dịch chuyển là đỏ giả.

Ràng buộc kỹ thuật đã chốt từ phase analyze: `tdq_lsp.py` là script Python chạy ngoài agent nên
**không gọi được tool MCP**. Vì thế phần này là luật cho agent, không thể là bậc script.

## 5. Việc phát sinh — khai báo đủ

1. **`skills/tdq-lsp-setup/SKILL.md` vượt trần R6** sau khi thêm bậc 7 (127 > 120 dòng). Nén ba
   đoạn (§rung 6, §Ollama, hai dòng cuối) về dưới trần. Task T1.5, không có trong plan gốc.
2. **Hai test đỏ MỚI ngoài mốc 101** do chính thay đổi của tôi: `test_intake_shape`
   (tdq-intake 137 > 120 dòng) và `test_skill_descriptions_total` (1622 > 1620 ký tự). Task T4.3.
   Cách sửa: tách nội dung phép kiểm hiệu ứng ra file `references/` riêng và rút gọn hai câu dài
   ở Part A — đúng khuôn `references/` mà skill này vốn dùng, không phải cắt bớt nội dung.
3. **Tôi gọi sai `tdq_checkportable.py`** — nó cần lệnh con và `--root`. Tôi kết luận nhầm là
   "không chạy được từ gốc repo" rồi thay bằng phép đếm grep. QC chỉ ra dạng đúng
   `check --root <bundle>`; chạy thế thì cả 3 bundle `CLEAN 91/140/84 file(s) match`.
4. **Phase `diagram` trong spec đã duyệt không tồn tại.** Spec §1b ghi `diagram | CÓ`, nhưng phase
   đó bị gỡ ngày 2026-09-01 và `skills/tdq-diagram/` đã bị xoá; tôi viết theo bản skill cũ còn
   trong context. Đầu ra số 9 (sơ đồ) của spec §2 vì thế BỎ. Spec đã niêm sha256 nên sai lệch ghi
   ở plan chứ không sửa ngược vào spec.

## 6. Kết quả

| Hạng mục | Trước | Sau |
|---|---|---|
| Số bậc của thang | 6 | 7 |
| Thang trên repo này | 6/6 ĐẠT, thoát 0 | 7/7 ĐẠT, thoát 0 |
| Thang khi thiếu `pyrightconfig.json` | **6/6 ĐẠT, thoát 0** | **6/7, thoát 3** |
| Luật thứ tự tìm kiếm | một thứ tự cứng cho mọi truy vấn | 4 loại truy vấn, mỗi loại một lớp đầu, có số đo |
| Kiểm bằng hiệu ứng | không có | bước bắt buộc ở intake, bỏ qua là lỗi QC |

Toàn bộ test: **100 failed / 1461 passed** so với mốc nền **101 failed / 1453 passed**. Thêm 8 test
mới (6 cho bậc 7, 2 cho luật) đều xanh.

Đối chiếu danh sách đỏ giữa lần chạy giữa chừng (103 đỏ) và lần chạy cuối: **0 test đỏ mới**, 3
test chuyển từ đỏ sang xanh — `test_intake_shape` và `test_skill_descriptions_total` (hai lỗi do
chính tôi gây ra, đã sửa ở T4.3) cùng `test_doc_lint::test_repo_docs_clean` (đỏ vì tài liệu đang
sửa dở, nay `doc_lint` toàn repo thoát 0).

## 7. Vòng QC

QC độc lập chấm Q1–Q6, Q8, Q10 PASS; Q7 và Q9 FAIL **ở câu lệnh DoD** chứ không ở nội dung, đã
sửa hai dòng. Nó cũng tìm ra một lỗi code thật mà test của chính tôi không bắt: ở bậc 7,
`thieu = thieu_b or thieu_a` khiến khi thiếu CẢ nhóm B lẫn nhóm A, phần chi tiết chỉ in nhóm B —
người đọc sửa xong `pyrightconfig.json` vẫn không biết `go.mod` cũng thiếu. Đã đổi thành
`thieu_b + thieu_a` (mức nghiêm trọng vẫn do nhóm B quyết định) kèm test mới
`test_thieu_ca_hai_nhom_thi_chi_tiet_liet_ke_ca_hai`. `tests/test_tdq_lsp.py` 37 xanh, thang vẫn
7/7 ĐẠT thoát 0, 3 bundle dựng lại và `CLEAN`.

Bài học: 6 test của tôi đều đi qua một nhóm mỗi lần, nên nhánh "cả hai cùng thiếu" chưa bao giờ
được chạy — đúng loại lỗ mà QC độc lập sinh ra để bịt.
