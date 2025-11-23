# Signal Hub Unificado - TraderCopilot

## 📋 Resumen

El backend de TraderCopilot ha sido refactorizado para convertirse en un **Signal Hub unificado**, donde TODAS las señales de trading (independientemente de su origen) usan un esquema de datos común y comparten la misma infraestructura de logging y exposición por API.

---

## 🎯 Objetivos Alcanzados

### 1. ✅ Schema Estándar de Señal

**Ubicación:** `backend/core/schemas.py`

- **Modelo `Signal`**: Esquema Pydantic unificado para TODAS las señales
- **Campos principales**:
  - `timestamp`: Momento de generación (UTC)
  - `strategy_id`: ID único de la estrategia (ej: `lite_v2`, `rsi_macd_v1`)
  - `mode`: Modo del análisis (LITE | PRO | ADVISOR | EVALUATED | CUSTOM)
  - `token`: Activo analizado (ETH, BTC, SOL, XAU, etc.)
  - `timeframe`: Temporalidad (30m, 1h, 4h, etc.)
  - `direction`: long | short | neutral
  - `entry`, `tp`, `sl`: Niveles de precio
  - `confidence`: Nivel de confianza 0-1
  - `rationale`: Justificación breve (≤240 chars)
  - `source`: Origen (LLM | ENGINE | MANUAL | LAB)
  - `extra`: Metadatos adicionales (dict libre)

### 2. ✅ Logger Unificado

**Ubicación:** `backend/core/signal_logger.py`

- **Función `log_signal(signal: Signal)`**: Punto único de entrada para logging
- **Persistencia dual**:
  - CSV: `logs/{MODE}/{token}.csv` (legacy/backup)
  - DB: Tabla `Signal` en PostgreSQL/SQLite
- **Compatibilidad**: Mantiene estructura de carpetas existente
- **Helper**: `signal_from_dict()` para migración de código legacy

### 3. ✅ Endpoints Adaptados

Los endpoints actuales ahora usan el sistema unificado:

#### `/analyze/lite`
- Crea instancia de `Signal` con `strategy_id="lite_v2"`
- Usa `log_signal()` para persistencia
- Mantiene compatibilidad de respuesta con frontend

#### `/analyze/pro`
- Crea instancia de `Signal` con `strategy_id="pro_v1_local"`
- Almacena markdown de análisis en `extra.analysis_markdown`
- Registra fuentes RAG usadas en `extra.rag_sources_used`

#### `/analyze/advisor`
- Crea instancia de `Signal` con `strategy_id="advisor_v1_local"`
- Almacena risk_score y alternatives en `extra`
- Usa `timeframe="N/A"` (no aplica para posiciones abiertas)

### 4. ✅ Compatibilidad con EVALUATED

**Estado:** ✅ Compatible

- El módulo `evaluated_logger.py` sigue funcionando sin cambios
- Lee señales de `logs/LITE/*.csv` (que ahora se generan por `log_signal()`)
- Escribe resultados en `logs/EVALUATED/{token}.evaluated.csv`
- La estructura de columnas CSV se mantiene idéntica
- **Próximo paso opcional**: Adaptar `evaluated_logger.py` para usar también `Signal`

### 5. ✅ Clase Base Strategy

**Ubicación:** `backend/strategies/base.py`

- **Clase abstracta `Strategy`**: Interfaz para todas las estrategias futuras
- **Contrato**:
  - `metadata() -> StrategyMetadata`: Describe la estrategia
  - `generate_signals() -> List[Signal]`: Produce señales
- **Modelo `StrategyMetadata`**: Catálogo de estrategias con:
  - `id`, `name`, `description`, `version`
  - `universe`: Tokens soportados
  - `risk_profile`: low | medium | high
  - `mode`: LITE | PRO | ADVISOR | CUSTOM
  - `source_type`: ENGINE | LLM | HYBRID | LAB

**Ejemplo de uso**:

```python
from strategies.base import Strategy, StrategyMetadata
from core.schemas import Signal
from datetime import datetime

class RSIMACDStrategy(Strategy):
    def metadata(self) -> StrategyMetadata:
        return StrategyMetadata(
            id="rsi_macd_v1",
            name="RSI + MACD Divergence",
            description="Detecta divergencias para señales contrarian",
            version="1.0.0",
            universe=["ETH", "BTC", "SOL"],
            risk_profile="medium",
            mode="CUSTOM",
            source_type="ENGINE",
        )
    
    def generate_signals(
        self,
        tokens: List[str],
        timeframe: str,
        context: Optional[Dict] = None
    ) -> List[Signal]:
        signals = []
        # Lógica de la estrategia
        signal = Signal(
            timestamp=datetime.utcnow(),
            strategy_id="rsi_macd_v1",
            mode="CUSTOM",
            token="ETH",
            timeframe="30m",
            direction="long",
            entry=3675.50,
            tp=3720.00,
            sl=3625.00,
            confidence=0.75,
            rationale="RSI divergence + MACD cross",
            source="LAB",
            extra={"rsi": 34.5, "macd": 2.3}
        )
        signals.append(signal)
        return signals
```

---

## 📁 Estructura de Archivos

```
backend/
├── core/                          # 🆕 Núcleo del Signal Hub
│   ├── __init__.py
│   ├── schemas.py                # Schema Signal unificado
│   └── signal_logger.py          # Logger centralizado
│
├── strategies/                    # 🆕 Sistema de estrategias
│   ├── __init__.py
│   └── base.py                   # Clase base Strategy
│
├── logs/                          # Logs CSV (sin cambios)
│   ├── LITE/
│   │   ├── eth.csv
│   │   ├── btc.csv
│   │   └── sol.csv
│   ├── PRO/
│   ├── ADVISOR/
│   └── EVALUATED/
│       └── eth.evaluated.csv
│
├── main.py                        # ✏️ Endpoints refactorizados
├── evaluated_logger.py            # ✅ Compatible (sin cambios)
├── models.py                      # Modelos request/response (sin cambios)
└── database.py                    # ORM SQLAlchemy (sin cambios)
```

---

## 🔄 Migración de Código Legacy

Si tienes código que usa `save_strict_log()` directamente:

### Antes (Legacy):
```python
log_entry = {
    "timestamp": datetime.utcnow().isoformat() + "Z",
    "token": "ETH",
    "timeframe": "30m",
    "direction": "long",
    "entry": 3675.50,
    "tp": 3720.00,
    "sl": 3625.00,
    "confidence": 0.68,
    "rationale": "Setup LONG",
    "source": "ENGINE",
}
save_strict_log("LITE", log_entry)
```

### Ahora (Signal Hub):
```python
from core.schemas import Signal
from core.signal_logger import log_signal

signal = Signal(
    timestamp=datetime.utcnow(),
    strategy_id="lite_v2",
    mode="LITE",
    token="ETH",
    timeframe="30m",
    direction="long",
    entry=3675.50,
    tp=3720.00,
    sl=3625.00,
    confidence=0.68,
    rationale="Setup LONG",
    source="ENGINE",
)
log_signal(signal)
```

### O usando el helper de transición:
```python
from core.signal_logger import signal_from_dict, log_signal

# Código legacy con dict
log_entry = {...}  # dict como antes

# Convertir y guardar
signal = signal_from_dict(log_entry, mode="LITE", strategy_id="lite_v2")
log_signal(signal)
```

---

## 🚀 Próximos Pasos

### Fase 2: Integración con trading_lab

1. **Crear adaptador de estrategias**:
   ```
   backend/strategies/lab_adapter.py
   ```
   - Importa estrategias de trading_lab
   - Las convierte en clases `Strategy`
   - Registra en catálogo del hub

2. **Endpoint de ejecución masiva**:
   ```
   POST /strategies/execute
   ```
   - Ejecuta múltiples estrategias en paralelo
   - Devuelve todas las señales generadas
   - Loguea automáticamente vía `log_signal()`

3. **Scheduler 24/7**:
   ```python
   # backend/scheduler.py
   from apscheduler.schedulers.background import BackgroundScheduler
   from strategies.lab_adapter import get_all_strategies
   
   def run_all_strategies():
       for strategy in get_all_strategies():
           if strategy.is_enabled():
               signals = strategy.generate_signals(...)
               for signal in signals:
                   log_signal(signal)
   
   scheduler = BackgroundScheduler()
   scheduler.add_job(run_all_strategies, 'interval', minutes=30)
   ```

### Fase 3: Dashboard de Estrategias

- UI para ver todas las estrategias disponibles
- Activar/desactivar estrategias
- Monitorear performance por `strategy_id`
- Comparar eficacia LITE vs PRO vs CUSTOM

---

## ✅ Verificación de Compatibilidad

### Tests realizados:

- ✅ Backend arranca sin errores
- ✅ Endpoints `/analyze/lite`, `/analyze/pro`, `/analyze/advisor` funcionan
- ✅ Logs CSV se generan en ubicaciones correctas
- ✅ Datos se guardan en base de datos
- ✅ `evaluated_logger.py` puede leer los nuevos CSV
- ✅ Estructura de columnas CSV es compatible

### Comandos de verificación:

```bash
# Arrancar backend
cd backend
python main.py

# Probar endpoints
curl -X POST http://localhost:8000/analyze/lite \
  -H "Content-Type: application/json" \
  -d '{"token":"eth","timeframe":"30m"}'

# Verificar logs CSV
ls -la backend/logs/LITE/
cat backend/logs/LITE/eth.csv

# Ejecutar evaluador (sin cambios)
cd backend
python evaluated_logger.py
```

---

## 📝 Notas Importantes

1. **No se rompió código existente**: `save_strict_log()` sigue disponible (pero se recomienda migrar)
2. **Compatibilidad CSV**: Los CSV mantienen exactamente las mismas columnas
3. **Base de datos**: El campo `extra` se guarda como string en `raw_response`
4. **EVALUATED**: Módulo intacto, puede adaptarse en futuro si se desea
5. **Performance**: Sin impacto, el logger unificado es tan eficiente como el anterior

---

## 🎓 Decisiones de Diseño

### ¿Por qué un schema unificado?

- **Consistencia**: Todas las señales hablan el mismo idioma
- **Escalabilidad**: Fácil agregar nuevas estrategias sin tocar logging
- **Trazabilidad**: `strategy_id` permite tracking de performance
- **Flexibilidad**: Campo `extra` permite metadatos custom

### ¿Por qué mantener CSV?

- **Backup**: Resiliente a fallos de DB
- **Debugging**: Fácil inspección manual
- **Legacy**: Compatible con scripts existentes
- **Portabilidad**: Transferible entre entornos

### ¿Por qué clase base Strategy?

- **Estandarización**: Todas las estrategias implementan mismo contrato
- **Descubrimiento**: Catálogo automático de estrategias
- **Testing**: Fácil crear mock strategies
- **Futuro**: Marketplace de estrategias de terceros

---

## 🤝 Contribuir

Para agregar una nueva estrategia:

1. Hereda de `Strategy` en `backend/strategies/`
2. Implementa `metadata()` y `generate_signals()`
3. Las señales se loguean automáticamente
4. Aparecen en `/logs/{mode}/{token}.csv` y en DB

**¡El Signal Hub está listo para crecer!** 🚀

---

**Autor:** Antigravity (Google Deepmind)  
**Fecha:** 2025-11-21  
**Versión:** 1.0.0
