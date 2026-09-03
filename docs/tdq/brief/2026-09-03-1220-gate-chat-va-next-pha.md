# Brief — Gate dừng trả lời trong chat, và Next step nói rõ pha kế tiếp

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## Nguyên văn

> okay vậy tôi muốn phân tích thêm tdq workflow để ở mỗi gate sẽ dừng và trả trong turn chat
> không tạo popup câu hỏi chỉ trả câu hỏi trong chat và end turn chờ người dùng chat reply, và
> next step ngoài script chạy cũng sẽ có instruction pha tiếp theo trong skill để agent biết pha
> tiếp theo là gì, phòng trường hợp dùng trong agent ko hỗ trợ hook

**Mục tiêu đọc được từ câu này — hai phần tách rời:**

1. **Mọi cổng duyệt hỏi bằng chat thường, rồi kết lượt.** Không dùng tool popup
   (`AskUserQuestion`) ở bất kỳ cổng nào. Hỏi xong là dừng lượt, chờ user trả lời bằng chat.
2. **Dòng `Next step:` của mỗi skill phải nói pha kế tiếp là gì**, không chỉ đưa câu lệnh script.
   Lý do user nêu: chạy trong agent **không hỗ trợ hook** thì không có `[TDQ:NEXT]` nào bơm
   hướng dẫn vào, agent phải tự đọc được pha tiếp theo từ chính skill.

**Phạm vi đoán ban đầu:** các skill có cổng (`tdq-intake`, `tdq-spec`, `tdq-plan`, `tdq-build`,
`tdq-check-status`), file luật `tdq-conventions/references/approval.md` và `phases.md`, cùng
test khoá luật. Chưa rõ có chạm hook hay script không — phần 2 nhắm vào trường hợp KHÔNG có hook.

**Chỗ chưa rõ, phải hỏi:**

- Phần 1: cấm popup ở mọi cổng, hay cấm ở mọi câu hỏi cho user (kể cả hỏi ngoài cổng)?
- Phần 2: "instruction pha tiếp theo" ghi tới mức nào — chỉ tên pha + skill nạp, hay chép cả
  việc-phải-làm và điều-kiện-xong của pha đó?
- Có cần cơ chế **chặn** (test/hook) hay chỉ cần luật viết ra là đủ?

## Hiểu & kiến thức

### Hiện trạng đo được (2026-09-03, trước khi sửa)

**Phần 1 — luật cấm popup đã có nhưng chỉ nằm ở MỘT chỗ hẹp.**
`skills/tdq-intake/references/interview.md:44` viết: "Always ask with a list in chat — no
AskUserQuestion". Đó là file của vòng phỏng vấn trong phase analyze. Quét toàn repo
(`skills/`, `hooks/`, `scripts/`) thì đây là chỗ **duy nhất** nhắc tên tool đó. Các cổng khác chỉ
viết "STOP and wait for the user" mà không nói hỏi bằng cách nào:

| Cổng | Chỗ viết | Có cấm popup không |
|---|---|---|
| chọn lane | `tdq-intake/SKILL.md:69` | không |
| duyệt spec | `tdq-spec/SKILL.md` (description + thân) | không |
| duyệt plan | `tdq-plan/SKILL.md` | không |
| chọn mode | pha `mode` trong `phases.md` | không |
| hỏi commit | `tdq-build/SKILL.md` | không |
| vá trạng thái | `tdq-check-status/SKILL.md:50,52` | không |
| vòng phỏng vấn | `tdq-intake/references/interview.md:44` | **có** |

Không có test nào khoá luật này. Luật riêng của user (`~/.claude/CLAUDE.md`) cũng có yêu cầu
tương tự nhưng đó là file ngoài repo, không đi theo bản portable.

**Phần 2 — `Next step:` hiện là câu lệnh, không phải mô tả pha.** 12 dòng `Next step:` trong
`skills/*/SKILL.md`; phần lớn chỉ đưa `tdq_state.py set phase=<x>`. Người/agent đọc xong biết
phải CHẠY gì, không biết pha kế tiếp LÀM gì. Thông tin đó có đủ trong
`tdq-conventions/references/phases.md` — bảng sinh tự động từ `PHASE_TABLE` của
`scripts/tdq_state.py`, mỗi pha một hàng (vào khi nào · việc duy nhất · lệnh onward · xong khi ·
cấm gì) — nhưng skill không trỏ sang hàng tương ứng.

**Vì sao điều này quan trọng khi không có hook:** hướng dẫn pha kế tiếp hiện được bơm bằng hook
`[TDQ:NEXT]` (`hooks/scripts/prompt_context.py`, dùng `tdq_state.phase_key`). Bản portable Codex
và Antigravity có hook riêng, nhưng host không hỗ trợ hook thì mất hoàn toàn lớp nhắc này —
đúng kịch bản user nêu.

### Host nào thiếu hook — cơ sở cho phần 2

Research làm **inline**, không giao sub-agent: luật phiên này ghi rõ "Do not call the AgentTool
unless the user requested it", đè lên bước 3 của `analyze-full.md`. Một truy vấn Tavily, nguồn:
`hidekazu-konishi.com/entry/cli_coding_agents_comparison.html` và `github.com/weykon/agent-hooks`.

| Host | Hook | Ghi chú |
|---|---|---|
| Claude Code | có | PreToolUse/PostToolUse/SessionStart/Stop |
| Codex CLI | có (từ ~0.128) | postToolUse, userPromptSubmitted, errorOccurred |
| Cursor | có | `~/.cursor/hooks.json` |
| Kiro / Amazon Q CLI | có | agentSpawn, userPromptSubmit, stop |
| OpenCode | có | stop, userPromptSubmit |
| Gemini CLI | **không** hook lifecycle | chỉ custom command + extension |
| GitHub Copilot CLI | **không** | chỉ custom agent + instruction + MCP |
| Aider | **không** | không MCP, không hook |

Kết luận: kịch bản user nêu là **thật**, không phải giả định. Gemini CLI và Copilot CLI đọc được
`SKILL.md` nhưng không có chỗ nào bơm `[TDQ:NEXT]`. Với hai host đó, mọi thứ agent biết về pha kế
tiếp phải nằm trong chính văn bản skill.

Hệ quả cho phần 1: các host đó cũng **không có** tool popup kiểu `AskUserQuestion`. Luật "hỏi bằng
chat rồi kết lượt" vì thế vừa là lựa chọn của user, vừa là mẫu số chung duy nhất chạy được ở mọi
host — không phải hạn chế riêng của Claude Code.

## Hỏi đáp

Vòng phỏng vấn ngày 2026-09-03 12:33. User trả lời `1a 2b nhưng chỉ bổ trợ nếu hook không work
ổn, 3a`, kèm một yêu cầu mới ngay trong câu trả lời.

**1 → A. Cấm popup ở MỌI câu hỏi cho user**, không chỉ 7 cổng. Một luật, không ngoại lệ. Hỏi xong
là kết lượt, chờ user chat trả lời.

**2 → B, có điều kiện.** `Next step:` ghi tên pha kế + trỏ sang hàng tương ứng trong
`phases.md`, KHÔNG chép cả việc-phải-làm và điều-kiện-xong vào từng skill. Nguyên văn điều kiện
user thêm: "chỉ bổ trợ nếu hook không work ổn". Nghĩa là lớp chữ này là **lớp dự phòng**, không
thay hook: hook `[TDQ:NEXT]` vẫn là đường chính khi host có hook; dòng `Next step:` chỉ gánh việc
khi host không bơm được gì. Hệ quả thiết kế: không nhân bản nội dung `phases.md` vào 12 skill —
tránh 12 bản sao lệch nhau — mà mỗi skill chỉ cần đủ để agent biết đi đâu đọc tiếp.

**3 → A. Có test khoá.** Luật viết ra không đủ; cần test quét `skills/` bắt tên tool popup, và
test bắt mọi dòng `Next step:` phải nêu pha kế tiếp.

**Yêu cầu thứ 4, mới, nguyên văn:** "tôi muốn bổ sung và cuối turn chat phải có một line gạch qua
để đảm bảo nhìn đúng ổn". Hiểu: mọi lượt chat kết thúc bằng một đường kẻ ngang `---` ở dòng cuối,
để user nhìn thấy lượt đã hết và khối hiển thị đúng. Hiện `---` đã có nhưng chỉ trong khối cổng
(thành phần 4 của `user-facing-block.md`), và ở đó nó nằm TRƯỚC khối trả lời chứ không phải dòng
cuối. Nên đây là luật mới, phải viết sao cho không mâu thuẫn với thành phần 5 ("khối trả lời là
phần cuối, không viết gì bên dưới") — sẽ chốt cách giải trong spec.

### Lộ trình

1. `spec` — chốt 4 luật: cấm popup mọi câu hỏi · `Next step:` nêu pha kế + trỏ `phases.md` ·
   test khoá cả hai · đường kẻ cuối lượt. Nêu rõ cách hoà giải luật mới với thành phần 4–5 của
   `user-facing-block.md`.
2. `diagram` — **BỎ**, vì repo này không có pha đó: `PHASE_TABLE` trong `scripts/tdq_state.py`
   chỉ có `no_state · analyze · spec · plan · mode · implement · qc · report · idle ·
   quick_analyze · quick`, và `skills/` không có `tdq-diagram`. Bản skill mà host nạp có nhắc
   pha này — đó là bản plugin khác, không phải mã trong repo. Theo repo.
3. `plan` — hợp đồng cho từng file: `user-facing-block.md`, `approval.md`, 12 `SKILL.md`,
   test mới trong `tests/`.
4. `mode` → `implement` → `qc` → `report`.

**Phạm vi file đã xác định:** `skills/tdq-conventions/references/user-facing-block.md` ·
`skills/tdq-conventions/references/approval.md` · `skills/tdq-conventions/references/phases.md`
(chỉ đọc, sinh tự động) · 12 `skills/*/SKILL.md` có dòng `Next step:` · `tests/` (test khoá mới).
Không chạm `hooks/` và `scripts/tdq_state.py`: hook vẫn là đường chính, phần này chỉ thêm lớp dự
phòng bằng chữ.
