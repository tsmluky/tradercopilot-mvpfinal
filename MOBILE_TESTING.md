# 📱 Cómo Testear TraderCopilot en tu Móvil

## ⚡ Opción 1: Red Local (Más Rápido)

### Paso 1: Obtén tu IP local

**Windows:**
```bash
ipconfig
# Busca "IPv4 Address" en tu adaptador WiFi
# Ejemplo: 192.168.1.100
```

**Mac/Linux:**
```bash
ifconfig
# Busca "inet" en tu adaptador WiFi
```

### Paso 2: Inicia los servidores con IP pública

**Backend:**
```bash
cd backend
uvicorn main:app --host 0.0.0.0 --port 8010
```

**Frontend:**
```bash
cd web
npm run dev -- --host
```

### Paso 3: Accede desde tu móvil

1. **Asegúrate** de que tu móvil está en la **misma WiFi**
2. Abre el navegador en tu móvil
3. Ve a: `http://TU_IP:3000`
   - Ejemplo: `http://192.168.1.100:3000`

### Paso 4: Instala como PWA

**Android (Chrome):**
1. Abre la app en Chrome
2. Toca el menú (⋮) arriba a la derecha
3. Toca "Instalar aplicación" o "Añadir a pantalla de inicio"
4. ¡Listo! Aparece el icono en tu home screen

**iOS (Safari):**
1. Abre la app en Safari
2. Toca el botón de compartir (□↑) abajo
3. Desplázate y toca "Añadir a pantalla de inicio"
4. Toca "Añadir"
5. ¡Listo! Aparece el icono en tu home screen

---

## 🌐 Opción 2: Ngrok (Acceso desde Internet)

### Ventajas:
- ✅ Funciona desde cualquier lugar
- ✅ No necesitas estar en la misma WiFi
- ✅ Puedes compartir con otros testers
- ✅ HTTPS automático (necesario para PWA en iOS)

### Paso 1: Instala Ngrok

```bash
# Descarga desde: https://ngrok.com/download
# O instala con npm:
npm install -g ngrok
```

### Paso 2: Inicia los servidores normalmente

```bash
# Terminal 1 - Backend
cd backend
pwsh tools/start_dev.ps1 -Port 8010

# Terminal 2 - Frontend
cd web
npm run dev
```

### Paso 3: Crea túnel con Ngrok

```bash
# Terminal 3 - Ngrok
ngrok http 3000
```

Verás algo como:
```
Forwarding  https://abc123.ngrok.io -> http://localhost:3000
```

### Paso 4: Actualiza la URL del backend

Edita `web/src/services/api.ts`:
```typescript
// Cambia:
const API_BASE_URL = 'http://127.0.0.1:8010';

// Por:
const API_BASE_URL = 'https://abc123.ngrok.io/api';
```

### Paso 5: Crea túnel para backend también

```bash
# Terminal 4
ngrok http 8010
```

Actualiza la URL en `api.ts` con la URL de ngrok del backend.

### Paso 6: Accede desde cualquier dispositivo

Abre `https://abc123.ngrok.io` en cualquier móvil, tablet, o computadora.

---

## 🚀 Opción 3: Deploy a Vercel (Producción)

### Ventajas:
- ✅ URL permanente
- ✅ HTTPS automático
- ✅ CDN global (super rápido)
- ✅ Gratis para proyectos personales

### Paso 1: Instala Vercel CLI

```bash
npm install -g vercel
```

### Paso 2: Deploy frontend

```bash
cd web
vercel --prod
```

Sigue las instrucciones:
- Project name: `tradercopilot`
- Framework: `Vite`
- Build command: `npm run build`
- Output directory: `dist`

### Paso 3: Obtendrás una URL

```
https://tradercopilot.vercel.app
```

### Paso 4: Deploy backend (Railway/Render)

**Opción A - Railway:**
1. Ve a https://railway.app
2. Conecta tu GitHub
3. Deploy `backend/` folder
4. Obtienes: `https://tradercopilot-backend.railway.app`

**Opción B - Render:**
1. Ve a https://render.com
2. Conecta tu GitHub
3. Deploy como "Web Service"
4. Obtienes: `https://tradercopilot-backend.onrender.com`

### Paso 5: Actualiza URLs

En `web/src/services/api.ts`:
```typescript
const API_BASE_URL = 'https://tradercopilot-backend.railway.app';
```

Redeploy frontend:
```bash
cd web
vercel --prod
```

---

## 📊 Qué Testear en Móvil

### Funcionalidad Básica
- [ ] La app carga correctamente
- [ ] Puedes navegar entre páginas
- [ ] Los botones son fáciles de tocar
- [ ] Los formularios funcionan
- [ ] El gráfico se ve bien

### Modos de Análisis
- [ ] LITE: Genera señal rápida
- [ ] PRO: Muestra análisis completo
- [ ] ADVISOR: Chat funciona

### Interacciones Táctiles
- [ ] Scroll suave
- [ ] Zoom en gráficos (si aplica)
- [ ] Botones responden al toque
- [ ] No hay elementos demasiado pequeños

### Performance
- [ ] Carga en < 5 segundos
- [ ] Navegación fluida
- [ ] Sin lag al escribir
- [ ] Gráficos cargan rápido

### PWA
- [ ] Se puede instalar
- [ ] Icono aparece en home screen
- [ ] Abre en pantalla completa
- [ ] Funciona offline (después de primera carga)

---

## 🐛 Problemas Comunes

### "No puedo acceder desde mi móvil"
- ✅ Verifica que estás en la misma WiFi
- ✅ Comprueba que el firewall no bloquea el puerto
- ✅ Usa la IP correcta (no 127.0.0.1)
- ✅ Asegúrate de que los servidores están corriendo

### "El backend no responde"
- ✅ Verifica que el backend está en `0.0.0.0:8010`
- ✅ Comprueba CORS en `backend/main.py`
- ✅ Mira la consola del navegador para errores

### "No puedo instalar la PWA"
- ✅ iOS requiere HTTPS (usa ngrok o deploy)
- ✅ Asegúrate de que `manifest.json` está accesible
- ✅ Verifica que el service worker se registró

### "La app es muy lenta"
- ✅ Comprueba tu conexión WiFi
- ✅ Cierra otras apps en el móvil
- ✅ Limpia caché del navegador

---

## 📝 Feedback a Recopilar

### Usabilidad
- ¿Es fácil de usar en móvil?
- ¿Los botones son suficientemente grandes?
- ¿El texto es legible?
- ¿La navegación es intuitiva?

### Performance
- ¿Qué tan rápido carga?
- ¿Hay lag al usar la app?
- ¿Los gráficos cargan bien?

### Diseño
- ¿Se ve profesional?
- ¿Los colores son agradables?
- ¿Hay elementos que no se ven bien?

### Features
- ¿Qué funcionalidad falta?
- ¿Qué mejorarías?
- ¿Usarías esta app?

---

## 🎯 Checklist de Testing

```
[ ] Accedí desde mi móvil
[ ] Instalé como PWA
[ ] Probé LITE mode
[ ] Probé PRO mode
[ ] Probé ADVISOR mode
[ ] Revisé los logs
[ ] Revisé el dashboard
[ ] Probé en orientación vertical
[ ] Probé en orientación horizontal
[ ] Probé offline (modo avión)
[ ] Compartí feedback
```

---

## 📞 Soporte

Si tienes problemas:
1. Revisa la consola del navegador (F12)
2. Toma screenshot del error
3. Anota los pasos para reproducir
4. Comparte con el equipo de desarrollo

---

**¡Listo para testear en móvil! 📱🚀**
