"""Record a bounded, reproducible Graphify code/full/wiki comparison."""
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "evals" / "graphify-full-wiki-ab"
LOG = ROOT / "evals" / "graphify_full_wiki_ab_logs.jsonl"
REPORT = ROOT / "docs" / "tdq" / "bench" / "2026-10-20-0032-graphify-full-wiki-ab.md"
REAL_FULL_LIMIT = 3


def run_cap(configurations):
    """Reject a run plan that exceeds the user-approved real full-extraction cap."""
    count = sum(name in {"full", "full_wiki"} for name in configurations)
    if count > REAL_FULL_LIMIT:
        raise ValueError(f"full extraction cap {REAL_FULL_LIMIT} exceeded by {count}")
    return count


def usage_or_none(payload):
    """Keep provider usage only when the backend actually returned it."""
    usage = payload.get("usage")
    return usage if isinstance(usage, dict) else None


def choose_selector(results):
    """Never change grep/LSP routing from incomplete or incomparable evidence."""
    required = ("code_only", "full", "full_wiki")
    complete = all(results.get(name, {}).get("status") == "OK" and
                   isinstance(results.get(name, {}).get("metrics"), dict)
                   for name in required)
    decision = "evaluate-graphify-context" if complete else "keep-current"
    reason = ("all three configurations have comparable retrieval/context metrics"
              if complete else "evidence lacks comparable retrieval/context metrics; selector stays unchanged")
    return {"decision": decision, "reason": reason, "exact_name": "grep",
            "relation_type_rename": "LSP",
            "concept_architecture": "Graphify + grep, then verify"}


def backend_env():
    """Map the approved Claude session endpoint to Graphify's OpenAI-compatible backend."""
    env = os.environ.copy()
    if env.get("ANTHROPIC_BASE_URL") and env.get("ANTHROPIC_AUTH_TOKEN"):
        env["OPENAI_BASE_URL"] = env["ANTHROPIC_BASE_URL"]
        env["OPENAI_API_KEY"] = env["ANTHROPIC_AUTH_TOKEN"]
        env.setdefault("OPENAI_MODEL", "custom-combo-no2")
    return env


def run_command(command, *, cwd, env):
    """Capture bounded command output without printing credentials."""
    started = time.perf_counter()
    try:
        result = subprocess.run(command, cwd=cwd, env=env, capture_output=True,
                                encoding="utf-8", errors="replace", timeout=900)
        return {"returncode": result.returncode, "stdout": result.stdout,
                "stderr": result.stderr,
                "latency_ms": (time.perf_counter() - started) * 1000}
    except subprocess.TimeoutExpired as error:
        return {"returncode": -1, "stdout": str(error.stdout or ""),
                "stderr": str(error.stderr or "timeout"),
                "latency_ms": (time.perf_counter() - started) * 1000}


def artifact_status(path):
    """Describe graph/wiki artifact existence without interpreting relevance."""
    output = path / "graphify-out"
    graph = output / "graph.json"
    wiki = output / "wiki" / "index.md"
    if not graph.is_file():
        return {"status": "MISSING", "reason": "graph.json was not produced"}
    try:
        payload = json.loads(graph.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        return {"status": "MISSING", "reason": f"graph unreadable: {error}"}
    return {"status": "OK", "nodes": len(payload.get("nodes", [])),
            "links": len(payload.get("links", payload.get("edges", []))),
            "wiki": wiki.is_file()}


def wiki_command(target):
    """Point export at extract's nested `--out/graphify-out` directory."""
    return ["graphify", "export", "wiki", "--graph",
            str(target / "graphify-out" / "graph.json")]


def run_configuration(name, command, *, needs_wiki=False):
    """Run one configuration and preserve raw output for later audit."""
    target = OUT / name
    target.mkdir(parents=True, exist_ok=True)
    env = backend_env()
    result = run_command(command + ["--out", str(target)], cwd=ROOT, env=env)
    if result["returncode"] != 0:
        return {"name": name, "status": "ERROR", "command": command,
                **result, "artifact": artifact_status(target)}
    if needs_wiki:
        wiki = run_command(wiki_command(target), cwd=ROOT, env=env)
        result["wiki_command"] = wiki
        if wiki["returncode"] != 0:
            return {"name": name, "status": "ERROR", "command": command,
                    **result, "artifact": artifact_status(target)}
    artifact = artifact_status(target)
    return {"name": name, "status": artifact["status"], "command": command,
            **result, "artifact": artifact}


def markdown(records, selector):
    """Summarize artifact/runtime evidence without claiming unmeasured accuracy."""
    lines = ["# Benchmark A/B — Graphify code-only, full và full + wiki", "",
             "- Root: `TDQ-Workflow` · Cap thực: 3 full extraction · backend/model không ghi secret.",
             "- Đây là benchmark artifact/runtime. Wiki là output derived, không được ingest ngược; vì vậy nó không tự tạo truy vấn `full_wiki` độc lập.",
             "", "| Cấu hình | Kết quả | Nodes | Links | Wiki | Thời gian (ms) |", "|---|---|---:|---:|---|---:|"]
    for record in records:
        artifact = record["artifact"]
        lines.append("| {name} | {status} | {nodes} | {links} | {wiki} | {latency:.2f} |".format(
            name=record["name"], status=record["status"],
            nodes=artifact.get("nodes", "—"), links=artifact.get("links", "—"),
            wiki=artifact.get("wiki", False), latency=record["latency_ms"]))
    lines += ["", "## Quyết định selector", "",
              f"- Decision: **{selector['decision']}** — {selector['reason']}.",
              f"- Tên chính xác: **{selector['exact_name']}**; quan hệ/kiểu/rename: **{selector['relation_type_rename']}**; khái niệm/kiến trúc: **{selector['concept_architecture']}**.",
              "- Không có P/R/F1 hoặc token/tool-call claim mới: benchmark này không có gold retrieval độc lập và backend có thể không trả usage.",
              "- Raw stdout/stderr và return code nằm trong JSONL; lỗi vẫn được giữ thay vì chuyển thành PASS."]
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    """Run approved configurations: one code-only baseline and at most two full runs."""
    configurations = ["code_only", "full", "full_wiki"]
    run_cap(configurations)
    records = [
        run_configuration("code_only", ["graphify", "extract", ".", "--code-only"]),
        run_configuration("full", ["graphify", "extract", ".", "--backend", "openai"]),
        run_configuration("full_wiki", ["graphify", "extract", ".", "--backend", "openai"], needs_wiki=True),
    ]
    selector = choose_selector({record["name"]: record for record in records})
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with LOG.open("w", encoding="utf-8") as handle:
        metadata = {"kind": "metadata", "at": datetime.now(timezone.utc).isoformat(),
                    "real_full_runs": run_cap(configurations), "selector": selector}
        handle.write(json.dumps(metadata, ensure_ascii=False) + "\n")
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")
    markdown(records, selector)
    print(json.dumps({"selector": selector, "records": len(records)}, ensure_ascii=False))


if __name__ == "__main__":
    sys.exit(main() or 0)
