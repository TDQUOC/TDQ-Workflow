"""Bounded current-source runtime probes; workload fixtures never call a provider."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import runpy
import subprocess
import sys
import time
import uuid

EVIDENCE = Path(__file__).resolve().parent
ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "scripts"))
NAMES = ("calibration-valid", "reject-early", "timeout-cleanup", "report-offline")
EXPECTED_SOURCE = "6f03e5bec06c11ed1bc7d9c14609d09ce9f3b55f2fc0b069057c80cce97543bc"
EXPECTED_INPUT = "ec60b7816e0f7efc06f5b4784e3fd3f5c3ea0adf604ddbbeaac8cff700e7d7d2"
EXPECTED_FULL_RECEIPT = "af40162d77cec49688bdd0f1c161d6ec66bd61bb89c7e7584571a89eb08e4d63"


def write_json(path, value):
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def binding(path):
    path = Path(path).resolve()
    return {"path": path.relative_to(ROOT).as_posix(),
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}


def current_source(adapter, folder):
    """Rehash Full's inventory; outer harness guards the live Git inventory too."""
    receipt = EVIDENCE / "runs/QC-F1-final-a114787b746743078d2bfb03a7fdfab9/receipt.json"
    require(binding(receipt)["sha256"] == EXPECTED_FULL_RECEIPT, "Full receipt digest differs")
    full = adapter.validate_receipt(receipt, ROOT, current=False)["source_before"]
    legacy = adapter.legacy
    current = {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
               if (ROOT / name).is_file() else "MISSING" for name in full["files"]}
    require(legacy.digest(current) == full["sha256"] == EXPECTED_SOURCE, "Frozen source bytes differ")
    child = legacy.source_snapshot(ROOT)
    differences = [name for name in sorted(set(child["files"]) | set(current))
                   if child["files"].get(name) != current.get(name)]
    write_json(folder / "source-inventory.json", {
        "full_receipt": binding(receipt), "source_sha256": legacy.digest(current),
        "child_git_inventory_sha256": child["sha256"], "child_inventory_different_paths": differences,
        "method": "rehash every Full inventory entry; outer guarded receipt checks current Git inventory"})
    return legacy.digest(current)


def require(value, reason):
    if not value:
        raise RuntimeError(reason)


def observe(path):
    """Observe entry/launch events, with a positive marker even for zero work."""
    captured_plans = []
    def record(kind, name=None):
        with path.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps({"pid": os.getpid(), "kind": kind, "name": name}) + "\n")

    def profile(frame, event, _arg):
        if (event == "return" and frame.f_code.co_name == "_dung_repo_tam"
                and Path(frame.f_code.co_filename).name == "tdq_bench.py"
                and _arg is not None):
            repo, relative = _arg
            plan = path.parent / ("sample-plan-" + str(len(captured_plans) + 1) + ".md")
            plan.write_bytes((Path(repo) / relative).read_bytes())
            captured_plans.append(plan)
            record("sample-plan-captured", plan.name)
        if event != "call":
            return
        name, file = frame.f_code.co_name, Path(frame.f_code.co_filename).name
        if file == "tdq_bench.py" and name == "_do_mot_luot":
            record("measurement", name)
        if file == "tdq_test.py" and name in {"chay_tron_bo_result", "_run_pytest", "_run_phase"}:
            record("runner", name)

    def audit(event, args):
        if event == "subprocess.Popen":
            # Windows audit events may have executable=None; do not parse payload argv.
            record("process", "subprocess.Popen")

    path.write_text("", encoding="utf-8")
    sys.addaudithook(audit)
    sys.setprofile(profile)
    record("observer-start", "profile+audit")


def invoke(script, arguments):
    previous = sys.argv
    sys.argv = [str(ROOT / "scripts" / script), *arguments]
    try:
        try:
            runpy.run_path(sys.argv[0], run_name="__main__")
        except SystemExit as error:
            return error.code if type(error.code) is int else (0 if error.code is None else 1)
        return 0
    finally:
        sys.argv = previous


def timeout_probe(folder):
    import tdq_codex
    import tdq_test_process as process
    import tdq_test_receipt as receipts

    require(os.name == "nt", "This runtime fixture requires Windows .cmd ownership")
    fixture = folder / "fixture-codex.py"
    record_path = folder / "ready.json"
    fixture.write_text('''import json,os,subprocess,sys,time
from pathlib import Path
if sys.argv[1:] == ["--version"]:
    print("fixture-codex 1.0",flush=True)
    raise SystemExit(0)
child=subprocess.Popen([sys.executable,"-c","import time;time.sleep(90)"])
home=os.environ["CODEX_HOME"]
record={"pid":os.getpid(),"descendant_pid":child.pid,"descendant_alive_at_ready":child.poll() is None,
        "home":home,"home_existed_at_ready":Path(home).is_dir(),
        "caller_home":os.environ.get("HOME"),"caller_userprofile":os.environ.get("USERPROFILE")}
path=Path(__file__).with_name("ready.json")
temporary=path.with_suffix(".tmp")
temporary.write_text(json.dumps(record),encoding="utf-8")
os.replace(temporary,path)
print("fixture descendant ready",flush=True)
time.sleep(90)
''', encoding="utf-8")
    wrapper = folder / "fixture-codex.cmd"
    wrapper.write_bytes(('@"%s" "%s" %%*\r\n' % (sys.executable, fixture)).encode("utf-8"))
    caller = folder / "caller"
    caller.mkdir()
    control_home = folder / "unrelated-home"
    control_home.mkdir()
    marker = control_home / "marker.txt"
    marker.write_text("unrelated job sentinel", encoding="utf-8")
    control = subprocess.Popen([sys.executable, "-c", "import time;time.sleep(90)"],
                               stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                               stderr=subprocess.DEVNULL)

    def unrelated():
        return {"pid": control.pid, "identity": receipts._process_identity(control.pid),
                "alive": control.poll() is None, "home_exists": control_home.is_dir(),
                "marker_sha256": binding(marker)["sha256"]}

    before = unrelated()
    try:
        started = time.monotonic()
        alive, version, reason = tdq_codex._kiem_song(str(wrapper), str(caller), "fixture-only", timeout=2)
        elapsed = time.monotonic() - started
        require(record_path.is_file(), "Missing live descendant handshake")
        record = json.loads(record_path.read_text(encoding="utf-8"))
        descendants = [record["pid"], record["descendant_pid"]]
        remaining = [pid for pid in descendants if process._windows_pid_alive(pid)]
        after = unrelated()
        facts = {"timeout_seconds": 2, "call_elapsed_seconds": elapsed,
                 "ready_observed": record["descendant_alive_at_ready"],
                 "descendants_observed": descendants, "descendants_alive_after": remaining,
                 "home_existed_before": record["home_existed_at_ready"],
                 "home_exists_after": Path(record["home"]).exists(),
                 "unrelated_before": before, "unrelated_after": after,
                 "alive_result": alive, "version": version, "reason": reason,
                 "caller_home_preserved": record["caller_home"] == os.environ.get("HOME"),
                 "caller_userprofile_preserved": record["caller_userprofile"] == os.environ.get("USERPROFILE")}
        require(not alive and "quá hạn" in reason and elapsed <= 8, "Timeout contract failed")
        require(not remaining and before == after and before["alive"], "Owned/unrelated process contract failed")
        require(facts["ready_observed"] and facts["home_existed_before"] and not facts["home_exists_after"], "HOME/handshake contract failed")
        require(facts["caller_home_preserved"] and facts["caller_userprofile_preserved"], "Caller HOME changed")
        return facts
    finally:
        control.terminate()
        control.wait(timeout=5)


def probe(name, folder):
    events_path = folder / "observer.jsonl"
    observe(events_path)
    if name in {"calibration-valid", "reject-early"}:
        output = folder / "measurement.json"
        if name == "calibration-valid" and os.name == "nt":
            # The existing sample-plan workload is shell `true`; cmd has no builtin.
            # Supply the same local portable command fixture used by test_bench.
            command_folder = folder / "fixture-bin"
            command_folder.mkdir()
            (command_folder / "true.cmd").write_bytes(
                ('@"%s" -c "pass"\r\n' % sys.executable).encode("utf-8"))
            os.environ["PATH"] = str(command_folder) + os.pathsep + os.environ.get("PATH", "")
        samples = "" if name == "calibration-valid" else "t_phat=1,t_phat=2"
        args = ["calibrate", "--task", "1", "--lap", "3", "--ra", str(output)]
        if samples:
            args += ["--mau-that", samples]
        before = set(folder.iterdir())
        exit_code = invoke("tdq_bench.py", args)
        rows = [json.loads(line) for line in events_path.read_text(encoding="utf-8").splitlines()]
        facts = {"measurement_calls": sum(row["kind"] == "measurement" for row in rows),
                 "command_exit_code": exit_code, "output_exists": output.is_file(),
                 "new_output_files": sorted(p.name for p in set(folder.iterdir()) - before)}
        if name == "calibration-valid":
            require(exit_code == 0 and facts["measurement_calls"] > 0 and output.is_file(), "Valid calibration failed")
            facts["sample_plans"] = [binding(path) for path in sorted(folder.glob("sample-plan-*.md"))]
            require(len(facts["sample_plans"]) == facts["measurement_calls"], "Missing observed sample plans")
            data = json.loads(output.read_text(encoding="utf-8"))
            require(all(row["so_mau"] >= 3 for row in data["hang_so"].values()), "Invalid sample counts")
        else:
            require(exit_code != 0 and facts["measurement_calls"] == 0 and facts["new_output_files"] == [], "Rejection performed work")
    elif name == "timeout-cleanup":
        facts = timeout_probe(folder)
    else:
        source = EVIDENCE / "final-result.json"
        input_binding = binding(source)
        require(input_binding["sha256"] == EXPECTED_INPUT, "Full input digest differs")
        exit_code = invoke("tdq_test.py", ["report", "--result", str(source),
                                          "--out-prefix", str(folder / "offline-report.v1")])
        rows = [json.loads(line) for line in events_path.read_text(encoding="utf-8").splitlines()]
        outputs = [folder / ("offline-report.v1" + suffix) for suffix in (".json", ".md", ".html")]
        facts = {"input": input_binding, "input_sha256": binding(source)["sha256"],
                 "runner_calls": sum(row["kind"] == "runner" for row in rows),
                 "outputs": [binding(path) for path in outputs], "command_exit_code": exit_code}
        require(exit_code == 0 and facts["runner_calls"] == 0 and input_binding == binding(source), "Offline report contract failed")
        require(json.loads(source.read_text(encoding="utf-8"))["status"] == "PASS", "Full input is not PASS")
    sys.setprofile(None)
    rows = [json.loads(line) for line in events_path.read_text(encoding="utf-8").splitlines()]
    require(any(row["kind"] == "observer-start" for row in rows), "Observer missing")
    facts["observer_enabled"] = True
    facts["observed_process_calls"] = sum(row["kind"] == "process" for row in rows)
    write_json(folder / "facts.json", facts)
    print("TDQ_RUNTIME_FACTS " + json.dumps(facts), flush=True)
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scenario-timeout", type=float, default=120)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--probe", choices=NAMES)
    parser.add_argument("--folder", type=Path)
    args = parser.parse_args()
    if args.probe:
        return probe(args.probe, args.folder)
    require(args.output is not None and 0 < args.scenario_timeout <= 120, "Output/cap required")
    from tdq_test_process import OwnedProcessJob
    import safe_run_telemetry
    run = EVIDENCE / "runtime-evidence" / uuid.uuid4().hex
    run.mkdir(parents=True)
    helper_snapshot = run / "runtime_checks.executed.py"
    helper_snapshot.write_bytes(Path(__file__).read_bytes())
    source = current_source(safe_run_telemetry, run)
    payload = {"schema": "tdq-optimize-runtime/v1", "source_sha256": source, "scenarios": []}
    for name in NAMES:
        folder = run / name
        folder.mkdir()
        started = time.monotonic()
        with OwnedProcessJob(ROOT, timeout_seconds=args.scenario_timeout) as job:
            result = job.run([sys.executable, "-X", "utf8", str(Path(__file__).resolve()),
                              "--probe", name, "--folder", str(folder)], phase=name)
            (folder / "stdout.txt").write_text(result["stdout"], encoding="utf-8")
            (folder / "stderr.txt").write_text(result["stderr"], encoding="utf-8")
            write_json(folder / "process.json", result)
        elapsed = time.monotonic() - started
        facts = json.loads((folder / "facts.json").read_text(encoding="utf-8")) if (folder / "facts.json").exists() else {}
        row = {"name": name, "classification": "fixture-process" if name in {"timeout-cleanup", "calibration-valid"} else "real-process",
               "elapsed_seconds": elapsed, "deadline_seconds": args.scenario_timeout,
               "exit_code": result["exit_code"],
               "process": {"pid": result["ownership"]["root_pid"],
                           "ownership_verified": result["ownership"]["verified"],
                           "cleanup_complete": result["cleanup_complete"]},
               "facts": facts, "evidence": [binding(helper_snapshot), binding(run / "source-inventory.json")] + [binding(p) for p in sorted(folder.rglob("*")) if p.is_file()]}
        payload["scenarios"].append(row)
        write_json(run / "runtime.json", payload)
        require(result["exit_code"] == 0 and result["cleanup_complete"] and result["ownership"]["verified"], "Scenario failed: " + name)
        require(elapsed <= args.scenario_timeout and (name != "timeout-cleanup" or elapsed <= 8), "Scenario cap exceeded: " + name)
    require(current_source(safe_run_telemetry, run) == source, "Source changed")
    write_json(args.output, payload)
    print("TDQ_SCOPE_RUNTIME " + json.dumps(binding(args.output)), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
