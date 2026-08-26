<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useFinanceStore } from '../stores/finance';
import { useCategoryStore } from '../stores/category';
import { useScheduledStore } from '../stores/scheduled';
import { scheduledService } from '../services/scheduledService';
import { CURRENCIES } from '../constants/currencies'; 
import { useScreen } from '../composables/useScreen';

import GlassCard from '../components/ui/GlassCard.vue';
import MetricCard from '../components/ui/MetricCard.vue';
import TransactionModal from '../components/forms/TransactionModal.vue';
import TransactionList from '../components/transactions/TransactionList.vue'; 
import TransactionDetailDrawer from '../components/forms/TransactionDetailDrawer.vue';
import PendingTrayWidget from '../components/ui/PendingTrayWidget.vue';
import ScheduleExecuteModal from '../components/forms/ScheduleExecuteModal.vue';
import GlobalAddModal from '../components/forms/GlobalAddModal.vue'; 
import ScheduleCreateModal from '../components/forms/ScheduleCreateModal.vue';
import ScheduleDetailDrawer from '../components/forms/ScheduleDetailDrawer.vue';
import MiniGlassBankCard from '../components/ui/MiniGlassBankCard.vue';

import GlassDrawer from '../components/ui/GlassDrawer.vue';
import ScheduleEditForm from '../components/forms/ScheduleEditForm.vue';

import { Loader2, TrendingUp, TrendingDown, RefreshCcw, ChevronRight, Wallet, Scale, Plus, ArrowRight } from 'lucide-vue-next';

const { isMobile } = useScreen();

const financeStore = useFinanceStore();
const categoryStore = useCategoryStore();
const scheduledStore = useScheduledStore();

const isTransactionModalOpen = ref(false);
const transactionModalInitialTab = ref<'expense' | 'income' | 'transfer'>('expense');
const isModalTabFixed = ref(false); 

const isScheduleCreateModalOpen = ref(false);
const scheduleCreateFrequency = ref('monthly'); 
const isDetailDrawerOpen = ref(false);
const selectedTransactionId = ref<string | null>(null);

const isGlobalAddModalOpen = ref(false); 

const isScheduleDrawerOpen = ref(false);
const selectedScheduleData = ref<any>(null);

const isExecuteModalOpen = ref(false);
const scheduleToExecute = ref<any>(null);

const isDirectEditModalOpen = ref(false);
const isSavingDirectEdit = ref(false);
const directEditApiError = ref('');

const handleCardClick = (type: 'expense' | 'income' | 'transfer' = 'expense') => {
  transactionModalInitialTab.value = type;
  isModalTabFixed.value = true; 
  isGlobalAddModalOpen.value = true;
};

const handleMainAddClick = () => {
  transactionModalInitialTab.value = 'expense';
  isModalTabFixed.value = false; 
  isGlobalAddModalOpen.value = true;
};

const openTransactionModalWithTab = (tab: 'expense' | 'income' | 'transfer') => {
  transactionModalInitialTab.value = tab;
  isTransactionModalOpen.value = true;
};

onMounted(() => {
  financeStore.fetchBalance();
  financeStore.fetchAccounts();
  financeStore.fetchRecentTransactions();
  categoryStore.fetchCategories();
  scheduledStore.fetchPendingTray();
});

const handleRefresh = async () => {
  await Promise.all([
    financeStore.refreshAllData(),
    scheduledStore.fetchPendingTray(),
    scheduledStore.fetchActiveSchedules()
  ]);
};

const formatCurrency = (val: number, currencyCode: string = 'CRC') => {
  const c = CURRENCIES.find(x => x.code === currencyCode);
  const symbol = c ? c.symbol : '$';
  const isNegative = val < 0; 
  
  const num = new Intl.NumberFormat('es-CR', { minimumFractionDigits: 2 }).format(Math.abs(val));
  
  return isNegative ? `-${symbol}${num}` : `${symbol}${num}`;
};

const handleOpenScheduleModal = (freq: string, initialTab: 'expense' | 'income' | 'transfer' = 'expense') => {
    scheduleCreateFrequency.value = freq;
    transactionModalInitialTab.value = initialTab;
    isScheduleCreateModalOpen.value = true;
};

const openTransactionDetail = (id: string) => {
  selectedTransactionId.value = id;
  isDetailDrawerOpen.value = true;
};

const handleExecuteClick = (sched: any) => {
    scheduleToExecute.value = sched;
    isExecuteModalOpen.value = true;
};

const handleRescheduleClick = (sched: any) => {
    selectedScheduleData.value = sched;
    isScheduleDrawerOpen.value = true;
};

const handleSkipClick = async (sched: any) => {
    try {
        await scheduledService.skipScheduled(sched.id);
        await handleRefresh();
    } catch (e: any) {
        alert("Error al intentar saltar el ciclo de facturación.");
    }
};

const handleDeleteClick = async (sched: any) => {
    if (!confirm(`¿Estás seguro de eliminar permanentemente la programación: ${sched.name}?`)) return;

    try {
        await scheduledService.deleteScheduled(sched.id);
        await handleRefresh();
    } catch (e: any) {
        alert("Error al intentar eliminar la programación.");
    }
};

const handleOpenEditorDirectly = (sched: any) => {
  selectedScheduleData.value = sched;
  isDirectEditModalOpen.value = true;
};

const handleDirectEditSave = async (updateData: any) => {
  if (!selectedScheduleData.value) return;
  isSavingDirectEdit.value = true;
  directEditApiError.value = '';
  
  try {
    await scheduledService.updateScheduled(selectedScheduleData.value.id, updateData);
    await handleRefresh();
    isDirectEditModalOpen.value = false;
  } catch (e: any) {
    directEditApiError.value = e.response?.data?.detail || "Error al actualizar la programación.";
  } finally {
    isSavingDirectEdit.value = false;
  }
};
</script>

<template>
  <div class="max-w-5xl mx-auto space-y-6 sm:space-y-8 pb-10 px-1 relative">
    
    <div class="flex justify-between items-end relative z-20 mb-6 px-2 sm:px-0">
      <div>
        <h3 class="text-2xl font-extrabold text-slate-900 dark:text-white tracking-tight leading-none">Resumen General</h3>
        <p class="text-xs font-semibold text-slate-500 dark:text-slate-400 mt-1.5">Tu panorama financiero hoy</p>
      </div>
      
      <div class="flex items-center gap-2 sm:gap-3">
        <button 
          @click="handleRefresh" 
          class="text-slate-400 hover:text-slate-800 dark:text-slate-500 dark:hover:text-white bg-slate-100 dark:bg-white/5 hover:bg-slate-200 dark:hover:bg-white/10 p-2.5 rounded-full transition-all duration-300"
          title="Sincronizar datos"
        >
          <RefreshCcw class="w-4 h-4" :class="{ 'animate-spin text-slate-900 dark:text-white': financeStore.isLoading || scheduledStore.isLoading }" />
        </button>

        <button 
          @click="handleMainAddClick"
          class="hidden lg:flex items-center gap-1.5 sm:gap-2 bg-slate-900 dark:bg-white text-white dark:text-slate-900 px-3 py-2 sm:px-4 sm:py-2.5 rounded-xl font-bold text-xs sm:text-sm hover:opacity-90 transition-opacity shadow-sm"
        >
          <Plus class="w-4 h-4" />
          <span>Agregar</span>
        </button>
      </div>
    </div>

    <div v-if="financeStore.isLoading && !financeStore.balance" class="flex justify-center items-center h-48">
      <Loader2 class="w-10 h-10 text-slate-800 dark:text-white animate-spin opacity-40" />
    </div>

    <div v-else-if="financeStore.balance" class="grid grid-cols-2 gap-3 sm:gap-4">
      
      <!-- Mobile: Ingresos, Gastos, Balance (como diquis-mobile) -->
      <template v-if="isMobile">
        <div class="col-span-1">
          <MetricCard 
            title="Ingresos"
            :amount="formatCurrency(financeStore.balance.metrics.monthly_income, financeStore.balance.currency)"
            :icon="TrendingUp"
            trend="up"
          />
        </div>

        <div class="col-span-1">
          <MetricCard 
            title="Gastos"
            :amount="formatCurrency(financeStore.balance.metrics.monthly_expense, financeStore.balance.currency)"
            :icon="TrendingDown"
            trend="down"
            class="[&_svg]:text-rose-500" 
          />
        </div>

        <div class="col-span-2">
          <MetricCard 
            title="Balance Total"
            :amount="formatCurrency(financeStore.balance.current_balance, financeStore.balance.currency)"
            :subtitle="financeStore.balance.wallet_name"
            :icon="Scale"
            trend="neutral"
          />
        </div>
      </template>

      <!-- Desktop: Balance, Ingresos, Gastos (clickeables) -->
      <template v-else>
        <div @click="handleCardClick('transfer')" class="col-span-2 cursor-pointer transition-transform hover:scale-[1.02] active:scale-[0.98]">
          <MetricCard 
            title="Balance Total"
            :amount="formatCurrency(financeStore.balance.current_balance, financeStore.balance.currency)"
            :subtitle="financeStore.balance.wallet_name"
            :icon="Wallet"
            trend="neutral"
          />
        </div>

        <div @click="handleCardClick('income')" class="col-span-1 cursor-pointer transition-transform hover:scale-[1.02] active:scale-[0.98]">
          <MetricCard 
            title="Ingresos"
            :amount="formatCurrency(financeStore.balance.metrics.monthly_income, financeStore.balance.currency)"
            :icon="TrendingUp"
            trend="up"
          />
        </div>

        <div @click="handleCardClick('expense')" class="col-span-1 cursor-pointer transition-transform hover:scale-[1.02] active:scale-[0.98]">
          <MetricCard 
            title="Gastos"
            :amount="formatCurrency(financeStore.balance.metrics.monthly_expense, financeStore.balance.currency)"
            :icon="TrendingDown"
            trend="down"
          />
        </div>
      </template>
    </div>

    <!-- Billeteras Carousel (solo mobile, como diquis-mobile) -->
    <div v-if="isMobile && financeStore.accounts && financeStore.accounts.length > 0" class="mt-8 mb-4">
      <div class="flex justify-between items-center mb-3 px-2 sm:px-0">
        <h3 class="text-[11px] font-bold text-slate-500 dark:text-slate-400 uppercase tracking-widest leading-none">Mis Billeteras</h3>
        
        <router-link to="/cuentas" class="text-[10px] font-bold text-slate-700 dark:text-slate-300 hover:text-slate-950 dark:hover:text-white flex items-center gap-1 bg-slate-100 dark:bg-white/5 hover:bg-slate-200 dark:hover:bg-white/10 px-3 py-1.5 rounded-full transition-colors duration-300">
          Gestionar Billeteras
        </router-link>
      </div>

      <div class="flex items-center overflow-x-auto gap-3 pb-3 pt-1 snap-x snap-mandatory custom-scrollbar-hide px-2 sm:px-0">
        <MiniGlassBankCard
          v-for="account in financeStore.accounts.slice(0, 5)"
          :key="account.id"
          :account="account"
          :is-selected="true"
          class="snap-start"
        />

        <router-link 
          v-if="financeStore.accounts.length > 5"
          to="/cuentas"
          class="snap-start shrink-0 flex items-center justify-center w-12 h-12 rounded-full bg-slate-100 dark:bg-white/5 border border-slate-200 dark:border-white/10 hover:bg-slate-200 dark:hover:bg-white/10 active:scale-95 transition-all ml-1 shadow-sm"
        >
          <ArrowRight class="w-5 h-5 text-slate-500 dark:text-slate-400" />
        </router-link>
      </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-2 gap-4 sm:gap-6 relative z-10 pb-8" :class="isMobile ? 'mt-4' : ''">
        
        <PendingTrayWidget 
            @execute="handleExecuteClick"
            @reschedule="handleRescheduleClick"
            @skip="handleSkipClick"
            @delete="handleDeleteClick"
        />

        <GlassCard class="p-5 flex flex-col">
          <div class="flex justify-between items-center mb-5 shrink-0">
            <h3 class="text-[11px] font-bold text-slate-500 dark:text-slate-400 uppercase tracking-widest leading-none">Movimientos Recientes</h3>
        
            <router-link to="/historial" class="text-[10px] font-bold text-slate-700 dark:text-slate-300 hover:text-slate-950 dark:hover:text-white flex items-center gap-1 bg-slate-100 dark:bg-white/5 hover:bg-slate-200 dark:hover:bg-white/10 px-3 py-1.5 rounded-full transition-colors duration-300">
              Ver todos <ChevronRight class="w-3 h-3 opacity-70" />
            </router-link>
          </div>
      
          <div class="flex-1">
              <TransactionList 
                :transactions="financeStore.recentTransactions.slice(0, 5)" 
                :is-loading="financeStore.isLoading" 
                @select="openTransactionDetail"
              />
          </div>
        </GlassCard>
    </div>

    <button 
      @click="handleMainAddClick"
      class="lg:hidden fixed bottom-24 right-5 z-40 w-14 h-14 bg-slate-900 dark:bg-white text-white dark:text-slate-900 rounded-full flex items-center justify-center shadow-[0_8px_24px_rgba(0,0,0,0.15)] dark:shadow-[0_8px_24px_rgba(255,255,255,0.25)] hover:scale-105 active:scale-95 transition-all duration-300 group"
    >
      <Plus class="w-6 h-6 transition-transform duration-300 group-hover:rotate-90" />
    </button>

    <TransactionModal 
      :is-open="isTransactionModalOpen" 
      :default-tab="transactionModalInitialTab"
      :hide-tabs="isModalTabFixed"
      @close="isTransactionModalOpen = false" 
    />

    <ScheduleCreateModal
      :is-open="isScheduleCreateModalOpen"
      :default-frequency="scheduleCreateFrequency"
      :default-tab="transactionModalInitialTab" 
      :hide-tabs="isModalTabFixed"
      @close="isScheduleCreateModalOpen = false"
      @refresh="handleRefresh"
    />

    <TransactionDetailDrawer 
      :is-open="isDetailDrawerOpen"
      :transaction-id="selectedTransactionId"
      @close="isDetailDrawerOpen = false"
      @updated="handleRefresh" 
    />

    <ScheduleExecuteModal 
      :is-open="isExecuteModalOpen"
      :schedule-to-execute="scheduleToExecute"
      @close="isExecuteModalOpen = false"
      @refresh="handleRefresh"
      @edit="handleOpenEditorDirectly" 
    />

    <ScheduleDetailDrawer 
      :is-open="isScheduleDrawerOpen"
      :schedule-id="selectedScheduleData?.id"
      :schedule-data="selectedScheduleData"
      @close="isScheduleDrawerOpen = false"
      @updated="handleRefresh"
    />

    <GlobalAddModal 
      :is-open="isGlobalAddModalOpen"
      context="all" 
      :initial-tab="transactionModalInitialTab"
      @close="isGlobalAddModalOpen = false"
      @select-transaction="openTransactionModalWithTab"
      @select-schedule="handleOpenScheduleModal"
    />
    
    <GlassDrawer 
      :is-open="isDirectEditModalOpen" 
      title="Editar Programación" 
      @close="isDirectEditModalOpen = false" 
    >
      <ScheduleEditForm 
        v-if="selectedScheduleData"
        :schedule="selectedScheduleData"
        :is-saving="isSavingDirectEdit"
        :api-error="directEditApiError"
        @save="handleDirectEditSave"
        @cancel="isDirectEditModalOpen = false"
        @clear-error="directEditApiError = ''"
      />
    </GlassDrawer>

  </div>
</template>

<style scoped>
.custom-scrollbar-hide::-webkit-scrollbar {
  display: none;
}
.custom-scrollbar-hide {
  -ms-overflow-style: none;
  scrollbar-width: none;
}
</style>