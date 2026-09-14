#!/usr/bin/env python3
"""The Codex CLI layer — a wrapper around `codex exec` for mode `codex implement`.

Dependency direction: this layer KNOWS `tdq_vungfile`, and `tdq_state` does NOT know this layer
(tests/test_kien_truc.py pins that with an AST check). The mode gate asks through the subprocess
`tdq_codex.py check --json`, so a machine without `codex` can still open the workflow.

The backbone principles:
- `check` never raises. Every problem is "not offerable WITH A REASON", exit 0. Four causes give
  four different sentences, because the reader needs to know what to do next.
- Every `codex` call leaves stdin NOT a TTY plus an explicit timeout — `codex exec` was measured
  hanging forever when stdin is a waiting pipe.
- Every output stream passes through `mask_secrets` before it leaves a function.

Env: TDQ_LOG=0 turns the log off (the log goes to stderr).
"""
import argparse
import datetime
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time

try:
    import tomllib
except ImportError:  # Python < 3.11: no provider copy, the temp home keeps only the model line
    tomllib = None

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from setup_status import mask_secrets  # noqa: E402

CO_REL = os.path.join("docs", "tdq", ".tdq-codex.json")
LOG_PROMPT_REL = os.path.join("docs", "tdq", ".tdq-codex-prompt.log")
HOME_PREFIX = "tdq-codex-home-"
TIMEOUT_KIEM_SONG = 30
TIMEOUT_RUN = 600
# The liveness turn only has to prove the model ANSWERS, so it may not write anything.
SANDBOX_KIEM_SONG = "read-only"
CAU_SAY_HI = "Reply with exactly one word: hi"

# The mode's MARKER environment variable: the gate hook inside the sandbox reads it to learn that
# this turn belongs to mode `codex`. The name deliberately carries no KEY/TOKEN/SECRET — secret
# masking tools scan variable names, and a matching name would mask the marker itself away.
BIEN_MOC = "TDQ_CODEX_TASK"
# The two zone variables for the early gate hook `hooks/scripts/codex_edit_gate.py`. The
# dependency runs exactly one way: `scripts/` SETS the variables, `hooks/` READS them — neither
# side imports the other. The value is JSON: a path may carry spaces, and an empty list must stay
# distinguishable from "not declared" (not declared means the hook only warns, never blocks).
BIEN_VUNG = "TDQ_CODEX_VUNG"
BIEN_KHOA = "TDQ_CODEX_KHOA"

# The ONLY PLACE a `codex exec` flag name is written. Everywhere else looks the table up; the
# self-check READS this same table and compares against it, so changing a flag touches one spot
# and no copy drifts away in silence.
CO_EXEC = {
    "lenh": "exec",
    "goc_repo": "-C",
    "sandbox": "-s",
    "sandbox_gia_tri": "workspace-write",
    "model": "-m",
    "schema": "--output-schema",
    "ket_qua": "-o",
    "bo_qua_tin_hook": "--dangerously-bypass-hook-trust",
    "bo_qua_kiem_git": "--skip-git-repo-check",
}


class LoiThieuModel(RuntimeError):
    """No model name. Loud on purpose: falling back to the machine's default model makes the
    result unreproducible with nobody noticing."""


class LoiChuaDo(RuntimeError):
    """Calling Codex before the test is red — the red→green beat loses its meaning."""


# ----------------------------------------------------------------- log service

def _log_enabled():
    return os.environ.get("TDQ_LOG", "1") != "0"


def log(message):
    """One stderr line with an ISO timestamp. Turn it off with TDQ_LOG=0."""
    if _log_enabled():
        stamp = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
        print(f"[{stamp}] tdq_codex: {mask_secrets(message)}", file=sys.stderr)


# ------------------------------------------------- machine-level consent flag

def doc_co_dong_y(cwd="."):
    """-> a dict of three keys. A missing OR BROKEN file both mean "no consent".

    A broken file must not take the mode gate down: the user sees mode `codex` as unofferable
    with a reason, not a traceback.
    """
    mac_dinh = {"nguoi_dung_dong_y": False, "quyet_dinh_luc": "", "codex_model": ""}
    duong = os.path.join(cwd, CO_REL)
    try:
        with open(duong, encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, ValueError):
        return mac_dinh
    if not isinstance(data, dict):
        return mac_dinh
    mac_dinh.update({k: data[k] for k in mac_dinh if k in data})
    return mac_dinh


def dat_co_dong_y(cwd, dong_y, model=None):
    """Record the USER's decision. Only two doors call this, both typed by the user after being
    asked: `tdq_codex.py dong-y` (source repo and bundles alike) and `tdq_checkportable.py setup
    --codex` (bundles) — nowhere else may set it on their behalf."""
    duong = os.path.join(cwd, CO_REL)
    os.makedirs(os.path.dirname(duong), exist_ok=True)
    data = {
        "nguoi_dung_dong_y": bool(dong_y),
        "quyet_dinh_luc": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
        "codex_model": model or "",
    }
    with open(duong, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    log(f"consent flag: {'yes' if dong_y else 'no'} · model={model or '(not set)'}")
    return data


# ------------------------------------------------------------- liveness check

def _dong_loi(stderr):
    """-> the most telling stderr line: the last `ERROR` line, else the last non-empty one."""
    dong = [d.strip() for d in (stderr or "").splitlines() if d.strip()]
    loi = [d for d in dong if "ERROR" in d]
    return mask_secrets((loi or dong or [""])[-1])[:160]


def doc_file_van_ban(duong):
    """-> the file's text, or "" when it is missing or unreadable."""
    try:
        with open(duong, encoding="utf-8") as f:
            return f.read()
    except OSError:
        return ""


def _kiem_song(duong_codex, cwd, model, timeout=TIMEOUT_KIEM_SONG):
    """-> (alive, version, reason). `codex --version`, then ONE real say-hi turn.

    `--version` alone proves nothing: it exits 0 with the router dead (measured — `check` said
    runnable while a real turn timed out at 60s). The say hi goes through the SAME temporary
    CODEX_HOME that `run` builds, so "alive" means `run` can reach the model too.

    Closed stdin and an explicit timeout are MANDATORY here, not belt-and-braces: `codex exec`
    hangs forever when stdin is a waiting pipe. Only this turn's own home is deleted afterwards —
    `cleanup` would also sweep the home of a `run` in progress.
    """
    try:
        proc = subprocess.run(
            [duong_codex, "--version"], capture_output=True, text=True,
            encoding="utf-8", timeout=timeout, stdin=subprocess.DEVNULL)
    except subprocess.TimeoutExpired:
        # i18n-allow: reason sentence shown to the user by the mode gate
        return False, "", f"`codex --version` quá hạn {timeout}s"  # i18n-allow
    except OSError as exc:
        # i18n-allow: reason sentence shown to the user by the mode gate
        return False, "", f"không chạy được `codex`: {type(exc).__name__}"  # i18n-allow
    if proc.returncode != 0:
        return False, "", f"`codex --version` exit {proc.returncode}: " \
                          f"{mask_secrets(proc.stderr.strip())[:120]}"
    phien_ban = mask_secrets((proc.stdout or proc.stderr).strip())

    c = CO_EXEC
    home = dung_codex_home(cwd, model)
    file_tra_loi = os.path.join(home, "say-hi.txt")
    lenh = [duong_codex, c["lenh"], c["goc_repo"], cwd, c["sandbox"], SANDBOX_KIEM_SONG,
            c["model"], model, c["ket_qua"], file_tra_loi, c["bo_qua_kiem_git"], CAU_SAY_HI]
    bat_dau = time.time()
    try:
        proc = subprocess.run(
            lenh, capture_output=True, text=True, encoding="utf-8", timeout=timeout,
            stdin=subprocess.DEVNULL, env=dict(os.environ, CODEX_HOME=home))
        tra_loi = (doc_file_van_ban(file_tra_loi) or proc.stdout or "").strip()
    except subprocess.TimeoutExpired:
        log(f"say hi: timeout {timeout}s · model={model}")
        # i18n-allow: reason sentence shown to the user by the mode gate
        return False, "", f"say hi quá hạn {timeout}s — model không trả lời"  # i18n-allow
    except OSError as exc:
        # i18n-allow: reason sentence shown to the user by the mode gate
        return False, "", f"say hi không chạy được `codex`: {type(exc).__name__}"  # i18n-allow
    finally:
        shutil.rmtree(home, ignore_errors=True)
    log(f"say hi: exit {proc.returncode} · {time.time() - bat_dau:.1f}s · model={model} "
        f"· reply={len(tra_loi)} chars")
    if proc.returncode != 0:
        # i18n-allow: reason sentence shown to the user by the mode gate
        return False, "", f"say hi exit {proc.returncode}: {_dong_loi(proc.stderr)}"  # i18n-allow
    if not tra_loi:
        # i18n-allow: reason sentence shown to the user by the mode gate
        return False, "", "say hi không nhận được câu trả lời nào từ model"  # i18n-allow
    return True, phien_ban, ""


# -------------------------------------------------------------------- check

def check(cwd="."):
    """-> a dict of five keys. NEVER raises, and always carries `ly_do` when unusable.

    Four causes, four different sentences:
    1. `codex` not installed        3. consent given but `codex` will not run
    2. `codex` present, not approved   4. everything in place but no model name
    """
    duong_codex = shutil.which("codex")
    if not duong_codex:
        return {"co": False, "chay_duoc": False, "phien_ban": "",
                # i18n-allow: reason and fix, quoted verbatim by the mode gate
                "ly_do": "chưa cài `codex` trên máy này",  # i18n-allow
                "goi_y": "npm i -g @openai/codex  (rồi chạy `codex login`)"}  # i18n-allow

    co = doc_co_dong_y(cwd)
    if not co["nguoi_dung_dong_y"]:
        return {"co": True, "chay_duoc": False, "phien_ban": "",
                # i18n-allow: reason and fix, quoted verbatim by the mode gate
                "ly_do": "có `codex` nhưng bạn chưa duyệt cho workflow gọi nó",  # i18n-allow
                "goi_y": "python3 scripts/tdq_codex.py dong-y --model <tên-model>"}  # i18n-allow

    # The model is asked BEFORE liveness: the say hi needs a model name, and without one it would
    # fall back to the machine default — exactly what this mode forbids.
    if not co["codex_model"]:
        return {"co": True, "chay_duoc": False, "phien_ban": "",
                # i18n-allow: reason and fix, quoted verbatim by the mode gate
                "ly_do": "thiếu tên model — mode này cấm rơi về model mặc định của máy",  # i18n-allow
                "goi_y": "python3 scripts/tdq_codex.py setup-model <tên-model>"}  # i18n-allow

    song, phien_ban, ly_do_song = _kiem_song(duong_codex, cwd, co["codex_model"])
    if not song:
        return {"co": True, "chay_duoc": False, "phien_ban": "",
                # i18n-allow: reason and fix, quoted verbatim by the mode gate
                "ly_do": f"`codex` có nhưng không chạy được — {ly_do_song}",  # i18n-allow
                "goi_y": ("xem provider/router trong ~/.codex/config.toml hoặc chạy `codex login`, "  # i18n-allow
                          "rồi chạy lại: python3 scripts/tdq_codex.py check")}  # i18n-allow

    return {"co": True, "chay_duoc": True, "phien_ban": phien_ban,
            "ly_do": "", "goi_y": ""}


# --------------------------------------------------------- choosing the model

def chon_model(cwd, co_dong_lenh=None):
    """The order: the `--model` flag → the `codex_model` key → LoiThieuModel plus the fix.

    There is no fourth branch. Returning an empty string here would mean letting `codex` pick the
    machine's default model — and the result would differ between two machines with nobody knowing.
    """
    if co_dong_lenh:
        return co_dong_lenh
    tu_cai_dat = doc_co_dong_y(cwd).get("codex_model") or ""
    if tu_cai_dat.strip():
        return tu_cai_dat.strip()
    raise LoiThieuModel(
        "no model name for mode `codex` — this mode must not fall back to the machine's default "
        "model. Fix: python3 scripts/tdq_codex.py setup-model <model-name> "
        "(or pass --model for this one turn)")


# ------------------------------------------------------- building the command

def dung_lenh(goc_repo, model, file_schema, file_ket_qua, prompt=None):
    """Build the argv of one `codex exec` turn, reading the CO_EXEC table and nothing else.

    No other function may stitch a flag name together by hand — that is the condition under which
    the "the table is the only place" check means anything.
    """
    c = CO_EXEC
    lenh = [
        "codex", c["lenh"],
        c["goc_repo"], goc_repo,
        c["sandbox"], c["sandbox_gia_tri"],
        c["model"], model,
        c["schema"], file_schema,
        c["ket_qua"], file_ket_qua,
        c["bo_qua_tin_hook"],
        c["bo_qua_kiem_git"],
    ]
    if prompt:
        lenh.append(prompt)
    return lenh


def hop_dong_chay():
    """The three MANDATORY properties of every `codex` call, split out so they can be checked.

    `codex exec` hangs forever when stdin is a waiting pipe — measured. So closed stdin and an
    explicit timeout are properties of the contract, not options.
    """
    return {"stdin": subprocess.DEVNULL, "timeout": TIMEOUT_RUN,
            "capture_output": True, "text": True, "encoding": "utf-8"}


def dung_env(cwd, home, ma_task, nen=None, vung=None, khoa=None):
    """The environment of one turn: the temporary CODEX_HOME, the marker variable, and the
    declared file zone.

    The zone enters the environment only when it was declared: a missing variable makes the early
    gate warn and let the call through, while an empty variable means "empty zone, write nothing" —
    two different things that must not be made to look alike.
    """
    env = dict(nen if nen is not None else os.environ)
    env["CODEX_HOME"] = home
    env[BIEN_MOC] = ma_task
    if vung is not None:
        env[BIEN_VUNG] = json.dumps(list(vung))
    if khoa is not None:
        env[BIEN_KHOA] = json.dumps(list(khoa))
    return env


# ----------------------------------------------------------- CODEX_HOME

def _duong_home(cwd):
    return os.path.join(cwd, "docs", "tdq", ".tdq-codex-home")


def thu_muc_codex_may():
    """The machine's own Codex config directory — `$CODEX_HOME` first, exactly as Codex reads it."""
    return os.environ.get("CODEX_HOME") or os.path.join(os.path.expanduser("~"), ".codex")


def _toml_khoa(khoa):
    return khoa if re.fullmatch(r"[A-Za-z0-9_-]+", khoa) else json.dumps(khoa, ensure_ascii=False)


def _toml_gia_tri(gia_tri):
    if isinstance(gia_tri, bool):
        return "true" if gia_tri else "false"
    if isinstance(gia_tri, (int, float)):
        return repr(gia_tri)
    if isinstance(gia_tri, list):
        return "[" + ", ".join(_toml_gia_tri(x) for x in gia_tri) + "]"
    if isinstance(gia_tri, dict):
        return "{ " + ", ".join(f"{_toml_khoa(k)} = {_toml_gia_tri(v)}"
                                for k, v in gia_tri.items()) + " }"
    return json.dumps(str(gia_tri), ensure_ascii=False)


def _toml_bang(ten, bang):
    """-> the lines of one TOML table; nested dicts become `[ten.con]` sub-tables."""
    dong = [f"[{ten}]"]
    dong += [f"{_toml_khoa(k)} = {_toml_gia_tri(v)}"
             for k, v in bang.items() if not isinstance(v, dict)]
    for k, v in bang.items():
        if isinstance(v, dict):
            dong += ["", *_toml_bang(f"{ten}.{_toml_khoa(k)}", v)]
    return dong


def _provider_cua_may(nguon):
    """-> (provider name, its table or None). A missing or broken config is ("", None).

    Only the provider the machine SELECTED is taken: without it Codex falls back to `openai`,
    which rejects a router model with 400 "model not supported when using Codex with a ChatGPT
    account" — measured on a machine behind `9router`.
    """
    if tomllib is None:
        return "", None
    try:
        with open(os.path.join(nguon, "config.toml"), "rb") as f:
            cfg = tomllib.load(f)
    except (OSError, ValueError):
        return "", None
    ten = cfg.get("model_provider")
    if not isinstance(ten, str) or not ten:
        return "", None
    bang = (cfg.get("model_providers") or {}).get(ten)
    return ten, (bang if isinstance(bang, dict) else None)


def dung_codex_home(cwd, model, nguon=None):
    """A temporary CODEX_HOME directory, mode 700: `auth.json` plus a minimal `config.toml`.

    It never copies the whole `~/.codex`: the less that enters the sandbox, the less can leak out.
    `config.toml` carries the workflow's model and ONLY the machine's selected provider table —
    no `[agents]`, `[projects]` or `[mcp_servers]`. That table may hold a live header key, so the
    file is 600 and the parent directory is gitignored.
    """
    nguon = nguon or thu_muc_codex_may()
    goc = _duong_home(cwd)
    os.makedirs(goc, exist_ok=True)
    home = tempfile.mkdtemp(prefix=HOME_PREFIX, dir=goc)
    os.chmod(home, 0o700)

    that = os.path.join(nguon, "auth.json")
    if os.path.exists(that):
        shutil.copy2(that, os.path.join(home, "auth.json"))
        os.chmod(os.path.join(home, "auth.json"), 0o600)

    ten, bang = _provider_cua_may(nguon)
    dong = [f"model = {_toml_gia_tri(model)}"]
    if ten:
        dong.append(f"model_provider = {_toml_gia_tri(ten)}")
    if bang is not None:
        dong += ["", *_toml_bang(f"model_providers.{_toml_khoa(ten)}", bang)]
    duong_config = os.path.join(home, "config.toml")
    with open(duong_config, "w", encoding="utf-8") as f:
        f.write("\n".join(dong) + "\n")
    os.chmod(duong_config, 0o600)
    log(f"temporary CODEX_HOME: {home} (mode 700) · provider={ten or '(codex default)'}")
    return home


def cleanup(cwd="."):
    """The SOLE owner of deleting temporary CODEX_HOMEs. Nothing to delete still returns 0 —
    cleanup has to be callable unconditionally at the end of a turn."""
    goc = _duong_home(cwd)
    if not os.path.isdir(goc):
        log("cleanup: no temporary CODEX_HOME at all")
        return 0
    so = 0
    for ten in os.listdir(goc):
        if ten.startswith(HOME_PREFIX):
            shutil.rmtree(os.path.join(goc, ten), ignore_errors=True)
            so += 1
    try:
        os.rmdir(goc)
    except OSError:
        pass
    log(f"cleanup: deleted {so} temporary CODEX_HOME(s)")
    return 0


# ----------------------------------------------------------------- the verdict

# The minimum shape of the result file. Missing this key means "we do not know what Codex did",
# and not knowing must FAIL rather than be guessed as done.
SCHEMA_KHOA_BAT_BUOC = ("xong",)


def khuon_schema():
    """The `--output-schema` handed to Codex. `additionalProperties: false` is what OpenAI strict
    mode demands; without it a real OpenAI provider rejects the schema instead of applying it."""
    return {"type": "object",
            "properties": {k: {"type": "boolean"} for k in SCHEMA_KHOA_BAT_BUOC},
            "required": list(SCHEMA_KHOA_BAT_BUOC),
            "additionalProperties": False}


# The deny markers, looked up as substrings of stdout. `codex` returns exit 0 both when the hook
# blocks and when the sandbox blocks, so the exit code must NOT decide on its own.
DAU_HIEU_DENY = ("permissionDecision", "BLOCKED")


RAO_CODE = "```"
NHAN_RAO_NHAN = ("", "json")


def _boc_rao(noi_dung):
    """Unwrap exactly one code fence that encloses the WHOLE (already stripped) text.

    Some routers drop `--output-schema`, and the model then wraps correct JSON in a markdown
    fence. Only the whole-file shape is unwrapped: an opening fence labelled empty or `json`, a
    closing line of only the fence, and no other fence in between. Anything else is returned
    untouched, so text around a fence still fails `json.loads` instead of being guessed at.
    """
    dong = noi_dung.splitlines()
    if len(dong) < 2 or not dong[0].startswith(RAO_CODE):
        return noi_dung
    nhan = dong[0][len(RAO_CODE):].strip().lower()
    giua = "\n".join(dong[1:-1])
    if nhan not in NHAN_RAO_NHAN or dong[-1].strip() != RAO_CODE or RAO_CODE in giua:
        return noi_dung
    return giua


# The CLOSED set of reasons a turn is not `xong`. Every non-xong verdict carries exactly one of
# these, so a log line says WHY without anyone rereading the raw result file.
MA_LY_DO = (
    "qua-han",              # killed by the timeout
    "bi-chan",              # a deny marker in stdout
    "exit-khac-0",          # codex exited non-zero
    "khong-co-ket-qua",     # the result file is missing or empty
    "ket-qua-sai-khuon",    # not a JSON object, or `xong` missing / not a boolean
    "model-bao-chua-xong",  # the model itself answered `xong: false`
)


def doc_ket_qua_ly_do(duong):
    """-> (dict, None) or (None, reason). Missing/empty file vs unreadable content are told apart.

    Bare JSON and JSON inside one whole-file code fence are both read; see `_boc_rao`.
    """
    try:
        with open(duong, encoding="utf-8") as f:
            noi_dung = f.read().strip()
    except OSError:
        return None, "khong-co-ket-qua"
    if not noi_dung:
        return None, "khong-co-ket-qua"
    try:
        data = json.loads(_boc_rao(noi_dung))
    except ValueError:
        return None, "ket-qua-sai-khuon"
    if not isinstance(data, dict):
        return None, "ket-qua-sai-khuon"
    return data, None


def doc_ket_qua(duong):
    """-> a dict or None. A missing file, an empty file and broken JSON are all None."""
    return doc_ket_qua_ly_do(duong)[0]


def _ly_do_ket_qua(ket_qua, ly_do_doc):
    """The reason carried by the result itself, or None when it says `xong` is exactly True."""
    if ket_qua is None:
        return ly_do_doc or "khong-co-ket-qua"
    if not isinstance(ket_qua, dict):
        return "ket-qua-sai-khuon"
    if any(k not in ket_qua for k in SCHEMA_KHOA_BAT_BUOC):
        return "ket-qua-sai-khuon"
    # `is`, not `==`: `1 == True` in Python, and a string "true" is not a boolean either.
    if ket_qua["xong"] is True:
        return None
    if ket_qua["xong"] is False:
        return "model-bao-chua-xong"
    return "ket-qua-sai-khuon"


def phan_quyet_ly_do(exit_code, ket_qua, stdout, qua_han, ly_do_doc=None):
    """Four columns of evidence -> (state, reason). The reason is None only for `xong`.

    The reading order is deliberate: a timeout beats everything (the process was killed, so every
    other marker is untrustworthy), then deny (blocked is blocked, even at exit 0), and only then
    the exit code and the result file. `ly_do_doc` is the reason `doc_ket_qua_ly_do` gave for a
    None result, so "no file" and "unreadable file" stay distinct.
    """
    if qua_han:
        return "timeout", "qua-han"
    if any(d in (stdout or "") for d in DAU_HIEU_DENY):
        return "deny", "bi-chan"
    if exit_code != 0:
        return "fail", "exit-khac-0"
    ly_do = _ly_do_ket_qua(ket_qua, ly_do_doc)
    return ("xong", None) if ly_do is None else ("fail", ly_do)


def phan_quyet(exit_code, ket_qua, stdout, qua_han):
    """Four columns of evidence -> one of four states: xong/fail/timeout/deny."""
    return phan_quyet_ly_do(exit_code, ket_qua, stdout, qua_han)[0]


# ------------------------------------------------- the early-fence self-check

HOOKS_JSON_REL = os.path.join(".codex", "hooks.json")
GATE_REL = os.path.join("hooks", "scripts", "codex_edit_gate.py")
TIMEOUT_KIEM_HOOK = 30


def kiem_hook_ban(cwd="."):
    """Can the early fence actually fire -> (can_fire, the reason when it cannot).

    Three cheap checks, entirely local, costing NOT ONE `codex` turn:
    1. `.codex/hooks.json` exists and wires both `PreToolUse` matchers to the right gate file;
    2. the `--dangerously-bypass-hook-trust` flag is in the flag table (without it Codex runs the
       hook in silence — issue #32491);
    3. a live test shot: call the gate file itself with a payload writing outside the zone and
       demand `deny` back. This catches a broken gate file, a missing run flag, or a Python that
       cannot load it — the cases reading configuration alone never sees.

    Never raises: this is a check, and it returns DATA for the caller to decide on.
    """
    duong_json = os.path.join(cwd, HOOKS_JSON_REL)
    try:
        with open(duong_json, encoding="utf-8") as f:
            khai = json.load(f)
    except (OSError, ValueError) as loi:
        return False, f"cannot read {HOOKS_JSON_REL} ({loi.__class__.__name__})"
    nhom = (khai.get("hooks") or {}).get("PreToolUse") or []
    matcher = sorted(str(n.get("matcher")) for n in nhom)
    if matcher != ["Bash", "apply_patch"]:
        return False, f"{HOOKS_JSON_REL} must wire exactly the two matchers Bash + apply_patch"
    if not all("codex_edit_gate.py" in (n.get("hooks") or [{}])[0].get("command", "")
               for n in nhom):
        return False, f"{HOOKS_JSON_REL} does not point back at the zone fence"
    # Look the TABLE up instead of retyping the flag name: writing it out here would create a
    # second copy, and changing the table while forgetting this spot would leave the check green
    # while the hook had already gone silent.
    co_bo_qua = CO_EXEC.get("bo_qua_tin_hook") or ""
    if not co_bo_qua.startswith("--"):
        return False, "the flag table has no `bo_qua_tin_hook` key, so the hook would run in silence"

    duong_gate = os.path.join(cwd, GATE_REL)
    payload = json.dumps({"hook_event_name": "PreToolUse", "tool_name": "Bash", "cwd": cwd,
                          "tool_input": {"command": "echo x > ngoai-vung-thu-ban.tmp"}})
    env = dict(os.environ, TDQ_LOG="0")
    env[BIEN_MOC] = "kiem-hook"
    env[BIEN_VUNG] = json.dumps(["scripts/khong-ton-tai.py"])
    env[BIEN_KHOA] = "[]"
    try:
        proc = subprocess.run([sys.executable, duong_gate], input=payload,
                              capture_output=True, text=True, encoding="utf-8",
                              timeout=TIMEOUT_KIEM_HOOK, env=env, cwd=cwd)
        ra = json.loads(proc.stdout or "{}")
    except (OSError, ValueError, subprocess.SubprocessError) as loi:
        return False, f"the fence test shot failed ({loi.__class__.__name__})"
    quyet = (ra.get("hookSpecificOutput") or {}).get("permissionDecision")
    if quyet != "deny":
        return False, f"test shot: the fence returned `{quyet}` instead of `deny`"
    return True, ""


def canh_bao_hook(ban_duoc, ly_do):
    """EXACTLY ONE warning line when the early fence cannot fire — and nothing more.

    Deliberately no self-downgrading branch: the deciding layer is the `git diff` audit in
    `tdq_vungfile.py`, which runs on git and so does not depend on Codex cooperating. A machine
    that rewrites its own configuration only adds a branch nobody has ever run.
    """
    if ban_duoc:
        return ""
    return (f"WARNING: the Codex early fence cannot fire ({ly_do}) — carrying on anyway, the "
            "`git diff` audit against the mark is the deciding layer of this turn")


# -------------------------------------------------------------------- the beat

def kiem_nhip(da_thay_do):
    """Block calling Codex before the test has been RUN and SEEN red.

    Without seeing red, the green that follows proves nothing: the test may have been green all
    along, or it may never touch the part Codex just wrote.
    """
    if not da_thay_do:
        raise LoiChuaDo(
            "the test has not been run to SEE it red — the beat of mode `codex` is red → Codex "
            "makes it green → the leader reruns it; skip the red step and the green means nothing")
    return True


def dong_log_nhip(ma_task, do, xanh):
    stamp = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
    moc = f"red={'yes' if do else 'not-yet'}"
    if xanh:
        moc += " green=yes"
    else:
        moc += " green=not-yet"
    return f"[{stamp}] beat {ma_task}: {moc}"


# --------------------------------------------------------- the log of one turn

def dong_log_luot(ma_task, model, home, giay, trang_thai, prompt, ly_do=None):
    """One line for one Codex call, carrying ALL SEVEN PIECES, plus `ly_do` when not `xong`.

    The seven: timestamp · task id · the REAL model name · the CODEX_HOME used · wall time ·
    state · the sha256 of the prompt plus its masked opening. The reason (one of MA_LY_DO) goes
    LAST, so `tdq_bench.MAU_LOG_LUOT`, anchored on the leading pieces, still reads the line.

    It records the sha256 rather than the text: a prompt carries code and sometimes internal
    paths, while this log line lands where git tracks it. The text itself goes only to
    LOG_PROMPT_REL, which is gitignored.
    """
    stamp = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
    bam = hashlib.sha256((prompt or "").encode("utf-8")).hexdigest()
    dau = mask_secrets((prompt or "")[:40]).replace("\n", " ")
    duoi = f" · ly_do={ly_do}" if ly_do and trang_thai != "xong" else ""
    return (f"[{stamp}] luot {ma_task} · model={model} · home={home} · "
            f"{giay:.1f}s · {trang_thai} · sha256={bam[:16]} · dau=\"{dau}\"{duoi}")


def in_log_luot(dong):
    """The turn line to stderr, behind the same TDQ_LOG switch as every other log line.

    Not through `log()`: the line already carries its own timestamp, and `tdq_bench` reads it back.
    """
    if _log_enabled():
        print(dong, file=sys.stderr)


def ghi_log_prompt(cwd, ma_task, prompt):
    """The prompt text into a file that IS gitignored. Turn it off with TDQ_LOG=0."""
    if not _log_enabled():
        return ""
    duong = os.path.join(cwd, LOG_PROMPT_REL)
    os.makedirs(os.path.dirname(duong), exist_ok=True)
    stamp = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
    with open(duong, "a", encoding="utf-8") as f:
        f.write(f"=== {stamp} {ma_task} ===\n{prompt}\n")
    return duong


# ----------------------------------------------------------------------- CLI

def cli(argv=None):
    p = argparse.ArgumentParser(prog="tdq_codex.py",
                                description=__doc__.split("\n")[0])
    p.add_argument("-C", "--cwd", default=".", help="repo root")
    sub = p.add_subparsers(dest="lenh", required=True)

    c = sub.add_parser("check", help="can this machine call Codex")
    c.add_argument("--json", action="store_true")

    m = sub.add_parser("setup-model", help="set the model name for mode codex")
    m.add_argument("ten")

    d = sub.add_parser("dong-y", help="the user approves mode codex (and names the model) in one step")
    d.add_argument("--model", default=None, help="model name; omitted → keep the one already set")

    r = sub.add_parser("run", help="run one task through Codex inside the declared file zone")
    r.add_argument("ma_task")
    r.add_argument("--prompt", required=True)
    r.add_argument("--model", default=None)
    r.add_argument("--vung", nargs="*", default=[], help="the file zone the task may touch")
    r.add_argument("--khoa", nargs="*", default=[], help="the locked zone, not to be touched")
    r.add_argument("--da-thay-do", action="store_true",
                   help="confirm the test was RUN and SEEN red before this turn")
    r.add_argument("--timeout", type=int, default=TIMEOUT_RUN)

    sub.add_parser("cleanup", help="delete every temporary CODEX_HOME")

    a = p.parse_args(argv)

    # One log line for EVERY sub-command, right at the entrance. Put it inside each branch and a
    # sub-command added later would run mute with nobody remembering — the default must be "speaks".
    log(f"{a.lenh} · cwd={a.cwd}")

    if a.lenh == "check":
        kq = check(a.cwd)
        log(f"check → runnable={kq['chay_duoc']}"
            + (f" · reason: {kq['ly_do']}" if kq["ly_do"] else ""))
        if a.json:
            print(json.dumps(kq, ensure_ascii=False))
        else:
            trang_thai = "runnable" if kq["chay_duoc"] else "NOT runnable"
            print(f"codex: {trang_thai}"
                  + (f" · {kq['phien_ban']}" if kq["phien_ban"] else ""))
            if kq["ly_do"]:
                print(f"  reason: {kq['ly_do']}")
                print(f"  fix: {kq['goi_y']}")
        return 0  # a machine without codex still exits 0 — that is an answer, not an error

    if a.lenh == "cleanup":
        return cleanup(a.cwd)

    if a.lenh == "run":
        return _cli_run(a)

    if a.lenh == "dong-y":
        return _cli_dong_y(a)

    co = doc_co_dong_y(a.cwd)
    dat_co_dong_y(a.cwd, co["nguoi_dung_dong_y"], model=a.ten)
    print(f"codex_model = {a.ten}")
    return 0


def _cli_dong_y(a):
    """The consent door that needs no `manifest.json`, so it works at the source repo root too.

    Same two conditions as `tdq_checkportable.cai_tang_codex`: the user typed it AND `codex` is on
    this machine. Missing `codex` → write nothing; a flag pointing at an absent CLI only misleads.
    """
    if not shutil.which("codex"):
        print("codex is not installed on this machine — install first: "
              "npm i -g @openai/codex (then `codex login`)")
        log("dong-y refused: codex not on PATH, flag not written")
        return 1
    model = a.model or doc_co_dong_y(a.cwd).get("codex_model") or None
    dat_co_dong_y(a.cwd, True, model=model)
    print(f"consent written to {CO_REL} · codex_model = {model or '(not set)'}")
    if not model:
        print("one step left: python3 scripts/tdq_codex.py setup-model <model-name>")
    return 0


def _cli_run(a):
    """One whole turn: check the beat → snapshot the mark → call Codex → verdict → zone audit.

    The audit lives INSIDE the turn rather than being left for the caller to remember: a "xong"
    turn that touched something outside the file zone is not done.
    """
    import tdq_vungfile

    kiem_nhip(a.da_thay_do)
    canh_bao = canh_bao_hook(*kiem_hook_ban(a.cwd))
    if canh_bao:
        log(canh_bao)
    model = chon_model(a.cwd, a.model)
    moc = tdq_vungfile.chup_moc(a.cwd)
    home = dung_codex_home(a.cwd, model)
    ghi_log_prompt(a.cwd, a.ma_task, a.prompt)

    file_schema = os.path.join(home, "schema.json")
    with open(file_schema, "w", encoding="utf-8") as f:
        json.dump(khuon_schema(), f)
    file_ket_qua = os.path.join(home, "ket-qua.json")

    lenh = dung_lenh(goc_repo=a.cwd, model=model, file_schema=file_schema,
                     file_ket_qua=file_ket_qua, prompt=a.prompt)
    khoa = tdq_vungfile.dung_vung_khoa(None, them=a.khoa)
    env = dung_env(a.cwd, home=home, ma_task=a.ma_task, vung=a.vung, khoa=khoa)

    bat_dau = time.time()
    qua_han = False
    try:
        proc = subprocess.run(lenh, env=env, **hop_dong_chay())
        exit_code, ra = proc.returncode, (proc.stdout or "")
    except subprocess.TimeoutExpired:
        exit_code, ra, qua_han = -1, "", True
    giay = time.time() - bat_dau

    ket_qua, ly_do_doc = doc_ket_qua_ly_do(file_ket_qua)
    trang_thai, ly_do = phan_quyet_ly_do(exit_code, ket_qua, ra, qua_han, ly_do_doc)
    in_log_luot(dong_log_luot(a.ma_task, model, home, giay, trang_thai, a.prompt, ly_do))

    kq = tdq_vungfile.hau_kiem(a.cwd, moc, a.vung, khoa)
    if trang_thai == "xong" and not kq.dat:
        trang_thai = "fail"

    print(json.dumps({"trang_thai": trang_thai, "giay": round(giay, 1),
                      "vung_file": kq.as_dict()}, ensure_ascii=False))
    return 0 if trang_thai == "xong" else 1


if __name__ == "__main__":
    sys.exit(cli())
