# SAARTHI master script (Windows PowerShell) — wrapper around scripts\dev.py.
#
# Usage (from PowerShell):
#   Set-ExecutionPolicy -Scope Process Bypass   # if scripts are blocked
#   .\run.ps1 setup | doctor | start | stop | test | check | health |
#               migrate | parity | smoke
#
# The Python work always happens in the project virtual environment (.venv);
# the wrapper only bootstraps the interpreter that can CREATE it. See
# scripts\dev.py for the full command reference; .env.example documents all
# required environment variables.
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root

$py = $null
if (Test-Path ".venv\Scripts\python.exe") {
  $py = ".venv\Scripts\python.exe"
} else {
  # Bootstrap interpreter: only used to CREATE the venv (never to install
  # into system Python).
  foreach ($candidate in @("python", "python3", "py")) {
    if (Get-Command $candidate -ErrorAction SilentlyContinue) {
      $py = $candidate
      break
    }
  }
}
if (-not $py) {
  Write-Error "run.ps1: Python 3 is required. Install Python 3 (with the venv module) and rerun: .\run.ps1 setup"
  exit 1
}

& $py scripts\dev.py @args
exit $LASTEXITCODE
