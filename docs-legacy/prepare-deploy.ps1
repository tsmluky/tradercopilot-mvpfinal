# Script para inicializar Git y preparar para despliegue
Write-Host "🚀 Preparando TraderCopilot para despliegue..." -ForegroundColor Cyan

# Verificar si Git está instalado
if (!(Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Git no está instalado. Por favor instala Git desde https://git-scm.com/" -ForegroundColor Red
    exit 1
}

# Inicializar repositorio si no existe
if (!(Test-Path ".git")) {
    Write-Host "📦 Inicializando repositorio Git..." -ForegroundColor Yellow
    git init
    git branch -M main
} else {
    Write-Host "✅ Repositorio Git ya existe" -ForegroundColor Green
}

# Añadir todos los archivos
Write-Host "📝 Añadiendo archivos..." -ForegroundColor Yellow
git add .

# Crear commit
Write-Host "💾 Creando commit..." -ForegroundColor Yellow
git commit -m "Preparado para despliegue en Railway y Vercel"

Write-Host ""
Write-Host "✅ ¡Listo para desplegar!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Próximos pasos:" -ForegroundColor Cyan
Write-Host "1. Crear repositorio en GitHub: https://github.com/new" -ForegroundColor White
Write-Host "2. Ejecutar estos comandos (reemplaza TU_USUARIO):" -ForegroundColor White
Write-Host "   git remote add origin https://github.com/TU_USUARIO/TraderCopilot.git" -ForegroundColor Gray
Write-Host "   git push -u origin main" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Seguir la guía en DEPLOY.md para desplegar en Railway y Vercel" -ForegroundColor White
Write-Host ""
