# Kiểm kê năng lực (bước B0)

(nhắc lại có chủ ý — bản gốc ở bước B0 của
[analyze-full.md](analyze-full.md).)

Goal: every skill/tool you have is CONSIDERED once. **Considering ≠ writing it down.**
Sweep everything; write into the brief only the lines that affect the work.

## Các bước

1. Run the command (it prints the table of skills on disk) and READ all of its output:
   ```
   python3 "./scripts/skill_inventory.py" --loc "<từ khoá của yêu cầu>"
   ```
   Flag `--loc` trims the table to the relevant part, NEVER hides a skill from source
   `project` or `plugin:tdq-workflow`, and the last line always reports how many were
   hidden. Suspect something is missing → you MUST re-run with `--tat-ca` before ruling.
2. Also sweep the built-in skills visible in context. Do not copy those into the brief.
3. Fill the table per the khuôn below: **one row per skill marked `DÙNG` or `NỀN`**, plus
   exactly one summary row for everything else.
4. Save the table into `docs/tdq/brief/<slug>.md` under the heading `### Năng lực dùng được`.

## Khuôn bảng (copy nguyên khối rồi điền)

```markdown
## Năng lực dùng được

Phân vân → DÙNG. Kiểm kê ngày <YYYY-MM-DD>: <N> skill trên đĩa, cộng skill built-in
trong context. Không xoá bảng này kể cả khi không có dòng DÙNG nào.

| Skill | Nguồn | Phán quyết | Dùng ở đâu / Lý do loại |
|---|---|---|---|
| <tên skill> | <user/project/plugin:x/built-in> | <DÙNG hoặc NỀN> | <dùng ở đâu> |
| Đã xét <N> skill khác | user/plugin/built-in | KHÔNG | khác lĩnh vực |
```

Ví dụ dòng đã điền (KHÔNG chép vào bảng thật):
`| dataviz | built-in | DÙNG | vẽ biểu đồ ở đầu ra #2 |` ·
`| Đã xét 240 skill khác | plugin | KHÔNG | khác lĩnh vực |`

The summary row merges many skills because their rejection reason is identical. A skill
rejected for a reason OTHER than `khác lĩnh vực` gets its own row, with that reason spelled
out.

## Luật điền ô "Phán quyết"

Only 3 values exist. Pick from the table below, top down, stopping at the first match:

| Nếu | Ghi |
|---|---|
| Skill là chính workflow đang chạy (tdq-*) | `NỀN` |
| Khớp đúng 1 trong 4 lý do loại ở bảng dưới | `KHÔNG` + lý do |
| Mọi trường hợp còn lại (kể cả phân vân) | `DÙNG` + dùng ở đâu |

## 4 lý do loại (đóng — cấm tự chế lý do khác)

| Lý do (ghi đúng cụm này vào ô) | Nghĩa là |
|---|---|
| `khác lĩnh vực` | Việc này không chạm tới thứ skill mô tả |
| `spec §3 đã chọn cách khác tốt hơn` | Có cách khác đã chốt trong spec, ghi rõ cách nào |
| `thiếu quyền/công cụ skill đó cần` | Skill cần thứ máy này không có |
| `user đã cấm` | User đã nói không dùng |

## Số phận từng phán quyết ở các phase sau

- `DÙNG` → the spec copies that row into section `## 3b` · the plan must carry a
  **khối hợp đồng 5 trường** (`Dùng/Để/Ra/Kiểm/Không dùng cho`) for it · QC runs the
  `Kiểm` field.
- `KHÔNG` → copy the row verbatim into spec §3b, nothing else needed.
- `NỀN` → copy the row verbatim into spec §3b, no contract needed.

Machine check: `doc_lint.py` rule R8 inspects the spec; `doc_lint.py --pair <spec> <plan>`
inspects the contract.

## Chế độ nhanh (express)

No table needed. The mini-plan carries exactly 1 line: `Ước tính sẽ dùng skill: <các skill
sẽ DÙNG, hoặc "không có">`.
