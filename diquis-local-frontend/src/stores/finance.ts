import { defineStore } from 'pinia';
import { ref } from 'vue';
import { financeService } from '../services/financeService';
import { accountService } from '../services/accountService';
import { useCategoryStore } from './category';
import type { BalanceData, Transaction } from '../types/transaction';
import type { Account } from '../types/account';

export const useFinanceStore = defineStore('finance', () => {
    const balance = ref<BalanceData | null>(null);
    const recentTransactions = ref<Transaction[]>([]);
    const monthlyTransactions = ref<Transaction[]>([]);
    const accounts = ref<Account[]>([]);

    const isLoading = ref(false);
    const isMonthlyLoading = ref(false);
    const hasLoadedInitialData = ref(false);

    async function fetchAccounts(forceRefresh = false) {
        if (accounts.value.length > 0 && !forceRefresh) return;
        try {
            accounts.value = await accountService.getAccounts();
        } catch (error) {
            console.error("Error cargando cuentas:", error);
        }
    }

    async function fetchBalance(forceRefresh = false) {
        if (hasLoadedInitialData.value && !forceRefresh) return;
        isLoading.value = true;
        try {
            balance.value = await financeService.getBalance();
            hasLoadedInitialData.value = true;
        } catch (error) {
            console.error("Error cargando el balance:", error);
        } finally {
            isLoading.value = false;
        }
    }

    async function fetchRecentTransactions(forceRefresh = false, accountId?: string) {
        if (recentTransactions.value.length > 0 && !forceRefresh && !accountId) return;
        try {
            recentTransactions.value = await financeService.getRecentTransactions(accountId);
        } catch (error) {
            console.error("Error cargando transacciones recientes:", error);
        }
    }

    async function fetchMonthlyTransactions(startDate: string, endDate: string, accountId?: string) {
        isMonthlyLoading.value = true;
        try {
            monthlyTransactions.value = await financeService.getTransactionsByDate(startDate, endDate, accountId);
        } catch (error) {
            console.error("Error cargando transacciones mensuales:", error);
        } finally {
            isMonthlyLoading.value = false;
        }
    }

    async function refreshAllData() {
        isLoading.value = true;
        const categoryStore = useCategoryStore();

        await Promise.all([
            fetchBalance(true),
            fetchAccounts(true),
            fetchRecentTransactions(true),
            categoryStore.fetchCategories(true)
        ]);

        isLoading.value = false;
    }

    function clearFinanceData() {
        balance.value = null;
        recentTransactions.value = [];
        monthlyTransactions.value = [];
        accounts.value = [];
        hasLoadedInitialData.value = false;
    }

    return {
        balance,
        recentTransactions,
        monthlyTransactions,
        accounts,
        isLoading,
        isMonthlyLoading,
        fetchBalance,
        fetchAccounts,
        fetchRecentTransactions,
        fetchMonthlyTransactions,
        refreshAllData,
        clearFinanceData
    };
});