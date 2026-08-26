<script setup lang="ts">
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '../stores/auth';
import { authService } from '../services/authService';
import GlassCard from '../components/ui/GlassCard.vue';
import ThemeToggle from '../components/ui/ThemeToggle.vue';
import { Loader2, Mail, Lock, Eye, EyeOff } from 'lucide-vue-next';

const router = useRouter();
const authStore = useAuthStore();
const email = ref('');
const password = ref('');
const isLoading = ref(false);
const error = ref('');

const showPassword = ref(false);
const ENABLE_SSO = ref(false);

const handleEmailLogin = async () => {
  isLoading.value = true;
  error.value = '';
  try {
    await authService.login({ username: email.value, password: password.value });
    const userData = await authService.getCurrentUser();
    authStore.setUser(userData);
    router.push('/');
  } catch (err: any) {
    error.value = err.response?.data?.detail || 'Credenciales incorrectas';
  } finally { 
    isLoading.value = false; 
  }
};

const handleSSOLogin = (provider: string) => {
  console.log(`Iniciando flujo SSO con ${provider}`);
};
</script>

<template>
  <GlassCard class="w-full max-w-[420px] p-8 md:p-10 mx-4">
    
    <div class="relative flex items-center justify-center mb-8 mt-2">
      <div class="text-center">
        <h1 class="text-4xl font-extrabold text-slate-950 dark:text-white tracking-tight">Diquis</h1>
        <p class="text-slate-500 dark:text-slate-400 mt-2 text-[10px] font-bold uppercase tracking-widest opacity-80">Iniciar Sesión</p>
      </div>
      <div class="absolute right-0">
        <ThemeToggle />
      </div>
    </div>

    <div v-if="error" class="mb-6 p-3 rounded-xl bg-red-50 dark:bg-red-500/10 border border-red-200 dark:border-red-500/20 backdrop-blur-md flex items-center gap-3 text-red-600 dark:text-red-400 text-sm font-medium">
      <span class="bg-red-500 rounded-full p-1 text-white shrink-0">
        <svg class="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M6 18L18 6M6 6l12 12" /></svg>
      </span>
      <span class="leading-tight">{{ error }}</span>
    </div>

    <form @submit.prevent="handleEmailLogin" class="space-y-4">
      <div class="relative group">
        <Mail class="absolute left-4 top-3.5 h-5 w-5 text-slate-400 dark:text-slate-500 group-focus-within:text-slate-800 dark:group-focus-within:text-white transition-colors" />
        <input v-model="email" type="email" required placeholder="Correo" class="w-full pl-12 pr-4 py-3.5 bg-white/50 dark:bg-black/20 border border-slate-200/50 dark:border-white/5 rounded-xl outline-none text-slate-900 dark:text-white transition-all focus:bg-white/80 dark:focus:bg-black/40 focus:ring-2 focus:ring-slate-950/20 dark:focus:ring-white/20">
      </div>
      
      <div class="relative group">
        <Lock class="absolute left-4 top-3.5 h-5 w-5 text-slate-400 dark:text-slate-500 group-focus-within:text-slate-800 dark:group-focus-within:text-white transition-colors" />
        <input v-model="password" :type="showPassword ? 'text' : 'password'" required placeholder="Contraseña" class="w-full pl-12 pr-12 py-3.5 bg-white/50 dark:bg-black/20 border border-slate-200/50 dark:border-white/5 rounded-xl outline-none text-slate-900 dark:text-white transition-all focus:bg-white/80 dark:focus:bg-black/40 focus:ring-2 focus:ring-slate-900/20 dark:focus:ring-white/20">
        
        <button type="button" @click="showPassword = !showPassword" class="absolute right-4 top-3.5 text-slate-400 dark:text-slate-500 hover:text-slate-800 dark:hover:text-white transition-colors focus:outline-none">
          <Eye v-if="!showPassword" class="h-5 w-5" />
          <EyeOff v-else class="h-5 w-5" />
        </button>
      </div>

      <button type="submit" :disabled="isLoading" class="w-full flex items-center justify-center gap-2 py-3.5 mt-6 bg-slate-900 dark:bg-white hover:bg-slate-800 dark:hover:bg-slate-200 text-white dark:text-slate-900 font-bold rounded-xl transition-all shadow-lg hover:shadow-xl disabled:opacity-50 disabled:cursor-not-allowed">
        <Loader2 v-if="isLoading" class="animate-spin h-5 w-5" />
        <span v-else>Entrar</span>
      </button>

      <div class="text-center pt-2">
        <router-link to="/auth/forgot-password" class="text-xs font-bold text-slate-500 hover:text-slate-900 dark:text-slate-400 dark:hover:text-white transition-colors">
          ¿Olvidaste tu contraseña?
        </router-link>
      </div>
    </form>

    <template v-if="ENABLE_SSO">
      <div class="mt-6 mb-6 flex items-center text-[10px] text-slate-400 dark:text-slate-500 uppercase font-bold tracking-widest">
        <div class="flex-1 border-t border-slate-200 dark:border-white/10"></div>
        <span class="px-4">O continúa con</span>
        <div class="flex-1 border-t border-slate-200 dark:border-white/10"></div>
      </div>

      <div class="grid grid-cols-2 gap-3">
        <button @click="handleSSOLogin('google')" type="button" class="flex items-center justify-center gap-2 py-3 px-4 rounded-xl bg-white/60 dark:bg-black/20 text-slate-700 dark:text-slate-300 text-sm font-bold border border-slate-200/50 dark:border-white/5 hover:bg-white/90 dark:hover:bg-white/10 transition-all shadow-sm">
          <svg class="w-5 h-5" viewBox="0 0 24 24">
              <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4" />
              <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853" />
              <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.2 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05" />
              <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335" />
          </svg>
          Google
        </button>
        <button @click="handleSSOLogin('microsoft')" type="button" class="flex items-center justify-center gap-2 py-3 px-4 rounded-xl bg-white/60 dark:bg-black/20 text-slate-700 dark:text-slate-300 text-sm font-bold border border-slate-200/50 dark:border-white/5 hover:bg-white/90 dark:hover:bg-white/10 transition-all shadow-sm">
          <svg class="w-5 h-5" viewBox="0 0 21 21" xmlns="http://www.w3.org/2000/svg">
            <rect x="1" y="1" width="9" height="9" fill="#f25022"/>
            <rect x="11" y="1" width="9" height="9" fill="#7fba00"/>
            <rect x="1" y="11" width="9" height="9" fill="#00a4ef"/>
            <rect x="11" y="11" width="9" height="9" fill="#ffb900"/>
          </svg>
          Microsoft
        </button>
      </div>
    </template>
    
    <div class="mt-8 text-center border-t border-slate-100 dark:border-white/5 pt-6">
      <p class="text-sm text-slate-500 dark:text-slate-400">
        ¿No tienes cuenta? <router-link to="/auth/registro" class="font-bold text-slate-900 dark:text-white hover:underline transition-all">Regístrate aquí</router-link>
      </p>
    </div>

  </GlassCard>
</template>