# BÁO CÁO — Đổi tên mode thực thi + phân tích lý do đề xuất

Ngày: 2026-08-14 · Lane: full · Mode: main (làm trực tiếp) · Plan: 13 task, tất cả `[x]`.

## Đã làm

- Mode tách hai lớp y như lane: `MODE_LABELS` / `MODE_ALIASES` + `mode_label()` /
  `normalize_mode()` trong `scripts/tdq_state.py`. Định danh máy vẫn là `main`/`subagent`
  nên state cũ, plan cũ và `--mode` cũ không phải migrate.
- Nhãn user đọc thấy: `main` → "làm trực tiếp (inline implement)", `subagent` → "giao trợ
  lý (sub-agent implement)". Đầu vào nhận cả tên cũ, tên mới và biến thể có "implement".
- Cổng mode giờ bắt buộc kèm đoạn **"Vì sao đề xuất"** 1–3 dòng, phải nêu đủ 4 căn cứ đọc
  từ chính plan (số task, chuỗi phụ thuộc, số file bị nhiều task cùng đụng, có nhãn
  `(mcp)` không) và một câu vì sao không chọn phương án còn lại.
- Khuôn nguyên văn + luật viết đoạn lý do dời sang `skills/tdq-plan/references/mode-gate.md`
  (SKILL.md có trần 100 dòng); nhãn mới cũng vào `plan-template.md` và `tdq-build/SKILL.md`.
- Hook đồng bộ: `_common.py` in nhãn thay vì định danh máy, `prompt_context.py` nhận nhãn
  mới, `edit_gate.py` gợi ý cả hai tên.

## Kết quả kiểm

- 10 hạng mục DoD: 9 PASS ngay, Q4 FAIL vòng 1 rồi PASS sau fix. Chi tiết + bằng chứng:
  `docs/tdq/qc/2026-08-14-doi-ten-mode-implement.md`.
- `python3 -m pytest tests/ -q` → 552 passed, 235 subtests. `doc_lint.py` exit 0 trên mọi
  file `.md` đã sửa.

## Đáng chú ý

- QC bắt được một lỗ do chính bản đổi tên gây ra: khuôn mới mời user nhắn "A"/"B" nhưng
  hook chỉ nhận tên mode, nên câu trả lời "A" bị coi là mơ hồ. Đã thêm `LETTER` +
  `mode_from_answer()`: A = mode plan đề xuất, B = mode còn lại; nhánh duyệt plan vẫn chỉ
  đọc tên mode (chữ "A" trong câu duyệt plan không mang nghĩa mode).
- `test_gate_merge.py::test_plan_skill_has_the_mode_gate` phải sửa theo: nghĩa của hai
  mode giờ gắn với nhãn hiển thị, không gắn với định danh máy.
- Không có commit gỡ chặn nào trong lượt build này.
