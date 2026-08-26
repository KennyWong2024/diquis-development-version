<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue';
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from 'chart.js';
import { Doughnut } from 'vue-chartjs';
import { CURRENCIES } from '../../../constants/currencies';

ChartJS.register(ArcElement, Tooltip, Legend);

const props = defineProps<{
  labels: string[];
  data: number[];
  colors: string[];
  title?: string;
  currency?: string;
}>();

const isDark = ref(false);
let observer: MutationObserver | null = null;

onMounted(() => {
  isDark.value = document.documentElement.classList.contains('dark');
  observer = new MutationObserver(() => {
    isDark.value = document.documentElement.classList.contains('dark');
  });
  observer.observe(document.documentElement, { attributes: true, attributeFilter: ['class'] });
});

onUnmounted(() => {
  if (observer) observer.disconnect();
});

const formatCurrency = (val: number, currencyCode: string = 'CRC') => {
  const c = CURRENCIES.find(x => x.code === currencyCode);
  const symbol = c ? c.symbol : '$';
  const isNegative = val < 0;
  const num = new Intl.NumberFormat('es-CR', { minimumFractionDigits: 0 }).format(Math.abs(val));
  return isNegative ? `-${symbol}${num}` : `${symbol}${num}`;
};

const chartData = computed(() => ({
  labels: props.labels,
  datasets: [
    {
      data: props.data,
      backgroundColor: props.colors,
      borderWidth: isDark.value ? 4 : 3,
      borderColor: isDark.value ? '#050505' : '#fbfbfb', 
      hoverOffset: 4,
      borderRadius: 2
    }
  ]
}));

const chartOptions = computed(() => ({
  responsive: true,
  maintainAspectRatio: false,
  cutout: '82%',
  plugins: {
    legend: { display: false },
    tooltip: {
      backgroundColor: isDark.value ? 'rgba(17, 17, 17, 0.95)' : 'rgba(255,255,255,0.95)',
      titleColor: isDark.value ? '#ffffff' : '#0f172a',
      bodyColor: isDark.value ? '#94a3b8' : '#475569',
      borderColor: isDark.value ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.05)',
      borderWidth: 1,
      padding: 12,
      displayColors: true,
      boxPadding: 6,
      usePointStyle: true,
      callbacks: {
        label: function(context: any) {
          let label = context.label || '';
          if (label) label += ': ';
          if (context.parsed !== null) {
            label += formatCurrency(context.parsed, props.currency || 'CRC');
          }
          return label;
        }
      }
    }
  }
}));

const totalSum = computed(() => props.data.reduce((a, b) => a + b, 0));
</script>

<template>
  <div class="relative w-full h-full min-h-[260px] flex items-center justify-center">
    
    <div class="absolute inset-0 z-10 p-2">
      <Doughnut v-if="data.length > 0" :data="chartData" :options="chartOptions" />
    </div>

    <div v-if="data.length > 0" class="absolute inset-0 flex flex-col items-center justify-center z-0 pointer-events-none mt-1">
      <p v-if="title" class="text-[9px] font-black text-slate-400 dark:text-slate-500 uppercase tracking-[0.2em] mb-1">
        {{ title }}
      </p>
      <p class="text-2xl sm:text-3xl font-black text-slate-900 dark:text-white tracking-tighter">
        {{ formatCurrency(totalSum, props.currency || 'CRC') }}
      </p>
    </div>

    <div v-if="data.length === 0" class="flex flex-col items-center justify-center text-slate-400 dark:text-slate-600">
      <div class="w-40 h-40 rounded-full border-[6px] border-dashed border-slate-200 dark:border-white/5 flex items-center justify-center mb-3">
        <span class="text-xs font-bold uppercase tracking-widest opacity-40">Sin Gastos</span>
      </div>
    </div>

  </div>
</template>