import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import type { User } from '../types/user';
import { authService } from '../services/authService';

export const useAuthStore = defineStore('auth', () => {
    const user = ref<User | null>(null);

    const isLoggedIn = ref<boolean>(localStorage.getItem('isLoggedIn') === 'true');

    const isAuthenticated = computed(() => isLoggedIn.value);

    function setUser(userData: User | null) {
        user.value = userData;
        if (userData) {
            isLoggedIn.value = true;
            localStorage.setItem('isLoggedIn', 'true');
        }
    }

    async function logout() {
        try {
            await authService.logout();
        } catch (error) {
            console.error("Error al cerrar sesión en el servidor", error);
        } finally {
            user.value = null;
            isLoggedIn.value = false;
            localStorage.removeItem('isLoggedIn');
        }
    }

    return {
        user,
        isAuthenticated,
        setUser,
        logout
    };
});