<script setup lang="ts">
import { ref, computed, watch } from 'vue';
import { useFinanceStore } from '../../stores/finance';
import { useCategoryStore } from '../../stores/category';
import { scheduledService } from '../../services/scheduledService';
import type { ScheduledCreate } from '../../types/scheduled';
import type { Category } from '../../types/category';
import { resolveIcon } from '../../utils/icons';
import { CURRENCIES } from '../../constants/currencies';
import { useScreen } from '../../composables/useScreen';

import GlassModal from '../ui/GlassModal.vue';
import GlassSelect from '../ui/GlassSelect.vue';
import GlassCurrencySelect from '../ui/GlassCurrencySelect.vue';
import GlassNativeDatePicker from '../ui/GlassNativeDatePicker.vue'; 
import GlassCurrencyInput from '../ui/GlassCurrencyInput.vue';
import { 
  Loader2, Briefcase, TrendingDown, ArrowRightLeft, Type, Calculator, Check, Star, Tag, Wallet, Info
} from 'lucide-vue-next';

const props = defineProps<{ 
  isOpen: boolean; 
  defaultFrequency?: string;
  defaultTab?: 'expense' | 'income' | 'transfer';
  hideTabs?: boolean 
}>();

const emit = defineEmits(['close', 'refresh']);

const financeStore = useFinanceStore();
const categoryStore = useCategoryStore();
const { isMobile } = useScreen();

const isSaving = ref(false);

const txType = ref<'income' | 'expense' | 'transfer'>('expense');
const name = ref('');
const amount = ref('');
const accountId = ref('');
const transferToAccountId = ref('');
const categoryId = ref('');
const isEstimated = ref(false);
const isEssential = ref(false);
const autoExecute = ref(false);
const frequency = ref('monthly');
const nextDate = ref(new Date());

const txCurrency = ref('CRC');

const frequencies = [
  { id: 'once', name: 'Una sola vez' },
  { id: 'daily', name: 'Diario' }, { id: 'weekly', name: 'Semanal' }, { id: 'biweekly', name: 'Quincenal' },
  { id: 'monthly', name: 'Mensual' }, { id: 'quarterly', name: 'Trimestral' }, { id: 'yearly', name: 'Anual' }
];

const dynamicTitle = computed(() => {
  if (!props.hideTabs) return "Añadir Programación";
  if (txType.value === 'income') return "Programar Ingreso";
  if (txType.value === 'transfer') return "Programar Ahorro";
  return "Programar Gasto";
});

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

watch(accountId, (newId) => {
  const acc = financeStore.accounts.find(a => a.id === newId);
  if (acc) {
    txCurrency.value = acc.currency;
  }
});

watch(isCrossCurrency, (isCross) => {
  if (isCross) {
    autoExecute.value = false;
  }
});

watch(() => props.isOpen, (val) => {
  if (val) {
    txType.value = props.defaultTab || 'expense';
    name.value = '';
    amount.value = '';
    
    if (financeStore.accounts.length > 0) {
      const validAccounts = financeStore.accounts.filter(a => txType.value === 'income' || a.allow_negative_balance);
      const defaultAccount = validAccounts.find(a => a.name === 'Billetera Principal') || validAccounts[0];
      
      if (defaultAccount) {
        accountId.value = defaultAccount.id;
        txCurrency.value = defaultAccount.currency;
      } else {
        accountId.value = '';
      }
    } else {
      accountId.value = '';
    }
    
    transferToAccountId.value = '';
    categoryId.value = '';
    isEstimated.value = false;
    isEssential.value = false;
    autoExecute.value = false;
    
    frequency.value = props.defaultFrequency || 'monthly';
    
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    tomorrow.setHours(12, 0, 0, 0);
    nextDate.value = tomorrow;
  }
});

const handleTabChange = (type: 'income' | 'expense' | 'transfer') => {
  txType.value = type;
  categoryId.value = '';
  
  const validAccounts = financeStore.accounts.filter(a => type === 'income' || a.allow_negative_balance);
  if (validAccounts.length > 0 && !validAccounts.find(a => a.id === accountId.value)) {
     const defaultAccount = validAccounts.find(a => a.name === 'Billetera Principal') || validAccounts[0];
     accountId.value = defaultAccount.id;
     txCurrency.value = defaultAccount.currency;
  }
};

const toggleAutoExecute = () => {
  if (!isCrossCurrency.value) {
    autoExecute.value = !autoExecute.value;
  }
};

const filteredCategories = computed(() => {
  if (txType.value === 'transfer') return [];
  return categoryStore.categories
    .filter((c: Category) => {
      if (txType.value === 'income') return c.domain === 'income';
      if (txType.value === 'expense') return c.domain !== 'income' && c.domain !== 'savings';
      return false;
    })
    .sort((a: Category, b: Category) => a.sort_order - b.sort_order) 
    .map((c: Category) => ({ id: c.id, name: c.name, icon: resolveIcon(c.icon) })); 
});

const selectedCategoryIcon = computed(() => {
  const cat = filteredCategories.value.find(c => c.id === categoryId.value);
  return cat ? cat.icon : Tag;
});

const allowedAccounts = computed(() => {
  return financeStore.accounts
    .filter(a => txType.value === 'income' || a.allow_negative_balance)
    .map(a => ({ id: a.id, name: a.name, icon: Wallet }));
});

// Lógica de validación unificada (Igual que TransactionModal)
const missingFields = computed(() => {
  const missing = [];
  
  if (!name.value.trim()) missing.push('nombre');
  if (Number(amount.value) <= 0) missing.push('monto');
  if (!accountId.value) missing.push('cuenta_origen');

  if (txType.value === 'transfer') {
    if (!transferToAccountId.value) missing.push('cuenta_destino');
    if (accountId.value && accountId.value === transferToAccountId.value) missing.push('cuentas_distintas');
  } else {
    if (!categoryId.value) missing.push('categoría');
  }

  return missing;
});

const hasMissingField = (field: string) => missingFields.value.includes(field);
const isValid = computed(() => missingFields.value.length === 0);

const handleSave = async () => {
    if (!isValid.value) return;
    isSaving.value = true;
    try {
        const payload: ScheduledCreate = {
            type: txType.value,
            name: name.value,
            expected_amount: Number(amount.value),
            currency: txCurrency.value,
            account_id: accountId.value,
            transfer_to_account_id: txType.value === 'transfer' ? transferToAccountId.value : undefined,
            category_id: txType.value !== 'transfer' ? categoryId.value : undefined,
            frequency: frequency.value as any,
            next_due_date: new Date(nextDate.value.getTime() - nextDate.value.getTimezoneOffset() * 60000).toISOString().split('T')[0],
            is_estimated: isEstimated.value,
            is_essential: isEssential.value,
            auto_execute: !isEstimated.value && autoExecute.value && !isCrossCurrency.value,
        };

        await scheduledService.createScheduled(payload);
        emit('refresh');
        emit('close');
    } catch (e: any) {
        alert(e.response?.data?.detail || "Hubo un error.");
    } finally {
        isSaving.value = false;
    }
};
</script>

<template>
  <GlassModal :is-open="isOpen" :title="dynamicTitle" @close="emit('close')" :scrollable="false" :no-padding="true">
    
    <div class="w-full h-full flex flex-col overflow-y-auto custom-scrollbar relative">
      
      <div class="p-4 sm:p-6 flex-1 shrink-0">
        
        <div v-if="!hideTabs" class="flex p-1.5 bg-slate-200/50 dark:bg-white/5 rounded-xl backdrop-blur-sm border border-slate-300/50 dark:border-white/5 mb-6 shadow-inner relative z-[50]">
          <button @click="handleTabChange('expense')" class="flex-1 flex items-center justify-center gap-2 py-2.5 rounded-lg text-sm font-bold transition-all duration-300" :class="txType === 'expense' ? 'bg-white dark:bg-[#1a1a1a] text-slate-900 dark:text-white shadow-md border border-slate-200 dark:border-white/5' : 'text-slate-500 hover:text-slate-700 dark:hover:text-slate-300 border border-transparent'">
            <TrendingDown class="w-4 h-4" :class="txType === 'expense' ? 'text-red-500 dark:text-red-400' : 'opacity-70'" /> Gasto
          </button>
          <button @click="handleTabChange('income')" class="flex-1 flex items-center justify-center gap-2 py-2.5 rounded-lg text-sm font-bold transition-all duration-300" :class="txType === 'income' ? 'bg-white dark:bg-[#1a1a1a] text-slate-900 dark:text-white shadow-md border border-slate-200 dark:border-white/5' : 'text-slate-500 hover:text-slate-700 dark:hover:text-slate-300 border border-transparent'">
            <Briefcase class="w-4 h-4" :class="txType === 'income' ? 'text-green-500 dark:text-green-400' : 'opacity-70'" /> Ingreso
          </button>
          <button @click="handleTabChange('transfer')" class="flex-1 flex items-center justify-center gap-2 py-2.5 rounded-lg text-sm font-bold transition-all duration-300" :class="txType === 'transfer' ? 'bg-white dark:bg-[#1a1a1a] text-slate-900 dark:text-white shadow-md border border-slate-200 dark:border-white/5' : 'text-slate-500 hover:text-slate-700 dark:hover:text-slate-300 border border-transparent'">
            <ArrowRightLeft class="w-4 h-4" :class="txType === 'transfer' ? 'text-slate-800 dark:text-slate-200' : 'opacity-70'" /> Ahorro
          </button>
        </div>

        <div class="space-y-6">
            <div class="relative group">
              <label class="flex items-center gap-2 text-xs font-bold uppercase tracking-widest mb-2 ml-1 transition-colors"
                     :class="hasMissingField('nombre') ? 'text-amber-500 dark:text-amber-400' : 'text-slate-500 dark:text-slate-400'">
                <Type class="w-4 h-4" /> Nombre del Evento
              </label>
              <input v-model="name" type="text" placeholder="Ej. Alquiler, Netflix, Salario..." 
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
                  <GlassCurrencyInput v-model="amount" :type="txType" :symbol="txCurrencySymbol" :auto-focus="!isMobile" />
                </div>

                <div class="mt-4 sm:mt-6 relative z-[45]">
                  <GlassCurrencySelect v-model="txCurrency" placeholder="Seleccionar Moneda..." />
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
                          <p class="text-[10px] leading-tight font-medium text-amber-700 dark:text-amber-400">
                            <span v-if="txType === 'transfer' && selectedAccount && selectedTransferAccount && selectedAccount.currency !== selectedTransferAccount.currency">
                                La auto-ejecución se desactiva en transferencias entre divisas distintas ({{ selectedAccount.currency }} a {{ selectedTransferAccount.currency }}).
                            </span>
                            <span v-else>
                                La auto-ejecución está deshabilitada porque la moneda programada ({{ txCurrency }}) es distinta a la de la cuenta. 
                            </span>
                          </p>
                        </div>
                      </transition>
                    </div>
                  </transition>

                </div>
            </div>

            <div class="space-y-4 sm:space-y-5 relative">
              <div class="relative z-[40]" :class="{ 'ring-1 ring-amber-400 dark:ring-amber-500/50 rounded-xl': hasMissingField('categoría') }">
                  <GlassSelect v-if="txType !== 'transfer'" v-model="categoryId" :options="filteredCategories" placeholder="Seleccionar Categoría..." :icon="selectedCategoryIcon" />
                  <p v-if="hasMissingField('categoría')" class="text-[10px] text-amber-500 absolute -bottom-4 right-2 font-semibold">Selecciona una categoría</p>
              </div>

              <div class="flex flex-col sm:flex-row gap-4 sm:gap-6 relative z-[30] mt-2">
                  <div class="w-full relative z-[35]" :class="{ 'ring-1 ring-amber-400 dark:ring-amber-500/50 rounded-xl': hasMissingField('cuenta_origen') }">
                    <GlassSelect v-model="accountId" :options="allowedAccounts" :placeholder="txType === 'income' ? 'Abonar a Cuenta...' : 'Pagar desde Cuenta...'" :icon="Wallet" />
                  </div>
                  <div v-if="txType === 'transfer'" class="w-full relative z-[25]" :class="{ 'ring-1 ring-amber-400 dark:ring-amber-500/50 rounded-xl': hasMissingField('cuenta_destino') || hasMissingField('cuentas_distintas') }">
                    <GlassSelect v-model="transferToAccountId" :options="financeStore.accounts.filter(a => a.id !== accountId).map(a => ({ id: a.id, name: a.name, icon: Wallet }))" placeholder="Cuenta Destino..." :icon="Wallet" />
                  </div>
              </div>

              <div class="h-1 sm:h-2"></div>

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
      </div>

      <div class="sticky bottom-0 left-0 w-full shrink-0 p-4 sm:p-6 bg-slate-50/95 dark:bg-[#111111]/95 backdrop-blur-xl border-t border-slate-200/50 dark:border-white/5 z-[60] shadow-[0_-15px_15px_-5px_rgba(0,0,0,0.05)] dark:shadow-[0_-15px_15px_-5px_rgba(0,0,0,0.4)]">
        <div class="flex justify-end min-h-[20px] mb-2 px-2 sm:px-0">
          <transition name="fade">
            <p v-if="!isValid && !isMobile" class="text-[10px] font-bold text-amber-500 dark:text-amber-400 uppercase tracking-wide flex items-center gap-1">
              <Info class="w-3 h-3" /> Revisa los campos marcados
            </p>
          </transition>
        </div>

        <button @click="handleSave" :disabled="!isValid || isSaving" class="w-full py-4 sm:py-3.5 bg-slate-900 dark:bg-white text-white dark:text-slate-900 font-bold rounded-xl flex items-center justify-center gap-2 transition-all shadow-lg hover:shadow-xl disabled:opacity-50 disabled:bg-slate-300 dark:disabled:bg-slate-800 disabled:text-slate-500 dark:disabled:text-slate-400 disabled:shadow-none active:scale-[0.98]">
          <Loader2 v-if="isSaving" class="animate-spin h-5 w-5" />
          <template v-else>
            <Check class="w-5 h-5" />
            <span>Programar</span>
          </template>
        </button>
      </div>

    </div>

  </GlassModal>
</template>

<style scoped>
.no-spinners::-webkit-inner-spin-button,
.no-spinners::-webkit-outer-spin-button { -webkit-appearance: none; appearance: none; margin: 0; }
.no-spinners { -moz-appearance: textfield; appearance: textfield; }
.fade-enter-active, .fade-leave-active { transition: opacity 0.2s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
.fade-slide-enter-active, .fade-slide-leave-active { transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1); max-height: 100px; opacity: 1; }
.fade-slide-enter-from, .fade-slide-leave-to { opacity: 0; max-height: 0; margin-top: 0; overflow: hidden; }
.custom-scrollbar::-webkit-scrollbar { width: 6px; }
.custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
.custom-scrollbar::-webkit-scrollbar-thumb { background: rgba(156, 163, 175, 0.3); border-radius: 10px; }
.custom-scrollbar::-webkit-scrollbar-thumb:hover { background: rgba(156, 163, 175, 0.5); }
</style>