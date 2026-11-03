import hashlib
import json
import os
import platform
import subprocess
import sys
import time
from pathlib import Path
import pytest

# Ensure scripts directory is on sys.path for both pytest and unittest discovery
_CURRENT_DIR = Path(__file__).resolve().parent
_REPO_ROOT = _CURRENT_DIR.parent
_SCRIPTS_DIR = _REPO_ROOT / "scripts"
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from archify_artifacts import (
    document_digest,
    source_fingerprint,
    build_manifest,
    check_manifest,
    bind_document,
    check_binding,
    publish_bundle,
    mark_stale,
    BINDING_START,
    BINDING_END,
)


# ---------------------------------------------------------------------------
# document_digest tests
# ---------------------------------------------------------------------------

def test_document_digest_basic(tmp_path):
    doc = tmp_path / "spec.md"
    doc.write_text("# Title\n\nContent here.\n", encoding="utf-8")
    expected = hashlib.sha256(b"# Title\n\nContent here.\n").hexdigest()
    assert document_digest(doc) == expected


def test_document_digest_with_binding(tmp_path):
    doc = tmp_path / "spec.md"
    raw_content = "# Title\n\nSome spec body.\n"
    binding = (
        f"{BINDING_START}\n"
        f"<!-- manifest: docs/manifest.json -->\n"
        f"<!-- manifest_digest: {'a'*64} -->\n"
        f"{BINDING_END}"
    )
    doc.write_text(raw_content + binding, encoding="utf-8")
    expected = hashlib.sha256(raw_content.encode("utf-8")).hexdigest()
    assert document_digest(doc) == expected


def test_document_digest_multiple_markers_fails(tmp_path):
    doc = tmp_path / "spec.md"
    content = (
        f"{BINDING_START}\nfirst\n{BINDING_END}\n"
        f"{BINDING_START}\nsecond\n{BINDING_END}\n"
    )
    doc.write_text(content, encoding="utf-8")
    with pytest.raises(ValueError, match="[Mm]ultiple"):
        document_digest(doc)


def test_document_digest_unmatched_start_fails(tmp_path):
    doc = tmp_path / "spec.md"
    content = f"# Title\n{BINDING_START}\nno end marker\n"
    doc.write_text(content, encoding="utf-8")
    with pytest.raises(ValueError, match="[Uu]nmatched"):
        document_digest(doc)


def test_document_digest_unmatched_end_fails(tmp_path):
    doc = tmp_path / "spec.md"
    content = f"# Title\nno start marker\n{BINDING_END}\n"
    doc.write_text(content, encoding="utf-8")
    with pytest.raises(ValueError, match="[Uu]nmatched"):
        document_digest(doc)


def test_document_digest_inverted_markers_fails(tmp_path):
    doc = tmp_path / "spec.md"
    content = f"# Title\n{BINDING_END}\n{BINDING_START}\n"
    doc.write_text(content, encoding="utf-8")
    with pytest.raises(ValueError, match="[Ee]nd.*before.*start"):
        document_digest(doc)


def test_document_digest_missing_file(tmp_path):
    doc = tmp_path / "nonexistent.md"
    with pytest.raises(FileNotFoundError):
        document_digest(doc)


# ---------------------------------------------------------------------------
# source_fingerprint tests
# ---------------------------------------------------------------------------

def test_source_fingerprint_basic_and_exclusions(tmp_path):
    # Standard source file
    src = tmp_path / "src"
    src.mkdir()
    (src / "app.py").write_text("print('app')", encoding="utf-8")
    (src / "util.py").write_text("print('util')", encoding="utf-8")

    # Excluded dirs
    (tmp_path / ".git").mkdir()
    (tmp_path / ".git" / "HEAD").write_text("ref", encoding="utf-8")
    (tmp_path / "node_modules").mkdir()
    (tmp_path / "node_modules" / "pkg.js").write_text("{}", encoding="utf-8")
    (tmp_path / ".venv").mkdir()
    (tmp_path / ".venv" / "pyvenv.cfg").write_text("home", encoding="utf-8")
    (tmp_path / "__pycache__").mkdir()
    (tmp_path / "__pycache__" / "app.pyc").write_text("bytes", encoding="utf-8")
    (tmp_path / "graphify-out").mkdir()
    (tmp_path / "graphify-out" / "graph.json").write_text("{}", encoding="utf-8")
    (tmp_path / "logs").mkdir()
    (tmp_path / "logs" / "test.log").write_text("log", encoding="utf-8")

    # Excluded prefix dirs
    (tmp_path / "docs" / "architecture").mkdir(parents=True)
    (tmp_path / "docs" / "architecture" / "index.html").write_text("html", encoding="utf-8")
    (tmp_path / "docs" / "tdq").mkdir(parents=True)
    (tmp_path / "docs" / "tdq" / "state.json").write_text("{}", encoding="utf-8")
    (tmp_path / "docs" / "workinglog").mkdir(parents=True)
    (tmp_path / "docs" / "workinglog" / "session.md").write_text("log", encoding="utf-8")

    # Excluded worktrees, env and credentials
    (tmp_path / ".tdq-worktrees").mkdir()
    (tmp_path / ".tdq-worktrees" / "branch.txt").write_text("wt", encoding="utf-8")
    (tmp_path / ".claude").mkdir()
    (tmp_path / ".claude" / "settings.json").write_text("{}", encoding="utf-8")
    (tmp_path / ".env").write_text("SECRET=1", encoding="utf-8")
    (tmp_path / ".env.local").write_text("SECRET=2", encoding="utf-8")
    (tmp_path / "credentials.json").write_text("{}", encoding="utf-8")
    (src / "id_rsa").write_text("key", encoding="utf-8")
    (src / "cert.pem").write_text("cert", encoding="utf-8")
    (src / "server.key").write_text("key", encoding="utf-8")

    # Excluded output candidate/receipts
    (src / "my.candidate.json").write_text("{}", encoding="utf-8")
    (src / "my.receipt.json").write_text("{}", encoding="utf-8")

    fp = source_fingerprint(tmp_path)
    assert "src/app.py" in fp
    assert "src/util.py" in fp

    # None of the excluded files should be present
    for k in fp:
        assert not k.startswith(".git")
        assert not k.startswith("node_modules")
        assert not k.startswith(".venv")
        assert not k.startswith("__pycache__")
        assert not k.startswith("graphify-out")
        assert not k.startswith("logs")
        assert not k.startswith(".tdq-worktrees")
        assert not k.startswith(".claude")
        assert not k.startswith("docs/architecture")
        assert not k.startswith("docs/tdq")
        assert not k.startswith("docs/workinglog")
        assert not k.endswith(".candidate.json")
        assert not k.endswith(".receipt.json")
        assert not k.startswith(".env")
        assert "credential" not in k.lower()
        assert not k.endswith(".pem")
        assert not k.endswith(".key")
        assert "id_rsa" not in k


def test_source_fingerprint_explicit_paths_confinement(tmp_path):
    src = tmp_path / "src"
    src.mkdir()
    (src / "main.py").write_text("main", encoding="utf-8")

    fp = source_fingerprint(tmp_path, paths=["src/main.py"])
    assert list(fp.keys()) == ["src/main.py"]

    # Outside project root path must fail confinement check
    with pytest.raises(ValueError, match="outside|escapes"):
        source_fingerprint(tmp_path, paths=["../outside.py"])


def test_source_fingerprint_symlink_outside_root(tmp_path):
    outside = tmp_path.parent / f"outside_{tmp_path.name}"
    outside.mkdir(parents=True, exist_ok=True)
    secret_file = outside / "secret.py"
    secret_file.write_text("secret", encoding="utf-8")

    src = tmp_path / "src"
    src.mkdir(parents=True, exist_ok=True)
    (src / "main.py").write_text("code", encoding="utf-8")

    link = src / "leak.py"
    try:
        os.symlink(secret_file, link)
    except OSError:
        pytest.skip("Symlinks not supported in this environment")

    fp = source_fingerprint(tmp_path)
    assert "src/main.py" in fp
    # The symlink pointing outside root must NOT be included
    assert "src/leak.py" not in fp


# ---------------------------------------------------------------------------
# build_manifest & check_manifest tests
# ---------------------------------------------------------------------------

def test_build_and_check_manifest_basic(tmp_path):
    doc = tmp_path / "doc.md"
    doc.write_text("# Spec\nBody.\n", encoding="utf-8")

    cand = tmp_path / "cand.json"
    cand.write_text('{"nodes": []}', encoding="utf-8")

    art = tmp_path / "art.html"
    art.write_text("<html></html>", encoding="utf-8")

    src = tmp_path / "src"
    src.mkdir()
    (src / "main.py").write_text("x = 1\n", encoding="utf-8")

    receipt = {
        "status": "pass",
        "engine": "archify 3.2.0",
        "api_key": "SUPER_SECRET_KEY",
        "token": "BEARER_SECRET",
    }

    manifest = build_manifest(
        project=tmp_path,
        document=doc,
        candidate=cand,
        artifact=art,
        receipt=receipt,
        evidence_kind="planned",
        request="2026-10-24-test",
        lane="full",
    )

    assert manifest["schema_version"] == 1
    assert manifest["evidence_kind"] == "planned"
    assert manifest["document_path"] == "doc.md"
    assert manifest["candidate_path"] == "cand.json"
    assert manifest["artifact_path"] == "art.html"
    assert "src/main.py" in manifest["source_files"]

    # Secrets sanitized
    assert manifest["receipt"]["api_key"] == "[REDACTED]"
    assert manifest["receipt"]["token"] == "[REDACTED]"
    assert manifest["receipt"]["engine"] == "archify 3.2.0"

    # check_manifest should be current
    res = check_manifest(tmp_path, manifest)
    assert res["status"] == "current"
    assert res["reasons"] == []


def test_check_manifest_detects_mutations(tmp_path):
    doc = tmp_path / "doc.md"
    doc.write_text("# Spec\n", encoding="utf-8")

    cand = tmp_path / "cand.json"
    cand.write_text('{"v": 1}', encoding="utf-8")

    art = tmp_path / "art.html"
    art.write_text("<html>1</html>", encoding="utf-8")

    src = tmp_path / "src"
    src.mkdir()
    (src / "main.py").write_text("init\n", encoding="utf-8")

    manifest = build_manifest(tmp_path, doc, cand, art, {"status": "pass"})
    assert check_manifest(tmp_path, manifest)["status"] == "current"

    # Mutate document
    doc.write_text("# Mutated Spec\n", encoding="utf-8")
    res = check_manifest(tmp_path, manifest)
    assert res["status"] == "stale"
    assert any("Document digest mismatch" in r for r in res["reasons"])
    doc.write_text("# Spec\n", encoding="utf-8")  # restore

    # Mutate candidate
    cand.write_text('{"v": 2}', encoding="utf-8")
    res = check_manifest(tmp_path, manifest)
    assert res["status"] == "stale"
    assert any("Candidate digest mismatch" in r for r in res["reasons"])
    cand.write_text('{"v": 1}', encoding="utf-8")  # restore

    # Mutate artifact
    art.write_text("<html>2</html>", encoding="utf-8")
    res = check_manifest(tmp_path, manifest)
    assert res["status"] == "stale"
    assert any("Artifact digest mismatch" in r for r in res["reasons"])
    art.write_text("<html>1</html>", encoding="utf-8")  # restore

    # Mutate source
    (src / "main.py").write_text("modified\n", encoding="utf-8")
    res = check_manifest(tmp_path, manifest)
    assert res["status"] == "stale"
    assert any("Source file modified" in r for r in res["reasons"])


def test_check_manifest_detects_additions_and_deletions(tmp_path):
    doc = tmp_path / "doc.md"
    doc.write_text("# Spec\n", encoding="utf-8")
    cand = tmp_path / "cand.json"
    cand.write_text('{}', encoding="utf-8")
    art = tmp_path / "art.html"
    art.write_text("<html></html>", encoding="utf-8")
    src = tmp_path / "src"
    src.mkdir()
    file_a = src / "a.py"
    file_a.write_text("a\n", encoding="utf-8")

    manifest = build_manifest(tmp_path, doc, cand, art, {"status": "pass"})
    assert check_manifest(tmp_path, manifest)["status"] == "current"

    # Delete source file
    file_a.unlink()
    res = check_manifest(tmp_path, manifest)
    assert res["status"] == "stale"
    assert any("Source file deleted" in r for r in res["reasons"])

    # Recreate file_a
    file_a.write_text("a\n", encoding="utf-8")

    # Add source file
    file_b = src / "b.py"
    file_b.write_text("b\n", encoding="utf-8")
    res = check_manifest(tmp_path, manifest)
    assert res["status"] == "stale"
    assert any("Source file added" in r for r in res["reasons"])


def test_check_manifest_missing_files_not_current(tmp_path):
    doc = tmp_path / "doc.md"
    doc.write_text("# Spec\n", encoding="utf-8")
    cand = tmp_path / "cand.json"
    cand.write_text('{}', encoding="utf-8")
    art = tmp_path / "art.html"
    art.write_text("<html></html>", encoding="utf-8")

    manifest = build_manifest(tmp_path, doc, cand, art, {"status": "pass"})
    art.unlink()

    res = check_manifest(tmp_path, manifest)
    assert res["status"] == "stale"
    assert any("missing" in r for r in res["reasons"])


def test_check_manifest_committed_revision(tmp_path):
    # Initialize a real git repo
    subprocess.run(["git", "init"], cwd=tmp_path, capture_output=True, check=True, timeout=10)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=tmp_path, check=True, timeout=10)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=tmp_path, check=True, timeout=10)

    doc = tmp_path / "doc.md"
    doc.write_text("# Spec\n", encoding="utf-8")
    cand = tmp_path / "cand.json"
    cand.write_text('{}', encoding="utf-8")
    art = tmp_path / "art.html"
    art.write_text("<html></html>", encoding="utf-8")

    subprocess.run(["git", "add", "."], cwd=tmp_path, check=True, timeout=10)
    subprocess.run(["git", "commit", "-m", "init commit"], cwd=tmp_path, capture_output=True, check=True, timeout=10)
    head_rev = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=True,
        timeout=10,
    ).stdout.strip()

    # Invalid revision format for committed
    bad_manifest = build_manifest(tmp_path, doc, cand, art, {}, evidence_kind="committed", revision="not-40-hex")
    assert check_manifest(tmp_path, bad_manifest)["status"] == "invalid"

    # Valid committed matching HEAD
    good_manifest = build_manifest(tmp_path, doc, cand, art, {}, evidence_kind="committed", revision=head_rev)
    assert check_manifest(tmp_path, good_manifest)["status"] == "current"

    # Make another commit: revision in manifest becomes stale
    (tmp_path / "other.txt").write_text("hello", encoding="utf-8")
    subprocess.run(["git", "add", "other.txt"], cwd=tmp_path, check=True, timeout=10)
    subprocess.run(["git", "commit", "-m", "second commit"], cwd=tmp_path, capture_output=True, check=True, timeout=10)

    res = check_manifest(tmp_path, good_manifest)
    assert res["status"] == "stale"
    assert any("revision mismatch" in r.lower() for r in res["reasons"])


def test_evidence_vs_freshness(tmp_path):
    doc = tmp_path / "doc.md"
    doc.write_text("# Spec\n", encoding="utf-8")
    cand = tmp_path / "cand.json"
    cand.write_text('{}', encoding="utf-8")
    art = tmp_path / "art.html"
    art.write_text("<html></html>", encoding="utf-8")

    # Planned evidence can be 'current' in freshness if files are unmodified
    manifest = build_manifest(tmp_path, doc, cand, art, {}, evidence_kind="planned")
    assert manifest["evidence_kind"] == "planned"
    assert check_manifest(tmp_path, manifest)["status"] == "current"


def test_check_manifest_json_scalar_or_null_or_array_invalid(tmp_path):
    # Test file containing null
    null_file = tmp_path / "null_manifest.json"
    null_file.write_text("null", encoding="utf-8")
    res = check_manifest(tmp_path, null_file)
    assert res["status"] == "invalid"
    assert any("JSON object" in r for r in res["reasons"])

    # Test file containing number
    num_file = tmp_path / "num_manifest.json"
    num_file.write_text("123", encoding="utf-8")
    res2 = check_manifest(tmp_path, num_file)
    assert res2["status"] == "invalid"

    # Test file containing array
    arr_file = tmp_path / "arr_manifest.json"
    arr_file.write_text("[]", encoding="utf-8")
    res3 = check_manifest(tmp_path, arr_file)
    assert res3["status"] == "invalid"

    # Test dict passed directly as None or list
    assert check_manifest(tmp_path, None)["status"] == "invalid"
    assert check_manifest(tmp_path, [])["status"] == "invalid"


def test_build_manifest_receipt_and_artifact_types_fail_closed(tmp_path):
    doc = tmp_path / "doc.md"
    doc.write_text("# Spec\n", encoding="utf-8")
    cand = tmp_path / "cand.json"
    cand.write_text("{}", encoding="utf-8")
    art = tmp_path / "art.html"
    art.write_text("<html></html>", encoding="utf-8")

    # Receipt is scalar string instead of dict
    with pytest.raises(TypeError, match="Receipt must be a dict"):
        build_manifest(tmp_path, doc, cand, art, "scalar-receipt")

    # Receipt is integer
    with pytest.raises(TypeError, match="Receipt must be a dict"):
        build_manifest(tmp_path, doc, cand, art, 123)

    # Document path is empty or invalid type
    with pytest.raises(TypeError, match="Document path must be a non-empty string"):
        build_manifest(tmp_path, "", cand, art, {})

    with pytest.raises(TypeError, match="Candidate path must be a non-empty string"):
        build_manifest(tmp_path, doc, 123, art, {})


def test_check_manifest_malformed_field_values(tmp_path):
    # document_path is non-string (int)
    bad_manifest1 = {
        "schema_version": 1,
        "evidence_kind": "planned",
        "document_path": 123,
        "document_digest": "a" * 64,
        "candidate_path": "cand.json",
        "candidate_digest": "b" * 64,
        "artifact_path": "art.html",
        "artifact_digest": "c" * 64,
        "source_files": {},
    }
    res1 = check_manifest(tmp_path, bad_manifest1)
    assert res1["status"] == "invalid"
    assert any("must be strings" in r for r in res1["reasons"])

    # document_digest is not 64-hex
    bad_manifest2 = {
        "schema_version": 1,
        "evidence_kind": "planned",
        "document_path": "doc.md",
        "document_digest": "not-64-hex",
        "candidate_path": "cand.json",
        "candidate_digest": "b" * 64,
        "artifact_path": "art.html",
        "artifact_digest": "c" * 64,
        "source_files": {},
    }
    res2 = check_manifest(tmp_path, bad_manifest2)
    assert res2["status"] == "invalid"
    assert any("must be 64-hex" in r for r in res2["reasons"])

    # source_paths is non-list
    bad_manifest3 = {
        "schema_version": 1,
        "evidence_kind": "planned",
        "document_path": "doc.md",
        "document_digest": "a" * 64,
        "candidate_path": "cand.json",
        "candidate_digest": "b" * 64,
        "artifact_path": "art.html",
        "artifact_digest": "c" * 64,
        "source_paths": "not-a-list",
        "source_files": {},
    }
    res3 = check_manifest(tmp_path, bad_manifest3)
    assert res3["status"] == "invalid"
    assert any("source_paths must be a list/tuple" in r for r in res3["reasons"])


def test_check_manifest_source_paths_traversal(tmp_path):
    doc = tmp_path / "doc.md"
    doc.write_text("# Spec\n", encoding="utf-8")
    cand = tmp_path / "cand.json"
    cand.write_text("{}", encoding="utf-8")
    art = tmp_path / "art.html"
    art.write_text("<html></html>", encoding="utf-8")

    # source_paths contains escaping traversal
    manifest = {
        "schema_version": 1,
        "evidence_kind": "planned",
        "document_path": "doc.md",
        "document_digest": hashlib.sha256(b"# Spec\n").hexdigest(),
        "candidate_path": "cand.json",
        "candidate_digest": hashlib.sha256(b"{}").hexdigest(),
        "artifact_path": "art.html",
        "artifact_digest": hashlib.sha256(b"<html></html>").hexdigest(),
        "source_paths": ["../escaped.py"],
        "source_files": {},
    }
    res = check_manifest(tmp_path, manifest)
    assert res["status"] == "invalid"
    assert any("Invalid source_paths" in r for r in res["reasons"])


def test_check_manifest_git_timeout(tmp_path, monkeypatch):
    doc = tmp_path / "doc.md"
    doc.write_text("# Spec\n", encoding="utf-8")
    cand = tmp_path / "cand.json"
    cand.write_text("{}", encoding="utf-8")
    art = tmp_path / "art.html"
    art.write_text("<html></html>", encoding="utf-8")

    manifest = {
        "schema_version": 1,
        "evidence_kind": "committed",
        "revision": "a" * 40,
        "document_path": "doc.md",
        "document_digest": hashlib.sha256(b"# Spec\n").hexdigest(),
        "candidate_path": "cand.json",
        "candidate_digest": hashlib.sha256(b"{}").hexdigest(),
        "artifact_path": "art.html",
        "artifact_digest": hashlib.sha256(b"<html></html>").hexdigest(),
        "source_files": {},
    }

    def mock_run(*args, **kwargs):
        raise subprocess.TimeoutExpired(cmd=args[0], timeout=10.0)

    monkeypatch.setattr(subprocess, "run", mock_run)

    res = check_manifest(tmp_path, manifest)
    assert res["status"] == "stale"
    assert any("timed out" in r.lower() for r in res["reasons"])


def test_source_fingerprint_unreadable_file_not_swallowed(tmp_path, monkeypatch):
    src = tmp_path / "src"
    src.mkdir()
    f = src / "unreadable.py"
    f.write_text("code", encoding="utf-8")

    real_open = open

    def mock_open(path, mode="r", *args, **kwargs):
        if "unreadable.py" in str(path) and "rb" in mode:
            raise PermissionError("Access denied to unreadable.py")
        return real_open(path, mode, *args, **kwargs)

    monkeypatch.setattr("builtins.open", mock_open)

    # source_fingerprint must raise OSError, not silently swallow it
    with pytest.raises(OSError, match="Unreadable source file.*Access denied"):
        source_fingerprint(tmp_path)

    # check_manifest caller must report invalid status
    doc = tmp_path / "doc.md"
    doc.write_text("# Spec\n", encoding="utf-8")
    cand = tmp_path / "cand.json"
    cand.write_text("{}", encoding="utf-8")
    art = tmp_path / "art.html"
    art.write_text("<html></html>", encoding="utf-8")

    manifest = {
        "schema_version": 1,
        "evidence_kind": "planned",
        "document_path": "doc.md",
        "document_digest": hashlib.sha256(b"# Spec\n").hexdigest(),
        "candidate_path": "cand.json",
        "candidate_digest": hashlib.sha256(b"{}").hexdigest(),
        "artifact_path": "art.html",
        "artifact_digest": hashlib.sha256(b"<html></html>").hexdigest(),
        "source_files": {},
    }
    check_res = check_manifest(tmp_path, manifest)
    assert check_res["status"] == "invalid"
    assert any("Unreadable source file" in r for r in check_res["reasons"])


def test_build_manifest_source_paths_generator_materialized(tmp_path):
    doc = tmp_path / "doc.md"
    doc.write_text("# Spec\n", encoding="utf-8")
    cand = tmp_path / "cand.json"
    cand.write_text("{}", encoding="utf-8")
    art = tmp_path / "art.html"
    art.write_text("<html></html>", encoding="utf-8")
    src = tmp_path / "src"
    src.mkdir()
    (src / "one.py").write_text("1", encoding="utf-8")

    # Pass a single-use generator
    paths_gen = (p for p in ["src/one.py"])
    manifest = build_manifest(tmp_path, doc, cand, art, {}, source_paths=paths_gen)

    # Verify source_paths was materialized and not emptied
    assert manifest["source_paths"] == ["src/one.py"]
    assert "src/one.py" in manifest["source_files"]


def test_check_manifest_child_files_verified_and_detects_mutation_and_escapes(tmp_path):
    doc = tmp_path / "doc.md"
    doc.write_text("# Spec\n", encoding="utf-8")
    cand = tmp_path / "cand.json"
    cand.write_text("{}", encoding="utf-8")

    arch_dir = tmp_path / "docs" / "architecture"
    arch_dir.mkdir(parents=True)
    art = arch_dir / "index.html"
    art.write_text("<html></html>", encoding="utf-8")

    child1 = arch_dir / "view1.html"
    child1.write_text("<div>v1</div>", encoding="utf-8")
    c1_hash = hashlib.sha256(b"<div>v1</div>").hexdigest()

    manifest = build_manifest(
        tmp_path, doc, cand, art, {},
        child_files={"view1.html": c1_hash},
    )
    assert check_manifest(tmp_path, manifest)["status"] == "current"

    # Mutate child file -> stale
    child1.write_text("<div>v1-mutated</div>", encoding="utf-8")
    res_mut = check_manifest(tmp_path, manifest)
    assert res_mut["status"] == "stale"
    assert any("Child file digest mismatch" in r for r in res_mut["reasons"])
    child1.write_text("<div>v1</div>", encoding="utf-8")  # restore

    # Delete child file -> stale
    child1.unlink()
    res_del = check_manifest(tmp_path, manifest)
    assert res_del["status"] == "stale"
    assert any("Child file missing" in r for r in res_del["reasons"])
    child1.write_text("<div>v1</div>", encoding="utf-8")  # restore

    # Child file escaping root -> invalid
    manifest_escaping = dict(manifest)
    manifest_escaping["child_files"] = {"../../escaped.html": c1_hash}
    res_esc = check_manifest(tmp_path, manifest_escaping)
    assert res_esc["status"] == "invalid"
    assert any("escapes" in r for r in res_esc["reasons"])

    # Child file bad digest format -> invalid
    manifest_bad_digest = dict(manifest)
    manifest_bad_digest["child_files"] = {"view1.html": "not-64-hex"}
    res_bad = check_manifest(tmp_path, manifest_bad_digest)
    assert res_bad["status"] == "invalid"
    assert any("must be 64-hex" in r for r in res_bad["reasons"])


# ---------------------------------------------------------------------------
# bind_document & check_binding tests
# ---------------------------------------------------------------------------

def test_bind_document_and_check_binding_no_self_cycle(tmp_path):
    doc = tmp_path / "doc.md"
    doc.write_text("# Design Spec\n\nSome text.\n", encoding="utf-8")

    # 1. Digest before binding
    digest_before = document_digest(doc)

    cand = tmp_path / "cand.json"
    cand.write_text('{}', encoding="utf-8")
    art = tmp_path / "art.html"
    art.write_text("<html></html>", encoding="utf-8")

    manifest = build_manifest(tmp_path, doc, cand, art, {"engine": "archify"})
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    # 2. Bind document
    bind_document(doc, manifest_path)

    # 3. Digest after binding MUST be identical (no self cycle)
    digest_after = document_digest(doc)
    assert digest_before == digest_after

    # 4. Check binding
    binding_res = check_binding(doc, manifest_path)
    assert binding_res["status"] == "current"
    assert binding_res["valid"] is True
    assert binding_res["reasons"] == []

    # 5. Tamper with manifest file -> check_binding detects mismatch
    manifest_path.write_text('{"tampered": true}', encoding="utf-8")
    binding_res2 = check_binding(doc, manifest_path)
    assert binding_res2["status"] == "stale"
    assert binding_res2["valid"] is False
    assert any("Manifest digest mismatch" in r for r in binding_res2["reasons"])


def test_bind_document_replaces_existing_block(tmp_path):
    doc = tmp_path / "doc.md"
    doc.write_text("# Spec\n\nContent.\n", encoding="utf-8")

    cand = tmp_path / "cand.json"
    cand.write_text('{}', encoding="utf-8")
    art = tmp_path / "art.html"
    art.write_text("<html></html>", encoding="utf-8")

    manifest1 = build_manifest(tmp_path, doc, cand, art, {"version": "1"})
    m1_path = tmp_path / "m1.json"
    m1_path.write_text(json.dumps(manifest1), encoding="utf-8")

    bind_document(doc, m1_path)
    assert check_binding(doc, m1_path)["valid"] is True

    manifest2 = build_manifest(tmp_path, doc, cand, art, {"version": "2"})
    m2_path = tmp_path / "m2.json"
    m2_path.write_text(json.dumps(manifest2), encoding="utf-8")

    # Replace binding
    bind_document(doc, m2_path)
    content = doc.read_text(encoding="utf-8")
    assert content.count(BINDING_START) == 1
    assert content.count(BINDING_END) == 1
    assert check_binding(doc, m2_path)["valid"] is True


def test_check_binding_missing_document_digest_fails_closed(tmp_path):
    doc = tmp_path / "doc.md"
    doc.write_text("# Spec\n", encoding="utf-8")
    m_path = tmp_path / "manifest.json"
    # Manifest missing document_digest
    m_path.write_text(json.dumps({"schema_version": 1, "document_path": "doc.md"}), encoding="utf-8")

    bind_document(doc, m_path)
    res = check_binding(doc, m_path)
    assert res["status"] == "invalid"
    assert res["valid"] is False
    assert any("missing valid 64-hex document_digest" in r for r in res["reasons"])


def test_check_binding_document_path_mismatch_fails_closed(tmp_path):
    doc = tmp_path / "doc.md"
    doc.write_text("# Spec\n", encoding="utf-8")
    cand = tmp_path / "cand.json"
    cand.write_text("{}", encoding="utf-8")
    art = tmp_path / "art.html"
    art.write_text("<html></html>", encoding="utf-8")

    manifest = build_manifest(tmp_path, doc, cand, art, {})
    m_path = tmp_path / "manifest.json"
    m_path.write_text(json.dumps(manifest), encoding="utf-8")

    bind_document(doc, m_path)
    assert check_binding(doc, m_path)["valid"] is True

    # Another document with the exact same content and binding, but different path
    other_doc = tmp_path / "other_doc.md"
    other_doc.write_text(doc.read_text(encoding="utf-8"), encoding="utf-8")

    res = check_binding(other_doc, m_path)
    assert res["status"] == "stale"
    assert res["valid"] is False
    assert any("Document path mismatch" in r for r in res["reasons"])


# ---------------------------------------------------------------------------
# publish_bundle tests
# ---------------------------------------------------------------------------

def test_publish_bundle_requires_index_and_manifest(tmp_path):
    staging = tmp_path / "staging"
    staging.mkdir()
    dest = tmp_path / "docs" / "architecture"

    # Empty staging
    with pytest.raises(ValueError, match="missing required"):
        publish_bundle(staging, dest)

    # Only index.html
    (staging / "index.html").write_text("<html></html>", encoding="utf-8")
    with pytest.raises(ValueError, match="missing required"):
        publish_bundle(staging, dest)


def test_publish_bundle_validates_hashes_fail_closed(tmp_path):
    staging = tmp_path / "staging"
    staging.mkdir()
    dest = tmp_path / "dest"
    dest.mkdir(parents=True)
    (dest / "index.html").write_text("original good", encoding="utf-8")

    (staging / "index.html").write_text("new content", encoding="utf-8")
    # Manifest has bad hash
    bad_manifest = {
        "schema_version": 1,
        "artifact_digest": "0" * 64,
    }
    (staging / "manifest.json").write_text(json.dumps(bad_manifest), encoding="utf-8")

    with pytest.raises(ValueError, match="[Hh]ash mismatch"):
        publish_bundle(staging, dest)

    # Destination preserved: last good untouched!
    assert (dest / "index.html").read_text(encoding="utf-8") == "original good"


def test_publish_bundle_missing_artifact_digest_fails_closed(tmp_path):
    staging = tmp_path / "staging"
    staging.mkdir()
    (staging / "index.html").write_text("content", encoding="utf-8")
    # manifest without artifact_digest
    (staging / "manifest.json").write_text(json.dumps({"schema_version": 1}), encoding="utf-8")

    dest = tmp_path / "dest"
    with pytest.raises(ValueError, match="missing required valid 64-hex artifact_digest"):
        publish_bundle(staging, dest)


def test_publish_bundle_staging_manifest_scalar_crashes_prevented(tmp_path):
    staging = tmp_path / "staging"
    staging.mkdir()
    (staging / "index.html").write_text("content", encoding="utf-8")
    (staging / "manifest.json").write_text("123", encoding="utf-8")

    dest = tmp_path / "dest"
    with pytest.raises(ValueError, match="must be a JSON object"):
        publish_bundle(staging, dest)


def test_publish_bundle_rejects_symlinks(tmp_path):
    staging = tmp_path / "staging"
    staging.mkdir()
    (staging / "index.html").write_text("<html></html>", encoding="utf-8")
    (staging / "manifest.json").write_text('{"schema_version": 1}', encoding="utf-8")

    target = tmp_path / "target.txt"
    target.write_text("target", encoding="utf-8")
    link = staging / "link.txt"
    try:
        os.symlink(target, link)
    except OSError:
        pytest.skip("Symlinks not supported")

    dest = tmp_path / "dest"
    with pytest.raises(ValueError, match="[Ss]ymlink"):
        publish_bundle(staging, dest)


def test_publish_bundle_rejects_nesting(tmp_path):
    staging = tmp_path / "staging"
    staging.mkdir()
    nested_dest = staging / "sub" / "dest"
    (staging / "index.html").write_text("<html></html>", encoding="utf-8")
    (staging / "manifest.json").write_text('{"schema_version": 1}', encoding="utf-8")

    with pytest.raises(ValueError, match="nested"):
        publish_bundle(staging, nested_dest)


def test_publish_bundle_success_and_preserves_last_good(tmp_path):
    staging = tmp_path / "staging"
    staging.mkdir()
    html_content = "<html>v1</html>"
    (staging / "index.html").write_text(html_content, encoding="utf-8")
    manifest = {
        "schema_version": 1,
        "artifact_digest": hashlib.sha256(html_content.encode("utf-8")).hexdigest(),
    }
    (staging / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")

    dest = tmp_path / "docs" / "architecture"
    res = publish_bundle(staging, dest)
    assert res == dest / "index.html"
    assert (dest / "index.html").read_text(encoding="utf-8") == html_content
    assert (dest / "manifest.json").exists()

    # Now publish v2 with hash failure: v1 remains intact
    staging2 = tmp_path / "staging2"
    staging2.mkdir()
    (staging2 / "index.html").write_text("<html>v2</html>", encoding="utf-8")
    bad_manifest = {
        "schema_version": 1,
        "artifact_digest": "bad_hash",
    }
    (staging2 / "manifest.json").write_text(json.dumps(bad_manifest), encoding="utf-8")

    with pytest.raises(ValueError):
        publish_bundle(staging2, dest)

    # v1 is still preserved!
    assert (dest / "index.html").read_text(encoding="utf-8") == "<html>v1</html>"


def test_publish_bundle_safe_lock_does_not_delete_unknown(tmp_path):
    staging = tmp_path / "staging"
    staging.mkdir()
    (staging / "index.html").write_text("<html></html>", encoding="utf-8")
    m = {
        "schema_version": 1,
        "artifact_digest": hashlib.sha256(b"<html></html>").hexdigest(),
    }
    (staging / "manifest.json").write_text(json.dumps(m), encoding="utf-8")

    dest = tmp_path / "dest"
    dest.mkdir(parents=True)
    lock_file = dest.parent / f".{dest.name}.lock"

    # Write unknown lock (e.g. from foreign host or invalid PID)
    foreign_lock = {
        "pid": 999999,
        "host": "foreign-host-1234",
        "time": time.time(),
    }
    lock_file.write_text(json.dumps(foreign_lock), encoding="utf-8")

    with pytest.raises((TimeoutError, RuntimeError)):
        publish_bundle(staging, dest)

    # Unknown lock must NOT have been deleted!
    assert lock_file.exists()


def test_publish_bundle_concurrency_lock(tmp_path):
    staging = tmp_path / "staging"
    staging.mkdir()
    (staging / "index.html").write_text("<html></html>", encoding="utf-8")
    m = {
        "schema_version": 1,
        "artifact_digest": hashlib.sha256(b"<html></html>").hexdigest(),
    }
    (staging / "manifest.json").write_text(json.dumps(m), encoding="utf-8")

    dest = tmp_path / "dest"
    dest.mkdir(parents=True)
    lock_file = dest.parent / f".{dest.name}.lock"

    # Active lock with current PID
    active_lock = {
        "pid": os.getpid(),
        "host": platform.node(),
        "time": time.time(),
    }
    lock_file.write_text(json.dumps(active_lock), encoding="utf-8")

    # Trying to publish should fail due to lock contention
    with pytest.raises(TimeoutError, match="lock held by existing process"):
        publish_bundle(staging, dest, timeout=0.1)

    # Lock owned by active PID is preserved
    assert lock_file.exists()


def test_publish_bundle_rollback_on_swap_failure(tmp_path, monkeypatch):
    staging = tmp_path / "staging"
    staging.mkdir()
    html_content = "<html>original good</html>"
    (staging / "index.html").write_text(html_content, encoding="utf-8")
    manifest = {
        "schema_version": 1,
        "artifact_digest": hashlib.sha256(html_content.encode("utf-8")).hexdigest(),
    }
    (staging / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")

    dest = tmp_path / "dest"
    publish_bundle(staging, dest)
    assert (dest / "index.html").read_text(encoding="utf-8") == html_content

    # Stage v2
    staging2 = tmp_path / "staging2"
    staging2.mkdir()
    v2_html = "<html>v2 content</html>"
    (staging2 / "index.html").write_text(v2_html, encoding="utf-8")
    m2 = {
        "schema_version": 1,
        "artifact_digest": hashlib.sha256(v2_html.encode("utf-8")).hexdigest(),
    }
    (staging2 / "manifest.json").write_text(json.dumps(m2), encoding="utf-8")

    # Simulate failure on the second os.replace (the temp_dest -> dest swap)
    real_replace = os.replace
    call_count = 0

    def mock_replace(src, dst):
        nonlocal call_count
        call_count += 1
        if call_count == 2:
            raise OSError("Simulated filesystem error during atomic swap")
        return real_replace(src, dst)

    monkeypatch.setattr(os, "replace", mock_replace)

    with pytest.raises(RuntimeError, match="rolled back to last good"):
        publish_bundle(staging2, dest)

    # Destination was restored to original good by rollback
    assert (dest / "index.html").read_text(encoding="utf-8") == html_content


def test_publish_bundle_rollback_failure_preserves_backup_and_reports_path(tmp_path, monkeypatch):
    staging = tmp_path / "staging"
    staging.mkdir()
    html_content = "<html>original good</html>"
    (staging / "index.html").write_text(html_content, encoding="utf-8")
    manifest = {
        "schema_version": 1,
        "artifact_digest": hashlib.sha256(html_content.encode("utf-8")).hexdigest(),
    }
    (staging / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")

    dest = tmp_path / "dest"
    publish_bundle(staging, dest)

    # Stage v2
    staging2 = tmp_path / "staging2"
    staging2.mkdir()
    v2_html = "<html>v2 content</html>"
    (staging2 / "index.html").write_text(v2_html, encoding="utf-8")
    m2 = {
        "schema_version": 1,
        "artifact_digest": hashlib.sha256(v2_html.encode("utf-8")).hexdigest(),
    }
    (staging2 / "manifest.json").write_text(json.dumps(m2), encoding="utf-8")

    real_replace = os.replace
    call_count = 0

    def mock_replace(src, dst):
        nonlocal call_count
        call_count += 1
        # Call 1: dest -> backup (allow)
        # Call 2: temp -> dest (fail swap)
        # Call 3: backup -> dest (fail rollback too)
        if call_count >= 2:
            raise OSError(f"Simulated replace failure #{call_count}")
        return real_replace(src, dst)

    monkeypatch.setattr(os, "replace", mock_replace)

    with pytest.raises(RuntimeError, match="Backup preserved at"):
        publish_bundle(staging2, dest)

    # Verify backup directories exist and were preserved (not deleted)
    backup_dirs = list(dest.parent.glob(f".{dest.name}.bak.*"))
    assert len(backup_dirs) >= 1
    assert any(b.is_dir() for b in backup_dirs)


def test_source_fingerprint_explicit_paths_directory_preserves_exclusions(tmp_path):
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()
    (docs_dir / "guide.md").write_text("# Guide", encoding="utf-8")

    # Excluded subdirectories under docs
    arch_dir = docs_dir / "architecture"
    arch_dir.mkdir()
    (arch_dir / "index.html").write_text("html", encoding="utf-8")

    tdq_dir = docs_dir / "tdq"
    tdq_dir.mkdir()
    (tdq_dir / "state.json").write_text("{}", encoding="utf-8")

    fp = source_fingerprint(tmp_path, paths=["docs"])
    assert "docs/guide.md" in fp
    assert "docs/architecture/index.html" not in fp
    assert "docs/tdq/state.json" not in fp


def test_check_manifest_explicit_source_deleted_is_stale_not_invalid(tmp_path):
    doc = tmp_path / "doc.md"
    doc.write_text("# Spec\n", encoding="utf-8")
    cand = tmp_path / "cand.json"
    cand.write_text("{}", encoding="utf-8")
    art = tmp_path / "art.html"
    art.write_text("<html></html>", encoding="utf-8")

    src = tmp_path / "src"
    src.mkdir()
    target_file = src / "temp.py"
    target_file.write_text("code = 1\n", encoding="utf-8")

    manifest = build_manifest(tmp_path, doc, cand, art, {}, source_paths=["src/temp.py"])
    assert check_manifest(tmp_path, manifest)["status"] == "current"

    # Delete the explicit source file
    target_file.unlink()

    # Must be stale, not invalid
    res = check_manifest(tmp_path, manifest)
    assert res["status"] == "stale"
    assert any("Source file deleted: src/temp.py" in r for r in res["reasons"])


# ---------------------------------------------------------------------------
# mark_stale tests
# ---------------------------------------------------------------------------

def test_mark_stale_absent_skips(tmp_path):
    res = mark_stale(tmp_path)
    assert res["status"] in ("skip", "skipped")
    # No status.json written
    assert not (tmp_path / "docs" / "architecture" / "status.json").exists()


def test_mark_stale_records_freshness_without_modifying_manifest(tmp_path):
    arch_dir = tmp_path / "docs" / "architecture"
    arch_dir.mkdir(parents=True)

    doc = tmp_path / "doc.md"
    doc.write_text("# Spec\n", encoding="utf-8")
    cand = tmp_path / "cand.json"
    cand.write_text('{}', encoding="utf-8")
    art = arch_dir / "index.html"
    art.write_text("<html></html>", encoding="utf-8")

    manifest = build_manifest(tmp_path, doc, cand, art, {"engine": "archify"})
    manifest_path = arch_dir / "manifest.json"
    manifest_raw = json.dumps(manifest, indent=2)
    manifest_path.write_text(manifest_raw, encoding="utf-8")

    res = mark_stale(tmp_path)
    assert res["status"] == "current"

    status_file = arch_dir / "status.json"
    assert status_file.exists()
    status_data = json.loads(status_file.read_text(encoding="utf-8"))
    assert status_data["status"] == "current"

    # manifest.json is NOT modified
    assert manifest_path.read_text(encoding="utf-8") == manifest_raw

    # Now modify document -> mark_stale records stale
    doc.write_text("# Modified\n", encoding="utf-8")
    res2 = mark_stale(tmp_path)
    assert res2["status"] == "stale"
    status_data2 = json.loads(status_file.read_text(encoding="utf-8"))
    assert status_data2["status"] == "stale"
    assert any("Document digest mismatch" in r for r in status_data2["reasons"])
