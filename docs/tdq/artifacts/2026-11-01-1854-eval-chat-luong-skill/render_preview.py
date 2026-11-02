"""Build the planned spec preview as a normal user; this is not a test receipt."""
import argparse
import importlib.util
import json
from pathlib import Path
import sys
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
SLUG = HERE.name
POLICY_PATH = ROOT / "docs/tdq/artifacts/2026-11-01-1045-toi-uu-bon-hang-muc/safe_run_telemetry.py"
spec = importlib.util.spec_from_file_location("_preview_dispatch", POLICY_PATH)
policy = importlib.util.module_from_spec(spec)
spec.loader.exec_module(policy)
sys.path.insert(0, str(ROOT / "scripts"))
from tdq_test_process import OwnedProcessJob

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dispatch-reply", type=Path)
    args = parser.parse_args()
    output = HERE / "preview-render"
    output.mkdir(exist_ok=True)
    if policy.legacy.elevated() and args.dispatch_reply is None:
        with patch.object(policy.legacy, "__file__", str(Path(__file__).resolve())):
            return policy.legacy.normal_dispatch([], output, 180)
    if policy.legacy.elevated():
        raise RuntimeError("Normal-user preview render required")
    command = [sys.executable, "-X", "utf8", str(ROOT / "scripts/tdq_archify.py"),
        "render", "--type", "workflow", "--candidate", str(HERE / "candidate.json"),
        "--out", str(ROOT / "docs/tdq/spec" / (SLUG + "-preview.html")),
        "--document", str(ROOT / "docs/tdq/spec" / (SLUG + ".md")),
        "--repo-root", str(ROOT), "--request", SLUG, "--lane", "full", "--evidence-kind", "planned"]
    with OwnedProcessJob(ROOT, timeout_seconds=180, env={
            "ARCHIFY_CHROME": "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe",
            "TDQ_KHONG_CHAM_MAY": "1", "TDQ_KHOI_TAO_NEN": "0"}) as job:
        result = job.run(command, phase="spec-preview-render")
    (output / "stdout.txt").write_text(result.pop("stdout"), encoding="utf-8")
    (output / "stderr.txt").write_text(result.pop("stderr"), encoding="utf-8")
    record = {"kind": "planned-preview-build-not-test-certification", "elevated": False,
              "command": command, "process": result}
    policy.legacy.write_json(output / "build.json", record)
    code = 0 if result["exit_code"] == 0 and result["cleanup_complete"] else 1
    if args.dispatch_reply:
        policy.legacy.write_json(args.dispatch_reply, {"exit_code": code, "elevated": False,
            "record": str(output / "build.json")})
    print(json.dumps({"exit_code": code, "record": str(output / "build.json")}))
    return code

if __name__ == "__main__":
    raise SystemExit(main())
