# 🗄️ Diquis Database (Capa de Datos)

¡Bienvenido al núcleo de los datos de Diquis! Aquí es donde ocurre la magia transaccional.

Esta carpeta contiene los scripts para configurar una base de datos PostgreSQL alojada nativamente en **Windows**. Está diseñada como una herramienta didáctica para que estudiantes y desarrolladores vean cómo se inicializa un esquema complejo de manera programática (Infrastructure as Code).

---

## ⚡ Guía Rápida — Inicializar Base de Datos por Código

Para evitar interfaces gráficas (como DBeaver) y problemas con variables de entorno de Windows (PATH), hemos preparado un script en PowerShell que encuentra tu instalación de PostgreSQL en Windows y ejecuta el código SQL maestro automáticamente.

### Ejecutar el Script (Windows PowerShell)

Abre **PowerShell** en Windows (asegúrate de **NO** estar en WSL) y ejecuta:

```powershell
cd "diquis-local-database"

# Ejecutar el script automático
.\init_db.ps1
```

El script localizará tu instalación de PostgreSQL, te pedirá la contraseña de tu usuario `postgres` y hará lo siguiente de manera automatizada:
1. Creará la base de datos `diquis` (si no existe).
2. Ejecutará el archivo `ddl/0. Init Completo.sql`, construyendo el esquema `app`, las tablas, funciones, triggers y los datos semilla (todo desde cero).

> **Nota:** Si tienes políticas de ejecución en PowerShell que bloquean la ejecución de scripts locales, ejecuta el siguiente comando primero:
> `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`

---

### Detalles Técnicos del DDL (`ddl/0. Init Completo.sql`)

El script maestro unifica y ejecuta de forma segura los siguientes pasos:
1. **Destrucción y Limpieza:** Hace un `DROP SCHEMA IF EXISTS app CASCADE;` para asegurar un entorno completamente limpio y libre de conflictos cada vez que lo ejecutas.
2. **Creación Estructural:** Define los tipos `ENUM` nativos y las tablas con las políticas RLS.
3. **Lógica Financiera:** Compila las funciones de PostgreSQL y asigna los Triggers (ej. validación de saldos y cuentas automáticas).
4. **Datos Semilla:** Inserta de forma atómica y protegida las categorías base necesarias para que la app funcione.
