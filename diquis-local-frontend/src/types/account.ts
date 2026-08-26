export interface Account {
    id: string;
    user_id: string;
    name: string;
    account_type: 'checking' | 'saving' | 'cash' | 'digital';
    currency: string;
    current_balance: number;
    allow_negative_balance: boolean;
    theme_color: string;
    is_system: boolean;
    is_active: boolean;
    created_at: string;
}

export interface AccountCreatePayload {
    name: string;
    account_type: 'checking' | 'saving' | 'cash' | 'digital';
    currency: string;
    initial_balance?: number;
    allow_negative_balance: boolean;
    theme_color: string;
}

export interface AccountUpdatePayload {
    name?: string;
    is_active?: boolean;
    theme_color?: string;
    allow_negative_balance?: boolean;
}