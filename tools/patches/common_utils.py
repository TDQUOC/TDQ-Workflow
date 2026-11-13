"""Shared filesystem, AST, byte-budget, and text transformation helpers."""
import ast
import io
import os
import shutil
import stat
from pathlib import Path
from typing import Dict, Iterable, List, Tuple


EXCLUDED_SCRIPTS = {
    "build_portable.py",
    "canvas_a4_ch4_ch7.py",
    "canvas_a4_rebuild.py",
    "canvas_draw.py",
    "canvas_layout_apply.py",
    "canvas_move_block.py",
    "check_canvas_layout.py",
}


def force_writable_rmtree(path: Path) -> None:
    """Remove directory tree safely on Windows even when read-only bits exist."""
    if not path.exists():
        return

    def _on_exc(func, target, _exc):
        os.chmod(target, stat.S_IWRITE)
        func(target)

    shutil.rmtree(path, onexc=_on_exc)


def copy_clean_tree(src: Path, dst: Path, exclude_names: Iterable[str] = ()) -> int:
    """Copy directory tree excluding caches and explicitly skipped filenames."""
    skip = {"__pycache__", ".pytest_cache", ".ruff_cache"} | set(exclude_names)
    count = 0
    for root, dirs, files in os.walk(src):
        dirs[:] = sorted(d for d in dirs if d not in skip)
        rel_root = Path(root).relative_to(src)
        out_dir = dst / rel_root
        out_dir.mkdir(parents=True, exist_ok=True)
        for name in sorted(files):
            if name in skip or name.endswith((".pyc", ".pyo")):
                continue
            shutil.copy2(Path(root) / name, out_dir / name)
            count += 1
    return count


def read_utf8(path: Path) -> str:
    """Read UTF-8 file normalizing CRLF to LF for deterministic patching."""
    return path.read_text(encoding="utf-8").replace("\r\n", "\n")


def write_utf8(path: Path, text: str) -> None:
    """Write UTF-8 text with LF newlines, creating parent folders."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)


def replace_exact(path: Path, old: str, new: str, *, label: str = "") -> None:
    """Replace an exact snippet once; fail loudly if the upstream baseline changed."""
    text = read_utf8(path)
    if old not in text:
        tag = f" ({label})" if label else ""
        raise RuntimeError(f"Patch anchor not found in {path}{tag}:\n{old[:180]}")
    updated = text.replace(old, new, 1)
    write_utf8(path, updated)


def ensure_utf8_import(path: Path) -> bool:
    """Ensure a Python module imports utf8_io when executed directly on Windows."""
    text = read_utf8(path)
    if "import utf8_io" in text:
        return False
    lines = text.splitlines()
    insert_at = 0
    if lines and lines[0].startswith("#!"):
        insert_at = 1
    while insert_at < len(lines) and (
        not lines[insert_at].strip() or lines[insert_at].startswith('"""') or lines[insert_at].startswith("'''")
    ):
        if lines[insert_at].startswith(('"""', "'''")):
            quote = lines[insert_at][:3]
            if lines[insert_at].count(quote) >= 2 and len(lines[insert_at].strip()) > 3:
                insert_at += 1
                break
            insert_at += 1
            while insert_at < len(lines) and quote not in lines[insert_at]:
                insert_at += 1
            insert_at += 1
            break
        insert_at += 1
    snippet = (
        "import os as _tdq_os, sys as _tdq_sys\n"
        "_tdq_here = _tdq_os.path.dirname(_tdq_os.path.abspath(__file__))\n"
        "_tdq_scripts = _tdq_os.path.normpath(_tdq_os.path.join(_tdq_here, '..', '..', 'scripts'))\n"
        "for _p in (_tdq_scripts, _tdq_here):\n"
        "    if _tdq_os.path.isdir(_p) and _p not in _tdq_sys.path:\n"
        "        _tdq_sys.path.insert(0, _p)\n"
        "import utf8_io  # noqa: E402,F401"
    )
    lines.insert(insert_at, snippet)
    write_utf8(path, "\n".join(lines) + "\n")
    return True


def verify_all_py_ast(root: Path) -> Tuple[int, List[str]]:
    """Parse every .py file under root with Python AST to catch syntax/escape faults."""
    checked = 0
    errors: List[str] = []
    for path in sorted(root.rglob("*.py")):
        checked += 1
        try:
            ast.parse(read_utf8(path), filename=str(path))
        except SyntaxError as exc:
            errors.append(f"{path}:{exc.lineno}:{exc.offset}: {exc.msg}")
    return checked, errors


def check_md_byte_budgets(root: Path, limit_bytes: int = 24000) -> Tuple[int, List[str]]:
    """Measure UTF-8 byte lengths of all rules/*.md and skills/*/SKILL.md."""
    checked = 0
    violations: List[str] = []
    patterns = ("rules/*.md", "skills/*/SKILL.md")
    for pat in patterns:
        for path in sorted(root.glob(pat)):
            checked += 1
            size = len(path.read_bytes())
            if size >= limit_bytes:
                rel = path.relative_to(root).as_posix()
                violations.append(f"{rel}: {size} bytes >= {limit_bytes}")
    return checked, violations


def make_rule_markdown(filename: str, frontmatter: Dict[str, str], body: str) -> str:
    """Format an Antigravity rule markdown document with optional YAML frontmatter."""
    if not frontmatter:
        return body.strip() + "\n"
    fm = ["---"]
    for key, val in frontmatter.items():
        if key == "globs":
            fm.append(f'{key}: "{val}"')
        else:
            fm.append(f"{key}: {val}")
    fm.append("---")
    return "\n".join(fm) + "\n\n" + body.strip() + "\n"
