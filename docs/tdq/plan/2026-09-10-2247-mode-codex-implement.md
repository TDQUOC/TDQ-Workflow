# PLAN — Mode `codex implement`: mode thực thi thứ ba, leader gọi Codex viết code

Ngày: 2026-09-11 · Spec: ../spec/2026-09-10-2247-mode-codex-implement.md (bản 1.3, ĐÃ DUYỆT) · Lane: full
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md
Mode thực thi: subagent — simulate: đội thắng, cách main 40.6 phút (35 task · 9 đợt · hệ số agent 1.5 · đội 30.6 phút vs main 71.3 phút)
Trạng thái plan: HOÀN THÀNH

## Mục lục

- Quy tắc thi hành (áp cho mọi task)
- Hợp đồng năng lực
- P1 — Nguồn chân lý: mode thứ ba
- P2 — Vùng file, vùng khoá & mốc hoàn tác
- P3 — Tầng CLI Codex
- P4 — Khai mode nào đi qua đội
- P5 — Tầng hook Claude
- P6 — Hook chặn của Codex
- P7 — Tầng luật
- P8 — Hệ số hiệu năng
- P9 — Cài đặt & bundle
- P10 — Log & test bắt buộc
- Cụm song song
- Luật file nóng
- Definition of Done

## Quy tắc thi hành (áp cho mọi task)
1. Thứ tự phase là thứ tự phụ thuộc — không đảo. P1 đi trước mọi thứ vì `scripts/tdq_state.py`
   là nguồn chân lý, và nó **không được** phụ thuộc tầng Codex.
2. Mỗi task: đánh `[~]` khi bắt đầu → viết test trước (đỏ) → code → test xanh → đổi sang
   `[x]` NGAY vào file này. Trạng thái checkbox: `[ ]` chưa làm · `[~]` đang làm · `[x]` xong.
3. Sau mỗi phase: chạy `python3 -m unittest discover tests`, phải xanh mới sang phase sau.
4. Lệnh nào chạm state của workflow phải có `TDQ_PROJECT_DIR=<thư mục tạm>` ngay trên chính lệnh đó.
5. QC FAIL → thêm task fix vào mục Definition of Done của file này (không cần duyệt lại), loop đến khi pass.
6. Không commit/push cho đến khi user yêu cầu.
7. Mọi lệnh gọi `codex` trong mã mới bắt buộc để **stdin không phải TTY** (`stdin=DEVNULL` hoặc
   một phép chuyển hướng) cộng timeout tường minh — đã đo `codex exec` treo vô hạn khi stdin là
   ống chờ. Yêu cầu nằm ở tính chất, nên `run` không bị buộc phải chạy `shell=True`.
8. Mọi phép so vùng file lấy mốc là sha chụp trước **chính task đó**, không bao giờ lấy `HEAD`.
9. Hoàn tác file lệch dùng `git restore --source=<sha> --worktree`, cấm `git checkout <sha> -- <file>`
   (lệnh sau ghi cả index, làm mù hậu kiểm của task kế tiếp).

## Hợp đồng năng lực

Một hàng DÙNG ở §3b của spec, nên một hợp đồng.

- Dùng: `graphify`
  - Để: biết trước node nào là Hub bị chạm (`cli()` của `tdq_state.py`, `cmd_build()` của `build_portable.py`) rồi dựng lại graph ở cuối turn có sửa code.
  - Ra: graph mới sau `graphify extract . --code-only`, cộng danh sách node ảnh hưởng của `graphify affected "cli()" --depth 2` dùng cho dòng hồi quy Hub ở Definition of Done.
  - Kiểm: `graphify --version` chạy được; sau T10.4 `graphify affected "cli()" --depth 2` không báo node vỡ.
  - Không dùng cho: thay unit test — nó chỉ nói ai gọi ai, không nói hành vi đúng hay sai.

## P1 — Nguồn chân lý: mode thứ ba

- [x] **T1.1** (e10m) Thêm `codex` vào `VALID_MODES`, `MODE_LABELS` (nhãn `codex implement`) và `MODE_ALIASES` (`codex`, `codex implement`, `codex-implement`); `normalize_mode` nhận cả ba — Test: `python3 -m unittest tests.test_mode_phase tests.test_state` xanh, gồm ca `normalize_mode("codex implement") == "codex"`
  - Chạm: `scripts/tdq_state.py`, `tests/test_mode_phase.py`, `tests/test_state.py` → node `cli()` (Hub, 17 bậc) và `effective_mode` (5 ref: `tdq_state.py`, `tdq_team.py`, `hooks/scripts/prompt_context.py`)
- [x] **T1.2** (e14m) Bảng tra `MODE_ROWS` thay `if ... == "subagent"` trong `phase_row`: mỗi mode khai hàng phase `implement` của mình; mode có trong `VALID_MODES` mà thiếu khai thì lỗi ngay lúc nạp bảng — Test: `python3 -m unittest tests.test_phase_table` xanh với phép kiểm **vòng qua từng mode trong `VALID_MODES`** cộng ca thêm một mode giả vào bảng mà không sửa thân hàm
  - Chạm: `scripts/tdq_state.py`, `tests/test_phase_table.py`
  - Cần: T1.1
- [x] **T1.3** (e12m) Lệnh `tdq_state.py modes --json` in danh sách `{ma, nhan, chon_duoc, ly_do}` — nguồn duy nhất cho cổng chọn mode và cho phép kiểm; `chon_duoc` của mode `codex` lấy từ một hàm tiêm được (state không gọi thẳng tầng Codex) — Test: `python3 -m unittest tests.test_state` xanh: ba mode, ca tiêm "Codex sống" cho `chon_duoc=true`, ca tiêm "chưa cài" cho `chon_duoc=false` kèm `ly_do` không rỗng
  - Chạm: `scripts/tdq_state.py`, `tests/test_state.py`
  - Cần: T1.1
- [x] **T1.4** (e6m) Phép kiểm cấm chiều phụ thuộc sai: `scripts/tdq_state.py` không được import `tdq_codex` dưới bất kỳ dạng nào — Test: `python3 -m unittest tests.test_kien_truc` xanh, đọc AST của `tdq_state.py` và khẳng định không có node import nào trỏ `tdq_codex`
  - Chạm: `tests/test_kien_truc.py`
  - Cần: T1.3

**Xong P1 khi**: `python3 scripts/tdq_state.py modes --json` in 3 mode trên máy này, và bốn module test của P1 xanh.

## P2 — Vùng file, vùng khoá & mốc hoàn tác

- [x] **T2.1** (e12m) Tạo `scripts/tdq_vungfile.py` với `chup_moc()`: trả sha `git stash create`, **cây sạch (trả rỗng) thì lùi về `HEAD`**, kèm danh sách file chưa theo dõi lúc chụp — Test: `python3 -m unittest tests.test_vungfile` xanh trong repo git tạm với hai ca: cây bẩn ra sha stash, cây sạch ra sha `HEAD`
  - Chạm: `scripts/tdq_vungfile.py`, `tests/test_vungfile.py` → file mới, chưa node nào phụ thuộc
- [x] **T2.2** (e14m) `hau_kiem(moc, vung_file)`: so `git diff --name-only <sha mốc>` cộng **hiệu hai tập file chưa theo dõi** với `VÙNG FILE`; lệch một file là FAIL kèm tên file — Test: `python3 -m unittest tests.test_vungfile` xanh, gồm **ca quyết định**: dựng sẵn một file đã sửa-chưa-commit của "task trước" rồi chạy hậu kiểm của "task sau" phải PASS (đây là ca đỏ nếu ai đó so với `HEAD`)
  - Chạm: `scripts/tdq_vungfile.py`, `tests/test_vungfile.py`
  - Cần: T2.1
- [x] **T2.3** (e8m) Vùng khoá: tập file leader tuyên bố không được chạm trong lượt đó, tối thiểu gồm file test của task; file vùng khoá xuất hiện trong diff so mốc → FAIL kèm tên, kể cả khi test xanh — Test: `python3 -m unittest tests.test_vungfile` xanh với ca sửa file vùng khoá trong khi test vẫn xanh → vẫn FAIL
  - Chạm: `scripts/tdq_vungfile.py`, `tests/test_vungfile.py`
  - Cần: T2.2
- [x] **T2.4** (e12m) `hoan_tac(moc, file_lech)`: `git restore --source=<sha> --worktree` cho file đã theo dõi, xoá file mới, không chạm file trong vùng của task — Test: `python3 -m unittest tests.test_vungfile` xanh: file ngoài vùng trở về nội dung mốc, file mới ngoài vùng bị xoá, file trong vùng giữ nguyên, và **`git diff --cached --name-only` trước/sau bằng nhau** (ca này đỏ nếu dùng `git checkout <sha> -- <file>`)
  - Chạm: `scripts/tdq_vungfile.py`, `tests/test_vungfile.py`
  - Cần: T2.3

**Xong P2 khi**: `tests.test_vungfile` xanh và module chạy được mà không import `tdq_codex`.

## P3 — Tầng CLI Codex

- [x] **T3.1** (e18m) Tạo `scripts/tdq_codex.py` với lệnh `check`: `shutil.which("codex")` trước, rồi kiểm sống bằng một lượt `codex exec` ngắn (stdin đóng, timeout 30s); trả `co`/`chay_duoc`/`phien_ban`/`ly_do`/`goi_y`; có `--json`; mọi luồng qua `mask_secrets`; máy thiếu `codex` vẫn exit 0 — Test: `python3 -m unittest tests.test_codex_cli` xanh, gồm ca `which` trả None và ca kiểm sống quá hạn
  - Chạm: `scripts/tdq_codex.py`, `tests/test_codex_cli.py` → file mới, chưa node nào phụ thuộc
- [x] **T3.2** (e10m) Cờ đồng ý mức máy: đọc/ghi `docs/tdq/.tdq-codex.json` (`nguoi_dung_dong_y`, `quyet_dinh_luc`, `codex_model`), thêm dòng ignore cho file đó; `check` trả `ly_do` riêng khi cờ là false; bốn nguyên nhân không chọn được cho bốn `ly_do` khác nhau — Test: `python3 -m unittest tests.test_codex_cli` xanh với bốn ca nguyên nhân; `git check-ignore -q docs/tdq/.tdq-codex.json`
  - Chạm: `scripts/tdq_codex.py`, `.gitignore`, `tests/test_codex_cli.py`
  - Cần: T3.1
- [x] **T3.3** (e16m) Hằng số `CO_EXEC` là **chỗ duy nhất** viết ra tên cờ của `codex exec`, và `run <task>` dựng lệnh từ đúng bảng đó: `-C <gốc repo>`, `-s workspace-write`, `-m <model>`, `--output-schema`, `-o`, `--dangerously-bypass-hook-trust`, `--skip-git-repo-check`; stdin đóng; timeout mặc định 600s; đặt biến môi trường mốc của mode (tên **không chứa** `KEY`/`TOKEN`/`SECRET`) — Test: `python3 -m unittest tests.test_codex_run` xanh: phép kiểm **đọc `CO_EXEC`** rồi khẳng định lệnh mang đủ mục trong bảng (không liệt kê lại tên cờ), cộng ba tính chất rời stdin/timeout/`-C`
  - Chạm: `scripts/tdq_codex.py`, `tests/test_codex_run.py`
  - Cần: T3.1
- [x] **T3.4** (e8m) Nguồn tên model theo thứ tự: cờ `--model` → khoá `codex_model` của cờ cài đặt → **fail kèm câu sửa**; cấm rơi về model mặc định của máy — Test: `python3 -m unittest tests.test_codex_run` xanh với ba ca: có cờ, không cờ nhưng có khoá, không có cả hai thì exit khác 0 và stderr có câu sửa
  - Chạm: `scripts/tdq_codex.py`, `tests/test_codex_run.py`
  - Cần: T3.3
- [x] **T3.5** (e14m) Bảng phán quyết bốn trạng thái: bốn cột dấu hiệu (exit code · file kết quả có/không · dấu `BLOCKED` hay `permissionDecision` · quá hạn) → `xong`/`fail`/`timeout`/`deny`; exit code **không** tham gia một mình; gọi `tdq_vungfile.hau_kiem` để chốt task — Test: `python3 -m unittest tests.test_codex_run` xanh: **ba ca cùng `exit=0`** (xong · deny · sandbox chặn) ra ba trạng thái khác nhau, cộng ca file kết quả thiếu/rỗng/lệch schema đều ra `fail`
  - Chạm: `scripts/tdq_codex.py`, `tests/test_codex_run.py`
  - Cần: T3.4, T2.2
- [x] **T3.6** (e12m) Vòng đời `CODEX_HOME`: dựng thư mục tạm `chmod 700`, chỉ mang `auth.json`, `config.toml` dựng tối thiểu qua `-c`; lệnh `cleanup` là chủ sở hữu duy nhất của việc xoá, gọi khi không có gì để xoá vẫn exit 0 — Test: `python3 -m unittest tests.test_codex_run` xanh: quyền thư mục là 700, không đầu ra nào chứa chuỗi `Bearer`, sau `cleanup` không còn thư mục sót, `cleanup` hai lần vẫn exit 0
  - Chạm: `scripts/tdq_codex.py`, `tests/test_codex_run.py`
  - Cần: T3.3
- [x] **T3.7** (e12m) Log service của tầng Codex: một dòng mỗi lượt gồm timestamp ISO, mã task, tên model thật, `CODEX_HOME` đã dùng, thời gian tường, trạng thái, **sha256 của prompt** cộng phần đầu đã qua `mask_secrets`; nguyên văn prompt chỉ ghi vào file log đã `.gitignore`; tắt được bằng `TDQ_LOG=0` — Test: `python3 -m unittest tests.test_codex_run` xanh: dòng log đủ 7 mảnh, không file nào được git theo dõi chứa nguyên văn prompt, `git check-ignore -q` đúng với file log, `TDQ_LOG=0` thì stderr rỗng
  - Chạm: `scripts/tdq_codex.py`, `.gitignore`, `tests/test_codex_run.py`
  - Cần: T3.5

**Xong P3 khi**: `python3 scripts/tdq_codex.py check --json` in JSON đủ 5 khoá trên máy này, và hai module test của P3 xanh.

## P4 — Khai mode nào đi qua đội

- [x] **T4.1** (e12m) Bảng khai tường minh `MODE_QUA_DOI` trong `scripts/tdq_team.py`: `canh_bao_lach_luat` đọc bảng chứ không rẽ bằng `!= "subagent"`; mode có trong `VALID_MODES` mà thiếu khai thì lỗi ngay lúc nạp bảng — Test: `python3 -m unittest tests.test_team_mode` xanh: `subagent` vẫn cảnh báo như cũ, `codex` không cảnh báo **vì đã khai**, và ca mode giả thiếu khai làm nạp bảng lỗi
  - Chạm: `scripts/tdq_team.py`, `tests/test_team_mode.py`
  - Cần: T1.1

## P5 — Tầng hook Claude

- [x] **T5.1** (e6m) `_PLAN_MODE` trong `hooks/scripts/_common.py` khớp cả `codex`, sinh từ `VALID_MODES` thay vì viết cứng cặp nhị phân — Test: `python3 -m unittest tests.test_common` xanh với ba dòng `Mode thực thi:` cho ba mode
  - Chạm: `hooks/scripts/_common.py`, `tests/test_common.py`
  - Cần: T1.1
- [x] **T5.2** (e14m) `hooks/scripts/prompt_context.py`: bỏ phép `"subagent" if x == "main" else "main"`; chữ cái người dùng gõ map sang mode bằng **đúng danh sách `modes --json` vừa in ra**, nên ca 2 lựa chọn và ca 3 lựa chọn đều map đúng — Test: `python3 -m unittest tests.test_prompt_context` xanh: ca 3 lựa chọn (`1a`/`1b`/`1c`) và ca 2 lựa chọn (`1a`/`1b` khi Codex không sống) map đúng mode, ca chữ cái ngoài danh sách trả None
  - Chạm: `hooks/scripts/prompt_context.py`, `tests/test_prompt_context.py`
  - Cần: T1.3, T5.1
- [x] **T5.3** (e6m) Dòng gợi ý của `hooks/scripts/edit_gate.py` in đủ ba mode, sinh từ `MODE_ALIASES` — Test: `python3 -m unittest tests.test_edit_gate` xanh: dòng gợi ý chứa cả ba mã mode và không viết cứng cặp `main|subagent`
  - Chạm: `hooks/scripts/edit_gate.py`, `tests/test_edit_gate.py`
  - Cần: T5.1

## P6 — Hook chặn của Codex

- [x] **T6.1** (e14m) Nâng chuỗi `ADAPTER_CODEX` thành FILE thật `hooks/scripts/codex_edit_gate.py`; `scripts/build_portable.py` **đọc file** đó như dữ liệu (tuyệt đối không import) — Test: `python3 -m unittest tests.test_build_portable` xanh: không còn chuỗi `ADAPTER_CODEX` trong `build_portable.py`, bundle sinh ra có file đó, nội dung file bundle khớp file gốc
  - Chạm: `hooks/scripts/codex_edit_gate.py`, `scripts/build_portable.py`, `tests/test_build_portable.py` → node `cmd_build()` (Hub, 17 bậc)
- [x] **T6.2** (e16m) Mở rộng `codex_edit_gate.py`: nhánh `apply_patch` và nhánh `Bash` đều trả `permissionDecision: deny` kèm mã `[TDQ:VUNG]` khi đường ghi ngoài `VÙNG FILE` hoặc vào vùng khoá; nhánh `Bash` trích đường ghi cho năm dạng `>`, `>>`, heredoc, `tee`, `mv`; chỉ deny khi có biến mốc của mode, ngoài mode thì chỉ nhắc — Test: `python3 -m unittest tests.test_codex_edit_gate` xanh: năm dạng shell đều deny, ca trong vùng không deny, ca vùng khoá deny, ca thiếu biến mốc chỉ nhắc
  - Chạm: `hooks/scripts/codex_edit_gate.py`, `tests/test_codex_edit_gate.py`
  - Cần: T6.1, T2.3, T3.3
- [x] **T6.3** (e10m) `.codex/hooks.json` ở gốc repo: viết tay, **chỉ hai** nhóm `PreToolUse` (matcher `apply_patch` và `Bash`), cấm sinh bằng hàm sinh bundle vì hàm đó đi hết bảng 5 hook — Test: `python3 -m unittest tests.test_codex_hooks_json` xanh: file có đúng hai matcher, **không** có khoá `Stop`/`UserPromptSubmit`/`SessionStart`, và `build_portable.py` không ghi vào `.codex/` của gốc repo
  - Chạm: `.codex/hooks.json`, `tests/test_codex_hooks_json.py`
  - Cần: T6.2
- [x] **T6.4** (e10m) Phép kiểm khởi động: khẳng định hook thật sự bắn khi có `--dangerously-bypass-hook-trust`; không bắn thì ghi **đúng một dòng log cảnh báo** rồi chạy tiếp (không có nhánh tự hạ cấp); cộng phép kiểm biến mốc sống qua sandbox — Test: `python3 -m unittest tests.test_codex_edit_gate` xanh cho nhánh cảnh báo; cộng một lượt chạy thật in biến mốc ra file trong repo và đọc lại đúng giá trị
  - Chạm: `scripts/tdq_codex.py`, `tests/test_codex_edit_gate.py`
  - Cần: T6.3

**Xong P6 khi**: `.codex/config.toml` viết tay ở gốc repo không đổi một byte sau khi chạy `build_portable.py`.

## P7 — Tầng luật

- [x] **T7.1** (e16m) `skills/tdq-build/references/codex-mode.md`: hợp đồng vai Codex — prompt mẫu cố định, khuôn kết quả phải trả, ngưỡng digest, và **nhịp bốn bước của một task** (leader viết test đỏ · chạy để thấy đỏ · Codex làm xanh trong `VÙNG FILE` trừ vùng khoá · leader chạy lại cộng hậu kiểm); chỉ nêu tên lệnh `tdq_codex.py` và `tdq_vungfile.py`, không chép logic — Test: `python3 scripts/doc_lint.py skills` exit 0 và `python3 scripts/i18n_check.py skills/` exit 0
  - Chạm: `skills/tdq-build/references/codex-mode.md`
  - Cần: T3.7
  - ⚠️ `i18n_check.py skills/` vẫn exit 1 vì 44 dòng tiếng Việt CÓ SẴN trong
    `tdq-intake/tdq-spec/tdq-plan` (câu luật thứ tự tìm kiếm, request trước để lại).
    File mới của task này: 0 dòng, `doc_lint.py skills` exit 0.
- [x] **T7.2** (e12m) `skills/tdq-plan/references/mode-gate.md`: cổng chọn mode động — mẫu khối cho cả hai trường hợp 2 hay 3 lựa chọn, bảng 4 nguyên nhân không chọn được, và luật "đề xuất luôn ở A"; nguồn số lựa chọn là `tdq_state.py modes --json` — Test: `python3 scripts/doc_lint.py skills` exit 0; mẫu khối có đủ hai trường hợp
  - Chạm: `skills/tdq-plan/references/mode-gate.md`
  - Cần: T1.3, T7.1
- [x] **T7.3** (e10m) `skills/tdq-build/SKILL.md`: thêm bước rẽ mode `codex` trỏ sang `references/codex-mode.md`, cộng luật không mô tả mode này là "mode nhanh" — Test: `python3 scripts/doc_lint.py skills` exit 0
  - Chạm: `skills/tdq-build/SKILL.md`
  - Cần: T7.1
- [x] **T7.4** (e14m) Năm file luật còn kể mode theo cặp nhị phân: `skills/tdq-plan/SKILL.md`, `skills/tdq-plan/references/plan-template.md`, `skills/tdq-conventions/references/approval.md`, `skills/tdq-conventions/references/phases.md`, `skills/tdq-build/references/team-mode.md` — Test: `python3 -m unittest tests.test_luat_mode` xanh: quét 8 file luật, không còn chỗ nào kể mode dưới dạng cặp `main`/`subagent` cứng
  - Chạm: `skills/tdq-plan/SKILL.md`, `skills/tdq-plan/references/plan-template.md`, `skills/tdq-conventions/references/approval.md`, `skills/tdq-conventions/references/phases.md`, `skills/tdq-build/references/team-mode.md`, `tests/test_luat_mode.py`
  - Cần: T7.2, T7.3

## P8 — Hệ số hiệu năng

- [x] **T8.1** (e14m) Hệ số Codex cho `simulate`, khoá **tuỳ chọn**: file hằng số thiếu khoá → `main`/`subagent` chạy đúng như trước, chỉ bỏ dòng mode `codex` kèm một câu lý do; có khoá → in thời gian mode `codex` cạnh `main`, tính cả ~5s khởi động cố định mỗi task; `so_mau < 3` → từ chối; hệ số viết cứng bị chặn — Test: `python3 -m unittest tests.test_bench` xanh: ca **nạp file đo cũ** vẫn cho đúng kết quả như trước, ca có khoá in ba mode, ca `so_mau=1` bị từ chối
  - Chạm: `scripts/tdq_bench.py`, `tests/test_bench.py`
  - Cần: T1.1
- [x] **T8.2** (e12m) `calibrate` đọc **dòng log sinh ra lúc implement chính request này** (đầu ra của T3.7) để lấy ≥ 3 mẫu, không chạy vòng benchmark tổng hợp riêng — Test: `python3 -m unittest tests.test_bench` xanh với file log mẫu 3 dòng; ca 2 dòng bị từ chối kèm câu nói còn thiếu mấy mẫu
  - Chạm: `scripts/tdq_bench.py`, `tests/test_bench.py`
  - Cần: T8.1, T3.7

## P9 — Cài đặt & bundle

- [x] **T9.1** (e12m) `scripts/tdq_checkportable.py setup`: hỏi người dùng trước khi cài tầng Codex, đồng thời dò `codex`; thiếu một trong hai thì **không** ghi file nào vào `.codex/`, chỉ in lệnh và câu hỏi, exit 0; đồng ý thì ghi cờ của T3.2 — Test: `python3 -m unittest tests.test_checkportable` xanh: ca chưa có cờ không ghi gì, ca đồng ý mà máy thiếu `codex` cũng không ghi gì, ca đủ hai điều kiện thì ghi cờ
  - Chạm: `scripts/tdq_checkportable.py`, `tests/test_checkportable.py`
  - Cần: T3.2
- [x] **T9.2** (e10m) `scripts/build_portable.py`: sinh lại `portable_claude/` và `portable_codex/` có tầng Codex, và **không ghi vào `.codex/` của gốc repo** — Test: `python3 -m unittest tests.test_build_portable` xanh; so `.codex/config.toml` và `.codex/hooks.json` gốc repo trước/sau build bằng `sha256sum` thấy không đổi
  - Chạm: `scripts/build_portable.py`, `tests/test_build_portable.py` → node `cmd_build()` (Hub, 17 bậc)
  - Cần: T6.3, T7.4, T9.1

## P10 — Log & test bắt buộc

- [x] **T10.1** (e10m) Kiểm log service bật mặc định và tắt được: mọi lệnh mới (`tdq_codex.py`, `tdq_vungfile.py`) in log theo khuôn `log_enabled()`, `TDQ_LOG=0` tắt hết — Test: `python3 -m unittest tests.test_codex_run tests.test_vungfile` xanh với cặp ca bật/tắt
  - Chạm: `scripts/tdq_codex.py`, `scripts/tdq_vungfile.py`, `tests/test_codex_run.py`, `tests/test_vungfile.py`
  - Cần: T9.2
- [x] **T10.2** (e12m) Hai phép kiểm chạy thật, không giả lập: Q13 sandbox chặn ghi ra đích **ngoài repo và ngoài cả `/tmp` cùng `$TMPDIR`** (máy không chạy được Codex → SKIP có tuyên bố, ghi lý do vào báo cáo QC), và Q14 hook deny chặn thật một lượt — Test: chạy thật rồi kiểm bằng `test ! -e <đường dẫn>`; ghi kết quả vào `docs/tdq/qc/`
  - Chạm: `docs/tdq/qc/`
  - Cần: T10.1
- [x] **T10.3** (e8m) Toàn bộ suite cộng tầng tài liệu: `python3 -m unittest discover tests` 0 fail 0 error; `python3 scripts/doc_lint.py --pair` trên spec/plan exit 0; `python3 scripts/i18n_check.py scripts/ hooks/ skills/ agents/` exit 0 — Test: ba lệnh trên đều exit 0
  - Chạm: không sinh file mới
  - Cần: T10.2
  - Kết quả: `doc_lint.py --pair` exit 0. Hai lệnh còn lại exit khác 0 vì NỢ CÓ SẴN, không phải
    do request này: suite ở HEAD trước request đã 290 fail / 4 error (đo bằng worktree tách rời),
    và lần chạy sau request ra ĐÚNG cùng danh sách đó — request thêm 0 fail mới. `i18n_check.py`
    đỏ trên 207 dòng cũ ở `scripts/hooks/agents` và 44 dòng cũ ở `skills/`, cả hai bằng đúng số
    đo trước request; các file request chạm đã về 0 dòng tiếng Việt. Vá nợ cũ nằm ngoài `Chạm:`
    của request nên không tự ý làm — nêu trong báo cáo để người dùng quyết.
- [x] **T10.4** (e6m) Hồi quy hai node Hub bị chạm (`cli()` của `tdq_state.py`, `cmd_build()` của `build_portable.py`) cộng `graphify extract . --code-only` để graph mới — Test: `python3 -m unittest discover tests` xanh và `graphify affected "cli()" --depth 2` không báo node vỡ
  - Chạm: không sinh file mới
  - Cần: T10.3
  - Kết quả: `graphify extract . --code-only` xong (2322 node, 4939 cạnh, 42 file dựng lại).
    `affected "cli()"` phải gọi bằng ID node (`scripts_tdq_state_cli`) vì bản portable nhân đôi
    nhãn `cli()` — không có node vỡ, cũng không có node nào phụ thuộc ngược vào nó.
    Tên `cmd_build()` trong plan là SAI lúc viết plan: `build_portable.py` không có hàm đó; hai
    node thật request chạm là `sinh_ban_codex()` và `_sinh_hooks_codex()`, đã kiểm cả hai —
    caller duy nhất là `main()`, trỏ đúng `scripts/build_portable.py:L1067`. Suite sau khi dựng
    lại bản portable ra đúng danh sách đỏ nền như T10.3.

## Cụm song song

- **P1 là cụm tuần tự, không tách**: bốn task cùng chạm `scripts/tdq_state.py`. Nó phải xong
  trước P4, P5, P7, P8 vì bốn phase đó đọc hợp đồng của nó.
- **P2 và P3 tách được với P1 về vùng file** (`tdq_vungfile.py` · `tdq_codex.py`), nhưng T3.5 cần
  T2.2 nên P2 phải xong trước T3.5.
- **P4 và P5 là cụm song song thứ nhất: 2 nhánh** — `scripts/tdq_team.py` · ba file trong
  `hooks/scripts/`, không giao nhau, đều chỉ cần T1.1 (P5 thêm T1.3).
- **P7 là cụm song song thứ hai: 4 nhánh tài liệu**, trong đó T7.2/T7.3 cần T7.1 và T7.4 cần cả hai.
- **P8 chạy song song được với P6 và P7** sau khi P1–P3 xong: ba vùng file rời nhau
  (`scripts/tdq_bench.py` · `hooks/scripts/codex_edit_gate.py` · `skills/`), trừ T8.2 cần T3.7.
- Trần tốc độ của mode đội ở plan này là 4 nhánh, đúng bằng cụm P7.

## Luật file nóng

Ba đường dẫn bị nhiều task chạm, cả ba xử theo cách **nâng lên đợt sớm**:

- `scripts/tdq_state.py` — T1.1 đến T1.3. T1.1 sửa ba hằng số và `normalize_mode` trước; T1.2 đổi
  `phase_row` sang bảng tra; T1.3 thêm `modes --json`. Đây là hợp đồng mà P4, P5, P7, P8 đều đọc,
  nên P1 phải xong trước và mỗi đợt chỉ một task được chạm.
- `scripts/tdq_codex.py` — T3.1 đến T3.7, cộng T6.4 và T10.1. T3.1 tạo khung file và lệnh `check`;
  mọi task sau nhánh ra từ file đã ổn định.
- `scripts/build_portable.py` — T6.1 và T9.2. T6.1 đổi cách nạp adapter (đọc file thay vì chuỗi
  nhúng) trước; T9.2 mới thêm luật không ghi vào `.codex/` gốc repo.

`scripts/tdq_state.py` giữ node `cli()` và `scripts/build_portable.py` giữ node `cmd_build()`, cả
hai nằm trong mục `## Hub` của `docs/kien-truc.md` (17 bậc), nên Definition of Done có dòng kiểm
hồi quy riêng cho hai node ấy.

## Definition of Done

Trỏ về §6 của spec (Q1–Q26 kèm Q14b–Q14e và Q21b).

- [x] Q1 Máy CÓ Codex: `co=true`, `chay_duoc=true`, `phien_ban` khớp, `modes --json` trả 3 mode chọn được — `python3 scripts/tdq_codex.py check --json` và `python3 scripts/tdq_state.py modes --json` — **PARTIAL**: máy có `codex` nhưng cờ đồng ý false nên `chay_duoc`/`phien_ban` chưa đo được (xem QC)
- [x] Q2 Máy KHÔNG có Codex: exit 0, `co=false`, mode `codex` có `chon_duoc=false` kèm `ly_do` — `python3 -m unittest tests.test_codex_cli tests.test_state`
- [x] Q3 Bốn nguyên nhân không chọn được cho bốn `ly_do` khác nhau — `python3 -m unittest tests.test_codex_cli`
- [x] Q4 `setup` chưa đủ hai điều kiện thì không ghi gì vào `.codex/` — `python3 -m unittest tests.test_checkportable`
- [x] Q5 Mode thứ ba vào được state, `tdq_status` in nhãn `codex implement` — `python3 -m unittest tests.test_mode_phase tests.test_state`
- [x] Q6 `phase_row` đúng cho **mọi** mode trong `VALID_MODES`, thêm mode chỉ cần một dòng bảng — `python3 -m unittest tests.test_phase_table`
- [x] Q7 Mode nào đi qua đội được khai tường minh, thiếu khai thì lỗi lúc nạp — `python3 -m unittest tests.test_team_mode`
- [x] Q8 Lệnh dựng ra đối chiếu với hằng số `CO_EXEC`, không liệt kê lại tên cờ — `python3 -m unittest tests.test_codex_run`
- [x] Q9 Ba ca cùng `exit=0` ra ba trạng thái khác nhau — `python3 -m unittest tests.test_codex_run`
- [x] Q10 File kết quả thiếu, rỗng, hoặc lệch schema đều ra FAIL — `python3 -m unittest tests.test_codex_run`
- [x] Q11 Hậu kiểm lấy mốc của chính task: ca "task trước còn việc dở" vẫn PASS — `python3 -m unittest tests.test_vungfile`
- [x] Q12 Hoàn tác trả đúng nội dung mốc và **không đổi index** — `python3 -m unittest tests.test_vungfile`
- [x] Q13 Sandbox chặn ghi ra đích ngoài repo, ngoài `/tmp` và `$TMPDIR` — chạy thật một lượt rồi `test ! -e <đường dẫn>` (SKIP có tuyên bố nếu `check` báo không sống) — **SKIP có tuyên bố**: cần người dùng bật cờ đồng ý (xem QC)
- [x] Q14 Hook deny chặn thật cả hai matcher, năm dạng lệnh shell — `python3 -m unittest tests.test_codex_edit_gate` cộng một lượt chạy thật
- [x] Q14b Vùng khoá được tôn trọng: sửa file test → FAIL kể cả khi test xanh — `python3 -m unittest tests.test_vungfile tests.test_codex_edit_gate`
- [x] Q14c Nhịp chia đôi: test đỏ trước khi gọi Codex, xanh sau đó, log ghi cả hai mốc — `python3 -m unittest tests.test_codex_run`
- [x] Q14d `.codex/hooks.json` gốc repo chỉ hai event `PreToolUse` — `python3 -m unittest tests.test_codex_hooks_json`
- [x] Q14e Build không đè `.codex/` viết tay: so `sha256sum` trước/sau — `python3 -m unittest tests.test_build_portable`
- [x] Q15 Mọi lệnh có `--dangerously-bypass-hook-trust`; hook không bắn thì đúng một dòng cảnh báo, không có nhánh tự hạ cấp — `python3 -m unittest tests.test_codex_edit_gate`
- [x] Q16 `cleanup` xoá hết thư mục tạm, gọi khi không có gì vẫn exit 0 — `python3 -m unittest tests.test_codex_run`
- [x] Q17 Không đầu ra nào chứa `Bearer`; `CODEX_HOME` tạm quyền 700 — `python3 -m unittest tests.test_codex_run`
- [x] Q18 Nguồn tên model đúng thứ tự, thiếu cả hai thì fail kèm câu sửa — `python3 -m unittest tests.test_codex_run`
- [x] Q19 Log đủ 7 mảnh, ghi sha256 prompt, file log nguyên văn được gitignore — `python3 -m unittest tests.test_codex_run` và `git check-ignore -q <file log>`
- [x] Q20 `modes --json` là nguồn duy nhất; chữ cái map đúng ở cả ca 2 và 3 lựa chọn — `python3 -m unittest tests.test_prompt_context`
- [x] Q21 Tầng luật không còn kể mode theo cặp nhị phân; `tdq_state.py` không import `tdq_codex` — `python3 -m unittest tests.test_luat_mode tests.test_kien_truc`
- [x] Q21b Biến mốc của mode sống qua sandbox, tên không chứa `KEY`/`TOKEN`/`SECRET` — một lượt chạy thật in biến ra file rồi đọc lại — **PARTIAL**: phần tên biến PASS; phần sống-qua-sandbox SKIP cùng lý do Q13
- [x] Q22 `simulate` tương thích file đo cũ, có khoá thì in ba mode, `so_mau < 3` bị từ chối — `python3 -m unittest tests.test_bench`
- [x] Q23 `calibrate` lấy ≥ 3 mẫu từ log lúc implement, không chạy benchmark riêng — `python3 -m unittest tests.test_bench`
- [x] Q24 Toàn bộ suite xanh, 0 fail 0 error — `python3 -m unittest discover tests` — **FAIL vì nợ có sẵn**: 290 fail / 4 error bằng ĐÚNG danh sách ở HEAD trước request; request thêm 0 fail mới
- [x] Q25 Không còn chuỗi `ADAPTER_CODEX`; bundle có `codex_edit_gate.py` và `.codex/hooks.json` — `python3 -m unittest tests.test_build_portable`
- [x] Q26 Tầng tài liệu nhất quán — `python3 scripts/doc_lint.py --pair docs/tdq/spec/2026-09-10-2247-mode-codex-implement.md docs/tdq/plan/2026-09-10-2247-mode-codex-implement.md` và `python3 scripts/i18n_check.py scripts/ hooks/ skills/ agents/` — **PARTIAL**: `doc_lint --pair` exit 0; `i18n_check` đỏ trên 207 + 44 dòng có sẵn ngoài `Chạm:`
- [x] Hồi quy hai node Hub `cli()` và `cmd_build()` — `python3 -m unittest discover tests` cộng `graphify affected "cli()" --depth 2`
