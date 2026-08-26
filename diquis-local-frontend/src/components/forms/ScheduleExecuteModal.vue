<script setup lang="ts">
import { ref, watch, computed } from 'vue';
import { scheduledService } from '../../services/scheduledService';
import { useFinanceStore } from '../../stores/finance';
import { CURRENCIES } from '../../constants/currencies'; 
import GlassModal from '../ui/GlassModal.vue';
import GlassCurrencyInput from '../ui/GlassCurrencyInput.vue'; 
import GlassAlert from '../ui/GlassAlert.vue'; 
import { 
  Loader2, CheckCircle2, ChevronLeft, 
  SkipForward, Edit2, Trash2, 
  TrendingUp, TrendingDown, ArrowRightLeft, Check, Calculator
} from 'lucide-vue-next';

const props = defineProps<{
  isOpen: boolean;
  scheduleToExecute: any | null;
}>();

const emit = defineEmits(['close', 'refresh', 'edit']);
const financeStore = useFinanceStore();

const actualAmount = ref('');
const exchangeRate = ref(''); 
const currentView = ref<'menu' | 'confirm'>('menu');
const isExecuting = ref(false);
const isSkipping = ref(false);
const isDeleting = ref(false);
const showDeleteConfirm = ref(false);

const apiError = ref('');
const showErrorPopup = ref(false);

const handleCloseError = () => {
  showErrorPopup.value = false;
  apiError.value = '';
};

watch(() => props.isOpen, (val) => {
    if (val && props.scheduleToExecute) {
        actualAmount.value = props.scheduleToExecute.expected_amount.toString();
        exchangeRate.value = ''; 
        currentView.value = 'menu';
        showDeleteConfirm.value = false;
        apiError.value = '';
        showErrorPopup.value = false;
    }
});

// --- LÓGICA MULTI-DIVISA ---
const selectedAccount = computed(() => {
  if (!props.scheduleToExecute) return null;
  return financeStore.accounts.find(a => a.id === props.scheduleToExecute.account_id);
});

const selectedTransferAccount = computed(() => {
  if (!props.scheduleToExecute || props.scheduleToExecute.type !== 'transfer') return null;
  return financeStore.accounts.find(a => a.id === props.scheduleToExecute.transfer_to_account_id);
});

const isCrossCurrency = computed(() => {
  if (!props.scheduleToExecute || !selectedAccount.value) return false;
  
  const txCurrency = props.scheduleToExecute.currency || 'CRC';
  const sourceMismatch = selectedAccount.value && txCurrency !== selectedAccount.value.currency;
  const transferMismatch = props.scheduleToExecute.type === 'transfer' && selectedAccount.value && selectedTransferAccount.value && selectedAccount.value.currency !== selectedTransferAccount.value.currency;
  
  return Boolean(sourceMismatch || transferMismatch);
});

const txCurrencySymbol = computed(() => {
  if (!props.scheduleToExecute) return '₡';
  const c = CURRENCIES.find(x => x.code === props.scheduleToExecute.currency);
  return c ? c.symbol : '$';
});

const finalImpactAmount = computed(() => {
  if (!actualAmount.value || !exchangeRate.value || !isCrossCurrency.value) return 0;
  return Number(actualAmount.value) * Number(exchangeRate.value);
});

const formatCurrency = (val: number, currencyCode: string = 'CRC') => {
  const c = CURRENCIES.find(x => x.code === currencyCode);
  const symbol = c ? c.symbol : '$';
  const num = new Intl.NumberFormat('es-CR', { minimumFractionDigits: 2 }).format(Math.abs(val));
  return `${symbol}${num}`;
};
// ---------------------------

const isValid = computed(() => {
    const hasAmount = actualAmount.value && Number(actualAmount.value) > 0;
    if (isCrossCurrency.value) {
      return hasAmount && exchangeRate.value && Number(exchangeRate.value) > 0;
    }
    return hasAmount;
});

const typeInfo = computed(() => {
    if (!props.scheduleToExecute) return { icon: ArrowRightLeft, color: 'text-slate-500', bg: 'bg-slate-100 dark:bg-white/5' };
    if (props.scheduleToExecute.type === 'income') return { icon: TrendingUp, color: 'text-emerald-500', bg: 'bg-emerald-50 dark:bg-emerald-500/10' };
    if (props.scheduleToExecute.type === 'expense') return { icon: TrendingDown, color: 'text-slate-700 dark:text-slate-300', bg: 'bg-slate-100 dark:bg-white/5' };
    return { icon: ArrowRightLeft, color: 'text-slate-500', bg: 'bg-slate-100 dark:bg-white/5' };
});

const handleConfirm = async () => {
    if (!isValid.value || !props.scheduleToExecute) return;
    isExecuting.value = true;
    apiError.value = '';
    showErrorPopup.value = false;

    try {
        const payload: any = {
            actual_amount: Number(actualAmount.value),
            occurred_at: new Date().toISOString()
        };

        if (isCrossCurrency.value) {
           payload.exchange_rate = Number(exchangeRate.value);
           payload.exchange_source = 'user';
        }

        await scheduledService.executeScheduled(props.scheduleToExecute.id, payload);
        emit('refresh');
        emit('close');
    } catch(e: any) {
        console.error(e);
        apiError.value = e.response?.data?.detail || "Error ejecutando la programación.";
        showErrorPopup.value = true;
    } finally {
        isExecuting.value = false;
    }
};

const handleSkip = async () => {
    if (!props.scheduleToExecute) return;
    isSkipping.value = true;
    try {
        await scheduledService.skipScheduled(props.scheduleToExecute.id);
        emit('refresh');
        emit('close');
    } catch(e: any) {
        alert("Error al saltar el ciclo");
    } finally {
        isSkipping.value = false;
    }
};

const handleDelete = async () => {
    if (!showDeleteConfirm.value) {
        showDeleteConfirm.value = true;
        return;
    }
    if (!props.scheduleToExecute) return;
    isDeleting.value = true;
    try {
        await scheduledService.deleteScheduled(props.scheduleToExecute.id);
        emit('refresh');
        emit('close');
    } catch(e: any) {
        alert("Error al eliminar la programación");
    } finally {
        isDeleting.value = false;
    }
};

const handleEdit = () => {
    emit('edit', props.scheduleToExecute);
    emit('close');
};
</script>

<template>
  <GlassModal :is-open="isOpen" title="Gestionar Programación" @close="emit('close')">
    
    <GlassAlert 
      :show="showErrorPopup" 
      :message="apiError" 
      type="error" 
      @close="handleCloseError" 
    />

    <div v-if="scheduleToExecute" class="flex flex-col items-center mb-8 relative">
      
      <transition name="fade">
        <button 
          v-if="currentView === 'confirm'" 
          @click="currentView = 'menu'" 
          class="absolute left-0 top-0 p-2 rounded-full bg-slate-100 dark:bg-white/5 text-slate-500 hover:text-slate-800 dark:hover:text-white transition-colors"
        >
            <ChevronLeft class="w-5 h-5" />
        </button>
      </transition>

      <div class="w-16 h-16 rounded-2xl flex items-center justify-center mb-3 shadow-inner border border-slate-200/50 dark:border-white/5" :class="typeInfo.bg">
          <component :is="typeInfo.icon" class="w-8 h-8" :class="typeInfo.color" />
      </div>
      <h3 class="text-xl font-extrabold text-slate-900 dark:text-white tracking-tight text-center">{{ scheduleToExecute.name }}</h3>
      <p class="text-[10px] font-bold text-slate-400 dark:text-slate-500 uppercase tracking-widest mt-1">
        {{ scheduleToExecute.is_estimated ? 'Monto Aproximado' : 'Monto Fijo' }}
      </p>
    </div>

    <div v-if="scheduleToExecute" class="relative min-h-[250px]">
      <transition name="view-slide" mode="out-in">
        
        <div v-if="currentView === 'menu'" class="space-y-3 w-full">
            
            <button @click="currentView = 'confirm'" class="w-full flex items-center gap-4 p-4 bg-white/60 dark:bg-white/5 border border-slate-200/50 dark:border-white/5 rounded-2xl hover:bg-white dark:hover:bg-white/10 transition-all group shadow-sm hover:shadow-md">
              <div class="w-10 h-10 rounded-xl bg-emerald-100 dark:bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 flex items-center justify-center shrink-0">
                <Check class="w-5 h-5" />
              </div>
              <div class="text-left flex-1">
                <p class="text-sm font-bold text-slate-800 dark:text-slate-200 group-hover:text-emerald-600 dark:group-hover:text-emerald-400 transition-colors">Registrar Pago</p>
                <p class="text-[10px] font-medium text-slate-500 dark:text-slate-400">Confirmar y aplicar a tus saldos</p>
              </div>
            </button>

            <button @click="handleSkip" :disabled="isSkipping" class="w-full flex items-center gap-4 p-4 bg-white/60 dark:bg-white/5 border border-slate-200/50 dark:border-white/5 rounded-2xl hover:bg-white dark:hover:bg-white/10 transition-all group">
              <div class="w-10 h-10 rounded-xl bg-slate-100 dark:bg-white/10 text-slate-600 dark:text-slate-400 flex items-center justify-center shrink-0">
                <Loader2 v-if="isSkipping" class="w-5 h-5 animate-spin" />
                <SkipForward v-else class="w-5 h-5" />
              </div>
              <div class="text-left flex-1">
                <p class="text-sm font-bold text-slate-800 dark:text-slate-200 transition-colors">Saltar este ciclo</p>
                <p class="text-[10px] font-medium text-slate-500 dark:text-slate-400">Mover al próximo vencimiento sin cobrar</p>
              </div>
            </button>

            <button @click="handleEdit" class="w-full flex items-center gap-4 p-4 bg-white/60 dark:bg-white/5 border border-slate-200/50 dark:border-white/5 rounded-2xl hover:bg-white dark:hover:bg-white/10 transition-all group">
              <div class="w-10 h-10 rounded-xl bg-blue-50 dark:bg-blue-500/10 text-blue-600 dark:text-blue-400 flex items-center justify-center shrink-0">
                <Edit2 class="w-5 h-5" />
              </div>
              <div class="text-left flex-1">
                <p class="text-sm font-bold text-slate-800 dark:text-slate-200 transition-colors">Editar / Reagendar</p>
                <p class="text-[10px] font-medium text-slate-500 dark:text-slate-400">Cambiar monto o fecha</p>
              </div>
            </button>

            <button @click="handleDelete" :disabled="isDeleting" class="w-full flex items-center gap-4 p-4 bg-white/60 dark:bg-white/5 border border-slate-200/50 dark:border-white/5 rounded-2xl hover:bg-red-50 dark:hover:bg-red-500/10 transition-all group mt-6" :class="{'border-red-200 dark:border-red-500/20 bg-red-50 dark:bg-red-500/10': showDeleteConfirm}">
              <div class="w-10 h-10 rounded-xl flex items-center justify-center shrink-0 transition-colors" :class="showDeleteConfirm ? 'bg-red-600 text-white' : 'bg-red-50 dark:bg-red-500/10 text-red-600 dark:text-red-400'">
                <Loader2 v-if="isDeleting" class="w-5 h-5 animate-spin" />
                <Trash2 v-else class="w-5 h-5" />
              </div>
              <div class="text-left flex-1">
                <p class="text-sm font-bold transition-colors" :class="showDeleteConfirm ? 'text-red-600 dark:text-red-400' : 'text-red-600 dark:text-red-400'">
                  {{ showDeleteConfirm ? '¿Seguro? Confirmar eliminación' : 'Eliminar Programación' }}
                </p>
                <p class="text-[10px] font-medium text-slate-500 dark:text-slate-400" v-if="!showDeleteConfirm">Detener y remover del calendario</p>
              </div>
            </button>

        </div>

        <div v-else class="space-y-6 w-full">
          <div class="p-6 bg-slate-50/50 dark:bg-[#111111]/40 border border-slate-200/50 dark:border-white/5 rounded-2xl relative">
              <p class="text-[10px] font-bold text-slate-400 dark:text-slate-500 uppercase tracking-widest mb-3 text-center">Monto a Registrar</p>
              
              <div class="flex justify-center">
                  <GlassCurrencyInput 
                    v-model="actualAmount" 
                    :type="scheduleToExecute.type" 
                    :symbol="txCurrencySymbol" 
                  />
              </div>

              <transition name="fade-slide">
                <div v-if="isCrossCurrency && selectedAccount" class="mt-6 p-3 bg-blue-50/50 dark:bg-blue-900/10 border border-blue-200/50 dark:border-blue-800/30 rounded-xl flex items-center justify-between gap-3">
                  <div class="flex items-center gap-2 text-slate-700 dark:text-slate-300">
                    <Calculator class="w-4 h-4 text-blue-500 shrink-0" />
                    <div class="text-left">
                      <p class="text-xs font-bold">Tipo de Cambio</p>
                      <p v-if="scheduleToExecute.type === 'transfer' && selectedTransferAccount" class="text-[9px] opacity-70">
                        1 {{ selectedAccount.currency }} = X {{ selectedTransferAccount.currency }}
                      </p>
                      <p v-else class="text-[9px] opacity-70">
                        1 {{ scheduleToExecute.currency }} = X {{ selectedAccount.currency }}
                      </p>
                    </div>
                  </div>
                  <input 
                    v-model="exchangeRate" 
                    type="number" 
                    step="0.01"
                    placeholder="Ej: 515.20"
                    class="w-24 px-2 py-1.5 text-sm text-right bg-white dark:bg-black/40 border border-slate-200 dark:border-white/10 rounded-lg outline-none focus:ring-2 focus:ring-blue-500/50 dark:text-white"
                  >
                </div>
              </transition>
              
              <transition name="fade">
                <div v-if="isCrossCurrency && Number(exchangeRate) > 0" class="mt-4 flex flex-col items-center">
                  <p class="text-[9px] font-bold text-slate-400 uppercase tracking-widest">Impacto en Billetera</p>
                  <p class="text-lg font-black text-slate-800 dark:text-slate-200">
                    {{ formatCurrency(finalImpactAmount, selectedAccount?.currency) }}
                  </p>
                </div>
              </transition>
          </div>

          <button 
              @click="handleConfirm" 
              :disabled="!isValid || isExecuting"
              class="w-full py-4 bg-slate-900 dark:bg-white text-white dark:text-slate-900 font-bold rounded-xl flex items-center justify-center gap-2 transition-all shadow-lg hover:shadow-xl disabled:opacity-50 disabled:cursor-not-allowed"
              >
              <Loader2 v-if="isExecuting" class="w-5 h-5 animate-spin" />
              <template v-else>
                 <CheckCircle2 class="w-5 h-5" /> Confirmar Transacción
              </template>
          </button>
        </div>

      </transition>
    </div>
  </GlassModal>
</template>

<style scoped>
.fade-enter-active, .fade-leave-active { transition: opacity 0.2s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }

.view-slide-enter-active, .view-slide-leave-active { transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1); }
.view-slide-enter-from { opacity: 0; transform: translateX(20px); }
.view-slide-leave-to { opacity: 0; transform: translateX(-20px); }

.fade-slide-enter-active, .fade-slide-leave-active { transition: all 0.3s ease; }
.fade-slide-enter-from, .fade-slide-leave-to { opacity: 0; transform: translateY(-10px); }
</style>