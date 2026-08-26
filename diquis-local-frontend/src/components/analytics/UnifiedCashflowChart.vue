<script setup lang="ts">
import { computed } from 'vue';
import { useAnalyticsStore } from '../../stores/analytics';
import GlassLineChart from '../ui/charts/GlassLineChart.vue';

const analyticsStore = useAnalyticsStore();

const chartLabels = computed(() => {
  if (!analyticsStore.cashflowReport) return [];
  return analyticsStore.cashflowReport.timeline.map(day => {
    const dateString = String(day.date).split('T')[0];
    const [year, month, d] = dateString.split('-');
    const localDate = new Date(Number(year), Number(month) - 1, Number(d));
    return new Intl.DateTimeFormat('es-CR', { day: '2-digit', month: 'short' }).format(localDate);
  });
});

const chartData = computed(() => {
  if (!analyticsStore.cashflowReport) return [];
  return analyticsStore.cashflowReport.timeline.map(day => day.balance);
});

const chartIsFuture = computed(() => {
  if (!analyticsStore.cashflowReport) return [];
  return analyticsStore.cashflowReport.timeline.map(day => day.is_future);
});
</script>

<template>
  <div class="relative w-full h-[280px] sm:h-[350px] mt-4 sm:mt-6 p-3 sm:p-6 bg-white/40 dark:bg-[#111]/40 backdrop-blur-2xl border border-slate-200/50 dark:border-white/5 rounded-2xl sm:rounded-[2.5rem] shadow-xl overflow-hidden">
    
    <div class="absolute top-3 sm:top-6 left-4 sm:left-8 z-10 flex gap-4">
      <div>
        <h4 class="text-[9px] sm:text-[10px] font-bold uppercase tracking-[0.2em] text-slate-400">Trayectoria de Capital</h4>
        <div class="flex items-center gap-2 mt-0.5 sm:mt-1">
          <span class="text-xl sm:text-2xl font-black text-slate-800 dark:text-white leading-none">Comportamiento</span>
        </div>
      </div>
      <div class="flex flex-col justify-end pb-1 hidden xs:block"> 
        <div class="flex items-center gap-2 text-[8px] sm:text-[9px] font-bold uppercase text-slate-500">
          <span class="w-3 h-0.5 sm:w-4 bg-slate-400"></span> Realidad
          <span class="w-3 sm:w-4 border-t-2 border-dashed border-slate-400 ml-1 sm:ml-2"></span> Proyección
        </div>
      </div>
    </div>

    <div v-if="analyticsStore.isLoading" class="w-full h-full flex items-center justify-center">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-slate-900 dark:border-white opacity-50"></div>
    </div>

    <div v-else-if="analyticsStore.cashflowReport && chartData.length > 0" class="w-full h-full pt-16 sm:pt-20">
      <GlassLineChart 
        :labels="chartLabels" 
        :data="chartData" 
        :is-future-map="chartIsFuture" 
        :currency="analyticsStore.cashflowReport.currency"
      />
    </div>

    <div v-else class="w-full h-full flex items-center justify-center text-slate-400 p-4 text-center">
      <p class="text-xs sm:text-sm font-bold">Selecciona un mes para analizar o crea movimientos programados.</p>
    </div>
    
  </div>
</template>