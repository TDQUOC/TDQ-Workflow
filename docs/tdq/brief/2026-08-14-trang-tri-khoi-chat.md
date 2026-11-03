# BRIEF — Trang trí khối chat cuối trả lời user

Ngày: 2026-08-14 · Lane: (chưa chốt)

## Nguyên văn

> okay bây giờ mở request là tôi muốn đoạn chat cuối mà trả lời cho người dùng có thể
> decorate thêm ví dụ như format, màu, textsize,.. để phân header và content và làm cho
> visual đẹp hơn không?

### Cách hiểu đầu tiên

**Mục tiêu.** Khối chat cuối turn mà Claude in ra cho user (khối trình spec, trình plan,
hỏi mode, báo cáo + hỏi commit — tất cả đang theo khuôn
`skills/tdq-conventions/references/user-facing-block.md`) hiện là văn xuôi thuần, header
và nội dung nhìn ngang nhau. User muốn biết **có thể trang trí thêm không** và nếu được
thì làm cho nó tách bạch header / content và nhìn đẹp hơn.

**Phạm vi đoán.**
- Trong: khuôn khối chat cuối ở `user-facing-block.md`, cộng mọi chỗ các skill `tdq-*`
  chép lại khuôn đó (lane-decision, interview, mode-gate, spec/SKILL, plan/SKILL,
  build/SKILL + report-template, quick-lane).
- Trong: test đang khoá khuôn — `tests/test_user_facing_block.py`.
- Ngoài (đoán): không đụng `hooks/`, không đụng `portable/`, không đổi nội dung chữ của
  các khối (chỉ đổi cách trình bày), không đổi luật duyệt.

**Chỗ chưa rõ (phải hỏi / phải kiểm chứng, cấm đoán).**
1. Câu này là **câu hỏi** ("có thể … không?") hay là **yêu cầu làm luôn**? Nếu chỉ hỏi thì
   đầu ra là câu trả lời có bằng chứng; nếu làm luôn thì đầu ra là sửa khuôn.
2. Terminal của Claude Code render Github-flavored markdown. **Chưa xác minh** được:
   markdown có đổi được **màu** không, có đổi được **cỡ chữ** không, heading `##` in ra
   trông thế nào, có nuốt ANSI escape không. Đây là ẩn số quyết định — trang trí bằng thứ
   không render được thì khối chat sẽ ra ký tự rác, hỏng đúng chỗ user đọc nhiều nhất.
3. Mức trang trí user muốn: chỉ đậm/nhạt + đường kẻ, hay bảng/emoji/khối trích dẫn?
4. Ràng buộc ngược từ chính repo: khuôn hiện tại đang được các hook và test kiểm chuỗi
   (vd dòng `➤ Trả lời:`); trang trí không được làm vỡ các phép kiểm đó.
5. Khối chat cuối còn bị đọc lại bởi máy (transcript, agent khác). Trang trí nhiều có làm
   khó đọc lại không.

## Hiểu & kiến thức

### Năng lực dùng được

Phân vân → DÙNG. Kiểm kê ngày 2026-08-14: 284 skill trên đĩa (lọc `--loc "markdown"` giữ
13, ẩn 271), cộng skill built-in trong context. Không xoá bảng này kể cả khi không có
dòng DÙNG nào.

| Skill | Nguồn | Phán quyết | Dùng ở đâu / Lý do loại |
|---|---|---|---|
| tdq-intake, tdq-spec, tdq-plan, tdq-build, tdq-conventions, tdq-status | plugin:tdq-workflow | NỀN | chính workflow đang chạy — và cũng chính là đối tượng bị sửa |
| tavily-search | plugin:tavily | DÙNG | research khả năng render của Claude Code (đang chạy, agent riêng) |
| claude-code-guide | built-in agent | DÙNG | nguồn nội bộ về hành vi render của Claude Code, bổ cho tavily |
| artifact-design, frontend-design, dataviz | built-in | KHÔNG | khác lĩnh vực — đầu ra ở đây là văn bản chat, không phải trang HTML hay biểu đồ |
| Đã xét 271 skill khác | user/plugin/built-in | KHÔNG | khác lĩnh vực |

### Bản đồ code — khuôn khối chat cuối nằm ở đâu

Nguồn duy nhất: `skills/tdq-conventions/references/user-facing-block.md` — 5 thành phần,
7 chỗ phải dùng, luật cứng (trong đó có **"Không emoji"**).

Chỗ chép lại khuôn hoặc in ra dòng `➤` (grep `➤`, đã loại `docs/`):

| Nhóm | File | Ghi chú |
|---|---|---|
| Khuôn gốc | `skills/tdq-conventions/references/user-facing-block.md` | ví dụ mẫu nằm trong khối ``` |
| Skill in khối | `tdq-spec/SKILL.md`, `tdq-plan/SKILL.md` + `references/mode-gate.md`, `tdq-intake/references/lane-decision.md` + `quick-lane.md`, `tdq-build/references/report-template.md`, `tdq-status/SKILL.md`, `tdq-conventions/SKILL.md` | 8 file |
| **Mã sinh chuỗi** | `scripts/tdq_state.py` (2 chỗ), `hooks/scripts/_common.py` (2 chỗ), `hooks/scripts/stop_gate.py` (1 chỗ) | hook/script tự in dòng gợi ý có `➤` — sửa khuôn mà bỏ đây là lệch |
| **Bản portable** | `portable/workflow/02-spec.md`, `03-plan.md`, `references/user-facing-block.md` | bản cho agent ngoài Claude Code |
| Test khoá khuôn | `tests/test_user_facing_block.py` (68 dòng) | kiểm: đủ 5 thành phần · đủ 7 chỗ · **cấm emoji, và chính file khuôn cũng không được có emoji** · mọi skill user-facing phải trỏ về khuôn |

### Kết quả research — render được tới đâu

Nguồn đầy đủ: `docs/tdq/research/2026-08-14-trang-tri-khoi-chat.md`.
Điều quyết định nhất: **ba mặt KHÔNG dùng chung một renderer** — issue anthropics/claude-code
#58983 cho thấy cùng một VS Code extension đã có hai chế độ render khác nhau (Terminal mode
làm phẳng bảng, Native UI render đúng). Vậy mẫu số chung phải lấy theo terminal, mặt khắt
khe nhất.

| Thứ user hỏi | Kết luận | Căn cứ |
|---|---|---|
| **Màu chữ** | **KHÔNG làm được** | markdown không có cú pháp màu; ANSI escape do model tự in — không có nguồn xác nhận được render, bằng chứng gián tiếp nghiêng về bị strip; HTML inline chắc chắn hỏng ở terminal |
| **Cỡ chữ** | **KHÔNG làm được** | không có cơ chế nào ngoài heading; terminal về vật lý chỉ một cỡ font |
| Heading `#`/`##` | Dùng được nhưng chỉ như **phân đoạn** | terminal render heading thành in đậm, KHÔNG phóng to, h2–h6 không phân biệt (#26390) |
| **Đậm / nghiêng / `inline code`** | **Dùng được, cả ba mặt** | #26390 |
| Gạch ngang `~~x~~` | TRÁNH | terminal in ra literal |
| Bảng markdown | TRÁNH bảng nhiều cột | terminal sụp key-value khi rộng, lệch cột với tiếng Việt/CJK, mất dòng, biến mất khi resize (#45111 #14763 #22311 #13438 #11274) |
| Khối code, danh sách | Dùng được | xác nhận ở terminal |
| Ký tự khung tự vẽ `┌─┬┐` | TRÁNH | lệch cột do tính sai độ rộng CJK |
| `---`, bullet `• ▸ ➤` | chưa có nguồn riêng | không đoán — nếu cần chốt thì phải tự kiểm bằng mắt trên cả ba mặt |
| Setting `theme` / `tui` / `outputStyle` | không giúp gì | chỉ đổi màu nền/engine hoặc system prompt, không thêm khả năng markdown |

**Hệ quả thẳng cho yêu cầu gốc:** trong ba thứ bạn nêu (format, màu, cỡ chữ) chỉ **format**
là làm được. Hai thứ còn lại không có đường nào an toàn trên cả ba mặt. Đây cũng đúng với
ràng buộc "dùng những cái formal" bạn bổ sung.

Hai điều rút ra buộc phải hỏi user:
1. Phạm vi sửa tới đâu — chỉ `skills/`, hay cộng `scripts/` + `hooks/`, hay cộng cả
   `portable/`? Ba nhóm này rơi ra ba mức rủi ro khác nhau.
2. Luật **"Không emoji"** đang được test khoá cứng. "Trang trí đẹp hơn" mà đụng vào ký tự
   trang trí thì phải quyết định giữ hay nới luật này — không được tự ý.

### Phạm vi đã chốt (sau vòng scope)

- **Mặt CHỌN:** trải nghiệm đọc (A) · tương thích ba mặt (B) · bảo trì / chống trôi khuôn (C) ·
  tương thích ngược với máy (D). Cả bốn — user trả lời `1a,b,c,d`.
- **Mặt LOẠI:** E "chỉ cần chạy được" — user không chọn, nên KHÔNG được rút gọn thành
  sửa mỗi file khuôn.
- **Bối cảnh bằng số:** 1 khuôn gốc + 8 file skill + 3 file mã sinh chuỗi + 3 file portable
  + 1 file test = **16 file**; khuôn có **5 thành phần**, dùng ở **7 chỗ**.
- **Mức đầu tư:** lane full (chuyên sâu) — spec → plan → implement → QC → report. Bốn mặt
  cùng chọn nghĩa là QC phải có hạng mục riêng cho từng mặt, không gộp.

**Mâu thuẫn phải gỡ ở vòng chi tiết.** User chọn 3B (nới luật, cho một bộ ký hiệu Unicode
cố định) NHƯNG cũng chọn 1B (tương thích ba mặt). Research kết luận với bullet Unicode đơn
lẻ (`• ▸ ➤`): rủi ro thấp nhưng **không có nguồn xác nhận trực tiếp** — font terminal của
người dùng có thể thiếu glyph → ra ô tofu `□`. Vậy 3B chỉ chốt được sau khi trả lời: lấy
bằng chứng render ở đâu ra.

### Lộ trình

| Bước/phase | Chạy? | Vì sao |
|---|---|---|
| Research web | ĐÃ XONG | 8 truy vấn, kết quả ở `docs/tdq/research/<slug>.md` — đây là ẩn số quyết định |
| Interview | ĐÃ XONG | 2 vòng (scope + chi tiết), hết chỗ đoán |
| Spec → plan → implement → QC → report | CÓ | khung bất biến, user chọn 4 mặt nên không cắt được bước nào |
| QC độc lập bằng agent `tdq-qc-tester` | CÓ | phạm vi đụng `hooks/` và `scripts/` — hỏng thì vỡ cả workflow, đáng một lượt kiểm độc lập |
| Review sâu bằng `tdq-reviewer` | BỎ | tuỳ chọn, user chưa yêu cầu |
| Kiểm bằng mắt trên ba mặt | BỎ | user chọn 2A — chỉ dùng cấu trúc/ký tự đã có bằng chứng, nên không cần user thao tác |
| Chia sub-agent | CHƯA QUYẾT | để cổng mode sau khi duyệt plan |

### Chốt kiến thức

- **Cách tiếp cận đã chọn:** trang trí bằng cấu trúc markdown đã xác nhận an toàn ở
  terminal (mặt khắt khe nhất) — in đậm nhãn trường, gạch đầu dòng, `inline code`, `---` —
  cộng đúng ba ký hiệu whitelist. Nhãn in đậm bọc **cả dấu hai chấm** (`**Mục tiêu:**`) để
  chuỗi con `Mục tiêu:` không đổi, giữ nguyên mặt D.
- **Đã loại:** màu (ANSI/HTML) — không có nguồn đảm bảo, gần như chắc ra ký tự rác ·
  cỡ chữ — không có cơ chế · bảng markdown trong khối chat — 5 issue lỗi · `~~` — in literal ·
  ký tự vẽ khung — lệch cột với tiếng Việt · heading làm phân cấp cỡ chữ — terminal chỉ ra bold.
- **Nguồn:** `docs/tdq/research/2026-08-14-trang-tri-khoi-chat.md`.

### Kiểm cổng

1. Làm ra gì: khuôn mới + 15 file đồng bộ + test siết whitelist. Rõ.
2. Cần model/download/cài đặt: KHÔNG — thuần sửa văn bản và chuỗi hằng.
3. Phạm vi QC: 10 hạng mục, mỗi mặt user chọn có ít nhất một hạng mục. Rõ.

## Hỏi đáp

### Vòng 1 — scope (2026-08-14)

| Câu hỏi | User trả lời | Hệ quả |
|---|---|---|
| 1. Request bao quanh mặt nào? | **A, B, C, D** (loại E) | Bốn mặt đều vào spec §6, mỗi mặt ≥ 1 dòng DoD |
| 2. Sửa tới đâu? | **A — cả ba nhóm** (8 skill + 3 file mã + 3 file portable) | `scripts/`, `hooks/`, `portable/` vào phạm vi. Khác hẳn request trước (chỉ `skills/`) |
| 3. Luật "Không emoji"? | **B — nới cho bộ ký hiệu Unicode cố định**, vẫn cấm emoji | Xem ghi chú dưới — rào cản là câu chữ trong khuôn, không phải cái test |

**Đã kiểm lại cái test, khác với phỏng đoán ban đầu.** `tests/test_user_facing_block.py:17`
cấm emoji bằng **dải mã**, không phải cấm mọi ký tự ngoài ASCII:
`[\U0001F300-\U0001FAFF☀-⛿✅❌⚠]` (tức U+1F300–U+1FAFF, U+2600–U+26FF, và 3 ký tự lẻ).
Các ký hiệu ứng viên `─` U+2500 · `│` U+2502 · `▸` U+25B8 · `•` U+2022 · `➤` U+27A4 đều
**nằm ngoài** các dải đó → test hiện tại đã cho qua sẵn. Vậy 3B thực chất là hai việc:
(1) sửa câu chữ luật trong khuôn từ "Không emoji" thành "Không emoji + chỉ được dùng bộ ký
hiệu liệt kê sau"; (2) siết test thành **whitelist** để ký hiệu ngoài danh sách bị chặn —
nếu không thì "nới" hoá ra là bỏ ngỏ, đúng thứ mặt C (chống trôi khuôn) muốn tránh.

### Vòng 2 — chi tiết (2026-08-14)

| Câu hỏi | User trả lời | Hệ quả |
|---|---|---|
| 1. Bộ ký hiệu được phép? | **A — bốn ký tự** `➤` `·` `▸` `—`, không ký tự cần căn cột | Loại hẳn nhóm vẽ khung `─ │ ├ └` |
| 2. Lấy bằng chứng render ở đâu? | **A — chỉ dùng thứ đã có bằng chứng chạy thật trong repo**, ký tự không có bằng chứng thì loại khỏi whitelist | Không cần user tự nhìn ba mặt |
| 3. Câu chữ có được viết lại? | **A — chỉ đổi trình bày**, giữ nguyên câu chữ và mọi chuỗi hook/test đang bắt | Thêm một hạng mục QC: 0 từ nội dung bị mất |

**Áp luật 2A vào đáp án 1A → `▸` bị loại.** Đã kiểm bằng lệnh:
`grep -c '▸' -r skills/ scripts/ hooks/ portable/` → **không có ở đâu cả**, tức `▸` là ký
tự MỚI, không có bằng chứng render. Ba ký tự còn lại đều đang chạy thật trong chuỗi in ra
cho user: `➤` và `·` ở `hooks/scripts/_common.py:181-183` và `scripts/tdq_state.py:586,690`,
`—` ở cùng các chuỗi đó cộng 26 file skill. Vậy **whitelist chốt là `➤` `·` `—`**. Đây là
hệ quả trực tiếp của chính luật 2A user chọn, không phải tôi tự thu hẹp.

**Chuỗi máy đang bắt (mặt D phải giữ nguyên) — đã grep, đúng ba nhóm:**
`➤ Duyệt: <hint> · Góp ý: nhắn trực tiếp` và `➤ Chọn cách làm: … · Góp ý: nhắn trực tiếp`
(sinh ở `hooks/scripts/_common.py:181-183`) · `plan đề xuất <nhãn mode>`
(`tests/test_context_hooks.py:170,175`) · lời chặn của `stop_gate.py:153` đòi in lại
"dòng ➤ Duyệt". Không có test nào bắt `Xem đầy đủ tại:` hay `- A (đề xuất):`, nhưng khuôn
vẫn giữ vì đó là bất biến do chính khuôn quy định.
