# tdq-workflow — Plugin Claude Code

Workflow spec-driven giúp Claude làm đúng ngay từ lần implement đầu: phân tích kỹ, interview đến khi rõ, spec/plan tiếng Việt phải được **bạn duyệt** trước khi Claude được sửa code, QC lặp đến khi pass, report ≤ 50 dòng.

## Pipeline

```
Intake ──► Analysis ──► Spec ──► Plan ──► Implement ──► QC ──► Report
 (lane?)   (interview)  [DUYỆT]  [DUYỆT]  (1 turn,      (loop   (≤50 dòng)
                                           tick ngay)    plan)
Lane quick: Analysis ngắn ──► Plan ≤10 dòng trong chat ──► [DUYỆT] ──► ghi log ──► Implement
```

- **Gate cứng bằng hook**: chưa duyệt spec/plan (hoặc quick) thì mọi Edit/Write ngoài `docs/` bị chặn — kèm nhắc Claude tiếp tục hoàn thiện spec/plan và hướng dẫn bạn lệnh duyệt.
- **Chỉ bạn duyệt được**: duyệt bằng cách tự gõ `/tdq-workflow:tdq-approve spec|plan|quick`. Claude không thể tự gọi lệnh này; state (`docs/tdq/state.json`) được 3 lớp hook + CLI bảo vệ chống ghi trực tiếp.
- **Chống trôi spec**: duyệt xong lưu sha256 — spec đổi sau duyệt sẽ bị cảnh báo.
- **Working log bắt buộc**: turn nào có thay đổi repo mà chưa append `docs/workinglog/<ngày>.md` sẽ bị chặn kết thúc turn.

## Cài đặt (chỉ trong repo/project)

```bash
claude --plugin-dir /đường/dẫn/tới/TDQWorkflow
```
Plugin không tự cài user-level. Muốn dùng mọi nơi: xem `docs/notes/user-level-install.md`.

**Bật workflow cho MỌI task**: hook chỉ enforce gate — để Claude chủ động đi đúng pipeline từ lúc nhận yêu cầu, dán block instruction trong `docs/notes/user-level-install.md` (mục 3) vào `~/.claude/CLAUDE.md` (user-level) hoặc `CLAUDE.md` root project (per-project). Block đã viết khớp với hook: lệnh duyệt, đường log `docs/workinglog/`, tick ngay khi task xong, graphify update cuối turn.

## Dùng hằng ngày

1. Nêu yêu cầu → Claude dùng `tdq-start`: tóm tắt, đề xuất lane **quick** (việc nhỏ, rõ) hay **full** (feature/phức tạp) và hỏi bạn chọn.
2. Lane full: Claude interview đến khi hết mơ hồ → viết spec (VI) → bạn gõ `/tdq-workflow:tdq-approve spec` → plan (VI, task nào cũng có test) → `/tdq-workflow:tdq-approve plan` → implement end-to-end 1 turn, tick `[x]` ngay khi từng task pass → QC loop → report.
3. Lane quick: plan ≤ 10 dòng trong chat → `/tdq-workflow:tdq-approve quick` → Claude ghi log rồi mới implement.
4. Xem trạng thái bất kỳ lúc nào: `/tdq-workflow:tdq-status`.

## Cấu trúc

| Thư mục | Vai trò |
|---|---|
| `skills/` (10) | tdq-start, analyze, spec, plan, implement, qc, report, approve, status, conventions |
| `agents/` (3) | tdq-reviewer, tdq-implementer, tdq-qc-tester |
| `hooks/` (6) | approve_gate, edit_gate, bash_gate, session_start, prompt_context, stop_gate |
| `scripts/tdq_state.py` | CLI đọc/ghi state an toàn (khóa các field duyệt) |
| `tests/` | 49 test (unit + e2e chain) — `python3 -m unittest discover tests` |

Doc sinh ra trong project của bạn: `docs/tdq/{requests,questions,research,knowledge,spec,plan,qc,reports}/` + `docs/workinglog/`.

## Quy ước cứng
- Spec/plan/report: tiếng Việt. Không placeholder, không bịa — thiếu thông tin thì hỏi.
- Sản phẩm build ra luôn bật sẵn logging service (timestamp, đủ debug) + unit test từng phần.
- Tên branch/commit không bắt đầu bằng `claude|antigravity|gemini|codex`; commit message không chứa dấu vết AI; chỉ commit khi bạn yêu cầu.
- Web search: `tavily-primary` trước, backup chỉ khi lỗi, có ghi nguồn.
