<script setup lang="ts">
import { ref, onMounted, watch } from 'vue';
import { useAnalyticsStore } from '../stores/analytics';
import GlassMonthStepper from '../components/ui/GlassMonthStepper.vue';
import UnifiedCashflowChart from '../components/analytics/UnifiedCashflowChart.vue';
import TrendMetricsStrip from '../components/transactions/TrendMetricsStrip.vue';
import { RefreshCcw } from 'lucide-vue-next';

const analyticsStore = useAnalyticsStore();
const selectedDate = ref(new Date());

const fetchAnalyticsForMonth = async (date: Date) => {
  const year = date.getFullYear();
  const month = date.getMonth();
  
  const startStr = `${year}-${String(month + 1).padStart(2, '0')}-01`;
  const lastDay = new Date(year, month + 1, 0).getDate();
  const endStr = `${year}-${String(month + 1).padStart(2, '0')}-${String(lastDay).padStart(2, '0')}`;
  
  await analyticsStore.fetchCashflow(startStr, endStr);
};

onMounted(() => {
  fetchAnalyticsForMonth(selectedDate.value);
});

watch(selectedDate, (newDate) => {
  fetchAnalyticsForMonth(newDate);
});
</script>

<template>
  <div class="max-w-5xl mx-auto space-y-6 sm:space-y-8 pb-10 px-1 relative">
    
    <div class="flex justify-between items-end relative z-20 mb-6 px-4 sm:px-0">
      <div>
        <h3 class="text-2xl font-extrabold text-slate-900 dark:text-white tracking-tight leading-none">Informes</h3>
        <p class="text-xs font-semibold text-slate-500 dark:text-slate-400 mt-1.5">Análisis y proyecciones de tus finanzas</p>
      </div>
      
      <div class="flex items-center gap-2 sm:gap-3">
        <button 
          @click="fetchAnalyticsForMonth(selectedDate)" 
          class="text-slate-400 hover:text-slate-800 dark:text-slate-500 dark:hover:text-white bg-slate-100 dark:bg-white/5 p-2.5 rounded-full transition-all duration-300 shadow-sm"
          title="Sincronizar datos"
        >
          <RefreshCcw class="w-4 h-4" :class="{ 'animate-spin text-slate-900 dark:text-white': analyticsStore.isLoading }" />
        </button>
      </div>
    </div>

    <div class="w-full space-y-6 bg-white/30 dark:bg-black/10 p-4 sm:p-6 rounded-2xl sm:rounded-[2.5rem] border border-slate-200/50 dark:border-white/5 shadow-sm">
      
      <div class="flex justify-center sm:justify-start items-center mb-6">
        <GlassMonthStepper v-model="selectedDate" />
      </div>

      <div class="space-y-6 animate-in fade-in duration-500">
        <TrendMetricsStrip />
        <UnifiedCashflowChart />
      </div>

    </div>

  </div>
</template>

<style scoped>
.hide-scrollbar {
  -ms-overflow-style: none;
  scrollbar-width: none;
}
.hide-scrollbar::-webkit-scrollbar {
  display: none;
}
</style>