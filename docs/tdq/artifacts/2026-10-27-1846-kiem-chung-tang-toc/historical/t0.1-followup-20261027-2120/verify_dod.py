"""Semantic request evidence verifier. Missing proof fails closed.

Index v2: schema, full_receipt (relative to evidence directory), baseline
{path,sha256}, remaps [{old,new,reason}], checks {D9:{benchmark:{path,sha256}},
D10:{benchmark:...}, D11:{benchmark:...,qc:{path,sha256}}, D12:{html,markdown,
browser,numbers:[{source:{path,sha256},pointer:'/summary/value'}]}}.
All bound artifacts are inside project; receipt paths stay inside evidence.
Hashes detect mutation, not malicious replacement of both evidence and hashes.
Independent QC identity/browser provenance remains an auditable attestation.
"""
import argparse
import ast
from html.parser import HTMLParser
import importlib
import json
from pathlib import Path
import struct
import subprocess
import sys
import tempfile
from urllib.parse import unquote, urlsplit
import xml.etree.ElementTree as ET

from safe_run import SCHEMA, digest, file_hash, source_snapshot


def contained(root, relative):
    """Reject evidence paths escaping the request directory."""
    path = (root / relative).resolve()
    if not path.is_relative_to(root.resolve()):
        raise ValueError("Evidence path escapes request")
    return path


def validate_status(receipt):
    """Reject unsigned, unsuccessful, elevated or configuration-mutating results."""
    signature = receipt.get("sha256")
    unsigned = {key: value for key, value in receipt.items() if key != "sha256"}
    if receipt.get("schema") != SCHEMA or signature != digest(unsigned):
        raise ValueError("Missing or changed receipt digest/schema")
    if receipt.get("exit_code") != 0 or receipt.get("verdict") != "PASS":
        raise ValueError("Command did not pass")
    if receipt.get("elevated") is not False or receipt.get("timed_out") is not False:
        raise ValueError("Elevated or timed out proof")
    if not receipt.get("config_before") or receipt["config_before"] != receipt.get("config_after"):
        raise ValueError("Missing or mutated personal config snapshot")
    if not receipt.get("source_before") or receipt["source_before"] != receipt.get("source_after"):
        raise ValueError("Missing or mutated source snapshot")
    if receipt.get("failure") or receipt.get("failures") or receipt.get("isolation", {}).get("cleanup") != "complete":
        raise ValueError("Harness failure or incomplete sandbox cleanup")


def validate_integrity(path):
    """Validate preserved bytes of PASS or FAIL receipts without certifying success."""
    receipt = json.loads(path.read_text(encoding="utf-8"))
    unsigned = {key: value for key, value in receipt.items() if key != "sha256"}
    if receipt.get("schema") != SCHEMA or receipt.get("sha256") != digest(unsigned):
        raise ValueError("Missing or changed receipt digest/schema")
    if not isinstance(receipt.get("artifacts"), dict):
        raise ValueError("Missing artifact inventory")
    for name, expected in receipt["artifacts"].items():
        if file_hash(contained(path.parent, name)) != expected:
            raise ValueError("Output digest mismatch")
    return receipt


def validate_receipt(path, root):
    """Check a successful normal-user receipt and every recorded output digest."""
    receipt = validate_integrity(path)
    validate_status(receipt)
    source = source_snapshot(root)
    if receipt.get("source_before") != source or receipt.get("source_after") != source:
        raise ValueError("Stale or changed source fingerprint")
    if not receipt.get("artifacts"):
        raise ValueError("Missing command outputs")
    return receipt


def validate_cases(entry, evidence, artifacts):
    """Require selected concrete JUnit cases with no skipped/error/failure outcome."""
    cases = entry.get("cases", [])
    if not cases:
        raise ValueError("No concrete case evidence")
    for case in cases:
        if case["junit"] not in artifacts:
            raise ValueError("JUnit file has no artifact digest")
        tree = ET.parse(contained(evidence, case["junit"]))
        matches = [node for node in tree.iter("testcase")
                   if node.get("classname", "") + "::" + node.get("name", "") == case["nodeid"]]
        if len(matches) != 1:
            raise ValueError("Missing, duplicate or non-pass required case: " + case["nodeid"])
        if any(child.tag in {"failure", "error", "skipped"} for child in matches[0]):
            raise ValueError("Non-pass required case: " + case["nodeid"])


def validate_artifacts(entry, evidence):
    """Check all artifact paths and bytes before examining their meaning."""
    artifacts = {}
    for artifact in entry.get("artifacts", []):
        if file_hash(contained(evidence, artifact["path"])) != artifact["sha256"]:
            raise ValueError("Evidence digest mismatch")
        artifacts[artifact["path"]] = artifact["sha256"]
    if not artifacts:
        raise ValueError("No digested evidence artifacts")
    return artifacts


def verify_preview(evidence, root):
    """Use the existing Archify verifier for the approved document binding."""
    slug = evidence.name
    spec = root / "docs/tdq/spec" / (slug + ".md")
    manifest = spec.with_name(slug + "-preview.manifest.json")
    command = [sys.executable, "-X", "utf8", str(root / "scripts/tdq_archify.py"),
               "verify", "--document", str(spec), "--manifest", str(manifest),
               "--project", str(root)]
    result = subprocess.run(command, cwd=root, capture_output=True, timeout=120)
    if result.returncode:
        raise ValueError("Archify preview binding verification failed")
    return {"check": "preview", "status": "BINDING_VERIFIED"}



BASELINE_SHA = "ba31b3b2df65709a2096d0430b95481d886a24509f57abe822e1ef5778eacd00"
MODULES = {
    "D1": ["test_tdq_test_manifest.py", "test_tdq_test_result.py"],
    "D2": ["test_skill_tokens.py"],
    "D3": ["test_tdq_test_process.py"],
    "D4": ["test_tdq_test.py", "test_tdq_runner_integration.py"],
    "D5": ["test_tdq_test_receipt.py", "test_tdq_runner_integration.py"],
    "D6": ["test_tdq_test_receipt.py"],
    "D7": ["test_tdq_readiness.py"],
    "D8": ["test_transcript_cache.py"],
}
TOKENIZER = [
    "KhungTest::test_log_bat_mac_dinh_va_tat_duoc",
    "DoTheoPhaseTest::test_in_du_sau_khoi_va_thoat_0",
    "DoTheoPhaseTest::test_khai_ro_la_tran_tren_chu_khong_phai_so_that",
    "DoMoTaTest::test_so_skill_khop_dung_skill_inventory",
    "DoMoTaTest::test_bang_co_ca_cot_token_va_cot_muc",
    "DoMoTaTest::test_token_chi_giu_ten_luon_nho_hon_token_mo_ta",
]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def bound_file(record, root):
    path = contained(root, record["path"])
    require(file_hash(path) == record["sha256"], "Artifact changed: " + str(path))
    return path


def product_modules(root):
    # Load only trusted project code, never a module path supplied by the index.
    scripts = str(root / "scripts")
    if scripts not in sys.path:
        sys.path.insert(0, scripts)
    return importlib.import_module("tdq_test_manifest"), importlib.import_module("tdq_test_result")


def verify_full(index, evidence, root):
    receipt_path = contained(evidence, index["full_receipt"])
    receipt = validate_receipt(receipt_path, root)
    command = receipt["command"]
    require(any(Path(arg).name == "tdq_test.py" for arg in command), "Full must use production runner")
    require("tron-bo" in command, "Command is not the Full runner entrypoint")
    require("--fresh" in command and "--reuse" in command, "Full must explicitly use fresh/off")
    require(command[command.index("--reuse") + 1] == "off", "Full reuse must be off")
    output = (receipt_path.parent / "stdout.txt").read_text(encoding="utf-8")
    markers = [line[len("TDQ_RESULT "):] for line in output.splitlines() if line.startswith("TDQ_RESULT ")]
    require(len(markers) == 1, "Missing or ambiguous TDQ_RESULT binding")
    result = json.loads(bound_file(json.loads(markers[0]), root).read_text(encoding="utf-8"))
    validate_full_payload(result, root)
    return result


def execution_files(result, root):
    files = {}
    require(bool(result.get("evidence")), "Missing result evidence")
    for record in result["evidence"].values():
        path = bound_file(record, root)
        require(path.name not in files, "Duplicate evidence basename")
        files[path.name] = path
    return files


def validate_full_payload(result, root):
    require(result.get("action") == "executed", "Final Full was not freshly executed")
    before = result.get("source_before")
    require(before and before == result.get("source_after"), "Full source changed")
    require(result.get("status") == "PASS" and result.get("exit_code") == 0, "Full failed")
    require(result.get("manifest", {}).get("scope") == "full", "Selected scope is not Full")
    files = execution_files(result, root)
    manifest_module, result_module = product_modules(root)
    sidecar = manifest_module.load_run_evidence(files["execution.json"])
    require(sidecar["manifest"] == result["manifest"], "Manifest differs from raw sidecar")
    require(sidecar["outcomes"] == result["case_outcomes"], "Case outcomes differ from raw sidecar")
    inventory = sorted({node.split("::")[0] for node in result["manifest"]["case_ids"]})
    parsed = result_module.from_junit_xml(files["execution.xml"].read_text(encoding="utf-8"),
        sidecar["exit_code"], inventory, manifest=sidecar["manifest"],
        outcomes=sidecar["outcomes"], completed=sidecar["completed"])
    require(parsed["status"] == "PASS" and parsed["details_complete"], "Raw XML/sidecar does not prove PASS")
    require(parsed["coverage"] == result["coverage"], "Coverage differs from recomputed evidence")
    require(parsed["coverage"]["complete"], "Case coverage incomplete")
    validate_skips(sidecar["outcomes"])


def validate_skips(outcomes):
    for case in outcomes:
        if case["outcome"] == "skip":
            require(bool(case.get("reason")) and bool(case.get("capability")),
                    "Skip lacks capability/reason: " + case["case_id"])


def declared_cases(path, relative):
    tree = ast.parse(path.read_text(encoding="utf-8-sig"))
    names = []
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith("test_"):
            names.append(relative + "::" + node.name)
        if isinstance(node, ast.ClassDef):
            names.extend(relative + "::" + node.name + "::" + child.name for child in node.body
                         if isinstance(child, ast.FunctionDef) and child.name.startswith("test_"))
    require(bool(names), "No declared regression assertions: " + relative)
    return names


def require_pass(case):
    require(case["outcome"] == "pass", "Required case did not PASS: " + case["case_id"])
    require(any(phase.get("phase") == "call" and phase.get("outcome") == "pass"
                for phase in case["phases"]), "Required assertion never ran: " + case["case_id"])


def verify_regressions(check, result, root):
    outcomes = {case["case_id"]: case for case in result["case_outcomes"]}
    required = []
    for name in MODULES[check]:
        relative = "tests/" + name
        required.extend(declared_cases(root / relative, relative))
    if check == "D2":
        required.extend("tests/test_skill_tokens.py::" + name for name in TOKENIZER)
    for prefix in required:
        cases = [case for name, case in outcomes.items() if name == prefix or name.startswith(prefix + "[")]
        require(bool(cases), "Required regression missing: " + prefix)
        for case in cases:
            if prefix.endswith("::test_posix_process_group_cleanup") and sys.platform == "win32":
                require(case["outcome"] in {"pass", "skip"}, "POSIX limitation not explicit")
            else:
                require_pass(case)
    return len(required)


def verify_baseline(index, result, root):
    path = bound_file(index["baseline"], root)
    require(file_hash(path) == BASELINE_SHA, "Baseline is not the reviewed original inventory")
    baseline = json.loads(path.read_text(encoding="utf-8"))["pytest_items"]
    old = {case["nodeid"] for case in baseline}
    require(len(old) == 3306 and len(baseline) == 3306, "Baseline must contain 3306 unique cases")
    current = set(result["manifest"]["case_ids"])
    remaps = index.get("remaps", [])
    require(len({item["old"] for item in remaps}) == len(remaps), "Duplicate remap")
    require(len({item["new"] for item in remaps}) == len(remaps), "Many-to-one baseline remap loses assertions")
    mapped = {item["old"]: item for item in remaps}
    require(set(mapped) == old - current, "Missing or unnecessary explicit baseline remaps")
    for item in remaps:
        require(item.get("reason") and item.get("new") in current, "Invalid baseline remap")
        require_pass(next(case for case in result["case_outcomes"] if case["case_id"] == item["new"]))
    return {"baseline_cases": 3306, "current_cases": len(current), "remapped": len(remaps)}


def verify_benchmark(entry, root, kind, expected_source=None):
    path = bound_file(entry["benchmark"], root)
    raw = json.loads(path.read_text(encoding="utf-8"))
    require(raw.get("schema") == "tdq-runtime-bench/v1" and raw.get("kind") == kind,
            "Wrong semantic benchmark kind/schema")
    require(isinstance(raw.get("samples"), list) and bool(raw["samples"]), "Benchmark has no raw samples")
    require(expected_source is not None, "Benchmark requires current Full source binding")
    product_modules(root)
    module = importlib.import_module("tdq_runtime_bench")
    checked = module.verify_report(path, expected_source=expected_source)
    require(checked.get("valid") is True and not checked.get("errors"), "Benchmark verifier rejected evidence")
    require(checked.get("verdict") in {"PERFORMANCE_MET", "FALLBACK_RECORDED"}, "Invalid benchmark verdict")
    return checked


def verify_qc(entry, root):
    qc = json.loads(bound_file(entry["qc"], root).read_text(encoding="utf-8"))
    require(qc.get("source_sha256") == source_snapshot(root)["sha256"], "QC source stale")
    require(qc.get("reviewer") and qc["reviewer"] not in qc.get("implementers", []), "QC not independent")
    require(bool(qc.get("implementers")) and qc.get("verdict") == "PASS", "Missing QC identity/verdict")
    report = bound_file(qc["report"], root).read_text(encoding="utf-8")
    require(qc["reviewer"] in report and qc["source_sha256"] in report and "PASS" in report,
            "QC report does not bind reviewer/source/verdict")
    require(isinstance(qc.get("findings"), list), "Missing QC findings")
    for finding in qc["findings"]:
        require(finding.get("resolution") and finding.get("status") == "resolved", "Unresolved QC finding")
        bound_file(finding["evidence"], root)
    return qc["reviewer"]


class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids, self.links, self.text = set(), [], []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if "id" in attrs:
            self.ids.add(attrs["id"])
        if tag == "a" and attrs.get("href"):
            self.links.append(attrs["href"])

    def handle_data(self, data):
        self.text.append(data)


def read_page(path):
    page = Page()
    page.feed(path.read_text(encoding="utf-8"))
    return page


def verify_links(path, page, root):
    require(bool(page.links), "HTML has no evidence links")
    for link in page.links:
        url = urlsplit(link)
        if url.scheme in {"https", "http", "mailto"}:
            continue
        require(not url.scheme and not url.netloc, "Unsupported local link")
        target = contained(root, str((path.parent / unquote(url.path)).resolve())) if url.path else path
        require(target.is_file(), "Broken local link: " + link)
        if url.fragment:
            require(target.suffix.lower() in {".html", ".htm"}, "Unverifiable local anchor")
            require(unquote(url.fragment) in read_page(target).ids, "Broken HTML anchor: " + link)


def verify_browser(record, html, root):
    browser = json.loads(bound_file(record, root).read_text(encoding="utf-8"))
    require(browser.get("html_sha256") == file_hash(html), "Browser viewed stale HTML")
    require(browser.get("tool") and browser.get("session_id"), "Missing browser provenance")
    views = browser.get("views", [])
    require({view.get("name") for view in views} == {"desktop", "mobile"}, "Both viewports required")
    for view in views:
        screenshot = bound_file(view["screenshot"], root).read_bytes()
        require(screenshot[:8] == b"\x89PNG\r\n\x1a\n", "Browser screenshot is not PNG")
        width, height = struct.unpack(">II", screenshot[16:24])
        require(width > 0 and height > 0, "Empty screenshot")
        observation = json.loads(bound_file(view["observation"], root).read_text(encoding="utf-8"))
        require(observation.get("html_sha256") == file_hash(html), "DOM observation is stale")
        require(observation["viewport"]["width"] == view["viewport"]["width"], "Viewport evidence mismatch")
        require(observation["scroll_width"] <= observation["client_width"], "Horizontal overflow")
        require(observation.get("console_errors") == [], "Browser console errors")
        viewport = view["viewport"]["width"]
        require(width >= viewport and height >= view["viewport"]["height"], "Screenshot smaller than observed viewport")
        require((viewport >= 1000) if view["name"] == "desktop" else (320 <= viewport <= 480), "Wrong viewport")


def verify_report(entry, root):
    html, markdown = bound_file(entry["html"], root), bound_file(entry["markdown"], root)
    page = read_page(html)
    md = markdown.read_text(encoding="utf-8")
    text = " ".join(page.text)
    for section in ("results", "raw-samples", "limitations", "before-after", "recommendations", "rollback"):
        require(section in page.ids and "<!-- " + section + " -->" in md, "Missing report section: " + section)
    require("--fresh" in text and "--reuse off" in text and "--workers 1" in text, "Missing concrete rollback")
    require(bool(entry.get("numbers")), "No numeric evidence bindings")
    for number in entry["numbers"]:
        raw = json.loads(bound_file(number["source"], root).read_text(encoding="utf-8"))
        value = raw
        for part in number["pointer"].split("/")[1:]:
            value = value[int(part)] if isinstance(value, list) else value[part]
        require(type(value) in {int, float}, "Report pointer is not numeric")
        require(str(value) in text and str(value) in md, "Report number differs from evidence")
    verify_links(html, page, root)
    verify_browser(entry["browser"], html, root)
    return {"local_links": len(page.links), "numeric_bindings": len(entry["numbers"])}


def verify(check, evidence, root):
    if check == "preview":
        return verify_preview(evidence, root)
    index = json.loads((evidence / "evidence-index.json").read_text(encoding="utf-8"))
    require(index.get("schema") == "tdq-evidence-index/v2", "Semantic index v2 required")
    if check == "report":
        check = "D12"
    if check in MODULES:
        result = verify_full(index, evidence, root)
        details = {"required_assertions": verify_regressions(check, result, root)}
        if check == "D1":
            details.update(verify_baseline(index, result, root))
    else:
        entry = index["checks"][check]
        full = verify_full(index, evidence, root)
        if check == "D12":
            allowed = []
            for benchmark_check, kind in (("D9", "full-pairs"), ("D10", "cache-pairs")):
                benchmark = index["checks"][benchmark_check]
                verify_benchmark(benchmark, root, kind, full["source_before"])
                allowed.append(bound_file(benchmark["benchmark"], root))
            for number in entry.get("numbers", []):
                require(bound_file(number["source"], root) in allowed, "Report number lacks verified benchmark source")
            details = verify_report(entry, root)
        else:
            kind = {"D9": "full-pairs", "D10": "cache-pairs", "D11": "runtime-smoke"}[check]
            details = verify_benchmark(entry, root, kind, full["source_before"])
            if check == "D11":
                details["reviewer"] = verify_qc(entry, root)
    return {"check": check, "status": "PASS", "details": details}


def simulated_full(root):
    manifest_module, result_module = product_modules(Path(__file__).resolve().parents[4])
    identifier = "tests/test_simulation.py::test_example"
    manifest = manifest_module.make_manifest([identifier], scope="full")
    case = {"case_id": identifier, "outcome": "pass", "reason": "", "capability": "",
            "subtests": [], "phases": [{"phase": phase, "outcome": "pass", "reason": "",
            "duration_seconds": 0.01} for phase in ("setup", "call", "teardown")]}
    xml = '<testsuite tests="1" failures="0" errors="0" skipped="0"><testcase classname="tests.test_simulation" name="test_example"/></testsuite>'
    result = result_module.from_junit_xml(xml, 0, ["tests/test_simulation.py"], manifest=manifest,
                                        outcomes=[case], completed=True)
    sidecar = {"schema_version": 1, "manifest": manifest, "outcomes": [case], "completed": True, "exit_code": 0}
    (root / "execution.json").write_text(json.dumps(sidecar), encoding="utf-8")
    (root / "execution.xml").write_text(xml, encoding="utf-8")
    result.update(action="executed", source_before={"key": "simulation"}, source_after={"key": "simulation"})
    result["evidence"] = {name: {"path": name, "sha256": file_hash(root / name)}
                          for name in ("execution.json", "execution.xml")}
    return result


def self_test():
    # Synthetic fixtures exercise validators, never attest this request's DoD.
    checks = []
    def rejected(name, action):
        try:
            action()
        except (ValueError, KeyError, OSError, ImportError):
            checks.append(name)
        else:
            raise AssertionError("False PASS: " + name)
    case = {"case_id": "fixture::test_x", "outcome": "pass", "phases": [{"phase": "call", "outcome": "pass"}]}
    require_pass(case)
    rejected("failed_required_case", lambda: require_pass(dict(case, outcome="fail")))
    rejected("assertion_never_ran", lambda: require_pass(dict(case, phases=[])))
    with tempfile.TemporaryDirectory(prefix="tdq-semantic-") as temporary:
        root = Path(temporary)
        full = simulated_full(root)
        validate_full_payload(full, root)
        checks.append("synthetic_full_sidecar_xml_accepted")
        rejected("forged_case_outcomes", lambda: validate_full_payload(dict(full, case_outcomes=[]), root))
        rejected("forged_coverage", lambda: validate_full_payload(dict(full, coverage={"complete": True}), root))
        (root / "tests").mkdir()
        (root / "tests/test_skill_tokens.py").write_text("def test_expected(): pass", encoding="utf-8")
        rejected("missing_required_case", lambda: verify_regressions("D2", {"case_outcomes": [case]}, root))
        payload = {"action": "executed", "source_before": {"key": "a"}, "source_after": {"key": "b"}}
        rejected("changed_source", lambda: validate_full_payload(payload, root))
        fake = root / "fake.json"
        fake.write_text(json.dumps({"schema": "tdq-runtime-bench/v1", "kind": "cache-pairs", "valid": True}))
        rejected("forged_benchmark_kind", lambda: verify_benchmark({"benchmark": {"path": "fake.json", "sha256": file_hash(fake)}}, root, "full-pairs"))
        rejected("forged_semantic_benchmark", lambda: verify_benchmark({"benchmark": {"path": "fake.json", "sha256": file_hash(fake)}}, root, "cache-pairs"))
        rejected("missing_browser", lambda: verify_browser({"path": "missing.json", "sha256": "x"}, fake, root))
        html = root / "report.html"
        html.write_text('<a href="#absent">broken</a>', encoding="utf-8")
        rejected("broken_anchor", lambda: verify_links(html, read_page(html), root))
        record = {"path": "fake.json", "sha256": file_hash(fake)}
        fake.write_text("{}", encoding="utf-8")
        rejected("mutated_artifact", lambda: bound_file(record, root))
    return {"status": "PASS", "simulation_only": True, "checks": checks}


def main():
    parser = argparse.ArgumentParser(description="Semantic DoD verifier; missing evidence fails closed")
    parser.add_argument("check", nargs="?", choices=["D" + str(i) for i in range(1, 13)] + ["preview", "report"])
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--project", type=Path, default=Path.cwd())
    parser.add_argument("--evidence-dir", type=Path, default=Path(__file__).resolve().parent)
    arguments = parser.parse_args()
    try:
        require(arguments.self_test or arguments.check, "Check or --self-test required")
        result = self_test() if arguments.self_test else verify(arguments.check, arguments.evidence_dir.resolve(), arguments.project.resolve())
    except (OSError, ValueError, KeyError, ImportError, TypeError, ET.ParseError) as error:
        print(json.dumps({"check": arguments.check, "status": "FAIL", "reason": str(error)}))
        return 1
    print(json.dumps(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
