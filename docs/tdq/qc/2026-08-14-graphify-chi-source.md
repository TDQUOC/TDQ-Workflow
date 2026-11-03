# QC — Tổ chức graphify: chỉ scan source, đọc có chủ đích

Ngày: 2026-08-14 · Plan: ../plan/2026-08-14-graphify-chi-source.md · Kết quả: 9/9 PASS

| # | Hạng mục | Lệnh | Output thật | Kết quả |
|---|---|---|---|---|
| Q1 | `.graphifyignore` đủ 8 thư mục | `grep -c '/$' .graphifyignore` | `8` | PASS |
| Q2 | Hook không còn gọi qua thuộc tính module | `grep -n 'tdq_state\.' hooks/scripts/*.py \| grep -v 'tdq_state\.py' \| wc -l` | `0` | PASS |
| Q3 | Suite đầy đủ xanh | `python3 -m pytest tests/ -q` | `536 passed, 206 subtests passed in 32.19s` | PASS |
| Q4 | Hook chạy thật không lỗi import | `echo '{}' \| python3 hooks/scripts/prompt_context.py; echo $?` | `0` | PASS |
| Q5 | Đồ thị thấy chuỗi hook → tdq_state | `graphify affected "turn_snapshot()"` | `- main() [calls] hooks/scripts/prompt_context.py:L75` | PASS |
| Q6 | Cạnh cross-file `hooks/* → tdq_state.py` | đếm trong `graph.json` | `38` (trước: 1) — `_common` 7 · `edit_gate` 7 · `prompt_context` 12 · `session_start` 3 · `stop_gate` 9 | PASS |
| Q7 | `graphify-out` ngoài pathspec | `git diff HEAD --name-only -- <các exclude> \| grep -c graphify-out` | `0`; `pytest tests/test_turn_snapshot.py -q` → `24 passed` | PASS |
| Q8 | Luật ĐỌC có mặt | `grep -c graphify <2 file reference>` | `analyze-full.md:3` · `quick-lane.md:2` | PASS |
| Q9 | Tài liệu qua lint | `python3 scripts/doc_lint.py <4 file .md>` | exit `0` | PASS |

## Kiểm thêm ngoài DoD

- Log service còn nguyên sau khi đổi lối import: `stop_gate._warn(...)` in
  `[2026-08-14T00:25:06+07:00] ⚠️ ...` ra stderr; `TDQ_LOG=0` → 0 dòng.
- Test đỏ trước khi sửa (bằng chứng red→green):
  `test_main_reads_turn_log_once` đỏ `AssertionError: 0 != 1`,
  `test_digest_ignores_graphify_out` đỏ trước khi thêm `"graphify-out"`.

## Hai phép đo đã chỉnh so với spec bản 1.0

Chỉ chỉnh CÁCH ĐO, không đổi điều kiện pass thực chất; đã sửa cả spec lẫn plan.

1. Q2 cũ đếm `grep -c 'tdq_state\.'` = 0. Không đạt được vì `prompt_context.py`,
   `stop_gate.py`, `edit_gate.py` in cho user chuỗi lệnh `tdq_state.py approve|set` —
   là chuỗi hiển thị, không phải lời gọi. Phép đo mới loại các dòng chứa `tdq_state.py`.
2. Q7 cũ đòi `git diff HEAD` sau loại trừ = 0 byte. Chỉ đúng khi cây làm việc sạch;
   turn này có thay đổi mã thật nên luôn khác 0. Phép đo mới hỏi đúng câu cần hỏi:
   không đường dẫn `graphify-out` nào lọt vào diff, cộng unit test mới.
