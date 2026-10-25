---
name: tdq-browser-research
description: Deep web research and SPA web scraping through Chrome DevTools MCP. Uses adaptive polling and exponential backoff timeouts to prevent missing delayed AJAX data.
---

# TDQ Browser Research — Deep Scraping & Delayed-Response Handling
<!-- muc-luc-dong:
  Overview & Anti-Miss mandate=10-25 ·
  Adaptive Polling Engine=26-65 ·
  Execution steps=66-95 ·
  Reporting checklist=96-115
-->

Load [tdq-conventions](../tdq-conventions/SKILL.md) and [tavily](../tdq-conventions/references/tavily.md).
Target: extract accurate information from JavaScript-heavy Single Page Applications (SPA) without missing data due to delayed network responses.

## Overview & Anti-Miss Mandate

Standard curl or static web fetch tools fail on modern web apps rendered dynamically by client-side JavaScript.
This skill commands Chrome DevTools MCP to evaluate runtime state and wait defensively until delayed data settles.

Pre-condition: Ensure Chrome is running with Remote Debugging on port 9222.
Command: `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/tdq_devtool_mcp.py" launch`

## Adaptive Polling Engine (Anti-Miss)

When dealing with slow endpoints, heavy dashboards, or paginated data tables, apply defensive polling:

1. **Initial Navigation**:
   - Call `mcp__chrome-devtools__navigate_page` with `timeout: 30000` (30 seconds minimum).
2. **Double-Check DOM Readiness**:
   - Evaluate `() => document.readyState === 'complete'` via `mcp__chrome-devtools__evaluate_script`.
   - Check pending resource fetches: `() => performance.getEntriesByType('resource').filter(r => !r.responseEnd).length`.
3. **Exponential Backoff Polling Loop**:
   - Check targeted selector or keyword via `mcp__chrome-devtools__take_snapshot`.
   - If target data is absent, wait progressively: 500ms -> 1000ms -> 2000ms -> 4000ms (up to 30s ceiling).
   - Only declare data absent after 4 failed exponential backoff iterations.

## Execution Steps

1. **Launch & Connect**: Verify port 9222 is listening; call `mcp__chrome-devtools__list_pages`.
2. **Navigate & Stabilize**: Load target URL, wait for stable network activity.
3. **Interactive Navigation**:
   - Handle cookie consent banners by clicking accept buttons if present.
   - Trigger infinite scroll or pagination clicks (`mcp__chrome-devtools__click`) if needed.
4. **Data Extraction**:
   - Run `mcp__chrome-devtools__evaluate_script` to extract JSON payloads, structured tables, or article content.
   - For visual references or complex diagrams, take full-page screenshot into `docs/workinglog/images/`.

Done when: dynamic content is fully captured from rendered DOM without truncated or missing data blocks.
Next step: the phase does not change — summarize insights into docs/tdq/research/<slug>.md or return structured data to the caller.
