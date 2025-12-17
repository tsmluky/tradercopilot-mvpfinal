# A-02: Demo Path (Guion Oficial)

**Objetivo:** Demo replicable en 3-5 minutos sin errores visibles.
**Setup:** `python backend/seed_strategies.py` (o equivalente) para tener logs frescos.

## 1. Login "Institucional"
*   **Acción:** Ir a `/login`.
*   **Input:** User: `demo@tradercopilot.com`, Pass: `demo`.
*   **Narrativa:** "El sistema tiene autenticación segura. Entramos como 'Analista Institucional'."
*   **Check:** Redirección rápida al Dashboard.

## 2. Dashboard & Radar (The "Hook")
*   **Acción:** Aterrizar en `/dashboard`.
*   **Narrativa:** "Este es el Mission Control. A la izquierda, métricas de rendimiento en tiempo real. Abajo, el Live Feed de anomalías."
*   **Demo:**
    *   Clic en una señal reciente (ej: ETH Scalp).
    *   Se abre el **Tactical Drawer** (si funciona) o redirige a Details.
    *   Mostrar métrica "Win Rate Last 24h".

## 3. Análisis Táctico (Scanner)
*   **Acción:** Navegar a **Scanner** (Radar icon).
*   **Narrativa:** "Nuestro motor procesa cientos de pares. Aquí filtramos solo ALTA probabilidad."
*   **Demo:**
    *   Clic en el botón **Refresh**.
    *   Explicar una tarjeta de señal (Token, Confianza, Dirección).
    *   Clic en **Analyze** en una tarjeta.

## 4. Deep Dive Analysis (Pro)
*   **Acción:** En la vista de análisis (Drawer o Page).
*   **Narrativa:** "No solo es detección técnica. La IA 'Pro Analyst' lee el contexto."
*   **Demo:**
    *   Ver el texto generado en "Rationale".
    *   Mencionar "Sentiment" y "Market Structure".

## 5. Cierre (Logs & Transparency)
*   **Acción:** Navegar a **Logs**.
*   **Narrativa:** "Todo queda registrado. Inmutable. Auditabilidad total."
*   **Demo:**
    *   Filtrar por ETH.
    *   Mostrar una señal "WIN" (verde).

## 6. (Opcional) Settings
*   **Acción:** Settings -> Ping Telegram.
*   **Narrativa:** "Alertas instantáneas a móvil."

---

## 🚫 Zonas Prohibidas (No entrar en demo)
1.  **Leaderboard**: Datos falsos.
2.  **Membership**: Botones de pago no funcionan.
3.  **Strategy Details -> Delete**: Puede romper el backend.
