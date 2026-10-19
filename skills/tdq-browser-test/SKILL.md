---
name: tdq-browser-test
description: E2E and visual UI/UX verification through Chrome DevTools MCP. Audits DOM structure, viewport responsiveness, element interactions, and console errors.
---

# TDQ Browser Test — Comprehensive 5-Layer UI/UX Audit
<!-- muc-luc-dong:
  Overview & Anti-Shallow mandate=10-25 ·
  Five inspection layers=26-75 ·
  Auto-Launch Chrome CDP=76-90 ·
  Reporting checklist=91-115
-->

Load [tdq-conventions](../tdq-conventions/SKILL.md) and [vision-test-loop](../tdq-build/references/vision-test-loop.md).
Target: eliminate shallow UI checks where an AI agent only peeks at HTML strings without verifying actual rendered behavior.

## Overview & Anti-Shallow Mandate

Never conclude that a web interface passes QC by checking static HTML or asserting that a class exists.
Every UI task requires active browser verification through Chrome DevTools MCP.

Pre-condition: Ensure Chrome is running with Remote Debugging on port 9222.
Command: `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/tdq_devtool_mcp.py" launch`

## Five Inspection Layers

### Layer 1: Structural Tree & Accessibility DOM Audit
1. Call `mcp__chrome-devtools__navigate_page` to the local or remote target URL.
2. Call `mcp__chrome-devtools__take_snapshot` to extract the accessibility tree.
3. Verify every primary layout region: Header, Navigation bar, Main content container, Form inputs, and Action buttons.
4. Ensure no critical container is empty or collapsed to 0px.

### Layer 2: Viewport Responsiveness & Visual Capture
1. **Desktop Baseline (1440x900)**:
   - Call `mcp__chrome-devtools__resize_page` with width 1440, height 900.
   - Call `mcp__chrome-devtools__take_screenshot` and review layout bounds.
2. **Mobile Viewport (375x812)**:
   - Call `mcp__chrome-devtools__resize_page` with width 375, height 812.
   - Verify layout stacks vertically without horizontal scrollbar overflow.
   - Capture mobile screenshot into `docs/workinglog/images/`.

### Layer 3: Interactive Element States (Hover, Focus, Submit)
1. **Hover & Focus**:
   - Call `mcp__chrome-devtools__hover` on navigation links, buttons, and card components.
   - Confirm active/focus styles trigger properly.
2. **Form Interaction**:
   - Call `mcp__chrome-devtools__fill_form` with boundary values (empty, Unicode, overlong string).
   - Call `mcp__chrome-devtools__click` to trigger form submission or state transitions.
   - Confirm validation error messages or success banners appear.

### Layer 4: Silent Fault Detection (Console & Network)
1. Call `mcp__chrome-devtools__list_console_messages` with types `["error", "warn"]`.
2. Any unhandled JavaScript error or uncaught promise rejection is an immediate FAIL.
3. Call `mcp__chrome-devtools__list_network_requests`.
4. Verify no critical static asset (CSS, JS, fonts) or API call returned HTTP 4xx or 5xx.

### Layer 5: CSS Cascade & Styling Health
1. Call `mcp__chrome-devtools__get_css_styles` on disputed elements.
2. Verify font sizes, contrast ratios, and cascade layers (`@layer`) are not overloaded unintentionally.

## Auto-Launch & Session Recovery

When `mcp__chrome-devtools__*` tools return connection refused:
1. Run `python3 scripts/tdq_devtool_mcp.py launch` to spin up Chrome with `--remote-debugging-port=9222`.
2. Wait 2 seconds for port readiness, then resume test flow.

## Reporting Checklist

Every UI/UX test run must output a structured verification block:
- **URL Tested**: target endpoint.
- **Tree Verification**: count of validated interactive elements.
- **Responsive Status**: Desktop PASS, Mobile PASS.
- **Console Log Status**: 0 errors, warnings recorded.
- **Artifacts Saved**: paths to generated screenshots.

Done when: all 5 inspection layers pass without unhandled errors, responsive viewports verified, and screenshots captured.
Next step: proceed to write QC evidence into docs/tdq/qc/<slug>.md or report findings.
