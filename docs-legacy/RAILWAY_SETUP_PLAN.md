# PLAN DE ACCIÓN COMPLETO - TraderCopilot Railway Setup

## 🎯 OBJETIVO
Conectar el scheduler local a Railway PostgreSQL y generar señales limpias con Donchian V2.

---

## 📋 PASOS A SEGUIR

### 1. **Obtener URL Pública de Railway**

Ve a Railway → Tu proyecto → PostgreSQL → Variables

Busca estas variables y cópialas:
- `PGHOST` (ejemplo: `monorail.proxy.rlwy.net`)
- `PGPORT` (ejemplo: `12345`)
- `PGUSER` (ejemplo: `postgres`)
- `PGPASSWORD` (ejemplo: `SzApckZdqOnbbbyeLeWLRVfBZWZtAaVu`)
- `PGDATABASE` (ejemplo: `railway`)

### 2. **Actualizar .env con URL Pública**

Reemplaza la línea `DATABASE_URL` en tu `.env` con:

```env
DATABASE_URL=postgresql://PGUSER:PGPASSWORD@PGHOST:PGPORT/PGDATABASE
```

**Ejemplo real:**
```env
DATABASE_URL=postgresql://postgres:SzApckZdqOnbbbyeLeWLRVfBZWZtAaVu@monorail.proxy.rlwy.net:12345/railway
```

⚠️ **IMPORTANTE:** La URL actual tiene `postgres.railway.internal` que solo funciona DENTRO de Railway, no desde tu PC.

---

### 3. **Limpiar Base de Datos (Opcional)**

Si quieres empezar de cero, ejecuta en Railway Query:

```sql
-- Ver cuántas señales hay
SELECT COUNT(*) FROM signal;

-- Borrar todas las señales antiguas
DELETE FROM signal;

-- Borrar evaluaciones
DELETE FROM signal_evaluation;

-- Verificar estrategias activas
SELECT strategy_id, enabled, name FROM strategy_config;
```

---

### 4. **Configurar Estrategias en Railway**

Ejecuta desde tu PC (una vez conectado):

```powershell
cd C:\Users\lukx\Desktop\TraderCopilot\backend
python setup_strategies.py
python disable_old_strategies.py
```

Esto creará `donchian_v2` en Railway y desactivará las demás.

---

### 5. **Limpiar Logs Locales**

```powershell
Remove-Item -Recurse -Force logs\*
New-Item -ItemType Directory -Path logs\CUSTOM, logs\PRO, logs\EVALUATED
```

---

### 6. **Arrancar Scheduler Conectado a Railway**

```powershell
python scheduler.py 60
```

Deberías ver:
```
[DB] Using Configured Database
✅ Strategies registered
  ℹ️  Active strategies: 1
```

---

### 7. **Monitorear Señales en Tiempo Real**

**Opción A - Logs Locales:**
```powershell
Get-Content -Path "logs\PRO\eth.csv" -Wait -Tail 5
```

**Opción B - Railway Database:**
```sql
SELECT timestamp, token, direction, entry, tp, sl, confidence 
FROM signal 
ORDER BY timestamp DESC 
LIMIT 10;
```

---

## 🔮 FUTURO: Múltiples Estrategias

Para manejar múltiples estrategias simultáneas:

1. **Priorización:** Añadir campo `priority` a `StrategyConfig`
2. **Deduplicación:** Si 2 estrategias dan señal del mismo token/dirección, tomar la de mayor confidence
3. **Diversificación:** Limitar máximo X señales por token en ventana de tiempo
4. **Dashboard:** Mostrar performance por estrategia individual

---

## 🧪 JESSE: Refinamiento de Estrategias

Plan para integrar Jesse:

1. **Backtest Masivo:** Correr Donchian V2 en múltiples timeframes (15m, 1h, 4h, 1d)
2. **Optimización Genética:** Usar `jesse optimize` para encontrar mejores parámetros
3. **Walk-Forward Testing:** Validar en datos out-of-sample
4. **Portfolio:** Combinar múltiples estrategias descorrelacionadas

**Próximo paso con Jesse:**
- Exportar datos históricos a formato Jesse
- Crear estrategia Jesse equivalente a Donchian V2
- Optimizar parámetros (period, ATR multipliers, EMA length)
- Validar en 2024-2025 (datos no vistos en backtest original)

---

## ✅ CHECKLIST

- [ ] Obtener URL pública de Railway
- [ ] Actualizar `.env`
- [ ] Verificar conexión: `python -c "from database import SessionLocal; print('OK')"`
- [ ] Ejecutar `setup_strategies.py`
- [ ] Ejecutar `disable_old_strategies.py`
- [ ] Limpiar logs locales
- [ ] Arrancar scheduler
- [ ] Verificar primera señal generada (esperar ~1h para timeframe 1h)

---

**¿Listo para empezar?** 🚀
