# TraderCopilot - Signal Hub + Estrategias 24/7 (COMPLETADO)

## 🎯 ¿Qué se hizo?

Transformamos el backend de TraderCopilot en un **Signal Hub unificado** con soporte para **estrategias automáticas 24/7**.

## 📦 Cambios (2 Fases)

### Fase 1: Signal Hub Unificado
- **Schema Signal** (`core/schemas.py`) → Modelo Pydantic estándar para TODAS las señales
- **Logger centralizado** (`core/signal_logger.py`) → `log_signal(signal)` persiste en CSV + DB
- **Clase Strategy** (`strategies/base.py`) → ABC para cualquier estrategia futura
- **Endpoints refactorizados** → LITE/PRO/ADVISOR usan Signal + log_signal()

### Fase 2: Estrategias 24/7
- **StrategyRegistry** (`strategies/registry.py`) → Catálogo de estrategias
- **StrategyConfig** (`models_db.py`) → Tabla DB con config + stats
- **Scheduler** (`scheduler.py`) → Loop Python que ejecuta estrategias enabled
- **API** (`routers/strategies.py`) → GET/PATCH/POST para gestionar estrategias
- **Setup** (`setup_strategies.py`) → Registra estrategias en DB

## 🚀 Cómo Usar

```bash
# Setup (una vez)
python setup_strategies.py

# Terminal 1: Backend
python main.py

# Terminal 2: Scheduler
python scheduler.py 10

# Activar estrategia
curl -X PATCH http://localhost:8000/strategies/rsi_macd_divergence_v1 \
  -d '{"enabled": true, "interval_seconds": 300}'
```

## 📊 Arquitectura

```
Strategy → Registry → Scheduler → log_signal() → CSV + DB
                          ↕
                   StrategyConfig (DB)
```

## 📝 Archivos

**Creados (17):** core/, strategies/, scheduler.py, routers/strategies.py, docs  
**Modificados (2):** main.py, models_db.py  
**Tests:** 12/12 PASS ✅

## 🎁 Beneficios

- ✅ Schema unificado (todas las señales iguales)
- ✅ Logger centralizado (un solo punto)
- ✅ Fácil agregar estrategias (heredar Strategy)
- ✅ Ejecutor 24/7 (sin Docker, solo Python loop)
- ✅ API completa (dashboard ready)

## 📚 Docs

- `RESUMEN_PARA_CHATGPT.md` → Explicación completa
- `FASE2_STRATEGIES_247.md` → Guía técnica
- `CHECK_COMPLETO_FINAL.md` → Instrucciones de uso
