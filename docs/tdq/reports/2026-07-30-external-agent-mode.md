# REPORT — Mode implement "external" (Codex/Antigravity qua worktree)

Ngày: 2026-07-30 · Spec: ../spec/2026-07-30-external-agent-mode.md (v1.1) ·
Plan: ../plan/2026-07-30-external-agent-mode.md (17 task, mode main) ·
QC: ../qc/2026-07-30-external-agent-mode.md

## Kết quả

- Mode thực thi thứ 3 `external`: user duyệt plan/quick kèm mode external →
  orchestrator tạo worktree `tdq-ext-<slug>`, giao TỪNG task cho Codex CLI hoặc
  Antigravity CLI (agy) headless, verify bằng chạy lại test thật, tick, merge.
- Lõi script (model thấp vẫn chạy đúng — mọi logic dễ hỏng nằm trong script):
  - `scripts/external_task.py`: run (retry ≤2 kèm lỗi cũ, timeout, validate JSON
    schema, chặn engine tự phát `fallback`) + parse-plan (dòng máy-đọc engine/model).
  - `scripts/external_report_schema.json`: report 6 khóa bắt buộc.
  - `scripts/external_models.py`: list model THẬT (agy models / probe codex, cache 7d).
- Model policy theo yêu cầu: user đưa 1–3 tên theo list thật → khó/TB/dễ; luật độ
  khó ghi cứng trong tdq-plan.
- Agents `codex-runner`/`agy-runner` (vỏ mỏng); skill tdq-plan/build/intake/conventions
  + hooks + tdq_state.py + doc portable + CLAUDE.md §10 đều nhận đủ 3 mode.
- Log service mặc định: `docs/tdq/external/<slug>/run.log` (ISO timestamp,
  `TDQ_EXTERNAL_LOG=0` tắt, `TDQ_EXTERNAL_TIMEOUT` chỉnh).

## QC (chi tiết trong file QC)

- Q1–Q8 PASS: suite 285 test OK; doc_lint + --pair exit 0; E2E thật 2 engine.
- Q9 PENDING: cài plugin codex cần user gõ 4 lệnh slash (đã hướng dẫn trong chat).
- E2E codex: engine tự viết code + test trong worktree, report hợp lệ, verify OK.
- E2E agy: phát hiện giới hạn thật — agy 1.1.8 headless `-p` KHÔNG sửa được file,
  report "done" là bịa → verify bắt được, đi đúng đường fallback (Claude tự làm,
  report kèm `"fallback": "claude"`). Cảnh báo đã ghi vào tdq-plan.

## Việc user cần làm

1. Cài plugin codex (4 lệnh slash — xem chat).
2. Quyết định commit (Claude không tự commit).

## Đề xuất tiếp

- Theo dõi bản agy mới; khi headless sửa được file thì gỡ cảnh báo trong tdq-plan.
- Request dọn CLAUDE.md §5 (câu spec/plan cho codex/antigravity cũ, chồng khái niệm
  với mode external §10).
