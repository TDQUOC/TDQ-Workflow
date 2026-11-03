$ErrorActionPreference = 'Stop'
$root = 'C:\Users\admin\Documents\Projects\ForAgentCode\TDQ-Workflow'
Set-Location $root
$env:ARCHIFY_UPDATE_CHECK_DISABLED = '1'
$env:ARCHIFY_ROOT = 'C:\Users\admin\Documents\archify'
$log = Join-Path $root 'docs\tdq\ba-runtime-preview.log'
& 'C:\Users\admin\AppData\Local\Programs\Python\Python313\python.exe' scripts/tdq_archify.py render --type workflow --candidate tests/fixtures/archify/workflow.json --out docs/tdq/ba-runtime-preview.html --quality standard | Out-File $log -Encoding utf8
('ExitCode=' + $LASTEXITCODE) | Out-File $log -Append -Encoding utf8
