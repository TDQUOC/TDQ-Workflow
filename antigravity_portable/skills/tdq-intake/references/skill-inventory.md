# Capability inventory (step B0)

(deliberate repeat — the source is step B0 of
[analyze-full.md](analyze-full.md).)

Goal: every skill/tool you have is CONSIDERED once. **Considering ≠ writing it down.**
Sweep everything; write into the brief only the lines that affect the work.

## The steps

1. Run the command (it prints the table of skills on disk) and READ all of its output:
   ```
   python3 "~/.gemini/config/plugins/tdq-workflow/scripts/skill_inventory.py" --loc "<keywords of the request>"
   ```
   Flag `--loc` trims the table to the relevant part, NEVER hides a skill from source
   `project` or `plugin:tdq-workflow`, and the last line always reports how many were
   hidden. Suspect something is missing → you MUST re-run with `--tat-ca` before ruling.
2. Also sweep the built-in skills visible in context. Do not copy those into the brief.
3. Fill the table per the template below: **one row per skill marked `DÙNG` or `NỀN`**, plus <!-- i18n-allow: canonical value in the default language -->
   exactly one summary row for everything else. <!-- i18n-allow: canonical verdict values -->
4. Save the table into `docs/tdq/brief/<slug>.md` under the heading `### Năng lực dùng được`. <!-- i18n-allow: canonical section name -->

## Table template (copy the whole block, then fill it in)

<!-- i18n-allow: document template written in the default language -->
```markdown
## Năng lực dùng được

Phân vân → DÙNG. Kiểm kê ngày <YYYY-MM-DD>: <N> skill trên đĩa, cộng skill built-in
trong context. Không xoá bảng này kể cả khi không có dòng DÙNG nào.

| Skill | Nguồn | Phán quyết | Dùng ở đâu / Lý do loại |
|---|---|---|---|
| <tên skill> | <user/project/plugin:x/built-in> | <DÙNG hoặc NỀN> | <dùng ở đâu> |
| Đã xét <N> skill khác | user/plugin/built-in | KHÔNG | khác lĩnh vực |
```

A filled-in example (do NOT copy it into the real table):
<!-- i18n-allow: sample rows written in the default language -->
`| dataviz | built-in | DÙNG | vẽ biểu đồ ở đầu ra #2 |` · <!-- i18n-allow: canonical value in the default language -->
`| Đã xét 240 skill khác | plugin | KHÔNG | khác lĩnh vực |` <!-- i18n-allow: canonical value in the default language -->

The summary row merges many skills because their rejection reason is identical. A skill
rejected for a reason OTHER than "wrong field" gets its own row, with that reason spelled
out.

## How to fill the "Phán quyết" cell <!-- i18n-allow: canonical column name -->

Only 3 values exist. Pick from the table below, top down, stopping at the first match:

| If | Write |
|---|---|
| The skill IS the running workflow itself (tdq-*) | `NỀN` | <!-- i18n-allow: canonical value in the default language -->
| It matches exactly 1 of the 4 rejection reasons below | `KHÔNG` + the reason | <!-- i18n-allow: canonical value in the default language -->
| Everything else (including "not sure") | `DÙNG` + where it is used | <!-- i18n-allow: canonical value in the default language -->

## The 4 rejection reasons (closed set — inventing another is banned)

| Reason (write this exact phrase into the cell) | Means |
|---|---|
| `khác lĩnh vực` | This work does not touch what the skill describes | <!-- i18n-allow: canonical value in the default language -->
| `spec §3 đã chọn cách khác tốt hơn` | The spec settled on another way; name which | <!-- i18n-allow: canonical value in the default language -->
| `thiếu quyền/công cụ skill đó cần` | The skill needs something this machine lacks | <!-- i18n-allow: canonical value in the default language -->
| `user đã cấm` | The user said not to use it | <!-- i18n-allow: canonical value in the default language -->

## What each verdict becomes in the later phases

- `DÙNG` → the spec copies that row into section `## 3b` · the plan must carry a <!-- i18n-allow: canonical value in the default language -->
  **5-field contract block** (`Dùng/Để/Ra/Kiểm/Không dùng cho`) for it · QC runs the <!-- i18n-allow: canonical value in the default language -->
  `Kiểm` field. <!-- i18n-allow: canonical field names -->
- `KHÔNG` → copy the row verbatim into spec §3b, nothing else needed. <!-- i18n-allow: canonical value in the default language -->
- `NỀN` → copy the row verbatim into spec §3b, no contract needed. <!-- i18n-allow: canonical value in the default language -->

Machine check: `doc_lint.py` rule R8 inspects the spec; `doc_lint.py --pair <spec> <plan>`
inspects the contract.

## The express pipeline

No table needed. The mini-plan carries exactly 1 line naming the skills that will be USED,
in the shape `Ước tính sẽ dùng skill: <...>`. <!-- i18n-allow: canonical label -->
