# Changelog

Mới nhất trên cùng. Ngày theo múi giờ máy phát hành.

## 0.55.0 — 2026-10-03

Luật tìm kiếm 4 tầng giờ được **cưỡng chế**, không chỉ được nhắc. Soi một phiên thật trên
excalidraw: ~20 lần grep qua 4 request, 0 lần hỏi lumen hay LSP cho tới khi user phải hỏi luật.
Báo cáo: `docs/tdq/reports/2026-10-03-0015-ep-luat-tim-kiem.md`.

- **Cổng tìm kiếm (`hooks/scripts/search_gate.py`, mã `TDQ:SEARCH`).** `PreToolUse` trên
  `Bash|Grep|PowerShell` **chặn** lần tìm code đi tắt tầng khái niệm. Request chưa hỏi
  lumen/LSP/graphify → chặn. Một lần hỏi mở khoá 10 lần tìm; sau đó grep kiểu đoán mò bị chặn
  lại. Miễn: lọc danh sách file, và tên có nguyên văn trong prompt. Phát lại phiên excalidraw:
  bắt 11, bắt oan 0, lọt 0. Đây là một điểm chặn mới — quyết định ghi ở `docs/kien-truc.md`.
- **Không kẹt.** Cổng đứng xuống khi tầng khái niệm chưa dựng xong hoặc mốc báo không tầng nào
  sẵn sàng. Nó cũng đứng xuống sau 3 lần chặn mà request chưa ghi được lần hỏi nào. Mỗi lần đứng
  xuống, nó nói ra một lần mỗi lượt.
- **Codex có cùng cổng.** Codex đã bỏ hook đi theo plugin, nên `tdq-setup` ghi `.codex/hooks.json`
  cấp project bằng đường tuyệt đối; khi plugin lên bản, entry cũ được sửa tại chỗ, không nhân
  đôi. `tdq-setup` cũng khai MCP lumen + LSP qua `codex mcp add` — chỉ thêm, có backup.
- **Tự dựng bộ tìm kiếm.** `SessionStart` ở một project thật (có `.git`) chưa sẵn sàng sẽ khởi
  động dựng nền tách rời, có khoá pid chống chạy chồng; tắt bằng `TDQ_KHOI_TAO_NEN=0`.
- **Thang kiểm thật hơn.** Bậc 3 khởi động language server thật; smoke grep theo ngôn ngữ thật
  của project; thang 8 bậc + smoke 4 tầng chạy bằng một lệnh.
- **Đường dẫn tuyệt đối trong output hook** khi project không có `scripts/` của plugin — lệnh in
  ra ở project khác giờ chạy được nguyên văn.
- **`scripts/search_replay.py`** phát lại một transcript qua đúng luật của cổng, để đo lại N khi
  có thêm phiên thật.

## 0.54.0 — 2026-10-02

Workflow nạp ít chữ hơn mà không mất một luật nào: **sàn tuân thủ của một request lane `full`
giảm 55.439 → 49.531 token (−10,7%)**, trong khi số mục luật TĂNG 334 → 342. Báo cáo:
`docs/tdq/reports/2026-09-28-2324-toi-uu-context-workflow.md`.

- **Cổng nhắc đọc lại (`hooks/scripts/read_gate.py`).** Đo trên một phiên thật 22,76 MB:
  `tdq_state.py` bị đọc 12 lần, `build_portable.py` 19 lần. Riêng hai file đó là 28% nội dung
  đọc vào. Và 98,2% input của phiên là đọc lại context đã giữ. Cổng CHỈ NHẮC, một lần cho mỗi
  file, và im khi `offset/limit` nhắm vùng chưa đọc hoặc khi file đã đổi. Nó giữ SỔ RIÊNG chứ
  không dùng sổ lượt chung. Lý do: sổ lượt bị xoá ở mỗi prompt. Ký ức dựng trên đó không thấy
  được đúng cái nó phải bắt — việc đọc lại qua nhiều lượt của một phiên.
- **Chỉ mục dòng cho file luật dài (`scripts/doc_index.py`).** Mỗi file dài nhận một khối chú
  thích HTML `<!-- muc-luc-dong: Tên=đầu-cuối · … -->`, nhờ đó đọc ĐÚNG MỘT MỤC bằng
  `offset/limit` thay cho đọc trọn file. Khối ở dạng chú thích chứ không phải bảng vì một bảng
  cùng lượng thông tin tốn ~230 token/file — tốn đúng vào ngân sách nó đang đi tiết kiệm.
- **Trần 3.500 token mỗi file luật, cưỡng chế được ở CI.** CI cố ý không có tokenizer, nên
  `scripts/token_budget.py` đo trên máy CÓ tokenizer và khoá con số bằng `sha256` trong
  `docs/tdq/token-budget.json`; rule **R13** của `doc_lint` chỉ so hash. Không dùng dòng hay byte
  làm đại lượng thay thế: đo trên 43 file, token/dòng lệch 4,1 lần và byte/token lệch 1,81 lần.
  Ba file vượt trần đã được dời phần CÓ ĐIỀU KIỆN sang file em — không nén luật, theo `soul.md`.
- **Bảy file em TẦNG 1.** Phần chỉ cần khi gặp đúng ca được tách khỏi file cha và trỏ thẳng từ
  `SKILL.md`, đúng luật một tầng. `plan-template` 5.067 → 3.493, `quick-lane` 4.356 → 3.419,
  `team-mode` 3.652 → 3.313, `uu-tien-tim-kiem` 3.449 → 2.067 token.
- **Câu luật tìm kiếm còn một bản.** Sáu bản nguyên văn của cùng một câu (1.125 token) thành một
  bản gốc + năm con trỏ ba dòng.
- **CI in bảng bề mặt context** (`continue-on-error`, một tổ hợp). Nó là SỐ ĐO, không phải luật:
  luật trần token mới được làm đỏ build.

## 0.53.0 — 2026-09-28

Bộ tìm kiếm chuyển từ "có cài" sang "chứng minh được là đang trả lời đúng", và **breaking
change**: skill `tdq-lsp-setup` đổi tên thành `tdq-setup`. Báo cáo:
`docs/tdq/reports/2026-09-28-0910-lumen-check-va-setup-tool.md`.

- **BREAKING — `tdq-lsp-setup` → `tdq-setup`.** Không giữ bí danh: gõ tên cũ sẽ không thấy gì.
  Tên cũ nói skill này chỉ lo LSP. Thực tế nó vốn đã cài cả lumen, và nay nhận luôn việc cài đủ
  phụ thuộc cho workflow. Bốn nhóm đã đổi theo: bảng trần dòng của `doc_lint`, danh sách thứ tự
  nạp của `build_portable`, năm chỗ trích luật tìm kiếm, và file test chống lệch.
- **Bậc 5 hết mù với chuyện "sống mà trả lời sai".** Nó từng chỉ hỏi "ollama có chạy không", nên
  suốt phiên 2026-09-28 nó báo ĐẠT trong khi MCP `lumen` chết cả phiên (`CONNECTION_CLOSED`).
  Nay nó hỏi lumen một câu thật rồi đọc câu trả lời, và đo xem index có nội dung MỚI của cây làm
  việc hay không. Cả hai phép đo đi bằng CLI: lumen 0.0.42 khai `defaultFreshnessTTL = 30s`, nên
  đường MCP có thể trả lời từ một lần "fresh" đã cũ.
- **Bậc 5 không còn dò ollama bằng PATH.** Socket được hỏi TRƯỚC; `which` chỉ còn để phân biệt
  "cài rồi mà đang ngủ" với "chưa cài bao giờ". Đo trên macOS: `/opt/homebrew/bin/ollama` có
  thật và login shell tìm ra, nhưng `shutil.which` từ tiến trình không-login trả `None` — thứ tự
  cũ kết luận "thiếu ollama" và in lệnh cài cho một daemon đang phục vụ.
- **Thêm bậc 8 — đồ thị graphify.** Công cụ thứ tư của bộ tìm kiếm trước nay không có bậc nào.
  Nó hỏng đúng kiểu một index không ai dựng lại. Đo được 2026-09-28: đồ thị cũ 8 ngày, 34% node
  (845/2415) trỏ vào thư mục đã xoá.

## 0.52.0 — 2026-09-27

CI xanh trên cả ba hệ ở lần chạy thứ hai, và **breaking change**: sàn Python lên 3.11. Báo cáo:
`docs/tdq/reports/2026-09-27-1905-ci-do-ba-he.md`.

- **BREAKING — sàn Python 3.8 → 3.11.** `PYTHON_MIN` đổi, lớp dự phòng `tomllib = None` trong
  `tdq_codex.py` bỏ hẳn cùng 6 guard `skipIf` của nó, ma trận CI đổi `3.10` → `3.11`. Ai đang
  chạy 3.8–3.10 sẽ không dùng được bản này. 3.11 là bản đầu tiên có `tomllib` trong thư viện
  chuẩn, và nay là bản thấp nhất được CI chạy thật.
- **Header `SessionStart` không còn phụ thuộc độ dài đường dẫn** — lỗi sản phẩm, đo trên macOS.
  Khối đầu có trần 600 ký tự và tính cả dòng `Project: <đường dẫn>`. Thư mục tạm của runner macOS
  là `/var/folders/36/tjdph2t965j8snz9_vkdnw0r0000gn/T/tmpXXXX`, đủ dài để `cap()` cắt mất dòng
  lệnh. Đường dẫn là dữ liệu của user, nên phần nhường là phần HIỂN THỊ.
  `duong_hien_thi()` giữ hai đoạn cuối trong trần 32 ký tự (`…/ForAgentCode/TDQ-Workflow`), còn
  `STATE.md` vẫn giữ đường dẫn tuyệt đối đầy đủ.
- **Phép kiểm dấu ngã hỏi đúng câu** — `con_dau_nga_chua_bung()` trong `tdq_checkportable.py`,
  dùng chung cho sản phẩm và ba file test. Bản cũ ("có ký tự ngã là sai") báo đỏ oan trên runner
  Windows, nơi thư mục nhà có dạng 8.3 (`RUNNER~1`). Tệ hơn: nó nuốt luôn nhánh `elif` phía sau,
  nên phép kiểm THẬT — bundle dựng dưới thư mục nhà của máy khác — không bao giờ chạy ở đó.
- **Fixture test viết theo hệ đang chạy** — 9 ca của `test_shim_python3` dựng PATH giả bằng đường
  dẫn Windows cho mọi hệ, mà `os.pathsep` trên POSIX là dấu hai chấm nên đường dẫn ổ đĩa bị xé
  làm hai. Sản phẩm vốn đúng; nay 9 ca đó chạy THẬT trên cả ba hệ thay vì bị skip, cộng một ca
  canh chính cái bẫy đó.
- **Cổng D7 không còn tự tắt trong im lặng** — `_cham_d7` từng `continue` khi không đọc được mốc
  thời gian của commit. Một mốc lạ vì thế làm cổng "agent khác vừa commit" tắt hẳn, mà trông y
  như "không có ai commit thêm". Nay nó báo rõ là không kết luận được.
- **Vá lỗi 0.50.0 để lại** — `_in_ket_qua` vẫn gọi `da_trusted()` và `duong_config_codex()`, hai
  hàm biến mất cùng lớp trust: một `NameError` ngồi chờ từ bản đó tới nay.
- **Đo trên máy thật, không đoán** — Linux (3.14.4) 1993 ca; macOS pyenv 3.13.15 và brew 3.14.7
  đều 1993 ca; Windows 3.13.15 2016 ca. Tất cả 0 fail, 0 error. CI xanh cả 6 job (run 36322434130).

## 0.51.0 — 2026-09-23

Mức độ QC thành quyết định của user, hỏi một lần trước khi viết spec. Báo cáo:
`docs/tdq/reports/2026-09-23-1148-hoi-muc-qc.md`.

- **Khoá `muc_qc`** — `lite|full|ultra|off`, mặc định `full`, chuẩn hoá fail-closed như
  `muc_gat`: giá trị rác, trống hay sai kiểu đều về `full`, nên không gõ nhầm nào mua được một
  vòng QC rẻ hơn. `schema_version` 5 → 6. `next` và `STATE.md` in mức QC trên dòng riêng, không
  gộp với `Lean level` — hai thang khác nhau, gộp là mời nhầm.
- **Hỏi ở đâu** — cuối phase `analyze` (bước 5c của `analyze-full.md`), TRƯỚC khi viết spec §6,
  vì hỏi sau là phải sửa mục user đã duyệt. Lane express hỏi ngay trong khối mời duyệt sẵn có,
  không thêm lượt dừng nào.
- **Bảng mức × loại kiểm** — một bảng duy nhất trong `skills/tdq-build/references/qc.md`, mỗi ô
  là CÓ hoặc KHÔNG cho bốn loại: DoD, unit test, smoke test, runtime test, cộng cột QC độc lập
  bằng agent. Mức mặc định `full` **không** chạy runtime test: đó là loại từng treo rất lâu, và
  một vòng QC treo thì bị bỏ dở, mất nhiều hơn được. `ultra` mới chạy runtime và gọi
  `tdq-qc-tester` — trước đây agent này treo vào câu "việc lớn hoặc rủi ro cao", không ngưỡng
  nào đo được, nên thực tế không bao giờ chạy.
- **Trần 120 giây** cho mỗi phép smoke/runtime: chạm trần thì giết tiến trình và ghi FAIL kèm
  lệnh, rồi phân tích xem là lỗi thật hay việc cần chạy lâu thật. Cấm tự nâng trần — nâng phải
  hỏi user, vì nâng trần cho một phép đang đỏ là vặn bóng đèn cho đèn khỏi sáng.
- **Gỡ cờ `--no-qc`** của `approve quick` cùng khoá `quick_qc_skipped`: một cơ chế duy nhất cho
  cả hai lane. Lệnh cũ chết kèm câu chỉ sang `set muc_qc=off`. Dòng nhắc duyệt không còn mời bỏ
  QC — `off` vẫn đặt tay được nhưng không bao giờ được bày ra trong danh sách chọn.
- **Test** — hai file mới khoá khoá state và luồng hỏi, một file khoá bảng mức cùng luật trần.
  Ba ca cũ ghim `schema_version = 5` nay đọc số từ chính sản phẩm.

## 0.50.0 — 2026-09-21

Học cách superpowers tổ chức: một nguồn `skills/`, mỗi host một adapter mỏng, không còn bản sao
nào trong repo. Báo cáo: `docs/tdq/reports/2026-09-21-0029-hoc-superpowers-da-host.md`.

- **Adapter Codex CLI** — `.agents/plugins/marketplace.json` (`"url": "./"`) và
  `.codex-plugin/plugin.json` (`"skills": "./skills/"`). Đo trên Codex CLI 0.155.1:
  `codex plugin list` ra `tdq-workflow@tdq-local`. Policy xác thực phải là `ON_INSTALL` hoặc
  `ON_USE` — CLI từ chối `NONE`, test khoá giá trị.
- **Adapter OpenCode** — `.opencode/plugins/tdq-workflow.js`, JavaScript thuần (`node:path`,
  `node:fs`, `node:url`), đọc thẳng `skills/*/SKILL.md`, bọc try/catch mọi bước để một lỗi không
  kéo sập plugin khác của host. Hướng dẫn cài ở `.opencode/INSTALL.md`.
- **Antigravity sinh tại chỗ** — `build_portable.py --sinh-agy` sinh layout vào
  `~/.gemini/config/plugins/tdq-workflow/` trên máy người dùng, bất biến, từ chối ghi đè thư
  mục không phải do nó sinh. Đường dẫn tuyệt đối vì thế là của đúng máy chạy.
- **Gỡ ba bundle** — `portable_claude/`, `portable_codex/`, `antigravity_portable/` ra khỏi repo
  (`git rm`, lịch sử còn nguyên). `build_portable.py` 1077 → 634 dòng, không còn hàm hay hằng nào
  không có nơi dùng (khoá bằng test đo khả năng với tới từ `main`); bỏ cờ `--only` (được nhận
  rồi lờ đi), và chạy không cờ nay thoát 2 thay vì dựng lại bundle NGAY TRONG repo.
  `tdq_checkportable.py` 675 → 560 dòng: bỏ lớp trust/codex, thiếu `manifest.json` chỉ còn là
  NOTE; giữ `setup --shim` và phần kiểm môi trường.
- **Sửa lỗi mã hoá của 0.49.0** — 89 lời gọi `subprocess` chế độ văn bản (20 trong `scripts/`)
  và 36 `open()` trong test chưa khai `encoding=`, nên Windows giải mã đầu ra UTF-8 bằng cp1252
  và `proc.stdout` thành `None`. Con số "1983 ca, 0 fail" của 0.49.0 đo khi máy có
  `PYTHONUTF8=1`; bỏ biến đó thì là 273 error. Khoá bằng `tests/test_ma_hoa_subprocess.py`
  (đọc AST, bắt cả lời gọi trải nhiều dòng). `codex_edit_gate.py` ép UTF-8 tại chỗ vì không
  được import `scripts/`.
- **`utf8_io` im trên pipe** — dòng "forced 2 stream(s)" chỉ in khi stderr là console (hoặc
  `TDQ_UTF8_LOG_FORCE=1`). Nó chạy lúc import, trước khi script đọc `--quiet` của chính mình,
  nên hook và test không có cách tắt.
- **Header `SessionStart`** — dòng nhắc graphify và dòng nhắc tên lệnh Python chuyển ra sau
  trần 600 ký tự, thành đoạn riêng. Trên Windows đường dẫn dài từng cắt dòng graphify còn
  `graphify is n…`.
- **Suite chạy được trên máy sạch** — thiếu pytest, anthropic-tokenizer, graphify, node hay
  codex thì ca tương ứng thành skip có ghi lý do: 1917 ca, 0 fail, 0 error, 30 skip. Phép dò
  tokenizer nay hỏi chính `skill_tokens` — bản cũ tìm `.venv-tokens/bin/python`, nên trên
  Windows ba ca luôn bị skip dù đã cài.
- **CI ba hệ** — `.github/workflows/test.yml`: Ubuntu, macOS, Windows × Python 3.10 và 3.13,
  không cài công cụ ngoài, không bật chế độ UTF-8, tắt `core.autocrlf` trước checkout. Chưa
  chạy lần nào trên GitHub.
- **Lumen trên Windows** — `tdq_lsp.py` cảnh báo khi plugin lumen thiếu `bin/lumen` và in lệnh
  chép `lumen-windows-amd64.exe` sang; script `run` của lumen đoán sai tên hệ dưới Git Bash.
- **Tài liệu** — README viết lại phần cài cho bốn host; `docs/kien-truc.md` thay tầng "luật bản
  ngoài" bằng tầng Adapter và ghi ngoại lệ đường dẫn adapter vào `Đã chốt`.

## 0.49.0 — 2026-09-20

Bộ workflow chạy được đủ tính năng trên Windows. Trước bản này cả 6 hook đều chết ngay ở dòng
`print` đầu tiên trên một máy Windows sạch, nên phần nhắc `[TDQ:*]` mất trắng mà không ai biết.
Báo cáo: `docs/tdq/reports/2026-09-20-1823-sua-tdq-chay-windows.md`.

- **`scripts/utf8_io.py`** — ép `stdout`/`stderr` sang UTF-8 với `errors="replace"`, idempotent,
  log service bật mặc định tắt bằng `TDQ_LOG=0`. Nạp qua `tdq_state.py` và
  `hooks/scripts/_common.py` (phủ 18/40 entry point) cộng một dòng import ở 21 file còn lại.
  Python lấy encoding console theo locale, mà Windows sạch trả `cp1252`, nên mọi `✓`, `✗` và
  tiếng Việt đều ném `UnicodeEncodeError`. Đo lại: 6/6 hook sống, không cần biến môi trường nào.
- **Shim `python3`** — `tdq_checkportable.py setup --shim` đặt hai file một dòng vào thư mục
  ổn định đứng đầu PATH, để 96 chuỗi lệnh trong `skills/` gõ được nguyên văn ở Git Bash,
  `cmd.exe` và PowerShell. `hooks.json` vì thế GIỮ `python3` cho cả ba hệ. Máy Windows chưa cài
  shim thì `session_start` in thêm đúng một dòng quy ước, đặt ngoài trần 600 ký tự của header.
- **`ten_lenh_python`** chuyển từ `build_portable.py` sang `tdq_ten_lenh.py` — hook không được
  import bộ dựng bundle; `build_portable` nay gọi lại, hết hai bản chép.
- **Dấu chéo ở biên xuất** — `observe`, `today_log_rel`, `context_surface`, `kiem_no_marker` đều
  in và ghi bằng `/`. Sổ turn được đối chiếu với đầu ra `git`, thứ luôn dùng `/`, nên một
  `docs\workinglog\x.md` từng làm cổng `Stop` chặn nhầm một lượt đã ghi log đầy đủ.
- **`tdq_state.xoa_cay`** — `shutil.rmtree` không xoá nổi file read-only trên Windows, mà git
  đánh dấu mọi object như vậy; dùng ở 4 chỗ xoá cây có `.git`.
- **Mode codex chạy được trên Windows** — `boc_lenh` bọc `.cmd` qua `cmd.exe /c`
  (`CreateProcess` không chạy batch file, cũng không tra `PATHEXT`), và tên lệnh nay lấy từ
  `shutil.which`. npm cài codex đúng dạng `codex.cmd`, nên trước bản này mode đó không thể chạy.
- **Layout mới của Claude Code** — `skill_inventory` quét thêm
  `~/.claude/skills/synced/<uuid>/<tên>/`, `tdq_lsp` thấy thêm plugin trong
  `~/.claude/plugins/synced/`. Bước kiểm kê năng lực B0 trên máy thử từ 0 lên 11 skill.
- **`.lumenignore`** — loại ba bundle portable khỏi index ngữ nghĩa: 1488 → 1140 file,
  27318 → 14503 chunk. Bản sao sinh ra từng chiếm hết top-10 của mọi truy vấn.
- **Luật mới** — `uu-tien-tim-kiem.md` mục 6: cấm mở file trước khi hỏi `find_references`.
  Đo được: hỏi thẳng ra 6 file, mở sẵn 3 file còn 4, mở sẵn 8 file còn 1.
- **Bộ test** — 1983 ca, 0 fail, 0 error trên Windows (trước: 670 fail / 97 error). Vá các ca
  tự dựng lại đường dẫn bằng `os.path.join`, đọc state sống của máy, hoặc set `HOME` mà quên
  `USERPROFILE` (`ntpath.expanduser` không đọc `HOME`). Ba ca không dựng lại được trên Windows
  (bit quyền POSIX, chmod thư mục) được bỏ qua kèm lý do.
- **`docs/claude-md-mau.md`** trần 3500 → 3800 byte theo phán quyết sẵn có của `soul.md`: trần
  kích thước là ràng buộc tầng 3, chạm trần thì nâng trần chứ không nén luật.
- **Xoá `portable_codex.zip`** — đứng yên từ 0.24.0 trong khi `portable_codex/` đã lên 0.48.0,
  và `build_portable.py` chưa bao giờ dựng nó.

## 0.48.0 — 2026-09-17

Nội hoá lối code Ponytail vào ruột TDQ-Workflow — Ponytail KHÔNG được cài làm plugin thứ hai,
phase và hai cổng duyệt giữ nguyên. Báo cáo:
`docs/tdq/reports/2026-09-16-2234-cong-sinh-ponytail-tdq.md`.

- **Luật `build less than asked`** — bậc thang 7 bậc (dừng ở bậc đầu tiên đứng được) cộng món 8
  "chạy trước, refactor sau", viết vào thân `skills/tdq-build/SKILL.md` và bảng chi tiết trong
  `references/rules/chung.md`. Sàn `cyclomatic ≤ 10 / cognitive ≤ 15` là SÀN: phương án vượt sàn
  chưa từng là phương án, không comment hay annotation nào mở được. Danh sách bất khả xâm phạm:
  input validation ở biên tin cậy, error handling chống mất dữ liệu, OWASP walk, accessibility,
  log service bật mặc định, unit test mỗi task red → green.
- **Bốn mức gắt `muc_gat`** — `off|lite|full|ultra`, khoá mới trong `docs/tdq/state.json` đọc/ghi
  qua `tdq_state.py`. Fail-closed về `full`: giá trị lạ, khoá trống hay file lỗi đều ra `full`, và
  không suy luận nào của agent chọn được `off` — chỉ user đặt. Đo thật: 0/72/133/139 dòng luật.
- **`hooks/scripts/luat_gon.py`** — hai hàm thuần đọc luật từ đĩa rồi lọc theo mức gắt. Luật viết
  MỘT chỗ, không bản sao trong mã. Thiếu file hay thiếu marker → một dòng cảnh báo, exit 0.
- **Ba kênh nạp luật, hook 5 → 6 trên 5 sự kiện** — `SessionStart` và `SubagentStart` bơm thân
  luật (đo thật 135 ms / 155 ms). Kênh `UserPromptSubmit` chỉ in một dòng nhắc 137 ký tự và
  KHÔNG đọc thân luật, để không ăn ngân sách 30 s chia chung. Mã thứ sáu `TDQ:GON` được khai
  trong spec trước khi thêm.
- **Skill `tdq-lean`** — ba chế độ `review|audit|debt` soi over-engineering, năm nhãn
  `delete/stdlib/native/yagni/shrink`, không có gì cắt thì nói đúng `Lean already. Ship.`
- **`scripts/kiem_no_marker.py`** — sổ nợ marker `ponytail:`: marker phải nêu cả trần và đường
  nâng cấp, thiếu thì exit khác 0 kèm `đường-dẫn:dòng`. Một lệnh chạy được, không framework,
  không fixture.
- **Test** — thêm 105 test, tất cả xanh. Tập TÊN test đỏ lệch 0 so với baseline `main` sạch.

## 0.47.0 — 2026-09-14

Lượt Codex sai khuôn thì lấy test làm chuẩn. Báo cáo:
`docs/tdq/reports/2026-09-14-1417-sai-khuon-lay-test-lam-chuan.md`.

- **Phán quyết của `tdq_codex.py run` thêm 2 khoá** — `ly_do` (mã thuộc `MA_LY_DO`, `null` khi
  `xong`) và `can_chay_lai_test`. Thứ tự 5 khoá cố định, `dung_phan_quyet` dựng dòng JSON.
- **Tập mã cứu được `MA_LY_DO_CHAY_LAI_TEST`** — chỉ `khong-co-ket-qua` và `ket-qua-sai-khuon`.
  `can_chay_lai_test` là `true` khi lượt `fail` vì một trong 2 mã đó VÀ vùng file `dat`; timeout,
  deny, exit khác 0, `xong: false` hay lệch vùng không bao giờ được cứu. `run` không tự đổi `fail`
  thành `xong`, exit vẫn 1.
- **Luật `codex-mode.md` bước 6** — leader chạy lại test: xanh thì tick `[x]` kèm ghi chú
  `(cứu bằng test · ly_do=<mã>)`, đỏ thì task fail. Checklist mode `codex` trong `tdq_state.py` và
  mục tự kiểm số 6 nói cùng điều đó.
- **Test đầu-cuối `RunDauCuoiTest`** — chạy `run` thật qua tiến trình con với Codex giả và
  `CODEX_HOME` giả: 5 ca phán quyết, cách ly cấu hình máy, log lượt tắt được bằng `TDQ_LOG=0`.

## 0.46.1 — 2026-09-14

Hai bản sửa cho mode `codex implement`. Báo cáo: `docs/tdq/reports/2026-09-14-1252-run-cham-fail-sai-schema.md`.

- **`tdq_codex.py run` chấm đúng lượt làm đúng** — nhận JSON trần hoặc đúng một rào code bọc trọn
  file (nhãn rỗng/`json`). Chỉ `xong` là boolean `true` mới là `xong`; trước đây `{"xong": false}`
  cũng bị chấm `xong`. Schema thêm `additionalProperties: false`.
- **Dòng log mang lý do** — lượt không xong kết thúc bằng `· ly_do=<mã>`, mã thuộc tập đóng `MA_LY_DO`.
- **Sửa `check` Codex** — gửi một lượt say hi thật thay vì chỉ `codex --version`. Có lệnh mới
  `dong-y --model`, và `CODEX_HOME` tạm mang theo bảng provider.

## 0.46.0 — 2026-09-14

Mode thực thi thứ ba: `codex implement`. Leader vẫn chạy tuần tự trong turn của mình như mode
`main`, nhưng từng task giao cho `codex exec` viết code rồi leader kiểm lại. Không có sub-agent,
không có worktree song song.
Báo cáo: `docs/tdq/reports/2026-09-10-2247-mode-codex-implement.md`.

- **`tdq_state.py` nhận mode thứ ba** — `VALID_MODES`/`MODE_LABELS` có `codex`, `phase_row` đọc
  bảng tra thay vì rẽ nhánh `if`, và lệnh mới `modes --json` in `{ma, nhan, chon_duoc, ly_do}`
  làm nguồn máy đọc được cho cổng chọn mode. `tdq_state.py` không được import tầng Codex.
- **`scripts/tdq_vungfile.py` mới** — `chup-moc`/`hau-kiem`/`hoan-tac`. Mốc git lấy riêng cho
  từng task, không so với `HEAD`. So với `HEAD` thì task sau FAIL oan vì việc chưa commit của task
  trước. Hoàn tác bằng `git restore --source=<sha> --worktree`, không đụng index. Vùng khoá gồm file test.
- **`scripts/tdq_codex.py` mới** — `check` dò máy và kiểm Codex còn sống. `run` chạy một lượt
  `codex exec` với stdin không phải TTY, mọi cờ gom về một bảng `CO_EXEC`. Phán quyết 4 trạng thái
  không dựa exit code. `cleanup` dọn `CODEX_HOME` tạm; log ghi sha256 của prompt thay nguyên văn.
- **Nhịp đỏ → xanh chia đôi** — leader viết test đỏ trước, Codex chỉ được làm xanh; sửa file test
  là FAIL kể cả khi test xanh.
- **Hàng rào `hooks/scripts/codex_edit_gate.py`** — nâng từ chuỗi nhúng trong `build_portable.py`
  thành file thật; dịch `apply_patch` và 5 dạng lệnh shell sang đường ghi, deny `[TDQ:VUNG]` khi
  ra ngoài vùng. `.codex/hooks.json` ở gốc repo viết tay, đúng hai matcher `PreToolUse`.
- **Cổng chọn mode động** — Codex sống thì 3 lựa chọn, không thì 2 lựa chọn kèm một dòng lý do.
  Cài lên máy mới phải có cả đồng ý của người dùng lẫn `codex` trên máy; cờ đồng ý mặc định false.
- **Giới hạn** — Q13 (sandbox chặn ghi ra ngoài) chưa chạy thật vì cờ đồng ý đang false. Suite
  290 fail / 4 error bằng đúng mốc trước request (danh sách giống hệt), request thêm 0 fail mới.

## 0.45.0 — 2026-09-05

Mỗi request tự mở nhánh git của nó. Trước bản này chỉ mode đội mới đẻ nhánh, còn mode
`main` làm thẳng lên nhánh user đang đứng. Một request dở dang vì thế không có chỗ nào để lùi
lại gọn gàng, còn nhánh tích hợp của mode đội thì sống sót thành nhánh mồ côi.
Báo cáo: `docs/tdq/reports/2026-09-05-0833-gitflow-nhanh-theo-request.md`.

- **Ba khoá state mới, `schema_version` 4 → 5** — `loai_request`, `nhanh_goc`, `nhanh_request`.
  Chỗ nạp state đã `setdefault` sẵn nên file schema 4 dựng tay nạp lên không mất khoá nào; có
  ca test khoá đúng điều đó.
- **Bước 3b của `tdq-intake` — mở nhánh request** — chỉ lane `full` và `quick`, tầng `nhỏ` không
  mở. Repo bẩn thì DỪNG, in file bẩn, hỏi user; cấm tự `git stash`. Loại request do Claude đề
  xuất ngay trong câu hỏi chọn lane, không hỏi thêm một câu nào.
- **Luật tên nhánh `<loại>/<mô tả>`** — đúng năm loại `feature`/`bugfix`/`hotfix`/`chore`/`docs`,
  kebab-case không dấu, dấu gạch chéo xuôi vì `git check-ref-format --branch` từ chối dạng kia.
  Bản dài ở `skills/tdq-intake/references/nhanh-request.md`.
- **Bước 11 của khuôn báo cáo — gộp nhánh về** — chạy trên CẢ hai câu trả lời commit/chưa:
  `git merge --no-ff` rồi `git branch -d`, sau đó xoá ba khoá state. Đây là chỗ chặn nhánh mồ côi
  ngay từ gốc.
- **Mode đội bỏ tầng nhánh tích hợp** — nhánh request thay chỗ nó, ba tầng còn hai. `tdq_team.py`
  thêm hàng rào: gộp ngay trên cây làm việc chính mà còn thay đổi ĐÃ THEO DÕI thì dừng, vì
  `merge --no-ff` sẽ nuốt luôn phần đang staged.
- **Dọn nhánh mồ côi `tdq/2026-08-23-1623-mindmap-html-hai-lop/tich-hop`** — xoá cả local và
  `origin` sau khi user xác nhận.

## 0.44.0 — 2026-09-03

Luật routing biết tới UI/UX. Trước bản này bảng routing không có dòng nào cho giao diện, mà
dòng chốt bảng lại bảo "việc không khớp dòng nào thì đừng kéo plugin vào" — nên `ui-ux-pro-max`
đang bị luật cản chứ không trung lập.
Báo cáo: `docs/tdq/report/2026-09-03-1949-uiux-pro-max-routing.md`.

- **Khối luật `UI/UX — three layers`** — chia việc giao diện làm ba tầng: chiến lược sản phẩm
  (chưa plugin nào phủ), quyết định thiết kế (tầng DUY NHẤT `ui-ux-pro-max` phủ), kiểm chứng
  trên máy thật (`chrome-devtools-mcp`). Kèm một dòng mới trong bảng routing.
- **Chữ dùng là tra cứu, không phải mệnh lệnh** — plugin được mô tả là "CATALOGUE TO CONSULT,
  not a step to execute"; mặc định tra khi trúng tầng 2, bỏ qua được chỉ cần một dòng lý do.
  Có ca test cấm các từ ra lệnh tuyệt đối lọt vào khối luật.
- **Ghép được, không loại trừ nhau** — `frontend-design`, `figma`, `chrome-devtools-mcp` dùng
  chung được khi hai bên bổ trợ. Loại trừ Unity/game vì bộ dữ liệu không có dòng nào cho nó.
- **Vá `skill_inventory.py`** — thử `<installPath>/skills` rồi mới `.claude/skills`, nên bước
  B0 hết mù với plugin để skill theo bố cục thứ hai: 0 → 7 dòng `plugin:ui-ux-pro-max`, các
  nguồn plugin khác không đổi một dòng nào.
- **Dọn `CHANGELOG.md`** — cắt 0.21.0–0.24.0 sang `CHANGELOG-archive.md` để file chính về
  dưới trần 500 dòng của doc_lint R6.

## 0.43.0 — 2026-09-03

Vá bốn lỗi đa nền tảng P1–P4 mà bản rà 1648 tìm ra. Không có máy Windows, nên mọi hạng mục
Windows nghiệm thu bằng THAM SỐ giả lập: mức khẳng định cao nhất là "hàm cho ra đúng tên lệnh
khi truyền hệ Windows vào", không phải "đã chạy được trên Windows".
Báo cáo: `docs/tdq/report/2026-09-03-1733-sua-loi-da-nen-tang.md`.

- **Tên lệnh Python chọn theo hệ đích (P1)** — `tien_to_python(nen_tang)` cho `py -3` trên
  Windows, `python3` nơi khác. Hook codex/agy sinh qua hàm đó. Riêng `hooks/hooks.json` là file
  nguồn viết tay nên có lệnh sinh lại tại máy đích: `build_portable.py --sinh-hook-claude
  [--he-dich win32]`, bất biến, chạy lần hai in `already correct`.
- **Cổng gác bundle agy hết là mã chết (P2)** — `kiem_layout_agy` parse JSON và chỉ soi `~`
  trong giá trị `command`, thay vì quét văn bản thô cả file. Hết dương tính giả, nhánh "dựng ở
  máy khác" nay nổ được, và `hooks.json` hỏng cú pháp được báo thay vì im lặng.
- **README bundle agy nói rõ chuyện gắn máy dựng (P3)** — đừng copy bundle dựng sẵn, tên lệnh
  Python khác nhau giữa các hệ, lệnh kiểm lại sau khi copy. Sửa ở hằng `README_AGY`, vì file
  README của bundle là file sinh ra.
- **Dòng `Test:` của plan chạy được nơi không có tên lệnh `python3` (P4)** — token đầu đổi sang
  `sys.executable`. Giữ `shell=True` để không hỏng plan cũ, thay bằng cảnh báo khi gặp toán tử
  shell vì cú pháp `cmd.exe` khác `sh`.

## 0.42.0 — 2026-09-03

Chống conflict khi chạy sub-agent implement: năm lỗ hổng H1–H5 từ chỗ chỉ là câu chữ trong tài
liệu nay đều có hàng rào máy. Kèm đổi toàn bộ sub-command của 5 script CLI sang tên tiếng Anh.
Báo cáo: `docs/tdq/report/2026-09-03-1527-sub-agent-chong-conflict.md`.

- **Tên lệnh tiếng Anh, tên cũ thành bí danh ẩn** — `scripts/tdq_ten_lenh.py` là một nguồn sự
  thật cho 22 sub-command của `tdq_team`, `tdq_bench`, `tdq_eval`, `tdq_lsp`, `tdq_state`. Bí
  danh giải ở tầng argv nên `--help` chỉ in tên mới, còn hook/bundle/tài liệu cũ vẫn chạy đúng.
  Giá trị dữ liệu (`mo`/`dong` của sổ worktree, mã lý do như `vung-khoa`) giữ nguyên tiếng Việt.
- **`check` kiểm lại thật (H5)** — chạy chính lệnh trên dòng `Test:` của task trong worktree của
  nó. `TICK-READY` của agent con không còn là lời tự khai.
- **`merge` từ chối nhánh có test đỏ, và tự rebase trước (H2)** — rebase lên bản tích hợp mới
  nhất, hỏng thì `rebase --abort` trả worktree về nguyên trạng.
- **Lệnh mới `resolve` (H4)** — chỉ đọc, in hai phía của từng file kẹt để gỡ conflict.
- **Dòng `Chạm:` thành hàng rào máy (H1)** — agent con ghi ra ngoài vùng đã khai thì bị chặn
  ngay lúc ghi, không phải lúc merge. Mode `main` không đổi hành vi.
- **`assign` cảnh báo file nóng (H3)** — đường dẫn nằm trên ≥2 dòng `Chạm:` được nêu tên trước
  khi mở nhánh nào, lúc mà cách sửa còn rẻ.

## 0.41.0 — 2026-09-03

Sửa tương thích thật với cả 3 host: Claude Code, Codex CLI 0.149, Antigravity CLI (agy) 1.1.11.
Trước bản này, bundle agy KHÔNG chạy được (hook sai đường dẫn, sai payload deny, layout không
phải plugin) và README codex thiếu hai thủ tục bắt buộc. Báo cáo:
`docs/tdq/reports/2026-09-03-1440-kiem-tuong-thich-3-host.md`.

- **`antigravity_portable/`** — dựng lại đúng chuẩn plugin agy 1.1.11: `plugin.json` ở gốc,
  `hooks.json` + `mcp_config.json` ở gốc, bỏ hẳn thư mục `config/`. **Bỏ hẳn
  `settings.json`**: file thật của người dùng giữ `model`/`colorScheme`/`trustedWorkspaces`,
  copy đè là mất cấu hình mà không thêm được hàng rào nào. README từ 6 đường cài đoán còn 3
  bước thật (copy thư mục · bật trong `config.json` · khai skill root trong `skills.json`).
- **`hooks/scripts/agy_pretooluse_gate.py`** — payload deny phát CẢ `allow_tool: false` lẫn
  `decision: "deny"` vì Google chưa công bố schema chính thức; thiếu khoá đúng thì deny bị bỏ
  qua trong im lặng. Đường dẫn `command` trong `hooks.json` nay là tuyệt đối đã bung `~` —
  dấu `~` trong nháy kép không được bung, hook chết exit 127.
- **`portable_codex/README.md`** — thêm mục trust hook (`trusted_hash` ghim NỘI DUNG hook, dựng
  lại bundle là mất trust, phải duyệt lại bằng `/hooks`) và mục export biến môi trường
  (`env_vars` chỉ khai TÊN biến, TOML không nội suy). 0.149 đã bật hooks sẵn, không cần
  `[features] hooks = true`.
- **`.claude-plugin/plugin.json`** — thêm `displayName` và `userConfig` cho 2 khoá Tavily,
  `sensitive: true` để giá trị không bao giờ hiện ra. Validator đòi thêm trường `title` (không
  có trong tài liệu).
- **`scripts/tdq_checkportable.py`** — nhận diện layout plugin agy, cảnh báo khi `hooks.json`
  còn `~` chưa bung hoặc mang `$HOME` của máy khác.
- **`tests/test_tuong_thich_host.py`** (mới) — 6 test khoá 6 điểm tương thích; 5 test agy cũ
  trong `test_build_portable.py` viết lại theo layout mới.

## 0.40.0 — 2026-09-03

Cổng hỏi bằng chat thường, dòng `Next step:` nêu tên pha kế, và đường kẻ `---` kết lượt. Kèm
phần hướng dẫn cài qua marketplace + auto-update + bump version trong `README.md`. Báo cáo:
`docs/tdq/report/2026-09-03-1220-gate-chat-va-next-pha.md`.

- **`skills/tdq-conventions/references/user-facing-block.md`** — luật cấm tool hỏi dạng popup
  (`AskUserQuestion`) chuyển từ `tdq-intake` lên tầng conventions, áp cho MỌI câu hỏi chứ không
  riêng 7 cổng duyệt; thêm thành phần 6 của khối trả lời: đúng một dòng `---` kết lượt.
- **`skills/tdq-conventions/references/approval.md`** — mục `## Hỏi xong là kết lượt`.
- **12 dòng `Next step:` trong 8 skill** — mỗi dòng nêu tên pha kế tiếp hoặc nói rõ pha không
  đổi kèm skill kế, để host không có hook vẫn đi đúng lộ trình. Lớp này là DỰ PHÒNG,
  `[TDQ:NEXT]` vẫn là đường chính.
- **`tests/test_luat_gate_chat.py`** (mới) — 7 test khoá ba luật trên; tên pha đọc thẳng từ
  `PHASE_TABLE` chứ không chép cứng.
- **`README.md`** — 3 cách cài (marketplace / `--plugin-dir` / bundle portable), mục
  `## Cập nhật` và thủ tục bump version bắt buộc mỗi lần release.

## 0.39.0 — 2026-09-03

Thang `tdq_lsp.py kiem` thêm **bậc 7** và luật thứ tự tìm kiếm đổi từ một thứ tự cứng sang chọn
lớp theo LOẠI truy vấn. Lý do: thang cũ báo **6/6 ĐẠT** trong cả trạng thái độ phủ truy vấn quan
hệ 7 % lẫn 100 % — nó kiểm sự tồn tại, không kiểm hiệu quả. Báo cáo:
`docs/tdq/report/2026-09-03-0053-sua-luat-va-kiem-lsp-that.md`.

- **`scripts/tdq_lsp.py`** — bảng `LANG_CONFIG` (file mốc gốc import cho 26 ngôn ngữ, chia nhóm
  A/B) và bậc 7 `bac7_cau_hinh_goc_import`. Nhóm B (Python, TS/JS, Lua, C/C++) thiếu file mốc thì
  **CHẶN, thoát 3** vì chỉ mục liên file chết âm thầm mà test vẫn xanh; nhóm A (`go.mod`,
  `Cargo.toml`…) chỉ cảnh báo vì thiếu là dự án không build được, tự lộ. Script chỉ in nội dung
  cần tạo và xin phép, không bao giờ tự ghi file.
- **`skills/tdq-lsp-setup/references/uu-tien-tim-kiem.md`** — luật gốc thay bằng bảng 4 loại truy
  vấn kèm số đo: quan hệ → `mcp__lsp__*` (phủ 15/15, grep chỉ precision 67 %); tên chính xác →
  grep (~0,1 s so với 3–6 s); khái niệm mơ hồ → lumen (LSP xếp đích hạng 13/62); chưa phân loại
  → gọi song song. Câu luật chép lại nguyên văn ở đủ 5 chỗ móc.
- **`skills/tdq-intake/references/kiem-lsp-hieu-ung.md`** (mới) — bước kiểm **bằng hiệu ứng** ở
  intake: so `find_references` với grep theo số file phân biệt, ĐẠT khi LSP ≥ grep. Bậc 7 bắt
  nguyên nhân đã biết, bước này bắt triệu chứng dù nguyên nhân là gì.
- **`pyrightconfig.json`** (mới) — chính file mốc mà repo này đang thiếu, đưa độ phủ truy vấn
  quan hệ từ 1/15 file lên 15/15.

## 0.38.0 — 2026-09-02

Năm luật rời `~/.claude/CLAUDE.md` về plugin, instruction toàn cục cắt 57 → **29 dòng (−49%)**.
Thứ tự bắt buộc: viết luật vào `skills/` trước, kiểm, rồi mới cắt. Phương án gốc:
`docs/tdq/report/2026-09-01-2301-quet-instruction-vao-plugin.md`.

- **`skills/tdq-conventions/`** — `approval.md` nhận luật "không tự vào plan mode" (dưới bảng
  "NOT an approval", cùng họ); `SKILL.md` §7 Git nhận luật init git/worktree và ngoại lệ tự
  commit khi build TDQ bị chặn, đặt sát dòng nó là ngoại lệ; §8 Research nhận luật mem0.
- **`scripts/doc_lint.py`** — trần R6 của `tdq-conventions` 165 → 168, đổi lấy 28 dòng bỏ khỏi
  file nạp mỗi lượt của mọi project.
- **`docs/tdq/audit/luat-hien-co.md`** — 10 neo lệch do phần chèn trên được trỏ lại đúng chỗ.

## 0.37.0 — 2026-09-01

Lane nhanh có bước phân tích HIỆN TÊN, và độ sâu của bước đó có ngưỡng rõ ràng. Trước bản này
`phase_key` nuốt mọi pha của lane nhanh về hàng `quick`, nên phân tích không nhìn thấy được ở
đâu cả. Quan trọng: đây là phương án KHÔNG thêm cổng duyệt — lane nhanh vẫn đúng một cổng.

- **`scripts/tdq_state.py`** — thêm hàng `quick_analyze` vào `PHASE_TABLE` và `PHASE_ORDER`;
  `phase_key` trả hàng đó khi `lane=quick`, `phase=analyze` và chưa duyệt. `CONG_THEO_LANE`
  và `APPROVE_TARGETS` giữ NGUYÊN — có test khoá riêng canh điều này. Thêm khoá `brief_file`
  để đăng ký đường dẫn brief, ngang hàng `spec_file`/`plan_file`.
- **`skills/tdq-intake`** — `quick-lane.md` từ 9 lên 10 bước, chèn bước ghi kết quả phân tích
  vào brief; thêm mục ngưỡng B0/B1/B2: B1 đọc code LUÔN LUÔN (LSP + lumen song song), B0 chỉ
  khi vùng chưa có tiền lệ, B2 chỉ khi có ẩn số ngoài. Bỏ B0 hay B2 phải ghi một dòng lý do
  vào `## Phạm vi` của mini-plan — bỏ im lặng là lỗi QC.
- Ngưỡng lấy từ số đo thật trên 43 request đã đóng sổ. Pha `analyze` trung vị 372 s model,
  một request lane nhanh trọn gói 533 s. Bắt cả ba bước không điều kiện làm lane nhanh chậm
  thêm ~70 %. Chi tiết: `docs/tdq/report/2026-09-01-2122-lane-nhanh-kiem-ke-nang-luc.md`.

## Lịch sử cũ hơn

Bản 0.36.0 trở xuống nằm ở `docs/CHANGELOG-archive.md` — tách ra ngày 2026-09-17 vì file
chỉ-thêm này vượt trần 500 dòng của `doc_lint` R6. Chữ nghĩa giữ nguyên, không xoá dòng nào.
