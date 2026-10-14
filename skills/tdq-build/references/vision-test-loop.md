# User-Scenario-Driven Testing and the Vision Test Loop
<!-- muc-luc-dong:
  Table of contents=13-23 · Trigger decision table=24-37 · Three-tier scenario framework=38-48 ·
  Six banned test anti-patterns (ANTI-1 to ANTI-6)=49-75 ·
  The 6 steps of the Vision Test Loop=76-112 · Bounding box to CSS mapping table=113-124 ·
  Loop caps and Reviewer Sub-agent=125-130 · Human-in-the-loop escalations=131-143 ·
  Self-check=144
-->

Soul: chất lượng > runtime > context cost · luật gốc: ../../tdq-conventions/references/soul.md <!-- i18n-allow: canonical Soul line -->
This reference gives a mechanical, step-by-step runbook so every model tier executes scenario tests and visual verification identically.

## Table of contents

- [Trigger decision table](#Trigger decision table)
- [Three-tier scenario framework](#Three-tier scenario framework)
- [Six banned test anti-patterns (ANTI-1 to ANTI-6)](#Six banned test anti-patterns (ANTI-1 to ANTI-6))
- [The 6 steps of the Vision Test Loop](#The 6 steps of the Vision Test Loop)
- [Bounding box to CSS mapping table](#Bounding box to CSS mapping table)
- [Loop caps and Reviewer Sub-agent](#Loop caps and Reviewer Sub-agent)
- [Human-in-the-loop escalations](#Human-in-the-loop escalations)
- [Self-check](#Self-check)

## Trigger decision table

Do not guess whether the Vision Test Loop applies; match the request against this table before coding.
Every visual task with a reference artifact must run the loop so the user does not have to give multi-round feedback.

| Reference artifact provided or mentioned | Loop required? | CLI flag to pass to `tdq_vision_diff.py` | Action when the artifact is missing or locked |
|---|---|---|---|
| Local mockup image (`.png`, `.jpg`, `.webp`) | YES — MANDATORY | `--source <path/to/mockup.png>` | Run `pause --loai dau-vao-user` and ask for the file path | <!-- i18n-allow: canonical pause kind -->
| Wireframe or layout sketch image | YES — MANDATORY | `--source <path/to/wireframe.png> --threshold 0.05` | Run `pause --loai dau-vao-user` and ask for the wireframe | <!-- i18n-allow: canonical pause kind -->
| Reference screenshot or baseline UI capture | YES — MANDATORY | `--source <path/to/screenshot.png>` | Run `pause --loai dau-vao-user` and ask for the baseline image | <!-- i18n-allow: canonical pause kind -->
| HTML/web prototype or live reference URL | YES — MANDATORY | Capture reference to `source.png`, then pass `--source source.png` | Run `pause --loai dau-vao-user` if the prototype URL is unreachable | <!-- i18n-allow: canonical pause kind -->
| Figma link (`https://www.figma.com/...`) | YES — MANDATORY | `--figma-url "<url>"` (reads `FIGMA_TOKEN` from env) | Exit code `3` → run `pause --loai dau-vao-user` and ask for `FIGMA_TOKEN` or a local export | <!-- i18n-allow: canonical pause kind -->
| Pure backend, CLI, or UI without any visual reference | NO — SKIP LOOP | Do not run `tdq_vision_diff.py` | Run the three-tier scenario tests only |

## Three-tier scenario framework

Every test in `spec`, `plan`, `implement`, and `qc` must represent a real user journey rather than an implementation detail.
Write each test scenario using the exact `Given - When - Then` formula across all three mandatory tiers:

| Tier | Name | Mandatory `Given - When - Then` formula | Minimum required per feature |
|---|---|---|---|
| Tier 1 | Core User Journey (Happy Path) | **Given** realistic user state and input · **When** the user triggers the public entry point · **Then** the final output, persisted state, and rendered UI match the expected result | At least 1 end-to-end flow |
| Tier 2 | Boundary & Edge Scenarios | **Given** empty, maximum-length, Unicode, or concurrent input · **When** the action runs · **Then** layout and state stay intact without truncation or crash | At least 2 boundary cases |
| Tier 3 | Failure & Recovery Scenarios | **Given** a network timeout, missing token, or invalid payload · **When** the call fails · **Then** a clear error appears, state rolls back cleanly, and the user can retry | At least 1 failure recovery case |

## Six banned test anti-patterns (ANTI-1 to ANTI-6)

Never write a test that matches any of the six patterns below; `tdq-qc-tester` rejects a task on sight when any `ANTI-*` pattern appears.

| Code | Anti-Pattern name | Mechanical detection rule | Required replacement |
|---|---|---|---|
| `ANTI-1` | Tautological / Mock-Returns-Mock | Mocking the function under test and asserting the mock's own return value | Call the real function or pipeline and assert on the produced output |
| `ANTI-2` | Existence-Only Assertion | Asserting only `is not None`, `True`, or `status == 200` without checking payload fields | Assert exact field values, data structure invariants, and state transitions |
| `ANTI-3` | Happy-Path-Only Bias | Writing tests that only pass valid inputs while ignoring malformed or missing inputs | Add Tier 2 boundary tests and Tier 3 failure tests in the same test file |
| `ANTI-4` | Source-String / Regex Scraping | Reading `.py` or `.html` source text with `in` or regex instead of executing the code | Import and run the function, CLI, or DOM render and check runtime behavior |
| `ANTI-5` | Implementation-Coupled Spying | Asserting internal private helper call counts instead of public outputs | Assert only on the public return value, files written, or observable side effects |
| `ANTI-6` | Blind Visual / DOM-Only UI Check | Checking only that `<div class="card">` exists without pixel comparison against the reference design | Render the page in a headless browser and run `tdq_vision_diff.py` |

```python
# WRONG (ANTI-1 + ANTI-2 + ANTI-4) — mocks the unit under test and checks only not-None:
def test_bad_report(mocker):
    mocker.patch("tdq_vision_diff.write_reports", return_value={"passed": True})
    result = tdq_vision_diff.write_reports()
    assert result is not None

# RIGHT (Tier 1 + Tier 3) — runs the real function on real images and asserts exact metrics:
def test_real_report_and_missing_token(tmp_path):
    rc = tdq_vision_diff.main(["--figma-url", "https://figma.com/file/abc/x?node-id=1-2",
                               "--dist", str(tmp_path / "d.png"), "--out-dir", str(tmp_path)])
    assert rc == 3  # Tier 3: missing FIGMA_TOKEN returns exit code 3 cleanly
```

## The 6 steps of the Vision Test Loop

When the Trigger decision table says **YES**, execute these 6 numbered steps in exact order without skipping any step:

1. Prepare the reference image (`source.png`) and the rendered build screenshot (`dist.png`) at the same viewport width and height.
   If the reference is a prototype HTML/URL, open it in `cloudcli-browser`, capture `source.png`, then capture the built UI to `dist.png`.

2. Run `scripts/tdq_vision_diff.py` to normalize the canvas, mask dynamic zones, compute pixel diff, draw numbered red bounding boxes `[1]`, `[2]`, and emit the dual `.md` + `.html` reports:
   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/tdq_vision_diff.py" \
     --source "<path/to/source.png>" \
     --dist "<path/to/dist.png>" \
     --out-dir "docs/tdq/reports/vision-<slug>" \
     --slug "<slug>" \
     --threshold 0.02 \
     --color-tolerance 12 \
     --ignore-boxes "0,0,0,0" \
     --round 1
   ```
   For a self-contained single-file HTML report, append `--embed-base64`.

3. Inspect the exit code and `docs/tdq/reports/vision-<slug>/metrics.json`:
   - Exit code `0` (`passed: true`, `mismatch_rate <= threshold`): proceed to Step 5 (Reviewer Sub-agent check).
   - Exit code `1` (`passed: false`, `mismatch_rate > threshold`): proceed to Step 4 (Self-healing CSS/HTML fix).
   - Exit code `3` (missing `FIGMA_TOKEN` or inaccessible reference URL): stop immediately and run the `dau-vao-user` pause command in the escalation section below. <!-- i18n-allow: canonical pause kind -->

4. Fix every numbered red bounding box `[1]`, `[2]` in `diff_highlight.png` and `<slug>.md`:
   - Read the `(x, y, w, h)` coordinates of each box `[1]`, `[2]` in `<slug>.md` or `metrics.json`.
   - Map each box to the DOM element at that position using the Bounding box to CSS mapping table below.
   - Edit the CSS/HTML to fix all boxes in a single batch, recapture `dist.png`, increment `--round`, and rerun Step 2.

5. Dispatch the independent Reviewer Sub-agent (`tdq-reviewer` or `tdq-qc-tester`) with `source.png`, `dist.png`, `diff_highlight.png`, and `<slug>.md`:
   - The Reviewer Sub-agent checks semantic fidelity (text truncation, broken icons, overlapping labels, contrast) that pixel ratios can miss.
   - The Reviewer Sub-agent is capped at **at most 1 feedback round** per task to prevent ping-pong loops.

6. Link both generated reports (`docs/tdq/reports/vision-<slug>/<slug>.md` and `<slug>.html`) in the QC file and final Report so the user can open the interactive slider, onion-skin overlay, and bounding box explorer immediately.

## Bounding box to CSS mapping table

Low-tier models must use this lookup table to translate each red box `[N]` on `diff_highlight.png` into a concrete code edit:

| Visual symptom inside red box `[N]` | Root cause in DOM / CSS | Exact CSS / HTML property to adjust |
|---|---|---|
| Red outline forms a thin shifted border around a card or button | Element position or spacing is offset by a few pixels | Check `margin`, `padding`, `gap`, `top`, `left`, and `box-sizing: border-box` |
| Red block covers a heading or paragraph width | Font size, weight, or line wrap differs from the reference | Check `font-size`, `font-weight`, `line-height`, `letter-spacing`, and `max-width` |
| Solid red fill across a container background or badge | Background color, gradient, or border radius does not match | Check `background-color`, `background-image`, `border-radius`, and `border-color` |
| Multiple boxes `[1]`, `[2]`, `[3]` shifted in the same direction | A parent flex/grid container has the wrong alignment or gap | Fix the parent container's `display`, `justify-content`, `align-items`, or `grid-template-columns` first |
| Red box sits over a live clock, random avatar, or ad banner | Dynamic content changed between captures | Add the region's `x,y,w,h` to `--ignore-boxes` instead of changing CSS |

## Loop caps and Reviewer Sub-agent

- **Hard cap of 3 rounds**: never run more than 3 rounds (`--round 1`, `2`, `3`) of automated visual fixing on a single task.
- **Early stop on plateau**: if Round `N` improves `mismatch_rate` by less than `0.002` (`0.2%`) compared to Round `N-1`, stop the loop immediately instead of burning tokens on Round `N+1`.
- **Single Reviewer Sub-agent turn**: the Reviewer Sub-agent may return at most 1 consolidated feedback list; apply it in one pass and do not re-loop with the reviewer.

## Human-in-the-loop escalations

When the loop cannot proceed automatically, run the exact pause command below and report to the user in chat:

- Missing reference file, unreachable prototype, or exit code `3` (`FIGMA_TOKEN` missing/denied):
  ```bash
  python3 "${CLAUDE_PLUGIN_ROOT}/scripts/tdq_state.py" pause --loai dau-vao-user --ly-do "Missing visual reference or FIGMA_TOKEN for Vision Test Loop"
  ```
- `mismatch_rate` still exceeds `--threshold` after 3 rounds or hits an early-stop plateau:
  ```bash
  python3 "${CLAUDE_PLUGIN_ROOT}/scripts/tdq_state.py" pause --loai tran-qc --ly-do "Vision Test Loop reached 3-round cap; see <slug>.html and diff_highlight.png"
  ```

## Self-check

- [ ] Checked the Trigger decision table for every mockup, wireframe, screenshot, prototype, or Figma reference
- [ ] Wrote tests covering Tier 1 (Happy Path), Tier 2 (Boundary), and Tier 3 (Failure Recovery) using `Given - When - Then`
- [ ] Confirmed zero `ANTI-1` through `ANTI-6` patterns exist in the test suite
- [ ] Ran `tdq_vision_diff.py` and verified `metrics.json`, `diff_highlight.png`, `<slug>.md`, and `<slug>.html` exist
- [ ] Resolved all red bounding boxes `[1]`, `[2]` within ≤ 3 rounds and ≤ 1 Reviewer Sub-agent turn
