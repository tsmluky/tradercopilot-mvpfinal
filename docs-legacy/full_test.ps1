# ============================================
# TraderCopilot - Workflow Completo de Testing
# ============================================

Write-Host @"
========================================
  TraderCopilot - Full Testing Workflow
========================================
"@ -ForegroundColor Cyan

Write-Host ""
Write-Host "Step 1: Generating signals..." -ForegroundColor Yellow
.\compare_strategies.ps1

Write-Host ""
Write-Host "Step 2: Evaluating signals..." -ForegroundColor Yellow
.\evaluate_signals.ps1

Write-Host ""
Write-Host "Step 3: Analyzing performance..." -ForegroundColor Yellow
.\view_performance.ps1 -Last 30

Write-Host ""
Write-Host "Step 4: Strategy comparison..." -ForegroundColor Yellow
.\analyze_strategies.ps1

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  ✅ Full workflow completed!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
