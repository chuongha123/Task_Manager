# Chay PowerShell: click phai -> Run with PowerShell, hoac:
#   powershell -ExecutionPolicy Bypass -File "D:\Desktop\Manager\Install-StartupTask.ps1"
# Dang ky chay khi dang nhap Windows (user hien tai), khong can Admin.

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$exePath = Join-Path $root "dist\ManagerTaskMonitor.exe"

if (-not (Test-Path -LiteralPath $exePath)) {
    Write-Error "Khong thay file EXE tai: $exePath"
    Write-Error "Hay build truoc: pyinstaller --onefile --noconsole --name ManagerTaskMonitor Task_Manager.py"
    exit 1
}

$taskName = "ManagerTaskMonitor"
$existing = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
if ($existing) {
    Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
    Write-Host "Da go task cu: $taskName"
}

$action = New-ScheduledTaskAction -Execute $exePath -WorkingDirectory $root
$trigger = New-ScheduledTaskTrigger -AtLogOn -User $env:USERNAME
$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -ExecutionTimeLimit ([TimeSpan]::Zero) `
    -RestartCount 3 `
    -RestartInterval (New-TimeSpan -Minutes 1)

Register-ScheduledTask `
    -TaskName $taskName `
    -Action $action `
    -Trigger $trigger `
    -Settings $settings `
    -Description "Task Manager monitor: CPU/RAM + Discord (run ManagerTaskMonitor.exe)"

Write-Host "OK: Task '$taskName' se chay khi ban dang nhap Windows."
Write-Host "Go bo: Unregister-ScheduledTask -TaskName '$taskName' -Confirm:`$false"
