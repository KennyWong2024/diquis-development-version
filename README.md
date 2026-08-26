# 🏦 Diquis: Potenciando tus Finanzas Personales (Legacy Open Source)

¡Te damos la bienvenida al código abierto de **Diquis**! 🚀

Diquis nació con la visión de empoderar a las personas en la gestión de sus finanzas personales, dándoles control absoluto, proyecciones inteligentes y una interfaz majestuosa. 

Lo que estás viendo en este repositorio es la **primera versión (Legacy)** de nuestra arquitectura web. Hoy en día, Diquis ha evolucionado radicalmente hacia una **aplicación móvil 100% offline, centrada estrictamente en la privacidad** y el control total de los datos por parte del usuario. Sin embargo, hemos decidido abrir este código de nuestra primera iteración en la nube para que sea una **herramienta didáctica para la comunidad**: estudiantes, profesores y desarrolladores curiosos que deseen explorar cómo se construye una plataforma financiera full-stack con tecnologías web modernas.

> 🌐 **Descubre la versión actual de Diquis:**
> - Visita nuestra página web: [diquis.cachollolabs.com/es/vision-general](https://diquis.cachollolabs.com/es/vision-general)
> - Descarga nuestra app en Google Play: [Diquis Mobile](https://play.google.com/store/apps/details?id=com.diquis.mobile)

---

## 🏗️ La Arquitectura de esta Versión

Este repositorio está estructurado en tres grandes bloques que han sido adaptados para ejecutarse de manera **100% local** y segura, sin dependencias de la nube:

1. **Base de Datos (`diquis-local-database`)**: PostgreSQL nativo con políticas de seguridad a nivel de fila (RLS) y triggers financieros.
2. **Backend (`diquis-local-backend`)**: Construido en Python con FastAPI y SQLAlchemy. Gestiona la lógica de negocio y protege las sesiones usando cookies seguras (HttpOnly / Zero-Trust).
3. **Frontend (`diquis-local-frontend`)**: Una interfaz vibrante y reactiva construida con Vue 3, Vite, Pinia y TailwindCSS.

---

## 🛠️ Requisitos Previos

Asegúrate de tener instalados los siguientes componentes en tu máquina:

### 1. Entorno Windows
* **PostgreSQL (14+)**: Instalado de forma nativa en Windows. *(Asegúrate de saber la contraseña del usuario `postgres`)*.
* **PowerShell**: Para ejecutar el script automático de base de datos.

### 2. Entorno WSL (Linux / Ubuntu)
* **Python 3.10+** (incluye `pip` y `venv`).
* **Node.js 18+** (incluye `npm`).

---

## 🚀 Guía Maestra de Despliegue (Paso a Paso)

Este es un entorno interconectado. Por favor, sigue estos 3 pasos en orden estricto.

### Paso 1: Inicializar la Base de Datos (En Windows)

1. Abre una terminal de **PowerShell en Windows** (Asegúrate de NO estar en WSL).
2. Navega al directorio de la base de datos:
   ```powershell
   cd "diquis-local-database"
   ```
3. Ejecuta el script de inicialización automática:
   ```powershell
   .\init_db.ps1
   ```
   > **¿Qué aprenderás aquí?** Este paso automatiza la creación de esquemas, tablas, y datos semilla. Demuestra cómo inicializar bases de datos por código, una habilidad invaluable en DevOps.

---

### Paso 2: Levantar el Backend (En WSL)

1. Abre tu terminal de **WSL (Ubuntu/Linux)**.
2. Navega al directorio del backend:
   ```bash
   cd "diquis-local-backend"
   ```
3. **Copia el archivo de variables de entorno**: 
   ```bash
   cp .env.example .env
   ```
   *(Abre `.env` y asegúrate de poner tu contraseña de PostgreSQL. Revisa que `POSTGRES_HOST` tenga la IP correcta, usualmente `127.0.0.1` funciona, pero si estás en WSL2 y postgres está en Windows, usa la IP de tu adaptador vEthernet, ej. `172.17.224.1`)*.
4. Ejecuta el bloque de preparación y arranque:
   ```bash
   # 1. Crea y activa el entorno virtual
   python3 -m venv venv
   source venv/bin/activate

   # 2. Instala las dependencias y arranca el servidor
   pip install -r requirements.txt
   uvicorn main:app --reload
   ```
   > El servidor quedará escuchando en `http://127.0.0.1:8000`. No cierres esta terminal.

---

### Paso 3: Levantar el Frontend (En WSL)

1. Abre **otra ventana/pestaña** de terminal en **WSL**.
2. Navega al directorio del frontend:
   ```bash
   cd "diquis-local-frontend"
   ```
3. **Copia el archivo de variables de entorno**: 
   ```bash
   cp .env.example .env
   ```
4. Ejecuta el bloque de instalación y arranque:
   ```bash
   # Instala todas las librerías necesarias y levanta la UI
   npm install
   npm run dev
   ```
   > El frontend quedará escuchando en `http://localhost:5173`. 

---

## 🎉 ¡Tu Laboratorio Financiero está Listo!

Abre tu navegador y ve a **[http://localhost:5173](http://localhost:5173)**.

* **Explora el Código:** Te invitamos a leer los archivos `README.md` que están dentro de cada una de las 3 carpetas. En ellos explicamos a profundidad conceptos técnicos ideales para aprender.
* **Crea un usuario**: Experimenta el flujo de autenticación seguro, registra transacciones, y observa cómo el frontend interactúa con la base de datos a través del API.

> 💡 **Regla de Oro de Cookies Locales:** Asegúrate de abrir el frontend escribiendo textualmente **`localhost`** en tu barra de direcciones en lugar de `127.0.0.1`. Esto asegura que navegadores modernos (como Chrome) traten el origen correctamente y permitan enviar la cookie de sesión cruzada al backend.
