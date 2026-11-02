# Yêu cầu — Tích hợp Ultracode vào TDQ Workflow
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## Nguyên văn

> okay vậy tôi muốn bạn mở request apply ultracode vào tdq-workflow nhưng ko cần set trần token

User yêu cầu mở request tích hợp cơ chế Ultracode (Workflow Engine đa tác tử) vào TDQ-Workflow, với yêu cầu đặc thù: **không cần set trần token** (không giới hạn budget ceiling để phục vụ vét cạn tối đa theo triết lý chất lượng).

### Phân tích ban đầu:
- **Mục tiêu**: Xây dựng cơ chế tích hợp Ultracode vào TDQ-Workflow; cho phép kích hoạt kịch bản Workflow đa tác tử tại các trạm phù hợp (Analyze đa chiều, Stress-test QC) mà không bị giới hạn cứng bởi trần token budget.
- **Phạm vi dự kiến**:
  - `skills/tdq-conventions/`: Bổ sung quy chế điều phối Ultracode song song với TDQ state machine; định nghĩa ngoại lệ ngân sách token khi người dùng chỉ định thả nổi trần.
  - `scripts/`: Nghiên cứu bổ sung template kịch bản JavaScript hoặc công cụ cầu nối phục vụ chạy multi-agent an toàn trong TDQ.
  - `skills/tdq-intake/`, `skills/tdq-build/`: Cập nhật hướng dẫn cho phase analyze và phase qc khi phát hiện keyword hoặc cấu hình ultracode.
  - `tests/`: Bộ kiểm chứng tự động cho các luật điều phối và ranh giới an toàn (bảo toàn State machine và Git safety).
- **Điểm cần làm rõ**:
  - Tích hợp dưới dạng cờ CLI (`--ultracode`), cấu hình state hay kích hoạt tự động theo keyword prompt?
  - Cơ chế cảnh báo hoặc giám sát khi chạy không trần token để tránh treo tiến trình vĩnh viễn?

## Hiểu & kiến thức

Pipeline `full` đã chọn bằng `1a`. Nhánh `feat/tich-hop-ultracode`, gốc `dev`, phase `analyze`. Request mở qua `--bo-qua-lsp` vì việc chính là luật orchestration/Workflow và bậc 8 Python chưa có bằng chứng module trong lượt init.

### Năng lực dùng được

| Năng lực | Nguồn | Phán quyết | Vai trò |
|---|---|---|---|
| `Workflow` + `workflow-authoring` | Claude Code built-in | DÙNG | Khảo sát fan-out, structured output và phản biện; là primitive được tích hợp |
| `tdq-intake`, `tdq-spec`, `tdq-plan`, `tdq-build`, `tdq-conventions` | plugin:tdq-workflow | NỀN | State machine, gate và tài liệu cần cập nhật |
| LSP + Graphify + Grep | MCP/CLI | DÙNG | Đối chiếu symbol, caller và vùng ảnh hưởng |
| `tdq-reviewer`, `tdq-qc-tester` | plugin agents | TÁI DÙNG | Reviewer/QC hiện có; không dựng role trùng |
| `tdq_team.py` / team mode | project | GIỮ NGUYÊN | Owner duy nhất của implement worktree, assignment, merge và cleanup |
| 18 skill còn lại | built-in/plugin | KHÔNG | Khác lĩnh vực |

### Fact đã kiểm

1. Ultracode là policy để Claude Code ưu tiên Dynamic Workflow cho task đủ lớn; không phải model hay effort level riêng. Workflow không thay thế TDQ state machine.
2. `budget.total` là `null` khi user không đặt target. `budget.remaining()` khi đó là `Infinity`; do đó không được dùng vòng lặp chỉ dựa trên budget. User đã chốt **không đặt trần token**, nhưng run vẫn cần tập việc/điều kiện kết thúc hữu hạn.
3. Workflow hỗ trợ `agent`, `pipeline`, `parallel`, structured output, resume và worktree isolation. `pipeline` là mặc định; `parallel` chỉ dùng khi cần barrier toàn tập.
4. TDQ hiện có state thật `idle|analyze|spec|plan|mode|implement|qc|report`; approval, state, tick, Git và worktree thuộc quyền của `tdq_state.py`/`tdq_team.py`.
5. `tdq_state.py` là single writer. Workflow agent không được gọi state CLI, approve, tick, commit, push hoặc merge.
6. Native Workflow worktree và TDQ worktree có ownership/ledger khác nhau. V1 không dùng `isolation: worktree` trong phase implement; `tdq_team.py` vẫn là owner duy nhất.
7. Guard subagent trước implement hiện bảo vệ Edit/Write; Bash/PowerShell và MCP write chưa thành hard fence đầy đủ. Prompt “read-only” không phải hàng rào kỹ thuật hoàn chỉnh.
8. Resume cache không tự biết HEAD, dirty tree, TDQ phase hoặc spec/plan hash. Không được dùng cache cũ nếu snapshot thay đổi.
9. QC hiện chỉ chạy các dòng DoD + QC-F1–F4; tích hợp Ultracode không tự tạo hạng mục QC ngoài contract đã duyệt.
10. Khảo sát lần này dùng 10 agent, 1.080.572 token subagent, 312 tool calls, không agent lỗi. Đây là minh chứng Workflow chạy được, chưa phải bằng chứng nó tốt hơn batch Agent hiện tại.

### Kiến trúc tối thiểu đề xuất (Ponytail)

V1 **không thêm adapter/script/CLI/state key/saved workflow**. Chỉ cập nhật luật tại các reference hiện có:

- Deep `analyze`: nếu user hoặc standing Ultracode đã chọn Workflow và việc đủ lớn, main agent có thể fan-out reader theo danh sách hữu hạn; kết quả đi vào brief hiện có. Nếu Workflow không có/không được phép/chưa cần, fallback sang batch Agent hoặc main agent như hiện tại.
- `spec`: Workflow không tự viết spec; chỉ được reviewer phản biện khi route đã chốt.
- `plan`: không để Workflow tự sinh task; chỉ hỗ trợ kiểm vùng chạm/phụ thuộc khi cần.
- `implement`: V1 không tích hợp Workflow. `tdq_team.py` giữ độc quyền worktree/assignment/merge.
- `qc`: chỉ dùng Workflow như QC độc lập/phản biện đúng DoD đã duyệt; output ghi vào file QC hiện có; không sửa production.
- State/gate/git: main agent TDQ giữ độc quyền. Permission chạy Workflow không đồng nghĩa user duyệt spec/plan/commit/push.
- Token: không đặt `budget.total`; điều kiện dừng là danh sách lane hữu hạn, mỗi lane chạy một lần, retry hẹp khi lỗi schema/runtime. Không loop vô hạn.

### Vùng file chạm dự kiến

| Vùng file | Tác động |
|---|---|
| `skills/tdq-intake/references/analyze-full.md` | Eligibility, fallback, completion accounting cho Workflow tại deep analyze |
| `skills/tdq-build/references/qc.md` | Ranh giới Workflow QC theo DoD; không mở rộng số mục QC |
| `skills/tdq-conventions/references/subagent-tuning.md` hoặc sibling phù hợp | Invariant state/git/read-only/no-token-ceiling/termination hữu hạn |
| `tests/` | Test nhỏ khóa phase boundary, fallback, accounting và cấm Workflow ở implement |

Không chạm `scripts/tdq_state.py`, `scripts/tdq_team.py`, hooks hoặc state schema trong phương án nhỏ nhất.

### Rủi ro chính

- Workflow reader có thể mutation qua shell/MCP nếu chỉ dựa vào prompt.
- Double fan-out nếu TDQ tự route trong khi standing Ultracode đã route.
- Null/error bị `.filter(Boolean)` làm biến mất, tạo coverage thiếu âm thầm.
- Resume cache stale sau thay đổi HEAD/dirty/spec/plan.
- Workflow worktree cạnh tranh ownership với TDQ worktree.
- Route tự động theo ngưỡng chưa đo sẽ lãng phí lớn; cần explicit intent hoặc chứng cứ eval.

### Lộ trình nháp

Analyze hiện tại → phỏng vấn chốt trigger/phạm vi/hàng rào/termination/eval → spec → plan → implement tối thiểu (luật + test) → QC `ultra` → report.

## Hỏi đáp

### Vòng 1 — đã chốt

User trả lời:

> 1A khi chọn lane có nhập thêm _ultracode và B có đề xuất 2 ở analysis có hỗ trợ cả express và deep luôn, deep thì có thể chọn thêm B và C, còn express thì agent auto apply vào phase khi cần (nếu người dùng chọn express_ultracode) 3A+B 4A+B nhưng cho phép ghi vào docs để báo cáo và có hướng dẫn trong promt (nhưng nhớ handle để tránh subagent cũng bị gate duyệt chặn khi máy có superpower hoặc tdq-workflow,.....) 5A 6A 7A

| Quyết định | Đã chốt |
|---|---|
| Trigger/lane | Khi chọn lane, user có thể thêm hậu tố `_ultracode`: `express_ultracode`, `deep_ultracode`, `1a_ultracode`. Hậu tố là policy; state canonical vẫn `quick|full` |
| Express | `express_ultracode` tự áp dụng Workflow ở phase cần thiết; không hỏi route phụ và không thêm gate |
| Deep | Hỗ trợ Workflow ở analyze/QC; user có thể chọn thêm spec review, plan review và implement |
| Host | Claude Code interactive + `claude -p` + Agent SDK |
| Read-only | Agent type/tool envelope chỉ đọc + harden gate; cho phép ghi report riêng dưới `docs/**`; prompt contract phải nói rõ đây là inherited subtask, không mở intake/gate mới |
| Gate plugin khác | Preflight hook/plugin. TDQ không thể override `deny` của Superpowers/managed policy; nếu docs write bị chặn thì agent trả structured output để main agent ghi |
| Token/termination | Không token ceiling; danh sách lane hữu hạn, mỗi lane một lần, retry hẹp; không loop vô hạn |
| Eval | KEEP khi tăng unique verified findings/completeness, không tăng false-positive; token chỉ báo cáo |
| QC | `ultra` |

### Kết quả probe sau vòng 1

- Không thêm `express_ultracode|deep_ultracode` vào `VALID_LANES`; intake bóc suffix trước khi gọi `tdq_state.py init`.
- Không thêm state key trong V1. Policy lưu trong brief/mini-plan/spec; hook và approval không cần đọc policy.
- Express giữ đúng một gate `approve quick`; route Workflow phải xuất hiện trong mini-plan trước gate.
- Deep giữ gate spec/plan hiện tại. Các lựa chọn spec review, plan review, implement là route trong analysis/mode, không phải state phase mới.
- Deep implement không dùng native Workflow worktree. Main agent chạy `tdq_team.py assign/audit/open/check/merge/tick/sweep`; Workflow chỉ điều phối `tdq-implementer` vào TDQ worktree đã cấp, không dùng `isolation: worktree`.
- Report path mỗi agent là duy nhất và request-scoped: `docs/tdq/artifacts/<slug>/<agent-id>.md`; không cho nhiều agent cùng sửa brief/spec/plan.
- Prompt contract bắt buộc: inherited subtask; no intake; no state/approval/Git mutation; no approval question; finite scope; structured result; docs write only to assigned path; no shell file writes.
- Interactive dùng approval flow hiện tại. `claude -p` phải thu lựa chọn trước launch; Agent SDK truyền capability/route với tool envelope cố định. Keyword trong transcript không tự nâng quyền.

### Lộ trình

| Bước/phase | CÓ/BỎ | Vì sao |
|---|---|---|
| Research web/Workflow | CÓ (đã xong) | 15 agent qua hai workflow; nguồn chính thức + khảo sát repo |
| Interview thêm | BỎ | Vòng 1 và probe đã chốt toàn bộ lựa chọn kiến trúc |
| Spec → plan | CÓ | Thay đổi hành vi routing/permission cần contract và test rõ |
| Implement | CÓ | Luật routing, prompt contract, harden gate và regression |
| QC độc lập | CÓ | User chọn `ultra`; cần runtime probe Workflow/hook/host |

Luồng tính năng:
1. Intake nhận lane có `_ultracode`, canonical hóa trước state init.
2. Express tự route Workflow hữu hạn và ghi route vào mini-plan.
3. Deep cho user chọn route analyze/spec review/plan review/implement/QC; TDQ giữ gate/state/Git.
4. Workflow agent read-only source, ghi report duy nhất dưới docs hoặc fallback structured output.
5. Eval quality quyết định KEEP/DROP; không đặt token ceiling.
