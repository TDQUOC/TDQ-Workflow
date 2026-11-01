# Runtime speed without weaker evidence
<!-- muc-luc-dong:
  When it applies=6-11 · What to do=12-74 · Self-check=75
-->

## When it applies

Use this guide when a request repeats test execution, static readiness probes or transcript
parsing, or when independent read calls are waiting unnecessarily. An opt-in flag alone does
not establish a speed improvement. Keep the approved gates, case inventory and QC requirements.

## What to do

1. Keep the defaults: one test worker, test reuse off, readiness cache off and transcript
   cache off. Run final correctness with fresh execution. From the project root:

   ```sh
   python scripts/tdq_test.py tron-bo --repo . --workers 1 --fresh --reuse off --timeout-seconds 1800
   ```

2. Batch only independent read calls. Await every result and inspect each failure separately.
   Keep mutations, approvals, lock transitions and dependent calls sequential. `&&` does not
   execute commands concurrently. Do not overlap benchmark samples with any other test job.

3. Use bounded test parallelism only after measuring the current suite. `--workers 2` opts in;
   legacy `--parallel` means two workers. Supplying both is a usage error. Collection and
   execution share a per-job timeout; each job and worker receives private temporary paths.
   Two workers do not by themselves prove that tests have independent external resources.

4. Enable test reuse explicitly with `--reuse auto` only for a scope with a validated
   `docs/tdq/reuse-policy.json` dependency declaration. Missing or unknown dependencies keep
   the scope ineligible and execute fresh. Never infer eligibility from a previous PASS.
   Collection, content hashing and evidence verification still cost time on a warm call.
   `executed`, `reused` and `joined` have distinct provenance; waiting for a job is not a second
   execution. A joined failure stays a failure. `--fresh` requires execution and invalidates
   old reusable evidence; if safe invalidation fails, the operation fails before execution.

5. Opt into static readiness reuse with `--readiness-cache auto` on `tdq_setup.py` or on
   `tdq_lsp.py check`. The active request supplies the namespace; `--request` can name it
   explicitly. Cache hits do not skip live doctor/connection, configuration, graph freshness
   or effect checks. Keep setup and its dependent check sequential so the check sees the
   completed setup. Cache lookup errors fall back to fresh probes.

6. Opt into normalized transcript parsing reuse with `--transcript-cache auto` on
   `tdq_timing.py`. Content is still read and hashed; changed files are parsed again. Filters,
   deduplication, aggregation and quality are recomputed. Active or unreadable files do not
   become complete merely because older cached data exists. Cache artifacts must not contain
   raw prompts, tool payloads, secrets or copied personal configuration.

7. Measure before recommending an opt-in. Run at least three serial/parallel pairs in
   AB/BA/AB order on the same source, inventory and environment, with reuse off. Recommend
   two workers only when correctness matches and median wall time improves by at least 20%.
   For each cache, retain at least three off/cold/warm triples, including hashing, verification,
   waiting and execution costs. Compare warm against off, and report cold overhead separately.
   Retain failed samples and retries. Use `tdq_runtime_bench.py` and its `verify` command for
   bound sample evidence; correctness failures never qualify as a performance fallback.

8. If measurements do not meet the threshold, keep serial/off and record the approved
   performance fallback with `tdq_state.py lech add`. Report fixtures as simulation; real log
   parsing is a separate workload. Do not extrapolate either into a whole-session speedup.
   Wall time and summed process resource time are different measures. Mark unavailable CPU
   measurements unavailable, and do not add overlapping saved-time estimates together.

9. Roll back an opt-in by selecting `--workers 1 --fresh --reuse off`,
   `--readiness-cache off` and `--transcript-cache off`. No cache deletion or personal-config
   edit is required. Cache retention may remove only the validated request namespace.
   `TDQ_LOG=0` disables metadata diagnostics; it does not disable tests or evidence checks.

RIGHT: two independent source reads run concurrently; the next decision waits for both.
WRONG: run setup and its readiness check concurrently, or hide a failed benchmark sample.

RIGHT: a faster warm cache is recommended only after comparison with cache off.
WRONG: call warm faster because it beats a very slow cold run while remaining slower than off.

## Self-check

Does every speed recommendation have current, source-bound measurements with equal case
outcomes, all samples retained, real/simulation labels and a working serial/off fallback?
If not, report the option as unverified and retain the defaults. A code change after measurement
requires renewed evidence for the affected measurements before recommending that code.
