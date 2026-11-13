---
trigger: model_decision
description: When choosing tools for web research, browser testing, code navigation, AST architecture diagrams, or external integrations.
---

# Domain Rule: MCP-First & Companion Extensions

- Prioritize MCP tools over shell workarounds: `lsp` (65 tools via agent-lsp), `chrome-devtools` (E2E browser inspection), `tavily-primary` (external web search).
- Use Archify (`tdq_archify.py`) for Spec preview & Report HTML manifests, Graphify (`tdq_graphify.py`) for blast-radius graphs, Vision Diff (`tdq_vision_diff.py`) for pixel comparisons, and Codex CLI (`tdq_codex.py`) when `--mode codex` is active.
