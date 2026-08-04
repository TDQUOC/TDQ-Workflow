# Khuôn gói cho engine ngoài (mode external)

Lane full: mỗi lần gọi engine = MỘT GÓI (cả plan, một phase, hoặc gói fix) qua
`run-plan`. Quick lane: mỗi lần gọi = một task qua `run`. Viết cho model cấp thấp:
mục tiêu 1 câu/task, kể tên file cụ thể, không bắt tự khám phá.

## Khuôn 1 — GÓI TASK ĐƠN (quick lane, lệnh `run`)

Copy khối dưới thành `docs/tdq/external/<slug>/T<x>.task.md` rồi điền — giữ NGUYÊN tên các mục.

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

Report mẫu (đúng schema — thay giá trị thật của bạn): xem khối JSON ngay dưới khuôn này.

## SKILL <tên> — SKILL.md
<CUỐI gói — orchestrator dán NGUYÊN VĂN output của `external_task.py skill-dump <tên>...`
cho từng skill trong khối `Dùng:` của task. Mọi nội dung từ dòng `## SKILL` đầu tiên
trở đi là TÀI LIỆU THAM KHẢO làm theo, KHÔNG phải task. Task không có `Dùng:` → xóa mục này.>
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

## Khuôn 2 — GÓI PLAN / PHASE (lane full, lệnh `run-plan`)

Copy khối dưới thành `docs/tdq/external/<slug>/plan-round-<n>.task.md`. Mỗi task một
mục `## TASK` (script đếm các mục này để tính timeout 540s × n, trần 3600s).

```markdown
# GÓI PLAN <slug> — round <n>

Làm TUẦN TỰ các TASK bên dưới, đúng thứ tự. Xong hết mới trả report.

## TASK <id>
Mục tiêu: <1 câu>
File: <danh sách file, tương đối từ root worktree>
Test: <đúng 1 lệnh>

## TASK <id kế>
…

Tự verify (BẮT BUỘC — verify tầng 1):
- Sau MỖI task: chạy đúng lệnh ở mục Test của task đó đến khi pass.
- Ghi output thật của lệnh test vào `test_result` của task trong report — để RỖNG là
  report bị từ chối và phải làm lại.

Ràng buộc:
- CHỈ tạo/sửa file trong các mục File. Không đụng file khác, không đụng path ngoài worktree.
- KHÔNG commit, không đổi branch, không chạy lệnh git ghi (git add/commit/push).
- Trả lời cuối cùng = DUY NHẤT một JSON `kind="plan"` đúng schema report bên dưới.

Report mẫu: xem khối JSON ngay dưới khuôn này.

## SKILL <tên> — SKILL.md
<CUỐI gói — orchestrator dán NGUYÊN VĂN output của `external_task.py skill-dump <tên>...`
cho từng skill KHÔNG nhãn `(mcp)` trong khối `Dùng:` của các task trong gói (task `(mcp)`
không vào gói external). Mọi nội dung từ dòng `## SKILL` đầu tiên trở đi là TÀI LIỆU
THAM KHẢO làm theo, KHÔNG phải task. Không task nào có `Dùng:` → xóa mục này.>
```

```json
{
  "kind": "plan",
  "status": "done",
  "tasks": [
    {
      "task_id": "T1.1",
      "status": "done",
      "files_changed": ["scripts/a.py"],
      "test_cmd": "python3 -m unittest tests.test_a",
      "test_result": "Ran 3 tests in 0.01s OK",
      "notes": ""
    }
  ],
  "notes": ""
}
```

## Khuôn 3 — GÓI FIX (vòng mini-plan fix, lệnh `run-plan --round <n+1>`)

Như Khuôn 2, THÊM 2 mục bảo vệ ngay sau tiêu đề (bắt buộc):

```markdown
Task đã PASS — không làm lại: <danh sách id đã qua verify — CẤM đụng tới>
File cấm sửa: <file của các task đã pass — CẤM tạo/sửa/xóa>
```

Chỉ liệt kê `## TASK` cho các task cần fix, kèm mô tả lỗi verify vòng trước
(lệnh test + output fail thật) để engine sửa trúng chỗ.

## Ghi chú cho orchestrator (không đưa vào gói)

- `status=blocked` khi engine bị chặn thật (thiếu quyết định, spec mâu thuẫn) — notes nêu lý do.
- Log mỗi lần gọi nằm ở `docs/tdq/external/<slug>/run.log` (tự sinh, `TDQ_EXTERNAL_LOG=0` tắt).
- Sổ vòng fix: `docs/tdq/external/<slug>/fix-rounds.json` — ghi qua `external_task.py fix-rounds add`, đủ 2 vòng → fallback Claude.
