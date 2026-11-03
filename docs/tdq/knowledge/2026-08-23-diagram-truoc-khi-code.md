# Dựng diagram giải thuật trước khi code — phân tích và đề xuất

Ngày: 2026-08-23 · Request: `2026-08-23-1125-diagram-giai-thuat-mind-map`
Spec: ../spec/2026-08-23-1125-diagram-giai-thuat-mind-map.md · Research: ../research/2026-08-23-1125-diagram-giai-thuat-mind-map.md
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

Sáu mục đánh số dưới đây trả lời đúng sáu câu user hỏi. Mọi đoạn mở đầu bằng `**Kết luận:**` đều kèm URL nguồn, hoặc chữ `suy luận` khi đó là lập luận chứ không phải số đo.

## Lược đồ dữ liệu

Một tính năng = một file JSON. Cây tổng của project = thư mục các file đó, cộng một file
`cay-tong.json` chỉ giữ quan hệ cha con giữa các nhánh.

Lược đồ cố ý tách làm hai phần. Phần `buoc` là **giải thuật**, dành cho người đọc và người duyệt. Phần `code` bên trong mỗi bước là **ánh xạ**, máy đối chiếu được với mã nguồn thật. Ranh giới này quyết định cả phương án: cái gì máy kiểm được thì máy kiểm, phần còn lại người lo.

| Trường | Kiểu | Bắt buộc | Nghĩa |
|---|---|---|---|
| `phien_ban` | chuỗi | có | bản của chính lược đồ, để đổi lược đồ sau này không vỡ file cũ |
| `tinh_nang` | chuỗi | có | tên tính năng, trùng tên file, là khoá nối vào `cay-tong.json` |
| `thuoc_nhanh` | chuỗi | có | vị trí trong cây tổng, ví dụ `Xác thực > Đăng nhập` |
| `cap_nhat` | chuỗi | có | ngày sửa gần nhất, dùng để phát hiện diagram bỏ hoang |
| `buoc` | mảng | có | các bước giải thuật, thứ tự trong mảng là thứ tự kể chuyện |
| `buoc[].ma` | chuỗi | có | mã bước, ví dụ `B3`, để bước khác trỏ tới |
| `buoc[].ten` | chuỗi | có | tên bước bằng ngôn ngữ nghiệp vụ, cấm dùng tên hàm |
| `buoc[].phia` | chuỗi | có | `client`, `server`, hay `chung` |
| `buoc[].tiep` | mảng | có | mã các bước đi tiếp, nhiều phần tử nghĩa là rẽ nhánh |
| `buoc[].loi` | mảng | không | các ca lỗi: `khi` là điều kiện, `xu_ly` là cách xử lý |
| `buoc[].code` | mảng | không | ánh xạ sang mã nguồn; rỗng nghĩa là bước chưa được code |
| `buoc[].code[].file` | chuỗi | có | đường dẫn thật tính từ gốc repo |
| `buoc[].code[].ham` | chuỗi | có | tên hàm, là thứ máy tra bằng LSP để biết còn tồn tại không |
| `buoc[].code[].module` | chuỗi | không | module hay helper mà hàm đó thuộc về |

Ba trường cuối là toàn bộ lý do lược đồ này khác một bản vẽ thường: chúng biến diagram từ
tài liệu chết thành thứ có thể kiểm bằng lệnh.

## Ví dụ: luồng login

Ví dụ dưới đây là **hư cấu minh hoạ** cho một project web giả định, không phải code của repo
này; tên file và tên hàm đặt theo lối thường gặp, không phải để tra cứu.

### Lớp 1 — giải thuật

Chỉ nghiệp vụ, không một tên hàm nào. Đây là lớp duy nhất user và người duyệt cần đọc.

```
B1 nhập email + mật khẩu
 └─ B2 kiểm tra tại chỗ (email đúng khuôn, mật khẩu ≥ 6 ký tự)
     ├─ sai → B2E hiện lỗi ngay dưới ô nhập, dừng
     └─ đúng → B3 gửi yêu cầu đăng nhập qua kênh mã hoá
         └─ B4 server tra người dùng theo email
             ├─ không có, hoặc mật khẩu băm không khớp → B4E trả lỗi chung "sai thông tin"
             └─ khớp → B5 phát token phiên + token làm mới
                 └─ B6 client lưu token, chuyển sang màn hình chính
```

Một chi tiết cố ý: B4E trả **một** thông báo chung cho cả hai ca sai. Đó là quyết định an
toàn, và nó nhìn thấy được ngay trên sơ đồ — điều rất khó thấy khi đọc code rải rác.

### Lớp 2 — function flow phía client

| Bước | Hàm | File | Module |
|---|---|---|---|
| B1 | `LoginForm.onSubmit` | `src/pages/login.tsx` | `pages` |
| B2 | `validateCredentials` | `src/lib/validators.ts` | `helper` |
| B2E | `showFieldError` | `src/lib/form-ui.ts` | `helper` |
| B3 | `authApi.login` | `src/api/auth.ts` | `api` |
| B6 | `session.persist` | `src/store/session.ts` | `store` |

### Lớp 3 — function flow phía server

| Bước | Hàm | File | Module |
|---|---|---|---|
| B4 | `AuthController.login` | `server/controllers/auth.py` | `controller` |
| B4 | `UserRepo.find_by_email` | `server/repo/user.py` | `repo` |
| B4E | `deny_login` | `server/controllers/auth.py` | `controller` |
| B5 | `TokenService.issue_pair` | `server/services/token.py` | `service` |

Hai bảng này là phần máy đối chiếu được: mỗi cặp file + hàm đem hỏi LSP, hàm biến mất thì
diagram bị đánh dấu lệch. Đây là chỗ diagram tự bảo vệ mình khỏi việc trở nên lỗi thời.

### Lớp 4 — vị trí trong cây tổng

```
Project ├─ Xác thực ├─ Đăng nhập ← luồng đang xem
        │           ├─ Đăng ký · └─ Quên mật khẩu
        ├─ Hồ sơ người dùng · └─ Thanh toán
```

Cây tổng chỉ giữ tên tính năng, không giữ bước. Nhờ vậy nó vẫn đọc được khi project có năm
mươi tính năng, và mở một nhánh đưa người đọc xuống đúng file JSON của nhánh đó.

## 1. Ý tưởng có giúp dev kiểm soát project không

Vấn đề user mô tả — code do AI sinh, dev không nắm giải thuật — là vấn đề đọc hiểu, không
phải vấn đề gõ phím. Đo được: dev dành khoảng 58% thời gian chỉ để đọc hiểu code (Xia et al.
2018, dẫn qua https://magazine.swissinformatics.org/en/the-curious-case-of-software-documentation).
Tài liệu thiết kế gắn kèm code làm việc đọc hiểu nhanh hơn trong thí nghiệm có đối chứng
(https://web.eecs.umich.edu/~weimerw/p/weimer-icpc2020.pdf).

Nhưng cùng lúc có một con số ngược chiều: khoảng 60% tài liệu lỗi thời trong sáu tháng nếu
không có cơ chế đồng bộ (https://document360.com/blog/documentation-drift), và tài liệu lỗi
thời hại hơn không có tài liệu vì nó dẫn người đọc đi sai
(https://fabric.so/blog/outdated-docs-are-worse-than-no-docs).

**Kết luận:** có giúp, nhưng lợi ích không đến từ việc vẽ, mà từ việc giữ bản vẽ đúng. Một diagram không có cơ chế kiểm tự động sẽ rơi vào nhóm 60% kia (https://document360.com/blog/documentation-drift). Đó là lý do lược đồ ở trên tách riêng trường `code[].file` và `code[].ham` — chúng là chỗ duy nhất máy phát hiện được diagram đã lệch khỏi code.

## 2. Có giúp Claude Code xử lý dự án lớn hơn không

Có bằng chứng thực nghiệm cho việc đưa cấu trúc code dạng graph cho agent. LocAgent cải thiện
độ chính xác định vị code và tỉ lệ sửa được issue (https://arxiv.org/html/2503.09089v1).
Prometheus cho kết quả tương tự bằng knowledge graph đa ngôn ngữ
(https://arxiv.org/html/2507.19942v1). Aider dùng repo map dựng từ AST thay cho RAG
(https://aider.chat/docs/repomap.html).

Phải nói rõ một khoảng cách: cả ba dùng graph SINH TỰ ĐỘNG từ code, còn thứ user muốn là
diagram nghiệp vụ VIẾT TAY. Không tìm được nghiên cứu định lượng cho loại thứ hai.

**Kết luận:** giúp, nhưng phần chắc chắn giúp là lớp ánh xạ hàm — nó cho agent một điểm vào
đúng thay vì quét cả repo (https://arxiv.org/html/2503.09089v1). Phần lớp giải thuật giúp
theo kiểu khác: nó cho agent biết ý ĐỊNH, thứ không suy ra được từ code, nên tránh được sửa
đúng cú pháp mà sai nghiệp vụ. Phần này là `suy luận`, chưa có số đo.

## 3. Có nên thêm vào tdq-workflow không

> Kết luận mục 3, mục 4 và mục 6 bên dưới là bản v1, đã bị user bác một phần ngày
> 2026-08-23. Bản đang có hiệu lực nằm ở mục `Bản sửa đổi v2` cuối tài liệu.

Workflow này đã có `graphify` sinh graph cấu trúc code, và có LSP trả lời quan hệ hàm. Cả
hai đều nói về code ĐANG CÓ. Không có thứ gì trong repo mô tả GIẢI THUẬT dự định — đó là một
khoảng trống thật, không phải việc trùng lặp.

Mô hình gần nhất đã có người làm: GitHub Spec Kit và Amazon Kiro đều chèn một bước thiết kế
có người duyệt trước khi sinh code (https://arxiv.org/html/2602.00180v1). Workflow này đã có
sẵn hai cổng duyệt spec và plan, nên hạ tầng duyệt không phải dựng mới.

**Kết luận:** nên thêm, nhưng thêm dưới dạng một MỤC trong tài liệu đã có, không phải một
phase mới. Lý do là chi phí cổng duyệt: mỗi phase mới đẻ thêm một lượt chờ user, mà mô hình
spec-kit cho thấy giá trị nằm ở chỗ có người duyệt thiết kế, không nằm ở số cổng
(https://arxiv.org/html/2602.00180v1).

## 4. Nếu nên thì chèn vào đâu

Chèn tách làm hai chỗ, đúng theo hai lớp của lược đồ:

| Lớp | Chèn vào | Ai viết | Vì sao chỗ đó |
|---|---|---|---|
| Giải thuật | mục mới `§2c Sơ đồ giải thuật` của spec | Claude, user duyệt | spec là chỗ chốt ý định, và nó đã có cổng duyệt |
| Function flow | dòng `Chạm:` sẵn có của plan | Claude | plan vốn đã liệt kê file mỗi task đụng |
| Cây tổng | `docs/tdq/mind-map/` sau khi build | script sinh | chỉ đúng khi code đã tồn tại |

Cách này đáp ứng đúng điều user muốn — giải thuật chốt TRƯỚC khi lên plan — mà không đẻ thêm
cổng duyệt nào. Lớp function flow gần như miễn phí vì plan đã ghi `Chạm:` cho mỗi task rồi.

### Cái giá phải trả

Ba cái giá, nói thẳng:

1. **Spec dài thêm.** Mỗi request tốn thêm một mục sơ đồ, ước chừng 15–30 dòng. Với request
   tầng `nhỏ` đó là chi phí thuần, không lợi ích. Giảm bằng cách chỉ bắt buộc ở lane `full`.
2. **Một lượt duyệt nặng hơn.** User phải đọc thêm sơ đồ trước khi gõ "duyệt spec". Nếu user
   duyệt cho xong thì cả bước này thành lễ nghi, và lễ nghi thì tệ hơn không làm.
3. **Nguy cơ lệch giữa spec và code.** Spec đã duyệt bị niêm sha, code thì đổi tiếp. Sơ đồ
   trong spec sẽ cũ dần. Đây là chi phí thật, chỉ giảm được bằng lệnh quét đối chiếu, không
   xoá được.

## 5. Trình bày text-diagram trong chat có ổn không

Claude Code hiện khối mermaid ra dạng CHỮ, không vẽ hình. Muốn thấy hình phải mở trình duyệt,
hoặc cài thêm công cụ render ASCII như termaid (https://github.com/fasouto/termaid). Bản ASCII
cũng chỉ là bản xem nhanh, bố cục không đúng như bản gốc
(https://qwenlm.github.io/qwen-code-docs/en/users/features/markdown-rendering).

Vậy nên khuôn cho chat phải là cây thụt lề thuần, không phải mermaid:

```
Đăng nhập  [6 bước · 2 nhánh lỗi]
├─ B1 nhập email + mật khẩu       client · LoginForm.onSubmit
├─ B2 kiểm tra tại chỗ            client · validateCredentials  (sai → B2E dừng)
├─ B3 gửi yêu cầu                 client · authApi.login
├─ B4 tra người dùng              server · AuthController.login (sai → B4E lỗi chung)
└─ B5..B6 phát token → lưu → vào app
```

**Kết luận:** ổn, với hai điều kiện. Một là dùng cây thụt lề chứ không dùng mermaid, vì
mermaid không render trong CLI (https://github.com/fasouto/termaid). Hai là chat chỉ hiện
BẢN RÚT GỌN như trên, còn bản đầy đủ nằm trong file — màn hình terminal hẹp, cây quá mười lăm
dòng là hết đọc được (`suy luận`).

## 6. Phương án đề xuất

Sáu bước, không thêm phase nào, không thêm cổng duyệt nào:

1. **Spec, lane `full`**: thêm mục `§2c Sơ đồ giải thuật` — cây thụt lề, chỉ ngôn ngữ nghiệp
   vụ, kèm các nhánh lỗi. Lane `quick` và tầng `nhỏ` bỏ qua.
2. **Duyệt spec**: user duyệt sơ đồ cùng lúc duyệt spec, không phát sinh lượt chờ mới.
3. **Plan**: mỗi task ghi mã bước nó hiện thực vào dòng `Chạm:` sẵn có, ví dụ `Chạm: … (B3)`.
4. **Sau build**: `scripts/tdq_mindmap.py sinh` đọc spec + plan, xuất
   `docs/tdq/mind-map/<slug>.json` theo lược đồ ở đầu tài liệu này.
5. **Đối chiếu**: `tdq_mindmap.py doi-chieu` hỏi LSP từng cặp file + hàm, bước nào trỏ vào
   hàm không còn thì báo lệch. Đây là cơ chế chống lỗi thời, và là phần đáng giá nhất.
6. **Xem**: `tdq_mindmap.py xem` gộp mọi file JSON thành một trang HTML tự chứa trong
   `docs/tdq/mind-map/index.html`, mở bằng trình duyệt, không cần mạng.

Chỉ một file mã nguồn mới, `scripts/tdq_mindmap.py`, thuần thư viện chuẩn Python: không npm,
không pip, không CDN. Thêm lệnh `dung-nguoc` quét repo cũ để dựng khung JSON ban đầu, phần
giải thuật để trống chờ người điền.

### Phương án bị loại

- **Thêm hẳn phase `diagram` giữa spec và plan.** Loại vì đẻ thêm một cổng duyệt, tức thêm
  một lượt chờ user cho MỌI request. Giá trị của spec-kit nằm ở chỗ có người duyệt thiết kế,
  không nằm ở số cổng (https://arxiv.org/html/2602.00180v1).
- **Dùng markmap.js để xuất HTML.** Loại vì cần Node.js, mà user đã chốt mọi thứ phải tự
  chứa. Cây thụt lề viết tay bằng HTML nội tuyến đủ dùng cho quy mô 10–50 tính năng.
- **Sinh tự động toàn bộ bằng code2flow.** Loại vì call graph không chứa ý định nghiệp vụ
  (https://github.com/scottrogowski/code2flow); nó trả lời "hàm nào gọi hàm nào", không trả
  lời "vì sao".

## Phản biện

### Điểm yếu 1 — sơ đồ viết tay vẫn drift, chỉ chậm hơn

Lệnh `doi-chieu` bắt được hàm biến mất, nhưng không bắt được giải thuật đổi mà tên hàm giữ
nguyên. Giảm: mỗi request sửa một tính năng đã có sơ đồ thì bắt buộc đọc lại sơ đồ đó, và
`cap_nhat` quá sáu tháng thì bị đánh dấu nghi ngờ.

### Điểm yếu 2 — bước vẽ dễ thành lễ nghi

User duyệt cho xong thì cả cơ chế mất tác dụng, mà chi phí vẫn còn nguyên. Giảm: bắt buộc sơ
đồ phải nêu ít nhất một nhánh LỖI; sơ đồ chỉ có đường thành công là dấu hiệu vẽ cho có.

### Điểm yếu 3 — chưa có số đo cho chính loại diagram này

Mọi số trong tài liệu này đo tài liệu kỹ thuật hoặc graph tự động, không đo sơ đồ giải thuật
nghiệp vụ viết tay. Giảm: chạy thử ba request thật, so thời gian và số lần sửa lại, rồi mới
bắt buộc toàn workflow.

## Đối chiếu công cụ sẵn có

| Công cụ | Nó cho gì | Vì sao không dùng thẳng |
|---|---|---|
| `graphify` (trong repo) | graph cấu trúc code | không có ý định nghiệp vụ, chỉ có quan hệ ký hiệu |
| agent-lsp / LSP | định nghĩa, người gọi, kiểu | trả lời từng câu hỏi lẻ, không dựng được luồng |
| code2flow | call graph tự động từ AST | thiếu ngữ nghĩa "vì sao", kém với ngôn ngữ động |
| Madge, Dependency-Cruiser | graph phụ thuộc module JS/TS | chỉ JS/TS, và ở mức module chứ không mức bước |
| markmap.js | mind map HTML tự chứa | cần Node.js, phạm nguyên tắc tự chứa user đã chốt |

Nguồn ba dòng cuối: https://github.com/scottrogowski/code2flow ·
https://www.upgradejs.com/blog/application-architecture-visualization.html · https://skillsllm.com/skill/mindmap-markmap-viewer

## Bản sửa đổi v2 — theo phản hồi user ngày 2026-08-23

User bác ba điểm của v1 và nêu một lý do v1 chưa cân đúng. Lý do đó là: `graphify` có dữ
liệu nhưng ĐỌC LUỒNG XỬ LÝ từ nó gần như bất khả thi ở dự án lớn, nên cần một lớp giải
thuật nghiệp vụ để user duyệt trước khi code, đồng thời làm lớp truy suất cho Claude khi
lên spec và plan. Cân lại theo lý do đó thì v1 sai chỗ nào, ghi rõ bên dưới.

### Ba thay đổi user yêu cầu

| # | v1 | v2 | v1 sai ở đâu |
|---|---|---|---|
| 1 | chỉ bắt buộc lane `full` | bắt buộc CẢ `full` và `quick` | v1 tối ưu chi phí; nhưng request `quick` cũng đụng luồng nghiệp vụ, bỏ qua là mất đúng chỗ cần |
| 2 | không thêm cổng duyệt, duyệt kèm spec | cổng duyệt RIÊNG cho sơ đồ | duyệt kèm spec thì sơ đồ bị đọc lướt; tách ra để user tập trung đúng một thứ |
| 3 | giải thuật và ánh xạ hàm ở hai file | gộp một dòng, tên hàm ghi trong ngoặc | tách hai chỗ thì phải đọc chéo mới hiểu; gộp lại vừa dễ đọc vừa dễ parse |

Thay đổi 2 lật đúng kết luận mục 3 và mục 4 ở trên. Ghi lại cho rõ: v1 loại phase `diagram`
vì nó đẻ thêm một lượt chờ. Lượt chờ đó là có thật, v2 không phủ nhận, nhưng user chấp nhận
trả giá để đổi lấy sự tập trung. Đây là quyết định của user, không phải kết luận từ nguồn.

### Vị trí mới trong workflow

```
lane full   analyze → [diagram ★] → spec → plan → mode → implement → qc → report
lane quick  intake  → [diagram ★] → mini-plan → implement → qc
                        ★ cổng duyệt riêng, user duyệt trước khi có bất kỳ file spec/plan nào
```

Sơ đồ đứng TRƯỚC spec chứ không nằm trong spec. Ba lý do. Một, nó là đầu vào để viết spec,
đúng như user nói: có lớp giải thuật thì spec và plan mới chuẩn. Hai, spec đã duyệt bị niêm
sha nên sửa được là một phiền phức, còn sơ đồ phải sống cùng code. Ba, lane `quick` không hề
có spec, nên nhét sơ đồ vào spec thì lane `quick` không dùng được.

### Khuôn một dòng, gộp giải thuật và tên hàm

Nguồn duy nhất viết tay là `docs/tdq/mind-map/<slug>.md`. Mỗi bước một dòng, tên file và tên
hàm nằm trong ngoặc đơn ở cuối dòng, đúng như user đề xuất:

```
# Đăng nhập
B1 · Nhập email và mật khẩu (src/pages/login.tsx::LoginForm.onSubmit)
B2 · Kiểm tra tại chỗ trước khi gửi (src/lib/validators.ts::validateCredentials)
B2! · email sai khuôn hoặc mật khẩu ngắn → báo lỗi tại ô nhập, dừng (src/lib/form-ui.ts::showFieldError)
B3 · Gửi yêu cầu qua kênh mã hoá (src/api/auth.ts::authApi.login)
B4 · Tra người dùng và đối chiếu băm (server/controllers/auth.py::AuthController.login)
B4! · không có người dùng hoặc băm sai → trả một lỗi chung (server/controllers/auth.py::deny_login)
B5 · Phát token phiên và token làm mới (server/services/token.py::TokenService.issue_pair)
B6 · Lưu token và vào màn hình chính (?)
```

Bốn quy ước, cả bốn đều máy kiểm được. Dấu `!` sau mã bước đánh dấu nhánh lỗi. Ngoặc `(?)`
nghĩa là hàm chưa tồn tại, hợp lệ lúc duyệt nhưng phải hết sạch trước khi qua phase `qc`.
Một dòng chỉ được một cặp `file::hàm`; bước đụng nhiều hàm thì tách thành nhiều dòng con.
File `.json` không viết tay nữa mà sinh ra từ file `.md` này, nên chỉ có một nguồn sự thật.

### Đối chiếu với code thật — chạy offline trên graphify sẵn có

Đây là chỗ v2 tận dụng được thứ đã có, đúng ý user. Kiểm `graphify-out/graph.json` của chính
repo này thấy: 1171 node, trong đó 673 node là HÀM, mỗi node có sẵn `source_file` và
`source_location` dạng số dòng; cạnh gồm 992 quan hệ `calls` và 631 quan hệ `contains`.

Nghĩa là lệnh đối chiếu không cần LSP, không cần mạng, không cần chạy server: nó chỉ cần
đọc file JSON đó rồi tra từng cặp `file::hàm` trong sơ đồ. Đây là điểm khác v1, vì v1 định
gọi LSP cho từng cặp — chậm hơn và phụ thuộc server đang chạy.

Vai trò hai bên tách bạch: `graphify` biết code có gì nhưng không biết vì sao, sơ đồ biết vì
sao nhưng không tự biết code còn hay mất. Ghép lại thì `graphify` thành lớp kiểm cho sơ đồ,
còn sơ đồ thành mục lục đọc được cho `graphify` — đúng vấn đề user nêu là không đọc nổi
luồng xử lý từ graph.

### Việc phải làm cho v2

| # | Việc | Đụng vào |
|---|---|---|
| 1 | Thêm phase `diagram` và gate `diagram_approved` | `scripts/tdq_state.py` |
| 2 | Viết `scripts/tdq_mindmap.py` với 5 lệnh `sinh` `kiem` `doi-chieu` `xem` `dung-nguoc` | file mới, thuần stdlib |
| 3 | Luật R13 cho file mind-map: đúng khuôn, có ít nhất một nhánh `!` | `scripts/doc_lint.py` |
| 4 | Chặn qua `qc` khi sơ đồ còn `(?)` hoặc còn dòng lệch | hook `stop_gate.py` |
| 5 | Skill mới `tdq-diagram` cho phase mới, sửa hai skill `tdq-intake` và `tdq-spec` | `skills/` |
| 6 | Template sơ đồ và khối trình bày để user duyệt | `skills/tdq-diagram/references/` |

### Cái giá của v2, nói thẳng

1. **Lane `quick` từ một chặng dừng thành hai.** Đây là cái giá lớn nhất và nó rơi vào đúng
   loại request vốn được thiết kế để nhanh. Giảm được một phần: tầng `nhỏ` vẫn miễn hoàn
   toàn, và sơ đồ của một request `quick` thường chỉ ba đến năm dòng.
2. **Mọi request đều tốn thêm một lượt chờ user.** Không giảm được, đây là thứ user cố ý đổi
   lấy sự tập trung.
3. **Sáu hạng mục ở bảng trên đụng vào lõi state và hook.** Rủi ro làm hỏng luồng đang chạy
   cao hơn hẳn v1 vốn chỉ thêm một mục vào template. Giảm: làm theo thứ tự 2 → 3 → 1 → 4,
   tức có công cụ và luật trước, chạm vào state machine sau cùng.
