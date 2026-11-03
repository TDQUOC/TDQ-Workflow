import argparse, ctypes, hashlib, json, os, subprocess, time
from pathlib import Path
from datetime import datetime
p=argparse.ArgumentParser()
p.add_argument("--label",required=True)
p.add_argument("--cwd",default=str(Path.cwd()))
p.add_argument("command",nargs=argparse.REMAINDER)
a=p.parse_args()
cmd=a.command[1:] if a.command[:1]==["--"] else a.command
root=Path("C:/Users/admin/Documents/Projects/ForAgentCode/TDQ-Workflow")
base=root/"docs/tdq/artifacts/2026-10-27-1246-do-dung-bao-toan-loi"
label=a.label
assert label and all(c.isalnum() or c in "-_." for c in label)
started=datetime.now().astimezone().isoformat()
head=subprocess.check_output(["git", "rev-parse", "HEAD"],cwd=a.cwd,text=True).strip()
source_paths=subprocess.check_output(["git", "ls-files", "scripts", "tests", "skills"],cwd=a.cwd,text=True).splitlines()
context={"head":head,"pid":os.getpid(),"elevated":bool(ctypes.windll.shell32.IsUserAnAdmin()) if os.name=="nt" else None,
         "source_sha256":{name:hashlib.sha256((Path(a.cwd)/name).read_bytes()).hexdigest() for name in source_paths if (Path(a.cwd)/name).is_file()},
         "utf8_env":{key:os.environ.get(key) for key in ("PYTHONUTF8","PYTHONIOENCODING")}}
base.joinpath(label+".context.json").write_text(json.dumps(context,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
t=time.perf_counter()
env=dict(os.environ,TDQ_KHONG_CHAM_MAY="1",TDQ_KHOI_TAO_NEN="0")
stdout=base/(label+".stdout.txt")
stderr=base/(label+".stderr.txt")
with stdout.open("wb") as out, stderr.open("wb") as err:
    r=subprocess.run(cmd,cwd=a.cwd,env=env,stdout=out,stderr=err)
receipt={"command":cmd,"cwd":a.cwd,"started_at":started,"seconds":round(time.perf_counter()-t,3),"exit_code":r.returncode,"stdout":stdout.name,"stderr":stderr.name}
base.joinpath(label+".json").write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps(receipt,ensure_ascii=False))
for f in (stdout,stderr):
    s=f.read_text(encoding="utf-8",errors="replace")
    if s: print(s[-3500:])
raise SystemExit(r.returncode)
