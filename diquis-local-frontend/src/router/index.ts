import { createRouter, createWebHistory } from 'vue-router';
import { useAuthStore } from '../stores/auth';
import { trackNavigation } from '../composables/useBackButton';

const router = createRouter({
    history: createWebHistory(import.meta.env.BASE_URL),
    routes: [
        {
            path: '/auth',
            component: () => import('../layouts/AuthLayout.vue'),
            meta: { requiresAuth: false },
            children: [
                {
                    path: 'login',
                    name: 'login',
                    component: () => import('../views/LoginView.vue'),
                },
                {
                    path: 'registro',
                    name: 'registro',
                    component: () => import('../views/RegisterView.vue'),
                },
                {
                    path: 'forgot-password',
                    name: 'forgot-password',
                    component: () => import('../views/ForgotPasswordView.vue'),
                },
                {
                    path: 'reset-password',
                    name: 'reset-password',
                    component: () => import('../views/ResetPasswordView.vue'),
                }
            ]
        },
        {
            path: '/',
            component: () => import('../layouts/MasterLayout.vue'),
            meta: { requiresAuth: true },
            children: [
                {
                    path: '',
                    name: 'dashboard',
                    component: () => import('../views/DashboardView.vue'),
                },
                {
                    path: 'proyecciones',
                    name: 'proyecciones',
                    component: () => import('../views/ProyeccionesView.vue'),
                },
                {
                    path: 'historial',
                    name: 'historial',
                    component: () => import('../views/HistorialView.vue'),
                },
                {
                    path: 'cuentas',
                    name: 'cuentas',
                    component: () => import('../views/AccountsView.vue'),
                },
                {
                    path: 'informes',
                    name: 'informes',
                    component: () => import('../views/AnalyticsView.vue'),
                },
                {
                    path: 'categorias',
                    name: 'categorias',
                    component: () => import('../views/CategoriesView.vue'),
                },
                {
                    path: 'perfil',
                    name: 'perfil',
                    component: () => import('../views/ProfileView.vue'),
                }
            ]
        },
        {
            path: '/:pathMatch(.*)*',
            redirect: '/auth/login'
        }
    ]
});

router.beforeEach((to, _from, next) => {
    const authStore = useAuthStore();

    if (to.meta.requiresAuth && !authStore.isAuthenticated) {
        next({ name: 'login' });
    }
    else if (['login', 'registro', 'forgot-password', 'reset-password'].includes(to.name as string) && authStore.isAuthenticated) {
        next({ name: 'dashboard' });
    }
    else {
        next();
    }
});

router.afterEach((_to, _from, failure) => {
    if (!failure) trackNavigation();
});

export default router;