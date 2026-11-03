# BRIEF — Cộng sinh Ponytail với TDQ-Workflow
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

Slug: `2026-09-16-2234-cong-sinh-ponytail-tdq` · lane full · loại `feature` ·
nhánh `feature/cong-sinh-ponytail-tdq` → hợp về `main`.

## Nguyên văn

Lượt mở request (nguyên văn người dùng):

> okay vậy mở request deep để có thể combine ponytail vào tdq workflow biết giữ đúng phase
> và gate của tdq-workflow còn những luật trái nhau thì chọn AGENTS.md:30 "ONE runnable
> check … no frameworks, no fixtures"; CLAUDE.md: "Mỗi task có unit test, đi theo red →
> green" — không có miễn trừ; CLAUDE.md: "Sản phẩm build ra luôn có log service bật mặc
> định… tắt được qua config"; ngưỡng cyclomatic ≤ 10 / cognitive ≤ 15, bạn chốt 2a là sàn
> không thương lượng

Lượt chốt cách đóng request cũ: `1A` — commit 9 file `docs/`, hợp `feature/hop-ponytail-vao-tdq`
về `main`, rồi mở request mới trên cây sạch. Đã làm: commit `6fb9970`, hợp `4faed21`, nhánh cũ
đã xoá, chưa push.

Lượt sửa hướng (nguyên văn người dùng, 2026-09-16):

> có vẻ đang không đúng ý tôi. Tôi muốn request này là sẽ lấy những behavior, skill, rule, hook
> ổn của ponytail để đưa vào tdqworkflow và cho nó thành một phần của tdq-workflow để hoạt động
> đưa ra kết quả ổn hơn, hãy phân tích lại và đưa lại list câu hỏi mới

### Tôi đọc yêu cầu thế nào

**BẢN ĐẦU SAI ĐỀ — giữ lại để thấy chỗ lệch.** Tôi đã đọc thành "hai plugin cùng cài trên một
máy, dựng lớp tương thích". Người dùng sửa: đây là **nội hoá**. Lấy behavior · skill · rule ·
hook nào tốt của Ponytail, **đưa vào thành ruột của TDQ-Workflow**, để TDQ ra kết quả tốt hơn.
Ponytail không cần tồn tại như plugin thứ hai.

**Mục tiêu (bản đã sửa):** TDQ-Workflow hấp thu phần tốt của Ponytail, giữ nguyên khung phase và
hai cổng duyệt. Đích không phải "cùng chạy được" mà là **TDQ ra kết quả tốt hơn** — cụ thể là
bớt over-engineer, vì đó là điều Ponytail làm được mà TDQ hôm nay không làm.

**Cái gì chết theo lần sửa đề này** (đã đo, không còn chịu tải thiết kế): dò xung đột hook plugin
ngoài · một núm mức gắt đọc `~/.config/ponytail/config.json` · `AGENTS.md` bị hai nguồn cùng ghi ·
ghim bản Ponytail · phép đo "hai `additionalContext` cùng sự kiện nối hay ghi đè". Không còn bên
thứ hai nào chạy thì không có gì để dàn xếp.

**Một chỗ tôi tự sửa lỗi của chính mình:** ở request trước tôi nói luồng 3 (hook `SubagentStart`
của TDQ) **phải xoá** vì trùng `~/Documents/ponytail/hooks/ponytail-subagent.js`. Dưới đề bài
nội hoá, lập luận đó **sai**: không cài Ponytail thì không có file nào để trùng, và TDQ **phải**
tự có hook đó nếu muốn luật xuống tới sub-agent. Phản đối trùng lặp chết theo.

**Bốn phán quyết đã chốt sẵn, không hỏi lại:**

| # | Chỗ trái nhau | Bên thắng | Hệ quả |
|---|---|---|---|
| 1 | Hình dạng phép kiểm | **Ponytail** — one runnable check, no frameworks, no fixtures | Check viết thêm phải gọn, không dựng fixture |
| 2 | Có được miễn test không | **TDQ** — mỗi task một unit test red→green, không miễn trừ | Bỏ hẳn "trivial one-liners need no test" |
| 3 | Log service | **TDQ** — bật mặc định, tắt được qua config | "No boilerplate nobody asked for" không áp lên log service |
| 4 | Ngưỡng phức tạp | **TDQ** — `cyclomatic ≤ 10 / cognitive ≤ 15` là sàn | Comment `ponytail:` không mở được sàn này |

**Chỗ tôi CHƯA dám tự hiểu** (sẽ hỏi, không đoán bù): phán quyết 1 và 2 đứng cạnh nhau thì
suite `unittest` **1802 test đang có** thuộc diện nào — giữ nguyên và luật mới chỉ áp cho check
viết thêm từ nay, hay có hàm ý gỡ dần framework khỏi các check cũ.

## Hiểu & kiến thức

### Năng lực dùng được

Phân vân → DÙNG. Kiểm kê ngày 2026-09-16: 8 skill trên đĩa lọt bộ lọc (ẩn 2), cộng skill
built-in trong context. Không xoá bảng này kể cả khi không có dòng DÙNG nào.

| Skill | Nguồn | Phán quyết | Dùng ở đâu / Lý do loại |
|---|---|---|---|
| tdq-lsp-setup | plugin:tdq-workflow | DÙNG | chứa bậc 6 `bac6_hook_xung_dot` — bộ dò xung đột plugin ngoài đã có sẵn, là chỗ mở rộng thay vì viết mới |
| tdq-status | plugin:tdq-workflow | DÙNG | mặt hiển thị trạng thái; nếu chọn mặt UX thì đây là nơi phơi cả hai núm mức gắt |
| tdq-check-status | plugin:tdq-workflow | DÙNG | đọc đĩa trực tiếp — dùng khi cần đối chiếu state TDQ với kho cấu hình của Ponytail |
| tdq-conventions | plugin:tdq-workflow | NỀN | luật gốc `soul.md`, tầng ngôn ngữ, giao thức duyệt |
| tdq-intake | plugin:tdq-workflow | NỀN | phase analyze này |
| tdq-spec | plugin:tdq-workflow | NỀN | phase kế tiếp |
| tdq-plan | plugin:tdq-workflow | NỀN | phase kế tiếp |
| tdq-build | plugin:tdq-workflow | NỀN | implement → qc → report |
| Đã xét 2 skill bị lọc ẩn + skill built-in | user/built-in | KHÔNG | khác lĩnh vực |

### Bản đồ mã đã đọc

Hình dạng TDQ hôm nay, đo ngày 2026-09-16:

- **Hook TDQ:** 5 mục trên 4 sự kiện — `SessionStart` (1), `UserPromptSubmit` (1),
  `PreToolUse` (2, matcher `Edit|Write|MultiEdit|NotebookEdit` và `Bash`), `Stop` (1).
  `[XÁC THỰC]` đọc từ `hooks/hooks.json`; khớp `docs/kien-truc.md:15`.
- **Hook Ponytail trên Claude Code:** 3 sự kiện — `SessionStart` (matcher
  `startup|resume|clear|compact`), `SubagentStart`, `UserPromptSubmit`, mỗi cái timeout 5s.
  `[XÁC THỰC]` đọc từ `~/Documents/ponytail/hooks/claude-codex-hooks.json`. Ponytail **không**
  đăng ký `PreToolUse` cho Claude Code — dòng `PreToolUse` duy nhất nằm ở
  `~/Documents/ponytail/hooks/qoder-hooks.json`, tức host khác.
- **Trùng sự kiện:** `SessionStart` và `UserPromptSubmit` — hai bên cùng bắn mỗi turn.
- **Kho mức gắt của Ponytail:** `~/.config/ponytail/config.json` (hoặc `$XDG_CONFIG_HOME`),
  `[XÁC THỰC]` `~/Documents/ponytail/hooks/ponytail-config.js:68`. Hoàn toàn tách khỏi
  `docs/tdq/state.json` — hai núm, hai kho, không cái nào biết cái kia.
- **Đường dẫn đụng nhau:** cả hai đều ghi `AGENTS.md` ở gốc project. `[XÁC THỰC]` Ponytail ở
  bản luật số 1 của `~/Documents/ponytail/scripts/check-rule-copies.js`; TDQ ở
  `scripts/build_portable.py:681`. Thư mục `.agents/` thì sống chung được — Ponytail vào
  `.agents/rules/`, TDQ vào `.agents/skills` (`scripts/build_portable.py:519`).
- **Ponytail hiện KHÔNG được cài:** `~/.claude/plugins/installed_plugins.json` chỉ có
  `tdq-workflow@tdq-local`. `[XÁC THỰC]` Nên chưa có gì đang đá nhau; đây là việc làm trước.

Phát hiện quan trọng nhất của phase này — **một nửa lớp tương thích đã tồn tại**:

`scripts/tdq_lsp.py:379` `bac6_hook_xung_dot` đã đọc `~/.claude/plugins/installed_plugins.json`,
bỏ qua plugin nhà (`scripts/tdq_lsp.py:44`), mở `hooks/hooks.json` của từng plugin ngoài, và
**báo chứ không bao giờ tự sửa file plugin khác** — đúng thái độ cần cho lớp tương thích.

Nhưng nó **hẹp có chủ đích và sẽ không thấy Ponytail**: nó chỉ soi sự kiện `PreToolUse`
(`scripts/tdq_lsp.py:391`) và chỉ khớp matcher chứa `Grep|Glob|Bash`
(`scripts/tdq_lsp.py:45`). Ponytail đăng ký `SessionStart`, `UserPromptSubmit`,
`SubagentStart` → **rơi ngoài tầm nhìn của bậc 6 hoàn toàn**. `[XÁC THỰC]`

Suy ra: phần "dò" của lớp tương thích là **mở rộng một hàm đã có**, không phải dựng mới —
đúng bậc 2 của chính bảng thang Ponytail ("does it already exist? reuse it").

Ràng buộc kiến trúc phải tôn trọng (`docs/kien-truc.md`, trạng thái NHÁP nhưng mục `Đã chốt`
có ngày):

- `docs/kien-truc.md:25` — chỉ `scripts/tdq_state.py` được ghi `docs/tdq/state.json`.
- `docs/kien-truc.md:26` — file code mới bắt buộc nằm trong `scripts/` hoặc `hooks/`.
- `docs/kien-truc.md:13` — `portable_*` là SINH, cấm sửa tay.
- `docs/kien-truc.md:49` — `soul.md` là luật gốc, đổi soul phải có người dùng duyệt.
- `docs/kien-truc.md:51` — luật trong `skills/` viết tiếng Anh; tài liệu cho người dùng theo
  `doc_lang`.

Nợ phát hiện bên lề, **không thuộc request này**: `~/.claude/plugins/cache/tdq-local/tdq-workflow/`
giữ cả `0.45.0`, `0.46.0`, `0.47.0`; `installed_plugins.json` trỏ `0.47.0` nhưng skill nạp trong
session này đến từ thư mục `0.46.0`. `[XÁC THỰC]` Lệch bản cache, đáng dọn ở request khác.

### Kiểm kê tài sản Ponytail — bảy món, đo ngày 2026-09-16

Đây là mục chịu tải thiết kế sau khi sửa đề. Đo trực tiếp trên `/Users/tdq/Documents/ponytail`
(đọc, không sửa). `AGENTS.md` 32 dòng · `skills/ponytail/SKILL.md` 120 dòng · 6 hook js 758
dòng · 6 command toml · tổng mã hook + script 1411 dòng.

| # | Món | Hạng | Ponytail có gì | TDQ hôm nay | Lấy được không |
|---|---|---|---|---|---|
| 1 | Thang 7 bậc + bộ rule gọn | rule | `~/Documents/ponytail/AGENTS.md:5` tới `:32`; bản dài `~/Documents/ponytail/skills/ponytail/SKILL.md:32` | **KHÔNG CÓ** — grep `YAGNI\|stdlib\|ladder` trong `skills/tdq-build/references/rules/chung.md` và `skills/tdq-conventions/references/soul.md` ra **0 dòng** `[XÁC THỰC]` | Lấy được, và đã dự thảo sẵn ở `docs/tdq/knowledge/2026-09-16-1447-du-thao-luat-ponytail.md` |
| 2 | **Nạp lại luật MỖI TURN** | behavior | `~/Documents/ponytail/hooks/ponytail-mode-tracker.js:136` — mỗi `UserPromptSubmit` chèn lại **toàn thân luật** | TDQ chèn **một dòng ngắn** `[TDQ:MÃ]` (`hooks/scripts/_common.py:141`), không chèn thân luật | Đây là **món đắt giá nhất và cũng đắt tiền nhất** — xem phân tích dưới |
| 3 | Luật xuống tới sub-agent | behavior | `~/Documents/ponytail/hooks/ponytail-subagent.js:25` — `SubagentStart` chèn luật vào đầu hội thoại subagent | **KHÔNG CÓ** — `tdq-implementer` chạy không có luật gọn nào | Lấy được. Nghiên cứu điều 4: context này **bị prune**, non-compliance đo được 40–60% → là lời nhắc, không phải hàng rào |
| 4 | Bốn mức gắt lite/full/ultra/off, lọc thân luật theo mức | behavior | `~/Documents/ponytail/hooks/ponytail-instructions.js:11` `filterSkillBodyForMode` — lọc **đúng dòng bảng cường độ và ví dụ**, giữ nguyên rule thường | TDQ có `implement_mode` nhưng đó là trục khác (ai làm), không phải trục gắt | Lấy được = luồng 2 của request trước (`muc_gat`) |
| 5 | Sáu command | skill | `/ponytail-review` (soi diff) · `/ponytail-audit` (soi cả repo) · `/ponytail-debt` (gom marker thành sổ nợ) · `/ponytail-gain` · `/ponytail-help` · `/ponytail` | TDQ có `tdq-check-status`, `tdq-status`; **không có** cái nào soi over-engineer | 3 món đầu lấy được, **0 dòng mã** — command là prompt thuần. `gain` thì không: chính nó cấm in số của repo thật |
| 6 | Quy ước comment `ponytail:` ghi trần + đường nâng | rule | `~/Documents/ponytail/AGENTS.md:28` | **KHÔNG CÓ** khái niệm marker nợ trong mã | Phán quyết 4 của bạn: marker **không** mở được sàn phức tạp. Nên nó sống như **sổ nợ**, không phải giấy miễn trừ |
| 7 | Toả ra 9 host (cursor, windsurf, cline, kiro…) | rule | `~/Documents/ponytail/scripts/check-rule-copies.js`, 9 bản **viết tay**, so byte 8 bản | TDQ **sinh** bằng `scripts/build_portable.py` | **KHÔNG lấy** — TDQ đã ở bậc cao hơn; canary của chính Ponytail đã để lọt lệch chữ (báo ở report request trước) |
| 8 | **Làm cho chạy trước, refactor sau** | rule | **Không có trong Ponytail** — người dùng tự ra luật ở lượt chốt scope | Không có | Lấy. Xem dưới |

**Món 8 — luật của người dùng, không phải của Ponytail.** Nguyên văn lượt chốt scope: *"thay vì
tổ chức code như kiểu library từ đầu thì hãy đi như clean code. step 1 khiến code hoạt động, sau
đó mới tính tới refactor để project clean nếu cần, hãy code simple nhất có thể, minimal và
directly nhất có thể thay vì xử lí theo kiểu over engineer quá nhiều namespace, class, function
không cần thiết khiến con đường đi của một tính năng rối như mạng nhện. chỉ refactor sau khi tính
năng feature done và hoạt động ổn"*.
Nó **khác** thang 7 bậc và không nằm trong đó: thang nói về **cỡ** của giải pháp, món 8 nói về
**thứ tự** (chạy được → rồi mới gọn) và về **hình dạng đường đi** (một tính năng phải lần theo
được, không phải xuyên qua nhiều tầng). Đây là luật riêng, phải viết thành câu riêng.

**Món 5 — đo thêm, và nó rẻ hơn tôi tưởng:** 6 command của Ponytail là `commands/*.toml`,
**không plugin.json nào khai chúng** (`~/Documents/ponytail/.claude-plugin/plugin.json` chỉ khai
`hooks`), và bản `.md` nằm dưới `~/Documents/ponytail/.opencode/command/` → `.toml` là khuôn
Codex, không phải khuôn command của Claude Code. `[XÁC THỰC]` Hệ quả: **nội dung prompt lấy được,
khuôn phải tự viết**. TDQ hiện **chưa có** thư mục `commands/` nào (`ls commands/` → không tồn
tại) → món 5 là 3 file markdown mới, 0 dòng mã.

**Món 2 là trục chính, và nó trả lời câu bạn hỏi mấy lượt trước ("tích hợp có giải quyết được
over-engineer không?").** Vì sao Ponytail ép được mà TDQ không: luật TDQ nằm trong `skills/`,
mà skill **nạp theo yêu cầu**; luật không được nhắc lại thì trôi sau mỗi lần compact. Ponytail
nạp lại toàn thân luật mỗi lượt, nên nó "ACTIVE EVERY RESPONSE" theo đúng nghĩa cơ học, không
phải theo nghĩa khẩu hiệu. Món 1 mà không có món 2 thì chỉ là thêm chữ vào một file skill.

**Giá của món 2, nói thẳng bằng số:** thân luật ~110 dòng nhân **mỗi lượt**; hook
`UserPromptSubmit` của TDQ hiện chỉ chèn 1 dòng và chia sẻ ngân sách timeout **30s** (nghiên cứu
điều 3); nghiên cứu điều 7 còn ghi bug #10871 hook plugin chạy **hai lần** → chèn hai lần. Soul
xếp `chất lượng > context cost` nên hướng đã rõ, nhưng đây là dòng chi phí phải nói ra trước khi
chốt, không phải sau.

**Chỗ căng nhất giữa hai bên, và nó không nằm trong bốn phán quyết của bạn:** Ponytail nói
"fewest files possible", "no boilerplate nobody asked for"; còn TDQ **bắt buộc** mỗi request có
brief + spec + plan + DoD + qc + report + working log. Theo thước Ponytail, chính quy trình TDQ
là boilerplate. Bốn phán quyết của bạn xử luật **về mã**, không xử chỗ này. Tôi không tự chốt.

### Kiểm hiệu ứng lớp tìm kiếm

Bậc thang `python3 scripts/tdq_lsp.py check`: **7/7 ĐẠT**. Kiểm hiệu ứng (bắt buộc, vì bậc
thang chỉ kiểm sự TỒN TẠI): chọn tươi `turn_log_append` tại `scripts/tdq_state.py:1456` —
grep hẹp trong `scripts/ tests/` ra 6 file, grep toàn repo ra 9 file; `find_references` trả
**32 ref** trên 3 namespace `TDQ-Workflow/scripts` · `hooks/scripts` (9 ref) ·
`TDQ-Workflow/tests`, phủ đúng **8 file nguồn thật**. File thứ 9 của grep là bản sinh
`antigravity_portable/` mà LSP đúng khi bỏ qua. **PASS** — và LSP tìm ra 9 ref trong `hooks/`
mà lần grep hẹp đầu tiên trượt hoàn toàn.

### Nghiên cứu ngoài

XONG — sub-agent `general-purpose`, 4 truy vấn, đầy đủ nguồn ở
`docs/tdq/research/2026-09-16-2234-cong-sinh-ponytail-tdq.md` (164 dòng). Bảy điều đổi thiết kế:

1. **Tầng hook không dàn xếp được.** `[XÁC THỰC]` Mọi hook khớp đều chạy, song song; bản copy
   của plugin **không bị dedupe** (dedupe chỉ áp cho cùng handler khai ở nhiều settings file);
   không có `priority`/`order`/`runAfter`; và **không có cách tắt chọn lọc** hook của plugin
   khác — chỉ `disableAllHooks` toàn bộ, hoặc disable cả plugin.
   `docs/tdq/research/2026-09-16-2234-cong-sinh-ponytail-tdq.md:25`
2. **Lỗ hổng lớn nhất — `[CHƯA BIẾT]`:** nhiều `additionalContext` trên cùng một sự kiện thì
   **nối hay ghi đè**, tài liệu im lặng hoàn toàn (đã kiểm 2 lần). Cùng tình trạng với hai
   `SessionStart` cùng set `initialUserMessage` / `sessionTitle` / `watchPaths` — các field này
   không phải string cộng dồn. **Phải tự đo, cấm đoán bù.**
   `docs/tdq/research/2026-09-16-2234-cong-sinh-ponytail-tdq.md:30`
3. **`UserPromptSubmit` là điểm chặn DUY NHẤT** trong ba sự kiện (exit 2 = xoá prompt người
   dùng). Nếu cả hai bên đều dùng nó làm gate thì bên exit 2 trước xoá prompt, bên kia mất tác
   dụng — và không có cấu hình nào dàn xếp được. Timeout sự kiện này bị hạ xuống **30s**, chia
   sẻ tài nguyên máy giữa hai hook, quá hạn thì **fail-open** (bỏ context, prompt vẫn đi).
   `docs/tdq/research/2026-09-16-2234-cong-sinh-ponytail-tdq.md:74`
4. **`SubagentStart`** không chặn được, chỉ chèn vào **đầu hội thoại subagent** chứ không phải
   system prompt, timeout 600s. `[BÊN-THỨ-BA]` issue #23885 đo được non-compliance 40–60% và
   ghi rõ context này **bị prune** → đừng coi nó là hàng rào cứng. Nhưng matcher của nó nhận
   **regex theo namespace plugin** (`^my-plugin:reviewer$`) — **cơ chế cách ly duy nhất được
   document trong toàn bộ tầng hook**. `docs/tdq/research/2026-09-16-2234-cong-sinh-ponytail-tdq.md:55`
5. **Claude Code đọc `CLAUDE.md`, KHÔNG đọc `AGENTS.md`.** `[XÁC THỰC]` Nên tranh chấp
   `AGENTS.md` giữa Ponytail (bản luật số 1) và `scripts/build_portable.py:681` **không phải
   xung đột luật** — nó là **xung đột ghi file, mất dữ liệu**: ai `Write` sau thắng tuyệt đối,
   nội dung bên kia biến mất, và spec AGENTS.md chỉ phân xử bằng proximity thư mục (hai bên
   cùng ở gốc project thì khoảng cách bằng nhau, spec không có gì để nói).
   `docs/tdq/research/2026-09-16-2234-cong-sinh-ponytail-tdq.md:127`
6. **Đường thoát sạch: chuyển tranh chấp từ tầng hook sang tầng rule file.** `[XÁC THỰC]` Rule
   file **concat theo thứ tự XÁC ĐỊNH** (root → cwd, `CLAUDE.local.md` sau `CLAUDE.md`); có
   `@import` đệ quy tối đa 4 hop; `.claude/rules/*.md` cho **mỗi plugin một file riêng**, không
   ai ghi đè ai, có `paths` frontmatter để path-scope; và `claudeMdExcludes` là **van cắt chọn
   lọc** — đối lập hẳn với `disableAllHooks` kiểu tất-cả-hoặc-không.
   `docs/tdq/research/2026-09-16-2234-cong-sinh-ponytail-tdq.md:136`
7. **Hai bug thật phải kiểm bằng hiệu ứng, không tin khai báo.** `[BÊN-THỨ-BA]` #10871: hook
   plugin chạy **hai lần, hai PID** → side effect nhân đôi, nguy cho hook ghi state/working log
   của TDQ. #10225: `UserPromptSubmit` khai trong plugin `hooks.json` register và match nhưng
   **không execute** (im lặng), cùng cấu hình đặt ở `~/.claude/settings.json` thì chạy.
   `docs/tdq/research/2026-09-16-2234-cong-sinh-ponytail-tdq.md:38`

Ngân sách phải nhớ: `[XÁC THỰC]` CLAUDE.md nên dưới 200 dòng, "longer files reduce adherence",
`@import` **không** giảm context; và "if two rules contradict each other, Claude may pick one
arbitrarily" — luật mâu thuẫn chính thức là hành vi tuỳ hứng, không có tie-break.

**Sau khi sửa đề, điều nào còn chịu tải:** điều 3 (ngân sách 30s và fail-open của
`UserPromptSubmit` — vì nội hoá món 2 là cắm vào đúng sự kiện đó) · điều 4 (`SubagentStart`
không chặn được và **bị prune** — chặn tôi hứa hão về món 3) · điều 6 (tầng rule file thứ tự
xác định — thành **lựa chọn kênh nạp** cho món 2, xem câu 2 vòng scope) · điều 7 (#10871 chạy
hai lần → món 2 chèn hai lần) · và ngân sách adherence "dài hơn thì tuân thủ kém hơn".
Điều 1, 2, 5 **chết theo lần sửa đề** — chúng nói về hai plugin dàn xếp với nhau.

### Phạm vi đã chốt

Chốt 2026-09-16, nguyên văn người dùng: `1abcde 2c 3a 4c` cộng luật món 8.

**Mặt CHỌN:** món 1 thân luật 7 bậc · món 2 nạp lại luật mỗi lượt qua **kênh C** (nền là rule
file, hook chỉ nhắc một dòng ngắn khi phase `implement`) · món 3 luật xuống sub-agent · món 4
bốn mức gắt lite/full/ultra/off mặc định `full` · món 5 ba command `review`/`audit`/`debt` ·
món 6 marker `ponytail:` làm **sổ nợ + QC fail khi marker thiếu trigger** · món 8 luật
"chạy trước, refactor sau".

**Mặt LOẠI:** món 7 toả 9 host (TDQ đã sinh tự động, lấy là hạ cấp) · `/ponytail-gain` (số
benchmark của người khác, và chính command đó cấm in số của repo thật) · `/ponytail-help` và
`/ponytail` (mức gắt đã có núm riêng ở món 4) · miễn trừ "trivial one-liners need no test"
(phán quyết 2) · marker `ponytail:` dùng để mở sàn phức tạp (phán quyết 4) · gỡ framework khỏi
1802 test cũ (chốt 3a) · mọi việc dàn xếp với Ponytail-như-plugin-thứ-hai (sai đề, đã bỏ).

**Bối cảnh bằng số:** TDQ hôm nay 8 skill · 5 hook trên 4 sự kiện · 915 dòng luật · 7 rule
doc_lint · 1802 test (294 đỏ có sẵn, nợ cũ) · 0 thư mục `commands/` · 0 dòng luật về YAGNI.
Ponytail cho vay: 32 dòng `AGENTS.md` + 120 dòng `SKILL.md` + 3 prompt command.

**Mức đầu tư suy ra** (không hỏi): **vừa-lớn**. Căn cứ: 7 món trải cả 4 hạng (rule, behavior,
skill, hook), trong đó món 2 và 4 chạm `hooks/` và `state.json` — tức chạm cổng và chạm trạng
thái, hai vùng `docs/kien-truc.md` ràng buộc chặt nhất; món 6 chạm `doc_lint`/QC. Không phải
"lớn" vì không món nào đòi kiến trúc mới: món 1/5/8 là văn bản, món 2 nửa nền là file, món 3/4
là một hook và một khoá state.

### Lộ trình

**Sáu luồng tính năng** request này được dựng từ đó — mỗi luồng một dòng, mỗi luồng truy được về
món trong kiểm kê:

| # | Luồng | Món | Chạm gì | Mới hay mở rộng |
|---|---|---|---|---|
| L1 | Thân luật tinh gọn: thang 7 bậc + rule gọn + "chạy trước, refactor sau" | 1, 8 | `skills/tdq-build/SKILL.md`, `skills/tdq-build/references/rules/chung.md` | Mở rộng. Dự thảo tiếng Anh đã có ở `docs/tdq/knowledge/2026-09-16-1447-du-thao-luat-ponytail.md`, còn thiếu món 8 |
| L2 | Kênh nạp always-on: chèn thân luật mỗi session và mỗi compact | 2 | `hooks/scripts/session_start.py` | **Mở rộng** — hook đã khớp `compact` vì không khai matcher |
| L3 | Dòng nhắc ngắn khi phase `implement` | 2 | `hooks/scripts/prompt_context.py` | Mở rộng — cơ chế `[TDQ:MÃ]` đã có ở `hooks/scripts/_common.py:141` |
| L4 | Luật xuống sub-agent | 3 | `hooks/hooks.json` + một file hook mới | **Mới** — thêm sự kiện `SubagentStart`, là sự kiện thứ năm |
| L5 | Bốn mức gắt `muc_gat`, mặc định `full`, lọc thân luật theo mức | 4 | `scripts/tdq_state.py` + hai hook của L2/L3 | Mở rộng state + mới một hàm lọc |
| L6 | Skill soi over-engineer + sổ nợ marker có cổng QC | 5, 6 | `skills/tdq-lean/SKILL.md`, `scripts/kiem_no_marker.py` | **Mới** |

**Sửa dòng L6 ngày 2026-09-16, lý do là số đo chứ không phải đổi ý** — bản đầu ghi
`commands/` + `scripts/doc_lint.py`, cả hai đều sai chỗ:
1. Tài liệu Claude Code xếp `commands/` là khuôn **CŨ** ("Skills as flat Markdown files. Use
   `skills/` for new plugins"), cách đặt tên không có tài liệu `[BÊN-THỨ-BA]`, và
   `docs/kien-truc.md:13` ghi bản portable sinh từ `skills/`+`hooks/`+`agents/`+`scripts/` —
   **không có `commands/`** → command sẽ không tới được bản ngoài. Đi bằng một skill.
2. `doc_lint.py` lint file markdown, còn marker `ponytail:` nằm trong comment file `.py` → sai
   miền. Đi bằng một script nhỏ riêng, đúng `docs/kien-truc.md:26`.

**Quyết định tôi tự chốt, ghi ra để bạn phủ quyết bằng một chữ:** giữ nguyên chuỗi marker
`ponytail:` chứ không đổi thành tên TDQ. Lý do: bạn gọi nó bằng tên đó ở cả hai lượt, giữ tên là
ghi công đúng nguồn, và đổi tên là việc không ai yêu cầu — chính bậc 1 của luật đang nội hoá.

**Bảng bước/phase:**

| Bước/phase | CÓ-BỎ | Vì sao |
|---|---|---|
| analyze | CÓ (xong) | 3 vòng hỏi, 8 món kiểm kê, 2 premise bị phá và sửa tại chỗ |
| Nghiên cứu ngoài thêm | **BỎ** | Đã 2 vòng: 4 truy vấn nền + 6 câu hỏi cơ chế plugin. Mọi `[CHƯA BIẾT]` còn lại đều đã chết theo lần sửa đề |
| spec | CÓ | Chạm `hooks/`, `state.json`, `doc_lint` — ba vùng `docs/kien-truc.md` ràng chặt nhất |
| plan | CÓ | Khung bất biến |
| implement | CÓ | Khung bất biến |
| Cắt cho sub-agent | **Để `tdq_bench.py` đo ở phase plan** | Không đoán bằng mắt; `Mode thực thi` do người dùng chốt ở cổng mode |
| QC bằng agent độc lập (`tdq-qc-tester`) | **CÓ** | Lượt này **sửa mã thật** (khác request trước chỉ ra tài liệu), và L2/L4 sửa hook — hook sai thì mọi request sau đều sai. Cần mắt thứ hai |
| Review sâu (`tdq-reviewer`) | BỎ | Chỉ gọi khi người dùng yêu cầu |
| report | CÓ | Khung bất biến |

**Ràng buộc riêng của lượt này, mang sang spec:** L2 và L4 chèn văn bản vào context **mọi
session và mọi sub-agent** — sai một lần là sai toàn hệ. Nên DoD phải có một hạng mục đo **hiệu
ứng thật** (chạy hook, đọc đầu ra), không chấp nhận "khai là chạy": nghiên cứu điều 7 ghi rõ bug
#10225 là hook register và match nhưng **không execute**.

### Cổng kiểm cuối phase analyze

| Câu | Trả lời |
|---|---|
| Phạm vi cuối đã rõ chưa: xây gì, cái gì mới, đầu ra chính xác là gì? | RÕ. 6 luồng ở bảng trên, 3 luồng mở rộng mã có sẵn, 3 luồng thêm mới (`SubagentStart`, `commands/`, hàm lọc mức). Đầu ra: luật nội hoá + 2 hook sửa + 1 hook mới + 1 khoá state + 3 command + 1 rule doc_lint |
| Có cần model / tải về / cài đặt gì không? | KHÔNG. Không thêm dependency, không cài Ponytail, không ghi ra ngoài repo (chốt 5a). Thang 7 bậc `tdq_lsp.py check` đã 7/7 ĐẠT |
| Phạm vi QC/test/validate đã định chưa? | ĐỊNH RỒI. Mỗi luồng một unit test red→green (phán quyết 2, không miễn trừ); thêm một hạng mục DoD đo hiệu ứng thật của hook; QC có agent độc lập; baseline 1802 test giữ nguyên theo `3a`, đối chiếu với `main` như request trước |

## Hỏi đáp

### Vòng 1 — scope (trình lần 1 lúc 2026-09-16, **thay bằng bản sửa** cùng ngày, chờ trả lời)

Vòng scope CHẠY, vì yêu cầu trúng dấu hiệu 1 (gọi tên cả một tính năng, không trỏ vào một
hành vi hay một file) và dấu hiệu 2 (quét khung 9 mặt thấy từ 3 mặt trở lên có thể áp mà yêu
cầu chưa nói gì tới).

**Trình lần 1 và lần 2 đều BỎ** — cả hai hỏi về việc dàn xếp hai plugin cùng cài, tức sai đề.
Lần 3 hỏi theo đúng đề nội hoá, dựa trên `### Kiểm kê tài sản Ponytail`:

| # | Câu | Các lựa chọn |
|---|---|---|
| 1 | Nội hoá món nào (chọn nhiều) | A thân luật 7 bậc · B nạp lại luật mỗi lượt · C luật xuống sub-agent · D bốn mức gắt · E ba command soi over-engineer · F chỉ lấy thân luật, không thêm cơ chế |
| 2 | Món B nạp qua kênh nào | A hook `UserPromptSubmit` · B `.claude/rules/*.md` · C nền là rule file + hook nhắc ngắn khi `implement` |
| 3 | Suite `unittest` 1802 test đứng đâu khi phán quyết 1 thành luật | A luật mới chỉ áp cho check viết từ nay · B gỡ dần framework khỏi check cũ · C đóng băng test cũ, luật mới áp cho mã mới trong `scripts/`+`hooks/` |
| 4 | Marker `ponytail:` làm gì trong TDQ | A sổ nợ thuần + lệnh gom · B không lấy · C sổ nợ + QC fail nếu marker thiếu trigger |

**Không hỏi, và vì sao:** (a) mức đầu tư — suy ra, không hỏi. (b) Quy trình TDQ có chịu thước
YAGNI của Ponytail không — người dùng đã ra lệnh "giữ đúng phase và gate" ở lượt mở request,
nên tôi coi **quy trình được miễn**, bậc 1 chỉ áp lên mã sản phẩm; nêu ra trong chat để người
dùng phủ quyết bằng một câu nếu tôi hiểu sai. (c) Món 7 (toả 9 host) — không lấy, TDQ đã sinh
tự động, đây là hạ cấp chứ không phải nâng cấp.

**Trả lời (nguyên văn 2026-09-16):** `1abcde 2c 3a 4c`. Tức: lấy cả năm món A–E (không chọn F
"chỉ lấy thân luật") · kênh nạp là C (nền rule file + hook nhắc ngắn khi `implement`) · suite
1802 test giữ nguyên, luật mới chỉ áp cho check viết từ nay · marker `ponytail:` là sổ nợ **và**
QC fail nếu thiếu trigger.
Cùng lượt đó người dùng ra thêm luật món 8 (xem `### Kiểm kê tài sản Ponytail`).
Không phủ quyết việc tôi coi quy trình TDQ được miễn bậc 1 → điều đó đứng.

### Vòng 2 — chi tiết (2026-09-16)

Không có câu nào cho người dùng. Ba chỗ còn mờ sau vòng 1 đều là việc **tôi phải đo**, không
phải việc người dùng quyết:

1. Plugin có ship được rule file always-on không — nửa "nền" của lựa chọn 2c đứng hay không phụ
   thuộc câu này. Đo bằng sub-agent `claude-code-guide`, 5 câu hỏi có nhãn tin cậy. **XONG, và
   kết quả phá premise của chính câu 2:**
   - `[XÁC THỰC]` **Plugin KHÔNG ship được rule file.** `plugin.json` không có key nào khai
     rule/instruction; cấu trúc plugin được document chỉ gồm `skills/ agents/ hooks/ .mcp.json
     .lsp.json monitors/ bin/ settings.json`. Nguồn: code.claude.com/docs/en/plugins.md.
   - `[XÁC THỰC]` `.claude/rules/` **chỉ** được quét ở hai gốc: `~/.claude/rules/` (user) và
     `<project>/.claude/rules/` (project). **Thư mục plugin không được quét.** Nguồn:
     code.claude.com/docs/en/memory.md.
   - `[XÁC THỰC]` Frontmatter rule file chỉ có **một** field được document: `paths`. Không có
     `paths` = nạp vô điều kiện.
   - `[XÁC THỰC]` **Không có kênh always-on nào cho plugin ngoài hook.** `settings.json` của
     plugin hiện chỉ nhận `agent` và `subagentStatusLine`. Skill không có `alwaysApply`.
   - `[XÁC THỰC]` Output hook **không** sống qua compact — bị tóm tắt cùng hội thoại. **Nhưng**
     hook `SessionStart` có matcher khớp source `compact` thì được **chạy lại** và output được
     thêm vào context sau compact. Đây chính là lý do cơ chế Ponytail đứng được: matcher của nó
     là `startup|resume|clear|compact` (`~/Documents/ponytail/hooks/claude-codex-hooks.json`).
   → Hệ quả: nửa "nền rule file" của lựa chọn 2c **không thể do plugin cung cấp**. Nó đòi một
   bước cài ghi file vào `~/.claude/rules/` hoặc `<project>/.claude/rules/`, tức **ghi ra ngoài
   repo**. Phải trình lại cho người dùng chọn, không tự quyết.
   - Nhịp đo tiếp, `[XÁC THỰC]` bảng "What survives compaction"
     (code.claude.com/docs/en/context-window.md): *"Project-root CLAUDE.md and unscoped rules |
     **Re-injected from disk**"*, và *"If a rule must persist across compaction, drop the
     `paths:` frontmatter or move it to the project-root CLAUDE.md."* → luật không `paths` sống
     qua compact, và cơ chế là **đọc lại file vật lý**, không giữ khối text cũ.

**Hai điều phát hiện này đổi, và một điều trong đó là tôi đã báo giá sai cho người dùng:**

- **Giá món 2 tôi báo quá cao.** Tôi nói "~110 dòng × MỖI LƯỢT" vì đó là cách Ponytail làm
  (`~/Documents/ponytail/hooks/ponytail-mode-tracker.js:136`, mỗi `UserPromptSubmit`). Nhưng để
  luật **bền** thì không cần mỗi lượt: chỉ cần mỗi **session** và mỗi **compact**, vì đó là hai
  thời điểm context bị dựng lại. Giá thật rẻ hơn nhiều lần, và không ăn vào ngân sách 30s của
  `UserPromptSubmit`.
- **Món 4 (bốn mức gắt) BẮT BUỘC kênh hook, không dùng được rule file.** Rule file là văn bản
  tĩnh trên đĩa; muốn lọc thân luật theo mức thì phải **ghi lại file mỗi lần đổi mức**. Còn hook
  lọc ngay lúc chèn — đó đúng là việc `~/Documents/ponytail/hooks/ponytail-instructions.js:11`
  `filterSkillBodyForMode` đang làm. `[SUY-CODE]` Nên món 4 và nửa "nền rule file" đối nhau.

### Vòng 3 — một câu, do premise câu 2 bị phá (2026-09-16, chờ trả lời)

Nửa "nền" của lựa chọn 2c không thể do plugin cung cấp. Bốn cách, trình trong chat.

**Trả lời (nguyên văn 2026-09-16):** `5a và default = full của ponytail`. Tức: **bỏ rule file**,
thân luật đi bằng hook `SessionStart` (đã chạy trên `compact`) cộng một dòng nhắc ngắn khi phase
`implement`; không ghi gì ra ngoài repo. Và `muc_gat` mặc định **`full`**, khớp mặc định của
Ponytail (`~/Documents/ponytail/skills/ponytail/SKILL.md:29`).

**Đo thêm sau khi chốt 5a, và nó làm việc nhẹ đi:** `hooks/hooks.json` khai `SessionStart`
**không có matcher** → nó khớp mọi source, kể cả `compact`. `[XÁC THỰC]` Nên không phải dựng hook
mới: chỉ **mở rộng `hooks/scripts/session_start.py`** đang có. Bậc 2 của chính thang Ponytail.
Số hook giữ nguyên 5 mục trên 4 sự kiện cho luồng này; chỉ luồng sub-agent mới thêm sự kiện
thứ năm.
2. Khuôn command của Claude Code — đã đo xong, xem món 5: `.toml` là khuôn Codex, phải tự viết `.md`.
3. Nơi đặt `muc_gat` — `docs/kien-truc.md:25` đã chốt chỉ `scripts/tdq_state.py` được ghi
   `docs/tdq/state.json`, nên không có gì để hỏi.

Chỗ tôi đã hỏi và người dùng đã xử ở vòng 1 nên **không hỏi lại**: suite 1802 test (3a).
