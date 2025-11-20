param(
    [Parameter(Mandatory = $true)]
    [string]$GitHubUser,

    [string]$RepoName = "tradercopilot-mvpfinal"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

Write-Host "== TraderCopilot · Publicar en GitHub ==" -ForegroundColor Cyan

# 1) Ubicar raíz del proyecto
$root = Join-Path $HOME "Desktop\TraderCopilot"
if (-not (Test-Path $root)) {
    throw "No se encontró la carpeta del proyecto: $root"
}

Set-Location $root
Write-Host "Raíz del proyecto: $root" -ForegroundColor Yellow

# 2) Inicializar repo Git si no existe
if (-not (Test-Path ".git")) {
    Write-Host "No se encontró .git, inicializando repositorio..." -ForegroundColor Yellow
    git init | Out-Null
} else {
    Write-Host "Repositorio Git ya existente." -ForegroundColor DarkGray
}

# 3) Crear .gitignore básico si no existe
if (-not (Test-Path ".gitignore")) {
    Write-Host "Creando .gitignore por defecto..." -ForegroundColor Yellow
@"
# === Python ===
__pycache__/
*.py[cod]
*.pyo
*.pyd
*.log
.venv/
venv/
.env
*.sqlite3

# === Node / Frontend ===
node_modules/
dist/
build/
.next/
.npm/
.pnp.*
coverage/
*.local

# === Editor / SO ===
.vscode/
.idea/
*.iml
.DS_Store
Thumbs.db

# === Otros ===
*.zip
*.bak
logs/
"@ | Set-Content ".gitignore" -Encoding UTF8
} else {
    Write-Host ".gitignore ya existe, se respeta el actual." -ForegroundColor DarkGray
}

# 4) Añadir cambios al stage
Write-Host "Añadiendo archivos al stage..." -ForegroundColor Yellow
git add . 

# 5) Comprobar si hay algo que commitear
$pending = git status --porcelain
if ([string]::IsNullOrWhiteSpace($pending)) {
    Write-Host "No hay cambios nuevos para commitear." -ForegroundColor DarkGray
} else {
    Write-Host "Creando commit..." -ForegroundColor Yellow
    git commit -m "Initial MVP final commit" | Out-Null
}

# 6) Asegurar rama main
Write-Host "Forzando rama 'main'..." -ForegroundColor Yellow
git branch -M main

# 7) Configurar remoto origin
$remoteName = "origin"
$remoteUrl  = "https://github.com/$GitHubUser/$RepoName.git"
Write-Host "Usando remoto: $remoteUrl" -ForegroundColor Yellow

$existingOrigin = git remote 2>$null | Select-String "^origin$" -Quiet
if (-not $existingOrigin) {
    Write-Host "Añadiendo remoto 'origin'..." -ForegroundColor Yellow
    git remote add $remoteName $remoteUrl
} else {
    Write-Host "Actualizando URL de 'origin'..." -ForegroundColor Yellow
    git remote set-url $remoteName $remoteUrl
}

# 8) Push a GitHub
Write-Host "Haciendo push a GitHub (main)..." -ForegroundColor Cyan
git push -u origin main

Write-Host "✅ Publicación completada. Revisa el repo en GitHub: $remoteUrl" -ForegroundColor Green
