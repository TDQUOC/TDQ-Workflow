# SPEC — Tổ chức graphify: chỉ scan source, đọc có chủ đích

<!-- doc-lint: allow R10 — spec viết trước khi có luật ranh giới module -->

Ngày: 2026-08-14 · Bản: 1.0 · Brief: ../brief/2026-08-14-graphify-chi-source.md · Lane: full
Trạng thái: CHỜ DUYỆT

## 1. Mục tiêu & phạm vi

- Mục tiêu: chốt graphify thành công cụ có luật rõ hai phía — đồ thị **chỉ chứa mã nguồn
  sản phẩm** (`scripts/`, `hooks/`), và workflow **chỉ tra đồ thị khi cần liên kết hoặc
  bản đồ tổng thể**. Kèm điều kiện để đồ thị thật sự tra được: đổi lối import
  `hooks/ → tdq_state` sang dạng graphify resolve được.
- Trong phạm vi:
  - `.graphifyignore` liệt kê đủ 8 thư mục cần loại.
  - Đổi `import tdq_state` + `tdq_state.f()` → `from tdq_state import f` + `f()` ở 6 file
    `hooks/scripts/`, 58 chỗ gọi.
  - Sửa `tests/test_bash_gate.py` cho khớp lối import mới.
  - Thêm luật ĐỌC vào `analyze-full.md` + `quick-lane.md`.
  - Thêm `"graphify-out"` vào `BOOKKEEPING_PATHS` (`scripts/tdq_state.py`).
- NGOÀI phạm vi:
  - Nâng phiên bản graphify (0.9.28 → 0.9.42): đã đo, không sửa được lỗi resolve, không
    đem lại gì cho việc này.
  - Đổi lối import trong `scripts/*.py` (`context_surface.py`, `skill_inventory.py` cũng
    dùng `import tdq_state`) — hai file tiện ích, không nằm trên đường chạy hook.
  - Bỏ `graphify extract` khỏi `tdq_finish.py`: giữ nguyên tần suất chạy mỗi turn.
  - Xoá `graphify-out/` khỏi git tracking.

## 1b. Lộ trình

Chép từ brief. User duyệt spec là duyệt luôn lộ trình này.

| Bước/phase | Chạy? | Vì sao |
|---|---|---|
| Phân tích | CÓ (xong) | 6 sự thật đã đo, không còn chỗ đoán |
| Research web (tavily) | BỎ | Ẩn số ngoài duy nhất — bản graphify mới — đã đo trực tiếp, âm tính |
| Interview | CÓ (xong) | Vòng 1, 4 câu, user trả lời 1B 2A 3A 4A |
| Spec + plan | CÓ | Khung bất biến |
| Implement | CÓ | Khung bất biến |
| Chia subagent | BỎ | 4 phase nối tiếp, phase 2 đụng 6 file cùng lúc, tách ra tốn hơn lợi |
| QC bám DoD | CÓ | Đổi 58 chỗ gọi trên đường chạy hook — phải có bằng chứng từng dòng |
| QC độc lập (agent) | BỎ | User chưa yêu cầu; suite 535 test đã phủ đủ 6 file hook |
| Review sâu (agent) | BỎ | Rủi ro tập trung ở đúng 1 chỗ đã biết trước (mock.patch) |
| Report | CÓ | Khung bất biến |

## 2. Đầu ra cụ thể

| # | Đầu ra | Đường dẫn/vị trí | Đo "xong" bằng |
|---|---|---|---|
| 1 | `.graphifyignore` đủ 8 mục | `.graphifyignore` | `grep -c '/$' .graphifyignore` = 8 |
| 2 | 6 file hook dùng from-import | `hooks/scripts/*.py` | `grep -n 'tdq_state\.' hooks/scripts/*.py \| grep -v 'tdq_state\.py' \| wc -l` = 0 |
| 3 | Test bash_gate khớp lối import mới | `tests/test_bash_gate.py` | `pytest tests/test_bash_gate.py -q` xanh |
| 4 | Đồ thị thấy chuỗi hook → tdq_state | `graphify-out/graph.json` | `graphify affected "turn_snapshot()"` ra ≥ 1 node |
| 5 | Luật ĐỌC trong 2 file reference | `skills/tdq-intake/references/{analyze-full,quick-lane}.md` | `grep -c graphify` mỗi file ≥ 1 |
| 6 | `graphify-out` ngoài pathspec | `scripts/tdq_state.py` | `graphify-out` nằm trong `BOOKKEEPING_PATHS`; `git diff HEAD --name-only` sau khi loại trừ không còn đường dẫn `graphify-out` |
| 7 | Test cho mục 6 | `tests/test_turn_snapshot.py` | `pytest tests/test_turn_snapshot.py -q` xanh |

## 3. Cách tiếp cận & lý do

- Chọn: đổi lối import ở tầng hook sang `from tdq_state import <tên hàm>`, giữ nguyên
  `sys.path` bơm bởi `_common.py`.
- Vì: đã đo trực tiếp trên cả 0.9.28 lẫn 0.9.42 — graphify chỉ sinh cạnh `calls`
  cross-file cho dạng `from M import f`; dạng `import M` + `M.f()` không sinh cạnh nào.
  Bằng chứng: `hooks/` có 58 chỗ gọi `tdq_state.*`, đồ thị chỉ có 1 cạnh
  `hooks/* → scripts/tdq_state.py`. Đây là điều kiện CẦN để đầu ra #4 đạt.
- Đã loại: nâng graphify lên 0.9.42 — extract cùng repo cho ra y hệt 412 node, cùng 12
  cặp cạnh cross-file, `turn_snapshot` vẫn không có cạnh gọi từ `prompt_context.py`.
- Đã loại: giữ nguyên `tdq_state.` cho dễ đọc — khi đó đồ thị mù đúng phần giá trị nhất
  (chuỗi hook → state), luật ĐỌC ở đầu ra #5 sẽ vô nghĩa với mọi câu hỏi về hook.

## 3b. Năng lực & công cụ

| Skill | Nguồn | Phán quyết | Dùng ở đâu / Lý do loại |
|---|---|---|---|
| tdq-spec | project | NỀN | Skill khung đang chạy cho phase này |
| graphify | user | DÙNG | Đầu ra #1, #4 — cấu hình quét và kiểm cạnh sau khi đổi import |
| mem0-memory | user | DÙNG | Chốt xong ghi 1 fact: graphify chỉ resolve from-import |
| superpowers:test-driven-development | plugin:superpowers | DÙNG | Đầu ra #3, #7 — red→green cho từng task |
| Đã xét 214 skill khác | user/plugin/built-in | KHÔNG | khác lĩnh vực |

## 4. Yêu cầu bắt buộc

- Log service bật mặc định: timestamp, đủ chi tiết debug, tắt/giảm được qua config.
  Việc này có runtime (sửa `hooks/scripts/*.py` và `scripts/tdq_state.py`) — giữ nguyên
  log service sẵn có của `tdq_state`, không thêm không bớt.
- Không placeholder, không TODO stub, không mock trình bày như dữ liệu thật.
- Mỗi thành phần có unit test riêng, chạy được bằng một lệnh.

## 5. Ràng buộc & rủi ro

| Rủi ro | Ảnh hưởng | Cách giảm |
|---|---|---|
| `mock.patch.object(tdq_state, "turn_log_read")` ở `tests/test_bash_gate.py:185` hết tác dụng sau khi bind tên lúc import | 1 test đỏ | Task riêng: patch vào chính module hook, giữ nguyên ý nghĩa phép kiểm |
| Thứ tự import: `from tdq_state import ...` phải chạy SAU `from _common import ...` (chính `_common` bơm `sys.path`) | 6 hook `ImportError`, workflow chết | Giữ đúng thứ tự, đánh dấu `# noqa: E402`; task 2.1 chạy trước, `pytest tests/` sau mỗi file |
| Đổi 58 chỗ gọi bằng tay dễ sót/nhầm tên hàm | Hook lỗi runtime, không lộ ra khi test chạy nhánh khác | DoD đếm `grep -c 'tdq_state\.'` = 0 cộng `pytest tests/` đủ 535 test |
| Import list dài, nhiều tên chung (`load`, `save`) lẫn vào namespace hook | Khó đọc, dễ đè tên | Đầu mỗi file ghi rõ khối import; QC kiểm không có tên nào trùng hàm cục bộ |
| `.graphifyignore` liệt kê thư mục tương lai có thể chứa code | Code mới vô tình không vào đồ thị | Ghi comment trong file nêu rõ; report nhắc lại |
| Cài graphify 0.9.42 trong venv scratchpad khi phân tích | Không ảnh hưởng — venv riêng, `--out` ra scratchpad | Không đụng bản 0.9.28 đang cài; venv nằm ngoài repo |

## 6. QC & Definition of Done

| # | Hạng mục kiểm | Lệnh/cách kiểm | Điều kiện PASS |
|---|---|---|---|
| Q1 | `.graphifyignore` đủ 8 thư mục | `grep -c '/$' .graphifyignore` | in ra `8` |
| Q2 | Không còn lối gọi qua module ở hook | `grep -n 'tdq_state\.' hooks/scripts/*.py \| grep -v 'tdq_state\.py' \| wc -l` | in ra `0` (chuỗi lệnh `tdq_state.py` in cho user không tính) |
| Q3 | Suite đầy đủ xanh | `python3 -m pytest tests/ -q` | `535 passed` trở lên, 0 failed |
| Q4 | Hook chạy thật không lỗi import | `echo '{}' \| python3 hooks/scripts/prompt_context.py; echo $?` | exit code `0` |
| Q5 | Đồ thị thấy chuỗi hook → tdq_state | `graphify extract . --code-only --force` rồi `graphify affected "turn_snapshot()"` | ra ≥ 1 node, có `prompt_context` |
| Q6 | Cạnh cross-file `hooks/* → tdq_state.py` tăng | đếm trong `graph.json` | ≥ 20 cạnh (trước: 1) |
| Q7 | `graphify-out` ngoài pathspec | `git diff HEAD --name-only -- <các exclude> \| grep -c graphify-out` cộng `pytest tests/test_turn_snapshot.py` | in `0` và test xanh |
| Q8 | Luật ĐỌC có mặt | `grep -c graphify skills/tdq-intake/references/analyze-full.md quick-lane.md` | mỗi file ≥ 1 |
| Q9 | Tài liệu qua lint | `python3 scripts/doc_lint.py <các file .md đổi>` | exit 0 |

DoD: cả Q1–Q9 PASS; plan tick hết `[x]`; `docs/tdq/reports/2026-08-14-graphify-chi-source.md`
đã viết; working log 2026-08-14 có dòng kết quả; không còn test đỏ.

## 7. Câu hỏi còn mở

(Rỗng.)
