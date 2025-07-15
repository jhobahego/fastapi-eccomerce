# Guía de Despliegue en Render

Esta guía te ayuda a desplegar tu aplicación FastAPI de e-commerce en Render usando Docker.

## 📋 Pre-requisitos

- [ ] Repositorio subido a GitHub
- [ ] Cuenta en [Render](https://render.com) (gratis)
- [ ] Proyecto configurado con `render.yaml`

## 🚀 Pasos para Desplegar

### 1. Conectar Repositorio

1. Ve a [render.com](https://render.com) e inicia sesión
2. Click en "New +" → "Blueprint"
3. Conecta tu cuenta de GitHub
4. Selecciona el repositorio `fastapi-eccomerce`
5. Render detectará automáticamente el `render.yaml`

### 2. Configurar Variables de Entorno

En el dashboard de Render, ve a tu servicio web y configura estas variables en la sección "Environment":

#### Variables Obligatorias:
```bash
ADMIN_EMAIL=tu_email@example.com
ADMIN_PASSWORD=tu_password_muy_seguro_123
```

#### Variables Recomendadas:
```bash
# CORS para tu frontend
BACKEND_CORS_ORIGINS=["https://tu-frontend.vercel.app", "https://tu-dominio.com"]

# Configuración opcional de email (si tienes SMTP)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=tu_email@gmail.com
SMTP_PASSWORD=tu_contraseña_de_aplicacion
EMAILS_FROM_EMAIL=noreply@tudominio.com
```

### 3. Variables Automáticas (Render las configura)

✅ **No necesitas configurar estas variables, Render las maneja automáticamente:**

- `DATABASE_URL` - Conexión a PostgreSQL
- `SECRET_KEY` - Clave de seguridad generada
- `PORT` - Puerto dinámico de Render
- `RENDER_EXTERNAL_HOSTNAME` - Hostname de tu app
- `RENDER_EXTERNAL_URL` - URL completa de tu app

## 🎯 Verificación del Despliegue

### URLs de tu aplicación:
- **API Principal**: `https://tu-app.onrender.com`
- **Documentación Swagger**: `https://tu-app.onrender.com/docs`
- **API v1**: `https://tu-app.onrender.com/api/v1`
- **ReDoc**: `https://tu-app.onrender.com/redoc`

### Verificar que funciona:
1. Visita `https://tu-app.onrender.com/docs`
2. Deberías ver la documentación interactiva de la API
3. Intenta hacer login con las credenciales del admin

## 🔧 Configuración del Proyecto

### Archivos importantes para Render:

- `render.yaml` - Configuración de servicios
- `Dockerfile` - Imagen de la aplicación
- `scripts/render-deploy.sh` - Script de inicialización
- `.dockerignore` - Archivos excluidos del build

### Lo que hace el deploy automáticamente:

1. ✅ Crea base de datos PostgreSQL gratuita
2. ✅ Construye imagen Docker de la aplicación
3. ✅ Ejecuta migraciones de Alembic
4. ✅ Ejecuta script de seed para datos iniciales
5. ✅ Inicia la aplicación con 4 workers

## 🐛 Troubleshooting

### Error de migración:
```bash
# Verifica logs en Render dashboard
# Asegúrate de que DATABASE_URL esté configurada
```

### Error de variables de entorno:
```bash
# Verifica que ADMIN_EMAIL y ADMIN_PASSWORD estén configurados
# en la sección Environment del dashboard
```

### Error de CORS:
```bash
# Agrega tu dominio frontend a BACKEND_CORS_ORIGINS:
# BACKEND_CORS_ORIGINS=["https://tu-frontend.com"]
```

### Aplicación no inicia:
```bash
# Revisa los logs en el dashboard de Render
# Verifica que el puerto esté correctamente configurado
```

## 📊 Monitoreo

En el dashboard de Render puedes:

- 📈 **Métricas**: CPU, memoria, requests
- 📋 **Logs**: Logs en tiempo real de la aplicación  
- 🔄 **Deploy**: Historial de deployments
- ⚙️ **Settings**: Configuración de variables de entorno

## 🔒 Seguridad en Producción

✅ **Configurado automáticamente:**
- Variables de entorno no están en el código
- Secrets no están en el repositorio
- PostgreSQL con SSL
- Aplicación con usuario no-root

⚠️ **Asegúrate de:**
- Usar contraseña segura para `ADMIN_PASSWORD`
- Configurar CORS solo para tus dominios
- Mantener `DEBUG=false` en producción

## 🚀 Actualizaciones

Para actualizar la aplicación:

1. Haz push a tu repositorio de GitHub
2. Render automáticamente detectará los cambios
3. Realizará un nuevo deploy automáticamente
4. No hay downtime (zero-downtime deployment)

---

¿Necesitas ayuda? Revisa los logs en el dashboard de Render o consulta la [documentación oficial](https://render.com/docs).
