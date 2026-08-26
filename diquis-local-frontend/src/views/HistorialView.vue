<script setup lang="ts">
import { ref, onMounted, watch, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useFinanceStore } from '../stores/finance';
import { useCategoryStore } from '../stores/category';
import GlassMonthStepper from '../components/ui/GlassMonthStepper.vue';
import GlassSelect from '../components/ui/GlassSelect.vue';
import TransactionList from '../components/transactions/TransactionList.vue'; 
import TransactionDetailDrawer from '../components/forms/TransactionDetailDrawer.vue'; 
import TransactionModal from '../components/forms/TransactionModal.vue'; 
import GlassCard from '../components/ui/GlassCard.vue';
import MiniGlassBankCard from '../components/ui/MiniGlassBankCard.vue';
import { Filter, ArrowDownUp, RefreshCcw, ChevronLeft, ChevronRight, Layers, Plus } from 'lucide-vue-next';

const route = useRoute();
const router = useRouter();
const financeStore = useFinanceStore();
const categoryStore = useCategoryStore();

const selectedDate = ref(new Date());
const filterType = ref('all');
const filterAccountId = ref<string | null>(null);

const isDetailDrawerOpen = ref(false);
const selectedTransactionId = ref<string | null>(null);
const isTransactionModalOpen = ref(false); 

const currentPage = ref(1);
const itemsPerPage = 10;

const filterOptions = [
  { id: 'all', name: 'Todos los movimientos', icon: ArrowDownUp },
  { id: 'income', name: 'Solo Ingresos', icon: ArrowDownUp },
  { id: 'expense', name: 'Solo Gastos', icon: ArrowDownUp },
];

const sortedAccounts = computed(() => {
  return [...financeStore.accounts].sort((a, b) => {
    const getPriority = (type: string) => {
      if (type === 'checking') return 1; 
      if (type === 'saving') return 2;   
      return 3;                                     
    };
    return getPriority(a.account_type) - getPriority(b.account_type);
  });
});

const createSecureSlug = (account: any) => {
  if (!account || !account.name || !account.id) return '';
  const nameSlug = account.name.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase().trim().replace(/[^a-z0-9 ]/g, "").replace(/\s+/g, "-");
  const shortId = account.id.split('-')[0]; 
  return `${nameSlug}-${shortId}`;
};

const loadMonthData = async () => {
  const year = selectedDate.value.getFullYear();
  const month = selectedDate.value.getMonth();
  const start = new Date(year, month, 1).toISOString();
  const end = new Date(year, month + 1, 0, 23, 59, 59).toISOString();
  await financeStore.fetchMonthlyTransactions(start, end, filterAccountId.value || undefined);
};

const handleManualRefresh = async () => {
  await categoryStore.fetchCategories(true);
  await loadMonthData();
};

const filteredTransactions = computed(() => {
  if (filterType.value === 'all') return financeStore.monthlyTransactions;
  return financeStore.monthlyTransactions.filter(tx => tx.type === filterType.value);
});

const handleAccountSelect = (account: any | null) => {
  if (account) {
    filterAccountId.value = account.id; 
    router.replace({ query: { ...route.query, cuenta: createSecureSlug(account) } });
  } else {
    filterAccountId.value = null; 
    const query = { ...route.query };
    delete query.cuenta; 
    router.replace({ query });
  }
};

watch([selectedDate, filterType, filterAccountId], () => { currentPage.value = 1; });
watch(filterAccountId, () => { loadMonthData(); });

const totalPages = computed(() => Math.max(1, Math.ceil(filteredTransactions.value.length / itemsPerPage)));
const paginatedTransactions = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage;
  return filteredTransactions.value.slice(start, start + itemsPerPage);
});

const nextPage = () => { if (currentPage.value < totalPages.value) currentPage.value++; };
const prevPage = () => { if (currentPage.value > 1) currentPage.value--; };

const openTransactionDetail = (id: string) => {
  selectedTransactionId.value = id;
  isDetailDrawerOpen.value = true;
};

const handleModalClose = () => {
  isTransactionModalOpen.value = false;
  loadMonthData(); 
};

onMounted(async () => {
  await categoryStore.fetchCategories();
  await financeStore.fetchAccounts();
  if (route.query.cuenta) {
    const shortId = (route.query.cuenta as string).split('-').pop();
    const matchedAccount = financeStore.accounts.find((a) => a.id.startsWith(shortId!));
    if (matchedAccount) filterAccountId.value = matchedAccount.id;
  }
  await loadMonthData();
});
watch(selectedDate, () => loadMonthData());
</script>

<template>
  <div class="max-w-5xl mx-auto flex flex-col min-h-[calc(100vh-8rem)] relative">
    
    <div class="flex justify-between items-end relative z-20 mb-6 px-4 sm:px-0">
      <div>
        <h3 class="text-2xl font-extrabold text-slate-900 dark:text-white tracking-tight leading-none">Historial</h3>
        <p class="text-xs font-semibold text-slate-500 dark:text-slate-400 mt-1.5">Registro de tus movimientos pasados</p>
      </div>
      
      <div class="flex items-center gap-2 sm:gap-3">
        <button 
          @click="handleManualRefresh" 
          class="text-slate-400 hover:text-slate-800 dark:text-slate-500 dark:hover:text-white bg-slate-100 dark:bg-white/5 p-2.5 rounded-full transition-all duration-300"
        >
          <RefreshCcw class="w-4 h-4" :class="{ 'animate-spin text-slate-900 dark:text-white': financeStore.isMonthlyLoading }" />
        </button>

        <button 
          @click="isTransactionModalOpen = true"
          class="hidden lg:flex items-center gap-1.5 sm:gap-2 bg-slate-900 dark:bg-white text-white dark:text-slate-900 px-4 py-2.5 rounded-xl font-bold text-sm hover:opacity-90 transition-opacity shadow-sm"
        >
          <Plus class="w-4 h-4" />
          <span>Agregar</span>
        </button>
      </div>
    </div>

    <div class="w-full overflow-x-auto pb-6 mb-2 hide-scrollbar px-4 sm:px-0">
        <div class="flex items-end gap-3 min-w-max pr-4 h-[120px]"> 
            <div 
                @click="handleAccountSelect(null)"
                class="relative cursor-pointer rounded-2xl p-4 flex flex-col justify-between transition-all duration-300 ease-out border overflow-hidden group shrink-0"
                :class="filterAccountId === null 
                  ? 'w-[180px] h-[110px] bg-slate-900/95 dark:bg-white/95 border-slate-800 dark:border-white shadow-lg' 
                  : 'w-[160px] h-[95px] bg-white/30 dark:bg-white/5 border-white/20 dark:border-white/5 opacity-60 scale-95 grayscale hover:grayscale-[50%] shadow-sm'"
            >
                <div class="flex justify-between items-start relative z-10">
                    <div class="w-7 h-7 rounded-lg flex items-center justify-center transition-colors" 
                         :class="filterAccountId === null ? 'bg-white/20 dark:bg-black/10' : 'bg-slate-200/50 dark:bg-white/10'">
                        <Layers class="w-4 h-4" :class="filterAccountId === null ? 'text-white dark:text-slate-900' : 'text-slate-500'" />
                    </div>
                </div>
                <div class="relative z-10 mt-auto">
                    <p class="text-xs font-black tracking-tight" :class="filterAccountId === null ? 'text-white dark:text-slate-900' : 'text-slate-600 dark:text-slate-300'">Todas las Cuentas</p>
                </div>
            </div>

            <MiniGlassBankCard v-for="acc in sortedAccounts" :key="acc.id" :account="acc" :is-selected="filterAccountId === acc.id" @click="handleAccountSelect(acc)" />
        </div>
    </div>

    <div class="flex-1 flex flex-col relative z-20 px-2 sm:px-0 pb-24">
        <div class="flex flex-col flex-1 space-y-4">
          <div class="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3 mb-4">
            <div class="w-full sm:w-auto flex justify-center sm:justify-start">
              <GlassMonthStepper v-model="selectedDate" />
            </div>
            <div class="w-full sm:w-64">
              <GlassSelect v-model="filterType" :options="filterOptions" placeholder="Filtrar por..." :icon="Filter" class="w-full" />
            </div>
          </div>

          <GlassCard class="p-2 sm:p-4 flex flex-col flex-1">
            <div class="flex-1"> 
              <TransactionList :transactions="paginatedTransactions" :isLoading="financeStore.isMonthlyLoading" @select="openTransactionDetail" />
            </div>

            <div v-if="filteredTransactions.length > 0 && !financeStore.isMonthlyLoading" class="mt-4 pt-4 border-t border-slate-200/50 dark:border-white/5 flex flex-col sm:flex-row items-center justify-between gap-4 px-2 sm:px-4">
              <p class="text-xs font-semibold text-slate-500 dark:text-slate-400">
                Mostrando <span class="text-slate-800 dark:text-white font-bold">{{ (currentPage - 1) * itemsPerPage + 1 }}</span> al <span class="text-slate-800 dark:text-white font-bold">{{ Math.min(currentPage * itemsPerPage, filteredTransactions.length) }}</span> de <span class="text-slate-800 dark:text-white font-bold">{{ filteredTransactions.length }}</span>
              </p>
              <div class="flex items-center gap-2">
                <button @click="prevPage" :disabled="currentPage === 1" class="p-2 rounded-xl border border-slate-200/50 bg-white dark:bg-white/5 text-slate-600 dark:text-slate-300 disabled:opacity-30 transition-all"><ChevronLeft class="w-4 h-4" /></button>
                <span class="text-xs font-bold text-slate-700 dark:text-slate-300 px-3 py-1.5 bg-slate-100/50 dark:bg-white/5 rounded-lg border border-slate-200/50">Pág {{ currentPage }} / {{ totalPages }}</span>
                <button @click="nextPage" :disabled="currentPage === totalPages" class="p-2 rounded-xl border border-slate-200/50 bg-white dark:bg-white/5 text-slate-600 dark:text-slate-300 disabled:opacity-30 transition-all"><ChevronRight class="w-4 h-4" /></button>
              </div>
            </div>
          </GlassCard>
        </div>
    </div>

    <button 
      @click="isTransactionModalOpen = true"
      class="lg:hidden fixed bottom-24 right-5 z-40 w-14 h-14 bg-slate-900 dark:bg-white text-white dark:text-slate-900 rounded-full flex items-center justify-center shadow-[0_8px_24px_rgba(0,0,0,0.15)] dark:shadow-[0_8px_24px_rgba(255,255,255,0.25)] active:scale-95 transition-all duration-300"
    >
      <Plus class="w-6 h-6" />
    </button>

    <TransactionModal :is-open="isTransactionModalOpen" @close="handleModalClose" />
    <TransactionDetailDrawer :is-open="isDetailDrawerOpen" :transaction-id="selectedTransactionId" @close="isDetailDrawerOpen = false" @updated="loadMonthData" />

  </div>
</template>

<style scoped>
.hide-scrollbar { -ms-overflow-style: none; scrollbar-width: none; }
.hide-scrollbar::-webkit-scrollbar { display: none; }
</style>