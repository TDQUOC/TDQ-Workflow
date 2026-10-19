# Checking a spec before presenting it

Split out of `spec-template.md` on 2026-10-02 (954 tokens). The three sections below are SELF-CHECK
work, done once at the end of phase `spec`. None of it is copied into the spec, so none of it has
to sit in context while the spec is written.

## §6 holds the CONDITION, never the check command

The spec is sealed with a sha256 when the user approves it, while **a concrete check
command is only correct AFTER the code exists** — test file name, selection flag, function
name. Write those into the spec and a wrong name found at QC time forces a re-approval,
even though the intent did not change by a single word. Measured in 2 of 7 cases in
`docs/tdq/reports/2026-08-18-2050-spec-doi-sau-khi-duyet.md`.

So: **the spec carries the PASS CONDITION, the plan carries the CHECK COMMAND.** The plan
is not sealed, so renaming a test file there is everyday work and touches no approval gate.

| Written in the spec (RIGHT) | Written in the spec (WRONG — move it to the plan) |
|---|---|
| editing a bookkeeping line leaves the sha alone, editing a numbered section changes it | `pytest tests/test_state.py -q -k sha` green |
| a new spec carrying a check command is blocked by the linter, an old spec still passes | `pytest tests/test_doc_lint.py -q -k r11` green |

Rule **R11** of `doc_lint.py` guards exactly this, and applies only to specs from
2026-08-19 onward.

## Measure every numeric threshold BEFORE approval

A §6 row whose PASS condition holds a numeric threshold (a comparator with a number other than
0/1, or a number with a unit: MB, %, ms, giây, token, dòng…) must fill two more cells. Rule **R14**
of `doc_lint.py` checks it on specs from `2026-10-03-0732` on, and `approve spec` refuses while R14
is red (the user alone may pass `--bo-qua-do "<reason>"`).

- **Đo trước** — a real measurement beats an estimate; an estimate names its source (vendor size, <!-- i18n-allow: canonical spec column name -->
  a quick run, a sibling project) and the margin left to the threshold. It must hold a number.
- **Dự phòng nếu trượt** — the option picked NOW in case the measurement misses. At implement <!-- i18n-allow: canonical spec column name -->
  time that cell is applied and recorded with `lech add`; the run does not stop to ask.

The case this exists for: a spec set "installer ≤ 200 MB" with no measurement; implement found the
WebView2 offline installer alone weighs 212 MB, and the run stopped to ask. Reading one vendor
download page at spec time would have caught it.

## Check before presenting

- Every output in §2 has at least one QC item in §6.
- §6 holds no `tests/...` path and no `-k` flag — the check command lives in the plan.
- §1b is present: every workflow step/phase says `CÓ` or `BỎ`, with the reason. <!-- i18n-allow: canonical spec section names -->
- §2b is present in lane full: one row per module, no two modules declaring one path.
- §3b is present: one row per skill marked `DÙNG` or `NỀN`, everything else merged into the <!-- i18n-allow: canonical spec section names -->
  summary row `Đã xét <N> skill khác` — machine-checked by `doc_lint.py` rule R8. <!-- i18n-allow: canonical spec section names -->
- A PASS condition in §6 is measurable by a command, not by feel.
- Every numeric threshold in §6 has `Đo trước` and `Dự phòng nếu trượt` filled — `doc_lint` R14. <!-- i18n-allow: canonical spec column names -->
- §7 is empty.
- No sentence uses a vague word ("phù hợp", "tối ưu", "nếu cần") without a concrete <!-- i18n-allow: the banned words are matched literally by doc_lint -->
  threshold beside it.

## The scope checklist — every box answered before presenting

| Question | The answer must live in |
|---|---|
| What does this work PRODUCE? | §1 mục tiêu + §2 bảng đầu ra <!-- i18n-allow: canonical spec section names --> |
| Are the areas dropped at the scope round written down? | §1 mục NGOÀI phạm vi <!-- i18n-allow: canonical spec section names --> |
| What is NEW compared with what exists today? | §3 cách tiếp cận <!-- i18n-allow: canonical spec section names --> |
| Which file/command/screen exactly is the output? | §2 cột đường dẫn/vị trí <!-- i18n-allow: canonical spec section names --> |
| Is a model needed (name, where it runs, cost)? | §1 phạm vi + §5 ràng buộc <!-- i18n-allow: canonical spec section names --> |
| Is any download/install needed? | §5 ràng buộc — ghi rõ tên gói và bản <!-- i18n-allow: canonical spec section names --> |
| How is QC/test/validate done? | §6 bảng QC + DoD <!-- i18n-allow: canonical spec section names --> |

One box still unanswered → the spec is not ready to present, go back to phase analyze.

## Fresher Accessibility Check — thẩm định độ thấu suốt cho Fresher Dev

Tự kiểm tra độ thân thiện và minh bạch của bản đặc tả với lập trình viên mới:

| Câu hỏi thẩm định | Yêu cầu đạt | Vị trí trong Spec |
|---|---|---|
| **Sơ đồ luồng (§2c)** | Có sơ đồ Mermaid rõ luồng gọi và dữ liệu di chuyển | §2c Luồng hoạt động |
| **Trước vs Sau (§2c)** | Bắt buộc với refactor/update: rõ thành phần cũ vs mới | §2c Bảng đối chiếu |
| **Giải thuật 1-2-3 (§3c)** | Từng bước logic mạch lạc, fresher có thể code lại | §3c Giải thuật |
| **Độ phức tạp (§3c)** | Có định lượng $O(T)$ và $O(S)$ kèm giải thích ngắn | §3c Độ phức tạp |
| **Ca góc hiểm (§3c)** | Nêu tối thiểu 2 edge cases kèm cách phòng thủ | §3c Ca góc hiểm |
| **Ẩn dụ trực quan (§3d)** | Có ví von thực tế đời thường giúp dễ hình dung | §3d Mental Model |
| **Thuật ngữ (§3d)** | Giải nghĩa các khái niệm mới hoặc viết tắt | §3d Glossary |

Tiêu chí quyết định: "Một lập trình viên fresher đọc bản spec này có nắm trọn kiến trúc và giải thuật mà AI chuẩn bị làm hay không?". Nếu câu trả lời là chưa rõ ràng, phải viết lại trước khi trình duyệt.

## Quy tắc chi tiết các phần điều kiện trong Spec

- **§2b Ranh giới module**: Hai module không được khai chung một đường dẫn. Trùng nghĩa là chưa tách xong — gộp lại thành một module, hoặc tách file ra trước.
- **§3b Năng lực & công cụ**: Một dòng cho mỗi skill DÙNG hoặc NỀN, cộng đúng một dòng tổng cho phần còn lại. Không xoá mục này kể cả khi không có dòng DÙNG nào.
- **§4 Yêu cầu bắt buộc**: Dòng Log service bắt buộc chỉ khi việc này có runtime (có ít nhất một task tạo hoặc sửa file mã nguồn chạy được). Không có runtime → thay bằng `Log service: BỎ — <lý do một câu>`.
- **§5 Ràng buộc kiến trúc**: Chép nguyên văn dòng luật từ `docs/kien-truc.md` mà việc này chạm tới. Chưa có `docs/kien-truc.md` → quay lại analyze sinh theo luật hồ sơ kiến trúc, không bỏ trống.
