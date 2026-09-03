# BRIEF — Ưu tiên dùng ui-ux-pro-max cho các case UI/UX phù hợp
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## Nguyên văn

> okay vậy hãy mở request bổ sung cho tdq-workflow alf nếu những case phù hợp này thì có thể ưu
> tiên dùng ui-ux-pro-max để có thể bổ trợ cho bộ ui ux chỉnh chu hơn

Ngữ cảnh trước đó trong cùng phiên: user hỏi ui-ux-pro-max là gì, làm được gì, phủ được những
nền tảng nào, và có bổ trợ cho mọi case UI/UX không. Kết luận đã trình bày và user đã đọc:
plugin này mạnh ở TẦNG QUYẾT ĐỊNH THIẾT KẾ (style, màu, font, token, component, luật theo
framework), yếu ở tầng chiến lược sản phẩm và không có tầng kiểm chứng trên máy thật.

**Đọc lần đầu của tôi**

- **Mục tiêu:** bổ sung luật vào bộ tdq-workflow để khi công việc rơi vào case UI/UX phù hợp
  thì ưu tiên nạp `ui-ux-pro-max`, nhằm đầu ra giao diện chỉn chu hơn.
- **Phạm vi đoán:** `skills/tdq-conventions/references/plugin-routing.md` là nhà tự nhiên —
  bảng routing ở đó hiện **không có dòng nào cho UI/UX** (chỉ có `figma` cho design-to-code).
  Có thể còn chạm tới bảng năng lực §3b của spec và pha build.
- **Chỗ chưa rõ:**
  1. "Case phù hợp" định nghĩa bằng gì — chỉ một dòng trong bảng routing, hay một khối luật
     riêng nói rõ khi nào dùng / khi nào không?
  2. Có cần ghép với `figma`, `frontend-design`, `chrome-devtools-mcp` (tầng kiểm chứng) thành
     một chuỗi, hay chỉ khai báo mỗi ui-ux-pro-max?
  3. Luật này chỉ nằm trong skill, hay còn phải xuất hiện trong ba bundle portable?
  4. Có ràng buộc "ưu tiên" ở mức nào: gợi ý mềm, hay bắt buộc như luật LSP+lumen?

## Hiểu & kiến thức

### Năng lực dùng được

Phân vân → DÙNG. Kiểm kê ngày 2026-09-03: 217 skill trên đĩa, cộng skill built-in trong
context. Không xoá bảng này kể cả khi không có dòng DÙNG nào.

| Skill | Nguồn | Phán quyết | Dùng ở đâu / Lý do loại |
|---|---|---|---|
| tdq-conventions | plugin:tdq-workflow | NỀN | luật gốc, chứa `plugin-routing.md` — nhà của luật mới |
| tdq-intake / spec / plan / build | plugin:tdq-workflow | NỀN | pipeline đang chạy |
| ui-ux-pro-max (7 skill) | plugin:ui-ux-pro-max | DÙNG | chính là đối tượng của request; đọc mô tả + dữ liệu để viết tiêu chí "case phù hợp" |
| frontend-design | plugin:frontend-design | DÙNG | chồng lấn với `ui-styling`; luật mới phải nói rõ khi nào chọn cái nào |
| figma | plugin:figma | DÙNG | đã có dòng routing riêng; luật mới phải không mâu thuẫn |
| chrome-devtools-mcp | plugin:chrome-devtools-mcp | DÙNG | có `a11y-debugging` + lighthouse — ứng viên cho tầng kiểm chứng mà ui-ux-pro-max thiếu |
| các skill `unity-*`, `ui-ugui/uitk/imgui` | user | KHÔNG | khác lĩnh vực — ui-ux-pro-max không có dữ liệu game |
| Đã xét 205 skill khác | user/plugin/built-in | KHÔNG | khác lĩnh vực |

### B1 — Đã đọc gì

- `skills/tdq-conventions/references/plugin-routing.md` — bảng routing 22 dòng. **Không có
  dòng nào cho UI/UX**; `figma` chỉ phủ design-to-code. Dòng cuối bảng: việc không khớp dòng
  nào thì làm bằng tool sẵn có, không kéo plugin vào cho tốn context.
- `skills/tdq-build/references/rules/index.md` + `html.md` — tầng luật theo NGÔN NGỮ, nạp khi
  ghi file. `html.md` có nhắc alt/label (a11y) nhưng không có gì về thiết kế thị giác.
- `scripts/skill_inventory.py` — công cụ của bước B0.
- Nguồn của ui-ux-pro-max: `src/ui-ux-pro-max/data/*.csv`, `scripts/search.py`, 7 SKILL.md.

### B2 — Số đo về ui-ux-pro-max (đếm trực tiếp, không lấy từ README)

- 88 style (50 `active`, 29 `supplemental`, 9 `deprecated`), 192 bảng màu, 74 cặp font,
  119 nguyên tắc UX, 25 loại biểu đồ, 22 stack.
- 22 stack chia: **12 web** (nextjs 61 dòng, react 61, shadcn 68, nuxt-ui 70, vue 49,
  svelte 55, angular 50, astro 53, nuxtjs 67, html-tailwind 59, laravel 50, threejs 53) ·
  **5 desktop** (javafx 75 — sâu nhất cả bộ, winui 59, uno 59, wpf 56, avalonia 56, uwp 55) ·
  **4 mobile** (jetpack-compose 52, flutter 52, react-native 51, swiftui 50).
- 119 nguyên tắc UX chia theo nền tảng: All 62 · Web 47 · Mobile 8 · VisionOS 2 →
  **luật UX dùng chung nghiêng hẳn về web**, dù luật theo framework thì cân cho cả ba nhóm.
- `stacks/nextjs.csv` gắn `Verified At: 2026-08-13` cho cả 60 dòng — dữ liệu còn mới.
- **Không có dòng nào cho Unity/Unreal** → không giẫm lên 31 skill `unity-*`.

### B3 — Một defect phát hiện trong lúc phân tích

`scripts/skill_inventory.py` **không nhìn thấy plugin ui-ux-pro-max**: chạy `--tat-ca` ra 0
dòng nguồn `plugin:ui-ux-pro-max`. Nguyên nhân xác định ở dòng 179 — hàm quét ghép đường dẫn
`<installPath>/skills`, trong khi plugin này để skill ở `<installPath>/.claude/skills/`.
Quét toàn bộ plugin đã bật: **chỉ đúng một plugin này bị**, các plugin khác đều có `skills/`.

Hệ quả đúng với request: bước B0 của mọi request về sau sẽ **không bao giờ liệt kê**
ui-ux-pro-max, nên dù có thêm dòng routing thì bảng năng lực §3b vẫn khuyết nó.

### B4 — Bốn lựa chọn cho hình hài luật mới

- **L1 — một dòng bảng routing.** Rẻ nhất, nhưng bảng routing chỉ nói "việc này thì dùng
  plugin kia", không diễn đạt được "chỉ tầng quyết định thiết kế, không tầng kiểm chứng".
- **L2 — dòng routing + một khối luật riêng** nêu rõ ba tầng (chiến lược / quyết định thiết
  kế / kiểm chứng), ui-ux-pro-max chỉ phủ tầng giữa, tầng ba chuyển cho chrome-devtools-mcp.
- **L3 — như L2, cộng luật ở tầng ngôn ngữ** (`rules/html.md`, `typescript-js.md`): ghi file
  giao diện thì nạp thêm ui-ux-pro-max, giống cách LSP+lumen là luật bắt buộc khi tìm ký hiệu.
- **L4 — như L3, cộng vá `skill_inventory.py`** để B0 nhìn thấy plugin (defect B3).

### Lộ trình

- `analyze` (đang chạy) → `spec` → `plan` → `implement` → `qc` → `report`.
- **Không có pha `diagram`**: pha này đã bị gỡ khỏi workflow ngày 2026-09-01
  (`scripts/tdq_state.py:73-82`, `PHASE_DA_GO = {"diagram": "spec"}`). Văn bản trong
  `skills/tdq-spec/SKILL.md` và `tdq-intake/SKILL.md` vẫn còn nhắc pha này — đó là chỗ luật
  chưa dọn theo mã, không phải bước bị bỏ sót ở request này.
- Request này sửa TÀI LIỆU LUẬT là chính, nên pha `implement` nhẹ; trọng lượng dồn vào việc
  định nghĩa tiêu chí "case phù hợp" cho chuẩn ở pha `spec`.

## Hỏi đáp

Nguyên văn câu trả lời của user:

> 1a bổ sung vào để claude biết nó như một bộ đề xuất cho claude code check khi cần dùng 2a 3a
> vẫn cho phép colapse với skill khác nếu 2 cái bổ trợ đc để tạo chất lượng tốt hơn 4a

**1 → A (L2), kèm bổ sung.** Một dòng bảng routing + khối luật riêng nêu ba tầng. Bổ sung của
user: viết sao cho Claude hiểu ui-ux-pro-max là **một BỘ ĐỀ XUẤT để tra khi cần**, không phải
một bước bắt buộc phải chạy. Chữ dùng trong luật phải mang nghĩa "tra cứu / đối chiếu", không
mang nghĩa "thực thi".

**2 → A.** Gợi ý mạnh: mặc định nạp khi trúng case, được phép bỏ qua nếu nêu lý do một dòng.

**3 → A, kèm bổ sung.** Phạm vi là mọi giao diện người dùng thật (web, mobile, desktop), loại
trừ Unity/game. Bổ sung của user: **cho phép ghép với skill khác** khi hai bên bổ trợ nhau để
ra chất lượng tốt hơn — không được viết luật theo kiểu loại trừ lẫn nhau. Cụ thể là các cặp
đã nêu ở B0: `frontend-design`, `figma`, `chrome-devtools-mcp` (tầng kiểm chứng).

**4 → A.** Luật xuống cả ba bundle portable bằng cách dựng lại, kiểm CLEAN.

Không còn câu hỏi mở.
