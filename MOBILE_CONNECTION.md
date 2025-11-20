# 📱 Guía Rápida: Conectar desde Móvil

## 🚨 Problema: "No puedo conectarme desde mi móvil"

### ✅ Solución Rápida: Usa Ngrok (Recomendado)

**Ngrok** crea un túnel de internet que hace tu app accesible desde CUALQUIER lugar:
- ✅ No necesitas misma WiFi
- ✅ Funciona con datos móviles (4G/5G)
- ✅ Puedes compartir con otros testers
- ✅ HTTPS automático (necesario para PWA en iOS)

---

## 🚀 Paso a Paso con Ngrok

### 1. Asegúrate de que tus servidores están corriendo

Deberías tener:
- ✅ Backend en puerto 8010
- ✅ Frontend en puerto 5173 (o 3000)

### 2. Ejecuta el script de acceso móvil

```bash
mobile-access.bat
```

Este script:
1. Te muestra tu IP local
2. Abre 2 túneles de Ngrok (frontend + backend)
3. Te da las URLs públicas

### 3. Copia las URLs de Ngrok

Verás algo como:
```
Frontend: https://abc123.ngrok.io -> http://localhost:5173
Backend:  https://xyz789.ngrok.io -> http://localhost:8010
```

### 4. Actualiza la URL del backend

Edita `web/src/services/api.ts`:

```typescript
// Línea ~3
const API_BASE_URL = 'https://xyz789.ngrok.io';  // ← Usa tu URL de ngrok
```

### 5. Reinicia el frontend

```bash
# Ctrl+C para detener
# Luego:
npm run dev -- --host
```

### 6. Abre la URL del frontend en tu móvil

```
https://abc123.ngrok.io
```

¡Listo! Funciona desde cualquier lugar 🎉

---

## 🔧 Opción Alternativa: Misma WiFi

Si prefieres no usar Ngrok:

### 1. Encuentra tu IP

```bash
ipconfig
```

Busca: `IPv4 Address: 192.168.1.XXX`

### 2. Verifica que el frontend está con --host

```bash
npm run dev -- --host
```

### 3. Abre en tu móvil (misma WiFi)

```
http://192.168.1.XXX:5173
```

### 4. Si no funciona:

**Desactiva temporalmente el Firewall de Windows:**
1. Windows Security → Firewall & network protection
2. Domain/Private/Public network → OFF (temporalmente)
3. Intenta de nuevo

O **Añade regla al firewall:**
```bash
# Como administrador:
netsh advfirewall firewall add rule name="Vite Dev Server" dir=in action=allow protocol=TCP localport=5173
netsh advfirewall firewall add rule name="FastAPI Backend" dir=in action=allow protocol=TCP localport=8010
```

---

## 🎯 Comparación

| Método | Pros | Contras |
|--------|------|---------|
| **Ngrok** | ✅ Funciona desde cualquier lugar<br>✅ HTTPS gratis<br>✅ Fácil de compartir | ⚠️ URL cambia cada vez<br>⚠️ Requiere cuenta (gratis) |
| **Misma WiFi** | ✅ Más rápido<br>✅ Sin dependencias | ⚠️ Solo misma red<br>⚠️ Problemas con firewall |

---

## 🐛 Troubleshooting

### "Ngrok dice 'command not found'"
```bash
npm install -g ngrok
```

### "Ngrok pide autenticación"
1. Crea cuenta gratis en https://ngrok.com
2. Copia tu authtoken
3. Ejecuta:
```bash
ngrok config add-authtoken TU_TOKEN_AQUI
```

### "El backend no responde"
Asegúrate de actualizar `API_BASE_URL` en `web/src/services/api.ts` con la URL de ngrok del backend.

### "La app carga pero no hay datos"
1. Verifica que ambos túneles están activos (frontend Y backend)
2. Revisa la consola del navegador (F12) para errores
3. Asegúrate de que la URL del backend es correcta

---

## 📝 Checklist

```
[ ] Ngrok instalado (npm install -g ngrok)
[ ] Backend corriendo (puerto 8010)
[ ] Frontend corriendo (puerto 5173)
[ ] Túnel de ngrok para frontend creado
[ ] Túnel de ngrok para backend creado
[ ] API_BASE_URL actualizada en api.ts
[ ] Frontend reiniciado
[ ] URL abierta en móvil
[ ] App funciona correctamente
```

---

## 💡 Tip Pro

**Guarda tus URLs de Ngrok** mientras testeas:
```
Frontend: https://abc123.ngrok.io
Backend:  https://xyz789.ngrok.io
```

Si cierras y vuelves a abrir ngrok, las URLs cambiarán y tendrás que actualizar `api.ts` de nuevo.

Para URLs permanentes, necesitas **Ngrok Pro** ($8/mes) o **deploy a producción** (Vercel/Railway).

---

**¿Funcionó? ¡Ahora puedes testear desde cualquier lugar! 🚀📱**
