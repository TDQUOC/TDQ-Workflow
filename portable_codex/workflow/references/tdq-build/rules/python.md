# Rule Python

Soul: chất lượng > runtime > context cost. Nạp sau `chung.md`, áp cho mọi file `.py`.

## Nguồn

- PEP 8 – Style Guide for Python Code — https://peps.python.org/pep-0008 (bản cập nhật
  2025-04-04) — chuẩn đặt tên, layout, import, so sánh.
- ruff — linter mặc định của TDQ cho Python (chạy các nhóm check kiểu F/E/B); URL chính
  thức chưa có trong research nên chỉ ghi tên lệnh, không bịa link.

## Khi nào áp dụng

- Viết hoặc sửa bất kỳ file `.py` nào, gồm cả script tiện ích và file test.
- Trước khi nộp code: chạy mục "Tự kiểm"; máy thiếu `ruff` thì ghi "chưa kiểm được".

## Luật Intentionality

Ba dạng lỗi Intentionality hay gặp nhất ở Python (soát trước mọi thứ khác):

1. **Tên sai chuẩn hoặc mơ hồ**: hàm/biến phải `snake_case`, class `PascalCase`, hằng
   `UPPER_CASE` (PEP 8); tên kiểu `process`, `data2`, `tmp` là tên chưa nói được việc.
2. **Nuốt lỗi**: `except:` trần hay `except Exception: pass` giấu bug — bắt đúng loại
   exception, log rồi xử lý hoặc ném tiếp.
3. **Code chết**: import không dùng, biến gán rồi bỏ — ruff báo nhóm F (F401, F841) → xoá.

## Ngưỡng đo được

- Cyclomatic ≤ 10, cognitive ≤ 15 mỗi hàm — theo `chung.md`, không có ngoại lệ Python.
- Độ dài dòng: PEP 8 đặt 79 ký tự; dự án được ghi đè bằng config của ruff
  (`line-length`) và phải ghi số đã chọn vào spec của request.

## Làm gì

1. Đặt tên theo PEP 8: module ngắn viết thường, hàm/biến `snake_case`, class
   `PascalCase`, hằng `UPPER_CASE`.
2. Import đứng đầu file, chia 3 nhóm theo thứ tự: chuẩn (stdlib) → bên thứ ba → nội bộ.
3. So sánh với `None` bằng `is None` / `is not None`; không viết `== True` với bool.
4. Không dùng mutable làm default argument (`def f(x, xs=[])` → dùng `xs=None` rồi gán).
5. Hàm public có docstring 1 dòng nêu việc; hàm dùng nội bộ thì tên phải tự giải thích.
6. Chạy `ruff check <đường dẫn>` và sửa hết lỗi báo ra.

## Tự kiểm

- [ ] `ruff check` sạch, hoặc đã ghi "chưa kiểm được" khi máy thiếu ruff
- [ ] Không `except:` trần, không mutable default, không import/biến thừa
- [ ] Tên đúng case theo PEP 8 và đọc lên ra đúng việc
- [ ] Trả lời được 3 câu hỏi Intentionality trong `chung.md`

## Ví dụ ĐÚNG/SAI

```python
# SAI — tên mơ hồ, mutable default, nuốt lỗi:
def Calc(d, out=[]):
    try:
        out.append(d["v"])
    except:
        pass
# ĐÚNG — tên nêu việc, default an toàn, lỗi có chủ đích:
def gom_gia_tri(ban_ghi: dict, dich: list | None = None) -> list:
    dich = [] if dich is None else dich
    if "v" not in ban_ghi:
        raise KeyError("ban_ghi thiếu khoá 'v'")
    dich.append(ban_ghi["v"])
    return dich
```
