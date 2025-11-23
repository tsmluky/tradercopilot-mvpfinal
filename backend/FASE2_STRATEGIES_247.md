# 🚀 Fase 2: Estrategias 24/7 - COMPLETADA

## 📋 Resumen

El backend ahora soporta **ejecución automática de estrategias 24/7** a través de un scheduler simple en loop Python.

**Lo mejor:** No requiere Docker, cron ni nada complejo. Solo `python scheduler.py` y ya está corriendo.

---

## ✅ Objetivos Cumplidos (Fase 2)

### 1. ✅ Sistema de Registro de Estrategias
- **Archivo:** `strategies/registry.py`
- **Función:** Catálogo centralizado de estrategias disponibles
- **Features**:
  - Registro automático de estrategias
  - Listar estrategias activas
  - Instanciar estrategias con config custom

### 2. ✅ Tabla de Configuración de Estrategias
- **Modelo DB:** `StrategyConfig` en `models_db.py`
- **Campos clave**:
  - `enabled`: Activar/desactivar estrategia
  - `interval_seconds`: Cada cuánto ejecutar
  - `tokens`: Tokens a analizar (JSON array)
  - `timeframes`: Timeframes a usar (JSON array)
  - `config_json`: Parámetros específicos de la estrategia
  - **Estadísticas:** `total_signals`, `win_rate`, `last_execution`

### 3. ✅ Scheduler Simple (Loop Python)
- **Archivo:** `scheduler.py`
- **Ejecución:** `python scheduler.py [interval_seconds]`
- **Características**:
  - Loop infinito que chequea estrategias activas
  - Respeta `interval_seconds` de cada estrategia
  - Loguea señales automáticamente vía `log_signal()`
  - No requiere Docker ni cron
  - Se puede detener con Ctrl+C

### 4. ✅ Endpoints API de Gestión
- **Router:** `routers/strategies.py`
- **Endpoints**:
  - `GET /strategies/` - Listar todas las estrategias
  - `GET /strategies/{id}` - Detalles de una estrategia
  - `PATCH /strategies/{id}` - Actualizar config (activar/desactivar)
  - `POST /strategies/{id}/execute` - Ejecutar manualmente (testing)

### 5. ✅ Script de Setup Inicial
- **Archivo:** `setup_strategies.py`
- **Función:** Registrar estrategias y crear configs en DB
- **Ejecución:** `python setup_strategies.py` (una sola vez)

---

## 📁 Archivos Creados (Fase 2)

```
backend/
├── strategies/
│   ├── registry.py                    # 🆕 Registry de estrategias
│   └── example_rsi_macd.py            # ✅ Ya existía (Fase 1)
│
├── routers/
│   └── strategies.py                  # 🆕 API endpoints
│
├── scheduler.py                       # 🆕 Scheduler 24/7 (loop simple)
├── setup_strategies.py                # 🆕 Setup inicial
└── models_db.py                       # ✏️ Modificado (+StrategyConfig)
```

## ✏️ Archivos Modificados

```
backend/main.py
  ├── Import: +StrategyConfig
  └── Router: +strategies_router
```

---

## 🎯 Flujo Completo: De Estrategia a Señal

### 1. **Crear una Estrategia**

```python
# backend/strategies/my_strategy.py
from strategies.base import Strategy, StrategyMetadata
from core.schemas import Signal
from datetime import datetime

class MyStrategy(Strategy):
    def metadata(self) -> StrategyMetadata:
        return StrategyMetadata(
            id="my_strategy_v1",
            name="My Custom Strategy",
            description="Mi estrategia personalizada",
            version="1.0.0",
            default_timeframe="1h",
            universe=["ETH", "BTC"],
            risk_profile="medium",
            mode="CUSTOM",
            source_type="ENGINE",
            enabled=True,
        )
    
    def generate_signals(self, tokens, timeframe, context=None):
        # Tu lógica aquí
        signals = []
        
        for token in tokens:
            # Calcular indicadores, detectar setups, etc.
            # ...
            
            signal = Signal(
                timestamp=datetime.utcnow(),
                strategy_id="my_strategy_v1",
                mode="CUSTOM",
                token=token,
                timeframe=timeframe,
                direction="long",
                entry=3675.50,
                tp=3720.00,
                sl=3625.00,
                confidence=0.75,
                rationale="Mi setup detectado",
                source="LAB",
                extra={"custom_data": "..."}
            )
            signals.append(signal)
        
        return signals
```

### 2. **Registrar la Estrategia**

```python
# backend/setup_strategies.py (agregar al script)
from strategies.my_strategy import MyStrategy

registry = get_registry()
registry.register(MyStrategy)
```

### 3. **Ejecutar Setup**

```bash
cd backend
python setup_strategies.py
```

Esto crea la config en la DB con `enabled=0` (desactivada).

### 4. **Activar desde API**

```bash
# Activar estrategia
curl -X PATCH http://localhost:8000/strategies/my_strategy_v1 \
  -H "Content-Type: application/json" \
  -d '{
    "enabled": true,
    "interval_seconds": 300,
    "tokens": ["ETH", "BTC", "SOL"],
    "timeframes": ["1h", "4h"]
  }'
```

### 5. **Iniciar Scheduler**

```bash
python scheduler.py 10  # Chequea cada 10 segundos
```

**Salida:**
```
===========================================================
🚀 TraderCopilot - Strategy Scheduler
===========================================================
Loop interval: 10s
Press Ctrl+C to stop

[2025-11-21 17:20:00] Iteration #1
  ℹ️  Active strategies: 1

  🔄 Executing: My Custom Strategy (my_strategy_v1)
  📊 Signal: ETH long @ 3675.5
  📊 Signal: BTC long @ 42000.0
  ✅ Generated 2 signals

  😴 Sleeping for 10s...
```

### 6. **Verificar Señales**

```bash
# Ver logs CSV
cat backend/logs/CUSTOM/eth.csv

# O via API
curl http://localhost:8000/logs/CUSTOM/eth
```

---

## 🎮 Comandos Útiles

### Setup Inicial
```bash
cd backend

# 1. Ejecutar setup (una sola vez)
python setup_strategies.py

# 2. Arrancar backend
python main.py  # en terminal 1

# 3. Arrancar scheduler
python scheduler.py 10  # en terminal 2 (chequea cada 10s)
```

### Gestión de Estrategias (API)

```bash
# Listar todas las estrategias
curl http://localhost:8000/strategies/

# Ver detalles de una estrategia
curl http://localhost:8000/strategies/rsi_macd_divergence_v1

# Activar estrategia
curl -X PATCH http://localhost:8000/strategies/rsi_macd_divergence_v1 \
  -H "Content-Type: application/json" \
  -d '{"enabled": true}'

# Desactivar estrategia
curl -X PATCH http://localhost:8000/strategies/rsi_macd_divergence_v1 \
  -H "Content-Type: application/json" \
  -d '{"enabled": false}'

# Cambiar intervalo (ejecutar cada 10 minutos = 600s)
curl -X PATCH http://localhost:8000/strategies/rsi_macd_divergence_v1 \
  -H "Content-Type: application/json" \
  -d '{"interval_seconds": 600}'

# Ejecutar manualmente (testing)
curl -X POST http://localhost:8000/strategies/rsi_macd_divergence_v1/execute \
  -H "Content-Type: application/json" \
  -d '{
    "tokens": ["ETH", "BTC"],
    "timeframe": "1h"
  }'
```

---

## 🎨 Dashboard de Estrategias (Futuro - Fase 3)

El backend YA está listo para el dashboard. Solo falta el frontend.

### Página "Estrategias" (Propuesta)

**Cards de Estrategias:**
```tsx
// web/src/pages/StrategiesPage.tsx

import { useStrategies } from '@/hooks/useStrategies';

export function StrategiesPage() {
  const { strategies, loading } = useStrategies();
  
  return (
    <div className="strategies-grid">
      {strategies.map(strategy => (
        <StrategyCard
          key={strategy.id}
          strategy={strategy}
          onToggle={() => toggleStrategy(strategy.id)}
        />
      ))}
    </div>
  );
}
```

**Card Individual:**
```tsx
<div className="strategy-card">
  <h3>{strategy.name}</h3>
  <p>{strategy.description}</p>
  
  <div className="stats">
    <span>📊 Signals: {strategy.total_signals}</span>
    <span>✅ Win Rate: {strategy.win_rate}%</span>
    <span>⏱️ Last: {strategy.last_execution}</span>
  </div>
  
  <div className="meta">
    <Badge>{strategy.risk_profile}</Badge>
    <Badge>{strategy.mode}</Badge>
  </div>
  
  <button onClick={() => onToggle()}>
    {strategy.enabled ? "🟢 Activa" : "⚪ Pausada"}
  </button>
</div>
```

**Hook Custom:**
```tsx
// web/src/hooks/useStrategies.ts
export function useStrategies() {
  const [strategies, setStrategies] = useState([]);
  
  useEffect(() => {
    fetch('http://localhost:8000/strategies/')
      .then(res => res.json())
      .then(setStrategies);
  }, []);
  
  const toggleStrategy = async (id: string) => {
    // PATCH /strategies/{id} {enabled: !current}
  };
  
  return { strategies, toggleStrategy };
}
```

---

## 🔒 Seguridad y Límites (Importante)

### Fase Actual (MVP)
- ✅ Estrategias solo en el backend (código)
- ✅ No hay ejecución de código de usuarios
- ✅ Configs en DB, lógica en servidor

### Futuro (Usuarios Custom)
Cuando quieras permitir que usuarios suban estrategias:

1. **Sandbox obligatorio:**
   - Contenedores Docker aislados
   - Límites de CPU/memoria
   - Timeout de ejecución

2. **DSL o bloques:**
   - No Python arbitrario
   - Visual strategy builder (bloques tipo Scratch)
   - O DSL seguro (tipo Pine Script de TradingView)

3. **Validación estricta:**
   - Backtesting out-of-sample
   - Walk-forward testing
   - Revisión manual antes de publicar

**No implementar esto hasta tener al menos 100-500 usuarios activos.**

---

## 📊 Métricas y Monitoring (Opcional - Fase 3)

### Estadísticas por Estrategia

El modelo `StrategyConfig` ya tiene campos para:
- `total_signals`: Contador de señales generadas
- `win_rate`: % de acierto (actualizado por evaluaciones)
- `avg_confidence`: Confianza promedio
- `last_execution`: Timestamp de última ejecución

**Actualización automática:**
```python
# En evaluated_logger.py, después de evaluar:
db = SessionLocal()
config = db.query(StrategyConfig).filter(
    StrategyConfig.strategy_id == signal.strategy_id
).first()

if config:
    # Recalcular win_rate basado en evaluaciones
    config.win_rate = calculate_win_rate(signal.strategy_id)
    db.commit()
```

### Dashboard de Performance
- Ranking de estrategias por win_rate
- Gráfica de señales generadas por día
- Comparativa LITE vs PRO vs CUSTOM
- ROI simulado (paper trading)

---

## 🎯 Próximos Pasos (Roadmap)

### ✅ Completado (Fase 1 + Fase 2)
- [x] Schema Signal unificado
- [x] Logger centralizado
- [x] Clase base Strategy
- [x] Registry de estrategias
- [x] Tabla StrategyConfig en DB
- [x] Scheduler simple (loop Python)
- [x] Endpoints API de gestión

### 📋 Pendiente (Fase 3 - Dashboard)
- [ ] Frontend: Página de estrategias
- [ ] Frontend: Cards de estrategias con stats
- [ ] Frontend: Toggle activar/desactivar
- [ ] Frontend: Ejecutar manualmente (testing)
- [ ] Frontend: Gráficas de performance

### 🔮 Futuro (Fase 4 - Avanzado)
- [ ] Backtesting integrado
- [ ] Paper trading automático
- [ ] Seguimiento de estrategias por usuarios
- [ ] Notificaciones push cuando se genera señal
- [ ] Rankings de usuarios (gamificación)
- [ ] **Mucho más adelante:** Usuarios suben estrategias

---

## 🎉 Conclusión

**El backend ahora es un sistema completo de gestión de estrategias 24/7.**

### ¿Qué tenemos?
- ✅ **Schema unificado** (Signal)
- ✅ **Logger centralizado** (log_signal)
- ✅ **Clase base** (Strategy)
- ✅ **Registry** (catálogo)
- ✅ **BD** (StrategyConfig)
- ✅ **Scheduler** (loop simple)
- ✅ **API** (gestión completa)

### ¿Cómo empezar?
```bash
cd backend

# Setup (una vez)
python setup_strategies.py

# Terminal 1: Backend
python main.py

# Terminal 2: Scheduler
python scheduler.py 10

# Activar estrategias vía API
curl -X PATCH http://localhost:8000/strategies/rsi_macd_divergence_v1 \
  -d '{"enabled": true}'
```

### ¿Qué sigue?
1. **Crear 2-3 estrategias básicas** (de trading_lab o nuevas)
2. **Dejarlas correr 1-2 semanas** para acumular datos
3. **Evaluar performance** con tu módulo EVALUATED
4. **Construir dashboard** cuando tengas datos reales que mostrar

**No te flipes con features avanzadas hasta tener esto rodando sólido.**

---

**Desarrollado por:** Antigravity (Google Deepmind)  
**Fecha:** 2025-11-21  
**Versión:** Fase 2 Completada ✅
