# SPEC — Trang trí khối chat cuối trả lời user

<!-- doc-lint: allow R10 — spec viết trước khi có luật ranh giới module -->

Ngày: 2026-08-14 · Bản: 1.0 · Brief: ../brief/2026-08-14-trang-tri-khoi-chat.md · Lane: full
Trạng thái: CHỜ DUYỆT

## 1. Mục tiêu & phạm vi

- **Mục tiêu:** làm khối chat cuối turn tách bạch nhãn với nội dung và dễ đọc hơn, bằng
  cấu trúc trình bày render đúng trên cả ba mặt (terminal CLI, desktop app, IDE extension),
  rồi khoá kết quả bằng test để khuôn không trôi. Đo được bằng 10 hạng mục ở §6.

- **Trong phạm vi** (16 file, đúng đáp án 2A của user):
  - Khuôn gốc `skills/tdq-conventions/references/user-facing-block.md` — viết lại thành:
    bảng "thành phần nào dùng cấu trúc nào", 7 luật trang trí đánh số, whitelist ký hiệu,
    và một khối mẫu **trước/sau** để người đọc thấy tận mắt.
  - 8 file skill chứa khối mẫu: `tdq-spec/SKILL.md` · `tdq-plan/SKILL.md` ·
    `tdq-plan/references/mode-gate.md` · `tdq-intake/references/lane-decision.md` ·
    `tdq-intake/references/quick-lane.md` · `tdq-intake/references/interview.md` ·
    `tdq-build/references/report-template.md` · `tdq-status/SKILL.md`.
  - 3 file mã sinh chuỗi: `scripts/tdq_state.py` (2 chỗ) · `hooks/scripts/_common.py`
    (2 chỗ) · `hooks/scripts/stop_gate.py` (1 chỗ).
  - 3 file portable: `portable/workflow/02-spec.md` · `03-plan.md` ·
    `portable/workflow/references/user-facing-block.md`.
  - 1 file test: `tests/test_user_facing_block.py` — siết thành whitelist.

- **NGOÀI phạm vi:**
  - **Màu chữ** — research kết luận không có đường nào an toàn: markdown không có cú pháp
    màu; ANSI do model tự in không có nguồn xác nhận được render (bằng chứng gián tiếp
    #6635, #18728 nghiêng về bị strip/hiện literal); HTML inline chắc chắn hỏng ở terminal.
  - **Cỡ chữ** — không có cơ chế nào ngoài heading, mà terminal về vật lý chỉ một cỡ font
    (#26390: h2–h6 render giống hệt nhau, chỉ thành bold).
  - **Mặt E của vòng scope** ("chỉ cần chạy được, sửa mỗi file khuôn") — user không chọn.
  - Viết lại câu chữ của các khối (user chọn 3A: chỉ đổi trình bày).
  - Đổi luật duyệt, đổi số thành phần (vẫn 5), đổi số chỗ phải dùng khuôn (vẫn 7).
  - Ký tự vẽ khung `─ │ ├ └ ┌ ┬ ┐`, bảng markdown trong khối chat, `~~gạch ngang~~`,
    heading `#` trong khối chat, emoji.

## 1b. Lộ trình

| Bước/phase | Chạy? | Vì sao |
|---|---|---|
| Research web | ĐÃ XONG | 8 truy vấn, `docs/tdq/research/2026-08-14-trang-tri-khoi-chat.md` — ẩn số quyết định của request này |
| Interview | ĐÃ XONG | 2 vòng (scope + chi tiết), không còn câu hỏi làm đổi kết quả |
| Spec → plan → implement → QC → report | CÓ | khung bất biến; user chọn cả 4 mặt nên không cắt bước nào |
| QC độc lập bằng agent `tdq-qc-tester` | CÓ | phạm vi đụng `hooks/` và `scripts/` — hỏng thì vỡ cả workflow |
| Review sâu bằng `tdq-reviewer` | BỎ | tuỳ chọn, user chưa yêu cầu |
| Kiểm bằng mắt trên ba mặt | BỎ | user chọn 2A — chỉ dùng cấu trúc/ký tự đã có bằng chứng chạy thật, nên không cần user thao tác |
| Chia sub-agent | CHƯA QUYẾT | quyết ở cổng mode sau khi duyệt plan |

## 2. Đầu ra cụ thể

| # | Đầu ra | Đường dẫn/vị trí | Đo "xong" bằng |
|---|---|---|---|
| 1 | Khuôn gốc bản mới: bảng cấu trúc 5 thành phần + 7 luật đánh số + whitelist + khối mẫu trước/sau | `skills/tdq-conventions/references/user-facing-block.md` | `grep -c '^| ' ` bảng ≥ 5 dòng; `grep -cE '^[1-7]\.' ` = 7; có cả `### Trước` và `### Sau` |
| 2 | 8 file skill: khối mẫu viết lại theo 7 luật | 8 đường dẫn ở §1 | test mới `test_sample_blocks_follow_rules` xanh |
| 3 | 3 file mã: chuỗi sinh ra khớp khuôn mới, chuỗi máy bắt giữ nguyên từng byte | `scripts/tdq_state.py`, `hooks/scripts/_common.py`, `hooks/scripts/stop_gate.py` | `python3 -m pytest tests/test_context_hooks.py -q` xanh |
| 4 | 3 file portable đồng bộ với khuôn gốc | `portable/workflow/02-spec.md`, `03-plan.md`, `references/user-facing-block.md` | test mới `test_portable_matches_source` xanh |
| 5 | Test siết whitelist ký hiệu + cấm cấu trúc rủi ro | `tests/test_user_facing_block.py` | file có ≥ 3 hàm test mới; toàn suite xanh |

## 3. Cách tiếp cận & lý do

- **Chọn:** trang trí bằng đúng những cấu trúc markdown đã có nguồn xác nhận chạy ở
  terminal — mặt khắt khe nhất trong ba mặt — rồi để hai mặt còn lại hưởng theo.
  Bảy luật trang trí:
  1. Nhãn trường in đậm, **dấu hai chấm nằm trong cặp sao**: `**Mục tiêu:** nội dung`.
     Nhờ vậy chuỗi con `Mục tiêu:` không đổi, mọi phép grep cũ vẫn khớp.
  2. Nội dung có từ 2 mục trở lên → mỗi mục một dòng `- `; dưới 2 mục thì viết thẳng
     cùng dòng với nhãn.
  3. Đường dẫn file bọc dấu nháy ngược: ``Xem đầy đủ tại: `docs/...` ``. Giữ nguyên
     tiền tố `Xem đầy đủ tại: ` dạng chữ thường không trang trí.
  4. Trong phần nội dung, tên file / lệnh / con số bọc `inline code`.
  5. Đường kẻ `---` giữ nguyên, luôn có đúng một dòng trống ở trên và dưới.
  6. Danh sách lựa chọn giữ nguyên khuôn `- A (đề xuất): nội dung`; được in đậm nhãn ngắn
     bên trong phần nội dung, cấm đụng vào cụm `- A (đề xuất):`.
  7. Dòng `➤` cuối khối giữ nguyên từng byte, vẫn là dòng cuối tin nhắn.
- **Whitelist ký hiệu ngoài ASCII: đúng ba ký tự** `➤` (U+27A4) · `·` (U+00B7) ·
  `—` (U+2014). Test kiểm theo Unicode category: ký tự loại `P*`/`S*` ngoài ASCII mà không
  thuộc whitelist → đỏ. Chữ tiếng Việt là loại `L*` nên không bị đụng.
- **Vì:** ba mặt KHÔNG dùng chung một renderer (#58983 — cùng một VS Code extension có
  Terminal mode làm phẳng bảng và Native UI render đúng), nên mẫu số chung phải lấy theo
  terminal. Ở terminal, #26390 xác nhận **đậm / nghiêng / `inline code` / khối code /
  danh sách / blockquote 1 cấp** hoạt động tốt.
- **Đã loại — `▸`** (ký tự thứ tư user nêu ở đáp án 1A): luật 2A user chọn là "chỉ dùng
  thứ đã có bằng chứng chạy thật". `grep -c '▸' -r skills/ scripts/ hooks/ portable/` cho
  0 kết quả ở mọi file, tức `▸` chưa từng in ra lần nào → không có bằng chứng → loại.
  Ba ký tự còn lại đều đang chạy thật (`_common.py:181-183`, `tdq_state.py:586,690`).
- **Đã loại — heading `#` làm phân cấp cỡ chữ:** terminal render mọi cấp heading thành
  bold như nhau (#26390), dùng vào chỉ tốn dòng mà không thêm thông tin thị giác.
- **Đã loại — bảng markdown trong khối chat:** 5 issue lỗi (#45111 #14763 #22311 #13438
  #11274): sụp thành key-value khi rộng, lệch cột với tiếng Việt, mất dòng, biến mất khi
  resize. Bảng trong file tài liệu thì vẫn dùng bình thường — file không render ở chat.

## 3b. Năng lực & công cụ

| Skill | Nguồn | Phán quyết | Dùng ở đâu / Lý do loại |
|---|---|---|---|
| tdq-intake | plugin:tdq-workflow | NỀN | phase analyze đã chạy xong, brief là đầu vào của spec này |
| tdq-spec | plugin:tdq-workflow | NỀN | đang chạy — sinh chính file này |
| tdq-plan | plugin:tdq-workflow | NỀN | phase kế tiếp |
| tdq-build | plugin:tdq-workflow | NỀN | implement + QC + report |
| tdq-conventions | plugin:tdq-workflow | NỀN | chứa chính khuôn bị sửa |
| tdq-status | plugin:tdq-workflow | NỀN | là một trong 8 file skill bị sửa |
| tavily-search | plugin:tavily | DÙNG | đã dùng ở phase analyze cho 8 truy vấn research; không gọi lại trong build |
| claude-code-guide | built-in agent | DÙNG | nguồn nội bộ về hành vi render, đối chiếu với kết quả tavily ở phase analyze |
| Đã xét 271 skill khác | user/plugin/built-in | KHÔNG | khác lĩnh vực |

## 4. Yêu cầu bắt buộc

- **Log service:** ba file mã bị đụng đã có log sẵn (`_info()` ở `stop_gate.py`); request
  này chỉ sửa chuỗi hiển thị, KHÔNG thêm và KHÔNG bớt một dòng log nào, không tắt log nào.
- Không placeholder, không TODO stub, không mock trình bày như dữ liệu thật.
- Mỗi thay đổi có test riêng chạy được bằng một lệnh: khuôn gốc và 8 khối mẫu do
  `tests/test_user_facing_block.py` phủ, 3 file mã do `tests/test_context_hooks.py` phủ,
  3 file portable do hàm test mới phủ.
- Giữ nguyên 100% câu chữ nội dung (đáp án 3A): chỉ được thêm ký tự trang trí
  (`*`, `` ` ``, `- `), cấm sửa/xoá/thêm từ.

## 5. Ràng buộc & rủi ro

| Rủi ro | Ảnh hưởng | Cách giảm |
|---|---|---|
| Sửa `hooks/` làm vỡ gate đang chạy | Cả workflow đứng, không duyệt được | Chạy `pytest tests/ -q` full suite; QC có hạng mục riêng grep từng chuỗi máy bắt; thêm một lượt QC độc lập bằng `tdq-qc-tester` |
| Test whitelist quá chặt, đỏ oan vì ký tự hợp lệ có sẵn | Không build tiếp được | Trước khi viết test, quét toàn bộ ký tự `P*`/`S*` ngoài ASCII đang có trong phạm vi kiểm; ký tự nào đang dùng hợp lệ thì hoặc vào whitelist hoặc sửa file, quyết theo luật 2A |
| Whitelist chốt 3 ký tự, hụt so với 4 ký tự user nêu | User có thể muốn `▸` thật | Đã nêu rõ ở §3 và ở khối trình spec; user duyệt spec là chốt luôn việc loại `▸` |
| `portable/` không có test sẵn | Bản portable trôi khỏi khuôn gốc mà không ai biết | Đầu ra #5 gồm hàm test `test_portable_matches_source` so khớp bản portable với khuôn gốc |
| Cách đo "0 từ bị mất" đếm nhầm vì ký tự trang trí dính vào từ | QC báo sai | Chuẩn hoá trước khi diff: xoá `*`, `` ` ``, và tiền tố `- ` ở đầu dòng, rồi mới tách từ và sort |
| Không cần model, không cần cài đặt gói mới | — | Toàn bộ việc là sửa văn bản và chuỗi hằng bằng Python chuẩn |

## 6. QC & Definition of Done

| # | Hạng mục kiểm | Lệnh/cách kiểm | Điều kiện PASS |
|---|---|---|---|
| Q1 | Mặt A — khuôn có bảng cấu trúc cho đủ 5 thành phần | `grep -A9 'Thành phần' skills/tdq-conventions/references/user-facing-block.md \| grep -c '^| '` | ≥ 6 (1 dòng tiêu đề + 5 thành phần) |
| Q2 | Mặt A — có đủ 7 luật trang trí đánh số | `grep -cE '^[1-7]\. ' skills/tdq-conventions/references/user-facing-block.md` | = 7 |
| Q3 | Mặt A — có khối mẫu trước/sau | `grep -c '### Trước\|### Sau' <khuôn>` | = 2 |
| Q4 | Mặt B — khối mẫu không chứa cấu trúc rủi ro | `grep -nE '~~\|<span\|\x1b\[\|^#{1,6} \|[─│┌┬┐├└]' <khuôn> <8 file skill>` | 0 kết quả |
| Q5 | Mặt B + 3B — whitelist ký hiệu | `python3 -m pytest tests/test_user_facing_block.py -q` | xanh, và hàm `test_symbol_whitelist` tồn tại, chỉ cho qua `➤ · —` |
| Q6 | Mặt D — chuỗi máy bắt còn nguyên | `grep -c '· Góp ý: nhắn trực tiếp' hooks/scripts/_common.py` và `grep -c 'plan đề xuất {mode}' hooks/scripts/_common.py` | lần lượt ≥ 2 và = 1 |
| Q7 | Mặt D — toàn bộ test cũ không đỏ và không giảm số test | `python3 -m pytest tests/ -q` | 0 failed, số test ≥ 569 (mốc bản 0.16.0) |
| Q8 | Mặt C — 8 file skill + 3 file portable đều trỏ về khuôn gốc | `grep -lc 'user-facing-block' <11 file>` | đủ 11 file |
| Q9 | Mặt C — bản portable khớp khuôn gốc | `python3 -m pytest tests/test_user_facing_block.py -k portable -q` | xanh |
| Q10 | 3A — 0 từ nội dung bị mất | với mỗi file đã sửa: `diff <(git show HEAD:<f> \| sed 's/[*`]//g; s/^- //' \| tr -s '[:space:]' '\n' \| sort) <(sed 's/[*`]//g; s/^- //' <f> \| tr -s '[:space:]' '\n' \| sort) \| grep -c '^<'` | = 0 với mọi file |

**DoD:** 10 hạng mục trên đều PASS kèm lệnh và output thật trong `docs/tdq/qc/<slug>.md` ·
mọi task trong plan tick `[x]` · `pytest tests/ -q` 0 failed · `doc_lint.py --pair` exit 0 ·
một lượt QC độc lập bằng `tdq-qc-tester` đã chạy và các phát hiện của nó được xử lý từng cái
(sửa, hoặc ghi rõ vì sao không sửa) · report ghi ở `docs/tdq/reports/<slug>.md`.

## 7. Câu hỏi còn mở

(rỗng)
