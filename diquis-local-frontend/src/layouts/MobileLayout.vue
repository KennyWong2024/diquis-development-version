<script setup lang="ts">
import { computed, onMounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { authService } from '../services/authService';
import { useAuthStore } from '../stores/auth';
import { 
  LayoutDashboard, 
  History, 
  Calendar, 
  LineChart,     
  Tags, 
  Wallet
} from 'lucide-vue-next';

const router = useRouter();
const route = useRoute();
const authStore = useAuthStore();

onMounted(async () => {
  if (!authStore.user && authStore.isAuthenticated) {
    try {
      const userData = await authService.getCurrentUser();
      authStore.setUser(userData);
    } catch (error) {
      authStore.logout();
      router.push('/auth/login');
    }
  }
});

const navigation = [
  { name: 'Inicio', path: '/', icon: LayoutDashboard },
  { name: 'Movimientos', path: '/historial', icon: History },
  { name: 'Planificación', path: '/proyecciones', icon: Calendar },    
  { name: 'Análisis', path: '/informes', icon: LineChart },            
  { name: 'Categorías', path: '/categorias', icon: Tags },        
];

const userFirstName = computed(() => {
  return authStore.user?.full_name?.split(' ')[0] || 'Usuario';
});

const userInitial = computed(() => {
  return userFirstName.value.charAt(0).toUpperCase();
});
</script>

<template>
  <div class="w-full h-screen bg-[#fbfbfb] dark:bg-[#050505] transition-colors duration-700 font-sans flex flex-col overflow-hidden relative">
    
    <header class="touch-none-fixed pt-safe px-5 border-b border-slate-200/50 dark:border-white/10 backdrop-blur-3xl bg-white/80 dark:bg-[#0a0a0c]/80 z-40 shrink-0 shadow-sm w-full">
      <div class="h-16 flex items-center justify-between w-full">
        <div class="flex items-center gap-2">
          <div class="p-1.5 bg-slate-900 dark:bg-white rounded-lg text-white dark:text-slate-900 shadow-md">
            <Wallet class="w-5 h-5" />
          </div>
          <span class="text-xl font-extrabold text-slate-800 dark:text-white tracking-tight">Diquis</span>
        </div>

        <router-link 
          to="/perfil"
          class="flex w-9 h-9 rounded-full items-center justify-center font-bold outline-none active:scale-95 transition-transform overflow-hidden bg-slate-900 dark:bg-white text-white dark:text-slate-900 shadow-sm"
        >
          <span>{{ userInitial }}</span>
        </router-link>
      </div>
    </header>

    <main class="flex-1 overflow-y-auto custom-scrollbar relative z-10 pb-[76px]">
      <div class="p-5 min-h-full flex flex-col">
        <div class="flex-1">
          <router-view v-slot="{ Component }">
            <transition name="fade" mode="out-in">
              <component :is="Component" />
            </transition>
          </router-view>
        </div>
        </div>
    </main>

    <nav class="touch-none-fixed fixed bottom-0 w-full bg-white/95 dark:bg-[#050505]/95 backdrop-blur-2xl border-t border-slate-200/50 dark:border-white/10 z-40 px-2 pb-safe shadow-[0_-4px_24px_rgba(0,0,0,0.05)] dark:shadow-[0_-4px_24px_rgba(0,0,0,0.4)]">
      <div class="flex items-center justify-around h-[68px]">
        <router-link 
          v-for="item in navigation" 
          :key="item.name" 
          :to="item.path"
          class="flex flex-col items-center justify-center w-full h-full gap-1 transition-colors duration-300 relative"
          :class="route.path.startsWith(item.path) && item.path !== '/' || route.path === item.path ? 'text-slate-900 dark:text-white' : 'text-slate-400 dark:text-slate-500 hover:text-slate-600 dark:hover:text-slate-300'"
        >
          <div v-if="route.path.startsWith(item.path) && item.path !== '/' || route.path === item.path" class="absolute top-0 left-1/2 -translate-x-1/2 w-8 h-1 bg-slate-900 dark:bg-white rounded-b-full"></div>
          <component :is="item.icon" class="w-[22px] h-[22px] mt-1 transition-transform duration-300" :class="route.path.startsWith(item.path) && item.path !== '/' || route.path === item.path ? 'scale-110' : ''" />
          <span class="text-[9px] tracking-tight font-semibold truncate max-w-[65px] text-center">{{ item.name }}</span>
        </router-link>
      </div>
    </nav>

  </div>
</template>

<style scoped>
.fade-enter-active, .fade-leave-active { transition: opacity 0.3s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
.pt-safe { padding-top: env(safe-area-inset-top); }
.pb-safe { padding-bottom: env(safe-area-inset-bottom); }
.custom-scrollbar::-webkit-scrollbar { width: 0px; background: transparent; }
</style>