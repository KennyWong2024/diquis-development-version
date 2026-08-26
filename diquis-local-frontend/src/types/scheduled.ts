export interface ScheduledTransaction {
    id: string;
    user_id: string;
    account_id: string;
    transfer_to_account_id: string | null;
    category_id: string | null;
    type: 'income' | 'expense' | 'transfer';
    name: string;
    expected_amount: number;
    currency: string;
    is_estimated: boolean;
    frequency: 'once' | 'daily' | 'weekly' | 'biweekly' | 'monthly' | 'quarterly' | 'yearly';
    next_due_date: string;
    is_essential: boolean;
    auto_execute: boolean;
    is_active: boolean;
    last_transaction_id: string | null;
    created_at: string;
    can_auto_execute: boolean;
    projected_account_amount: number | null;
    projected_exchange_rate: number | null;
    projected_fx_source: string | null;
}

export interface ScheduledCreate {
    account_id: string;
    transfer_to_account_id?: string;
    category_id?: string;
    type: 'income' | 'expense' | 'transfer';
    name: string;
    expected_amount: number;
    currency?: string;
    is_estimated?: boolean;
    frequency: 'once' | 'daily' | 'weekly' | 'biweekly' | 'monthly' | 'quarterly' | 'yearly';
    next_due_date: string;
    is_essential?: boolean;
    auto_execute?: boolean;
}

export interface ScheduledUpdate {
    account_id?: string;
    transfer_to_account_id?: string;
    category_id?: string;
    name?: string;
    expected_amount?: number;
    frequency?: 'once' | 'daily' | 'weekly' | 'biweekly' | 'monthly' | 'quarterly' | 'yearly';
    next_due_date?: string;
    is_estimated?: boolean;
    is_essential?: boolean;
    is_active?: boolean;
    auto_execute?: boolean;
}

export interface ScheduledExecute {
    actual_amount: number;
    occurred_at: string;
    description?: string;
    exchange_rate?: number;
    exchange_source?: string;
}

export interface ProjectionEvent {
    date: string;
    scheduled_id: string;
    name: string;
    type: 'income' | 'expense' | 'transfer';
    amount: number;
    currency?: string;
    projected_account_amount?: number;
}

export interface DailyProjection {
    date: string;
    projected_balance: number;
    events: ProjectionEvent[];
}

export interface CashflowProjections {
    current_balance: number;
    days_projected: number;
    timeline: DailyProjection[];
}