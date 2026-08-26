import { api } from './api';
import type { Account, AccountCreatePayload, AccountUpdatePayload } from '../types/account';

export const accountService = {
    async getAccounts(): Promise<Account[]> {
        const response = await api.get<Account[]>('/accounts/');
        return response.data;
    },

    async createAccount(data: AccountCreatePayload): Promise<Account> {
        const response = await api.post<Account>('/accounts/', data);
        return response.data;
    },

    async updateAccount(id: string, data: AccountUpdatePayload): Promise<Account> {
        const response = await api.put<Account>(`/accounts/${id}`, data);
        return response.data;
    },

    async deleteAccount(id: string): Promise<{ status: string; detail: string }> {
        const response = await api.delete<{ status: string; detail: string }>(`/accounts/${id}`);
        return response.data;
    }
};