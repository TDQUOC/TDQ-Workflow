# SPEC — Đổi tên mode thực thi + phân tích lý do đề xuất

Ngày: 2026-08-14 · Bản: 1.0 · Brief: ../brief/2026-08-14-doi-ten-mode-implement.md · Lane: full
Trạng thái: CHỜ DUYỆT

## 1. Mục tiêu & phạm vi

- Mục tiêu: cổng `mode` gọi hai lựa chọn bằng nhãn thân thiện — "làm trực tiếp (inline
  implement)" và "giao trợ lý (sub-agent implement)" — và luôn kèm 1–3 dòng phân tích vì
  sao đề xuất đúng mode đó cho plan đang chờ, dựa trên số liệu thật của plan.
- Trong phạm vi: lớp hiển thị và lớp nhận câu trả lời của mode (`scripts/tdq_state.py`,
  `hooks/scripts/_common.py`, `hooks/scripts/prompt_context.py`,
  `hooks/scripts/edit_gate.py`), khuôn skill `tdq-plan` + `tdq-build` +
  `plan-template.md`, và test tương ứng.
- NGOÀI phạm vi: giá trị chuẩn `main|subagent` trong state và tham số `--mode` (giữ
  nguyên theo đáp án 1A); thư mục `portable/`; cách chọn mode lúc build.

## 1b. Lộ trình

| Bước/phase | Chạy? | Vì sao |
|---|---|---|
| Research web | BỎ | Thuần nội bộ, quy ước của chính repo, không có ẩn số bên ngoài. |
| Interview | CÓ (xong) | 4 câu đã hỏi, đáp án `1a 2a 3a 4b` ghi ở brief. |
| Spec + plan | CÓ | Khung bất biến. |
| Implement | CÓ | Sửa 4 file mã, 3 file skill, test. |
| QC độc lập (agent) | BỎ | Thay đổi lớp hiển thị, rủi ro thấp; QC bằng lệnh là đủ. |
| Report | CÓ | Khung bất biến. |

## 2. Đầu ra cụ thể

| # | Đầu ra | Đường dẫn/vị trí | Đo "xong" bằng |
|---|---|---|---|
| 1 | `MODE_LABELS` + `mode_label()` | `scripts/tdq_state.py` | `mode_label("main")` trả `làm trực tiếp (inline implement)` |
| 2 | `MODE_ALIASES` + `normalize_mode()` dùng khi parse `--mode` và dạng gõ tắt | `scripts/tdq_state.py` | `approve plan --mode inline` → `implement_mode = main` |
| 3 | Checklist phase `mode` nêu nhãn mới và bắt buộc đoạn phân tích lý do | `scripts/tdq_state.py` mục `mode` | `tdq_state.py next` ở phase `mode` in đủ 2 nhãn |
| 4 | `APPROVE_HINTS["mode"]` dùng nhãn mới, vẫn nêu được cách gõ | `hooks/scripts/_common.py` | Lời nhắc chứa "inline" và "sub-agent" |
| 5 | Regex nhận câu trả lời chấp nhận cả tên cũ lẫn tên mới | `hooks/scripts/prompt_context.py` | `looks_like_approval` đúng với 4 chuỗi mẫu |
| 6 | Khuôn khối hỏi mode mới + luật viết đoạn phân tích | `skills/tdq-plan/SKILL.md` bước 1 và 6 | grep thấy nhãn mới và mục luật phân tích |
| 7 | Nhãn mới trong khuôn plan và skill build | `plan-template.md`, `skills/tdq-build/SKILL.md` | grep thấy nhãn ở cả hai file |
| 8 | Test cho nhãn, alias, regex | `tests/test_mode_phase.py`, `tests/test_prompt_context.py` | Hai file test chạy xanh |

## 3. Cách tiếp cận & lý do

- Chọn: tách lớp hiển thị khỏi lớp giá trị, đúng mẫu hình `LANE_LABELS`/`LANE_ALIASES`
  đã có sẵn cho lane trong cùng file `tdq_state.py`.
- Vì: state cũ, plan cũ và mọi test đang dùng chuỗi `main|subagent`; đổi giá trị chuẩn sẽ
  kéo theo migrate state và làm dòng `Mode thực thi:` của plan cũ vô nghĩa. Nguồn: đọc
  trực tiếp `scripts/tdq_state.py:29-47,499-504,975-1000` và
  `hooks/scripts/_common.py:36-43`.
- Đoạn phân tích lý do lấy số liệu từ chính plan: số task, task có phụ thuộc nối tiếp,
  số file bị nhiều task cùng đụng, có nhãn `(mcp)` hay không. Ngưỡng đề xuất giữ nguyên
  luật cũ ở `skills/tdq-plan/SKILL.md` bước 1: trên 6 task mà file rời nhau → đề xuất
  `subagent`; đụng chung file hoặc phụ thuộc chặt → `main`.
- Đã loại: đổi thẳng giá trị chuẩn thành `inline|sub-agent` — vì phải migrate state và
  sửa `_PLAN_MODE`, đổi lấy đúng một lợi ích là tên biến đẹp hơn.

## 3b. Năng lực & công cụ

| Skill | Nguồn | Phán quyết | Dùng ở đâu / Lý do loại |
|---|---|---|---|
| tdq-intake | plugin:tdq-workflow | NỀN | Skill khung đang chạy cho phase analyze. |
| mem0-memory | user | DÙNG | Ghi 1 fact về quy ước nhãn mode sau khi chốt. |
| graphify | user | KHÔNG | khác lĩnh vực — việc nằm ở chuỗi hiển thị, không phải câu hỏi liên kết mã. |
| Đã xét 60 skill khác | user/plugin/built-in | KHÔNG | khác lĩnh vực |

## 4. Yêu cầu bắt buộc

- Log service: GIỮ NGUYÊN — việc này có runtime (`tdq_state.py`, hook) nhưng không thêm
  luồng mới; `_info`/`_warn` sẵn có phải còn chạy và vẫn tắt được bằng `TDQ_LOG=0`.
- Không placeholder, không TODO stub.
- Mỗi thay đổi hành vi có unit test riêng, chạy được bằng một lệnh.

## 5. Ràng buộc & rủi ro

| Rủi ro | Ảnh hưởng | Cách giảm |
|---|---|---|
| Regex nhận mode bắt nhầm chữ "inline" trong câu khác | Ghi nhận chọn mode sai | Giữ `\b` biên từ, thêm test cho câu nhiễu |
| Nhãn dài làm lời nhắc một dòng bị cắt cụt | User mất phần đề xuất | Giữ phần "plan đề xuất …" ở ĐẦU chuỗi như hiện nay |
| Đoạn phân tích thành sáo rỗng | Mất đúng thứ user muốn | Luật ghi rõ 4 căn cứ bắt buộc lấy từ plan |
| Sửa tài liệu skill làm hỏng test khuôn sẵn có | Suite đỏ | Chạy full suite ở QC |

## 6. QC & Definition of Done

| # | Hạng mục kiểm | Lệnh/cách kiểm | Điều kiện PASS |
|---|---|---|---|
| Q1 | Nhãn hiển thị đúng | `python3 -c "import sys;sys.path.insert(0,'scripts');import tdq_state as s;print(s.mode_label('main'),'|',s.mode_label('subagent'))"` | In `làm trực tiếp (inline implement) \| giao trợ lý (sub-agent implement)` |
| Q2 | Alias mới ghi đúng giá trị chuẩn | `approve plan --mode inline` trên repo tạm rồi `get implement_mode` | In `main` |
| Q3 | Tương thích ngược | `approve plan --mode subagent` rồi `get implement_mode` | In `subagent` |
| Q4 | Regex nhận cả 4 cách gõ | `python3 -c` gọi `looks_like_approval` với `main`, `subagent`, `inline implement`, `sub-agent` | Cả 4 trả `True` |
| Q5 | Checklist phase `mode` nêu đủ 2 nhãn | `python3 scripts/tdq_state.py next` ở phase `mode` | Output chứa `inline implement` và `sub-agent implement` |
| Q6 | Khuôn hỏi mode và luật phân tích có mặt | `grep -c "inline implement" skills/tdq-plan/SKILL.md` và grep mục luật phân tích | Cả hai > 0 |
| Q7 | Nhãn có ở plan-template và tdq-build | `grep -l "inline implement" skills/tdq-plan/references/plan-template.md skills/tdq-build/SKILL.md` | Liệt kê đủ 2 file |
| Q8 | Log service còn nguyên | Gọi `_warn` với `TDQ_LOG` mặc định và `TDQ_LOG=0` | Mặc định có dòng timestamp, `TDQ_LOG=0` không dòng nào |
| Q9 | Suite đầy đủ xanh | `python3 -m pytest tests/ -q` | `0 failed`, số test ≥ 536 |
| Q10 | Tài liệu qua lint | `python3 scripts/doc_lint.py <các file .md đã sửa>` | exit 0 |

DoD: đủ 8 đầu ra ở §2, cả 10 hạng mục QC PASS kèm output thật, không còn chỗ nào in ra
chữ `main`/`subagent` trần cho user ở cổng mode.

## 7. Câu hỏi còn mở

(rỗng)
