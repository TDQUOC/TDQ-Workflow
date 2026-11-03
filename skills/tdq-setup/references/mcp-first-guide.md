# MCP-first connection and recovery guide

## When it applies

Use for tool discovery, spec/plan capability choices and runtime operations. Inventory, schema,
connection and permission are separate checks; a configured server does not prove readiness.

## What to do

1. Identify the goal, input file, destination and authorized action. Make short internal steps
   with a completion check; ask only for missing facts that change the result.
2. Inspect tools and skills available in this session. Prefer specialized MCP tools over blind
   shell/UI guesses, but use one tool if sufficient; do not add hops for their own sake.
3. Pre-flight Check: probe the actual configured connection before a deep operation or delegation. Default ports
   below are examples, not proof that the server uses them.

| Runtime | Safe probe | Ready means |
|---|---|---|
| Chrome DevTools MCP | Configured CDP endpoint, e.g. `http://127.0.0.1:9222/json/version`, then page listing | Endpoint responds and intended page/profile is identifiable |
| Unity Engine | Configured Editor MCP status/socket | Editor/plugin handshake succeeds |
| Roblox Studio | Configured Studio plugin bridge status | Intended Place is connected |
| Database | Authorized read-only `SELECT 1` | Connection responds within its permission scope |
| Native desktop | Installed agent-desktop status and fresh window snapshot | Interactive session and intended process/window are accessible |

4. Web uses Chrome MCP. Native dialogs/apps use agent-desktop when needed; local file work uses
   dedicated file/CLI tools. Direct upload_file is preferred if exposed and file is accessible
   on the browser host. A JavaScript dialog handler is not a Windows file-picker handler.
5. On handoff, verify page/process/window identity, file and destination from fresh observations.
   After upload, verify attachment. After download/Save As, verify final file existence, type
   and expected content; a click or partial download is insufficient.
6. Disconnected installed tool: inspect the cause; launch/reconnect the existing app or dedicated
   profile only within existing authorization. Probe again. Do not close personal windows,
   overwrite profiles, run OAuth or change permission settings to force readiness.
7. If recovery needs user interaction, provide the exact connection instructions and blocker.
   Do not guess runtime state or claim success. Never bypass a denied action with another tool.
8. Missing tool or dependency (including LSP): research official sources, confirm OS support,
   propose user-level installation, required permissions, verification and uninstall commands.
   Wait for user approval before installing; do not fetch/run installers merely to probe them.
9. Delivery unknown: observe destination before retrying a send/upload. Retry only after new
   evidence or changed conditions; no-progress failures end with a blocker. Prefer completion
   events/tool waits to tight polling. Report partial and unsupported work separately.

## Connection instructions

- Chrome: use an existing dedicated debug profile and configured localhost endpoint; never ask
  to close all personal Chrome windows. If approved and already installed, the existing
  `python scripts/tdq_devtool_mcp.py launch` path may start it. Check its scope before invoking.
- Unity: open the intended project, open the installed MCP plugin's status panel and start its
  configured server. Menu names depend on the installed plugin; inspect rather than invent.
- Roblox: open the intended Place and enable the installed bridge. If a setting or permission
  change is required, explain it and request authorization instead of changing it silently.
- Native desktop: use the current interactive session. UAC secure desktop, a locked desktop
  and another session are unsupported; do not elevate or alter ACLs to bypass them.

## Self-check

Does each claimed result have observable evidence? Does every recovery keep the original
permission scope, identity and destination? Were missing tools proposed rather than installed?
RIGHT: reconnect an authorized test profile, probe, upload directly, verify attachment and file.
WRONG: assume a configured server is live, force a native hop, install without approval or
repeat an upload after timeout without checking whether it already arrived.
