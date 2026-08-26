import { api } from './api';
import type {
    BalanceData,
    Transaction,
    TransactionDetail,
    TransactionUpdate,
    TransactionCreate,
    TransactionItemCreate
} from '../types/transaction';

export const financeService = {
    async getBalance(): Promise<BalanceData> {
        const response = await api.get<BalanceData>('/transactions/balance');
        return response.data;
    },

    async getRecentTransactions(accountId?: string): Promise<Transaction[]> {
        let url = '/transactions/?limit=10';
        if (accountId) {
            url += `&account_id=${accountId}`;
        }
        const response = await api.get<Transaction[]>(url);
        return response.data;
    },

    async getTransactionsByDate(startDate: string, endDate: string, accountId?: string): Promise<Transaction[]> {
        let url = `/transactions/?limit=100&start_date=${startDate}&end_date=${endDate}`;
        if (accountId) {
            url += `&account_id=${accountId}`;
        }
        const response = await api.get<Transaction[]>(url);
        return response.data;
    },

    async getTransactionDetail(transactionId: string): Promise<TransactionDetail> {
        const response = await api.get<TransactionDetail>(`/transactions/${transactionId}`);
        return response.data;
    },

    async deleteTransaction(transactionId: string): Promise<void> {
        await api.delete(`/transactions/${transactionId}`);
    },

    async updateTransaction(transactionId: string, data: TransactionUpdate): Promise<Transaction> {
        const response = await api.put<Transaction>(`/transactions/${transactionId}`, data);
        return response.data;
    },

    async createTransaction(data: TransactionCreate): Promise<Transaction> {
        const response = await api.post<Transaction>('/transactions/', data);
        return response.data;
    },

    async addTransactionItem(transactionId: string, data: TransactionItemCreate): Promise<any> {
        const response = await api.post(`/transactions/${transactionId}/items`, data);
        return response.data;
    }
};