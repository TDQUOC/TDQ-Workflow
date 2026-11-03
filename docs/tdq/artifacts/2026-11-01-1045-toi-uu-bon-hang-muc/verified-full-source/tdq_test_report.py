"""Pure execution timing summaries and offline, source-bound report export.

summarize_result(result) does no file/process/state work; a runner may attach it
as slow_tests. render_json/markdown/html consume the same summary. export_report
reads an external result and returns {summary,input_sha256,result_status,outputs}.
JSON is the last commit marker and binds MD/HTML digests. Export success and
quality describe the report/durations, never replace the source verdict/exit.
"""
from collections import Counter, defaultdict
from datetime import datetime, timezone
import hashlib
from html import escape
import json
import math
import os
from pathlib import Path
import sys
import tempfile
from urllib.parse import quote, urlsplit


SCHEMA_VERSION = 1
TOP_LIMIT = 20
STATUSES = {"PASS", "FAIL", "ERROR", "INCOMPLETE", "SKIP"}


class ReportError(ValueError):
    """The input cannot safely produce the requested report."""


def _log(stage, **metadata):
    if os.environ.get("TDQ_LOG", "1").lower() not in {"0", "false", "off"}:
        fields = " ".join(f"{key}={value}" for key, value in metadata.items())
        print(f"[{datetime.now(timezone.utc).isoformat()}] test-report stage={stage} {fields}", file=sys.stderr)


def _number(value):
    if type(value) not in (int, float) or value < 0:
        return False
    try:
        return math.isfinite(value)
    except OverflowError:
        return False


def _finite_sum(values):
    try:
        total = math.fsum(values)
    except OverflowError:
        return None
    return total if math.isfinite(total) else None


def _validate_result(result):
    status = result.get("status") if isinstance(result, dict) else None
    if not isinstance(status, str) or status not in STATUSES:
        raise ReportError("Input is not a supported result object with a source status")
    version = result.get("schema_version", 1)
    if type(version) is not int or version not in (1, 2):
        raise ReportError("Unsupported result schema version")
    rows = result.get("case_outcomes")
    if rows is not None and not isinstance(rows, list):
        raise ReportError("case_outcomes must be an array")


def _identifier(row):
    value = row.get("case_id") if isinstance(row, dict) else None
    if not isinstance(value, str) or not value.strip() or "\x00" in value:
        return None
    return value if value.split("::")[0].strip() else None


def _phase_structure(phases):
    if not isinstance(phases, list) or not phases:
        return "missing_phases"
    if any(not isinstance(phase, dict) or not isinstance(phase.get("phase"), str)
           or phase["phase"] not in {"setup", "call", "teardown"}
           or "subtest" in phase for phase in phases):
        return "invalid_phase"
    names = [phase["phase"] for phase in phases]
    if len(set(names)) != len(names):
        return "duplicate_phase"
    setup = next((phase for phase in phases if phase["phase"] == "setup"), {})
    expected = {"setup", "teardown"}
    if setup.get("outcome") not in ("skip", "fail", "error"):
        expected.add("call")
    return "incomplete_phases" if set(names) != expected else ""


def _case_duration(case):
    phases = case.get("phases")
    reason = _phase_structure(phases)
    if reason:
        return None, reason
    if any("duration_seconds" not in phase for phase in phases):
        return None, "missing_duration"
    values = [phase["duration_seconds"] for phase in phases]
    if not all(_number(value) for value in values):
        return None, "invalid_duration"
    total = _finite_sum(values)
    return (total, "") if total is not None else (None, "invalid_duration_total")


def _collect_cases(cases):
    counts = Counter(identifier for row in cases if (identifier := _identifier(row)) is not None)
    ranked, issues, unranked, incomplete = [], {}, {}, set()
    for index, case in enumerate(cases):
        identifier = _identifier(case)
        if identifier is None:
            issues[("", index)] = {"case_id": None, "reason": "invalid_case_id", "row_index": index}
            continue
        module = identifier.split("::")[0]
        duration, reason = (None, "duplicate_case_id") if counts[identifier] > 1 else _case_duration(case)
        if reason:
            issues[(identifier, 0)] = {"case_id": identifier, "reason": reason}
            unranked[identifier] = {"case_id": identifier, "reason": reason}
            incomplete.add(module)
        else:
            outcome = case.get("outcome")
            ranked.append({"case_id": identifier, "module": module, "duration_seconds": duration,
                           "outcome": outcome if isinstance(outcome, str) else "unknown"})
    return ranked, list(issues.values()), list(unranked.values()), incomplete, counts


def _collect_modules(cases, incomplete):
    groups = defaultdict(list)
    for case in sorted(cases, key=lambda row: row["case_id"]):
        groups[case["module"]].append(case["duration_seconds"])
    ranked, unranked = [], []
    for module in sorted(set(groups) | incomplete):
        seconds = _finite_sum(groups[module]) if groups[module] else None
        if module in incomplete or seconds is None:
            unranked.append({"module": module, "known_duration_seconds": seconds,
                             "reason": "incomplete_case_data" if module in incomplete else "invalid_duration_total"})
        else:
            ranked.append({"module": module, "duration_seconds": seconds,
                           "case_count": len(groups[module])})
    return ranked, unranked


def _wall(result):
    timings = result.get("timings")
    if timings is None:
        return None, "unavailable"
    if not isinstance(timings, dict):
        return None, "invalid"
    value = timings.get("wall_seconds")
    if value is None:
        return None, "unavailable"
    return (value, "complete") if _number(value) else (None, "invalid")


def summarize_result(result):
    """Rank complete execution phase sums without double-counting subtests."""
    _validate_result(result)
    cases = result.get("case_outcomes") or []
    rows, issues, unranked, incomplete, counts = _collect_cases(cases)
    modules, unranked_modules = _collect_modules(rows, incomplete)
    if not cases:
        issues.append({"case_id": None, "reason": "no_execution_cases"})
    known = _finite_sum(row["duration_seconds"] for row in rows) if rows else None
    if rows and known is None:
        issues.append({"case_id": None, "reason": "invalid_execution_total"})
    complete = bool(rows) and not issues and not unranked_modules
    quality = "complete" if complete else ("partial" if rows else "unavailable")
    wall, wall_quality = _wall(result)
    summary = {"schema_version": SCHEMA_VERSION, "result_status": result["status"],
               "result_exit_code": result.get("exit_code") if type(result.get("exit_code")) is int else None,
               "source_action": result.get("action") if isinstance(result.get("action"), str) else None,
               "case_count": len(counts), "observed_rows": len(cases), "ranked_case_count": len(rows),
               "module_count": len(modules) + len(unranked_modules),
               "quality": {"status": quality,
                           "issues": sorted(issues, key=lambda row: (row["case_id"] or "", row["reason"], row.get("row_index", -1))),
                           "unranked_cases": sorted(unranked, key=lambda row: row["case_id"]),
                           "unranked_modules": unranked_modules},
               "top_cases": sorted(rows, key=lambda row: (-row["duration_seconds"], row["case_id"]))[:TOP_LIMIT],
               "top_modules": sorted(modules, key=lambda row: (-row["duration_seconds"], row["module"]))[:TOP_LIMIT],
               "execution_phase_seconds": known if complete else None,
               "known_execution_phase_seconds": known, "wall_seconds": wall, "wall_quality": wall_quality}
    return summary


def render_json(summary):
    """Serialize the shared summary, rejecting accidental non-finite output."""
    return json.dumps(summary, ensure_ascii=True, allow_nan=False, indent=2, sort_keys=True) + "\n"


def _display(value):
    return "unavailable" if value is None else str(value)


def _markdown(value):
    text = escape(_display(value), quote=True)
    return text.replace("\\", "\\\\").replace("|", "\\|").replace("`", "\\`").replace("\r", "\\r").replace("\n", "\\n")


def _table_rows(summary, role):
    if role == "cases":
        return [(row["case_id"], row["duration_seconds"], row["outcome"]) for row in summary["top_cases"]]
    return [(row["module"], row["duration_seconds"], row["case_count"]) for row in summary["top_modules"]]


def _markdown_table(headers, rows):
    lines = ["| " + " | ".join(headers) + " |", "|" + "---|" * len(headers)]
    lines.extend("| " + " | ".join(_markdown(cell) for cell in row) + " |" for row in rows)
    return "\n".join(lines)


def _safe_href(summary):
    href = summary.get("input_href")
    if not isinstance(href, str):
        return None
    url = urlsplit(href)
    return href if not url.scheme and not url.netloc else None


def render_markdown(summary):
    """Render the existing summary without rereading or reaggregating input."""
    lines = ["# Execution timing report", "",
             f"Original result: {_markdown(summary['result_status'])}; exit code: {_markdown(summary['result_exit_code'])}.",
             f"Duration quality: {_markdown(summary['quality']['status'])}; cases: {summary['case_count']}.",
             f"Execution phase total: {_markdown(summary['execution_phase_seconds'])} s; known phases: {_markdown(summary['known_execution_phase_seconds'])} s.",
             f"Wall time (separate): {_markdown(summary['wall_seconds'])} s ({summary['wall_quality']}).", "",
             "## Top20 cases", _markdown_table(("Case ID", "Phase seconds", "Outcome"), _table_rows(summary, "cases")), "",
             "## Top20 modules", _markdown_table(("Module", "Phase seconds", "Cases"), _table_rows(summary, "modules")), "",
             "## Quality and limits", "Only execution setup/call/teardown phases are summed; subtests are not added again.",
             "Incomplete cases/modules are unranked. Known phase time is not suite wall time or CPU time."]
    lines.extend(f"- {_markdown(row['case_id'])}: {_markdown(row['reason'])}" for row in summary["quality"]["issues"][:TOP_LIMIT])
    lines.extend([f"Unranked cases: {len(summary['quality']['unranked_cases'])}; modules: {len(summary['quality']['unranked_modules'])}. Full quality details are in JSON.",
                  "", "## Provenance", f"Input SHA256: {_markdown(summary.get('input_sha256'))}."])
    href = _safe_href(summary)
    if href:
        lines.append(f"[Input result]({href})")
    return "\n".join(lines) + "\n"


def _html_table(headers, rows):
    head = "".join('<th scope="col">' + escape(header) + "</th>" for header in headers)
    body = "".join("<tr>" + "".join("<td>" + escape(_display(cell), quote=True) + "</td>" for cell in row) + "</tr>" for row in rows)
    return '<div class="table-scroll"><table><thead><tr>' + head + "</tr></thead><tbody>" + body + "</tbody></table></div>"


def render_html(summary):
    """Render escaped, self-contained HTML using the same summary values."""
    text = lambda value: escape(_display(value), quote=True)
    issues = "".join("<li>" + text(row["case_id"]) + ": " + text(row["reason"]) + "</li>"
                     for row in summary["quality"]["issues"][:TOP_LIMIT])
    href = _safe_href(summary)
    source = '<p><a href="' + escape(href, quote=True) + '">Input result</a></p>' if href else ""
    return ('<!DOCTYPE html>\n<html lang="en"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width,initial-scale=1">'
            '<title>Execution timing report</title><style>'
            '*{box-sizing:border-box}body{margin:0;background:#f3f6f9;color:#173047;font:16px/1.6 system-ui,sans-serif}'
            'main{max-width:1120px;margin:auto;padding:28px 20px}header,section{background:white;padding:24px;border:1px solid #dce4ec;border-radius:12px;margin-bottom:18px;min-width:0}'
            'h1{font-size:clamp(1.6rem,4vw,2.3rem);line-height:1.2}h2{font-size:1.3rem}a{color:#075e8a;overflow-wrap:anywhere}'
            'p,li,code{overflow-wrap:anywhere}.table-scroll{max-width:100%;overflow-x:auto}table{width:100%;min-width:480px;border-collapse:collapse;font-size:.9rem}'
            'th,td{padding:10px;text-align:left;vertical-align:top;border-bottom:1px solid #dce4ec;overflow-wrap:anywhere}th{background:#edf4f8}td:first-child{max-width:740px}'
            '@media(max-width:600px){main{padding:12px}header,section{padding:18px}body{font-size:15px}}'
            '</style></head><body><main><header><h1>Execution timing report</h1><p>Original result: <strong>'
            + text(summary["result_status"]) + "</strong>; exit code: " + text(summary["result_exit_code"])
            + ". Duration quality: " + text(summary["quality"]["status"]) + "; cases: " + text(summary["case_count"])
            + ".</p><p>Execution phase total: " + text(summary["execution_phase_seconds"]) + " s; known phases: "
            + text(summary["known_execution_phase_seconds"]) + " s. Wall time (separate): " + text(summary["wall_seconds"])
            + " s (" + text(summary["wall_quality"]) + ').</p><nav aria-label="Report sections"><a href="#top-cases">Cases</a> · <a href="#top-modules">Modules</a> · <a href="#quality">Quality</a> · <a href="#provenance">Provenance</a></nav></header>'
            '<section id="top-cases"><h2>Top20 cases</h2>'
            + _html_table(("Case ID", "Phase seconds", "Outcome"), _table_rows(summary, "cases"))
            + '</section><section id="top-modules"><h2>Top20 modules</h2>'
            + _html_table(("Module", "Phase seconds", "Cases"), _table_rows(summary, "modules"))
            + '</section><section id="quality"><h2>Quality and limits</h2><p>Only execution setup/call/teardown phases are summed; subtests are not added again. Incomplete cases/modules are unranked. Phase sums are not suite wall time or CPU time.</p><ul>'
            + issues + "</ul><p>Unranked cases: " + text(len(summary["quality"]["unranked_cases"])) + "; modules: "
            + text(len(summary["quality"]["unranked_modules"])) + ". Full quality details are in JSON.</p></section>"
            '<section id="provenance"><h2>Provenance</h2><p>Input SHA256: <code>'
            + text(summary.get("input_sha256")) + "</code></p>" + source + "</section></main></body></html>\n")


def _read_result(path, expected_sha256):
    before = path.stat()
    content = path.read_bytes()
    after = path.stat()
    identity = lambda stat: (stat.st_dev, stat.st_ino, stat.st_size, stat.st_mtime_ns)
    if identity(before) != identity(after):
        raise ReportError("Input changed while reading")
    checksum = hashlib.sha256(content).hexdigest()
    if expected_sha256 is not None and (not isinstance(expected_sha256, str) or expected_sha256.lower() != checksum):
        raise ReportError("Input SHA256 does not match expected digest")
    try:
        result = json.loads(content)
    except (ValueError, UnicodeError) as error:
        raise ReportError("Input is not readable result JSON") from error
    _validate_result(result)
    return result, checksum


def _stage_bytes(destination, content):
    stream = tempfile.NamedTemporaryFile(dir=destination.parent, prefix=".tdq-report-", suffix=".tmp", delete=False)
    temporary = Path(stream.name)
    try:
        with stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
    except BaseException:
        # Preserve published outputs even on an interrupted staging write.
        temporary.unlink(missing_ok=True)
        raise
    return temporary


def _restore(committed, backups):
    retained = set()
    for path in reversed(committed):
        try:
            if path in backups:
                os.replace(backups[path], path)
            else:
                path.unlink(missing_ok=True)
        except OSError:
            retained.add(backups.get(path, path))
    return retained


def _publish_bundle(contents, source, checksum):
    staged, backups, attempted, retained = {}, {}, [], set()
    try:
        for path, content in contents.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            staged[path] = _stage_bytes(path, content)
            if path.exists():
                backups[path] = _stage_bytes(path, path.read_bytes())
        if hashlib.sha256(source.read_bytes()).hexdigest() != checksum:
            raise ReportError("Input changed during export")
        _log("commit", outputs=len(staged))
        for path, temporary in staged.items():
            attempted.append(path)
            os.replace(temporary, path)
    except BaseException as error:
        # Restore earlier outputs even if interruption arrives just after replace.
        retained = _restore(attempted, backups)
        _log("rollback", retained=len(retained), error=type(error).__name__)
        if retained:
            raise OSError("Export failed; rollback incomplete; recovery files: "
                          + ", ".join(str(path) for path in sorted(retained))) from error
        raise
    finally:
        for temporary in (*staged.values(), *backups.values()):
            if temporary not in retained:
                temporary.unlink(missing_ok=True)


def export_report(result_path, out_prefix, expected_sha256=None):
    """Export JSON/MD/HTML from one external input snapshot without running tests."""
    source = Path(result_path).resolve()
    prefix = Path(out_prefix).absolute()
    paths = {role: prefix.parent / (prefix.name + suffix) for role, suffix in
             (("markdown", ".md"), ("html", ".html"), ("json", ".json"))}
    if any(path.resolve() == source for path in paths.values()):
        raise ReportError("Output must not overwrite the input result")
    _log("read")
    try:
        result, checksum = _read_result(source, expected_sha256)
        summary = summarize_result(result)
        _log("summary", cases=summary["case_count"], ranked=summary["ranked_case_count"],
             quality=summary["quality"]["status"], result_status=summary["result_status"])
        summary["input_sha256"] = checksum
        try:
            summary["input_href"] = quote(Path(os.path.relpath(source, prefix.parent)).as_posix(), safe="/")
        except ValueError:
            summary["input_href"] = None  # Different volumes cannot form a relative link.
        markdown, page = render_markdown(summary), render_html(summary)
        summary["artifacts"] = {
            role: {"path": paths[role].name, "sha256": hashlib.sha256(text.encode("utf-8")).hexdigest()}
            for role, text in (("markdown", markdown), ("html", page))}
        contents = {paths["markdown"]: markdown.encode("utf-8"), paths["html"]: page.encode("utf-8"),
                    paths["json"]: render_json(summary).encode("utf-8")}
        _log("stage", outputs=len(contents))
        _publish_bundle(contents, source, checksum)
    except (OSError, ValueError) as error:
        _log("failed", error=type(error).__name__)
        raise
    _log("exported", outputs=len(paths), result_status=summary["result_status"])
    return {"summary": summary, "input_sha256": checksum, "result_status": summary["result_status"],
            "outputs": {role: {"path": str(path), "sha256": hashlib.sha256(contents[path]).hexdigest()}
                        for role, path in paths.items()}}
