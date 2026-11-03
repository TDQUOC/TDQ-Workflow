# TASK E2E-CODEX

Mục tiêu: viết hàm `add(a, b)` trả về `a + b` trong scripts/samples/e2e_codex.py và unit test cho nó trong tests/test_e2e_codex.py.

File:
- scripts/samples/e2e_codex.py
- tests/test_e2e_codex.py

Test: python3 -m unittest tests.test_e2e_codex

Ràng buộc:
- CHỈ tạo/sửa các file trong mục File. Không đụng file khác, không đụng path ngoài worktree hiện tại.
- Dòng import trong file test PHẢI là: `from scripts.samples.e2e_codex import add`. Lệnh Test chạy từ root của worktree.
- KHÔNG commit, không đổi branch, không chạy lệnh git ghi (git add/commit/push).
- Chạy lệnh ở mục Test đến khi pass rồi mới trả lời.
- Trả lời cuối cùng = DUY NHẤT một JSON đúng schema report như mẫu dưới, không kèm văn xuôi.

Report mẫu (thay giá trị thật của bạn):

```json
{
  "task_id": "E2E-CODEX",
  "status": "done",
  "files_changed": ["scripts/samples/e2e_codex.py", "tests/test_e2e_codex.py"],
  "test_cmd": "python3 -m unittest tests.test_e2e_codex",
  "test_result": "Ran 2 tests in 0.001s OK",
  "notes": ""
}
```
