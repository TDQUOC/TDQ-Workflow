# SPEC — Cắt token thừa trong TDQ workflow

Ngày: 2026-08-09 · Bản: 1.0 · Brief: ../brief/2026-08-09-cat-token-thua-workflow.md · Lane: full
Trạng thái: CHỜ DUYỆT

## 1. Mục tiêu & phạm vi

- Mục tiêu: cắt 6 điểm nghẽn C1–C6 đã chốt ở báo cáo audit 2026-08-09. Đo bằng 3 con số:
  bảng kiểm kê năng lực trong brief giảm từ 242 dòng xuống ≤ 6 dòng; bảng đó bị ghi 2 lần
  thay vì 3 lần; `docs/claude-md-mau.md` và `~/.claude/CLAUDE.md` trở lại giống hệt nhau.
- Trong phạm vi:
  - C1 — luật ghi bảng kiểm kê năng lực (chỉ ghi dòng DÙNG và NỀN).
  - C2 — bỏ bảng `## Năng lực → task` khỏi khuôn plan.
  - C3 — log service và phase `Log & test` chỉ bắt buộc khi việc có runtime.
  - C4 — bỏ mục chi tiết từng phase khỏi `phases.md`.
  - C5 — câu hỏi chốt vòng interview chỉ hỏi khi vòng đó có câu hỏi.
  - C6 — rút gọn `docs/claude-md-mau.md` rồi đồng bộ sang `~/.claude/CLAUDE.md`.
  - Bỏ trường `Nạp` khỏi khối hợp đồng skill (user chốt câu 3, phương án A).
- NGOÀI phạm vi:
  - Mọi gate duyệt: 2 gate lane full, 1 gate lane quick, luật user chốt mode. Giữ nguyên.
  - Trường `Ra`, `Kiểm`, `Không dùng cho` của khối hợp đồng. Giữ nguyên.
  - Chép `### Lộ trình` từ brief sang spec §1b. Giữ nguyên.
  - Luật QC bám đúng số dòng DoD, trần 3 vòng fix, `doc_lint` R4, hook `[TDQ:NEXT]`,
    `tdq_finish.py`. Giữ nguyên.
  - Sửa lại spec và plan cũ đã nằm trong `docs/tdq/` (user chốt câu 4, phương án A).
  - Tầng `nhỏ` và ba ngoại lệ không-gate đã báo cáo. Để riêng một request sau.

## 1b. Lộ trình

Chép từ brief mục `### Lộ trình`. User duyệt spec là duyệt luôn lộ trình này.

| Bước/phase | Chạy? | Vì sao |
|---|---|---|
| Research web | BỎ | thuần nội bộ: chỉ sửa markdown và 2 script Python của repo này |
| Interview | XONG | 4 câu đã hỏi, user trả lời 1A 2A 3A 4A |
| Spec + plan, 2 gate duyệt | CÓ | khung bất biến, và user yêu cầu giữ gate |
| Chia subagent | BỎ | 6 hạng mục đụng chồng lên 4 file chung, chạy song song sẽ xung đột |
| QC độc lập bằng agent | BỎ | mọi dòng DoD đã là lệnh chạy được, không cần góc nhìn thứ hai |
| Review sâu bằng agent | BỎ | phạm vi nhỏ, đã đọc hết file liên quan |

## 2. Đầu ra cụ thể

| # | Đầu ra | Đường dẫn/vị trí | Đo "xong" bằng |
|---|---|---|---|
| 1 | Luật ghi bảng năng lực gọn: chỉ dòng DÙNG và NỀN, cộng 1 dòng tổng `Đã xét N skill khác` | `skills/tdq-intake/references/skill-inventory.md` | `grep -c "Đã xét"` trả về ≥ 1 |
| 2 | Khuôn spec §3b theo luật mới; §4 log service có điều kiện runtime | `skills/tdq-spec/references/spec-template.md` | `grep -c "có runtime"` trả về ≥ 1 |
| 3 | Khuôn plan: bỏ bảng ánh xạ năng lực, hợp đồng còn 5 trường, phase log có điều kiện | `skills/tdq-plan/references/plan-template.md` | `grep -c "Năng lực → task"` trả về 0 |
| 4 | `CONTRACT_FIELDS` bỏ `Nạp` | `scripts/doc_lint.py` | `python3 -c "import doc_lint; assert 'Nạp' not in doc_lint.CONTRACT_FIELDS"` |
| 5 | `PHASE_TABLE`: `phases-doc` không sinh mục chi tiết từng phase; bước interview quick có điều kiện | `scripts/tdq_state.py` | `phases-doc` không in dòng bắt đầu bằng `## analyze` |
| 6 | `phases.md` sinh lại từ hằng mới | `skills/tdq-conventions/references/phases.md` | `tests/test_phase_table.py::test_docs_match_constant` xanh |
| 7 | Luật hỏi chốt vòng interview có điều kiện | `skills/tdq-intake/references/interview.md` | `grep -c "có ít nhất một câu hỏi"` trả về ≥ 1 |
| 8 | Bản mẫu CLAUDE.md rút gọn, và file thật đồng bộ với nó | `docs/claude-md-mau.md`, `~/.claude/CLAUDE.md` | `diff` hai file trả về rỗng |
| 9 | Test cho từng thay đổi ở đầu ra 1–8 | `tests/test_doc_lint.py`, `tests/test_phase_table.py`, `tests/test_skill_shape.py` | `python3 -m pytest tests -q` xanh |

## 3. Cách tiếp cận & lý do

- Chọn: sửa tại nguồn sự thật của từng thứ, rồi để test cũ làm hàng rào.
  `phases.md` sửa qua hằng `PHASE_TABLE` trong `tdq_state.py` rồi sinh lại bằng
  `phases-doc`. `CLAUDE.md` sửa qua `docs/claude-md-mau.md` rồi đồng bộ ra file thật.
- Vì: hai file đó đều có test canh sẵn. `tests/test_phase_table.py::test_docs_match_constant`
  bắt trường hợp sửa tay `phases.md`. `tests/test_claude_md_core.py` giữ 12 luật bất biến
  và trần 3.500 byte cho bản mẫu. Sửa đúng nguồn thì test cũ thành DoD miễn phí.
- Đã loại: sửa thẳng `phases.md` và `~/.claude/CLAUDE.md` — vì cả hai đều là bản sinh ra,
  sửa tay sẽ lệch lại đúng như hiện trạng đang đo được (bản mẫu 3.463 byte, file thật
  4.243 byte, `diff` khác rỗng).
- Đã loại: đổi `doc_lint` R8 thành đếm số dòng bảng §3b — vì R8 hiện chỉ kiểm tính hợp lệ
  của dòng có mặt, nên C1 và C2 không cần đụng tới Python.

## 3b. Năng lực & công cụ

Chép từ brief mục `### Năng lực dùng được`. Kiểm kê ngày 2026-08-09: 242 skill trên đĩa,
cộng khoảng 30 skill built-in trong context. Áp luật gom của `skill-inventory.md`.

| Skill | Nguồn | Phán quyết | Dùng ở đâu / Lý do loại |
|---|---|---|---|
| tdq-intake, tdq-spec, tdq-plan, tdq-build, tdq-conventions, tdq-status | project | NỀN | chính workflow đang chạy, cũng là đối tượng bị sửa |
| graphify | user | DÙNG | sinh lại graph cuối turn có đổi code, đầu ra #4 và #5 |
| mem0-memory | user | DÙNG | ghi một fact về hình dạng workflow sau khi cắt |
| 240 skill còn lại: figma, canva, mongodb, cloudflare, postman, hyperframes, huggingface, adobe, qt, astronomer, unreal, datarobot, base44, tavily, firecrawl, chrome-devtools, playwright, dataviz, frontend-design, artifact | user/plugin/built-in | KHÔNG | khác lĩnh vực — việc này chỉ sửa markdown và 2 script Python nội bộ |

## 4. Yêu cầu bắt buộc

- Log service: **BỎ, có lý do**. Việc này không tạo phần mềm có runtime. Đầu ra là 7 file
  markdown và 2 script Python đã có sẵn log qua `tdq_finish.py`. Đây chính là trường hợp
  mà C3 sinh ra để xử lý.
- Không placeholder, không TODO stub, không mock trình bày như dữ liệu thật.
- Mỗi đầu ra có một phép kiểm chạy được bằng một lệnh, ghi ở cột cuối §2.

## 5. Ràng buộc & rủi ro

| Rủi ro | Ảnh hưởng | Cách giảm |
|---|---|---|
| Bỏ trường `Nạp` làm sub-agent mất đường dẫn `SKILL.md` | Agent ngoài không nạp được skill | Chuyển câu đường dẫn vào trường `Để`, giữ nguyên nội dung, chỉ bớt một nhãn |
| Sửa `~/.claude/CLAUDE.md` ảnh hưởng mọi project khác của user | Mất luật ở project ngoài | `tests/test_claude_md_core.py` canh 12 luật bất biến; chỉ cắt phần đã có ở file đích trong `MOVED` |
| Cắt mục chi tiết `phases.md` làm mất chỉ dẫn khi chưa nạp skill | Claude không biết bước cụ thể | Bảng 8 cột và khối lệnh nguyên văn ở lại; cột "việc duy nhất" đã mang nội dung đó |
| Test cũ hardcode chuỗi sắp bị xoá | Suite đỏ sau khi sửa | Chạy full suite ở QC; sửa test theo luật mới nằm trong đầu ra #9 |

## 6. QC & Definition of Done

| # | Hạng mục kiểm | Lệnh/cách kiểm | Điều kiện PASS |
|---|---|---|---|
| Q1 | Bảng năng lực gọn đã thành luật | `grep -c "Đã xét" skills/tdq-intake/references/skill-inventory.md` | ≥ 1 |
| Q2 | Khuôn spec có điều kiện runtime | `grep -c "có runtime" skills/tdq-spec/references/spec-template.md` | ≥ 1 |
| Q3 | Khuôn plan hết bảng ánh xạ năng lực | `grep -c "Năng lực → task" skills/tdq-plan/references/plan-template.md` | 0 |
| Q4 | Hợp đồng skill còn 5 trường | `cd scripts && python3 -c "import doc_lint; print('Nạp' in doc_lint.CONTRACT_FIELDS)"` | in `False` |
| Q5 | `phases-doc` hết mục chi tiết từng phase | `python3 scripts/tdq_state.py phases-doc \| grep -c "^## analyze"` | 0 |
| Q6 | `phases.md` khớp hằng nguồn | `python3 -m pytest tests/test_phase_table.py -q` | 0 fail |
| Q7 | Luật hỏi chốt interview có điều kiện | `grep -c "có ít nhất một câu hỏi" skills/tdq-intake/references/interview.md` | ≥ 1 |
| Q8 | Bản mẫu và file thật giống hệt nhau | `diff docs/claude-md-mau.md ~/.claude/CLAUDE.md` | không in gì, exit 0 |
| Q9 | Luật bất biến của CLAUDE.md còn đủ | `python3 -m pytest tests/test_claude_md_core.py -q` | 0 fail |
| Q10 | Doc lint sạch trên file vừa sửa | `python3 scripts/doc_lint.py <các file skills vừa sửa>` | exit 0 |
| Q11 | Toàn bộ test suite | `python3 -m pytest tests -q` | 0 fail |

DoD: 11 hạng mục Q1–Q11 đều PASS, mỗi hạng mục có lệnh và output thật ghi trong
`docs/tdq/qc/2026-08-09-cat-token-thua-workflow.md`.

## 7. Câu hỏi còn mở

(Rỗng.)
