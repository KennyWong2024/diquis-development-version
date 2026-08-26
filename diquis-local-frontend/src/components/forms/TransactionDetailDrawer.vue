<script setup lang="ts">
import { ref, watch, computed } from 'vue';
import { financeService } from '../../services/financeService';
import type { TransactionUpdate } from '../../types/transaction';
import { useFinanceStore } from '../../stores/finance';
import { useCategoryStore } from '../../stores/category'; 
import type { Category } from '../../types/category'; 
import { CURRENCIES } from '../../constants/currencies';
import GlassDrawer from '../ui/GlassDrawer.vue';
import TransactionEditForm from './TransactionEditForm.vue';
import GlassAlert from '../ui/GlassAlert.vue';
import {
  Loader2, Trash2, Calendar, FileText, ShoppingCart,
  Car, Utensils, Home, HeartPulse, Zap, Briefcase, PiggyBank, MoreHorizontal, Star, TrendingDown, TrendingUp, Edit2,
  Wallet, ArrowRightLeft 
} from 'lucide-vue-next';

const props = defineProps<{
  isOpen: boolean;
  transactionId: string | null;
}>();

const emit = defineEmits(['close', 'updated']);
const financeStore = useFinanceStore();
const categoryStore = useCategoryStore(); 

const txData = ref<any>(null);
const isLoading = ref(false);
const isDeleting = ref(false);
const showDeleteConfirm = ref(false);
const isEditing = ref(false); 
const isSavingEdit = ref(false);

const apiError = ref('');
const showErrorPopup = ref(false);

const handleCloseError = () => {
  showErrorPopup.value = false;
  apiError.value = '';
};

const domainIconMap: Record<string, any> = {
  grocery: ShoppingCart, transport: Car, food_out: Utensils, home: Home, health: HeartPulse, 
  utilities: Zap, savings: PiggyBank, income: Briefcase, other: MoreHorizontal, entertainment: Star, education: FileText
};

const formatCurrency = (val: number, currencyCode?: string) => {
  const num = new Intl.NumberFormat('es-CR', { minimumFractionDigits: 2 }).format(val);
  if (currencyCode) {
    const c = CURRENCIES.find(x => x.code === currencyCode);
    return `${c ? c.symbol : '$'}${num}`;
  }
  return num;
};

const formatDateTime = (isoString: string) => {
  if (!isoString) return '';
  return new Intl.DateTimeFormat('es-CR', { day: '2-digit', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' }).format(new Date(isoString));
};

const loadTransactionDetail = async () => {
  if (!props.transactionId) return;
  isLoading.value = true;
  try {
    txData.value = await financeService.getTransactionDetail(props.transactionId);
  } catch (error) {
    console.error("Error cargando detalle:", error);
  } finally {
    isLoading.value = false;
  }
};

watch(() => props.isOpen, (isOpen) => {
  if (isOpen) {
    showDeleteConfirm.value = false;
    isEditing.value = false; 
    apiError.value = ''; 
    showErrorPopup.value = false;
    loadTransactionDetail();
  } else {
    txData.value = null;
    apiError.value = '';
    showErrorPopup.value = false;
    isEditing.value = false;
  }
});

const categoryInfo = computed(() => {
  if (!txData.value) return null;
  const cat = categoryStore.categories.find((c: Category) => c.id === txData.value.category_id);
  const title = cat ? cat.name : (txData.value.type === 'expense' ? 'Gasto General' : (txData.value.type === 'transfer' ? 'Transferencia' : 'Ingreso General'));
  const icon = cat && domainIconMap[cat.domain] ? domainIconMap[cat.domain] : (txData.value.type === 'expense' ? TrendingDown : (txData.value.type === 'transfer' ? ArrowRightLeft : TrendingUp));
  return { title, icon };
});

const sourceAccount = computed(() => {
  if (!txData.value) return null;
  return financeStore.accounts.find(a => a.id === txData.value.account_id);
});

const destAccount = computed(() => {
  if (!txData.value || txData.value.type !== 'transfer') return null;
  return financeStore.accounts.find(a => a.id === txData.value.transfer_to_account_id);
});

const handleDelete = async () => {
  if (!showDeleteConfirm.value) {
    showDeleteConfirm.value = true;
    return;
  }
  
  isDeleting.value = true;
  apiError.value = ''; 
  showErrorPopup.value = false;

  try {
    if (props.transactionId) {
      await financeService.deleteTransaction(props.transactionId);
      await financeStore.refreshAllData(); 
      emit('updated'); 
      emit('close'); 
    }
  } catch (error: any) {
    console.error("Error eliminando:", error);
    apiError.value = error.response?.data?.detail || "No se pudo eliminar la transacción debido a un error de red.";
    showErrorPopup.value = true;
    showDeleteConfirm.value = false; 
  } finally {
    isDeleting.value = false;
  }
};

const handleUpdate = async (updateData: TransactionUpdate, updatedItems: any[] | null = null) => {
  if (!props.transactionId) return;
  
  isSavingEdit.value = true;
  apiError.value = ''; 
  showErrorPopup.value = false;

  try {
    await financeService.updateTransaction(props.transactionId, updateData);
    
    if (updatedItems && updatedItems.length > 0) {
      const newItems = updatedItems.filter(item => typeof item.id === 'number');
      if (newItems.length > 0) {
        await Promise.all(newItems.map(item => {
          return financeService.addTransactionItem(props.transactionId as string, {
            product_name: item.name,
            quantity: Number(item.qty),
            line_total: Number(item.price) * Number(item.qty), 
            is_essential: item.isEssential
          });
        }));
      }
    }

    await financeStore.refreshAllData();
    emit('updated');
    emit('close'); 
    
  } catch (error: any) {
    console.error("Error actualizando:", error);
    apiError.value = error.response?.data?.detail || "Hubo un problema al actualizar la transacción.";
    showErrorPopup.value = true;
  } finally {
    isSavingEdit.value = false;
  }
};
</script>

<template>
  <GlassDrawer :is-open="isOpen" :title="isEditing ? 'Editar Transacción' : (txData?.type === 'expense' ? 'Detalle de Gasto' : (txData?.type === 'transfer' ? 'Detalle de Transferencia' : 'Detalle de Ingreso'))" @close="emit('close')">
    
    <GlassAlert 
      :show="showErrorPopup" 
      :message="apiError" 
      :type="'error'" 
      @close="handleCloseError" 
    />
    
    <div v-if="isLoading" class="flex flex-col items-center justify-center h-64 gap-4">
      <Loader2 class="w-8 h-8 animate-spin text-slate-400" />
      <p class="text-sm font-medium text-slate-500">Cargando datos...</p>
    </div>

    <div v-else-if="txData && isEditing" class="h-full">
      <TransactionEditForm 
        :transaction="txData" 
        :is-saving="isSavingEdit"
        @save="handleUpdate"
        @cancel="isEditing = false; apiError = ''; showErrorPopup = false;"
      />
    </div>

    <div v-else-if="txData && !isEditing" class="flex flex-col h-full animate-in fade-in slide-in-from-left-4 duration-300">
      
      <div class="flex flex-col items-center mb-8 mt-6">
        <div class="w-16 h-16 rounded-2xl flex items-center justify-center mb-4 bg-slate-100 dark:bg-white/5 border border-slate-200/50 dark:border-white/5 shadow-inner">
          <component :is="categoryInfo?.icon" class="w-8 h-8 text-slate-700 dark:text-slate-300" />
        </div>
        <h3 class="text-4xl font-black text-slate-900 dark:text-white tracking-tighter mb-1">
          {{ txData.type === 'expense' ? '-' : (txData.type === 'income' ? '+' : '') }}{{ formatCurrency(txData.amount, txData.currency) }}
        </h3>
        <p class="text-sm font-bold text-slate-500 dark:text-slate-400 uppercase tracking-widest">{{ categoryInfo?.title }}</p>
        
        <div v-if="txData.is_essential" class="mt-3 flex items-center gap-1.5 px-3 py-1 bg-amber-50 dark:bg-amber-500/10 text-amber-600 dark:text-amber-400 border border-amber-200/50 dark:border-amber-500/20 rounded-full text-[10px] font-bold uppercase tracking-widest shadow-sm">
          <Star class="w-3 h-3 fill-amber-500" /> Gasto Indispensable
        </div>
      </div>

      <div class="space-y-4 mb-8 bg-slate-50/50 dark:bg-black/20 p-5 rounded-2xl border border-slate-200/50 dark:border-white/5">
        
        <div class="flex items-center gap-3">
          <Wallet class="w-5 h-5 text-slate-400 shrink-0" />
          <div class="flex-1">
            <p class="text-[10px] font-bold text-slate-500 uppercase tracking-wider mb-0.5">{{ txData.type === 'income' ? 'Ingresado a' : 'Pagado desde' }}</p>
            <p class="text-sm font-bold text-slate-900 dark:text-white">{{ sourceAccount?.name || 'Cuenta Desconocida' }}</p>
          </div>
        </div>

        <template v-if="txData.type === 'transfer' && destAccount">
          <div class="w-full h-px bg-slate-200/50 dark:bg-white/5 ml-8"></div>
          <div class="flex items-center gap-3">
            <ArrowRightLeft class="w-5 h-5 text-slate-400 shrink-0" />
            <div class="flex-1">
              <p class="text-[10px] font-bold text-slate-500 uppercase tracking-wider mb-0.5">Transferido a</p>
              <p class="text-sm font-bold text-slate-900 dark:text-white">{{ destAccount.name }}</p>
            </div>
          </div>
        </template>

        <div class="w-full h-px bg-slate-200/50 dark:bg-white/5"></div>
        
        <div class="flex items-start gap-3">
          <Calendar class="w-5 h-5 text-slate-400 mt-0.5 shrink-0" />
          <div>
            <p class="text-[10px] font-bold text-slate-500 uppercase tracking-wider mb-0.5">Fecha y Hora</p>
            <p class="text-sm font-medium text-slate-900 dark:text-white">{{ formatDateTime(txData.occurred_at) }}</p>
          </div>
        </div>
        
        <div class="w-full h-px bg-slate-200/50 dark:bg-white/5"></div>
        
        <div class="flex items-start gap-3">
          <FileText class="w-5 h-5 text-slate-400 mt-0.5 shrink-0" />
          <div>
            <p class="text-[10px] font-bold text-slate-500 uppercase tracking-wider mb-0.5">Nota</p>
            <p class="text-sm font-medium text-slate-900 dark:text-white" :class="!txData.description ? 'italic opacity-60' : ''">
              {{ txData.description || 'Sin descripción adicional' }}
            </p>
          </div>
        </div>
      </div>

      <div v-if="txData.items && txData.items.length > 0" class="mb-8">
        <p class="text-xs font-bold text-slate-500 uppercase tracking-wider mb-3 px-2">Desglose de Compra</p>
        <div class="bg-white/50 dark:bg-white/5 border border-slate-200/50 dark:border-white/5 rounded-2xl overflow-hidden shadow-sm">
          <div v-for="(item, index) in txData.items" :key="item.id" class="px-4 py-3 flex justify-between items-center" :class="{ 'border-t border-slate-100 dark:border-white/5': index !== 0 }">
            <div class="flex flex-col">
              <span class="text-sm font-bold text-slate-800 dark:text-slate-200 flex items-center gap-1.5">
                {{ item.product_name }}
                <Star v-if="item.is_essential" class="w-3 h-3 fill-amber-500 text-amber-500" />
              </span>
              <span class="text-[11px] font-medium text-slate-500 dark:text-slate-400">{{ item.quantity }} x {{ formatCurrency(item.unit_price, txData.currency) }}</span>
            </div>
            <span class="text-sm font-black text-slate-900 dark:text-white">{{ formatCurrency(item.line_total, txData.currency) }}</span>
          </div>
        </div>
      </div>

      <div class="flex-1"></div>

      <div class="mt-8 flex gap-3">
        <button 
          @click="handleDelete" 
          :disabled="isDeleting"
          class="flex-1 py-3.5 rounded-xl font-bold text-sm transition-all duration-300 flex items-center justify-center gap-2 border"
          :class="showDeleteConfirm ? 'bg-red-600 text-white border-red-600 shadow-md hover:bg-red-700' : 'bg-red-50 dark:bg-red-500/10 text-red-600 dark:text-red-400 border-red-200 dark:border-red-500/20 hover:bg-red-100 dark:hover:bg-red-500/20'"
        >
          <Loader2 v-if="isDeleting" class="w-4 h-4 animate-spin" />
          <Trash2 v-else class="w-4 h-4" />
          {{ showDeleteConfirm ? '¿Seguro? Confirmar' : 'Eliminar' }}
        </button>

        <button 
          v-if="!showDeleteConfirm" 
          @click="isEditing = true; apiError = ''; showErrorPopup = false;"
          class="flex-1 flex items-center justify-center gap-2 py-3.5 bg-slate-900 dark:bg-white text-white dark:text-slate-900 rounded-xl font-bold text-sm transition-all shadow-md hover:bg-slate-800 dark:hover:bg-slate-200"
        >
          <Edit2 class="w-4 h-4" />
          Editar
        </button>
      </div>

    </div>
  </GlassDrawer>
</template>

<style scoped>
.fade-slide-enter-active, .fade-slide-leave-active { transition: all 0.3s ease; }
.fade-slide-enter-from, .fade-slide-leave-to { opacity: 0; transform: translateY(-10px); }
</style>