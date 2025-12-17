Milestone M0 — Reality Check & Demo Path (Reality & Hardening)
A-01 Matriz de Alineación (Promesa vs Realidad)

Objetivo: listar features prometidas vs estado real y decidir acción.
Entregable: docs/alignment_matrix.md

Contenido mínimo:

Feature / Pantalla / Endpoint

Estado (OK / Parcial / Roto / No existe)

Evidencia (link a archivo o endpoint)

Acción (Fix / Hide / Remove / Defer)

Prioridad (P0 demo / P1 sale / P2 post-sale)

DoD:

100% de features visibles en UI y landing están auditadas.

Toda feature “Rota” tiene acción asignada (Kill/Hide/Fix).

A-02 Demo Path (guion exacto de demo)

Objetivo: demo replicable en 3–5 minutos.
Entregable: docs/demo_path.md

Incluye:

Paso a paso (login → dashboard → ver señales → detalle → paper trade opcional si existe)

Datos necesarios (qué tokens, qué timeframe, qué usuario)

“Recovery path” (qué hacer si falla un endpoint)

DoD:

Cualquier persona técnica lo ejecuta en local en <10 min de setup.

Demo completa sin depender de datos externos frágiles (usa seed mínimo).

A-03 Kill List / Zombie Removal

Objetivo: eliminar/hide botones/pantallas que no funcionan.
Entregable: PR “kill-list”.

DoD:

No quedan CTAs que lleven a pantallas rotas.

Los flags/links a features “post-sale” quedan etiquetados como “Coming soon” (sin navegación a rutas rotas).

A-04 Seed mínimo adelantado (para soportar demo desde ya)

Objetivo: la demo no depende de “hoy hay señales”.
Entregable: scripts/seed_demo_data.py (o .ps1 si aplica) que puebla DB con 20–50 registros realistas.

DoD:

seed_demo_data deja datos visibles en dashboard y logs.

Existe scripts/reset_db (borrar y sembrar) para resetear antes de demos.

Milestone M1 — Core Hardening (DB + Idempotencia + Scheduler)
B-01/B-02 DB Schema Review (models_db.py)

Objetivo: garantizar campos mínimos para signals, users, runs.
Acción: revisión de models_db.py + migraciones.

Checklist recomendado (mínimo):

User: id, email, password_hash (o provider), created_at

Signal: id, user_id, token, mode, timeframe, signal_time (o candle_time), payload/summary, created_at

(Opcional pero útil) SchedulerRun: id, started_at, finished_at, status, notes

DoD:

Migraciones existen (Alembic o equivalente).

DB puede recrearse desde cero con migrate + seed.

B-04 Idempotencia real: UniqueConstraint + idempotency_key

Objetivo: no duplicar señales por reintentos, reboots o doble scheduler.
Implementación recomendada:

Añadir columna idempotency_key (string) en Signal.

Calcular key determinística (hash) con: user_id|token|mode|timeframe|signal_time (y strategy_id si existe).

UNIQUE(idempotency_key).

DoD:

Insertar la misma señal 2 veces no crea duplicado.

Se valida con test manual/script: ejecutar ingest 2 veces → count no cambia.

Hay logs: “duplicate ignored” vs “inserted”.

B-05 Logger Upsert (UPSERT / INSERT OR IGNORE)

Objetivo: el logger no rompe y respeta idempotencia.
Acción: modificar log_signal() para usar UPSERT/IGNORE según DB.

DoD:

log_signal nunca genera excepción por duplicado (manejo limpio).

Registra resultado: inserted/ignored/updated.

B-06 Scheduler Lock robusto (DB lock con TTL)

Objetivo: evitar múltiples instancias del scheduler en multi-replica o restarts.
Implementación (preferida):

Tabla scheduler_lock:

lock_name (PK)

owner_id (uuid/string)

expires_at (datetime)

updated_at

Algoritmo:

Acquire: UPDATE ... WHERE expires_at < now OR owner_id = mine

Set expires_at = now + TTL (ej 60s)

Heartbeat: refresh cada 30s

Release: set expires_at = now (o delete)

DoD:

Si se levantan 2 instancias, solo una ejecuta jobs.

Si el proceso muere, el lock expira y otra instancia toma control.

Logs explícitos de lock.

B-07 Health/Ready + errores centralizados (observabilidad mínima)

Objetivo: evitar demos a ciegas y facilitar soporte.
Entregables:

/health (OK si app viva)

/ready (OK si DB accesible + migraciones ok)

middleware de request_id + logging de latencias

DoD:

Health endpoints devuelven estado real (no hardcoded).

Errores devuelven JSON consistente; frontend muestra mensaje legible.

Milestone M2 — Security & SaaS Minimum
C-01 Auth end-to-end (Frontend + Backend)

Objetivo: login funcional y persistencia de sesión.
DoD:

Login funciona en local y en deploy.

Refresh / token persistence (según arquitectura) sin “logout silencioso”.

C-02 JWT Middleware en endpoints críticos

Scope mínimo:

Proteger: /analyze, /signals, /paper/*, endpoints de historial.

Permitir públicos: /health, /ready, /pricing (frontend).

DoD:

Sin token → 401 consistente.

Con token → acceso correcto.

C-03 User Isolation (multi-tenant lite)

Objetivo: un usuario no ve datos de otro.
DoD:

Todas las queries de señales/historial filtran por user_id.

Test manual: seed con 2 usuarios → cada uno ve solo lo suyo.

C-04 Rate limiting + request limits (mínimo anti-abuso)

Objetivo: evitar abuso trivial.
DoD:

Rate limit en login y analyze.

Límite tamaño payload (ej. 64KB) y timeouts en llamadas externas.

Milestone M3 — Monetización (mínima para venta)
D-01 Pricing Page (estática)

Objetivo: narrativa comercial y conversión.
DoD:

Página /pricing clara con tiers, límites, CTA.

CTA conduce a “Contact / Join waitlist / Buy” (según estrategia actual).

Milestone M4 — Paper Trading (mínimo impecable)
E-01/E-02 Paper Trading Engine (simple, no broker completo)

Scope mínimo:

Abrir/cerrar posición simulada

PnL estimado

Fees según reglas definidas (si aplica)

Persistencia en DB

DoD:

5 trades demo reproducibles con seed.

No hay estados corruptos (ej: cerrar trade inexistente).

Milestone M5 — Admin Owner Panel (simple)
F-01 Admin básico

Scope mínimo:

ver usuarios

ver señales totales / últimas señales

ver estado del scheduler lock / últimas ejecuciones

DoD:

Solo accesible a owner (flag/rol).

Útil para demo y para comprador.

Milestone M6 — Packaging final (sale-ready)
G-01 Seed Data “realista” (versión final)

Objetivo: base demo impecable.
DoD:

Script idempotente (puede correr varias veces sin duplicar).

Dataset razonable por token/timeframe/mode.

G-02 “Buyer Package”

Entregables:

README sale-ready (setup, deploy, env vars)

arquitectura (1 diagrama)

lista de “opportunities post-sale” (scope controlado)

DoD:

Un tercero puede levantarlo en <30 min con instrucciones.

Orden exacto de ejecución recomendado (PRs)

PR0: docs/alignment_matrix.md + docs/demo_path.md

PR1: Kill List (hide/remove zombies)

PR2: Seed mínimo + reset scripts (para demo inmediata)

PR3: DB migrations + idempotency_key + UniqueConstraint

PR4: log_signal UPSERT/IGNORE

PR5: DB scheduler lock con TTL + logs

PR6: health/ready + middleware errores

PR7: Auth/JWT + user isolation

PR8: rate limiting + request limits

PR9: pricing page

PR10: paper trading mínimo

PR11: admin panel básico

PR12: buyer package final

Notas de control de alcance (anti-scope creep)

No agregar estrategias nuevas.

No ejecución real en exchanges (paper only).

No backtesting heavy como parte del sale-ready.

No “marketplace” complejo: solo configuración y narrativa.