# PLAN — Bản portable_codex dùng đúng cơ chế native của Codex CLI

Ngày: 2026-08-17 · Spec: ../spec/2026-08-17-1139-codex-native-layers.md (bản 1.0, ĐÃ DUYỆT) · Lane: full · Trạng thái: HOÀN THÀNH
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md
Mode thực thi: main — 15/17 task dồn vào đúng 2 file (`scripts/build_portable.py`, `scripts/tdq_checkportable.py`) và P2–P4 đều phụ thuộc kết quả trinh sát của P1, nên chia song song chỉ tạo xung đột merge. (ĐỀ XUẤT, user chốt lúc duyệt)
Trạng thái plan: ĐÃ DUYỆT (spec 12:20, plan 12:27, mode `main` 12:30)

## Quy tắc thi hành (áp cho mọi task)
1. Thứ tự phase là thứ tự phụ thuộc — không đảo.
2. Mỗi task: đánh `[~]` khi bắt đầu → viết test trước (đỏ) → code → test xanh → đổi sang
   `[x]` NGAY vào file này. Trạng thái checkbox: `[ ]` chưa làm · `[~]` đang làm · `[x]` xong.
3. Sau mỗi phase: chạy toàn bộ test suite, phải xanh mới sang phase sau.
4. Lệnh nào chạm state của workflow phải có `TDQ_PROJECT_DIR=<thư mục tạm>` ngay trên chính lệnh đó.
5. QC FAIL → thêm task fix vào mục QC của file này (không cần duyệt lại), loop đến khi pass.
6. Không commit/push cho đến khi user yêu cầu.
7. **Không lệnh nào trong plan này được ghi vào `~/.codex/` thật khi đang thử nghiệm.** Mọi lần
   chạy `codex` để trinh sát/kiểm đều phải qua `CODEX_HOME=<thư mục tạm>` (T1.1 xác minh biến
   này). Ngoại lệ duy nhất là Q9 ở phase QC, và chỉ sau khi T3.x đã có test khoá phần sao lưu.

## P1 — Trinh sát bằng chạy thật (giải R2 trước khi viết bất kỳ cấu hình nào)

Lý do phase này đứng trước: hai ẩn số — cwd của tiến trình hook, và tên tool thật để viết
`matcher` — quyết định luôn nội dung `.codex/hooks.json`. Đoán rồi sửa sau chính là lỗi của
request trước.

- [x] **T1.1** (e8m) Xác minh biến `CODEX_HOME` có đổi được thư mục cấu hình của Codex không — Test: `CODEX_HOME=<tmp> codex --version` chạy được VÀ sau đó `<tmp>` có file/thư mục do codex tạo; không có thì dừng, báo user, vì mọi bước thử còn lại đều dựa vào nó
  - Ghi nhận khi làm: PASS. `codex-cli 0.147.0-alpha.6.5`; sau khi chạy, `<tmp>/tmp/` được
    chính codex tạo ra → biến có tác dụng, mọi bước thử sau chạy an toàn ngoài `~/.codex`.
- [x] **T1.2** (e15m) Viết `tests/probe_codex_hook.py` — hook thăm dò ghi nguyên payload stdin + `os.getcwd()` ra file JSON, cắm vào `<tmp>/hooks.json` cho đủ 4 event TDQ dùng — Test: chạy trực tiếp bằng `echo '{}' | python3 tests/probe_codex_hook.py` → sinh đúng 1 file JSON có khoá `cwd_process`
  - Ghi nhận khi làm: PASS, exit 0, dòng jsonl có đủ `cwd_process`/`argv`/`payload`.
    Tra thêm tài liệu hooks chính thức: `hooks.json` của Codex có **cùng khuôn** với
    `hooks/hooks.json` của repo (bọc trong khoá `hooks`, mỗi event là mảng
    `{matcher, hooks:[{type:"command", command}]}`), `matcher` là **regex khớp `tool_name`**.
    Khác tên trường: `timeout` (không phải `timeout_sec`), `statusMessage`,
    `additionalContextLimit`, `async`, `commandWindows`. Ví dụ chính thức dùng
    `$(git rev-parse --show-toplevel)` trong `command` → **command chạy qua shell**, mở đường
    giải R2 mà không cần đường dẫn tuyệt đối.
- [x] **T1.3** (e20m) Chạy `codex` thật trên một project tạm đã bật trusted trong `CODEX_HOME` tạm, thực hiện một lần sửa file + một lệnh shell — Test: file thăm dò chứa payload của cả `SessionStart`, `UserPromptSubmit`, `PreToolUse`, `Stop`; ghi lại `tool_name` thật của tool sửa file và tool chạy lệnh
  - Ghi nhận khi làm: PASS sau 4 lượt chạy thật. Chi tiết + bằng chứng ở `../qc/<slug>.md`
    mục `## Trinh sát`. Bốn phát hiện: (1) Codex gác hook bằng **trust hash** riêng, ngoài
    `trust_level`; (2) cwd tiến trình hook = gốc project; (3) `tool_name` shell = `Bash`,
    `tool_input.command` trùng Claude Code; (4) `tool_name` sửa file = `apply_patch`, và
    `tool_input` chỉ có `command` chứa patch text — **không có `file_path`**.
- [x] **T1.4** (e10m) Chốt R2 bằng số liệu T1.3: ghi vào `docs/tdq/qc/<slug>.md` mục `## Trinh sát` — cwd của tiến trình hook, tên tool thật, và kết luận `hooks.json` dùng đường dẫn tương đối hay phải sinh tại máy đích — Test: mục `## Trinh sát` tồn tại, nêu rõ một trong hai nhánh kèm output thật
  - Ghi nhận khi làm: PASS. Chốt **nhánh đường dẫn tương đối** → `.codex/hooks.json` là file
    tĩnh trong `manifest.files`, không sinh lúc `setup`. R2 đóng.
  - **Phát sinh ngoài dự kiến (T2.4 phải xử):** matcher gate sửa file đổi thành `apply_patch`,
    và `edit_gate.py` cần lớp mỏng đọc đường dẫn ra khỏi thân patch — lệch quyết định A2.

**Xong P1 khi**: biết chính xác cwd + tên tool, và đã chốt nhánh đường dẫn cho `hooks.json`.

## P2 — Sinh lớp native trong `portable_codex/`

- [x] **T2.1** (e18m) `sinh_ban_codex()` sinh `.agents/skills/<tên>/SKILL.md` cho 8 skill (kèm `references/`), frontmatter đủ `name` + `description` — Test: `tests/test_build_portable.py` mới, mỗi SKILL.md parse được frontmatter và có đủ 2 trường
  - Ghi nhận khi làm: PASS. Chép NGUYÊN cây skill sang `.agents/skills/<tên>/` (không đánh
    số lại) để liên kết `../<skill>/SKILL.md` giữa các skill còn trỏ đúng.
  - Chạm: `sinh_ban_codex` → không hàm nào gọi nó ngoài `main()` và `tests/`; `main()` nằm trong mục `## Hub` của `docs/kien-truc.md` (bậc 20) nên thêm dòng DoD hồi quy: `python3 scripts/build_portable.py --only claude` vẫn exit 0 và `portable_claude/` không đổi một byte
- [x] **T2.2** (e15m) Sinh `.codex/config.toml` chứa `[mcp_servers.<tên>]` cho 2 server, chỉ TÊN biến môi trường — Test: `tomllib.load()` ra đủ 2 server; không giá trị nào trong file khớp giá trị biến môi trường thật
  - Ghi nhận khi làm: PASS. Dùng `env_vars = ["<TÊN BIẾN>"]` chứ không `env = {X = "${X}"}`:
    Codex KHÔNG khai triển `${VAR}` trong TOML nên dạng kia truyền sang MCP đúng chuỗi 6 ký
    tự, vừa sai vừa che mất lỗi. `env_vars` chuyển tiếp biến từ môi trường cha.
  - Chạm: `sinh_mcp` (trong `tdq_checkportable.py`) → `sinh_ban_claude` cũng dùng; test phải khoá `.mcp.json` của bản claude không đổi
- [x] **T2.3** (e12m) Copy cây `hooks/` vào GỐC bundle (cạnh `scripts/`) để `_common.py` suy đúng `../../scripts` — Test: bơm payload JSON mẫu vào `python3 <bundle>/hooks/scripts/edit_gate.py` → exit 0, stdout parse được thành JSON có `hookSpecificOutput`
- [x] **T2.4** (e20m) Sinh `.codex/hooks.json` từ `hooks/hooks.json`: ánh xạ 5 hook sang 4 event Codex, `PreToolUse` có 2 matcher group, matcher lấy từ T1.3 — Test: JSON có đủ 4 event; `PreToolUse` đúng 2 group; mọi `command` trỏ tới file có thật trong bundle
  - Dùng: `WebFetch`
  - Để: đọc lại `codex-rs/hooks/src/schema.rs` chốt tên trường wire (`matcher`, `hooks`,
    `timeout_sec`) khi T1.3 cho payload không khớp mong đợi. Agent ngoài không có skill
    system: dùng lệnh curl tương đương lên `raw.githubusercontent.com/openai/codex/main/…`.
  - Ra: `portable_codex/.codex/hooks.json`
  - Kiểm: `python3 -c "import json;d=json.load(open('portable_codex/.codex/hooks.json'));print(sorted(d))"`
  - Không dùng cho: tra cứu lại phần MCP/skill/trust — ba mục đó đã xác minh CAO ở phase analyze
  - Ghi nhận khi làm: PASS, KHÔNG cần WebFetch — T1.3 đã cho payload thật nên không còn ẩn số
    về tên trường wire. Matcher chốt: `apply_patch` + `Bash`. Sinh thêm
    `hooks/scripts/codex_edit_gate.py` (adapter apply_patch → `file_path`), file này chỉ có ở
    bundle codex, `hooks/scripts/edit_gate.py` của repo giữ nguyên.
- [x] **T2.5** (e10m) Đưa toàn bộ file mới vào `manifest.json` theo nhánh đã chốt ở T1.4 — Test: `python3 scripts/tdq_checkportable.py check --root portable_codex` exit 0, in `SẠCH`, chạy dưới 5 giây

  - Ghi nhận khi làm: PASS. `check --root portable_codex` → `SẠCH 121 file khớp manifest`,
    0.027s. Không cần luật manifest riêng: file native nằm trong cây bundle nên vòng quét
    của `sinh_manifest` bắt được hết.

**Xong P2 khi**: bản sinh có đủ 4 nhóm hiện vật native và `check` báo sạch.

## P3 — `setup --trust` (quyết định 3B, lần này là mã chạy thật)

- [x] **T3.1** (e15m) Thêm cờ `--trust` cho lệnh `setup`; không có cờ thì tuyệt đối không đụng `~` — Test: chạy `setup` trần với `HOME` giả → file `~/.codex/config.toml` giả không đổi một byte
- [x] **T3.2** (e20m) Ghi block `[projects."<path>"] trust_level = "trusted"` vào `<CODEX_HOME>/config.toml`, giữ nguyên phần còn lại của file — Test: file giả có sẵn `[mcp_servers.x]` → sau khi chạy vẫn còn nguyên khối đó VÀ có thêm block projects đúng đường dẫn tuyệt đối của bundle
- [x] **T3.3** (e12m) Bắt buộc sao lưu `<file>.tdq-bak-<timestamp>` trước khi ghi, và không ghi đè block projects đã có sẵn cho cùng đường dẫn — Test: đúng 1 file `.tdq-bak-*`, nội dung cũ còn nguyên trong đó; chạy `--trust` hai lần liên tiếp không sinh block trùng
- [x] **T3.4** (e10m) `check` báo trạng thái trusted của bundle (có/chưa), không crash khi thiếu `~/.codex/config.toml` — Test: `HOME` giả rỗng → `check` vẫn exit theo đúng mã của phần file, in dòng nêu rõ chưa trusted và hậu quả

  - Ghi nhận khi làm (T3.1–T3.4): PASS, 9 test mới ở `tests/test_checkportable.py::TestTrustCodex`,
    `python3 -m pytest tests/test_checkportable.py -q` → 27 passed. Hàm mới:
    `duong_config_codex` · `da_trusted` · `bat_trusted`. `da_trusted` chỉ đọc tới đầu block
    kế tiếp nên `trust_level` của project KHÁC không bị tính nhầm. Mọi test đặt
    `CODEX_HOME=<tmp>` → `~/.codex` thật không bị đụng lần nào.

**Xong P3 khi**: 4 test trên xanh và không đường nào ghi ra `~` khi thiếu cờ `--trust`.

## P4 — Tài liệu hết giả định sai

- [x] **T4.1** (e12m) Viết lại `README_CODEX` + `AGENTS_MD` trong `build_portable.py`: nêu đủ ba lớp native, và nói thẳng hậu quả nếu project chưa trusted — Test: `grep -rn "không có skill/hook system\|hook là cơ chế riêng của Claude Code" portable_codex/ scripts/` → 0 dòng
- [x] **T4.2** (e8m) Sửa docstring module `build_portable.py` và docstring `sinh_ban_codex()` — Test: cùng lệnh grep của T4.1 vẫn 0 dòng; docstring nêu đúng mốc `Codex CLI >= 0.147.0`
- [x] **T4.3** (e8m) Cập nhật `portable_src/skills/tdq-checkportable/SKILL.md`: thêm `setup --trust`, chỉ nhắc tên lệnh, không chép nội dung script — Test: `python3 scripts/doc_lint.py` trên file đó exit 0
- [x] **T4.4** (e6m) Sửa `docs/kien-truc.md`: dòng tầng `portable/` → `portable_claude/` + `portable_codex/` — Test: `grep -n "portable" docs/kien-truc.md` không còn dòng nào nhắc thư mục `portable/` đã xoá

  - Ghi nhận khi làm (T4.1–T4.4): PASS. `grep -rn "không có skill/hook system|hook là cơ chế
    riêng của Claude Code" portable_codex/ scripts/ docs/kien-truc.md` → rỗng (rc=1).
    README/AGENTS.md nay nêu **bốn** việc thủ công (thêm bước duyệt hook trong TUI), và
    `docs/kien-truc.md` ghi đúng hai thư mục bản sinh thay cho `portable/` đã xoá.

**Xong P4 khi**: không còn câu nào trong repo mô tả sai năng lực Codex.

## P5 — Log & test bắt buộc

- [x] **T5.1** (e8m) Log service cho phần mới: mọi hành động ghi ra ngoài bundle (`--trust`) log đủ để dựng lại đã ghi gì vào file nào, timestamp, tắt bằng `TDQ_LOG=0` — Test: `TDQ_LOG=0 python3 … setup --trust` với `HOME` giả → stderr rỗng; bỏ biến đi thì stderr có dòng nêu tên file đã ghi
- [x] **T5.2** (e10m) Unit test cho từng thành phần, chạy bằng một lệnh — Test: `python3 -m pytest tests/ -q` exit 0, 0 failed
  - Ghi nhận khi làm (T5.1): PASS bằng `TestTrustCodex::test_log_tat_duoc_va_neu_ten_file_da_ghi`
    — `setup --trust` in ra stderr tên file đã ghi + block đã thêm; `TDQ_LOG=0` im hoàn toàn.
  - Ghi nhận khi làm (T5.2): `python3 -m pytest tests/ -q` → **764 passed, 375 subtests**, 0 failed.
- [x] **T5.3** (e25m) QC độc lập: giao agent kiểm lại toàn bộ Q1–Q10 mà không tin lời khai của phase implement — Test: file qc có kết luận PASS/FAIL kèm output thật cho từng hạng mục
  - Dùng: `tdq-qc-tester`
  - Để: chạy lại từng lệnh trong Definition of Done trên cây làm việc thật, tự thăm dò biên
    (bundle chỉ đọc, `HOME` rỗng, `config.toml` sẵn có nội dung), và đặc biệt kiểm Q9 bằng
    `codex` thật. Agent ngoài không có skill system: đọc `agents/tdq-qc-tester.md` rồi làm theo.
  - Ra: `docs/tdq/qc/2026-08-17-1139-codex-native-layers.md`
  - Kiểm: file qc tồn tại, đủ 10 hạng mục, mỗi hạng mục có output thật kèm PASS/FAIL
  - Không dùng cho: tự sửa mã khi FAIL — agent chỉ báo, task fix do phase implement làm
  - Ghi nhận khi làm: PASS toàn bộ, 0 khuyết tật. Agent tự thăm dò thêm 7 biên (CODEX_HOME
    không tồn tại, chạy hai lần, block projects của path khác, bundle chỉ đọc, TDQ_LOG=0…)
    và xác nhận `~/.codex` thật không bị đụng (sha256 trước/sau giống hệt). Bảng đầy đủ ở
    `../qc/2026-08-17-1139-codex-native-layers.md`.

## Definition of Done

Trỏ về §6 spec. Từng hạng mục + lệnh kiểm:

- **Q1** bộ test không đỏ — `python3 -m pytest tests/ -q`
- **Q2** 8 skill đúng chuẩn Codex — `python3 -m pytest tests/test_build_portable.py -q`
- **Q3** MCP đọc được, không lộ khoá — `python3 -c "import tomllib;d=tomllib.load(open('portable_codex/.codex/config.toml','rb'));print(sorted(d['mcp_servers']))"`
- **Q4** `hooks.json` đủ 5 hook / 4 event — `python3 -c "import json;print(sorted(json.load(open('portable_codex/.codex/hooks.json')).keys()))"`
- **Q5** hook chạy được trong bố cục bundle — bơm payload mẫu vào `portable_codex/hooks/scripts/edit_gate.py`
- **Q6** `setup --trust` ghi thật + có backup — `python3 -m pytest tests/test_checkportable.py -q`
- **Q7** bundle sạch sau khi sinh — `time python3 scripts/tdq_checkportable.py check --root portable_codex`
- **Q8** không còn giả định sai — `grep -rn "không có skill/hook system\|hook là cơ chế riêng của Claude Code" portable_codex/ scripts/ docs/kien-truc.md`
- **Q9** **Codex thật nạp được bản sinh** — chép bundle ra thư mục thử, `setup --trust`, chạy `codex`, dán output vào file qc
- **Q10** hồ sơ kiến trúc khớp thực tế — `grep -n "portable" docs/kien-truc.md`
- **Hồi quy T2.1** — `python3 scripts/build_portable.py --only claude` exit 0 và `portable_claude/` không đổi một byte

Thêm: mọi task tick `[x]`; QC độc lập bằng agent `tdq-qc-tester` PASS; report ghi rõ version
Codex CLI đã kiểm thật và mọi chỗ lệch so với spec.
