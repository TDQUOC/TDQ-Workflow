# Khuôn gói task cho engine ngoài (mode external)

Mỗi lần gọi engine = MỘT task. Copy khối dưới thành file tạm (vd
`docs/tdq/external/<slug>/T<x>.task.md`) rồi điền — giữ NGUYÊN tên các mục.
Viết cho model cấp thấp: mục tiêu 1 câu, kể tên file cụ thể, không bắt tự khám phá.

```markdown
# TASK <id — trùng id trong plan, vd T2.1>

Mục tiêu: <đúng 1 câu, 1 việc — vd: viết hàm add(a, b) trong scripts/samples/e2e_codex.py và unit test cho nó>

File: <danh sách file được tạo/sửa — đường dẫn TƯƠNG ĐỐI từ root worktree, mỗi dòng một file>
- scripts/samples/e2e_codex.py
- tests/test_e2e_codex.py

Test: <đúng 1 lệnh chạy từ root worktree — vd: python3 -m unittest tests.test_e2e_codex>

Ràng buộc:
- CHỈ tạo/sửa các file trong mục File. Không đụng file khác, không đụng path ngoài worktree.
- KHÔNG commit, không đổi branch, không chạy lệnh git ghi (git add/commit/push).
- Chạy lệnh ở mục Test đến khi pass rồi mới trả lời.
- Trả lời cuối cùng = DUY NHẤT một JSON đúng schema report bên dưới, không kèm văn xuôi.

Report mẫu (đúng schema — thay giá trị thật của bạn):
```

```json
{
  "task_id": "T2.1",
  "status": "done",
  "files_changed": ["scripts/samples/e2e_codex.py", "tests/test_e2e_codex.py"],
  "test_cmd": "python3 -m unittest tests.test_e2e_codex",
  "test_result": "Ran 2 tests in 0.001s OK",
  "notes": ""
}
```

Ghi chú cho orchestrator (không đưa vào gói task):
- `status=blocked` khi engine bị chặn thật (thiếu quyết định, spec mâu thuẫn) — notes nêu lý do.
- Log mỗi lần gọi nằm ở `docs/tdq/external/<slug>/run.log` (tự sinh, `TDQ_EXTERNAL_LOG=0` tắt).
