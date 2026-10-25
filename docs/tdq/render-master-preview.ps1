$ErrorActionPreference = 'Stop'
$root = 'C:\Users\admin\Documents\Projects\ForAgentCode\TDQ-Workflow'
Set-Location $root
$env:ARCHIFY_UPDATE_CHECK_DISABLED = '1'
$env:ARCHIFY_ROOT = 'C:\Users\admin\Documents\archify'
& 'C:\Users\admin\AppData\Local\Programs\Python\Python313\python.exe' scripts/tdq_archify.py sync-master --model models/master.json --project docs/tdq/master-demo --out docs/architecture --quality standard | Out-File 'docs/tdq/master-runtime-preview.log' -Encoding utf8
('ExitCode=' + $LASTEXITCODE) | Out-File 'docs/tdq/master-runtime-preview.log' -Append -Encoding utf8
