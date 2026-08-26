<script setup lang="ts">
import { ref, computed, watch } from 'vue';
import { 
  AlertTriangle, Key, Eye, EyeOff, Trash2, X, Loader2 
} from 'lucide-vue-next';

const props = defineProps<{
  isOpen: boolean;
  isLoading?: boolean;
}>();

const emit = defineEmits(['close', 'confirm']);

const password = ref('');
const confirmationWord = ref('');
const showPassword = ref(false);

const TARGET_WORD = 'ELIMINAR';

watch(() => props.isOpen, (newVal) => {
  if (!newVal) {
    setTimeout(() => {
      password.value = '';
      confirmationWord.value = '';
      showPassword.value = false;
    }, 300);
  }
});

const isFormValid = computed(() => {
  return password.value.length >= 8 && confirmationWord.value === TARGET_WORD;
});

const handleClose = () => {
  if (!props.isLoading) {
    emit('close');
  }
};

const handleConfirm = () => {
  if (isFormValid.value && !props.isLoading) {
    emit('confirm', password.value);
  }
};
</script>

<template>
  <transition name="modal-pop">
    <div 
      v-if="isOpen" 
      class="fixed inset-0 z-[9999] flex items-center justify-center p-4 sm:p-6 bg-slate-900/60 dark:bg-black/80 backdrop-blur-md"
    >
      <div 
        class="relative w-full max-w-md p-6 sm:p-8 rounded-[2rem] border border-rose-500/30 dark:border-rose-500/20 bg-white/10 dark:bg-black/40 text-slate-800 dark:text-white flex flex-col items-center backdrop-blur-2xl shadow-[0_0_60px_rgba(225,29,72,0.15)] dark:shadow-[0_0_60px_rgba(225,29,72,0.1)]"
      >
        <button 
          v-if="!isLoading"
          @click="handleClose" 
          class="absolute top-5 right-5 p-2 rounded-full hover:bg-slate-200/50 dark:hover:bg-white/10 text-slate-500 dark:text-slate-400 transition-colors"
        >
          <X class="w-5 h-5" />
        </button>

        <div class="w-16 h-16 sm:w-20 sm:h-20 rounded-full bg-rose-500/20 dark:bg-rose-500/10 flex items-center justify-center mb-4 sm:mb-6 shadow-inner border border-rose-500/30 text-rose-600 dark:text-rose-500 ring-4 ring-rose-500/10">
          <AlertTriangle class="w-8 h-8 sm:w-10 sm:h-10 drop-shadow-md" />
        </div>
        
        <h4 class="text-xl sm:text-2xl font-black tracking-tight mb-2 drop-shadow-sm text-center">
          Eliminar Cuenta
        </h4>
        
        <div class="text-sm sm:text-[15px] font-medium leading-relaxed text-slate-600 dark:text-slate-300 mb-6 text-center space-y-2">
          <p>
            Esta acción es <strong class="text-rose-600 dark:text-rose-400">permanente e irreversible</strong>. 
          </p>
          <p class="text-xs sm:text-sm opacity-80">
            Se borrarán todas tus cuentas, presupuestos, categorías e historial de transacciones.
          </p>
        </div>

        <div class="w-full space-y-4 mb-8">
          <div class="space-y-1.5">
            <label class="text-[11px] font-bold text-slate-500 dark:text-slate-400 uppercase tracking-widest ml-1">
              Tu Contraseña Actual
            </label>
            <div class="relative">
              <Key class="absolute left-4 top-3.5 h-5 w-5 text-slate-400" />
              <input 
                v-model="password" 
                :type="showPassword ? 'text' : 'password'" 
                placeholder="Ingresa tu contraseña" 
                :disabled="isLoading"
                class="w-full pl-12 pr-12 py-3 bg-white/50 dark:bg-black/20 rounded-xl outline-none text-slate-900 dark:text-white font-medium border border-slate-200/50 dark:border-white/10 focus:ring-2 focus:ring-rose-500/50 transition-all placeholder:text-slate-400"
              >
              <button 
                type="button" 
                @click="showPassword = !showPassword" 
                class="absolute right-4 top-3.5 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200"
              >
                <EyeOff v-if="showPassword" class="h-5 w-5" />
                <Eye v-else class="h-5 w-5" />
              </button>
            </div>
          </div>

          <div class="space-y-1.5">
            <label class="text-[11px] font-bold text-slate-500 dark:text-slate-400 uppercase tracking-widest ml-1">
              Confirmación de Seguridad
            </label>
            <p class="text-[11px] text-slate-500 dark:text-slate-400 ml-1 mb-1">
              Escribe la palabra <strong class="text-rose-600 dark:text-rose-400 select-all">ELIMINAR</strong> para continuar.
            </p>
            <input 
              v-model="confirmationWord" 
              type="text" 
              placeholder="ELIMINAR" 
              :disabled="isLoading"
              class="w-full px-4 py-3 bg-rose-50/50 dark:bg-rose-950/20 rounded-xl outline-none text-rose-700 dark:text-rose-400 font-bold border border-rose-200/50 dark:border-rose-500/20 focus:ring-2 focus:ring-rose-500/50 transition-all text-center tracking-widest uppercase placeholder:tracking-normal placeholder:opacity-50"
            >
          </div>
        </div>

        <div class="w-full flex flex-col-reverse sm:flex-row gap-3">
          <button 
            @click="handleClose" 
            :disabled="isLoading"
            class="flex-1 py-3.5 rounded-xl font-bold tracking-wide transition-all border border-slate-200 dark:border-white/10 text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-white/5 disabled:opacity-50" 
          >
            Cancelar
          </button>
          
          <button 
            @click="handleConfirm" 
            :disabled="!isFormValid || isLoading"
            class="flex-1 py-3.5 rounded-xl font-bold tracking-wide transition-all shadow-lg flex items-center justify-center gap-2" 
            :class="isFormValid 
              ? 'bg-rose-600 hover:bg-rose-700 text-white shadow-rose-500/30' 
              : 'bg-slate-200 dark:bg-white/5 text-slate-400 dark:text-slate-600 cursor-not-allowed border border-transparent dark:border-white/5'"
          >
            <Loader2 v-if="isLoading" class="w-5 h-5 animate-spin" />
            <Trash2 v-else class="w-5 h-5" />
            {{ isLoading ? 'Destruyendo...' : 'Destruir Cuenta' }}
          </button>
        </div>

      </div>
    </div>
  </transition>
</template>

<style scoped>
.modal-pop-enter-active, .modal-pop-leave-active { 
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1); 
}
.modal-pop-enter-from, .modal-pop-leave-to { 
  opacity: 0; 
  transform: scale(0.95); 
}
</style>