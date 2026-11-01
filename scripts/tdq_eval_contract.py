"""Pure Eval contracts. No filesystem/process access; only log() writes stderr.

Validators return dictionaries with valid/errors (paired: accepted/mismatched_fields).
Creators raise ValueError on invalid inputs. Gate consumes individual A/B trial records,
not report verdicts. Callers resolve symlinks and supply project-relative paths; a git
symlink mode in diff is review-required. Runtime scripts require explicit target context.
"""
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import itertools
import json
import math
import os
import re
import sys

CELL_FIELDS = ("host", "model", "permission_profile", "tool_aliases", "cache_profile")
IDENTITY_FIELDS = CELL_FIELDS + ("scorer_version", "corpus_version", "check_set")
PLAN_FIELDS = (
    "plan_version", "experiment_id", "targets", "base_identity", "candidate_identity",
    "change_kind", "hypothesis", "evaluation_kind", "corpus_id", "dev_cases_sha256",
    "holdout_cases_sha256", "rubric_version", "scorer_version", "expected_triggers",
    "negative_cases", "required_metrics", "cells", "repetitions", "order_policy", "thresholds",
)
BINDING_FIELDS = ("base_identity", "candidate_identity", "targets", "dev_cases_sha256",
                  "holdout_cases_sha256", "scorer_version", "rubric_version", "evaluation_kind")
TOKEN_FIELDS = ("input_tokens", "output_tokens", "cache_read_tokens", "cache_write_tokens")
COUNT_FIELDS = ("tool_calls_count", "model_calls_count", "retries_count", "user_interventions_count")
KINDS = ("mechanism", "agent-effectiveness")
SENSITIVE = re.compile(r"secret|token|prompt|payload|bearer|password|api.?key|sk-", re.I)


def _log_enabled():
    return all(os.environ.get(key, "1").strip().lower() not in {"0", "false", "off"}
               for key in ("TDQ_EVAL_LOG", "TDQ_LOG"))


def _safe_log(value):
    text = str(value)
    if SENSITIVE.search(text):
        return "[redacted]"
    return text.replace("\n", "\\n").replace("\r", "\\r")


def log(thong_diep, muc="thong-tin", **fields):
    """Write sanitized ISO UTC log; metadata restricted to documented debug fields."""
    if muc not in {"thong-tin", "canh-bao", "loi"}:
        raise ValueError("invalid log level")
    if not _log_enabled():
        return
    metadata = " ".join(f"{key}={_safe_log(fields[key])}" for key in
                        ("experiment", "cell", "trial", "reason", "cleanup") if key in fields)
    print(f"[{datetime.now(timezone.utc).isoformat()}] {muc}: {_safe_log(thong_diep)} {metadata}",
          file=sys.stderr)


def _canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"), allow_nan=False)


def _digest(value):
    return hashlib.sha256(_canonical(value).encode("utf-8")).hexdigest()


def _text(value):
    return isinstance(value, str) and bool(value.strip())


def _hash(value, commit=False):
    pattern = r"(?:[0-9a-f]{40}|[0-9a-f]{64})" if commit else r"[0-9a-f]{64}"
    return isinstance(value, str) and re.fullmatch(pattern, value) is not None


def _model(value):
    return _text(value) and not re.search(r"(^|[-/:])(latest|default|auto)($|[-/:])", value, re.I)


def _safe_path(path):
    if not isinstance(path, str) or not path or path != path.strip():
        return False
    if re.search(r"[:\x00-\x1f%]", path) or path.startswith(("/", "\\")):
        return False
    return all(part not in {"", ".", ".."} and not part.endswith((" ", "."))
               for part in path.replace("\\", "/").split("/"))


def _bookkeeping_line(line):
    line = line.strip()
    if re.fullmatch(r"Ngày:\s*\d{4}-\d{2}-\d{2}", line):
        return "Ngày: <date>"
    if re.fullmatch(r"Bản:\s*\d+(?:\.\d+)*", line):
        return "Bản: <version>"
    if re.fullmatch(r"Trạng thái:\s*(CHỜ DUYỆT|ĐÃ DUYỆT|ĐANG LÀM|HOÀN THÀNH)", line):
        return "Trạng thái: <status>"
    return re.sub(r"^(\s*-\s*)\[[ ~x>]\]", r"\1[ ]", line)


def _bookkeeping_diff(diff):
    if not isinstance(diff, str):
        return False
    removed, added = [], []
    for line in diff.splitlines():
        if line.startswith(("---", "+++")):
            continue
        if line.startswith("-"):
            removed.append(_bookkeeping_line(line[1:]))
        if line.startswith("+"):
            added.append(_bookkeeping_line(line[1:]))
    return bool(removed) and removed == added


def _path_kind(path, runtime_targets):
    if path in runtime_targets:
        return "behavioral"
    if path.startswith(("hooks/", ".claude-plugin/", ".agents/plugins/", ".opencode/plugins/")):
        return "behavioral"
    if re.fullmatch(r"skills/.+/(?:SKILL\.md|references/.+)|agents/[^/]+\.md|manifest\.json", path):
        return "behavioral"
    if path.startswith(("docs/tdq/", "docs/workinglog/", "graphify-out/")):
        return "bookkeeping"
    if re.fullmatch(r"README\.md|CHANGELOG[^/]*\.md|docs/.*\.md", path):
        return "docs_only"
    if path.startswith(("src/", "app/", "scripts/", "tests/")):
        return "app_code"
    return "review-required"


def classify_target(path, diff_text=None, runtime_plugin_targets=None):
    """Classify project-relative target; unknown/unsafe paths never receive exemption."""
    kind = "review-required"
    if _safe_path(path) and not re.search(r"\b120000\b", diff_text or ""):
        kind = _path_kind(path.replace("\\", "/"), runtime_plugin_targets or ())
        if kind == "behavioral" and _bookkeeping_diff(diff_text):
            kind = "bookkeeping"
    return {"requires_eval": kind in {"behavioral", "review-required"}, "change_kind": kind}


def _select_targets(results, kind):
    return [path for path, result in results if result["change_kind"] == kind]


def classify_targets(paths, diff_by_path=None, runtime_plugin_targets=None):
    """Partition targets; explicit runtime_plugin_targets binds plugin scripts in projects."""
    paths = [paths] if isinstance(paths, str) else list(paths or [])
    diffs = diff_by_path or {}
    results = [(p, classify_target(p, diffs.get(p), runtime_plugin_targets)) for p in paths]
    kinds = {r["change_kind"] for _, r in results}
    order = ("review-required", "behavioral", "bookkeeping", "docs_only", "app_code")
    kind = next(filter(kinds.__contains__, order), "review-required")
    return {"requires_eval": kind in {"behavioral", "review-required"}, "change_kind": kind,
            "behavioral_targets": _select_targets(results, "behavioral"),
            "exempt_targets": [p for p, r in results if not r["requires_eval"]],
            "review_required_targets": _select_targets(results, "review-required")}


phan_loai_target = classify_target


def _require(condition, reason):
    if not condition:
        raise ValueError(reason)


def _string_list(value, nonempty=False):
    return isinstance(value, list) and (bool(value) or not nonempty) and all(_text(v) for v in value)


def _validate_cell(cell):
    _require(isinstance(cell, dict), "invalid cell")
    _require(all(k in cell for k in CELL_FIELDS), "missing cell identity")
    _require(_text(cell["host"]) and _model(cell["model"]), "unresolved host/model")
    _require(_text(cell["permission_profile"]) and _text(cell["cache_profile"]), "invalid cell profile")
    aliases = cell["tool_aliases"]
    _require(isinstance(aliases, dict), "invalid tool_aliases")
    _require(all(_text(k) and _string_list(v) for k, v in aliases.items()), "invalid tool aliases")


def _validate_targets(targets):
    _require(isinstance(targets, (list, dict)) and bool(targets), "invalid targets")
    _require(all(_safe_path(p) for p in targets), "unsafe target")
    _require(len(set(targets)) == len(targets), "duplicate targets")
    if isinstance(targets, dict):
        _require(all(_hash(h) for h in targets.values()), "invalid target hash")


def _validate_plan_values(plan):
    _require(plan["plan_version"] == "v1", "unsupported plan version")
    _require(plan["evaluation_kind"] in KINDS, "invalid evaluation kind")
    _require(plan["order_policy"] == "AB_BA", "invalid order policy")
    _require(type(plan["repetitions"]) is int and plan["repetitions"] >= 1, "invalid repetitions")
    _require(_hash(plan["base_identity"], commit=True), "unresolved base identity")
    _require(plan["candidate_identity"] == "planned" or _hash(plan["candidate_identity"]), "unresolved candidate")
    _require(all(_hash(plan[k]) for k in ("dev_cases_sha256", "holdout_cases_sha256")), "invalid corpus hash")
    _require(plan["change_kind"] in {"behavioral", "review-required", "bookkeeping", "docs_only", "app_code"},
             "invalid change kind")
    _validate_targets(plan["targets"])


def _validate_plan_collections(plan):
    for key in ("experiment_id", "hypothesis", "corpus_id", "rubric_version", "scorer_version"):
        _require(_text(plan[key]), f"invalid {key}")
    for key in ("expected_triggers", "negative_cases", "required_metrics"):
        _require(_string_list(plan[key]), f"invalid {key}")
    cases = plan["expected_triggers"] + plan["negative_cases"]
    _require(bool(cases) and len(cases) == len(set(cases)), "empty/duplicate cases")
    _require(bool(plan["required_metrics"]), "missing required metrics")
    _require(set(plan["required_metrics"]) <= {"trigger_accuracy", "outcome_quality", "efficiency_metrics"},
             "unknown required metric")
    _require(isinstance(plan["thresholds"], dict), "invalid thresholds")
    _require(isinstance(plan["cells"], list) and bool(plan["cells"]), "empty cells")
    for cell in plan["cells"]:
        _validate_cell(cell)
    _require(len({_canonical(c) for c in plan["cells"]}) == len(plan["cells"]), "duplicate cells")


def validate_eval_plan(plan):
    """Validate v1 plan; reject aliases, nonfinite JSON, missing or malformed fields."""
    try:
        _require(isinstance(plan, dict), "plan must be object")
        _require(all(k in plan for k in PLAN_FIELDS), "missing required plan field")
        _canonical(plan)
        _validate_plan_values(plan)
        _validate_plan_collections(plan)
    except (ValueError, TypeError) as exc:
        return {"valid": False, "errors": [str(exc)]}
    return {"valid": True, "errors": []}


def create_eval_plan(**fields):
    """Create independent validated plan; only plan_version defaults to v1."""
    plan = deepcopy({"plan_version": "v1", **fields})
    result = validate_eval_plan(plan)
    _require(result["valid"], "; ".join(result["errors"]))
    return plan


def compute_experiment_hash(plan):
    """Hash all locked v1 fields; display metadata and stored hash excluded."""
    result = validate_eval_plan(plan)
    _require(result["valid"], "; ".join(result["errors"]))
    return _digest({k: plan[k] for k in PLAN_FIELDS})


def _gate(verdict, reason, **fields):
    return dict(verdict=verdict, reason=reason, passed=verdict == "PASS", live_run_authorized=False, **fields)


def _valid_waiver(waiver):
    if not isinstance(waiver, dict):
        return False
    return (all(_text(waiver.get(k)) for k in ("reason", "by", "scope"))
            and waiver["by"].startswith("user:"))


def _metric_coverage(record, required):
    metrics = normalize_trial_metrics(record)
    available = {"trigger_accuracy": metrics["trigger_accuracy"]["availability"] == "available",
                 "outcome_quality": metrics["outcome_quality"]["availability"] == "available",
                 "efficiency_metrics": metrics["efficiency_metrics"]["tokens"]["availability"] == "available"}
    return all(available.get(key, False) for key in required)


def _evidence_binding(row, trial, plan):
    _require(isinstance(row, dict), "invalid evidence")
    _require(all(row.get(k) == v for k, v in trial.items()), "stale_trial_identity")
    _require(all(row.get(k) == plan[k] for k in BINDING_FIELDS), "stale_evidence_binding")
    _require(_hash(row.get("raw_trace_sha256")) and _hash(row.get("outcome_sha256")), "missing_artifact_hash")
    expected_provenance = "synthetic/offline" if plan["evaluation_kind"] == "mechanism" else "live"
    _require(row.get("provenance") == expected_provenance, "wrong_claim_provenance")
    expected_trigger = row["case_id"] in plan["expected_triggers"]
    _require(row.get("expected_trigger") is expected_trigger, "stale_trigger_oracle")
    _require(_metric_coverage(row, plan["required_metrics"]), "unavailable_metrics")
    expected = dict({k: trial[k] for k in CELL_FIELDS}, base_commit=plan["base_identity"],
                    candidate_commit=plan["candidate_identity"], corpus_version=plan["corpus_id"],
                    scorer_version=plan["scorer_version"], rubric_version=plan["rubric_version"],
                    evaluation_kind=plan["evaluation_kind"], check_set=list(row.get("checks", {})))
    _require(validate_paired_identity(expected, row.get("manifest"))["valid"], "invalid_evidence_manifest")


def _report_gate(plan, actual, records):
    _require(_hash(plan["candidate_identity"]), "planned_candidate")
    _require(isinstance(plan["targets"], dict) and actual == plan["targets"], "stale_target_hash")
    experiment_hash = compute_experiment_hash(plan)
    _require(plan.get("experiment_hash", experiment_hash) == experiment_hash, "stale_experiment_hash")
    schedule = build_ab_ba_schedule(plan["expected_triggers"] + plan["negative_cases"],
                                    plan["cells"], plan["repetitions"], experiment_hash)
    _require(isinstance(records, list) and len(records) == len(schedule), "incomplete_trial_coverage")
    indexed = {r.get("trial_id"): r for r in records if isinstance(r, dict)}
    _require(len(indexed) == len(schedule), "duplicate_trial")
    for trial in schedule:
        _evidence_binding(indexed.get(trial["trial_id"]), trial, plan)
    return _gate("PASS", "complete_evidence", experiment_hash=experiment_hash)


def check_eval_gate(plan, stage="pre_implement", actual_target_hashes=None,
                    evidence_records=None, waiver=None):
    """Check offline evidence, never authorize live execution or treat waiver as PASS."""
    if stage not in {"pre_implement", "pre_report"}:
        return _gate("FAIL", "invalid_stage")
    if _valid_waiver(waiver):
        return _gate("WAIVED_USER", waiver["reason"], waiver=deepcopy(waiver))
    result = validate_eval_plan(plan)
    if not result["valid"]:
        return _gate("INCOMPLETE", "invalid_plan", errors=result["errors"])
    if stage == "pre_implement":
        return _gate("PASS", "valid_plan", experiment_hash=compute_experiment_hash(plan))
    try:
        return _report_gate(plan, actual_target_hashes, evidence_records)
    except (ValueError, TypeError, KeyError) as exc:
        return _gate("INCOMPLETE", str(exc))


def _validate_manifest(manifest):
    _require(isinstance(manifest, dict), "manifest must be object")
    _canonical(manifest)
    _validate_cell(manifest)
    _require(all(_text(manifest.get(k)) for k in ("scorer_version", "corpus_version")), "missing scorer/corpus")
    _require(_string_list(manifest.get("check_set"), nonempty=True), "invalid check_set")
    _require(len(set(manifest["check_set"])) == len(manifest["check_set"]), "duplicate checks")
    _require(all(_hash(manifest.get(k), commit=True) for k in ("base_commit", "candidate_commit")),
             "invalid commit identity")


def validate_paired_identity(base_manifest, candidate_manifest):
    """Reject mismatched control variables and source identities, including absent fields."""
    errors = []
    for manifest in (base_manifest, candidate_manifest):
        try:
            _validate_manifest(manifest)
        except (ValueError, TypeError) as exc:
            errors.append(str(exc))
    base = base_manifest if isinstance(base_manifest, dict) else {}
    candidate = candidate_manifest if isinstance(candidate_manifest, dict) else {}
    keys = IDENTITY_FIELDS + ("base_commit", "candidate_commit", "evaluation_kind", "rubric_version")
    mismatched = [k for k in keys if base.get(k) != candidate.get(k)]
    valid = not errors and not mismatched
    return {"valid": valid, "accepted": valid, "errors": errors, "mismatched_fields": mismatched}


def classify_record_provenance(record):
    """Preserve legacy/fixture labels; a single trace cannot certify a paired experiment."""
    if not isinstance(record, dict):
        return "historical_unverified"
    if not (_text(record.get("host")) and _model(record.get("model"))):
        return "historical_unverified"
    if not all(_hash(record.get(k)) for k in ("raw_trace_sha256", "experiment_hash")):
        return "historical_unverified"
    if record.get("provenance") == "synthetic/offline":
        return "synthetic/offline"
    return "live_unverified" if record.get("provenance") == "live" else "historical_unverified"


def _number(value, integer=False):
    if value is None:
        return None
    _require(type(value) in (int, float), "metric must be numeric")
    _require(math.isfinite(value) and value >= 0, "metric must be finite/nonnegative")
    _require(not integer or type(value) is int, "metric must be integer")
    return value


def _tokens(raw):
    usage = raw.get("tokens", raw.get("usage", {}))
    _require(isinstance(usage, dict), "invalid token usage")
    result = {k: _number(usage.get(k), integer=True) for k in TOKEN_FIELDS}
    present = sum(v is not None for v in result.values())
    result["availability"] = {0: "unavailable", 4: "available"}.get(present, "partial")
    return result


def _trigger(raw):
    expected, observed = raw.get("expected_trigger"), raw.get("observed_trigger")
    provenance = raw.get("trigger_provenance")
    available = type(expected) is bool and type(observed) is bool and _text(provenance)
    return {"expected_trigger": expected if type(expected) is bool else None,
            "observed_trigger": observed if type(observed) is bool else None,
            "matched": expected == observed if available else None,
            "availability": "available" if available else "unavailable",
            "provenance": provenance if _text(provenance) else "unavailable"}


def _outcome(raw):
    status = raw.get("execution_status", "missing")
    passed = raw.get("passed") if type(raw.get("passed")) is bool else None
    score = _number(raw.get("score"))
    _require(score is None or score <= 1, "score outside [0,1]")
    checks = raw.get("checks", {})
    _require(isinstance(checks, dict), "invalid checks")
    if status in {"failed", "timeout"}:
        passed, score = False, 0.0
    elif status != "completed":
        passed, score = None, None
    available = passed is not None and score is not None
    return {"passed": passed, "score": score, "checks": deepcopy(checks),
            "availability": "available" if available else "unavailable", "execution_status": status}


def _estimate(tokens, card):
    if card is None:
        return None
    _require(isinstance(card, dict), "invalid rate card")
    _require(_text(card.get("source")) and _text(card.get("snapshot_at")), "missing rate provenance")
    rates = card.get("rates")
    _require(isinstance(rates, dict) and bool(rates), "missing rates")
    for value in rates.values():
        _number(value)
    names = ("input_per_mtok", "output_per_mtok", "cache_read_per_mtok", "cache_write_per_mtok")
    if tokens["availability"] != "available" or not all(k in rates for k in names):
        return None
    _require(all(rates[k] is not None for k in names), "missing rate")
    return sum(tokens[t] * rates[r] / 1_000_000 for t, r in zip(TOKEN_FIELDS, names))


def _cost(raw, tokens, card):
    observed = _number(raw.get("total_cost_usd"))
    billed = _number(raw.get("billed_cost_usd"))
    estimate = _estimate(tokens, card)
    sources = {"observed_usage": observed, "rate_estimate": estimate, "provider_billed": billed}
    source = next((k for k in ("provider_billed", "observed_usage", "rate_estimate")
                   if sources[k] is not None), None)
    return dict(sources, total_cost_usd=observed, source=source,
                availability="available" if observed is not None else "unavailable",
                rate_card=deepcopy(card))


def normalize_trial_metrics(raw_record, rate_card=None):
    """Normalize flat adapter record, preserving missing values and distinct cost sources.

    Token counts are disjoint input/output/cache buckets, not inclusive provider totals.
    total_cost_usd always means observed usage cost; estimates/billing never overwrite it.
    """
    _require(isinstance(raw_record, dict), "record must be object")
    tokens = _tokens(raw_record)
    efficiency = {k: _number(raw_record.get(k), integer=True) for k in COUNT_FIELDS}
    efficiency.update(tokens=tokens, cost=_cost(raw_record, tokens, rate_card),
                      complexity_count=_number(raw_record.get("complexity_count"), integer=True),
                      wall_latency_seconds=_number(raw_record.get("wall_latency_seconds")))
    return {"trigger_accuracy": _trigger(raw_record), "outcome_quality": _outcome(raw_record),
            "efficiency_metrics": efficiency}


def build_ab_ba_schedule(cases, cells, repetitions, experiment_hash):
    """Produce deterministic A/B trials; each repetition is one pair, odd AB/even BA."""
    case_ids = [c.get("case_id") if isinstance(c, dict) else c for c in cases]
    _require(_string_list(case_ids, nonempty=True), "invalid cases")
    _require(len(set(case_ids)) == len(case_ids), "duplicate cases")
    _require(type(repetitions) is int and repetitions >= 1, "invalid repetitions")
    _require(_hash(experiment_hash), "invalid experiment hash")
    _require(isinstance(cells, list) and bool(cells), "missing cells")
    for cell in cells:
        _validate_cell(cell)
    _require(len({_canonical(c) for c in cells}) == len(cells), "duplicate cells")
    schedule = []
    for cell, case_id, repeat in itertools.product(cells, case_ids, range(1, repetitions + 1)):
        for variant in ("AB" if repeat % 2 else "BA"):
            trial = dict(deepcopy(cell), case_id=case_id, repetition=repeat, variant=variant,
                         experiment_hash=experiment_hash)
            schedule.append(dict(trial, trial_id=_digest(trial)))
    return schedule


def _validate_pair(pair):
    _require(isinstance(pair, dict) and _text(pair.get("pair_id")), "invalid pair")
    base, candidate = pair.get("baseline"), pair.get("candidate")
    _require(isinstance(base, dict) and isinstance(candidate, dict), "missing pair member")
    provenance = classify_record_provenance(base)
    _require(provenance != "historical_unverified", "unverified_pair")
    _require(provenance == classify_record_provenance(candidate), "mixed_provenance")
    _require(base["experiment_hash"] == candidate["experiment_hash"], "mixed_experiment")
    _require(all(base.get(k) == candidate.get(k) for k in CELL_FIELDS), "mixed_cell")
    _require(validate_paired_identity(base.get("manifest"), candidate.get("manifest"))["valid"], "invalid_pair_identity")
    for record in (base, candidate):
        _require(all(record.get(k) == record["manifest"].get(k) for k in CELL_FIELDS), "stale_manifest_cell")
    return base, candidate, provenance


def _recommendation_inputs(records):
    _require(isinstance(records, list) and bool(records), "missing_pairs")
    ids, cells, experiments, provenances, normalized = set(), set(), set(), set(), []
    for pair in records:
        base, candidate, provenance = _validate_pair(pair)
        _require(pair["pair_id"] not in ids, "duplicate_pair")
        ids.add(pair["pair_id"])
        cells.add(_canonical({k: base[k] for k in CELL_FIELDS}))
        experiments.add(base["experiment_hash"])
        provenances.add(provenance)
        normalized.append((normalize_trial_metrics(base), normalize_trial_metrics(candidate)))
    _require(len(cells) == len(experiments) == len(provenances) == 1, "mixed_cell_or_experiment")
    return normalized, next(iter(provenances))


def _policy(policy):
    _require(isinstance(policy, dict), "missing_policy")
    _require(type(policy.get("min_pairs")) is int and policy["min_pairs"] >= 1, "invalid_min_pairs")
    for key in ("quality_margin", "efficiency_margin"):
        value = _number(policy.get(key))
        _require(value is not None and value <= 1, f"invalid_{key}")
    return policy


def _quality_summary(pairs):
    scores, triggers = [[], []], [[], []]
    for pair in pairs:
        for index, metrics in enumerate(pair):
            outcome, trigger = metrics["outcome_quality"], metrics["trigger_accuracy"]
            _require(outcome["availability"] == trigger["availability"] == "available", "unavailable_metrics")
            scores[index].append(outcome["score"])
            triggers[index].append(float(trigger["matched"]))
    return ([sum(v) / len(v) for v in scores], [sum(v) / len(v) for v in triggers])


def _efficiency_value(metrics, key):
    efficiency = metrics["efficiency_metrics"]
    if key == "tokens":
        tokens = efficiency["tokens"]
        return sum(tokens[k] for k in TOKEN_FIELDS) if tokens["availability"] == "available" else None
    if key == "cost":
        return efficiency["cost"]["observed_usage"]
    return efficiency[key]


def _efficiency_gain(pairs, margin):
    observed = False
    for key in ("tokens", "cost", "wall_latency_seconds", "complexity_count"):
        values = [[_efficiency_value(pair[i], key) for pair in pairs] for i in (0, 1)]
        if any(v is None for group in values for v in group):
            continue
        observed = True
        base, candidate = map(sum, values)
        if base > 0 and (base - candidate) / base > margin:
            return True, observed
    return False, observed


def _recommend(pairs, policy):
    scores, triggers = _quality_summary(pairs)
    margin = policy["quality_margin"]
    if scores[1] < scores[0] - margin or triggers[1] < triggers[0] - margin:
        return "DROP", "guardrail_regression", False
    if scores[1] > scores[0] + margin:
        return "KEEP", "quality_improved", True
    gain, observed = _efficiency_gain(pairs, policy["efficiency_margin"])
    if gain:
        return "TRIM", "efficiency_improved", True
    if not observed:
        return "INCONCLUSIVE", "unavailable_metrics", True
    reason = "baseline_ceiling" if scores == [1, 1] else "no_meaningful_delta"
    return "INCONCLUSIVE", reason, True


def evaluate_cell_recommendation(cell_records, policy=None):
    """Decide one cell from explicit paired records; policy margins are locked by caller.

    No default policy, no pooled host/model score, no automatic mutation. This is a
    deterministic margin rule, not a significance test or certification of live benefit.
    """
    result = {"verdict": "INCONCLUSIVE", "reason": "missing_evidence", "guardrail_ok": None,
              "sample_count": 0, "provenance": "unverified", "auto_mutate_allowed": False}
    try:
        policy = _policy(policy)
        pairs, provenance = _recommendation_inputs(cell_records)
        result.update(sample_count=len(pairs), provenance=provenance)
        _require(len(pairs) >= policy["min_pairs"], "insufficient_pairs")
        verdict, reason, guardrail = _recommend(pairs, policy)
        result.update(verdict=verdict, reason=reason, guardrail_ok=guardrail)
    except (ValueError, TypeError, KeyError) as exc:
        result["reason"] = str(exc)
    return result
