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
| User interface: style, palette, font, token, component (web/mobile/desktop) | ui-ux-pro-max |
| Repo review/analysis via an external index | greptile |
| Static quality/security scanning | sonarqube |
| Log / trace observability | lumen |
| Per-language LSP | `<lang>-lsp` (clangd, gopls, jdtls, kotlin, lua, php, ruby, rust-analyzer, swift, csharp) |

Work matching no row → do it with the tools already at hand; do not drag a plugin in and pay
the context weight for nothing.

## UI/UX — three layers

Interface work splits into three layers, and they are NOT looked up in the same place:

1. **Product strategy** — who it is for, which flow, which metric decides it is good. No plugin
   covers this; ask the user and write it into the spec.
2. **Design decisions** — style, palette, font pairing, token, component, per-framework rules.
   This is where `ui-ux-pro-max` is strong, and it is the ONLY layer it covers.
3. **Verification on a real machine** — a11y, lighthouse, measuring layout while it runs:
   `chrome-devtools-mcp` (`a11y-debugging`, `lighthouse_audit`). `ui-ux-pro-max` has no such layer.

`ui-ux-pro-max` is a CATALOGUE TO CONSULT, not a step to execute. Treat it as the reference book
Claude Code opens when it wants a grounded option — 88 styles, 192 palettes, 74 font pairings,
119 UX guidelines, 22 stacks — then decides for itself. Its 7 skills: `ui-ux-pro-max` (the search
engine over that data), `ui-styling` (shadcn/Tailwind components), `design-system` (three-layer
tokens), `design` (the umbrella skill), `brand`, `banner-design`, `slides`.

Strength of the rule: default to consulting it when the work lands in layer 2; it may be skipped,
just write one line saying why.

Scope: every real user interface — web, mobile, desktop. Not for Unity/game work: the data set has
no row for Unity or Unreal, and that work belongs to the `unity-*` skills.

Combines with, never exclusive — use them together when the two make the result better:

- `frontend-design` — builds the web UI for real; `ui-ux-pro-max` picks the palette/font/token
  first, `frontend-design` writes the code.
- `figma` — a design file already exists → figma is the source of truth (design-to-code);
  `ui-ux-pro-max` only fills the gaps the design leaves open.
- `chrome-devtools-mcp` — once it is built, measure it again at layer 3.

## Appendix

`~/.claude/plugin-tiers.json` has both `always_off` and `on_demand` EMPTY → the
SessionStart/SessionEnd hook running `plugin_tiers.py reset` is a no-op and turns no plugin
back off. The old tier file (lazy-load mode): `~/.claude/plugin-tiers.json.bak-2026-08-06`.

To go back to lazy-load for a lighter context: add the plugin name to `on_demand` (off by
default, re-enable with `python3 ~/.claude/~/.gemini/config/plugins/tdq-workflow/scripts/plugin_tiers.py enable <name>`) or to
`always_off` (never enabled) in `~/.claude/plugin-tiers.json` — only when the user asks for it
explicitly.
