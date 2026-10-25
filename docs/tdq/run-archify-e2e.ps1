$ErrorActionPreference = 'Stop'
$root = 'C:\Users\admin\Documents\Projects\ForAgentCode\TDQ-Workflow'
Set-Location $root
$env:ARCHIFY_UPDATE_CHECK_DISABLED = '1'
$env:ARCHIFY_ROOT = 'C:\Users\admin\Documents\archify'
$log = Join-Path $root 'docs\tdq\archify-e2e.log'
$principal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
('Elevated=' + $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) | Out-File $log -Encoding utf8
& 'C:\Users\admin\AppData\Local\Programs\Python\Python313\python.exe' -m pytest tests/test_archify_e2e.py -q --tb=short | Out-File $log -Append -Encoding utf8
('ExitCode=' + $LASTEXITCODE) | Out-File $log -Append -Encoding utf8
