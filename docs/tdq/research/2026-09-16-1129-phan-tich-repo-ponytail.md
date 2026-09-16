# Phân tích repo Ponytail v4.10.0

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

Ngày phân tích: 2026-09-16 · Đối tượng: `DietrichGebert/ponytail`, bản clone tại
`/Users/tdq/Documents/ponytail`, `package.json` khai `@dietrichgebert/ponytail` v4.10.0 ·
166 file tracked (57 `.md`, 45 `.js`, 20 `.json`, 6 `.py`, 6 `.toml`).

Viết cho người **chưa từng nghe tới Ponytail**. Không cần đọc repo trước.
Mọi khẳng định về code đều kèm `đường-dẫn:dòng` để bạn tự kiểm.

---

## Tóm tắt điều hành

1. **Ponytail là một bộ luật chống xây thừa cho agent lập trình** — 121 dòng tiếng Anh trong
   `skills/ponytail/SKILL.md` — cộng một tầng ống dẫn bơm bộ luật đó vào ~20 nền tảng agent.
2. Luật ép agent leo **thang 7 bậc** (bậc 1: "việc này có cần tồn tại không") và dừng ở bậc đầu
   tiên còn đứng vững; cường độ chỉnh được qua **5 mode** `off/lite/full/ultra/review`.
3. **Kiến trúc đáng học:** một nguồn chân lý duy nhất, adapter chỉ `require` lại builder chung,
   và một hàm `writeHookOutput()` với **5 khuôn JSON** cho 5 họ host khác nhau.
4. **Kỷ luật nổi bật nhất:** hook thà không bơm được luật còn hơn treo phiên của người dùng —
   ba lớp phòng thủ chống treo, mọi lời gọi stdout đều nuốt lỗi.
5. **Rủi ro lớn nhất (mục 4.2–4.3):** adapter Hermes `__init__.py` **phá chính luật "keep adapters
   thin" của repo** — nó chép lại toàn bộ builder bằng Python. Hai bản **đã lệch nhau thật** ở một
   biểu thức chính quy; hôm nay chưa phát tác, và **không guard nào canh cái lệch đó**.
6. Hai lệch nhỏ hơn: mode `review` hành xử khác nhau giữa bản JS và Python mà không được ghi tài
   liệu; và lời hứa "mode giữ đến hết phiên" chỉ đúng theo nghĩa đen với đúng một host (`pi`).
7. **Sức khoẻ repo:** 94/95 test pass ở bộ gốc, 23/23 và 3/3 ở hai bộ con. Test đỏ duy nhất là do
   máy thiếu `pandas`, **không phải lỗi repo**.
8. **So với TDQ-Workflow:** hai thứ **vuông góc, không cạnh tranh** — Ponytail quản *nội dung*
   quyết định kỹ thuật, TDQ quản *quy trình* ra quyết định. Chúng ghép được vào nhau, và chúng
   chọn hướng fail ngược nhau một cách có lý (mục 6.4).

---

## 1. Ponytail là gì

### Ponytail là gì trong 5 dòng

1. Một **bộ luật chống xây thừa** cho agent lập trình, viết bằng tiếng Anh trong đúng một file.
2. Luật ép agent leo một **thang 7 bậc** và dừng ở bậc đầu tiên còn đứng vững — bậc 1 là "việc
   này có cần tồn tại không".
3. Có **5 mức cường độ**: `off` / `lite` / `full` (mặc định) / `ultra` / `review`.
4. Phần còn lại của repo chỉ là **ống dẫn**: bơm bộ luật đó vào ~20 nền tảng agent khác nhau,
   mỗi nền tảng một kiểu móc nối.
5. Không cài vào code sản phẩm của bạn, không chạy lúc build — nó chỉ tác động vào **ngữ cảnh**
   con agent nhận được.

Ponytail **không phải** linter, không phải framework, không phải thư viện bạn import.
Nó là **một bộ luật viết bằng tiếng Anh, cộng với hệ thống ống dẫn để nhét bộ luật đó vào đầu
con agent ở mọi lượt trả lời, trên khoảng 20 nền tảng agent khác nhau.**

Bộ luật ép agent chọn giải pháp *lười nhất mà vẫn chạy được*. Câu mở đầu của nó
(`skills/ponytail/SKILL.md:22-24`):

> You are a lazy senior developer. Lazy means efficient, not careless. […] The best code is the
> code never written.

Vấn đề nó giải: agent lập trình có xu hướng xây thừa — tạo abstraction cho một trường hợp, thêm
dependency cho việc ba dòng code làm xong, sinh boilerplate "để sau này dùng". Ponytail là một
đối trọng thường trực chống lại xu hướng đó.

**Hai tầng triển khai** — đây là ý tưởng trung tâm của cả repo
(`docs/agent-portability.md`):

| Tầng | Cách hoạt động | Ví dụ nền tảng |
|---|---|---|
| **Tầng plugin** | Có hook vòng đời → code chạy được, tự bơm luật vào mỗi lượt, đổi mode lúc đang chạy | Claude Code, Codex, Cursor, Qoder, Copilot, opencode, pi, Hermes |
| **Tầng chỉ-dẫn** | Host chỉ biết đọc một file rule → chép luật vào đúng tên file host chờ đợi | Windsurf, Cline, Kiro, Grok, Devin, và `AGENTS.md` dùng chung |

Khác biệt thực tế giữa hai tầng: tầng plugin **đổi mode được giữa phiên** (`/ponytail ultra`) và
bơm được cả vào sub-agent; tầng chỉ-dẫn thì luật luôn bật ở một mức cố định, muốn đổi phải sửa file.

**Bề mặt người dùng:** 6 skill trong `skills/` (`ponytail`, `-review`, `-audit`, `-debt`,
`-gain`, `-help`) và 6 lệnh cùng tên trong `commands/*.toml`. Đáng chú ý là `ponytail-debt`: bộ
luật bắt buộc mỗi lần cắt góc có chủ đích phải để lại một chú thích `ponytail:` ghi rõ trần chịu
đựng và đường nâng cấp (`skills/ponytail/SKILL.md:64`), và `ponytail-debt` đi thu hoạch đúng các
chú thích đó thành một cuốn sổ nợ kỹ thuật. Tức repo tự áp dụng luật của chính nó — trong mã
nguồn Ponytail có nhiều chú thích `ponytail:` thật, ví dụ
`hooks/ponytail-runtime.js:8` và `pi-extension/index.js:74`.

---

## 2. Bộ luật và 5 mode (mặt A)

### 2.1 Một file là nguồn chân lý

Toàn bộ luật nằm trong **`skills/ponytail/SKILL.md`** (121 dòng). Mọi nền tảng, mọi adapter cuối
cùng đều đọc lại đúng file này. Cấu trúc:

| Mục | Dòng | Nội dung |
|---|---|---|
| Persistence | `:26-30` | Luật có hiệu lực **mọi câu trả lời**; chỉ tắt bằng "stop ponytail"/"normal mode" |
| The ladder | `:32-54` | Thang 7 bậc — trái tim của bộ luật |
| Rules | `:56-64` | Cấm abstraction không ai yêu cầu, cấm boilerplate, ưu tiên xoá hơn thêm |
| Output | `:66-75` | Khuôn trả lời: `[code] → skipped: [X], add when [Y].` |
| Intensity | `:77-88` | Bảng 3 mức lite/full/ultra + ví dụ mẫu cho từng mức |
| When NOT to be lazy | `:90-112` | Các vùng cấm đơn giản hoá |
| Boundaries | `:114-120` | Ponytail quản *xây cái gì*, không quản *nói năng thế nào* |

### 2.2 Thang 7 bậc — dừng ở bậc đầu tiên còn đứng vững

Trích `skills/ponytail/SKILL.md:36-42`:

1. **Việc này có cần tồn tại không?** Nhu cầu suy diễn → bỏ, nói một dòng. (YAGNI)
2. **Repo đã có sẵn chưa?** Có helper/util/kiểu/mẫu đang sống ở đây → dùng lại. Repo ghi rõ:
   viết lại thứ nằm cách đó vài file là loại rác phổ biến nhất.
3. **Thư viện chuẩn làm được không?** Dùng.
4. **Tính năng sẵn có của nền tảng phủ được không?** `<input type="date">` hơn thư viện picker,
   CSS hơn JS, ràng buộc DB hơn code ứng dụng.
5. **Dependency đã cài sẵn giải quyết được không?** Dùng. Không bao giờ thêm dependency mới cho
   việc vài dòng code làm xong.
6. **Có thể gói thành một dòng không?** Một dòng.
7. **Chỉ khi đó:** lượng code tối thiểu chạy được.

Hai điều kiện đi kèm quan trọng không kém cái thang, và là chỗ Ponytail tự phòng thân trước cáo
buộc "lười ẩu":

- Thang chạy **sau khi đã hiểu vấn đề, không thay cho việc hiểu** (`:44-48`). Nguyên văn ở
  `:97-101`: *"Never lazy about understanding the problem […] Laziness that skips comprehension
  to ship a small diff is the dangerous kind."*
- **Sửa bug là sửa gốc, không sửa triệu chứng** (`:50-54`): trước khi sửa phải grep mọi nơi gọi
  hàm sắp đụng; một guard trong hàm dùng chung là diff nhỏ hơn một guard ở từng nơi gọi.

### 2.3 Vùng cấm đơn giản hoá

`skills/ponytail/SKILL.md:90-112` liệt kê những thứ **không bao giờ** được cắt: kiểm tra đầu vào
ở biên tin cậy, xử lý lỗi chống mất dữ liệu, biện pháp bảo mật, nền tảng về khả năng tiếp cận,
và bất cứ thứ gì người dùng yêu cầu rõ ràng. Thêm hai điều ít gặp ở các bộ luật kiểu này:

- **Phần cứng không bao giờ lý tưởng như trên giấy** (`:103-105`): đồng hồ thật trôi, cảm biến
  thật lệch — phải chừa núm hiệu chỉnh, không chỉ chừa ít code.
- **Code lười mà không có phép kiểm đi kèm là code chưa xong** (`:107-112`): logic không tầm
  thường phải để lại ĐÚNG MỘT phép kiểm chạy được — một `demo()`/`__main__` dùng `assert` hoặc
  một file `test_*.py` nhỏ. Không framework, không fixture. Và YAGNI cũng áp dụng cho test:
  một dòng tầm thường thì không cần test.

### 2.4 Năm mode, nhưng chỉ bốn được làm mặc định

`hooks/ponytail-config.js` khai `VALID_MODES = ['off','lite','full','ultra','review']` nhưng
`RUNTIME_MODES` chỉ có 4 mức đầu.

| Mode | Nghĩa | Ghi chú |
|---|---|---|
| `off` | Tắt hẳn | Với hook JS, "tắt" = **xoá file cờ** `.ponytail-active`; vắng file nghĩa là tắt (`hooks/ponytail-runtime.js:51-57`) |
| `lite` | Vẫn xây thứ được yêu cầu, chỉ nêu thêm một dòng phương án lười hơn để người dùng chọn | |
| `full` | **Mặc định.** Thang 7 bậc được thi hành đầy đủ | |
| `ultra` | Cực đoan YAGNI: xoá trước khi thêm, ship one-liner rồi chất vấn luôn phần còn lại của yêu cầu | |
| `review` | Chỉ soi diff tìm chỗ xây thừa | **Chỉ theo phiên, không được đặt làm mặc định** — `writeDefaultMode()` từ chối, lý do ghi là issue #377 |

**Thứ tự phân giải mode** (`hooks/ponytail-config.js`, hàm `getDefaultMode()`):
biến môi trường `PONYTAIL_DEFAULT_MODE` → `config.json` (tìm theo `XDG_CONFIG_HOME/ponytail`,
`~/.config/ponytail`, `%APPDATA%\ponytail`) → rơi về `'full'`. File config được strip BOM trước
khi parse (`.replace(/^﻿/,'')`) — một chi tiết nhỏ cho thấy repo có va thật với Windows.

### 2.5 Lọc luật theo mode: cắt đúng 2 loại dòng

Hàm `filterSkillBodyForMode()` (`hooks/ponytail-instructions.js:11-41`) không dựng luật từ đầu —
nó **đọc chính `SKILL.md` rồi cắt bớt**. Trình tự: bỏ frontmatter, rồi loại đúng hai dạng dòng
có nhãn là tên mode nhưng không khớp mode hiện tại:

- dòng bảng cường độ: `^\|\s*\*\*(.+?)\*\*\s*\|` — ví dụ `| **lite** | …`
- dòng ví dụ mẫu: `^-\s*([^:]+):\s*"` — ví dụ `- lite: "Done, cache added…"`

Dấu ngoặc kép trong mẫu thứ hai **là bắt buộc và có chủ ý**. Comment ngay tại chỗ
(`hooks/ponytail-instructions.js:33-36`) giải thích: thiếu nó thì một bullet luật bình thường lỡ
bắt đầu bằng tên mode — kiểu `- Full: …` — sẽ bị âm thầm xoá ở mọi mode khác, dù nó là văn xuôi
phải giữ nguyên. Chi tiết tưởng vụn này sẽ quay lại ở **mục 4** như đầu mối của một lỗi lệch thật.

Nếu đọc file thất bại, `getFallbackInstructions()` (`:43-75`) trả về một bản luật rút gọn
**nhúng cứng trong JS** — nên agent không bao giờ rơi vào trạng thái không có luật.

Riêng mode `review` đi đường khác: nó nằm trong `INDEPENDENT_MODES`
(`hooks/ponytail-instructions.js:8`), và `getPonytailInstructions()` trả về **đúng một dòng** trỏ
sang skill `/ponytail-review` thay vì bơm bộ luật (`:80-82`).

---

## 3. Kiến trúc đa host (mặt B)

Đây là phần thú vị nhất về mặt kỹ thuật. Bài toán: **cùng một bộ luật, ~20 host, mỗi host một
giao thức móc nối khác nhau, và không host nào chịu đổi theo bạn.**

### 3.1 Một nguồn chân lý, ba vòng đồng tâm

```
skills/ponytail/SKILL.md          ← luật gốc, 121 dòng, con người sửa ở đây
        │
        ├── hooks/ponytail-instructions.js   ← builder JS: đọc SKILL.md, lọc theo mode
        │        ├── hooks/ponytail-activate.js      (SessionStart)
        │        ├── hooks/ponytail-mode-tracker.js  (UserPromptSubmit)
        │        ├── hooks/ponytail-subagent.js      (SubagentStart)
        │        ├── pi-extension/index.js           → require(builder)
        │        ├── ponytail-mcp/instructions.js    → require(builder)
        │        └── .opencode/plugins/ponytail.mjs  → require(builder)
        │
        ├── AGENTS.md  ← bản rút gọn của luật, và là bản gốc của 7 bản chép
        │        └── scripts/check-rule-copies.js so byte 7 bản chép với nó
        │
        └── __init__.py  ← Hermes: CHÉP LẠI builder bằng Python (xem mục 4)
```

Vòng 1 (builder JS) là nơi mọi adapter JS hội tụ — adapter chỉ `require` rồi gắn vào event của
host, không tự dựng luật. Vòng 2 là tầng chỉ-dẫn. Vòng 3 là chỗ kiến trúc bị rách, mục 4 phân tích.

### 3.2 Ba hook vòng đời của tầng plugin

| Hook | File | Khi nào chạy | Làm gì |
|---|---|---|---|
| `SessionStart` | `hooks/ponytail-activate.js` | Mở/khôi phục/xoá/nén phiên (matcher `startup\|resume\|clear\|compact`, `hooks/claude-codex-hooks.json:5`) | Ghi file cờ `.ponytail-active` (`:55`), bơm luật đã lọc (`:61`), và dò xem statusline đã cấu hình chưa (`:64-106`) |
| `UserPromptSubmit` | `hooks/ponytail-mode-tracker.js` | Mỗi lần người dùng gửi prompt | Bắt lệnh `/ponytail …` để đổi mode (`:44-107`), bắt câu "stop ponytail" (`:110-114`), và với Qoder thì bơm lại toàn bộ luật mỗi lượt (`:121-138`) |
| `SubagentStart` | `hooks/ponytail-subagent.js` | Mỗi lần agent cha sinh sub-agent | Bơm cùng bộ luật vào sub-agent — vì context của `SessionStart` **không** chảy xuống sub-agent (`:4-6`, issue #252) |

Hai chi tiết đáng học ở đây:

- **Lời nhắc statusline chỉ hiện đúng một lần.** `hooks/ponytail-activate.js:75-80` ghi một file cờ
  `.ponytail-statusline-nudged` sau lần nhắc đầu, kèm lý do viết thẳng trong comment: *"Repeating
  it every session start turns a helpful hint into a nag."*
- **Lọc sub-agent theo loại.** Đặt `PONYTAIL_SUBAGENT_MATCHER` là một regex thì luật chỉ bơm vào
  sub-agent có `agent_type` khớp (`hooks/ponytail-subagent.js:8-11`, issue #506). Quan trọng hơn là
  **hướng fail**: payload hỏng, stdin lỗi, hay hết giờ đều **fail open — vẫn bơm**
  (`:50-52`), để việc khoanh vùng không bao giờ âm thầm làm rơi bộ luật.

### 3.3 Hợp đồng "không bao giờ treo phiên"

Hook chạy chặn trước mỗi lượt, nên một hook treo là **đóng băng cả phiên làm việc**. Repo xử lý
chuyện này rất kỷ luật, và ghi rõ nguyên nhân gốc (`hooks/ponytail-mode-tracker.js:147-155`): trên
Windows, Claude Code chạy hook qua một lớp bọc PowerShell `if {}` có thể nuốt mất JSON prompt,
nên sự kiện stdin `end` **không bao giờ bắn** (#443). Ba lớp phòng thủ đi cùng nhau:

1. `process.stdin.on('error', …)` → xử lý ngay những gì đã nhận rồi thoát.
2. `setTimeout(…, 1000).unref()` → hết 1 giây thì tự cứu. `.unref()` khiến hàng rào này **không**
   cộng thêm độ trễ vào đường chạy bình thường.
3. Cờ `done` chống chạy hai lần khi cả `end` lẫn timeout cùng bắn.

Và **mọi** lời gọi `writeHookOutput()` đều nằm trong `try/catch` nuốt lỗi, với lý do lặp lại ở
nhiều file: *"stdout closed/EPIPE at hook exit must not surface as a hook failure"*
(`hooks/ponytail-activate.js:46-48`, `:113-115`, `hooks/ponytail-subagent.js:26-28`).

Nói gọn: **Ponytail thà không bơm được luật còn hơn làm hỏng phiên của bạn.** Đây là ưu tiên
thiết kế đúng cho một thứ chạy chèn vào mọi lượt.

### 3.4 Nhận diện host và 5 khuôn JSON đầu ra

Một file duy nhất (`hooks/ponytail-runtime.js`) gánh cả việc đoán host lẫn việc nói đúng
"phương ngữ" của host đó. Thứ tự nhận diện là **loại trừ dần**, cố ý
(`hooks/ponytail-runtime.js:19-29`):

1. `isCopilot` — `COPILOT_PLUGIN_DATA`, **hoặc** `CLAUDE_PLUGIN_ROOT` có chứa `agent-plugins` và
   `.vscode` (`:13-20`). Comment `ponytail:` ở `:8-12` ghi rõ nợ này: VS Code Copilot không đặt
   `COPILOT_PLUGIN_DATA`, thiếu fallback thì Ponytail tưởng nhầm là Claude Code (#528).
2. `isCodex` — `PLUGIN_DATA`.
3. `isQoder` — `QODER_SESSION_ID`.
4. `isCursor` — `CURSOR_VERSION`, **xếp sau cùng có chủ ý** (`:23-28`): biến này chỉ tồn tại
   trong môi trường Cursor dựng riêng cho tiến trình hook, nên không rò sang phiên Claude Code
   chạy trong terminal của Cursor.

Kết quả nhận diện đổi **hai** thứ: **thư mục lưu cờ** (`:31-37` — Codex dùng `PLUGIN_DATA`, Qoder
dùng `~/.qoder`, Cursor dùng `~/.cursor`) và **khuôn JSON in ra stdout**. `writeHookOutput()`
(`:80-131`) có đúng **5 nhánh**:

| # | Host | Khuôn stdout | Dòng |
|---|---|---|---|
| 1 | Copilot | `{additionalContext}` — **chỉ** khi event là `SessionStart`; mọi event khác in `{}` | `:81-86` |
| 2 | Codex | `{systemMessage:"PONYTAIL:<MODE>", hookSpecificOutput:{hookEventName, additionalContext}}` | `:87-97` |
| 3 | Qoder | Như Codex nhưng **bỏ** `systemMessage` | `:98-110` |
| 4 | Cursor | `{additional_context}` (snake_case!), thêm `continue:true` khi là `UserPromptSubmit`; không có context thì **in rỗng**, vì Cursor coi stdout không parse được là lỗi | `:111-122` |
| 5 | Claude gốc | `SubagentStart` phải bọc `{hookSpecificOutput:{…}}`; mọi event khác in **văn bản thô** | `:123-130` |

Nhánh 5 là chỗ dễ sai nhất và repo đoán đúng: phía Anthropic xác thực rằng chỉ 4 event
(`SessionStart`, `UserPromptSubmit`, `UserPromptExpansion`, `PostModelSwitch`) biến stdout thô
thành context — mọi event khác **bắt buộc** dùng `hookSpecificOutput.additionalContext`. Nên cái
`if (event === 'SubagentStart')` ở `:125` không phải mẹo vặt, nó là đúng đặc tả.

### 3.5 Bảng host → file → cách bơm

Cột cuối ghi rõ nguồn: **[repo]** = repo tự khai, **[xác thực]** = đã đối chiếu tài liệu nhà
cung cấp (chi tiết và URL ở mục 5).

| Host | File khai báo | Điểm móc | Cách luật đi vào |
|---|---|---|---|
| Claude Code | `.claude-plugin/plugin.json` → `hooks/claude-codex-hooks.json` | `SessionStart`, `SubagentStart`, `UserPromptSubmit` | stdout thô, riêng SubagentStart bọc JSON **[xác thực]** |
| Codex | `.codex-plugin/plugin.json`, **dùng chung** file hook của Claude | như trên, nhận biết qua `PLUGIN_DATA` | `additionalContext` **[xác thực, kèm một điểm chặn — mục 5]** |
| Copilot | `.github/plugin/plugin.json` → `hooks/copilot-hooks.json` | `sessionStart`, `userPromptSubmitted` (camelCase, có cả nhánh `bash` và `powershell`) | chỉ `sessionStart` đọc được context **[xác thực]** |
| Cursor | `hooks/cursor-hooks.json` merge vào `~/.cursor/hooks.json`, **hoặc** rule luôn bật `.cursor/rules/ponytail.mdc` | `sessionStart`, `beforeSubmitPrompt` | `additional_context`; sub-agent **không** nhận được luật **[xác thực]** |
| Qoder | `.qoder-plugin/plugin.json` → `hooks/qoder-hooks.json` (là **bản mẫu** phải chép tay vào `settings.json`) | `UserPromptSubmit`, `PreToolUse` matcher `task\|Task` | không có `SessionStart` → prompt đầu tiên gánh luôn việc kích hoạt **[xác thực]** |
| opencode | `opencode.json` + `.opencode/plugins/ponytail.mjs` | `config`, `experimental.chat.system.transform`, `command.execute.before` | nối luật vào mảng `system` mỗi lượt **[xác thực]** |
| pi | khoá `pi:{extensions,skills}` trong `package.json` | `before_agent_start` | trả về `{systemPrompt}` **[xác thực]** |
| Hermes | `plugin.yaml` + `__init__.py` | `pre_llm_call`, `pre_gateway_dispatch` | trả `{"context": …}` **[repo]** |
| MCP | `ponytail-mcp/index.js` | prompt `ponytail` + tool `ponytail_instructions` | **không có đường luôn-bật**, người dùng phải gọi tay **[xác thực]** |
| Gemini CLI | `gemini-extension.json`, `contextFileName: AGENTS.md` | — | cố ý không dùng hook **[xác thực]** |
| Windsurf · Cline · Kiro · Grok · Devin | `.windsurf/rules/`, `.clinerules/`, `.kiro/steering/`, `.agents/rules/`, `AGENTS.md` | — | file rule thuần **[xác thực]** |

### 3.6 Tầng chỉ-dẫn được canh bằng byte

`scripts/check-rule-copies.js:15-27` lấy `AGENTS.md` làm bản gốc rồi **so byte** 7 bản chép:
`.cursor/rules/ponytail.mdc`, `.windsurf/rules/ponytail.md`, `.clinerules/ponytail.md`,
`.agents/rules/ponytail.md`, `.qoder/rules/ponytail.md`, `.github/copilot-instructions.md`,
`.kiro/steering/ponytail.md`. Hai bản có frontmatter riêng của host thì bị strip trước khi so.

`SKILL.md` **không** so byte được (nó dài hơn bản rút gọn), nên script chuyển sang canh 9 cụm từ
`INVARIANTS` phải tồn tại nguyên văn ở cả `SKILL.md` lẫn `AGENTS.md` (`:44-62`). Script tự nhận
đúng giới hạn của mình bằng một chú thích `ponytail:` — *"canary, not full equality"* — và ghi
sẵn đường nâng cấp: sinh các bản chép từ `SKILL.md` nếu canary này để lọt drift thật. Đây là
**đúng tinh thần bộ luật của chính nó**: một phép kiểm chạy được, không framework, có ghi nợ.

Một cơ chế lùi bước đáng chú ý: khi phát hiện `.cursor/rules/ponytail.mdc` có trong workspace,
hook **không bơm gì cả** mà chỉ trả về một dòng thông báo (`hooks/ponytail-runtime.js:59-78`,
`hooks/ponytail-activate.js:41-51`). Lý do: rule luôn bật đã đặt bộ luật trước mọi prompt, và không
hook nào tắt được một rule — bơm thêm bản thứ hai chỉ tạo ra hai bản có thể mâu thuẫn. Thông báo
đó còn dặn agent nói lại với người dùng rằng muốn đổi mode thì phải xoá rule đi.

---

## 4. Chất lượng và rủi ro kỹ thuật (mặt C)

### 4.1 Số đo thật, đo lại hôm nay

| Bộ test | Kết quả |
|---|---|
| `node --test tests/*.test.js` (gốc) | **94 pass / 95 test / 1 fail** |
| `npm test --prefix pi-extension` | **23 / 23 pass** |
| `npm test --prefix ponytail-mcp` | **3 / 3 pass** |

**Test đỏ duy nhất không phải lỗi của repo.** Đó là
`tests/correctness.test.js:77` — *"csv: correct pandas one-liner passes"* — và nó **thực sự thi
hành** đoạn Python `import pandas as pd` qua `benchmarks/correctness`. Máy này không có `pandas`
(`ModuleNotFoundError`), nên assert ở `:85` thành `false !== true`. Đây là **thiếu môi trường**,
không phải khiếm khuyết mã nguồn.

Nhưng có một điểm đáng lưu ý về chính cách đóng gói test: script `test` ở `package.json` nối ba
bộ bằng `&&` (`node --test tests/*.test.js && npm test --prefix pi-extension && npm test --prefix
ponytail-mcp`). Nghĩa là **một test đỏ ở bộ gốc sẽ chặn đứng hai bộ sau, chúng không hề chạy**.
Trên một máy thiếu `pandas`, `npm test` báo đỏ và im lặng bỏ qua 26 test hoàn toàn lành. Phải gọi
tay từng bộ mới thấy con số thật.

Mặt tích cực thì rõ: 95 test cho một repo 166 file, các hook có test riêng, và **nhiều test bám
thẳng vào số hiệu issue** (#443 treo phiên, #506 lọc sub-agent, #817 Cursor, #528 VS Code
Copilot) — dấu hiệu của một repo sửa bug bằng cách để lại phép kiểm, đúng điều bộ luật của nó đòi.

### 4.2 Phát hiện 1 — adapter Hermes KHÔNG mỏng, nó phá chính luật của repo

Repo tự đặt ra luật cho adapter, `docs/agent-portability.md:37`:

> Keep adapters thin. When a host supports skills or hooks, point it at the […]

Và mọi adapter JS đều giữ đúng luật đó — cả ba đều `require` chung một builder:

- `pi-extension/index.js` → `require("../hooks/ponytail-instructions.js")`
- `ponytail-mcp/instructions.js` (26 dòng, mỏng đúng nghĩa)
- `.opencode/plugins/ponytail.mjs`

**Nhưng `__init__.py` (217 dòng, plugin Hermes, đi cặp với `plugin.yaml`) viết lại TOÀN BỘ builder
bằng Python.** Nó có bản sao riêng của: hằng số mode, `_config_dir()`, `_default_mode()`,
`_strip_frontmatter()`, `_filter_skill_body_for_mode()`, `_fallback_instructions()` và
`build_injected_context()`.

Lý do kỹ thuật thì chính đáng — tiến trình Python không `require` được một module CommonJS. Cái
giá phải trả cũng rõ: **hai bản cài đặt của cùng một logic, và việc giữ chúng khớp nhau hoàn toàn
là thủ công.** Đây không phải lỗi phong cách; mục 4.3 cho thấy nó đã đẻ ra lệch thật.

### 4.3 Phát hiện 2 — hai bản lọc luật đã lệch nhau, và chưa ai canh

Nhắc lại mục 2.5: bản JS cố ý **đòi dấu ngoặc kép** khi nhận diện dòng ví dụ mẫu, với một comment
dài giải thích vì sao (`hooks/ponytail-instructions.js:33-36`), và có hẳn một test mang tên
*"filterSkillBodyForMode does not drop a rule bullet whose label matches a mode name"*
(`pi-extension/test/helpers.test.js:121`) để canh đúng điều đó.

Bản Python **không có dấu ngoặc kép** (`__init__.py:80`):

```python
example_label = re.match(r"^-\s*([^:]+):\s*", line)   # JS: /^-\s*([^:]+):\s*"/
```

Hôm nay hai bản vẫn lọc **giống hệt nhau**, vì cả ba dòng ví dụ ở `skills/ponytail/SKILL.md:85-87`
đều có ngoặc kép. Nên đây là **lỗi tiềm ẩn, chưa phát tác** — nhưng nó phát tác vào đúng ngày ai
đó thêm vào `SKILL.md` một bullet luật bình thường bắt đầu bằng tên mode, kiểu `- Full: …`. Khi
đó: bản JS giữ dòng luật ấy ở mọi mode (test canh), bản Python **âm thầm xoá** nó ở mọi mode khác
— tức người dùng Hermes nhận một bộ luật thiếu, không báo lỗi, không ai biết.

**Và không có tấm lưới nào bắt được chuyện đó:**

- `scripts/check-rule-copies.js` canh 7 bản chép của `AGENTS.md` nhưng **không hề nhắc tới
  `__init__.py`** (kiểm chứng: grep `__init__` trong `scripts/` không ra kết quả nào).
- `tests/hermes-plugin.test.js` có test cho bản Python, nhưng nó kiểm Python **một mình** — không
  bao giờ đem đầu ra của Python so với đầu ra của JS trên cùng một đầu vào.

Một test so sánh chéo hai builder trên cùng `SKILL.md` sẽ đóng được khe hở này — nhưng xin nhắc
lại phạm vi của tài liệu: đây là repo bên thứ ba, chúng ta **không** đề xuất bản vá.

### 4.4 Phát hiện 3 — `review` mode xử sự khác nhau giữa hai bản, có test mà không có tài liệu

Cùng một mode `review`, hai kết quả khác hẳn:

| | Trả về gì |
|---|---|
| **JS** (`hooks/ponytail-instructions.js:80-82`) | **Một dòng** trỏ sang skill `/ponytail-review` |
| **Python** (`__init__.py:110-112`) | **Toàn bộ thân** `skills/ponytail-review/SKILL.md`, bơm thẳng vào context |

Đây **không phải tai nạn** — có test khẳng định hành vi Python là cố ý:
`tests/hermes-plugin.test.js:152`, *"Hermes plugin review mode injects the real review skill
body"*. Vấn đề là sự khác biệt này **không được ghi ở đâu cả**: người đọc `SKILL.md` hay
`docs/agent-portability.md` không có cách nào biết rằng chi phí context của `review` trên Hermes
lớn hơn hẳn trên các host khác.

### 4.5 Phát hiện 4 — "mode giữ đến hết phiên" chỉ đúng theo nghĩa đen với đúng một host

`skills/ponytail/SKILL.md` hứa mức cường độ giữ nguyên *"until changed or session end"*. Thực tế
mode được lưu ở **ba phạm vi khác nhau**:

| Host | Lưu ở đâu | Phạm vi thật |
|---|---|---|
| **pi** | `pi.appendEntry('ponytail-mode')`, đọc lại bằng `resolveSessionMode()` (`pi-extension/index.js`) | **Đúng theo phiên** — chỉ host này khớp lời hứa |
| **Hook JS** (Claude, Codex, Cursor, Qoder, Copilot) | File `.ponytail-active` trong thư mục state (`hooks/ponytail-runtime.js:39-44`) | **Phạm vi máy** — hai phiên chạy song song dùng chung một file, phiên này đổi mode thì phiên kia đổi theo |
| **Hermes** | Biến toàn cục `_current_mode` của tiến trình (`__init__.py:27`, ghi ở `:168`/`:176`) | **Phạm vi tiến trình** — và `_pre_llm_call(session_id="")` **có nhận** `session_id` nhưng **không dùng** (`__init__.py:125-126`), nên mọi phiên trong cùng tiến trình chia nhau một mode |

Hệ quả thực tế, không lý thuyết: mở hai cửa sổ Claude Code, gõ `/ponytail ultra` ở cửa sổ A thì
cửa sổ B cũng nhảy sang `ultra` ở lượt sau. Đó là hành vi hợp lý cho một cái cờ trên máy, nhưng
nó không phải cái câu "session end" mô tả.

### 4.6 Đánh giá chung

**Điểm mạnh — thật, không xã giao:**

- **Hướng fail được chọn có ý thức ở mọi chỗ:** hook thà im còn hơn treo phiên (mục 3.3), bộ lọc
  sub-agent thà bơm thừa còn hơn bỏ sót, đọc file lỗi thì có bản luật dự phòng nhúng cứng.
- **Comment giải thích *vì sao*, không giải thích *cái gì*.** Gần như mọi đoạn khó đều kèm số hiệu
  issue và mô tả tình huống hỏng thật (`hooks/ponytail-runtime.js:8-12`, `:23-28`,
  `hooks/ponytail-mode-tracker.js:147-155`). Đây là chất lượng trên trung bình khá xa.
- **Repo tự ăn món mình nấu:** có chú thích `ponytail:` ghi nợ kỹ thuật thật trong chính mã nguồn,
  và `check-rule-copies.js` tự nhận mình là *"canary, not full equality"* kèm đường nâng cấp.

**Rủi ro, xếp theo mức độ:**

| # | Rủi ro | Mức | Vì sao |
|---|---|---|---|
| 1 | Hai bản builder JS/Python lệch nhau âm thầm (4.3) | **Cao** | Đã lệch thật, chưa phát tác, không guard nào bắt |
| 2 | `review` mode khác nhau giữa hai bản, không tài liệu (4.4) | Trung bình | Có test nên không vỡ, nhưng gây hiểu sai chi phí context |
| 3 | `.ponytail-active` là phạm vi máy chứ không phải phiên (4.5) | Trung bình | Lệch với lời hứa trong chính bộ luật |
| 4 | `npm test` nối bằng `&&` che mất 26 test khi bộ gốc đỏ (4.1) | Thấp–TB | Làm sai lệch nhận định về sức khoẻ repo |
| 5 | Nhận diện host dựa hoàn toàn vào biến môi trường | Thấp | Host đổi tên biến là hỏng im lặng — repo đã dính đúng cú này một lần với VS Code Copilot (#528) |

---

## 5. Repo tự khai vs nhà cung cấp xác nhận (mặt D)

Mục này trả lời một câu hỏi rất thực tế: **Ponytail nói nó chạy trên ~20 nền tảng — có bao nhiêu
phần trong đó là sự thật kiểm chứng được, và bao nhiêu là repo tự nói?**

Cách đọc nhãn:

- **đã xác thực (URL)** — đã mở tài liệu chính thức của nhà cung cấp và đối chiếu.
- **repo tự khai** — chỉ có trong mã nguồn/tài liệu Ponytail, chưa đối chiếu được nguồn ngoài.

### 5.1 Nhóm "file rule" — tầng chỉ-dẫn

| Nền tảng | Ponytail ship gì | Trạng thái | Nguồn |
|---|---|---|---|
| Cursor | `.cursor/rules/ponytail.mdc` | **đã xác thực (URL)** — và xác thực luôn lựa chọn đuôi `.mdc`: file `.md` đặt trong `.cursor/rules` **bị hệ thống rule bỏ qua** | cursor.com/docs/rules |
| Windsurf | `.windsurf/rules/ponytail.md` | **đã xác thực (URL)** — nhưng kèm cảnh báo: Windsurf nay là Devin Desktop, đường **ưu tiên** đã chuyển sang `.devin/rules/*.md`, `.windsurf/rules/` chỉ còn là **fallback kế thừa**. Giới hạn 12.000 ký tự/file | docs.devin.ai/desktop/cascade/memories |
| Kiro | `.kiro/steering/ponytail.md` | **đã xác thực (URL)** — đúng thư mục, đúng khoá frontmatter `inclusion: always\|fileMatch\|manual` | kiro.dev/docs/steering |
| Qoder | `.qoder/rules/ponytail.md` + hooks trong `settings.json` | **đã xác thực (URL)** — cả hai đường đều đúng tài liệu | docs.qoder.com/user-guide/rules · docs.qoder.com/qoder/hooks |
| Cline | `.clinerules/ponytail.md` | **đã xác thực (URL)** — `.clinerules/` đúng là thư mục được gộp; tài liệu còn nói Cline gộp cả `.txt`, không chỉ `.md` | docs.cline.bot/features/cline-rules |
| Devin / Grok | `.agents/rules/ponytail.md`, `AGENTS.md` | **đã xác thực (URL)** cho `AGENTS.md`; đường `.agents/rules/` là **repo tự khai** | agents.md |
| `AGENTS.md` (dùng chung) | Bản luật rút gọn | **đã xác thực (URL)** — quy ước mở, hơn 20 công cụ hỗ trợ, hơn 60.000 dự án dùng. Đây là lá bài mạnh nhất của tầng chỉ-dẫn | agents.md |

### 5.2 Nhóm "plugin / hook" — tầng plugin

| Nền tảng | Ponytail dựa vào điều gì | Trạng thái | Nguồn |
|---|---|---|---|
| Claude Code | `plugin.json`; hook `SessionStart`/`SubagentStart`/`UserPromptSubmit`; stdout thô trừ SubagentStart | **đã xác thực (URL)**, và xác thực đúng chỗ tinh tế nhất: tài liệu ghi rõ chỉ `UserPromptSubmit`, `UserPromptExpansion`, `SessionStart`, `PostModelSwitch` biến stdout văn bản thuần thành context — nên nhánh bọc JSON riêng cho `SubagentStart` (`hooks/ponytail-runtime.js:125`) là **đúng đặc tả, không phải mẹo**. `SubagentStart` cũng là event có thật | code.claude.com/docs/en/hooks · /plugins-reference |
| Claude Code (manifest) | Repo khai `name`+`version`+`description` | **đã xác thực (URL)** — nhưng tài liệu nói **chỉ `name` là bắt buộc**; hai trường kia là tự nguyện, không sai nhưng cũng không bắt buộc như repo ngụ ý | code.claude.com/docs/en/plugins-reference |
| Codex | Dùng **chung** file hook với Claude Code | **đã xác thực (URL), kèm một đính chính của chính tôi:** vòng nghiên cứu trước kết luận "Codex chỉ đọc hook ở đường dẫn cố định nên `claude-codex-hooks.json` sẽ không tự nạp". Tài liệu cho thấy **chữ "chỉ" là sai** — ngoài `~/.codex/hooks.json`, `<repo>/.codex/hooks.json` và `[hooks]` trong `config.toml`, plugin **còn bundle hook được qua manifest hoặc `hooks/hooks.json`**. Vậy chiến lược dùng chung file của Ponytail khả thi hơn tôi tưởng | learn.chatgpt.com/docs/hooks |
| Copilot | `hooks/copilot-hooks.json`, schema `{"version":1,…}`, event camelCase | **đã xác thực (URL)** — đúng schema, đúng kiểu camelCase; tài liệu nói thêm PascalCase vẫn được chấp nhận để tương thích VS Code | docs.github.com/en/copilot/reference/hooks-reference |
| Cursor (hook) | `hooks/cursor-hooks.json`, `sessionStart` + `beforeSubmitPrompt` | **đã xác thực (URL)** — schema `{"version":1,"hooks":{…}}` đúng | cursor.com/docs/agent/hooks |
| Gemini CLI | `gemini-extension.json` + `contextFileName: AGENTS.md`, **cố ý không dùng hook** | **đã xác thực (URL)** — khoá `contextFileName` có thật (mặc định `GEMINI.md`). Và quyết định né hook là hợp lý: Gemini CLI có hook nhưng tên event khác hoàn toàn (`BeforeAgent`/`BeforeModel`/`PreCompress`…), dùng chung file là bất khả | github.com/google-gemini/gemini-cli — docs/extensions/reference.md, docs/hooks/reference.md |
| MCP | `ponytail-mcp/`: prompt + tool, **không có đường luôn-bật** | **đã xác thực (URL)** — và đây là xác thực quan trọng nhất về mặt kiến trúc: spec nói `prompts` là **user-controlled** (người dùng phải tự chọn), còn `instructions` thì chỉ **MAY** được thêm vào system prompt. Nghĩa là MCP **không thể** thay hook; `ponytail-mcp/` đúng là tầng bổ sung, không phải tầng chính | modelcontextprotocol.io/specification/2025-06-18/server/prompts |
| opencode | Hook `experimental.chat.system.transform` | **đã xác thực (URL) — nhưng chỉ ở type, không ở docs.** Type đã publish của `@opencode-ai/plugin` khai đúng hook này với đúng chữ ký; trang tài liệu chính thức **không liệt kê nó**. Đây là rủi ro thật: Ponytail đang bám vào một API mang chữ `experimental` và không có cam kết tài liệu | unpkg.com/@opencode-ai/plugin/dist/index.d.ts |
| pi | Khoá `pi:{extensions,skills}`, hook `before_agent_start` trả `{systemPrompt}` | **đã xác thực (URL) về cơ chế, nhưng gói đã đổi tên:** `@mariozechner/pi-coding-agent` **đã deprecated** ("please use @earendil-works/pi-coding-agent instead"); gói mới đang ở 0.85.1 | registry.npmjs.org/@mariozechner/pi-coding-agent |
| Hermes | `plugin.yaml` + `__init__.py`, hook `pre_llm_call`/`pre_gateway_dispatch` | **repo tự khai** — không tìm được tài liệu nhà cung cấp công khai để đối chiếu. Đáng lưu ý: đây cũng chính là adapter có vấn đề chất lượng nặng nhất (mục 4.2–4.4) | — |

### 5.3 Ba điều rút ra từ mặt D

1. **Phần lớn lời khai của repo là thật, và thật ở mức chi tiết.** Không chỉ "có hỗ trợ nền tảng
   X" mà đúng cả đuôi file (`.mdc` chứ không phải `.md`), đúng schema hook, đúng kiểu chữ
   camelCase. Đây là repo có đi đọc tài liệu, không phải đoán.
2. **Ba chỗ đã cũ so với thực tế nhà cung cấp:** `.windsurf/rules/` tụt xuống hàng fallback,
   gói `pi` đã đổi tên, và hook opencode được dùng chỉ tồn tại ở type chứ không có trong docs.
   Không cái nào làm repo hỏng hôm nay — cả ba đều là **nợ bảo trì**, loại nợ sinh ra từ việc
   phụ thuộc vào ~20 nền tảng bên thứ ba đang chuyển động.
3. **Một đính chính của chính tài liệu này** (hàng Codex, mục 5.2): kết luận "Codex sẽ không tự
   nạp file hook đặt tên khác" là **quá mạnh**. Tôi ghi lại đây thay vì lặng lẽ sửa, vì mặt D
   này chính là mặt nói về việc phân biệt điều đã kiểm chứng với điều mới chỉ nghe nói.

---

## 6. So sánh rộng với TDQ-Workflow, trên cả vòng đời một request

### 6.1 Kết luận trước, lập luận sau

**Hai thứ này không cạnh tranh nhau — chúng nằm ở hai trục vuông góc, và ghép được vào nhau.**

- **Ponytail điều chỉnh *NỘI DUNG* của quyết định kỹ thuật:** xây ít nhất có thể, dừng ở bậc thang
  đầu tiên còn đứng vững.
- **TDQ-Workflow điều chỉnh *QUY TRÌNH* ra quyết định:** ai duyệt, duyệt ở chặng nào, bằng chứng
  nào phải để lại, lượt làm việc được phép kết thúc khi nào.

Một người có thể chạy cả hai cùng lúc mà không xung đột: Ponytail sống bên trong bước *implement*
của TDQ, như một luật viết code; TDQ không có ý kiến gì về việc bạn nên dùng `lru_cache` hay tự
viết class cache.

### 6.2 Bảng đối chiếu theo từng chặng của vòng đời

| # | Chặng | Ponytail | TDQ-Workflow |
|---|---|---|---|
| 1 | **Tiếp nhận yêu cầu** | Không có khái niệm "request". Luật áp vào mọi lượt chat như nhau | `tdq-intake`: mở request có slug, chọn lane `quick`/`full`, đặt loại request, mở nhánh git riêng |
| 2 | **Phân tích trước khi làm** | Có, nhưng ở dạng mệnh lệnh cho agent: *"Never lazy about understanding the problem"* (`skills/ponytail/SKILL.md:97-101`) — không sinh ra sản phẩm nào | Một file brief bắt buộc 3 mục, có bậc phân tích B0/B1/B2, có vòng chốt phạm vi, có kiểm lớp tìm kiếm (LSP/grep/lumen) |
| 3 | **Chốt phạm vi & spec** | Không có. Việc "cắt phạm vi" xảy ra *ngầm* trong đầu agent qua bậc 1 của thang ("việc này có cần tồn tại không") | Vòng scope tối đa 5 mặt + spec có ranh giới module, mức đầu tư được **suy ra** chứ không hỏi |
| 4 | **Lập kế hoạch** | Không có | File plan: task có mã, ước lượng `(eNm)`, dòng `Chạm:` làm bản đồ bán kính ảnh hưởng, DoD mỗi dòng kiểm được bằng một lệnh |
| 5 | **Cổng duyệt của con người** | **Không có cổng nào.** Người dùng chỉ điều khiển *cường độ* (`/ponytail lite\|full\|ultra\|off`) | Cổng cứng: `spec` → `plan` → `mode`, ghi nhận bằng `tdq_state.py approve` kèm **nguyên văn câu người dùng**; câu mơ hồ không tính là duyệt |
| 6 | **Thực thi** | Định hình *cách* viết: thang 7 bậc, khuôn trả lời `[code] → skipped: [X], add when [Y]` | Định hình *ai* viết và *theo thứ tự nào*: 3 mode (`main` / `subagent` nhiều worktree / `codex`), tick `[ ]`→`[~]`→`[x]` ngay khi từng task pass |
| 7 | **Kiểm chất lượng** | Một luật: code lười phải kèm **đúng một** phép kiểm chạy được, không framework (`skills/ponytail/SKILL.md:107-112`); cộng skill `/ponytail-review` soi diff tìm chỗ xây thừa | Pha QC riêng: đếm đúng số dòng DoD, mỗi dòng một phép kiểm có bằng chứng, tối đa 3 vòng fix, có cả agent QC độc lập |
| 8 | **Nhật ký & truy vết** | Chú thích `ponytail:` ghi nợ kỹ thuật tại chỗ, `/ponytail-debt` đi thu hoạch thành sổ nợ | `docs/workinglog/YYYY-MM-DD.md` là **điểm chặn**: chưa ghi thì không kết thúc được lượt |
| 9 | **Trạng thái bền vững giữa các lượt** | Một chuỗi ký tự: mode hiện tại, trong file `.ponytail-active` hoặc biến tiến trình | Một máy trạng thái: `state.json` với phase, các cờ duyệt, đường dẫn tài liệu, nhánh — và **chỉ được ghi qua CLI** |
| 10 | **Bàn giao / báo cáo** | Không có | Báo cáo ≤50 dòng, hỏi người dùng về commit, hợp nhánh về `nhanh_goc` |
| 11 | **Ép tuân thủ** | Bơm lại luật **mỗi lượt** — phòng agent quên | Hook `[TDQ:*]` chặn ở cổng Stop: còn task mở thì không cho kết thúc lượt |
| 12 | **Đa nền tảng** | **~20 host**, 5 khuôn JSON đầu ra, 7 bản chép luật được canh bằng byte | Gắn chặt với Claude Code (skill + hook + `tdq_state.py`); không có tầng chuyển đổi host |

### 6.3 Những chặng KHÔNG so được, và vì sao

Ba chỗ dưới đây, đặt hai bên cạnh nhau là so sai — không phải bên nào thiếu, mà là **câu hỏi
không áp dụng**:

- **Chặng 3, 4, 10 (spec, plan, báo cáo).** Ponytail không có *không phải vì nó sơ sài*, mà vì nó
  không phải bộ điều phối công việc. Nó là một tài liệu 121 dòng được bơm vào context. Chê
  Ponytail thiếu plan cũng vô nghĩa như chê một bộ coding-style là thiếu máy CI.
- **Chặng 12 (đa nền tảng).** Ngược lại, TDQ-Workflow không có tầng đa host *không phải vì nó
  kém di động*, mà vì nó được xây cho đúng một host và khai thác rất sâu host đó (hook chặn Stop,
  sub-agent, worktree, state CLI). Bài toán 5 khuôn JSON của Ponytail nảy sinh **chính xác vì** nó
  từ chối bám vào một host.
- **Chặng 5 (cổng duyệt).** Ponytail *cố ý* không có cổng. Thêm một cổng duyệt vào Ponytail sẽ
  phá mục đích của nó: nó phải vô hình và không tốn công người dùng, nếu không sẽ chẳng ai bật.

### 6.4 Một đối lập đáng suy nghĩ: hai bên chọn hướng fail ngược nhau

Đây là điểm so sánh giá trị nhất, và nó không nằm ở "bên nào nhiều tính năng hơn".

| | Khi có sự cố |
|---|---|
| **Ponytail** | **Fail open — không bao giờ chặn.** Hook lỗi, stdin treo, đọc file hỏng → nuốt lỗi, bơm bản dự phòng, hoặc bơm rỗng, nhưng phiên làm việc **luôn chạy tiếp** (`hooks/ponytail-mode-tracker.js:147-155`) |
| **TDQ-Workflow** | **Fail closed — chặn có chủ ý.** Chưa ghi working log → không kết thúc được lượt. Còn task mở → hook `[TDQ:UNFINISHED]` từ chối đóng lượt. Muốn thoát phải **khai lý do** bằng `pause --ly-do` |

Cả hai đều đúng, vì cái giá của lỗi khác nhau: Ponytail hỏng thì mất một lời khuyên về style —
rẻ; đóng băng phiên làm việc của người dùng — đắt. TDQ hỏng thì mất dấu vết của một thay đổi code
thật — đắt; bắt người dùng gõ thêm một câu — rẻ.

### 6.5 TDQ-Workflow có thể học gì (và không nên học gì)

**Đáng học:**

- **Chú thích nợ có cấu trúc, thu hoạch được bằng máy.** Mẫu `ponytail:` + `/ponytail-debt` là một
  ý hay và rẻ: nợ kỹ thuật nằm ngay cạnh dòng code sinh ra nó, thay vì trong một file `TODO.md`
  không ai đọc. TDQ hiện ghi quyết định vào working log — đúng chỗ cho *quy trình*, nhưng không
  phải chỗ cho *nợ tại dòng code*.
- **Guard tự nhận giới hạn của chính nó.** `check-rule-copies.js` tự viết *"canary, not full
  equality"* kèm đường nâng cấp. Một phép kiểm thành thật về chỗ nó không phủ tới thì đáng tin hơn
  một phép kiểm im lặng.
- **Comment ghi số hiệu issue và tình huống hỏng thật**, thay vì mô tả lại code.

**Không nên học:**

- **Chép logic sang ngôn ngữ thứ hai rồi giữ khớp bằng tay** (mục 4.2–4.3). TDQ-Workflow có
  `scripts/*.py` và các skill markdown mô tả cùng một luật — đây đúng là loại lệch mà Ponytail
  đang mắc. Bài học rút ra: **chỗ nào buộc phải có hai bản, chỗ đó phải có một test so sánh chéo
  hai bản**, không phải một test cho mỗi bản.
- **Hứa một phạm vi mà cài đặt không giữ được** (mục 4.5, "session end" nhưng thực tế là phạm vi
  máy). Tài liệu nói quá cài đặt là một dạng nợ âm thầm.
