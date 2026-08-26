import { defineStore } from 'pinia';
import { ref } from 'vue';
import { scheduledService } from '../services/scheduledService';
import type { ScheduledTransaction, CashflowProjections } from '../types/scheduled';

export const useScheduledStore = defineStore('scheduled', () => {
    const activeSchedules = ref<ScheduledTransaction[]>([]);

    const pendingSchedules = ref<ScheduledTransaction[]>([]);
    const projections = ref<CashflowProjections | null>(null);
    const isLoading = ref(false);

    async function fetchActiveSchedules() {
        try {
            activeSchedules.value = await scheduledService.getSchedules();
        } catch (error) {
            console.error("Error cargando plantillas activas:", error);
        }
    }

    async function fetchPendingTray() {
        try {
            pendingSchedules.value = await scheduledService.getPendingTray();
        } catch (error) {
            console.error("Error cargando pagos programados pendientes:", error);
        }
    }

    async function fetchProjections(days: number = 30) {
        try {
            projections.value = await scheduledService.getProjections(days);
        } catch (error) {
            console.error("Error cargando proyecciones:", error);
        }
    }

    async function refreshAll() {
        isLoading.value = true;
        await Promise.all([
            fetchActiveSchedules(),
            fetchPendingTray(),
            fetchProjections(30)
        ]);
        isLoading.value = false;
    }

    return {
        activeSchedules,
        pendingSchedules,
        projections,
        isLoading,
        fetchActiveSchedules,
        fetchPendingTray,
        fetchProjections,
        refreshAll
    };
});