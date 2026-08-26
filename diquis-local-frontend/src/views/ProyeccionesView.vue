<script setup lang="ts">
import { ref } from 'vue';
import { useScheduledStore } from '../stores/scheduled';
import ProjectionsTab from '../components/transactions/ProjectionsTab.vue';
import GlobalAddModal from '../components/forms/GlobalAddModal.vue'; 
import ScheduleCreateModal from '../components/forms/ScheduleCreateModal.vue';
import TransactionModal from '../components/forms/TransactionModal.vue'; 
import GlassSelect from '../components/ui/GlassSelect.vue';
import { RefreshCcw, Plus, Filter, ArrowDownUp } from 'lucide-vue-next'; 

const scheduledStore = useScheduledStore();

const isGlobalAddModalOpen = ref(false); 
const isScheduleCreateModalOpen = ref(false);
const scheduleCreateFrequency = ref('monthly'); 
const filterType = ref('all');

const filterOptions = [
  { id: 'all', name: 'Todos los programados', icon: ArrowDownUp },
  { id: 'income', name: 'Solo Ingresos', icon: ArrowDownUp },
  { id: 'expense', name: 'Solo Gastos', icon: ArrowDownUp },
];

const handleOpenScheduleModal = (freq: string) => {
    scheduleCreateFrequency.value = freq;
    isScheduleCreateModalOpen.value = true;
};

const isTransactionModalOpen = ref(false);

const handleManualRefresh = async () => {
  await scheduledStore.refreshAll();
};
</script>

<template>
  <div class="max-w-5xl mx-auto flex flex-col min-h-[calc(100vh-8rem)] relative px-2 sm:px-0">
    
    <div class="flex justify-between items-end relative z-50 mb-6 sm:mb-8">
      <div>
        <h3 class="text-2xl font-extrabold text-slate-900 dark:text-white tracking-tight leading-none">Planificación</h3>
        <p class="text-xs font-semibold text-slate-500 dark:text-slate-400 mt-1.5">Organiza tus ingresos y gastos futuros</p>
      </div>
      
      <div class="flex items-center gap-2 sm:gap-3">
        <button 
          @click="handleManualRefresh" 
          class="text-slate-400 hover:text-slate-800 dark:text-slate-500 dark:hover:text-white bg-slate-100 dark:bg-white/5 p-2.5 rounded-full transition-all duration-300 shadow-sm"
        >
          <RefreshCcw class="w-4 h-4" :class="{ 'animate-spin text-slate-900 dark:text-white': scheduledStore.isLoading }" />
        </button>

        <button 
          @click="isGlobalAddModalOpen = true"
          class="hidden lg:flex items-center gap-2 bg-slate-900 dark:bg-white text-white dark:text-slate-900 px-4 py-2.5 rounded-xl font-bold text-sm hover:opacity-90 transition-opacity shadow-sm"
        >
          <Plus class="w-4 h-4" />
          <span>Agregar</span>
        </button>
      </div>
    </div>

    <div class="flex justify-end mb-6 relative z-40 px-2 sm:px-0">
      <div class="w-full sm:w-64">
        <GlassSelect 
          v-model="filterType" 
          :options="filterOptions" 
          placeholder="Filtrar por..." 
          :icon="Filter"
          class="w-full"
        />
      </div>
    </div>

    <div class="flex-1 flex flex-col relative z-20 pb-24">
        <div class="flex flex-col flex-1 animate-in fade-in slide-in-from-bottom-4 duration-500">
          <ProjectionsTab v-model:filter-type="filterType" />
        </div>
    </div>

    <button 
      @click="isGlobalAddModalOpen = true"
      class="lg:hidden fixed bottom-24 right-5 z-40 w-14 h-14 bg-slate-900 dark:bg-white text-white dark:text-slate-900 rounded-full flex items-center justify-center shadow-[0_8px_24px_rgba(0,0,0,0.15)] dark:shadow-[0_8px_24px_rgba(255,255,255,0.25)] active:scale-95 transition-all duration-300"
    >
      <Plus class="w-6 h-6" />
    </button>

    <ScheduleCreateModal
      :is-open="isScheduleCreateModalOpen"
      :default-frequency="scheduleCreateFrequency"
      @close="isScheduleCreateModalOpen = false"
      @refresh="handleManualRefresh"
    />

    <TransactionModal 
      :is-open="isTransactionModalOpen" 
      @close="isTransactionModalOpen = false" 
    />

    <GlobalAddModal 
      :is-open="isGlobalAddModalOpen"
      context="planning" 
      @close="isGlobalAddModalOpen = false"
      @select-transaction="isTransactionModalOpen = true" 
      @select-schedule="handleOpenScheduleModal"
    />

  </div>
</template>