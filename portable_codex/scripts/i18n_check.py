#!/usr/bin/env python3
"""Report source lines that still carry Vietnamese text.

This is the single measuring tool of the internationalisation work: rule bodies,
code comments and machine-printed strings must all end up in English, while the
documents the workflow writes for the user stay in the user's own language.

Usage:
    python3 scripts/i18n_check.py scripts/ hooks/
    python3 scripts/i18n_check.py --kind comment scripts/tdq_state.py
    python3 scripts/i18n_check.py --json skills/

Prints `file:line: [kind] text`; exit 1 when anything is left, 0 when clean,
2 on a bad path or a bad flag.
A line that must keep its Vietnamese on purpose (a quoted user sentence, a
regex of Vietnamese keywords) carries the marker `i18n-allow` and is skipped.
In a markdown file, an HTML comment carrying the same marker right above a
fenced block exempts that whole block — a template is copied verbatim, so the
marker cannot be written inside it.
Env: TDQ_LOG=0 turns the log service off (on by default, one ISO-timestamp
line on stderr).
"""
import io
import json
import os
import re
import sys
import tokenize
from datetime import datetime

EXIT_SYNTAX = 2
ALLOW_MARKER = "i18n-allow"
KINDS = ("comment", "string", "body")
SCAN_SUFFIXES = (".py", ".md", ".json", ".txt")
SKIP_DIRS = {".git", "__pycache__", ".venv", "node_modules",
             "portable_claude", "portable_codex"}

# Vietnamese-only letters. Plain ASCII words are shared with English, so only a
# diacritic (or the letter đ) proves the line is Vietnamese.  # i18n-allow
VIETNAMESE = re.compile(
    "[àáảãạăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợ"  # i18n-allow
    "ùúủũụưừứửữựỳýỷỹỵđ]", re.IGNORECASE)  # i18n-allow


def _log(message):
    """Log service: one ISO-timestamp line on stderr. Off with TDQ_LOG=0.

    On stderr, not stdout: stdout is the machine-readable channel of this tool
    (`file:line:` rows, or JSON), and mixing the log into it breaks any script
    that pipes the result.
    """
    if os.environ.get("TDQ_LOG", "1") != "0":
        print(f"[{datetime.now().isoformat(timespec='seconds')}] i18n_check: {message}",
              file=sys.stderr)


def collect(paths):
    """Expand files and directories into a sorted list of files to scan."""
    files = []
    for path in paths:
        if os.path.isfile(path):
            files.append(path)
            continue
        for root, dirs, names in os.walk(path):
            dirs[:] = sorted(d for d in dirs if d not in SKIP_DIRS)
            for name in sorted(names):
                if name.endswith(SCAN_SUFFIXES):
                    files.append(os.path.join(root, name))
    return sorted(set(files))


def python_line_kinds(source):
    """Map line number → "comment" or "string" for one Python source text.

    Anything the tokenizer does not mark stays unmapped and counts as body.
    A file that cannot be tokenized (broken syntax) yields an empty map, so
    every one of its lines counts as body rather than being silently skipped.
    """
    kinds = {}
    try:
        tokens = list(tokenize.generate_tokens(io.StringIO(source).readline))
    except (tokenize.TokenError, IndentationError, SyntaxError):
        return kinds
    for token in tokens:
        if token.type == tokenize.COMMENT:
            kinds.setdefault(token.start[0], "comment")
        elif token.type == tokenize.STRING:
            for line in range(token.start[0], token.end[0] + 1):
                kinds.setdefault(line, "string")
    return kinds


def allowed_fence_lines(lines):
    """Line numbers inside a markdown fenced block that an HTML comment exempts.

    A template block is copied into a document WORD FOR WORD, so the per-line
    marker cannot live inside it — it would travel into the copy. The marker
    therefore goes on an HTML comment right above the opening fence:

        <!-- i18n-allow: approval block, written in the user's language -->
        ```
        ...
        ```
    """
    allowed = set()
    marked = False
    inside = False
    for number, text in enumerate(lines, start=1):
        stripped = text.strip()
        if stripped.startswith("```"):
            if inside:
                inside = False
            else:
                inside = marked
            if inside:
                allowed.add(number)
            marked = False
            continue
        if inside:
            allowed.add(number)
        elif stripped.startswith("<!--") and ALLOW_MARKER in stripped:
            marked = True
        elif stripped:
            marked = False
    return allowed


def scan_file(path):
    """Return one finding dict per Vietnamese line of a single file."""
    with open(path, encoding="utf-8", errors="ignore") as fh:
        source = fh.read()
    kinds = python_line_kinds(source) if path.endswith(".py") else {}
    lines = source.splitlines()
    fenced = allowed_fence_lines(lines) if path.endswith(".md") else set()
    findings = []
    for number, text in enumerate(lines, start=1):
        if not VIETNAMESE.search(text) or ALLOW_MARKER in text or number in fenced:
            continue
        findings.append({"file": path, "line": number,
                         "kind": kinds.get(number, "body"),
                         "text": text.strip()})
    return findings


def main(argv):
    kind = None
    as_json = False
    paths = []
    rest = list(argv)
    while rest:
        arg = rest.pop(0)
        if arg == "--json":
            as_json = True
        elif arg == "--kind":
            if not rest or rest[0] not in KINDS:
                print(f"Usage: --kind {'|'.join(KINDS)}", file=sys.stderr)
                return EXIT_SYNTAX
            kind = rest.pop(0)
        else:
            paths.append(arg)
    if not paths:
        print("Usage: i18n_check.py [--kind comment|string|body] [--json] <path>...",
              file=sys.stderr)
        return EXIT_SYNTAX
    missing = [p for p in paths if not os.path.exists(p)]
    if missing:
        for path in missing:
            print(f"⚠️ not found: {path}", file=sys.stderr)
        return EXIT_SYNTAX

    files = collect(paths)
    _log(f"scan {len(files)} file(s), kind={kind or 'all'}")
    findings = []
    for path in files:
        findings += scan_file(path)
    if kind:
        findings = [f for f in findings if f["kind"] == kind]

    if as_json:
        print(json.dumps({"scanned": len(files), "findings": findings},
                         ensure_ascii=False, indent=2))
    else:
        for found in findings:
            print(f"{found['file']}:{found['line']}: [{found['kind']}] {found['text']}")
        print(f"{len(findings)} Vietnamese line(s) in {len(files)} file(s)")
    _log(f"done — {len(findings)} line(s), exit {1 if findings else 0}")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
