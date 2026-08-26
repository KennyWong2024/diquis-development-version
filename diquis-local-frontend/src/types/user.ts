export interface User {
    id: string;
    email: string;
    full_name: string;
    date_of_birth: string | null;
    country_code: string;
    default_currency: string;
    timezone: string;
    is_active: boolean;
}

export interface UserCreatePayload {
    email: string;
    full_name: string;
    password: string;
    date_of_birth?: string | null;
    country_code?: string;
    default_currency?: string;
    timezone?: string;

}

export interface UserUpdatePayload {
    full_name?: string;
    country_code?: string;
    default_currency?: string;
    timezone?: string;
}