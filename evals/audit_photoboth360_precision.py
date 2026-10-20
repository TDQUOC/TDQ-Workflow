"""Measure source-scoped Graphify retrieval without model/API calls."""
import hashlib
import json
import posixpath
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

BASE = Path(__file__).resolve().parent
GOLD = BASE / "photoboth360_precision_gold.json"
LOG = BASE / "photoboth360_precision_logs.jsonl"
SUMMARY = BASE / "photoboth360_precision_summary.md"


def sha(path):
    """Fingerprint bytes rather than relying on modification times."""
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def classify(actual, expected, universe):
    """Compare judged sets; never count an unjudged item as a false positive."""
    actual, expected, universe = set(actual), set(expected), set(universe)
    judged = actual & universe
    tp, fp, fn = judged & expected, judged - expected, expected - judged
    precision = len(tp) / len(judged) if judged else None
    recall = len(tp) / len(expected) if expected else None
    denominator = 2 * len(tp) + len(fp) + len(fn)
    return {"tp": sorted(tp), "fp": sorted(fp), "fn": sorted(fn),
            "unjudged": sorted(actual - universe), "actual": sorted(actual),
            "expected": sorted(expected), "precision": precision,
            "recall": recall, "f1": 2 * len(tp) / denominator if denominator else None,
            "judged_coverage": len(judged) / len(actual) if actual else None}


def rank_metrics(files, relevant):
    """Use fixed k=5; missing slots count zero, RR is truncated at ten."""
    files = list(dict.fromkeys(files))
    hits = len(set(files[:5]) & set(relevant))
    positions = [i for i, f in enumerate(files[:10], 1) if f in relevant]
    return {"p_at_5": hits / 5,
            "r_at_5": hits / len(relevant) if relevant else None,
            "hit_at_5": int(hits > 0),
            "rr_at_10": 1 / positions[0] if positions else 0,
            "first_relevant_rank": positions[0] if positions else None}


def dedup_files(scored, nodes):
    """Keep each file's first occurrence, retaining Graphify's own tie order."""
    seen, output = set(), []
    for score, node in scored:
        file = nodes[node].get("source_file", "").replace("\\", "/")
        if file and file not in seen:
            seen.add(file)
            output.append({"file": file, "score": score, "node": node})
    return output


def parse_cli(output):
    """Read only NODE source annotations, not echoed seeds or EDGE text."""
    if output.strip() == "No matching nodes found.":
        return []
    files = re.findall(r"^NODE .*?\[src=(.*?) loc=", output, re.MULTILINE)
    if not files:
        raise ValueError("No parseable NODE records; not an empty retrieval")
    return list(dict.fromkeys(f.replace("\\", "/") for f in files))


def checked_output(code, output, error):
    """Refuse to interpret command failures as successful empty searches."""
    if code != 0:
        raise RuntimeError(f"CLI exit {code}: {error}")
    return parse_cli(output)


def import_target(file, spec, root):
    """Resolve literal requires independently from graph IDs."""
    if not spec.startswith("."):
        return "pkg:" + spec
    relative = posixpath.normpath(posixpath.join(posixpath.dirname(file), spec))
    options = [relative, relative + ".js", relative + "/index.js"]
    for option in options:
        if (root / option).is_file():
            return option
    return "rel:" + relative


def verify(gold):
    """Check frozen input fingerprints and query source evidence."""
    import graphify.serve as serve
    root = Path(gold["target"])
    fingerprints = gold["fingerprints"]
    assert sha(root / gold["graph"]) == fingerprints["graph_sha256"]
    assert sha(serve.__file__) == fingerprints["scorer_sha256"]
    for file, digest in fingerprints["source_sha256"].items():
        assert sha(root / file) == digest, file
    for query in gold["queries"]:
        for file, evidence in query["relevant"].items():
            line = (root / file).read_text(encoding="utf-8").splitlines()[evidence["line"] - 1]
            assert evidence["text"] in line, (query["id"], file)


def expected_imports(gold, file):
    """Attach source lines to every manually reviewed literal import."""
    root = Path(gold["target"])
    lines = (root / file).read_text(encoding="utf-8").splitlines()
    result = {}
    for spec in gold["sources"][file]["imports"]:
        target = import_target(file, spec, root)
        evidence = [i for i, line in enumerate(lines, 1)
                    if re.search(r"require\([\"']" + re.escape(spec) + r"[\"']\)", line)]
        assert evidence, (file, spec)
        result[target] = {"specifier": spec, "lines": evidence}
    return result


def actual_imports(file, edges, nodes, expected):
    """Decode exact graph endpoints, disclosing lossy identifier normalization."""
    expected_ids = {}
    for target, evidence in expected.items():
        spec = evidence["specifier"]
        if target.startswith("pkg:"):
            key = "ref_" + re.sub(r"[^a-z0-9]+", "_", spec.lower()).strip("_")
        else:
            path = target.removeprefix("rel:")
            key = re.sub(r"[^a-z0-9]+", "_", re.sub(r"\.js$", "", path).lower()).strip("_")
        assert key not in expected_ids, "Ambiguous normalized import identity"
        expected_ids[key] = target
    selected = [e for e in edges if e.get("relation") == "imports_from"
                and e.get("source_file") == file]
    actual = []
    for edge in selected:
        target = edge["target"]
        node = nodes.get(target, {})
        actual.append(expected_ids.get(target, node.get("source_file") or "unresolved:" + target))
    return actual, selected


def function_evidence(gold, file):
    """Locate reviewed named definitions, excluding comment-only mentions."""
    lines = (Path(gold["target"]) / file).read_text(encoding="utf-8").splitlines()
    evidence = {}
    for name in gold["sources"][file]["functions"]:
        pattern = r"(?:exports\." + name + r"\s*=|\bfunction\s+" + name + r"\s*\(|\b" + name + r"\s*:\s*function)"
        evidence[name] = [{"line": i, "text": line.strip()} for i, line in enumerate(lines, 1)
                          if not line.lstrip().startswith("//") and re.search(pattern, line)]
        assert evidence[name], (file, name)
    return evidence


def evaluate_inventory(gold, raw):
    """Compare exact dependency and named-function inventories per source file."""
    nodes = {n["id"]: n for n in raw["nodes"]}
    edges = raw.get("links", raw.get("edges", []))
    records = []
    for file, source in gold["sources"].items():
        started = time.perf_counter()
        expected = expected_imports(gold, file)
        actual, selected = actual_imports(file, edges, nodes, expected)
        all_targets = set(actual) | set(expected)
        records.append({"id": file, "kind": "imports", "status": "OK",
                        **classify(actual, expected, all_targets),
                        "evidence": expected, "raw_edges": selected,
                        "latency_ms": (time.perf_counter() - started) * 1000})
        started = time.perf_counter()
        functions = [n for n in nodes.values() if n.get("source_file") == file
                     and n.get("_callable") is True]
        labels = [re.sub(r"\(.*$", "", n["label"]).split(".")[-1] for n in functions]
        universe = set(labels) | set(source["functions"])
        records.append({"id": file, "kind": "functions", "status": "OK",
                        **classify(labels, source["functions"], universe),
                        "raw_nodes": functions,
                        "latency_ms": (time.perf_counter() - started) * 1000,
                        "evidence": function_evidence(gold, file)})
    return records


def run_cli(gold, query):
    """Capture the complete budgeted context response and command errors."""
    command = ["graphify", "query", query, "--budget", "1500", "--graph",
               str(Path(gold["target"]) / gold["graph"])]
    started = time.perf_counter()
    record = {"command": command, "stdout": "", "stderr": ""}
    try:
        result = subprocess.run(command, cwd=gold["target"], capture_output=True,
                                encoding="utf-8", errors="strict", timeout=30,
                                creationflags=0x08000000 if sys.platform == "win32" else 0)
        record = {"command": command, "stdout": result.stdout, "stderr": result.stderr,
                  "returncode": result.returncode}
        record["files"] = checked_output(result.returncode, result.stdout, result.stderr)
        record["status"] = "OK"
    except (subprocess.TimeoutExpired, UnicodeError, RuntimeError, ValueError) as error:
        record.update({"status": "ERROR", "error": str(error)})
        if isinstance(error, subprocess.TimeoutExpired):
            record.update({"stdout": str(error.stdout or ""),
                           "stderr": str(error.stderr or "")})
    record["latency_ms"] = (time.perf_counter() - started) * 1000
    return record


def evaluate_query(gold, query, graph):
    """Separate native full-graph scorer order from CLI traversal context."""
    from graphify.serve import _query_terms, _score_nodes
    total_started = time.perf_counter()
    started = time.perf_counter()
    scored = _score_nodes(graph, _query_terms(query["text"]))
    ranking = dedup_files(scored, graph.nodes)
    scope = set(gold["sources"])
    judged = [r for r in ranking if r["file"] in scope]
    files = [r["file"] for r in judged]
    relevant = set(query["relevant"])
    result = {"id": query["id"], "query": query, "kind": "query", "status": "OK",
              "ranking": {**classify(files[:5], relevant, scope),
                          **rank_metrics(files, relevant), "scoped_files": judged,
                          "full_file_order": ranking,
                          "raw_scored_nodes": scored,
                          "top10_unjudged_files": [r for r in ranking[:10] if r["file"] not in scope],
                          "latency_ms": (time.perf_counter() - started) * 1000}}
    cli = run_cli(gold, query["text"])
    if cli["status"] == "OK":
        cli.update(classify(cli["files"], relevant, scope))
    else:
        result["status"] = "ERROR"
    result["cli_context"] = cli
    result["latency_ms"] = (time.perf_counter() - total_started) * 1000
    return result


def aggregate(results):
    """Report micro confusion counts and macro means, ignoring undefined ratios."""
    totals: dict = {k: sum(len(r[k]) for r in results) for k in ("tp", "fp", "fn")}
    tp, fp, fn = (totals[k] for k in ("tp", "fp", "fn"))
    totals["precision"] = tp / (tp + fp) if tp + fp else None
    totals["recall"] = tp / (tp + fn) if tp + fn else None
    totals["f1"] = 2 * tp / (2 * tp + fp + fn) if 2 * tp + fp + fn else None
    for key in ("precision", "recall", "f1"):
        values = [r[key] for r in results if r[key] is not None]
        totals["macro_" + key] = sum(values) / len(values) if values else None
        totals["macro_" + key + "_n"] = len(values)
    return totals


def detail_lines(records):
    """List concrete wrong and missed identities without changing labels."""
    lines = []
    for record in records:
        if record["kind"] == "query":
            lines += [f"\n### {record['id']} · {record['query']['text']}",
                      f"Scorer scoped top5 FP: {record['ranking']['fp']}",
                      f"Scorer scoped top5 FN: {record['ranking']['fn']}",
                      f"CLI FP: {record['cli_context'].get('fp', 'ERROR')}",
                      f"CLI FN: {record['cli_context'].get('fn', 'ERROR')}"]
        elif record["fp"] or record["fn"]:
            lines += [f"\n### {record['kind']} · {record['id']}",
                      f"FP: {record['fp']}", f"FN: {record['fn']}"]
    return lines


def summary_metrics(records):
    """Aggregate the four distinct evaluation surfaces separately."""
    queries = [r for r in records if r["kind"] == "query"]
    groups = {k: [r for r in records if r["kind"] == k] for k in ("imports", "functions")}
    groups["scorer_top5_scoped"] = [r["ranking"] for r in queries]
    groups["cli_context_scoped"] = [r["cli_context"] for r in queries if r["cli_context"]["status"] == "OK"]
    aggregates = {k: aggregate(v) for k, v in groups.items()}
    means = {k: sum(r["ranking"][k] for r in queries) / len(queries)
             for k in ("p_at_5", "r_at_5", "hit_at_5", "rr_at_10")}
    return queries, aggregates, means


def report(records, fingerprints):
    """Render results without imposing a quality pass threshold."""
    queries, aggregates, means = summary_metrics(records)
    lines = ["# Graphify — precision, recall và ranking thực đo", "",
             "11 file JS nodeserver · 12 truy vấn (6 EN, 6 VI) · file-level relevance trực tiếp · graph giữ nguyên.",
             "Gold set do agent đọc source lập; mẫu có chủ đích, chưa phải gold độc lập do người thẩm định. Không suy rộng toàn dự án.",
             "", "## Kết quả tổng hợp", "", "```json",
             json.dumps({"aggregates": aggregates, "ranking_means": means}, ensure_ascii=False, indent=2), "```",
             "", "## Từng truy vấn", "", "| ID | P@5 | R@5 | Hit@5 | RR@10 | TP/FP/FN top5 scoped | CLI TP/FP/FN |", "|---|---:|---:|---:|---:|---|---|"]
    for r in queries:
        m, c = r["ranking"], r["cli_context"]
        counts = "/".join(str(len(m[k])) for k in ("tp", "fp", "fn"))
        cli_counts = "/".join(str(len(c[k])) for k in ("tp", "fp", "fn")) if c["status"] == "OK" else "ERROR"
        lines.append(f"| {r['id']} | {m['p_at_5']:.3f} | {m['r_at_5']:.3f} | {m['hit_at_5']} | {m['rr_at_10']:.3f} | {counts} | {cli_counts} |")
    lines += ["", "## Diễn giải và giới hạn", "",
              "Ranking đo scorer nội bộ trên FULL graph rồi lọc về 11 file judged và khử trùng file theo lần đầu. Đây là ranking scoped lạc quan hơn trải nghiệm full corpus; thứ hạng NODE trong CLI không phải ranking. Raw full order và top10 unjudged có trong JSONL.",
              "P@5 dùng mẫu số cố định 5 (slot thiếu = 0); Recall@5 = TP@5/số file đúng; Hit@5 và RR@10 theo scoped order. Ties giữ thứ tự scorer, không sắp theo gold. FP/FN ranking là tại cutoff 5, không phải toàn danh sách.",
              "Precision không có prediction, recall không có gold hoặc F1 có denominator 0 = null, không tự gán 100%; macro bỏ null và ghi số mẫu n. CLI lỗi không chấm như tập rỗng; báo riêng tỷ lệ lỗi.",
              "Imports so endpoint exact sau normalize ID package/relative path, collision bị từ chối; ID normalize có mất thông tin. Functions là inventory callable theo file, không chứng minh contains ownership hoặc call-flow đúng. Anonymous callbacks và dynamic require ngoài phạm vi gold.",
              "Nguồn/dòng imports trong từng record; function inventory có raw source snapshot trong metadata và raw node location. Chưa có kiểm tra độc lập bởi con người. CLI raw output là toàn bộ response trong budget 1500, không phải toàn bộ graph.",
              "Hash trước/sau phải khớp. Không rebuild graph nên snapshot có thể cũ; hash chỉ chứng minh ổn định lúc đo, không chứng minh graph đồng bộ hoàn toàn với source.",
              "", "## Fingerprints", "```json", json.dumps(fingerprints, indent=2), "```"]
    lines += detail_lines(records)
    SUMMARY.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return {"aggregates": aggregates, "ranking_means": means,
            "cli_errors": sum(r["status"] == "ERROR" for r in queries)}


def main():
    """Freeze-run-verify with append-only raw records and a derived report."""
    from graphify.serve import _load_graph
    gold_hash = sha(GOLD)
    gold = json.loads(GOLD.read_text(encoding="utf-8"))
    verify(gold)
    root = Path(gold["target"])
    graph = _load_graph(str(root / gold["graph"]))
    raw = json.loads((root / gold["graph"]).read_text(encoding="utf-8"))
    metadata = {"kind": "metadata", "at": datetime.now(timezone.utc).isoformat(),
                "gold_sha256": gold_hash, **gold["fingerprints"],
                "source_snapshots": {f: (root / f).read_text(encoding="utf-8") for f in gold["sources"]}}
    records = []
    with LOG.open("x", encoding="utf-8") as log:
        log.write(json.dumps(metadata, ensure_ascii=False) + "\n")
        for record in evaluate_inventory(gold, raw):
            records.append(record)
            log.write(json.dumps(record, ensure_ascii=False) + "\n")
        for query in gold["queries"]:
            record = evaluate_query(gold, query, graph)
            records.append(record)
            log.write(json.dumps(record, ensure_ascii=False) + "\n")
            log.flush()
            print(query["id"], record["status"], flush=True)
        verify(gold)
        assert sha(GOLD) == gold_hash, "Gold changed during run"
        log.write(json.dumps({"kind": "integrity", "before_after_match": True}) + "\n")
    print(json.dumps(report(records, metadata | {"source_snapshots": "in JSONL"}), ensure_ascii=False))


if __name__ == "__main__":
    main()
