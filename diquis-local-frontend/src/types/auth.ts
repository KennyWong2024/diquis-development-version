export interface LoginCredentials {
    username: string;
    password: string;
}

export interface AuthResponse {
    mensaje: string;
}

export interface DetailResponse {
    detail: string;
}

export interface ForgotPasswordPayload {
    email: string;
}

export interface ResetPasswordPayload {
    token: string;
    new_password: string;
}

export interface ChangePasswordPayload {
    current_password: string;
    new_password: string;
}

export interface DeleteAccountPayload {
    current_password: string;
}