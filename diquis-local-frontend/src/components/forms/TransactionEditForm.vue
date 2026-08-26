<script setup lang="ts">
import { ref, computed, watch } from 'vue';
import { useFinanceStore } from '../../stores/finance';
import { useCategoryStore } from '../../stores/category';
import { CURRENCIES } from '../../constants/currencies';
import GlassSelect from '../ui/GlassSelect.vue';
import GlassNativeDatePicker from '../ui/GlassNativeDatePicker.vue';
import GlassCurrencyInput from '../ui/GlassCurrencyInput.vue';
import GlassSmallCurrencyInput from '../ui/GlassSmallCurrencyInput.vue';
import GlassAlert from '../ui/GlassAlert.vue';
import { resolveIcon } from '../../utils/icons';
import { 
  FileText, Loader2, Tag, Check, X, Star, Trash2, Plus, Calculator, Coins, Wallet
} from 'lucide-vue-next';
import type { TransactionUpdate } from '../../types/transaction';
import type { Category } from '../../types/category';

interface FormItem {
  id: number | string;
  name: string;
  qty: number;
  price: string;
  isEssential: boolean;
}

const props = defineProps<{ 
  transaction: any; 
  isSaving: boolean;
  apiError?: string;
}>();

const emit = defineEmits<{
  (e: 'save', data: TransactionUpdate, items: FormItem[] | null): void;
  (e: 'cancel'): void;
  (e: 'clearError'): void;
}>();

const financeStore = useFinanceStore();
const categoryStore = useCategoryStore();

const txType = ref<'expense' | 'income' | 'transfer'>(props.transaction?.type || 'expense');
const amount = ref<string>((props.transaction?.amount || 0).toString());
const categoryId = ref<string>(props.transaction?.category_id || '');
const accountId = ref<string>(props.transaction?.account_id || '');
const transferToAccountId = ref<string>(props.transaction?.transfer_to_account_id || '');
const description = ref<string>(props.transaction?.description || '');
const date = ref<Date>(props.transaction?.occurred_at ? new Date(props.transaction.occurred_at) : new Date());
const isEssential = ref<boolean>(!!props.transaction?.is_essential); 
const txCurrency = ref<string>(props.transaction?.currency || 'CRC');
const exchangeRate = ref<string>(props.transaction?.exchange_rate && props.transaction.exchange_rate !== 1 ? props.transaction.exchange_rate.toString() : '');

const transactionItems = props.transaction?.items || [];
const isItemized = ref<boolean>(transactionItems.length > 0);

const items = ref<FormItem[]>(
  isItemized.value 
    ? transactionItems.map((i: any) => ({
        id: i.id || Date.now() + Math.random(),
        name: i.product_name || '',
        qty: Number(i.quantity) || 1,
        price: i.quantity ? (Number(i.line_total) / Number(i.quantity)).toString() : '0',
        isEssential: !!i.is_essential
      }))
    : [{ id: Date.now(), name: '', qty: 1, price: '', isEssential: false }]
);

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

const domainsAllowedToItemize = ['grocery', 'home'];
const showItemizedOption = computed(() => {
  if (txType.value === 'income') return false;
  const cat = categoryStore.categories.find((c: Category) => c.id === categoryId.value);
  return cat ? domainsAllowedToItemize.includes(cat.domain) : false;
});

const formatCurrency = (val: number, currencyCode?: string) => {
  const num = new Intl.NumberFormat('es-CR', { minimumFractionDigits: 2 }).format(val);
  if (currencyCode) {
    const c = CURRENCIES.find(x => x.code === currencyCode);
    return `${c ? c.symbol : '$'}${num}`;
  }
  return num;
};

const addItem = () => items.value.push({ id: Date.now(), name: '', qty: 1, price: '', isEssential: false });
const removeItem = (id: number | string) => {
  if (items.value.length > 1) items.value = items.value.filter(item => item.id !== id);
};

const totalItemized = computed(() => {
  return items.value.reduce((sum, item) => sum + ((Number(item.price) || 0) * (item.qty || 1)), 0);
});

const missingFields = computed(() => {
  const missing = [];
  
  if (isItemized.value) {
    if (items.value.length === 0) missing.push('productos');
    else if (!items.value.every(i => (i.name || '').trim() !== '' && i.qty > 0 && Number(i.price) > 0)) missing.push('datos en productos');
  } else {
    if (Number(amount.value) <= 0) missing.push('monto');
  }

  if (txType.value === 'transfer') {
    if (!transferToAccountId.value) missing.push('cuenta destino');
    if (accountId.value && accountId.value === transferToAccountId.value) missing.push('cuentas distintas');
  } else {
    if (!categoryId.value) missing.push('categoría');
  }
  
  if (isCrossCurrency.value && (!exchangeRate.value || Number(exchangeRate.value) <= 0)) {
    missing.push('tasa de cambio');
  }

  return missing;
});

const isValid = computed(() => missingFields.value.length === 0 && accountId.value !== '');

const handleSave = () => {
  if (!isValid.value) return;

  const finalAmount = isItemized.value ? totalItemized.value : Number(amount.value);
  const isoDate = !isNaN(date.value.getTime()) ? date.value.toISOString() : new Date().toISOString();

  const updateData: TransactionUpdate = {
    type: txType.value,
    amount: finalAmount,
    category_id: categoryId.value || undefined,
    account_id: accountId.value || undefined,
    transfer_to_account_id: transferToAccountId.value || undefined,
    description: description.value || undefined,
    exchange_rate: isCrossCurrency.value ? Number(exchangeRate.value) : undefined,
    exchange_source: isCrossCurrency.value ? 'user' : undefined,
    occurred_at: isoDate
  };

  emit('save', updateData, isItemized.value ? items.value : null);
};
</script>

<template>
  <GlassAlert :show="showError" :message="errorMessage" type="error" @close="handleCloseError" />

  <div class="flex flex-col h-full animate-in fade-in slide-in-from-right-4 duration-300">
    
    <div class="mb-6 flex-1">
      
      <transition name="fade">
        <div v-if="showItemizedOption" class="flex items-center justify-between mb-6 px-4 py-3 bg-white/50 dark:bg-black/20 rounded-xl border border-slate-200/50 dark:border-white/5 shadow-sm">
          <div class="flex items-center gap-2.5 text-sm font-semibold text-slate-700 dark:text-slate-300">
            <component :is="resolveIcon('ShoppingCart')" class="w-4 h-4" /> ¿Desglosar factura detallada?
          </div>
          <button @click="isItemized = !isItemized" class="relative inline-flex h-6 w-11 items-center rounded-full transition-colors duration-300" :class="isItemized ? 'bg-slate-800 dark:bg-slate-200' : 'bg-slate-300 dark:bg-white/10 shadow-inner'">
            <span class="inline-block h-4 w-4 transform rounded-full bg-white transition duration-300 shadow" :class="isItemized ? 'translate-x-6' : 'translate-x-1'" />
          </button>
        </div>
      </transition>

      <div class="mb-6 text-center">
        <p class="text-[10px] font-bold text-slate-400 dark:text-slate-500 uppercase tracking-widest mb-3">
          {{ isItemized ? 'Monto Total Calculado' : 'Monto de la transacción' }}
        </p>
        
        <transition name="fade" mode="out-in">
          <div v-if="!isItemized" class="flex justify-center w-full">
            <GlassCurrencyInput v-model="amount" :type="txType" :symbol="txCurrencySymbol" />
          </div>
          
          <div v-else class="flex justify-center items-center gap-1 w-full px-2">
            <span class="font-extrabold text-slate-300 dark:text-slate-600 transition-all duration-200" 
                  :class="formatCurrency(totalItemized).length < 7 ? 'text-3xl' : 'text-2xl'">{{ txCurrencySymbol }}</span>
            <span class="font-extrabold text-slate-900 dark:text-white truncate max-w-[320px] transition-all duration-200 ease-out"
                  :class="formatCurrency(totalItemized).length < 7 ? 'text-6xl md:text-7xl' : (formatCurrency(totalItemized).length < 10 ? 'text-5xl md:text-6xl' : (formatCurrency(totalItemized).length < 13 ? 'text-4xl md:text-5xl' : 'text-3xl md:text-4xl'))">
              {{ formatCurrency(totalItemized) }}
            </span>
          </div>
        </transition>
      </div>
      
      <div class="mt-4 relative z-[45] opacity-70 cursor-not-allowed">
        <label class="flex items-center gap-2 text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-widest mb-2 ml-1">
          <Coins class="w-4 h-4" /> Moneda Original (Bloqueada)
        </label>
        <div class="w-full flex items-center justify-between px-4 py-3.5 bg-slate-100/50 dark:bg-black/20 border border-slate-200/50 dark:border-white/5 rounded-xl">
           <span class="text-sm font-bold text-slate-700 dark:text-slate-300">{{ txCurrency }}</span>
        </div>
      </div>

      <transition name="fade-slide">
        <div v-if="isCrossCurrency && selectedAccount" class="mt-4 p-3 bg-blue-50/50 dark:bg-blue-900/10 border border-blue-200/50 dark:border-blue-800/30 rounded-xl flex items-center justify-between gap-3">
          <div class="flex items-center gap-2 text-slate-700 dark:text-slate-300">
            <Calculator class="w-4 h-4 text-blue-500 shrink-0" />
            <div class="text-left">
              <p class="text-xs font-bold">Tipo de Cambio</p>
              <p v-if="txType === 'transfer' && selectedTransferAccount" class="text-[9px] opacity-70">
                1 {{ selectedAccount.currency }} = X {{ selectedTransferAccount.currency }}
              </p>
              <p v-else class="text-[9px] opacity-70">
                1 {{ txCurrency }} = X {{ selectedAccount.currency }}
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

      <div class="flex justify-center my-6 h-10">
        <transition name="fade">
          <button v-if="txType === 'expense' && !isItemized" @click="isEssential = !isEssential" class="flex items-center gap-2 px-4 py-2 rounded-full text-xs font-bold transition-all duration-300 border" :class="isEssential ? 'bg-amber-50 dark:bg-amber-500/10 text-amber-600 dark:text-amber-400 border-amber-200 dark:border-amber-500/20 shadow-sm' : 'bg-slate-100 dark:bg-white/5 text-slate-500 dark:text-slate-400 border-slate-200/50 dark:border-white/5 hover:bg-slate-200 dark:hover:bg-white/10'">
            <Star class="w-3.5 h-3.5 transition-all" :class="isEssential ? 'fill-amber-500 text-amber-500' : 'opacity-70'" />
            {{ isEssential ? 'Gasto Indispensable' : 'Marcar como Indispensable' }}
          </button>
        </transition>
      </div>

      <transition name="items-expand">
        <div v-if="isItemized" class="space-y-3 mb-8 border-t border-b border-slate-200/50 dark:border-white/5 py-6 overflow-hidden">
          <div v-for="item in items" :key="item.id" class="flex gap-2 items-center bg-white/50 dark:bg-[#1a1a1a]/40 p-2 rounded-xl border border-slate-200/50 dark:border-white/5 shadow-inner group transition-all">
            <button @click="item.isEssential = !item.isEssential" class="p-1.5 rounded-md transition-colors shrink-0" :class="item.isEssential ? 'text-amber-500 bg-amber-50 dark:bg-amber-500/10' : 'text-slate-400 hover:text-amber-500 hover:bg-slate-100 dark:hover:bg-white/5'" title="Marcar como indispensable">
              <Star class="w-4 h-4 transition-all" :class="item.isEssential ? 'fill-amber-500' : ''" />
            </button>
            <input v-model="item.name" type="text" placeholder="Producto..." class="flex-1 min-w-[80px] bg-transparent px-1 text-sm outline-none dark:text-white placeholder:text-slate-400 dark:placeholder:text-slate-600">
            <input v-model="item.qty" type="number" min="1" placeholder="Cant." class="w-14 no-spinners bg-white/80 dark:bg-black/20 px-2 py-1.5 rounded-lg text-sm text-center outline-none dark:text-white border border-slate-200/50 dark:border-white/5">
            <div class="w-24 shrink-0">
              <GlassSmallCurrencyInput v-model="item.price" />
            </div>
            <button @click="removeItem(item.id)" class="p-1.5 text-slate-400 hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-500/10 rounded-md transition-colors shrink-0 md:opacity-0 md:group-hover:opacity-100">
              <Trash2 class="w-4 h-4" />
            </button>
          </div>
          <button @click="addItem" class="w-full py-3 mt-2 flex items-center justify-center gap-2 text-sm font-bold text-slate-700 dark:text-slate-300 bg-white/70 dark:bg-white/5 hover:bg-white dark:hover:bg-white/10 rounded-xl border border-slate-200/50 dark:border-white/5 transition-colors shadow-sm">
            <Plus class="w-4 h-4" /> Añadir Producto
          </button>
        </div>
      </transition>

      <div class="space-y-4">
        <div class="relative z-[30]">
          <GlassSelect v-if="txType !== 'transfer'" v-model="categoryId" :options="filteredCategories" placeholder="Seleccionar Categoría..." :icon="selectedCategoryIcon" />
        </div>

        <div class="flex flex-col sm:flex-row gap-4 relative z-[20]">
          <div class="w-full relative z-[25]">
            <GlassSelect v-model="accountId" :options="financeStore.accounts.map(a => ({ id: a.id, name: a.name, icon: Wallet }))" :placeholder="txType === 'income' ? 'Abonar a Cuenta...' : 'Pagar desde Cuenta...'" :icon="Wallet" />
            <transition name="fade">
              <p v-if="selectedAccount" class="absolute -bottom-4 right-2 text-[10px] font-semibold text-slate-400 dark:text-slate-500">
                Saldo: {{ formatCurrency(selectedAccount.current_balance, selectedAccount.currency) }}
              </p>
            </transition>
          </div>
          <div v-if="txType === 'transfer'" class="w-full relative z-[15]">
            <GlassSelect v-model="transferToAccountId" :options="financeStore.accounts.filter(a => a.id !== accountId).map(a => ({ id: a.id, name: a.name, icon: Wallet }))" placeholder="Destino del Ahorro..." :icon="Wallet" />
            <transition name="fade">
              <p v-if="selectedTransferAccount" class="absolute -bottom-4 right-2 text-[10px] font-semibold text-slate-400 dark:text-slate-500">
                Saldo: {{ formatCurrency(selectedTransferAccount.current_balance, selectedTransferAccount.currency) }}
              </p>
            </transition>
          </div>
        </div>

        <div class="h-1"></div> 

        <div class="flex flex-col sm:flex-row gap-4 relative z-[10]">
          <div class="w-full sm:w-[50%] shrink-0">
            <GlassNativeDatePicker v-model="date" />
          </div>
          <div class="relative group flex-1">
            <FileText class="absolute left-4 top-3.5 h-5 w-5 text-slate-400 dark:text-slate-500 group-focus-within:text-slate-800 dark:group-focus-within:text-white transition-colors" />
            <input v-model="description" type="text" placeholder="Nota rápida (Opcional)" class="w-full pl-12 pr-4 py-3.5 bg-white/50 dark:bg-black/20 border border-slate-200/50 dark:border-white/5 rounded-xl outline-none text-slate-900 dark:text-white placeholder:text-slate-400 transition-all focus:bg-white/80 dark:focus:bg-black/40 focus:ring-2 focus:ring-slate-900/20 dark:focus:ring-white/20">
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
        <Check v-else class="w-4 h-4" />
        {{ isSaving ? 'Guardando...' : 'Guardar Cambios' }}
      </button>
    </div>

  </div>
</template>

<style scoped>
.fade-slide-enter-active, .fade-slide-leave-active { transition: all 0.3s ease; }
.fade-slide-enter-from, .fade-slide-leave-to { opacity: 0; transform: translateY(-10px); }
</style>