export type PaymentMethod = 'cash' | 'debit' | 'credit' | 'transfer' | 'sinpe' | 'digital';
export type TransactionType = 'income' | 'expense' | 'transfer';

export interface BalanceMetrics {
    monthly_income: number;
    monthly_expense: number;
}

export interface BalanceData {
    wallet_name: string;
    currency: string;
    current_balance: number;
    metrics: BalanceMetrics;
}

export interface TransactionItem {
    id: string;
    transaction_id: string;
    product_name: string;
    subcategory_id: string | null;
    quantity: number;
    unit_price: number;
    line_total: number;
    is_essential: boolean;
}

export interface Transaction {
    id: string;
    type: TransactionType;
    amount: number;
    currency: string;
    amount_in_account_currency: number;
    exchange_rate: number;
    exchange_source: string;
    description: string | null;
    category_id: string | null;
    account_id: string;
    transfer_to_account_id: string | null;
    occurred_at: string;
    is_essential: boolean;
    payment_method: PaymentMethod;
    notes: string | null;
    is_deleted: boolean;
}

export interface TransactionDetail extends Transaction {
    items: TransactionItem[];
}

export interface TransactionCreate {
    type: TransactionType;
    amount: number;
    account_id?: string;
    transfer_to_account_id?: string;
    category_id?: string;
    description?: string;
    occurred_at?: string;
    payment_method?: PaymentMethod;
    notes?: string;
    is_essential?: boolean;
    currency?: string;
    exchange_rate?: number;
    exchange_source?: string;
}

export interface TransactionUpdate {
    type?: TransactionType;
    amount?: number;
    category_id?: string;
    account_id?: string;
    transfer_to_account_id?: string;
    description?: string;
    occurred_at?: string;
    payment_method?: PaymentMethod;
    notes?: string;
    exchange_rate?: number;
    exchange_source?: string;
}

export interface TransactionItemCreate {
    product_name: string;
    subcategory_id?: string;
    quantity: number;
    line_total: number;
    is_essential: boolean;
}