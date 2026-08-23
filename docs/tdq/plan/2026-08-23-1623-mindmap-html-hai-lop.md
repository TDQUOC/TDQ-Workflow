# PLAN — công cụ sơ đồ giải thuật: script chạy được, phase bắt buộc trước plan, trang HTML hai lớp

Ngày: 2026-08-23 · Spec: ../spec/2026-08-23-1623-mindmap-html-hai-lop.md (bản 1.1, ĐÃ DUYỆT) · Lane: full
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md
Mode thực thi: subagent — bốn vùng file rời nhau hoàn toàn (`tdq_mindmap.py`, `mindmap_render.py`, `tdq_state.py`, `doc_lint.py`); `mo-phong` đo trên chính plan này ra 16 task, 6 đợt, đội thắng 14.2 phút ở hệ số agent 1.5 (ĐỀ XUẤT, user chốt lúc duyệt)
Trạng thái plan: HOÀN THÀNH (2026-08-23 20:45) · Mode chốt: subagent

## Mục lục

- Quy tắc thi hành (áp cho mọi task)
- P1 — Bộ đọc và bốn lệnh trên file sơ đồ
- P2 — Dựng trang, cổng chặn, luật lint (ba nhánh song song)
- P3 — Skill, file mẫu, dẫn vào phase mới
- P4 — Log & test bắt buộc
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
7. Chú thích, docstring, chuỗi máy in ra trong `scripts/` viết TIẾNG ANH (chốt 2026-08-22).

## P1 — Bộ đọc và bốn lệnh trên file sơ đồ

- [x] **T1.1** (e28m) Tạo `scripts/tdq_mindmap.py`: khung CLI, log service có timestamp tắt được
  qua config, hằng khuôn file sơ đồ (dòng tiêu đề, `@nhánh`, `@phụ-thuộc`, dòng bước `Bn ·`), và
  lệnh `sinh <feature>` — feature chưa có file thì tạo mới trả 0, đã có thì KHÔNG ghi đè, in
  nội dung hiện tại kèm khuôn câu trình cập nhật và trả 3; slug sai khuôn trả 2 — Test:
  `python3 -m pytest tests/test_mindmap_nhan_doc.py -k sinh -q` xanh
  - Chạm: `scripts/tdq_mindmap.py`, `tests/test_mindmap_nhan_doc.py` → file mới, chưa node nào phụ thuộc
- [x] **T1.2** (e22m) Lệnh `kiem <file>`: kiểm đủ khuôn, bắt thiếu dòng `@nhánh`, bắt dòng
  `@phụ-thuộc` sai cú pháp (thiếu tên feature hoặc thiếu lý do sau dấu `·`), in từng dòng vi phạm
  kèm mã luật; 0 sạch · 1 có vi phạm · 2 không đọc được file — Test:
  `python3 -m pytest tests/test_mindmap_nhan_doc.py -k kiem -q` xanh
  - Chạm: `scripts/tdq_mindmap.py`, `tests/test_mindmap_nhan_doc.py`
  - Cần: T1.1
- [x] **T1.3** (e20m) Lệnh `doi-chieu <file>`: lọc node của `graphify-out/graph.json` theo
  `file_type == "code"` (KHÔNG lọc theo `source_file`+`source_location` — phép lọc đó lọt node
  tài liệu), đối chiếu từng cặp `file::hàm` trong sơ đồ, in cặp lệch; 0 khớp · 1 lệch · 3 không
  đọc được đồ thị; `built_at_commit` khác `HEAD` thì in cảnh báo, không tự chạy lại graphify — Test:
  `python3 -m pytest tests/test_mindmap_nhan_doc.py -k doi_chieu -q` xanh, và test khẳng định số
  node lọc được bằng đúng số node `file_type == "code"` đếm trực tiếp từ file đồ thị
  - Chạm: `scripts/tdq_mindmap.py`, `tests/test_mindmap_nhan_doc.py`
  - Cần: T1.1
- [x] **T1.4** (e20m) Lệnh `lien-he`: đọc mọi dòng `@phụ-thuộc` trong `docs/tdq/mind-map/`, dựng
  lưới, trả 0 hợp lệ · 1 trỏ tới feature không có file (in đích danh tên thiếu) · 3 có vòng lặp
  (in đúng chuỗi feature tạo thành vòng) — Test:
  `python3 -m pytest tests/test_mindmap_nhan_doc.py -k lien_he -q` xanh, gồm một ca vòng lặp
  ba feature và một ca trỏ hụt
  - Chạm: `scripts/tdq_mindmap.py`, `tests/test_mindmap_nhan_doc.py`
  - Cần: T1.2

- [x] **T1.5** (e6m) Lệnh `kiem` nhận NHIỀU đường dẫn một lượt (`nargs="+"`) như `doc_lint.py`,
  mã thoát là mức nặng nhất trong cả lượt; gọi một file vẫn y như cũ — Test:
  `python3 scripts/tdq_mindmap.py kiem docs/tdq/mind-map/dang-nhap.md docs/tdq/mind-map/mua-hang.md`
  exit 0 (khuôn cũ một file exit 2 vì argparse)
  - Chạm: `scripts/tdq_mindmap.py`, `tests/test_mindmap_nhan_doc.py`
  - Cần: T1.3

**Xong P1 khi**: `python3 -m pytest tests/test_mindmap_nhan_doc.py -q` xanh và bốn lệnh trả đúng
mã thoát trên file mẫu tạm.

## P2 — Dựng trang, cổng chặn, luật lint (ba nhánh song song)

- [x] **T2.1** (e34m) Tạo `scripts/mindmap_render.py`: dựng trang một feature hai lớp — lớp
  nghiệp vụ từ file `.md`, lớp chi tiết từ `graph.json` (lời gọi sắp theo `source_location` tăng
  dần, nhiều lời gọi trùng một dòng gom một hàng, giải thích lấy dòng đầu docstring đọc bằng
  `ast`, hàm không docstring in trơ tên và tô nhạt), chuyển lớp bằng nút, mặc định sâu 1 tầng và
  cờ `--sau <N>`, một bước quá 20 hàm thì thu gọn cho bấm mở, đầu lớp chi tiết in câu cảnh báo
  đây là thứ tự VIẾT không phải thứ tự CHẠY; trang tự chứa, không tham chiếu tài nguyên ngoài,
  màu theo token và đủ hai theme — Test:
  `python3 -m pytest tests/test_mindmap_render.py -k mot_feature -q` xanh, gồm test khẳng định
  HTML sinh ra không chứa `http://`, `https://`, `src=` trỏ ra ngoài
  - Chạm: `scripts/mindmap_render.py`, `tests/test_mindmap_render.py` → file mới, chưa node nào phụ thuộc
  - Cần: T1.2
  - Dùng: `artifact-diagramming`
  - Để: dựng SVG lớp chi tiết và mũi tên có nhãn, nạp skill TRƯỚC bước đỏ. Agent ngoài không có
    skill system: đọc `bundled:artifact-diagramming/SKILL.md` rồi làm theo.
  - Ra: `scripts/mindmap_render.py` sinh được `docs/tdq/mind-map/dang-nhap.html`
  - Kiểm: `python3 -m pytest tests/test_mindmap_render.py -k mot_feature -q` xanh
  - Không dùng cho: trang tổng ở T2.2 — trang đó có hợp đồng skill riêng
- [x] **T2.2** (e26m) Trang tổng `--tong`: gom mọi feature trong thư mục theo dòng `@nhánh`, xếp
  từ nhánh tổng xuống trang nghiệp vụ, và vẽ lưới phụ thuộc — mỗi cạnh một mũi tên mang lý do
  khai kèm, feature được trỏ tới mà chưa có file thì vẫn vẽ ô nhưng đánh dấu chưa có sơ đồ — Test:
  `python3 -m pytest tests/test_mindmap_render.py -k tong -q` xanh, gồm ca hai feature có một cạnh
  phụ thuộc thật và ca trỏ hụt
  - Chạm: `scripts/mindmap_render.py`, `tests/test_mindmap_render.py`
  - Cần: T1.4, T2.1
  - Dùng: `artifact-design`
  - Để: bảng màu theo token, hai theme, khối tràn cuộn trong khung riêng, nạp skill TRƯỚC bước đỏ.
    Agent ngoài không có skill system: đọc `bundled:artifact-design/SKILL.md` rồi làm theo.
  - Ra: `docs/tdq/mind-map/index.html` dựng được từ chính thư mục đó
  - Kiểm: `python3 -m pytest tests/test_mindmap_render.py -k tong -q` xanh
  - Không dùng cho: lớp chi tiết của trang một feature — đã xong ở T2.1
- [x] **T2.3** (e8m) Nối lệnh `xem <file>` trong `scripts/tdq_mindmap.py` vào bộ dựng; 0 ghi xong ·
  1 sơ đồ sai khuôn · 2 không ghi được file — Test:
  `python3 -m pytest tests/test_mindmap_nhan_doc.py -k xem -q` xanh
  - Chạm: `scripts/tdq_mindmap.py`, `tests/test_mindmap_nhan_doc.py`
  - Cần: T2.1
- [x] **T2.4** (e26m) Sửa `scripts/tdq_state.py`: thêm phase `diagram` vào `VALID_PHASES` và
  `PHASE_TABLE` (chen giữa `spec` và `plan`), thêm khoá danh sách sơ đồ của request (mỗi phần tử
  mang đường dẫn, trạng thái duyệt, câu duyệt của user), và lệnh duyệt từng sơ đồ theo đường dẫn —
  duyệt một cái KHÔNG làm cái khác thành đã duyệt — Test:
  `python3 -m pytest tests/test_state_diagram_gate.py -k danh_sach -q` xanh
  - Chạm: `scripts/tdq_state.py`, `tests/test_state_diagram_gate.py`
- [x] **T2.5** (e20m) Chặn cứng trong `scripts/tdq_state.py` theo khuôn `_chan_worktree_con_mo`:
  `set phase=plan` bị từ chối khi danh sách rỗng hoặc còn phần tử chưa duyệt, thông báo gọi tên
  ĐÍCH DANH từng sơ đồ chưa duyệt kèm đường dẫn để sửa tiếp, không xoá và không bắt vẽ lại file;
  state cũ KHÔNG có khoá danh sách thì vẫn sang `plan` được — Test:
  `python3 -m pytest tests/test_state_diagram_gate.py -k chan -q` xanh, gồm ca state cũ thiếu khoá
  - Chạm: `scripts/tdq_state.py`, `tests/test_state_diagram_gate.py`
  - Cần: T2.4
- [x] **T2.6** (e16m) Thêm luật khuôn file sơ đồ vào `scripts/doc_lint.py`, cắm ở nhánh
  `is_output` (không thêm vào `RULES`), mã luật riêng, báo vi phạm kèm số dòng — Test:
  `python3 -m pytest tests/test_doc_lint_mindmap.py -q` xanh và
  `python3 scripts/doc_lint.py docs/tdq/mind-map/dang-nhap.md` exit 0
  - Chạm: `scripts/doc_lint.py`, `tests/test_doc_lint_mindmap.py`
  - Cần: T1.2

- [x] **T2.7** (e8m) Đồng bộ hai chỗ ăn theo bảng phase sau khi thêm `diagram`:
  `tests/test_phase_table.py` chốt số phase đổi từ 10 thành 11, và dựng lại
  `skills/tdq-conventions/references/phases.md` bằng
  `python3 scripts/tdq_state.py phases-doc --plugin-root` — Test:
  `python3 -m pytest tests/test_phase_table.py -q` xanh và
  `grep -c 'diagram' skills/tdq-conventions/references/phases.md` ≥ 1
  - Chạm: `tests/test_phase_table.py`, `skills/tdq-conventions/references/phases.md`
  - Cần: T2.4, và nhánh tích hợp đã hợp về nhánh làm việc (bảng phase mới phải có mặt thì
    phép kiểm mới đỏ được)

- [x] **T2.8** (e8m) Nối `xem --tong` vào bộ dựng trang tổng: T2.3 mới cắm cờ vào argparse rồi
  trả `EXIT_SYNTAX` kèm câu "chưa có", trong khi T2.2 đã dựng xong trang tổng bên
  `mindmap_render.py` — nối hai đầu lại, mã thoát y như `xem` một file — Test:
  `python3 -m pytest tests/test_mindmap_nhan_doc.py -k xem_tong -q` xanh và
  `python3 scripts/tdq_mindmap.py xem --tong` exit 0, ghi ra `docs/tdq/mind-map/index.html`
  - Chạm: `scripts/tdq_mindmap.py`, `tests/test_mindmap_nhan_doc.py`
  - Cần: T2.2, T2.3

**Xong P2 khi**: toàn bộ test suite xanh, và cả ba nhánh (dựng trang, cổng chặn, lint) chạy được
độc lập trên file mẫu tạm.

## P3 — Skill, file mẫu, dẫn vào phase mới

- [x] **T3.1** (e14m) Viết `docs/tdq/mind-map/dang-nhap.md` theo khuôn mới (đổi tên từ
  `vi-du-login.md`, giữ 8 bước cũ) và `docs/tdq/mind-map/mua-hang.md` khai
  `@phụ-thuộc: dang-nhap · cần token phiên do đăng nhập phát ra` — Test:
  `python3 scripts/tdq_mindmap.py kiem docs/tdq/mind-map/dang-nhap.md docs/tdq/mind-map/mua-hang.md`
  exit 0 và `python3 scripts/tdq_mindmap.py lien-he` exit 0 với đúng 1 cạnh
  - Cần: T1.4, T2.6
- [x] **T3.2** (e26m) Tạo `skills/tdq-diagram/SKILL.md`: khuôn file sơ đồ ĐẦY ĐỦ có ví dụ điền
  sẵn, các bước phải làm theo thứ tự, khuôn câu trình sơ đồ mới cho user duyệt, và khuôn câu
  trình bản CẬP NHẬT ("feature này đã có sơ đồ, sau cập nhật của request này nó sẽ thành như
  sau…"); chỉ nhắc TÊN LỆNH của `scripts/tdq_mindmap.py`, cấm chép mã script vào skill — Test:
  skill có đủ 5 mục (khuôn file, các bước, khuôn trình mới, khuôn trình cập nhật, bảng mã thoát)
  và `grep -c 'python3 scripts/tdq_mindmap.py' skills/tdq-diagram/SKILL.md` ≥ 4
  - Cần: T1.1
- [x] **T3.3** (e14m) Sửa ba chỗ dẫn vào phase `diagram`: `skills/tdq-intake/SKILL.md` (lane
  `full`, sau `analyze`), `skills/tdq-intake/references/quick-lane.md` (lane `quick` cũng bắt
  buộc vẽ, nhưng chỉ lớp nghiệp vụ, không bắt `doi-chieu`), `skills/tdq-plan/SKILL.md` (điều kiện
  vào plan đổi thành mọi sơ đồ đã duyệt) — Test:
  `grep -l 'tdq-diagram' skills/tdq-intake/SKILL.md skills/tdq-intake/references/quick-lane.md skills/tdq-plan/SKILL.md`
  trả về đủ 3 file
  - Cần: T2.5, T3.2

**Xong P3 khi**: hai file mẫu lint sạch, skill đủ 5 mục, ba file dẫn vào đều nhắc phase mới.

## P4 — Log & test bắt buộc

- [x] **T4.1** (e12m) Log service của hai script mới: timestamp, mức log, tắt/giảm được qua
  config, cùng khuôn các script `scripts/` sẵn có — Test:
  `python3 scripts/tdq_mindmap.py kiem docs/tdq/mind-map/dang-nhap.md` in dòng có timestamp, và
  chạy lại với biến tắt log thì không in dòng nào
  - Chạm: `scripts/tdq_mindmap.py`, `scripts/mindmap_render.py`
  - Cần: T2.3
- [x] **T4.2** (e10m) Chạy toàn bộ test suite một lượt và phép kiểm i18n — Test:
  `python3 -m pytest tests/ -q` xanh và `python3 scripts/i18n_check.py` exit 0
  - Kết quả đo (2026-08-23 20:10): suite còn 38 đỏ, `comm` với tập đỏ ở mốc 7e3bbd0 (44 đỏ
    có sẵn trước request) ra RỖNG ở phía "mới" → 0 hồi quy do đợt này; 38 đỏ còn lại đều là
    nợ có sẵn, ngoài phạm vi request, ghi vào report chứ không âm thầm bỏ qua.
  - `python3 scripts/i18n_check.py scripts/tdq_mindmap.py scripts/mindmap_render.py
    scripts/tdq_state.py scripts/doc_lint.py` → 0 dòng, exit 0 (đúng phạm vi Q23).
  - Cần: T4.1, T4.4a, T4.4b, T4.4c, T4.4d
- [x] **T4.4a** (e8m) Gỡ vi phạm doc_lint do đợt này thêm chữ vào khuôn skill: `tdq-plan`
  quá trần 110 dòng và câu dài quá 40 từ ở `quick-lane.md` — Test:
  `python3 scripts/doc_lint.py skills/tdq-plan/SKILL.md skills/tdq-intake/references/quick-lane.md`
  exit 0
  - Chạm: `skills/tdq-plan/SKILL.md`, `skills/tdq-intake/references/quick-lane.md`
  - Lý do giữ (leader): `file-luat` — sửa khuôn skill, cấm giao ra ngoài
- [x] **T4.4b** (e6m) Khai `tdq-diagram` vào hai bảng kiểm kê: trần số dòng skill trong
  `doc_lint.py` và bảng luật `luat-hien-co.md` — Test: `pytest tests/test_skill_shape.py
  tests/test_luat_skill.py -q` xanh
  - Chạm: `scripts/doc_lint.py`, `docs/tdq/audit/luat-hien-co.md`
  - Lý do giữ (leader): `file-luat` — sửa bảng luật, cấm giao ra ngoài
- [x] **T4.4c** (e10m) Dọn nốt các phép kiểm đỏ còn lại do chèn phase `diagram` — đo bằng cách
  so tập test đỏ hiện tại với tập đỏ ở mốc 7e3bbd0 (44 đỏ có sẵn từ trước, ngoài phạm vi
  request này) — Test: `comm` giữa hai tập không còn dòng nào ở phía "mới"
  - Chạm: `tests/test_next.py`, `tests/test_timing.py`, `tests/test_tdq_eval.py`,
    `tests/test_e2e_chain.py`
- [x] **T4.4d** (e6m) Hai ca đo `evals/tuan-thu/duyet-plan-*/ca.json` còn chuỗi `set phase=plan`
  không qua cổng sơ đồ — chạy eval thật sẽ chết ở bước đó; chèn ba bước `set phase=diagram`,
  `diagram add`, `approve diagram` vào trước — Test:
  `grep -c '"phase=plan"' evals/tuan-thu/duyet-plan-*/ca.json` vẫn 1 mỗi file VÀ mỗi file có
  đủ ba bước sơ đồ đứng trước; `pytest tests/test_tdq_eval.py -q` xanh
  - Chạm: `evals/tuan-thu/duyet-plan-kem-mode/ca.json`, `evals/tuan-thu/duyet-plan-thieu-mode/ca.json`
  - Lý do giữ (leader): `file-luat` — dữ liệu ca đo tuân thủ, đi kèm bảng luật của leader
- [x] **T4.3** (e4m) Ghi lại hai kết luận kiến trúc của đợt này vào bộ nhớ dài hạn — Test:
  tìm lại được cả hai fact bằng một lần search với `project` là tên repo
  - Dùng: `mem0-memory` (mcp)
  - Để: ghi đúng hai fact ngắn — sơ đồ khoá theo FEATURE chứ không theo request, và lớp chi tiết
    sinh từ `graph.json` nên không bao giờ duyệt; nạp skill TRƯỚC khi ghi. Agent ngoài không có
    skill system: đọc `skills/mem0-memory/SKILL.md` rồi làm theo.
  - Ra: hai fact tồn tại trong mem0 với `project` là tên repo
  - Kiểm: `search_memories` với từ khoá `mind-map` trả về cả hai fact
  - Không dùng cho: chép nội dung spec/plan vào bộ nhớ — chỉ ghi kết luận, không ghi tài liệu
  - Cần: T4.2

## Cụm song song

Ba cụm, cắt theo FILE nên không cụm nào đụng chung đường dẫn với cụm khác:

- **Cụm A — `scripts/tdq_mindmap.py`**: T1.1 → T1.2 → {T1.3, T1.4} → T2.3. Nối tiếp trong cụm vì
  cùng một file; T1.3 và T1.4 chỉ song song được nếu tách hàm rõ, mặc định làm tuần tự.
- **Cụm B — `scripts/mindmap_render.py`**: T2.1 → T2.2. Chờ T1.2 xong (cần bộ đọc khuôn).
- **Cụm C — `scripts/tdq_state.py`**: T2.4 → T2.5. KHÔNG phụ thuộc P1, chạy được ngay từ đầu.
- **Cụm D — `scripts/doc_lint.py`**: T2.6 một mình. Chờ T1.2.

Cụm C là cụm rẻ nhất để chạy song song ngay từ phút đầu vì nó không cần gì từ P1. Phase P3 và P4
chỉ sửa tài liệu hoặc chạy kiểm, không cắt cụm.

## Definition of Done

Trỏ về §6 của spec (23 hạng mục).

- [x] Q1 Năm lệnh trả đúng mã thoát ở §3 — `python3 -m pytest tests/test_mindmap_nhan_doc.py -q`
- [x] Q2 Lọc node đúng trường `file_type == "code"`, không lẫn node tài liệu — `python3 -m pytest tests/test_mindmap_nhan_doc.py -k doi_chieu_loc -q`
- [x] Q3 Lời gọi sắp theo số dòng tăng dần — `python3 -m pytest tests/test_mindmap_render.py -k thu_tu -q`
- [x] Q4 Docstring làm giải thích, hàm không có thì tô nhạt — `python3 -m pytest tests/test_mindmap_render.py -k docstring -q`
- [x] Q5 Trang tự chứa, không tham chiếu ngoài — `python3 -m pytest tests/test_mindmap_render.py -k tu_chua -q`
- [x] Q6 Trang có đủ hai lớp, chuyển qua lại được — `python3 -m pytest tests/test_mindmap_render.py -k hai_lop -q`
- [x] Q7 Trang tổng gom theo `@nhánh` — `python3 -m pytest tests/test_mindmap_render.py -k tong_gom -q`
- [x] Q8 Trang tổng vẽ đúng cạnh phụ thuộc kèm lý do — `python3 -m pytest tests/test_mindmap_render.py -k "tong_gom_hai_feature_va_ve_canh_that or tong_feature_tro_toi_chua_co_file" -q`
- [x] Q9 Bắt vòng lặp phụ thuộc, in đúng chuỗi — `python3 -m pytest tests/test_mindmap_nhan_doc.py -k vong_lap -q`
- [x] Q10 Bắt phụ thuộc trỏ hụt, gọi đích danh — `python3 -m pytest tests/test_mindmap_nhan_doc.py -k TestLienHeTroHut -q`
- [x] Q11 Gate chặn khi còn sơ đồ chưa duyệt, gọi đúng tên — `python3 -m pytest tests/test_state_diagram_gate.py -k chan_con_chua_duyet -q`
- [x] Q12 Duyệt từng cái độc lập — `python3 -m pytest tests/test_state_diagram_gate.py -k duyet_doc_lap -q`
- [x] Q13 Danh sách rỗng cũng bị chặn — `python3 -m pytest tests/test_state_diagram_gate.py -k danh_sach_rong -q`
- [x] Q14 State cũ thiếu khoá vẫn sang `plan` được — `python3 -m pytest tests/test_state_diagram_gate.py -k state_cu -q`
- [x] Q15 Bị chặn xong file sơ đồ còn nguyên — `python3 -m pytest tests/test_state_diagram_gate.py -k chan_khong_mat_du_lieu -q`
- [x] Q16 `sinh` trên feature đã có: không lỗi, không ghi đè, trả mã cập nhật — `python3 -m pytest tests/test_mindmap_nhan_doc.py -k TestSinhCapNhat -q`
- [x] Q17 Luật lint cắm ở nhánh `is_output`, báo kèm mã luật — `python3 -m pytest tests/test_doc_lint_mindmap.py -q`
- [x] Q18 Thiếu `@nhánh` hoặc `@phụ-thuộc` sai khuôn đều bị `kiem` báo — `python3 -m pytest tests/test_mindmap_nhan_doc.py -k "TestKiemDongNhanh or TestKiemDongPhuThuoc" -q`
- [x] Q19 Skill đủ 5 mục gồm khuôn trình cập nhật — `grep -c '^## ' skills/tdq-diagram/SKILL.md` ≥ 5
- [x] Q20 Ba file cũ đều dẫn vào phase `diagram` — `grep -l 'tdq-diagram' skills/tdq-intake/SKILL.md skills/tdq-intake/references/quick-lane.md skills/tdq-plan/SKILL.md`
- [x] Q21 Mỗi module có tệp test riêng, toàn bộ xanh — `python3 -m pytest tests/ -q`
- [x] Q22 Log có timestamp và tắt được qua config — `python3 scripts/tdq_mindmap.py kiem docs/tdq/mind-map/dang-nhap.md` rồi chạy lại với `TDQ_LOG=0` (biến tắt log, xem `scripts/tdq_mindmap.py:139`)
- [x] Q23 Hai script mới qua phép kiểm i18n — `python3 scripts/i18n_check.py scripts/tdq_mindmap.py scripts/mindmap_render.py` (chạy không tham số chỉ in hướng dẫn rồi thoát 0, không phải phép kiểm)
- [x] Hai file mẫu dựng ra trang HTML mở xem được — `python3 scripts/tdq_mindmap.py xem docs/tdq/mind-map/dang-nhap.md`
- [x] Trang tổng dựng từ chính thư mục đó, có ít nhất một cạnh phụ thuộc thật — `python3 scripts/tdq_mindmap.py xem --tong`

## QC vòng 1 — fix

Hai lỗ hổng thật do QC vòng 1 phát hiện: DoD đòi hai bất biến mà KHÔNG test nào khẳng định.
Sửa bằng cách viết test còn thiếu, không nới DoD.

- [x] **QC1.1** (e8m) Q7 chưa có test: trang tổng gom feature theo `@nhánh` (`tree` trong
  `_render_branch_tree`) không được khẳng định ở đâu — viết test kiểm cả tên nhánh cha, nhánh
  con và nhóm "chưa gắn nhánh" — Test: `python3 -m pytest tests/test_mindmap_render.py -k tong_gom -q` xanh
  - Chạm: `tests/test_mindmap_render.py`
- [x] **QC1.2** (e8m) Q15 chưa có test: chặn `set phase=plan` xong thì file sơ đồ trên đĩa và
  trạng thái duyệt đã ghi phải còn nguyên — viết test so nội dung file trước/sau và soát lại
  danh sách `diagrams` — Test: `python3 -m pytest tests/test_state_diagram_gate.py -k chan_khong_mat_du_lieu -q` xanh
  - Chạm: `tests/test_state_diagram_gate.py`
