<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { authService } from '../services/authService';
import GlassCard from '../components/ui/GlassCard.vue';
import ThemeToggle from '../components/ui/ThemeToggle.vue';
import { Loader2, Lock, Eye, EyeOff, Check, X } from 'lucide-vue-next';

const route = useRoute();
const router = useRouter();

const token = ref('');
const newPassword = ref('');
const isLoading = ref(false);
const error = ref('');
const isSuccess = ref(false);
const showPassword = ref(false);

onMounted(() => {
  const queryToken = route.query.token as string;
  if (queryToken) {
    token.value = queryToken;
  } else {
    error.value = 'El enlace de recuperación es inválido o está incompleto.';
  }
});

const passwordReqs = computed(() => ({
  length: newPassword.value.length >= 8,
  uppercase: /[A-Z]/.test(newPassword.value),
  lowercase: /[a-z]/.test(newPassword.value),
  number: /[0-9]/.test(newPassword.value),
  special: /[^A-Za-z0-9]/.test(newPassword.value)
}));

const passwordScore = computed(() => {
  return Object.values(passwordReqs.value).filter(Boolean).length;
});

const passwordStrengthProps = computed(() => {
  if (newPassword.value.length === 0) return { color: 'bg-white/10', text: '', width: '0%' };
  if (passwordScore.value <= 2) return { color: 'bg-red-500', text: 'Débil', width: '33%' };
  if (passwordScore.value <= 4) return { color: 'bg-yellow-500', text: 'Media', width: '66%' };
  return { color: 'bg-green-500', text: 'Fuerte', width: '100%' };
});

const isFormValid = computed(() => {
  return token.value !== '' && passwordScore.value === 5;
});

const handleResetPassword = async () => {
  if (!isFormValid.value) return;
  
  isLoading.value = true;
  error.value = '';
  
  try {
    await authService.resetPassword({
      token: token.value,
      new_password: newPassword.value
    });
    
    isSuccess.value = true;
    setTimeout(() => {
      router.push('/auth/login');
    }, 3000);
    
  } catch (err: any) {
    error.value = err.response?.data?.detail || 'El enlace ha expirado o no es válido.';
  } finally {
    isLoading.value = false;
  }
};
</script>

<template>
  <GlassCard class="w-full max-w-[420px] p-8 md:p-10 mx-4">
    
    <div class="relative flex items-center justify-center mb-8 mt-2">
      <div class="text-center">
        <h1 class="text-3xl font-extrabold text-slate-950 dark:text-white tracking-tight">Nueva</h1>
        <p class="text-slate-500 dark:text-slate-400 mt-2 text-[10px] font-bold uppercase tracking-widest opacity-80">Contraseña</p>
      </div>
      <div class="absolute right-0">
        <ThemeToggle />
      </div>
    </div>

    <div v-if="isSuccess" class="text-center space-y-6">
      <div class="w-16 h-16 bg-green-100 dark:bg-green-500/20 text-green-600 dark:text-green-400 rounded-full flex items-center justify-center mx-auto mb-4">
        <Check class="w-8 h-8" />
      </div>
      <h3 class="text-xl font-bold text-slate-900 dark:text-white">¡Actualización exitosa!</h3>
      <p class="text-sm text-slate-600 dark:text-slate-400">
        Tu contraseña ha sido actualizada. Serás redirigido al inicio de sesión en unos segundos.
      </p>
    </div>

    <template v-else>
      <div v-if="error" class="mb-6 p-3 rounded-xl bg-red-50 dark:bg-red-500/10 border border-red-200 dark:border-red-500/20 backdrop-blur-md flex items-center gap-3 text-red-600 dark:text-red-400 text-sm font-medium">
        <span class="bg-red-500 rounded-full p-1 text-white shrink-0">
          <svg class="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M6 18L18 6M6 6l12 12" /></svg>
        </span>
        <span class="leading-tight">{{ error }}</span>
      </div>

      <form @submit.prevent="handleResetPassword" class="space-y-4">
        <div class="relative group">
          <Lock class="absolute left-4 top-3.5 h-5 w-5 text-slate-400 dark:text-slate-500 group-focus-within:text-slate-800 dark:group-focus-within:text-white transition-colors" />
          <input 
            v-model="newPassword" 
            :type="showPassword ? 'text' : 'password'" 
            required 
            placeholder="Nueva contraseña" 
            :disabled="!token"
            class="w-full pl-12 pr-12 py-3.5 bg-white/50 dark:bg-black/20 border border-slate-200/50 dark:border-white/5 rounded-xl outline-none text-slate-900 dark:text-white transition-all focus:bg-white/80 dark:focus:bg-black/40 focus:ring-2 focus:ring-slate-900/20 dark:focus:ring-white/20 disabled:opacity-50"
          >
          
          <button type="button" @click="showPassword = !showPassword" :disabled="!token" class="absolute right-4 top-3.5 text-slate-400 dark:text-slate-500 hover:text-slate-800 dark:hover:text-white transition-colors focus:outline-none disabled:opacity-50">
            <Eye v-if="!showPassword" class="h-5 w-5" />
            <EyeOff v-else class="h-5 w-5" />
          </button>

          <div class="mt-2.5 h-1 w-full bg-white/10 rounded-full overflow-hidden shadow-inner">
            <div class="h-full transition-all duration-500 ease-out" :class="passwordStrengthProps.color" :style="{ width: passwordStrengthProps.width }"></div>
          </div>

          <div class="grid grid-cols-2 gap-2 mt-3 text-[10px] font-medium transition-opacity duration-300 uppercase tracking-wide" :class="newPassword.length > 0 ? 'opacity-100' : 'opacity-0 h-0 overflow-hidden'">
            <div class="flex items-center gap-1.5" :class="passwordReqs.length ? 'text-green-600 dark:text-green-400' : 'text-slate-400 dark:text-slate-500'">
              <Check v-if="passwordReqs.length" class="w-3 h-3" /> <X v-else class="w-3 h-3" /> Mín. 8 letras
            </div>
            <div class="flex items-center gap-1.5" :class="passwordReqs.uppercase ? 'text-green-600 dark:text-green-400' : 'text-slate-400 dark:text-slate-500'">
              <Check v-if="passwordReqs.uppercase" class="w-3 h-3" /> <X v-else class="w-3 h-3" /> 1 Mayúscula
            </div>
            <div class="flex items-center gap-1.5" :class="passwordReqs.lowercase ? 'text-green-600 dark:text-green-400' : 'text-slate-400 dark:text-slate-500'">
              <Check v-if="passwordReqs.lowercase" class="w-3 h-3" /> <X v-else class="w-3 h-3" /> 1 Minúscula
            </div>
            <div class="flex items-center gap-1.5" :class="passwordReqs.number ? 'text-green-600 dark:text-green-400' : 'text-slate-400 dark:text-slate-500'">
              <Check v-if="passwordReqs.number" class="w-3 h-3" /> <X v-else class="w-3 h-3" /> 1 Número
            </div>
            <div class="flex items-center gap-1.5" :class="passwordReqs.special ? 'text-green-600 dark:text-green-400' : 'text-slate-400 dark:text-slate-500'">
              <Check v-if="passwordReqs.special" class="w-3 h-3" /> <X v-else class="w-3 h-3" /> 1 Símbolo
            </div>
          </div>
        </div>

        <button type="submit" :disabled="isLoading || !isFormValid" class="w-full flex items-center justify-center gap-2 py-3.5 mt-2 bg-slate-900 dark:bg-white hover:bg-slate-800 dark:hover:bg-slate-200 text-white dark:text-slate-900 font-bold rounded-xl transition-all shadow-lg hover:shadow-xl disabled:opacity-50 disabled:cursor-not-allowed">
          <Loader2 v-if="isLoading" class="animate-spin h-5 w-5" />
          <span v-else>Actualizar</span>
        </button>
      </form>
    </template>

  </GlassCard>
</template>