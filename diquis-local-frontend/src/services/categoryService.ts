import { api } from './api';
import type { Category, CategoryCreate, CategoryUpdate } from '../types/category';

export const categoryService = {
    async getCategories(): Promise<Category[]> {
        const response = await api.get<Category[]>('/categories/');
        return response.data;
    },
    async createCategory(data: CategoryCreate): Promise<Category> {
        const response = await api.post<Category>('/categories/', data);
        return response.data;
    },
    async updateCategory(id: string, data: CategoryUpdate): Promise<any> {
        const response = await api.put(`/categories/${id}`, data);
        return response.data;
    },
    async deleteCategory(id: string): Promise<void> {
        await api.delete(`/categories/${id}`);
    }
};