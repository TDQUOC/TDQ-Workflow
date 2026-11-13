# TDQ-Workflow trên Antigravity — Báo Cáo Kiểm Toán Thực Nghiệm Toàn Diện & Kế Hoạch Chuyển Đổi (v2.0 — Sau Đợt Deep Rescan 100%)

- **Ngày kiểm toán & quét vét cạn (Pass 1 + Pass 2 Deep Rescan):** `2026-11-13`
- **Kho mã nguồn gốc đối chiếu:** `C:\Users\admin\Documents\Projects\ForAgentCode\TDQ-Workflow`
  - **Nhánh phát triển (`dev` @ `b423ee06`):** Phiên bản **`v0.97.0`** (`6.230` file tracked; đang vượt `origin/dev` **48 commit**; chứa toàn bộ nâng cấp `v0.96.0` & `v0.97.0` + 1 brief đang mở ở working tree `2026-11-11-1435-chan-tu-sua-khi-feedback.md`).
  - **Nhánh phát hành runtime (`main` @ `6f03655c`, tag `v0.95.0`):** Phiên bản **`v0.95.0`** (`175` file runtime sạch được sinh bằng Git plumbing `build_portable.py --sinh-main --nguon dev --nhanh-dich main`; không tồn tại nhánh tên `release/*` hay `skills/tdq-release/`).
- **Bản plugin đang cài trên máy:** `C:\Users\admin\.gemini\config\plugins\tdq-workflow` — Phiên bản **`v0.74.0`** (tụt **23 phiên bản** do chưa có cơ chế auto-sync; `agy plugin validate` báo **1 error đỏ, 2 warnings, 1 note**).
- **10 Hồ sơ bằng chứng chuyên sâu trong workspace (`docs/research/`):**
  - *Đợt 1 (Audit nền tảng & chạy thử E2E):*
    1. [01-soul-and-rules-audit.md](./research/01-soul-and-rules-audit.md) — Giải phẫu Soul, 15 luật `R1–R15`, quy ước ngôn ngữ/ký hiệu & chuẩn Rules của Antigravity.
    2. [02-pipeline-skills-agents-audit.md](./research/02-pipeline-skills-agents-audit.md) — Giải phẫu State Machine `v6`, 11+1 Skills & 6 Subagents.
    3. [03-hooks-and-gates-simulation.md](./research/03-hooks-and-gates-simulation.md) — Audit 20 tệp Hooks (23 mã `TDQ:*`) & giả lập `cmd /c` với payload `protojson`.
    4. [04-antigravity-adapter-audit.md](./research/04-antigravity-adapter-audit.md) — Kiểm toán `build_portable.py --sinh-agy` & cấu hình thực tế trên máy.
    5. [05-cli-e2e-and-extensions-audit.md](./research/05-cli-e2e-and-extensions-audit.md) — Kiểm toán CLI scripts, `pytest` (151 tests) & chạy E2E thực tế trên kho Git nháp.
  - *Đợt 2 (Deep Rescan vét cạn 100% nhánh Release, 67 Scripts, 74 tệp Skills, Edge-case Hooks & `agy plugin validate`):*
    6. [06-rescan-release-branch-and-git.md](./research/06-rescan-release-branch-and-git.md) — Kiểm toán nhánh `main` (`v0.95.0`) vs `dev` (`v0.97.0`), worktrees, stashes, `claude-export/` & 12 khoảng trống phát hành.
    7. [07-rescan-all-67-scripts-and-tools.md](./research/07-rescan-all-67-scripts-and-tools.md) — Rà từng dòng 67 file `.py` trong `scripts/`, `portable_src/`, `tools_kiem/`, `evals/` (phát hiện 28 lỗi `NEW-01` → `NEW-28`).
    8. [08-rescan-skills-templates-and-tool-mapping.md](./research/08-rescan-skills-templates-and-tool-mapping.md) — Đệ quy 74 file `skills/**`, `agents/`, `.opencode/`, `.codex/` & bảng định lượng 20 nhóm mismatch `M01` → `M20`.
    9. [09-rescan-hooks-subagents-and-windows-io.md](./research/09-rescan-hooks-subagents-and-windows-io.md) — Kiểm thử thực nghiệm 14 ca góc hiểm (`EC-01` → `EC-14`) trên Subagent Worktree, Brain Artifacts, NTFS Race & Windows `cp1252`.
    10. [10-rescan-agy-host-spec-and-validator.md](./research/10-rescan-agy-host-spec-and-validator.md) — Đối chiếu 8 plugin cài sẵn & kiểm chứng trực tiếp bằng trình biên dịch chính chủ `agy.exe plugin validate --strict --json`.

---

## Mục Lục

1. [Tóm Tắt Điều Hành & Kết Luận Tổng Quát](#1-tóm-tắt-điều-hành--kết-luận-tổng-quát)
2. [Kiến Trúc Nhánh Phát Hành (`dev` vs `main`) & Các Thay Đổi Mới Ở `v0.96.0–v0.97.0`](#2-kiến-trúc-nhánh-phát-hành-dev-vs-main--các-thay-đổi-mới-ở-v0960v0970)
3. [Kiến Trúc Nguyên Bản Của TDQ-Workflow (Soul, Rules, Pipeline, Gates)](#3-kiến-trúc-nguyên-bản-của-tdq-workflow-soul-rules-pipeline-gates)
4. [Tổng Hợp Toàn Bộ Điểm Gãy & Lỗ Hổng Thực Nghiệm Trên Antigravity + Windows](#4-tổng-hợp-toàn-bộ-điểm-gãy--lỗ-hổng-thực-nghiệm-trên-antigravity--windows)
5. [Kiểm Chứng Thực Nghiệm 7 Extension & Companion Engine](#5-kiểm-chứng-thực-nghiệm-7-extension--companion-engine)
6. [Đặc Tả Kỹ Thuật Chi Tiết 7 Nhóm Việc Cần Sửa (Zero-Blind-Spot Porting Blueprint)](#6-đặc-tả-kỹ-thuật-chi-tiết-7-nhóm-việc-cần-sửa-zero-blind-spot-porting-blueprint)

---

## 1. Tóm Tắt Điều Hành & Kết Luận Tổng Quát

> [!CAUTION]
> **KẾT LUẬN SAU 2 ĐỢT QUÉT VÉT CẠN: Bản xuất `TDQ-Workflow` hiện tại CHƯA THỂ HOẠT ĐỘNG ĐẦY ĐỦ trên Antigravity, và đợt Deep Rescan lần 2 đã bắt được thêm hàng loạt bẫy P0 chí mạng mà nếu chỉ sửa bề mặt sẽ gây Deadlock hoặc mất trạng thái ngay khi chạy thật.**
> - **Nền tảng gốc cần lấy làm chuẩn (Baseline):** Bắt buộc lấy **`dev @ b423ee06` (`v0.97.0`)**, **KHÔNG** lấy `main @ 6f03655c` (`v0.95.0`, đang tụt 48 commit và thiếu toàn bộ cơ chế `v0.96.0–v0.97.0`).
> - **Công cụ kiểm chứng chính chủ có sẵn trên máy:** Lệnh `agy plugin validate <dir> --strict --json` kiểm tra trực tiếp mọi quy tắc Go struct/YAML/trần `24.000 bytes` của Antigravity. Mọi bản build của chúng ta phải đạt **`ExitCode = 0, errors = 0, warnings = 0`**.
> - **Khả năng tương thích đích:** Antigravity 2.0 hỗ trợ đầy đủ mọi thành phần gốc (`SessionStart`, `PreInvocation`, `PreToolUse`, `PostToolUse`, `PostInvocation`, `Stop`, `rules/AGENTS.md` + `rules/*.md` có `trigger: glob | model_decision`, `agents/*.md`, `skills/`, `mcp_config.json`, `invoke_subagent`) để chạy **100% Full Native TDQ-Workflow**.

### Bảng Chẩn Đoán Tổng Thể Theo 9 Phân Hệ

| Phân hệ | Quy mô gốc (`dev` `v0.97.0`) | Hiện trạng trên Antigravity & Các Bẫy P0/P1 Đã Chứng Minh Thực Nghiệm | Đánh giá |
| :--- | :--- | :--- | :--- |
| **1. Nhánh Release & Đồng bộ Host** | `dev` (`v0.97.0`) vs `main` (`v0.95.0`, Git plumbing) | `--sinh-main`, `tdq_setup.py`, `session_start.py` chỉ đồng bộ Claude (`~/.claude`) & Codex (`~/.codex`), bỏ rơi hoàn toàn Antigravity ở `v0.74.0`; `doc_phien_ban_plugin()` trả `None` trên `plugin.json` gốc | **Đứt gãy đồng bộ** |
| **2. Trình xuất `--sinh-agy` (Windows)** | Copy & thay `${CLAUDE_PLUGIN_ROOT}` | Thay `C:\Users\...` vào `.py` gây nổ `SyntaxError: unicodeescape \U` (`tdq_setup.py`, `tdq_checkportable.py`); regex `\b(scripts/\|hooks/)` làm hỏng tên file ví dụ trong prose; `RELEASE_EXCLUDE_SCRIPTS` vô tình loại mất `tdq_knowledge.py` | **Hỏng P0** |
| **3. Soul & Luật (`rules/`)** | `soul.md` + `TDQ:TOOLS` + 12 file luật ngôn ngữ | `0 bytes` trong `plugins/tdq-workflow/rules/`; Antigravity hỗ trợ **đồng thời** `rules/AGENTS.md` (`always_on`) VÀ `rules/*.md` (`trigger: glob \| model_decision`) dưới trần `24.000 B/file` | **0% tự nạp** |
| **4. Lifecycle Hooks & Gates** | 20 file trong `hooks/` (23 mã `TDQ:*`) | `hooks.json` lỗi đỏ Go unmarshal; sai khóa camelCase & `cwd=plugin_dir`; **Subagent bắn `PreInvocation` + `Stop` trên cùng workspace gây xóa `.tdq-turn.jsonl` của cha và deadlock vô hạn ở `Stop`**; ghi artifact vào `<appDataDir>/brain/` làm `stop_gate.py` khóa cứng; 56 tool LSP lazy đi qua `call_mcp_tool` lọt lưới matcher | **0 / 17 chạy đúng** |
| **5. Hệ thống Skills & Shell** | 74 file trong `skills/` + 1 file `portable_src/` | Rớt 2 skill `tdq-browser-*`; 128 lệnh `python3` (lỗi `rc=9009` dưới `CreateProcessW`); 12 dòng nối lệnh `\` + `&&` + `TDQ_PROJECT_DIR=/tmp/...` gãy trên PowerShell 5.1; chưa cấm `ask_question`; `tdq-checkportable` gọi cờ đã xóa `--trust` (`rc=2`) | **~50%** |
| **6. Đội ngũ Subagents (`agents/`)** | 6 file `agents/tdq-*.md` | Rớt `6/6`; **`model: haiku` (mới ở `v0.97.0`) và `tools: Bash, Read...` dạng chuỗi đều bị `agy plugin validate` báo ERROR đỏ và loại bỏ agent**; các tool `grep_search`, `find_by_name`, `list_dir` **không tồn tại** trên Antigravity 2.0; thiếu `send_message` | **0 / 6 nạp được** |
| **7. Extensions & MCP Servers** | `lsp`, `chrome-devtools`, `tavily`, `archify`, `graphify`, `vision`, `codex` | CLI sống 100%; MCP hỏng sạch + **bẫy mới:** khai báo mảng `"variables"` trong `mcp_config.json` sẽ **tự động TẮT toàn bộ plugin `tdq-workflow`** cho đến khi người dùng điền tay trên UI! | **CLI 100% · MCP 0%** |
| **8. Core CLI (`scripts/*.py`)** | 67 file `.py` + `tools_kiem/` + `evals/` | Phát hiện thêm **8 bug P0 trên Windows**: `tdq_finish.py` `.strip()` cắt mất chữ đầu tiên của file (`docs/...` → `ocs/...`, bỏ qua `doc_lint`!); `lsp_module.py` ống `IBM437` giết nhầm `agent-lsp` đang sống bằng `taskkill /F`; `search_rules.py` chặn oan mọi lệnh PowerShell có `"C:\path\"` hoặc `` `n `` và trượt split `L887` cho `mcp_`; `tdq_state.load()` gặp UTF-8 BOM liền đổi tên `state.json` sang `.corrupt-*` xóa trắng trạng thái! | **Cần vá 8 P0 + 11 P1** |
| **9. Concurrency & Transcript** | Sổ cái `.tdq-*.jsonl` & `tdq_transcript.py` | 8 tiến trình song song ghi `.tdq-turn.jsonl` trên NTFS mất **29.1% dòng**; `PreInvocation` chạy ở mọi bước model (15 lần/lượt, tốn 2.5s+ nếu không fast-path); `transcript.jsonl` của Antigravity mã hóa JSON **2 lớp** trong `tool_calls[].args` | **Mù Transcript & Race** |

---

## 2. Kiến Trúc Nhánh Phát Hành (`dev` vs `main`) & Các Thay Đổi Mới Ở `v0.96.0–v0.97.0`

Kết quả kiểm toán Git (`git ls-remote`, `git log`, `git diff main..dev`, worktrees, stashes — chi tiết tại [06-rescan-release-branch-and-git.md](./research/06-rescan-release-branch-and-git.md)):

1. **Cơ chế nhánh Release thật sự (`dev` → `main`):**
   - Kho gốc **không có** nhánh tên `release/*`, **không có** `skills/tdq-release/`, và `.github/workflows/test.yml` không có bước CI release.
   - Nhánh **`main` (`6f03655c`, tag `v0.95.0`, 175 files)** chính là nhánh phát hành runtime sạch, được tổng hợp từ `dev` mà không cần `git checkout` thông qua Git plumbing (`git ls-tree` → `GIT_INDEX_FILE` tạm → `git write-tree` → `git commit-tree` → `git update-ref refs/heads/main`) bên trong `scripts/build_portable.py --sinh-main --nguon dev --nhanh-dich main` (dòng `595–736`).
   - Toàn bộ các nhánh phụ (`bugfix/*`, `feature/*`, `tdq/*`, `local-sync`) và 2 worktree đang mở (`.claude/worktrees/agent-a37e138360abceb26` & `agent-a45a16c73f42c0ad5`) đã được xác minh **100% đã gộp (hoặc trùng khớp từng byte bản vá)** vào `dev`. 6 stash đều là bản sao lưu Archify cũ từ `v0.80–v0.84`.
2. **Chênh lệch 48 commit giữa `main` (`v0.95.0`) và `dev` (`v0.97.0`):**
   - **`v0.96.0` (chỉ có trên `dev`):**
     - `tdq_state.py`: Bổ sung `_archify_gate()` và `_chan_report_thieu()` (`ARCHIFY_MOC = "2026-11-09-0143"`), bắt buộc có `.manifest.json` đạt trạng thái `"current"` trước khi `approve spec` / `approve quick` và trước khi đóng `phase=idle`.
     - `hooks/scripts/read_gate.py`: Bổ sung thuật toán chống đọc lặp theo tỷ lệ giao thoa dòng `>= 70%` (`_tinh_overlap_ratio`).
     - `soul.md`: Bổ sung Bất biến Clean Code #4 (*Tư duy Phản tỉnh & Giả thuyết + 5 Whys*).
   - **`v0.97.0` (chỉ có trên `dev`):**
     - `scripts/doc_lint.py`: Bổ sung luật **`rule_r15`** bắt buộc mọi Task Block trong Plan có chạm mã nguồn phải có mục đặc tả kỹ thuật / thuật toán / logic *(tuy nhiên quên đặt mốc ngày slug, làm gãy 6/6 bộ test seed trong `evals/tuan-thu/`!)*.
     - `plan-template.md` & `plan-template-huong-dan.md`: Chuẩn hóa **Self-Contained Task Block** và **4 Khóa An Toàn Cơ Học** *(trong đó Khóa #2 ghi cứng tên tool Claude: `Dùng Edit. CẤM dùng Write trên file có sẵn`)*.
     - `agents/tdq-implementer.md` & `team-mode.md`: Đổi sang **`model: haiku` / `effort: medium`** và thêm bảng **Dynamic Model Tier Routing** (`haiku` / `sonnet` / `opus`) — gây lỗi đỏ trực tiếp trên bộ nạp agent của Antigravity!
3. **Yêu cầu đang mở dở trong Working Tree của `dev` (`2026-11-11-1435-chan-tu-sua-khi-feedback.md`):**
   - Phát hiện lỗ hổng thật trong `edit_gate.py:115, 137` + `tdq_state.py:2942`: khi đóng yêu cầu về `phase="report"` hoặc `"idle"`, các cờ `spec_approved` / `plan_approved` / `quick_approved` cũ **không được xóa**, nên khi người dùng phản hồi có bug sau đó, `cong_dang_cho(state)` trả `None` và cho phép AI tự ý sửa thẳng code nguồn không cần phân tích hay xin phép (`[TDQ:FEEDBACK]` + Bất biến #5 *"Triage Before Touch"*).

---

## 3. Kiến Trúc Nguyên Bản Của TDQ-Workflow (Soul, Rules, Pipeline, Gates)

- **Hiến pháp `Soul` (`soul.md`):** Thứ bậc bất khả xâm phạm **`chất lượng > runtime > context cost`**; giọng điệu **`đơn giản, dễ hiểu, ngắn gọn · trực quan, đầy đủ thông tin`**; viết luật cho model yếu nhất có đủ `When it applies` / `What to do` / `Self-check`; Placement Law giữ Tier 1 & Tier 2 trong `SKILL.md`; 4 bất biến Clean Code (+ Bất biến #5 *Triage Before Touch*) và thang 7 nấc `TDQ:GON` (*YAGNI trước SOLID*, bật Log Service có timestamp mặc định).
- **15 Luật Linter (`R1–R15` trong `doc_lint.py` + `token_budget.py`):** Khóa chặt cấu trúc từng bước, trần 40 từ/câu, trần dòng từng `SKILL.md`, khóa SHA-256 của 62 tệp `references/**/*.md` (`<= 3.500` tokens/tệp; cộng thêm file thứ 63 là `handoff-schema.json`), cấm thiếu dấu tiếng Việt (`R12`), bắt buộc baseline/fallback cho tiêu chí số (`R14`), và bắt buộc đặc tả thuật toán trong từng Task Block (`R15`).
- **User-Facing Block & Tìm kiếm 3 tầng:** Cấm tuyệt đối popup hỏi đáp (`AskUserQuestion` / `ask_question`), cấm emoji, chỉ dùng đúng 6 ký tự Unicode phi-ASCII (`➤`, `·`, `—`, `→`, `–`, `…`); bắt buộc đi qua **LSP** hoặc **Graphify** trước để mở cửa sổ **10 lượt tìm chuỗi**.
- **Pipeline 3 làn (`nhỏ`, `quick`, `full`) + 10 cổng chặn cứng trong `tdq_state.py` (`v6`) + cơ chế `Verify-by-Effect`** đối chiếu vân tay SHA-256 thật trên đĩa tại cổng `Stop`.

---

## 4. Tổng Hợp Toàn Bộ Điểm Gãy & Lỗ Hổng Thực Nghiệm Trên Antigravity + Windows

### 4.1. Nhóm Lỗi Đóng Gói & Cấu Hình Host (`agy plugin validate` Đã Xác Thực)
1. **`[P0]` Nổ `SyntaxError: unicodeescape` trên Windows (`build_portable.py:477-485, 583-590`):** Thay `${CLAUDE_PLUGIN_ROOT}` bằng đường dẫn Windows `C:\Users\...` thẳng vào file `.py` làm hỏng `tdq_setup.py`, `tdq_checkportable.py`, `tdq_state.py`. Ngoài ra regex `\b(scripts/|hooks/)` thay nhầm cả tên file ví dụ trong văn xuôi (`scripts/alpha.py`, `scripts/a.py`, `scripts/scan.py`), và `RELEASE_EXCLUDE_SCRIPTS` (13 file) chứa cả `tdq_knowledge.py`!
2. **`[P0]` Kết quả chạy `agy plugin validate` trên bản cài `v0.74.0`:**
   - **ERROR đỏ:** `hooks.json` có khóa chuỗi `"description"` ở top-level làm Go struct `JSONHookSpec` bỏ qua toàn bộ tệp `hooks.json` (cộng thêm `Stop` bọc sai `{"hooks": [...]}` và thiếu `"matcher"`).
   - **WARNING:** `mcp_config.json` truyền nguyên chuỗi đen `"${TAVILY_API_KEY}"` đè hỏng môi trường cho cả `tavily-primary` và `tavily-backup`.
   - **Bẫy `"variables"` mới phát hiện:** Nếu khai báo mảng `"variables"` trong `mcp_config.json`, **Antigravity tự động đặt toàn bộ plugin `tdq-workflow` về trạng thái OFF** cho tới khi người dùng nhập tay đủ mọi biến trên giao diện UI!
   - **Quy tắc nội suy `${PLUGIN_ROOT}`:** Trong `hooks.json`, `${PLUGIN_ROOT}` **KHÔNG** được nội suy trong chuỗi `command` (chỉ có trong `os.environ`; lệnh hook phải viết đường dẫn tương đối `"py -3 -X utf8 \"hooks/scripts/...\""` vì `cwd = <plugin_dir>`). Trong `mcp_config.json`, `${PLUGIN_ROOT}` chỉ được nội suy trong `args`, `env`, `cwd`, **cấm dùng trong `command`**.
3. **`[P0]` Lỗi đỏ bộ nạp `agents/*.md` & Bẫy tên Tool trên Antigravity 2.0:**
   - `model: haiku` (mới thêm ở `tdq-implementer.md` `v0.97.0`) bị `agy plugin validate` báo **ERROR đỏ**: `Invalid model tier haiku. The loader skips this agent` (chỉ nhận `inherit | flash_lite | flash | pro`).
   - `tools: Bash, Read, Grep, Glob` dạng chuỗi dấu phẩy bị báo **ERROR đỏ**: `cannot unmarshal !!str into []string. The loader skips this agent`. Bỏ trống `tools:` bị giáng xuống chỉ đọc.
   - **Điểm mù công cụ trên Antigravity 2.0 (`language_server.exe`):** Quét 835 lời gọi tool thật trên 16 `transcript.jsonl` và `<declaration:default_api:*>` chứng minh **`grep_search`, `find_by_name`, `list_dir` KHÔNG TỒN TẠI trên Antigravity 2.0** (và máy Windows này cũng **không có `rg` hay `grep`** trên `PATH` PowerShell!). Nếu không cấp `run_command` cho `tdq-reviewer` và `tdq-security-reviewer`, hai agent này sẽ mù hoàn toàn khả năng duyệt thư mục và chạy `git diff`!

### 4.2. Nhóm 8 Showstoppers P0 Trong Hooks, Subagents & Worktrees (`EC-01` → `EC-13`)
1. **`[P0 — EC-01]` Sửa Artifact của Antigravity làm khóa cứng `stop_gate.py`:** Trên Windows, `<appDataDir>\brain\<id>\*.md` nằm cùng ổ `C:` với dự án nên `os.path.relpath` thành công (`..\..\..\..\.gemini\...`), bị `edit_gate.py:96` ghi `"edit"` vào `.tdq-turn.jsonl` trước khi kiểm tra `trong_project`, khiến `stop_gate.py` chặn không cho dừng lượt với lỗi `[TDQ:LOG]` & `[TDQ:TICK]`!
2. **`[P0 — EC-02]` Lỗi sống ở repo gốc làm chết toàn bộ hàng rào phía sau trong `edit_gate.py`:** Khi chưa tạo file `docs/workinglog/YYYY-MM-DD.md` của ngày hôm đó, `remind("TDQ:LOG")` (`edit_gate.py:158` + `_common.py:207`) gọi `sys.exit(0)` ở **mọi** lần sửa file (lần 1 `"allow"`, lần 2..N thoát sớm vì `already_reminded`), biến toàn bộ dòng `170–289` (`TDQ:TEAM`, `ngoai_vung_khai`, `TDQ:TICK`) thành **dead code 100%**!
3. **`[P0 — EC-03 & EC-06]` Đụng độ vòng đời Subagent trên `PreInvocation`, `PreToolUse` & `Stop`:** Antigravity không gửi `agent_id` trong stdin và chạy đủ `PreInvocation` → `PreToolUse` → `Stop` cho mọi subagent trên cùng `workspacePaths[0]`:
   - Subagent chạy `PreInvocation` làm xóa sổ cái của cha;
   - Subagent trước phase `implement` lọt qua khóa `payload.get("agent_id")` sửa được `src/*` và `state.json`;
   - Subagent khi xong việc bị `stop_gate.py` nhốt vô hạn bằng `"decision": "continue"` do `[TDQ:LOG]` / `[TDQ:UNFINISHED]` của phiên cha!
4. **`[P0 — EC-04 & EC-05]` Vừa khóa nhầm trong Worktree vừa lọt lưới trên Repo gốc:**
   - **Khóa nhầm (`EC-04`):** Sau khi `tdq_team.py assign` và mở worktree, Leader đánh dấu `[>]` vào `plan.md` làm đổi `sha_file(plan)`. Hàm `canh_bao_lach_luat` (`tdq_team.py:1615`) vẫn so `plan_sha` thô thay vì `kiem_tra_stale()`, khóa cứng mọi thao tác sửa của subagent bên trong `.tdq-worktrees/<slug>/<task>/`!
   - **Lọt lưới (`EC-05`):** Khi nhánh `tdq/<slug>/t1.1` đã mở (`_co_nhanh == True`) và có `[>]` (`has_doing == True`), nếu subagent (`Workspace="inherit"`) hoặc Leader sửa nhầm `<main_repo>/src/foo.py` bên ngoài `.tdq-worktrees/`, cả 3 rào chắn (`canh_bao_lach_luat`, `ngoai_vung_khai`, `TDQ:TICK`) đều bỏ qua! *(Lưu ý: `swarm` hoặc `Workspace="share"|"branch"` không dùng được vì tạo bản sao ngoài `.tdq-worktrees/` thiếu file `state.json` chưa commit).*
5. **`[P0 — EC-07]` Bỏ lọt 56/65 tool LSP dạng Lazy (`call_mcp_tool`):** Chỉ các tool bật `"eager": true` mới có tên `mcp_tdq-workflow_lsp_*`; toàn bộ 56 tool LSP còn lại được gọi qua `call_mcp_tool(ServerName="tdq-workflow_lsp", ToolName=...)` nên lọt hoàn toàn khỏi `lsp_gate.py` và `search_observe.py` (khiến `search_gate.py` không bao giờ được mở khóa!).
6. **`[P0 — GAP-1 & EC-09]` 8 script hook in thẳng stdout thô + Sai toán học `StartLine`/`EndLine`/`ByteOffset`:** `read_gate.py`, `stop_gate.py`, `session_start.py`, `prompt_context.py`, `search_observe.py`, `search_gate.py`, `lsp_gate.py`, `ask_gate.py` gọi `print()`/`sys.exit(0)` trực tiếp không qua adapter; `read_file` của Antigravity dùng dòng kết thúc bao gồm `EndLine` (`limit = EndLine - eff_start + 1`, không phải `limit = EndLine`) và phân trang `ByteOffset=46080` cho file > 46 KB (nếu không miễn trừ `ByteOffset > 0` sẽ báo nhầm lặp `[TDQ:DOC]`).
7. **`[P1 — EC-10 & EC-12]` Race condition NTFS (mất 29.1% dòng) & Độ trễ `PreInvocation`:** `PreInvocation` bắn trước **mỗi bước model** trong cùng 1 lượt (15 bước = 15 lần, mất 2.5s+ và xóa snapshot giữa lượt nếu không tách bước 1 với bước 2..N); ghi chung `.tdq-turn.jsonl` giữa 8 tiến trình song song trên NTFS mất 93/320 dòng do `os.replace` đụng `WinError 5`/`32`.

### 4.3. Nhóm 8 Lỗi P0 + 11 Lỗi P1 Trong 67 File `scripts/*.py` Trên Windows (`NEW-01` → `NEW-28`)
1. **`[P0 — NEW-01]` `tdq_finish.py:73, 86-93` cắt cụt ký tự đầu tên file:** `_run()` gọi `.strip()` trên kết quả `git status --porcelain` làm mất dấu cách đầu của dòng `" M docs/tdq/spec/..."`, khiến `line[3:]` cắt mất chữ `'d'` thành `"ocs/tdq/spec/..."` → `os.path.exists()` trả `False` → **bỏ qua im lặng `doc_lint.py` và `token_budget.py`!** Ngoài ra thiếu `-c core.quotepath=false -z` làm hỏng tên file tiếng Việt.
2. **`[P0 — NEW-02]` `lsp_module.py:503-521, 560` giết nhầm `agent-lsp` đang chạy:** Gọi PowerShell WMI với `CREATE_NO_WINDOW` làm `[Console]::OutputEncoding` rơi về `IBM437`, biến đường dẫn tiếng Việt thành `D?An_...` → `os.path.isdir()` trả `False` → `don_broker()` gọi `taskkill /F` giết chết `agent-lsp` đang sống!
3. **`[P0 — NEW-03 & NEW-04]` `search_rules.py` chặn oan lệnh PowerShell hợp lệ & trượt split LSP ở dòng `887`:**
   - Dòng `887` dùng `re.split(r"__|\.", ten)[-1]` nên không tách được tên tool từ `mcp_tdq-workflow_lsp_find_references` (1 gạch dưới)!
   - Hàm `_tach_script` (`dòng 261-285`) coi dấu `\` cuối đường dẫn `"C:\Users\admin\"` là ký tự thoát ngoặc kép của POSIX và coi backtick `` `n `` của PowerShell là command substitution → gán `la_malformed=True` → **chặn cứng (`deny`) các lệnh PowerShell bình thường ở MỌI phase!** Đồng thời `search_rules.py` thiếu `import utf8_io` khi chạy CLI.
4. **`[P0 — NEW-05]` `tdq_state.py:409-427` xóa trắng trạng thái khi gặp UTF-8 BOM:** PowerShell 5.1 `Set-Content -Encoding UTF8` ghi 3 byte BOM; `tdq_state.load()` đọc bằng `encoding="utf-8"` bị `JSONDecodeError`, lập tức **đổi tên `state.json` thành `state.json.corrupt-<ts>`** và reset workflow về `None`!
5. **`[P0 — NEW-06 & NEW-07]` `tdq_setup.py` & `tdq_codex_mcp.py` làm hỏng môi trường chéo:** `session_start.py` gọi `tdq_setup.py` mất `12.68s`, văng `WinError 206` trên `.claude/worktrees/`, ghi đè `~/.claude/CLAUDE.md` và tạo `.codex/hooks.json` trỏ vào đường dẫn không tồn tại; `doc_phien_ban_plugin()` trả `None` trên `plugin.json` gốc của Antigravity.
6. **`[P0 — NEW-08]` Đứt gãy 3 tầng giữa `tdq_harvest.py` và `tdq_knowledge.py`:** Quét sai thư mục (`docs/workinglog` thay vì cả `docs/tdq/logs`), lệch khóa `status:` vs `trang_thai:`, và `tdq_knowledge.py check` không đệ quy vào `candidates/` & `approved/`.
7. **Các lỗi `P1` tiêu biểu khác (`NEW-09` → `NEW-19`):** `tdq_state._probe_codex` tìm `scripts/tdq_codex.py` trong repo người dùng thay vì `GOC_PLUGIN`; `tdq_team.py` thiếu `-c core.longpaths=true` (trên máy này `core.longpaths` đang tắt `false`!), rớt đường dẫn `\` trong `_PATH` và thiếu `rules/`, `.gemini/` trong `TIEN_TO_FILE_LUAT`; `skill_tokens.py` gọi `os.execv` bị lỗi trên Windows MSVCRT; `skill_inventory.py` mù thư mục skill Antigravity; `doc_lint.py` `rule_r15` thiếu mốc ngày slug làm hỏng 6/6 eval seeds và thiếu tiếng Anh; `tdq_checkportable/SKILL.md` gọi cờ đã xóa `setup --trust` (`rc=2`); `tdq_eval.py` phân loại nhầm đường dẫn `docs\tdq\plan\*.md` trên Windows là sửa code nguồn!

---

## 5. Kiểm Chứng Thực Nghiệm 7 Extension & Companion Engine

| # | Extension / Engine | Hạ tầng Máy (OS / Binary) | Giải Pháp Tích Hợp Chuẩn Cho Antigravity (Không Bị Tắt Plugin) |
| :--- | :--- | :--- | :--- |
| **1** | **Agent-LSP MCP** (`agent-lsp.exe`) | Sống 100% (`65 tools` khi truyền đủ 7 language server args từ `fnm\aliases\default\...`). | Khai báo server `"lsp"` trong `mcp_config.json` (Antigravity tự prefix thành `tdq-workflow_lsp`), bật `"eager": true` cho 9 tool chính, bắt thêm `call_mcp_tool` ở hook cho 56 tool lazy; sửa ống `IBM437` trong `lsp_module.py` và cho `tdq_lsp.py` đọc cấu hình Antigravity thật. |
| **2** | **Chrome DevTools MCP** | Sống 100% trên `127.0.0.1:9222` (`33 tools`). `chrome-devtools-plugin` đang cài chỉ có `skills/`, **không có `mcp_config.json`**. | Đóng gói server `"chrome-devtools"` (`cmd.exe /c npx -y chrome-devtools-mcp@latest --browserUrl=http://127.0.0.1:9222`) ngay trong `mcp_config.json` của `tdq-workflow` (không đụng độ plugin có sẵn), khôi phục 2 skill `tdq-browser-research` & `tdq-browser-test`. |
| **3** | **Tavily MCP** | Spawn được (`5 tools`), lỗi `401` do thiếu khóa OS và truyền chuỗi đen `"${TAVILY_API_KEY}"`. | **TUYỆT ĐỐI KHÔNG khai báo `"variables"`** trong `mcp_config.json` (vì sẽ làm tắt toàn bộ plugin `tdq-workflow`!). Nếu có khóa trong cấu hình cục bộ khi chạy `tdq_setup.py` / `--sinh-agy` thì điền trực tiếp vào `mcp_config.json` cục bộ (chỉ sinh `tavily-backup` khi có khóa phụ thật); nếu dùng biến OS thì bỏ hẳn khóa khỏi `"env"` để kế thừa tự nhiên; fallback sạch về `search_web`. |
| **4** | **Archify Visual BA** | Sống 100% (`Node v24.21.0` + `~/Documents/archify`, xuất HTML `806 KB` đạt 4 cổng). | Giữ nguyên kiến trúc CLI, đổi `"utf-8"` sang `"utf-8-sig"` khi đọc JSON và thêm `.gemini`, `.agents` vào `EXCLUDED_DIR_NAMES`. |
| **5** | **Graphify AST** | Sống 100% (`graphify.exe`, BFS 2 bước nhảy). | Thêm `docs/tdq`, `.tdq-worktrees`, `.gemini`, `.agents` vào `tdq_graphify.OUTPUT_DIRS` để cập nhật `state.json` không làm bẩn trạng thái `stale` của Graphify. |
| **6** | **Vision Diff & Canvas** | Sống 100% (`Pillow 13.0.0` + 6 script `canvas_*.py`). | Bỏ dòng nối lệnh `\` cuối dòng trong `vision-test-loop.md:87-94` và đổi gợi ý `python3` sang `py -3`. |
| **7** | **Codex CLI** | Có binary (`codex.cmd`), chờ `dong-y`. | Sửa `tdq_state._probe_codex` & `tdq_codex.kiem_hook_ban` tìm trong `GOC_PLUGIN`, bọc `_cli_run` trong `OwnedProcessJob`, sửa `sys.stdin.reconfigure` trong `codex_edit_gate.py`, và chặn `tdq_codex_mcp.py` ghi đè `.codex/hooks.json` hỏng. |

---

## 6. Đặc Tả Kỹ Thuật Chi Tiết 7 Nhóm Việc Cần Sửa (Zero-Blind-Spot Porting Blueprint)

### Nhóm 1 `[P0]` — Nâng Cấp Trình Đóng Gói Antigravity, Kiểm Định `agy plugin validate` & Cơ Chế Đồng Bộ
- [ ] **Chốt Baseline nguồn từ `dev @ b423ee06` (`v0.97.0`):** Giữ đầy đủ `_archify_gate`, `_chan_report_thieu`, `read_gate` overlap 70%, `soul.md` #4 và `doc_lint` R15.
- [ ] **Sửa dứt điểm `build_portable.py --sinh-agy`:**
  1. **Không bao giờ thay biến vào tệp `.py` (`doi_bien=False` cho `*.py`):** Để Python tự suy ra `GOC_PLUGIN = Path(__file__).resolve().parent.parent`; chỉ biến đổi văn bản trên các tệp `.md` (giữ nguyên các tệp `.json` như `handoff-schema.json`).
  2. **Chuẩn hóa đường dẫn & Regex an toàn trên `.md`:** Chuyển `goc_cai` sang dấu gạch chéo xuôi POSIX (`C:/Users/...`) trước khi thay `${CLAUDE_PLUGIN_ROOT}`; thu hẹp regex đường dẫn tương đối để chỉ khớp đúng tên script thật của plugin (`scripts/(?:tdq_\w+|doc_lint|kiem_no_marker|scan_block_symbols|skill_inventory|step_audit|token_audit)\.py`), không làm hỏng các ví dụ `scripts/alpha.py` trong tài liệu.
  3. **Đóng gói đủ 12 Skills (`11` gốc + `tdq-checkportable`), 6 Subagents, 20 tệp Hooks, `assets/logo.svg`, `plugin.json` chuẩn** (có `displayName`, `logo`, `suggestedPrompts`).
  4. **Bộ lọc Script chuẩn xác:** Loại 12 script dev/canvas nội bộ và `scripts/samples/*`, **NHƯNG GIỮ LẠI `scripts/tdq_knowledge.py`** để đi cặp với `tdq_harvest.py`!
- [ ] **Cổng kiểm định cứng khi Build (`Zero-Error Gate`):** Cuối bước build tự động chạy:
  1. `ast.parse` trên 100% tệp `.py` xuất ra;
  2. **`agy plugin validate <dich> --strict --json`** — bắt buộc `ExitCode == 0`, `errors == 0`, `warnings == 0`, kiểm tra mọi `SKILL.md` và `rules/*.md` đều `< 24.000 bytes`!
- [ ] **Script cài đặt / đồng bộ tự động (`install_agy.py` hoặc `--install-agy`):** Đồng bộ bản build vào `C:\Users\admin\.gemini\config\plugins\tdq-workflow` (nhắc người dùng bật qua `agy plugin enable tdq-workflow` hoặc `customization://tdq-workflow`, tuyệt đối không sửa tay `config.json`).

### Nhóm 2 `[P0]` — Kiến Trúc Luật 2 Tầng (`rules/AGENTS.md` + `rules/*.md` Lazy) & Biên Dịch Ngôn Ngữ Tool/Shell
- [ ] **Tầng 1 — Luật Thường Trực `rules/AGENTS.md` (`~8.500 – 10.500 B` < `24.000 B`, ~11% ngân sách `20k tokens`):**
  - Chứa Hiến pháp `Soul` (kèm Bất biến #5 *Triage Before Touch*), quy tắc bắt buộc mở `tdq-intake` (trừ Tier `nhỏ`), quy tắc **cấm tuyệt đối gọi tool `ask_question`** và cấm chuyển sang `/plan` nội tại hay bật `RequestFeedback: true` ở các cổng duyệt TDQ (phân biệt rõ `/plan` của Antigravity với `/tdq-plan` của TDQ!).
  - Quy tắc **PowerShell 5.1 trên Windows**: mỗi `run_command` là một phiên mới; dùng `;` thay vì `&&`; dùng `$env:TDQ_PROJECT_DIR = "$env:TEMP\..."; py -3 ...` thay vì `VAR=val`; không dùng `\` nối dòng cuối câu lệnh; dùng `Select-String` / `Get-ChildItem` / `py -3` thay vì `rg` / `grep` trần (vì không có trên `PATH` Windows).
  - Bảng ánh xạ công cụ chính xác của **Antigravity 2.0**:
    - `Bash` → `run_command`; `Read (offset, limit)` → `read_file (StartLine, EndLine)`; `Edit` → `edit_file`; `Write` → `write_file`.
    - Tìm kiếm khái niệm → `mcp_tdq-workflow_lsp_*` (hoặc `call_mcp_tool` cho LSP lazy) + `tdq_graphify.py`; tìm chuỗi/liệt kê file → `run_command` (`Select-String`, `Get-ChildItem`) *(không hướng dẫn gọi `grep_search`/`find_by_name`/`list_dir` vì không tồn tại trong Antigravity 2.0)*.
    - `Agent` / `Task` → `invoke_subagent` (`TypeName="tdq-implementer"` tên trần không tiền tố, `Workspace="inherit"`, `Model` chỉ thuộc `inherit | flash_lite | flash | pro`; **cấm dùng `swarm`** cho các wave của `tdq_team.py`).
- [ ] **Tầng 2 — Luật Ngôn Ngữ & Chuyên Đề Lazy (`rules/lang-*.md` với `trigger: glob` & `rules/domain-*.md` với `trigger: model_decision`):**
  - Xuất tự động từ `skills/tdq-build/references/rules/*.md` sang `rules/` với `trigger: glob` (`globs: "**/*.py"`, `"**/*.ts, **/*.tsx"`, v.v. viết dạng 1 chuỗi phân tách dấu phẩy, không dùng mảng YAML hay `{a,b}`) để nạp tự động khi chạm file mã nguồn mà tốn **0 token nền** (vẫn giữ nguyên 100% các file trong `skills/tdq-build/references/rules/` để không vi phạm `doc_lint.py` R9/R13).
- [ ] **Biên dịch tự động 20 nhóm Mismatch (`M01–M20`) trong bản xuất `skills/**` & `README.md`:**
  - Đổi `python3 ` → `py -3 `, gộp 12 dòng nối `\` thành 1 dòng, sửa `&&` ở `tdq-status/SKILL.md:13` thành `;`, sửa `VAR=val` ở `tdq-conventions/SKILL.md:102` & `plan-template.md:36`, đổi `Edit`/`Write` trong Khóa cơ học #2 của `plan-template*.md` sang `edit_file`/`write_file`, đổi `mcp__lsp__*` → `mcp_tdq-workflow_lsp_*`, đổi `haiku/sonnet/opus` → `flash/inherit/pro`, thêm cấm `ask_question`, làm mềm `mem0-memory` thành tùy chọn, sửa lại toàn bộ `tdq-checkportable/SKILL.md` (bỏ cờ `--trust`), và bỏ các lệnh không tồn tại `/mcp`, `/skills`, `/code-review`, `/hooks`.

### Nhóm 3 `[P0]` — Kiến Trúc Lại Bộ Lifecycle Hooks Song Ngữ, Chống Deadlock Subagent & Sharding NTFS
- [ ] **Xuất `hooks/hooks.json` chuẩn Antigravity (sạch `0` cảnh báo `agy plugin validate --strict`):**
  - Đặt tại `hooks/hooks.json` (hoặc gốc plugin), dùng đường dẫn tương đối `"py -3 -X utf8 \"hooks/scripts/<name>.py\""` (không dùng `${PLUGIN_ROOT}` trong `command`).
  - Đăng ký đầy đủ: `SessionStart`, `PreInvocation`, `PreToolUse` (`edit_file|write_file|...`, `read_file|view_file`, `run_command|manage_task`, `mcp_.*lsp_.*|call_mcp_tool`, `ask_question`, `invoke_subagent|swarm|define_subagent`), `PostToolUse` (`run_command|read_file|mcp_.*(lsp|graphify|txtai).*|call_mcp_tool`), `PostInvocation`, và `Stop`.
- [ ] **Nâng cấp toàn diện `hooks/scripts/_common.py` và toàn bộ các hook con:**
  1. **Đọc `stdin` an toàn UTF-8 (`sys.stdin.buffer.read().decode("utf-8-sig")`) & Chuẩn hóa mọi đầu ra qua `_common.py`:** Sửa toàn bộ các lệnh `print()` / `sys.exit(0)` trần trong `read_gate.py`, `stop_gate.py`, `session_start.py`, `prompt_context.py`, `search_observe.py`, `search_gate.py`, `lsp_gate.py`, `ask_gate.py` (`GAP-1`), thêm `import utf8_io` cho `luat_gon.py` và sửa `sys.stdin.reconfigure` cho `codex_edit_gate.py` (`EC-13`).
  2. **Nhận diện Subagent tất định (`EC-03`, `EC-06`, `GAP-8`):** Kiểm tra dòng đầu (`step_index: 0`) của `payload["transcriptPath"]` (cache kết quả theo `conversationId` trong `docs/tdq/.tdq-runtime/session-<convId>.json`, tốn `< 1 ms`) kết hợp sổ đăng ký `PreToolUse(invoke_subagent|swarm)`. Nếu `step_0.type != "USER_INPUT"` → `is_subagent = True`, tự gán `payload["agent_id"] = conversationId`:
     - Ở `SessionStart` / `PreInvocation` của subagent: chỉ tiêm `[TDQ:GON]` ở bước 1, **tuyệt đối không xóa sổ cái của Leader** và không tiêm `[TDQ:INTAKE]`/`[TDQ:APPROVE]`.
     - Ở `Stop` của subagent: **lập tức trả `{"decision": "allow"}`** để không bao giờ bị nhốt bởi `[TDQ:LOG]` hay `[TDQ:UNFINISHED]`!
     - Ở `PreToolUse(invoke_subagent)` trong `implement_mode == "subagent"`: chặn nếu truyền `Workspace` thuộc `("share", "branch")` cho `tdq-implementer`.
  3. **Fast-path cho `PreInvocation` bước 2..N (`EC-12`) & Cắt bỏ đồng bộ Claude trong `session_start.py` (`EC-11`):** Lưu `last_user_input_sha` + `turn_active` theo `conversationId`; bước 1 mới chụp `turn_snapshot` (`~170ms`), các bước gọi tool 2..N chỉ rút và bơm hàng đợi nhắc nhở (`< 5ms`) mà không reset snapshot giữa lượt! Gỡ bỏ đoạn gọi `claude plugin update` mất `12.7s` khỏi nhánh Antigravity của `session_start.py`.
  4. **Giải bọc `call_mcp_tool` (`EC-07`) & Chuẩn hóa toán học `read_file` (`EC-09`):** Khi `toolCall.name == "call_mcp_tool"`, bóc `ServerName` + `ToolName` + `Arguments` thành `mcp_<ServerName>_<ToolName>` để `lsp_gate.py` và `search_observe.py` bắt đủ 100% tool LSP lazy. Với `read_file`: nếu `ByteOffset > 0` thì miễn cảnh báo đọc lặp; tính đúng `eff_start = StartLine or 1`, `limit = (EndLine - eff_start + 1) if EndLine else 800`.
  5. **Miễn trừ thư mục Brain Artifacts (`EC-01`) & Sửa lỗi thoát sớm `remind("TDQ:LOG")` (`EC-02`):** Loại trừ mọi đường dẫn thuộc `artifactDirectoryPath` / `<appDataDir>/brain/` hoặc nằm ngoài `realpath(cwd)` trước khi gọi `observe("edit")`; đổi `remind()` sang xếp hàng trong bộ nhớ và chỉ flush sau khi vượt qua toàn bộ các cổng `block()`!
  6. **Khóa chặt 2 chiều cho Worktree (`EC-04` & `EC-05`) + Khóa `[TDQ:FEEDBACK]` (`EC-08`):**
     - Sửa `tdq_team.py:1615` dùng `kiem_tra_stale(plan, ban_do)[0]` thay vì `plan_sha` thô; bỏ qua `canh_bao_lach_luat` khi sửa trong `.tdq-worktrees/` nhưng chặn cứng subagent nếu sửa code trên repo gốc ngoài `.tdq-worktrees/` và bỏ lỗ hổng `_co_nhanh` ở `tdq_team.py:1628`.
     - Bổ sung kiểm tra các cmdlet ghi file của PowerShell (`Set-Content`, `Add-Content`, `Out-File`, `New-Item`, `Remove-Item`, `Move-Item`, `Copy-Item`) và `manage_task(send_input)` vào `bash_gate.py`.
     - Chặn sửa code nguồn khi `phase in ("idle", "report")` bằng cổng **`[TDQ:FEEDBACK]`** (bắt buộc phân loại 3 mức theo `soul.md` hoặc khai báo token sửa nhanh `hotfix --tier nho` tối đa 2 file).
  7. **Chuẩn hóa đầu ra JSON & Sharding sổ cái theo `conversationId` (`EC-10`):**
     - `PreToolUse` trả `{"decision": "deny", "reason": ...}` khi chặn và `{"decision": "allow"}` khi cho qua (xếp hàng nhắc nhở sang `PostInvocation`/`PreInvocation` kế tiếp).
     - `Stop` của Leader chỉ xét chặn khi `terminationReason == "NO_TOOL_CALL"`, trả `{"decision": "continue", "reason": ...}` khi giữ lại và `{"decision": "allow"}` ở mọi trường hợp khác.
     - Tách sổ cái runtime theo phiên `docs/tdq/.tdq-runtime/{turn,read,snap,streak,reminders}-<convId>.jsonl` kèm khóa tệp `msvcrt.locking` cho các file dùng chung (`.tdq-search.jsonl`, `sessions.json`).

### Nhóm 4 `[P0]` — Biên Dịch Chuẩn 6 Subagents (`agents/tdq-*.md`) Pass 100% `agy plugin validate`
- [ ] **Chuẩn hóa YAML Frontmatter cho cả 6 tệp trong `plugins/tdq-workflow/agents/`:**
  - Lược bỏ `effort:` và `color:`; đổi `model: haiku` ở `tdq-implementer.md` thành `model: inherit` (hoặc `flash` theo cấu hình được phép); `tools:` bắt buộc là mảng YAML chỉ chứa các tool có thật trên Antigravity 2.0:
    - `tdq-implementer`, `tdq-build-resolver`, `tdq-refactor-cleaner`: `tools: [read_file, edit_file, write_file, run_command, manage_task, send_message]`
    - `tdq-qc-tester`: `tools: [read_file, run_command, manage_task, send_message]`
    - `tdq-reviewer`, `tdq-security-reviewer`: `tools: [read_file, run_command, send_message]` *(quyền cấm sửa file/chạy lệnh ghi được cưỡng chế cơ học bởi `edit_gate.py` + `bash_gate.py` dựa trên `agent_type` trong `sessions.json`!)*.
- [ ] **Tiêm 3 quy tắc vận hành Antigravity vào thân cả 6 Subagents:**
  1. Gộp quy tắc `[TDQ:GON]` từ `subagent_start.py`.
  2. Mọi lệnh `run_command` trên worktree phải mở đầu bằng `Set-Location "<WORKTREE>"; ` và mọi lệnh `read_file`/`edit_file`/`write_file` phải truyền đường dẫn tuyệt đối `<WORKTREE>/...`.
  3. **Bắt buộc** gọi `send_message(Recipient="<caller_conversation_id>", Message="<báo cáo/JSON handoff>")` khi hoàn tất vì đầu ra văn bản thường của subagent không tự chuyển về cho Leader trên Antigravity!

### Nhóm 5 `[P1]` — Cấu Hình `mcp_config.json` Chuẩn Xác & Nâng Cấp Setup/LSP/DevTools Đa Host
- [ ] **Sinh `mcp_config.json` không khai báo `"variables"` (tránh tự tắt plugin):**
  1. `"lsp"`: `command` trỏ tuyệt đối tới `agent-lsp.exe`, `args` trỏ các language server bền vững (`AppData\Roaming\fnm\aliases\default\...`, cấm `fnm_multishells`), bật `"eager": true` cho 9 tool cốt lõi.
  2. `"chrome-devtools"`: `command: "cmd.exe"`, `args: ["/c", "npx", "-y", "chrome-devtools-mcp@latest", "--browserUrl=http://127.0.0.1:9222"]`.
  3. `"tavily-primary"` (và `"tavily-backup"` chỉ khi có khóa phụ thật): Không đặt placeholder `"${TAVILY_API_KEY}"`; để `tdq_setup.py` đồng bộ khóa cục bộ khi cài đặt hoặc bỏ khỏi `"env"` để kế thừa biến OS.
- [ ] **Nâng cấp `tdq_setup.py`, `setup_status.py`, `tdq_lsp.py`, `lsp_module.py`, `tdq_devtool_mcp.py`, `tdq_codex_mcp.py`, `skill_inventory.py`:**
  - `doc_phien_ban_plugin()` đọc thêm `plugin.json` gốc (`NEW-06`); bỏ `shlex.split` POSIX trên đường dẫn Windows và hỗ trợ `\` + `py -3` trong `_RE_LENH_WORKFLOW` (`NEW-18`); tắt mọi tác vụ ghi `~/.claude/CLAUDE.md` và `.codex/hooks.json` khi chạy ở chế độ Antigravity (`GAP-3`, `NEW-07`).
  - Cho `tdq_lsp.py`, `lsp_module.py`, `tdq_devtool_mcp.py`, `setup_status.py`, `skill_inventory.py` đọc trực tiếp cấu hình `~/.gemini/config/plugins/tdq-workflow/` và `~/.gemini/antigravity/mcp_config.json` (`NEW-13`).

### Nhóm 6 `[P0/P1]` — Vá Trọn Bộ Lỗi Lõi CLI Trên Windows (`NEW-01` → `NEW-28`)
- [ ] **`tdq_finish.py` (`NEW-01`):** Đổi sang `git -c core.quotepath=false status --porcelain -z` (không dùng `.strip()` cắt mất dấu cách đầu dòng `" M "`), mở rộng `step_khoa_token` kiểm tra cả `agents/` và `rules/`.
- [ ] **`lsp_module.py` (`NEW-02`):** Thêm `[Console]::OutputEncoding = [System.Text.Encoding]::UTF8;` vào đầu lệnh PowerShell WMI (dòng `504`) và không bao giờ giết broker có `cha_song == True` khi đường dẫn chứa `'?'`.
- [ ] **`search_rules.py` (`NEW-03`, `NEW-04`):** Thêm `import utf8_io`; sửa cả dòng `868` lẫn `887` bằng named regex cho `mcp_<server>_lsp_<tool>`; nhận diện `run_command` (`CommandLine`) và PowerShell `Get-ChildItem -Recurse`; sửa `_tach_script` không báo lỗi `malformed` oan cho đường dẫn `"C:\path\"` và ký tự thoát `` `n `` của PowerShell!
- [ ] **Chống hỏng file do UTF-8 BOM (`NEW-05`):** Đổi toàn bộ trình đọc JSON/Markdown/AST trong `tdq_state.py`, `tdq_test.py`, `tdq_checkstatus.py`, `doc_lint.py`, `tdq_archify.py`, `tdq_skill_eval.py` từ `encoding="utf-8"` sang `encoding="utf-8-sig"`.
- [ ] **`tdq_team.py` & `tdq_state.py` & `tdq_test*.py` (`NEW-09..12`, `NEW-19`, `NEW-23`):** Thêm `-c core.longpaths=true` + dọn nhánh mồ côi khi lỗi tạo worktree; cho phép `\` trong `_PATH`; bổ sung `rules/`, `.gemini/`, `.agents/`, `.tdq-worktrees` vào `TIEN_TO_FILE_LUAT`, `PRUNE_DIRS`, `OUTPUT_DIRS`, `EXCLUDED_DIR_NAMES`; thêm `"qc_file": None` vào `default_state()`; sửa `_probe_codex` tìm trong `GOC_PLUGIN`; sửa `skill_tokens.py` bỏ `os.execv`; đệ quy `tat_ca_module()` trong `tdq_test.py` và retry cả `winerror == 5` trong `tdq_test_process.py`.
- [ ] **`tdq_harvest.py` & `tdq_knowledge.py` (`NEW-08`) + `doc_lint.py` R15 (`NEW-17`):** Thống nhất thư mục log, schema `trang_thai:` và quét đệ quy cho `tdq_knowledge.py`; thêm mốc ngày slug và từ khóa tiếng Anh (`Touch:`/`Files:`, `Pseudocode:`) cho `rule_r15`.

### Nhóm 7 `[P2]` — Bộ Đọc Transcript Antigravity (Giải Mã Double-JSON) & Hỗ Trợ Host Eval
- [ ] **Cập nhật `tdq_transcript.py`, `tdq_timing.py`, `step_audit.py`, `token_audit.py`, `search_replay.py`, `tdq_eval*.py`:**
  - Thêm `import utf8_io` cho `tdq_transcript.py` và `tdq_worktree_registry.py`.
  - Bổ sung bộ đọc `<appDataDir>/brain/<conversation-id>/.system_generated/logs/transcript.jsonl` (bỏ qua `transcript_full.jsonl` và `chunks/`).
  - **Xử lý Double-JSON trong `tool_calls[].args`:** Tự động `json.loads()` thêm 1 lớp đối với các giá trị chuỗi JSON lồng bên trong `args` (`"\"pytest -q\""` → `"pytest -q"`) trước khi trích xuất `CommandLine` / `Path`.
  - Bổ sung host `"antigravity"` vào `tdq_ten_lenh.py`, `tdq_timing.py`, `tdq_eval_hosts.py`, `tdq_eval_contract.py` và chuẩn hóa `\` trước khi kiểm tra thư mục tài liệu trong `tdq_eval.py:_ghi_ma_nguon` (`NEW-15`).
