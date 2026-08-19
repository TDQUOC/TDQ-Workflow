# Python rules

Soul: chất lượng > runtime > context cost. Load after `chung.md`; applies to every `.py` file.

## Nguồn

- PEP 8 – Style Guide for Python Code — https://peps.python.org/pep-0008 (updated
  2025-04-04) — naming, layout, imports, comparisons.
- ruff — TDQ's default Python linter (runs the F/E/B style check groups); its official URL is
  not in the research file, so only the command name is given, no invented link.

## Khi nào áp dụng

- Writing or changing any `.py` file, utility scripts and test files included.
- Before submitting code: run the "Tự kiểm" section; if the machine lacks `ruff`, write
  "chưa kiểm được".

## Luật Intentionality

The three most common Intentionality defects in Python (review these before anything else):

1. **Off-standard or vague names**: functions/variables must be `snake_case`, classes
   `PascalCase`, constants `UPPER_CASE` (PEP 8); names like `process`, `data2`, `tmp` do not
   say what the thing does.
2. **Swallowing errors**: a bare `except:` or `except Exception: pass` hides bugs — catch the
   right exception type, log it, then handle or rethrow.
3. **Dead code**: unused imports, variables assigned then dropped — ruff reports group F
   (F401, F841) → delete them.

## Ngưỡng đo được

- Cyclomatic ≤ 10, cognitive ≤ 15 per function — per `chung.md`, no Python exception.
- Line length: PEP 8 sets 79 characters; a project overrides it through ruff's config
  (`line-length`) and must record the chosen number in the request's spec.

## Làm gì

1. Name per PEP 8: short lowercase modules, `snake_case` functions/variables, `PascalCase`
   classes, `UPPER_CASE` constants.
2. Imports at the top of the file, in three ordered groups: stdlib → third-party → local.
3. Compare with `None` using `is None` / `is not None`; never write `== True` on a bool.
4. Never use a mutable as a default argument (`def f(x, xs=[])` → take `xs=None` and assign).
5. Public functions carry a one-line docstring stating the job; internal helpers must be
   self-explanatory by name.
6. Run `ruff check <đường dẫn>` and fix everything it reports.

## Tự kiểm

- [ ] `ruff check` clean, or "chưa kiểm được" recorded because the machine lacks ruff
- [ ] No bare `except:`, no mutable default, no unused import/variable
- [ ] Names use the PEP 8 case and read as the work they do
- [ ] The 3 Intentionality questions in `chung.md` are answerable

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
