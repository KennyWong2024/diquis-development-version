<script setup lang="ts">
import { ref, computed, watch } from 'vue';
import { useFinanceStore } from '../../stores/finance';
import { useCategoryStore } from '../../stores/category';
import { CURRENCIES } from '../../constants/currencies';
import GlassSelect from '../ui/GlassSelect.vue';
import GlassNativeDatePicker from '../ui/GlassNativeDatePicker.vue';
import GlassCurrencyInput from '../ui/GlassCurrencyInput.vue';
import GlassAlert from '../ui/GlassAlert.vue';
import { resolveIcon } from '../../utils/icons';
import { 
  Type, Loader2, Check, X, Star, Calculator, Coins, Wallet, Info
} from 'lucide-vue-next';
import type { ScheduledUpdate } from '../../types/scheduled';
import type { Category } from '../../types/category';

const props = defineProps<{ 
  schedule: any; 
  isSaving: boolean;
  apiError?: string;
}>();

const emit = defineEmits<{
  (e: 'save', data: ScheduledUpdate): void;
  (e: 'cancel'): void;
  (e: 'clearError'): void;
}>();

const financeStore = useFinanceStore();
const categoryStore = useCategoryStore();

// Inicialización segura de la fecha
const initDate = () => {
  if (!props.schedule?.next_due_date) return new Date();
  const [sYear, sMonth, sDay] = props.schedule.next_due_date.split('T')[0].split('-').map(Number);
  return new Date(sYear, sMonth - 1, sDay);
};

const txType = ref<'expense' | 'income' | 'transfer'>(props.schedule?.type || 'expense');
const name = ref(props.schedule?.name || '');
const amount = ref<string>((props.schedule?.expected_amount || 0).toString());
const accountId = ref(props.schedule?.account_id || '');
const transferToAccountId = ref(props.schedule?.transfer_to_account_id || '');
const categoryId = ref(props.schedule?.category_id || '');
const frequency = ref(props.schedule?.frequency || 'monthly');
const nextDate = ref<Date>(initDate());
const isEstimated = ref<boolean>(!!props.schedule?.is_estimated);
const autoExecute = ref<boolean>(!!props.schedule?.auto_execute);
const isEssential = ref<boolean>(!!props.schedule?.is_essential);
const txCurrency = ref<string>(props.schedule?.currency || 'CRC');

const frequencies = [
  { id: 'daily', name: 'Diario' }, { id: 'weekly', name: 'Semanal' }, { id: 'biweekly', name: 'Quincenal' },
  { id: 'monthly', name: 'Mensual' }, { id: 'quarterly', name: 'Trimestral' }, { id: 'yearly', name: 'Anual' }
];

const showError = ref(false);
const errorMessage = ref('');

watch(() => props.apiError, (newErr) => {
  if (newErr) {
    errorMessage.value = newErr;
    showError.value = true;
  }
});

const handleCloseError = () => {
  showError.value = false;
  emit('clearError'); 
};

const selectedAccount = computed(() => financeStore.accounts.find(a => a.id === accountId.value));
const selectedTransferAccount = computed(() => financeStore.accounts.find(a => a.id === transferToAccountId.value));

const txCurrencySymbol = computed(() => {
  const c = CURRENCIES.find(x => x.code === txCurrency.value);
  return c ? c.symbol : '$';
});

const isCrossCurrency = computed(() => {
  const sourceMismatch = selectedAccount.value && txCurrency.value !== selectedAccount.value.currency;
  const transferMismatch = txType.value === 'transfer' && selectedAccount.value && selectedTransferAccount.value && selectedAccount.value.currency !== selectedTransferAccount.value.currency;
  return Boolean(sourceMismatch || transferMismatch);
});

const toggleAutoExecute = () => {
  if (!isCrossCurrency.value) {
    autoExecute.value = !autoExecute.value;
  }
};

const filteredCategories = computed(() => {
  if (txType.value === 'transfer') return [];
  return categoryStore.categories
    .filter((c: Category) => txType.value === 'income' ? c.domain === 'income' : c.domain !== 'income')
    .sort((a: Category, b: Category) => a.sort_order - b.sort_order) 
    .map((c: Category) => ({ id: c.id, name: c.name, icon: resolveIcon(c.icon) })); 
});

const selectedCategoryIcon = computed(() => {
  const cat = filteredCategories.value.find(c => c.id === categoryId.value);
  return cat ? cat.icon : Type;
});

const allowedAccounts = computed(() => {
  return financeStore.accounts
    .filter(a => txType.value === 'income' || a.allow_negative_balance)
    .map(a => ({ id: a.id, name: a.name, icon: Wallet }));
});

const missingFields = computed(() => {
  const missing = [];
  if (!name.value.trim()) missing.push('nombre');
  if (Number(amount.value) <= 0) missing.push('monto');
  if (!accountId.value) missing.push('cuenta origen');

  if (txType.value === 'transfer') {
    if (!transferToAccountId.value) missing.push('cuenta destino');
    if (accountId.value && accountId.value === transferToAccountId.value) missing.push('cuentas distintas');
  } else {
    if (!categoryId.value) missing.push('categoría');
  }
  return missing;
});

const hasMissingField = (field: string) => missingFields.value.includes(field);
const isValid = computed(() => missingFields.value.length === 0);

const handleSave = () => {
  if (!isValid.value) return;

  const y = nextDate.value.getFullYear();
  const m = String(nextDate.value.getMonth() + 1).padStart(2, '0');
  const d = String(nextDate.value.getDate()).padStart(2, '0');
  const bulletproofDateString = `${y}-${m}-${d}`;

  const updateData: ScheduledUpdate = {
    name: name.value,
    expected_amount: Number(amount.value),
    account_id: accountId.value,
    transfer_to_account_id: transferToAccountId.value || undefined,
    category_id: categoryId.value || undefined,
    frequency: frequency.value as any,
    next_due_date: bulletproofDateString,
    is_estimated: isEstimated.value,
    auto_execute: !isEstimated.value && autoExecute.value && !isCrossCurrency.value,
    is_essential: isEssential.value,
  };

  emit('save', updateData);
};
</script>

<template>
  <div class="flex flex-col h-full animate-in fade-in slide-in-from-right-4 duration-300">
    <GlassAlert :show="showError" :message="errorMessage" type="error" @close="handleCloseError" class="mb-4" />

    <div class="flex-1 overflow-y-auto pr-2 custom-scrollbar space-y-6">
      
      <div class="relative group mt-2">
        <label class="flex items-center gap-2 text-xs font-bold uppercase tracking-widest mb-2 ml-1 transition-colors"
               :class="hasMissingField('nombre') ? 'text-amber-500 dark:text-amber-400' : 'text-slate-500 dark:text-slate-400'">
          <Type class="w-4 h-4" /> Nombre del Evento
        </label>
        <input v-model="name" type="text" placeholder="Ej. Alquiler, Netflix..." 
               class="w-full px-4 py-3.5 bg-white/50 dark:bg-black/20 border rounded-xl outline-none text-slate-900 dark:text-white transition-all focus:bg-white/80 dark:focus:bg-black/40 focus:ring-2 focus:ring-slate-900/20 dark:focus:ring-white/20"
               :class="hasMissingField('nombre') ? 'border-amber-400 dark:border-amber-500/50' : 'border-slate-200/50 dark:border-white/5'">
      </div>

      <div class="p-4 sm:p-6 bg-slate-50/50 dark:bg-[#111111]/40 border rounded-2xl relative transition-all"
           :class="hasMissingField('monto') ? 'border-amber-400 dark:border-amber-500/50 shadow-[0_0_10px_rgba(251,191,36,0.1)]' : 'border-slate-200/50 dark:border-white/5'">
          
          <p class="text-[10px] font-bold uppercase tracking-widest mb-3 text-center pt-1"
             :class="hasMissingField('monto') ? 'text-amber-500 dark:text-amber-400' : 'text-slate-400 dark:text-slate-500'">
            Monto Proyectado
          </p>
          
          <div class="flex justify-center">
            <GlassCurrencyInput v-model="amount" :type="txType" :symbol="txCurrencySymbol" />
          </div>

          <div class="mt-4 relative z-[45] opacity-70 cursor-not-allowed">
            <label class="flex items-center gap-2 text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-widest mb-2 ml-1">
              <Coins class="w-4 h-4" /> Moneda Original (Bloqueada)
            </label>
            <div class="w-full flex items-center justify-between px-4 py-3.5 bg-slate-100/50 dark:bg-black/20 border border-slate-200/50 dark:border-white/5 rounded-xl">
              <span class="text-sm font-bold text-slate-700 dark:text-slate-300">{{ txCurrency }}</span>
            </div>
          </div>

          <div class="mt-6 space-y-2 relative z-[10]">
            <div class="flex items-center justify-between p-3 bg-white/80 dark:bg-black/40 rounded-xl border border-slate-200/50 dark:border-white/5 backdrop-blur-sm shadow-sm">
                <div class="flex items-center gap-3">
                    <div class="p-1.5 rounded-lg bg-slate-100 dark:bg-white/5 text-slate-500 dark:text-slate-400">
                        <Calculator class="w-4 h-4" />
                    </div>
                    <div class="text-left">
                        <p class="text-xs font-bold text-slate-700 dark:text-slate-300">Monto Aproximado</p>
                        <p class="text-[9px] font-medium text-slate-400">El valor puede variar</p>
                    </div>
                </div>
                <button @click="isEstimated = !isEstimated; if(isEstimated) autoExecute = false" class="w-11 h-6 rounded-full relative transition-colors duration-300 shadow-inner shrink-0" :class="isEstimated ? 'bg-slate-800 dark:bg-white' : 'bg-slate-300 dark:bg-slate-700'">
                    <div class="absolute top-1 left-1 w-4 h-4 rounded-full bg-white dark:bg-slate-900 transition-transform duration-300 shadow-sm" :class="isEstimated ? 'translate-x-5' : 'translate-x-0'"></div>
                </button>
            </div>

            <transition name="fade-slide">
              <div v-if="txType === 'expense'" class="flex items-center justify-between p-3 rounded-xl border backdrop-blur-sm transition-all duration-300 shadow-sm" :class="isEssential ? 'bg-amber-50/80 dark:bg-amber-500/5 border-amber-200/50 dark:border-amber-500/20' : 'bg-white/80 dark:bg-black/40 border-slate-200/50 dark:border-white/5'">
                <div class="flex items-center gap-3">
                  <div class="p-1.5 rounded-lg" :class="isEssential ? 'bg-amber-100 dark:bg-amber-500/10 text-amber-600 dark:text-amber-400' : 'bg-slate-100 dark:bg-white/5 text-slate-500 dark:text-slate-400'">
                    <Star class="w-4 h-4 transition-all" :class="isEssential ? 'fill-amber-500' : ''" />
                  </div>
                  <div class="text-left transition-colors">
                    <p class="text-xs font-bold" :class="isEssential ? 'text-amber-700 dark:text-amber-300' : 'text-slate-700 dark:text-slate-300'">Gasto Indispensable</p>
                    <p class="text-[9px] font-medium" :class="isEssential ? 'text-amber-600/70 dark:text-amber-400/70' : 'text-slate-400'">Marcar como necesidad básica</p>
                  </div>
                </div>
                <button @click="isEssential = !isEssential" class="w-11 h-6 rounded-full relative transition-colors duration-300 shadow-inner shrink-0" :class="isEssential ? 'bg-amber-500 dark:bg-amber-400' : 'bg-slate-300 dark:bg-slate-700'">
                  <div class="absolute top-1 left-1 w-4 h-4 rounded-full bg-white transition-transform duration-300 shadow-sm" :class="isEssential ? 'translate-x-5 bg-white dark:bg-slate-900' : 'translate-x-0'"></div>
                </button>
              </div>
            </transition>

            <transition name="fade-slide">
              <div v-if="!isEstimated" class="flex flex-col gap-2">
                <div class="flex items-center justify-between p-3 rounded-xl border backdrop-blur-sm transition-all duration-300 shadow-sm" :class="[autoExecute ? 'bg-white dark:bg-black/40 border-slate-300 dark:border-white/20' : 'bg-white/80 dark:bg-black/40 border-slate-200/50 dark:border-white/5', isCrossCurrency ? 'opacity-50 grayscale' : '']">
                  <div class="flex items-center gap-3">
                      <div class="p-1.5 rounded-lg" :class="autoExecute ? 'bg-slate-200 dark:bg-white/20 text-slate-800 dark:text-white' : 'bg-slate-100 dark:bg-white/5 text-slate-500 dark:text-slate-400'">
                          <Check class="w-4 h-4" />
                      </div>
                      <div class="text-left">
                          <p class="text-xs font-bold" :class="autoExecute ? 'text-slate-900 dark:text-white' : 'text-slate-700 dark:text-slate-300'">Auto-ejecución</p>
                          <p class="text-[9px] font-medium" :class="autoExecute ? 'text-slate-500 dark:text-slate-400' : 'text-slate-400'">Se aplica solo al llegar la fecha</p>
                      </div>
                  </div>
                  <button @click="toggleAutoExecute" :disabled="isCrossCurrency" class="w-11 h-6 rounded-full relative transition-colors duration-300 shadow-inner shrink-0 disabled:cursor-not-allowed" :class="autoExecute ? 'bg-slate-800 dark:bg-slate-200' : 'bg-slate-300 dark:bg-slate-700'">
                      <div class="absolute top-1 left-1 w-4 h-4 rounded-full transition-transform duration-300 shadow-sm" :class="autoExecute ? 'translate-x-5 bg-white dark:bg-slate-900' : 'translate-x-0 bg-white'"></div>
                  </button>
                </div>
                <transition name="fade">
                  <div v-if="isCrossCurrency" class="px-3 py-2 bg-amber-50/80 dark:bg-amber-500/10 border border-amber-200 dark:border-amber-500/20 rounded-lg flex items-center gap-2">
                    <Info class="w-4 h-4 text-amber-500 shrink-0" />
                    <p class="text-[10px] leading-tight font-medium text-amber-700 dark:text-amber-400">La auto-ejecución requiere que las divisas coincidan.</p>
                  </div>
                </transition>
              </div>
            </transition>
          </div>
      </div>

      <div class="space-y-4 sm:space-y-5 relative">
        <div class="relative z-[40]" :class="{ 'ring-1 ring-amber-400 dark:ring-amber-500/50 rounded-xl': hasMissingField('categoría') }">
            <GlassSelect v-if="txType !== 'transfer'" v-model="categoryId" :options="filteredCategories" placeholder="Seleccionar Categoría..." :icon="selectedCategoryIcon" />
        </div>

        <div class="flex flex-col sm:flex-row gap-4 sm:gap-6 relative z-[30] mt-2">
            <div class="w-full relative z-[35]" :class="{ 'ring-1 ring-amber-400 dark:ring-amber-500/50 rounded-xl': hasMissingField('cuenta origen') }">
              <GlassSelect v-model="accountId" :options="allowedAccounts" :placeholder="txType === 'income' ? 'Abonar a Cuenta...' : 'Pagar desde Cuenta...'" :icon="Wallet" />
            </div>
            <div v-if="txType === 'transfer'" class="w-full relative z-[25]" :class="{ 'ring-1 ring-amber-400 dark:ring-amber-500/50 rounded-xl': hasMissingField('cuenta destino') || hasMissingField('cuentas distintas') }">
              <GlassSelect v-model="transferToAccountId" :options="financeStore.accounts.filter(a => a.id !== accountId).map(a => ({ id: a.id, name: a.name, icon: Wallet }))" placeholder="Cuenta Destino..." :icon="Wallet" />
            </div>
        </div>

        <div class="flex flex-col sm:flex-row gap-4 relative z-[20]">
            <div class="w-full relative z-[25]">
                <GlassSelect v-model="frequency" :options="frequencies" placeholder="Repetir..." />
            </div>
            <div class="w-full relative z-[20]">
                <GlassNativeDatePicker v-model="nextDate" />
            </div>
        </div>
      </div>
    </div>

    <div class="flex gap-3 mt-4 pt-4 border-t border-slate-200/50 dark:border-white/5 shrink-0 bg-white/30 dark:bg-black/10 -mx-6 px-6 pb-2">
      <button @click="emit('cancel')" :disabled="isSaving" class="flex-1 py-3.5 rounded-xl font-bold text-sm text-slate-600 dark:text-slate-300 bg-white/50 dark:bg-white/5 border border-slate-200/50 dark:border-white/5 hover:bg-white dark:hover:bg-white/10 transition-all flex items-center justify-center gap-2">
        <X class="w-4 h-4" /> Cancelar
      </button>
      <button @click="handleSave" :disabled="!isValid || isSaving" class="flex-[2] py-3.5 bg-slate-900 dark:bg-white text-white dark:text-slate-900 rounded-xl font-bold text-sm transition-all shadow-md hover:bg-slate-800 dark:hover:bg-slate-200 flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed">
        <Loader2 v-if="isSaving" class="w-4 h-4 animate-spin" />
        <Check v-else class="w-4 h-4" /> Guardar Cambios
      </button>
    </div>

  </div>
</template>

<style scoped>
.fade-slide-enter-active, .fade-slide-leave-active { transition: all 0.3s ease; }
.fade-slide-enter-from, .fade-slide-leave-to { opacity: 0; transform: translateY(-10px); }
.custom-scrollbar::-webkit-scrollbar { width: 6px; }
.custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
.custom-scrollbar::-webkit-scrollbar-thumb { background: rgba(156, 163, 175, 0.3); border-radius: 10px; }
.custom-scrollbar::-webkit-scrollbar-thumb:hover { background: rgba(156, 163, 175, 0.5); }
</style>