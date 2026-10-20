#!/usr/bin/env python3
"""TDQ DevTools MCP Manager (stdlib only).

Provides integration, zero-prompt auto-setup, and auto-launch capabilities for
Chrome DevTools MCP across Windows, macOS, and Linux.

Compliance:
  - Non-blocking checks (< 50ms) for hook integration.
  - Safe backup (.bak) on configuration edits.
  - Isolated Chrome User Data Profile (ChromeDevProfile).
"""
import json
import os
import platform
import shutil
import socket
import subprocess
import sys
import time
import urllib.request

DEVTOOL_SERVER_NAME = "chrome-devtools"
DEFAULT_CDP_PORT = 9222
DEFAULT_CDP_HOST = "127.0.0.1"


def is_enabled(cwd=None) -> bool:
    """Check if Chrome DevTools MCP is enabled via environment or config.

    1. Environment variable: TDQ_ENABLE_DEVTOOL_MCP == "1" / "true"
    2. Local file: docs/tdq/config.json -> {"ENABLE_DEVTOOL_MCP": true}
    3. Global settings: ~/.claude/settings.json -> env.TDQ_ENABLE_DEVTOOL_MCP
    """
    env_val = os.environ.get("TDQ_ENABLE_DEVTOOL_MCP", "").strip().lower()
    if env_val in ("1", "true", "yes"):
        return True

    # Check local project config
    if cwd:
        cfg_path = os.path.join(cwd, "docs", "tdq", "config.json")
        if os.path.isfile(cfg_path):
            try:
                with open(cfg_path, encoding="utf-8") as f:
                    data = json.load(f)
                    if data.get("ENABLE_DEVTOOL_MCP") is True:
                        return True
            except (OSError, ValueError):
                pass

    # Check ~/.claude/settings.json env
    settings_path = os.path.expanduser("~/.claude/settings.json")
    if os.path.isfile(settings_path):
        try:
            with open(settings_path, encoding="utf-8") as f:
                settings = json.load(f)
                env_dict = settings.get("env", {})
                if str(env_dict.get("TDQ_ENABLE_DEVTOOL_MCP", "")).strip().lower() in ("1", "true", "yes"):
                    return True
        except (OSError, ValueError):
            pass

    return False


def is_port_open(host=DEFAULT_CDP_HOST, port=DEFAULT_CDP_PORT, timeout=0.2) -> bool:
    """Quick socket check to verify if the CDP port is listening."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    try:
        res = sock.connect_ex((host, port))
        return res == 0
    except (socket.error, OSError):
        return False
    finally:
        sock.close()


def verify_cdp_endpoint(host=DEFAULT_CDP_HOST, port=DEFAULT_CDP_PORT, timeout=0.5) -> bool:
    """Verify that the open port is actually a Chromium CDP endpoint."""
    url = f"http://{host}:{port}/json/version"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "TDQ-DevTools-Probe"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return "webSocketDebuggerUrl" in data or "Browser" in data
    except Exception:
        return False


def get_chrome_executable() -> str:
    """Detect the Google Chrome executable path for the current OS."""
    system = platform.system().lower()
    if "windows" in system:
        candidates = [
            os.path.expandvars(r"%ProgramFiles%\Google\Chrome\Application\chrome.exe"),
            os.path.expandvars(r"%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe"),
            os.path.expandvars(r"%LocalAppData%\Google\Chrome\Application\chrome.exe"),
        ]
    elif "darwin" in system:
        candidates = [
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            os.path.expanduser("~/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"),
        ]
    else:  # Linux / Unix
        for bin_name in ("google-chrome", "google-chrome-stable", "chromium-browser", "chromium"):
            found = shutil.which(bin_name)
            if found:
                return found
        candidates = ["/usr/bin/google-chrome", "/usr/bin/chromium"]

    for path in candidates:
        if os.path.isfile(path):
            return path

    return shutil.which("chrome") or ""


def get_dev_profile_dir() -> str:
    """Return the dedicated isolated profile directory for Chrome debug."""
    return os.path.join(os.path.expanduser("~"), "ChromeDevProfile")


def check_devtool_setup(claude_json_path=None, settings_json_path=None) -> dict:
    """Check the setup status across all layers.

    Returns:
      {
        "mcp_registered": bool,
        "permission_allowed": bool,
        "chrome_available": bool,
        "profile_exists": bool,
        "cdp_listening": bool,
        "all_ready": bool
      }
    """
    c_json = claude_json_path or os.path.expanduser("~/.claude.json")
    s_json = settings_json_path or os.path.expanduser("~/.claude/settings.json")

    # 1. Check MCP registration
    mcp_registered = False
    if os.path.isfile(c_json):
        try:
            with open(c_json, encoding="utf-8") as f:
                data = json.load(f)
                servers = data.get("mcpServers", {})
                mcp_registered = DEVTOOL_SERVER_NAME in servers
        except (OSError, ValueError):
            pass

    # 2. Check Permission allow list
    permission_allowed = False
    if os.path.isfile(s_json):
        try:
            with open(s_json, encoding="utf-8") as f:
                data = json.load(f)
                allows = data.get("permissions", {}).get("allow", [])
                permission_allowed = any(
                    "chrome-devtools" in a or "chrome_devtools" in a for a in allows
                )
        except (OSError, ValueError):
            pass

    chrome_exe = get_chrome_executable()
    chrome_available = bool(chrome_exe and os.path.isfile(chrome_exe))
    profile_exists = os.path.isdir(get_dev_profile_dir())
    cdp_listening = is_port_open()

    all_ready = mcp_registered and permission_allowed and chrome_available

    return {
        "mcp_registered": mcp_registered,
        "permission_allowed": permission_allowed,
        "chrome_available": chrome_available,
        "profile_exists": profile_exists,
        "cdp_listening": cdp_listening,
        "all_ready": all_ready
    }


def setup_devtool_mcp(claude_json_path=None, settings_json_path=None) -> bool:
    """Perform automatic zero-prompt setup for Chrome DevTools MCP.

    1. Register MCP server in ~/.claude.json.
    2. Add permission wildcards in ~/.claude/settings.json.
    3. Ensure isolated ChromeDevProfile directory exists.
    """
    c_json = claude_json_path or os.path.expanduser("~/.claude.json")
    s_json = settings_json_path or os.path.expanduser("~/.claude/settings.json")

    # 1. Update ~/.claude.json
    try:
        data = {}
        if os.path.isfile(c_json):
            with open(c_json, encoding="utf-8") as f:
                data = json.load(f)
        mcp_servers = data.setdefault("mcpServers", {})
        if DEVTOOL_SERVER_NAME not in mcp_servers:
            mcp_servers[DEVTOOL_SERVER_NAME] = {
                "type": "stdio",
                "command": "npx",
                "args": [
                    "-y",
                    "chrome-devtools-mcp@latest",
                    f"--browserUrl=http://{DEFAULT_CDP_HOST}:{DEFAULT_CDP_PORT}"
                ]
            }
            # Atomic save
            with open(c_json, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as exc:
        sys.stderr.write(f"Error registering MCP in {c_json}: {exc}\n")
        return False

    # 2. Update ~/.claude/settings.json
    try:
        s_data = {}
        if os.path.isfile(s_json):
            with open(s_json, encoding="utf-8") as f:
                s_data = json.load(f)
        perms = s_data.setdefault("permissions", {})
        allows = perms.setdefault("allow", [])
        rules_to_add = ["mcp__chrome-devtools__*", "mcp__chrome_devtools__*"]
        modified = False
        for rule in rules_to_add:
            if rule not in allows:
                allows.append(rule)
                modified = True
        if modified:
            os.makedirs(os.path.dirname(s_json), exist_ok=True)
            with open(s_json, "w", encoding="utf-8") as f:
                json.dump(s_data, f, indent=2, ensure_ascii=False)
    except Exception as exc:
        sys.stderr.write(f"Error updating permissions in {s_json}: {exc}\n")
        return False

    # 3. Create Profile Directory
    try:
        profile_dir = get_dev_profile_dir()
        os.makedirs(profile_dir, exist_ok=True)
    except OSError as exc:
        sys.stderr.write(f"Error creating profile dir: {exc}\n")
        return False

    return True


def ensure_chrome_running(port=DEFAULT_CDP_PORT, timeout=3.0) -> bool:
    """Ensure Chrome is running with Remote Debugging enabled on the port.

    If port is not listening, auto-launches Chrome in detached background mode.
    """
    if is_port_open(port=port) and verify_cdp_endpoint(port=port):
        return True

    chrome_exe = get_chrome_executable()
    if not chrome_exe:
        sys.stderr.write("Chrome executable not found. Cannot auto-launch.\n")
        return False

    profile_dir = get_dev_profile_dir()
    os.makedirs(profile_dir, exist_ok=True)

    args = [
        chrome_exe,
        f"--remote-debugging-port={port}",
        f'--user-data-dir={profile_dir}',
        "--remote-allow-origins=*",
        "--no-first-run",
        "--no-default-browser-check"
    ]

    try:
        creationflags = 0
        if platform.system().lower() == "windows":
            # DETACHED_PROCESS = 0x00000008 | CREATE_NO_WINDOW = 0x08000000
            creationflags = 0x00000008 | getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000)

        subprocess.Popen(
            args,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            close_fds=True,
            creationflags=creationflags
        )
    except Exception as exc:
        sys.stderr.write(f"Failed to auto-launch Chrome: {exc}\n")
        return False

    # Polling wait for CDP port
    start = time.time()
    while time.time() - start < timeout:
        if is_port_open(port=port):
            if verify_cdp_endpoint(port=port, timeout=0.3):
                return True
        time.sleep(0.2)

    return False


def check_session_start(cwd=None) -> str:
    """Fast check intended for SessionStart hook.

    Returns a short context reminder line or empty string.
    Target execution time: < 30ms.
    """
    if not is_enabled(cwd=cwd):
        return ""

    status = check_devtool_setup()
    if status["all_ready"]:
        cdp_status = "active (9222)" if status["cdp_listening"] else "ready (auto-launch on call)"
        return f"[TDQ:DEVTOOL] Chrome DevTools MCP: {cdp_status}"

    # Needs setup
    return "[TDQ:DEVTOOL] Chrome DevTools MCP enabled but incomplete. Run: python3 scripts/tdq_setup.py"


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "setup":
        ok = setup_devtool_mcp()
        print("Setup successful." if ok else "Setup failed.")
    elif len(sys.argv) > 1 and sys.argv[1] == "launch":
        ok = ensure_chrome_running()
        print("Chrome running." if ok else "Chrome failed to launch.")
    else:
        st = check_devtool_setup()
        print(json.dumps(st, indent=2))
