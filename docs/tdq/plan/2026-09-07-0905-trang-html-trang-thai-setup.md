# PLAN — Trang HTML trạng thái setup TDQ-Workflow

Ngày: 2026-09-07 · Spec: ../spec/2026-09-07-0905-trang-html-trang-thai-setup.md (bản 1.0, ĐÃ DUYỆT) · Lane: full
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md
Mode thực thi: **main** (user chốt lúc duyệt) — đo bằng `tdq_bench simulate` trên chính plan này với hệ số agent 1.5: đội 21.5 phút so với main 26.5 phút, hơn 5.0 phút (ĐỀ XUẤT, user chốt lúc duyệt)
Trạng thái plan: HOÀN THÀNH

## Mục lục

- Quy tắc thi hành (áp cho mọi task)
- P1 — Bộ thu số liệu
- P2 — Bộ kết xuất HTML
- P3 — CLI & tích hợp repo
- P4 — Log & test bắt buộc
- P5 — QC độc lập
- Luật file nóng
- Cụm song song
- Definition of Done

## Quy tắc thi hành (áp cho mọi task)
1. Thứ tự phase là thứ tự phụ thuộc — không đảo.
2. Mỗi task: đánh `[~]` khi bắt đầu → viết test trước (đỏ) → code → test xanh → đổi sang
   `[x]` NGAY vào file này. Trạng thái checkbox: `[ ]` chưa làm · `[~]` đang làm · `[x]` xong.
3. Sau mỗi phase: chạy toàn bộ test suite, phải xanh mới sang phase sau.
4. Lệnh nào chạm state của workflow phải có `TDQ_PROJECT_DIR=<thư mục tạm>` ngay trên chính lệnh đó.
5. QC FAIL → thêm task fix vào mục QC của file này (không cần duyệt lại), loop đến khi pass.
6. Không commit/push cho đến khi user yêu cầu.
7. Không lệnh nào trong plan này được sửa cấu hình máy; mọi lệnh ngoài chỉ ĐỌC.

## P1 — Bộ thu số liệu

- [x] **T1.1** (e14m) Dựng khung `scripts/setup_status.py`: log service theo đúng khuôn
  `TDQ_LOG` của repo, hàm bọc lệnh ngoài `_run_tool()` (thiếu binary → ô "chưa cài" kèm lệnh
  cài gợi ý, không ném exception, không tự cài), và hàm `mask_secrets()` che mọi giá trị đứng
  sau `key=`/`apikey=`/`token=`/`authorization` — Test: `python3 -m unittest tests.test_setup_status -k mask` xanh, gồm ca chuỗi chứa `tvly-dev-` giả và ca binary không tồn tại
  - Chạm: `scripts/setup_status.py`, `tests/test_setup_status.py` → file mới, chưa node nào phụ thuộc

- [x] **T1.2** (e14m) Collector `thu_dependency()`: graphify, lumen, agent-lsp, ollama — có/không,
  phiên bản, đường dẫn binary; cộng `thu_lumen()` lấy model qua `tdq_lsp._model_lumen()` và các
  endpoint đọc từ `~/.config/lumen/config.yaml` — Test: `python3 -m unittest tests.test_setup_status -k dependency` xanh trên fixture giả lập cả ca có lẫn ca thiếu binary
  - Chạm: `scripts/setup_status.py`, `tests/test_setup_status.py` → phụ thuộc `scripts/tdq_lsp.py` (chỉ import, không sửa)
  - Cần: T1.1

- [x] **T1.3** (e12m) Collector `thu_workflow()`: skill trên đĩa qua `skill_inventory.inventory()`,
  hook + bề mặt tài liệu qua `context_surface.scan()` và `measure_hooks()`, state hiện tại qua
  `tdq_state`, cộng 7 bậc từ `tdq_lsp.chay_kiem()` — Test: `python3 -m unittest tests.test_setup_status -k workflow` xanh, khẳng định mỗi khối trả về khoá cố định kể cả khi nguồn rỗng
  - Chạm: `scripts/setup_status.py`, `tests/test_setup_status.py` → import `scripts/skill_inventory.py`, `scripts/context_surface.py`, `scripts/tdq_lsp.py` (chỉ đọc)
  - Cần: T1.2

- [x] **T1.4** (e18m) Collector `thu_thuc_nhan()` — phần "Claude Code thực sự nhận được gì":
  parse `claude mcp list` ra tên + trạng thái kết nối + URL/lệnh đã đi qua `mask_secrets()`; đọc
  khối `args` và `env` của server `lsp` trong `~/.claude.json`, chạy `agent-lsp doctor` với chính
  `env` đó (có `DOTNET_ROOT`) rồi parse `Status: ok|failed` thành cặp **khai báo / thực nhận**
  — Test: `python3 -m unittest tests.test_setup_status -k thuc_nhan` xanh trên fixture output thật, gồm ca định dạng lạ → ghi "không phân tích được" thay vì vỡ
  - Chạm: `scripts/setup_status.py`, `tests/test_setup_status.py` → file đã có từ T1.1
  - Cần: T1.3

**Xong P1 khi**: gọi `thu_tat_ca()` trên máy này trả về dict đủ 4 khối, không ném exception, và toàn bộ test của P1 xanh.

## P2 — Bộ kết xuất HTML

- [x] **T2.1** (e16m) Tạo `scripts/setup_status_render.py`: hàm `render(data) -> str` dựng trang
  tự chứa (CSS nội tuyến, không script/font/ảnh ngoài), 4 khối workflow · dependency · chi tiết ·
  MCP, chữ hiển thị tiếng Việt, mỗi ô thiếu dữ liệu hiện "không đọc được" kèm lý do — Test: `python3 -m unittest tests.test_setup_status_render` xanh, khẳng định chuỗi HTML không chứa `http://`/`https://` trong `src=`/`href=` và có đủ 4 tiêu đề khối
  - Chạm: `scripts/setup_status_render.py`, `tests/test_setup_status_render.py` → file mới, chưa node nào phụ thuộc
  - Cần: T1.1

- [x] **T2.2** (e6m) Bảng "khai báo vs thực nhận" cho language server và dòng ghi rõ giới hạn:
  skill built-in của Claude Code không đọc được từ script — Test: `python3 -m unittest tests.test_setup_status_render -k khai_bao` xanh với fixture 14 khai / 13 sống, trang phải nêu đúng tên server chết và có đúng một dòng nói về skill built-in
  - Chạm: `scripts/setup_status_render.py`, `tests/test_setup_status_render.py`, `scripts/setup_status.py` → file từ T2.1; sửa đúng một hằng số ghi chú trong `setup_status.py`
  - Cần: T2.1

**Xong P2 khi**: render chạy được trên máy trắng, không cần agent-lsp/lumen/ollama/graphify.

## P3 — CLI & tích hợp repo

- [x] **T3.1** (e8m) CLI `main()` của `scripts/setup_status.py`: thu → render → ghi
  `setup_status.html` ở gốc repo, thoát 0 kể cả khi vài nguồn lỗi, in đường dẫn file ra stdout
  — Test: chạy `python3 scripts/setup_status.py` thật, `echo $?` bằng 0 và file tồn tại, mở ra có đủ 4 khối
  - Chạm: `scripts/setup_status.py`, `tests/test_setup_status.py` → file từ T1.4
  - Cần: T1.4, T2.2

- [x] **T3.2** (e3m) Thêm `setup_status.html` vào `.gitignore` — Test: sinh trang xong `git status --porcelain | grep setup_status.html` không ra dòng nào
  - Chạm: `.gitignore` → file cấu hình, không node code nào phụ thuộc
  - Cần: T3.1

## P4 — Log & test bắt buộc

- [x] **T4.1** (e5m) Log service bật mặc định trên cả 2 script: mỗi nguồn một dòng ISO timestamp
  ra stderr kèm thời gian và kết quả; `TDQ_LOG=0` im hoàn toàn — Test: `python3 scripts/setup_status.py 2>/tmp/tdq-log.txt >/dev/null; head -1 /tmp/tdq-log.txt` có timestamp, còn `TDQ_LOG=0 python3 scripts/setup_status.py 2>/tmp/tdq-log0.txt >/dev/null; wc -c < /tmp/tdq-log0.txt` trả 0 (dùng file thay pipe vì zsh MULTIOS làm `2>&1 >/dev/null` vẫn nhả stdout vào pipe), và nội dung HTML hai lần chạy giống nhau
  - Chạm: `scripts/setup_status.py`, `scripts/setup_status_render.py` → file từ T3.1 và T2.2
  - Cần: T3.1

- [x] **T4.2** (e5m) Toàn bộ test chạy bằng một lệnh, không thêm ca đỏ so với nền — Test: `python3 -m unittest discover -s tests -t tests -p 'test_setup_status*.py'` xanh, và suite tổng có số ca đỏ bằng đúng nền đo trước khi làm
  - Chạm: `tests/test_setup_status.py`, `tests/test_setup_status_render.py` → file từ P1–P2
  - Cần: T4.1

- [x] **T4.3** (e4m) Sửa hồi quy phát hiện lúc chạy suite: `subprocess.run(..., text=True)` mới
  thêm làm `tests/test_bao_cao_da_nen_tang.py` đỏ vì báo cáo đa nền tảng đếm số chỗ `subprocess`
  thiếu `encoding=`. Đổi sang `encoding="utf-8", errors="replace"` — đúng luật đa nền tảng của
  repo, không phải sửa con số trong báo cáo — Test: `python3 -m unittest discover -s tests -t tests -p 'test_bao_cao_da_nen_tang.py'` xanh
  - Chạm: `scripts/setup_status.py` → file từ T4.1
  - Cần: T4.2

## P5 — QC độc lập

- [x] **T5.1** (e10m) Giao `tdq-qc-tester` chấm lại Q1–Q10 và ghi bằng chứng vào
  `docs/tdq/qc/2026-09-07-0905-trang-html-trang-thai-setup.md` — Test: file QC tồn tại, có kết luận PASS/FAIL cho từng Q kèm lệnh đã chạy
  - Dùng: `tdq-lsp-setup`
  - Để: cấp cho QC đúng thang 7 bậc và thứ tự tìm kiếm để đối chiếu khối "workflow" của trang với thực tế máy, nạp trước bước chấm.
    Agent ngoài không có skill system: đọc `skills/tdq-lsp-setup/SKILL.md` rồi làm theo.
  - Ra: `docs/tdq/qc/2026-09-07-0905-trang-html-trang-thai-setup.md`
  - Kiểm: `python3 scripts/tdq_lsp.py check` và số bậc trong file QC khớp số bậc trang HTML hiển thị
  - Không dùng cho: cài đặt hay sửa bất kỳ language server nào — QC chỉ đọc

- [x] **T5.2** (e5m) Đối chiếu khối state của trang với state thật — Test: request slug, lane và phase trên trang khớp đúng output của `python3 scripts/tdq_state.py get`
  - Dùng: `tdq-status`
  - Để: lấy đúng cách đọc state chuẩn để so với những gì trang tự đọc, nạp trước khi so.
    Agent ngoài không có skill system: đọc `skills/tdq-status/SKILL.md` rồi làm theo.
  - Ra: một mục đối chiếu trong file QC ở T5.1
  - Kiểm: `python3 scripts/tdq_state.py get` và trang HTML hiện cùng slug/lane/phase
  - Không dùng cho: ghi hay đổi state — chỉ đọc

- [x] **T5.3** (e8m) Chạy plan này đến hết và đóng sổ theo đúng khuôn build — Test: mọi task trong file này `[x]`, working log ngày có mục của request
  - Dùng: `tdq-build`
  - Để: giữ đúng luật đỏ-xanh, tick ngay khi test xanh, và đường đóng turn duy nhất qua `tdq_finish.py`, nạp từ đầu phase implement.
    Agent ngoài không có skill system: đọc `skills/tdq-build/SKILL.md` rồi làm theo.
  - Ra: plan này tick đủ + `docs/workinglog/2026-09-07.md` có mục
  - Kiểm: `grep -c '^- \[ \]' docs/tdq/plan/2026-09-07-0905-trang-html-trang-thai-setup.md` trả 0
  - Không dùng cho: commit hay push — chỉ làm khi user yêu cầu riêng

## Luật file nóng

`scripts/setup_status.py` là file nóng: 5 task chạm (T1.1–T1.4, T3.1). Xử lý theo cách **nâng
lên đợt sớm**: T1.1 dựng khung dùng chung (log, `_run_tool`, `mask_secrets`, hình dạng dict) ở
đợt đầu tiên, các task sau nhánh ra từ khung đã ổn định; đồng thời T1.2 → T1.3 → T1.4 → T3.1
khai `Cần:` thành một chuỗi, nên máy xếp chúng vào các đợt KHÁC nhau, không bao giờ có hai
worktree cùng sửa file này. `tests/test_setup_status.py` đi kèm từng task nên nóng theo đúng
cách đó và được chuỗi `Cần:` bảo vệ y hệt.

## Cụm song song

- **Cụm A** — `scripts/setup_status.py` + `tests/test_setup_status.py`: T1.1 → T1.2 → T1.3 →
  T1.4 → T3.1. Nội bộ tuần tự, không tách được.
- **Cụm B** — `scripts/setup_status_render.py` + `tests/test_setup_status_render.py`: T2.1 →
  T2.2. Chỉ cần hình dạng dict từ T1.1, nên chạy song song được với T1.2–T1.4.
- **Cụm C** — `.gitignore`: T3.2, một task, chờ T3.1.

Trần tốc độ của mode đội là 2 luồng. `tdq_bench simulate` chia được 13 task thành 7 đợt, giao
9 task cho trợ lý và giữ 4 task cho leader; kết quả đo: đội 21.5 phút, main 26.5 phút — cụm B
chạy song song đủ để cắt 5.0 phút khỏi đường găng, ngay cả khi tính trợ lý chậm hơn 1.5 lần.

## QC vòng 1 — fix

Nguồn: agent `tdq-qc-tester` chấm độc lập — Q1–Q10, QC-F1..F3 đều PASS, nhưng nêu 4 khuyết tật
nằm ngoài DoD. Defect "cột thực nhận bỏ qua dòng `[error]` của doctor" đã ĐO LẠI và BÁC: chạy
doctor 3 lần cho `Summary: 14 ok, 0 failed` và `rc=0` ổn định, còn các dòng `[error] ... exited
with error after 0s` là nhiễu lúc đóng tiến trình, mỗi lần một tập khác (4 → 7 → 5 dòng, server
khác nhau); đếm chúng là "chết" sẽ báo hỏng SAI. Thay bằng QC1.2 dưới đây.

- [x] **QC1.1** (e8m) `mask_secrets()` che thêm cờ CLI và biến môi trường, không chỉ query
  string: `--api-key=X`, `--token X`, `TAVILY_API_KEY=X` — Test: `mask_secrets('/usr/bin/mcpx --api-key=bimat1 TAVILY_API_KEY=bimat2')` không còn `bimat1`/`bimat2`, vẫn giữ tên tham số
  - Chạm: `scripts/setup_status.py`, `tests/test_setup_status.py`
- [x] **QC1.2** (e10m) Đối chiếu chéo kết luận của `agent-lsp doctor`: đọc dòng `Summary: N ok,
  M failed` và returncode, lệch với số đếm theo từng server thì ghi cảnh báo vào `chi_tiet`;
  thêm một dòng trên trang nói rõ dòng `[error]` lúc đóng tiến trình KHÔNG tính là chết —
  Test: fixture Summary lệch số đếm sinh ra cảnh báo, fixture khớp thì không
  - Chạm: `scripts/setup_status.py`, `scripts/setup_status_render.py`, `tests/test_setup_status.py`, `tests/test_setup_status_render.py`
- [x] **QC1.3** (e3m) Lệnh cài agent-lsp gợi ý sai (`npm install -g @agent-lsp/cli`) — lấy đúng
  hằng `INSTALL_AGENT_LSP` của `scripts/tdq_lsp.py` thay vì chép tay — Test: gợi ý cho
  `agent-lsp` bằng đúng `tdq_lsp.INSTALL_AGENT_LSP`
  - Chạm: `scripts/setup_status.py`, `tests/test_setup_status.py`
- [x] **QC1.4** (e5m) `render()` chịu được dict sai kiểu (`{'workflow': 123}`) thay vì ném
  `AttributeError` — Test: `render({'workflow': 123, 'mcp': 'x'})` trả HTML có "không đọc được"
  - Chạm: `scripts/setup_status_render.py`, `tests/test_setup_status_render.py`
- [x] **QC1.5** (e6m) QC-F4/OCP: thêm một khối mới cho trang phải sửa cả `KHOI` lẫn thân
  `render()` — gộp thành một bảng dữ liệu duy nhất (mã, tiêu đề, khoá dữ liệu, hàm dựng) để
  thêm khối là thêm ĐÚNG một dòng — Test: `render` không còn dict `than` viết tay, trang vẫn đủ 4 khối
  - Chạm: `scripts/setup_status_render.py`, `tests/test_setup_status_render.py`
- [x] **QC1.6** (e4m) Bản vá QC1.2 tự có lỗi: `_RE_DOCTOR_TOM_TAT` neo `^` nhưng dùng
  `re.search` không cờ `re.M`, nên chỉ khớp khi `Summary:` nằm đúng đầu chuỗi — fixture test
  lại đúng như vậy nên test xanh giả, còn trang thật báo nhầm "không thấy dòng Summary". Thêm
  `re.M` và một ca ghim đặt `Summary` ở cuối output — Test: `_doi_chieu_doctor` với output có
  khối server rồi mới tới `Summary` trả `""`; trang sinh thật không còn dòng cảnh báo
  - Chạm: `scripts/setup_status.py`, `tests/test_setup_status.py`

## Definition of Done

- [x] Q1 Trang tự chứa, mở offline vẫn đủ — `python3 -m unittest discover -s tests -t tests -p 'test_setup_status_render.py' -k TuChua`
- [x] Q2 Không rò bí mật, khoá giả không lọt vào HTML — `python3 -m unittest discover -s tests -t tests -p 'test_setup_status.py' -k CheBiMat`
- [x] Q3 Phân biệt khai báo vs thực nhận, chỉ đúng tên server chết — `python3 -m unittest discover -s tests -t tests -p 'test_setup_status_render.py' -k KhaiBaoVaThucNhan`
- [x] Q4 Đủ 4 khối trên trang sinh thật — `grep -c 'data-khoi=' setup_status.html` trả 4
- [x] Q5 Nguồn thiếu thì ghi "không đọc được", vẫn thoát 0 — `PATH=/usr/bin:/bin python3 scripts/setup_status.py; echo $?`
- [x] Q6 Có đúng một dòng về giới hạn skill built-in — `grep -c 'skill built-in' setup_status.html` trả 1
- [x] Q7 Log bật mặc định, `TDQ_LOG=0` im — `TDQ_LOG=0 python3 scripts/setup_status.py 2>/tmp/tdq-log0.txt >/dev/null; wc -c < /tmp/tdq-log0.txt` trả 0
- [x] Q8 Không bẩn git — `git status --porcelain | grep -c setup_status.html` trả 0
- [x] Q9 Test kết xuất chạy được không cần công cụ ngoài — `python3 -m unittest discover -s tests -t tests -p 'test_setup_status_render.py'`
- [x] Q10 Không hồi quy — `python3 -m unittest discover -s tests -t tests -p 'test_*.py'` số ca đỏ bằng nền
- [x] Q11 QC độc lập kết luận PASS — `cat docs/tdq/qc/2026-09-07-0905-trang-html-trang-thai-setup.md`
