#!/usr/bin/env python3
"""File zone, locked zone and the undo mark — the fence of mode `codex implement`.

The problem: the leader hands one task to an outside agent (Codex) to write code, and that
agent can write anywhere in the repo. Three notions build the fence:

- **The mark** (`chup_moc`): a snapshot of the working tree RIGHT BEFORE the task. Every later
  comparison uses this mark, never `HEAD` — the previous task usually left uncommitted work, and
  comparing against `HEAD` would blame that work on this task.
- **The file zone** (`hau_kiem`): the set of paths the task may touch. One stray file is a FAIL,
  and the file is named.
- **The locked zone** (`dung_vung_khoa`): the subset that must NOT be touched even though it sits
  inside the file zone — at minimum the task's own test file. The red→green beat only means
  something while whoever makes it green cannot edit the measuring stick.

The undo uses `git restore --source=<sha> --worktree`. `git checkout <sha> -- <file>` is banned:
it writes the index too, blinding the next task's audit.

Env: TDQ_LOG=0 turns the log off (the log goes to stderr).
"""
import argparse
import datetime
import json
import os
import subprocess
import sys

EXIT_LECH = 3


# ----------------------------------------------------------------- log service

def _log_enabled():
    return os.environ.get("TDQ_LOG", "1") != "0"


def log(message):
    """Write progress to stderr with a timestamp. Turn it off with TDQ_LOG=0."""
    if _log_enabled():
        stamp = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
        print(f"[{stamp}] tdq_vungfile: {message}", file=sys.stderr)


# ----------------------------------------------------------------------- git

def _git(cwd, *args, check=True):
    proc = subprocess.run(["git", *args], cwd=cwd, capture_output=True,
                          text=True, encoding="utf-8", timeout=120,
                          stdin=subprocess.DEVNULL)
    if check and proc.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)}: {proc.stderr.strip()}")
    return proc.stdout


def _dong(text):
    return [d for d in text.splitlines() if d.strip()]


# --------------------------------------------------------------------- mark

class Moc:
    """A snapshot of the working tree before a task.

    `sha` is what every comparison rests on; `chua_theo_doi` must ride along because `git stash
    create` does NOT wrap untracked files, so without remembering them separately a file the
    previous task just created would be counted against the next one.
    """

    __slots__ = ("sha", "chua_theo_doi")

    def __init__(self, sha, chua_theo_doi):
        self.sha = sha
        self.chua_theo_doi = tuple(sorted(chua_theo_doi))

    def as_dict(self):
        return {"sha": self.sha, "chua_theo_doi": list(self.chua_theo_doi)}

    @classmethod
    def from_dict(cls, d):
        return cls(d["sha"], d.get("chua_theo_doi", []))

    def __repr__(self):
        return f"Moc(sha={self.sha[:8]}, chua_theo_doi={len(self.chua_theo_doi)})"


def _file_chua_theo_doi(cwd):
    return _dong(_git(cwd, "ls-files", "--others", "--exclude-standard"))


def chup_moc(cwd="."):
    """-> Moc. On a CLEAN tree `git stash create` returns an empty string — fall back to `HEAD`.

    This is the main trap: skip that branch and `sha` stays empty, so every later `git diff`
    compares against an empty string and silently PASSes everything.
    """
    sha = _git(cwd, "stash", "create").strip()
    if not sha:
        sha = _git(cwd, "rev-parse", "HEAD").strip()
        log(f"chup-moc: clean tree → falling back to HEAD {sha[:8]}")
    else:
        log(f"chup-moc: dirty tree → stash sha {sha[:8]}")
    chua = _file_chua_theo_doi(cwd)
    log(f"chup-moc: {len(chua)} untracked file(s) at snapshot time")
    return Moc(sha, chua)


# ---------------------------------------------------------------- zone audit

class KetQua:
    """The audit result. `dat` is False when a file strayed OR the locked zone was touched."""

    __slots__ = ("dat", "lech", "khoa_bi_cham")

    def __init__(self, lech, khoa_bi_cham):
        self.lech = tuple(sorted(lech))
        self.khoa_bi_cham = tuple(sorted(khoa_bi_cham))
        self.dat = not self.lech and not self.khoa_bi_cham

    def as_dict(self):
        return {"dat": self.dat, "lech": list(self.lech),
                "khoa_bi_cham": list(self.khoa_bi_cham)}


def _chuan(duong):
    return os.path.normpath(duong).replace(os.sep, "/")


def dung_vung_khoa(file_test, them=None):
    """A task's locked zone ALWAYS contains that task's test file.

    When the caller forgets, this function remembers — which is why it exists instead of every
    call site stitching the list together itself.
    """
    khoa = {_chuan(file_test)} if file_test else set()
    khoa.update(_chuan(d) for d in (them or []))
    return sorted(khoa)


def hau_kiem(cwd, moc, vung_file, vung_khoa=None):
    """Compare the current tree with the MARK (never with HEAD) -> KetQua.

    Two sources of change must be added up: `git diff` against the mark's sha for tracked files,
    and the DIFFERENCE of the two untracked sets for files this task created.
    """
    vung = {_chuan(d) for d in vung_file}
    khoa = {_chuan(d) for d in (vung_khoa or [])}

    da_doi = {_chuan(d) for d in _dong(_git(cwd, "diff", "--name-only", moc.sha))}
    moi = {_chuan(d) for d in _file_chua_theo_doi(cwd)} - set(moc.chua_theo_doi)
    cham = da_doi | moi

    lech = sorted(cham - vung)
    khoa_bi_cham = sorted(cham & khoa)
    kq = KetQua(lech, khoa_bi_cham)
    if kq.dat:
        log(f"hau-kiem: PASS — {len(cham)} file(s) touched, all inside the zone")
    else:
        log(f"hau-kiem: STRAY — outside the zone {lech} · locked zone touched {khoa_bi_cham}")
    return kq


# ---------------------------------------------------------------------- undo

def hoan_tac(cwd, moc, file_lech):
    """Put every stray file back to its content at the mark, WITHOUT touching the index.

    Tracked file: `git restore --source=<sha> --worktree`. A file this task created (absent from
    the mark): delete it. A file inside the task's zone is one the caller must not pass in here —
    this function guesses nothing on its own.
    """
    da_xoa, da_tra = [], []
    for duong in file_lech:
        duong = _chuan(duong)
        # Presence in the mark decides "restore" versus "delete"; cat-file -e returns non-zero
        # when the path does not exist at that sha, hence check=False.
        proc = subprocess.run(["git", "cat-file", "-e", f"{moc.sha}:{duong}"],
                              cwd=cwd, capture_output=True, text=True,
                              encoding="utf-8", timeout=60,
                              stdin=subprocess.DEVNULL)
        if proc.returncode == 0:
            _git(cwd, "restore", "--source", moc.sha, "--worktree", "--", duong)
            da_tra.append(duong)
        else:
            thuc = os.path.join(cwd, duong)
            if os.path.exists(thuc):
                os.unlink(thuc)
            da_xoa.append(duong)
    log(f"hoan-tac: restored to the mark {da_tra} · deleted new file(s) {da_xoa}")
    return {"da_tra": da_tra, "da_xoa": da_xoa}


# ----------------------------------------------------------------------- CLI

def cli(argv=None):
    p = argparse.ArgumentParser(prog="tdq_vungfile.py", description=__doc__.split("\n")[0])
    p.add_argument("-C", "--cwd", default=".", help="repo root (default: the current directory)")
    sub = p.add_subparsers(dest="lenh", required=True)

    sub.add_parser("chup-moc", help="snapshot the mark before a task, printing JSON to stdout")

    hk = sub.add_parser("hau-kiem", help="compare the current tree with the mark")
    hk.add_argument("--moc", required=True, help="the mark as JSON (a string or @path)")
    hk.add_argument("--vung", nargs="*", default=[], help="the file zone the task may touch")
    hk.add_argument("--khoa", nargs="*", default=[], help="the locked zone, not to be touched")

    ht = sub.add_parser("hoan-tac", help="put stray files back to their content at the mark")
    ht.add_argument("--moc", required=True)
    ht.add_argument("--file", nargs="+", required=True)

    a = p.parse_args(argv)

    if a.lenh == "chup-moc":
        print(json.dumps(chup_moc(a.cwd).as_dict(), ensure_ascii=False))
        return 0

    moc = Moc.from_dict(_doc_json(a.moc))
    if a.lenh == "hau-kiem":
        kq = hau_kiem(a.cwd, moc, a.vung, a.khoa)
        print(json.dumps(kq.as_dict(), ensure_ascii=False))
        return 0 if kq.dat else EXIT_LECH
    print(json.dumps(hoan_tac(a.cwd, moc, a.file), ensure_ascii=False))
    return 0


def _doc_json(raw):
    if raw.startswith("@"):
        with open(raw[1:], encoding="utf-8") as f:
            return json.load(f)
    return json.loads(raw)


if __name__ == "__main__":
    sys.exit(cli())
