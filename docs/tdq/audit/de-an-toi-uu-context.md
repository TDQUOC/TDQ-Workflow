# Đề án tối ưu context cho bộ workflow TDQ

Ngày: 2026-08-17 · Request: 2026-08-17-2121-toi-uu-context-workflow
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

Số và bằng chứng chạy thật nằm ở [do-thuc-nghiem.md](do-thuc-nghiem.md). File này chỉ
diễn giải và xếp thứ tự. Request này **không sửa một dòng skill nào** — đúng phạm vi
user chốt ở câu 6a.

## 0. Kết luận trước, lập luận sau

**Tối ưu được, và biên độ lớn hơn tôi ước lượng lúc mở request.** Con số quyết định:

| chỗ tốn | token hiện | sau tối ưu | cách |
|---|---|---|---|
| Mô tả 284 skill trong system prompt | 29.788 | 3.661 | hướng D — cấu hình, không sửa code |
| Thân skill + reference một request lane full | 70.924 (trần) | chưa đo | hướng B + C |
| Chính văn bản luật | — | −37,6% | hướng A — dịch tiếng Anh |

Việc đáng làm ngay là **hướng D**: 87,7% phần tốn nhất, sửa một file cấu hình, không
đụng luật, đảo ngược trong 10 giây. Ba hướng còn lại đắt hơn nhiều và phải xếp sau.

Và một kết luận âm tính, quan trọng ngang phần trên: **hướng E (router thay mô tả)
CHƯA nên làm** — lý do ở §5, kèm số đo.

## 1. Hướng A — dịch bộ luật sang tiếng Anh

Đo thật trên `approval.md`: 1.070 → 668 token, **hệ số 0,624, tiết kiệm 37,6%**. Bản
tiếng Anh dài hơn về ký tự mà vẫn ít token hơn — lợi ích đến từ tokenizer (tiếng Việt
1,68 ký tự/token, tiếng Anh 2,97), không từ việc viết ngắn lại.

Ba điều phải nói kèm, nếu không con số 37,6% sẽ bị dùng sai:

1. **Đây là cận dưới của một file khó dịch**, không phải hệ số điển hình. `approval.md`
   đầy chuỗi tiếng Việt cấm dịch (`duyệt`, `chốt`, `cái này`) vì đó là chữ user gõ.
2. **Rule trình bày tiếng Việt vẫn giữ được** — đúng như user đặt vấn đề lúc mở request.
   Luật "output cho user viết tiếng Việt" là một dòng trong văn bản; văn bản viết bằng
   tiếng gì không quyết định output viết bằng tiếng gì. Không có xung đột kỹ thuật.
3. **Rủi ro cao nhất trong năm hướng** vì đụng thẳng vào chữ của luật. Lưới an toàn đã
   dựng sẵn: [luat-hien-co.md](luat-hien-co.md) (329 điểm neo) + `tests/test_luat_skill.py`.
   Nhưng lưới đó khoá *sự tồn tại của chữ*, và bản dịch thay chữ — nên trước khi dịch
   phải chuyển lưới sang khoá *hành vi*, không thì lưới đỏ toàn bộ và vô dụng.

User đã chốt (câu 2a): hướng A để riêng một request sau. Đề án giữ nguyên quyết định đó.

## 2. Hướng B — cắt output tool

Lợi ích lớn nhất, rủi ro thấp nhất: không đụng một dòng luật nào. Chỗ tốn không nằm ở
văn bản skill mà ở thứ tool trả về giữa request — đọc cả file khi chỉ cần 20 dòng,
`grep` không giới hạn, đọc lại file đã có trong context.

Luật cho hướng này **đã có sẵn** ở `skills/tdq-conventions/references/context-budget.md`
và §10 của `tdq-conventions/SKILL.md`. Nghĩa là hướng B phần lớn không phải viết luật
mới mà là làm cho luật sẵn có được tuân thủ.

Chưa đo được trong request này: cần log số token tool trả về qua vài chục request thật
mới có mẫu. Đó là việc của request sau, và nó cần một thước đo chưa tồn tại.

## 3. Hướng C — nạp reference theo nhu cầu

Số nói rõ vì sao hướng này đáng: thân 5 skill cộng lại **15.205** token, còn 25 file
reference cộng lại **55.719** token — phần reference nặng gấp 3,7 lần phần thân.

Bộ skill đã làm đúng progressive disclosure ở mức thân-trỏ-reference. Chỗ còn cải
thiện là bên trong file reference: vài file đủ lớn để tự chúng nên tách tiếp.

Cảnh báo về chính con số này: 70.924 là **TRẦN TRÊN**, không phải lượng token một
request thật tiêu. Nó cộng cả 25 reference, còn một request chỉ mở vài cái. Lấy trần
đi so với số thật sau tối ưu sẽ ra một mức "tiết kiệm" ảo. Đo trước/sau phải cùng một
cách đo.

## 4. Hướng D — `skillOverrides` (nên làm TRƯỚC)

Cơ chế có sẵn của Claude Code, khai trong `~/.claude/settings.json`. Bốn mức:

| mức | model thấy mô tả | model gọi được | `/tên` gọi được |
|---|---|---|---|
| (không khai) | có | có | có |
| `name-only` | không, chỉ thấy tên | có | có |
| `user-invocable-only` | không | **không** | có |
| `off` | không | không | không |

Ba kịch bản, đo trên đúng 284 skill đang bật:

| kịch bản | token mô tả còn lại | tiết kiệm |
|---|---|---|
| giữ nguyên | 29.788 | — |
| tất cả về `name-only` (trừ 23 skill workflow) | 4.171 | 86,0% |
| đề xuất: `name-only` + `off` cho 41 skill lạc mục | **3.661** | **87,7%** |

Mọi số ở bảng này đo cùng một cách với `skill_tokens.py --mo-ta`: token mô tả + token
tên + 6 token khung cho mỗi mục trong danh sách. Nói rõ vì đổi cách đo giữa chừng là
cách dễ nhất để tạo ra một mức "tiết kiệm" không có thật.

Đáng chú ý: bậc `off` chỉ thêm được 1,7 điểm phần trăm so với `name-only` thuần
(4.171 → 3.661). Gần như toàn bộ lợi ích nằm ở việc **giấu mô tả**, không ở việc tắt
hẳn skill. Nên nếu phân vân nhóm nào lạc mục, cứ để `name-only` — mất rất ít mà không
mất quyền gọi skill.

File đề xuất: [skill-overrides-de-xuat.json](skill-overrides-de-xuat.json), 261 khoá,
đã kiểm 100% khoá có thật và 100% giá trị hợp lệ. **Chưa áp vào đâu** — md5 của
`~/.claude/settings.json` không đổi.

Ba giới hạn phải biết trước khi áp:

1. **Cấu hình TĨNH.** Không có cơ chế tự bật lại một skill khi hội thoại chạm đúng chủ
   đề. Tắt là tắt cho tới khi user sửa file và mở phiên mới.
2. **Không lắp được vector DB vào chính nó.** `skillOverrides` là bảng tên → mức, không
   phải điểm nối cho bộ tra cứu. Muốn tra cứu động thì phải đi đường hook (§5).
3. **Đây là tiết kiệm CỬA SỔ CONTEXT, không phải tiết kiệm tiền.** Phần mô tả skill nằm
   trong system prompt và được prompt-cache; cắt nó làm rộng chỗ để làm việc, chứ không
   giảm hoá đơn tương ứng 87,7%.

Một điều **chưa xác nhận được** và nó chạm thẳng vào kiến trúc: `name-only` có còn cho
model tự gọi skill không. Bằng chứng chuỗi trong binary nói là còn; chưa chạy thật được
vì quy tắc 7 cấm ghi settings và `skillOverrides` chỉ đọc lúc mở phiên. Cách user tự
kiểm trong 1 phút: xem §4 của [do-thuc-nghiem.md](do-thuc-nghiem.md).

## 5. Hướng E — kho tra cứu skill (BM25/vector) — KHUYẾN NGHỊ CHƯA LÀM

Ý tưởng user nêu ở vòng 4: cất tên + mô tả skill ra ngoài, cần thì tra rồi chỉ nạp vài
skill liên quan. Tiền lệ có thật trong chính Claude Code: `ToolSearch` làm đúng vậy với
tool. Nên ý tưởng đúng về nguyên lý. Request này dựng nguyên mẫu
[`scripts/skill_router.py`](../../../scripts/skill_router.py) (BM25, offline) và đo.

Bốn kiến trúc, tính trên 284 skill:

| kiến trúc | token thường trực | token mỗi lần tra | ghi chú |
|---|---|---|---|
| giữ nguyên | 29.788 | 0 | hiện tại |
| `name-only` toàn bộ | 4.171 | 0 | hướng D |
| `off` + router, model tự nhớ đi tra | ~0 | ~800 | rẻ nhất, nhưng xem lỗ hổng dưới |
| `off` + router + hook `UserPromptSubmit` | ~0 | ~800 (tự động) | bịt được lỗ hổng |

**Tỉ lệ tra trúng đo trên 22 prompt mẫu — đây là số chặn đường:**

| | top-1 | top-5 |
|---|---|---|
| toàn bộ 22 prompt | **27,3%** | **45,5%** |
| nhóm dễ (prompt nhắc thẳng tên công cụ) | — | 90,0% |
| nhóm vừa (nói việc, không nói tên công cụ) | — | 16,7% |
| nhóm khó (nói ý định bằng lời thường) | — | **0,0%** |

**Khuyến nghị: KHÔNG chuyển sang router.** Top-5 45,5% nghĩa là hơn một nửa số lần,
skill đúng không lọt nổi vào 5 kết quả đầu. Router tra trượt tệ hơn hẳn tốn token: mất
một skill lẽ ra phải dùng, và **không ai biết là đã mất** — không có tín hiệu lỗi nào.
Ngưỡng để đổi ý là top-5 ≥ 90%.

Nguyên nhân gốc — và đây là phần đáng giá nhất của phép đo này. Không phải BM25 kém.
Cùng MỘT ý định hỏi bằng hai thứ tiếng, top-5:

| ý định | hỏi tiếng Việt | hỏi tiếng Anh |
|---|---|---|
| "kiểm tra chất lượng code trước khi merge" / code quality gate | TRƯỢT | trúng |
| "nghiên cứu sâu một chủ đề trên web" / deep research a topic | TRƯỢT | trúng |
| "mọi thứ trông lệch nhau" / misaligned layout | TRƯỢT | TRƯỢT |
| "nhân vật đi xuyên tường" / character passes through walls | TRƯỢT | TRƯỢT |
| **tổng** | **0/4** | **2/4** |

Hai ca cuối trượt cả hai thứ tiếng — tra từ khoá còn hỏng ở chỗ khác nữa, không chỉ ở
ngôn ngữ. Điều đó làm khuyến nghị "chưa chuyển sang router" mạnh thêm chứ không yếu đi.

Kho mô tả gần như toàn tiếng Anh; user gõ tiếng Việt. Tra từ khoá không bắc được cầu
qua khoảng cách ngôn ngữ đó. (Tệ hơn: trước khi lọc hư từ, mọi câu hỏi tiếng Việt đều
trả về 6 skill `tdq-*` — chỉ vì đó là 6 mô tả tiếng Việt duy nhất trong kho nên "cho",
"này", "một" có IDF cực cao. Đã lọc hư từ hai thứ tiếng trong nguyên mẫu.)

Hệ quả bắc cầu sang hướng A, và đây là chỗ hai hướng đá nhau: **dịch bộ workflow sang
tiếng Anh làm khoảng cách này RỘNG THÊM.** Sau khi dịch, 6 mô tả tiếng Việt cuối cùng
cũng thành tiếng Anh, và router lexical mất nốt phần đang chạy được. Làm hướng A trước
rồi mới tính hướng E là tự chặn đường mình.

Nếu về sau vẫn muốn hướng E, hai điều kiện phải có trước:
* **Embedding đa ngữ** thay cho BM25 (vector DB đúng như user hình dung ban đầu — số đo
  này chính là căn cứ để nâng, thay vì nâng theo cảm giác), và
* **hook `UserPromptSubmit`** để tra tự động. Không có nó thì kiến trúc dựa vào việc
  model *nhớ* phải đi tra — mà một model không thấy mô tả skill thì cũng không biết là
  có gì để mà tra. Đây là lỗ hổng tự bịt miệng, không phải lỗi thỉnh thoảng.

## 6. Thứ tự nên làm

| # | hướng | tiết kiệm | rủi ro | vì sao xếp ở đây |
|---|---|---|---|---|
| 1 | D — `skillOverrides` | 26.127 token (87,7%) | thấp | sửa cấu hình, không đụng luật, đảo ngược tức thì |
| 2 | C — tách reference | chưa đo (phần 55.719) | thấp | không đổi nội dung luật, chỉ đổi lúc nạp |
| 3 | B — cắt output tool | chưa đo | thấp | luật đã có sẵn, phần lớn là làm cho được tuân thủ |
| 4 | A — dịch tiếng Anh | −37,6% văn bản luật | **cao** | đụng chữ của luật; cần lưới khoá hành vi trước |
| — | E — router | — | — | **chưa làm**, chờ top-5 ≥ 90% |

Trước khi bắt đầu bất cứ hướng nào: ba bản `skills/`, `portable_claude/`,
`portable_codex/` hiện **giống hệt nhau về nội dung** (§1 của do-thuc-nghiem.md), nên
chi phí sửa là ×1 chứ không ×3. Nhưng chúng đang đồng bộ bằng quy trình, chưa có test
nào khoá. Việc đầu tiên của request tối ưu đầu tiên nên là dựng test khoá điều đó —
trước khi có thay đổi hàng loạt nào chạy qua.

## Vòng 2026-08-19 — chốt lại hướng A sau khi đối chiếu soul

Yêu cầu gốc turn này: đo lại xem dịch skill sang tiếng Anh có tối ưu hơn không, có cách
optimize nào khác cho bộ workflow không. Vòng đo trước (08-17, mục 1-6 ở trên) đã trả
lời phần số — vòng này bổ sung ba lượt research web + một thực nghiệm dịch độc lập, rồi
đối chiếu lại với thứ tự ưu tiên của chính dự án (soul.md: chất lượng > runtime >
context cost) để chốt câu hỏi còn treo của hướng A: có nên làm không, không chỉ là tiết
kiệm bao nhiêu.

**Số đo mới** — dịch `skills/tdq-build/SKILL.md` (99 dòng) sang tiếng Anh, đo bằng
`anthropic_tokenizer` thật (không ước lượng char/4):

| Bản | Ký tự | Token | Ký tự/token |
|---|---|---|---|
| Tiếng Việt (gốc) | 6.396 | 3.579 | 1,79 |
| Tiếng Anh (dịch) | 7.701 | 2.034 | 3,79 |

Hệ số EN/VI = 0,568 → tiết kiệm 43,2%, khớp khoảng 37,6-43,2% đã đo ở vòng trước
(chênh do chọn file mẫu khác nhau, cùng bậc độ lớn).

**Phát hiện mới, quan trọng hơn con số:** một nghiên cứu 35 ngôn ngữ (2025) đo việc
model tuân thủ chỉ dẫn khi NGÔN NGỮ CHỈ DẪN và NGÔN NGỮ NỘI DUNG lệch nhau — độ chính
xác giảm tới 50% so với khi hai ngôn ngữ khớp nhau. Bộ workflow này: user gõ tiếng
Việt, code/output phần lớn tiếng Việt (working log, spec, plan, report) — dịch riêng
SKILL.md sang tiếng Anh tạo đúng kiểu lệch mà nghiên cứu đó đo. Prompt caching (2026)
giảm 90% chi phí đọc cache và không xoá "context rot" (model suy giảm hành vi trước khi
chạm trần cửa sổ ngữ cảnh) — nhưng context rot là trục chất lượng thấp hơn rủi ro lệch
ngôn ngữ, không phải lý do để bỏ qua rủi ro đó.

**Đối chiếu soul (chất lượng > runtime > context cost):** lợi ích của hướng A (~40%
token) nằm ở trục thấp nhất (context cost, vốn đã giảm nhẹ bớt tác động vì caching).
Rủi ro mới tìm thấy (lệch ngôn ngữ chỉ dẫn/nội dung, giảm chính xác tới 50%) nằm ở trục
cao nhất (chất lượng). Làm hướng A tức là đánh đổi ngược thứ tự ưu tiên chính dự án đã
tự đặt ra.

**Kết luận:** hướng A (dịch skill sang tiếng Anh) — **khuyến nghị KHÔNG làm** ở trạng
thái bằng chứng hiện tại. Đây là khuyến nghị dựa trên bằng chứng, không phải cấm tuyệt
đối: nếu sau này có lưới khoá hành vi đủ tốt (như `luat-hien-co.md` đã dựng ở vòng
trước) VÀ đo thực tế cho thấy lệch ngôn ngữ không ảnh hưởng đáng kể ở bộ luật cụ thể
này, có thể xét lại. Bốn hướng D, C, B, E ở mục 6 phía trên **không đổi** — thứ tự nên
làm vẫn D → C → B, hướng A hoãn, hướng E chưa đủ điều kiện.

## Vòng 2026-08-19 (2) — pattern hybrid: có, nhưng khác hẳn "dịch nguyên khối"

Câu hỏi user đặt ra tiếp sau vòng trước: (1) có cách nào dịch skill sang tiếng Anh mà VẪN
giữ giao tiếp user + output/rule/behavior đúng như bản Việt không; (2) các bộ skill tiếng
Anh khác user đang dùng thật (vd. `superpowers`) đang đảm bảo chất lượng bằng cơ chế gì.

**Trả lời (1) — có pattern, nhưng KHÔNG phải "dịch hết".** 5 truy vấn research mới (chi
tiết: `docs/tdq/research/2026-08-19-0029-skill-vi-anh-hybrid.md`) tìm được nguồn giải
đúng mâu thuẫn giữa "35 ngôn ngữ" (dẫn ở vòng trước) và một nghiên cứu RAG doanh nghiệp
(EMNLP) đo ngược chiều — hai bên đá nhau vì khác LOẠI TÁC VỤ: "35 ngôn ngữ" đo trích xuất
từ tài liệu (chỉ dẫn phải khớp ngôn ngữ tài liệu), còn EMNLP đo lý luận/sinh văn bản có
luật phức tạp (chỉ dẫn tiếng Anh làm mỏ neo ổn định). TDQ SKILL.md — luật gate điều kiện,
tick discipline — gần nhóm thứ hai hơn.

Từ đó, một nguồn khác (promptquorum.com) cho cây quyết định tách theo LOẠI NỘI DUNG:
luật lý luận/định dạng phức tạp → viết tiếng Anh được (không phải rủi ro, có thể còn giúp
tuân thủ tốt hơn); còn khuôn user-facing (report, câu hỏi option, ví dụ few-shot) và khai
báo ngôn ngữ đầu ra → PHẢI giữ tiếng Việt, tách riêng, không bị pha vào phần luật. Cảnh
báo trực tiếp: "dịch nguyên prompt" (đúng cách hướng A gốc định làm) cho kết quả tệ hơn
viết lại từ đầu; không khai báo tường minh ngôn ngữ đầu ra thì model đoán sai đôi lúc.

**Trả lời (2) — vì sao `superpowers` "có vẻ ổn".** Không phải vì đã giải bài toán khớp
ngôn ngữ — mà vì (a) tác vụ của nó là quy trình/tool-call (TDD, debug), ít nhạy ngôn ngữ
đầu ra hơn TDQ (không có yêu cầu cứng "output phải 100% tiếng Việt"), và (b) không có gate
nào đo lệch ngôn ngữ trong các bộ đó — lệch có xảy ra cũng không ai thấy. TDQ có
`doc_lint.py`/`stop_gate.py` làm lộ vấn đề ngay nếu có, các bộ kia thì không — không thể
dùng "chạy tốt" của chúng làm bằng chứng an toàn cho TDQ.

**Kết luận:** pattern hybrid (tách luật-lý-luận vs khuôn-user-facing) là một hướng patch
khả thi, khác hẳn và có cơ sở tốt hơn hướng A gốc (dịch nguyên khối) — nhưng **CHƯA làm ở
đây**, và trước khi làm cần thêm 2 điều kiện: (a) lưới khoá hành vi rà đúng ranh giới
"luật lý luận" vs "khuôn user-facing" cho từng skill (không chỉ khoá nội dung như
`luat-hien-co.md` hiện có), (b) một gate mới đo được "output có đúng tiếng Việt không" —
hiện TDQ chưa có gate này, và bằng chứng cho thấy khai báo tường minh ngôn ngữ đầu ra là
điều kiện CẦN chứ không ĐỦ. Thứ tự nên làm ở mục 6 phía trên **không đổi**: D → C → B, A
(kể cả bản hybrid) vẫn hoãn tới khi đủ 2 điều kiện trên.

## Đính chính 2026-08-19 — con số 87,7% của hướng D là SAI

Request `2026-08-19-0046-huong-d-skill-overrides` bắt tay vào áp hướng D và phát hiện
tiền đề của nó không đúng. Giữ nguyên mục 4 và mục 0 phía trên để thấy sai ở đâu; đọc
mục này trước khi tin bất kỳ con số nào của hướng D.

**Sai ở đâu.** Mục 0 và mục 4 giả định `skillOverrides` áp cho mọi skill nên đề xuất
261 khoá và kết luận 29.788 → 3.661 token (87,7%). Tài liệu chính thức
(`code.claude.com/docs/en/skills`, mục "Override skill visibility from settings") nói
ngược lại, nguyên văn: *"Plugin skills are not affected by `skillOverrides`. Manage those
through `/plugin` instead."* Trang `settings` và một nguồn thứ ba độc lập xác nhận lại.

**Số đúng.** Đo lại bằng `scripts/skill_tokens.py --mo-ta` (cùng cách đo, kho skill
không đổi, vẫn 29.788 token):

| Nhóm | Token mô tả | `skillOverrides` áp được? |
|---|---|---|
| 33 skill nguồn `user` | 2.981 (10,0%) | CÓ |
| 251 skill nguồn `plugin` | 26.807 (90,0%) | **KHÔNG** |

Đưa cả 33 skill `user` về `name-only` tiết kiệm **2.632 token (8,8%)**, không phải 87,7%.
File `skill-overrides-de-xuat.json` đã được sinh lại còn đúng 33 khoá có tác dụng thật.

**Hai đòn bẩy mới, đề án cũ chưa biết** (`code.claude.com/docs/en/settings`) — áp cho MỌI
skill kể cả plugin, tức chạm được đúng 90% token mà `skillOverrides` không với tới:

- `skillListingMaxDescChars` (mặc định 1536): trần ký tự mô tả từng skill trong listing.
  Đo thật: 800 → −2,2% · 500 → −13,5% · **300 → −32,9% (9.814 token)** · 200 → −48,2%.
- `skillListingBudgetFraction`: ngân sách tổng cho phần listing.

Đã áp ngày 2026-08-19: D1 (33 khoá `name-only`) + D2 (`skillListingMaxDescChars: 300`).
Mức tiết kiệm hợp lại ~12.446 token (41,8%) — nhưng đây là số ĐO TRƯỚC, cấu hình chỉ đọc
lúc mở phiên nên phải xác nhận ở phiên mới. Chi tiết bằng chứng:
[../research/2026-08-19-0046-huong-d-skill-overrides.md](../research/2026-08-19-0046-huong-d-skill-overrides.md).

**Bài học cho các hướng còn lại (C, B, A, E):** con số 87,7% đứng suốt hai ngày vì không
ai kiểm tiền đề "cơ chế này có áp cho đối tượng mình định áp không". Trước khi tin mức
tiết kiệm của hướng C/B/A/E, kiểm tiền đề bằng tài liệu chính thức rồi mới đo.

## Đính chính hướng C 2026-08-19 — số đo thiếu, và tiền đề "tách sâu thêm" sai

Request `2026-08-19-0121-huong-c-nap-reference` bắt tay vào hướng C và phát hiện hai lỗi
trong mục 3 phía trên. Giữ nguyên mục 3 để thấy sai ở đâu.

**Lỗi 1 — thước đo sót một thư mục.** `scripts/skill_tokens.py` dùng
`glob("references/*.md")` không đệ quy nên bỏ qua trọn `tdq-build/references/rules/`
(10 file, 14.554 token). Con số 55.719 của mục 3 và trần 70.924 vì thế đều thấp hơn thực
tế. Đo lại bằng bản đã sửa: **37 file reference = 77.611 token**, trần đủ file **93.739**
(số đo trước khi request này sửa nội dung).

**Lỗi 2 — tiền đề "vài file đủ lớn để tự chúng nên tách tiếp" đi ngược hướng dẫn chính
thức.** `platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices` khuyên
giữ reference đúng MỘT tầng từ `SKILL.md`; nguồn thứ hai nói thẳng *"Claude may partially
read files when they're referenced from other referenced files"* và *"Do not create
reference files that point to other reference files."* Tách sâu thêm đẩy luật xuống tầng
model có thể đọc nửa vời — hỏng ở trục `chất lượng`, trục cao nhất của soul.

**Việc thật của hướng C hoá ra ngược lại: LÀM NÔNG, không làm sâu.** Đo bằng đồ thị link:
14/37 file reference không được `SKILL.md` nào trỏ thẳng, 36 link reference→reference,
chuỗi sâu nhất tầng 4 (`SKILL.md` → `clean-code.md` → `rules/chung.md` → `rules/index.md`
→ `rules/<ngôn ngữ>.md`). Đã đưa cả 14 file về tầng 1, chừa đúng một ngoại lệ có khoá
test: nhóm điều phối theo ngôn ngữ `rules/`, nơi cửa vào `rules/index.md` ở tầng 1 và
phải trỏ đủ mọi file anh em.

**Và hướng C KHÔNG tiết kiệm token — nó tốn thêm.** Số trước/sau cùng một cách đếm:

| Khối | Trước | Sau | Chênh |
|---|---|---|---|
| Thân 5 skill | 16.128 | 16.538 | +410 |
| 37 file reference | 77.611 | 78.718 | +1.107 |
| Một request lane full thật tiêu | 50.796 | 52.086 | **+1.290 (+2,5%)** |

Đổi lại: 14 file luật rời khỏi vùng đọc-nửa-vời, 8 file dài có mục lục để đọc chọn lọc,
và thước đo hết sai. Theo soul (`chất lượng > runtime > context cost`) đây là đổi đúng
chiều — nhưng phải gọi đúng tên: **hướng C là việc chất lượng, không phải việc tiết kiệm.**
Xếp nó ở vị trí thứ 2 trong bảng ưu tiên mục 6 với lý do "tiết kiệm token" là xếp sai lý do.

**Bài học lặp lại lần thứ hai** (lần đầu ở hướng D): cả hai lần, con số của đề án sai vì
không ai kiểm cách đo và tiền đề. Trước khi tin mức tiết kiệm của hướng B, A, E — kiểm
thước đo trước, kiểm tiền đề bằng tài liệu chính thức sau, rồi mới đo.

## Đính chính hướng B 2026-08-19 — thước đo đã có sẵn, và nó đang đếm sai ảnh

Ba đính chính, cùng một nguyên nhân đã lặp lần thứ ba: không ai kiểm thước đo trước khi
tin con số.

**1. Tiền đề "cần một thước đo chưa tồn tại" (mục 2) SAI.** `scripts/token_audit.py` đã
có từ trước request này, đo đúng carry-cost theo transcript thật. Việc phải làm không
phải viết thước đo mới mà là sửa hai chỗ nó đếm sai.

**2. Thước đo cũ ước lượng ký tự/4 — hụt 47% tổng.** Luật gốc của bộ này là văn bản
tiếng Việt có dấu, thứ mà ký tự/4 hụt nặng. Đếm bằng `anthropic-tokenizer` thật thì tổng
carry-cost cao hơn 47,3% so với số cũ trên cùng 5 phiên.

**3. Ảnh bị tính theo độ dài chuỗi base64 — sai gấp ~186 lần.** Một ảnh chụp canvas
960×1605 px tốn `⌈960/28⌉ × ⌈1605/28⌉ = 2.030` token thị giác, nhưng chuỗi base64 của nó
dài tương đương 378.014 token. Đây là chỗ sai nguy hiểm nhất: nó chỉ đúng một kết luận
— "cắt năng lực chụp màn hình đi" — và đó là cắt nhầm.

| Nhóm (5 phiên, cùng bộ transcript) | Cách đếm cũ | Cách đếm mới | Nhận xét |
|---|---|---|---|
| TỔNG carry-cost | 2.609.256.040 | 3.844.300.565 | +47,3%: ký tự/4 hụt trên tiếng Việt |
| `Read file` | 918.557.908 (35,2%) | 1.756.427.790 (45,7%) | nhóm tốn nhất, cả hai cách đếm |
| Cụm tool MCP | 479.537.211 (18,4%) | 71.779.419 (**1,9%**) | 18,4% cũ gần hết là ảnh bị đếm sai |

**Hệ quả cho chính hướng B.** Con số "MCP tốn 18,1%" từng là lý do chọn
`MAX_MCP_OUTPUT_TOKENS` làm đòn bẩy cấu hình. Đo lại đúng: 1,9%. Khoá đó vẫn được đặt
(25.000), nhưng phải gọi đúng tên — nó chặn ca hiếm khổng lồ trong tương lai, **không**
cắt chi phí đang có.

**`BASH_MAX_OUTPUT_LENGTH` bị loại, không phải bỏ quên.** Đo 3.067 lệnh Bash: đầu ra lớn
nhất 25.654 ký tự, **không lệnh nào chạm trần mặc định 30.000**. Hạ trần đó không cắt
được gì đang có, mà lại thêm rủi ro cắt cụt đúng lần chạy test dài — chất lượng đứng trên
context cost.

**Chỗ chưa kiểm chứng được trong request này.** Luật mới và hook nhắc chỉ tác động lên
PHIÊN MỚI. Mọi phép đo ở trên là trên transcript đã có, nên chúng chứng minh thước đo
đúng, không chứng minh hành vi đã đổi. Muốn biết luật có ăn hay không: chạy
`token_audit.py --sessions 5` sau vài phiên mới rồi so `Read`/lần và tỉ lệ đọc lại.
