# Kiểm kê năng lực (bước B0)

Mục tiêu: mọi skill/công cụ đang có đều được XÉT một lần. **Xét ≠ ghi ra.**
Rà thì rà hết; viết vào brief thì chỉ viết dòng có ảnh hưởng tới việc.

## Các bước

1. Chạy lệnh (in bảng skill trên đĩa) và ĐỌC hết output:
   ```
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/skill_inventory.py"
   ```
2. Rà thêm các skill built-in đang thấy trong context. Không chép chúng vào brief.
3. Điền bảng theo khuôn dưới: **một dòng cho mỗi skill `DÙNG` hoặc `NỀN`**, cộng đúng
   một dòng tổng cho toàn bộ phần còn lại.
4. Lưu bảng vào `docs/tdq/brief/<slug>.md` dưới heading `### Năng lực dùng được`.

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

Dòng tổng gộp được nhiều skill vì lý do loại của chúng giống hệt nhau. Skill nào bị loại
vì lý do KHÁC `khác lĩnh vực` thì tách thành dòng riêng, ghi rõ lý do.

## Luật điền ô "Phán quyết"

Chỉ có 3 giá trị. Chọn theo bảng, từ trên xuống, dừng ở dòng khớp đầu tiên:

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

- `DÙNG` → spec chép dòng đó vào mục `## 3b` · plan phải có **khối hợp đồng 5 trường**
  (`Dùng/Để/Ra/Kiểm/Không dùng cho`) cho nó · QC chạy trường `Kiểm`.
- `KHÔNG` → chép nguyên dòng vào spec §3b, không cần gì thêm.
- `NỀN` → chép nguyên dòng vào spec §3b, không cần hợp đồng.

Kiểm bằng máy: `doc_lint.py` rule R8 soi spec; `doc_lint.py --pair <spec> <plan>` soi hợp đồng.

## Chế độ nhanh (express)

Không cần bảng. Mini-plan có đúng 1 dòng: `Năng lực: <các skill sẽ DÙNG, hoặc "không có">`.
