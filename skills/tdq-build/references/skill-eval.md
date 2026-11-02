# Skill and Plugin Quality Evaluation
<!-- muc-luc-dong:
  1. Purpose and scope=10-23 · 2. Preflight and isolation=24-36 · 3. Eval-plan contract=37-51 ·
  4. Execution and pairing=52-62 · 5. Metrics and reporting=63-77 ·
  Ultracode routing evaluation=78-83 · 6. Decision policy=84
-->

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## 1. Purpose and scope

This procedure governs quality, behavioral, and efficiency evaluation for TDQ
skills, hooks, and plugins. It applies whenever a change alters instruction text,
metadata affecting triggers, or hook execution behavior.

- **Offline gates**: Workflow gates (`pre_implement`, `pre_report`) inspect plans and
  evidence offline. Gates never launch model sessions or generate synthetic PASS marks.
- **Scope classifier**: Pure documentation (`README.md`, `CHANGELOG*.md`), bookkeeping
  edits (dates, version numbers, status checkboxes), and unrelated application code are
  exempt from evaluation requirements.
- **No unverified certification**: Historical records lacking full host/model/tool provenance
  are tagged `historical_unverified` and cannot certify a candidate branch.

## 2. Preflight and isolation

Evaluation trials must run under strict isolation on supported hosts (`claude`, `codex`):

- **No credential scraping**: Never access macOS Keychain, Windows Credential Store, or
  unauthorized configuration stores to guess tokens. Preflight uses `--version` or native
  capability probes; it never sends a dummy prompt ("say hi") to test connectivity.
- **Environment isolation**: Each trial executes with a dedicated temporary `workspace`,
  `home`, and `config` directory (`CLAUDE_CONFIG_DIR`, `CODEX_HOME`). Trials must not
  point at the user's real `$HOME` or inherit unisolated global plugins.
- **Owned processes**: Subprocess lifecycles use Windows Job Objects or POSIX process groups
  via `OwnedProcessJob`. Descendants are terminated cleanly on timeout or failure.

## 3. Eval-plan contract

Before code implementation starts, an evaluation plan must be locked via
`scripts/tdq_skill_eval.py plan` or registered in workflow state:

- **Plan fields**: `plan_version`, `experiment_id`, `targets`, `base_identity`,
  `candidate_identity`, `change_kind`, `hypothesis`, `evaluation_kind`, `corpus_id`,
  `dev_cases_sha256`, `holdout_cases_sha256`, `rubric_version`, `scorer_version`,
  `expected_triggers`, `negative_cases`, `required_metrics`, `cells`, `repetitions`,
  `order_policy`, and `thresholds`.
- **Identity invariants**: Model aliases (`latest`, `default`, `auto`) and non-finite
  numbers (`NaN`, `Inf`) are rejected.
- **Experiment hash**: Changes to corpus, targets, or scorers alter the experiment hash,
  making previous trial evidence stale.

## 4. Execution and pairing

Trials must be executed through `scripts/tdq_skill_eval.py run`:

- **Balanced pairing**: Repetitions alternate between `AB` and `BA` orders across identical
  evaluation cells to prevent position and cache bias.
- **Finite budgets**: Quotas, deadlines, and retry caps are strictly enforced. All trial
  attempts are recorded; failed attempts are never deleted to present an artificial pass rate.
- **Streaming verification**: Raw JSONL transcripts are hashed streaming with chunked SHA-256.
  Transcripts exceeding size or event budgets fail immediately rather than truncating silently.

## 5. Metrics and reporting

The report generator (`scripts/tdq_skill_eval.py report`) runs fully offline:

- **Three metric groups**:
  1. `trigger_accuracy`: expected vs observed invocation with provenance.
  2. `outcome_quality`: deterministic oracle checks, task pass/fail, execution status.
  3. `efficiency_metrics`: token usage (input, output, cache read/write), latency,
     retries, and tool calls.
- **Cost provenance**: Missing costs remain `null` with `availability: "unavailable"`.
  Costs are never reported as `$0.00` when unobserved. Reports clearly separate
  `observed_usage`, `rate_estimate` (derived from dated rate cards), and `provider_billed`.
- **Cell separation**: Results are grouped per `(host, model)` cell. Aggregating across
  disparate hosts or models into a single score is prohibited.

## Ultracode routing evaluation

Compare Workflow with batch Agent on the same case/host/model/permission envelope. KEEP only when
unique verified findings or completeness rises without higher false-positive rate; token/latency
remain reported evidence, not ceilings.

## 6. Decision policy

Recommendations are deterministic and categorized into four verdicts:

- `KEEP`: Candidate demonstrates superior outcome quality or trigger precision with
  statistically sufficient sample sizes.
- `TRIM`: Candidate matches baseline quality while reducing complexity, latency, or token cost.
- `DROP`: Candidate regresses on quality, misses critical guardrails, or increases cost
  without quality benefit.
- `INCONCLUSIVE`: Sample size is below minimum threshold, primary metrics are unavailable,
  or both baseline and candidate hit ceiling without measurable divergence.

Recommendations advise human maintainers; they never automatically delete rules, mutate code,
or modify Ponytail intensity settings.
