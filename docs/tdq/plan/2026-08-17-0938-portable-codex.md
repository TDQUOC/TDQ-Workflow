# PLAN — Bộ portable tự sinh cho hai harness, có skill tự kiểm & tự setup

Ngày: 2026-08-17 · Spec: ../spec/2026-08-17-0938-portable-codex.md (bản 1.0, ĐÃ DUYỆT) · Lane: full
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md
Mode thực thi: main — chuỗi phụ thuộc tuyến tính chặt (manifest do P1 định hình thì P2 mới kiểm được, P3 mới gọi được), và `build_portable.py` bị 6 task cùng đụng nên chạy song song sẽ xung đột file. (user chốt "a" lúc 2026-08-17T10:23)
Trạng thái plan: HOÀN THÀNH — QC PASS vòng 3

## Quy tắc thi hành (áp cho mọi task)
1. Thứ tự phase là thứ tự phụ thuộc — không đảo.
2. Mỗi task: đánh `[~]` khi bắt đầu → viết test trước (đỏ) → code → test xanh → đổi sang
   `[x]` NGAY vào file này. Trạng thái checkbox: `[ ]` chưa làm · `[~]` đang làm · `[x]` xong.
3. Sau mỗi phase: chạy toàn bộ test suite, phải xanh mới sang phase sau.
4. Lệnh nào chạm state của workflow phải có `TDQ_PROJECT_DIR=<thư mục tạm>` ngay trên chính lệnh đó.
5. QC FAIL → thêm task fix vào mục QC của file này (không cần duyệt lại), loop đến khi pass.
6. Không commit/push cho đến khi user yêu cầu.

## P1 — Bộ sinh: khung, manifest, rewrite biến

- [x] **T1.1** (e14m) Tạo `scripts/build_portable.py` khung CLI: `--dest` (mặc định repo root),
  `--only claude|codex`, log service theo `TDQ_LOG`; định nghĩa hằng `SOURCE_DIRS` và
  `EXCLUDE` (loại `.git`, `docs/tdq`, `graphify-out`, `__pycache__`, `.pytest_cache`, `.venv`,
  `tests`) — Test: `python3 scripts/build_portable.py --help` exit 0 và in đủ 3 cờ
- [x] **T1.2** (e12m) Hàm `sinh_manifest(root)` → dict đủ 5 khối `files` (đường dẫn + sha256),
  `version` (đọc từ `.claude-plugin/plugin.json`), `python_min`, `external_commands`,
  `mcp_servers` — Test: `tests/test_build_portable.py::test_manifest_du_5_khoi`
- [x] **T1.3** (e10m) Hàm `doi_bien_plugin_root(text)` đổi `${CLAUDE_PLUGIN_ROOT}` và
  `$CLAUDE_PLUGIN_ROOT` → `${CLAUDE_PROJECT_DIR}`, trả kèm SỐ LẦN thay để đối chiếu —
  Test: `tests/test_build_portable.py::test_doi_bien_dem_dung_so_lan`
- [x] **T1.4** (e8m) Hàm `copy_loc(src, dst)` copy cây thư mục theo `EXCLUDE`, giữ quyền thực thi
  — Test: `tests/test_build_portable.py::test_copy_khong_mang_rac` (không có `state.json`,
  `.git`, `graphify-out` trong đích)

**Xong P1 khi**: `python3 -m pytest tests/test_build_portable.py -q` xanh với 4 test trên.

## P2 — Sinh bản `portable_claude/`

- [x] **T2.1** (e16m) Hàm `sinh_ban_claude(dest)`: dựng `.claude/skills/` (copy `skills/tdq-*`),
  `.claude/agents/` (copy `agents/*.md`), `scripts/` (copy script cần cho runtime) — Test:
  `tests/test_build_portable.py::test_ban_claude_du_thu_muc`
  Ghi nhận khi làm: `hooks/scripts/_common.py` suy thư mục scripts bằng `../../scripts`, nên
  `hooks/` và `scripts/` buộc phải nằm cạnh nhau trong một gốc chung. Gốc đó là
  `.claude/tdq/` (không đổ thẳng vào `.claude/`, vì skill chỉ được nạp ở đúng
  `.claude/skills/`). Kéo theo: rewrite biến phải thành `${CLAUDE_PROJECT_DIR}/.claude/tdq`,
  không phải `${CLAUDE_PROJECT_DIR}` trần — nếu không mọi lệnh gọi script trỏ hụt một tầng.
- [x] **T2.2** (e14m) Sinh `.claude/settings.json` từ `hooks/hooks.json`: chuyển 5 hook sang
  khoá `hooks`, đường dẫn dùng `${CLAUDE_PROJECT_DIR}`; giữ nguyên `env` từ `.claude/settings.json`
  nguồn — Test: `tests/test_build_portable.py::test_settings_co_du_5_hook_va_bien_dung`
  - Chạm: `hooks/hooks.json` đọc như dữ liệu văn bản → không import module hook (giữ luật
    `scripts/` không import `hooks/`)
- [x] **T2.3** (e8m) Sinh `.mcp.json` liệt kê MCP server bộ này cần (`tavily-primary`,
  `tavily-backup`), biến có default kiểu `${CLAUDE_PROJECT_DIR:-.}`, KHÔNG chứa giá trị secret
  — Test: `tests/test_build_portable.py::test_mcp_json_khong_co_secret`
- [x] **T2.4** (e10m) Bảo đảm bản claude sạch biến plugin: chạy rewrite trên mọi file text đã
  copy, đối chiếu số lần thay khớp số chỗ đếm ở nguồn — Test:
  `tests/test_build_portable.py::test_ban_claude_khong_con_plugin_root`

**Xong P1–P2 khi**: sinh thử vào thư mục tạm, `grep -rc CLAUDE_PLUGIN_ROOT` trả tổng 0.

## P3 — Sinh bản `portable_codex/`

- [x] **T3.1** (e14m) Hàm `sinh_ban_codex(dest)`: chuyển `skills/tdq-*/SKILL.md` thành
  `workflow/NN-<tên>.md` (đánh số theo thứ tự phase), copy `references/`, copy `scripts/` —
  Test: `tests/test_build_portable.py::test_ban_codex_du_file_workflow`
- [x] **T3.2** (e10m) Sinh `AGENTS.md` từ khuôn: mô tả workflow, trỏ `workflow/`, nêu rõ bước
  đầu tiên là chạy `06-checkportable.md` — Test:
  `tests/test_build_portable.py::test_agents_md_tro_checkportable_dau_tien`
- [x] **T3.3** (e8m) Sinh `workflow/phases.md` bằng cách gọi lại logic `phases-doc` của
  `tdq_state.py` (không chép bảng tay) — Test:
  `tests/test_build_portable.py::test_phases_md_khop_phase_table`
  - Chạm: `scripts/tdq_state.py` (chỉ ĐỌC hằng `PHASE_TABLE`, không sửa) → không node nào phụ thuộc

**Xong P3 khi**: `python3 scripts/build_portable.py --dest /tmp/tdqp` sinh đủ hai thư mục.

## P4 — Bộ kiểm & tự setup

- [x] **T4.1** (e16m) Tạo `scripts/tdq_checkportable.py`: lệnh `check --root <dir>` đọc
  `manifest.json`, so sha256 từng file, báo thiếu/sai, exit 0 khi sạch — Test:
  `tests/test_checkportable.py::test_phat_hien_file_sua_1_byte`
- [x] **T4.2** (e12m) Kiểm môi trường: Python tối thiểu, lệnh ngoài (`git`, `graphify`), MCP
  server khai trong manifest; thiếu thì báo rõ tên, không crash — Test:
  `tests/test_checkportable.py::test_bao_thieu_git_khong_crash`
- [x] **T4.3** (e18m) Lệnh `setup` tự vá theo quyết định 3B (quyền tối đa): tạo file/thư mục
  thiếu, cài package khi cần, sửa được cả config user-level; **bắt buộc** backup
  `<file>.tdq-bak-<timestamp>` trước khi ghi đè và log đủ để dựng lại việc đã làm — Test:
  `tests/test_checkportable.py::test_setup_backup_truoc_khi_ghi_de`
- [x] **T4.4** (e10m) Chặn rò secret: mọi đường in ra (log, report) chỉ in TÊN khoá, không in
  giá trị — Test: `tests/test_checkportable.py::test_khong_in_gia_tri_secret`

**Xong P4 khi**: `python3 -m pytest tests/test_checkportable.py -q` xanh.

## P5 — Skill `tdq-checkportable` & instruction mặc định

- [x] **T5.1** (e10m) Sinh `portable_claude/.claude/skills/tdq-checkportable/SKILL.md` — chỉ
  NHẮC lệnh `python3 scripts/tdq_checkportable.py check|setup`, tuyệt đối không chép logic
  (luật kiến trúc `skills/` chỉ nhắc tên lệnh) — Test: `grep -c "def \|^import " <file>` = 0
  Ghi nhận khi làm: nguồn của skill này KHÔNG đặt trong `skills/`. Đặt ở đó làm vỡ hai test
  khoá ngân sách context của bộ chính (`test_skill_shape::test_exactly_six_skills`,
  `test_token_budget::test_skill_descriptions_total`) — đúng ra vì skill này chỉ có nghĩa ở
  máy đích, không phải skill của repo. Nguồn nằm ở `portable_src/skills/tdq-checkportable/`.
- [x] **T5.2** (e8m) Sinh `portable_codex/workflow/06-checkportable.md` — bản instruction cho
  harness không có skill system, cùng nội dung lệnh — Test:
  `tests/test_build_portable.py::test_codex_co_file_checkportable`
- [x] **T5.3** (e10m) Instruction mặc định của CẢ HAI bản trỏ chạy `tdq-checkportable` đầu
  tiên (bản claude: dòng trong `SKILL.md` gốc + README; bản codex: `AGENTS.md`) — Test:
  `tests/test_build_portable.py::test_ca_hai_ban_deu_goi_check_dau_tien`
- [x] **T5.4** (e12m) README mỗi bản nêu **ba giới hạn cứng** (trust dialog, MCP approve,
  restart khi thư mục mới) và cảnh báo `tdq-checkportable` có quyền tự setup tối đa — Test:
  `tests/test_build_portable.py::test_readme_neu_du_3_gioi_han`

**Xong P5 khi**: cả hai bản sinh ra đều có file skill/instruction và README đủ cảnh báo.

## P6 — Tích hợp & dọn bản cũ

- [x] **T6.1** (e8m) Sinh thật `portable_claude/` và `portable_codex/` vào repo, thêm cả hai
  vào `.graphifyignore` để đồ thị không đếm trùng bản sao — Test:
  `grep -c "portable_claude\|portable_codex" .graphifyignore` ≥ 2
- [x] **T6.2** (e6m) Xoá thư mục `portable/` viết tay cũ — Test: `test -d portable` trả false
  - Chạm: `portable/` → không node nào phụ thuộc (đã kiểm: `.graphifyignore` loại tài liệu)
- [x] **T6.3** (e8m) Cập nhật `README.md` root + `docs/notes/user-level-install.md`: thêm cách
  dùng bản portable mới, bỏ chỉ dẫn trỏ `portable/` cũ — Test:
  `grep -c "portable/" README.md docs/notes/user-level-install.md` = 0
- [x] **T6.4** (e6m) Bump version trong `.claude-plugin/plugin.json` + ghi `CHANGELOG.md` —
  Test: `python3 scripts/doc_lint.py CHANGELOG.md` exit 0

**Xong P6 khi**: repo có hai thư mục portable mới, không còn `portable/`.

## P7 — Log & test bắt buộc

- [x] **T7.1** (e8m) Log service bật mặc định cho cả hai script mới (timestamp ISO, ra stderr,
  tắt bằng `TDQ_LOG=0` — cùng khuôn `tdq_timing.py`) — Test:
  `TDQ_LOG=0 python3 scripts/build_portable.py --dest /tmp/x 2>&1 | wc -l` = 0 dòng log
- [x] **T7.2** (e10m) Chạy trọn bộ test repo, không để test đỏ nào — Test:
  `python3 -m pytest tests/ -q` exit 0

## P8 — QC độc lập

- [x] **T8.1** (e20m) Giao agent `tdq-qc-tester` chạy độc lập 10 hạng mục DoD, dán output thật
  vào `docs/tdq/qc/2026-08-17-0938-portable-codex.md` — Test: file QC tồn tại, đủ 10 mục,
  không mục nào FAIL
  - Dùng: `tdq-build`
  - Để: điều phối bước QC + viết report cuối theo khuôn, nạp skill TRƯỚC bước đỏ. Agent ngoài
    không có skill system: đọc `skills/tdq-build/SKILL.md` rồi làm theo.
  - Ra: `docs/tdq/qc/2026-08-17-0938-portable-codex.md` và `docs/tdq/reports/2026-08-17-0938-portable-codex.md`
  - Kiểm: `test -f docs/tdq/qc/2026-08-17-0938-portable-codex.md && grep -c "PASS" $_` ≥ 10
  - Không dùng cho: sửa code sản phẩm — QC chỉ kiểm và báo, fix đi qua vòng `## QC vòng N`.
- [x] **T8.2** (e10m) Nghi vấn API Claude Code phát sinh lúc implement → tra cứu xác minh trước
  khi code theo phỏng đoán — Test: mọi kết luận về cơ chế Claude Code trong report đều có
  dẫn nguồn docs
  - Dùng: `claude-code-guide`
  - Để: xác minh cơ chế nạp skill/hook/MCP ở project-level khi implement gặp chỗ chưa chắc,
    nạp skill TRƯỚC bước đỏ. Agent ngoài không có skill system: hỏi trực tiếp tài liệu
    code.claude.com/docs rồi làm theo.
  - Ra: câu trả lời có dẫn nguồn, ghi vào report mục ghi chú kỹ thuật
  - Kiểm: `grep -c "code.claude.com" docs/tdq/reports/2026-08-17-0938-portable-codex.md` ≥ 1
  - Không dùng cho: quyết định thay user về phạm vi hay kiến trúc — chỉ tra cứu sự thật kỹ thuật.
- [x] **T8.3** (e8m) Chốt sổ plan: QC FAIL thì thêm task fix dưới `## QC vòng N — fix` theo
  đúng khuôn rồi làm red→green; QC pass hết thì tick nốt checkbox còn sót và đổi header
  thành HOÀN THÀNH — Test: không còn dòng `- [ ]` nào trong plan và header ghi HOÀN THÀNH
  - Dùng: `tdq-plan`
  - Để: giữ plan đúng khuôn khi thêm task fix vòng QC và lúc chốt sổ, nạp skill TRƯỚC bước đỏ.
    Agent ngoài không có skill system: đọc `skills/tdq-plan/SKILL.md` rồi làm theo.
  - Ra: `docs/tdq/plan/2026-08-17-0938-portable-codex.md` ở trạng thái HOÀN THÀNH
  - Kiểm: `grep -c "^- \[ \]" docs/tdq/plan/2026-08-17-0938-portable-codex.md` = 0
  - Không dùng cho: đổi phạm vi hay thêm task ngoài vòng fix QC — việc đó phải quay lại spec.

## Definition of Done

Trỏ về §6 của spec. Mười hạng mục, mỗi dòng một lệnh kiểm:

1. Q1 Test tự động toàn bộ — `python3 -m pytest tests/ -q` exit 0
2. Q2 Sinh được cả hai bản — `python3 scripts/build_portable.py --dest /tmp/tdqp` exit 0, tồn tại 2 thư mục
3. Q3 Không sót biến plugin — `grep -rc "CLAUDE_PLUGIN_ROOT" /tmp/tdqp/portable_claude` tổng = 0
4. Q4 Manifest khớp thực tế — `python3 scripts/tdq_checkportable.py check --root /tmp/tdqp/portable_claude` exit 0
5. Q5 Phát hiện được hỏng — sửa 1 byte rồi chạy lại Q4, exit khác 0 và chỉ đúng tên file bị sửa
6. Q6 Phát hiện thiếu lệnh ngoài — chạy check với `PATH` không có `git`, báo thiếu và không crash
7. Q7 Bản sinh không chứa rác — `find /tmp/tdqp -name state.json -o -name ".git" -o -name "graphify-out"` rỗng
8. Q8 Skill không chép logic — `grep -c "def \|import " portable_claude/.claude/skills/tdq-checkportable/SKILL.md` = 0
9. Q9 Bản cũ đã bỏ — `test -d portable` trả false
10. Q10 Log service hoạt động — bật có log timestamp, `TDQ_LOG=0` thì im

## QC — vòng fix 1

QC độc lập (agent `tdq-qc-tester`) trả VERDICT FAIL. Q1–Q10 PASS, nhưng phát hiện 5 khuyết
tật mà 10 hạng mục DoD không phủ tới. Task fix (không đổi phạm vi spec):

- [x] **F1.1** (e10m) `tdq_checkportable.py` tự tìm gốc bundle: đi ngược lên từ vị trí script
  tới thư mục đầu tiên có `manifest.json`, thay vì mặc định `dirname(dirname(__file__))` —
  chạy đúng "Bước 0" mà chính tài liệu hướng dẫn thì hiện đang exit 1 trên bundle sạch —
  Test: `tests/test_checkportable.py::test_chay_khong_can_root`
- [x] **F1.2** (e8m) Bản codex cũng có `README.md` (spec §2 đầu ra #4); test canh cửa kiểm CẢ
  HAI bản chứ không chỉ bản claude — Test:
  `tests/test_build_portable.py::test_readme_neu_du_3_gioi_han`
- [x] **F1.3** (e16m) `setup` phải vá thật hoặc nói thật: `.claude/settings.json` và `.mcp.json`
  thiếu/lệch thì sinh lại (ghi đè có backup `.tdq-bak-`), phần không tự vá được thì exit khác
  0 kèm chỉ dẫn chép lại từ bản gốc. Kéo `_sinh_settings`/`_sinh_mcp` sang
  `tdq_checkportable.py` (file DUY NHẤT đi theo bundle) và cho `build_portable.py` import
  lại — Test: `tests/test_checkportable.py::test_setup_va_that_va_bao_dung`
- [x] **F1.4** (e8m) Tài liệu bản sinh nói đúng năng lực thật của `setup` — bỏ lời hứa "tự cài
  gói / sửa cấu hình mức người dùng" mà mã không có đường nào thực hiện — Test:
  `tests/test_build_portable.py::test_tai_lieu_khong_hua_qua_nang_luc`
- [x] **F1.5** (e6m) `manifest.json` có `files` rỗng là manifest HỎNG, không phải "sạch 0
  file" — Test: `tests/test_checkportable.py::test_manifest_rong_la_loi`

## QC — vòng fix 2

Vòng 2: 5 khuyết tật vòng 1 PASS hết, DoD Q1–Q10 và 17 mục hồi quy PASS. Còn 5 điểm nhỏ:

- [x] **F2.1** (e8m) `to_ten_khoa` là dead code và có ternary hai nhánh trùng nhau — cho nó
  caller thật (`check` in trạng thái biến môi trường MCP cần có) hoặc bỏ hẳn — Test:
  `tests/test_checkportable.py::test_check_bao_trang_thai_bien_mcp`
- [x] **F2.2** (e8m) `setup` trên bundle chỉ đọc ném traceback `PermissionError` — phải báo
  lỗi tử tế và exit khác 0 — Test: `tests/test_checkportable.py::test_setup_bundle_chi_doc`
- [x] **F2.3** (e4m) Docstring của chính `tdq_checkportable.py` vẫn hứa "cài gói, sửa cấu hình
  mức người dùng" — Test: `tests/test_checkportable.py::test_docstring_khong_hua_qua`
- [x] **F2.4** (e6m) Mất trắng `settings.json` thì in đồng thời `ĐÃ LÀM sinh lại` và `CÒN …`,
  đọc như tự mâu thuẫn; phải nói rõ sinh lại được phần hook nhưng khối `env` không tái tạo
  được — Test: `tests/test_checkportable.py::test_settings_mat_trang_bao_ro`
- [x] **F2.5** (e4m) `setup` ghi `.mcp.json` cả ở bản codex, nơi file đó không có trong
  manifest — chỉ vá thứ manifest thật sự đòi — Test:
  `tests/test_checkportable.py::test_setup_khong_them_file_la`
