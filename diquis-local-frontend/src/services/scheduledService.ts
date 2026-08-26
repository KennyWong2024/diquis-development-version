import { api } from './api';
import type {
    ScheduledTransaction, ScheduledCreate, ScheduledUpdate,
    ScheduledExecute, CashflowProjections
} from '../types/scheduled';

export const scheduledService = {
    async getSchedules(): Promise<ScheduledTransaction[]> {
        const response = await api.get<ScheduledTransaction[]>('/scheduled/');
        return response.data;
    },
    async getPendingTray(): Promise<ScheduledTransaction[]> {
        const response = await api.get<ScheduledTransaction[]>('/scheduled/pending');
        return response.data;
    },
    async createScheduled(data: ScheduledCreate): Promise<ScheduledTransaction> {
        const response = await api.post<ScheduledTransaction>('/scheduled/', data);
        return response.data;
    },
    async updateScheduled(id: string, data: ScheduledUpdate): Promise<ScheduledTransaction> {
        const response = await api.put<ScheduledTransaction>(`/scheduled/${id}`, data);
        return response.data;
    },
    async deleteScheduled(id: string): Promise<void> {
        await api.delete(`/scheduled/${id}`);
    },
    async executeScheduled(id: string, data: ScheduledExecute): Promise<{ status: string, transaction_id: string }> {
        const response = await api.post(`/scheduled/${id}/execute`, data);
        return response.data;
    },
    async getProjections(days: number = 15): Promise<CashflowProjections> {
        const response = await api.get<CashflowProjections>(`/scheduled/projections?days=${days}`);
        return response.data;
    },
    async skipScheduled(id: string): Promise<{ status: string, message: string }> {
        const response = await api.post(`/scheduled/${id}/skip`);
        return response.data;
    }
};