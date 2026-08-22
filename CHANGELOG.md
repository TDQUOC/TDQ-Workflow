# Changelog

Mới nhất trên cùng. Ngày theo múi giờ máy phát hành.

## 0.29.0 — 2026-08-22

Đóng sổ mà còn ô tick trống thì hook nhắc. Trước bản này `plan_tick_state()` chỉ đếm ô có mã
task in đậm, nên mọi dòng Definition of Done đều vô hình: plan tick đủ task là `all_done` bật
True dù cả 19 dòng DoD còn trống. Chốt chặn `[TDQ:TICK]` lại chỉ bắn ở phase `implement` và
`qc` — đúng lúc đóng sổ ở `report` thì không còn ai canh, bảo hiểm duy nhất là một câu văn
xuôi trong khuôn report dựa vào trí nhớ của model.

- **Nhắc `[TDQ:DOD]` ở phase `report` và `idle`**: bắn khi QC đã PASS sạch mà ô tick còn
  trống, nêu cả số task lẫn số dòng DoD còn lại. Nó **chỉ nhắc, không chặn** — turn vẫn kết
  thúc bình thường. Nhắc xếp đầu danh sách hint để không bị cắt mất khi đã có bốn nhắc khác.
- **Ba bộ đọc riêng trong `scripts/tdq_state.py`**: `dod_tick_state()`, `qc_result_state()`,
  `task_open_count()`. Cố ý KHÔNG nới `_TASK_LINE`: bốn nơi phụ thuộc hợp đồng trả về của
  `plan_tick_state()`, nới ra là lệch `all_done` và lệch cả ETA của status line.
- **Bốn cửa im lặng** giữ cho hook chạy ở user scope không cằn nhằn nhầm: sai phase · mục DoD
  không dùng ô tick (plan viết trước đây đếm 0, không bao giờ bị nhắc) · đã tick đủ · file qc
  chưa có, còn FAIL, hoặc còn hạng mục chưa kết luận.
- **Hai khuôn skill cập nhật theo**: plan bắt DoD viết dạng ô tick, report bước 8 nói rõ phải
  tick CẢ HAI loại ô — ô task từng phase và ô Definition of Done.
- **Bộ dò trùng lặp tài liệu `scripts/doc_dup.py`**: cắt shingle, gộp khối, đếm token bằng bộ
  đếm thật trong `.venv-tokens`; thiếu thư viện thì thoát mã 3 chứ không lùi về ước lượng
  ký-tự-chia-bốn. Kèm hồ sơ rà soát bốn mặt và bảng top 10 đề xuất tối ưu.

## 0.28.0 — 2026-08-22

Worktree do workflow đẻ ra không còn nằm lại ăn disk. Trước bản này, mode đội tạo worktree
cho từng task rồi bỏ đó: không ai nhớ có bao nhiêu cái, cái nào merge rồi, cái nào còn việc
chưa commit. Nay có sổ, có lệnh quét, và có ba chốt kiểm không cho quên.

- **Sổ worktree sống xuyên request**: `docs/tdq/worktrees.json` (máy đọc) +
  `docs/tdq/worktrees.md` (người đọc), ghi qua đúng một cửa là `scripts/tdq_team.py`.
  Module `scripts/tdq_worktree_registry.py` (mới) thuần dữ liệu, không gọi git một lần nào,
  nên ba nơi đọc nó — lệnh đội, cổng state, hook — dùng chung một khuôn. Cả hai file đã
  gitignore: chúng chứa đường dẫn tuyệt đối của máy bạn.
- **Lệnh mới `soat` / `soat --don`**: quét mọi worktree của MỌI request, in bảng tuổi ·
  dung lượng · sạch · đã merge, cảnh báo khi tổng vượt 500 MB hoặc một worktree quá 7 ngày.
  Chỉ đụng tới bên trong `.tdq-worktrees/`; thư mục ngoài vùng đó chỉ được liệt kê, không
  bao giờ bị xoá — nó có thể là chỗ làm việc của chính bạn.
- **Xoá cần đủ ba điều kiện**, không bao giờ theo cảm tính: sạch · nhánh đã nằm trong nhánh
  tích hợp · git không giữ khoá. Thiếu một điều là KHÔNG xoá gì cả. `hop` tự dọn worktree và
  nhánh task khi đủ ba, giữ nhánh tích hợp.
- **Worktree chưa dọn được luôn kèm đường ra**: khối `NOT CLEANED UP YET` in cuối kết quả
  lệnh, mỗi lý do chặn có ít nhất một phương án chạy được thật. Skill bắt đặt khối đó ở cuối
  turn theo `doc_lang` của user, lệnh giữ nguyên văn. Năm lý do đóng: còn việc chưa commit ·
  file bị gitignore mà không sinh lại được · chưa merge · git khoá · git từ chối vì lý do
  khác. Lý do thứ hai đáng giá nhất: một `.env` bị `git worktree remove` xoá là mất hẳn.
- **Ba chốt không cho quên**: `hop` kiểm ngay sau khi merge · `tdq_state.py set phase=qc`
  từ chối mở khi sổ còn dòng mở · hook in một dòng `[TDQ:WORKTREE]` mỗi turn cho tới khi
  sạch. Sổ thiếu hoặc hỏng thì cả ba đều im lặng đi tiếp, không bao giờ giết turn.
- QC độc lập chạy 2 lượt, bắt 16 khiếm khuyết, sửa 15 qua 3 vòng fix. Đáng kể nhất: `mo`
  kiểm ghi được sổ TRƯỚC khi tạo worktree nên không đẻ worktree mồ côi. Kế đó là bỏ
  `--force` khỏi mọi `worktree remove`, để git giữ vai lưới an toàn cuối. Chi tiết:
  `docs/tdq/qc/2026-08-22-1033-quan-ly-worktree.md`.

Còn nợ: vẫn chưa chấm lại bộ `evals/tuan-thu` trên cây đã dịch (nợ từ 0.27.0).

## 0.27.0 — 2026-08-22

Bộ workflow nói được với người dùng ở mọi ngôn ngữ. Luật viết bằng tiếng Anh — thứ model
đọc chính xác nhất và tốn ít token nhất — còn tài liệu sinh ra cùng mọi câu nói với user
đi theo ngôn ngữ của chính user. Trước bản này, muốn dùng workflow là phải đọc được tiếng
Việt.

- **Ngôn ngữ chia 3 tầng**, ghi ở mục `## 0. Language` của `tdq-conventions/SKILL.md`:
  luật (`skills/`, `agents/`, chú thích + docstring của `hooks/` và `scripts/`) và chuỗi
  máy in ra viết TIẾNG ANH cố định, không bảng tra i18n; tài liệu và lời thoại viết theo
  trường `doc_lang`.
- `doc_lang` khai đúng một lần lúc mở request — `tdq_state.py init <slug> <lane> --lang <mã>`
  — và cố định suốt request. Thiếu cờ hoặc state cũ không có trường thì lùi về `vi`, state
  đời trước đọc lên không lỗi.
- Đã dịch: 44 file `skills/**/*.md`, 3 file `agents/*.md`, toàn bộ `hooks/` và `scripts/`.
  Đếm bằng `i18n_check.py`: `skills/`+`agents/` 1127 → 0 dòng tiếng Việt, `hooks/`+`scripts/`
  3099 → 0. Description của 7 skill dài thêm về ký tự (1063 → 1334) nhưng **giảm nửa về
  token** (628 → 304, đo bằng `anthropic-tokenizer`) — đây là phần luôn nằm trong system prompt.
- `scripts/i18n_check.py` (mới): quét một vùng đường dẫn, tách 3 loại dòng
  (`--kind comment|string|body`), exit 1 khi còn sót. Cụm `i18n-allow` trên dòng là cửa
  miễn cho chuỗi user thấy phải giữ nguyên từng chữ; một dòng chú thích HTML ngay trên
  khối ``` miễn cho cả khối khuôn mẫu.
- Cổng duyệt nhận **tiếng Anh** ("approve spec", "approve plan") và **một chữ cái** `a`–`d`
  ở cổng mode, đúng như bộ ca âm cũ vẫn phải trượt. Hai ca eval mới
  (`duyet-spec-tieng-anh`, `duyet-bang-chu-cai`) khoá hai đường này; bộ `evals/tuan-thu`
  đi từ 10 lên 12 ca.
- Gộp 6 commit chưa phát hành trước đó. Về context: bộ skill chuyển thể lai · thước đo
  đếm token thật cộng luật cắt output · phẳng hoá reference về tầng 1. Về lỗi đọc plan:
  `doc_plan` không còn nuốt dòng `Chạm:`/`Cần:` khi mô tả task xuống dòng · mã task có
  chữ sau số (`T2A.1`, `T2.4b`) không còn vô hình.

Còn nợ: chưa chấm lại bộ `evals/tuan-thu` trên cây đã dịch — xem mục "Giới hạn" của
`docs/tdq/reports/2026-08-21-2351-quoc-te-hoa-workflow.md`.

## 0.26.0 — 2026-08-18

Cổng duyệt thôi kêu oan. Đo trên 58 request có spec: 7 ca phải xin duyệt lại, trong đó
5 ca là hệ quả của chính thiết kế chứ không phải người dùng làm sai
(`docs/tdq/reports/2026-08-18-2050-spec-doi-sau-khi-duyet.md`). Cổng kêu vì lý do vô hại
nhiều lần thì lúc nó kêu đúng cũng không còn ai nghe.

- `tdq_state.sha256_noi_dung()`: `spec_sha256`/`plan_sha256` băm PHẦN NỘI DUNG, tính từ
  heading `##` đầu tiên. Vùng đầu file (Ngày, Bản, Trạng thái, đường dẫn brief) là sổ sách
  của chính workflow — ghi sổ không còn bị coi là "tài liệu đổi sau khi duyệt". Không có
  heading `##` thì băm cả file. Ba nơi so băm (`tdq_state`, hook `prompt_context`,
  `tdq_checkstatus` ca lệch D3) dùng chung đúng một hàm.
- `doc_lint` rule **R11**: spec có slug từ 2026-08-19 trở đi không được ghi đường dẫn
  `tests/test_*` hay cờ `-k` trong §6 — spec giữ ĐIỀU KIỆN PASS, lệnh kiểm là việc của
  plan. 58 spec sẵn có không bị đụng tới.
- Khuôn spec §6 đổi cột "Cách kiểm" thành "Điều kiện PASS", có bảng ĐÚNG/SAI;
  `qc.md` bỏ đoạn dặn chịu đựng sha lệch.
- `tdq_state.cong_dang_cho()`: cổng duyệt còn thiếu tính theo ĐÚNG lane, `stop_gate` và
  `edit_gate` dùng chung. Trước đó `stop_gate` duyệt danh sách cứng
  `("spec", "plan", "quick")` nên lane quick — vốn không có cổng `spec` — luôn bị nhắc
  "spec vẫn chưa được ghi nhận duyệt", kể cả với request đã duyệt và đã đóng sổ.
  `edit_gate` khi lane rỗng/lạ nay nhắc cổng đầu tiên thay vì im lặng.

## 0.25.0 — 2026-08-18

Mode đội: leader chia việc, agent con chạy song song — và tính modular chuyển thành thuộc
tính của TÀI LIỆU, không còn phụ thuộc mode thực thi.

- `scripts/tdq_team.py`: bản đồ phân công (`phan-cong`, `kiem-ke`, `cum`, `mo`, `kiem`,
  `hop`, `don`), trần 4 nhánh một đợt. Hook `[TDQ:TEAM]` chặn leader tự gõ code của task
  đã hứa giao; file ngoài project được miễn vì bản đồ không nói gì về vùng đó.
- `scripts/tdq_bench.py`: đo và mô phỏng main so với đội, `mo-phong --plan <file>` đọc plan
  thật để cổng đề xuất mode không phải chép lại luật chia đợt.
- Khuôn spec thêm mục ranh giới module; plan luôn khai `Chạm:` và dựng `## Cụm song song`.
  Lane quick được sinh agent con khi mini-plan có từ 3 task tách rời trở lên.
- `scripts/skill_router.py`, `scripts/skill_tokens.py`: đo và định tuyến chi phí context
  của bộ skill.

## 0.24.0 — 2026-08-17

`portable_codex/` thôi làm markdown đọc tay, chuyển sang dùng đúng ba lớp native của Codex
CLI. Giả định trong 0.23.0 — "Codex không có hệ thống skill/hook" — đã sai với bản hiện tại:
thăm dò bằng `codex exec` thật (`codex-cli 0.147.0-alpha.6.5`) cho thấy Codex tự quét
`.agents/skills/`, đọc `.codex/config.toml` cho MCP và `.codex/hooks.json` cho hook.

- `build_portable.py` sinh thêm cho bản codex: `.agents/skills/` (8 skill), `.codex/config.toml`
  (`[mcp_servers.*]`, khai bằng `env_vars` vì Codex KHÔNG nở `${VAR}` trong TOML), và
  `.codex/hooks.json` (4 event / 5 hook, lệnh dùng đường dẫn tương đối vì hook chạy với
  cwd = gốc project). `hooks/` và `scripts/` nằm cạnh nhau ở gốc bundle theo ràng buộc của
  `_common.py`. `workflow/NN-*.md` giữ nguyên làm bản dự phòng cho harness khác.
- Sinh thêm `hooks/scripts/codex_edit_gate.py`: Codex sửa file bằng tool `apply_patch` với
  `tool_input.command` là thân patch và KHÔNG có `file_path`, nên adapter rút đường dẫn từ
  patch rồi gọi lại `edit_gate.py`. Hook gốc trong repo không bị sửa.
- `tdq_checkportable.py` thêm `setup --trust`: ghi `[projects."<path>"] trust_level = "trusted"`
  vào `~/.codex/config.toml` (hoặc `$CODEX_HOME`), luôn sao lưu `<file>.tdq-bak-<timestamp>`,
  không ghi chồng block đã có. `check` báo thêm dòng trạng thái trusted.
- Codex có HAI cổng tin cậy độc lập: trust project (mở được bằng `--trust`) và trust hash của
  hook, chỉ duyệt được trong giao diện. README/AGENTS.md/SKILL.md đổi từ "ba việc máy không
  tự làm được" thành bốn.
- README của cả hai bundle có mục `## Cài ở máy mới` liệt kê từng bước theo thứ tự; bản codex
  thêm mục ba cách trust và giải thích vì sao bước kiểm đầu tiên phải chạy thẳng file thay vì
  gọi skill. Test khoá mọi đường dẫn lệnh nêu trong README phải có thật trong chính bundle.

## 0.23.0 — 2026-08-17

Bản portable thôi viết tay, chuyển sang tự sinh — và tách làm hai bản cho hai loại harness.
`portable/` cũ là bản chép tay, README của chính nó ghi "sửa `skills/` xong nhớ đồng bộ
tay", còn test khoá đồng bộ đã bị xoá từ 0.10.0: nó đã trôi khỏi bản gốc mà không ai biết.

- Thêm `scripts/build_portable.py`: sinh `portable_claude/` (Claude Code: `.claude/skills`,
  `.claude/agents`, 5 hook trong `.claude/settings.json`, `.mcp.json`) và `portable_codex/`
  (markdown thuần: `AGENTS.md` + `workflow/NN-*.md`) từ MỘT nguồn.
- Bản claude đặt `hooks/` và `scripts/` cạnh nhau dưới `.claude/tdq/` vì `_common.py` suy
  thư mục scripts bằng `../../scripts`; mọi `${CLAUDE_PLUGIN_ROOT}` được đổi kèm đúng tiền
  tố đó, và số lần thay được đối chiếu để bắt file bị bỏ sót.
- Thêm `scripts/tdq_checkportable.py` + skill `tdq-checkportable` (nguồn ở `portable_src/`,
  không tính vào ngân sách context của bộ chính): đối chiếu sha256 theo `manifest.json`,
  kiểm Python/lệnh ngoài/MCP, `setup` tự vá và luôn sao lưu `<file>.tdq-bak-<timestamp>`.
- `.mcp.json` sinh ra chỉ ghi TÊN biến môi trường, không bao giờ ghi giá trị khoá.
- Xoá `portable/` viết tay; `.graphifyignore` loại ba thư mục portable mới.

## 0.22.0 — 2026-08-16

Clean code thôi làm cổng hỏi, thành luật thường trực. Trước bản này mỗi request chạm mã
nguồn phải trả lời "Bật clean code cho request này chứ?", rồi cuối request chạy
`scripts/code_rule_scan.py`. Cổng đó tốn một lượt hỏi mà không trả lại bảo đảm nào:
script phụ thuộc linter cài sẵn trên máy, request trước vừa báo `CHƯA KIỂM ĐƯỢC — thiếu
ruff` cho cả 5 file Python.

- Luật mới `skills/tdq-conventions/references/clean-code.md`: 5 nguyên tắc SOLID, mỗi
  nguyên tắc hai bản đọc (khi có class / khi chỉ có hàm và module) vì repo này có 4 class
  trên 280 hàm. LSP mang nhãn giới hạn: bản đọc cho hàm là suy diễn, không phải trích
  Liskov. Mỗi nguyên tắc kèm một ví dụ ĐÚNG và một ví dụ SAI trỏ vào file thật.
- `tdq-conventions/SKILL.md` §11 nạp luật này mỗi turn; trần dòng của skill nới 130 → 133.
- Gỡ cổng hỏi: `tdq-spec/SKILL.md` bỏ bước 1b, `spec-template.md` bỏ dòng
  `Clean code: BẬT|TẮT` và mục `## Khuôn hỏi clean code`.
- QC: hạng mục cố định thứ tư QC-F4 — trả lời checklist 5 câu có/không, câu nào "không"
  thì sửa code rồi ghi chỗ đã sửa. Đổi khớp ở cả `skills/` và `portable/`.
- Xoá `scripts/code_rule_scan.py`, `tests/test_code_rule_scan.py`,
  `tests/test_clean_code_workflow.py` (graphify xác nhận script là lá, không ai gọi).
- Bù kiểm bằng lệnh: `doc_lint` R9 phủ thêm `clean-code.md`, và
  `tests/test_clean_code_rule.py` (20 test) khoá hình dạng file luật.

## 0.21.0 — 2026-08-16

Skill thứ bảy: `tdq-check-status` — dò lại một request đang dở rồi tiếp tục mà không mất
dữ liệu cũ. Trước bản này, mất ngữ cảnh là mất luôn chỗ dừng: `tdq-status` chỉ đọc lại
`state.json`, mà `state.json` chính là thứ có thể sai. Ba tình huống đã gặp: session chết
phải mở session mới, đổi sang máy khác, và giao một phase cho agent ngoài rồi quay lại.

- Nguyên tắc mới: **đĩa là bằng chứng, `state.json` là lời khai**. Bộ dò đọc
  `docs/tdq/**`, git (`log -20`, `status --short`) và working log hôm nay, rồi đối chiếu
  với state. Lệch nhau thì tin đĩa.
- `scripts/tdq_checkstatus.py report [--json]`: chỉ ĐỌC, không bao giờ ghi `state.json`.
  Nó chấm 11 ca lệch D1–D11 theo một bảng cứng, không để model tự nghĩ chẩn đoán.
- Ba mức kết luận: `TIẾP TỤC ĐƯỢC` · `VÁ RỒI TIẾP TỤC` · `CẦN USER QUYẾT`.
- **Luật không mất dữ liệu.** Lệnh vá chỉ thuộc hai họ `tdq_state.py set …` và
  `tdq_state.py approve …`. Một hàm chặn nội bộ ném lỗi nếu mẫu lệnh chạm tới lệnh khởi
  tạo lại, lệnh đặt về mặc định, `rm`, `mv` hay chuyển hướng ghi đè.
- Một cổng gật duy nhất: trình báo cáo → user gật một lần → chạy hết lệnh vá → đi tiếp.
- `skills/tdq-check-status/` có 7 bước, khuôn báo cáo 6 mục và bảng D1–D11; bản
  `portable/workflow/05-check-status.md` khớp từng bước cho agent ngoài Claude Code.
- `tdq-status` giữ nguyên vai trò báo nhanh, chỉ thêm một dòng trỏ sang skill mới.
- Trần tổng `description` của skill nới 900 → 1080 ký tự cho skill thứ bảy.

## 0.20.0 — 2026-08-15

Tên file document mang thêm giờ phút, và workflow tự đếm thời gian: mỗi request tốn bao
lâu, mỗi phase tốn bao lâu. Trước bản này `state.json` chỉ có `updated_at` và ba mốc duyệt
— không suy ra được phase nào ngốn thời gian, nên mọi nhận định về "chậm ở đâu" đều là đoán.

- Slug mới: `YYYY-MM-DD-HHMM-<kebab ≤5 từ, không dấu>`, giờ chèn sau ngày để sort tên trùng
  sort thời gian. **Hai định dạng cùng sống.** Slug cũ chỉ có ngày vẫn ĐỌC được, nên 269
  file tài liệu cũ giữ nguyên tên. Nhưng `tdq_state.py init` TỪ CHỐI slug ghi mới thiếu giờ
  phút: cảnh báo suông thì chuẩn mới sẽ trôi ngay lần đầu ai đó bỏ qua.
- `scripts/tdq_state.py`: thêm `parse_slug()` (trả `(ngày, giờ-phút hoặc None, phần chữ)`),
  `schema_version` lên 4 với hai trường mới `started_at` và `phase_history`. Mỗi lần ĐỔI
  phase ghi một mốc; set lại đúng phase đang đứng thì không ghi (tránh mốc 0 giây), quay
  lại phase cũ thì ghi mốc mới — đó là cơ sở đếm "số lần vào".
- `scripts/tdq_timing.py` (mới): `show` in bảng Phase · Treo tường · Model chạy · Số lần
  vào; `status` in một dòng đồng hồ cho `tdq-status`; `close` append đúng một dòng JSON vào
  `docs/tdq/timing.jsonl`. Hai cột cố ý khác nguồn: treo tường lấy từ mốc state (gồm cả
  thời gian chờ user duyệt), model chạy cộng khoảng cách giữa các bước model trong
  transcript và bỏ khoảng > `MAX_GAP_SECONDS` (tái dùng ngưỡng của `step_audit.py`).
  Không đọc được transcript thì cột model in `—` kèm lý do, vẫn thoát 0.
- Đóng sổ tự động ở hai cửa: `init` chốt sổ request cũ TRƯỚC khi reset state (không thì mốc
  của request bỏ dở bay mất), và `tdq_finish.py --phase idle` chốt sổ khi hết request. Đóng
  sổ hai lần cho cùng một request không đẻ dòng thứ hai.
- Khuôn report bắt buộc có mục `## Thời gian`; `skills/tdq-status/SKILL.md` in thêm dòng
  `⏱` của phase đang chạy. Công thức slug đã đồng bộ ở `skills/`, `scripts/`, `portable/`.

## 0.19.0 — 2026-08-15

Cắt thời gian xử lý một request mà không đụng vào luật hay chất lượng đầu ra. Nguyên nhân
đo được: tổng thời gian tỉ lệ thẳng với SỐ BƯỚC (mỗi tool call ≈ một round-trip 3–4 s),
context chỉ ảnh hưởng nhẹ; luật gộp tool call đã có nhưng nằm trong file reference ít nạp
và bị đóng khung là "tiết kiệm context" — tầng thấp nhất của soul, nên bỏ qua vẫn hợp lệ.

- `skills/tdq-conventions/SKILL.md` §10 đổi thành "Luật một lượt (tầng 2 — runtime)":
  luật gộp chuyển hẳn vào thân skill (nạp mỗi turn) theo khuôn ba mục. Trần dòng của
  skill này nới 120 → 130 — trần dòng là ràng buộc tầng 3, không được nén luật tầng 2.
- `references/context-budget.md` tách hai phần rõ ràng: chi phí bước (tầng 2) và chi phí
  context (tầng 3). Thêm bảng **Cấm gộp** 4 ca (bước đỏ→xanh của TDD, đang khoanh vùng
  lỗi, lệnh phá hủy, lệnh sau cần kết quả lệnh trước). Sáu luật cũ giữ nguyên văn.
- Luật đọc lại file là luật **MỀM**: còn nhớ đủ thì đừng đọc lại. Nhưng có 5 ca BẮT BUỘC
  đọc lại: context bị nén, lần trước đọc một phần, file có thể đã đổi, sắp sửa chính file
  đó, nhớ không chắc. Nghi ngờ thì đọc lại — không đổi chất lượng lấy tốc độ.
- `references/soul.md` thêm mục "Xếp luật vào tầng nào": luật đổi số bước → tầng runtime,
  đổi số token → tầng context cost, đổi đúng-sai đầu ra → tầng chất lượng. Ba tầng gốc
  giữ nguyên văn. Bản `portable/AGENTS.md` có luật một lượt tương đương.
- `scripts/step_audit.py` (mới): đo 5 chỉ số chi phí bước, gom theo `requestId` — đếm theo
  bản ghi jsonl thổi phồng số bước và luôn ra 1,00 tool call mỗi lượt. `token_audit.py`
  sửa lỗi suy đường dẫn: tên project có gạch dưới cũng đổi thành `-`.
- Test: 596 → 608 (`tests/test_step_budget.py` mới, 12 test).

## 0.18.0 — 2026-08-14

Set "soul" cho bộ workflow: chất lượng code agent > runtime > context cost. Ba tầng ưu
tiên này thành luật gốc, mọi khuôn tài liệu khai nó ra, và luật cũ được rà lại theo nó.
Kèm theo là thư viện rule ngôn ngữ để model yếu cũng viết code sạch, cùng năm cơ chế
chặn nợ kiến trúc do quick-fix.

- `skills/tdq-conventions/references/soul.md` (mới): ba tầng ưu tiên kèm luật phân xử khi
  hai tầng đụng nhau. Skill nền và bản portable trỏ về đây, mỗi file đúng một dòng.
- Rà 28 file luật theo soul, biên bản ở `docs/tdq/knowledge/2026-08-14-ra-soat-luat-theo-soul.md`.
  Hai chỗ SỬA: khoá cứng phạm vi QC trong `qc.md`, và ngưỡng context trong `context-budget.md`.
- `skills/tdq-build/references/rules/` (mới, 10 file): chỉ mục + 7 file ngôn ngữ, mỗi file
  cùng một khuôn (Intentionality, mùi code, công cụ lint, nguồn chính thức có URL thật).
- `scripts/code_rule_scan.py` (mới): quét file đã đổi theo bảng rule, ba trạng thái PASS /
  LỖI / CHƯA KIỂM ĐƯỢC — thiếu công cụ lint thì báo đúng trạng thái, không PASS khống.
  Log stderr có timestamp, tắt bằng `--im`, chi tiết bằng `--chi-tiet`. Không tự cài gói.
- Cổng clean code ở phase spec: việc chạm mã nguồn thì hỏi user BẬT/TẮT, đáp án ghi vào
  spec §4. TẮT vẫn tổ chức code theo rule ngôn ngữ, chỉ bỏ bước scan cuối request.
- Năm cơ chế chống nợ kiến trúc: M1 hồ sơ `docs/kien-truc.md` sinh một lần mỗi project ·
  M2 khối "Ràng buộc kiến trúc phải giữ" trong spec §5 · M3 luật "Tìm rồi mới tạo" ở bước
  code · M4 dòng `Chạm:` trong plan lấy từ `graphify affected` · M5 ba hạng mục QC cố định
  QC-F1→F3, đồng bộ nguyên văn giữa bản skill và bản portable.
- Năm khuôn tài liệu (brief, spec, plan, qc, report) đều có dòng Soul.
- Test: 574 → 596 (306 subtest). Nghiệm thu thật bằng agent Haiku đọc rule soát file mẫu
  5 lỗi cố ý — nêu đúng 5/5, không hỏi lại câu nào.

## 0.17.0 — 2026-08-14

Trang trí khối chat cuối trả lời user: dùng markdown mà cả ba mặt (terminal, app,
extension) đều dựng được, tách nhãn khỏi nội dung, và chốt bằng test thay vì bằng trí nhớ.
Màu và cỡ chữ không làm được — ba mặt không dùng chung bộ dựng, mẫu số chung là markdown
terminal dựng được. Nguyên tắc xuyên suốt: **chỉ thêm dấu đánh dấu, không đổi một từ nào**
của nội dung đang chạy.

- `skills/tdq-conventions/references/user-facing-block.md`: viết lại. Thêm bảng 5 thành
  phần kèm cấu trúc trình bày dùng cho từng thành phần, mục `## Bảy luật trang trí`, bảng
  6 ký hiệu ngoài ASCII được phép, và ví dụ đối chiếu `### Trước` / `### Sau`.
- Luật cấm emoji giữ nguyên; chỗ nới đúng một điểm là ký hiệu Unicode, giới hạn trong sáu
  ký tự `➤ · — → – …`. Cả sáu đều có bằng chứng đang in ra cho user trong kho. Ký tự `▸`
  bị loại vì grep toàn kho ra 0 kết quả. Ký tự kẻ khung bị cấm vì đòi canh cột.
- Trang trí khối mẫu trong 8 file skill và 3 file bản portable: nhãn trường in đậm với dấu
  hai chấm nằm TRONG cặp sao, đường dẫn và tên lệnh bọc nháy ngược. Năm chỗ mã sinh chuỗi
  giữ nguyên từng byte để hook và test cũ không lệch.
- `skills/tdq-status/SKILL.md`: bỏ `✔` và `⏳` ở dòng báo trạng thái duyệt, thay bằng chữ
  in đậm. Đây là chỗ duy nhất trong kho còn dạy Claude in emoji ra cho user.
- `scripts/scan_block_symbols.py` (mới): quét ký tự Unicode loại `P*`/`S*` ngoài ASCII
  trong 12 file phạm vi, có chế độ `--chi-khoi` chỉ quét nội dung khối in cho user.
- `tests/test_user_facing_block.py`: 4 → 10 test (58 subtest). Thêm phép kiểm whitelist ký
  hiệu, phép kiểm khối mẫu theo luật 1/3/7, phép kiểm chuỗi do mã sinh, phép kiểm bản
  portable khớp khuôn gốc, và bảng `SO_KHOI` chặn trường hợp phép kiểm chạy rỗng mà vẫn
  xanh. Toàn bộ suite: 569 → 574 test.

## 0.16.0 — 2026-08-14

Cắt chi phí context của chính workflow mà không bỏ một luật nào: đếm mệnh lệnh theo 10
cụm file cho **7 cụm tăng · 3 cụm giữ nguyên · 0 cụm giảm**. Nguyên tắc áp dụng xuyên
suốt: dời văn bản xuống tầng `đọc khi cần` và để lại dòng trỏ có chữ BẮT BUỘC, tuyệt đối
không xoá luật.

- `scripts/skill_inventory.py`: thêm `--loc <từ khoá>` và `--tat-ca`. Bản lọc CẤM ẩn skill
  nguồn `project` và `plugin:tdq-workflow` (hai nguồn quyết định phán quyết DÙNG ở bước
  B0), và luôn in dòng cuối báo đã ẩn bao nhiêu kèm lệnh xem đủ. Chạy không cờ giữ nguyên
  từng byte. Bước B0 dùng `--loc`: **39.722 → 1.845 byte** mỗi lần chạy (≈ −9.300 token).
- `skills/tdq-intake/SKILL.md`: nhánh chế độ nhanh dời sang
  `references/quick-lane.md`, đánh số lại thành 12 bước. Thân 1.844 → 1.288 token.
- `skills/tdq-build/SKILL.md`: Phần B (QC) và Phần C (Report) dời xuống `references/qc.md`
  và `references/report-template.md`. Thân 1.936 → 1.536 token.
- `skills/tdq-conventions/`: phần nền/giải thích của 3 file gom vào mục `## Phụ lục`,
  **giữ nguyên 100% câu chữ** (diff theo từ: 0 từ bị mất).
- `skills/tdq-intake/references/scope-round.md`: khử 2 từ mơ hồ thành điều kiện đo được.
- 8 chỗ cố ý chép lại luật giữa các file nay có nhãn "nhắc lại có chủ ý" — chống việc
  lần sau bị nhầm là trùng lặp rồi xoá đi.
- `agents/tdq-implementer.md`, `tdq-qc-tester.md`, `tdq-reviewer.md`: thêm khối
  "Return format — copy this shape exactly".
- Tổng tầng `nạp khi gọi skill` **8.473 → 7.579 token** (−10,6%). Test 563 → 569 passed,
  0 failed. QC 15 hạng mục, Q1–Q14 PASS; một lượt QC độc lập bằng agent `tdq-qc-tester`
  chạy lại từ đầu cho cùng phán quyết. Model hạng thấp chạy thử: không bỏ bước nào.
- Chưa đụng `hooks/` và `portable/` — bản portable chưa nhận các thay đổi này.

Bản 0.15.0 trở về trước: xem [CHANGELOG-archive.md](CHANGELOG-archive.md).
