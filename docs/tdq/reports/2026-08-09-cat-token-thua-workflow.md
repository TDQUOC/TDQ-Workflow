# REPORT — Cắt token thừa trong TDQ workflow

Ngày: 2026-08-09 · Lane: full · Mode: main · QC: 11/11 PASS (vòng 1, không phải fix)

## Đã làm

- **C1** `skill-inventory.md`: bảng kiểm kê không còn chép 242 skill. Luật mới: một dòng cho
  mỗi skill `DÙNG`/`NỀN`, cộng đúng một dòng tổng `Đã xét <N> skill khác — khác lĩnh vực`.
  Bỏ mục "Bảng quá dài" vì luật mới đã bao.
- **C2** `plan-template.md`: xoá hẳn mục `## Năng lực → task` — bản chép thứ ba của cùng
  bảng năng lực (brief → spec §3b đã đủ).
- **C3** Phase log/test thành **có điều kiện**: chỉ bắt buộc khi việc có runtime; không có
  runtime thì ghi đúng một dòng `Log: BỎ — <lý do>` (spec §4 và plan-template).
- **C4** `phases-doc` thôi sinh mục chi tiết từng phase (nó lặp lại SKILL.md của chính phase
  đó). `phases.md`: **89 → 33 dòng**. Checklist đầy đủ vẫn lấy được qua `tdq_state.py next`.
- **C5** Câu chốt vòng interview thành có điều kiện — chỉ hỏi khi vòng đó thật sự có câu hỏi,
  hết dựng vòng rỗng chỉ để hỏi "Bạn muốn bổ sung thêm gì không?".
- **C6** `docs/claude-md-mau.md` là nguồn sự thật duy nhất, đã hợp nhất phần chỉ có ở bản
  live (§8 plugin, §9 mem0), cắt chi tiết đã nằm ở file đích, rồi sync ra `~/.claude/CLAUDE.md`.
  Hai file nay `diff` rỗng; 3.460 byte so với 4.243 byte của bản live cũ.
- **Phụ**: hợp đồng skill còn 5 trường (bỏ `Nạp`, câu chỉ đường SKILL.md dời vào `Để`),
  `doc_lint.CONTRACT_FIELDS` và test đi kèm cập nhật theo.

## Kiểm chứng

412 test `unittest` xanh · `doc_lint.py` exit 0 trên 6 file skills đã sửa · 11 dòng DoD PASS,
bằng chứng trong `docs/tdq/qc/2026-08-09-cat-token-thua-workflow.md` · graph đã sinh lại
(`graphify extract . --code-only`: 3.092 node, 3.846 edge) · fact dài hạn đã lưu vào mem0.

## Cần biết

- `tests/test_phase_table.py::test_render_no_regex_escape_artifact` phải sửa: nó soi mục chi
  tiết từng phase mà C4 vừa xoá. Bản mới soi khối "Lệnh nguyên văn" — vẫn bắt đủ 3 lỗi cũ.
- Test của T3.2 trong plan đổi so với bản duyệt (soi hằng `PHASE_TABLE` thay vì output
  `phases-doc`), lý do ghi ngay tại dòng task.
- **Không đụng gate duyệt**: quick vẫn 1 cổng, full vẫn 2 cổng (spec + plan).

Chưa commit gì. Bạn muốn tôi commit đợt thay đổi này không?
