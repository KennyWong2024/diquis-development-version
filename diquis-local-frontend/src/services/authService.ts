import { api } from './api';
import type {
    LoginCredentials,
    ForgotPasswordPayload,
    ResetPasswordPayload,
    ChangePasswordPayload,
    DeleteAccountPayload,
    AuthResponse,
    DetailResponse
} from '../types/auth';
import type { User, UserCreatePayload, UserUpdatePayload } from '../types/user';

export const authService = {
    async register(userData: UserCreatePayload): Promise<User> {
        const response = await api.post<User>('/auth/registro', userData);
        return response.data;
    },

    async login(credentials: LoginCredentials): Promise<AuthResponse> {
        const formData = new URLSearchParams();
        formData.append('username', credentials.username);
        formData.append('password', credentials.password);

        const response = await api.post<AuthResponse>('/auth/login/access-token', formData, {
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
        });
        return response.data;
    },

    async logout(): Promise<AuthResponse> {
        const response = await api.post<AuthResponse>('/auth/logout');
        return response.data;
    },

    async getCurrentUser(): Promise<User> {
        const response = await api.get<User>('/users/me');
        return response.data;
    },

    async updateProfile(userData: UserUpdatePayload): Promise<User> {
        const response = await api.put<User>('/users/me', userData);
        return response.data;
    },

    async forgotPassword(payload: ForgotPasswordPayload): Promise<AuthResponse> {
        const response = await api.post<AuthResponse>('/auth/forgot-password', payload);
        return response.data;
    },

    async resetPassword(payload: ResetPasswordPayload): Promise<AuthResponse> {
        const response = await api.post<AuthResponse>('/auth/reset-password', payload);
        return response.data;
    },

    async changePassword(payload: ChangePasswordPayload): Promise<DetailResponse> {
        const response = await api.post<DetailResponse>('/users/me/change-password', payload);
        return response.data;
    },

    async deleteAccount(payload: DeleteAccountPayload): Promise<DetailResponse> {
        const response = await api.delete<DetailResponse>('/users/me', { data: payload });
        return response.data;
    }
};