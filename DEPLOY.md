# 🚀 TraderCopilot - Guía de Despliegue en Railway

## 📋 Requisitos Previos

1. **Cuenta de GitHub** - Para subir el código
2. **Cuenta de Railway** - Crear en [railway.app](https://railway.app)
3. **API Key de DeepSeek** - Obtener en [platform.deepseek.com](https://platform.deepseek.com)

---

## 🎯 Paso 1: Subir el Código a GitHub

### Opción A: Crear Repositorio Nuevo

```bash
cd c:\Users\lukx\Desktop\TraderCopilot
git init
git add .
git commit -m "Initial commit - TraderCopilot"
```

Luego en GitHub:
1. Ir a [github.com/new](https://github.com/new)
2. Crear repositorio llamado `TraderCopilot`
3. NO marcar "Initialize with README"
4. Copiar la URL del repo (ej: `https://github.com/TU_USUARIO/TraderCopilot.git`)

```bash
git remote add origin https://github.com/TU_USUARIO/TraderCopilot.git
git branch -M main
git push -u origin main
```

---

## 🚂 Paso 2: Desplegar Backend en Railway

1. **Ir a [railway.app](https://railway.app)** y hacer login con GitHub

2. **Crear Nuevo Proyecto**:
   - Click en "New Project"
   - Seleccionar "Deploy from GitHub repo"
   - Elegir el repositorio `TraderCopilot`
   - Railway detectará automáticamente el backend

3. **Configurar Root Directory**:
   - En Settings → Service Settings
   - Root Directory: `backend`
   - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

4. **Añadir Base de Datos PostgreSQL**:
   - Click en "+ New" → "Database" → "Add PostgreSQL"
   - Railway creará automáticamente la variable `DATABASE_URL`

5. **Configurar Variables de Entorno**:
   - Ir a "Variables" tab
   - Añadir:
     - `DEEPSEEK_API_KEY` = tu_api_key_aquí
     - `DEEPSEEK_MODEL` = deepseek-chat
     - `EXCHANGE_ID` = binance

6. **Deploy**:
   - Railway desplegará automáticamente
   - Esperar a que el deploy termine (2-3 minutos)
   - Copiar la URL pública (ej: `https://tradercopilot-backend.up.railway.app`)

---

## 🌐 Paso 3: Desplegar Frontend en Vercel

1. **Ir a [vercel.com](https://vercel.com)** y hacer login con GitHub

2. **Importar Proyecto**:
   - Click en "Add New..." → "Project"
   - Seleccionar el repositorio `TraderCopilot`
   - Framework Preset: Vite
   - Root Directory: `web`

3. **Configurar Variables de Entorno**:
   - En "Environment Variables" añadir:
     - `VITE_API_BASE_URL` = `https://TU-BACKEND.up.railway.app`
     - (Usar la URL que copiaste de Railway)

4. **Deploy**:
   - Click en "Deploy"
   - Esperar 1-2 minutos
   - Tu app estará en `https://tradercopilot.vercel.app`

---

## ✅ Paso 4: Verificar que Todo Funciona

1. **Abrir tu app**: `https://tradercopilot.vercel.app`
2. **Generar una señal LITE** para ETH
3. **Verificar en Railway**:
   - Ir a tu servicio backend
   - Click en "Deployments" → "View Logs"
   - Deberías ver: `[DB] ✅ Señal guardada: LITE - ETH - ...`

---

## 🔧 Comandos Útiles

### Ver logs del backend:
```bash
# En Railway Dashboard → Tu Servicio → View Logs
```

### Actualizar el código:
```bash
git add .
git commit -m "Actualización"
git push
# Railway y Vercel se actualizarán automáticamente
```

### Ver base de datos:
```bash
# En Railway Dashboard → PostgreSQL → Data
```

---

## 🆘 Solución de Problemas

### Backend no arranca:
- Verificar logs en Railway
- Asegurarse de que `DEEPSEEK_API_KEY` esté configurada
- Verificar que PostgreSQL esté conectado

### Frontend no conecta con Backend:
- Verificar que `VITE_API_BASE_URL` apunte a la URL correcta de Railway
- Verificar CORS en los logs del backend

### Base de datos vacía:
- Generar una señal desde el frontend
- Verificar logs: `[DB] ✅ Señal guardada`
- Si no aparece, revisar logs de errores

---

## 📊 Monitoreo

- **Railway**: Ver uso de recursos y logs en tiempo real
- **Vercel**: Ver analytics y performance
- **Uptime**: Railway tiene 500 horas gratis/mes (suficiente para 24/7)

---

## 💰 Costos

- **Railway**: Gratis (500 horas/mes)
- **Vercel**: Gratis (ilimitado para hobby)
- **Total**: $0/mes 🎉

---

¿Necesitas ayuda? Revisa los logs en Railway/Vercel o contacta al equipo.
