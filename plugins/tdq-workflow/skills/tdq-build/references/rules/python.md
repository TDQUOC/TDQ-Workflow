# Python rules

Soul: chất lượng > runtime > context cost <!-- i18n-allow: canonical Soul line -->. Load after `chung.md`; applies to every `.py` file.

## Sources

- PEP 8 – Style Guide for Python Code — https://peps.python.org/pep-0008 (updated
  2025-04-04) — naming, layout, imports, comparisons.
- ruff — TDQ's default Python linter (runs the F/E/B style check groups); its official URL is
  not in the research file, so only the command name is given, no invented link.

## When it applies

- Writing or changing any `.py` file, utility scripts and test files included.
- Before submitting code: run the "Self-check" section; if the machine lacks `ruff`, write
  "not checked yet".

## The Intentionality rule

The three most common Intentionality defects in Python (review these before anything else):

1. **Off-standard or vague names**: functions/variables must be `snake_case`, classes
   `PascalCase`, constants `UPPER_CASE` (PEP 8); names like `process`, `data2`, `tmp` do not
   say what the thing does.
2. **Swallowing errors**: a bare `except:` or `except Exception: pass` hides bugs — catch the
   right exception type, log it, then handle or rethrow.
3. **Dead code**: unused imports, variables assigned then dropped — ruff reports group F
   (F401, F841) → delete them.

## Measurable thresholds

- Cyclomatic ≤ 10, cognitive ≤ 15 per function — per `chung.md`, no Python exception.
- Line length: PEP 8 sets 79 characters; a project overrides it through ruff's config
  (`line-length`) and must record the chosen number in the request's spec.

## What to do

1. Name per PEP 8: short lowercase modules, `snake_case` functions/variables, `PascalCase`
   classes, `UPPER_CASE` constants.
2. Imports at the top of the file, in three ordered groups: stdlib → third-party → local.
3. Compare with `None` using `is None` / `is not None`; never write `== True` on a bool.
4. Never use a mutable as a default argument (`def f(x, xs=[])` → take `xs=None` and assign).
5. Public functions carry a one-line docstring stating the job; internal helpers must be
   self-explanatory by name.
6. Run `ruff check <path>` and fix everything it reports.

## Self-check

- [ ] `ruff check` clean, or "not checked yet" recorded because the machine lacks ruff
- [ ] No bare `except:`, no mutable default, no unused import/variable
- [ ] Names use the PEP 8 case and read as the work they do
- [ ] The 3 Intentionality questions in `chung.md` are answerable

## RIGHT/WRONG examples

```python
# WRONG — vague name, mutable default, swallowed error:
def Calc(d, out=[]):
    try:
        out.append(d["v"])
    except:
        pass
# RIGHT — the name states the work, a safe default, a deliberate error:
def collect_values(record: dict, out: list | None = None) -> list:
    out = [] if out is None else out
    if "v" not in record:
        raise KeyError("record has no key 'v'")
    out.append(record["v"])
    return out
```
