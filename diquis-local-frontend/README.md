# 🎨 Diquis Frontend (Capa de Presentación)

¡Bienvenido al rostro de Diquis! 

Este cliente web está desarrollado con las últimas tecnologías maduras en el ecosistema **Vue 3**. Su propósito en este repositorio de código abierto es servir como un recurso didáctico para que estudiantes y desarrolladores vean cómo construir una experiencia de usuario inmersiva, interfaces limpias (*glassmorphism*) y una arquitectura altamente escalable.

## 🛠️ Tecnologías Principales

- **Framework**: Vue 3 (Composition API, `<script setup>`)
- **Lenguaje**: TypeScript estricto
- **Estilos**: Tailwind CSS 4+ (Modo oscuro integrado nativamente, sombras en UI Glass)
- **Estado Global**: Pinia
- **Routing**: Vue Router (Con protección local mediante `Navigation Guards`)
- **Peticiones HTTP**: Axios con interceptores automáticos resilientes
- **Iconografía**: `lucide-vue-next`

## 🏗️ Arquitectura de Carpetas (Separation of Concerns)

Para simplificar el desarrollo y evitar acoplamientos densos, segmentamos el frontend:

```text
frontend/
├── src/
│   ├── assets/         # Recursos estáticos
│   ├── components/     # Componentes visuales reutilizables o "tontos"
│   │   └── ui/         # Componentes core de diseño (GlassCard, ThemeToggle)
│   ├── views/          # Pantallas de la aplicación (LoginView, RegisterView, Dashboard)
│   ├── layouts/        # Contenedores de vista superior (AuthLayout vs MainLayout)
│   ├── router/         # Configurador de VueRouter + Middlewares
│   ├── stores/         # Cajas de estado global de Pinia (ej. auth.ts, transactions.ts)
│   ├── services/       # Cliente HTTP abstracto dedicado al REST (authService.ts)
│   ├── composables/    # Lógica de reusabilidad Reactiva Custom (ej. useTheme.ts)
│   ├── types/          # Interfaces TS. Nuestro "Espejo" del esquema Pydantic Backend
│   ├── App.vue         # Cascarón Raíz de montaje
│   └── main.ts         # Punto de entrada / Instancia
```

## 🔐 Seguridad e Integración Cero Confianza (Zero-Trust API)

Uno de los logros principales de esta UI es que no almacena llaves a la vista:
1. **Storage Seguro por Instinto**: Dado que el Backend de Diquis es capaz de inyectar las credenciales mediante **Cookies HttpOnly**, Pinia no almacena el Token ni lo pegamos en `LocalStorage`. Esto mitiga automáticamente ataques *XSS* (Cross-Site Scripting). La información fluye segura por la red al hacer `withCredentials: true` en Axios.
2. **Auto-Curación y Renovación de Tokens (`api.ts`)**: Los interceptores de Axios están adiestrados para "cazar" el momento en que el servidor responde con un Error Automático 401. Antes de enviar al usuario fuera, Axios solicita secretamente refrescar la Cookie mediante la API, detiene las operaciones intermitentemente, y las relanza cuando el token es válido una vez más.

## 🚀 Flujos Completados a la Fecha

1. **Gestor Dinámico de Temas (Oscuro/Claro)**: Creado como Composable nativo `useTheme.ts`, acoplado completamente a la lógica local de perfiles y a `Tailwind`.
2. **Módulo Auth Visual y Defensivo**: Formulario de Login reactivo y una majestuosa UI de Registro con calculadoras de fuerza de contraseña, saneado de carácteres y respuesta in-app a errores del `POST`.
3. **SSO Preparativo**: Capas visuales montadas para Google/Microsoft Login listos para empalmar.

## 📦 Instrucciones para Desarrolladores (Quickstart)

```bash
# 1. Instalar dependencias puras (NPM, Yarn, pnpm, o Bun)
npm install 

# 2. Encender ambiente de desarollo en HMR (Vite Dev Server)
npm run dev
```
