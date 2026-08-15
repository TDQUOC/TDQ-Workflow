# SPEC — Slug có giờ phút + đếm thời gian mỗi request và mỗi phase

Ngày: 2026-08-15 · Bản: 1.0 · Brief: ../brief/2026-08-15-gio-phut-dem-thoi-gian.md · Lane: full
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md
Trạng thái: CHỜ DUYỆT

## 1. Mục tiêu & phạm vi

- Mục tiêu: slug của request TDQ mang thêm giờ phút (`YYYY-MM-DD-HHMM-<kebab>`), và mỗi
  request có số liệu thời gian đo được — tổng thời gian request cùng thời gian từng phase,
  ghi song song hai loại: đồng hồ treo tường và thời gian model chạy.
- Trong phạm vi:
  - Đổi công thức slug ở mọi chỗ luật đang in nó ra.
  - Hàm phân giải slug chấp nhận CẢ HAI định dạng khi đọc, bắt buộc có giờ phút khi ghi mới.
  - `state.json` thêm mốc mở request và lịch sử phase; chỉ `tdq_state.py` được ghi.
  - CLI mới `scripts/tdq_timing.py`: in bảng thời gian, và đóng sổ vào `docs/tdq/timing.jsonl`.
  - Bảng thời gian trong report cuối request; một dòng đồng hồ trong `tdq-status`.
- NGOÀI phạm vi (chép từ brief `### Phạm vi đã chốt`, mặt LOẠI):
  - Bảo mật — dữ liệu thời gian không có gì nhạy cảm.
  - Hiệu năng runtime của chính phép đo — trừ một ngưỡng ở §5.
  - Đa nền tảng — công cụ chạy trên máy của user, không đóng gói đi đâu.
  - Đổi tên 269 file tài liệu cũ (user chốt câu 2: giữ nguyên).

## 1b. Lộ trình

| Bước/phase | Chạy? | Vì sao |
|---|---|---|
| Research web | BỎ | việc thuần nội bộ, không có ẩn số bên ngoài |
| Vòng scope | CÓ | đã chạy ở analyze, dấu hiệu 2 |
| Interview chi tiết | CÓ | đã chạy 2 vòng, hết câu hỏi làm đổi kết quả |
| Spec riêng + plan checkbox | CÓ | khung bất biến của chế độ chuyên sâu |
| Chia subagent | BỎ | các task nối nhau trên cùng vài file, tách worktree chỉ đẻ xung đột |
| QC độc lập bằng agent | BỎ | mọi hạng mục DoD chạy được bằng một lệnh |
| Review sâu `tdq-reviewer` | BỎ | phạm vi đã khoá bằng 7 câu trả lời của user |
| Report | CÓ | khung bất biến |

## 2. Đầu ra cụ thể

| # | Đầu ra | Đường dẫn/vị trí | Đo "xong" bằng |
|---|---|---|---|
| 1 | Công thức slug mới trong luật — 9 chỗ đã đếm | `skills/tdq-conventions/SKILL.md:77`, `skills/tdq-conventions/references/phases.md` (4 chỗ), `skills/tdq-intake/SKILL.md:34`, `scripts/tdq_state.py` (3 chỗ bảng `next`), `docs/tdq/STATE.md:20`, `portable/AGENTS.md:79`, `portable/workflow/phases.md` (4 chỗ), `portable/workflow/01-intake.md:26` | `grep -rn "YYYY-MM-DD-" skills scripts docs/tdq/STATE.md portable` — mọi dòng đều có `HHMM` |
| 2 | Hàm `parse_slug()` hai định dạng | `scripts/tdq_state.py` | `pytest tests/test_timing.py -k parse_slug` |
| 3 | `init` bắt buộc slug có giờ phút | `scripts/tdq_state.py` lệnh `init` | `pytest tests/test_timing.py -k init_bat_buoc` |
| 4 | Schema state có `started_at` + `phase_history` | `scripts/tdq_state.py` `default_state()`, nhánh `set phase=` | `pytest tests/test_timing.py -k phase_history` |
| 5 | CLI `tdq_timing.py show` in bảng thời gian | `scripts/tdq_timing.py` | `pytest tests/test_timing.py -k bang_thoi_gian` |
| 6 | CLI `tdq_timing.py close` append sổ | `scripts/tdq_timing.py` → `docs/tdq/timing.jsonl` | `pytest tests/test_timing.py -k dong_so` |
| 7 | `tdq_finish --phase idle` tự đóng sổ | `scripts/tdq_finish.py` | `pytest tests/test_timing.py -k finish_dong_so` |
| 8 | Bảng thời gian bắt buộc trong report | `skills/tdq-build/SKILL.md` hoặc reference khuôn report | `pytest tests/test_timing.py -k khuon_report` |
| 9 | Dòng đồng hồ trong `tdq-status` | `skills/tdq-status/SKILL.md` | `pytest tests/test_timing.py -k status_dong_ho` |
| 10 | Phát hành | `CHANGELOG.md` + `.claude-plugin/plugin.json` 0.20.0 | `grep 0.20.0` cả hai file |

## 3. Cách tiếp cận & lý do

- Chọn: **hai loại thời gian đo bằng hai nguồn khác nhau, hiện cạnh nhau.** Đồng hồ treo
  tường lấy từ mốc trong `state.json`; thời gian model chạy lấy từ transcript bằng cách cộng
  khoảng cách giữa các bước model nằm trong cửa sổ của từng phase, tái dùng `iter_events`,
  `_parse_time` và ngưỡng `MAX_GAP_SECONDS` của `scripts/step_audit.py`.
- Vì: hai con số trả lời hai câu khác nhau. Phase chờ user duyệt 2 giờ thì treo tường là 2 giờ
  còn model chạy 3 phút — chỉ có cột thứ hai mới nói được chỗ nào tối ưu được.
- Chọn: **slug hai định dạng, đọc rộng ghi hẹp.** Đọc chấp nhận cả `YYYY-MM-DD-<kebab>` lẫn
  `YYYY-MM-DD-HHMM-<kebab>`; ghi mới bắt buộc có giờ phút, `init` từ chối slug thiếu.
- Vì: 269 file cũ giữ nguyên tên theo yêu cầu user, nên phần đọc phải rộng. Còn nếu phần ghi
  chỉ cảnh báo thay vì từ chối thì chuẩn mới sẽ trôi — cảnh báo không đổi được hành vi.
- Đã loại: đổi tên toàn bộ file cũ — user chốt giữ nguyên; giá là sửa 142 tham chiếu chéo mà
  không thêm thông tin nào.
- Đã loại: lưu lịch sử phase trong working log — log là văn xuôi, muốn cộng số phải parse chữ.
- Đã loại: gộp phép đo thời gian vào `step_audit.py` — script đó đo cả phiên theo transcript,
  không biết gì về request và phase; trộn vào sẽ buộc nó đọc `state.json`.

## 3b. Năng lực & công cụ

| Skill | Nguồn | Phán quyết | Dùng ở đâu / Lý do loại |
|---|---|---|---|
| tdq-conventions | plugin:tdq-workflow | NỀN | skill khung đang chạy; chính nó chứa công thức slug (đầu ra 1) |
| tdq-intake | plugin:tdq-workflow | DÙNG | sửa công thức slug ở `SKILL.md:34` (đầu ra 1) |
| tdq-spec | plugin:tdq-workflow | NỀN | skill khung đang chạy ở phase này |
| tdq-plan | plugin:tdq-workflow | DÙNG | phase kế tiếp, viết plan checkbox |
| tdq-build | plugin:tdq-workflow | DÙNG | khuôn report phải có bảng thời gian (đầu ra 8) |
| tdq-status | plugin:tdq-workflow | DÙNG | thêm dòng đồng hồ (đầu ra 9) |
| mem0-memory | plugin:mem0 | DÙNG | chốt xong ghi một fact ngắn về chuẩn slug mới |
| Đã xét 278 skill khác | user/plugin/built-in | KHÔNG | khác lĩnh vực |

## 4. Yêu cầu bắt buộc

- Log service bật mặc định: timestamp, đủ chi tiết debug, tắt được qua `TDQ_LOG=0` — giống
  `step_audit.py`. Áp cho `scripts/tdq_timing.py`.
- Không placeholder, không TODO stub, không mock trình bày như dữ liệu thật.
- Mỗi thành phần có unit test riêng, chạy được bằng một lệnh.
- Clean code: TẮT (user chốt 2026-08-15 12:18, đáp án B) — bỏ bước `code_rule_scan.py` cuối
  request; code viết ra vẫn tổ chức theo rule ngôn ngữ trong `skills/tdq-build/references/rules/`.

## 5. Ràng buộc & rủi ro

Ràng buộc kiến trúc phải giữ (chép từ `docs/kien-truc.md` — bản NHÁP, user chưa chốt, nên ở
đây là ràng buộc tự nguyện):

- "Chỉ `scripts/tdq_state.py` được ghi `docs/tdq/state.json`" — việc này chạm ở `phase_history`:
  `tdq_timing.py` chỉ ĐỌC state, mọi mốc thời gian do `tdq_state.py` đóng dấu.
- "`skills/` chỉ được nhắc TÊN LỆNH của `scripts/`, cấm chép nội dung script" — việc này chạm ở
  `tdq-status/SKILL.md` và khuôn report: chỉ ghi tên lệnh `tdq_timing.py show`.
- "File code MỚI bắt buộc nằm trong `scripts/` hoặc `hooks/`" — `tdq_timing.py` nằm ở `scripts/`.

| Rủi ro | Ảnh hưởng | Cách giảm |
|---|---|---|
| `state.json` đang chạy chưa có `phase_history` | đọc state cũ vỡ | `default_state()` vá field thiếu khi load; test riêng cho state schema cũ |
| Không tìm thấy transcript (chạy ở máy khác, log bị xoá) | cột thời gian model rỗng | cột đó in `—` và một dòng lý do, KHÔNG làm hỏng bảng treo tường |
| Cửa sổ phase trùm cả lúc user đi ăn cơm | thời gian model bị thổi phồng | dùng lại ngưỡng `MAX_GAP_SECONDS = 300` của `step_audit.py`, khoảng dài hơn không tính |
| Đọc transcript 135 MB mỗi lần `show` | lệnh chậm, khó chịu khi hỏi status | đọc theo dòng, không nạp cả file; ngưỡng: `show` xong dưới 2 giây trên transcript 135 MB |
| Request bị `init` đè khi còn dở | mất lịch sử phase của request cũ | `init` đóng sổ request cũ vào `timing.jsonl` trước khi reset |

## 6. QC & Definition of Done

| # | Hạng mục kiểm | Lệnh/cách kiểm | Điều kiện PASS |
|---|---|---|---|
| Q1 | Luật không còn công thức slug cũ | `grep -rn "YYYY-MM-DD-" skills scripts docs/tdq/STATE.md portable` | mọi dòng khớp đều có `HHMM`; bản `portable/` khớp bản `skills/` |
| Q2 | `parse_slug` đọc được slug cũ | `pytest tests/test_timing.py -k parse_slug_cu` | 1 passed |
| Q3 | `parse_slug` đọc được slug mới | `pytest tests/test_timing.py -k parse_slug_moi` | 1 passed |
| Q4 | `init` từ chối slug thiếu giờ phút | `pytest tests/test_timing.py -k init_bat_buoc` | 1 passed, thoát khác 0 kèm thông báo nêu đúng công thức |
| Q5 | `set phase=` đóng dấu vào `phase_history` | `pytest tests/test_timing.py -k phase_history` | 1 passed |
| Q6 | Phase vào lại lần hai cộng dồn kèm số lần | `pytest tests/test_timing.py -k quay_lui` | 1 passed, ra `2 lần` |
| Q7 | State cũ thiếu field vẫn đọc được | `pytest tests/test_timing.py -k state_cu` | 1 passed |
| Q8 | `show` in đủ hai cột thời gian | `pytest tests/test_timing.py -k bang_thoi_gian` | 1 passed |
| Q9 | Không có transcript thì cột model in `—` | `pytest tests/test_timing.py -k khong_transcript` | 1 passed, thoát 0 |
| Q10 | Khoảng chờ dài hơn 300 giây không tính vào thời gian model | `pytest tests/test_timing.py -k nguong_cho` | 1 passed |
| Q11 | `close` append đúng một dòng JSON hợp lệ | `pytest tests/test_timing.py -k dong_so` | 1 passed |
| Q12 | `init` đóng sổ request cũ trước khi reset | `pytest tests/test_timing.py -k init_dong_so` | 1 passed |
| Q13 | `tdq_finish --phase idle` gọi đóng sổ | `pytest tests/test_timing.py -k finish_dong_so` | 1 passed |
| Q14 | Khuôn report bắt buộc có bảng thời gian | `pytest tests/test_timing.py -k khuon_report` | 1 passed |
| Q15 | `tdq-status` có dòng đồng hồ | `pytest tests/test_timing.py -k status_dong_ho` | 1 passed |
| Q16 | Log bật mặc định, tắt được bằng `TDQ_LOG=0` | `TDQ_LOG=0 python3 scripts/tdq_timing.py show 2>err >/dev/null; wc -l < err` | 0 dòng stderr; không đặt biến thì ≥ 2 dòng |
| Q17 | `show` chạy dưới 2 giây trên transcript thật | `time python3 scripts/tdq_timing.py show` | dưới 2,0 giây |
| Q18 | Toàn bộ suite không hồi quy | `python3 -m pytest -q` | không test nào đỏ, số test ≥ 608 |
| Q19 | Lint mọi file tài liệu đã sửa | `python3 scripts/doc_lint.py <các file>` | exit 0 |
| Q20 | Phát hành đúng bản | `grep -c "0.20.0" CHANGELOG.md .claude-plugin/plugin.json` | cả hai ≥ 1 |

DoD: cả 20 hạng mục Q1–Q20 PASS bằng đúng lệnh ghi ở cột giữa; thêm QC-F1 chạy toàn bộ suite,
QC-F2 hồi quy mọi vùng ghi ở dòng `Chạm:` của plan, QC-F3 đối chiếu ba ràng buộc kiến trúc §5.

## 7. Câu hỏi còn mở

(rỗng)
