# Install-TexWatcher.ps1
# Run this ONCE as Administrator to register the watcher as a Windows Scheduled Task.
# After installation it starts automatically at login — no manual step needed.

$TaskName   = "TexFileWatcher"
$ScriptPath = "INSERT PATH\Watch-TexFiles.ps1"
$User       = $env:USERNAME

# Remove old task if it exists
if (Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue) {
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
    Write-Host "Removed existing task."
}

$action  = New-ScheduledTaskAction `
    -Execute "powershell.exe" `
    -Argument "-ExecutionPolicy Bypass -WindowStyle Hidden -File `"$ScriptPath`""

$trigger = New-ScheduledTaskTrigger -AtLogOn -User $User

$settings = New-ScheduledTaskSettingsSet -ExecutionTimeLimit (New-TimeSpan -Hours 0) -RestartCount 3 -RestartInterval (New-TimeSpan -Minutes 1) -StartWhenAvailable

Register-ScheduledTask `
    -TaskName  $TaskName `
    -Action    $action `
    -Trigger   $trigger `
    -Settings  $settings `
    -RunLevel  Highest `
    -Force

Write-Host ""
Write-Host "Installed! The watcher will start automatically at every login."
Write-Host "To start it now without logging out:"
Write-Host "  Start-ScheduledTask -TaskName '$TaskName'"
