# Watch-TexFiles.ps1
# Watches C:\Users\yanng\Documents\CV for new or modified .tex files
# and automatically compiles them to PDF using MiKTeX pdflatex.
#
# SETUP (run once as Administrator):
#   Right-click → "Run with PowerShell" on Install-TexWatcher.ps1
#
# MANUAL START:
#   powershell -ExecutionPolicy Bypass -File "INSERT PATH\Watch-TexFiles.ps1"

$WatchFolder = "INSERT PATH"
$LogFile     = "$WatchFolder\tex-watcher.log"

function Write-Log {
    param([string]$Message)
    $ts = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    "$ts  $Message" | Tee-Object -FilePath $LogFile -Append | Write-Host
}

function Compile-Tex {
    param([string]$TexPath)

    $dir  = Split-Path $TexPath -Parent
    $file = Split-Path $TexPath -Leaf
    $base = [System.IO.Path]::GetFileNameWithoutExtension($file)
    $pdf  = Join-Path $dir "$base.pdf"

    Write-Log "Compiling: $file"

    # Run twice so cross-references resolve
    for ($i = 1; $i -le 2; $i++) {
        $result = & pdflatex `
            -interaction=nonstopmode `
            -output-directory=$dir `
            $TexPath 2>&1

        if ($LASTEXITCODE -ne 0) {
            Write-Log "ERROR on pass $i for $file — check $dir\$base.log"
            return
        }
    }

    # Clean up auxiliary files
    foreach ($ext in @('.aux', '.out', '.toc', '.fls', '.fdb_latexmk')) {
        $aux = Join-Path $dir "$base$ext"
        if (Test-Path $aux) { Remove-Item $aux -Force }
    }

    Write-Log "Done: $pdf"
}

# ── Watcher setup ──────────────────────────────────────────────────────────────
$watcher                     = New-Object System.IO.FileSystemWatcher
$watcher.Path                = $WatchFolder
$watcher.Filter              = "*.tex"
$watcher.IncludeSubdirectories = $true
$watcher.NotifyFilter        = [System.IO.NotifyFilters]::FileName `
                             -bor [System.IO.NotifyFilters]::LastWrite
$watcher.EnableRaisingEvents = $true

# Debounce: track last compile time per file to avoid double-firing
$lastCompile = @{}

$action = {
    $path = $Event.SourceEventArgs.FullPath

    # Skip MiKTeX temp files and log files
    if ($path -match '\.(log|aux|out|fls|fdb_latexmk)$') { return }

    $now = [datetime]::Now
    if ($lastCompile.ContainsKey($path)) {
        $elapsed = ($now - $lastCompile[$path]).TotalSeconds
        if ($elapsed -lt 5) { return }   # ignore if compiled < 5s ago
    }
    $lastCompile[$path] = $now

    Compile-Tex -TexPath $path
}

$created = Register-ObjectEvent $watcher Created -Action $action
$changed = Register-ObjectEvent $watcher Changed -Action $action

Write-Log "Watcher started — monitoring $WatchFolder for .tex files"
Write-Log "Press Ctrl+C to stop."

# Keep the script alive
try {
    while ($true) { Start-Sleep -Seconds 2 }
} finally {
    Unregister-Event $created.Id
    Unregister-Event $changed.Id
    $watcher.Dispose()
    Write-Log "Watcher stopped."
}
