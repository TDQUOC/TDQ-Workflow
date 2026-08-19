# Đo token trước/sau khi dịch hybrid

Ngày: 2026-08-19 · Request: 2026-08-19-1616-huong-a-dich-hybrid
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

File này giữ SỐ. Luật hybrid và ranh giới giữ tiếng Việt nằm ở
`docs/tdq/spec/2026-08-19-1616-huong-a-dich-hybrid.md`.

## Cách đo

- Bộ đếm: `anthropic-tokenizer` trong `.venv-tokens/`, cùng bộ đếm mà
  `scripts/skill_tokens.py` dùng. Không ước lượng ký tự chia bốn.
- "Trước" là bản ở `HEAD` (commit `ea0cdbd`), lấy bằng `git archive HEAD`.
  "Sau" là bản trong cây làm việc. Hai bản đo bằng đúng một lần gọi bộ đếm.
- Đơn vị: token của TOÀN BỘ file, kể cả frontmatter. Bảng `--theo-phase` của
  `skill_tokens.py` cắt frontmatter nên số tổng ở hai bảng dưới lệch nhau — đó là
  hai cách đo khác nhau, không trộn.

## Tổng

| Phép đo | Trước | Sau | Chênh |
|---|---|---|---|
| Tổng 44 file `.md` trong `skills/` | 100.189 | 68.843 | -31,3% |
| Trần lane full (`skill_tokens.py --theo-phase`) | 92.470 | 62.989 | -31,9% |

Ngưỡng của spec (Q7) là giảm ít nhất 30%. Cả hai cách đo đều đạt.

## Trần lane full theo khối phase

| Khối phase | Trước | Sau | Chênh |
|---|---|---|---|
| luôn nạp | 4.600 | 2.798 | -39,2% |
| intake | 2.760 | 1.686 | -38,9% |
| spec | 1.752 | 1.306 | -25,5% |
| plan | 3.325 | 2.324 | -30,1% |
| build | 3.601 | 2.275 | -36,8% |
| luật kèm (mọi reference) | 76.432 | 52.600 | -31,2% |

## Từng file

Sắp theo số token tiết kiệm được, nhiều nhất lên trước.

| File (dưới `skills/`) | Trước | Sau | Chênh | % |
|---|---|---|---|---|
| `tdq-conventions/references/context-budget.md` | 3.982 | 1.911 | -2.071 | -52,0% |
| `tdq-conventions/SKILL.md` | 4.709 | 2.861 | -1.848 | -39,2% |
| `tdq-conventions/references/clean-code.md` | 3.375 | 1.754 | -1.621 | -48,0% |
| `tdq-intake/references/quick-lane.md` | 5.243 | 3.785 | -1.458 | -27,8% |
| `tdq-conventions/references/soul.md` | 2.804 | 1.348 | -1.456 | -51,9% |
| `tdq-build/references/team-mode.md` | 4.034 | 2.589 | -1.445 | -35,8% |
| `tdq-build/SKILL.md` | 3.701 | 2.375 | -1.326 | -35,8% |
| `tdq-intake/references/analyze-full.md` | 2.783 | 1.486 | -1.297 | -46,6% |
| `tdq-build/references/qc.md` | 3.041 | 1.790 | -1.251 | -41,1% |
| `tdq-intake/references/interview.md` | 2.517 | 1.346 | -1.171 | -46,5% |
| `tdq-intake/references/scope-round.md` | 3.626 | 2.484 | -1.142 | -31,5% |
| `tdq-intake/SKILL.md` | 2.865 | 1.791 | -1.074 | -37,5% |
| `tdq-plan/SKILL.md` | 3.425 | 2.424 | -1.001 | -29,2% |
| `tdq-conventions/references/reminder-codes.md` | 1.878 | 1.020 | -858 | -45,7% |
| `tdq-check-status/SKILL.md` | 1.982 | 1.347 | -635 | -32,0% |
| `tdq-conventions/references/subagent-tuning.md` | 1.466 | 837 | -629 | -42,9% |
| `tdq-build/references/report-template.md` | 2.105 | 1.497 | -608 | -28,9% |
| `tdq-build/references/rules/chung.md` | 1.676 | 1.100 | -576 | -34,4% |
| `tdq-build/references/rules/them-ngon-ngu.md` | 1.509 | 950 | -559 | -37,0% |
| `tdq-build/references/rules/index.md` | 1.574 | 1.017 | -557 | -35,4% |
| `tdq-plan/references/mode-gate.md` | 1.851 | 1.315 | -536 | -29,0% |
| `tdq-spec/references/spec-template.md` | 3.825 | 3.306 | -519 | -13,6% |
| `tdq-build/references/rules/cpp.md` | 1.497 | 990 | -507 | -33,9% |
| `tdq-check-status/references/bang-lech.md` | 2.356 | 1.859 | -497 | -21,1% |
| `tdq-build/references/rules/rust.md` | 1.400 | 925 | -475 | -33,9% |
| `tdq-conventions/references/measure-scenario.md` | 1.030 | 558 | -472 | -45,8% |
| `tdq-build/references/rules/python.md` | 1.383 | 924 | -459 | -33,2% |
| `tdq-status/SKILL.md` | 1.398 | 944 | -454 | -32,5% |
| `tdq-build/references/rules/go.md` | 1.449 | 1.000 | -449 | -31,0% |
| `tdq-build/references/rules/typescript-js.md` | 1.501 | 1.054 | -447 | -29,8% |
| `tdq-spec/SKILL.md` | 1.852 | 1.406 | -446 | -24,1% |
| `tdq-plan/references/plan-template.md` | 4.700 | 4.273 | -427 | -9,1% |
| `tdq-build/references/rules/html.md` | 1.339 | 948 | -391 | -29,2% |
| `tdq-intake/references/skill-inventory.md` | 1.885 | 1.500 | -385 | -20,4% |
| `tdq-build/references/rules/csharp.md` | 1.287 | 907 | -380 | -29,5% |
| `tdq-conventions/references/approval.md` | 1.070 | 707 | -363 | -33,9% |
| `tdq-conventions/references/plugin-routing.md` | 1.091 | 738 | -353 | -32,4% |
| `tdq-intake/references/issue-triage.md` | 933 | 583 | -350 | -37,5% |
| `tdq-intake/references/lane-decision.md` | 1.743 | 1.393 | -350 | -20,1% |
| `tdq-conventions/references/worklog-images.md` | 577 | 313 | -264 | -45,8% |
| `tdq-check-status/references/report-template.md` | 1.469 | 1.236 | -233 | -15,9% |
| `tdq-conventions/references/tavily.md` | 513 | 507 | -6 | -1,2% |
| `tdq-conventions/references/phases.md` | 2.229 | 2.229 | 0 | +0,0% |
| `tdq-conventions/references/user-facing-block.md` | 3.516 | 3.516 | 0 | +0,0% |
| **Tổng** | **100.189** | **68.843** | **-31.346** | **-31,3%** |

## Hai file không đổi — có chủ ý

`references/phases.md` và `references/user-facing-block.md` giữ nguyên 0% vì cả hai
gần như chỉ chứa khuôn câu nói với user và tên phase. Dịch chúng là vi phạm chính
ranh giới hybrid: phần user đọc phải ở tiếng Việt.

`references/tavily.md` chỉ giảm 6 token vì thân file đã là tên tool và câu lệnh.

## Ba file giảm ít nhất — vì sao

| File | Chênh | Lý do |
|---|---|---|
| `tdq-plan/references/plan-template.md` | -9,1% | gần hết file nằm trong khối khuôn được chép thẳng vào file plan, phải giữ tiếng Việt |
| `tdq-spec/references/spec-template.md` | -13,6% | như trên, chỉ dịch được phần văn xuôi ngoài khối khuôn |
| `tdq-check-status/references/report-template.md` | -15,9% | phần lớn là output thật của bộ dò, chép nguyên văn |
