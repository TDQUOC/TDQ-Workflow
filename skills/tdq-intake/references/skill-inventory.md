# Kiểm kê năng lực (bước B0)

Mục tiêu: mọi skill/công cụ đang có đều được XÉT một lần, thành một bảng máy kiểm được.
Không xét = bỏ sót; xét rồi loại có lý do = hợp lệ.

## Các bước

1. Chạy lệnh (in bảng skill trên đĩa):
   ```
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/skill_inventory.py"
   ```
2. CHÉP THÊM các skill built-in đang thấy trong context vào bảng (chúng không có trên đĩa).
3. Điền bảng theo khuôn dưới — mỗi skill đúng 1 dòng, mỗi dòng DÙNG một skill riêng.
4. Lưu bảng vào `docs/tdq/knowledge/<slug>.md` dưới heading `## Năng lực dùng được`.

## Khuôn bảng (copy nguyên khối rồi điền)

```markdown
## Năng lực dùng được

Phân vân → DÙNG. Không xoá bảng này kể cả khi mọi dòng là KHÔNG.

| Skill | Nguồn | Phán quyết | Dùng ở đâu / Lý do loại |
|---|---|---|---|
| <tên skill> | <user/project/plugin:x/built-in> | <DÙNG, KHÔNG hoặc NỀN> | <dùng ở đâu, hoặc lý do loại> |
```

Ví dụ dòng đã điền (KHÔNG chép vào bảng thật):
`| dataviz | built-in | DÙNG | vẽ biểu đồ ở đầu ra #2 |` ·
`| graphify | user | KHÔNG | khác lĩnh vực |`

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

- `DÙNG` → spec chép dòng đó vào mục `## 3b` · plan phải có **khối hợp đồng 6 trường**
  (`Dùng/Nạp/Để/Ra/Kiểm/Không dùng cho`) cho nó · QC chạy trường `Kiểm`.
- `KHÔNG` → chép nguyên dòng vào spec §3b, không cần gì thêm.
- `NỀN` → chép nguyên dòng vào spec §3b, không cần hợp đồng.

Kiểm bằng máy: `doc_lint.py` rule R8 soi spec; `doc_lint.py --pair <spec> <plan>` soi hợp đồng.

## Bảng quá dài

Trên 20 skill: giữ riêng từng dòng `DÙNG` và `NỀN`; gom các dòng `KHÔNG` cùng lý do
vào 1 dòng, cột Skill liệt kê tên cách nhau bằng dấu phẩy.

## Lane quick

Không cần bảng. Mini-plan có đúng 1 dòng: `Năng lực: <các skill sẽ DÙNG, hoặc "không có">`.
