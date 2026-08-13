# Brief — Siết luật tick checkbox cho lane quick

Ngày: 2026-08-12

## Nguyên văn

> hi tôi đang muốn bạn check giúp tôi ở lane quick tôi đang nghi vấn có vấn đề là task
> ko đc tick ngay khi xong, nghĩa là ban đầu trống hay có cảm giác là khi mà xong all
> task claude mới tick vào hãy check và phân tích và báo cáo cho tôi hiện trạng của nó

Sau báo cáo hiện trạng, user chốt phương án **C** = làm cả A và B:

- A: bổ sung dấu `[~]` vào checklist phase `quick` (`scripts/tdq_state.py`) và khuôn
  mini-plan trong `skills/tdq-intake/references/quick-lane.md`, cho khớp hook đang có.
- B: `hooks/scripts/edit_gate.py` chuyển `TDQ:TICK` từ *nhắc* sang *chặn* khi
  phase ∈ (implement, qc) và đang sửa file ngoài `docs/`.

### Cách hiểu đầu tiên

- Mục tiêu: ba lớp (skill quick, bảng phase, hook) nói cùng một luật tick; và luật đó
  được ép bằng hook chứ không chỉ khuyên.
- Phạm vi đoán: `scripts/tdq_state.py` (PHASE_TABLE["quick"]), `skills/tdq-intake/
  references/quick-lane.md`, `skills/tdq-intake/SKILL.md` (Phần C bước 7),
  `hooks/scripts/edit_gate.py`, `tests/test_edit_gate.py`.
- Chỗ chưa rõ: điều kiện chặn của B — chặn ngay lần sửa code đầu tiên hay chỉ chặn khi
  plan tồn tại và có task; và có nới cho file test hay không.

## Hiểu & kiến thức

(để trống — lane quick không dùng mục này)

## Hỏi đáp

(để trống — lane quick không dùng mục này)
