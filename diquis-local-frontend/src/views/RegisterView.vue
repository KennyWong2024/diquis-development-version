<script setup lang="ts">
import { ref, computed, watch } from 'vue';
import { useRouter } from 'vue-router';
import { authService } from '../services/authService';
import { useAuthStore } from '../stores/auth'; 
import GlassCard from '../components/ui/GlassCard.vue';
import ThemeToggle from '../components/ui/ThemeToggle.vue';
import GlassCurrencySelect from '../components/ui/GlassCurrencySelect.vue'; 
import GlassCountrySelect from '../components/ui/GlassCountrySelect.vue'; 
import { CURRENCIES } from '../constants/currencies'; 
import { Loader2, Mail, Lock, User, Calendar, Check, X, Eye, EyeOff } from 'lucide-vue-next'; 

const router = useRouter();
const authStore = useAuthStore(); 

const isLoading = ref(false);
const error = ref('');

const fullName = ref('');
const email = ref('');
const password = ref('');
    const dateOfBirth = ref('');
const selectedCountryCode = ref('cr');
const selectedCurrency = ref('CRC'); 

const showPassword = ref(false);

watch(selectedCountryCode, (newCountry) => {
  if (newCountry) {
    const matchedCurrency = CURRENCIES.find(c => c.countryCode.toLowerCase() === newCountry.toLowerCase());
    if (matchedCurrency) {
      selectedCurrency.value = matchedCurrency.code;
    }
  }
});

const sanitizeName = () => {
  fullName.value = fullName.value.replace(/[^a-zA-ZáéíóúÁÉÍÓÚñÑ\s]/g, '');
};

const isValidEmail = computed(() => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email.value);
});

const passwordReqs = computed(() => ({
  length: password.value.length >= 8,
  uppercase: /[A-Z]/.test(password.value),
  lowercase: /[a-z]/.test(password.value),
  number: /[0-9]/.test(password.value),
  special: /[^A-Za-z0-9]/.test(password.value)
}));

const passwordScore = computed(() => {
  return Object.values(passwordReqs.value).filter(Boolean).length;
});

const passwordStrengthProps = computed(() => {
  if (password.value.length === 0) return { color: 'bg-white/10', text: '', width: '0%' };
  if (passwordScore.value <= 2) return { color: 'bg-red-500', text: 'Débil', width: '33%' };
  if (passwordScore.value <= 4) return { color: 'bg-yellow-500', text: 'Media', width: '66%' };
  return { color: 'bg-green-500', text: 'Fuerte', width: '100%' };
});

const isFormValid = computed(() => {
  return fullName.value.trim().length >= 3 && 
         isValidEmail.value && 
         passwordScore.value === 5 && 
         dateOfBirth.value !== '' &&
         selectedCountryCode.value !== '' &&
         selectedCurrency.value !== ''; 
});

const handleRegister = async () => {
  if (!isFormValid.value) return;

  isLoading.value = true;
  error.value = '';
  try {
    await authService.register({
      email: email.value,
      password: password.value,
      full_name: fullName.value.trim(),
      date_of_birth: dateOfBirth.value,
      country_code: selectedCountryCode.value.toUpperCase(),
      default_currency: selectedCurrency.value
    });
    
    await authService.login({ username: email.value, password: password.value });
    const userData = await authService.getCurrentUser();
    authStore.setUser(userData);
    router.push('/');
  } catch (err: any) {
    error.value = err.response?.data?.detail || 'No se pudo crear la cuenta. Verifica tus datos o tu código de invitación.';
  } finally {
    isLoading.value = false;
  }
};
</script>

<template>
  <GlassCard class="relative w-full max-w-[450px] p-8 md:p-10 mx-4">
    
    <div class="relative flex items-center justify-center mb-8 mt-2">
      <div class="text-center">
        <h1 class="text-3xl font-extrabold text-slate-950 dark:text-white tracking-tight">Crear Cuenta</h1>
        <p class="text-slate-500 dark:text-slate-400 mt-1 text-xs font-semibold">Te damos la bienvenida a Diquis</p>
      </div>
      <div class="absolute right-0">
        <ThemeToggle />
      </div>
    </div>

    <div v-if="error" class="mb-6 p-3 rounded-xl bg-red-50 dark:bg-red-500/10 border border-red-200 dark:border-red-500/20 flex items-center gap-3 text-red-600 dark:text-red-400 text-sm">
      <span class="shrink-0">⚠️</span>
      <span class="leading-tight">{{ error }}</span>
    </div>

    <form @submit.prevent="handleRegister" class="space-y-4">
      
      <div class="relative group">
        <User class="absolute left-4 top-3.5 h-5 w-5 text-slate-400 dark:text-slate-500 group-focus-within:text-slate-800 dark:group-focus-within:text-white transition-colors" />
        <input v-model="fullName" @input="sanitizeName" type="text" required placeholder="Nombre Completo" class="w-full pl-12 pr-4 py-3.5 bg-white/50 dark:bg-black/20 border border-slate-200/50 dark:border-white/5 rounded-xl outline-none text-slate-900 dark:text-white transition-all focus:bg-white/80 dark:focus:bg-black/40 focus:ring-2 focus:ring-slate-900/20 dark:focus:ring-white/20">
      </div>
      
      <div class="relative group">
        <Mail class="absolute left-4 top-3.5 h-5 w-5 text-slate-400 dark:text-slate-500 group-focus-within:text-slate-800 dark:group-focus-within:text-white transition-colors" />
        <input v-model="email" type="email" required placeholder="Correo electrónico" :class="['w-full pl-12 pr-4 py-3.5 bg-white/50 dark:bg-black/20 border rounded-xl outline-none text-slate-900 dark:text-white transition-all focus:bg-white/80 dark:focus:bg-black/40 focus:ring-2 focus:ring-slate-900/20 dark:focus:ring-white/20', email.length > 0 && !isValidEmail ? 'border-red-400 dark:border-red-500/50' : 'border-slate-200/50 dark:border-white/5']">
      </div>

      <div class="relative group">
        <Calendar class="absolute left-4 top-3.5 h-5 w-5 text-slate-400 dark:text-slate-500 group-focus-within:text-slate-800 dark:group-focus-within:text-white transition-colors" />
        <input 
          v-model="dateOfBirth" 
          :type="dateOfBirth ? 'date' : 'text'"
          @focus="($event.target as HTMLInputElement).type = 'date'"
          @blur="!dateOfBirth && (($event.target as HTMLInputElement).type = 'text')"
          placeholder="Fecha de Nacimiento"
          required 
          class="w-full pl-12 pr-4 py-3.5 bg-white/50 dark:bg-black/20 border border-slate-200/50 dark:border-white/5 rounded-xl outline-none text-slate-900 dark:text-white transition-all focus:bg-white/80 dark:focus:bg-black/40 focus:ring-2 focus:ring-slate-900/20 dark:focus:ring-white/20 [color-scheme:light] dark:[color-scheme:dark]"
        >
      </div>

      <div class="grid grid-cols-2 gap-4">
          <div class="relative z-[60]">
            <GlassCountrySelect v-model="selectedCountryCode" placeholder="País..." />
          </div>
          <div class="relative z-[50]">
            <GlassCurrencySelect v-model="selectedCurrency" placeholder="Moneda..." />
          </div>
      </div>

      <div class="relative group">
        <Lock class="absolute left-4 top-3.5 h-5 w-5 text-slate-400 dark:text-slate-500 group-focus-within:text-slate-800 dark:group-focus-within:text-white transition-colors" />
        <input v-model="password" :type="showPassword ? 'text' : 'password'" required placeholder="Contraseña" class="w-full pl-12 pr-12 py-3.5 bg-white/50 dark:bg-black/20 border border-slate-200/50 dark:border-white/5 rounded-xl outline-none text-slate-900 dark:text-white transition-all focus:bg-white/80 dark:focus:bg-black/40 focus:ring-2 focus:ring-slate-900/20 dark:focus:ring-white/20">
        
        <button type="button" @click="showPassword = !showPassword" class="absolute right-4 top-3.5 text-slate-400 dark:text-slate-500 hover:text-slate-800 dark:hover:text-white transition-colors focus:outline-none">
          <Eye v-if="!showPassword" class="h-5 w-5" />
          <EyeOff v-else class="h-5 w-5" />
        </button>

        <div class="mt-2.5 h-1 w-full bg-white/10 rounded-full overflow-hidden shadow-inner">
          <div class="h-full transition-all duration-500 ease-out" :class="passwordStrengthProps.color" :style="{ width: passwordStrengthProps.width }"></div>
        </div>

        <div class="grid grid-cols-2 gap-2 mt-3 text-[10px] font-medium transition-opacity duration-300 uppercase tracking-wide" :class="password.length > 0 ? 'opacity-100' : 'opacity-0 h-0 overflow-hidden'">
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



      <button type="submit" :disabled="isLoading || !isFormValid" class="w-full flex items-center justify-center gap-2 py-3.5 bg-slate-900 dark:bg-white hover:bg-slate-800 dark:hover:bg-slate-200 text-white dark:text-slate-900 font-bold rounded-xl transition-all shadow-lg hover:shadow-xl disabled:opacity-50 disabled:cursor-not-allowed mt-6">
        <Loader2 v-if="isLoading" class="animate-spin h-5 w-5" />
        <span v-else>Comenzar ahora</span>
      </button>
    </form>

    <div class="mt-8 text-center">
      <p class="text-sm text-slate-500 dark:text-slate-400">
        ¿Ya tienes cuenta? <router-link to="/auth/login" class="font-bold text-slate-900 dark:text-white hover:underline transition-all">Inicia sesión</router-link>
      </p>
    </div>
  </GlassCard>
</template>