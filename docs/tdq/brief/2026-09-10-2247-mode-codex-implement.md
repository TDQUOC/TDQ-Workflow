# BRIEF — Mode `codex implement`: agent con gọi Codex CLI thay vì sub-agent Claude
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## Nguyên văn

> tôi muốn mở request tạo ra thêm 1 agent và một mode codex implement. nghĩa là khi chọn mode
> đó sẽ tạo sub agent implement nhưng thay vì tạo subagent của claude code thì mỗi sub agent
> sẽ gọi codex thực thi. và claude sẽ check nhanh lại và tuần tự plan task sẽ y hệt claude sub
> agent implement

- **Mục tiêu**: thêm một cách chạy phase `implement` thứ ba. Hôm nay state chỉ có
  `VALID_MODES = ("main", "subagent")` (`scripts/tdq_state.py:31`); request này thêm mode thứ ba
  trong đó mỗi task được giao **không** cho sub-agent Claude mà cho **Codex CLI** thực thi.
- **Hai sản phẩm người dùng nêu rõ**:
  1. **Thêm 1 agent** — một định nghĩa agent mới bên cạnh `agents/tdq-implementer.md`, đóng vai
     người bọc (wrapper) gọi Codex và mang kết quả về đúng khuôn
     `TASK/STATUS/FILES/TEST/BRANCH/TICK-READY/NOTES`.
  2. **Thêm 1 mode** — nhãn người dùng chọn ở mode gate (hôm nay là 2 lựa chọn A/B ở
     `skills/tdq-plan/references/mode-gate.md`), ghi vào state như mode thứ ba.
- **Hai ràng buộc người dùng đặt ra, đọc thẳng từ câu nói**:
  - *"claude sẽ check nhanh lại"* — Claude không giao xong là tin: sau mỗi task Codex trả về,
    Claude phải tự kiểm lại. Bộ máy hôm nay đã có sẵn chỗ móc vào: `tdq_team.py check <task>`
    chạy lại đúng lệnh trên dòng `Test:` của task **bên trong worktree của task đó**, và `merge`
    từ chối nhánh có test đỏ (`skills/tdq-build/references/team-mode.md`).
  - *"tuần tự plan task sẽ y hệt claude sub agent implement"* — thứ tự và cách chia task KHÔNG
    đổi: vẫn `assign` → `audit` → vòng `wave`/`open`/`check`/`merge`/`sweep`, vẫn bộ 5 lý do
    giữ task `LY_DO_GIU`, vẫn một worktree một task. Mode mới chỉ đổi **ai gõ code trong
    worktree**, không đổi cách chia việc.

### Đã đo được gì ngay ở bước intake

- **Codex CLI có sẵn và chạy được không tương tác**: `/Users/tdq/.local/bin/codex`,
  `codex-cli 0.154.0`. `codex exec` có đủ mọi thứ một wrapper cần —
  `-C/--cd <DIR>` (đặt gốc làm việc = worktree của task), `-s/--sandbox workspace-write`,
  `--json` (JSONL sự kiện), `-o/--output-last-message <FILE>` (lấy đúng tin cuối, không phải
  parse cả log), `--output-schema <FILE>` (ép khuôn JSON trả về), `--skip-git-repo-check`,
  `--worktree`. Nghĩa là khuôn trả về 7 dòng của `tdq-implementer` có thể ép bằng schema chứ
  không phải nhắc suông.
- **Repo đã có sẵn một tầng Codex**: `portable_codex/` (bundle mang đi máy khác) với
  `hooks/scripts/codex_edit_gate.py`, `.codex/config.toml`, `.codex/hooks.json`, và
  `tdq_checkportable.py setup --trust` biết cách khai báo project tin cậy trong `~/.codex`.
  Tức là kinh nghiệm "Codex chạy hook/skill của TDQ" đã có, không phải làm từ số 0.
- **Tầng tìm kiếm (bậc 1b)**: `tdq_lsp.py check` → **7/7 bậc ĐẠT**, 0 cảnh báo.
- **Kiểm hiệu ứng index**: chọn `normalize_mode` (`scripts/tdq_state.py:862`).
  `grep -rn` → 3 file riêng biệt (`scripts/tdq_state.py`, `hooks/scripts/prompt_context.py`,
  `tests/test_mode_phase.py`); `mcp__lsp__find_references` → 9 ref thuộc 3 namespace, map về
  đúng 3 file đó. 3 ≥ 3 → **ĐẠT**, index trả lời được liên file.
  *Bẫy ghi lại để lần sau đỡ mất công*: gọi `find_references` trước khi file được mở trả
  `lsp error -32001: invalid AST`, và `find_symbol` toàn workspace trả 0 symbol; chạy
  `list_symbols` trên file đó một lần rồi gọi lại thì ra đủ. Không phải index hỏng.

### Kiểm kiến trúc hai tầng người dùng bổ sung (đo bằng lệnh thật)

Người dùng chốt thêm: **vẫn là Claude làm leader, vẫn phát task cho sub-agent Claude chạy song
song ở worktree riêng** — chỉ khác là mỗi sub-agent ấy *gọi Codex ở chế độ bỏ qua phê duyệt*
để không bật popup xin quyền, và Codex là người thực thi task. Tức hai tầng
(leader Claude → sub-agent Claude → tiến trình Codex), không phải leader gọi thẳng Codex.

Bốn điều đã đo được, không suy đoán:

1. **Chạy được thật, không hỏi gì.** Dò trong scratchpad:
   `codex exec -C <dir> -s workspace-write -c approval_policy="never" --skip-git-repo-check -o last.txt "<prompt>"`
   → `exit=0`, file được tạo đúng nội dung, tin cuối nằm gọn trong `last.txt`, không một lần
   chờ phê duyệt. **Bẫy cú pháp**: `codex exec` KHÔNG nhận `-a/--ask-for-approval`
   (`error: unexpected argument '-a' found`) — cờ đó chỉ có ở bản tương tác; ở `exec` phải đi
   qua `-c approval_policy="never"`.
2. **Phía Claude không popup.** `~/.claude/settings.json` có `defaultMode: bypassPermissions`
   và `Bash` nằm trong danh sách `allow`, nên sub-agent Claude gọi `codex` qua Bash là chạy
   thẳng. Phía Codex, `~/.codex/config.toml` khai `[projects."/Users/tdq"]`
   `trust_level = "trusted"` — repo và mọi worktree dưới `/Users/tdq` đều đã tin cậy sẵn.
3. **Hàng rào vùng file của TDQ hiện KHÔNG áp được lên Codex.** Đây là chỗ vỡ, và nó là chỗ
   quan trọng nhất. Luật "sub-agent ghi ra file ngoài `Chạm:` thì bị chặn tại lúc ghi" do hook
   `PreToolUse` của **Claude Code** thực hiện (`hooks/hooks.json` → `edit_gate.py`,
   `bash_gate.py`). Codex là tiến trình khác, tool call của nó không đi qua hook đó. Ở gốc repo
   `.codex/` chỉ có `config.toml`, **không có `hooks.json`** → một lượt Codex chạy trong repo
   này hiện không bị TDQ chặn gì cả. Bản mẫu để nối lại thì đã có sẵn trong
   `portable_codex/.codex/hooks.json`: `PreToolUse` matcher `apply_patch` → `codex_edit_gate.py`,
   matcher `Bash` → `bash_gate.py`. Thêm chi tiết đo được: lượt dò trên cho thấy Codex ghi file
   bằng `/bin/zsh -lc "printf ... > hello.txt"`, tức **chuyển hướng shell chứ không phải
   `apply_patch`** — nên nhánh phải gánh việc chặn là `bash_gate.py`, và nó cần đọc được cả
   dạng chuyển hướng. Cờ `--dangerously-bypass-hook-trust` tồn tại vì hook của Codex đòi được
   tin cậy trước; đây là thứ phải quyết ở spec.
4. **"Gọi codex" trên máy này KHÔNG phải gọi model của Codex.** `~/.codex/config.toml` đặt
   `model = "ag/gemini-3.8-flash-medium"` qua `model_provider = "9router"` trỏ vào router nội bộ
   `http://127.0.0.1:20128/v1` (đang sống, trả `http 200`), và `default_subagent_model` cũng
   vậy. Lượt dò in cảnh báo `Model metadata for 'ag/gemini-3.8-flash-medium' not found.
   Defaulting to fallback metadata; this can degrade performance`. `codex login status` báo
   `Logged in using ChatGPT` nhưng phần khai model ghi đè lên đó. Nghĩa là mode mới, chạy như
   cấu hình hiện tại, sẽ giao task cho một model Gemini Flash qua router nội bộ — chuyện này
   phải nói rõ với người dùng vì nó đổi hẳn kỳ vọng về chất lượng task.

5. **Hàng rào worktree thì CÓ thật, hàng rào từng file thì KHÔNG.** Đo tiếp để biết chỗ vỡ ở
   điểm 3 rộng tới đâu: đứng ở một thư mục nháp làm `cwd`, yêu cầu Codex ghi đường dẫn tuyệt
   đối vào trong repo chính. Kết quả `exit=0` nhưng **không có file nào được tạo**, Codex trả
   lời `Thao tác bị chặn bởi cơ chế sandbox ("operation not permitted")`, và log in
   `sandbox: workspace-write [workdir, /tmp, $TMPDIR]`. Nghĩa là: cách ly **ở mức worktree**
   do chính sandbox của Codex bảo đảm ở tầng hệ điều hành, Codex không tự vượt được — đúng
   thứ mode mới cần nhất. Chỗ còn thiếu chỉ là hàng rào **mịn hơn một bậc**: trong worktree
   của mình, Codex vẫn sửa được file ngoài `VÙNG FILE` của task. Chốt lại: mất hàng rào lúc
   ghi, còn nguyên hàng rào lúc gộp — nên cách vá khớp với chính câu người dùng
   (*"claude sẽ check nhanh lại"*) là **hậu kiểm trong worktree**: `git status --porcelain` /
   `git diff --name-only` so với `VÙNG FILE`, lệch một file là task FAIL.

**Ghi chú an toàn (không chép giá trị vào bất cứ đâu)**: `~/.codex/config.toml` đang chứa một
khoá `Authorization: Bearer …` dạng chữ thường, không mã hoá, ngay trong file cấu hình. Bất cứ
công cụ nào in file đó ra đều làm lộ khoá. Cần nhắc người dùng, và mọi thứ request này sinh ra
mà có đọc `~/.codex/config.toml` đều phải che theo đúng lối `mask_secrets` của
`scripts/setup_status.py`.

### Chỗ chưa rõ (để hỏi ở vòng phân tích)

- Codex chạy ở **quyền sandbox** nào, và cơ chế phê duyệt lệnh của Codex xử lý thế nào để một
  agent không tương tác không bị treo giữa đường.
- **Song song hay tuần tự**: sub-agent Claude cùng đợt chạy đồng thời trong một lượt trả lời.
  Nhiều tiến trình `codex exec` cùng lúc có phải cách chạy mong muốn, hay chạy lần lượt.
- *"Check nhanh lại"* dừng ở mức nào: chỉ `tdq_team.py check` (chạy lại test) hay Claude còn
  phải đọc diff của Codex trước khi gộp.
- Mode mới **thay** mode `subagent` hay **đứng cạnh** nó (mode gate thành 3 lựa chọn), và
  `tdq_bench.py simulate` — thứ quyết định đề xuất mode nào — có phải học thêm hệ số cho Codex.

## Hiểu & kiến thức

### Năng lực dùng được

Phân vân → DÙNG. Kiểm kê ngày 2026-09-10: 9 skill trên đĩa, cộng skill built-in
trong context. Không xoá bảng này kể cả khi không có dòng DÙNG nào.

| Skill | Nguồn | Phán quyết | Dùng ở đâu / Lý do loại |
|---|---|---|---|
| graphify | user | DÙNG | cuối mỗi turn có sửa code: `graphify extract . --code-only`; và `god-nodes` để biết `phase_row`/`cli` là hub trước khi chạm |
| tdq-conventions | plugin:tdq-workflow | NỀN | luật gốc của mọi phase, request này sửa chính tầng luật đó |
| tdq-intake | plugin:tdq-workflow | NỀN | phase đang chạy |
| tdq-spec | plugin:tdq-workflow | NỀN | phase kế tiếp |
| tdq-plan | plugin:tdq-workflow | NỀN | chứa `references/mode-gate.md` — file BỊ SỬA của request này |
| tdq-build | plugin:tdq-workflow | NỀN | chứa `references/team-mode.md` và bước rẽ mode — file BỊ SỬA |
| tdq-status | plugin:tdq-workflow | NỀN | in mode đang chọn, phải biết mode thứ ba |
| tdq-check-status | plugin:tdq-workflow | NỀN | đọc state, phải hiểu mode thứ ba |
| tdq-lsp-setup | plugin:tdq-workflow | NỀN | bậc 1b đã chạy, 7/7 ĐẠT |
| Đã xét 5 skill built-in khác (artifact-*, workshop, workflow-authoring) | built-in | KHÔNG | khác lĩnh vực |

### Chỗ mode bị đóng đinh trong code — đo bằng LSP + grep, không đoán

`subagent` không phải một chuỗi ở một chỗ; nó là **13 điểm neo**. Đây là bản đồ sửa chữa:

| # | Chỗ | Dạng ràng buộc | Vì sao đáng lo |
|---|---|---|---|
| 1 | `scripts/tdq_state.py:31` `VALID_MODES = ("main", "subagent")` | tuple đóng | nguồn chân lý, thêm phần tử là xong |
| 2 | `scripts/tdq_state.py:56` `MODE_LABELS` | nhãn hiển thị | phải có nhãn tiếng Việt cho mode mới |
| 3 | `scripts/tdq_state.py:64` `MODE_ALIASES` | bảng bí danh | người dùng gõ "codex" phải về đúng mode |
| 4 | `scripts/tdq_state.py:862` `normalize_mode` | chuẩn hoá | 9 ref / 3 namespace, đã đo bằng `find_references` |
| 5 | `scripts/tdq_state.py:1137` `IMPLEMENT_SUBAGENT_ROW` | hàng phase riêng | mode mới cần hàng riêng của nó |
| 6 | `scripts/tdq_state.py:1236` `phase_row()` — `if ... == "subagent"` | **rẽ nhánh cứng** | thêm mode thứ ba là thêm `if` thứ hai; đây là chỗ vi phạm OCP, nên đổi sang bảng tra `mode → row` |
| 7 | `scripts/tdq_team.py:1282` `canh_bao_lach_luat` — `if effective_mode(...) != "subagent": return None` | **hàng rào tự tắt** | "chỗ DUY NHẤT quyết định có đang lách luật hay không". Mode thứ ba lọt qua đây là mất sạch hàng rào team, không một test nào đỏ |
| 8 | `hooks/scripts/_common.py:49` `_PLAN_MODE = re.compile(r"...(main\|subagent)")` | regex đóng | đọc mode từ plan, không khớp là coi như không có mode |
| 9 | `hooks/scripts/prompt_context.py:58` `MODE` regex | regex đóng | nhận mode từ câu người dùng |
| 10 | `hooks/scripts/prompt_context.py:118` `return "subagent" if suggested == "main" else "main"` | **logic hai trạng thái** | phép đảo nhị phân; ba mode thì "cái còn lại" không còn nghĩa |
| 11 | `hooks/scripts/edit_gate.py:80` gợi ý `--mode <main\|subagent>` | chuỗi trợ giúp | in sai hướng dẫn cho người dùng |
| 12 | `skills/tdq-build/SKILL.md` bước 1 | rẽ 2 nhánh | phải thành 3 nhánh |
| 13 | `skills/tdq-plan/references/mode-gate.md` | đúng 2 lựa chọn A/B | mode gate phải thành 3 lựa chọn |

Cộng thêm **17 file test** có nhắc `subagent`, riêng `tests/test_mode_phase.py` là 16 ca.
`tests/test_agent_frontmatter.py` khoá thêm 4 điều với agent mới: phải khai `model` và
`effort`; phải có một dòng trong `skills/tdq-conventions/references/subagent-tuning.md`;
phải khai ngưỡng digest; phải cấm dán output thô của tool.

Kết luận đọc code: điểm 6, 7, 10 là ba chỗ **không thể thêm mode bằng cách thêm một `if`**
mà không làm hỏng thứ khác. Điểm 7 là chỗ nguy hiểm nhất vì nó **im lặng** khi hỏng.

### Research đa hướng — 14 điều đổi được thiết kế

Toàn văn: `docs/tdq/research/2026-09-10-2247-mode-codex-implement.md` (4 góc, 99 dòng).
Rút ra những điều **đổi thiết kế**, kèm mức tin cậy của nguồn:

1. `codex exec` **vốn đã ép `approval: never`** vì không có TTY; cờ `-c approval_policy="never"`
   là thừa nhưng vô hại → giữ cho tường minh, chống config cá nhân của máy khác. [kinh nghiệm]
2. `approval_policy="untrusted"` **bị khai tử** ở v0.149.0 và nay fail cứng — tuyệt đối không
   sinh giá trị đó ở bất cứ đâu (ta đang ở 0.154.0). [chính thức]
3. Mặc định của `codex exec` là `read-only` → **bắt buộc** truyền `-s workspace-write`.
   `--full-auto` là compat cũ, in cảnh báo deprecate → không dùng. [kinh nghiệm]
4. `--output-schema <file>` + `-o <file>` là cơ chế **chính thức** để ép khuôn JSON kết quả →
   dùng làm giao thức báo cáo task giữa Codex và sub-agent Claude, **đừng parse văn xuôi**.
   Schema nên `additionalProperties: false` và `required` đầy đủ. [chính thức]
5. **Không có bảng exit code** nào được tài liệu hoá → xác minh phải bằng **hiệu ứng thật**
   (`git diff` trong worktree + chạy lại test), không tin exit code. [không tìm được]
6. Matcher hook `Bash` và `apply_patch` (khớp cả alias `Edit`/`Write`) là **tên có thật** —
   bản mẫu `portable_codex/.codex/hooks.json` không bịa. Không có matcher tên `shell`. [chính thức]
7. `PreToolUse` của Codex **chỉ deny được**; `allow`/`ask`/`updatedInput` bị runtime từ chối →
   gate phải là một quyết định duy nhất "deny + reason", không thể rewrite đường dẫn. [kinh nghiệm]
8. Độ phủ của `apply_patch` **bị nghi ngờ** (nhiều nguồn: chỉ đường `Bash` bắn hook) → gate
   `Bash` là phòng thủ chính, và hook **không được là hàng rào duy nhất**. [kinh nghiệm]
9. Issue **#32491**: `codex exec` bỏ qua trust đã persist, hook project chỉ chạy khi truyền
   `--dangerously-bypass-hook-trust` → nếu dùng hook thì phải truyền **mỗi lần gọi**. [chính thức, issue mở]
10. Hooks có thể cần `[features] codex_hooks = true`; hai nguồn **mâu thuẫn** → phải đo trên máy.
11. **Xung đột chạy song song là thật**: issue #11435 (các phiên exec song song lẫn session
    restore của nhau), #20213 (khoá SQLite không retry BUSY → treo), codex-plugin-cc#382
    (`~/.codex` không an toàn nhiều người ghi). → mỗi sub-agent phải được cấp **`CODEX_HOME`
    riêng** + `[history] persistence = "none"`, và phải sao auth vào đó. [chính thức]
12. `--ephemeral` chỉ có ở `exec` nhưng ngữ nghĩa không tài liệu hoá → chỉ bổ trợ, **không
    thay** `CODEX_HOME` riêng. [không rõ]
13. "Codex báo tests pass" **không phải bằng chứng**; đo thực tế thấy output subagent mất ~40%
    → kênh kết quả phải là **file**, thiếu file hoặc parse fail = FAIL. [kinh nghiệm]
14. Cần **timeout tường minh ≥ 10 phút** (orchestrator thật dùng 600000 ms) và phải phân biệt
    ba trạng thái *timeout / fail / deny* trong log. Overhead của leader ≈ 8x so với Codex →
    mode chỉ đáng cho task lớn. Ghi **nguyên văn prompt** gửi Codex vào log, vì `AGENTS.md`
    và skill của Codex là hành vi ẩn không nhìn thấy từ phía leader. [kinh nghiệm]

### Đo lại trên máy này những chỗ research để ngỏ (Codex 0.154.0)

Research nêu 3 điều "phải đo" và 1 điều "mâu thuẫn nguồn". Đã dò hết bằng một repo nháp có
`.codex/hooks.json` gắn hook thật. Kết quả:

| # | Câu hỏi | Kết quả đo | Đổi gì trong thiết kế |
|---|---|---|---|
| Đ1 | `codex exec` có tự ép `approval: never`? | **CÓ**. Không truyền cờ nào, log vẫn in `approval: never` và `sandbox: workspace-write` | cờ `-c approval_policy="never"` là thừa; giữ để tường minh |
| Đ2 | Hook project có tự chạy? | **KHÔNG**. Lượt không có cờ: file được ghi, hook **không bắn** | issue #32491 tái hiện được ở 0.154.0 |
| Đ3 | `--dangerously-bypass-hook-trust` có làm hook chạy? | **CÓ**. Hook bắn, log in cảnh báo `hooks may run without review` | phải truyền cờ này **mỗi lần gọi**, nếu chọn dùng hook |
| Đ4 | Có cần `[features] codex_hooks = true`? | **KHÔNG**. Hook chạy mà không cần flag | gỡ được điều "mâu thuẫn nguồn" của research |
| Đ5 | `PreToolUse` deny có chặn thật? | **CÓ**. Trả `permissionDecision: deny` → file **không** được tạo, Codex tự báo `BLOCKED`. Nhưng **`exit=0`** | lớp 3 dùng được thật; và một lần nữa: **cấm tin exit code** |
| Đ6 | `CODEX_HOME` riêng có chạy? | **CÓ**. Session ghi vào home riêng (1 file), `~/.codex/sessions` không thêm. `[history] persistence = "none"` không làm vỡ gì | cách ly song song khả thi, nhưng xem cạm bẫy C3 |

**Khuôn payload hook của Codex** (đo thật, để agent mới không phải đoán): stdin nhận JSON có
`session_id`, `turn_id`, `transcript_path`, `cwd`, `hook_event_name`, `model`,
`permission_mode`, `tool_name`, `tool_use_id`, và `tool_input.command`. Có `tool_input.command`
nghĩa là gate `Bash` **đọc được nguyên văn lệnh** → hậu kiểm đường dẫn trong lệnh là làm được.
Khuôn trả về `hookSpecificOutput.permissionDecision` giống hệt Claude Code, nên
`hooks/scripts/_common.py:132-171` dùng lại được không phải viết mới.

### Ba cạm bẫy sẽ làm mode mới hỏng nếu không xử ở spec

- **C1 — `codex exec` TREO vô hạn khi stdin không phải TTY.** Lượt dò đầu tiên chỉ in
  `Reading additional input from stdin...` rồi đứng im quá 120 giây, không tạo file, không
  trả về. Thêm `< /dev/null` là chạy ngay, `exit=0`. Đây là cạm bẫy chết người vì sub-agent
  Claude gọi `codex` qua Bash thì stdin **không bao giờ** là TTY: thiếu một ký tự
  chuyển hướng là cả một đợt task treo, và leader thì đang `await` chờ sub-agent.
  Chốt: mọi lệnh gọi Codex bắt buộc có `< /dev/null` **và** một timeout tường minh.
- **C2 — `exit=0` nói lên rất ít.** Ba lượt dò khác nhau đều `exit=0`: lượt ghi được file,
  lượt bị hook deny, và lượt bị sandbox chặn. Nghĩa là "Codex xong việc" và "Codex bị chặn
  giữa đường" **không phân biệt được bằng exit code**. Bằng chứng duy nhất tin được là
  hiệu ứng thật trong worktree cộng file `-o` có khuôn.
- **C3 — `CODEX_HOME` riêng nhân bản credential.** Để home riêng dùng được, phải sao cả
  `config.toml` (đang chứa `Authorization: Bearer …` dạng chữ thường) và `auth.json`. Mỗi
  task một home nghĩa là **N bản sao khoá sống nằm trong thư mục tạm**. Bản dò đã xoá ngay
  sau khi đo. Spec phải chốt cách khác: chỉ sao `auth.json`, hoặc symlink, hoặc dựng
  `config.toml` tối thiểu bằng `-c` chứ không sao nguyên file; cộng `chmod 700` và xoá bắt
  buộc ở bước `sweep`.

### Ba đường phòng thủ, xếp theo độ tin cậy

Gộp đo được và research, hàng rào của mode mới **không** nên dựa vào một lớp:

| Lớp | Cơ chế | Độ tin cậy | Chặn được gì |
|---|---|---|---|
| 1 | sandbox `workspace-write` + `-C <worktree>` | **cao** — tầng OS, đã đo `operation not permitted` | ghi ra ngoài worktree |
| 2 | hậu kiểm `git diff --name-only` so `VÙNG FILE` | **cao** — chạy bởi Claude, không phụ thuộc Codex | sửa file ngoài vùng, trong worktree |
| 3 | hook `.codex/hooks.json` matcher `Bash` | **trung bình** — deny đã đo là chặn thật (Đ5), nhưng cần `--dangerously-bypass-hook-trust` mỗi lần và độ phủ `apply_patch` còn ngờ | chặn sớm ngay lúc ghi, kèm lý do `[TDQ:*]` |

Lớp 1 và 2 đủ để mode chạy đúng và an toàn. Lớp 3 thêm được cái lớp 2 không có: chặn **ngay
lúc ghi** kèm lý do, thay vì phát hiện sau khi Codex đã làm xong cả task. Cái giá của lớp 3 là
phải nối `.codex/hooks.json` ở gốc repo và truyền một cờ tên `--dangerously-…` mỗi lần gọi.
Đây là chỗ phải để người dùng quyết.

### Đo hiệu năng cho mặt 1c (số thật, không phỏng đoán)

Người dùng chọn mặt HIỆU NĂNG nên phải có số kiểm được. Bốn lượt dò trong repo nháp:

| Lượt | Việc | Thời gian tường |
|---|---|---|
| 1–3 | không làm gì, chỉ trả một chữ `READY` | **5,7s · 4,2s · 5,2s** |
| 4 | task thật: tạo `calc.py` + `test_calc.py`, chạy `pytest` | **105,8s** |

Hai điều rút ra:

- **Chi phí khởi động cố định ≈ 5 giây mỗi lần gọi `codex exec`.** Rẻ. Nghĩa là phép kiểm sống
  "codex say hi" ở chặng 2 của yêu cầu câu 6 tốn khoảng 5 giây — chấp nhận được, nhưng vẫn nên
  nhớ kết quả trong phiên để không trả giá đó ở mọi lần hỏi.
- **Codex có thể NHANH HƠN leader trên cùng một task.** Hằng số đã đo của repo là
  `t_task = 122,16s` (`docs/tdq/bench/2026-08-17-2001-smoke-test-main-vs-doi-thuc-do.json`).
  Lượt 4 làm việc tương đương trong 105,8s → tỉ lệ **≈ 0,87x**, trong khi hệ số mặc định cho
  sub-agent Claude là **1,5x** (tức chậm hơn leader một nửa). Nếu con số này đứng được sau khi
  đo đủ mẫu, mode mới **nhanh hơn cả hai mode cũ**, và đó là lý do thật để mode tồn tại — chứ
  không phải chỉ để tiết kiệm context.

**Cảnh báo về chính con số này**: `tdq_bench.py` đòi `so_mau >= 3` cho mỗi hằng số và từ chối
mô phỏng nếu thiếu — đúng luật, vì 0,87x hiện chỉ có **1 mẫu**. Nên spec phải ghi: hệ số Codex
là thứ **phải đo bằng `tdq_bench.py calibrate`** trong phase implement, không được viết cứng
0,87 vào code dựa trên một lần chạy. Và mẫu đo phải cùng loại việc với `t_task`, không phải
lượt trả `READY`.

Kiểm chứng lượt 4 không tin lời Codex: tôi tự grep log thấy `1 passed in 0.01s` và file
`calc.py` có đúng `def add(a, b): return a + b`. Đúng cách lớp 2 sẽ làm trong sản phẩm.

### Sáu luồng tính năng request này được ghép từ

1. **Luồng cài đặt** — dò `codex` trên máy, hỏi người dùng có cài tầng Codex không, ghi lại
   lựa chọn đó; chỉ cài khi cả hai đều thuận.
2. **Luồng cổng mode** — trước khi in lựa chọn, chạy phép kiểm sống "codex say hi"; sống thì
   hiện 3 lựa chọn, chết thì hiện 2 kèm đúng một dòng lý do theo bảng 4 nguyên nhân.
3. **Luồng thực thi** — leader chia task y hệt mode `subagent`, sub-agent Claude mở worktree
   rồi gọi `codex exec` (có `< /dev/null`, có timeout, có `CODEX_HOME` riêng, có `-m` ghim
   model), nhận kết quả qua `--output-schema` + `-o`.
4. **Luồng hàng rào** — lớp 1 sandbox giới hạn ở worktree, lớp 2 hậu kiểm `git diff --name-only`
   so `VÙNG FILE`, lớp 3 hook `.codex/hooks.json` chặn ngay lúc ghi.
5. **Luồng bảo trì** — đổi ba chỗ rẽ nhánh cứng (`phase_row`, `canh_bao_lach_luat`, phép đảo
   nhị phân ở `prompt_context`) sang bảng tra `mode → hành vi`, để mode thứ tư không phải sửa
   13 chỗ.
6. **Luồng đo** — dạy `tdq_bench.py simulate` hệ số riêng cho Codex cộng chi phí khởi động cố
   định, và một ngưỡng "task nhỏ hơn X thì mode này lỗ".

### Lộ trình

| Bước/phase | CÓ-BỎ | Vì sao |
|---|---|---|
| analyze (đang chạy) | CÓ | đang ở đây; đã xong tồn kho, đọc code, research, phỏng vấn |
| research thêm một vòng | BỎ | 4 góc research cộng 6 phép đo trên máy đã trả lời hết; chỗ ngờ duy nhất còn lại (độ phủ `apply_patch`) đã có lớp 2 bù, không cần tìm thêm |
| spec | CÓ | khung bất biến; và request có 6 luồng cùng 3 mặt chất lượng, không thể nhảy sang plan |
| review spec bằng `tdq-reviewer` | CÓ | request sửa 13 điểm neo và ba hàng rào an toàn; một mắt thứ hai đọc spec rẻ hơn nhiều so với phát hiện thiếu lúc implement |
| plan | CÓ | khung bất biến; turn khác với spec theo luật |
| review plan bằng `tdq-reviewer` | CÓ | plan phải chia được vùng file cho 13 điểm neo mà không tạo file nóng; đây đúng là thứ `assign` sẽ in `HOT FILE` nếu chia sai |
| mode | CÓ | nhưng **chỉ chọn được `main` hoặc `subagent`** — mode thứ ba là sản phẩm của request này, chưa tồn tại lúc làm nó |
| implement | CÓ | khung bất biến |
| đo thời gian thật bằng `tdq_bench.py thuc-do` | CÓ | mặt HIỆU NĂNG người dùng đã chọn (1c) đòi con số kiểm được, không phải phỏng đoán; đã có 3 mẫu chi phí khởi động 4,2/5,2/5,7 giây làm nền |
| dựng lại bundle bằng `build_portable.py` | CÓ | `portable_claude/` và `portable_codex/` là đồ SINH; mode mới không có trong bundle thì máy mới không dùng được, mà chặng 1 của yêu cầu câu 6 nói đúng về máy mới |
| QC độc lập bằng `tdq-qc-tester` | CÓ | request này tự sửa hàng rào chống lách luật của chính nó; tự kiểm là xung đột lợi ích, phải có người ngoài chạy lại |
| report | CÓ | khung bất biến |
| chia việc cho nhiều sub-agent | HOÃN | quyết ở cổng mode sau khi có plan, bằng `tdq_bench.py simulate` chứ không bằng cảm giác |

### Trả lời 3 câu cổng

1. **Phạm vi cuối đã rõ chưa?** Rõ. Xây: 1 agent mới, 1 mode mới đứng cạnh `subagent`, cổng
   năng lực hai chặng, hàng rào 3 lớp, bảng tra thay 3 chỗ rẽ cứng, hệ số Codex cho `simulate`.
   Đầu ra là file trong `scripts/`, `hooks/`, `agents/`, `skills/`, `tests/`, cộng bundle sinh
   lại. KHÔNG làm: đổi cách chia task (người dùng chốt phải y hệt), đổi mode `main`/`subagent`,
   sửa `~/.codex/config.toml` của người dùng.
2. **Có cần model / tải / cài gì không?** Không cần tải gì cho việc phát triển: `codex` 0.154.0
   đã có trên máy, LSP 7/7 đạt. Nhưng sản phẩm **có** một bước cài cho máy khác, và đó chính
   là chặng 1 của yêu cầu câu 6 — phải hỏi người dùng, cấm tự cài.
3. **Phạm vi QC/test/validate đã định chưa?** Định rồi: mỗi task một unit test đi red → green;
   17 file test đang nhắc `subagent` phải còn xanh; `tests/test_agent_frontmatter.py` khoá 4
   điều với agent mới; cộng ba phép kiểm hiệu ứng thật không tin exit code — sandbox chặn ghi
   ngoài worktree, hook deny chặn được file, và `codex exec` không treo khi stdin không phải
   TTY. QC do `tdq-qc-tester` chạy lại, không phải tôi tự nhận.

## Hỏi đáp

### Vòng 1 (2026-09-10 23:12) — vòng scope + 4 câu cốt lõi

Vòng scope CHẠY, theo dấu hiệu 1 và 2 của `scope-round.md`: request nêu cả một cách chạy mới
(mode + agent), và quét 9 mặt ISO 25010 thấy ít nhất 4 mặt có thể áp mà câu người dùng không
nói gì (bảo mật, tin cậy, bảo trì, hiệu năng).

1. Request này bạn muốn bao quanh những mặt nào? (chọn nhiều được)
- A (đề xuất): BẢO MẬT + TIN CẬY — spec sẽ có hàng rào 3 lớp, hook Codex ở gốc repo, luật cách ly `CODEX_HOME` và cách xử khoá sống, cộng luật timeout/`< /dev/null`
- B: BẢO TRÌ — spec sẽ có mục đổi `phase_row` và `canh_bao_lach_luat` sang bảng tra `mode → hành vi`, để mode thứ tư sau này không phải sửa 13 chỗ
- C: HIỆU NĂNG — spec sẽ có mục dạy `tdq_bench.py simulate` hệ số riêng cho Codex và ngưỡng "task nhỏ hơn X thì đừng dùng mode này"
- D: chỉ cần chạy được — bỏ hết các mặt trên, spec chỉ lo đúng luồng chính: giao task, Codex làm, Claude kiểm, gộp

2. Tối đa bao nhiêu tiến trình Codex chạy cùng lúc trong một đợt?
- A (đề xuất): 2–3 — vừa đủ nhanh, mỗi tiến trình một `CODEX_HOME` riêng, tránh khoá SQLite mà research ghi nhận ở issue #20213
- B: 1 (tuần tự) — an toàn nhất, không cần cách ly `CODEX_HOME`, nhưng mất hẳn lợi thế song song của mode
- C: 4–6 — nhanh nhất, nhưng phải chịu rủi ro tranh khoá và tôi phải viết thêm cơ chế thử lại
- D: tôi tự ghi số

3. Mode mới đứng cạnh mode `subagent` hay thay nó?
- A (đề xuất): đứng cạnh — cổng chọn mode thành 3 lựa chọn, bạn chọn từng request; giữ được đường lùi khi Codex hỏng
- B: thay hẳn — cổng vẫn 2 lựa chọn, "giao trợ lý" từ nay là Codex; gọn hơn nhưng mất đường lùi
- C: đứng cạnh và trở thành mặc định khi có `codex` trên máy — tôi tự đề xuất mode này, bạn vẫn đổi được

4. "Claude check nhanh lại" đi tới mức nào sau mỗi task Codex trả về?
- A (đề xuất): chạy lại test + so `git diff --name-only` với `VÙNG FILE` — máy kiểm, không cần Claude đọc; lệch một file là task FAIL
- B: như A, cộng Claude đọc nguyên diff trước khi gộp — chắc nhất, nhưng tốn context đúng bằng thứ mode này định tiết kiệm
- C: như A, cộng Claude đọc diff CHỈ khi test đỏ hoặc có file lệch vùng — kiểm sâu đúng lúc cần
- D: chỉ chạy lại test — nhanh nhất, nhưng mất hẳn hàng rào vùng file (lớp 2)

5. Codex trên máy này đang chạy `ag/gemini-3.8-flash-medium` qua router nội bộ `9router`, không
   phải model của Codex. Bạn muốn mode mới xử thế nào?
- A (đề xuất): mode tự ghim model qua `-m` và ghi tên model vào log mỗi task — bạn biết chắc ai làm task, không phụ thuộc cấu hình máy
- B: dùng đúng cấu hình `~/.codex` hiện có, chỉ ghi tên model vào log — không can thiệp máy bạn
- C: mode từ chối chạy nếu model không phải model của Codex — chặt nhất, nhưng mode sẽ không chạy được trên máy này lúc này

6. Bạn muốn bổ sung thêm gì không?
- A (đề xuất): Không, đủ rồi — làm tiếp đi.
- B: Có — tôi nói thêm.

**Trả lời (nguyên văn, 2026-09-10 23:20):** `1abc 2a 3a 4a 5a 6 lúc install vào máy mới sẽ hỏi
người dùng có muốn install ko, đồng thời check xem có codex không phải thoải người dùng có codex
và muốn install thì mới okay và khi gọi codex implement cũng sẽ gọi check codex say hi xem có trả
về ko nếu có thì lúc chọn mode mới show codex implement còn ko thì ko cho chọn codex implement và
giải thích nhanh issue tại sao codex implement ko cho chọn`

Chốt lại thành 6 quyết định:

| Câu | Chọn | Nghĩa với spec |
|---|---|---|
| 1 | A + B + C (cả ba mặt, chỉ bỏ D) | spec phải có đủ: hàng rào 3 lớp và luật cách ly; bảng tra `mode → hành vi` thay các `if` cứng; hệ số Codex cho `tdq_bench.py simulate` kèm ngưỡng task |
| 2 | A — 2–3 tiến trình Codex song song | mỗi tiến trình một `CODEX_HOME` riêng, kèm luật xoá ở `sweep` |
| 3 | A — đứng cạnh `subagent` | cổng chọn mode thành 3 lựa chọn, `VALID_MODES` thành 3 phần tử, giữ đường lùi |
| 4 | A — chạy lại test + so `git diff --name-only` với `VÙNG FILE` | máy kiểm, Claude không đọc diff ở đường thường; lệch một file là task FAIL |
| 5 | A — mode tự ghim model qua `-m`, ghi tên model vào log mỗi task | không phụ thuộc `~/.codex` của máy; log nói rõ ai làm task |
| 6 | Yêu cầu MỚI — cổng năng lực hai chặng (xem ngay dưới) | mode phải tự ẩn khi máy không có Codex |

### Yêu cầu mới ở câu 6 — cổng năng lực hai chặng

Người dùng thêm một điều không có trong câu hỏi, và nó đổi hình dáng sản phẩm: **không phải
ai cũng có Codex**, nên mode mới không được là thứ luôn hiện ra.

**Chặng 1 — lúc install vào máy mới.** Phải hỏi người dùng có muốn cài tầng Codex hay không,
và song song đó tự dò xem máy có `codex` chưa. Chỉ khi **cả hai** đúng — máy có `codex` VÀ
người dùng đồng ý — thì mới cài. Khớp đúng luật đã có ở bậc 1b: `tdq_lsp.py` in ra lệnh cài
rồi **chờ người dùng cho phép**, tuyệt đối không tự cài (`tdq_lsp.py` khai rõ điều này, và
`Bac(...)` mang sẵn ô lệnh-sửa cho việc đó).

**Chặng 2 — lúc tới cổng chọn mode.** Trước khi in danh sách lựa chọn, phải gọi một phép
kiểm sống kiểu *"codex say hi"* xem Codex có trả lời không:

- Trả lời được → cổng chọn mode hiện **3 lựa chọn**, có `codex implement`.
- Không trả lời được → cổng chỉ hiện **2 lựa chọn** như hôm nay, và phải **nói ngay lý do
  vì sao `codex implement` không chọn được**, một dòng, đúng nguyên nhân đã dò ra.

Đây là điểm khác biệt về bản chất so với hai mode cũ: `main` và `subagent` **luôn** dùng
được, còn mode thứ ba **phụ thuộc môi trường**. Nên nó không thể chỉ là một phần tử thêm vào
`VALID_MODES`; nó cần một khái niệm mới: **mode khả dụng tại thời điểm hỏi**.

Bốn nguyên nhân "không chọn được" phải phân biệt được, vì cách sửa khác nhau hoàn toàn:

| Nguyên nhân | Dò bằng gì | Câu giải thích cho người dùng nói gì |
|---|---|---|
| chưa cài `codex` | `shutil.which("codex")` trả None | cài Codex CLI rồi chọn lại |
| có `codex` nhưng chưa đăng nhập / router chết | phép kiểm sống trả mã lỗi | đăng nhập lại hoặc bật router |
| có `codex`, chạy được nhưng quá hạn | phép kiểm sống hết timeout | mạng hoặc model chậm, thử lại |
| người dùng đã từ chối cài tầng Codex ở chặng 1 | cờ ghi lại lúc setup | bạn đã tắt tầng này, mở lại bằng lệnh setup |

Khuôn code để dùng lại, không viết mới: `scripts/setup_status.py:132` `_run_tool()` đã làm
đúng việc này — `shutil.which` trước, `subprocess.run(..., encoding="utf-8")` có timeout, trả
**dữ liệu** (`co` / `chay_duoc` / `ma` / `chi_tiet` / `goi_y`) chứ không raise, và mọi luồng
đi qua `mask_secrets` trước khi ra ngoài. Ba tính chất ấy đúng hết ba thứ mode này cần: máy
thiếu công cụ là trạng thái bình thường chứ không phải sự cố; có ô `goi_y` để in lệnh cài; và
có che khoá — cần thiết vì `~/.codex/config.toml` đang giữ khoá sống.

### Vòng 2 (2026-09-11 00:02) — người dùng đổi kiến trúc sau khi đọc spec 1.0

Nguyên văn: *"vậy thì đổi lại là codex implement sẽ ko đưa cho subagent và main a gent sẽ gọi
lệnh cho codex implent như main implement nhưng thay vì claude code làm sẽ gọi codex làm thôi."*

Đây là góp ý spec, không phải duyệt. Nó bỏ tầng giữa của kiến trúc ba tầng ở tin nhắn thứ hai:
không còn sub-agent Claude, không còn worktree song song. Leader chạy tuần tự trong turn của
mình, mỗi task một lượt `codex exec`.

**Cái mất theo:** tầng sub-agent, worktree song song, giới hạn 2–3 tiến trình, một `CODEX_HOME`
cho mỗi tiến trình (còn đúng một), toàn bộ phần dính `scripts/tdq_team.py` ngoài một dòng khai,
và **lý do "nhanh hơn"** — vì song song là thứ duy nhất mang lại tốc độ. Đo được: một task thật
Codex mất 105,8s so với `t_task = 122,16s` của leader, nên chạy tuần tự là xấp xỉ ngang `main`.
Giá trị còn lại của mode là đổi người viết code, không phải rút ngắn thời gian; điều này đã nói
thẳng với người dùng trước khi họ trả lời vòng 2.

**Cái mất kèm mà phải bù:** lớp sandbox hẹp. Bản 1.0 có `-C <worktree>` nên Codex chỉ ghi được
trong worktree của task; bản 1.1 chạy trong repo nên `-C <gốc repo>`, Codex ghi được khắp repo
(vẫn không ra ngoài repo — đã đo). Bán kính này đúng bằng bán kính `main implement` hôm nay.

Hai câu hỏi vòng 2 và câu trả lời `1a 2a`:

| Câu | Chọn | Nghĩa cho spec |
|---|---|---|
| 1 | A — bỏ file trong `agents/`, hợp đồng vai của Codex thành file luật `skills/tdq-build/references/codex-mode.md` | không tạo file chết trong `agents/`; nhưng prompt mẫu cố định, khuôn kết quả Codex phải trả, và ngưỡng digest vẫn phải có, chỉ là nằm ở tầng luật; kéo theo bỏ dòng trong `subagent-tuning.md` và bỏ ràng buộc của bộ kiểm frontmatter agent |
| 2 | A — mốc hoàn tác git trước mỗi task, hậu kiểm vùng file sau mỗi task | mốc là sha `git stash create` cộng danh sách file chưa theo dõi; file lệch vùng thì trả về nội dung mốc, file mới thì xoá; không mở worktree tạm |

Chốt lại ba lớp phòng thủ của bản 1.1: sandbox chặn ghi **ra ngoài repo** (tầng hệ điều hành, đã
đo) · hậu kiểm `git diff --name-only` so `VÙNG FILE` cộng mốc hoàn tác (chạy bằng git, không thể
tắt) · hook `PreToolUse` chặn ngay lúc ghi (chặn sớm kèm lý do, cần cờ
`--dangerously-bypass-hook-trust` mới bắn).
