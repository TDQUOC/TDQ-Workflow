#!/usr/bin/env python3
"""codex_edit_gate.py — the bridge between Codex `apply_patch` and the shared `edit_gate.py`.

This is the real SOURCE file, edit it here. `scripts/build_portable.py` only READS it as
data and copies it into the bundle — it never imports this file, because importing a hook
is running it.

Why it is needed: Claude Code sends `tool_input.file_path`, while Codex sends
`tool_input.command` holding the whole patch body (`*** Update File: <path>`). `edit_gate.py`
reads `file_path`, so running it straight under Codex yields an empty path — the gate exits 0
while guarding nothing at all, a silent failure.

Its second job: the EARLY fence of mode `codex`. Inside a `codex exec` turn driven by the
workflow, the marker variable `TDQ_CODEX_TASK` is set, and `TDQ_CODEX_VUNG` / `TDQ_CODEX_KHOA`
declare the file zone Codex may write and the zone it must not touch. A write path landing
outside the zone, or inside the locked zone, returns `permissionDecision: deny` with the
code `[TDQ:VUNG]`.

Three deliberate limits, written down so nobody later "fixes" them by mistake:
- With NO marker variable it never denies. A `codex` session the user runs on their own is
  none of this hook's business.
- With the marker but no declared zone it warns and lets the call through instead of denying
  everything. This hook is only the early layer; the deciding layer is the `git diff` audit in
  `tdq_vungfile.py`. A hook that blocks harmless commands whenever configuration is missing
  gets switched off, and then its correct half is lost too.
- Standard library only, no import of `_common`/`tdq_state`. This hook runs inside the Codex
  sandbox, where `scripts/` may not load; it calls `edit_gate.py` as a sub-process.

Env: TDQ_LOG=0 turns the log off (it goes to stderr). Exit code and stdout come straight
from `edit_gate.py`.
"""
import datetime
import json
import os
import re
import subprocess
import sys

MAU_PATCH = re.compile(r"^\*\*\* (?:Update|Add|Delete) File: (.+)$", re.MULTILINE)

# The mode's marker variable plus the two zone variables. No name carries KEY/TOKEN/SECRET,
# because Codex strips variables that look like secrets before handing them to a shell command
# (measured during the research phase).
BIEN_MOC = "TDQ_CODEX_TASK"
BIEN_VUNG = "TDQ_CODEX_VUNG"
BIEN_KHOA = "TDQ_CODEX_KHOA"
MA_VUNG = "TDQ:VUNG"

# Writing by redirection: `> f` and `>> f`. `(?<![0-9&])` skips `2>` and `>&2` — those are
# stream redirections, not file writes. Heredocs need no rule of their own: `cat <<EOF > f`
# and `cat > f <<EOF` each carry exactly one `> f`, and this rule catches both.
MAU_GHI = re.compile(r"(?<![0-9&])>>?\s*([^\s;&|<>()]+)")
# `tee` and `mv`: take EVERY non-flag argument up to the next shell operator. For `mv` both
# source and destination count as changes — a source file disappearing is also touching it.
MAU_THAM_SO = re.compile(r"\b(tee|mv)\b((?:\s+(?:-[^\s;&|<>]+|[^\s;&|<>()-][^\s;&|<>()]*))+)")
KHONG_PHAI_FILE = ("/dev/null", "/dev/stdout", "/dev/stderr")


def log(message):
    if os.environ.get("TDQ_LOG", "1") != "0":
        stamp = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
        print(f"[{stamp}] {message}", file=sys.stderr)


def tach_duong_dan_patch(than):
    """The FIRST path in the patch body, or an empty string. Never raises on odd input."""
    khop = MAU_PATCH.search(than or "")
    return khop.group(1).strip() if khop else ""


def tach_moi_duong_patch(than):
    """EVERY path in the patch body — a deny must look at all of them, not just the first."""
    return [d.strip() for d in MAU_PATCH.findall(than or "") if d.strip()]


def tach_duong_ghi_shell(lenh):
    """The paths a shell command WRITES, for the five shapes `>`, `>>`, heredoc, `tee`, `mv`.

    Deliberately over-inclusive rather than under-inclusive: one path too many only makes the
    hook ask again, while one path too few lets Codex write outside the zone with nobody
    seeing it until the audit.
    """
    lenh = lenh or ""
    duong = [d for d in MAU_GHI.findall(lenh)]
    for _ten, phan in MAU_THAM_SO.findall(lenh):
        duong.extend(t for t in phan.split() if not t.startswith("-"))
    ra = []
    for d in duong:
        d = d.strip().strip("'\"")
        if d and d not in KHONG_PHAI_FILE and not d.startswith("&") and d not in ra:
            ra.append(d)
    return ra


def duong_ghi(payload):
    """Every path this payload intends to write, whichever tool it arrived through."""
    tool_input = payload.get("tool_input") or {}
    if tool_input.get("file_path"):
        return [tool_input["file_path"]]
    than = tool_input.get("command") or ""
    if MAU_PATCH.search(than):
        return tach_moi_duong_patch(than)
    return tach_duong_ghi_shell(than)


def _chuan(duong, goc):
    """Normalise every path to repo-relative with `/` separators, so comparisons speak one language."""
    d = os.path.normpath(duong)
    if os.path.isabs(d) and goc:
        try:
            tuong_doi = os.path.relpath(d, goc)
        except ValueError:
            return d.replace(os.sep, "/")
        if not tuong_doi.startswith(".."):
            d = tuong_doi
    return d.replace(os.sep, "/").rstrip("/")


def _doc_ds(ten_bien, goc):
    raw = os.environ.get(ten_bien) or ""
    try:
        ds = json.loads(raw) if raw.strip() else []
    except ValueError:
        ds = [phan for phan in raw.split(os.pathsep) if phan]
    return [_chuan(d, goc) for d in ds if str(d).strip()]


def thuoc(duong, vung):
    """A path is inside the zone when it IS an entry, or sits under a directory entry."""
    return any(duong == v or duong.startswith(v + "/") for v in vung)


def pham_vung(duong, vung, khoa):
    """The reason to block, or an empty string when this path may be written.

    The locked zone is checked FIRST: a test file sitting inside the file zone is still
    off limits, and that is exactly the case where the order of the checks decides
    right from wrong.
    """
    if thuoc(duong, khoa):
        # deny reason read by the Codex turn, in the document language
        return f"`{duong}` nằm trong VÙNG KHOÁ của task — Codex không được sửa file test"  # i18n-allow
    if not thuoc(duong, vung):
        # deny reason read by the Codex turn, in the document language
        return f"`{duong}` nằm ngoài VÙNG FILE đã khai cho task"  # i18n-allow
    return ""


def deny(ly_do):
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": f"[{MA_VUNG}] {ly_do} — "
                                        # deny tail read by the Codex turn
                                        "sửa đúng file trong vùng, hoặc báo leader nới vùng.",  # i18n-allow
        }
    }, ensure_ascii=False))


def kiem_vung(payload):
    """The blocking reason for this payload, or empty when the zone fence has no say."""
    if not os.environ.get(BIEN_MOC):
        return ""  # outside a workflow-driven Codex turn this hook is not the host
    goc = payload.get("cwd") or os.getcwd()
    vung = _doc_ds(BIEN_VUNG, goc)
    khoa = _doc_ds(BIEN_KHOA, goc)
    if not vung:
        log("codex_edit_gate: marker variable set but no VÙNG FILE declared — warning only, "  # i18n-allow: canonical zone name
            "the git diff audit stays the deciding layer")
        return ""
    for duong in duong_ghi(payload):
        ly_do = pham_vung(_chuan(duong, goc), vung, khoa)
        if ly_do:
            return ly_do
    return ""


def main():
    raw = sys.stdin.read()
    try:
        payload = json.loads(raw) if raw.strip() else {}
    except ValueError:
        # A broken payload must not block the session: the gate is a reminder, not a security mechanism.
        log("codex_edit_gate: payload is not JSON, skipping")
        print("{}")
        return 0
    ly_do = kiem_vung(payload)
    if ly_do:
        log(f"codex_edit_gate: DENY — {ly_do}")
        deny(ly_do)
        return 0
    tool_input = payload.get("tool_input") or {}
    if not tool_input.get("file_path"):
        duong = tach_duong_dan_patch(tool_input.get("command"))
        if duong:
            tool_input["file_path"] = duong
            payload["tool_input"] = tool_input
            log(f"codex_edit_gate: apply_patch -> {duong}")
        else:
            log("codex_edit_gate: could not extract a path from the patch body")
    that = os.path.join(os.path.dirname(os.path.abspath(__file__)), "edit_gate.py")
    # encoding is spelled out: the deny reason carries Vietnamese, and a Windows host would
    # otherwise decode it with the ANSI code page and hand back mojibake.
    proc = subprocess.run([sys.executable, that], input=json.dumps(payload),
                          capture_output=True, text=True, encoding="utf-8")
    sys.stdout.write(proc.stdout)
    sys.stderr.write(proc.stderr)
    return proc.returncode


if __name__ == "__main__":
    sys.exit(main())
