# Prompt para Rediseño del Frontend de TraderCopilot

**Rol**: Eres un Senior Frontend Engineer y UX/UI Designer experto en aplicaciones financieras y dashboards de trading.

**Objetivo**: Transformar el frontend actual de TraderCopilot (React + Vite) en un Dashboard de Trading de nivel institucional, visualmente impactante y funcionalmente robusto.

**Contexto**:
Tenemos un backend potente que genera señales con 3 estrategias principales:
1. **BB Mean Reversion (1h)**: 71% Win Rate (La joya de la corona).
2. **BB Mean Reversion (15m)**: Alta frecuencia.
3. **Donchian Breakout (4h)**: Swing trading.
4. **RSI Divergence (1h)**: Alta precisión.

Necesitamos que el frontend refleje la calidad de estas estrategias.

---

## 🎨 Requerimientos de Diseño (Look & Feel)

1.  **Tema**: "Cyberpunk Finance" o "Institutional Dark".
    *   Fondo: Oscuro profundo (`#0f172a` o similar).
    *   Acentos: Verde Neón (`#10b981`) para WIN/LONG, Rojo Neón (`#ef4444`) para LOSS/SHORT, Azul Eléctrico (`#3b82f6`) para Info/Neutral.
    *   Superficies: Glassmorphism sutil (transparencia + blur) para tarjetas y paneles.
    *   Tipografía: `Inter` o `JetBrains Mono` para datos numéricos.

2.  **Layout**:
    *   **Sidebar**: Navegación (Dashboard, Signals, Strategies, Settings).
    *   **Header**: Estado del sistema (Scheduler Status: 🟢 Running), Precio de BTC/ETH en tiempo real (ticker).
    *   **Main Content**: Grid responsive.

---

## 🛠️ Funcionalidades a Implementar

### 1. Dashboard Home (Vista Principal)
Quiero ver de un vistazo cómo va mi dinero/sistema.
*   **KPI Cards (Top Row)**:
    *   Total Signals (24h).
    *   Global Win Rate (%).
    *   Total PnL (R-Multiple).
    *   Active Strategies (3/9).
*   **Performance Chart**: Un gráfico de línea simple mostrando el PnL acumulado en el tiempo.
*   **Live Signals Feed**: Lista compacta de las últimas 5 señales generadas.

### 2. Strategies View (Nueva Página)
Una vista dedicada a mostrar el "menú" de estrategias disponibles.
*   **Strategy Cards**: Cada estrategia (BB Mean Rev, Donchian, etc.) tiene su tarjeta.
    *   Nombre y Timeframe (ej: "BB Mean Reversion • 1h").
    *   Badge de Estado: "Active" (Verde) o "Standby" (Gris).
    *   Mini-sparkline o métrica clave (ej: "71% WR").
    *   Botón "View Details" (para ver logs específicos de esa estrategia).

### 3. Signals Table (Mejorada)
La tabla actual es muy básica. Necesitamos:
*   **Columnas**: Time, Token (con icono), Strategy, Type (LONG/SHORT), Entry, TP/SL, Confidence (Barra de progreso), Status (OPEN/WIN/LOSS).
*   **Filtrado**: Por Token, Por Estrategia, Por Resultado.
*   **Visuals**:
    *   LONG = Texto Verde / Flecha Arriba.
    *   SHORT = Texto Rojo / Flecha Abajo.
    *   Confidence > 0.8 = Resaltado brillante.

### 4. Componentes Reutilizables
*   `StatusBadge`: Para mostrar WIN/LOSS/OPEN con estilo.
*   `TrendIcon`: Flechas dinámicas.
*   `ConfidenceMeter`: Una barrita visual de 0 a 100%.

---

## 💻 Instrucciones Técnicas

1.  Usa **Tailwind CSS** para todo el estilizado.
2.  Usa **Lucide React** para iconos.
3.  Usa **Recharts** o **Lightweight Charts** para los gráficos.
4.  Mantén la estructura de carpetas actual (`web/src/components`, `web/src/pages`).
5.  Crea un nuevo componente `Layout.tsx` para manejar el Sidebar/Header común.
6.  Conecta con la API existente (`/api/signals`, `/api/strategies`). *Nota: Si faltan endpoints, simula los datos por ahora o pide crearlos.*

---

## 🚀 Primer Paso: El Dashboard
Empieza creando el layout principal y la vista de "Dashboard Home" con los KPI Cards y la tabla de señales recientes mejorada.

**Entregable**: Código modificado de `App.tsx` y nuevos componentes en `src/components/dashboard/`.
