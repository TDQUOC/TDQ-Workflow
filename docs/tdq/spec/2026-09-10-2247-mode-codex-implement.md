# SPEC — Mode `codex implement`: mode thực thi thứ ba, leader gọi Codex viết code

Ngày: 2026-09-10 · Bản: 1.3 · Brief: ../brief/2026-09-10-2247-mode-codex-implement.md · Lane: full
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md
Trạng thái: ĐÃ DUYỆT 2026-09-11T12:37 (user nhắn "duyệt spec" — bản 1.3; bản 1.1 đã duyệt
2026-09-11T00:11, bản 1.2 sửa theo 18 finding của `tdq-reviewer`, bản 1.3 thêm 7 chỗ của vòng đo
2026-09-11 với lựa chọn `1a 2a`, nên user duyệt lại)

Bản 1.1 đổi kiến trúc theo vòng hỏi đáp thứ hai: bỏ tầng sub-agent và worktree song song của bản
1.0. Mode chạy **tuần tự ngay trong turn của leader**, đúng như `main implement`, chỉ khác ở chỗ
người gõ code là Codex.

Bản 1.2 không đổi kiến trúc, chỉ siết chỗ đo được: tách module vùng file ra khỏi tầng CLI, đặt
module state lên trước (nó không được phụ thuộc tầng Codex), nâng file hook Codex đang bị nhúng
thành file thật thay vì thêm file thứ hai cùng vai, gom cờ dòng lệnh về **một** bảng duy nhất,
ghim nguồn tên model, bỏ cơ chế tự hạ cấp, và đổi bốn hạng mục QC không đo được thành đo được.
Danh sách đối chiếu 18 finding ở §7.

Bản 1.3 vá 7 chỗ tìm ra khi đo thêm trên máy sau bản 1.2, người dùng chọn `1a 2a`. Hai chỗ nặng
nhất là lỗi im lặng: hậu kiểm không có mốc so sánh nên **task sau FAIL oan vì việc của task
trước**, và lệnh hoàn tác sai làm mù chính lớp hậu kiểm. Chỗ thứ ba đổi cách chạy từng task:
**leader viết test đỏ trước, Codex chỉ được làm nó xanh** — test không còn do người bị kiểm viết.
Đối chiếu đủ 7 chỗ ở §7.

## Mục lục

- 1. Mục tiêu & phạm vi
- 1b. Lộ trình
- 2. Đầu ra cụ thể
- 2b. Ranh giới module
- 3. Cách tiếp cận & lý do
- 3b. Năng lực & công cụ
- 4. Yêu cầu bắt buộc
- 5. Ràng buộc & rủi ro
- 6. QC & Definition of Done
- 7. Câu hỏi còn mở

## 1. Mục tiêu & phạm vi

- **Mục tiêu**: thêm mode thực thi thứ ba tên `codex implement`, đứng cạnh `main` và `subagent`.
  Nó chạy **giống `main`**: leader làm tuần tự từng task theo đúng thứ tự plan, trong cùng một
  turn, không phát task cho ai. Khác duy nhất một điểm: mỗi task, thay vì tự viết code, leader
  gọi `codex exec` ở chế độ không xin phê duyệt để Codex viết, rồi leader kiểm lại ngay bằng
  hiệu ứng thật trước khi tick. Mode chỉ hiện ra ở cổng chọn khi máy thật sự chạy được Codex.

**Trong phạm vi**

- Mode mới: mã máy `codex`, nhãn đọc `codex implement`, thêm vào `VALID_MODES`.
- Cổng năng lực **hai chặng**: chặng cài đặt (hỏi người dùng, dò `codex`, phải đủ cả hai) và
  chặng chọn mode (kiểm sống, hiện 2 hay 3 lựa chọn, kèm một dòng lý do khi không chọn được).
- Bộ chạy một task bằng Codex: dựng lệnh từ **một** bảng cờ duy nhất, đọc kết quả từ file có
  khuôn, phân biệt bốn trạng thái *xong / fail / timeout / deny* bằng bảng phán quyết, dựng và
  **xoá** `CODEX_HOME` tạm.
- Module riêng cho mốc hoàn tác cộng hậu kiểm vùng file, để hook và mode `main` dùng lại được.
  Hậu kiểm so với **mốc của chính task**, không so với `HEAD`.
- Nhịp red → green chia đôi giữa hai người: **leader viết test đỏ**, Codex chỉ được làm nó xanh;
  file test là **vùng khoá** với Codex trong lượt đó.
- Lệnh in danh sách mode ở dạng **máy đọc được**, để cổng chọn mode và phép kiểm cùng đọc một
  nguồn.
- Hợp đồng vai của Codex (prompt mẫu, khuôn kết quả trả về, ngưỡng digest) nằm ở tầng luật
  `skills/`, không nằm ở `agents/`.
- Hai lớp hàng rào còn lại: hậu kiểm `git diff --name-only` so `VÙNG FILE` · hook `PreToolUse`
  của Codex chặn ngay lúc ghi, **mở rộng file hook đã có** chứ không thêm file mới cùng vai.
- Bỏ các chỗ rẽ nhánh cứng theo mode, thay bằng bảng tra `mode → hành vi`.
- Hệ số Codex cho `tdq_bench.py simulate`, đo bằng `calibrate`.
- Sinh lại `portable_claude/` và `portable_codex/` bằng `scripts/build_portable.py`.

**NGOÀI phạm vi**

- **Tầng sub-agent Claude và worktree song song** — có trong bản 1.0, người dùng bỏ ở vòng 2:
  *"codex implement sẽ ko đưa cho subagent và main agent sẽ gọi lệnh cho codex implement như
  main implement"*. Kéo theo bỏ luôn: giới hạn 2–3 tiến trình, một `CODEX_HOME` cho mỗi tiến
  trình, và mọi thứ dính `scripts/tdq_team.py` ngoài một dòng khai tường minh.
- File agent mới trong `agents/` — người dùng chọn 1A: không còn ai được phát task thì file
  trong `agents/` là file chết.
- Chạy Codex trong worktree tạm dù tuần tự — người dùng chọn 2A: dùng mốc hoàn tác git.
- Đổi cách chia task, thứ tự task, hay hành vi của mode `main` và mode `subagent`.
- Sửa `~/.codex/config.toml` hay `~/.codex/auth.json` của người dùng.
- Bỏ mode `subagent` — giữ nguyên, để còn đường lùi.

## 1b. Lộ trình

Chép từ brief mục `### Lộ trình`, đã cắt các bước chỉ phục vụ kiến trúc bản 1.0. User duyệt spec
là duyệt luôn lộ trình này.

| Bước/phase | Chạy? | Vì sao |
|---|---|---|
| analyze | CÓ (xong) | tồn kho, đọc code, research 4 góc, 10 phép đo, phỏng vấn 2 vòng |
| Research web thêm một vòng | BỎ | 4 góc research cộng 10 phép đo trên máy đã trả lời hết; chỗ ngờ duy nhất còn lại (độ phủ `apply_patch`) đã có lớp hậu kiểm bù |
| Interview | CÓ (xong) | vòng 1 sáu câu, vòng 2 hai câu đổi kiến trúc |
| spec | CÓ | khung bất biến |
| Review spec bằng `tdq-reviewer` | CÓ | chạy sau khi duyệt spec, trước khi viết plan; request sửa hàng rào an toàn của chính pipeline nên cần một mắt thứ hai |
| plan | CÓ | khung bất biến, turn khác với spec theo luật |
| Review plan bằng `tdq-reviewer` | CÓ | plan phải cắt vùng file cho các điểm neo mà không sinh file nóng |
| mode | CÓ | nhưng **chỉ chọn được `main` hoặc `subagent`** — mode thứ ba là sản phẩm của chính request này, chưa tồn tại lúc làm nó |
| implement | CÓ | khung bất biến |
| Đo thời gian thật bằng `tdq_bench.py calibrate` | CÓ | mặt hiệu năng đòi con số kiểm được; 0,87x hiện chỉ có 1 mẫu, luật đòi tối thiểu 3 |
| Dựng lại bundle bằng `build_portable.py` | CÓ | `portable_*` là đồ sinh; chặng cài đặt phải nói đúng về máy mới |
| QC độc lập bằng `tdq-qc-tester` | CÓ | request tự sửa hàng rào của chính nó, tự kiểm là xung đột lợi ích |
| report | CÓ | khung bất biến |

## 2. Đầu ra cụ thể

| # | Đầu ra | Đường dẫn/vị trí | Đo "xong" bằng |
|---|---|---|---|
| 1 | Dò năng lực Codex: `check` (dò cài + kiểm sống), có `--json` | `scripts/tdq_codex.py` | `tdq_codex.py check --json` in JSON có `co`, `chay_duoc`, `phien_ban`, `ly_do`, `goi_y`; máy không có `codex` vẫn exit 0 và `co=false` |
| 2 | Cờ quyết định cài tầng Codex, mức máy, không đẩy lên repo | `docs/tdq/.tdq-codex.json`, thêm dòng vào `.gitignore` | file có `nguoi_dung_dong_y`, `quyet_dinh_luc`, `codex_model`; `check` đọc được và trả lý do `user đã từ chối` khi cờ là false |
| 3 | **Một** bảng cờ dòng lệnh duy nhất, cộng `run` dựng lệnh từ đúng bảng đó | `scripts/tdq_codex.py` | hằng số bảng cờ là chỗ duy nhất viết ra tên cờ; lệnh `run` sinh ra bằng đúng bảng ấy, không có cờ nào viết rời; **stdin không bao giờ là TTY** (`stdin=DEVNULL` hoặc một phép chuyển hướng — không bắt buộc phải là chuỗi `< /dev/null`, để `run` được gọi dạng danh sách chứ không phải `shell=True`); có timeout tường minh |
| 4 | Nguồn tên model ghim rõ, thiếu thì fail tường minh | `scripts/tdq_codex.py` | thứ tự lấy model: cờ dòng lệnh `--model` → khoá `codex_model` của đầu ra 2 → **fail kèm câu sửa**; không bao giờ im lặng dùng model mặc định của máy; tên model thật ghi vào log mỗi task |
| 5 | Bảng phán quyết bốn trạng thái, không dùng exit code | `scripts/tdq_codex.py` | bảng có bốn cột dấu hiệu (exit code · file kết quả có/không · nội dung `BLOCKED` hay `permissionDecision` · quá hạn) và trả đúng một trong `xong / fail / timeout / deny`; ba ca `exit=0` khác nhau (xong · bị deny · bị sandbox chặn) ra ba trạng thái khác nhau |
| 6 | Vòng đời `CODEX_HOME` tạm: dựng và **xoá** | `scripts/tdq_codex.py` | `tdq_codex.py cleanup` là chủ sở hữu duy nhất của việc xoá; gọi nó xong không còn thư mục tạm nào của mode; gọi khi không có gì để xoá vẫn exit 0 |
| 7 | Mốc hoàn tác cộng hậu kiểm vùng file, **module riêng** dùng lại được | `scripts/tdq_vungfile.py` | chụp mốc trả sha `git stash create`, **cây sạch (trả rỗng) thì lùi về `HEAD`**; hậu kiểm so `git diff --name-only <sha mốc của chính task>` cộng **hiệu hai tập file chưa theo dõi** — tuyệt đối không so với `HEAD`, vì task trước để lại việc chưa commit; lệch một file là FAIL và in đúng tên; hoàn tác dùng `git restore --source=<sha> --worktree` (chỉ chạm cây làm việc, **không** chạm index) và xoá file mới; module này không import `tdq_codex` nên hook và mode `main` gọi được |
| 7b | Vùng khoá của một lượt Codex | `scripts/tdq_vungfile.py` | vùng khoá là tập file leader tuyên bố Codex không được chạm trong lượt đó, tối thiểu gồm **file test của task**; file vùng khoá xuất hiện trong diff so mốc → FAIL kèm tên file, kể cả khi test xanh |
| 8 | Mode thứ ba trong nguồn chân lý | `scripts/tdq_state.py` | `VALID_MODES == ("main", "subagent", "codex")`; `normalize_mode("codex implement") == "codex"`; `mode_label("codex") == "codex implement"`; `tdq_state.py` **không** import `tdq_codex` |
| 9 | Bảng tra `mode → hàng phase` thay `if` cứng | `scripts/tdq_state.py` | thân `phase_row` không còn chuỗi `"subagent"`; bảng trả đúng hàng cho **mọi** mode trong `VALID_MODES`; thêm mode thứ tư chỉ cần thêm một dòng bảng |
| 10 | Lệnh in danh sách mode ở dạng máy đọc được | `scripts/tdq_state.py` | `tdq_state.py modes --json` in danh sách `{ma, nhan, chon_duoc, ly_do}`; cổng chọn mode và phép kiểm cùng đọc đầu ra này, nên "hiện 2 hay 3 lựa chọn" thành câu đo được chứ không phải câu đọc bằng mắt |
| 11 | Khai tường minh mode nào đi qua đội | `scripts/tdq_team.py` | `canh_bao_lach_luat` đọc bảng khai (`codex` không đi qua đội) chứ không rơi vào nhánh mặc định; mode có trong `VALID_MODES` mà thiếu khai thì lỗi ngay lúc nạp bảng |
| 12 | Hook chặn của Codex: **nâng** chuỗi `ADAPTER_CODEX` đang nhúng thành file thật rồi mở rộng, không thêm file thứ hai cùng vai | `hooks/scripts/codex_edit_gate.py`, `.codex/hooks.json` ở gốc repo | file tồn tại trên đĩa và `build_portable.py` **đọc** nó; nhánh `Bash` trích được đường ghi từ lệnh shell cho năm dạng `>`, `>>`, heredoc, `tee`, `mv`; payload ghi ngoài `VÙNG FILE` hoặc vào vùng khoá → stdout có `permissionDecision: deny` kèm mã `[TDQ:VUNG]`; trong vùng → không deny; ngoài mode `codex` → chỉ nhắc |
| 12b | `.codex/hooks.json` ở gốc repo chỉ có **hai** event `PreToolUse` | `.codex/hooks.json` | file khai đúng hai matcher `apply_patch` và `Bash`, và **không** có `Stop`, `UserPromptSubmit`, `SessionStart`; cấm sinh nó bằng hàm sinh bundle (hàm ấy đi hết bảng 5 hook, sẽ cắm `stop_gate.py` chặn kết thúc lượt Codex và `prompt_context.py` bơm `[TDQ:*]` vào prompt của Codex) |
| 12c | Khai rõ file `.codex/` nào viết tay, file nào sinh | `.codex/config.toml`, `.codex/hooks.json`, `scripts/build_portable.py` | `.codex/config.toml` ở gốc repo là file **viết tay đang được git theo dõi** (có `shell_environment_policy` và các biến `TDQ_SEARCH_*`) — lần build sau không được đè nó; biến môi trường mốc của mode có tên **không chứa** `KEY`, `TOKEN`, `SECRET`, vì Codex lọc biến trông như bí mật |
| 13 | Bỏ phép đảo nhị phân mode ở tầng hook | `hooks/scripts/prompt_context.py`, `hooks/scripts/_common.py`, `hooks/scripts/edit_gate.py` | `_PLAN_MODE` khớp cả `codex`; không còn phép `"subagent" if x == "main" else "main"`; chữ cái người dùng gõ được map sang mode bằng **đúng danh sách vừa in ra** (đầu ra 10), nên 2 hay 3 lựa chọn đều đúng; dòng gợi ý của `edit_gate.py` in đủ ba mode |
| 14 | Hợp đồng vai Codex (gồm nhịp *leader viết test đỏ → Codex làm xanh*), cổng chọn mode động, và **tất cả** file luật còn kể mode theo cặp nhị phân | `skills/tdq-build/references/codex-mode.md`, `skills/tdq-build/SKILL.md`, `skills/tdq-plan/SKILL.md`, `skills/tdq-plan/references/mode-gate.md`, `skills/tdq-plan/references/plan-template.md`, `skills/tdq-conventions/references/approval.md`, `skills/tdq-conventions/references/phases.md`, `skills/tdq-build/references/team-mode.md` | file hợp đồng có prompt mẫu cố định, khuôn kết quả Codex phải trả, ngưỡng digest, **nhịp bốn bước của một task** (leader viết test đỏ · chạy để thấy đỏ · Codex làm xanh trong `VÙNG FILE` trừ vùng khoá · leader chạy lại cộng hậu kiểm), mẫu cổng chọn cho cả hai trường hợp 2 hay 3 lựa chọn kèm bảng 4 nguyên nhân; một phép kiểm quét tầng luật khẳng định **không còn** chỗ nào kể mode dưới dạng cặp `main`/`subagent` cứng; mọi file chỉ nêu **tên lệnh**, không chép logic |
| 15 | Hệ số Codex cho mô phỏng, **tuỳ chọn** để không phá file đo cũ | `scripts/tdq_bench.py` | file hằng số thiếu khoá Codex → `simulate` cho `main` và `subagent` vẫn chạy đúng như trước, chỉ bỏ dòng mode `codex` kèm một câu lý do; có khoá thì in thời gian mode `codex` cạnh `main`; hằng số phải do `calibrate` đo với `so_mau >= 3`; hệ số viết cứng bị chặn |
| 16 | Bundle sinh lại có tầng Codex, cài đặt hỏi trước | `scripts/build_portable.py`, `scripts/tdq_checkportable.py` | `build_portable.py` **đọc file** `hooks/scripts/codex_edit_gate.py` thay vì giữ chuỗi `ADAPTER_CODEX`; `tdq_checkportable.py setup` hỏi trước khi cài tầng Codex và ghi cờ ở đầu ra 2 |
| 17 | Log của mode không lọt vào repo công khai | `.gitignore`, `scripts/tdq_codex.py` | file log của mode được `.gitignore` liệt kê; dòng log ghi **sha256 của prompt** cộng phần đầu đã qua `mask_secrets`, không ghi nguyên văn prompt vào bất cứ file nào được git theo dõi |

## 2b. Ranh giới module

Dựng từ quan hệ gọi thật, không từ tên thư mục. Ba phép đo LSP làm nền: `normalize_mode` có
9 ref thuộc 3 namespace; `effective_mode` có 5 ref, trong đó **2 ref nằm ở `hooks/scripts`**
(`prompt_context.py:22` import, `:175` gọi) — đó là chỗ tầng hook chạm vào tầng CLI; `phase_row`
có 4 ref, 2 ở `scripts` và 2 ở tầng test, tức nó là **nội bộ** `tdq_state.py`, sửa được mà không
lan sang hook.

| Module | Vùng file (file nguồn) | Phụ thuộc module | Đầu ra §2 nào |
|---|---|---|---|
| M1 · Mode thứ ba, bảng tra, lệnh in mode | `scripts/tdq_state.py` | không | 8, 9, 10 |
| M2 · Vùng file, vùng khoá & mốc hoàn tác | `scripts/tdq_vungfile.py` | không | 7, 7b |
| M3 · Tầng CLI Codex | `scripts/tdq_codex.py`, `.gitignore` | M1, M2 | 1, 2, 3, 4, 5, 6, 17 |
| M4 · Khai mode nào đi qua đội | `scripts/tdq_team.py` | M1 | 11 |
| M5 · Hook chặn của Codex | `hooks/scripts/codex_edit_gate.py`, `.codex/hooks.json` | M2 | 12, 12b, 12c |
| M6 · Tầng hook Claude | `hooks/scripts/prompt_context.py`, `hooks/scripts/_common.py`, `hooks/scripts/edit_gate.py` | M1 | 13 |
| M7 · Tầng luật | 8 file luật ở đầu ra 14 | M1, M3 | 14 |
| M8 · Hệ số hiệu năng | `scripts/tdq_bench.py` | M1 | 15 |
| M9 · Cài đặt & bundle | `scripts/build_portable.py`, `scripts/tdq_checkportable.py` | M3, M5, M7 | 16 |

Mỗi module sở hữu luôn phần test của chính nó, và test ấy thuộc vùng file của module đó chứ
không của module khác. Tên file test **chốt ở plan**, không chốt ở spec: spec bị niêm bằng sha
lúc duyệt, nên một cái tên đoán sai ở đây buộc phải duyệt lại.

**M1 phụ thuộc = không, và nó là module ĐẦU TIÊN.** `tdq_state.py` là nguồn chân lý mà M4, M6,
M7, M8 đều đọc, đồng thời là hub (`cli()` 17 bậc theo `docs/kien-truc.md`). Nếu nó phải chờ tầng
Codex thì mode thứ ba không vào được state trước khi có `codex`, và tệ hơn: `tdq_state.py` sẽ
import `tdq_codex.py` — biến nguồn chân lý thành thứ phụ thuộc một CLI ngoài. Cấm chiều phụ
thuộc đó, và có phép kiểm khẳng định `tdq_state.py` không import `tdq_codex`.

**M2 tách khỏi M3 vì hai lý do đo được.** Một: hook ở M5 cần đúng logic "đường ghi này có trong
`VÙNG FILE` không", mà `hooks/` không được để `scripts/` gọi ngược — để logic ấy trong
`tdq_codex.py` thì hook phải kéo theo cả tầng gọi `codex`. Hai: mốc hoàn tác cộng hậu kiểm vùng
file không có gì riêng của Codex, nên mode `main` dùng lại được nguyên vẹn.

M3 gom sáu đầu ra vào một file vì cả sáu cùng một lý do đổi: chúng là mặt tiếp xúc duy nhất với
`codex` CLI. Tách `check` ra khỏi `run` sẽ tạo hai file cùng phải sửa mỗi lần cờ của `codex exec`
đổi, tức chia sai đường cắt.

## 3. Cách tiếp cận & lý do

**Chọn: leader chạy tuần tự, mỗi task một lượt `codex exec`, hai lớp hàng rào cộng một mốc hoàn
tác, và bảng tra thay rẽ nhánh cứng.**

Vì sao từng mảnh, kèm bằng chứng đo được:

- **Sandbox vẫn là lớp ngoài, nhưng bán kính rộng hơn bản 1.0.** Đo thật: yêu cầu Codex ghi
  đường dẫn tuyệt đối ra ngoài `cwd` trả `operation not permitted`, không file nào được tạo, log
  in `sandbox: workspace-write [workdir, /tmp, $TMPDIR]`. Chạy tuần tự trong repo nghĩa là
  `-C <gốc repo>`, nên Codex ghi được khắp repo. Phải nói đúng ba vùng ghi được — **repo,
  `/tmp`, `$TMPDIR`** — chứ không nói gọn là "khoanh trong repo", vì hậu kiểm chỉ soi repo. Đo
  thêm được một thứ đáng giá: sandbox chặn cả ghi vào `.git/`, `git commit` trong lượt Codex trả
  `.git/index.lock: operation not permitted`. Nghĩa là mọi thay đổi của Codex buộc phải nằm lại
  trong cây làm việc, nơi hậu kiểm nhìn thấy.
- **Mốc hoàn tác git bù đúng phần bán kính vừa nới.** Người dùng chọn 2A. Trước mỗi task ghi lại
  sha `git stash create` cộng danh sách file chưa theo dõi; file lệch vùng thì trả về nội dung
  mốc, file mới thì xoá. Cách này không đụng vào cây làm việc lúc chụp mốc, nên không phá phần
  việc đang dở của các task trước. Một chi tiết phải viết ra vì nó im lặng làm sai: cây sạch thì
  `git stash create` trả **chuỗi rỗng**, không trả sha — ca đó lùi về `HEAD`, chứ không được coi
  là "không có mốc".
- **Hậu kiểm so với mốc của chính task, không so với `HEAD`.** Đây là chỗ kiến trúc tuần tự khác
  hẳn bản 1.0: mỗi worktree hồi đó là cây sạch, còn bây giờ task T1 sửa file rồi **không** commit,
  nên đến T2 mà so với `HEAD` thì file của T1 hiện ra như file lệch và T2 FAIL oan — càng về cuối
  plan càng chắc FAIL. Mốc so sánh là sha đã chụp trước chính task đó.
- **Hoàn tác bằng `git restore --source=<sha> --worktree`, không bằng `git checkout <sha> -- <file>`.**
  `git checkout` từ một commit ghi cả index, nên sau khi hoàn tác thì `git diff` không còn thấy
  file vừa lệch — lớp hậu kiểm của task tiếp theo bị mù đúng ở file đáng nghi nhất. Đây là lỗi im
  lặng, mà lớp hàng rào này tồn tại để chặn đúng loại đó.
- **Test đỏ do leader viết, Codex chỉ được làm xanh.** Người dùng chọn 2A. Nếu Codex viết cả code
  lẫn test rồi leader "chạy lại test" thì thước đo do chính người bị đo làm ra: một test rỗng
  nghĩa vẫn xanh và task vẫn được tick. Nhịp bốn bước: leader viết test đỏ · chạy để thấy đỏ ·
  Codex làm xanh · leader chạy lại cộng hậu kiểm. Kèm theo là **vùng khoá**: file test không nằm
  trong phần Codex được ghi, và chạm vào nó là FAIL kể cả khi test xanh. Giá phải trả là mỗi task
  thêm một nhịp của leader; đó là giá của việc thước đo độc lập với người bị đo.
- **Vùng file là module riêng, không nằm trong tầng Codex.** Hook ở M5 cần đúng phép hỏi "đường
  ghi này có trong `VÙNG FILE` không"; để phép ấy trong `tdq_codex.py` thì `hooks/` phải kéo theo
  cả tầng gọi `codex`, ngược chiều phụ thuộc mà `docs/kien-truc.md` cho phép. Tách ra còn được
  thêm một thứ: mode `main` dùng lại nguyên vẹn vì trong đó không có gì riêng của Codex.
- **Một bảng cờ duy nhất, không kể tên cờ ở hai chỗ.** Danh sách cờ của `codex exec` là thứ sẽ
  đổi theo phiên bản Codex. Kể nó ở hằng số rồi kể lại lần nữa trong phép kiểm nghĩa là bản sau
  sửa một chỗ, chỗ kia vẫn xanh. Nên phép kiểm đối chiếu **với bảng**, và bảng là chỗ duy nhất
  viết ra tên cờ.
- **Nguồn tên model ghim rõ, thiếu thì fail.** Trên máy này `codex` đi qua router nội bộ, model
  mặc định không phải model của Codex. Im lặng dùng mặc định nghĩa là chất lượng task đổi mà log
  vẫn "xong". Thứ tự: cờ `--model` → khoá `codex_model` trong cờ cài đặt → fail kèm câu sửa.
- **Hậu kiểm `git diff --name-only` là lớp không thể tắt.** Người dùng chọn 4A ở vòng 1. Lớp này
  chạy bằng git, không phụ thuộc Codex hợp tác, nên nó là lớp chắc chắn còn sống trong mọi cấu
  hình. Lệch một file so `VÙNG FILE` là task FAIL.
- **Hook Codex là lớp chặn sớm, có giá trị thật nhưng không được là hàng rào duy nhất.** Đo thật:
  trả `permissionDecision: deny` thì file **không** được tạo và Codex tự báo `BLOCKED`; payload
  có `tool_input.command` nên đọc được nguyên văn lệnh. Nhưng hook **không tự chạy**: thiếu
  `--dangerously-bypass-hook-trust` là hook im lặng (issue #32491, còn nguyên ở 0.154.0), và độ
  phủ `apply_patch` còn ngờ. Nên tính đúng đắn dựa vào hậu kiểm, hook chỉ để chặn sớm kèm lý do.
  Hệ quả thiết kế: **không có cơ chế tự hạ cấp**. Hook không bắn thì ghi một dòng log cảnh báo và
  chạy tiếp, vì hậu kiểm mới là lớp quyết định — thêm một máy tự đổi cấu hình chỉ tạo thêm nhánh
  chưa ai chạy.
- **Mở rộng file hook đã có, không thêm file thứ hai cùng vai.** `build_portable.py:540` đã giữ
  chuỗi `ADAPTER_CODEX` và sinh ra `hooks/scripts/codex_edit_gate.py`, và `HOOK_CODEX:531` đã khai
  matcher `apply_patch` cùng `Bash`. Thêm một `codex_gate.py` nữa là hai file cùng vai, hai chỗ
  phải nhớ sửa. Nên: nâng chuỗi đang nhúng thành file thật rồi mở rộng chính nó.
- **Nhưng KHÔNG dùng lại hàm sinh của bundle cho `.codex/hooks.json` ở gốc repo.** Hàm ấy đi hết
  bảng 5 hook, tức sẽ cắm `Stop → stop_gate.py` và `UserPromptSubmit → prompt_context.py` vào mọi
  lượt `codex exec`: lượt Codex bị chính cổng chặn-kết-thúc của pipeline giữ lại, và prompt của nó
  bị bơm thêm `[TDQ:*]`. File ở gốc repo chỉ được có hai event `PreToolUse`.
- **`.codex/config.toml` ở gốc repo là file viết tay đã có, không phải chỗ trống.** Nó đang được
  git theo dõi và mang `shell_environment_policy` cùng các biến `TDQ_SEARCH_*`. Đo thêm: với
  `inherit = "core"`, biến môi trường tự đặt **vẫn** đi tới được lệnh shell của Codex, nên biến
  mốc của mode dùng được — miễn tên nó không chứa `KEY`, `TOKEN`, `SECRET`, vì Codex lọc biến
  trông như bí mật.
- **Bảng tra `mode → hành vi` thay `if`.** Người dùng chọn 1B ở vòng 1. Hôm nay `phase_row` rẽ
  bằng `if ... == "subagent"`, và `canh_bao_lach_luat` **tự tắt** bằng `!= "subagent"`. Chỗ thứ
  hai là chỗ nguy hiểm nhất: nó im lặng khi hỏng, không test nào đỏ. Với kiến trúc mới, mode
  `codex` đúng là không đi qua đội — nhưng điều đó phải được **khai tường minh** trong bảng, chứ
  không đúng nhờ rơi vào nhánh mặc định. Mode mới quên khai thì lỗi lộ ra lúc nạp bảng.
- **Kênh kết quả là file có khuôn, không phải văn xuôi.** `--output-schema` là cơ chế chính thức;
  và đo thật cho thấy `exit=0` xuất hiện ở cả ba ca khác nhau — làm xong, bị hook deny, bị
  sandbox chặn. Nên exit code không dùng để phán quyết.
- **Hợp đồng vai nằm ở `skills/`, không ở `agents/`.** Người dùng chọn 1A. Không còn ai được phát
  task thì file trong `agents/` là file chết, còn thứ leader thật sự cần vẫn là một prompt mẫu cố
  định cộng khuôn kết quả — hai thứ đó là luật, và luật thuộc `skills/`.
- **Cổng năng lực hai chặng theo đúng khuôn đã có.** `setup_status.py:132 _run_tool()` đã làm sẵn
  ba tính chất cần: `shutil.which` trước, `subprocess.run(..., encoding="utf-8")` có timeout, trả
  **dữ liệu** chứ không raise, và mọi luồng qua `mask_secrets`. Dùng lại khuôn ấy. Chặng cài đặt
  theo lối `tdq_lsp.py`: in lệnh rồi **chờ người dùng cho phép**, cấm tự cài.
- **Nói thật về hiệu năng thay vì hứa nhanh.** Đo được: `codex exec` mất ~5s khởi động cố định,
  và 105,8s cho một task thật so với `t_task = 122,16s` của leader. Chạy tuần tự thì mode này
  xấp xỉ ngang `main`, không nhanh hơn — giá trị của nó là đổi người viết code. Vì vậy `simulate`
  phải in được thời gian mode `codex` cạnh `main` để người dùng thấy đúng con số, chứ mode này
  không được quảng cáo là mode nhanh.

**Đã loại**

- **Tầng sub-agent Claude cộng worktree song song (bản 1.0)** — người dùng bỏ ở vòng 2. Đây là
  thứ duy nhất mang lại tốc độ, nên bỏ nó cũng bỏ luôn lý do "nhanh hơn"; ghi rõ ở trên.
- **Vẫn tạo `agents/tdq-codex-implementer.md` rồi gọi tuần tự một task một lượt (1B)** — được
  cái output rất dài của Codex bị hấp thụ trong sub-agent, nhưng nó thêm lại đúng tầng người dùng
  vừa bỏ. Bù lại bằng ngưỡng digest trong hợp đồng vai: leader chỉ đọc file kết quả có khuôn.
- **Mở worktree tạm cho từng task dù chạy tuần tự (2B)** — giữ được sandbox hẹp, nhưng thêm một
  bước gộp cho mỗi task; người dùng chọn mốc hoàn tác.
- **Dùng `--ignore-user-config`** — nghe hợp cho tự động hoá, nhưng nó bỏ luôn cấu hình cần dùng.
  Thay bằng một `CODEX_HOME` riêng dựng tối thiểu.
- **Sao nguyên `~/.codex/config.toml` vào `CODEX_HOME` riêng** — chạy được, đã đo, nhưng nhân bản
  khoá `Authorization: Bearer` sống ra thư mục tạm. Thay bằng: chỉ mang `auth.json`, `config.toml`
  dựng tối thiểu qua `-c`, thư mục `chmod 700`, xoá bắt buộc khi hết request.
- **Chỉ chạy lại test, bỏ so vùng file** — người dùng loại ở vòng 1, và nó bỏ mất lớp hàng rào
  duy nhất không thể tắt.
- **Viết cứng hệ số 0,87 vào code** — con số thật, nhưng chỉ 1 mẫu, còn luật đòi `so_mau >= 3`.

## 3b. Năng lực & công cụ

Chép từ brief mục `### Năng lực dùng được`. Phân vân → DÙNG.

| Skill | Nguồn | Phán quyết | Dùng ở đâu / Lý do loại |
|---|---|---|---|
| graphify | user | DÙNG | cuối turn có sửa code chạy `graphify extract . --code-only`; `god-nodes` để biết `cli()` là hub trước khi chạm M2 |
| tdq-conventions | plugin:tdq-workflow | NỀN | luật gốc, gồm khuôn khối nói với người dùng dùng cho cổng chọn mode |
| tdq-intake | plugin:tdq-workflow | NỀN | phase analyze đã chạy |
| tdq-spec | plugin:tdq-workflow | NỀN | phase đang chạy |
| tdq-plan | plugin:tdq-workflow | NỀN | chứa `references/mode-gate.md` — file bị sửa ở M6 |
| tdq-build | plugin:tdq-workflow | NỀN | chứa bước rẽ mode — file bị sửa ở M6 |
| tdq-status | plugin:tdq-workflow | NỀN | in mode đang chọn, phải biết mode thứ ba |
| tdq-check-status | plugin:tdq-workflow | NỀN | đọc state, phải hiểu mode thứ ba |
| tdq-lsp-setup | plugin:tdq-workflow | NỀN | bậc 1b đã chạy, 7/7 đạt; khuôn "chờ người dùng cho phép" của nó là mẫu cho chặng cài đặt |
| Đã xét 5 skill built-in khác | built-in | KHÔNG | khác lĩnh vực |

## 4. Yêu cầu bắt buộc

- **Log service bật mặc định**: mỗi lần gọi Codex ghi một dòng có timestamp, task, **tên model
  thật** (người dùng chọn 5A ở vòng 1), `CODEX_HOME` đã dùng, thời gian tường, trạng thái kết
  thúc, và **sha256 của prompt cộng phần đầu đã che** — không ghi nguyên văn prompt vào file được
  git theo dõi, vì repo này công khai và prompt mang nội dung file. Muốn đọc lại nguyên văn thì
  đọc file log đã được `.gitignore`. Phân biệt được `xong / fail / timeout / deny`. Tắt hoặc giảm
  được qua config, theo lối `log_enabled()` đã có trong `tdq_state.py`.
- Không placeholder, không TODO stub, không mock trình bày như dữ liệu thật.
- Mỗi thành phần có unit test riêng, chạy được bằng một lệnh, đi red → green.
- Code bám 5 nguyên tắc SOLID theo `skills/tdq-conventions/references/clean-code.md` và rule
  ngôn ngữ trong `skills/tdq-build/references/rules/`.
- **Mọi lệnh gọi Codex bắt buộc để stdin KHÔNG phải TTY, cộng một timeout tường minh (mặc định
  600 giây).** Đã đo: `codex exec` treo vô hạn khi stdin là một ống chờ, mà leader gọi qua Bash
  thì stdin không bao giờ là TTY. Cách đạt là `stdin=DEVNULL` hoặc một phép chuyển hướng — yêu
  cầu nằm ở **tính chất**, không ở chuỗi `< /dev/null`, để `run` không bị buộc phải chạy
  `shell=True` mới thoả.
- **Tên model phải tường minh.** Lấy theo thứ tự cờ `--model` → `codex_model` của cờ cài đặt →
  fail kèm câu sửa. Cấm im lặng rơi về model mặc định của máy.
- **Không tin exit code.** Mọi phán quyết dựa trên hiệu ứng thật trong repo cộng file kết quả có
  khuôn.
- **Cấm in nội dung `~/.codex/config.toml` ra bất cứ đâu**; mọi luồng đi qua `mask_secrets`.
- **Tick `[x]` ngay khi từng task pass**, đúng như mode `main` — mode này không gom tick chờ cuối.
- **Red → green chia đôi**: leader viết test đỏ và chạy để thấy đỏ TRƯỚC khi gọi Codex; Codex chỉ
  được làm nó xanh. File test là vùng khoá của lượt đó, chạm vào là FAIL.
- **Hậu kiểm luôn có mốc**: mọi phép so vùng file lấy mốc là sha chụp trước chính task đó, không
  bao giờ lấy `HEAD`.

## 5. Ràng buộc & rủi ro

Ràng buộc kiến trúc phải giữ (chép từ `docs/kien-truc.md`, chỉ dòng việc này chạm):

- *"`hooks/` được gọi `scripts/`; `scripts/` không được import `hooks/`"* — chạm ở M9:
  `build_portable.py` phải **đọc file** `hooks/scripts/codex_edit_gate.py` như dữ liệu, tuyệt đối
  không `import` nó. Chiều ngược lại cũng bị chặn một chỗ nữa: `tdq_state.py` (M1) không được
  import `tdq_codex.py`, vì nguồn chân lý không được phụ thuộc một CLI ngoài.
- *"`skills/` chỉ được nhắc tên lệnh của `scripts/`, cấm chép nội dung script vào skill"* —
  chạm ở M7: 8 file luật nêu tên `tdq_codex.py` và `tdq_vungfile.py`, không chép logic dò hay
  logic hậu kiểm.
- *"Chỉ `scripts/tdq_state.py` được ghi `docs/tdq/state.json`"* — chạm ở M3: cờ cài đặt là quyết
  định **mức máy**, không phải mức request, nên nằm ở file riêng `docs/tdq/.tdq-codex.json`.
- *"File code MỚI bắt buộc nằm trong `scripts/` hoặc `hooks/`"* — chạm ở M2, M3, M5:
  `scripts/tdq_vungfile.py`, `scripts/tdq_codex.py` và `hooks/scripts/codex_edit_gate.py` đều
  đúng chỗ. `.codex/hooks.json` ở gốc repo là file cấu hình, không phải file code — và nó là file
  MỚI viết tay, cạnh `.codex/config.toml` viết tay đã có; cả hai đều không được `build_portable.py`
  đè.
- *"`portable_claude/`, `portable_codex/` SINH bằng `scripts/build_portable.py`, không sửa tay"* —
  chạm ở M9: chỉ sinh lại.
- *"luật trong `skills/`, `agents/`, chú thích/docstring và chuỗi máy in ra viết TIẾNG ANH; tài
  liệu cho user theo `doc_lang`"* — chạm ở M7: file luật viết tiếng Anh, mẫu khối chat cho người
  dùng giữ tiếng Việt kèm `i18n-allow`.

| Rủi ro | Ảnh hưởng | Cách giảm |
|---|---|---|
| Sandbox cho ghi cả `/tmp` và `$TMPDIR`, không chỉ repo | câu "hàng rào khoanh Codex trong repo" là nói quá; hậu kiểm chỉ soi repo nên file rơi ra `/tmp` không ai thấy | tài liệu viết đúng ba vùng ghi được; đích thử ở Q13 đặt ngoài cả ba vùng; hậu kiểm không đổi phạm vi vì task chỉ được tính xong theo hiệu ứng trong repo |
| `codex exec` treo vô hạn khi stdin là ống chờ (đã đo: quá 120s, không trả về) | cả turn implement treo, và vì chạy tuần tự thì mọi task sau đứng chờ | "stdin không phải TTY" là yêu cầu bắt buộc ở §4; cộng timeout 600s; cộng một phép kiểm khẳng định lệnh sinh ra luôn có stdin đã bị đóng |
| Codex ghi được khắp repo, không còn bị worktree khoanh lại | một task viết đè file của task khác, hoặc file luật, và hỏng lan ra ngoài task | mốc hoàn tác trước mỗi task cộng hậu kiểm vùng file sau mỗi task (M2); lệch là FAIL và trả file về mốc, không tick |
| Hậu kiểm so với `HEAD` thay vì so với mốc của chính task | task sau FAIL oan vì việc chưa commit của task trước, và càng về cuối plan càng chắc FAIL — mode gần như không dùng được | mốc so sánh là sha chụp trước chính task đó, cộng hiệu hai tập file chưa theo dõi; có phép kiểm dựng đúng ca "task trước còn việc dở" |
| Hoàn tác bằng `git checkout <sha> -- <file>` ghi cả index | sau khi hoàn tác, `git diff` không còn thấy file vừa lệch → hậu kiểm của task sau bị mù đúng ở file đáng nghi nhất | dùng `git restore --source=<sha> --worktree`; có phép kiểm khẳng định index không đổi sau khi hoàn tác |
| Codex viết cả code lẫn test rồi leader chỉ chạy lại test đó | thước đo do chính người bị đo làm ra; test rỗng nghĩa vẫn xanh và task vẫn được tick | leader viết test đỏ trước, Codex chỉ làm xanh; file test là vùng khoá, chạm vào là FAIL kể cả khi test xanh |
| `.codex/hooks.json` gốc repo nếu sinh bằng hàm sinh bundle sẽ mang cả 5 event | mỗi lượt `codex exec` bị `stop_gate.py` giữ lại và bị `prompt_context.py` bơm `[TDQ:*]` vào prompt — pipeline tự chặn chính nó | file gốc repo chỉ có hai event `PreToolUse`; có phép kiểm khẳng định không có khoá `Stop` và `UserPromptSubmit` |
| `.codex/config.toml` gốc repo là file viết tay đang được git theo dõi, trùng tên với file `build_portable.py` sinh cho bundle | lần build sau đè mất cấu hình thật của người dùng | khai rõ trong tài liệu file nào viết tay file nào sinh; có phép kiểm khẳng định build không ghi vào `.codex/` của gốc repo |
| Log ghi nguyên văn prompt, mà repo này công khai | nội dung file trong prompt lọt vào lịch sử git công khai | dòng log ghi sha256 prompt cộng phần đầu đã che; nguyên văn chỉ nằm ở file log đã `.gitignore` |
| Cây sạch thì `git stash create` trả chuỗi rỗng chứ không trả sha | mốc hoàn tác rỗng, tưởng "không có gì để hoàn tác" trong khi thật ra là "chưa có gì thay đổi" | ca cây sạch lùi về `HEAD`; có phép kiểm riêng cho ca này |
| Thêm khoá hệ số Codex vào file hằng số có thể làm `simulate` chết với file đo cũ | `simulate` cho `main`/`subagent` — thứ đang dùng hằng ngày — hỏng vì một mode chưa ai chạy | khoá Codex là **tuỳ chọn**: thiếu thì bỏ dòng mode `codex` kèm một câu lý do, hai mode cũ chạy nguyên như trước; có phép kiểm nạp file đo cũ |
| `canh_bao_lach_luat` tự tắt với mọi mode khác `subagent`, hỏng trong im lặng | với mode mới thì kết quả đúng nhưng đúng do may; mode thứ tư sẽ sai mà không ai biết | đổi sang bảng khai tường minh: mode trong `VALID_MODES` mà thiếu khai thì lỗi ngay lúc nạp bảng |
| `exit=0` xuất hiện ở cả ba ca: xong, bị deny, bị sandbox chặn | tưởng task xong trong khi Codex bị chặn giữa đường | phán quyết bằng hiệu ứng thật cộng file kết quả có khuôn; thiếu file hoặc parse fail = FAIL |
| `CODEX_HOME` riêng có thể nhân bản khoá `Authorization: Bearer` sống ra thư mục tạm | rò khoá thật của người dùng | chỉ mang `auth.json`, `config.toml` dựng tối thiểu qua `-c`; `chmod 700`; xoá bắt buộc khi hết request; kiểm khẳng định không còn thư mục sót |
| Hook Codex im lặng nếu thiếu `--dangerously-bypass-hook-trust` (issue #32491 còn nguyên ở 0.154.0) | tưởng có lớp chặn sớm mà thực ra không có | truyền cờ ở **mỗi** lần gọi; cộng một phép kiểm khởi động khẳng định hook thật sự bắn; không bắn thì ghi **một dòng log cảnh báo** rồi chạy tiếp — không có máy tự hạ cấp, vì hậu kiểm mới là lớp quyết định |
| Độ phủ `apply_patch` của hook còn ngờ theo research, và Codex ghi file được cả bằng lệnh shell | hook bỏ sót đường ghi file | khai đủ **hai** matcher `apply_patch` và `Bash`; nhánh `Bash` trích đường ghi cho năm dạng `>`, `>>`, heredoc, `tee`, `mv`; và hậu kiểm không phụ thuộc hook nên tính đúng đắn không đổi |
| `.codex/hooks.json` ở gốc repo áp lên cả phiên Codex của **người dùng** | người dùng bị chặn ngoài ý muốn khi tự dùng Codex trong repo | gate chỉ deny khi có bằng chứng đang chạy dưới mode (biến môi trường do `tdq_codex.py run` đặt); ngoài mode thì chỉ nhắc, cùng triết lý `bash_gate.py` |
| Trên máy này `codex` chạy `ag/gemini-3.8-flash-medium` qua router nội bộ, không phải model của Codex | chất lượng task khác hẳn kỳ vọng | ghim model qua `-m`, nguồn giá trị theo đúng thứ tự ở đầu ra 4, thiếu thì fail; ghi tên model thật vào log mỗi task |
| `CODEX_HOME` tạm không còn ai xoá: kiến trúc bản 1.0 có bước dọn theo đợt, bản 1.2 chạy tuần tự thì không | thư mục tạm mang `auth.json` nằm lại trên máy | `tdq_codex.py cleanup` là chủ sở hữu tường minh của việc xoá; DoD có một dòng riêng cho nó |
| Mode dễ bị hiểu là "mode nhanh" trong khi chạy tuần tự nó ngang `main` | người dùng chọn mode vì tốc độ rồi thất vọng | `simulate` in thời gian mode `codex` cạnh `main` bằng số đo thật; hằng số phải có `so_mau >= 3`; cổng chọn mode không mô tả mode này là nhanh hơn |
| 17 file test đang nhắc `subagent`, riêng bộ kiểm mode/phase có 16 ca | sửa `VALID_MODES` làm đỏ hàng loạt | M2 làm trước và chạy full suite ngay; ưu tiên sửa test sang vòng lặp trên `VALID_MODES` thay vì liệt kê tay |
| Một lượt Codex mất ~5s khởi động cố định | plan nhiều task nhỏ thì phần khởi động chiếm phần lớn thời gian | `simulate` tính cả phần khởi động cố định vào thời gian mode `codex`, nên plan nhiều task vụn sẽ tự thua ở con số chứ không cần luật riêng |

## 6. QC & Definition of Done

| # | Hạng mục kiểm | Điều kiện PASS |
|---|---|---|
| Q1 | Cổng năng lực trên máy CÓ Codex | `check --json` trả `co=true`, `chay_duoc=true`, `phien_ban` khớp `codex --version`; `tdq_state.py modes --json` trả **3** mode `chon_duoc=true` |
| Q2 | Cổng năng lực trên máy KHÔNG có Codex | dò giả lập `shutil.which` trả None → exit 0, `co=false`, `ly_do` là `chưa cài`, `goi_y` có lệnh cài; `modes --json` trả 3 mode nhưng mode `codex` có `chon_duoc=false` và `ly_do` không rỗng |
| Q3 | Bốn nguyên nhân không chọn được phân biệt được | bốn ca (chưa cài · chạy được nhưng lỗi · quá hạn · người dùng từ chối) trả bốn `ly_do` khác nhau, mỗi cái một câu sửa khác nhau |
| Q4 | Chặng cài đặt không tự cài | `tdq_checkportable.py setup` khi chưa có cờ đồng ý thì **không** ghi file nào vào `.codex/`, chỉ in lệnh và câu hỏi; exit 0 |
| Q5 | Mode thứ ba vào được state | `normalize_mode` nhận `codex`, `codex implement`, `codex-implement`; ghi được mode `codex`; `tdq_status` in nhãn `codex implement` |
| Q6 | Bảng tra thay rẽ nhánh cứng, đo bằng vòng lặp trên `VALID_MODES` | phép kiểm chạy vòng qua **từng** mode trong `VALID_MODES` và đòi `phase_row` trả hàng đúng cho mọi mode; thêm một mode giả vào bảng thì nó cũng phải qua, và **không** sửa thân hàm — tức "mode mới chỉ cần thêm một dòng bảng" là câu đo được, không phải câu đếm chuỗi trong source |
| Q7 | Mode nào đi qua đội được khai tường minh | mode trong `VALID_MODES` mà thiếu khai → lỗi ngay lúc nạp bảng; `canh_bao_lach_luat` vẫn cảnh báo đúng như cũ cho `subagent`, và không cảnh báo cho `codex` vì đã khai, không vì rơi nhánh mặc định |
| Q8 | Lệnh gọi Codex dựng đúng, đối chiếu với bảng cờ | phép kiểm đọc **hằng số bảng cờ** rồi khẳng định lệnh sinh ra mang đủ mục trong bảng — không liệt kê lại tên cờ lần thứ hai; cộng ba tính chất rời: stdin không phải TTY, có timeout, `-C` trỏ gốc repo |
| Q9 | Bảng phán quyết: bốn trạng thái không lẫn nhau | ca quá hạn → `timeout`; ca hook chặn → `deny`; ca test đỏ → `fail`; ca xong → `xong`; và **ba ca cùng `exit=0`** (xong · deny · sandbox chặn) ra ba trạng thái khác nhau |
| Q10 | Kết quả đọc từ file có khuôn | file `-o` thiếu, rỗng, hoặc không khớp `--output-schema` → task FAIL, không được coi là xong |
| Q11 | Hậu kiểm vùng file, mốc là chính task | repo có một file lệch `VÙNG FILE` → FAIL và in đúng tên; không lệch → PASS; module chạy được mà không cần `tdq_codex`; và ca quyết định: **dựng sẵn một file đã sửa-chưa-commit từ "task trước", rồi chạy hậu kiểm của "task sau" → PASS**, vì mốc là sha của task sau chứ không phải `HEAD` |
| Q12 | Mốc hoàn tác, gồm ca cây sạch và ca index | file đã theo dõi bị sửa ngoài vùng → trả về đúng nội dung lúc chụp mốc; file mới ngoài vùng → bị xoá; phần việc trong vùng **không** bị chạm; **cây sạch → mốc là `HEAD`**; và **index không đổi sau khi hoàn tác** (`git diff --cached --name-only` trước và sau bằng nhau) — ca này đỏ nếu ai đó dùng `git checkout <sha> -- <file>` |
| Q13 | Sandbox chặn ghi ra ngoài repo | chạy thật một lượt Codex ghi một đường dẫn tuyệt đối **ngoài repo và ngoài cả `/tmp` cùng `$TMPDIR`** (ba vùng sandbox cho ghi) → không có file được tạo. `check` báo không chạy được → hạng mục này **SKIP có tuyên bố**, ghi rõ lý do trong báo cáo QC, không tính là PASS |
| Q14b | Vùng khoá được tôn trọng | Codex sửa file test của task → FAIL kèm tên file, **kể cả khi test chạy xanh**; hook nhận payload ghi vào vùng khoá → `permissionDecision: deny` |
| Q14c | Nhịp red → green chia đôi | với một task mẫu: trước khi gọi Codex, test đã tồn tại và **chạy ra đỏ**; sau khi Codex xong, cùng test đó xanh; log của task ghi cả hai mốc đỏ và xanh; ca Codex sửa test để làm xanh bị Q14b bắt |
| Q14d | `.codex/hooks.json` gốc repo chỉ hai event | file có đúng hai nhóm `PreToolUse` với matcher `apply_patch` và `Bash`; **không** có khoá `Stop`, `UserPromptSubmit`, `SessionStart`; một phép kiểm khẳng định file này không do hàm sinh bundle tạo ra |
| Q14e | Build không đè `.codex/` viết tay | chạy `build_portable.py` rồi so `.codex/config.toml` và `.codex/hooks.json` ở gốc repo trước/sau: không đổi một byte |
| Q14 | Hook deny chặn thật, cả hai matcher | `codex_edit_gate.py` nhận payload `apply_patch` ghi ngoài vùng → `permissionDecision: deny` kèm mã `[TDQ:*]`; payload `Bash` ghi ngoài vùng ở năm dạng `>`, `>>`, heredoc, `tee`, `mv` → cả năm đều deny; chạy thật một lượt với hook đã nối → file **không** được tạo; ngoài mode `codex` → chỉ nhắc |
| Q15 | Hook được nối đúng, không có máy tự hạ cấp | mọi lệnh Codex đều mang `--dangerously-bypass-hook-trust`; phép kiểm khởi động thấy hook không bắn → **đúng một dòng log cảnh báo** và chạy tiếp; không có nhánh code nào tự đổi cấu hình hay tự bớt lớp |
| Q16 | Vòng đời `CODEX_HOME` | `tdq_codex.py cleanup` xoá hết thư mục tạm của mode; gọi khi không có gì để xoá vẫn exit 0; sau `cleanup` không còn thư mục nào sót |
| Q17 | Không rò khoá | không đầu ra nào của `tdq_codex.py` chứa chuỗi `Bearer`; `CODEX_HOME` tạm có quyền `700` |
| Q18 | Nguồn tên model | có cờ `--model` → dùng nó; không có cờ mà cờ cài đặt có `codex_model` → dùng khoá đó; không có cả hai → **fail kèm câu sửa**, không rơi về mặc định |
| Q19 | Log đủ để debug mà không rò ra repo công khai | mỗi lần gọi Codex có một dòng log chứa timestamp, task, **tên model thật**, `CODEX_HOME` đã dùng, thời gian tường, trạng thái, **sha256 của prompt** và phần đầu prompt đã qua `mask_secrets`; không file nào được git theo dõi chứa nguyên văn prompt; file log nguyên văn có mặt trong `.gitignore` |
| Q20 | Danh sách mode là một nguồn duy nhất, máy đọc được | `modes --json` là nguồn của cổng chọn; chữ cái người dùng gõ map về mode bằng đúng danh sách vừa in, nên ca 2 lựa chọn và ca 3 lựa chọn đều map đúng; không còn phép `"subagent" if x == "main" else "main"` |
| Q21 | Tầng luật không còn kể mode theo cặp nhị phân | một phép kiểm quét 8 file luật ở đầu ra 14 và khẳng định không còn chỗ nào kể mode dưới dạng cặp `main`/`subagent` cứng; `tdq_state.py` không import `tdq_codex` |
| Q21b | Biến mốc của mode sống qua sandbox | tên biến không chứa `KEY`, `TOKEN`, `SECRET`; chạy thật một lượt Codex in biến đó ra file trong repo → giá trị đúng (đã đo được một lần ở vòng 2026-09-11, phép kiểm giữ lại để bản Codex sau không lặng lẽ đổi) |
| Q22 | Hiệu năng nói bằng số đo, và tương thích ngược | file hằng số **thiếu** khoá Codex → `simulate` cho `main`/`subagent` chạy đúng như trước, chỉ bỏ dòng mode `codex` kèm một câu lý do; **có** khoá → in thời gian mode `codex` cạnh `main`; `so_mau < 3` → từ chối; không hệ số nào viết cứng |
| Q23 | Ba mẫu đo lấy từ việc thật | ba dòng log của Q19 sinh ra **trong lúc implement chính request này** là nguồn của `calibrate`; không chạy vòng benchmark tổng hợp riêng chỉ để lấy mẫu |
| Q24 | Toàn bộ suite còn xanh | toàn bộ test của repo xanh hết, kể cả 17 file đang nhắc `subagent` |
| Q25 | Bundle sinh lại đúng | `build_portable.py` đọc `hooks/scripts/codex_edit_gate.py` từ đĩa (không còn chuỗi `ADAPTER_CODEX` nhúng); bundle sinh ra có file đó và có `.codex/hooks.json` khai đủ hai matcher |
| Q26 | Tầng tài liệu nhất quán | `doc_lint.py` trên spec/plan exit 0; `i18n_check.py` quét `scripts/ hooks/ skills/ agents/` exit 0; file luật chỉ nêu tên lệnh, không chép logic |

**DoD** — tuyên bố xong khi tất cả đúng:

- 20 đầu ra ở §2 (1–17 kèm 7b, 12b, 12c) đều tồn tại và đo được đúng cột "Đo xong bằng".
- Q1 đến Q26 kèm Q14b–Q14e và Q21b đều PASS (Q13 được phép SKIP có tuyên bố khi máy không chạy
  được Codex), do `tdq-qc-tester` chạy lại chứ không phải tôi tự nhận.
- Mỗi task đã tick đều chứng minh được nhịp chia đôi: test đỏ trước khi gọi Codex, xanh sau đó,
  và file test không nằm trong diff của Codex.
- Hàng rào được chứng minh bằng **hiệu ứng thật** (file không được tạo, file được trả về mốc,
  task FAIL), không phải bằng exit code hay lời tự báo.
- Toàn bộ suite test xanh; `doc_lint.py` exit 0; `i18n_check.py` trên tầng 1-2 exit 0.
- Bundle `portable_claude/` và `portable_codex/` được sinh lại, không sửa tay.
- `tdq_codex.py cleanup` đã chạy và không còn `CODEX_HOME` tạm nào sót lại.
- Mode `main` và `subagent` không đổi hành vi: chạy lại nguyên bộ test của chúng thấy xanh, và
  `simulate` với file hằng số **cũ** vẫn cho đúng kết quả như trước.

## 7. Câu hỏi còn mở

Rỗng. Vòng 1 sáu câu đã trả lời (`1abc 2a 3a 4a 5a` cộng yêu cầu cổng năng lực hai chặng ở câu
6); vòng 2 hai câu đã trả lời (`1a` bỏ file trong `agents/`, hợp đồng vai sang `skills/`; `2a`
mốc hoàn tác git thay worktree tạm). Bốn ẩn số kỹ thuật còn lại đã đóng bằng phép đo trên máy chứ
không bằng suy đoán: Codex có cần feature flag hay không, hook có tự chạy hay không, deny có chặn
thật hay không, `CODEX_HOME` riêng có chạy hay không.

### Đối chiếu 18 finding của `tdq-reviewer` (bản 1.1 → 1.2)

| Finding | Xử lý | Ở đâu trong bản 1.2 |
|---|---|---|
| 1. `exit=0` phủ ba ca, cần bảng phán quyết | NHẬN | đầu ra 5, Q9 |
| 2. Danh sách cờ bị kể hai chỗ | NHẬN | đầu ra 3, Q8 (đối chiếu với bảng, không liệt kê lại) |
| 3. Bắt buộc chuỗi `< /dev/null` buộc `shell=True` | NHẬN | §4 đổi thành "stdin không phải TTY", đầu ra 3, dòng rủi ro 1 |
| 4. Không còn ai xoá `CODEX_HOME` | NHẬN | đầu ra 6 (`cleanup`), Q16, DoD, dòng rủi ro mới |
| 5. Giá trị `-m` lấy từ đâu | NHẬN | đầu ra 4, §3, §4, Q18 |
| 6. Hai matcher và đường ghi bằng lệnh shell | NHẬN | đầu ra 12, Q14, dòng rủi ro `apply_patch` |
| 7. Đã có `codex_edit_gate.py` sinh sẵn, đừng thêm file cùng vai | NHẬN | đầu ra 12 và 16, M5, M9, §3, Q25 |
| 8. Còn 5 file luật kể mode theo cặp nhị phân | NHẬN | đầu ra 14 (8 file), M7, Q21 |
| 9. Hệ số Codex làm chết file đo cũ | NHẬN | đầu ra 15, Q22, dòng rủi ro mới |
| 10. Cây sạch thì `git stash create` trả rỗng | NHẬN | đầu ra 7, §3, Q12, dòng rủi ro mới |
| 11. "Hiện 2 hay 3 lựa chọn" không đo được | NHẬN | đầu ra 10 (`modes --json`), Q1, Q2, Q20 |
| 12. Đích thử sandbox phải ngoài cả `/tmp` và `$TMPDIR` | NHẬN | Q13, kèm SKIP có tuyên bố |
| 13. Q6 đếm chuỗi trong source thì lách được | NHẬN | Q6 đổi thành vòng lặp trên `VALID_MODES` |
| 14. M2 không được phụ thuộc M1 cũ, state phải đi trước | NHẬN | state thành M1, phụ thuộc = không; §2b có đoạn riêng; Q21 cấm import |
| 15. Đo hệ số tốn thêm vòng chạy | NHẬN CÓ SỬA | giữ module hệ số (người dùng chọn 1C), nhưng ba mẫu lấy từ log lúc implement — Q23 |
| 16. Cơ chế tự hạ cấp là nhánh không ai chạy | NHẬN | bỏ hẳn; §3 và Q15 chỉ còn một dòng log cảnh báo |
| 17. Logic vùng file bị khoá trong tầng Codex | NHẬN | `scripts/tdq_vungfile.py` thành M2, đầu ra 7, §2b, §3 |
| 18. Dòng trạng thái chưa ghi việc đã duyệt | NHẬN | dòng `Trạng thái` ở đầu file |

### Bảy chỗ thêm ở vòng đo 2026-09-11 (bản 1.2 → 1.3, user chọn `1a 2a`)

| Chỗ | Vì sao là lỗi | Ở đâu trong bản 1.3 |
|---|---|---|
| A. Hậu kiểm không có mốc so sánh | task sau FAIL oan vì việc chưa commit của task trước | đầu ra 7, §3, §4, Q11, dòng rủi ro |
| B. Hoàn tác bằng `git checkout … -- <file>` ghi cả index | làm mù hậu kiểm của task sau đúng ở file đáng nghi nhất | đầu ra 7, §3, Q12, dòng rủi ro |
| C. `.codex/hooks.json` gốc repo nếu sinh bằng hàm sinh bundle sẽ mang 5 event | `stop_gate.py` giữ lượt Codex lại, `prompt_context.py` bơm `[TDQ:*]` vào prompt của nó | đầu ra 12b, §3, Q14d, dòng rủi ro |
| D. Test do chính người bị kiểm viết | test rỗng nghĩa vẫn xanh, task vẫn được tick | §1, đầu ra 7b và 14, §3, §4, Q14b, Q14c, dòng rủi ro |
| E. `.codex/config.toml` gốc repo là file viết tay đã được git theo dõi | lần build sau đè mất cấu hình thật của người dùng | đầu ra 12c, §3, §5, Q14e, Q21b |
| F. Sandbox cho ghi cả `/tmp` và `$TMPDIR` | câu "khoanh Codex trong repo" là nói quá | §3, Q13, dòng rủi ro |
| G. Log ghi nguyên văn prompt vào repo công khai | nội dung file lọt vào lịch sử git công khai | đầu ra 17, §4, Q19, dòng rủi ro |

Hai chỗ nghi ở cùng vòng đó đã bị **phép đo bác bỏ**, ghi lại để không ai điều tra lại: biến môi
trường tự đặt không bị `inherit = "core"` cắt (lượt thử in ra đúng giá trị), và Codex **không**
commit được vì sandbox chặn ghi `.git/` (`index.lock: operation not permitted`).
