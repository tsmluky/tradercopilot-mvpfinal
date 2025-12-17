# A-01: Matriz de Alineación (Promesa vs Realidad)

**Objetivo:** Auditar el estado real de cada feature visible o prometida.
**Prioridad:** P0 (Demo) > P1 (Sale) > P2 (Future)

## Feature Audit

| Feature / Pantalla | Endpoint / Archivo | Estado | Evidencia | Acción (Fix/Hide/Kill) | Prioridad |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Login / Auth** | `LoginPage.tsx` -> `/auth/token` | **Partial** | Dev Bypass activo, no valida password real si no hay DB. | Fix Bypass (M2) | P0 |
| **Dashboard** | `Dashboard.tsx` -> `/logs` | **OK** | Carga logs y calcula stats localmente. | - | P0 |
| **Live Feed (Scanner)** | `ScannerPage.tsx` -> `/logs/recent` | **OK** | Backend `logs.py` sirve datos. | - | P0 |
| **Signal Details** | `StrategyDetailsPage.tsx` | **Partial** | Falta botón "Simulate" (Paper Trading). | Hide "Delete" (User shouldn't del), Add Simulate later | P0 |
| **Paper Trading** | N/A | **Missing** | No hay `routers/paper.py` ni tablas `paper_orders`. | Implementar Backend (M4) | P1 |
| **Backtesting** | `routers/backtest.py` | **OK/Partial** | Existe endpoint `/backtest/run`. | Check UI connection | P2 |
| **Analysis (Pro)** | `/analyze/pro` | **OK** | Determinista (sin LLM real aún). | Connect Lazy LLM later | P1 |
| **Advisor Chat** | `/analyze/advisor/chat` | **OK** | Stub / DeepSeek integration ready. | - | P1 |
| **Logs View** | `LogsPage.tsx` | **OK** | Funcional. | - | P1 |
| **Leaderboard** | `LeaderboardPage.tsx` | **Mock** | `api.ts` retorna datos hardcoded. | **KILL / HIDE** (Feature compleja para MVP) | P2 |
| **Membership** | `MembershipPage.tsx` | **BROKEN** | `api.upgradeSubscription` no existe en `api.ts`. | **HIDE** until Stripe integration (M3) | P2 |
| **Settings** | `SettingsPage.tsx` | **Partial** | Ping Telegram funciona. Profile read-only. | - | P2 |

## Zombie / Kill List Candidates
1.  **Leaderboard**: "Global Trader Ranking" es fake. Mejor ocultar para venta a menos que se implemente rápido. -> **Propuesta: HIDE**.
2.  **Membership**: Botones de Upgrade no hacen nada. -> **Propuesta: HIDE or "Coming Soon" toast**.
3.  **Strategy Details -> DELETE AGENT**: Peligroso. Un usuario no debería borrar estrategias del sistema. -> **Propuesta: KILL**.

## Notes
- **Critical Gap for Sale**: Login is too weak (dev bypass). Paper Trading (the "Wow" factor) is missing completely.
- **Good News**: Core loop (Signals -> Dashboard -> Logs) works well.
