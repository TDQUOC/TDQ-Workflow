"""Run locked response-only A/B cases; leave quality unavailable until rubric review."""
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "scripts"))
import tdq_eval_contract
import tdq_skill_eval

ART = Path(__file__).resolve().parent
plan = json.loads((ART / "eval-plan.json").read_text(encoding="utf-8"))
paths = list(plan["targets"])
sources = {}
for variant, source in (("A", ART / "baseline"), ("B", ROOT)):
    hashes = {name: hashlib.sha256((source / name).read_bytes()).hexdigest() for name in paths}
    sources[variant] = {"root": str(source), "hashes": hashes}
plan["targets"] = sources["B"]["hashes"]
plan["base_identity"] = tdq_eval_contract._digest(sources["A"]["hashes"])
plan["candidate_identity"] = tdq_eval_contract._digest(sources["B"]["hashes"])
plan["execution_notes"]["status"] = "bound_response_only_trials"
profile = {"sources": sources, "timeout_seconds": 120, "max_retries": 0,
           "max_total_attempts": 1}
for name, value in (("eval-plan-bound.json", plan), ("host-profile.json", profile)):
    (ART / name).write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")
validation = tdq_skill_eval.plan_eval(plan)
if not validation["valid"]:
    raise SystemExit(validation["errors"])
def command_for_trial(trial, isolated):
    instructions = Path(isolated["workspace_dir"]) / "instructions.txt"
    instructions.write_text(trial["instructions"], encoding="utf-8")
    return ["claude", "--print", "--verbose", "--output-format", "stream-json",
            "--model", trial["model"], "--system-prompt-file", str(instructions),
            "--tools", "", "--strict-mcp-config", "--mcp-config", '{"mcpServers":{}}',
            "--setting-sources", "", "--", trial["prompt"]]


result = tdq_skill_eval.run_eval(ART / "eval-plan-bound.json", ART / "corpus.json",
                                ART / "host-profile.json", ART / "trials",
                                command_builder=command_for_trial)
print(json.dumps(result))
