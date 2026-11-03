$ErrorActionPreference = 'Stop'
$root = 'C:\Users\admin\Documents\Projects\ForAgentCode\TDQ-Workflow'
$log = Join-Path $root 'docs\tdq\native-browser-probe.log'
$identity = [Security.Principal.WindowsIdentity]::GetCurrent()
$principal = New-Object Security.Principal.WindowsPrincipal($identity)
$elevated = $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
('Elevated=' + $elevated) | Out-File -FilePath $log -Encoding utf8
if ($elevated) { 'Probe requires a non-elevated process; no browser launched.' | Out-File -FilePath $log -Append -Encoding utf8; exit 2 }
Set-Location $root
$env:ARCHIFY_UPDATE_CHECK_DISABLED = '1'
$node = 'C:\Users\admin\AppData\Roaming\fnm\aliases\default\node.exe'
if (-not (Test-Path $node)) { $node = (Get-Command node -ErrorAction Stop).Source }
& $node 'C:/Users/admin/Documents/archify/archify/bin/archify.mjs' finalize workflow 'C:/Users/admin/Documents/archify/archify/examples/agent-tool-call.workflow.json' 'docs/tdq/native-browser-probe.html' --json | Out-File -FilePath $log -Append -Encoding utf8
('ExitCode=' + $LASTEXITCODE) | Out-File -FilePath $log -Append -Encoding utf8
