# tdq-workflow — Plugin Claude Code

Workflow spec-driven giúp agent làm đúng ngay từ lần implement đầu: phân tích kỹ, interview đến khi rõ, spec/plan tiếng Việt phải được **bạn duyệt** trước khi agent được sửa code, QC lặp đến khi pass, report ≤ 50 dòng.

Từ 0.3.0, bộ instruction được viết lại theo hướng **bước đánh số + mốc "Xong khi:" + con trỏ "Bước kế tiếp:"**, để cả model nhỏ chạy local cũng đi đúng workflow, không phải đoán.

## Pipeline

```
Intake ──► Analysis ──► Spec ──► Plan ──► Implement ──► QC ──► Report
 (lane?)   (interview)  [DUYỆT]  [DUYỆT]  (1 turn,      (loop   (≤50 dòng)
                                           tick ngay)    plan)
Lane quick: Analysis ngắn ──► Plan ≤10 dòng trong chat ──► [DUYỆT] ──► ghi log ──► Implement
```

## Cách hook điều khiển agent

Hook **nhắc, không chặn tool**. Mỗi lời nhắc là một dòng mã đóng:

| Mã | Khi nào xuất hiện |
|---|---|
| `TDQ:NEXT` | đầu session / đầu mỗi turn — phase hiện tại + việc kế tiếp |
| `TDQ:APPROVE` | sửa file ngoài `docs/` khi spec/plan/quick chưa được ghi nhận duyệt |
| `TDQ:LOG` | turn có thay đổi repo mà chưa append `docs/workinglog/<ngày>.md` |
| `TDQ:STATE` | định ghi thẳng `docs/tdq/state.json` thay vì dùng CLI |
| `TDQ:GIT` | lệnh git commit/push/branch — kiểm quy ước tên và message |

Instruction bắt agent: thấy `[TDQ:<MÃ>]` → làm việc trong đó TRƯỚC, xong in `✓ [TDQ:<MÃ>]`.

**Verify-by-effect**: hook không tin lời agent. Mỗi turn ghi một sổ tạm (`docs/tdq/.tdq-turn.jsonl`) gồm dòng `remind` (hook đã nhắc mã nào) và dòng `observe` (hiệu ứng thật: đã sửa file gì, đã ghi log chưa, đã gọi CLI state chưa). Hook `Stop` đối chiếu hai bên — agent in `✓` mà không có hiệu ứng thật thì vẫn bị bắt. Điểm **chặn** duy nhất còn lại là working log.

Từ 0.3.1, hook còn **nhìn thẳng vào đĩa**: đầu turn chụp `sha256` của working log hôm nay cùng vân tay `git status` + `git diff HEAD`, cuối turn so lại. Nhờ vậy cách ghi không còn quan trọng — append log bằng `cat >>`/`tee`/`sed -i` vẫn được công nhận, và sửa repo hoàn toàn bằng shell vẫn bị đòi ghi log. Project không phải git repo thì rơi về đối chiếu bằng sổ turn như cũ.

## Duyệt bằng chat thường

Nhắn "duyệt spec", "ok plan mode main", "duyệt quick" — không cần cú pháp lệnh. Agent ghi nhận vào state kèm **nguyên văn** câu bạn nói (`spec_approved_by` / `plan_approved_by` / `quick_approved_by`) để còn đối chiếu. Câu mơ hồ ("ok", "spec ok chưa?") KHÔNG được tính là duyệt — agent phải hỏi lại. Duyệt xong lưu sha256 của spec; spec đổi sau khi duyệt sẽ bị cảnh báo.

## Cài đặt (chỉ trong repo/project)

```bash
claude --plugin-dir /đường/dẫn/tới/TDQWorkflow
```
Plugin không tự cài user-level. Muốn dùng mọi nơi: xem `docs/notes/user-level-install.md`.

**Bật workflow cho MỌI task**: dán block instruction trong `docs/notes/user-level-install.md` (mục 3) vào `~/.claude/CLAUDE.md` (user-level) hoặc `CLAUDE.md` root project (per-project).


## Dùng hằng ngày

1. Nêu yêu cầu → agent dùng `tdq-intake`: tóm tắt, đề xuất lane **quick** (việc nhỏ, rõ) hay **full** (feature/phức tạp) và hỏi bạn chọn.
2. Lane full: interview đến khi hết mơ hồ → spec (VI) → bạn nhắn "duyệt spec" → plan (VI, task nào cũng có test).
   Agent đề xuất mode thực thi, bạn nhắn "duyệt plan mode main" (hoặc `subagent`).
   Rồi implement end-to-end 1 turn, tick `[x]` ngay khi từng task pass → QC loop → report.
3. Lane quick: plan ≤ 10 dòng trong chat → bạn nhắn "duyệt quick" → agent ghi log rồi mới implement.
4. Xem trạng thái bất kỳ lúc nào: skill `tdq-status`, hoặc `python3 scripts/tdq_state.py next`.

## Cấu trúc

| Thư mục | Vai trò |
|---|---|
| `skills/` (6) | tdq-intake, tdq-spec, tdq-plan, tdq-build, tdq-status, tdq-conventions |
| `agents/` (3) | tdq-reviewer, tdq-implementer, tdq-qc-tester |
| `hooks/` (5) | edit_gate, bash_gate (nhắc), session_start, prompt_context, stop_gate (chặn working log) |
| `scripts/tdq_state.py` | CLI state: `next \| get \| init \| set \| approve \| reset \| phases-doc` |
| `docs/claude-md-mau.md` | bản mẫu để chép sang `~/.claude/CLAUDE.md` |
| `tests/` | `python3 -m unittest discover tests` |

Bảng phase (nguồn duy nhất là hằng `PHASE_TABLE` trong `scripts/tdq_state.py`) được **sinh tự động** ra `skills/tdq-conventions/references/phases.md` bằng `python3 scripts/tdq_state.py phases-doc` — không sửa tay.

Doc sinh ra trong project của bạn: `docs/tdq/{brief,research,spec,plan,qc,reports}/` + `docs/workinglog/`. `brief/` gộp yêu cầu + kiến thức + hỏi đáp vào một file.

## Quy ước cứng
- Spec/plan/report: tiếng Việt. Không placeholder, không bịa — thiếu thông tin thì hỏi.
- Ghi state CHỈ bằng `scripts/tdq_state.py`, không sửa tay `state.json`.
- Sản phẩm build ra luôn bật sẵn logging service (timestamp, đủ debug) + unit test từng phần.
- Tên branch/commit không bắt đầu bằng `claude|antigravity|gemini|codex`; commit message không chứa dấu vết AI; chỉ commit khi bạn yêu cầu.
- Web search: `tavily-primary` trước, backup chỉ khi lỗi, có ghi nguồn.
