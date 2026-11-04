# BRIEF — Master kiến trúc Archify có drill-down

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## Nguyên văn

> okay bây giờ bổ sung thêm là tôi muốn một project phải luôn có master kiến trúc bằng archify html, có đầy đủ từ master chart, và có thẻ click và để detail ra, ví dụ như flow tổng hợp là cần login rồi vào cms,... thì có thể click vào tag login để mở ra flow xử lí login là nhập username password, rồi mã hoá sao rồi gửi lên server sao ,... ví dụ như vậy hyax mở request handle update master kiến trúc file html đó, vầ nếu có update phải có trình bày dễ hiểu và graph archify thuật toán trước và sau và còn master kiến trúc archify cũng sẽ luôn đucợ check và update theo kiến trúc mới nhất của project.. Ngoài ra còn vấn đề thứ 2 là tôi muốn là báo cáo hoặc spec hoặc mọi cách trình bày trong tdq-workflow sẽ được trình bày theo style giúp người dùng dễ hiểu hơn. như hình này và set đó làm soul luôn, trong setup của tdq-workflow cũng sẽ có set việc trình bày đơn giản dễ hiểu nhất cho người dùng vào user-instruction của agent luôn

## Hiểu & kiến thức

**Đọc lần đầu — mục tiêu**

1. **Master kiến trúc sống:** mỗi project luôn có một HTML master kiến trúc do Archify sinh, có master chart và mỗi node/luồng (vd `login`, `cms`) **click được để mở chi tiết** luồng con (đăng nhập: nhập username/password → mã hoá thế nào → gửi server ra sao). Master phải luôn được **kiểm tra và cập nhật** theo kiến trúc mới nhất của project; khi cập nhật phải có **trước/sau dễ hiểu**.
2. **Chuẩn trình bày dễ hiểu:** mọi văn bản TDQ-Workflow sinh ra (report, spec, plan, QC, chat block…) theo một style dễ đọc như ảnh mẫu; style đó nằm trong **soul** và được **setup ghi vào user-instruction** của agent.

**Phạm vi request này:** `skills/tdq-build/references/archify-lifecycle.md`, `scripts/tdq_archify.py` + `scripts/archify_*`, master model/bundle và các test tương ứng. **Không chạm** soul, `scripts/tdq_setup.py` (KHOI_HUONG_DAN), user-instruction hay templates trình bày; phần này chuyển sang request kế tiếp theo lựa chọn `2B`.

**Cần eval:** có — thay đổi luật/thân skill và hành vi mặc định, nên phải có eval-plan trước implement.

### Năng lực dùng được

| Năng lực | Verdict | Vai trò trong request |
|---|---|---|
| `tdq_archify.py sync-master/status/verify` | DÙNG | Dựng, kiểm freshness và bind bundle master có manifest/source fingerprint. |
| Archify `explainer` | DÙNG | Cách sẵn có duy nhất để một HTML chứa overview và mở modal cho sơ đồ con. |
| Graphify + LSP + Grep | DÙNG | Lấy symbol/call edge có nguồn, chọn luồng sâu; không suy diễn data/security flow. |
| `tdq_finish.py` | DÙNG CÓ GIỚI HẠN | Đang chỉ ghi master stale, không tự dựng lại; là điểm đặt check rẻ. |
| `tdq-browser-test` | DÙNG | Kiểm modal/click/focus/keyboard và console của master HTML sau khi dựng. |
| `tdq-build` + Archify lifecycle | DÙNG | Buộc verify master/report; không thay luồng phase hiện có. |
| Web research | BỎ | Đây là hành vi nội bộ của engine và workflow local; engine/source/test hiện hữu là nguồn trực tiếp. |

### Khảo sát mã và engine

| Vùng file chạm | Phát hiện qua lớp nào | Tác động & quan hệ |
|---|---|---|
| `scripts/tdq_archify.py`, `scripts/archify_artifacts.py`, `scripts/archify_model.py` | LSP + đọc cấu trúc + Workflow survey | `sync-master` dựng từng view rồi atomic-swap `docs/architecture/`; `status` so manifest, source fingerprint, child file và binding. |
| `scripts/tdq_finish.py` | LSP + Graphify `affected step_archify` | Chỉ gọi `mark_stale`, không tự viết master; check hiện đo khoảng 59–62 ms trên 162 source files. |
| `docs/tdq/models/master.model.json`, `docs/architecture/manifest.json` | Grep + Workflow survey | Model có 6 view; portal hiện chỉ là index tĩnh liên kết các HTML view rời. |
| `C:/Users/admin/Documents/archify/archify/explainer/*` | Survey engine trực tiếp | Native SVG node chỉ focus + Semantic Passport; `explainer` mới có link mở modal native viewer theo diagram/node. |
| `graphify-out/graph.json` | Graphify + survey dữ liệu | Có callable/call edge/source line, nhưng thiếu route, request/response, parameter lineage, hashing/security semantics và runtime trace. |
| `hooks/*`, `scripts/tdq_team.py`, `scripts/tdq_state.py` | Survey trigger | Không hook nào refresh master. Refresh trong hook/merge dễ làm tree dirty hoặc block turn; không dùng làm default. |

### Sự thật kỹ thuật đã chốt

- Native Archify **không** cho node SVG mang `href`/`onclick` mở flow con. Nó chỉ mở Semantic Passport (metadata, source link, upstream/downstream). Không tự thêm handler lách schema.
- Một file **explainer** có thể chứa overview và nhiều diagram block. Link trong prose/step có thể mở modal viewer của diagram được chỉ định; click node trên preview native chỉ mở **chính diagram chứa node**, focus vào node — chưa có chuyển trực tiếp từ node overview sang diagram con. Muốn đúng thao tác bấm node `Login` → diagram Login cần mở rộng engine Archify hoặc đổi UX sang thẻ/link `Login` cạnh sơ đồ. Không hứa tính năng chưa tồn tại.
- Luồng con chỉ được nói điều code/manifest/test chứng minh. Graph hiện tại đủ cho “hàm A gọi B ở file:line”; chưa đủ cho “password được hash thế nào, gửi HTTP endpoint nào, response gì”. Muốn mức đó cần inventory route/handler/data contract có chủ đích hoặc bằng chứng runtime — không được bịa từ call edge.
- “Luôn cập nhật” không thể là tự viết model mù sau mọi tool call: master cần agent hiểu source để chọn và mô tả flow. Phương án an toàn khả thi là **mọi `tdq_finish` kiểm freshness; source đổi thì mark stale; trước report/merge của request chạm source, bắt refresh + verify master hoặc nêu rõ fallback**. Không refresh tại SessionStart, hook mỗi tool hay `tdq_team merge`.
- Project docs-only/rỗng vẫn cần master: render một overview nêu không có code flow và link evidence; không tạo login/flow giả.
- Master hiện stale: `docs/architecture/status.json` có 44 lý do; graphify snapshot cũng stale (không dùng wiki/graph cũ để dựng master mới).

### Lộ trình

| Bước/phase | CÓ-BỎ | Vì sao |
|---|---|---|
| Analyze + scope/detail interview | CÓ | Chốt giao diện drill-down, mức evidence cho flow, lifecycle refresh, project fallback và QC trước spec. |
| Spec + preview Before/After | CÓ | Thay đổi kiến trúc/HTML phải mô tả master cũ → explainer drill-down mới, không cập nhật silent. |
| Plan + eval-plan | CÓ | Skill/lifecycle thay đổi cần đo policy và runtime UI riêng trước implement. |
| Implement theo TDQ team | CÓ | Chạm engine adapter, master model, lifecycle, tests; chia wave theo file nóng. |
| QC ultra + browser test + agent QC độc lập | CÓ | Xác nhận click, bàn phím, modal, stale/refresh/fallback và không claim flow không có evidence. |
| Report | CÓ | Có HTML Before/After, master current/verified hoặc nêu stale/fallback thật. |

### Phạm vi đã chốt

- Mặt CHỌN: master overview + thẻ flow mở modal; detail có bằng chứng; freshness check mọi `tdq_finish`, refresh+verify ở cổng report/merge; project docs-only/rỗng không dựng flow giả; QC ultra.
- Mặt LOẠI: sửa engine Archify để click trực tiếp node; tự đoán data/security flow từ graph; auto-refresh tại mọi tool call/SessionStart; thay soul/setup/user-instruction và style trình bày (request kế tiếp).
- Bối cảnh: một project bất kỳ; hiện mẫu TDQ có 6 view master, graphify snapshot 3518 nodes/7433 links nhưng stale; Archify `explainer` sẵn có modal/link.
- Mức đầu tư suy ra: đầy đủ — master là đầu ra thường trực cho nhiều project, phải giữ source provenance và xử lý stale.

### Quyết định kỹ thuật

- Dùng thẻ/link ở cạnh overview (`1a`), không sửa engine; modal mở native diagram con theo `@steps.target` hoặc inline block link. Luồng con chỉ dựng khi có code/route/test chứng minh; thiếu thì ghi “chưa xác minh”.
- `tdq_finish` chỉ kiểm và ghi stale; request chạm source cần dựng lại model/candidate rồi `sync-master` + verify trước report/merge. Không báo current nếu nguồn/candidate/child HTML không khớp. Nếu Archify không chạy được, giữ last-good và báo fallback/stale rõ, không tự xóa.
- Đầu ra chính của request: `docs/architecture/index.html` master overview có thẻ flow con và evidence; Before/After Archify mô tả luồng cũ/mới, không giả runtime trace. Đầu ra tài liệu style/soul/user-instruction thuộc request khác theo `2B`.
- Không có câu hỏi còn lại làm thay đổi sản phẩm; QC `ultra` đã ghi qua CLI.

## Hỏi đáp

- Pipeline: người dùng chọn **1a** = chuyên sâu (deep), kèm hậu tố `_ultracode`.
- Phạm vi: người dùng chọn **2B** = tách hai request. Request này chỉ làm **master kiến trúc Archify có drill-down + tự kiểm/cập nhật**; chuẩn trình bày dễ hiểu (soul + user-instruction) chuyển sang request kế tiếp, mở sau khi request này đóng.
- User trả lời nguyên văn «1a 2a 3a 4a»: chọn modal trong cùng HTML, chỉ thông tin có bằng chứng code/route/test, `tdq_finish` kiểm stale và refresh+verify ở cổng report/merge, QC ultra. Ghi mức QC bằng `tdq_state.py set muc_qc=ultra`.
- Người dùng trả lời «1a»: chọn **thẻ/link `Login` cạnh sơ đồ tổng** mở modal flow con trong cùng HTML. Không sửa engine Archify để bấm node overview trực tiếp.
- Vòng scope: BỎ — phạm vi đã được chốt bằng lựa chọn tách request; nền tảng và kích thước repo đo từ mã; lựa chọn modal, bằng chứng, lifecycle và QC đã được hỏi riêng. Project docs-only/rỗng dùng overview ghi rõ không có code flow, không tạo luồng giả.
