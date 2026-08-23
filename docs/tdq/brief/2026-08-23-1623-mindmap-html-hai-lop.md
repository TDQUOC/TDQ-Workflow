# BRIEF — viết thật tdq_mindmap.py, diagram bắt buộc trước plan, HTML tổng project hai lớp

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## Nguyên văn

> Okay mở request đó đi đồng thời kiêm luôn việc check là tôi muốn diagram nghiệp vụ luôn có
> trước khi lên plan để dev nắm thuật toán giải thuật xử lí còn ở html diagram tổng project sẽ
> có 2 lớp 1 lớp như lúc duyệt 1 lớp detail biết mỗi khi đi qua 1 function phải có 1 step check
> giúp tôi như vậy thì có phù hợp không

Câu trước đó của user, là thứ mở ra request này:

> đã build lại folder mind-map html chưa?

### Đọc lần đầu

**Mục tiêu.** Ba việc, nhưng chung một trục: biến lớp sơ đồ giải thuật từ đề xuất trên giấy
thành thứ chạy được.

1. Viết thật `scripts/tdq_mindmap.py` — hiện chưa tồn tại, hai file `.html`/`.json` trong
   `docs/tdq/mind-map/` là đồ viết tay từ commit `f4427f0`, không phải sản phẩm build.
2. Chốt luật: sơ đồ nghiệp vụ phải có và được duyệt TRƯỚC khi lên plan, để người làm nắm giải
   thuật trước khi viết code. Đây đúng là phase `diagram` đã thiết kế ở
   `docs/tdq/knowledge/2026-08-23-thiet-ke-mind-map-v2.md` mục 3.
3. HTML sơ đồ tổng project có HAI LỚP: lớp nghiệp vụ (đúng thứ user đã duyệt) và lớp chi tiết,
   trong đó mỗi hàm đi qua là một bước.

**Phạm vi đoán.** Cắm vào `scripts/tdq_state.py` (phase + gate), `scripts/doc_lint.py` (luật
khuôn), skill `tdq-plan` và `tdq-intake` (chặn viết plan khi chưa duyệt sơ đồ), file mới
`scripts/tdq_mindmap.py`, và test cho nó. Request này ĐỘNG VÀO CODE THẬT, khác hai request
trước chỉ sinh tài liệu.

**Trả lời thẳng câu "như vậy có phù hợp không".** Hai ý không cùng độ chắc:

- **Ý 2 (diagram trước plan): phù hợp, và gần như đã sẵn sàng.** Nó chính là phase `diagram`
  trong bản thiết kế v2, đã có chữ ký lệnh, hàng `PHASE_TABLE`, và ba chỗ cắm vào `tdq_state.py`
  đều đã đọc và xác minh. Việc còn lại là làm, không phải nghĩ.
- **Ý 3 (lớp detail mỗi hàm một bước): rủi ro nằm ở chỗ lớp đó lấy dữ liệu từ đâu.** Viết tay
  thì không sống nổi — một luồng đăng nhập đi qua vài chục hàm, và nó lệch ngay lần refactor đầu
  tiên. Sinh tự động từ `graphify-out/graph.json` thì khả thi, nhưng phải nói rõ giới hạn: đồ thị
  gọi hàm cho biết hàm A CÓ THỂ gọi hàm B, không cho biết trong kịch bản này nó CÓ gọi hay không,
  cũng không cho biết thứ tự gọi và không diễn giải rẽ nhánh. Dựng thẳng ra thì lớp detail là một
  cây toả, không phải một chuỗi bước.

**Chỗ chưa rõ.** Bốn câu, phải hỏi trước khi viết spec:

1. Lớp detail sinh tự động từ graphify hay người viết tay?
2. "Tổng project" nghĩa là gộp mọi sơ đồ của mọi request vào một trang, hay là một sơ đồ riêng
   viết ở mức toàn hệ thống?
3. Chặn cứng hay chặn mềm: chưa duyệt sơ đồ thì `tdq_state.py` từ chối sang phase plan, hay chỉ
   nhắc rồi vẫn cho đi?
4. Lane `quick` và tầng `nhỏ` có phải vẽ sơ đồ không, hay chỉ lane `full`?

## Hiểu & kiến thức

### Năng lực dùng được

Chạy `python3 scripts/skill_inventory.py --loc "mind map diagram html, phase gate trạng thái,
đồ thị gọi hàm graphify, test python"` — giữ 7, ẩn 213.

| Năng lực | Nguồn | Phán quyết | Vì sao |
|---|---|---|---|
| `tdq-intake` `tdq-spec` `tdq-plan` `tdq-build` | plugin | DÙNG | khung bắt buộc của lane full |
| `tdq-conventions` | plugin | DÙNG | luật ngôn ngữ, working log, khối trình bày |
| `tdq-status` `tdq-check-status` | plugin | BỎ | chỉ để báo trạng thái, request này không cần |
| `artifact-design` `artifact-diagramming` | built-in | CÂN NHẮC | có kiến thức dựng SVG/HTML tự chứa, hợp lệnh `xem`; quyết ở phase plan |
| `mem0-memory` | project | DÙNG | ghi lại kết luận về lớp detail sau khi chốt |

### Đã xác minh bằng cách đọc file thật

1. **Đồ thị CÓ cạnh gọi hàm.** `graphify-out/graph.json` để cạnh ở khoá `links` (không phải
   `edges`), 2203 cạnh, trong đó `relation: calls` 992 cạnh và `indirect_call` 62 cạnh.
2. **Cạnh gọi CÓ số dòng nơi gọi.** 1054/1054 cạnh gọi mang `source_location`. Nghĩa là các
   lời gọi bên trong một hàm sắp được theo thứ tự dòng — với code chạy thẳng thì thứ tự dòng
   xấp xỉ thứ tự chạy. Đây là thứ làm lớp detail khả thi hơn tôi nói ở lần đọc đầu.
3. **Giới hạn thật của thứ tự đó.** Nó là thứ tự VIẾT, không phải thứ tự CHẠY: rẽ nhánh, vòng
   lặp, return sớm đều không được diễn giải; và nhiều lời gọi trùng một dòng thì hoà nhau
   (thấy thật ở `scripts/tdq_eval.py` L547 có 4 lời gọi cùng dòng).
4. **Một chỗ SAI trong bản thiết kế v2 phải sửa.** Thuật toán `doi-chieu` ở mục 1 lọc node hàm
   bằng "có cả `source_file` lẫn `source_location`". Lọc vậy ra 1165/1171 node, gồm cả node
   tài liệu (`CHANGELOG.md` cũng có `source_location: L1`). Trường đúng để lọc là
   `file_type == "code"` — 711 node.
5. **Chặn cứng phải nằm ở `scripts/tdq_state.py`, không nằm ở hook.** `docs/kien-truc.md` mục
   `Đã chốt` ngày 2026-07-29: "hook chỉ nhắc và kiểm bằng hiệu ứng thật, không trả `deny` vì lý
   do chưa duyệt". Tiền lệ chặn đúng chỗ là `_chan_worktree_con_mo` trong `tdq_state.py`.
6. **File code mới bắt buộc nằm trong `scripts/` hoặc `hooks/`.** `.graphifyignore` loại mọi
   thư mục khác, đặt chỗ khác thì đồ thị không thấy. `scripts/tdq_mindmap.py` là đúng chỗ.
7. **Luật ngôn ngữ cho file code mới.** Chốt 2026-08-22: chú thích, docstring và mọi chuỗi máy
   in ra trong `scripts/` viết TIẾNG ANH cố định; `scripts/i18n_check.py` gác việc này.
8. **Đã có tiền lệ sinh HTML tự chứa** trong `scripts/tdq_lsp.py` — đọc lại trước khi tự nghĩ
   cách dựng trang.
9. `VALID_PHASES` dòng 68 hiện là 8 phase, chưa có `diagram`. `OUTPUT_DIRS` của `doc_lint.py`
   ở dòng 448, nhánh `is_output` ở dòng 601. `tests/` hiện có 65 mục.

### Bỏ vòng research ngoài — lý do

Mọi ẩn số của request này đều nằm trong repo: khuôn file của chính mình, đồ thị của chính mình,
máy trạng thái của chính mình. Câu hỏi ngoài duy nhất đáng hỏi là "đồ thị gọi tĩnh có suy ra
được thứ tự chạy không" — đã tự trả lời bằng cách đọc chính `graph.json` ở mục 2 và 3, chắc hơn
mọi nguồn ngoài.

### Bỏ vòng hỏi phạm vi — lý do

User đã tự khai phạm vi thành ba hạng mục rời, gọi tên rõ từng cái. Hỏi lại "muốn động vào vùng
nào" là hỏi thứ vừa được trả lời.

### Tự quyết, không hỏi

Độ sâu lớp detail mặc định 1 tầng (chỉ các hàm mà hàm của bước gọi thẳng), mở thêm bằng cờ
`--sau <N>`. Lý do: 1 tầng đã đủ trả lời "bước này chạm vào đâu", còn đi sâu hơn thì số node
tăng theo cấp số nhân và trang HTML mất tác dụng.

## Hỏi đáp

### Vòng 1 — đã chốt

| # | Hỏi | User chốt | Ghi chú kèm theo |
|---|---|---|---|
| 1 | Lớp detail lấy dữ liệu từ đâu | **A** — sinh tự động từ `graph.json`, không viết tay, không cần duyệt | bổ sung: mỗi hàm phải nói ra được chức năng, bằng giải thích kèm hoặc bằng chính tên hàm |
| 2 | "Sơ đồ tổng project" là gì | **A** — một trang gộp mọi sơ đồ, có mục lục | bổ sung: xếp từ tổng thể xuống trang nghiệp vụ — đăng nhập, đặt hàng, thanh toán… |
| 3 | Chưa duyệt có sang plan được không | **A** — chặn cứng ở `tdq_state.py` | lý do user nêu: sơ đồ là thuật toán, chưa duyệt thì phải GIỮ LẠI để dev sửa cho đúng ý đồ, chặn không được xoá hay bắt vẽ lại |
| 4 | Ai phải vẽ | **A** — chỉ lane `full` | |
| 5 | Phạm vi request | **A** — cả ba hạng mục một lượt | |

Hệ quả của câu 2: trang tổng gom nhóm theo đường dẫn nghiệp vụ, không gom theo slug request.
Khuôn v1 cũ đã từng có sẵn trường này — `docs/tdq/mind-map/vi-du-login.json` mang
`"thuoc_nhanh": "Xác thực > Đăng nhập"`. Lấy lại ý đó chứ không nghĩ mới.

### Đo thêm sau vòng 1

Đếm bằng `ast` trên `scripts/` và `hooks/`: 655 hàm, 392 hàm có docstring (59%). 263 hàm còn
lại phần lớn là hàm phụ rất ngắn mà tên đã tự nói hết — `_now`, `_load_json`, `_warn`.

Kết luận rút ra, ảnh hưởng thẳng tới yêu cầu bổ sung của câu 1: **"tên hàm phải nói ra chức
năng" là luật máy KHÔNG kiểm được.** Không có phép đo nào chấm được một cái tên là rõ hay tối.
Máy chỉ kiểm được thứ đếm được: hàm này có docstring hay không. Vì vậy chỗ này phải chọn giữa
một luật máy gác được và một luật chỉ người gác được.

### Vòng 2 — đã chốt

| # | Hỏi | User chốt | Ghi chú kèm theo |
|---|---|---|---|
| 6 | Giải thích mỗi hàm ở lớp detail lấy từ đâu | **A** — docstring dòng đầu; hàm thiếu thì in trơ tên và tô nhạt, không chặn, không fail | luật "tên phải rõ nghĩa" giữ ở mức con người, máy không gác |
| 7 | Dòng nhánh nghiệp vụ trong khuôn | **A** — thêm dòng BẮT BUỘC `@nhánh: Xác thực > Đăng nhập` ngay dưới tiêu đề | trang tổng gom nhóm bằng đúng dòng này |

Yêu cầu thêm của user, không nằm trong câu hỏi nào: **skill phải mang khuôn mẫu chi tiết** để
Claude Code đọc xong là biết phải làm gì, không phải đoán.

### Hết câu hỏi

Không còn câu nào đổi được kết quả. Ba câu cổng đều trả lời được: phạm vi rõ (một script mới,
một phase mới, một trang tổng, một skill mới, kèm test); không cần model, không cần tải, không
cần cài gì; phạm vi kiểm đã định ở mục QC của spec.

### Lộ trình

| Bước/phase | CÓ-BỎ | Vì sao |
|---|---|---|
| analyze | CÓ | đã chạy xong, hai vòng hỏi, không còn ẩn số |
| research ngoài | BỎ | mọi ẩn số nằm trong repo, đã tự đọc `graph.json` để trả lời |
| vòng hỏi phạm vi | BỎ | user tự khai phạm vi thành ba hạng mục gọi tên rõ |
| spec | CÓ | khung bắt buộc lane full |
| plan | CÓ | khung bắt buộc lane full |
| mode | CÓ | request đụng code thật, phải để user chọn cách chạy |
| implement | CÓ | khung bắt buộc |
| qc | CÓ | request đầu tiên của loạt này sinh code chạy được, bắt buộc kiểm |
| QC độc lập bằng agent | BỎ | user chưa yêu cầu dùng sub-agent; QC tự chạy nhưng mọi dòng DoD phải là lệnh CHẠY được thuật toán, không phải `grep` tên biến |
| review sâu bằng `tdq-reviewer` | BỎ | user chưa yêu cầu |
| report | CÓ | khung bắt buộc |

Dòng "QC độc lập" ghi thêm lý do vì đây là bài học vừa rút hôm nay: bản thiết kế v2 đạt QC 12/12
mà vẫn lọt lỗi lọc node, do hạng mục kiểm chỉ `grep` tên trường chứ không chạy phép lọc.
