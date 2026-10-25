#!/usr/bin/env python3
"""
Document Placement Gate: Enforces clean workspace discipline by preventing agents from
dumping arbitrary markdown notes or summary files outside governed documentation directories.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _common  # noqa: E402, F401

# Governed spaces where markdown files are strictly permitted
ALLOWED_MD_PREFIXES = (
    "docs/tdq/",
    "docs/workinglog/",
    "docs/archive/",
    "skills/",
    "agents/",
    "tests/",
)

# Explicitly allowed root-level markdown files
ALLOWED_ROOT_FILES = {
    "README.md",
    "CHANGELOG.md",
    "CONTRIBUTING.md",
    "LICENSE.md",
}


def is_markdown_allowed(target_file_path: str, repo_root: Path = Path(".")) -> bool:
    """Check if the given markdown file path is located in an authorized directory."""
    try:
        p = Path(target_file_path)
        # Only inspect markdown files
        if p.suffix.lower() != ".md":
            return True

        # Normalize relative path to project root
        try:
            rel = p.resolve().relative_to(repo_root.resolve()).as_posix()
        except ValueError:
            rel = p.as_posix()

        # Check root whitelist
        if "/" not in rel and rel in ALLOWED_ROOT_FILES:
            return True

        # Check permitted folder spaces
        for prefix in ALLOWED_MD_PREFIXES:
            if rel.startswith(prefix):
                return True

        return False
    except Exception:
        return True


def validate_file_write(target_path: str) -> int:
    """Validate target path and exit 1 with explicit rejection if unauthorized."""
    if not is_markdown_allowed(target_path):
        print(
            f"[TDQ DOC-GATE REJECTION] Unauthorized markdown file placement: '{target_path}'.\n"
            "Rule: All generated documentation files must be placed within 'docs/tdq/' or 'docs/workinglog/'.\n"
            "Spawning rogue summary files in root or source directories is prohibited.",
            file=sys.stderr,
        )
        return 1
    return 0


def main():
    if len(sys.argv) > 1:
        sys.exit(validate_file_write(sys.argv[1]))
    sys.exit(0)


if __name__ == "__main__":
    main()
