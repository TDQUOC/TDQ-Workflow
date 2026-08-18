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
