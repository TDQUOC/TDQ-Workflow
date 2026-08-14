# PLAN — Soul cho workflow và thư viện rule kỹ thuật đa ngôn ngữ

Ngày: 2026-08-14 · Spec: ../spec/2026-08-14-set-soul-workflow.md (bản 1.2, ĐÃ DUYỆT) · Lane: full
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md
Mode thực thi: main — luật nền và phép kiểm phải nhất quán từng câu chữ; riêng P4 (7 file
rule ngôn ngữ) là chỗ giao trợ lý được, user chốt ở cổng mode.
Trạng thái plan: HOÀN THÀNH 2026-08-14 · duyệt 22:28 · mode main user chốt 22:32

## Quy tắc thi hành (áp cho mọi task)
1. Thứ tự phase là thứ tự phụ thuộc — không đảo.
2. Mỗi task: đánh `[~]` khi bắt đầu → viết test trước (đỏ) → code → test xanh → đổi sang
   `[x]` NGAY vào file này. Trạng thái checkbox: `[ ]` chưa làm · `[~]` đang làm · `[x]` xong.
3. Sau mỗi phase: chạy toàn bộ test suite, phải xanh mới sang phase sau.
4. Lệnh nào chạm state của workflow phải có `TDQ_PROJECT_DIR=<thư mục tạm>` ngay trên chính lệnh đó.
5. QC FAIL → thêm task fix vào mục QC của file này (không cần duyệt lại), loop đến khi pass.
6. Không commit/push cho đến khi user yêu cầu.

## P0 — Đo mốc trước khi sửa

- [x] **T0.1** (n2 e6m) Đo mốc và ghi số vào chính task này: tổng token 6 file
  `skills/*/SKILL.md` bằng `token_audit.py`, số test hiện có, `doc_lint` toàn kho —
  Test: `python3 scripts/token_audit.py` và `python3 -m pytest tests/ -q` chạy được, số
  ghi lại trong plan (mốc để đối chiếu ở Q14 và Q15)
  - Mốc token: 6 SKILL.md = 26.664 ký tự ≈ 6.666 token (build 1320 · conventions 1599 ·
    intake 1107 · plan 1366 · spec 792 · status 482). `token_audit.py` chỉ đo transcript,
    không đo file → Q14 dùng cùng phép ước `ký tự / 4` cho hai lần đo nên vẫn so được.
  - Mốc test: `574 passed, 280 subtests passed` · Mốc doc_lint toàn kho: exit 0, còn 3
    nhắc R4/R5 sẵn có trong `portable/` (không thuộc phạm vi request) · `skills/` có
    đúng 28 file `.md`.

**Xong P0 khi**: plan có 3 con số mốc, chưa sửa file nào.

## P1 — Soul và máy giữ soul

- [x] **T1.1** (n5 e15m) Tạo `tests/test_soul_rules.py` với test `thu_tu_uu_tien`: đọc
  `soul.md`, đòi 3 tầng xuất hiện đúng thứ tự chất lượng → runtime → context cost, và có
  mục phạm vi áp dụng nêu tên brief/spec/plan/qc/report — Test: chạy lần đầu phải ĐỎ vì
  chưa có `soul.md` → đã đỏ đúng 2 test lúc 22:34
- [x] **T1.2** (n6 e25m) Viết `skills/tdq-conventions/references/soul.md` theo đúng khuôn
  3 mục, dưới 150 dòng, gồm 4 nguyên tắc: mục đích harness · thứ tự ưu tiên và luật phân
  xử khi hai luật đá nhau · viết cho model yếu nhất · phạm vi áp dụng (mọi skill, mọi tài
  liệu request, mọi bổ sung sau này) — Test: `pytest tests/test_soul_rules.py -k thu_tu`
  chuyển XANH
- [x] **T1.3** (n3 e10m) Thêm test `dong_tro_soul` rồi thêm dòng trỏ soul vào
  `skills/tdq-conventions/SKILL.md` mục `## 11. Chất lượng` và vào `portable/AGENTS.md` —
  Test: `pytest -k dong_tro_soul` xanh, `grep -c soul` ≥ 1 ở cả hai file
  - Fix lint kèm theo: SKILL.md chạm trần 120 dòng → nén dòng trỏ còn 1 dòng; AGENTS.md
    mục "Không có ở bản portable" có câu 51 từ SẴN TỪ TRƯỚC → tách 4 câu (ghi vào biên
    bản P3). Lint 2 file exit 0, 27 test liên quan xanh.
- [x] **T1.4** (n7 e30m) Thêm rule R9 vào `scripts/doc_lint.py`: file khớp `soul.md` hoặc
  `references/rules/` phải có đủ 3 heading `## Khi nào áp dụng`, `## Làm gì`, `## Tự kiểm`;
  file ngoài phạm vi không bị soi — Test: `pytest -k r9` xanh, gồm một ca file thiếu mục
  cho exit 1 và một ca file ngoài phạm vi cho exit 0

**Xong P1 khi**: `soul.md` tồn tại, 4 test mới xanh, `doc_lint` chính nó vẫn exit 0.

## P2 — Soul áp cho tài liệu từng request

- [x] **T2.1** (n4 e15m) — đỏ 5 subtest → sửa đủ 5 khuôn → 5 subtest xanh, lint 5 file
  exit 0 — Thêm test `khuon_tai_lieu` đòi dòng `Soul:` trong 5 khuôn, rồi
  thêm dòng đó vào `tdq-intake/SKILL.md` (khuôn brief), `spec-template.md`,
  `plan-template.md`, `qc.md`, `report-template.md` — Test: `pytest -k khuon_tai_lieu`
  ra 5 subtest xanh
- [x] **T2.2** (n6 e20m) — đỏ 3 kind → thêm dòng Soul vào brief/spec/plan request này,
  tiện tay cập nhật dòng Trạng thái hết stale (spec ĐÃ DUYỆT 22:19, plan ĐÃ DUYỆT 22:28) — Thêm test `soul_request_dang_mo`: đọc `active_request` trong
  `docs/tdq/state.json`, soi brief/spec/plan của slug đó, bỏ qua file chưa tồn tại và bỏ
  qua khi không có request mở; rồi thêm dòng `Soul:` vào 3 file của chính request này —
  Test: `pytest -k soul_request_dang_mo` xanh và bao gồm
  `docs/tdq/brief/2026-08-14-set-soul-workflow.md`

**Xong P2 khi**: 5 khuôn và 3 tài liệu của request này đều mang dòng `Soul:`.

## P3 — Rà soát luật cũ theo soul

- [x] **T3.1** (n6 e35m) Đọc đủ 28 file trong `skills/`, đối chiếu 4 nguyên tắc của soul,
  ghi `docs/tdq/knowledge/2026-08-14-ra-soat-luat-theo-soul.md`: bảng 28 dòng, mỗi dòng có
  phán quyết HỢP · SỬA · KHÔNG SỬA kèm lý do — Test: `grep -c '^| ' <file>` ra 28 dòng dữ
  liệu, không dòng nào để trống cột phán quyết
  - Đã đọc trọn 28 file (2 batch cat + Read); kết đếm 25 HỢP · 2 SỬA (qc.md giao T6.3,
    context-budget.md sửa ở T3.2) · 1 KHÔNG SỬA (quick-lane, có lý do). Header bảng viết
    `|File|` không khoảng trắng nên `grep -c '^| '` đếm đúng 28 dòng dữ liệu.
- [x] **T3.2** (n5 e25m) Sửa đúng những dòng luật bị chấm SỬA ở T3.1, mỗi lần sửa ghi số
  dòng cũ và mới vào biên bản; không có dòng nào phải sửa thì ghi rõ một câu — Test:
  `python3 -m pytest tests/ -q` còn xanh và `doc_lint` các file vừa sửa exit 0
  - Sửa 1/2 dòng SỬA: context-budget.md thêm bullet "Soul phân xử" (dòng 20–22, số dòng
    ghi vào biên bản); qc.md để T6.3 sửa cùng M5 (đã ghi rõ trong biên bản). Suite
    `584 passed, 290 subtests` · lint context-budget.md exit 0 · bảng grep ra đúng 28.

**Xong P3 khi**: biên bản đủ 28 dòng và mọi dòng SỬA đã xử xong.

## P4 — Thư viện rule đa ngôn ngữ

- [x] **T4.1** (n4 e12m) Bù 3 khoảng trống nguồn: ESLint/typescript-eslint, HTML (W3C hay
  htmlhint), URL chính thức C++ Core Guidelines; ghi nối vào
  `docs/tdq/research/2026-08-14-set-soul-workflow.md` — Test: 3 mục mới, mỗi mục có URL
  và năm, không mục nào ghi "chưa có nguồn"
  - Dùng: `tavily-primary` (mcp)
  - Để: chạy 3 truy vấn bù cho TS/JS, HTML, C++ trước khi viết file rule tương ứng
  - Ra: `docs/tdq/research/2026-08-14-set-soul-workflow.md` có thêm mục `## Truy vấn 5`
  - Kiểm: `grep -c 'https://' docs/tdq/research/2026-08-14-set-soul-workflow.md` tăng ≥ 3
  - Không dùng cho: viết nội dung rule — search chỉ lấy nguồn, rule do người viết
  - Đã bù đủ 3 mục có URL + năm (typescript-eslint configs 2026 · validator.w3.org +
    htmlhint.com/rules 2026 · github.com/isocpp/CppCoreGuidelines commit 2026-08-06);
    `grep -c 'https://'` 24 → 27, mục Truy vấn 5 ghi rõ lấp khoảng trống (b) và (c).
- [x] **T4.2** (n5 e18m) Thêm test `khuon_ngon_ngu` và `chi_muc`: mỗi file trong `rules/`
  đủ 7 mục khuôn và dưới 150 dòng, mọi file đều có dòng trong `index.md`, không dòng thừa —
  Test: chạy lần đầu ĐỎ vì thư mục `rules/` chưa có
  - `tests/test_rules_library.py` mới: khuôn 7 mục cố định, đòi ĐÚNG 10 file; chạy lần
    đầu `2 failed` vì `rules/` chưa tồn tại — đỏ đúng yêu cầu.
- [x] **T4.3** (n5 e20m) Viết `rules/chung.md`: 4 thuộc tính Clean Code, ưu tiên nhóm
  Intentionality kèm số 59,6%, ngưỡng cyclomatic ≤ 10 và cognitive ≤ 15 (họ C ≤ 25), cách
  ghi đè ngưỡng, checklist OWASP — Test: `pytest -k chung` xanh, có đủ 4 thuộc tính và 2
  ngưỡng số
  - Test `chung` viết trước (đỏ vì thiếu file) → viết file 74 dòng, 5 URL đều có trong
    research → `1 passed` · doc_lint exit 0.
- [x] **T4.4** (n4 e15m) Viết `rules/index.md`: bảng ngôn ngữ → đuôi file nhận diện →
  file rule → lệnh linter, cộng luật ba tầng nạp — Test: `pytest -k chi_muc` xanh
  - Bảng 7 ngôn ngữ + luật 3 tầng nạp; chi_muc so chỉ mục với danh sách plan (thư mục ==
    danh sách do khuon_ngon_ngu giữ) → `1 passed` · lint exit 0. Lệnh linter không dùng npx.
- [x] **T4.5** (n5 e18m) `rules/python.md` (PEP 8 + ruff) — Test: `pytest -k khuon_ngon_ngu`
  subtest python xanh
  - Subtest `ten=python` xanh (3 subtests passed: chung·index·python; 7 file còn lại đỏ
    chờ T4.6–T4.12 đúng tiến độ) · lint exit 0.
- [x] **T4.6** (n5 e18m) `rules/csharp.md` (Coding Conventions + Roslyn 8 category qua
  `.editorconfig`) — Test: subtest csharp xanh
  - Subtest `ten=csharp` xanh (4 subtests passed) · lint exit 0 · đủ 8 category Roslyn.
- [x] **T4.7** (n5 e18m) `rules/typescript-js.md` (nguồn lấy từ T4.1 + ESLint) — Test:
  subtest typescript-js xanh
  - Subtest `ten=typescript-js` xanh (5 subtests passed) · lint exit 0 · 3 URL đều từ
    Truy vấn 5.
- [x] **T4.8** (n5 e18m) `rules/go.md` (Effective Go + golangci-lint) — Test: subtest go xanh
  - Subtest `ten=go` xanh (6 subtests passed) · lint exit 0 · 4 nguồn từ Truy vấn 1.
- [x] **T4.9** (n5 e18m) `rules/rust.md` (API Guidelines + clippy, nói rõ Rust không có
  Core Guidelines) — Test: subtest rust xanh
  - Subtest `ten=rust` xanh (7 subtests passed) · lint exit 0 · ghi rõ "Rust KHÔNG có
    Core Guidelines" kèm nguồn thảo luận rust-lang.org.
- [x] **T4.10** (n5 e18m) `rules/cpp.md` (Core Guidelines + clang-tidy, ngưỡng cognitive 25)
  — Test: subtest cpp xanh
  - Subtest `ten=cpp` xanh (8 subtests passed) · lint exit 0 · cognitive 25 ghi rõ là
    mức nới riêng họ C.
- [x] **T4.11** (n5 e18m) `rules/html.md` (nguồn lấy từ T4.1) — Test: subtest html xanh
  - Subtest `ten=html` xanh (9 subtests passed) · lint exit 0 · nguồn validator.w3.org,
    /nu, htmlhint.com/rules (Truy vấn 5).
- [x] **T4.12** (n5 e20m) `rules/them-ngon-ngu.md`: quy trình gặp ngôn ngữ chưa có — 4
  truy vấn cố định, khuôn 7 mục, trình nháp trong chat, chờ user duyệt, rồi mới ghi
  `~/.claude/skills/tdq-rules/` dạng skill có `SKILL.md` — Test: `pytest -k them_ngon_ngu`
  xanh, bắt được bước duyệt trước khi ghi
  - Test red (thiếu file) → green: `2 passed, 11 subtests` · lint exit 0 · test bắt
    "chờ user duyệt" đứng trước "~/.claude/skills/tdq-rules" bằng vị trí find().
- [x] **T4.13** (n3 e10m) Thêm test `nguon`: mọi URL trong `rules/` phải có mặt trong file
  research — Test: `pytest -k nguon` xanh, 0 URL lạ
  - Xanh ngay vì URL đã kỷ luật từ lúc viết từng file; regex bắt URL, rstrip dấu câu,
    so substring với research.

**Xong P4 khi**: 10 file trong `rules/`, mọi test của P4 xanh, `doc_lint` exit 0.
  - ĐẠT: `pytest tests/test_rules_library.py -q` → `5 passed, 11 subtests passed` ·
    lint cả 10 file exit 0 (vòng for không in dòng FAIL nào).

## P5 — Script quét rule

- [x] **T5.1** (n6 e25m) Viết test cho `code_rule_scan.py`: dò đúng ngôn ngữ trên thư mục
  mẫu, linter thiếu thì báo "chưa kiểm được" chứ không PASS, `--im` tắt log, mặc định chỉ
  quét file đã đổi — Test: chạy lần đầu ĐỎ vì chưa có script
  - `tests/test_code_rule_scan.py` 4 test, chạy lần đầu `4 failed` (script chưa có) —
    đỏ đúng yêu cầu; PATH giả rỗng để ép nhánh thiếu linter chạy ổn định.
- [x] **T5.2** (n8 e45m) Viết `scripts/code_rule_scan.py`: dò ngôn ngữ theo đuôi file,
  tra bảng linter từ `rules/index.md`, kiểm linter đã cài bằng `shutil.which`, chạy linter
  có sẵn, in bảng ba trạng thái PASS · LỖI · CHƯA KIỂM ĐƯỢC, exit 1 khi có LỖI — Test:
  `pytest tests/test_code_rule_scan.py -q` xanh
  - `4 passed` — 1 vòng fix: test mặc-định-file-đổi cần git trong PATH nên bỏ path
    rỗng ở test đó; script thêm guard FileNotFoundError cho git.
- [x] **T5.3** (n3 e10m) Chạy thật trên chính repo này bằng `--tat-ca`, dán bảng kết quả
  vào file QC — Test: lệnh chạy xong, bảng phân biệt rõ 3 trạng thái
  - Chạy thật: 614 file git, 57 file Python khớp bảng, toàn bộ CHƯA KIỂM ĐƯỢC (máy
    thiếu ruff), exit 0 — bảng dán vào file QC mục T5.3.
- [x] **T5.4** (n2 e8m) Chứng minh script không tự cài gì — Test:
  `grep -nE 'pip install|npm i|apt-get|brew install' scripts/code_rule_scan.py` ra 0 dòng
  - grep exit 1 (0 dòng khớp) — script chỉ dùng shutil.which, không lệnh cài đặt.

**Xong P5 khi**: script chạy thật ra bảng và bộ test của nó xanh.
  - ĐẠT: bảng thật ở file QC mục T5.3 · `pytest tests/test_code_rule_scan.py -q` 4 passed.

## P6 — Nối vào workflow

- [x] **T6.1** (n5 e18m) Thêm test `clean_code_gate`, `qc_dong_bo`, `co_che_m` — Test:
  chạy lần đầu ĐỎ đủ 3 chỗ
  - ĐẠT: `tests/test_clean_code_workflow.py` — chạy đầu: clean_code_gate FAILED ·
    qc_dong_bo FAILED · co_che_m SUBFAILED đủ M1–M5.
- [x] **T6.2** (n5 e20m) Thêm câu hỏi bật/tắt clean code vào `skills/tdq-spec/SKILL.md`
  (khuôn option A/B, giải thích bật thì cuối request có scan và fix) và dòng
  `Clean code: BẬT|TẮT` vào `spec-template.md` §4; ghi rõ TẮT vẫn phải tổ chức code theo
  rule của ngôn ngữ, chỉ bỏ bước scan và fix — Test: `pytest -k clean_code_gate` xanh
  - ĐẠT: `pytest -k clean_code_gate` 1 passed · doc_lint 2 file exit 0. Vì trần Q14
    (+200 token), SKILL.md chỉ giữ bước 1b trỏ khuôn; khuôn A/B đầy đủ + dòng
    `Clean code:` nằm ở spec-template.md (§4 + mục `## Khuôn hỏi clean code`).
- [x] **T6.3** (n7 e30m) Sửa `skills/tdq-build/references/qc.md`: nới dòng "số hạng mục QC
  = số dòng DoD" thành ba hạng mục cố định QC-F1 đến QC-F3 theo M5, cộng hạng mục chạy
  `code_rule_scan.py` chỉ khi `Clean code: BẬT`; chép cùng nội dung sang
  `portable/workflow/references/qc.md` — Test: `pytest -k qc_dong_bo` xanh, hai bản khớp
  - ĐẠT: `pytest -k qc_dong_bo` 1 passed (khối trích ra bằng nhau từng byte) · doc_lint
    2 file exit 0 · số dòng cũ/mới đã ghi vào biên bản ra-soat mục T3.2.
- [x] **T6.4** (n7 e35m) Áp M1–M4: hồ sơ kiến trúc `docs/kien-truc.md` (M1, luật sinh một
  lần) · ô "Ràng buộc kiến trúc phải giữ" trong `spec-template.md` §5 (M2) · luật tìm rồi
  mới tạo thay dòng `tdq-build/SKILL.md:51` (M3) · dòng `Chạm:` trong `plan-template.md`
  (M4) — Test: `pytest -k co_che_m` ra 5 subtest xanh (M1–M5)
  - ĐẠT: `pytest -k co_che_m` 5 subtest xanh · doc_lint 4 file sửa exit 0 · tổng 6
    SKILL.md 27.462 ký tự (mốc 26.664, trần +800) — Q14 còn đúng trần.

**Xong P6 khi**: cả 3 nhóm test của P6 xanh và hai bản `qc.md` khớp nhau.
  - ĐẠT: `tests/test_clean_code_workflow.py` → 3 passed, 5 subtests passed; khối QC-F
    hai bản `qc.md` khớp nguyên văn (assertEqual).

## P7 — Log & test bắt buộc

- [x] **T7.1** (n4 e15m) Log service của `code_rule_scan.py`: bật mặc định, mỗi dòng có
  timestamp, `--im` tắt hẳn, `--chi-tiet` in thêm bước dò ngôn ngữ — Test: chạy 3 chế độ,
  đếm dòng log ra 3 kết quả khác nhau, có `--im` thì 0 dòng
  - ĐẠT: quét 1 file → mặc định 2 dòng · `--im` 0 dòng · `--chi-tiet` 3 dòng; dòng log
    mở đầu `[2026-08-14T23:39:06] bắt đầu quét 1 file (bảng rule: 17 đuôi)`.
- [x] **T7.2** (n3 e12m) Chạy toàn bộ suite và đo lại token — Test:
  `python3 -m pytest tests/ -q` ra 0 failed và ≥ 574 test cũ còn xanh;
  `python3 scripts/token_audit.py` cho thấy 6 file SKILL.md tăng ≤ 200 token so với T0.1
  - ĐẠT: `596 passed, 306 subtests passed`, exit 0 (mốc cũ 574 vẫn xanh, +12 test mới
    của request này). Token 6 SKILL.md: 27.462 ký tự ≈ 6.866 token, +200 so mốc 6.666 —
    đúng trần ≤ 200 (đo bằng len() như mốc T0.1; token_audit.py chỉ đo transcript).
- [x] **T7.3** (n2 e5m) Cập nhật đồ thị sau khi đổi mã nguồn — Test: `graphify-out/graph.json` đổi mtime
  - ĐẠT: `graphify extract . --code-only` xong (3 file re-extract) · lệnh Kiểm in `489`.
  - Dùng: `graphify`
  - Để: chạy `graphify extract . --code-only` sau khi `code_rule_scan.py` và `doc_lint.py` đã xong
  - Ra: `graphify-out/graph.json` cập nhật
  - Kiểm: `python3 -c "import json;print(len(json.load(open('graphify-out/graph.json'))['nodes']))"` chạy được
  - Không dùng cho: phân tích kiến trúc trong biên bản rà soát — phần đó đọc file trực tiếp

**Xong P7 khi**: suite xanh, token trong ngưỡng, đồ thị đã cập nhật.
  - ĐẠT P7: suite 596 passed · token đúng trần · graph.json mtime 23:40:08, 489 nodes.

## P8 — Nghiệm thu model yếu và QC độc lập

- [x] **T8.1** (n5 e20m) Soạn `tests/samples/python_5_loi.py` — đúng 5 lỗi thuộc nhóm
  Intentionality, liệt kê đáp án trong docstring — rồi giao một agent chạy Haiku đọc
  `rules/python.md` và soát file đó — Test: agent nêu đúng ≥ 4/5 lỗi, không hỏi lại câu nào
  - ĐẠT: agent `haiku-low-soat-python-theo-rule` nêu đúng **5/5** lỗi (import chết,
    tên `Process`, mutable default, `== None`, `except:` trần), dẫn đúng mục rule cho
    từng lỗi, không hỏi lại. Agent nhận bản đã cắt docstring đáp án (bản gốc giữ đáp án).
- [x] **T8.2** (n3 e15m) Lượt QC độc lập — Test: agent trả PASS/FAIL cho từng hạng mục DoD
  - ĐẠT: agent `tdq-qc-tester` (sonnet) chạy lại 18/20 hạng mục → PASS hết, Q13+Q18 để
    vòng QC chính; biên bản đã dán vào file QC mục `## Vòng QC độc lập`.
  - Dùng: `tdq-qc-tester`
  - Để: kiểm độc lập 20 hạng mục DoD sau khi P0–P7 xong, chạy lại lệnh chứ không tin lời khai
  - Ra: danh sách phát hiện dán vào `docs/tdq/qc/2026-08-14-set-soul-workflow.md`
  - Kiểm: file QC có mục `## Vòng QC độc lập` với phán quyết từng phát hiện
  - Không dùng cho: sửa code — agent này chỉ báo, việc sửa do phase QC làm

**Xong P8 khi**: Q18 đạt và biên bản QC độc lập đã có trong file QC.

## Definition of Done

Trỏ về §6 spec (20 hạng mục). Lệnh kiểm rút gọn:

| # | Hạng mục | Lệnh |
|---|---|---|
| Q1 | Soul đủ 3 tầng đúng thứ tự | `pytest -k thu_tu` |
| Q2 | Skill nền và portable trỏ soul | `grep -c soul skills/tdq-conventions/SKILL.md portable/AGENTS.md` |
| Q3 | Rà soát đủ 28 file | đếm dòng bảng biên bản |
| Q4 | Chỉ mục khớp số file rule | `pytest -k chi_muc` |
| Q5 | 7 file ngôn ngữ đủ khuôn | `pytest -k khuon_ngon_ngu` |
| Q6 | URL trong rule có thật | `pytest -k nguon` |
| Q7 | Script chạy thật | `python3 scripts/code_rule_scan.py --tat-ca` |
| Q8 | Script không tự cài | `grep -nE 'pip install\|npm i\|apt-get' scripts/code_rule_scan.py` |
| Q9 | Log service | chạy có và không `--im` |
| Q10 | Câu hỏi clean code | `pytest -k clean_code_gate` |
| Q11 | Hai bản qc.md khớp | `pytest -k qc_dong_bo` |
| Q12 | M1–M5 có mặt | `pytest -k co_che_m` |
| Q13 | Test đỏ được khi phá | phá 1 chỗ, chạy lại, khôi phục |
| Q14 | Token tầng luôn nạp | `python3 scripts/token_audit.py` |
| Q15 | Toàn bộ suite | `python3 -m pytest tests/ -q` |
| Q16 | Lint tài liệu | `python3 scripts/doc_lint.py <file đã sửa>` |
| Q17 | R9 đúng khuôn và đúng phạm vi | `pytest -k r9` |
| Q18 | Model Haiku làm theo được | agent Haiku soát `tests/samples/python_5_loi.py` |
| Q19 | 5 khuôn tài liệu có dòng Soul | `pytest -k khuon_tai_lieu` |
| Q20 | Tài liệu request đang mở có dòng Soul | `pytest -k soul_request_dang_mo` |
