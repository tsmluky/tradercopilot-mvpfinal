param(
    [string]$BackendPort = "8000",
    [string]$WebPort     = "5173"
)

# Ruta raíz del proyecto = padre de la carpeta "scripts"
$projectRoot = (Get-Item $PSScriptRoot).Parent.FullName

$pythonExe   = Join-Path $projectRoot ".venv\Scripts\python.exe"
$backendPath = Join-Path $projectRoot "backend"
$webPath     = Join-Path $projectRoot "web"

Write-Host "Usando proyecto en: $projectRoot" -ForegroundColor Cyan
Write-Host "Python: $pythonExe" -ForegroundColor Cyan

if (-not (Test-Path $pythonExe)) {
    Write-Host "ERROR: No se encontró .venv o python.exe en .venv\Scripts" -ForegroundColor Red
    exit 1
}

# Lanzar backend en una nueva ventana de PowerShell
Write-Host "Iniciando backend en http://127.0.0.1:$BackendPort ..." -ForegroundColor Green
Start-Process pwsh -ArgumentList @(
    "-NoExit",
    "-Command",
    "cd `"$backendPath`"; `"$pythonExe`" -m uvicorn main:app --reload --port $BackendPort"
)

# Lanzar web en otra nueva ventana de PowerShell
Write-Host "Iniciando web en http://127.0.0.1:$WebPort ..." -ForegroundColor Green
Start-Process pwsh -ArgumentList @(
    "-NoExit",
    "-Command",
    "cd `"$webPath`"; npm run dev -- --host 0.0.0.0 --port $WebPort"
)

Write-Host "Todo lanzado. Abre el navegador en http://localhost:$WebPort" -ForegroundColor Yellow
