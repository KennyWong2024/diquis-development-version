<script setup lang="ts">
import { ref, watch, computed } from 'vue';
import GlassModal from '../ui/GlassModal.vue';
import GlassAlert from '../ui/GlassAlert.vue';
import { 
  Loader2, Palette, Type, Trash2, AlertTriangle, Coins, TrendingDown 
} from 'lucide-vue-next';
import { CURRENCIES } from '../../constants/currencies';
import type { Account, AccountUpdatePayload } from '../../types/account';

const props = defineProps<{
  isOpen: boolean;
  account: Account | null;
  isSaving: boolean;
  errorMsg?: string;
}>();

const emit = defineEmits<{
  (e: 'close'): void;
  (e: 'save', payload: AccountUpdatePayload & { id: string }): void;
  (e: 'delete', id: string): void;
  (e: 'clearError'): void;
}>();

const editName = ref('');
const editColor = ref('');
const editAllowNegative = ref(false);
const showDeleteConfirm = ref(false);
const showErrorPopup = ref(false);
const localApiError = ref('');

const colors = [
  { id: 'blue', name: 'Azul Zafiro', hex: 'bg-blue-500', border: 'border-blue-400' },
  { id: 'red', name: 'Rojo Rubí', hex: 'bg-red-500', border: 'border-red-400' },
  { id: 'green', name: 'Verde Esmeralda', hex: 'bg-emerald-500', border: 'border-emerald-400' },
  { id: 'gold', name: 'Oro Premium', hex: 'bg-amber-400', border: 'border-amber-300' },
  { id: 'silver', name: 'Plata Clásica', hex: 'bg-slate-300', border: 'border-slate-400' },
  { id: 'black', name: 'Negro Élite', hex: 'bg-gray-900', border: 'border-gray-700' }
];

watch(() => props.errorMsg, (newErr) => {
  if (newErr) {
    localApiError.value = newErr;
    showErrorPopup.value = true;
  }
});

watch(() => props.isOpen, (newVal) => {
  if (newVal && props.account) {
    editName.value = props.account.name;
    editColor.value = props.account.theme_color || 'silver';
    editAllowNegative.value = props.account.allow_negative_balance;
    showDeleteConfirm.value = false; 
    showErrorPopup.value = false;
    localApiError.value = '';
  }
});

const accountCurrency = computed(() => {
  if (!props.account) return null;
  return CURRENCIES.find(x => x.code === props.account?.currency) || null;
});

const accountCurrencyDisplay = computed(() => {
  if (!accountCurrency.value) return props.account?.currency || '';
  return `${accountCurrency.value.code} - ${accountCurrency.value.name}`;
});

const handleCloseError = () => {
  showErrorPopup.value = false;
  localApiError.value = '';
  emit('clearError');
};

const handleSave = () => {
  if (!props.account) return;
  
  emit('save', {
    id: props.account.id,
    name: editName.value.trim(),
    theme_color: editColor.value,
    allow_negative_balance: editAllowNegative.value
  });
};

const handleDelete = () => {
  if (!props.account) return;
  if (showDeleteConfirm.value) {
    emit('delete', props.account.id);
  } else {
    showDeleteConfirm.value = true;
  }
};
</script>

<template>
  <GlassModal :is-open="isOpen" title="Editar Cuenta" @close="emit('close')">
    
    <GlassAlert 
      :show="showErrorPopup" 
      :message="localApiError" 
      type="error" 
      @close="handleCloseError" 
    />

    <div class="space-y-6">
      
      <div>
        <label class="flex items-center gap-2 text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-widest mb-2 ml-1">
          <Type class="w-4 h-4" /> Nombre de la Cuenta
        </label>
        <input 
          v-model="editName" 
          type="text" 
          placeholder="Ej. Billetera Principal"
          class="w-full px-4 py-3.5 bg-white/50 dark:bg-black/20 border border-slate-200/50 dark:border-white/5 rounded-xl outline-none text-slate-900 dark:text-white transition-all focus:bg-white/80 dark:focus:bg-black/40 focus:ring-2 focus:ring-slate-900/20 dark:focus:ring-white/20"
        >
      </div>

      <div class="opacity-70 cursor-not-allowed">
        <label class="flex items-center gap-2 text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-widest mb-2 ml-1">
          <Coins class="w-4 h-4" /> Moneda Asignada (No editable)
        </label>
        <div class="w-full flex items-center justify-between px-4 py-3.5 bg-slate-100/50 dark:bg-black/20 border border-slate-200/50 dark:border-white/5 rounded-xl select-none">
           <div class="flex items-center gap-2">
             <img 
               v-if="accountCurrency"
               :src="`https://flagcdn.com/${accountCurrency.countryCode}.svg`" 
               :alt="accountCurrency.code"
               class="w-[18px] h-[14px] object-cover rounded-[2px] shadow-sm"
             />
             <span class="text-sm font-bold text-slate-700 dark:text-slate-300">{{ accountCurrencyDisplay }}</span>
           </div>
        </div>
      </div>

      <div>
        <div class="flex items-center justify-between p-4 rounded-xl bg-slate-50/80 dark:bg-black/20 border border-slate-200/50 dark:border-white/5 hover:bg-slate-100 dark:hover:bg-white/5 transition-colors">
          <div class="flex items-center gap-3">
            <div class="p-2 rounded-lg" :class="editAllowNegative ? 'bg-rose-100 dark:bg-rose-500/20 text-rose-600 dark:text-rose-400' : 'bg-slate-200 dark:bg-white/10 text-slate-500'">
              <TrendingDown class="w-4 h-4" />
            </div>
            <div>
              <p class="text-sm font-bold text-slate-800 dark:text-white">Admitir saldos negativos</p>
              <p class="text-[10px] sm:text-xs text-slate-500 dark:text-slate-400 mt-0.5">Permite que el balance caiga por debajo de cero</p>
            </div>
          </div>
          <button 
            @click="editAllowNegative = !editAllowNegative" 
            class="relative inline-flex h-6 w-11 items-center rounded-full transition-colors duration-300 focus:outline-none focus:ring-2 focus:ring-emerald-500/50 shrink-0"
            :class="editAllowNegative ? 'bg-emerald-500' : 'bg-slate-300 dark:bg-white/20'"
          >
            <span class="inline-block h-4 w-4 transform rounded-full bg-white shadow-sm transition duration-300" :class="editAllowNegative ? 'translate-x-6' : 'translate-x-1'" />
          </button>
        </div>
      </div>

      <div>
        <label class="flex items-center gap-2 text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-widest mb-3 ml-1">
          <Palette class="w-4 h-4" /> Diseño de la Tarjeta
        </label>
        
        <div class="grid grid-cols-2 sm:grid-cols-3 gap-3">
          <button 
            v-for="color in colors" 
            :key="color.id"
            @click="editColor = color.id"
            class="relative flex flex-col items-center justify-center p-4 rounded-2xl border-2 transition-all duration-300 group overflow-hidden"
            :class="editColor === color.id ? 'border-slate-800 dark:border-white bg-white/60 dark:bg-white/10 shadow-md scale-[1.02]' : 'border-transparent bg-white/30 dark:bg-black/20 hover:bg-white/50 dark:hover:bg-white/5'"
          >
            <div class="w-8 h-8 rounded-full mb-2 shadow-inner border transition-transform duration-300 group-hover:scale-110" :class="[color.hex, color.border]"></div>
            <span class="text-[10px] font-bold text-slate-700 dark:text-slate-300 uppercase tracking-wider text-center">{{ color.name }}</span>
            <div v-if="editColor === color.id" class="absolute top-2 right-2 text-slate-800 dark:text-white">
              <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7" /></svg>
            </div>
          </button>
        </div>
      </div>

    </div>

    <div class="mt-8 space-y-3">
      <button 
        @click="handleSave" 
        :disabled="isSaving || !editName.trim()"
        class="w-full py-4 bg-slate-900 dark:bg-white hover:bg-slate-800 dark:hover:bg-slate-200 text-white dark:text-slate-900 font-bold rounded-xl transition-all shadow-lg hover:shadow-xl flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        <Loader2 v-if="isSaving" class="animate-spin h-5 w-5" />
        <span v-else>Guardar Cambios</span>
      </button>

      <transition name="fade">
        <button 
          @click="handleDelete" 
          :disabled="isSaving"
          class="w-full py-3.5 rounded-xl font-bold transition-all flex items-center justify-center gap-2 disabled:opacity-50"
          :class="showDeleteConfirm ? 'bg-red-500 hover:bg-red-600 text-white shadow-lg shadow-red-500/20' : 'bg-transparent text-slate-500 hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-500/10 border border-transparent hover:border-red-200 dark:hover:border-red-500/20'"
        >
          <template v-if="showDeleteConfirm">
            <AlertTriangle class="w-4 h-4" /> ¿Estás seguro? Eliminar cuenta
          </template>
          <template v-else>
            <Trash2 class="w-4 h-4" /> Eliminar Cuenta
          </template>
        </button>
      </transition>
    </div>

  </GlassModal>
</template>

<style scoped>
.fade-enter-active, .fade-leave-active { transition: opacity 0.3s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>