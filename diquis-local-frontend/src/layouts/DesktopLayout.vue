<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { authService } from '../services/authService';
import { useAuthStore } from '../stores/auth';
import ThemeToggle from '../components/ui/ThemeToggle.vue';
import { 
  LayoutDashboard, 
  History,       
  LineChart,     
  Wallet,
  ChevronLeft,
  CreditCard,
  Heart,
  Calendar,
  Tags 
} from 'lucide-vue-next';

const router = useRouter();
const route = useRoute();
const authStore = useAuthStore();

const isDesktopMenuCollapsed = ref(false);

const currentYear = computed(() => new Date().getFullYear());

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
  { name: 'Calendario', path: '/proyecciones', icon: Calendar },    
  { name: 'Análisis', path: '/informes', icon: LineChart },            
  { name: 'Categorías', path: '/categorias', icon: Tags },        
  { name: 'Billeteras', path: '/cuentas', icon: CreditCard }, 
];

const toggleDesktopMenu = () => {
  isDesktopMenuCollapsed.value = !isDesktopMenuCollapsed.value;
};

const sidebarWidthClass = computed(() => {
  return isDesktopMenuCollapsed.value ? 'w-20' : 'w-64';
});

const timeGreeting = computed(() => {
  const hour = new Date().getHours();
  if (hour >= 5 && hour < 12) return 'Buenos días';
  if (hour >= 12 && hour < 19) return 'Buenas tardes';
  return 'Buenas noches';
});

const userFirstName = computed(() => {
  return authStore.user?.full_name?.split(' ')[0] || 'Usuario';
});

const userInitial = computed(() => {
  return userFirstName.value.charAt(0).toUpperCase();
});

const currentDateDisplay = computed(() => {
  const date = new Date();
  return new Intl.DateTimeFormat('es-CR', { weekday: 'long', day: 'numeric', month: 'long' }).format(date);
});
</script>

<template>
  <div class="w-full h-screen bg-[#fbfbfb] dark:bg-[#050505] transition-colors duration-700 font-sans flex overflow-hidden relative">
    
    <aside 
      :class="[
        'relative z-50 transition-all duration-300 ease-in-out shrink-0 flex flex-col h-full',
        'bg-white/60 dark:bg-slate-950/70 backdrop-blur-3xl border-r border-slate-200/50 dark:border-white/10 shadow-[4px_0_24px_rgba(0,0,0,0.03)] dark:shadow-[4px_0_24px_rgba(0,0,0,0.5)]',
        sidebarWidthClass
      ]"
    >
      <button 
        @click="toggleDesktopMenu"
        class="absolute -right-3 top-6 flex bg-white/90 dark:bg-slate-800/90 backdrop-blur-md border border-slate-200/90 dark:border-slate-600/90 rounded-full p-1 shadow-md z-10 text-slate-500 hover:text-slate-900 dark:hover:text-white transition-transform"
        :class="{ 'rotate-180': isDesktopMenuCollapsed }"
      >
        <ChevronLeft class="w-4 h-4" />
      </button>

      <div class="h-20 flex items-center px-6 border-b border-slate-200/50 dark:border-white/5 shrink-0 overflow-hidden">
        <div class="flex items-center gap-3 transition-all duration-300 w-full" :class="isDesktopMenuCollapsed ? 'justify-center' : ''">
          <div class="p-2 bg-slate-900 dark:bg-white rounded-xl text-white dark:text-slate-900 shadow-xl shrink-0">
            <Wallet class="w-5 h-5" />
          </div>
          <span class="text-2xl font-extrabold text-slate-800 dark:text-white tracking-tight transition-opacity duration-300 whitespace-nowrap drop-shadow-sm" :class="isDesktopMenuCollapsed ? 'opacity-0 w-0 hidden' : 'opacity-100 w-auto'">Diquis</span>
        </div>
      </div>

      <nav class="flex-1 px-3 py-6 space-y-2.5 overflow-y-auto custom-scrollbar z-10">
        <router-link 
          v-for="item in navigation" 
          :key="item.name" 
          :to="item.path"
          class="flex items-center rounded-xl font-semibold transition-all duration-300 relative group border border-transparent"
          :class="[
            route.path.startsWith(item.path) && item.path !== '/' || route.path === item.path 
              ? 'bg-white/80 dark:bg-white/10 backdrop-blur-xl text-slate-950 dark:text-white shadow-[0_2px_8px_rgba(0,0,0,0.05)] dark:shadow-[0_2px_12px_rgba(0,0,0,0.4)] border-t border-l border-white/80 dark:border-t-white/15 dark:border-l-white/10' 
              : 'text-slate-600 dark:text-slate-400 hover:bg-white/40 dark:hover:bg-white/5 hover:text-slate-900 dark:hover:text-slate-100',
            isDesktopMenuCollapsed ? 'justify-center px-0 py-3' : 'justify-start gap-3.5 px-4 py-3.5'
          ]"
          :title="isDesktopMenuCollapsed ? item.name : ''"
        >
          <component :is="item.icon" class="w-5 h-5 shrink-0 drop-shadow-sm" :class="route.path.startsWith(item.path) && item.path !== '/' || route.path === item.path ? 'opacity-100' : 'opacity-70 group-hover:opacity-100'" />
          <span class="transition-opacity duration-300 whitespace-nowrap" :class="isDesktopMenuCollapsed ? 'opacity-0 w-0 hidden' : 'opacity-100 w-auto'">{{ item.name }}</span>
        </router-link>
      </nav>

      <div class="p-3 border-t border-slate-200/50 dark:border-white/5 shrink-0 z-10 mt-auto">
        <router-link 
          to="/perfil"
          class="flex items-center rounded-xl transition-all duration-300 border border-transparent hover:bg-white/50 dark:hover:bg-white/5 group"
          :class="[
            route.path === '/perfil' ? 'bg-white/80 dark:bg-white/10 shadow-sm border-white/80 dark:border-white/15' : '',
            isDesktopMenuCollapsed ? 'justify-center p-2' : 'justify-start gap-3 p-2.5'
          ]"
          :title="isDesktopMenuCollapsed ? 'Mi Perfil' : ''"
        >
          <div class="w-9 h-9 shrink-0 rounded-full bg-slate-900 dark:bg-white text-white dark:text-slate-900 flex items-center justify-center font-bold text-sm shadow-sm group-hover:scale-105 transition-transform duration-300">
            {{ userInitial }}
          </div>
          <div class="flex flex-col min-w-0 transition-opacity duration-300" :class="isDesktopMenuCollapsed ? 'opacity-0 w-0 hidden' : 'opacity-100 w-auto'">
            <span class="text-sm font-bold text-slate-800 dark:text-white truncate">{{ userFirstName }}</span>
            <span class="text-[11px] font-semibold text-slate-500 dark:text-slate-400 truncate">Gestionar Perfil</span>
          </div>
        </router-link>
      </div>
    </aside>

    <main class="flex-1 flex flex-col h-full min-w-0 overflow-hidden relative z-10">
      
      <header class="h-20 flex items-center justify-between px-10 border-b border-slate-200/50 dark:border-white/10 backdrop-blur-3xl bg-white/20 dark:bg-[#0a0a0c]/40 z-20 shrink-0 transition-all duration-300">
        
        <div class="flex items-center gap-3">
          <div class="flex w-10 h-10 rounded-full bg-slate-900 dark:bg-white text-white dark:text-slate-900 items-center justify-center font-bold shadow-sm border border-white dark:border-white/10">
            {{ userInitial }}
          </div>
          <div>
            <h2 class="text-lg font-extrabold text-slate-900 dark:text-white leading-tight flex items-center gap-1.5 tracking-tight drop-shadow-sm">
              <span class="font-medium text-slate-500 dark:text-slate-400">{{ timeGreeting }},</span>
              {{ userFirstName }}
            </h2>
            <p class="text-[10px] font-bold text-slate-400 dark:text-slate-500 uppercase tracking-widest mt-0.5 capitalize">
              {{ currentDateDisplay }}
            </p>
          </div>
        </div>

        <div class="relative flex items-center justify-center">
          <ThemeToggle />
        </div>
      </header>

      <div class="flex-1 overflow-y-auto p-10 z-10 custom-scrollbar relative flex flex-col">
        <div class="flex-1">
          <router-view v-slot="{ Component }">
            <transition name="fade" mode="out-in">
              <component :is="Component" />
            </transition>
          </router-view>
        </div>

        <footer class="w-full mt-12 pt-6 pb-2 border-t border-slate-200/50 dark:border-white/5 flex flex-row items-center justify-between gap-3 text-[11px] font-semibold text-slate-400 dark:text-slate-500 shrink-0">
          <p class="tracking-wide">© {{ currentYear }} Diquis. Todos los derechos reservados.</p>
          <div class="flex items-center gap-1.5">
            <span>Powered by</span>
            <span class="text-slate-700 dark:text-slate-300 font-extrabold flex items-center gap-1 hover:text-rose-500 dark:hover:text-rose-400 transition-colors cursor-default">
              Cachollo Labs
              <Heart class="w-3.5 h-3.5 text-rose-500 fill-rose-500/20" />
            </span>
          </div>
        </footer>
      </div>
    </main>
  </div>
</template>

<style scoped>
.fade-enter-active, .fade-leave-active { transition: opacity 0.2s ease, transform 0.2s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; transform: translateY(5px); }

.custom-scrollbar::-webkit-scrollbar { width: 6px; }
.custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
.custom-scrollbar::-webkit-scrollbar-thumb { background: rgba(150, 150, 150, 0.3); border-radius: 10px; border: 1px solid transparent; background-clip: padding-box;}
:global(.dark) .custom-scrollbar::-webkit-scrollbar-thumb { background: rgba(255, 255, 255, 0.15); border: 1px solid transparent; background-clip: padding-box;}
</style>