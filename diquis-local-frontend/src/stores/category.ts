import { defineStore } from 'pinia';
import { ref } from 'vue';
import { categoryService } from '../services/categoryService';
import type { Category } from '../types/category';

export const useCategoryStore = defineStore('category', () => {
    const categories = ref<Category[]>([]);
    const isLoading = ref(false);

    async function fetchCategories(forceRefresh = false) {
        if (categories.value.length > 0 && !forceRefresh) return;

        isLoading.value = true;
        try {
            categories.value = await categoryService.getCategories();
        } catch (error) {
            console.error("Error cargando categorías:", error);
        } finally {
            isLoading.value = false;
        }
    }

    function clearCategories() {
        categories.value = [];
    }

    return {
        categories,
        isLoading,
        fetchCategories,
        clearCategories
    };
});