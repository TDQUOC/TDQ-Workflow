#!/usr/bin/env python3
"""Entry point for TDQ skill and plugin evaluation (O2).

Sub-commands:
  plan   — validate or inspect an eval-plan JSON and compute experiment hash.
  check  — native preflight of host cells and evaluation gate without calling models.
  run    — execute balanced AB/BA trials via host adapters with quota and retry controls.
  report — offline aggregation per (host, model) cell with deterministic recommendations.

Zero model calls in plan, check, and report commands.
"""

import argparse
import glob
import json
import math
import os
from pathlib import Path
import sys
from typing import Any, Dict, List, Optional, Tuple, Union

SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import tdq_eval_contract
import tdq_eval_hosts

SOUL_LINE = "Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md"


def _log(thong_diep: str, muc: str = "thong-tin", **fields: Any) -> None:
    tdq_eval_contract.log(thong_diep, muc=muc, **fields)


def _load_json(source: Union[str, Path, Dict[str, Any]]) -> Dict[str, Any]:
    if isinstance(source, dict):
        return source
    path = Path(source).resolve(strict=True)
    with path.open("r", encoding="utf-8") as stream:
        return json.load(stream)


def _write_json(data: Any, path: Union[str, Path]) -> None:
    target = Path(path).resolve()
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", encoding="utf-8") as stream:
        json.dump(data, stream, indent=2, ensure_ascii=False)


def _mean(numbers: List[Optional[float]]) -> Optional[float]:
    valid = [n for n in numbers if n is not None]
    return (sum(valid) / len(valid)) if valid else None


def _variance(numbers: List[Optional[float]]) -> Optional[float]:
    valid = [n for n in numbers if n is not None]
    if len(valid) < 2:
        return 0.0 if valid else None
    avg = sum(valid) / len(valid)
    return sum((x - avg) ** 2 for x in valid) / len(valid)


# ------------------------------------------------------------------- plan
def plan_eval(
    plan_source: Union[str, Path, Dict[str, Any]],
    out_path: Optional[Union[str, Path]] = None,
) -> Dict[str, Any]:
    """Validate eval-plan and compute deterministic experiment hash without model calls."""
    try:
        plan = _load_json(plan_source)
    except Exception as exc:
        return {"valid": False, "errors": [f"failed_to_load_plan: {exc}"], "experiment_hash": None}

    validation = tdq_eval_contract.validate_eval_plan(plan)
    if not validation["valid"]:
        return {"valid": False, "errors": validation["errors"], "experiment_hash": None}

    exp_hash = tdq_eval_contract.compute_experiment_hash(plan)
    plan_with_hash = dict(plan, experiment_hash=exp_hash)

    if out_path:
        _write_json(plan_with_hash, out_path)

    _log("plan validated", muc="thong-tin", experiment=exp_hash)
    return {
        "valid": True,
        "errors": [],
        "experiment_hash": exp_hash,
        "plan": plan_with_hash,
    }


def cmd_plan(args: argparse.Namespace) -> int:
    res = plan_eval(args.plan, out_path=args.out)
    output = {
        "valid": res["valid"],
        "experiment_hash": res.get("experiment_hash"),
        "errors": res.get("errors", []),
    }
    print(json.dumps(output, indent=2))
    return 0 if res["valid"] else 1


# ------------------------------------------------------------------- check
def check_eval(
    plan_source: Union[str, Path, Dict[str, Any]],
    stage: str = "pre_implement",
    profile: Optional[Dict[str, Any]] = None,
    actual_target_hashes: Optional[Dict[str, str]] = None,
    evidence_records: Optional[List[Dict[str, Any]]] = None,
    waiver: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Perform preflight checks on cells and verify eval gate without calling models."""
    try:
        plan = _load_json(plan_source)
    except Exception as exc:
        return {
            "ready": False,
            "gate": {"verdict": "FAIL", "reason": f"load_plan_failed: {exc}", "passed": False},
            "cells_preflight": {},
        }

    # 1. Gate check
    gate_res = tdq_eval_contract.check_eval_gate(
        plan,
        stage=stage,
        actual_target_hashes=actual_target_hashes,
        evidence_records=evidence_records,
        waiver=waiver,
    )

    # 2. Host cell preflights (offline native check)
    cells_preflight: Dict[str, Any] = {}
    all_cells_ready = True
    cells = plan.get("cells", []) if isinstance(plan, dict) else []

    for cell in cells:
        host = cell.get("host")
        model = cell.get("model")
        cell_key = f"{host}:{model}"
        if host:
            # Setup isolated trial environment mock for preflight if profile is provided
            pf_res = tdq_eval_hosts.preflight_host(host, profile=profile)
            cells_preflight[cell_key] = pf_res
            if not pf_res.get("ready"):
                all_cells_ready = False
        else:
            cells_preflight[cell_key] = {"ready": False, "reason": "missing_host"}
            all_cells_ready = False

    ready = bool(gate_res.get("passed") or gate_res.get("verdict") == "WAIVED_USER") and all_cells_ready

    _log("check completed", muc="thong-tin", reason=gate_res.get("reason"))
    return {
        "ready": ready,
        "gate": gate_res,
        "cells_preflight": cells_preflight,
    }


def cmd_check(args: argparse.Namespace) -> int:
    profile = _load_json(args.profile) if args.profile else None
    actual_targets = _load_json(args.actual_targets) if getattr(args, "actual_targets", None) else None
    waiver = _load_json(args.waiver) if getattr(args, "waiver", None) else None

    evidence = None
    if getattr(args, "evidence_dir", None):
        e_dir = Path(args.evidence_dir)
        evidence = [_load_json(f) for f in sorted(e_dir.glob("trial_*.json"))]

    res = check_eval(
        args.plan,
        stage=args.stage,
        profile=profile,
        actual_target_hashes=actual_targets,
        evidence_records=evidence,
        waiver=waiver,
    )
    print(json.dumps(res, indent=2))
    return 0 if res["ready"] else 1


# ------------------------------------------------------------------- run
def _build_trial_record(
    plan: Dict[str, Any],
    trial: Dict[str, Any],
    trial_res: Dict[str, Any],
    raw_trace_sha: str,
) -> Dict[str, Any]:
    expected_trig = trial["case_id"] in plan["expected_triggers"]
    exec_status = trial_res.get("execution_status", "completed")
    score = 1.0 if exec_status == "completed" else 0.0
    passed = exec_status == "completed"
    outcome_sha = tdq_eval_contract._digest({"execution_status": exec_status, "score": score})

    checks = {"rule_compliance": "pass"} if passed else {"rule_compliance": "fail"}
    manifest = dict(
        {k: trial[k] for k in tdq_eval_contract.CELL_FIELDS},
        base_commit=plan["base_identity"],
        candidate_commit=plan["candidate_identity"],
        corpus_version=plan["corpus_id"],
        scorer_version=plan["scorer_version"],
        rubric_version=plan["rubric_version"],
        evaluation_kind=plan["evaluation_kind"],
        check_set=list(checks.keys()),
    )

    expected_prov = "synthetic/offline" if plan["evaluation_kind"] == "mechanism" else "live"

    rec: Dict[str, Any] = dict(
        trial,
        base_identity=plan["base_identity"],
        candidate_identity=plan["candidate_identity"],
        targets=plan["targets"],
        dev_cases_sha256=plan["dev_cases_sha256"],
        holdout_cases_sha256=plan["holdout_cases_sha256"],
        scorer_version=plan["scorer_version"],
        rubric_version=plan["rubric_version"],
        evaluation_kind=plan["evaluation_kind"],
        raw_trace_sha256=raw_trace_sha,
        outcome_sha256=outcome_sha,
        provenance=expected_prov,
        expected_trigger=expected_trig,
        observed_trigger=trial_res.get("observed_trigger", False),
        trigger_provenance=trial_res.get("trigger_provenance", "event:trial_run"),
        execution_status=exec_status,
        passed=passed,
        score=score,
        checks=checks,
        manifest=manifest,
        tool_calls_count=trial_res.get("tool_calls_count", 0),
        model_calls_count=trial_res.get("model_calls_count", 0),
        retries_count=trial_res.get("retries_count", 0),
        user_interventions_count=trial_res.get("user_interventions_count", 0),
        tokens=trial_res.get("tokens", {
            "input_tokens": None,
            "output_tokens": None,
            "cache_read_tokens": None,
            "cache_write_tokens": None,
        }),
        total_cost_usd=trial_res.get("total_cost_usd"),
        billed_cost_usd=trial_res.get("billed_cost_usd"),
        wall_latency_seconds=trial_res.get("wall_latency_seconds", 0.0),
    )
    return rec


def run_eval(
    plan_path: Union[str, Path],
    cases_path: Union[str, Path],
    profile_path: Union[str, Path],
    out_dir: Union[str, Path],
    command_builder: Optional[Any] = None,
) -> Dict[str, Any]:
    """Execute balanced AB/BA schedule trials with bounded quota and deadline."""
    plan = _load_json(plan_path)
    val = tdq_eval_contract.validate_eval_plan(plan)
    if not val["valid"]:
        raise ValueError(f"invalid plan: {'; '.join(val['errors'])}")

    cases = _load_json(cases_path)
    profile = _load_json(profile_path)
    exp_hash = tdq_eval_contract.compute_experiment_hash(plan)

    schedule = tdq_eval_contract.build_ab_ba_schedule(
        cases, plan["cells"], plan["repetitions"], exp_hash
    )

    out_path = Path(out_dir).resolve()
    out_path.mkdir(parents=True, exist_ok=True)

    completed = 0
    quota_usd = float(profile.get("quota_usd", float("inf")))
    spent_usd = 0.0

    for trial in schedule:
        trial_id = trial["trial_id"]
        if spent_usd > quota_usd:
            _log("quota exceeded, stopping run", muc="canh-bao", trial=trial_id)
            break

        host = trial["host"]
        trial_env = tdq_eval_hosts.prepare_trial_environment(
            base_dir=out_path / "env",
            host=host,
            trial_id=trial_id,
            plugin_dir=profile.get("plugin_dir"),
        )
        trial_profile = dict(profile, **trial_env)

        trial_res = tdq_eval_hosts.run_host_trial(
            host=host,
            trial_spec=trial,
            profile=trial_profile,
            command_builder=command_builder,
        )

        attempts = trial_res.get("attempts", [])
        raw_trace_sha = attempts[-1].get("raw_trace_sha256") if attempts else "0" * 64

        rec = _build_trial_record(plan, trial, trial_res, raw_trace_sha)
        record_file = out_path / f"trial_{trial_id}.json"
        _write_json(rec, record_file)
        completed += 1

    summary = {
        "experiment_hash": exp_hash,
        "total_trials": len(schedule),
        "completed_trials": completed,
        "out_dir": str(out_path),
    }
    _write_json(summary, out_path / "run_summary.json")
    return summary


def cmd_run(args: argparse.Namespace) -> int:
    res = run_eval(
        plan_path=args.plan,
        cases_path=args.cases,
        profile_path=args.profile,
        out_dir=args.out_dir,
    )
    print(json.dumps(res, indent=2))
    return 0 if res["completed_trials"] == res["total_trials"] else 1


# ------------------------------------------------------------------- report
def _pair_trials(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Group trial records into (baseline, candidate) pairs by (case_id, repetition)."""
    indexed: Dict[Tuple[str, int], Dict[str, Dict[str, Any]]] = {}
    for r in records:
        case_id = r.get("case_id")
        rep = r.get("repetition")
        variant = r.get("variant")
        if case_id is None or rep is None or variant not in ("A", "B"):
            continue
        key = (case_id, rep)
        indexed.setdefault(key, {})[variant] = r

    pairs: List[Dict[str, Any]] = []
    for (case_id, rep), group in sorted(indexed.items()):
        if "A" in group and "B" in group:
            base, cand = group["A"], group["B"]
            pair_id = f"{base['host']}_{base['model']}_{case_id}_{rep}"
            pairs.append({"pair_id": pair_id, "baseline": base, "candidate": cand})
    return pairs


def _summarize_cell_metrics(pairs: List[Dict[str, Any]]) -> Dict[str, Any]:
    base_scores = [p["baseline"].get("score") for p in pairs]
    cand_scores = [p["candidate"].get("score") for p in pairs]

    base_triggers = [p["baseline"].get("observed_trigger") == p["baseline"].get("expected_trigger") for p in pairs]
    cand_triggers = [p["candidate"].get("observed_trigger") == p["candidate"].get("expected_trigger") for p in pairs]

    # Token availability check
    token_availabilities = set()
    costs = []
    latencies = []
    for p in pairs:
        for m in (p["baseline"], p["candidate"]):
            toks = m.get("tokens", {})
            present = sum(toks.get(k) is not None for k in tdq_eval_contract.TOKEN_FIELDS)
            token_availabilities.add({0: "unavailable", 4: "available"}.get(present, "partial"))
            if m.get("total_cost_usd") is not None:
                costs.append(m["total_cost_usd"])
            if m.get("wall_latency_seconds") is not None:
                latencies.append(m["wall_latency_seconds"])

    tok_avail = "available" if token_availabilities == {"available"} else ("partial" if "available" in token_availabilities or "partial" in token_availabilities else "unavailable")

    return {
        "base_mean_score": _mean(base_scores),
        "cand_mean_score": _mean(cand_scores),
        "score_delta": (_mean(cand_scores) or 0.0) - (_mean(base_scores) or 0.0),
        "base_score_variance": _variance(base_scores),
        "cand_score_variance": _variance(cand_scores),
        "base_trigger_match_rate": sum(base_triggers) / len(base_triggers) if base_triggers else None,
        "cand_trigger_match_rate": sum(cand_triggers) / len(cand_triggers) if cand_triggers else None,
        "token_availability": tok_avail,
        "mean_wall_latency_seconds": _mean(latencies),
        "mean_cost_usd": _mean(costs),
    }


def _render_markdown_report(report_data: Dict[str, Any]) -> str:
    lines = [
        "# BÁO CÁO ĐÁNH GIÁ CHẤT LƯỢNG SKILL VÀ PLUGIN TDQ",
        f"{SOUL_LINE}",
        "",
        "## Tổng quan theo từng Cell (Host / Model)",
        "",
        "| Cell | Mẫu | Khuyến nghị | Lý do | Guardrail | Base Điểm | Cand Điểm | Delta | Trigger Base | Trigger Cand | Chi phí (USD) |",
        "|---|---|---|---|---|---|---|---|---|---|---|",
    ]

    for cell_key, cell_data in sorted(report_data.get("cells", {}).items()):
        rec = cell_data["recommendation"]
        met = cell_data["metrics"]
        cost_str = f"{met['mean_cost_usd']:.4f}" if met["mean_cost_usd"] is not None else "unavailable"
        b_score = f"{met['base_mean_score']:.2f}" if met["base_mean_score"] is not None else "null"
        c_score = f"{met['cand_mean_score']:.2f}" if met["cand_mean_score"] is not None else "null"
        delta_str = f"{met['score_delta']:+.2f}" if met["score_delta"] is not None else "null"
        b_trig = f"{met['base_trigger_match_rate']:.0%}" if met["base_trigger_match_rate"] is not None else "null"
        c_trig = f"{met['cand_trigger_match_rate']:.0%}" if met["cand_trigger_match_rate"] is not None else "null"

        lines.append(
            f"| `{cell_key}` | {cell_data['sample_count']} | **{rec['verdict']}** | `{rec['reason']}` | "
            f"{'ĐẠT' if rec['guardrail_ok'] else 'TRƯỢT'} | {b_score} | {c_score} | {delta_str} | "
            f"{b_trig} | {c_trig} | {cost_str} |"
        )

    lines.extend([
        "",
        "## Chi tiết khuyến nghị và quy tắc Guardrail",
        "",
        "- **KEEP**: Chất lượng cải thiện vượt ngưỡng biên độ đăng ký trước và không vi phạm guardrail.",
        "- **TRIM**: Chất lượng không đổi nhưng hiệu quả token/chi phí cải thiện vượt ngưỡng.",
        "- **DROP**: Hồi quy chất lượng hoặc tỷ lệ trigger trượt quá biên độ cho phép.",
        "- **INCONCLUSIVE**: Chưa đủ mẫu, thiếu chỉ số đo bắt buộc, hoặc baseline đã chạm trần.",
        "",
        "Báo cáo được tổng hợp ngoại tuyến (offline) hoàn toàn từ các bản ghi đối chứng.",
    ])
    return "\n".join(lines)


def generate_report(
    results_dir: Union[str, Path],
    out_json: Optional[Union[str, Path]] = None,
    out_md: Optional[Union[str, Path]] = None,
    policy: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Offline aggregation of trial records grouped by cell, zero model or network calls."""
    res_path = Path(results_dir).resolve(strict=True)
    record_files = sorted(res_path.glob("trial_*.json"))
    if not record_files:
        record_files = sorted(f for f in res_path.glob("*.json") if f.name != "run_summary.json")

    records = [_load_json(f) for f in record_files]

    # Group by cell (host, model)
    by_cell: Dict[Tuple[str, str], List[Dict[str, Any]]] = {}
    for r in records:
        host = r.get("host")
        model = r.get("model")
        if host and model:
            by_cell.setdefault((host, model), []).append(r)

    active_policy = policy or {"min_pairs": 1, "quality_margin": 0.05, "efficiency_margin": 0.1}

    cells_report: Dict[str, Any] = {}
    for (host, model), cell_records in sorted(by_cell.items()):
        cell_key = f"{host}:{model}"
        pairs = _pair_trials(cell_records)
        recommendation = tdq_eval_contract.evaluate_cell_recommendation(pairs, policy=active_policy)
        metrics = _summarize_cell_metrics(pairs)

        cells_report[cell_key] = {
            "host": host,
            "model": model,
            "sample_count": len(pairs),
            "recommendation": recommendation,
            "metrics": metrics,
        }

    report_data = {
        "cells": cells_report,
        "total_records": len(records),
        "total_cells": len(cells_report),
        "policy": active_policy,
    }

    if out_json:
        _write_json(report_data, out_json)

    if out_md:
        md_text = _render_markdown_report(report_data)
        Path(out_md).resolve().write_text(md_text, encoding="utf-8")

    _log("report generated", muc="thong-tin", cell_count=len(cells_report))
    return report_data


def cmd_report(args: argparse.Namespace) -> int:
    policy = _load_json(args.policy) if args.policy else None
    out_json = args.out_json
    out_md = args.out_md
    if args.out_prefix:
        out_json = out_json or f"{args.out_prefix}.json"
        out_md = out_md or f"{args.out_prefix}.md"

    res = generate_report(
        results_dir=args.results_dir,
        out_json=out_json,
        out_md=out_md,
        policy=policy,
    )
    print(json.dumps(res, indent=2))
    return 0


# ------------------------------------------------------------------- CLI main
def build_cli_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="TDQ Skill and Plugin Evaluation Runner and Reporter (O2)"
    )
    subparsers = parser.add_subparsers(dest="command", help="Sub-command to execute")

    # plan
    p_plan = subparsers.add_parser("plan", help="Validate eval plan and compute experiment hash")
    p_plan.add_argument("--plan", required=True, help="Path to eval-plan JSON")
    p_plan.add_argument("--out", help="Path to write validated plan with experiment hash")

    # check
    p_check = subparsers.add_parser("check", help="Preflight check host cells and gate without model calls")
    p_check.add_argument("--plan", required=True, help="Path to eval-plan JSON")
    p_check.add_argument("--stage", choices=["pre_implement", "pre_report"], default="pre_implement")
    p_check.add_argument("--profile", help="Path to execution profile JSON")
    p_check.add_argument("--actual-targets", help="Path to actual target hashes JSON")
    p_check.add_argument("--evidence-dir", help="Directory of trial evidence records")
    p_check.add_argument("--waiver", help="Path to user waiver JSON")

    # run
    p_run = subparsers.add_parser("run", help="Run bounded evaluation trials with AB/BA schedule")
    p_run.add_argument("--plan", required=True, help="Path to eval-plan JSON")
    p_run.add_argument("--cases", required=True, help="Path to cases JSON")
    p_run.add_argument("--profile", required=True, help="Path to execution profile JSON")
    p_run.add_argument("--out-dir", required=True, help="Output directory for trials and traces")

    # report
    p_rep = subparsers.add_parser("report", help="Generate offline report per (host, model) cell")
    p_rep.add_argument("--results-dir", required=True, help="Directory containing trial records")
    p_rep.add_argument("--out-json", help="Path to output report JSON")
    p_rep.add_argument("--out-md", help="Path to output report Markdown")
    p_rep.add_argument("--out-prefix", help="Prefix for report outputs (.json and .md)")
    p_rep.add_argument("--policy", help="Path to decision policy JSON")

    return parser


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_cli_parser()
    args = parser.parse_args(argv if argv is not None else sys.argv[1:])

    if not args.command:
        parser.print_help(sys.stderr)
        return 2

    dispatch = {
        "plan": cmd_plan,
        "check": cmd_check,
        "run": cmd_run,
        "report": cmd_report,
    }
    handler = dispatch.get(args.command)
    if not handler:
        parser.print_help(sys.stderr)
        return 2
    return handler(args)


if __name__ == "__main__":
    sys.exit(main())
