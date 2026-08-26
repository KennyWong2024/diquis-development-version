import { defineStore } from 'pinia';
import { ref } from 'vue';
import { analyticsService } from '../services/analyticsService';
import type { CashflowReport } from '../types/analytics';

export const useAnalyticsStore = defineStore('analytics', () => {
    const cashflowReport = ref<CashflowReport | null>(null);
    const isLoading = ref<boolean>(false);
    const error = ref<string | null>(null);
    async function fetchCashflow(startDate: string, endDate: string) {
        isLoading.value = true;
        error.value = null;
        try {
            cashflowReport.value = await analyticsService.getCashflow(startDate, endDate);
        } catch (e: any) {
            console.error("[Analytics Store] Error cargando flujo de caja:", e);
            error.value = e.response?.data?.detail || "No se pudo cargar el análisis.";
        } finally {
            isLoading.value = false;
        }
    }

    function clearAnalytics() {
        cashflowReport.value = null;
        error.value = null;
    }

    return {
        cashflowReport,
        isLoading,
        error,
        fetchCashflow,
        clearAnalytics
    };
});