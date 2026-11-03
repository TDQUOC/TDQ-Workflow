# SPEC — Nội hoá luật Ponytail vào ruột TDQ-Workflow

Ngày: 2026-09-16 · Bản: 1.0 · Brief: ../brief/2026-09-16-2234-cong-sinh-ponytail-tdq.md · Lane: full
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md
Trạng thái: CHỜ DUYỆT

## Mục lục

- 1. Mục tiêu & phạm vi
- 1b. Lộ trình
- 2. Đầu ra cụ thể
- 2b. Ranh giới module
- 3. Cách tiếp cận & lý do
- 3b. Năng lực & công cụ
- 4. Yêu cầu bắt buộc
- 5. Ràng buộc & rủi ro
- 6. QC & Definition of Done
- 7. Câu hỏi còn mở

## 1. Mục tiêu & phạm vi

- **Mục tiêu:** đưa thang 7 bậc chống over-engineer của Ponytail cộng luật "chạy trước,
  refactor sau" thành luật RUỘT của TDQ-Workflow, và dựng kênh nạp để luật đó **có mặt trong
  ngữ cảnh ở mọi phiên, sau mọi lần compact, và ở đầu mỗi sub-agent** — thay vì nằm trong
  `skills/` chờ được nạp theo yêu cầu. Đo được bằng: chạy hook thật thì thấy thân luật trong
  đầu ra ở cả ba kênh, và hạ được cường độ bằng một khoá state 4 giá trị.
- Ponytail **không** được cài thêm như plugin thứ hai. Chữ thì vay, cơ chế thì TDQ tự dựng.

**Trong phạm vi** — sáu luồng L1–L6 ở §1b, gom thành 8 đầu ra ở §2:

- Thân luật tinh gọn viết một lần vào `skills/` (thang 7 bậc + bộ rule gọn + luật "chạy
  trước, refactor sau").
- Một bộ đọc-và-lọc thân luật theo mức gắt, các hook dùng chung.
- Ba kênh nạp: mỗi phiên + mỗi compact (`SessionStart`), một dòng nhắc ngắn khi phase
  `implement` (`UserPromptSubmit`), và đầu mỗi sub-agent (`SubagentStart` — sự kiện thứ năm).
- Khoá state `muc_gat` bốn giá trị `lite | full | ultra | off`, mặc định **`full`**.
- Một skill soi over-engineer ba chế độ `review | audit | debt`.
- Một phép kiểm sổ nợ cho marker `ponytail:` trong mã nguồn.

**NGOÀI phạm vi** — chép từ brief `### Phạm vi đã chốt`, mặt LOẠI:

- Món 7 "toả ra 9 host" của Ponytail — TDQ đã **sinh** bản ngoài bằng `scripts/build_portable.py`,
  lấy 9 bản viết tay là hạ cấp.
- `/ponytail-gain` — số benchmark của repo khác, và chính command đó cấm in số của repo thật.
- `/ponytail-help` và `/ponytail` — mức gắt đã có núm riêng là `muc_gat`.
- Miễn trừ "trivial one-liners need no test" — phán quyết 2 của người dùng đã loại.
- Dùng marker `ponytail:` để mở sàn `cyclomatic ≤ 10 / cognitive ≤ 15` — phán quyết 4 đã loại.
  Marker sống như **sổ nợ**, không phải giấy miễn trừ.
- Gỡ framework khỏi 1802 test cũ — chốt `3a`: phán quyết 1 chỉ áp cho check viết từ nay.
- Mọi việc dàn xếp với Ponytail-như-plugin-thứ-hai (dò xung đột hook, đọc
  `~/.config/ponytail/config.json`, ghim phiên bản) — sai đề, đã bỏ ở lượt sửa đề.
- Ghi bất cứ gì ra ngoài repo — chốt `5a`.
- **Viết trình kiểm `cyclomatic`/`cognitive`** — đo ngày 2026-09-16: grep
  `cyclomatic|cognitive|complexity` trong `scripts/*.py` và `hooks/scripts/*.py` ra **0 dòng**,
  tức sàn đó hôm nay là luật văn bản chưa có máy canh. Đây là việc THẬT còn thiếu, nhưng người
  dùng không yêu cầu ở lượt này và nó không thuộc món nào trong kiểm kê → ghi ra đây làm nợ,
  không làm lén.
- Dựng lại kho `docs/tdq/audit/skill-index.json` (nợ cũ, 284 test đỏ có sẵn) — xem §5.

## 1b. Lộ trình

Chép từ brief mục `### Lộ trình`. Người dùng duyệt spec là duyệt luôn lộ trình này.

**Sáu luồng tính năng**, mỗi luồng truy được về món trong bảng kiểm kê 8 món của brief:

| # | Luồng | Món | Chạm gì | Mới hay mở rộng |
|---|---|---|---|---|
| L1 | Thân luật tinh gọn: thang 7 bậc + rule gọn + "chạy trước, refactor sau" | 1, 8 | `skills/tdq-build/SKILL.md`, `skills/tdq-build/references/rules/chung.md` | Mở rộng |
| L2 | Kênh nạp always-on: thân luật vào mỗi phiên và mỗi compact | 2 | `hooks/scripts/session_start.py` | Mở rộng — hook đã khớp `compact` vì không khai matcher |
| L3 | Dòng nhắc ngắn khi phase `implement` | 2 | `hooks/scripts/prompt_context.py`, `hooks/scripts/_common.py` | Mở rộng — cơ chế `[TDQ:MÃ]` đã có |
| L4 | Luật xuống sub-agent | 3 | `hooks/hooks.json` + một file hook mới | **Mới** — sự kiện thứ năm |
| L5 | Bốn mức gắt `muc_gat`, mặc định `full`, lọc thân luật theo mức | 4 | `scripts/tdq_state.py`, `hooks/scripts/luat_gon.py` | Mở rộng state + một hàm lọc mới |
| L6 | Skill soi over-engineer + sổ nợ marker có cổng kiểm | 5, 6 | `skills/tdq-lean/SKILL.md`, `scripts/kiem_no_marker.py` | **Mới** |

**Hai chỗ L6 lệch khỏi brief, đo ngày 2026-09-16, sửa tại đây chứ không im lặng:**

1. Brief ghi L6 đi bằng `commands/` (thư mục mới). Tài liệu Claude Code xếp `commands/` là
   **khuôn CŨ** — nguyên văn "Skills as flat Markdown files. Use `skills/` for new plugins" —
   và cách đặt tên cho `commands/` **không có trong tài liệu** `[BÊN-THỨ-BA]`. Thêm nữa,
   `docs/kien-truc.md:13` ghi bản portable sinh từ `skills/`+`hooks/`+`agents/`+`scripts/`,
   **không có `commands/`** → command sẽ không tới được bản ngoài. Nên L6 đi bằng **một skill**.
2. Brief ghi cổng kiểm marker nới vào `scripts/doc_lint.py`. `doc_lint.py` lint file markdown,
   còn marker `ponytail:` nằm trong comment của file `.py` → sai miền. Nên là **một script nhỏ
   riêng**, đúng `docs/kien-truc.md:26`.

**Bảng bước/phase:**

| Bước/phase | Chạy? | Vì sao |
|---|---|---|
| analyze | CÓ (xong) | 3 vòng hỏi, 8 món kiểm kê, 2 premise bị phá và sửa tại chỗ |
| Research web thêm | BỎ | Đã 2 vòng (4 truy vấn nền + 6 câu cơ chế plugin) cộng một vòng đo khuôn command và trần hook ở phase này. Không còn `[CHƯA BIẾT]` nào chặn việc |
| Interview thêm | BỎ | Scope đã chốt ở 3 vòng; §7 rỗng |
| spec | CÓ | Chạm `hooks/`, `state.json`, `skills/` — ba vùng `docs/kien-truc.md` ràng chặt nhất |
| plan | CÓ | Khung bất biến |
| implement | CÓ | Khung bất biến |
| Cắt cho sub-agent | Để `tdq_bench.py` đo ở phase plan | Không đoán bằng mắt; `Mode thực thi` do người dùng chốt ở cổng mode |
| QC độc lập (agent `tdq-qc-tester`) | **CÓ** | Lượt này sửa mã thật và sửa hook — hook sai thì mọi request sau đều sai. Cần mắt thứ hai |
| Review sâu (`tdq-reviewer`) | BỎ | Chỉ gọi khi người dùng yêu cầu |
| report | CÓ | Khung bất biến |

## 2. Đầu ra cụ thể

| # | Đầu ra | Đường dẫn/vị trí | Đo "xong" bằng |
|---|---|---|---|
| 1 | Thân luật tinh gọn: câu luật tầng 1–2 trong thân skill, bảng 7 bậc + ví dụ trong reference giữa một cặp marker máy đọc được | `skills/tdq-build/SKILL.md`, `skills/tdq-build/references/rules/chung.md` | Khối giữa cặp marker chứa đủ 7 bậc và câu "chạy trước, refactor sau"; cả hai file không có dòng tiếng Việt ngoài marker miễn trừ |
| 2 | Bộ đọc + lọc thân luật theo mức gắt — hai hàm thuần, không class | `hooks/scripts/luat_gon.py` (mới) | Bốn mức cho bốn kết quả khác nhau; `off` ra rỗng; mức lạ ra như `full` |
| 3 | Thân luật vào ngữ cảnh mỗi phiên và mỗi lần compact | `hooks/scripts/session_start.py` | Chạy hook với `source=compact` thấy thân luật trong đầu ra; khối đầu vẫn trong trần cũ |
| 4 | Dòng nhắc ngắn mã `TDQ:GON` khi phase `implement` | `hooks/scripts/prompt_context.py`, `hooks/scripts/_common.py` | Phase `implement` có dòng đó, phase khác không có; danh sách mã đóng lên đúng 6 mã |
| 5 | Kênh nạp luật cho sub-agent, sự kiện thứ năm | `hooks/scripts/subagent_start.py` (mới), `hooks/hooks.json` | Hook nhận payload `SubagentStart` và in thân luật; khai báo lên 6 mục trên 5 sự kiện |
| 6 | Khoá state `muc_gat`, bốn giá trị, mặc định `full` | `scripts/tdq_state.py` | Đọc/ghi được qua CLI; khoá trống ra `full`; giá trị lạ ra `full`; bốn giá trị hợp lệ nhận được |
| 7 | Skill soi over-engineer ba chế độ `review` (soi diff) · `audit` (soi cả repo) · `debt` (gom marker thành sổ nợ) | `skills/tdq-lean/SKILL.md` (mới) | Ba mục chế độ có đủ; khai `argument-hint`; skill có mặt trong chỉ mục sau khi dựng lại kho |
| 8 | Phép kiểm sổ nợ marker `ponytail:` — một lệnh chạy được, không framework, không fixture | `scripts/kiem_no_marker.py` (mới) | Marker thiếu đường nâng → mã thoát khác 0 kèm `đường-dẫn:dòng`; marker đủ → mã 0; repo hiện tại → mã 0 |

## 2b. Ranh giới module

| Module | Vùng file | Phụ thuộc module | Đầu ra §2 nào |
|---|---|---|---|
| M1 thân-luật | `skills/tdq-build/SKILL.md`, `skills/tdq-build/references/rules/chung.md` | không | 1 |
| M2 bộ-đọc-lọc | `hooks/scripts/luat_gon.py` | M1 (đọc file của M1 lúc chạy) | 2 |
| M3 kênh-phiên | `hooks/scripts/session_start.py` | M2, M6 | 3 |
| M4 kênh-nhắc-ngắn | `hooks/scripts/prompt_context.py`, `hooks/scripts/_common.py` | M6 | 4 |
| M5 kênh-sub-agent | `hooks/scripts/subagent_start.py`, `hooks/hooks.json` | M2, M6 | 5 |
| M6 mức-gắt | `scripts/tdq_state.py` | không | 6 |
| M7 skill-soi | `skills/tdq-lean/SKILL.md` | không | 7 |
| M8 nợ-marker | `scripts/kiem_no_marker.py` | không | 8 |

Không hai module nào khai chung một đường dẫn. Vùng file trên chỉ kể **file sản phẩm**; file
test của từng module do phase `plan` đặt tên, vì tên test chỉ đúng được sau khi mã tồn tại
(luật R11 của `doc_lint`). Ranh giới đã tách rõ ở hai chỗ dễ trùng: ba assertion trần ngân sách
của kênh phiên thuộc **M3**, hành vi nhắc ngắn thuộc **M4**; khoá `muc_gat` do **M6** sở hữu,
ba kênh M3/M4/M5 chỉ ĐỌC qua CLI.

M1, M2, M6, M7, M8 không phụ thuộc lẫn nhau → cắt song song được. M3, M4, M5 phải chờ M2 và M6.

## 3. Cách tiếp cận & lý do

- **Chọn:** luật viết **một lần** vào `skills/`, các hook **đọc từ đĩa** rồi lọc theo mức gắt —
  không chép lại chữ luật vào mã. Ba kênh nạp là **mở rộng hai hook có sẵn + thêm một hook**.
  Mức gắt là **một khoá state**, bộ lọc là **hai hàm thuần** trong một module mới.
- **Vì:**
  - Bậc 2 của chính thang đang nội hoá — mở rộng chỗ đúng thay vì dựng tầng mới. Đo được:
    `hooks/hooks.json` khai `SessionStart` **không có matcher** nên nó đã khớp mọi source kể cả
    `compact` `[XÁC THỰC]`; `hooks/scripts/_common.py:126` đã có sẵn cơ chế nhắc mã kèm dedupe.
  - Luật chép hai chỗ thì lệch — `docs/kien-truc.md:24` nói đúng câu đó, và report lượt trước đã
    bắt được Ponytail lệch chữ giữa hai bản viết tay của chính nó.
  - Món 8 của người dùng: hàm thuần, không class, không namespace mới, một tính năng lần theo
    được từ khoá state tới dòng in ra.
  - Món 1 mà không có món 2 thì chỉ là thêm chữ vào một file skill — luật nằm trong `skills/`
    nạp theo yêu cầu, không được nhắc lại thì trôi sau mỗi lần compact.
- **Đã loại:**
  - `.claude/rules/*.md` làm nền — plugin **không ship được** rule file `[XÁC THỰC]`: `plugin.json`
    không có khoá rule, `.claude/rules/` chỉ quét ở `~/.claude/` và gốc project. Đây chính là
    premise bị phá của lựa chọn `2c`; người dùng chốt lại `5a`.
  - Chèn toàn thân luật **mỗi lượt** qua `UserPromptSubmit` như Ponytail làm — đắt mà không cần:
    `SessionStart` đã khớp `compact`, nên mỗi-phiên + mỗi-compact là đủ để luật không trôi. Thêm
    nữa `UserPromptSubmit` chia ngân sách timeout 30s với mọi hook khác. **Đây là chỗ tôi báo giá
    sai cho người dùng ở phase analyze** ("~110 dòng × mỗi lượt"); giá thật thấp hơn nhiều.
  - Ba file `commands/*.md` — `commands/` là khuôn cũ theo tài liệu, cách đặt tên không có tài
    liệu, và bản portable không sinh từ `commands/`. Xem §1b mục 1.
  - Ba skill riêng cho ba chế độ — bậc 1: ba cửa cho ba việc đọc chung một thân luật là thừa.
    Một skill `tdq-lean` với `argument-hint: "[review|audit|debt]"` làm đủ cả ba.
  - Nới `scripts/doc_lint.py` để quét marker trong mã nguồn — kéo một dụng cụ đúng ra khỏi miền
    của nó. Xem §1b mục 2.
  - Đổi tên marker `ponytail:` thành tên TDQ — không ai yêu cầu, và giữ tên là ghi công đúng
    nguồn. Đã ghi ở brief để người dùng phủ quyết bằng một chữ.

## 3b. Năng lực & công cụ

| Skill | Nguồn | Phán quyết | Dùng ở đâu / Lý do loại |
|---|---|---|---|
| tdq-lsp-setup | plugin:tdq-workflow | DÙNG | thang 7 bậc lớp tìm kiếm + bảng ưu tiên tìm kiếm, dùng khi dựng `Chạm:` cho M3/M4 (hook có 9 ref mà grep hẹp trượt hết) |
| tdq-status | plugin:tdq-workflow | DÙNG | mặt hiển thị trạng thái — nơi phơi khoá `muc_gat` của đầu ra 6 |
| tdq-check-status | plugin:tdq-workflow | DÙNG | đọc đĩa trực tiếp, dùng để đối chiếu `muc_gat` trong state với giá trị hook thật nhận được |
| tdq-conventions | plugin:tdq-workflow | NỀN | luật gốc `soul.md`, tầng ngôn ngữ, giao thức duyệt |
| tdq-intake | plugin:tdq-workflow | NỀN | phase analyze đã xong |
| tdq-spec | plugin:tdq-workflow | NỀN | phase này |
| tdq-plan | plugin:tdq-workflow | NỀN | phase kế tiếp |
| tdq-build | plugin:tdq-workflow | NỀN | implement → qc → report; cũng là file bị sửa ở M1 |
| Đã xét 2 skill khác | user/built-in | KHÔNG | khác lĩnh vực |

## 4. Yêu cầu bắt buộc

- **Log service bật mặc định:** ba kênh nạp mỗi lần chạy ghi một dòng vào **sổ lượt có sẵn**
  (`turn_log_append` trong `scripts/tdq_state.py`), có timestamp, ghi rõ kênh nào, mức gắt nào,
  bao nhiêu dòng luật đã chèn — đủ để về sau trả lời "vì sao lượt đó luật không có mặt". Núm
  tắt là `muc_gat=off`: tắt kênh thì tắt luôn dòng log của kênh. Không dựng sổ log thứ hai.
- Không placeholder, không TODO stub, không mock trình bày như dữ liệu thật.
- **Mỗi thành phần có unit test riêng, chạy được bằng một lệnh, đi red → green** — phán quyết 2
  của người dùng: **không có miễn trừ**, kể cả cho hàm một dòng.
- **Phép kiểm viết thêm phải gọn** — phán quyết 1, theo `~/Documents/ponytail/AGENTS.md:30`:
  một lệnh chạy được, không dựng framework, không dựng fixture. Hai phán quyết này không đánh
  nhau: test **có**, nhưng viết gọn.
- Code viết ra bám 5 nguyên tắc SOLID theo `skills/tdq-conventions/references/clean-code.md` và
  bám rule ngôn ngữ trong `skills/tdq-build/references/rules/`. Sàn `cyclomatic ≤ 10 /
  cognitive ≤ 15` là **sàn không thương lượng** (phán quyết 4) — marker `ponytail:` không mở
  được sàn này.
- **Thứ tự làm việc, luật món 8 của người dùng:** làm cho chạy trước, refactor sau; code đơn
  giản nhất và đi thẳng nhất có thể; không thêm namespace/class/hàm mà tính năng không cần.

## 5. Ràng buộc & rủi ro

Ràng buộc kiến trúc phải giữ (chép từ `docs/kien-truc.md`, chỉ những dòng việc này chạm tới):

- `docs/kien-truc.md:12` — "Luật · `skills/` · văn bản chỉ dẫn model; không chạy được, không có
  trạng thái" → chạm ở M1: thân luật là markdown thuần, mọi cơ chế nằm ở M2/M3/M4/M5.
- `docs/kien-truc.md:13` — bản ngoài `portable_claude/`, `portable_codex/` **SINH** bằng
  `scripts/build_portable.py` từ `skills/`+`hooks/`+`agents/`+`scripts/`, **không sửa tay** →
  lượt này sửa cả `skills/` và `hooks/` nên bắt buộc sinh lại, và cấm sửa tay bản sinh.
- `docs/kien-truc.md:15` — "5 hook cắm vào Claude Code" → M5 làm số này thành **6 hook trên 5
  sự kiện**; chính dòng tài liệu đó phải được cập nhật trong lượt này.
- `docs/kien-truc.md:25` — chỉ `scripts/tdq_state.py` được ghi `docs/tdq/state.json` → M6 thêm
  khoá `muc_gat` ở đó; M3/M4/M5 chỉ đọc.
- `docs/kien-truc.md:26` — file code MỚI bắt buộc nằm trong `scripts/` hoặc `hooks/` → M2 và M5
  vào `hooks/scripts/`, M8 vào `scripts/`.
- `docs/kien-truc.md:49` — `soul.md` là luật gốc, đổi soul phải có user duyệt → lượt này
  **KHÔNG chạm** `soul.md`.
- `docs/kien-truc.md:51` — luật trong `skills/` viết **tiếng Anh** cố định → M1 và M7 viết tiếng
  Anh; spec/plan/report vẫn tiếng Việt.
- `skills/tdq-conventions/references/soul.md:99` — luật tầng 1 và 2 phải nằm trong **thân** một
  skill, chỉ luật tầng 3 và bảng chi tiết được đẩy vào file reference → buộc M1 chia hai chỗ:
  câu luật vào thân `SKILL.md`, bảng 7 bậc + ví dụ vào `chung.md`. Cùng dòng đó nói thêm: chạm
  trần dòng của skill thì **nâng trần**, không nén luật cho vừa.
- `hooks/scripts/_common.py:70` — "The CLOSED list of codes (spec §2.1). Adding a new code means
  editing the spec first." → **spec này khai mã thứ sáu `TDQ:GON`**, dùng cho đầu ra 4. Đây là
  chỗ ràng buộc đòi spec phải nói trước khi mã được thêm.
- `hooks/scripts/session_start.py:8` — trần ngân sách hiện tại "≤ 12 dòng / 600 ký tự (spec
  §2.7)", khoá bằng **ba assertion** trong hai file test của tầng hook (đo `len(out) <= 600` trên
  đầu ra `session_start`) → thân luật ~110 dòng **không lọt trần này**. Cách xử đã chốt: **giữ nguyên trần 12 dòng/600
  ký tự cho KHỐI ĐẦU** (dòng luật tuân thủ + khối `next`, phần không được phép bị cắt), và khai
  **trần riêng cho khối thân luật** đứng sau nó: ≤ 140 dòng / 7000 ký tự cho toàn bộ đầu ra.
  Ba assertion kia được sửa để đo khối đầu, có ghi chú lý do và ngày tại chỗ.
- Không cần model, không tải về, không cài đặt gói nào. Không thêm dependency ngoài stdlib.
  Không ghi bất cứ gì ra ngoài repo (chốt `5a`).

| Rủi ro | Ảnh hưởng | Cách giảm |
|---|---|---|
| Hook của plugin chạy **hai lần** với 2 PID (bug #10871) | thân luật chèn hai lần, tốn ngữ cảnh gấp đôi | Mỗi kênh dedupe theo lượt như `already_reminded` đang làm; một hạng mục QC đo số lần thân luật xuất hiện |
| Hook plugin **khai đúng mà không chạy** (bug #10225) | khai báo xanh, hiệu ứng bằng 0 | Mọi hạng mục QC đo bằng **đầu ra thật của hook**, cấm kết luận từ dòng khai trong `hooks.json` |
| `additionalContext` của sub-agent **bị prune**, non-compliance đo được 40–60% (issue #23885) | M5 không bảo đảm sub-agent tuân luật | Khai rõ ngay trong tài liệu: M5 là **lời nhắc, không phải hàng rào**; không đặt DoD nào dựa vào việc sub-agent tuân thủ |
| Nạp ~110 dòng luật mỗi phiên và mỗi compact làm phình ngữ cảnh | tốn token mọi phiên | Bốn mức gắt là núm hạ thật: `lite` cắt bảng cường độ, `off` tắt hẳn. Soul xếp chất lượng > context cost nên mặc định vẫn `full` |
| `UserPromptSubmit` chia **ngân sách 30s** với mọi hook khác, fail-open | hook chậm làm trôi lượt | M4 chỉ in một dòng ngắn ≤ 3 dòng/200 ký tự, **không đọc thân luật** |
| Sửa ba assertion trần 600 ký tự | có thể che một hồi quy thật | Trần cũ **giữ nguyên nguyên số** trên khối đầu; chỉ khối thân luật có trần riêng. Không hạ số nào |
| Skill thứ 9 phải có mặt trong `docs/tdq/audit/skill-index.json` — kho này commit 2026-08-18, còn ghi home cũ, đang làm 284 test đỏ | M7 có thể "xong" mà không ai tìm ra skill | Một hạng mục QC đòi skill mới xuất hiện sau khi dựng lại kho; **sửa gốc nợ 284 test đỏ nằm NGOÀI phạm vi**, đối chiếu baseline `main` như lượt trước |
| Đọc file luật lúc chạy hook → file bị đổi tên hoặc marker bị xoá thì kênh im lặng | luật mất mà không ai biết | Thiếu marker → hook in một dòng cảnh báo và trả mã 0 (fail-open, không chặn lượt); một hạng mục QC đo đúng trường hợp này |
| Bốn mức gắt đọc lỗi | có thể tụt về `off` và tắt luật lặng lẽ | **Fail-closed về `full`**, không bao giờ về `off` — giá trị lạ, khoá trống, file lỗi đều ra `full` |

## 6. QC & Definition of Done

| # | Hạng mục kiểm | Điều kiện PASS |
|---|---|---|
| Q1 | Thân luật có mặt và đúng chỗ | Khối giữa cặp marker trong `chung.md` chứa đủ 7 bậc theo thứ tự; câu luật "chạy trước, refactor sau" và câu bậc 1 nằm trong **thân** `SKILL.md` chứ không trong reference; cả hai file không có dòng tiếng Việt nào thiếu marker miễn trừ |
| Q2 | Bộ lọc theo mức gắt | Bốn mức cho bốn số dòng khác nhau; `full` giữ đủ 7 bậc; `off` trả về rỗng; mức lạ, chuỗi rỗng và `None` đều trả về y như `full` |
| Q3 | Kênh phiên chèn thật, kể cả sau compact | Chạy hook với payload `source=compact` thấy thân luật trong đầu ra; cũng thấy với `startup` và `resume`; khối đầu vẫn ≤ 12 dòng / 600 ký tự; toàn bộ đầu ra ≤ 140 dòng / 7000 ký tự |
| Q4 | Kênh nhắc ngắn | Ở phase `implement` đầu ra chứa mã `TDQ:GON`; ở các phase khác không chứa; dòng nhắc ≤ 3 dòng / 200 ký tự; danh sách mã đóng có đúng 6 mã |
| Q5 | Kênh sub-agent | Hook nhận payload sự kiện `SubagentStart` và in thân luật đã lọc; `hooks.json` khai 6 mục trên 5 sự kiện và đọc được bằng máy; payload thiếu khoá → mã thoát 0 và không in rác |
| Q6 | Khoá mức gắt | Đọc/ghi được qua CLI state; khoá trống ra `full`; giá trị lạ ra `full`; bốn giá trị hợp lệ nhận đủ; không file nào ngoài `scripts/tdq_state.py` ghi vào `docs/tdq/state.json` |
| Q7 | Skill soi over-engineer | File có ba mục chế độ `review`/`audit`/`debt`, khai `argument-hint` liệt kê đúng ba chế độ, viết tiếng Anh; sau khi dựng lại kho chỉ mục thì skill mới có mặt trong đó |
| Q8 | Phép kiểm sổ nợ marker | Marker `ponytail:` thiếu đường nâng → mã thoát khác 0 và in đúng `đường-dẫn:dòng`; marker có đường nâng → mã 0; chạy trên repo hiện tại → mã 0; phép kiểm không import framework test nào và không cần fixture |
| Q9 | Đo bằng hiệu ứng, không tin lời khai | Cả ba kênh được kết luận từ **đầu ra thật của hook khi chạy**, không từ dòng khai trong `hooks.json`; thân luật xuất hiện **đúng một lần** mỗi lần nạp |
| Q10 | Bản ngoài khớp bản gốc | `portable_claude/` và `portable_codex/` chứa thân luật mới; cả hai được **sinh lại**, không có dấu sửa tay; `docs/kien-truc.md:15` đã đổi từ 5 hook sang 6 hook trên 5 sự kiện |
| Q11 | Suite không xấu đi | Tập tên test đỏ trên nhánh **lệch 0** so với baseline trên `main` sạch, cả hai chiều; ba assertion trần bị sửa đều có ghi chú lý do và ngày ngay tại dòng sửa |
| Q12 | Không rò ra ngoài repo | Không đường dẫn nào ngoài cây repo bị ghi; `~/Documents/ponytail` không có file nào bị đổi |
| Q13 | Luật món 8 được giữ khi viết mã | Mỗi file mã mới không có class nào mà tính năng không cần; mỗi tính năng lần được từ khoá state tới dòng in ra trong **không quá 3 nhịp gọi**; mọi hàm mới trong sàn `cyclomatic ≤ 10 / cognitive ≤ 15` |

**DoD** — xong khi cả 13 điều dưới đây đúng, mỗi điều kiểm được bằng một lệnh:

1. Tám đầu ra ở §2 đều tồn tại, không rỗng, ở đúng đường dẫn đã khai.
2. Thân luật tinh gọn có đủ 7 bậc cộng luật "chạy trước, refactor sau", chia đúng hai chỗ theo
   `soul.md:99`.
3. Ba kênh nạp đều chèn thân luật thật khi chạy hook, kể cả kênh phiên với `source=compact`.
4. Khoá `muc_gat` có bốn giá trị, mặc định `full`, và mọi đường lỗi đều fail-closed về `full`.
5. Skill `tdq-lean` có ba chế độ và có mặt trong chỉ mục skill sau khi dựng lại kho.
6. Phép kiểm sổ nợ marker chạy được bằng một lệnh, không framework, không fixture, và xanh trên
   repo hiện tại.
7. Mỗi module M1–M8 có unit test riêng, đi red → green, không module nào được miễn.
8. Ngân sách được giữ: khối đầu của kênh phiên ≤ 12 dòng / 600 ký tự; dòng nhắc ngắn ≤ 3 dòng /
   200 ký tự; toàn bộ đầu ra kênh phiên ≤ 140 dòng / 7000 ký tự.
9. Danh sách mã đóng có đúng 6 mã, và spec này là chỗ khai mã thứ sáu.
10. Bản `portable_claude/` và `portable_codex/` được sinh lại và chứa luật mới; không sửa tay.
11. `docs/kien-truc.md` đã cập nhật số hook.
12. Tập test đỏ lệch 0 so với baseline `main`; ba assertion trần bị sửa có ghi chú lý do + ngày.
13. Không có gì được ghi ra ngoài repo, và repo Ponytail không bị sửa dòng nào.

## 7. Câu hỏi còn mở

(Rỗng.)
