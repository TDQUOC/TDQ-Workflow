"""Observe actual process launches and calibration rounds; never replace them."""
import json
import os
import re
import sys


def record(kind, program=None):
    case = os.environ.get("TDQ_SCOPE_ACTIVE_CASE")
    path = os.environ.get("TDQ_SCOPE_WORK_LOG")
    if not case or not path:
        return
    row = {"case_id": case, "pid": os.getpid(), "kind": kind}
    if program is not None:
        row["program"] = program
    with open(path, "a", encoding="utf-8") as stream:
        stream.write(json.dumps(row) + "\n")


def audit(event, args):
    if event == "subprocess.Popen":
        argv = args[1]
        if isinstance(argv, (list, tuple)):
            executable = argv[0]
        else:
            first = re.match(r'^\s*(?:"([^"]*)"|(\S+))', os.fsdecode(argv))
            executable = first.group(1) or first.group(2)
        program = os.path.basename(os.fsdecode(executable)).lower()
        record("git" if program in {"git", "git.exe", "git.cmd"} else "process", program)


def profile(frame, event, _arg):
    if event == "call" and frame.f_code.co_name == "_do_mot_luot":
        if os.path.basename(frame.f_code.co_filename) == "tdq_bench.py":
            record("calibration")


sys.addaudithook(audit)
sys.setprofile(profile)
