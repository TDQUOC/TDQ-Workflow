# SPEC — bỏ pha sơ đồ mind map khỏi quy trình TDQ

Ngày: 2026-08-31 · Bản: 1.0 · Brief: ../brief/2026-08-31-1703-bo-pha-so-do-mind-map.md · Lane: full
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md
Trạng thái: CHỜ DUYỆT

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

- Mục tiêu: gỡ hẳn pha `diagram` và cổng duyệt sơ đồ khỏi quy trình TDQ, để lane `full`
  chạy `analyze → spec → plan → mode → implement → qc → report` và lane `nhanh` không còn
  bước vẽ sơ đồ; xoá luôn hai script sinh/dựng sơ đồ và skill `tdq-diagram`.
- Trong phạm vi:
  - `scripts/tdq_state.py`: gỡ pha `diagram` khỏi `VALID_PHASES`/`PHASE_ORDER`, gỡ target
    `diagram` khỏi `APPROVE_TARGETS`, gỡ `DIAGRAM_KEY` và toàn bộ hàm `_heal_diagrams`,
    `_diagram_id`, `diagram_entries`, `diagram_pending`, `_diagram_register`,
    `_cli_approve_diagram`, `_cli_diagram`, điều kiện vào pha `plan`, checklist pha
    `diagram`, dòng `| Diagrams |` của bảng trạng thái.
  - Xoá `scripts/tdq_mindmap.py`, `scripts/mindmap_render.py`, `skills/tdq-diagram/`.
  - `scripts/doc_lint.py`: gỡ import `tdq_mindmap` và nhánh `check_diagram`, gỡ ngân sách
    token `"tdq-diagram": 155`.
  - Skill/tài liệu luật: `tdq-conventions/references/phases.md`, `tdq-spec/SKILL.md`,
    `tdq-plan/SKILL.md`, `tdq-intake/SKILL.md`, `tdq-intake/references/quick-lane.md`.
  - Test: xoá 4 file test riêng của mind-map, sửa 5 file test còn nhắc pha `diagram`.
  - Sinh lại `portable_claude/` và `antigravity_portable/`, dọn file thừa còn sót.
  - Tương thích ngược cho state cũ và cho lệnh CLI đã gỡ.
  - `CHANGELOG.md` + bump version.
- NGOÀI phạm vi:
  - `docs/tdq/mind-map/` (16 file .md/.html/.json) — GIỮ NGUYÊN làm tư liệu lịch sử.
  - Docs lịch sử của các request cũ (brief/plan/qc/report) — GIỮ NGUYÊN, là biên bản đã chốt.
  - `scripts/canvas_a4_ch4_ch7.py`, `scripts/canvas_a4_rebuild.py`,
    `scripts/canvas_layout_apply.py`, `docs/diagrams/*.excalidraw` — tính năng tài liệu
    kiến trúc, không thuộc pipeline mind-map.
  - Không đổi bất kỳ cổng duyệt nào khác (spec, plan, quick, mode).

## 1b. Lộ trình

Chép từ brief mục `### Lộ trình`. User duyệt spec là duyệt luôn lộ trình này.

| Bước/phase | Chạy? | Vì sao |
|---|---|---|
| analyze | CÓ | đã xong, 8 câu hỏi đã chốt |
| Research web | BỎ | việc thuần nội bộ repo, không có ẩn số bên ngoài |
| Interview | CÓ | đã chạy 2 vòng, không còn câu hỏi mở |
| spec | CÓ | sửa bộ máy state và cổng chặn, bắt buộc có cổng duyệt |
| diagram | BỎ | user chốt miễn trừ — đây chính là pha đang bị gỡ |
| plan | CÓ | nhiều file, cần checklist task có test |
| mode | CÓ | hỏi main hay subagent sau khi duyệt plan |
| implement | CÓ | — |
| QC độc lập (agent) | CÓ | sửa chính bộ máy chặn quy trình, tự QC dễ mù điểm |
| report | CÓ | — |

## 2. Đầu ra cụ thể

| # | Đầu ra | Đường dẫn/vị trí | Đo "xong" bằng |
|---|---|---|---|
| 1 | Máy state không còn pha `diagram` | `scripts/tdq_state.py` | `set phase=diagram` bị từ chối; `set phase=plan` chỉ cần `spec_approved=true` |
| 2 | Lệnh CLI cũ báo lỗi có nghĩa | `scripts/tdq_state.py` | `approve diagram <path>` và `diagram add|list` in thông điệp nêu rõ pha đã gỡ, thoát khác 0 |
| 3 | State cũ còn key `diagrams` vẫn nạp được | `scripts/tdq_state.py` | nạp state có key `diagrams` không lỗi, key bị bỏ qua, `status` không in dòng Diagrams |
| 4 | Hai script sơ đồ và skill bị xoá | `scripts/tdq_mindmap.py`, `scripts/mindmap_render.py`, `skills/tdq-diagram/` | ba đường dẫn không còn tồn tại |
| 5 | Lint không còn phụ thuộc mind-map | `scripts/doc_lint.py` | không còn import `tdq_mindmap`; lint cả `docs/tdq/mind-map/` thoát 0 |
| 6 | Tài liệu luật hết pha diagram | `skills/tdq-conventions/references/phases.md`, `tdq-spec`, `tdq-plan`, `tdq-intake` + `quick-lane.md` | grep `diagram`/`mind-map` trong `skills/` trả 0 dòng |
| 7 | Bộ test sạch | `tests/` | 4 file test mind-map bị xoá, 5 file còn lại sửa xong, `pytest tests/ -q` không có lỗi mới so với mốc trước khi sửa |
| 8 | Bản portable đồng bộ | `portable_claude/`, `antigravity_portable/` | không còn file mind-map/tdq-diagram; kiểm tra toàn vẹn bundle thoát 0 |
| 9 | CHANGELOG + version | `CHANGELOG.md`, file khai version | có mục bản mới mô tả việc gỡ pha |

## 2b. Ranh giới module

| Module | Vùng file | Phụ thuộc module | Đầu ra §2 nào |
|---|---|---|---|
| state | `scripts/tdq_state.py` | không | 1, 2, 3 |
| công-cụ-sơ-đồ | `scripts/tdq_mindmap.py`, `scripts/mindmap_render.py`, `skills/tdq-diagram/` | không | 4 |
| lint | `scripts/doc_lint.py` | công-cụ-sơ-đồ | 5 |
| luật-skill | `skills/tdq-conventions/references/phases.md`, `skills/tdq-spec/SKILL.md`, `skills/tdq-plan/SKILL.md`, `skills/tdq-intake/SKILL.md`, `skills/tdq-intake/references/quick-lane.md` | state | 6 |
| test | `tests/` | state, lint, công-cụ-sơ-đồ | 7 |
| phát-hành | `portable_claude/`, `antigravity_portable/`, `CHANGELOG.md` | mọi module trên | 8, 9 |

## 3. Cách tiếp cận & lý do

- Chọn: xoá thẳng, không để cờ bật/tắt. Gỡ pha khỏi `PHASE_ORDER`/`VALID_PHASES` trước,
  rồi lần theo lỗi test đỏ để dọn hết nhánh chết; hai lệnh CLI cũ giữ lại đúng một nhánh
  chặn in thông điệp "pha diagram đã gỡ khỏi quy trình" thay vì biến mất im lặng.
- Vì: user chốt "xoá sạch"; một cờ tuỳ chọn giữ lại 2250 dòng code và 2500 dòng test cho
  đường đi không ai chạy, trái nguyên tắc soul (chất lượng > context cost). Giữ thông điệp
  lỗi có nghĩa vì phiên cũ và bản portable cũ vẫn có thể gọi lệnh cũ.
- Đã loại:
  - Chuyển pha thành tuỳ chọn mặc định tắt — vì vẫn phải nuôi toàn bộ code và test.
  - Xoá luôn `docs/tdq/mind-map/` — user chốt giữ làm tư liệu lịch sử.
  - Sửa docs lịch sử cho nhất quán — biên bản đã chốt, sửa là làm sai lịch sử.

## 3b. Năng lực & công cụ

| Skill | Nguồn | Phán quyết | Dùng ở đâu / Lý do loại |
|---|---|---|---|
| tdq-intake | plugin:tdq-workflow | NỀN | skill khung đang chạy |
| tdq-spec | plugin:tdq-workflow | NỀN | skill khung viết spec này |
| tdq-plan | plugin:tdq-workflow | DÙNG | viết plan sau khi duyệt spec |
| tdq-build | plugin:tdq-workflow | DÙNG | chạy plan ở pha implement |
| tdq-conventions | plugin:tdq-workflow | DÙNG | `references/phases.md` là đầu ra 6 |
| tdq-lsp-setup | plugin:tdq-workflow | DÙNG | thứ tự tìm kiếm LSP+lumen, đã kiểm 6/6 bậc |
| tdq-status | plugin:tdq-workflow | DÙNG | soát bảng trạng thái sau khi gỡ dòng Diagrams |
| tdq-check-status | plugin:tdq-workflow | DÙNG | kiểm state cũ còn key `diagrams` nạp được |
| tdq-diagram | plugin:tdq-workflow | KHÔNG | user đã cấm — là đối tượng bị xoá của chính việc này |
| graphify | project | DÙNG | chạy lại cuối mỗi turn có đổi code |
| superpowers:test-driven-development | plugin | DÙNG | mọi task viết test đỏ trước |
| Đã xét 214 skill khác | user/plugin/built-in | KHÔNG | khác lĩnh vực |

## 4. Yêu cầu bắt buộc

- Log service bật mặc định: timestamp, đủ chi tiết debug, tắt/giảm được qua config —
  giữ nguyên cơ chế log sẵn có của `tdq_state.py` và `doc_lint.py`, không thêm không bớt.
- Không placeholder, không TODO stub, không mock trình bày như dữ liệu thật.
- Mỗi thành phần có unit test riêng, chạy được bằng một lệnh.
- Code viết ra bám 5 nguyên tắc SOLID theo
  `skills/tdq-conventions/references/clean-code.md`, và bám rule ngôn ngữ trong
  `skills/tdq-build/references/rules/`.

## 5. Ràng buộc & rủi ro

Ràng buộc kiến trúc phải giữ (chép từ `docs/kien-truc.md`):

- `Chỉ scripts/tdq_state.py được ghi docs/tdq/state.json; mọi nơi khác chỉ đọc qua CLI.` —
  việc này chạm ở `scripts/tdq_state.py`, mọi thay đổi state vẫn đi qua CLI.
- `skills/ chỉ được nhắc tên lệnh của scripts/, cấm chép nội dung script vào skill.` —
  việc này chạm ở 5 file skill, chỉ sửa mô tả pha và tên lệnh.
- `tests/ gọi được vào mọi tầng; không tầng nào được import tests/.` — việc này chạm ở
  9 file test.
- `2026-07-29: hook chỉ nhắc và kiểm bằng hiệu ứng thật, không trả deny vì lý do "chưa duyệt".` —
  việc này chạm gián tiếp qua `hooks/` đọc pha; không hook nào nhắc `diagram` nên không sửa.

| Rủi ro | Ảnh hưởng | Cách giảm |
|---|---|---|
| Gỡ pha làm hỏng cổng `plan` hoặc `implement` | quy trình mất chặn, code chạy trước khi duyệt | test khoá riêng cho cổng `plan` và `implement` sau khi gỡ |
| State đang chạy dở của phiên cũ có `phase=diagram` | phiên cũ kẹt, không set được pha nào | nạp state có `phase=diagram` → tự nâng về `spec`, in cảnh báo |
| `doc_lint` mất `check_diagram` nhưng `docs/tdq/mind-map/` vẫn còn 16 file | lint đỏ hàng loạt trên file lịch sử | lint cả thư mục đó phải thoát 0 (đầu ra 5) |
| Bản portable còn file cũ sau khi sinh lại | hai nơi lệch luật | dọn file thừa và kiểm toàn vẹn bundle (đầu ra 8) |
| Repo đang có 61 test đỏ từ trước | không phân biệt được lỗi mới | chốt mốc số test đỏ trước khi sửa, so sánh sau |

## 6. QC & Definition of Done

| # | Hạng mục kiểm | Điều kiện PASS |
|---|---|---|
| Q1 | Pha `diagram` không còn hợp lệ | đặt pha `diagram` bị từ chối, thông điệp nêu pha đã gỡ |
| Q2 | Thứ tự pha mới | chuỗi pha là `no_state → analyze → spec → plan → mode → implement → qc → report` |
| Q3 | Cổng vào `plan` | `spec_approved=true` là đủ để vào `plan`, không đòi sơ đồ nào |
| Q4 | Lệnh `approve diagram` | thoát khác 0, thông điệp nêu rõ pha đã gỡ, không phải lỗi lệnh lạ chung chung |
| Q5 | Lệnh `diagram add`/`diagram list` | như Q4 |
| Q6 | State cũ có key `diagrams` | nạp không lỗi, key bị bỏ qua, ghi lại state thì key biến mất |
| Q7 | State cũ có `phase=diagram` | tự nâng về `spec` kèm cảnh báo, không văng lỗi |
| Q8 | Bảng trạng thái | không còn dòng Diagrams |
| Q9 | File bị xoá | 2 script và thư mục skill `tdq-diagram` không còn tồn tại |
| Q10 | `doc_lint` độc lập | không còn import `tdq_mindmap`; lint toàn bộ `docs/` thoát 0 |
| Q11 | Ngân sách token skill | bảng ngân sách không còn khoá `tdq-diagram`, lint skill thoát 0 |
| Q12 | Tài liệu luật | grep `diagram`/`mind-map`/`mindmap` trong `skills/` trả 0 dòng |
| Q13 | Lane nhanh | mô tả lane nhanh không còn bước vẽ sơ đồ |
| Q14 | Bộ test | không còn file test mind-map; số test đỏ không tăng so với mốc trước khi sửa |
| Q15 | Bản portable | không còn file mind-map/tdq-diagram trong cả hai bundle; kiểm toàn vẹn thoát 0 |
| Q16 | Chạy thật một vòng | tạo request giả, đi từ `analyze` tới `report` không vướng cổng sơ đồ |
| Q17 | CHANGELOG + version | có mục bản mới nêu việc gỡ pha, version tăng |

DoD: 17 hạng mục Q1–Q17 PASS · 9 đầu ra §2 có mặt · `pytest tests/ -q` không có lỗi mới so
với mốc trước khi sửa · `python3 scripts/doc_lint.py docs skills` thoát 0 · agent QC độc lập
xác nhận PASS có bằng chứng · report ghi trong `docs/tdq/reports/`.

## 7. Câu hỏi còn mở

(rỗng)
