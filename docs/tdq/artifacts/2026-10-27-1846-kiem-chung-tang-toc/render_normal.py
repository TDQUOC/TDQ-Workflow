"""Capture the spec preview render at the user's normal Windows integrity level."""
import ctypes
import json
from pathlib import Path
import subprocess
import sys
import time

A = Path(__file__).resolve().parent
ROOT = A.parents[3]
slug = A.name
plugin = Path('C:/Users/admin/.codex/plugins/cache/tdq-local/tdq-workflow/0.84.2')
command = [sys.executable, '-X', 'utf8', str(plugin / 'scripts/tdq_archify.py'), 'render',
           '--type', 'workflow', '--candidate', str(A / 'candidate.json'),
           '--out', str(ROOT / 'docs/tdq/spec' / (slug + '-preview.html')),
           '--document', str(ROOT / 'docs/tdq/spec' / (slug + '.md')),
           '--request', slug, '--lane', 'full', '--evidence-kind', 'planned']
started = time.perf_counter()
with (A / 'preview-normal.stdout.txt').open('wb') as out, (A / 'preview-normal.stderr.txt').open('wb') as err:
    proc = subprocess.run(command, cwd=ROOT, stdout=out, stderr=err, timeout=120)
receipt = {'command': command, 'exit_code': proc.returncode,
           'elevated': bool(ctypes.windll.shell32.IsUserAnAdmin()),
           'seconds': round(time.perf_counter() - started, 3)}
(A / 'preview-normal.json').write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8')
