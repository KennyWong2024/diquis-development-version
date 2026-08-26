import { App as CapApp } from '@capacitor/app';
import { Capacitor } from '@capacitor/core';
import type { Router } from 'vue-router';

/**
 * Sistema centralizado de manejo del botón "Atrás" de Android para Capacitor.
 * 
 * Funciona con un sistema de prioridades:
 *   - Prioridad ALTA: Cerrar modales/drawers abiertos
 *   - Prioridad MEDIA: Navegar hacia atrás en el router
 *   - Prioridad BAJA: Minimizar la app si estamos en la pantalla principal
 */

type BackHandler = {
  id: string;
  priority: number;
  handler: () => void;
};

// Registro global de handlers activos
const activeHandlers: BackHandler[] = [];

// Profundidad de navegación interna del router
let navigationDepth = 0;

/**
 * Registrar un handler que se ejecutará cuando se presione "atrás".
 * Handlers con mayor prioridad se ejecutan primero.
 * Típicamente: modales (prioridad 100), drawers (prioridad 90).
 */
export function registerBackHandler(id: string, handler: () => void, priority: number = 100) {
  // Evitar duplicados: si ya existe con ese id, lo reemplazamos
  unregisterBackHandler(id);
  activeHandlers.push({ id, priority, handler });
}

/**
 * Desregistrar un handler por su id.
 */
export function unregisterBackHandler(id: string) {
  const index = activeHandlers.findIndex(h => h.id === id);
  if (index !== -1) {
    activeHandlers.splice(index, 1);
  }
}

/**
 * Consultar si hay handlers activos (modales/drawers abiertos).
 */
export function hasActiveHandlers(): boolean {
  return activeHandlers.length > 0;
}

/**
 * Consultar si se puede navegar hacia atrás en el historial del router.
 */
export function canGoBack(): boolean {
  return navigationDepth > 1;
}

/**
 * Incrementar la profundidad de navegación. 
 * Se llama desde el router.afterEach.
 */
export function trackNavigation() {
  navigationDepth++;
}

/**
 * Decrementar la profundidad de navegación cuando se va atrás.
 */
export function untrackNavigation() {
  if (navigationDepth > 0) navigationDepth--;
}

/**
 * Inicializar el listener del botón "Atrás" de Android.
 * Solo se activa en plataformas nativas (no en web).
 * 
 * Lógica:
 * 1. Si hay un modal/drawer abierto → cerrarlo
 * 2. Si hay historial de navegación → router.back()
 * 3. Si estamos en el dashboard → minimizar la app
 * 4. Si estamos en otra pantalla sin historial → ir al dashboard
 */
export function initBackButtonHandler(router: Router) {
  if (!Capacitor.isNativePlatform()) return;

  CapApp.addListener('backButton', () => {
    // 1. Si hay handlers activos (modal/drawer abierto), ejecutar el de mayor prioridad
    if (activeHandlers.length > 0) {
      // Ordenar por prioridad descendente y ejecutar el primero
      const sorted = [...activeHandlers].sort((a, b) => b.priority - a.priority);
      sorted[0].handler();
      return;
    }

    // 2. Si hay historial de navegación, volver atrás
    if (canGoBack()) {
      untrackNavigation();
      router.back();
      return;
    }

    // 3. Si estamos en el dashboard (pantalla principal), minimizar la app
    const currentRoute = router.currentRoute.value;
    if (currentRoute.name === 'dashboard' || currentRoute.path === '/') {
      CapApp.minimizeApp();
      return;
    }

    // 4. Si estamos en otra pantalla sin historial, navegar al dashboard
    router.push('/');
  });
}
