$projectRoot = (Get-Item $PSScriptRoot).Parent.FullName
$pythonExe   = Join-Path $projectRoot ".venv\Scripts\python.exe"
$labPath     = Join-Path $projectRoot "trading_lab"

if (-not (Test-Path $pythonExe)) {
    Write-Host "ERROR: No se encontró .venv. Crea y configura el entorno antes." -ForegroundColor Red
    exit 1
}

Set-Location $labPath
Write-Host "Ejecutando engine.py en $labPath ..." -ForegroundColor Green
& $pythonExe "engine.py"
