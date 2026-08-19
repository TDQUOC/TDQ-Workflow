# Routing work → plugin

**Status since 2026-08-06: EVERY plugin is already enabled at user scope.**

## Protocol

1. An enabled plugin → **use it directly, no permission needed**. The table below only picks
   the right plugin for the right job; it is no longer an approval gate.
2. You must still **ASK the user first** before: installing a NEW plugin/marketplace; running
   OAuth or entering a credential for a service; calling a tool that **writes or deletes on an
   external service** (create a Notion page, write to a DB, deploy, upload an asset…). Reading
   is free.
3. Code review → use the built-in `/code-review`, not another review plugin.

## Routing table

Use only the exact names in the right column.

| Work touches | Plugin |
|---|---|
| Airflow / DAG / data pipeline | data-engineering |
| Hugging Face / model training / ML dataset | huggingface-skills |
| Video / motion graphics | hyperframes |
| DataRobot | datarobot-agent-skills |
| Figma / design-to-code | figma |
| Qt / QML | qt-development-skills |
| Cloudflare Workers / Pages / Zero Trust | cloudflare |
| Canva | canva |
| Adobe / Photoshop / bulk image editing | adobe-for-creativity |
| MongoDB | mongodb |
| Postman / API collection testing | postman |
| Machine operations outside the repo (apps, system files) | desktop-commander |
| Base44 | base44 |
| Unreal Engine | unreal-engine-skills-for-claude-code |
| Notion | notion |
| Redis | redis-development |
| Large-scale web crawling | firecrawl |
| Browser debugging over CDP | chrome-devtools-mcp |
| Repo review/analysis via an external index | greptile |
| Static quality/security scanning | sonarqube |
| Log / trace observability | lumen |
| Per-language LSP | `<lang>-lsp` (clangd, gopls, jdtls, kotlin, lua, php, ruby, rust-analyzer, swift, csharp) |

Work matching no row → do it with the tools already at hand; do not drag a plugin in and pay
the context weight for nothing.

## Appendix

`~/.claude/plugin-tiers.json` has both `always_off` and `on_demand` EMPTY → the
SessionStart/SessionEnd hook running `plugin_tiers.py reset` is a no-op and turns no plugin
back off. The old tier file (lazy-load mode): `~/.claude/plugin-tiers.json.bak-2026-08-06`.

To go back to lazy-load for a lighter context: add the plugin name to `on_demand` (off by
default, re-enable with `python3 ~/.claude/scripts/plugin_tiers.py enable <tên>`) or to
`always_off` (never enabled) in `~/.claude/plugin-tiers.json` — only when the user asks for it
explicitly.
