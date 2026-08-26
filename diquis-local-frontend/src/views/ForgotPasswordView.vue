<script setup lang="ts">
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { authService } from '../services/authService';
import GlassCard from '../components/ui/GlassCard.vue';
import ThemeToggle from '../components/ui/ThemeToggle.vue';
import { Loader2, Mail, ArrowLeft } from 'lucide-vue-next';

const router = useRouter();
const email = ref('');
const isLoading = ref(false);
const isSuccess = ref(false);
const error = ref('');

const handleForgotPassword = async () => {
  if (!email.value) return;
  
  isLoading.value = true;
  error.value = '';
  
  try {
    await authService.forgotPassword({ email: email.value });
    isSuccess.value = true;
  } catch (err: any) {
    if (err.response?.status === 429) {
      error.value = 'Has intentado demasiadas veces. Por favor, espera un minuto.';
    } else {
      error.value = 'Hubo un problema al procesar tu solicitud. Intenta de nuevo más tarde.';
    }
  } finally {
    isLoading.value = false;
  }
};
</script>

<template>
  <GlassCard class="w-full max-w-[420px] p-8 md:p-10 mx-4">
    
    <div class="relative flex items-center justify-center mb-8 mt-2">
      <button @click="router.push('/auth/login')" class="absolute left-0 text-slate-400 hover:text-slate-800 dark:text-slate-500 dark:hover:text-white transition-colors">
        <ArrowLeft class="w-5 h-5" />
      </button>
      <div class="text-center">
        <h1 class="text-3xl font-extrabold text-slate-950 dark:text-white tracking-tight">Recuperar</h1>
        <p class="text-slate-500 dark:text-slate-400 mt-2 text-[10px] font-bold uppercase tracking-widest opacity-80">Contraseña</p>
      </div>
      <div class="absolute right-0">
        <ThemeToggle />
      </div>
    </div>

    <div v-if="isSuccess" class="text-center space-y-6">
      <div class="w-16 h-16 bg-emerald-100 dark:bg-emerald-500/20 text-emerald-600 dark:text-emerald-400 rounded-full flex items-center justify-center mx-auto mb-4">
        <Mail class="w-8 h-8" />
      </div>
      <h3 class="text-xl font-bold text-slate-900 dark:text-white">Revisa tu bandeja</h3>
      <p class="text-sm text-slate-600 dark:text-slate-400">
        Hemos enviado un correo a <span class="font-bold text-slate-900 dark:text-white">{{ email }}</span> con las instrucciones para restablecer tu contraseña.
      </p>
      <p class="text-xs text-slate-500 dark:text-slate-400 mt-4">
        No olvides revisar tu carpeta de Spam.
      </p>
      <button @click="router.push('/auth/login')" class="w-full mt-6 py-3.5 bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-900 dark:text-white font-bold rounded-xl transition-all">
        Volver al inicio de sesión
      </button>
    </div>

    <template v-else>
      <p class="text-sm text-slate-600 dark:text-slate-300 text-center mb-6">
        Ingresa el correo electrónico asociado a tu cuenta y te enviaremos un enlace seguro.
      </p>

      <div v-if="error" class="mb-6 p-3 rounded-xl bg-red-50 dark:bg-red-500/10 border border-red-200 dark:border-red-500/20 backdrop-blur-md flex items-center gap-3 text-red-600 dark:text-red-400 text-sm font-medium">
        <span class="bg-red-500 rounded-full p-1 text-white shrink-0">
          <svg class="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M6 18L18 6M6 6l12 12" /></svg>
        </span>
        <span class="leading-tight">{{ error }}</span>
      </div>

      <form @submit.prevent="handleForgotPassword" class="space-y-4">
        <div class="relative group">
          <Mail class="absolute left-4 top-3.5 h-5 w-5 text-slate-400 dark:text-slate-500 group-focus-within:text-slate-800 dark:group-focus-within:text-white transition-colors" />
          <input 
            v-model="email" 
            type="email" 
            required 
            placeholder="Correo electrónico" 
            class="w-full pl-12 pr-4 py-3.5 bg-white/50 dark:bg-black/20 border border-slate-200/50 dark:border-white/5 rounded-xl outline-none text-slate-900 dark:text-white transition-all focus:bg-white/80 dark:focus:bg-black/40 focus:ring-2 focus:ring-slate-950/20 dark:focus:ring-white/20"
          >
        </div>
        
        <button type="submit" :disabled="isLoading" class="w-full flex items-center justify-center gap-2 py-3.5 mt-2 bg-slate-900 dark:bg-white hover:bg-slate-800 dark:hover:bg-slate-200 text-white dark:text-slate-900 font-bold rounded-xl transition-all shadow-lg hover:shadow-xl disabled:opacity-50 disabled:cursor-not-allowed">
          <Loader2 v-if="isLoading" class="animate-spin h-5 w-5" />
          <span v-else>Enviar enlace</span>
        </button>
      </form>
    </template>

  </GlassCard>
</template>