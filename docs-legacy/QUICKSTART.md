# 🚀 TraderCopilot - Quick Start Guide

## Inicio Rápido

### 1. Arrancar el Sistema
```powershell
# Terminal 1: Backend API
cd backend
uvicorn main:app --reload --port 8010

# Terminal 2: Scheduler (Estrategias Automáticas)
cd backend
python scheduler.py

# Terminal 3: Frontend
cd web
npm run dev
```

O usa el script todo-en-uno:
```powershell
.\start.bat
```

---

## Comandos Esenciales

### Generar Señales Manualmente
```powershell
# Generar con estrategia específica
.\generate_signals.ps1 -Strategy "donchian_v2" -Timeframe "4h"

# Generar con todas las estrategias
.\generate_signals.ps1 -Strategy "ALL"

# Solo un token específico
.\generate_signals.ps1 -Tokens @("ETH")
```

### Evaluar Señales (Verificar si alcanzaron TP/SL)
```powershell
# Evaluar todas las señales pendientes
.\evaluate_custom_signals.ps1

# Ver performance
.\view_performance.ps1

# Ver últimas 20 señales evaluadas
.\view_performance.ps1 -Last 20
```

### Monitoreo
```powershell
# Monitor en tiempo real (actualiza cada 5s)
.\monitor_signals.ps1

# Ver señales generadas
.\view_signals.ps1

# Ver solo señales de ETH
.\view_signals.ps1 -Token ETH

# Verificar estado de la base de datos
.\check_db_signals.ps1
```

### Análisis y Optimización
```powershell
# Comparar todas las estrategias
.\compare_strategies.ps1

# Test rápido de Donchian en múltiples timeframes
.\test_donchian_timeframes.ps1

# Análisis completo de performance
.\analyze_performance.ps1

# Optimización de timeframes (TARDA ~10 min)
.\optimize_timeframes.ps1
```

---

## Configuración del Sistema

### Estrategias Activas
Edita `backend/seed_strategies.py` y ejecuta:
```powershell
python backend/seed_strategies.py
```

### Cambiar Tokens
Por defecto: ETH, BTC, SOL

Para cambiar, edita `backend/seed_strategies.py`:
```python
existing.tokens = json.dumps(["ETH", "BTC", "SOL", "AVAX"])
```

### Cambiar Timeframes
Edita `backend/seed_strategies.py`:
```python
(DonchianBreakoutV2(), ["4h", "1d"]),  # Añadir 1d
```

### Cambiar Intervalo de Ejecución
Por defecto: 60 segundos

```python
existing.interval_seconds = 300  # 5 minutos
```

---

## Estructura de Archivos

```
TraderCopilot/
├── backend/
│   ├── strategies/          # Código de estrategias
│   │   ├── base.py         # Clase base
│   │   ├── donchian_v2.py  # Donchian Breakout V2
│   │   ├── bb_mean_reversion.py  # BB Mean Reversion
│   │   └── ...
│   ├── logs/               # Señales generadas (CSV)
│   │   ├── CUSTOM/         # Señales de estrategias
│   │   ├── LITE/           # Señales LITE (manual)
│   │   ├── PRO/            # Señales PRO (AI)
│   │   └── EVALUATED/      # Señales evaluadas
│   ├── main.py             # API FastAPI
│   ├── scheduler.py        # Ejecutor de estrategias
│   └── seed_strategies.py  # Configuración de estrategias
├── web/                    # Frontend React
├── *.ps1                   # Scripts de PowerShell
├── WINNING_STRATEGIES.md   # Documentación de estrategias
├── SYSTEM_STATUS.md        # Estado del sistema
└── QUICKSTART.md           # Esta guía
```

---

## Flujo de Trabajo Típico

### Desarrollo de Nueva Estrategia
1. Crear archivo en `backend/strategies/mi_estrategia.py`
2. Heredar de `Strategy` base class
3. Implementar `analyze()` y `generate_signals()`
4. Registrar en `backend/seed_strategies.py`
5. Ejecutar seed: `python backend/seed_strategies.py`
6. Probar: `.\generate_signals.ps1 -Strategy "mi_estrategia"`
7. Evaluar: `.\evaluate_custom_signals.ps1`
8. Analizar: `.\view_performance.ps1`

### Testing de Estrategia Existente
1. Generar señales: `.\generate_signals.ps1`
2. Evaluar: `.\evaluate_custom_signals.ps1`
3. Ver resultados: `.\view_performance.ps1`
4. Ajustar parámetros si es necesario
5. Repetir

### Despliegue a Producción
1. Verificar que estrategias estén validadas (Win Rate > 50%)
2. Configurar en `seed_strategies.py`
3. Ejecutar seed
4. Reiniciar scheduler: `.\restart_scheduler.ps1`
5. Monitorear: `.\monitor_signals.ps1`

---

## Troubleshooting

### "No signals generated"
- Verifica que la estrategia esté habilitada en la DB
- Comprueba que los datos de mercado se estén descargando
- Revisa los logs del scheduler

### "CORS errors" en frontend
- Verifica que el backend esté en puerto 8010
- Revisa `web/src/constants.ts` → `API_BASE_URL`
- Comprueba `web/.env.local`

### "Database locked"
- Detén el scheduler antes de ejecutar seed
- Usa `db.commit()` después de cada operación

### "UnicodeEncodeError" en scripts
- Ya está arreglado en los scripts actuales
- Si aparece, añade al inicio del script Python:
  ```python
  import sys, io
  sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
  ```

---

## Recursos

- **Documentación**: `WINNING_STRATEGIES.md`, `SYSTEM_STATUS.md`
- **Resultados**: `performance_analysis.csv`, `optimization_results.csv`
- **Logs**: `backend/logs/`
- **Base de Datos**: SQLite (`backend/tradercopilot.db`) o PostgreSQL (Railway)

---

## Próximos Pasos Sugeridos

1. ✅ Monitorear las 3 estrategias activas durante 24-48h
2. ✅ Evaluar performance real
3. ✅ Ajustar filtro RSI de 15m si es necesario
4. 🔄 Desarrollar RSI Divergence Strategy
5. 🔄 Implementar sistema de alertas (Discord/Telegram)
6. 🔄 Dashboard de monitoreo en tiempo real

---

**¡Estás listo para generar señales de trading de alta calidad!** 🚀

**Última Actualización**: 2025-11-30
