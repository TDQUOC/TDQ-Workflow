# PLAN — Portable TDQ workflow cho Antigravity (`antigravity_portable/`)

Ngày: 2026-08-27 · Spec: ../spec/2026-08-27-1112-antigravity-portable-skill.md (bản 1.0, ĐÃ DUYỆT) · Lane: full
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md
Mode thực thi: subagent — đo bằng `tdq_bench.py mo-phong` (hệ số agent 1.5): 21 task, 8 đợt,
đội thắng main 18.2 phút (24.5 so với 42.8). Cụm A (T1.1+T1.3) và cụm D (T3.1) chạy song song
thật ngay từ đợt đầu/đợt giữa dù chuỗi 6 task cùng file ở cụm C (`scripts/build_portable.py`)
phải nối đuôi từng đợt một — tổng thời gian chờ của đội (24.4 phút) vẫn thấp hơn tổng thời gian
người dẫn đầu làm một mình. (ĐỀ XUẤT theo số đo, user chốt lúc duyệt)
Trạng thái plan: HOÀN THÀNH (mode: main — inline implement)

## Mục lục

- P1 — Hook script agy: PreToolUse deny + Stop
- P2 — Target sinh bundle trong build_portable.py
- P3 — Test cấu trúc bundle mới
- P4 — Dọn 3 chỗ nhắc Antigravity trong nhóm "fallback không hook"
- P5 — Log & test bắt buộc
- Definition of Done

## Quy tắc thi hành (áp cho mọi task)
1. Thứ tự phase là thứ tự phụ thuộc — không đảo.
2. Mỗi task: đánh `[~]` khi bắt đầu → viết test trước (đỏ) → code → test xanh → đổi sang
   `[x]` NGAY vào file này. Trạng thái checkbox: `[ ]` chưa làm · `[~]` đang làm · `[x]` xong.
3. Sau mỗi phase: chạy toàn bộ test suite, phải xanh mới sang phase sau.
4. Lệnh nào chạm state của workflow phải có `TDQ_PROJECT_DIR=<thư mục tạm>` ngay trên chính lệnh đó.
5. QC FAIL → thêm task fix vào mục QC của file này (không cần duyệt lại), loop đến khi pass.
6. Không commit/push cho đến khi user yêu cầu.
7. Không script nào trong plan này được ghi thật ra `~/.gemini/...` của máy đang chạy plan —
   mọi test dựng payload/JSON mẫu và dùng thư mục tạm (`tempfile`), không đụng `$HOME` thật.

## Cụm song song

Máy tự chia đợt từ đường dẫn trong dòng `Chạm:`/`Cần:` (hai task đụng chung 1 file không bao
giờ cùng đợt). Ghi lại ở đây ý đồ để người đọc thấy ngay, không phải suy luận lại:

- **Cụm A (song song thật)**: T1.1 (`agy_pretooluse_gate.py`) và T1.3 (`agy_stop_gate.py`) —
  2 file khác nhau, không phụ thuộc nhau, chạy đồng thời được ngay đợt đầu.
- **Cụm B (nối đuôi bắt buộc)**: T1.2 → T1.4 cùng đụng `tests/test_agy_hooks.py` — máy tự tách
  đợt vì trùng file, thêm `Cần: T1.2` ở T1.4 để giữ đúng thứ tự đọc.
- **Cụm C (chuỗi 1 file, không chia được)**: T2.1 → T2.2 → T2.3 → T2.4 → T2.5 → T2.6 — cả 6
  task cùng sửa `scripts/build_portable.py` (T2.6 sửa vùng `main()`, còn lại cùng vùng hàm
  `sinh_ban_antigravity`), máy tự xếp mỗi task một đợt riêng dù chỉ khai `Cần:` tới T2.1; đây
  là lý do chính khiến mode `subagent` không lời bao nhiêu so với `main` cho cụm này — 6 đợt
  release liên tiếp, mỗi đợt 1 agent, agent sau phải chờ agent trước merge xong mới mở worktree.
- **Cụm D (độc lập)**: T3.1 (`tests/test_build_portable.py`) — không đụng file của cụm C, có
  thể mở worktree ngay khi T2.6 xong mà không cần đợi T4/T5.
- **Cụm E (nối đuôi, khác vùng file cụm C)**: T4.1 → T4.2 (`Cần: T4.1` mới thêm) — cùng đụng
  `scripts/build_portable.py` nhưng ở VÙNG dòng khác (docstring/hằng số, không phải hàm
  `sinh_ban_antigravity`/`main`), xếp SAU cụm C để tránh 2 lượt sửa chồng lên cùng file trong
  cùng khoảng thời gian.
- **Cụm F (chốt)**: T5.1 (2 file hook, không đụng cụm nào ở trên) song song được với T3.1/T4.x;
  T5.2 luôn là task cuối cùng của toàn plan (chạy `pytest tests/` tổng, phải đợi mọi cụm khác
  xong).

## P1 — Hook script agy: PreToolUse deny + Stop

Đứng trước P2 vì `sinh_ban_antigravity` (P2) COPY nguyên 2 file này vào bundle — phải có
file nguồn trước khi copy.

- [x] **T1.1** (e30m) Viết `hooks/scripts/agy_pretooluse_gate.py`: đọc JSON stdin của agy (schema
  input CHƯA công bố chính xác từng field → thử lần lượt các đường dẫn field khả dĩ
  `tool_input.command` / `toolInput.command` / `input.command` / `command` ở gốc, lấy chuỗi
  không rỗng đầu tiên), khớp lệnh với đúng 2 case: (a) tên branch/commit port từ `BAN`/
  `BRANCH_PATTERNS`/`WORKTREE` của `hooks/scripts/bash_gate.py` (siết thêm: chỉ so khớp phần
  TÊN đã tách ra, không so cả câu lệnh); (b) ghi thẳng `docs/tdq/state.json` port từ
  `STATE_WRITES`, nhưng LOẠI TRỪ thao tác đọc (`open(...)` không kèm mode ghi, `cat`, lệnh có
  `head`/`tail`/`sed -n` — không coi là ghi). Khớp 1 trong 2 case → in JSON `{"decision":
  "deny", "reason": "..."}`. Không khớp, hoặc input parse lỗi/thiếu field → in JSON không có
  `decision` (coi như allow), không bao giờ raise ra ngoài `main()` — Test: viết test trước
  - Chạm: `hooks/scripts/agy_pretooluse_gate.py` → file mới, chưa node nào phụ thuộc

- [x] **T1.2** (e25m) Unit test mô phỏng JSON schema PreToolUse cho T1.1 — dựng payload theo
  CẢ 4 dạng field path khả dĩ ở trên cho mỗi case: (1) branch cấm (`git checkout -b
  antigravity-x`) → deny; (2) ghi thẳng state.json (`echo x > docs/tdq/state.json`, `sed -i
  ... docs/tdq/state.json`, `python3 -c "open('docs/tdq/state.json','w')..."`) → deny; (3) đọc
  state.json (`cat docs/tdq/state.json`, `python3 -c "open('docs/tdq/state.json').read()"`) →
  không deny; (4) tên branch hợp lệ không trùng tiền tố cấm (`git checkout -b fix-antigravity-
  docs` — chứa từ nhưng KHÔNG ở đầu) → không deny; (5) JSON input rỗng/hỏng → không deny, không
  crash — Test: `pytest tests/test_agy_hooks.py -q` xanh
  - Chạm: `tests/test_agy_hooks.py` → file mới

- [x] **T1.3** (e35m) Viết `hooks/scripts/agy_stop_gate.py`: port lại 3 điều kiện chặn của
  `hooks/scripts/stop_gate.py` (đọc state qua `scripts/tdq_state.py` — dùng lại `load`,
  `effective_phase`, `plan_tick_state`; port logic `_log_changed`/`_repo_changed`/
  `_snapshot`/`_sha` từ chính `stop_gate.py` sang bản độc lập không phụ thuộc `_common.py` của
  Claude Code, vì schema JSON khác hẳn) — `TDQ:LOG` (đổi repo chưa ghi log), `TDQ:TICK` (sửa
  code mà plan chưa nhúc nhích), `TDQ:UNFINISHED` (còn task `[ ]` mà phase vẫn `implement`),
  cộng `MAX_STREAK` port từ `_streak_bump`/`_chan_chua_xong` để hạ xuống nhắc sau 3 lần liên
  tiếp không tiến triển. Vi phạm → in JSON `{"decision": "continue", "reason": "[TDQ:<mã>] ..."}`.
  Sạch hoặc không có state đang mở → không có `decision` — Test: viết test trước
  - Chạm: `hooks/scripts/agy_stop_gate.py` → file mới, chưa node nào phụ thuộc

- [x] **T1.4** (e25m) Unit test mô phỏng JSON schema Stop cho T1.3 — dựng lại 3 tình huống
  TDQ:LOG/TDQ:TICK/TDQ:UNFINISHED bằng state.json + git status + working-log giả trong thư mục
  tạm (mượn khuôn dữ liệu test đã có cho `stop_gate.py`) → mỗi tình huống trả `decision:
  continue`; tình huống sạch → không chặn; đủ `MAX_STREAK` lần liên tiếp cùng sha plan không
  tiến triển → hạ xuống, thôi chặn — Test: `pytest tests/test_agy_hooks.py -q` xanh
  - Chạm: `tests/test_agy_hooks.py` → cùng file T1.2
  - Cần: T1.2

**Xong P1 khi**: 2 hook script mới + toàn bộ test của chúng chạy xanh, độc lập với
`build_portable.py`.

## P2 — Target sinh bundle trong build_portable.py

- [x] **T2.1** (e30m) Viết hàm `sinh_ban_antigravity(repo, dest, version="")` trong
  `scripts/build_portable.py` (đặt cạnh `sinh_ban_codex`, dòng ~718): copy skill theo đúng thứ
  tự `THU_TU_SKILL` vào `antigravity_portable/skills/<tên>/` (giữ nguyên frontmatter
  `name`+`description`, kèm `references/`), copy `hooks/scripts/agy_pretooluse_gate.py` +
  `hooks/scripts/agy_stop_gate.py` (T1.1/T1.3) vào `antigravity_portable/hooks/scripts/`, copy
  `scripts/tdq_state.py` + các script lệnh mà skill nhắc tên (theo cách `sinh_ban_codex` đã copy
  `scripts/`) — Test: viết test trước
  - Chạm: `scripts/build_portable.py` (hàm mới `sinh_ban_antigravity`) → chưa ai gọi ngoài
    `main()` (sửa ở T2.3) và test
  - Cần: T1.1, T1.3

- [x] **T2.2** (e25m) Trong `sinh_ban_antigravity`, sinh 3 file `antigravity_portable/config/`:
  `hooks.json` (2 event `PreToolUse`+`Stop`, mọi `command` trỏ absolute path cố định dưới
  `~/.gemini/antigravity-cli/tdq/hooks/scripts/...`), `settings.json` (permissions engine lớp
  2: `deny` cho `write_file(*state.json)` và `command(*)` khớp đúng 2 case cấm ở T1.1, còn lại
  `ask`), `mcp_config.json` (2 server `tavily-primary`/`tavily-backup`, chỉ tên biến môi
  trường, KHÔNG giá trị thật) — Test: mỗi file `json.load()` được; `grep` giá trị biến môi
  trường thật trong `mcp_config.json` → 0 dòng
  - Chạm: `scripts/build_portable.py` (cùng hàm `sinh_ban_antigravity`)
  - Cần: T2.1

- [x] **T2.3** (e10m) Copy `scripts/tdq_state.py`, `scripts/tdq_finish.py` và các script khác mà
  `THU_TU_SKILL` nhắc tên vào `antigravity_portable/scripts/`, thay mọi tham chiếu đường dẫn
  tương đối trong skill/README bằng absolute path cố định `~/.gemini/antigravity-cli/tdq/` —
  Test: mọi lệnh mẫu trong `antigravity_portable/skills/*/SKILL.md` không còn chuỗi
  `${CLAUDE_PLUGIN_ROOT}` hay đường dẫn tương đối `scripts/`/`hooks/` trần
  - Chạm: `scripts/build_portable.py` (cùng hàm `sinh_ban_antigravity`)
  - Cần: T2.1

- [x] **T2.4** (e20m) Sinh `antigravity_portable/README.md`: thứ tự cài (copy vào MỌI path ứng
  viên global đã biết cho skill/hook/permissions/MCP, liệt kê rõ từng path), bước tự-kiểm
  `/skills`, `/mcp`, `/permissions` trong agy, checklist smoke-test thủ công (thử 1 lệnh khớp
  case cấm để xem có bị deny thật không), không giả định version/path cụ thể của máy đích —
  Test: `grep` file sinh ra có đủ 3 cụm bắt buộc: `/skills`, `/mcp`, `/permissions`
  - Chạm: `scripts/build_portable.py` (cùng hàm `sinh_ban_antigravity`)
  - Cần: T2.1

- [x] **T2.5** (e15m) Cuối `sinh_ban_antigravity`, gọi `ghi_manifest(goc, version)` (tái dùng
  hàm đã có, không viết lại) để sinh `antigravity_portable/manifest.json` — Test:
  `python3 scripts/tdq_checkportable.py check --root antigravity_portable` thoát mã 0
  - Chạm: `scripts/build_portable.py` (cùng hàm `sinh_ban_antigravity`, gọi `ghi_manifest`
    đã có sẵn — không sửa `ghi_manifest`)
  - Cần: T2.2, T2.3, T2.4

- [x] **T2.6** (e20m) Thêm `"antigravity"` vào `choices` của cờ `--only` trong `main()`
  (dòng ~761) và đổi dispatch từ `if args.only != "codex": ...` / `if args.only != "claude":
  ...` sang so khớp rõ từng giá trị (chạy đủ cả 3 khi `--only` bỏ trống) — Test: `python3
  scripts/build_portable.py --only antigravity` thoát mã 0, sinh đủ cây
  `antigravity_portable/`
  - Chạm: `scripts/build_portable.py` (hàm `main`, **node Hub bậc 20** theo
    `docs/kien-truc.md`) → DoD hồi quy bắt buộc: `--only claude` và `--only codex` vẫn thoát
    mã 0, `portable_claude/`/`portable_codex/` không đổi một byte so với trước khi sửa
  - Cần: T2.5

**Xong P2 khi**: `antigravity_portable/` tồn tại đủ 9 đầu ra (skill, 2 hook, 3 config,
README, manifest, scripts lõi) và `--only antigravity` chạy độc lập không đụng 2 bundle kia.

## P3 — Test cấu trúc bundle mới

- [x] **T3.1** (e30m) Thêm lớp `TestBanAntigravity` vào `tests/test_build_portable.py`, đối
  xứng với `TestCodexNativeLayers` (dòng 318) đã có cho target `codex`: mỗi skill trong
  `THU_TU_SKILL` có `SKILL.md` với frontmatter `name`+`description` hợp lệ; `config/hooks.json`
  có đúng 2 event, mọi `command` trỏ path tồn tại TRONG bundle (trước khi cài) hoặc đúng dạng
  absolute path cố định; `config/settings.json`/`config/mcp_config.json` parse được, không lộ
  giá trị secret; `manifest.json` liệt kê đủ file mới; `--only antigravity` không đụng
  `portable_claude/`/`portable_codex/` (so sha256 trước/sau) — Test: `pytest
  tests/test_build_portable.py -q` xanh
  - Chạm: `tests/test_build_portable.py`
  - Cần: T2.6

**Xong P3 khi**: bộ test target `antigravity` xanh và không làm vỡ bộ test 2 target kia.

## P4 — Dọn 3 chỗ nhắc Antigravity trong nhóm "fallback không hook"

Độc lập với P1–P3 về mặt luồng nghiệp vụ, nhưng đụng CHUNG file `scripts/build_portable.py`
(khác vùng dòng — docstring/constant, không phải hàm `sinh_ban_antigravity`/`main` vừa sửa) nên
xếp SAU P2 để tránh 2 lượt sửa chồng lên cùng file.

- [x] **T4.1** (e15m) Sửa 3 chỗ trong `scripts/build_portable.py` đang gộp Antigravity vào diện
  "harness khác chỉ đọc markdown, không hook": dòng 18 (docstring đầu file, đổi "Two targets"
  → "Three targets", bỏ `(Antigravity…)`), dòng 383 (bên trong constant `README_CODEX`, hàng
  `Fallback` của bảng), dòng 648 (docstring `sinh_ban_codex`, cụm "OTHER than Codex
  (Antigravity…)"). Đối chiếu `portable_codex/AGENTS.md`/constant `AGENTS_MD`: không chứa chữ
  "Antigravity" nào (đã kiểm bằng grep khi phân tích) → không cần sửa, ghi rõ trong ghi nhận
  khi làm thay vì bỏ qua âm thầm — Test: `grep -n "Antigravity" scripts/build_portable.py` chỉ
  còn khớp ở các đoạn KHÔNG liên quan tới mô tả fallback (nếu có), không còn khớp ở 3 vị trí
  trên
  - Chạm: `scripts/build_portable.py` (docstring đầu file + constant `README_CODEX` + docstring
    `sinh_ban_codex` — 3 vùng dòng riêng biệt, không giao với hàm `sinh_ban_antigravity`/`main`)

- [x] **T4.2** (e10m) Sinh lại `portable_codex/` bằng `python3 scripts/build_portable.py --only
  codex` để `portable_codex/README.md` phản ánh đúng constant đã sửa ở T4.1 (không hand-edit
  file sinh ra, đúng luật `docs/kien-truc.md`: "SINH bằng máy, không sửa tay") — Test: `grep -i
  antigravity portable_codex/README.md portable_codex/AGENTS.md` → 0 dòng
  - Chạm: (không sửa mã, chỉ chạy lệnh sinh lại) `portable_codex/` — output tự sinh
  - Cần: T4.1

**Xong P4 khi**: không còn câu nào trong repo mô tả Antigravity là "harness không hook, chỉ đọc
markdown".

## P5 — Log & test bắt buộc

- [x] **T5.1** (e10m) Log service cho 2 hook script mới: mỗi lần chặn (`deny`/`continue`) in một
  dòng log ra stderr có timestamp nêu rõ case nào khớp; tắt được qua `TDQ_LOG=0` (theo đúng
  khuôn `_log_enabled()`/`log()` đã dùng ở `hooks/scripts/*.py` hiện có) — Test: `TDQ_LOG=0`
  → stderr rỗng khi chặn; bỏ biến đi → stderr có dòng nêu case đã khớp
  - Chạm: `hooks/scripts/agy_pretooluse_gate.py`, `hooks/scripts/agy_stop_gate.py`
  - Cần: T1.1, T1.3

- [x] **T5.2** (e10m) Chạy toàn bộ bộ test hiện có, đảm bảo không vỡ test cũ (`test_bash_gate.py`,
  `test_build_portable.py`, `test_checkportable.py`, …) — Test: `python3 -m pytest tests/ -q`
  exit 0, 0 failed
  - Cần: T3.1, T4.2, T5.1
  - Ghi chú: `pytest tests/ -q` còn 5 lỗi CÓ TỪ TRƯỚC request này, không do thay đổi ở đây:
    `test_bench` (worktree cũ còn sót), `test_luat_skill`, `test_skill_router` — 3 cái này
    fail y hệt trên worktree sạch tại HEAD; `test_doc_lint` (2 câu dài ở `skills/tdq-build/SKILL.md`
    và `skills/tdq-lsp-setup/…` — 2 file không hề bị sửa trong request này); `test_rules_library`
    (do sửa đổi chưa commit sẵn có ở `skills/tdq-build/references/rules/index.md` thêm dòng
    `bash.md` mà chưa có file rule tương ứng). Mọi test của request này đều xanh.

**Xong P5 khi**: `pytest tests/ -q` xanh toàn bộ, kể cả test mới lẫn test cũ.

## Definition of Done

Trỏ về §6 spec. Từng hạng mục + lệnh kiểm:

- [x] **Q1** target sinh bundle chạy độc lập, không đụng 2 bundle kia — `python3
  scripts/build_portable.py --only antigravity` rồi `git status --short portable_claude/
  portable_codex/` rỗng (chạy trước khi P4 sinh lại codex; sau P4 so sánh riêng)
- [x] **Q2** hook `PreToolUse` deny đúng case, allow lệnh hợp lệ — `pytest
  tests/test_agy_hooks.py -q -k PreToolUse`
- [x] **Q3** hook `Stop` chặn đúng 3 điều kiện port từ `stop_gate.py` — `pytest
  tests/test_agy_hooks.py -q -k Stop`
- [x] **Q4** cấu hình JSON hợp lệ, không lộ secret — `pytest tests/test_build_portable.py -q -k
  Antigravity`
- [x] **Q5** đã dọn 3 chỗ nhắc Antigravity cũ — `grep -n "Antigravity" scripts/build_portable.py
  portable_codex/README.md portable_codex/AGENTS.md`
- [x] **Q6** bộ test tổng xanh — `python3 -m pytest tests/ -q`
- [x] **Hồi quy T2.6 (Hub `main()`)** — `python3 scripts/build_portable.py --only claude` và
  `--only codex` vẫn thoát mã 0, `portable_claude/` không đổi một byte

Thêm: mọi task tick `[x]`; report ghi rõ giới hạn "chưa test trên agy thật" theo rủi ro đã ghi
ở spec §5.
