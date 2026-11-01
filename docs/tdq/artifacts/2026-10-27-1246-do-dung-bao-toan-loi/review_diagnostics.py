"""Read-only diagnostics; production files and test declarations remain unchanged."""
import hashlib
import inspect
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest

A = Path(__file__).resolve().parent
ROOT = A.parents[3]


def token_child():
    sys.path.insert(0, str(ROOT / "tests"))
    import test_skill_tokens as module
    selected = []
    for cls in (module.KhungTest, module.DoTheoPhaseTest, module.DoMoTaTest):
        for name, method in list(vars(cls).items()):
            if name.startswith("test_") and getattr(method, "__unittest_skip__", False):
                original = inspect.unwrap(method)
                assert original is not method
                setattr(cls, name, original)
                selected.append(cls(name))
    assert len(selected) == 6
    result = unittest.TextTestRunner(verbosity=2).run(unittest.TestSuite(selected))
    return 0 if result.wasSuccessful() and not result.skipped else 1


def main():
    if "--token-child" in sys.argv:
        return token_child()
    config = Path.home() / ".claude" / "CLAUDE.md"
    before = hashlib.sha256(config.read_bytes()).hexdigest()
    results = []
    with tempfile.TemporaryDirectory(prefix="tdq-review-diagnostics-") as tmp:
        home = Path(tmp) / "home"
        home.mkdir()
        env = dict(os.environ, HOME=str(home), USERPROFILE=str(home),
                   TDQ_KHONG_CHAM_MAY="1", TDQ_KHOI_TAO_NEN="0")
        commands = [
            ("parallel-no-tmpdir", [sys.executable, "-m", "pytest", "-n", "2", "-p", "no:tmpdir",
             "-p", "no:cacheprovider", "-q", "--tb=short", "--junitxml=" + str(A / "review-parallel-no-tmpdir.xml"),
             "tests/test_archify_artifacts.py::test_document_digest_basic"], 60),
            ("parallel-with-tmpdir", [sys.executable, "-m", "pytest", "-n", "2", "-p", "no:cacheprovider",
             "--basetemp=" + str(Path(tmp) / "pytest"), "-q", "--tb=short",
             "--junitxml=" + str(A / "review-parallel-with-tmpdir.xml"),
             "tests/test_archify_artifacts.py::test_document_digest_basic"], 60),
            ("tokenizer-available", [str(ROOT / ".venv-tokens" / "Scripts" / "python.exe"),
             "-c", "import anthropic_tokenizer; print('tokenizer import OK')"], 60),
            ("tokenizer-six-assertions", [sys.executable, "-X", "utf8", str(Path(__file__).resolve()), "--token-child"], 300),
        ]
        for label, command, timeout in commands:
            start = time.perf_counter()
            with (A / ("review-" + label + ".stdout.txt")).open("wb") as out, (A / ("review-" + label + ".stderr.txt")).open("wb") as err:
                process = subprocess.run(command, cwd=ROOT, env=env, stdout=out, stderr=err, timeout=timeout)
            results.append({"label": label, "command": command, "exit_code": process.returncode,
                            "seconds": round(time.perf_counter() - start, 3)})
            print(json.dumps(results[-1]), flush=True)
    report = {"results": results, "real_user_config_unchanged": hashlib.sha256(config.read_bytes()).hexdigest() == before,
              "scope": "Diagnostic commands only; bounded workers instead of auto; skip decorators unwrapped in memory only for six tokenizer assertions"}
    (A / "review-diagnostics.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return 0 if report["real_user_config_unchanged"] else 1


if __name__ == "__main__":
    sys.exit(main())
