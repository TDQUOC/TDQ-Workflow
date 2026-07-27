---
name: tdq-spec
description: Write the Vietnamese spec for a TDQ request, register it in state, get it reviewed, then wait for user approval. Full lane, after tdq-analyze.
---

# TDQ Spec

Read [tdq-conventions](../tdq-conventions/SKILL.md). Spec is written in VIETNAMESE. Never write spec and plan in the same turn.

## Steps

1. **Draft** `docs/tdq/spec/<slug>.md` from `knowledge/<slug>.md`. Required sections (VI):
   - Mục tiêu & phạm vi (in-scope / out-of-scope rõ ràng)
   - Đầu ra cụ thể (files, features, behaviors — đo đếm được)
   - Kiến trúc / cách tiếp cận + lý do chọn (kèm nguồn research nếu có)
   - Yêu cầu bắt buộc: logging service bật mặc định (timestamp, đủ chi tiết debug); không placeholder/mock-as-real; unit test cho từng phần
   - Ràng buộc & rủi ro
   - Phạm vi QC/test/validate (điều kiện pass đo được)
   - Câu hỏi còn mở: PHẢI rỗng — nếu còn, quay lại tdq-analyze

2. **Self-review, then subagent review.** Re-read for gaps/contradictions, fix. Then spawn the `tdq-reviewer` agent on the spec file; apply valid findings; note rejected ones + why at the end of the spec.

3. **Register the file** (approval validation requires this):
   `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/tdq_state.py" set spec_file=docs/tdq/spec/<slug>.md`

4. **Present & wait.** In chat (VI): tóm tắt spec ≤ 10 dòng, ngay dưới đó in đúng dòng:
   `➤ Để duyệt: gõ /tdq-workflow:tdq-approve spec · Góp ý: nhắn trực tiếp`
   Then STOP the turn. Do not proceed, do not write the plan. If the user gives feedback instead of approving → revise the spec, bump its version, re-present, wait again.

After the approve hook confirms, move to [tdq-plan](../tdq-plan/SKILL.md) (next turn): `... set phase=plan`.
