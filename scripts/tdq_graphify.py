"""Run TDQ's full Graphify transaction and verify its provenance (stdlib only)."""
import hashlib
import json
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

MANIFEST = Path("graphify-out") / "tdq-full-manifest.json"
OUTPUT_DIRS = {".git", ".venv", "__pycache__", "graphify-out", "node_modules"}
INPUT_SUFFIXES = {".adoc", ".c", ".cc", ".cpp", ".cs", ".go", ".h", ".html",
                  ".java", ".js", ".json", ".jsx", ".kt", ".md", ".mdx", ".org",
                  ".php", ".py", ".rb", ".rs", ".rst", ".sh", ".swift", ".ts",
                  ".tsx", ".txt", ".yaml", ".yml"}
CONFIG_NAMES = {".graphifyignore", "graphify.yaml", "graphify.yml"}


@dataclass(frozen=True)
class Outcome:
    ok: bool
    stale: bool
    message: str


def _sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _stable_digest(items):
    body = "\n".join(f"{name}\0{value}" for name, value in sorted(items.items()))
    return hashlib.sha256(body.encode("utf-8")).hexdigest()


def input_files(project):
    """Return source and documentation inputs, never Graphify's derived output."""
    root = Path(project)
    files = []
    for path in root.rglob("*"):
        if not path.is_file() or any(part in OUTPUT_DIRS for part in path.relative_to(root).parts):
            continue
        if path.suffix.lower() in INPUT_SUFFIXES:
            files.append(path)
    return sorted(files)


def _config_files(project):
    root = Path(project)
    return [root / name for name in CONFIG_NAMES if (root / name).is_file()]


def _runtime_marker():
    """Record selection metadata only; secrets are intentionally never read or logged."""
    return {"backend": os.environ.get("GRAPHIFY_BACKEND", "auto"),
            "model": os.environ.get("GRAPHIFY_MODEL") or os.environ.get("OPENAI_MODEL")
            or os.environ.get("ANTHROPIC_MODEL") or "auto"}


def _fingerprint(project):
    root = Path(project)
    inputs = {str(path.relative_to(root)).replace("\\", "/"): _sha256(path)
              for path in input_files(root)}
    configs = {str(path.relative_to(root)).replace("\\", "/"): _sha256(path)
               for path in _config_files(root)}
    return {"inputs": inputs, "input_digest": _stable_digest(inputs),
            "configs": configs, "config_digest": _stable_digest(configs),
            "runtime": _runtime_marker()}


def _fail(detail):
    return Outcome(False, True, f"Graphify full extraction failed: {detail}. Use LSP + grep until it is fresh.")


def full_extract(project, *, runner, timeout=900):
    """Extract code and semantic inputs, export wiki, then atomically publish provenance."""
    project = Path(project)
    fingerprint = _fingerprint(project)
    code, output = runner(["graphify", "extract", "."], str(project), timeout)
    if code != 0:
        return _fail(output or f"exit {code}")
    code, output = runner(["graphify", "wiki"], str(project), timeout)
    if code != 0:
        return _fail(output or f"wiki exit {code}")
    manifest = project / MANIFEST
    manifest.parent.mkdir(parents=True, exist_ok=True)
    payload = {"status": "fresh", "generated_at": datetime.now(timezone.utc).isoformat(),
               **fingerprint, "wiki": "graphify-out/wiki/index.md"}
    temp = manifest.with_suffix(".tmp")
    temp.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temp.replace(manifest)
    return Outcome(True, False, "Graphify full extraction and wiki are fresh.")


def freshness(project):
    """Treat absent, malformed, incomplete or changed provenance as stale."""
    manifest = Path(project) / MANIFEST
    if not manifest.is_file():
        return Outcome(False, True, "Graphify full manifest is missing. Use LSP + grep until it is fresh.")
    try:
        saved = json.loads(manifest.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        return Outcome(False, True, f"Graphify full manifest is unreadable: {error}. Use LSP + grep until it is fresh.")
    current = _fingerprint(project)
    if saved.get("status") != "fresh" or saved.get("inputs") != current["inputs"]:
        return Outcome(False, True, "Graphify full inputs changed. Use LSP + grep until it is fresh.")
    if saved.get("configs") != current["configs"] or saved.get("runtime") != current["runtime"]:
        return Outcome(False, True, "Graphify full configuration changed. Use LSP + grep until it is fresh.")
    if not (Path(project) / saved.get("wiki", "")).is_file():
        return Outcome(False, True, "Graphify wiki is missing. Use LSP + grep until it is fresh.")
    return Outcome(True, False, "Graphify full graph and wiki are fresh.")
