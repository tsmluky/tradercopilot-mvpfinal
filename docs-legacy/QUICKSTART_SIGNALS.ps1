# ============================================
# TraderCopilot - Quick Start Guide
# ============================================

Write-Host @"
========================================
  TraderCopilot - Quick Start Guide
========================================

📊 GENERAR SEÑALES MANUALMENTE
----------------------------------------
1. Generar con Donchian V2 (1h):
   .\generate_signals.ps1

2. Cambiar timeframe:
   .\generate_signals.ps1 -Timeframe "4h"

3. Solo un token específico:
   .\generate_signals.ps1 -Tokens @("ETH")

4. Usar otra estrategia:
   .\generate_signals.ps1 -Strategy "ma_cross_v1"

5. Todas las estrategias:
   .\generate_signals.ps1 -Strategy "ALL"


📈 TESTS RÁPIDOS
----------------------------------------
1. Test Donchian en múltiples timeframes:
   .\test_donchian_timeframes.ps1

2. Comparar todas las estrategias:
   .\compare_strategies.ps1


📋 VER RESULTADOS
----------------------------------------
1. Ver últimas 10 señales:
   .\view_signals.ps1

2. Ver últimas 20 señales:
   .\view_signals.ps1 -Last 20

3. Solo señales de ETH:
   .\view_signals.ps1 -Token ETH

4. Ver señales PRO:
   .\view_signals.ps1 -Mode PRO


🔍 MONITOREO
----------------------------------------
1. Monitor en tiempo real:
   .\monitor_signals.ps1

2. Verificar base de datos:
   .\check_db_signals.ps1


⚙️ ESTRATEGIAS DISPONIBLES
----------------------------------------
- donchian_v2          (Donchian Breakout V2)
- ma_cross_v1          (MA Cross 10/50)
- donchian_breakout_v1 (Donchian Breakout 20)
- bb_mean_reversion_v1 (BB Mean Reversion)


🎯 TIMEFRAMES DISPONIBLES
----------------------------------------
15m, 30m, 1h, 4h, 1d


💡 TIPS
----------------------------------------
- El scheduler ahora ejecuta cada 60 segundos
- Las señales se guardan en CSV y DB
- Usa Ctrl+C para detener el monitor
- Los CSVs están en: backend/logs/LITE/*.csv

========================================
"@ -ForegroundColor Cyan
