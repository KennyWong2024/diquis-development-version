import { api } from './api';
import type { CashflowReport } from '../types/analytics';

export const analyticsService = {
    async getCashflow(startDate: string, endDate: string): Promise<CashflowReport> {
        const response = await api.get<CashflowReport>('/analytics/cashflow', {
            params: {
                start_date: startDate,
                end_date: endDate
            }
        });
        return response.data;
    }
};