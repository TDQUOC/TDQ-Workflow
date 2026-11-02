import os
import re
import sys

sys.path.insert(0, "tests")
from test_luat_skill import BANG, ROOT, doc_bang, luat_con_khong, neo

rows = {code: (path, line, new or old) for code, path, line, old, new in doc_bang()}
cache = {}
out = []
fixed = 0
for raw in open(BANG, encoding="utf-8"):
    match = re.match(r"^\| (L\d+) \| `([^`:]+):(\d+)` \|", raw)
    if match and match.group(1) in rows:
        path, line, anchor = rows[match.group(1)]
        lines = cache.setdefault(path, open(os.path.join(ROOT, path), encoding="utf-8").read().splitlines())
        if not (line - 1 < len(lines) and luat_con_khong(neo(anchor), lines[line - 1])):
            hits = [index + 1 for index, value in enumerate(lines) if luat_con_khong(neo(anchor), value)]
            if len(hits) == 1:
                raw = raw.replace(f"`{path}:{line}`", f"`{path}:{hits[0]}`", 1)
                fixed += 1
    out.append(raw)
with open(BANG, "w", encoding="utf-8", newline="") as stream:
    stream.write("".join(out))
print(fixed)
