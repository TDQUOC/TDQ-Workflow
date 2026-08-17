# SPEC — Bản portable_codex dùng đúng cơ chế native của Codex CLI

Ngày: 2026-08-17 · Bản: 1.0 · Brief: ../brief/2026-08-17-1139-codex-native-layers.md · Lane: full
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md
Trạng thái: CHỜ DUYỆT

## 1. Mục tiêu & phạm vi

- **Mục tiêu:** `portable_codex/` chép vào một project bất kỳ thì Codex CLI (>= 0.147.0) tự nạp
  được **skill**, **MCP server** và **cả 5 hook** của bộ TDQ — thay vì chỉ có markdown đọc tay
  như hiện nay. Đo bằng: chạy `codex` thật trên bản sinh và thấy Codex liệt kê đủ 8 skill,
  2 MCP server, và hook chặn được một hành động thử.
- **Trong phạm vi:**
  - Sửa `sinh_ban_codex()` trong `scripts/build_portable.py` để sinh thêm 4 nhóm hiện vật native.
  - Thêm lệnh `setup --trust` vào `scripts/tdq_checkportable.py`: ghi
    `[projects."<path>"] trust_level = "trusted"` vào `~/.codex/config.toml`, có sao lưu.
  - Viết lại `AGENTS.md`, `README_CODEX` và docstring `build_portable.py`/`sinh_ban_codex()`
    cho hết giả định "harness không có skill/hook system".
  - Sửa `docs/kien-truc.md`: dòng tầng `portable/` trỏ vào thư mục đã bị xoá.
  - Test cho từng phần + một mức kiểm mới: chạy `codex` thật trên bản sinh.
- **NGOÀI phạm vi:**
  - `portable_claude/` — đang đúng, đã QC 3 vòng, không đụng.
  - `skills/`, `hooks/`, `agents/` nguồn của repo — chỉ đọc để sinh, không sửa.
  - Hỗ trợ harness khác (Antigravity, Gemini CLI) ở mức native — vẫn chỉ có `workflow/NN-*.md`.
  - Các event Codex bộ TDQ không dùng: `PermissionRequest`, `PostToolUse`, `PreCompact`,
    `PostCompact`, `SubagentStart`, `SubagentStop`.
  - Không chạy vòng scope ở phase analyze (lý do đã ghi ở brief), nên không có mặt nào bị loại
    ở vòng đó để chép vào đây.

## 1b. Lộ trình

| Bước/phase | Chạy? | Vì sao |
|---|---|---|
| Research web | BỎ | 2 vòng đã xong, phần hook chốt bằng source `codex-rs/hooks`; 3 rủi ro còn lại thuộc loại chỉ chạy thật mới biết |
| Interview | BỎ (đã xong) | vòng 1 gồm 4 câu, user đã trả lời `1a 2a 3b 4a` |
| Spec + plan | CÓ | khung bất biến |
| Implement | CÓ | khung bất biến |
| Chạy thật `codex` trên bản sinh | CÓ | request trước QC 3 vòng vẫn không bắt được spec sai, vì QC chỉ đối chiếu bản sinh với spec |
| QC độc lập (agent `tdq-qc-tester`) | CÓ | request trước QC bắt 10 khuyết tật — tỷ lệ quá cao để bỏ |
| Review sâu spec/plan (`tdq-reviewer`) | BỎ | user chưa yêu cầu; thay đổi khu trú trong 2 file mã |
| Report | CÓ | khung bất biến |

## 2. Đầu ra cụ thể

| # | Đầu ra | Đường dẫn/vị trí | Đo "xong" bằng |
|---|---|---|---|
| 1 | Skill theo chuẩn Codex, 8 skill, mỗi skill có frontmatter `name`+`description` | `portable_codex/.agents/skills/<tên>/SKILL.md` (+ `references/`) | `python3 -m pytest tests/test_build_portable.py -q` xanh; mọi SKILL.md parse được frontmatter và có đủ 2 trường |
| 2 | Cấu hình MCP cấp project | `portable_codex/.codex/config.toml` | `tomllib.load()` ra `mcp_servers` đủ 2 server; không chuỗi nào chứa giá trị khoá |
| 3 | Cấu hình 5 hook TDQ | `portable_codex/.codex/hooks.json` | JSON parse được; đủ 4 event `SessionStart`/`UserPromptSubmit`/`PreToolUse`/`Stop`, trong đó `PreToolUse` có 2 matcher group |
| 4 | Cây hook chạy được, cạnh `scripts/` | `portable_codex/hooks/scripts/*.py` + `portable_codex/scripts/*.py` | chạy `python3 <bundle>/hooks/scripts/edit_gate.py` với payload JSON qua stdin → exit 0, in JSON hợp lệ |
| 5 | Lệnh tự bật trusted | `scripts/tdq_checkportable.py` lệnh `setup --trust` | test: `~/.codex/config.toml` giả có sẵn nội dung → sau khi chạy có thêm block `[projects."…"]` và có đúng 1 file `.tdq-bak-*` |
| 6 | Tài liệu hết giả định sai, và nêu **bốn** việc thủ công (thêm: duyệt hook trong giao diện Codex) | `AGENTS.md`, `README_CODEX`, docstring `build_portable.py` | `grep -r "không có skill/hook system\|hook là cơ chế riêng của Claude Code" portable_codex/ scripts/build_portable.py` → 0 dòng |
| 7 | `manifest.json` phủ hết file mới | `portable_codex/manifest.json` | `python3 scripts/tdq_checkportable.py check --root portable_codex` exit 0 ngay sau khi sinh |
| 8 | Hồ sơ kiến trúc khớp thực tế | `docs/kien-truc.md` | `grep -c "portable/" docs/kien-truc.md` → 0 dòng nhắc thư mục đã xoá |
| 9 | Bằng chứng Codex nạp thật | `docs/tdq/qc/<slug>.md` | chạy `codex` trên bản sinh, dán output cho thấy skill/MCP/hook được nạp |

## 3. Cách tiếp cận & lý do

- **Chọn:** giữ nguyên bộ sinh một-nguồn. `sinh_ban_codex()` sinh thêm các lớp native từ chính
  `skills/` + `hooks/` + `hooks/hooks.json` đang có; không tạo nguồn thứ hai.
- **Vì:** giao thức hook của Codex **trùng khít** giao thức Claude Code mà
  `hooks/scripts/_common.py` đang dùng — input JSON qua stdin (`cwd`, `tool_name`, `tool_input`),
  output `hookSpecificOutput.permissionDecision` = `allow|deny|ask` và `decision` =
  `approve|block`. Xác minh CAO, đọc thẳng `codex-rs/hooks/src/schema.rs` +
  `codex-rs/core/src/hook_runtime.rs` (nguồn đầy đủ:
  `docs/tdq/research/2026-08-17-1139-codex-native-layers.md`). Nên chỉ cần **ánh xạ cấu hình**,
  không cần dịch giao thức.
- **Bố cục bundle sau thay đổi** — `hooks/` và `scripts/` nằm cạnh nhau ở GỐC bundle, không lồng
  trong `.codex/`, vì `hooks/scripts/_common.py` suy `scripts/` bằng `../../scripts`:
  ```
  portable_codex/
    AGENTS.md  README.md  manifest.json
    .agents/skills/<tên>/SKILL.md        ← Codex tự nạp (progressive disclosure)
    .codex/config.toml                   ← mcp_servers
    .codex/hooks.json                    ← 5 hook
    hooks/scripts/*.py                   ← mã hook, dùng lại nguyên
    scripts/*.py                         ← CLI (tdq_state, tdq_finish, tdq_checkportable…)
    workflow/NN-*.md + references/        ← giữ, đường lui cho harness khác
  ```
- **Ánh xạ 5 hook** (`hooks/hooks.json` → `.codex/hooks.json`):

  | Hook TDQ | Event Claude Code | Event Codex | Matcher |
  |---|---|---|---|
  | `session_start.py` | SessionStart | `SessionStart` | — |
  | `prompt_context.py` | UserPromptSubmit | `UserPromptSubmit` | — |
  | `edit_gate.py` | PreToolUse | `PreToolUse` | tool sửa file (chốt bằng chạy thật, xem §5 R2) |
  | `bash_gate.py` | PreToolUse | `PreToolUse` | tool chạy lệnh (chốt bằng chạy thật, xem §5 R2) |
  | `stop_gate.py` | Stop | `Stop` | — |
- **Đã loại:** viết lớp adapter riêng dịch giao thức Codex ↔ TDQ — vì giao thức đã trùng, thêm
  một lớp nữa là thêm một chỗ có thể lệch mà không mua được gì (user chốt A2 = A).
- **Đã loại:** bỏ `workflow/NN-*.md` khi đã có `.agents/skills/` — cả hai sinh từ cùng một nguồn
  trong cùng một lần chạy nên không có rủi ro lệch, và nó là đường lui cho harness khác
  (user chốt A4 = A).
- **Đã loại:** thu hẹp lời hứa trong tài liệu thay vì viết mã (cách xử lý của request trước cho
  quyết định 3B) — lần này quyền ghi `~/.codex/config.toml` phải là **mã chạy thật có test khoá**,
  không được viết vào tài liệu nếu mã không làm.

## 3b. Năng lực & công cụ

| Skill | Nguồn | Phán quyết | Dùng ở đâu / Lý do loại |
|---|---|---|---|
| tdq-conventions | plugin:tdq-workflow | NỀN | luật gốc, mọi skill khác nạp trước |
| tdq-intake | plugin:tdq-workflow | NỀN | đã chạy phase intake + analyze |
| tdq-spec | plugin:tdq-workflow | NỀN | skill đang chạy |
| tdq-plan | plugin:tdq-workflow | NỀN | viết plan ngay sau khi spec được duyệt |
| tdq-build | plugin:tdq-workflow | NỀN | implement + QC + report |
| tdq-qc-tester | plugin:tdq-workflow | DÙNG | agent QC độc lập, đầu ra #1–#9 |
| WebFetch | built-in | DÙNG | đọc lại source Codex khi chốt matcher tool ở §5 R2 |
| tdq-status | plugin:tdq-workflow | KHÔNG | khác lĩnh vực — user không hỏi trạng thái |
| Đã xét 278 skill khác | user/plugin/built-in | KHÔNG | khác lĩnh vực |

## 4. Yêu cầu bắt buộc

- Log service bật mặc định: timestamp, đủ chi tiết debug, tắt/giảm được qua config. Việc này CÓ
  runtime (`build_portable.py`, `tdq_checkportable.py`) — cả hai đã có `log()` ghi stderr kèm
  timestamp, tắt bằng `TDQ_LOG=0`; phần thêm mới phải dùng đúng cơ chế đó, đặc biệt lệnh
  `setup --trust` phải log đủ để dựng lại được đã ghi gì vào file nào.
- Không placeholder, không TODO stub, không mock trình bày như dữ liệu thật.
- Mỗi thành phần có unit test riêng, chạy được bằng một lệnh.
- Code viết ra bám 5 nguyên tắc SOLID theo `skills/tdq-conventions/references/clean-code.md`,
  và bám rule ngôn ngữ trong `skills/tdq-build/references/rules/`.
- **Không bao giờ in hay ghi GIÁ TRỊ khoá** — chỉ TÊN biến môi trường, ở mọi file sinh ra và
  mọi dòng log.

## 5. Ràng buộc & rủi ro

Ràng buộc kiến trúc phải giữ (chép từ `docs/kien-truc.md`):

- *"`hooks/` được gọi `scripts/`; `scripts/` **không** được import `hooks/`"* — việc này chạm ở
  `scripts/build_portable.py` (chỉ COPY cây `hooks/`, không import) và ở bố cục bundle.
- *"File code MỚI bắt buộc nằm trong `scripts/` hoặc `hooks/`"* — mã mới chỉ vào
  `scripts/tdq_checkportable.py` và `scripts/build_portable.py`, không tạo file mã ở chỗ khác.
- *"`skills/` chỉ được nhắc tên lệnh của `scripts/`, cấm chép nội dung script vào skill"* — chạm ở
  `portable_src/skills/tdq-checkportable/SKILL.md` khi mô tả `setup --trust`.
- Hồ sơ này đang ở trạng thái **NHÁP — chờ user chốt**; dòng tầng `portable/` đã lỗi thời và
  được sửa trong chính request này (đầu ra #8).

| Rủi ro | Ảnh hưởng | Cách giảm |
|---|---|---|
| R1. Project `untrusted` → Codex bỏ qua TOÀN BỘ `.codex/`: cả MCP lẫn hook im lặng không chạy | Người dùng tưởng đã có cổng canh mà thực ra không có — đúng loại ảo giác request này sinh ra để diệt | `setup --trust` ghi thật vào `~/.codex/config.toml` (user chốt A3 = B), có backup; `check` báo rõ trạng thái trusted; README nói thẳng hậu quả nếu chưa trusted |
| R2. Chưa biết Codex đặt cwd nào khi chạy hook, và tên tool thật để viết `matcher` | `.codex/hooks.json` sai đường dẫn hoặc sai matcher → hook không bao giờ chạy | Task riêng ở plan: chạy `codex` thật, đọc payload stdin thật. Tiêu chí chốt: chạy được bằng đường dẫn tương đối tính từ gốc project → giữ `hooks.json` trong `manifest.files`; KHÔNG chạy được → chuyển `hooks.json` sang loại sinh-tại-máy-đích (đường dẫn tuyệt đối), loại khỏi `manifest.files`, và thêm hạng mục QC riêng kiểm nó tồn tại + parse được + mọi đường dẫn trỏ tới file có thật |
| R3. Ghi vào `~/.codex/config.toml` là ghi ra ngoài bundle, không hoàn tác được bằng cách xoá thư mục | Hỏng cấu hình Codex của user | Bắt buộc `<file>.tdq-bak-<timestamp>` trước khi ghi; chỉ chèn thêm block `[projects."<path>"]`, không viết lại phần khác của file; log đủ để dựng lại hành động; `--trust` là cờ tường minh, `setup` trần không tự làm |
| R4. Bản stable là 0.147.0 nhưng máy user đang chạy `0.147.0-alpha.6.5` | Có thể khác chi tiết so với source `main` đã đọc | Chạy thật trên chính máy này; ghi version đã kiểm vào report và vào `manifest.json` |
| R5. `.agents/skills` cấp project ổn hơn user-level nhưng độ ổn định qua các version chưa chắc 100% | Skill không được nạp trên bản Codex khác | Chỉ sinh ở cấp project; giữ `workflow/NN-*.md` làm đường lui; `check` báo được cả hai lớp có mặt hay không |
| R6. Số file bản codex tăng mạnh (68 → ~200) vì thêm `hooks/` + `.agents/skills/` | `manifest.json` phình, `check` chậm hơn | Chấp nhận: `check` chỉ đọc + sha256, đo bằng Q7 với ngưỡng < 5 giây |

## 6. QC & Definition of Done

| # | Hạng mục kiểm | Lệnh/cách kiểm | Điều kiện PASS |
|---|---|---|---|
| Q1 | Bộ test toàn repo không đỏ | `python3 -m pytest tests/ -q` | exit 0, 0 failed |
| Q2 | 8 skill sinh đúng chuẩn Codex | `python3 -m pytest tests/test_build_portable.py -q` | exit 0; mỗi `.agents/skills/*/SKILL.md` có frontmatter đủ `name` + `description` |
| Q3 | MCP config đọc được, không lộ khoá | `python3 -c "import tomllib;d=tomllib.load(open('portable_codex/.codex/config.toml','rb'));print(sorted(d['mcp_servers']))"` | in đủ 2 server; không chuỗi nào trong file khớp giá trị biến môi trường thật |
| Q4 | `hooks.json` đủ 5 hook / 4 event | `python3 -c "import json;print(sorted(json.load(open('portable_codex/.codex/hooks.json')).keys()))"` | có `SessionStart`, `UserPromptSubmit`, `PreToolUse`, `Stop`; `PreToolUse` có 2 matcher group |
| Q5 | Hook chạy được trong bố cục bundle | bơm payload JSON mẫu vào `python3 portable_codex/hooks/scripts/edit_gate.py` | exit 0, stdout parse được thành JSON có `hookSpecificOutput` |
| Q6 | `setup --trust` ghi thật + có backup | `python3 -m pytest tests/test_checkportable.py -q` (test dùng `$HOME` giả) | exit 0; `config.toml` giả có thêm block `[projects."…"]`; đúng 1 file `.tdq-bak-*`; nội dung cũ còn nguyên trong bản sao lưu |
| Q7 | Bundle sạch ngay sau khi sinh | `time python3 scripts/tdq_checkportable.py check --root portable_codex` | exit 0, in `SẠCH`, thời gian < 5 giây |
| Q8 | Không còn giả định sai trong tài liệu | `grep -rn "không có skill/hook system\|hook là cơ chế riêng của Claude Code" portable_codex/ scripts/ docs/kien-truc.md` | 0 dòng khớp |
| Q9a | **Codex nạp được bản sinh — mức tự động** | chép `portable_codex/` vào thư mục thử, `setup --trust`, chạy `codex` với cờ bỏ qua cổng tin cậy hook | chứng minh CẤU HÌNH đúng: skill TDQ được liệt kê, MCP server có mặt, cả 5 hook nổ. Dán output vào file qc |
| Q9b | **Codex nạp được bản sinh — mức thật** | cùng bundle đó, chạy `codex` KHÔNG cờ bỏ qua, người dùng duyệt hook một lần trong giao diện | chứng minh LUỒNG NGƯỜI DÙNG đi được: sau khi duyệt, hook nổ mà không cần cờ nào. Ghi rõ nếu không thực hiện được vòng thủ công |
| Q10 | Hồ sơ kiến trúc khớp thực tế | `grep -n "portable" docs/kien-truc.md` | không còn dòng nào nhắc thư mục `portable/` đã bị xoá |

**DoD:** Q1–Q8, Q9a, Q9b, Q10 đều PASS có bằng chứng dán trong `docs/tdq/qc/<slug>.md`; mọi task trong plan
tick `[x]`; QC độc lập bằng agent `tdq-qc-tester` cho kết quả PASS; report nêu rõ version Codex
CLI đã kiểm thật và mọi chỗ lệch so với spec (nếu có).

## 7. Câu hỏi còn mở

(rỗng)
