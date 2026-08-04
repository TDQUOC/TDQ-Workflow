# Khuôn AGENTS.md cho worktree external

Orchestrator chép NGUYÊN VĂN khối fence dưới đây thành file `AGENTS.md` ở ROOT
worktree `tdq-ext-<slug>` TRƯỚC khi gọi runner lần đầu. Codex tự nạp qua `--cd`;
agy tự parse ở workspace root — không cần cấu hình thêm.

BẮT BUỘC: xóa `AGENTS.md` khỏi worktree TRƯỚC bước diff-check/merge — file này
không được lọt vào diff merge về repo.

```markdown
# AGENTS — luật làm việc trong worktree này

## Quy trình mỗi task
- Làm đúng thứ tự task trong gói. Không bỏ task, không gộp task.
- Mỗi task theo red → green: chạy lệnh test của task TRƯỚC (phải fail),
  code xong chạy lại đến khi pass.
- Chỉ sửa file nêu trong task. Không sửa file ngoài phạm vi gói.
- Không placeholder, không TODO — thiếu thông tin thì ghi vào notes của report.

## Test
- Chạy test từ thư mục `tests/`: `cd tests && python3 -m unittest <module> -v`.
- Không dùng pytest. Không sửa test có sẵn trừ khi task yêu cầu rõ.
- Ghi nguyên văn output test vào `test_result` của report — cấm ghi "OK" suông
  khi chưa chạy.

## Cấm
- KHÔNG commit, KHÔNG push, KHÔNG tạo branch — orchestrator lo git.
- KHÔNG cài package mới, KHÔNG sửa file ngoài worktree này.
- KHÔNG sửa `docs/tdq/state.json` hay chạy `tdq_state.py`.
- KHÔNG phát khóa `fallback` trong report.

## Report (bắt buộc, output cuối cùng)
- In DUY NHẤT một JSON đúng schema, không kèm văn xuôi ngoài JSON:

  {
    "kind": "plan",
    "status": "done",
    "tasks": [
      {"task_id": "T1", "status": "done", "files_changed": ["a.py"],
       "test_cmd": "python3 -m unittest tests.test_a", "test_result": "OK",
       "notes": ""}
    ],
    "notes": ""
  }

- Mỗi task trong gói = một phần tử trong `tasks`, `test_result` không rỗng.
- Task bị chặn → `status: "blocked"` + lý do trong `notes`, vẫn báo đủ task.
```
