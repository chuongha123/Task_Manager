# Go dang ky khoi dong tu dong
$taskName = "ManagerTaskMonitor"
$existing = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
if (-not $existing) {
    Write-Host "Khong co task: $taskName"
    exit 0
}
Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
Write-Host "Da go: $taskName"
