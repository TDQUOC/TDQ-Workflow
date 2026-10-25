$ErrorActionPreference = 'Stop'
$root = 'C:\Users\admin\Documents\Projects\ForAgentCode\TDQ-Workflow'
Set-Location $root
$env:ARCHIFY_UPDATE_CHECK_DISABLED = '1'
$env:ARCHIFY_ROOT = 'C:\Users\admin\Documents\archify'
$python = 'C:\Users\admin\AppData\Local\Programs\Python\Python313\python.exe'
$principal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
$metadata = Join-Path $root 'docs\tdq\archify-final-qc-status.log'
('Elevated=' + $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) | Out-File $metadata -Encoding utf8
('Started=' + (Get-Date -Format o)) | Out-File $metadata -Append -Encoding utf8
$p = Start-Process -FilePath $python -ArgumentList 'scripts/tdq_test.py tron-bo' -WorkingDirectory $root -NoNewWindow -PassThru -Wait -RedirectStandardOutput (Join-Path $root 'docs\tdq\archify-final-qc-stdout.log') -RedirectStandardError (Join-Path $root 'docs\tdq\archify-final-qc-stderr.log')
('ExitCode=' + $p.ExitCode) | Out-File $metadata -Append -Encoding utf8
('Finished=' + (Get-Date -Format o)) | Out-File $metadata -Append -Encoding utf8
