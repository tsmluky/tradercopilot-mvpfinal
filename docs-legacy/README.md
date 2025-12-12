# 📈 TraderCopilot

**Asistente de Trading con IA** - Análisis técnico, señales automatizadas y gestión de riesgo impulsado por DeepSeek AI.

![Status](https://img.shields.io/badge/status-active-success.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

---

## 🌟 Características

- **🤖 Análisis LITE**: Señales automáticas basadas en indicadores técnicos (RSI, EMA, MACD)
- **🧠 Análisis PRO**: Análisis profundo de mercado con IA (DeepSeek)
- **⚖️ Risk Advisor**: Asesor de riesgo interactivo con chat en tiempo real
- **📊 Gráficos en Tiempo Real**: Visualización de precios con Recharts
- **💾 Persistencia**: Base de datos PostgreSQL/SQLite para histórico de señales
- **📱 PWA Ready**: Funciona como app móvil (instalable)

---

## 🚀 Inicio Rápido (Desarrollo Local)

### Requisitos

- Python 3.11+
- Node.js 18+
- API Key de DeepSeek ([obtener aquí](https://platform.deepseek.com))

### 1. Clonar el Repositorio

```bash
git clone https://github.com/tsmluky/TraderCopilot.git
cd TraderCopilot
```

### 2. Configurar Backend

```bash
cd backend
cp .env.example .env
# Editar .env y añadir tu DEEPSEEK_API_KEY
pip install -r requirements.txt
```

### 3. Configurar Frontend

```bash
cd ../web
npm install
```

### 4. Iniciar Aplicación

**Opción A: Script Automático (Windows)**
```bash
cd ..
.\start.bat
```

**Opción B: Manual**
```bash
# Terminal 1 - Backend
cd backend
pwsh tools/start_dev.ps1 -Port 8010

# Terminal 2 - Frontend
cd web
npm run dev
```

Abrir: `http://localhost:5173`

---

## 🌐 Despliegue en Producción

Ver guía completa en **[DEPLOY.md](./DEPLOY.md)**

### Resumen Rápido

1. **Backend → Railway** (gratis, 500h/mes)
   - PostgreSQL incluido
   - Deploy automático desde GitHub

2. **Frontend → Vercel** (gratis, ilimitado)
   - Deploy automático desde GitHub
   - SSL/HTTPS incluido

**Costo total: $0/mes** 🎉

---

## 📁 Estructura del Proyecto

```
TraderCopilot/
├── backend/              # FastAPI + Python
│   ├── main.py          # API principal
│   ├── database.py      # Configuración DB
│   ├── models_db.py     # Modelos SQLAlchemy
│   ├── deepseek_client.py  # Cliente IA
│   ├── indicators/      # Indicadores técnicos
│   └── logs/            # Logs CSV (backup)
│
├── web/                 # React + Vite + TypeScript
│   ├── src/
│   │   ├── components/  # Componentes UI
│   │   ├── services/    # API client
│   │   ├── pages/       # Páginas
│   │   └── types/       # TypeScript types
│   └── public/
│
├── DEPLOY.md           # Guía de despliegue
└── README.md           # Este archivo
```

---

## 🛠️ Tecnologías

### Backend
- **FastAPI** - Framework web moderno
- **SQLAlchemy** - ORM para PostgreSQL/SQLite
- **CCXT** - Datos de mercado en tiempo real
- **TA-Lib** - Indicadores técnicos
- **DeepSeek** - Modelo de lenguaje (LLM)

### Frontend
- **React 19** - UI library
- **Vite** - Build tool
- **TypeScript** - Type safety
- **Recharts** - Gráficos
- **TailwindCSS** - Styling
- **React Router** - Navegación

---

## 📊 Uso

### 1. Análisis LITE (Rápido)
- Selecciona token (ETH, BTC, SOL, XAU)
- Selecciona timeframe (30m, 1h, 4h)
- Click en "LITE" → Señal instantánea

### 2. Análisis PRO (IA)
- Mismo proceso que LITE
- Click en "PRO" → Análisis profundo con IA
- Incluye: contexto de mercado, análisis técnico, plan de trading

### 3. Risk Advisor (Chat)
- Introduce parámetros de tu posición
- Click en "ADVISOR" → Chat interactivo
- Pregunta sobre riesgo, ajustes, escenarios

---

## 🔐 Variables de Entorno

### Backend (.env)
```env
DEEPSEEK_API_KEY=sk-xxxxx
DEEPSEEK_MODEL=deepseek-chat
EXCHANGE_ID=binance
```

### Frontend (.env.local)
```env
VITE_API_BASE_URL=http://127.0.0.1:8010
```

---

## 📝 Licencia

MIT License - Ver [LICENSE](LICENSE) para más detalles.

---

## 🤝 Contribuir

Las contribuciones son bienvenidas! Por favor:

1. Fork el proyecto
2. Crea una rama (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

---

## 📧 Contacto

¿Preguntas? Abre un [issue](https://github.com/TU_USUARIO/TraderCopilot/issues)

---

**⚠️ Disclaimer**: Esta herramienta es solo para fines educativos. No constituye asesoramiento financiero. Opera bajo tu propio riesgo.
