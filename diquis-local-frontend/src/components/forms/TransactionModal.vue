<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue';
import { financeService } from '../../services/financeService';
import { categoryService } from '../../services/categoryService';
import type { Category } from '../../types/category';
import { resolveIcon } from '../../utils/icons';
import { useFinanceStore } from '../../stores/finance';
import { useCategoryStore } from '../../stores/category';
import { CURRENCIES } from '../../constants/currencies'; 
import { useScreen } from '../../composables/useScreen';
import GlassModal from '../ui/GlassModal.vue';
import GlassSelect from '../ui/GlassSelect.vue';
import GlassCurrencySelect from '../ui/GlassCurrencySelect.vue';
import GlassNativeDatePicker from '../ui/GlassNativeDatePicker.vue'; 
import GlassCurrencyInput from '../ui/GlassCurrencyInput.vue';
import GlassSmallCurrencyInput from '../ui/GlassSmallCurrencyInput.vue';
import GlassAlert from '../ui/GlassAlert.vue'; 
import { 
  TrendingUp, TrendingDown, Tag, FileText, Plus, Trash2, Loader2, Star, Wallet, ArrowRightLeft, Info, Calculator 
} from 'lucide-vue-next';

const props = defineProps<{ 
  isOpen: boolean,
  defaultTab?: 'expense' | 'income' | 'transfer',
  hideTabs?: boolean 
}>();

const emit = defineEmits(['close']);
const financeStore = useFinanceStore();
const categoryStore = useCategoryStore();
const { isMobile } = useScreen();

const date = ref(new Date());
const isCalendarPickerOpen = ref(false);
const isSaving = ref(false);
const apiError = ref(''); 
const categoriesDB = ref<Category[]>([]);
const txType = ref<'expense' | 'income' | 'transfer'>('expense');
const amount = ref<string>('');
const categoryId = ref('');
const accountId = ref('');
const transferToAccountId = ref('');
const description = ref('');
const isEssential = ref(false);
const txCurrency = ref('CRC');
const exchangeRate = ref<string>('');

const isItemized = ref(false);
const items = ref([{ id: Date.now(), name: '', qty: 1, price: '', isEssential: false }]);

const dynamicTitle = computed(() => {
  if (!props.hideTabs) return "Nueva Transacción";
  if (txType.value === 'income') return "Nuevo Ingreso";
  if (txType.value === 'transfer') return "Nueva Transferencia";
  return "Nuevo Gasto";
});

onMounted(async () => {
  try {
    categoriesDB.value = await categoryService.getCategories();
  } catch (error) {
    console.error("Error cargando categorías:", error);
  }
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
    exchangeRate.value = '';
  }
});

watch(() => props.isOpen, (newVal) => {
  if (newVal) {
    txType.value = props.defaultTab || 'expense';
    apiError.value = ''; 
    date.value = new Date();
    exchangeRate.value = '';
    if (financeStore.accounts.length > 0) {
      if (!accountId.value) {
        const main = financeStore.accounts.find(a => a.name === "Billetera Principal");
        accountId.value = main ? main.id : financeStore.accounts[0].id;
      }
      if (!transferToAccountId.value) {
        const saving = financeStore.accounts.find(a => a.account_type === "saving");
        transferToAccountId.value = saving ? saving.id : '';
      }
    }
  }
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
  if (txType.value === 'income' || txType.value === 'transfer') return false;
  const cat = categoriesDB.value.find((c: Category) => c.id === categoryId.value);
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
const removeItem = (id: number) => {
  if (items.value.length > 1) items.value = items.value.filter(item => item.id !== id);
};
const totalItemized = computed(() => {
  return items.value.reduce((sum, item) => sum + ((Number(item.price) || 0) * (Number(item.qty) || 1)), 0);
});

const missingFields = computed(() => {
  const missing = [];
  
  if (isItemized.value) {
    if (items.value.length === 0) missing.push('productos');
    else if (!items.value.every(i => i.name.trim() !== '' && Number(i.qty) > 0 && Number(i.price) > 0)) missing.push('datos de productos');
  } else {
    if (Number(amount.value) <= 0) missing.push('monto');
  }

  if (txType.value === 'transfer') {
    if (!transferToAccountId.value) missing.push('cuenta_destino');
    if (accountId.value && accountId.value === transferToAccountId.value) missing.push('cuentas_distintas');
  } else {
    if (!categoryId.value) missing.push('categoría');
  }

  if (isCrossCurrency.value && (!exchangeRate.value || Number(exchangeRate.value) <= 0)) {
    missing.push('tasa_cambio');
  }

  return missing;
});

const hasMissingField = (field: string) => missingFields.value.includes(field);
const isValid = computed(() => missingFields.value.length === 0 && accountId.value !== '');

const handleTabChange = (type: 'expense' | 'income' | 'transfer') => {
  txType.value = type;
  categoryId.value = '';
  amount.value = '';
  description.value = '';
  isEssential.value = false;
  isItemized.value = false;
  apiError.value = ''; 
  date.value = new Date(); 
};

const handleSave = async () => {
  if (!isValid.value) return;
  isSaving.value = true;
  apiError.value = ''; 

  try {
    const finalAmount = isItemized.value ? totalItemized.value : Number(amount.value);
    const isoDateToSave = date.value.toISOString();

    const newTx = await financeService.createTransaction({
      type: txType.value,
      amount: finalAmount,
      currency: txCurrency.value,
      exchange_rate: isCrossCurrency.value ? Number(exchangeRate.value) : undefined,
      exchange_source: isCrossCurrency.value ? 'user' : undefined,
      account_id: accountId.value,
      transfer_to_account_id: txType.value === 'transfer' ? transferToAccountId.value : undefined,
      category_id: txType.value === 'transfer' ? undefined : categoryId.value,
      description: description.value || undefined,
      occurred_at: isoDateToSave
    });

    if (isItemized.value && items.value.length > 0) {
      await Promise.all(items.value.map(item => {
        return financeService.addTransactionItem(newTx.id, {
          product_name: item.name,
          quantity: Number(item.qty),
          line_total: Number(item.price) * Number(item.qty), 
          is_essential: item.isEssential
        });
      }));
    }

    await financeStore.refreshAllData();
    handleTabChange(txType.value); 
    items.value = [{ id: Date.now(), name: '', qty: 1, price: '', isEssential: false }];
    emit('close');

  } catch (error: any) {
    console.error("Error guardando transacción:", error);
    apiError.value = error.response?.data?.detail || "Ocurrió un error inesperado al guardar. Revisa tu conexión.";
  } finally {
    isSaving.value = false;
  }
};
</script>

<template>
  <GlassModal :is-open="isOpen" :title="dynamicTitle" @close="emit('close')" :scrollable="false" :no-padding="true">
    
    <div class="w-full h-full flex flex-col overflow-y-auto custom-scrollbar relative">
      
      <div class="p-4 sm:p-6 flex-1 shrink-0">
        
        <GlassAlert class="mb-4" :show="!!apiError" :message="apiError" type="error" @close="apiError = ''" />

        <div v-if="!hideTabs" class="flex p-1.5 bg-slate-200/50 dark:bg-white/5 rounded-xl backdrop-blur-sm border border-slate-300/50 dark:border-white/5 mb-6 shadow-inner relative z-[50]">
          <button @click="handleTabChange('expense')" class="flex-1 flex items-center justify-center gap-2 py-2.5 rounded-lg text-sm font-bold transition-all duration-300" :class="txType === 'expense' ? 'bg-white dark:bg-[#1a1a1a] text-slate-900 dark:text-white shadow-md border border-slate-200 dark:border-white/5' : 'text-slate-500 hover:text-slate-700 dark:hover:text-slate-300 border border-transparent'">
            <TrendingDown class="w-4 h-4" :class="txType === 'expense' ? 'text-red-500 dark:text-red-400' : 'opacity-70'" /> Gasto
          </button>
          <button @click="handleTabChange('income')" class="flex-1 flex items-center justify-center gap-2 py-2.5 rounded-lg text-sm font-bold transition-all duration-300" :class="txType === 'income' ? 'bg-white dark:bg-[#1a1a1a] text-slate-900 dark:text-white shadow-md border border-slate-200 dark:border-white/5' : 'text-slate-500 hover:text-slate-700 dark:hover:text-slate-300 border border-transparent'">
            <TrendingUp class="w-4 h-4" :class="txType === 'income' ? 'text-green-500 dark:text-green-400' : 'opacity-70'" /> Ingreso
          </button>
          <button @click="handleTabChange('transfer')" class="flex-1 flex items-center justify-center gap-2 py-2.5 rounded-lg text-sm font-bold transition-all duration-300" :class="txType === 'transfer' ? 'bg-white dark:bg-[#1a1a1a] text-slate-900 dark:text-white shadow-md border border-slate-200 dark:border-white/5' : 'text-slate-500 hover:text-slate-700 dark:hover:text-slate-300 border border-transparent'">
            <ArrowRightLeft class="w-4 h-4" :class="txType === 'transfer' ? 'text-slate-800 dark:text-slate-200' : 'opacity-70'" /> Transferir
          </button>
        </div>

        <div class="p-4 sm:p-6 bg-slate-50/50 dark:bg-[#111111]/40 border border-slate-200/50 dark:border-white/5 rounded-2xl relative mb-4 transition-all"
             :class="{ 'border-amber-400 dark:border-amber-500/50 shadow-[0_0_10px_rgba(251,191,36,0.1)]': hasMissingField('monto') && amount === '' }">
          
          <p class="text-[10px] font-bold text-slate-400 dark:text-slate-500 uppercase tracking-widest mb-3 text-center pt-1"
             :class="{ 'text-amber-500 dark:text-amber-400': hasMissingField('monto') && amount === '' }">
            {{ isItemized ? 'Monto Total Calculado' : 'Monto de la transacción' }}
          </p>
          
          <transition name="fade" mode="out-in">
            <div v-if="!isItemized" class="flex justify-center">
              <GlassCurrencyInput 
                v-model="amount" 
                :type="txType" 
                :auto-focus="!isMobile"
                :symbol="txCurrencySymbol" 
              />
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

          <div class="mt-4 sm:mt-6 relative z-[45]">
            <GlassCurrencySelect v-model="txCurrency" placeholder="Seleccionar Moneda..." />
          </div>

          <transition name="fade-slide">
            <div v-if="isCrossCurrency && selectedAccount" class="mt-4 p-3 bg-blue-50/50 dark:bg-blue-900/10 border rounded-xl flex flex-wrap sm:flex-nowrap items-center justify-between gap-3"
                 :class="hasMissingField('tasa_cambio') ? 'border-amber-400 dark:border-amber-500/50' : 'border-blue-200/50 dark:border-blue-800/30'">
              <div class="flex items-center gap-2 text-slate-700 dark:text-slate-300">
                <Calculator class="w-4 h-4 text-blue-500 shrink-0" />
                <div class="text-left">
                  <p class="text-xs font-bold" :class="{ 'text-amber-600 dark:text-amber-400': hasMissingField('tasa_cambio') }">Tipo de Cambio</p>
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
                type="number" step="0.01" placeholder="Ej: 515.20"
                class="w-full sm:w-24 px-2 py-1.5 text-sm sm:text-right bg-white dark:bg-black/40 border border-slate-200 dark:border-white/10 rounded-lg outline-none focus:ring-2 focus:ring-blue-500/50 dark:text-white"
              >
            </div>
          </transition>
        </div>

        <div class="flex flex-col gap-2 mb-6">
          <transition name="fade-slide">
            <div v-if="showItemizedOption" class="flex items-center justify-between p-3 bg-white/80 dark:bg-black/40 rounded-xl border border-slate-200/50 dark:border-white/5 backdrop-blur-sm shadow-sm">
              <div class="flex items-center gap-3">
                <div class="p-1.5 rounded-lg bg-slate-100 dark:bg-white/5 text-slate-500 dark:text-slate-400">
                  <component :is="resolveIcon('ShoppingCart')" class="w-4 h-4" />
                </div>
                <div class="text-left">
                  <p class="text-xs font-bold text-slate-700 dark:text-slate-300">Factura Detallada</p>
                  <p class="text-[9px] font-medium text-slate-400">Desglosar por productos</p>
                </div>
              </div>
              <button @click="isItemized = !isItemized" class="w-11 h-6 rounded-full relative transition-colors duration-300 shadow-inner shrink-0" :class="isItemized ? 'bg-slate-800 dark:bg-slate-200' : 'bg-slate-300 dark:bg-slate-700'">
                <div class="absolute top-1 left-1 w-4 h-4 rounded-full bg-white transition-transform duration-300 shadow-sm" :class="isItemized ? 'translate-x-5 bg-white dark:bg-slate-900' : 'translate-x-0'"></div>
              </button>
            </div>
          </transition>

          <transition name="fade-slide">
            <div v-if="txType === 'expense' && !isItemized" class="flex items-center justify-between p-3 rounded-xl border backdrop-blur-sm transition-all duration-300 shadow-sm" :class="isEssential ? 'bg-amber-50/80 dark:bg-amber-500/5 border-amber-200/50 dark:border-amber-500/20' : 'bg-white/80 dark:bg-black/40 border-slate-200/50 dark:border-white/5'">
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
        </div>

        <transition name="items-expand">
          <div v-if="isItemized" class="space-y-3 mb-6 py-2 overflow-hidden">
            <div v-for="item in items" :key="item.id" class="flex flex-wrap sm:flex-nowrap gap-2 items-center bg-slate-50/50 dark:bg-[#111111]/40 p-2 sm:p-3 rounded-2xl border border-slate-200/50 dark:border-white/5 shadow-inner group transition-all">
              <button @click="item.isEssential = !item.isEssential" class="p-1.5 rounded-xl transition-colors shrink-0" :class="item.isEssential ? 'text-amber-500 bg-amber-50 dark:bg-amber-500/10 border border-amber-200/50 dark:border-amber-500/20' : 'text-slate-400 hover:text-amber-500 hover:bg-slate-100 dark:hover:bg-white/5 border border-transparent'" title="Marcar como indispensable">
                <Star class="w-4 h-4 transition-all" :class="item.isEssential ? 'fill-amber-500' : ''" />
              </button>
              <input v-model="item.name" type="text" placeholder="Producto..." class="flex-1 min-w-[120px] bg-transparent px-1 text-sm font-medium outline-none dark:text-white placeholder:text-slate-400 dark:placeholder:text-slate-600">
              <div class="flex gap-2 w-full sm:w-auto mt-2 sm:mt-0 justify-end">
                <input v-model="item.qty" type="number" min="1" placeholder="Cant." class="w-14 no-spinners bg-white/80 dark:bg-black/20 px-2 py-1.5 rounded-lg text-sm font-bold text-center outline-none dark:text-white border border-slate-200/50 dark:border-white/5">
                <div class="w-24 shrink-0">
                  <GlassSmallCurrencyInput v-model="item.price" />
                </div>
                <button @click="removeItem(item.id)" class="p-1.5 text-slate-400 hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-500/10 rounded-xl transition-colors shrink-0 sm:opacity-0 sm:group-hover:opacity-100">
                  <Trash2 class="w-4 h-4" />
                </button>
              </div>
            </div>
            <button @click="addItem" class="w-full py-3 flex items-center justify-center gap-2 text-xs font-bold text-slate-500 dark:text-slate-400 border border-dashed border-slate-300 dark:border-slate-700 rounded-2xl hover:bg-slate-50 dark:hover:bg-white/5 hover:text-slate-700 dark:hover:text-slate-300 hover:border-slate-400 dark:hover:border-slate-500 transition-all">
              <Plus class="w-4 h-4" /> Añadir otro producto
            </button>
          </div>
        </transition>

        <div class="space-y-4 sm:space-y-5 relative">
          <div class="relative z-[40]" :class="{ 'ring-1 ring-amber-400 dark:ring-amber-500/50 rounded-xl': hasMissingField('categoría') }">
            <GlassSelect v-if="txType !== 'transfer'" v-model="categoryId" :options="filteredCategories" placeholder="Seleccionar Categoría..." :icon="selectedCategoryIcon" />
            <p v-if="hasMissingField('categoría')" class="text-[10px] text-amber-500 absolute -bottom-4 right-2 font-semibold">Selecciona una categoría</p>
          </div>

          <div class="flex flex-col sm:flex-row gap-4 sm:gap-6 relative z-[30] mt-2">
            <div class="w-full relative z-[35]">
              <GlassSelect v-model="accountId" :options="financeStore.accounts.map(a => ({ id: a.id, name: a.name, icon: Wallet }))" :placeholder="txType === 'income' ? 'Abonar a...' : 'Pagar desde...'" :icon="Wallet" />
              <transition name="fade">
                <p v-if="selectedAccount" class="absolute -bottom-4 right-2 text-[10px] font-semibold text-slate-400 dark:text-slate-500">
                  Saldo: {{ formatCurrency(selectedAccount.current_balance, selectedAccount.currency) }}
                </p>
              </transition>
            </div>
            <div v-if="txType === 'transfer'" class="w-full relative z-[25]" :class="{ 'ring-1 ring-amber-400 dark:ring-amber-500/50 rounded-xl': hasMissingField('cuenta_destino') || hasMissingField('cuentas_distintas') }">
              <GlassSelect v-model="transferToAccountId" :options="financeStore.accounts.filter(a => a.id !== accountId).map(a => ({ id: a.id, name: a.name, icon: Wallet }))" placeholder="Cuenta Destino..." :icon="Wallet" />
              <transition name="fade">
                <p v-if="selectedTransferAccount" class="absolute -bottom-4 right-2 text-[10px] font-semibold text-slate-400 dark:text-slate-500">
                  Saldo: {{ formatCurrency(selectedTransferAccount.current_balance, selectedTransferAccount.currency) }}
                </p>
              </transition>
            </div>
          </div>

          <div class="h-1 sm:h-2"></div>

          <div class="flex flex-col sm:flex-row gap-4 relative z-[10]">
            <div class="w-full sm:w-[50%] shrink-0">
              <GlassNativeDatePicker v-model="date" @toggle="isCalendarPickerOpen = $event" />
            </div>
            <div class="relative group flex-1">
              <FileText class="absolute left-4 top-3.5 h-5 w-5 text-slate-400 dark:text-slate-500 group-focus-within:text-slate-800 dark:group-focus-within:text-white transition-colors" />
              <input v-model="description" type="text" placeholder="Nota rápida (Opcional)" class="w-full pl-12 pr-4 py-3.5 bg-white/50 dark:bg-black/20 border border-slate-200/50 dark:border-white/5 rounded-xl outline-none text-slate-900 dark:text-white placeholder:text-slate-400 transition-all focus:bg-white/80 dark:focus:bg-black/40 focus:ring-2 focus:ring-slate-900/20 dark:focus:ring-white/20">
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
          <span v-else>Guardar Transacción</span>
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
.fade-slide-enter-active, .fade-slide-leave-active { transition: all 0.3s ease; }
.fade-slide-enter-from, .fade-slide-leave-to { opacity: 0; transform: translateY(-8px); }
.items-expand-enter-active, .items-expand-leave-active { transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1); max-height: 500px; opacity: 1; }
.items-expand-enter-from, .items-expand-leave-to { max-height: 0; opacity: 0; padding-top: 0; padding-bottom: 0; margin-top: 0; margin-bottom: 0; border-color: transparent; }
.custom-scrollbar::-webkit-scrollbar { width: 6px; }
.custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
.custom-scrollbar::-webkit-scrollbar-thumb { background: rgba(156, 163, 175, 0.3); border-radius: 10px; }
.custom-scrollbar::-webkit-scrollbar-thumb:hover { background: rgba(156, 163, 175, 0.5); }
</style>