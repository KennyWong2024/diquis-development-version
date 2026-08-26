export interface DailyCashflow {
    date: string;
    real_income: number;
    real_expense: number;
    projected_income: number;
    projected_expense: number;
    balance: number;
    is_future: boolean;
}

export interface CashflowReport {
    currency: string;
    start_date: string;
    end_date: string;
    starting_balance: number;
    ending_balance: number;
    timeline: DailyCashflow[];
}