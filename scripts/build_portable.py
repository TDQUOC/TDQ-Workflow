#!/usr/bin/env python3
"""build_portable.py — generate the three portable bundles of TDQ Workflow from ONE source.

Why this file exists: the old `portable/` bundle was written by hand, its own README said
"Not generated — after editing `skills/` remember to sync by hand", and the test that locked
the sync was deleted back in 0.10.0. A hand-written bundle always rots over time. Generating
it by machine is the only way to keep the portable bundle correct.

Three targets, one source (`skills/`, `hooks/`, `agents/`, `scripts/`):

    portable_claude/  — for Claude Code: `.claude/skills`, `.claude/agents`,
                        `.claude/settings.json` (hooks), `.mcp.json`, `scripts/`.
                        Every `${CLAUDE_PLUGIN_ROOT}` becomes `${CLAUDE_PROJECT_DIR}`
                        because that variable ONLY exists when running as a registered plugin.
    portable_codex/   — for Codex CLI >= 0.147.0, using its three native layers exactly:
                        `.agents/skills/`, `.codex/config.toml` (MCP), `.codex/hooks.json`
                        + `hooks/`. Plus `AGENTS.md` + `workflow/NN-*.md` as the fallback
                        for any OTHER harness that can only read markdown.
    antigravity_portable/ — for Antigravity CLI (agy): a plugin directory copied to
                        `~/.gemini/config/plugins/tdq-workflow/` — `plugin.json`, `skills/`,
                        `hooks.json` (a REAL `PreToolUse` deny and a `Stop` `continue`),
                        `mcp_config.json`.

All three carry a `manifest.json` (file+sha256, version, minimum python, external commands, MCP)
so `tdq_checkportable.py` on the target machine can check and patch itself.

Usage:
    python3 scripts/build_portable.py                    # generate all three into the repo root
    python3 scripts/build_portable.py --dest /tmp/x      # generate into another folder
    python3 scripts/build_portable.py --only claude      # only one bundle

Env: TDQ_LOG=0 turns the progress log off (the log goes to stderr).
Exit: 0 done · 1 generation error · 2 bad syntax.
"""

import argparse
import datetime
import json
import os
import re
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from claude_export import plugin_version, sha256_of  # noqa: E402
# The logic that builds the two config files lives in `tdq_checkportable.py`, not here: only
# that file ships with the bundle. Importing it back keeps exactly one copy of the logic.
from tdq_checkportable import sinh_mcp, sinh_settings  # noqa: E402

EXIT_LOI = 1
EXIT_SYNTAX = 2

# Source folders carried into the portable bundle. `tests/` is deliberately absent: the bundle
# exists to run the workflow in someone else's project, not to run this repo's own tests.
SOURCE_DIRS = ("skills", "hooks", "agents", "scripts")

# Junk must never leak into the generated bundle. `docs/tdq` heads the list because it holds the
# state, brief, spec and plan of THIS source repo — shipping that elsewhere leaks internal data.
EXCLUDE_DIRS = frozenset({
    ".git", "docs", "graphify-out", "__pycache__", ".pytest_cache", ".venv",
    "tests", "node_modules", ".remember", "ClaudeExport", "claude-export",
    "portable", "portable_claude", "portable_codex",
})
EXCLUDE_FILES = frozenset({
    ".DS_Store", "state.json", ".tdq-turn.jsonl",
    # The generator itself does not ship with what it generates: it only means something in the
    # source repo, and it quotes the plugin variable verbatim, so a rewrite would break its constant.
    "build_portable.py",
    # Same for the compliance measurement suite: it only runs in the source repo, and it SETS the
    # `CLAUDE_PLUGIN_ROOT` variable for the child processes of a measured session — a rewrite would
    # change the very constant it needs kept intact.
    "tdq_eval.py",
})

# agy-specific hooks matter ONLY to the antigravity bundle. They are deliberately NOT in
# `EXCLUDE_FILES`: that set also drives `sinh_manifest`, so listing them there would ship them
# inside the agy bundle unlisted by its own manifest. Instead the claude/codex builds hand this
# set to `copy_loc(..., bo_qua_them=...)` for their wholesale `hooks/` copy — Claude Code's
# PreToolUse only ever reminds and Codex has no `Stop`-continue mechanism, so neither target can
# do anything with a hard-deny hook written against agy's own schema.
FILE_HOOK_AGY = frozenset({"agy_pretooluse_gate.py", "agy_stop_gate.py"})

MANIFEST_NAME = "manifest.json"
PYTHON_MIN = "3.8"
EXTERNAL_COMMANDS = ("git", "graphify")
MCP_SERVERS = ("tavily-primary", "tavily-backup")

BIEN_CU = "CLAUDE_PLUGIN_ROOT"
BIEN_MOI = "CLAUDE_PROJECT_DIR"


# ----------------------------------------------------------------- log service

def _log_enabled():
    return os.environ.get("TDQ_LOG", "1") != "0"


def log(message):
    """Log progress to stderr with a timestamp. Turn it off with TDQ_LOG=0."""
    if _log_enabled():
        stamp = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
        print(f"[{stamp}] {message}", file=sys.stderr)


# ------------------------------------------------------------ variable rewrite

def doi_bien_plugin_root(text, thay_bang=None):
    """`${CLAUDE_PLUGIN_ROOT}` and `$CLAUDE_PLUGIN_ROOT` → `${CLAUDE_PROJECT_DIR}`.

    `thay_bang` allows a path suffix to be appended. The claude bundle needs that: the workflow root
    sits at `.claude/tdq/`, not at the project root, so a bare `${CLAUDE_PROJECT_DIR}` would build
    a path one level short — and the script call then silently finds no file.

    Returns `(new text, number of replacements)`. The count is worth more than the result: grepping
    the generated bundle for 0 matches only proves "gone from the files ALREADY COPIED", while
    comparing the count with the number counted in the source catches a file that should have been
    copied and was not — a hook broken by an empty variable fails silently on the other machine.
    """
    dang_ngoac = "${" + BIEN_CU + "}"
    dang_tran = "$" + BIEN_CU
    moi = thay_bang or ("${" + BIEN_MOI + "}")
    so_lan = text.count(dang_ngoac)
    text = text.replace(dang_ngoac, moi)
    # Once the braced form is replaced, whatever still carries a bare `$` is the real bare form.
    so_lan += text.count(dang_tran)
    text = text.replace(dang_tran, moi)
    return text, so_lan


def dem_bien_trong_cay(goc):
    """Count every use of the plugin variable in a folder tree — the reference number for QC."""
    tong = 0
    for thu_muc, _, files in os.walk(goc):
        for ten in files:
            noi_dung = _doc_text(os.path.join(thu_muc, ten))
            if noi_dung is not None:
                tong += noi_dung.count(BIEN_CU)
    return tong


# --------------------------------------------------------------------- copy

def _bo_qua_thu_muc(ten):
    return ten in EXCLUDE_DIRS


def _bo_qua_file(ten):
    return ten in EXCLUDE_FILES or ten.endswith((".pyc", ".pyo"))


def _doc_text(path):
    """Read a file as text; return None if it is binary (left untouched so it cannot be broken)."""
    try:
        with open(path, encoding="utf-8") as f:
            return f.read()
    except (UnicodeDecodeError, OSError):
        return None


def copy_loc(nguon, dich, doi_bien=False, thay_bang=None, bo_qua_them=()):
    """Copy a folder tree through the filter, keeping the executable bit. Returns the rewrite count.

    `doi_bien=True` is only for the claude bundle: text files are rewritten as they are written and
    binary files copied as-is. Keeping the `x` bit is mandatory — without it the hook cannot run.
    `bo_qua_them` drops extra file names for THIS call only, without touching `EXCLUDE_FILES`
    (which `sinh_manifest` shares) — see `FILE_HOOK_AGY`.
    """
    so_lan_doi = 0
    for thu_muc, thu_muc_con, files in os.walk(nguon):
        thu_muc_con[:] = [d for d in thu_muc_con if not _bo_qua_thu_muc(d)]
        tuong_doi = os.path.relpath(thu_muc, nguon)
        dich_hien_tai = dich if tuong_doi == "." else os.path.join(dich, tuong_doi)
        os.makedirs(dich_hien_tai, exist_ok=True)
        for ten in files:
            if _bo_qua_file(ten) or ten in bo_qua_them:
                continue
            src = os.path.join(thu_muc, ten)
            dst = os.path.join(dich_hien_tai, ten)
            noi_dung = _doc_text(src) if doi_bien else None
            if noi_dung is None:
                shutil.copy2(src, dst)
            else:
                noi_dung, lan = doi_bien_plugin_root(noi_dung, thay_bang)
                so_lan_doi += lan
                with open(dst, "w", encoding="utf-8") as f:
                    f.write(noi_dung)
                shutil.copystat(src, dst)
    return so_lan_doi


# --------------------------------------------------------- claude bundle

# The workflow root inside the target project. NOT dumped straight into `.claude/`:
# `hooks/scripts/_common.py` finds `scripts/` via `../../scripts` relative to itself, so `hooks/`
# and `scripts/` must sit side by side under one root; `skills/` and `agents/` are the opposite —
# Claude Code scans only `.claude/skills` and `.claude/agents`. A folder of its own satisfies both.
GOC_TDQ = ".claude/tdq"

# The skill that only means something on the TARGET machine (`tdq-checkportable`) lives here and
# not in `skills/`: putting it there would make the main bundle pay for one more description in
# every session's context budget, for a skill this repo never runs.
PORTABLE_SRC = "portable_src"
TEN_BAN_CLAUDE = "portable_claude"

README_CLAUDE = """# TDQ Workflow — portable bundle for Claude Code

## Install on a new machine — follow this exact order

1. **Copy** the whole content of this folder into the root of your project, keeping
   `.claude/` and `.mcp.json` as they are.
2. **Check** before opening Claude Code:
   ```
   python3 .claude/tdq/scripts/tdq_checkportable.py check
   ```
   Read by prefix: `CLEAN` done · `MISSING` not there · `DRIFT` differs from the manifest ·
   `NOTE` something only you can do.
3. **Patch** if there is any `MISSING`/`DRIFT`: `python3 .claude/tdq/scripts/tdq_checkportable.py setup`
   (see the warning section below — it can only rebuild two files).
4. **Set the environment variables** for MCP if `check` reports them missing. The script
   deliberately does NOT do it for you and never prints a key value — it only names the
   variable.
5. **Open Claude Code** in that project. The first time it asks whether you trust this
   folder → **click yes**. Without that, the hooks and the project config have no effect.
6. **Restart the session** so the skills and agents in the new folder get scanned.
7. **Approve the MCP servers** — every server in `.mcp.json` needs one approval from you.

Once the seven steps are done, say `run the tdq-checkportable skill` so the machine runs a
final check for you.

## Three things the machine CANNOT do for you

1. **Trust the folder** — step 5 above. Only you can click it; no command-line flag in this
   bundle replaces it.
2. **Approve the MCP servers** — step 7.
3. **Restart** — step 6. Skip it and the new skills just sit there, with no error at all.

## Warning about self-patching

`setup` rebuilds exactly the two config files the bundle holds enough data to recreate:
`.claude/settings.json` (from the bundled `hooks.json`) and `.mcp.json`. Overwriting always
leaves a backup at `<file>.tdq-bak-<timestamp>`, and the `env` block you added yourself is
kept.

Any other file that is missing or has drifted is **not** invented by `setup` — it reports
`LEFT …` and exits non-zero; the only correct source is the original bundle, copy it from
there. Want a check without any change: use `check`.

## Secret keys

`.mcp.json` only records the NAMES of environment variables, never a key value. Set the
variables yourself on your own machine before using MCP.
"""


def _sinh_settings(repo, dich_settings):
    """`hooks/hooks.json` + the repo `env` block → `.claude/settings.json` of the target project."""
    cai_dat = sinh_settings(repo, os.path.join(repo, "hooks", "hooks.json"))
    duong_env = os.path.join(repo, ".claude", "settings.json")
    if os.path.isfile(duong_env):
        with open(duong_env, encoding="utf-8") as f:
            cu = json.load(f)
        if "env" in cu:
            cai_dat["env"] = cu["env"]
    cai_dat.setdefault("env", {})
    _ghi_json(dich_settings, cai_dat)
    return 0


def _ghi_json(duong, du_lieu):
    """Write JSON byte-for-byte the way `tdq_checkportable._ghi_json_co_backup` writes it.

    One newline off here is a different sha256: `setup` regenerates the file and the very next
    `check` reports DRIFT, even though the content means exactly the same thing.
    """
    with open(duong, "w", encoding="utf-8") as f:
        f.write(json.dumps(du_lieu, ensure_ascii=False, indent=2, sort_keys=True) + "\n")


def _sinh_mcp(duong):
    _ghi_json(duong, sinh_mcp())


def sinh_ban_claude(repo, dest, version=""):
    """Build `<dest>/portable_claude/` — the bundle copied straight into a Claude Code project."""
    goc = os.path.join(dest, TEN_BAN_CLAUDE)
    if os.path.isdir(goc):
        shutil.rmtree(goc)
    thu_muc_claude = os.path.join(goc, ".claude")
    tdq = os.path.join(goc, GOC_TDQ)
    moi = "${" + BIEN_MOI + "}/" + GOC_TDQ

    tong_doi = 0
    tong_doi += copy_loc(os.path.join(repo, "skills"),
                         os.path.join(thu_muc_claude, "skills"), True, moi)
    tong_doi += copy_loc(os.path.join(repo, PORTABLE_SRC, "skills"),
                         os.path.join(thu_muc_claude, "skills"), True, moi)
    tong_doi += copy_loc(os.path.join(repo, "agents"),
                         os.path.join(thu_muc_claude, "agents"), True, moi)
    tong_doi += copy_loc(os.path.join(repo, "scripts"),
                         os.path.join(tdq, "scripts"), True, moi)
    tong_doi += copy_loc(os.path.join(repo, "hooks"),
                         os.path.join(tdq, "hooks"), True, moi, FILE_HOOK_AGY)
    tong_doi += _sinh_settings(repo, os.path.join(thu_muc_claude, "settings.json"))
    _sinh_mcp(os.path.join(goc, ".mcp.json"))

    with open(os.path.join(goc, "README.md"), "w", encoding="utf-8") as f:
        f.write(README_CLAUDE)

    con_lai = dem_bien_trong_cay(goc)
    if con_lai:
        raise RuntimeError(f"the claude bundle still has {con_lai} use(s) of {BIEN_CU}")
    log(f"{TEN_BAN_CLAUDE}: rewrote {tong_doi} plugin-variable use(s), 0 left")

    ghi_manifest(goc, version)
    return goc


# ---------------------------------------------------------- codex bundle

TEN_BAN_CODEX = "portable_codex"

# Reading order, not alphabetical order: a harness with no skill system has nothing to pick the
# right file at the right moment, so the number in the file name IS the routing mechanism.
THU_TU_SKILL = (
    "tdq-conventions",
    "tdq-lsp-setup",  # read before intake: it settles the search layer every later phase uses
    "tdq-intake",
    "tdq-spec",
    "tdq-plan",
    "tdq-build",
    "tdq-checkportable",  # source in PORTABLE_SRC, not in `skills/`
    "tdq-status",
    "tdq-check-status",
)

DONG_SOUL_AGENTS = ("Soul: chất lượng > runtime > context cost · luật gốc: "  # i18n-allow
                    "`workflow/references/tdq-conventions/soul.md`")

AGENTS_MD = """# TDQ Workflow — guide for agents

{soul}

This bundle runs a pipeline with approval gates: intake → spec → plan → implement → QC →
report. Only the USER may approve, and every state change goes through `scripts/tdq_state.py`.

## Step 0 — check compatibility BEFORE anything else

```
python3 scripts/tdq_checkportable.py check
```

If it reports something missing, run `python3 scripts/tdq_checkportable.py setup`: it rebuilds
the two config files that can be recreated (`.claude/settings.json`, `.mcp.json`), always
leaves a backup at `<file>.tdq-bak-<timestamp>` before overwriting, and reports `LEFT …` for
whatever is only correct when copied from the original bundle.

The line `NOTE project is not trusted` is the most important line this command prints: while
untrusted, Codex ignores both `.codex/config.toml` and `.codex/hooks.json`, and the bundle
runs as if it were not there.

## Running on Codex CLI (>= {codex_min}) — use the native layer, no need to read `workflow/`

- `.agents/skills/` — Codex loads skills by `description` on its own, you do not pick files.
- `.codex/config.toml` — MCP servers; environment variable NAMES only, set them yourself.
- `.codex/hooks.json` + `hooks/` — machine-guarded approval gates (`SessionStart`,
  `UserPromptSubmit`, `PreToolUse` for `Bash` and `apply_patch`, `Stop`).

## Another harness — read `workflow/` in the exact numbered order

With no skill system, the number in the file name IS the routing mechanism:

{danh_sach}

Full phase table: `workflow/phases.md` (generated from the `PHASE_TABLE` constant, never
edited by hand).

## Four things the machine CANNOT do for you

1. Grant access to the project folder on the first run (`setup --trust` can do this for you).
2. Approve the hooks in the Codex UI — hooks have their own trust gate, `--trust` does NOT
   open it.
3. Approve every MCP server declared in `.codex/config.toml`.
4. Restart the session after a new instruction folder is added.
"""


README_CODEX = """# TDQ Workflow — portable bundle for Codex CLI

This bundle uses the REAL native mechanisms of Codex, not markdown read by hand:

| Layer | File in the bundle | What Codex does with it |
|---|---|---|
| Skill | `.agents/skills/<name>/SKILL.md` | scanned automatically, loaded on demand by `description` |
| MCP | `.codex/config.toml` | `[mcp_servers.<name>]`, environment variable NAMES only |
| Hook | `.codex/hooks.json` + `hooks/` | guards `SessionStart`, `UserPromptSubmit`, `PreToolUse`, `Stop` |
| Fallback | `workflow/NN-*.md` | for any OTHER markdown-only harness to read in order |

Needs Codex CLI >= {codex_min}. An older build can still use `workflow/*.md`, but gets none
of the native layers.

## Install on a new machine — follow this exact order

The order matters: **trust FIRST, run AFTER**. While the project is untrusted, Codex skips
the WHOLE `.codex/` layer — MCP is not loaded, `hooks.json` is not read, and the bundle
looks empty without a single error.

1. **Copy** the whole content of this folder into the project root.
2. **Trust the project folder** — see the three ways just below.
3. **Check**:
   ```
   python3 scripts/tdq_checkportable.py check
   ```
   The output holds one line saying whether the project is trusted yet. Read by prefix:
   `CLEAN` done · `MISSING` not there · `DRIFT` differs from the manifest · `NOTE` something
   only you can do.
4. **Patch** if there is any `MISSING`/`DRIFT`: `python3 scripts/tdq_checkportable.py setup` —
   it rebuilds the two config files that can be recreated, always leaves a backup at
   `<file>.tdq-bak-<timestamp>` before overwriting, and reports `LEFT …` for whatever is only
   correct when copied from the original bundle.
5. **Set the environment variables** for MCP if `check` reports them missing. The script
   deliberately does NOT do this for you and never prints a key value — it only names the
   variable.
6. **Open Codex CLI** in the project, then **restart the session** once so the skills in
   `.agents/skills/` get scanned.
7. **Approve the hooks** in the Codex UI — a SEPARATE gate, see "Four things" below.
8. **Approve the MCP servers** — one approval per server.

## Trust — three ways, pick one

**Way 1 — let the script do it, no need to open Codex:**

```
cd <project root the bundle was copied into>
python3 scripts/tdq_checkportable.py setup --trust
```

**Way 2 — click inside Codex:** open Codex CLI right in the project folder; the first time it
enters an unknown folder it asks whether it may work here → pick the option that trusts the
folder.

**Way 3 — edit by hand** `~/.codex/config.toml` (or `$CODEX_HOME/config.toml`), adding:

```toml
[projects."/absolute/path/to/the/project"]
trust_level = "trusted"
```

The path must be ABSOLUTE with symlinks resolved, matching exactly the folder Codex runs in —
one character off and it does not take.

Way 1 is the ONLY path in this bundle that writes outside the bundle: it always leaves a
`<file>.tdq-bak-<timestamp>`, keeps the rest of the file untouched, and never writes over an
existing block. Without the `--trust` flag, `setup` does not touch that file at all.

To check that it took: run `check` again and read the trusted status line.

## Four things the machine CANNOT do for you

1. **Trust the folder** — `setup --trust` can do it for you (Way 1 above), or click yes in
   Codex.
2. **Approve the hooks** — hooks have their OWN trust gate: Codex shows "Review hooks" in the
   UI and you have to approve once. `--trust` does not open this gate, and editing
   `hooks.json` means approving again. Until approved, the hooks stay silent and never run.
3. **Approve the MCP servers** — every server in `.codex/config.toml` needs one approval from
   you.
4. **Restart** — new instructions are only loaded after the session restarts.

## Trust hook — separate from trusting the folder, and it is pinned to CONTENT

Hooks carry their own trust gate, and it is not the project-trust gate above. On a live
`codex-cli 0.149.0-alpha.4.3` (checked 2026-09-03) every entry under `[hooks.state...]` in
`~/.codex/config.toml` carries a `trusted_hash = "sha256:..."` field. That hash is taken over
the hook's CONTENT, which has two consequences:

1. A hook only runs after you approve it once — run `/hooks` inside Codex and approve. Until
   then it is silent, and silence looks exactly like a hook that works and has nothing to say.
2. **Rebuilding this bundle revokes that trust.** Any edit to a hook script changes its
   content, so the stored hash no longer matches and the hook goes back to untrusted. After
   every rebuild of this bundle, open `/hooks` and approve again.

Hooks are enabled by default on 0.149 — there is no `[features] hooks = true` to set, and
adding one is not what makes them run. Approval is.

## Environment variables — `env_vars` only names them, it never sets them

`[mcp_servers.*]` in `.codex/config.toml` uses `env_vars`, an array of variable NAMES that
Codex whitelists FROM YOUR SHELL. TOML does no interpolation, so nothing in this bundle can
give those variables a value. Export them yourself before starting Codex:

```
export TAVILY_API_KEY=<your key>
```

Put that line in your shell profile if you want it to survive a new terminal. A variable that
is not exported means the MCP server starts without it and its calls fail at runtime, not at
startup — so check `/mcp` if a search tool goes quiet.

## Why step 3 runs the file directly instead of saying "run the tdq-checkportable skill"

The skill lives inside this very bundle, and Codex only scans `.agents/skills/` after the
project is trusted and the session has restarted. Calling the skill at the first step is a
circular dependency; running `python3 scripts/tdq_checkportable.py` straight from the
terminal is not. From the next time on, once everything is loaded, call the skill normally.

## Secret keys

No file in here holds a key value, only environment variable NAMES (`env_vars` in
`config.toml`). Set the variables yourself on your own machine before using MCP.
"""


# ------------------------------------------- native layer of Codex CLI (>= 0.147.0)

# The three folders Codex scans by itself. Names and places are dictated by Codex:
#   `.agents/skills/<name>/SKILL.md`  — skills, loaded on demand by the frontmatter description
#   `.codex/config.toml`              — MCP servers (loaded only once the project is trusted)
#   `.codex/hooks.json`               — hooks (still needing their own approval in the TUI)
GOC_SKILL_CODEX = ".agents/skills"
GOC_CAU_HINH_CODEX = ".codex"
CODEX_MIN = "0.147.0"

# Mapping of TDQ hooks → Codex event + matcher. The matcher is a regex on `tool_name`, and the
# REAL Codex tool names were measured with a probe hook (see `docs/tdq/qc/2026-08-17-1139-*.md`):
# the command tool is named `Bash` (same as Claude Code), while the file-editing tool is named
# `apply_patch` — NOT `Edit|Write|MultiEdit|NotebookEdit`. Keep Claude Code's matcher and the hook
# never fires, without an error either: the approval gate is off in silence.
HOOK_CODEX = (
    ("SessionStart", None, "session_start.py"),
    ("UserPromptSubmit", None, "prompt_context.py"),
    ("PreToolUse", "apply_patch", "codex_edit_gate.py"),
    ("PreToolUse", "Bash", "bash_gate.py"),
    ("Stop", None, "stop_gate.py"),
)

# The adapter is generated into the bundle; the repo's `hooks/scripts/edit_gate.py` is NOT edited.
# Why keep it apart: `edit_gate.py` is shared code for both harnesses, while the difference here
# is purely the shape of Codex's own `tool_input`. Folding it in would make Claude Code carry a
# branch that never runs, and every gate edit would have to remember two payload shapes.
ADAPTER_CODEX = '''#!/usr/bin/env python3
"""codex_edit_gate.py — the bridge between Codex `apply_patch` and the shared `edit_gate.py`.

AUTO-GENERATED by `scripts/build_portable.py`. Hand edits here are lost on the next build.

Why it is needed: Claude Code sends `tool_input.file_path`, while Codex sends
`tool_input.command` holding the whole patch body (`*** Update File: <path>`). `edit_gate.py`
reads `file_path`, so running it straight under Codex yields an empty path — the gate exits 0
while guarding nothing at all, a silent failure.

Env: TDQ_LOG=0 turns the log off (it goes to stderr). Exit code and stdout come straight
from `edit_gate.py`.
"""
import datetime
import json
import os
import re
import subprocess
import sys

MAU_PATCH = re.compile(r"^\\*\\*\\* (?:Update|Add|Delete) File: (.+)$", re.MULTILINE)


def log(message):
    if os.environ.get("TDQ_LOG", "1") != "0":
        stamp = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
        print(f"[{stamp}] {message}", file=sys.stderr)


def tach_duong_dan_patch(than):
    """The FIRST path in the patch body, or an empty string. Never raises on odd input."""
    khop = MAU_PATCH.search(than or "")
    return khop.group(1).strip() if khop else ""


def main():
    raw = sys.stdin.read()
    try:
        payload = json.loads(raw) if raw.strip() else {}
    except ValueError:
        # A broken payload must not block the session: the gate is a reminder, not a security mechanism.
        log("codex_edit_gate: payload is not JSON, skipping")
        print("{}")
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
    proc = subprocess.run([sys.executable, that], input=json.dumps(payload),
                          capture_output=True, text=True)
    sys.stdout.write(proc.stdout)
    sys.stderr.write(proc.stderr)
    return proc.returncode


if __name__ == "__main__":
    sys.exit(main())
'''


def doc_frontmatter(text):
    """One-level YAML frontmatter of SKILL.md → dict. Empty dict if there is no `---` block.

    No YAML library: the bundle runs on a strange machine with a bare Python, and one more
    dependency is one more reason for the portable bundle to die at the first step.
    """
    if not text or not text.startswith("---"):
        return {}
    het = text.find("\n---", 3)
    if het < 0:
        return {}
    truong = {}
    for dong in text[3:het].splitlines():
        if ":" in dong and not dong.startswith(" "):
            khoa, _, gia_tri = dong.partition(":")
            truong[khoa.strip()] = gia_tri.strip()
    return truong


def tach_duong_dan_patch(than):
    """The first path in the body of an `apply_patch`, or an empty string.

    The version that actually runs lives in `ADAPTER_CODEX` (running on the target machine). This
    one lets the test lock the behaviour without unpacking the bundle first.
    """
    khop = re.search(r"^\*\*\* (?:Update|Add|Delete) File: (.+)$", than or "", re.MULTILINE)
    return khop.group(1).strip() if khop else ""


def _sinh_config_toml(duong):
    """`.codex/config.toml` — declare MCP servers in the Codex `[mcp_servers.<name>]` shape.

    Only environment variable NAMES go in, through `env_vars`, never values: Codex does NOT expand
    `${VAR}` in TOML, so writing `env = {X = "${X}"}` would pass MCP that literal string rather than
    the key. `env_vars` is how Codex forwards a variable from the parent environment — exactly what
    is needed, and the only way that keeps secrets out of the file.
    """
    khai_bao = sinh_mcp()["mcpServers"]
    dong = [
        "# TDQ Workflow — Codex CLI config, AUTO-GENERATED by scripts/build_portable.py.",
        f"# Needs Codex CLI >= {CODEX_MIN}. Only loaded once the project is trusted.",
        "",
    ]
    for ten in sorted(khai_bao):
        cau_hinh = khai_bao[ten]
        dong.append(f"[mcp_servers.{ten}]")
        dong.append(f'command = {json.dumps(cau_hinh["command"])}')
        dong.append("args = [" + ", ".join(json.dumps(a) for a in cau_hinh["args"]) + "]")
        ten_bien = sorted(cau_hinh.get("env") or {})
        if ten_bien:
            dong.append("env_vars = [" + ", ".join(json.dumps(b) for b in ten_bien) + "]")
        dong.append("")
    with open(duong, "w", encoding="utf-8") as f:
        f.write("\n".join(dong))


def _sinh_hooks_codex(duong):
    """`.codex/hooks.json` — the same wire shape as `hooks/hooks.json`, other matchers and paths.

    The paths are RELATIVE on purpose: real measurement shows Codex runs the hook process with cwd =
    the project root, so `hooks/scripts/x.py` is correct on every machine. That makes this a static
    file inside `manifest.json`, not something `setup` has to regenerate on the target machine.
    """
    su_kien = {}
    for ten_event, matcher, ten_file in HOOK_CODEX:
        nhom = {"hooks": [{
            "type": "command",
            "command": f'python3 "hooks/scripts/{ten_file}"',
        }]}
        if matcher:
            nhom["matcher"] = matcher
        su_kien.setdefault(ten_event, []).append(nhom)
    _ghi_json(duong, {
        "description": "TDQ workflow for Codex CLI — auto-generated, never edited by hand",
        "hooks": su_kien,
    })


def sinh_ban_codex(repo, dest, version=""):
    """Build `<dest>/portable_codex/` — the bundle using the REAL native mechanisms of Codex CLI.

    Four groups of artifacts:
      `.agents/skills/`    skills Codex loads by description;
      `.codex/config.toml` MCP servers (environment variable NAMES only);
      `.codex/hooks.json` + `hooks/`  machine-guarded approval gates, reusing the repo's code;
      `workflow/NN-*.md`   the markdown read in order, keeping this bundle usable by any
                           markdown-only harness OTHER than Codex.

    The first three layers need Codex CLI >= 0.147.0 and a trusted project; the hooks additionally
    need the user to approve once in the TUI. Nothing in here can do those steps for you.
    """
    import tdq_state

    goc = os.path.join(dest, TEN_BAN_CODEX)
    if os.path.isdir(goc):
        shutil.rmtree(goc)
    thu_muc_wf = os.path.join(goc, "workflow")
    os.makedirs(thu_muc_wf, exist_ok=True)
    os.makedirs(os.path.join(goc, GOC_CAU_HINH_CODEX), exist_ok=True)

    # A harness other than Claude Code sets no `CLAUDE_*` variable at all, so the paths in this
    # bundle must be relative to the bundle root — the user `cd`s in and runs, that is all.
    moi = "."
    copy_loc(os.path.join(repo, "scripts"), os.path.join(goc, "scripts"), True, moi)

    dong_danh_sach = []
    for so, ten_skill in enumerate(THU_TU_SKILL, start=1):
        thu_muc_skill = os.path.join(repo, "skills", ten_skill)
        if not os.path.isdir(thu_muc_skill):
            thu_muc_skill = os.path.join(repo, PORTABLE_SRC, "skills", ten_skill)
        nguon = os.path.join(thu_muc_skill, "SKILL.md")
        if not os.path.isfile(nguon):
            continue
        ten_file = f"{so:02d}-{ten_skill[len('tdq-'):]}.md"
        noi_dung, _ = doi_bien_plugin_root(_doc_text(nguon), moi)
        with open(os.path.join(thu_muc_wf, ten_file), "w", encoding="utf-8") as f:
            f.write(noi_dung)
        thu_muc_ref = os.path.join(thu_muc_skill, "references")
        if os.path.isdir(thu_muc_ref):
            copy_loc(thu_muc_ref, os.path.join(thu_muc_wf, "references", ten_skill), True, moi)
        # Native layer: copy the skill tree AS IS into `.agents/skills/<name>/` — keeping the folder
        # name is what keeps the `../<other skill>/SKILL.md` links inside SKILL.md pointing at the right
        # place, which the `workflow/NN-*.md` bundle loses because it has to renumber them.
        copy_loc(thu_muc_skill, os.path.join(goc, GOC_SKILL_CODEX, ten_skill), True, moi)
        dong_danh_sach.append(f"- `workflow/{ten_file}`")

    # `hooks/` must sit at the bundle ROOT next to `scripts/`: `hooks/scripts/_common.py` derives the
    # script folder as `../../scripts` relative to itself. Put it under `.codex/` and that breaks.
    copy_loc(os.path.join(repo, "hooks"), os.path.join(goc, "hooks"), True, moi, FILE_HOOK_AGY)
    duong_adapter = os.path.join(goc, "hooks", "scripts", "codex_edit_gate.py")
    with open(duong_adapter, "w", encoding="utf-8") as f:
        f.write(ADAPTER_CODEX)
    os.chmod(duong_adapter, 0o755)
    _sinh_config_toml(os.path.join(goc, GOC_CAU_HINH_CODEX, "config.toml"))
    _sinh_hooks_codex(os.path.join(goc, GOC_CAU_HINH_CODEX, "hooks.json"))

    with open(os.path.join(thu_muc_wf, "phases.md"), "w", encoding="utf-8") as f:
        f.write(tdq_state.render_phases_md() + "\n")

    with open(os.path.join(goc, "AGENTS.md"), "w", encoding="utf-8") as f:
        f.write(AGENTS_MD.format(danh_sach="\n".join(dong_danh_sach), codex_min=CODEX_MIN,
                         soul=DONG_SOUL_AGENTS))

    with open(os.path.join(goc, "README.md"), "w", encoding="utf-8") as f:
        f.write(README_CODEX.format(codex_min=CODEX_MIN))

    con_lai = dem_bien_trong_cay(goc)
    if con_lai:
        raise RuntimeError(f"the codex bundle still has {con_lai} use(s) of {BIEN_CU}")
    log(f"{TEN_BAN_CODEX}: {len(dong_danh_sach)} skill (native + workflow), "
        f"{len(HOOK_CODEX)} hook(s), {len(MCP_SERVERS)} MCP server(s), 0 plugin variable left")

    ghi_manifest(goc, version)
    return goc


# ---------------------------------------------------- antigravity (agy) bundle

TEN_BAN_AGY = "antigravity_portable"

# 2026-09-03: the older "spray the config into 6 guessed paths" design is gone. It was written
# when no source pinned agy's real layout; a READ-ONLY survey of a live `agy 1.1.11` install
# settled the question — none of those 6 candidate paths existed on disk. The real layout is a
# plain plugin directory:
#     ~/.gemini/config/plugins/<name>/{plugin.json, skills/, hooks.json, mcp_config.json}
# switched on by the key `plugins.<name>.enabled` in ~/.gemini/config/config.json, with extra
# skill roots registered as `entries[].path` in ~/.gemini/config/skills.json. So this bundle IS
# that plugin directory: the install is one copy plus two small config keys.
TEN_PLUGIN_AGY = "tdq-workflow"
GOC_AGY = f"~/.gemini/config/plugins/{TEN_PLUGIN_AGY}"

# The two user-owned config files the install has to touch. Neither is ever written by this
# script nor shipped in the bundle — the README names the one key to add, because both files
# hold unrelated user settings an overwrite would destroy.
AGY_CONFIG_JSON = "~/.gemini/config/config.json"
AGY_SKILLS_JSON = "~/.gemini/config/skills.json"

HOOK_AGY = (
    ("PreToolUse", "agy_pretooluse_gate.py"),
    ("Stop", "agy_stop_gate.py"),
)

# The bundle used to ship a `settings.json` mirroring the branch-name ban into agy's permissions
# engine. Dropped 2026-09-03: the real `~/.gemini/antigravity-cli/settings.json` holds the user's
# `model`/`colorScheme`/`trustedWorkspaces` and has no `permissions` block at all, so the copy
# step destroyed user settings while adding no guard. The hook is the guard.

README_AGY = """# TDQ Workflow — plugin bundle for Antigravity CLI (agy)

This directory IS an agy plugin: `plugin.json` at the root, `skills/` beside it, plus
`hooks.json` and `mcp_config.json`. The layout was read off a live `agy 1.1.11` install on
2026-09-03. Installing is one copy plus two config keys.

## Install — this exact order

1. **Copy this whole directory** to the plugin root, keeping the directory name:
   ```
   {goc_agy}/
   ```

2. **Enable the plugin** in `{config_json}` — add the key, keep everything else that file
   already holds:
   ```json
   {{ "plugins": {{ "{ten_plugin}": {{ "enabled": true }} }} }}
   ```

3. **Register the skill root** in `{skills_json}`, appending to the existing `entries` array:
   ```json
   {{ "entries": [ {{ "path": "{goc_agy}/skills" }} ] }}
   ```

4. **Set the environment variables** the MCP servers need. This bundle only ever records
   variable NAMES, never a key value — export `TAVILY_API_KEY` (and the backup server's
   variable) yourself before using MCP.

5. **Restart agy**, then self-check with agy's own commands:
   - `agy plugin list` — is `{ten_plugin}` listed and enabled?
   - `/skills` — do the `{danh_sach_ten}` skills show up?
   - `/mcp` — are `tavily-primary`/`tavily-backup` listed as configured servers?

6. **Smoke-test the hard deny.** Ask agy to run one of the banned cases (e.g.
   `git checkout -b antigravity-test`, or writing straight to `docs/tdq/state.json` through the
   shell) and confirm it is refused. Not refused → the hook did not load; re-check steps 1–2.

## The hook `command` paths are absolute, and baked at build time

agy requires an ABSOLUTE `command`; a `~` inside quotes is not expanded and the hook dies with
exit 127. `hooks.json` therefore carries a real expanded path — the home folder of the machine
that BUILT the bundle. Copying a prebuilt bundle to another user's machine leaves those paths
pointing at the wrong home. Rebuild it locally instead — run the repo's `build_portable.py`
from a clone of TDQ-Workflow, then copy the freshly built directory over.
`python3 scripts/tdq_checkportable.py check --root <this directory>` prints a NOTE when the
baked home does not match the current one.

## What this bundle cannot do for you

1. **Restart agy** — step 5. Skip it and the files just sit there, unloaded.
2. **Set the MCP environment variables** — step 4.
3. **Guarantee the layout on a different agy version.** It was verified against `agy 1.1.11`
   only; step 5's self-check is how you find out on YOUR machine.

## Secret keys

`mcp_config.json` records only the NAMES of environment variables, never a key value.
"""


def _sua_duong_dan_tuong_doi_agy(goc):
    """Second-pass rewrite, agy bundle only, `.md` text under `skills/` — a bare `scripts/`/
    `hooks/` mention NOT already prefixed by `GOC_AGY` becomes absolute too.

    `doi_bien_plugin_root` only rewrites `${CLAUDE_PLUGIN_ROOT}`. Several skill files were
    written assuming a project-relative cwd (true for Codex, whose bundle sets `moi="."`) —
    false here, since agy installs its core at one fixed absolute path outside any project.
    Scoped to `.md` only: touching `.py` source would corrupt real import paths.
    """
    tien_to = GOC_AGY + "/"
    mau = re.compile(r"(?<!" + re.escape(tien_to) + r")\b(scripts/|hooks/)")
    so_lan = 0
    for thu_muc, thu_muc_con, files in os.walk(goc):
        thu_muc_con[:] = [d for d in thu_muc_con if not _bo_qua_thu_muc(d)]
        for ten in files:
            if not ten.endswith(".md"):
                continue
            duong = os.path.join(thu_muc, ten)
            noi_dung = _doc_text(duong)
            if noi_dung is None:
                continue
            moi, n = mau.subn(tien_to + r"\1", noi_dung)
            if n:
                so_lan += n
                with open(duong, "w", encoding="utf-8") as f:
                    f.write(moi)
    return so_lan


def goc_agy_tuyet_doi():
    """`GOC_AGY` with `~` expanded — agy needs an ABSOLUTE `command`.

    A `~` inside the double quotes of a `command` string is NOT expanded by the shell, so the
    old form died with exit 127 (source N5). Expansion happens at BUILD time, which means a
    bundle built on one machine carries that machine's `$HOME`: rebuild locally
    (`python3 scripts/build_portable.py`) rather than copying a prebuilt bundle between users.
    `tdq_checkportable.py check` prints a NOTE when the baked home is not the current one.
    """
    return os.path.expanduser(GOC_AGY)


def _sinh_hooks_agy(duong):
    """`hooks.json` at the plugin root — commands are absolute paths into the plugin's own tree.

    Wire shape follows the agent-hooks contract documented for agy (source N5, 2026-09-03):
    an event map whose entries carry `hooks[].type = "command"`.
    """
    su_kien = {}
    goc = goc_agy_tuyet_doi()
    for ten_event, ten_file in HOOK_AGY:
        su_kien.setdefault(ten_event, []).append({"hooks": [{
            "type": "command",
            "command": f"python3 {goc}/hooks/scripts/{ten_file}",
        }]})
    _ghi_json(duong, {
        "description": "TDQ workflow for Antigravity CLI (agy) — auto-generated, never edited "
                        "by hand. Lives at the plugin root; agy reads it once the plugin is "
                        "enabled in ~/.gemini/config/config.json — see README.md.",
        "hooks": su_kien,
    })


def _sinh_plugin_json_agy(duong, version):
    """`plugin.json` at the plugin root — the one file that makes agy treat this directory as a
    plugin. A live `agy 1.1.11` install ships plugins whose manifest is as small as
    `{"name": "firebase"}`, so only `name` is load-bearing; the rest is for humans."""
    _ghi_json(duong, {
        "name": TEN_PLUGIN_AGY,
        "version": version or "0",
        "description": "Spec-driven TDQ workflow: intake → spec → plan → build → QC → report.",
    })


def _sinh_mcp_agy(duong):
    _ghi_json(duong, sinh_mcp())


def sinh_ban_antigravity(repo, dest, version=""):
    """Build `<dest>/antigravity_portable/` — bundle for Antigravity CLI (agy), user-level/global.

    Unlike the claude/codex bundles (project-level, copied into one project's own tree), this
    one is meant to be copied into agy's GLOBAL config paths under `$HOME` — see `README_AGY`.
    The bundle's own core (`skills/`, `scripts/`, `hooks/scripts/`) sits at one FIXED canonical
    path (`GOC_AGY`) that every generated config file's `command`/path field points at.
    """
    goc = os.path.join(dest, TEN_BAN_AGY)
    if os.path.isdir(goc):
        shutil.rmtree(goc)
    os.makedirs(goc, exist_ok=True)

    # No `CLAUDE_*` variable exists outside Claude Code, and the install path is fixed and
    # absolute rather than relative to a project cwd — every `${CLAUDE_PLUGIN_ROOT}` becomes
    # that fixed absolute path directly.
    moi = GOC_AGY
    copy_loc(os.path.join(repo, "scripts"), os.path.join(goc, "scripts"), True, moi)

    dong_danh_sach = []
    for ten_skill in THU_TU_SKILL:
        thu_muc_skill = os.path.join(repo, "skills", ten_skill)
        if not os.path.isdir(thu_muc_skill):
            thu_muc_skill = os.path.join(repo, PORTABLE_SRC, "skills", ten_skill)
        nguon = os.path.join(thu_muc_skill, "SKILL.md")
        if not os.path.isfile(nguon):
            continue
        copy_loc(thu_muc_skill, os.path.join(goc, "skills", ten_skill), True, moi)
        dong_danh_sach.append(ten_skill)
    _sua_duong_dan_tuong_doi_agy(os.path.join(goc, "skills"))

    os.makedirs(os.path.join(goc, "hooks", "scripts"), exist_ok=True)
    for ten_file in ("agy_pretooluse_gate.py", "agy_stop_gate.py"):
        src = os.path.join(repo, "hooks", "scripts", ten_file)
        dst = os.path.join(goc, "hooks", "scripts", ten_file)
        shutil.copy2(src, dst)
        os.chmod(dst, 0o755)

    _sinh_plugin_json_agy(os.path.join(goc, "plugin.json"), version)
    _sinh_hooks_agy(os.path.join(goc, "hooks.json"))
    _sinh_mcp_agy(os.path.join(goc, "mcp_config.json"))

    with open(os.path.join(goc, "README.md"), "w", encoding="utf-8") as f:
        f.write(README_AGY.format(
            goc_agy=GOC_AGY,
            ten_plugin=TEN_PLUGIN_AGY,
            config_json=AGY_CONFIG_JSON,
            skills_json=AGY_SKILLS_JSON,
            danh_sach_ten=", ".join(dong_danh_sach),
        ))

    con_lai = dem_bien_trong_cay(goc)
    if con_lai:
        raise RuntimeError(f"the antigravity bundle still has {con_lai} use(s) of {BIEN_CU}")
    log(f"{TEN_BAN_AGY}: {len(dong_danh_sach)} skill(s), {len(HOOK_AGY)} hook(s), "
        f"{len(MCP_SERVERS)} MCP server(s), 0 plugin variable left")

    ghi_manifest(goc, version)
    return goc


# ------------------------------------------------------------------ manifest

def sinh_manifest(goc, version=""):
    """Scan the folder tree → a manifest dict with all 5 blocks.

    `manifest.json` leaves itself out of the list: it is written AFTER the scan, so listing itself
    would record a sha256 that never matches its own final content.
    """
    files = {}
    for thu_muc, thu_muc_con, ten_files in os.walk(goc):
        thu_muc_con[:] = [d for d in thu_muc_con if not _bo_qua_thu_muc(d)]
        for ten in ten_files:
            if _bo_qua_file(ten):
                continue
            duong_day_du = os.path.join(thu_muc, ten)
            tuong_doi = os.path.relpath(duong_day_du, goc).replace(os.sep, "/")
            if tuong_doi == MANIFEST_NAME:
                continue
            files[tuong_doi] = sha256_of(duong_day_du)
    return {
        "files": files,
        "version": version,
        "python_min": PYTHON_MIN,
        "external_commands": list(EXTERNAL_COMMANDS),
        "mcp_servers": list(MCP_SERVERS),
    }


def ghi_manifest(goc, version=""):
    man = sinh_manifest(goc, version)
    with open(os.path.join(goc, MANIFEST_NAME), "w", encoding="utf-8") as f:
        json.dump(man, f, ensure_ascii=False, indent=2, sort_keys=True)
    log(f"manifest: {len(man['files'])} file(s) in {os.path.basename(goc)}")
    return man


# -------------------------------------------------------------------------- CLI

def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="build_portable.py",
        description="Generate the two portable bundles (claude, codex) of TDQ Workflow from one source.")
    parser.add_argument("--dest", help="destination folder, defaults to the repo root")
    parser.add_argument("--only", choices=("claude", "codex", "antigravity"),
                        help="generate only one bundle instead of all three")
    parser.add_argument("--repo", help="source repo root, defaults to the script location")
    args = parser.parse_args(argv)

    repo = args.repo or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    dest = args.dest or repo
    version = plugin_version(repo)
    log(f"start · repo={repo} · dest={dest} · version={version or '—'}")

    os.makedirs(dest, exist_ok=True)
    try:
        if args.only in (None, "claude"):
            sinh_ban_claude(repo, dest, version)
        if args.only in (None, "codex"):
            sinh_ban_codex(repo, dest, version)
        if args.only in (None, "antigravity"):
            sinh_ban_antigravity(repo, dest, version)
    except (OSError, RuntimeError) as loi:
        log(f"ERROR {loi}")
        return EXIT_LOI
    log("done")
    return 0


if __name__ == "__main__":
    sys.exit(main())
