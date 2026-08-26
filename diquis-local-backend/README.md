# 🧠 Diquis Backend (API & Lógica de Negocio)

¡Bienvenido a los cerebros de la operación! 

Esta API está construida con **FastAPI** (Python) y **SQLAlchemy**. Su propósito didáctico es enseñarte cómo se estructura un backend financiero moderno: rápido, asíncrono y seguro.

Aquí aprenderás cómo implementamos un sistema de **Zero-Trust (Cero Confianza)**: en lugar de enviar tokens JWT que el Frontend almacena en lugares vulnerables (como LocalStorage), este backend inyecta los tokens directamente en tu navegador usando **Cookies HttpOnly**. ¡Un patrón de seguridad indispensable para aplicaciones modernas!

---

## ⚡ Guía de Ejecución

> **Importante:** La base de datos debe estar configurada en Windows primero. Para instrucciones sobre la base de datos, revisa el README en la carpeta `diquis-local-database`.

### Paso 1 — Variables de Entorno

El archivo `.env` en este directorio ya viene configurado para ejecución local. Solo verifica que la contraseña coincida con tu PostgreSQL en Windows:

```env
POSTGRES_USER=postgres
POSTGRES_PASSWORD=contraseña_de_tu_postgresql          
POSTGRES_HOST=127.0.0.1
POSTGRES_PORT=5432
POSTGRES_DB=diquis
SECRET_KEY=diquis_local_dev_secret_key_2026_change_in_prod
```
*(Nota sobre WSL: Normalmente `127.0.0.1` funciona perfecto desde WSL para conectarse a Windows 11. Si falla la conexión a la base de datos, podrías necesitar cambiar el HOST a la IP de red local de tu máquina Windows).*

### Paso 2 — Instalar Dependencias (WSL / Linux)

Abre tu terminal de Ubuntu/Debian en **WSL** y ejecuta:

```bash
# 1. Navegar al directorio backend dentro de tu sistema de archivos montado
cd "/mnt/c/Users/kenny/Documents/Projects/diquis-v1/legacy/diquis-local-backend/backend"

# 2. Crear entorno virtual de Python
python3 -m venv venv

# 3. Activar el entorno virtual
source venv/bin/activate

# 4. Instalar dependencias
pip install -r requirements.txt
```

### Paso 3 — Arrancar el Servidor (WSL)

Con el entorno virtual activado (`(venv)` aparece en la terminal), ejecuta:

```bash
uvicorn main:app --reload
```

### Paso 4 — Verificar

| Qué | URL (Ábrelas en tu navegador de Windows) |
|-----|-----|
| Health Check | [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health) |
| Swagger Docs | [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) |

Si el health check responde `"database_status": "conectada 🚀"`, la conexión WSL <-> Windows está funcionando perfectamente.

---

## 🧑‍💻 Siguientes Pasos (Usuarios y Frontend)

¡El backend ya está listo y corriendo! A partir de este punto, **lo más recomendable es que vayas al proyecto del Frontend** y arranques la interfaz gráfica. Desde ahí podrás registrarte, iniciar sesión y usar Diquis de forma natural.

Sin embargo, si eres desarrollador y quieres **experimentar directamente con el API** (usando Postman o la interfaz interactiva en `http://127.0.0.1:8000/docs`), estos son los endpoints más importantes:

* **Crear Usuario:** `POST /api/v1/auth/registro`
  *(Nota: Al registrarte, la base de datos creará automáticamente tu "Billetera Principal" y una "Cuenta de Ahorros").*
* **Login:** `POST /api/v1/auth/login/access-token` 
  *(Maneja la sesión automáticamente estableciendo cookies seguras HttpOnly).*
* **Cuentas Financieras:** `GET /api/v1/accounts`
* **Transacciones:** `GET` y `POST` en `/api/v1/transactions`

¡Eso es todo de lado del servidor! **👉 Ya puedes ir a arrancar el Frontend.**

---

## 🏗️ Arquitectura del Backend

```text
backend/
├── app/
│   ├── api/                 # Capa 1: Routers y controladores de Endpoints
│   │   ├── dependencies.py  # Inyectores críticos (Token Blacklist, RLS, Auth DB)
│   │   └── endpoints/       # auth, users, categories, transactions, accounts, scheduled, analytics
│   ├── schemas/             # Capa 2: Data Transfer Objects y validación (Pydantic)
│   ├── services/            # Capa 3: Entidades lógicas abstractas o cruce de datos
│   ├── crud/                # Capa 4: DAL (Consultas mediante SQLAlchemy)
│   ├── models/              # Capa 5: Modelos ORM reflejados fielmente de PostgreSQL
│   ├── core/                # Core Global (JWT, Variables de .env, Loggers, Limiter)
│   └── db/                  # Configuración de conexión a la base de datos
└── main.py                  # Entry point del servidor, CORS y Middleware de Logs
```

## 🛡️ Seguridad

- **RLS (Row-Level Security)**: Cada request inyecta `set_config('app.current_user_id', ...)` en PostgreSQL. Un usuario nunca puede ver datos de otro.
- **Token Blacklist**: Al hacer logout, el JWT se invalida en la BD.
- **Timing Attack Mitigation**: `dummy_verify()` evita enumeración de usuarios.
- **Rate Limiting**: `slowapi` limita intentos de login y password reset.
- **Pessimistic Locking**: `.with_for_update()` en transacciones financieras.

## 📧 Recuperación de Contraseña (Modo Local)

En modo local, el endpoint `/forgot-password` **imprime el enlace de recuperación en la consola del servidor (WSL)** en vez de enviar un email real. Busca en los logs de la terminal:

```
📧 [LOCAL] Enlace de recuperación de contraseña para tu@correo.com:
   🔗 http://localhost:5173/auth/reset-password?token=abc123...
```

## 🔄 Servicios Automáticos

El backend arranca con un scheduler (`APScheduler`) en segundo plano que ejecuta:

| Job | Frecuencia | Descripción |
|-----|-----------|-------------|
| Tipos de cambio | 2:00 y 14:00 UTC | Descarga tasas de `open.er-api.com` (requiere internet) |
| Auto-ejecución de pagos | Cada 15 min | Ejecuta transacciones programadas vencidas |
| Limpieza de tokens | 3:00 UTC | Borra tokens expirados de la blacklist |
