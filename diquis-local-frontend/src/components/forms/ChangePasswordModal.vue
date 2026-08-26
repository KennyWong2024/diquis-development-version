<script setup lang="ts">
import { ref, computed } from 'vue';
import { authService } from '../../services/authService';
import GlassModal from '../ui/GlassModal.vue';
import { KeyRound, Lock, CheckCircle2, Loader2, AlertCircle, Eye, EyeOff, Check, X } from 'lucide-vue-next';

const props = defineProps<{ isOpen: boolean }>();
const emit = defineEmits(['close', 'success']);

const currentPassword = ref('');
const newPassword = ref('');
const confirmPassword = ref('');

const showCurrent = ref(false);
const showNew = ref(false);
const showConfirm = ref(false);

const isLoading = ref(false);
const errorMessage = ref('');

const resetForm = () => {
  currentPassword.value = '';
  newPassword.value = '';
  confirmPassword.value = '';
  errorMessage.value = '';
  showCurrent.value = false;
  showNew.value = false;
  showConfirm.value = false;
};

const handleClose = () => {
  resetForm();
  emit('close');
};

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

const isValid = computed(() => {
  return currentPassword.value.length > 0 && 
         passwordScore.value === 5 && 
         newPassword.value === confirmPassword.value;
});

const getPasswordMatchError = computed(() => {
  if (confirmPassword.value.length > 0 && newPassword.value !== confirmPassword.value) {
    return 'Las contraseñas nuevas no coinciden';
  }
  return '';
});

const handleSubmit = async () => {
  if (!isValid.value) return;
  
  isLoading.value = true;
  errorMessage.value = '';

  try {
    await authService.changePassword({
      current_password: currentPassword.value,
      new_password: newPassword.value
    });
    
    resetForm();
    emit('success', 'Contraseña actualizada exitosamente');
    emit('close');
  } catch (error: any) {
    errorMessage.value = error.response?.data?.detail || 'Error al cambiar la contraseña. Verifica tu contraseña actual.';
  } finally {
    isLoading.value = false;
  }
};
</script>

<template>
  <GlassModal :is-open="isOpen" title="Seguridad" @close="handleClose">
    
    <div class="flex flex-col items-center mb-6 text-center">
      <div class="w-16 h-16 rounded-full bg-slate-100 dark:bg-white/5 flex items-center justify-center mb-4 border border-slate-200/50 dark:border-white/5 shadow-inner">
        <KeyRound class="w-8 h-8 text-slate-700 dark:text-slate-300" />
      </div>
      <h3 class="text-xl font-extrabold text-slate-800 dark:text-white tracking-tight">Cambiar Contraseña</h3>
      <p class="text-xs font-medium text-slate-500 dark:text-slate-400 mt-1 max-w-[250px]">Crea una contraseña fuerte para mantener tu cuenta segura.</p>
    </div>

    <transition name="fade-slide">
      <div v-if="errorMessage" class="mb-6 p-3 bg-rose-50 dark:bg-rose-500/10 border border-rose-200 dark:border-rose-500/20 rounded-xl flex items-start gap-3 text-rose-700 dark:text-rose-400 text-sm shadow-sm">
        <AlertCircle class="w-5 h-5 shrink-0 mt-0.5" />
        <span class="font-medium leading-snug">{{ errorMessage }}</span>
      </div>
    </transition>

    <div class="space-y-4 mb-8">
      
      <div class="relative group">
        <Lock class="absolute left-4 top-3.5 h-5 w-5 text-slate-400 transition-colors group-focus-within:text-slate-800 dark:group-focus-within:text-white" />
        <input 
          v-model="currentPassword" 
          :type="showCurrent ? 'text' : 'password'" 
          placeholder="Contraseña Actual" 
          class="w-full pl-12 pr-12 py-3.5 bg-white/50 dark:bg-black/20 border border-slate-200/50 dark:border-white/5 rounded-xl outline-none text-slate-900 dark:text-white transition-all focus:bg-white/80 dark:focus:bg-black/40 focus:ring-2 focus:ring-slate-900/20 dark:focus:ring-white/20"
        >
        <button type="button" @click="showCurrent = !showCurrent" class="absolute right-4 top-3.5 text-slate-400 hover:text-slate-700 dark:hover:text-slate-300 transition-colors">
            <EyeOff v-if="showCurrent" class="w-5 h-5" />
            <Eye v-else class="w-5 h-5" />
        </button>
      </div>

      <div class="w-full h-px bg-slate-200/50 dark:bg-white/5 my-4"></div>

      <div class="relative group">
        <KeyRound class="absolute left-4 top-3.5 h-5 w-5 text-slate-400 transition-colors group-focus-within:text-emerald-500" />
        <input 
          v-model="newPassword" 
          :type="showNew ? 'text' : 'password'" 
          placeholder="Nueva Contraseña" 
          class="w-full pl-12 pr-12 py-3.5 bg-white/50 dark:bg-black/20 border border-slate-200/50 dark:border-white/5 rounded-xl outline-none text-slate-900 dark:text-white transition-all focus:bg-white/80 dark:focus:bg-black/40 focus:ring-2 focus:ring-emerald-500/20"
        >
        <button type="button" @click="showNew = !showNew" class="absolute right-4 top-3.5 text-slate-400 hover:text-slate-700 dark:hover:text-slate-300 transition-colors">
            <EyeOff v-if="showNew" class="w-5 h-5" />
            <Eye v-else class="w-5 h-5" />
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

      <div class="relative group mt-2">
        <CheckCircle2 class="absolute left-4 top-3.5 h-5 w-5 transition-colors" :class="newPassword && newPassword === confirmPassword && passwordScore === 5 ? 'text-emerald-500' : 'text-slate-400 group-focus-within:text-emerald-500'" />
        <input 
          v-model="confirmPassword" 
          :type="showConfirm ? 'text' : 'password'" 
          placeholder="Confirmar Nueva Contraseña" 
          class="w-full pl-12 pr-12 py-3.5 bg-white/50 dark:bg-black/20 border border-slate-200/50 dark:border-white/5 rounded-xl outline-none text-slate-900 dark:text-white transition-all focus:bg-white/80 dark:focus:bg-black/40 focus:ring-2 focus:ring-emerald-500/20"
        >
        <button type="button" @click="showConfirm = !showConfirm" class="absolute right-4 top-3.5 text-slate-400 hover:text-slate-700 dark:hover:text-slate-300 transition-colors">
            <EyeOff v-if="showConfirm" class="w-5 h-5" />
            <Eye v-else class="w-5 h-5" />
        </button>
      </div>
      
      <div class="min-h-[20px] px-2">
         <p v-if="getPasswordMatchError" class="text-xs font-bold text-amber-500 dark:text-amber-400">
           {{ getPasswordMatchError }}
         </p>
      </div>

    </div>

    <div class="flex mt-4 pt-4 border-t border-slate-200/50 dark:border-white/5 shrink-0 bg-white/30 dark:bg-black/10 -mx-6 px-6 pb-2">
      <button 
        @click="handleSubmit" 
        :disabled="!isValid || isLoading"
        class="w-full py-3.5 bg-slate-900 dark:bg-white text-white dark:text-slate-900 font-bold rounded-xl flex items-center justify-center gap-2 transition-all shadow-lg hover:shadow-xl disabled:opacity-50 disabled:cursor-not-allowed"
      >
        <Loader2 v-if="isLoading" class="animate-spin h-5 w-5" />
        <span v-else>Actualizar Contraseña</span>
      </button>
    </div>

  </GlassModal>
</template>

<style scoped>
.fade-slide-enter-active, .fade-slide-leave-active { transition: all 0.3s ease; }
.fade-slide-enter-from, .fade-slide-leave-to { opacity: 0; transform: translateY(-10px); }
</style>