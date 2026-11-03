# SPEC — Bộ portable tự sinh cho hai harness, có skill tự kiểm & tự setup

<!-- doc-lint: allow R10 — spec viết trước khi có luật ranh giới module -->

Ngày: 2026-08-17 · Bản: 1.0 · Brief: ../brief/2026-08-17-0938-portable-codex.md · Lane: full
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md
Trạng thái: CHỜ DUYỆT

## 1. Mục tiêu & phạm vi

- Mục tiêu: từ nguồn duy nhất trong repo này, **tự sinh** hai thư mục portable —
  `portable_claude/` (bản Claude Code đầy đủ: skill + hook + sub-agent + MCP) và
  `portable_codex/` (bản markdown thuần cho harness không có skill/hook system) — sao cho
  người dùng chỉ cần copy một thư mục vào project của họ trên máy khác là dùng được, và một
  skill `tdq-checkportable` tự kiểm tính toàn vẹn + tự setup thứ còn thiếu.

- Trong phạm vi:
  - `scripts/build_portable.py` — sinh cả hai bản từ `skills/`, `hooks/`, `agents/`, `scripts/`.
  - `scripts/tdq_checkportable.py` — bộ kiểm + tự vá, chạy được độc lập bằng một lệnh.
  - Skill `tdq-checkportable` ở cả hai bản (dạng phù hợp từng harness) — chỉ gọi lệnh, không
    chép logic (luật kiến trúc `skills/` chỉ nhắc tên lệnh).
  - `manifest.json` trong mỗi bản: file + sha256, version bộ, Python tối thiểu, lệnh ngoài
    cần có, MCP server cần có.
  - Rewrite `${CLAUDE_PLUGIN_ROOT}` → `${CLAUDE_PROJECT_DIR}` khi sinh bản claude.
  - Instruction mặc định của cả hai bản trỏ `tdq-checkportable` chạy đầu tiên.
  - Thay `portable/` viết tay hiện có bằng `portable_codex/` tự sinh (xoá thư mục cũ).

- NGOÀI phạm vi:
  - Không sửa `scripts/claude_export.py` (cơ chế bundle máy-sang-máy, mục đích khác).
  - Không tự cài MCP server lên máy đích (chỉ phát hiện thiếu + hướng dẫn; xem §5 rủi ro R3).
  - Không tìm cách vượt trust dialog / MCP approve / restart — ba giới hạn cứng của Claude
    Code, chỉ phát hiện và báo.
  - Không đóng gói `.git`, `docs/tdq/` (state, brief, spec, plan của repo nguồn), `graphify-out/`.
  - Không hỗ trợ harness thứ ba ngoài Claude Code và nhóm dùng `AGENTS.md`.

## 1b. Lộ trình

| Bước/phase | Chạy? | Vì sao |
|---|---|---|
| Research web | CÓ (đã xong) | Ẩn số ngoài: cơ chế project-level của Claude Code; đã xác minh qua docs chính thức, kết quả ở brief |
| Đọc code hiện trạng | CÓ (đã xong) | 2 nhánh khảo sát: cơ chế đóng gói sẵn có + phụ thuộc đường dẫn |
| Interview | CÓ (đã xong) | 2 vòng: chốt nghĩa "codex", rồi chốt 1A/2C/3B/4A |
| Vòng scope | CÓ (đã xong) | Chính là vòng 1A-4A ở brief |
| Spec → Plan → Implement | CÓ | Việc đụng hook/settings/script sinh code, cần plan checkbox từng task |
| QC độc lập (agent `tdq-qc-tester`) | CÓ | Rủi ro cao nhất là bản sinh gãy im lặng ở máy khác; cần người kiểm độc lập chạy thật |

## 2. Đầu ra cụ thể

| # | Đầu ra | Đường dẫn/vị trí | Đo "xong" bằng |
|---|---|---|---|
| 1 | Script sinh bản portable | `scripts/build_portable.py` | `python3 scripts/build_portable.py --dest <tmp>` exit 0, sinh đủ 2 thư mục |
| 2 | Script kiểm + tự vá | `scripts/tdq_checkportable.py` | `python3 scripts/tdq_checkportable.py check` exit 0 trên bản vừa sinh |
| 3 | Bản Claude Code | `portable_claude/` | có `.claude/settings.json`, `.claude/skills/`, `.claude/agents/`, `.mcp.json`, `scripts/`, `manifest.json`, `README.md` |
| 4 | Bản markdown thuần | `portable_codex/` | có `AGENTS.md`, `workflow/`, `scripts/`, `manifest.json`, `README.md` |
| 5 | Skill tự kiểm (bản claude) | `portable_claude/.claude/skills/tdq-checkportable/SKILL.md` | grep thấy lệnh gọi script, KHÔNG chép logic |
| 6 | Skill tự kiểm (bản codex) | `portable_codex/workflow/06-checkportable.md` | `AGENTS.md` trỏ tới file này ở bước đầu |
| 7 | Manifest mỗi bản | `<bản>/manifest.json` | sha256 khớp 100% file thực tế; có đủ 5 khối bắt buộc (§4) |
| 8 | Unit test | `tests/test_build_portable.py`, `tests/test_checkportable.py` | `python3 -m pytest tests/test_build_portable.py tests/test_checkportable.py` xanh |
| 9 | Xoá bản viết tay cũ | `portable/` không còn | `test -d portable` trả về false |

## 3. Cách tiếp cận & lý do

- Chọn: **một nguồn — hai đích, sinh bằng script**, không viết tay bản nào.
- Vì: `portable/` hiện tại là bằng chứng ngược — README của nó ghi rõ "Không tự sinh, sửa
  `skills/` xong nhớ đồng bộ tay", và test khoá đồng bộ `test_portable_sync.py` đã bị xoá từ
  0.10.0, nên bản đó gần như chắc chắn đang lệch với `skills/` thật. Sinh tự động là cách
  duy nhất khiến bản portable không mục theo thời gian.
- Vì (kỹ thuật): khảo sát cho thấy phần khó nhất **đã sẵn sàng** — không có hard-code
  `/Users/...` nào, `resolve_project_dir()` đã ưu tiên `TDQ_PROJECT_DIR` > git root > cwd nên
  state luôn nằm ở project user, script pure stdlib, cross-link giữa skill đều tương đối.
  Rào cản còn lại chỉ là `${CLAUDE_PLUGIN_ROOT}` (17 file) — mà mã Python **không đọc biến
  này**, nên rewrite là thao tác chuỗi thuần, không phải sửa logic.
- Vì (bản claude khả thi không cần lệnh cài): docs chính thức xác nhận Claude Code tự nạp
  `.claude/skills/`, `.claude/agents/`, hook trong `.claude/settings.json` (hỗ trợ
  `${CLAUDE_PROJECT_DIR}`, có ví dụ chính thức) và `.mcp.json` ở root project.
- Đã loại: **mở rộng `portable/` hiện có** — vì giữ nguyên cách viết tay là giữ nguyên nguồn
  gây lệch.
- Đã loại: **dùng `extraKnownMarketplaces`/`enabledPlugins`** — hai field này chỉ *enable*
  plugin đã cài, không tự tải/cài, nên không phục vụ được kịch bản "chỉ copy folder".
- Đã loại: **tái dùng `claude_export.py`** — cùng kỹ thuật (manifest + sha256 + lọc secret)
  nhưng đích đến khác hẳn (dựng lại môi trường máy mới, có `git clone`, copy `~/.claude`).
  Sẽ **học lại cách làm manifest/lọc secret** từ nó, không sửa hay gọi vào nó.

## 3b. Năng lực & công cụ

| Skill | Nguồn | Phán quyết | Dùng ở đâu / Lý do loại |
|---|---|---|---|
| `tdq-intake` | plugin:tdq-workflow | NỀN | Skill khung đang chạy — đã lo intake + analyze |
| `tdq-spec` | plugin:tdq-workflow | NỀN | Skill khung đang chạy — sinh chính file này |
| `tdq-plan` | plugin:tdq-workflow | DÙNG | Turn sau khi duyệt spec: viết plan checkbox |
| `tdq-build` | plugin:tdq-workflow | DÙNG | Thực thi plan + QC + report |
| `tdq-conventions` | plugin:tdq-workflow | NỀN | Luật chung, mọi skill đều nạp |
| `claude-code-guide` | built-in (agent) | DÙNG | Đã dùng xác minh cơ chế project-level; dùng lại nếu implement phát sinh nghi vấn API |
| Đã xét 40 skill khác | user/plugin/built-in | KHÔNG | khác lĩnh vực |

## 4. Yêu cầu bắt buộc

- Log service bật mặc định: timestamp, đủ chi tiết debug, tắt/giảm được qua config
  (`TDQ_LOG=0`, giống `tdq_timing.py`). Áp cho cả `build_portable.py` và
  `tdq_checkportable.py` — hai script này có runtime.
- **Riêng `tdq_checkportable.py` khi tự setup (quyết định 3B — quyền tối đa):** mọi hành vi
  ghi ra ngoài project phải (a) log đủ để dựng lại việc đã làm, (b) backup file user-level
  trước khi sửa (`<file>.tdq-bak-<timestamp>`), (c) **không bao giờ in giá trị secret** ra
  log/report — chỉ in tên khoá.
- Không placeholder, không TODO stub, không mock trình bày như dữ liệu thật.
- Mỗi thành phần có unit test riêng, chạy được bằng một lệnh.
- Code viết ra bám 5 nguyên tắc SOLID theo `skills/tdq-conventions/references/clean-code.md`,
  và bám rule ngôn ngữ trong `skills/tdq-build/references/rules/`. Luật này luôn áp.
- `manifest.json` có đúng 5 khối: `files` (đường dẫn + sha256), `version`, `python_min`,
  `external_commands`, `mcp_servers`.

## 5. Ràng buộc & rủi ro

Ràng buộc kiến trúc phải giữ (chép từ `docs/kien-truc.md` — chỉ dòng việc này chạm tới):

- "File code MỚI bắt buộc nằm trong `scripts/` hoặc `hooks/`" — việc này chạm ở
  `scripts/build_portable.py` và `scripts/tdq_checkportable.py` (đúng luật). Thư mục
  `portable_*/scripts/` là **bản sao do máy sinh**, không phải code mới viết tay; phải thêm
  vào `.graphifyignore` để đồ thị không đếm trùng.
- "`skills/` chỉ được nhắc tên lệnh của `scripts/`, cấm chép nội dung script vào skill" —
  việc này chạm ở skill `tdq-checkportable`: skill chỉ gọi
  `python3 scripts/tdq_checkportable.py`, toàn bộ logic nằm trong script.
- "`hooks/` được gọi `scripts/`; `scripts/` không được import `hooks/`" — việc này chạm ở
  `build_portable.py` (đọc `hooks/hooks.json` như **dữ liệu văn bản** để rewrite biến, không
  import module hook).
- "Chỉ `scripts/tdq_state.py` được ghi `docs/tdq/state.json`" — hai script mới **không** ghi
  state, chỉ đọc nếu cần.

| Rủi ro | Ảnh hưởng | Cách giảm |
|---|---|---|
| R1 Bản sinh gãy im lặng ở máy khác | Cao — user mất niềm tin, khó debug từ xa | QC phải chạy thật: sinh vào thư mục tạm, chạy `tdq_checkportable.py` trên đó, không kiểm bằng mắt |
| R2 Rewrite biến sót một chỗ | Cao — hook gãy, mà hook gãy thì im lặng | Test riêng: grep bản sinh phải có 0 chuỗi `CLAUDE_PLUGIN_ROOT`; đồng thời đếm số chỗ thay phải khớp số chỗ nguồn |
| R3 Quyền tự setup tối đa (3B) gây hại máy user | Cao — sửa `~/.claude`, cài package | Backup trước khi sửa + log đầy đủ + không đụng secret; README nêu rõ skill này có quyền đó |
| R4 Manifest lệch sau khi sửa nguồn | Trung bình — check báo sai | Manifest sinh cùng lúc với file, không viết tay; test kiểm sha256 khớp thực tế |
| R5 `portable/` cũ bị xoá nhưng có người đang dùng | Thấp | README bản mới ghi rõ đường chuyển đổi; nội dung cũ được bản `portable_codex/` thay thế đủ |
| R6 Bản sinh mang theo state/rác của repo nguồn | Trung bình — lộ dữ liệu nội bộ | Danh sách loại trừ tường minh trong script + test kiểm bản sinh không chứa `docs/tdq/state.json`, `.git`, `graphify-out` |

## 6. QC & Definition of Done

| # | Hạng mục kiểm | Lệnh/cách kiểm | Điều kiện PASS |
|---|---|---|---|
| Q1 | Test tự động toàn bộ | `python3 -m pytest tests/ -q` | Exit 0, không test đỏ |
| Q2 | Sinh được cả hai bản | `python3 scripts/build_portable.py --dest /tmp/tdqp` | Exit 0; tồn tại `/tmp/tdqp/portable_claude` và `/tmp/tdqp/portable_codex` |
| Q3 | Không sót biến plugin | `grep -rc "CLAUDE_PLUGIN_ROOT" /tmp/tdqp/portable_claude` | Tổng số khớp = 0 |
| Q4 | Manifest khớp thực tế | `python3 scripts/tdq_checkportable.py check --root /tmp/tdqp/portable_claude` | Exit 0, báo "manifest khớp" |
| Q5 | Phát hiện được hỏng | Sửa 1 byte một file trong bản sinh rồi chạy lại Q4 | Exit khác 0, chỉ đúng tên file bị sửa |
| Q6 | Phát hiện thiếu lệnh ngoài | Chạy check với `PATH` không có `git` | Báo thiếu `git`, không crash |
| Q7 | Bản sinh không chứa rác | `find /tmp/tdqp -name state.json -o -name ".git" -o -name "graphify-out"` | Không kết quả |
| Q8 | Skill không chép logic | `grep -c "def \|import " portable_claude/.claude/skills/tdq-checkportable/SKILL.md` | 0 |
| Q9 | Bản cũ đã bỏ | `test -d portable` | Trả về false (đã xoá) |
| Q10 | Log service hoạt động | `TDQ_LOG=0 python3 scripts/build_portable.py --dest /tmp/tdqp2 2>&1 \| wc -l` so với khi bật | Bật có log timestamp, tắt thì im |

DoD: cả 10 hạng mục Q1–Q10 PASS · hai thư mục `portable_claude/` và `portable_codex/` tồn
tại trong repo và sinh lại được bằng một lệnh · `portable/` đã xoá · `tests/` có hai file
test mới đều xanh · `manifest.json` mỗi bản đủ 5 khối · README mỗi bản nêu rõ ba giới hạn
cứng (trust dialog, MCP approve, restart) và cảnh báo quyền tự setup của `tdq-checkportable`.

## 7. Câu hỏi còn mở

(rỗng)
