import json,os,subprocess,sys,time
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
