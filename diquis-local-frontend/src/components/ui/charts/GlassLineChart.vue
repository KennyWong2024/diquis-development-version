<script setup lang="ts">
import { computed } from 'vue';
import {
  Chart as ChartJS, CategoryScale, LinearScale, PointElement,
  LineElement, Title, Tooltip, Filler
} from 'chart.js';
import { Line } from 'vue-chartjs';
import { CURRENCIES } from '../../../constants/currencies';

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Filler);

const props = defineProps<{
  labels: string[];
  data: number[];
  isFutureMap?: boolean[];
  currency?: string;
}>();

const formatCurrency = (val: number, currencyCode: string = 'CRC') => {
  const c = CURRENCIES.find(x => x.code === currencyCode);
  const symbol = c ? c.symbol : '$';
  const isNegative = val < 0;
  const num = new Intl.NumberFormat('es-CR', { minimumFractionDigits: 0 }).format(Math.abs(val));
  return isNegative ? `-${symbol}${num}` : `${symbol}${num}`;
};

const chartDataConfig = computed(() => ({
  labels: props.labels,
  datasets: [{
    label: 'Saldo Unificado',
    data: props.data,
    borderWidth: 3,
    pointRadius: 0,
    pointHoverRadius: 6,
    pointBackgroundColor: '#fff',
    fill: true,
    
    backgroundColor: (context: any) => {
      const chart = context.chart;
      const { ctx, chartArea, scales } = chart;
      if (!chartArea || !scales.y) return null;
      
      const yZero = scales.y.getPixelForValue(0);
      const gradient = ctx.createLinearGradient(0, chartArea.top, 0, chartArea.bottom);
      
      if (yZero > chartArea.bottom) {
        gradient.addColorStop(0, 'rgba(16, 185, 129, 0.2)'); 
        gradient.addColorStop(1, 'rgba(0, 0, 0, 0)');
      } 
      else if (yZero < chartArea.top) {
        gradient.addColorStop(0, 'rgba(244, 63, 94, 0.2)'); 
        gradient.addColorStop(1, 'rgba(0, 0, 0, 0)');
      } 
      else {
        const zeroRatio = (yZero - chartArea.top) / (chartArea.bottom - chartArea.top);
        gradient.addColorStop(0, 'rgba(16, 185, 129, 0.2)'); 
        gradient.addColorStop(Math.max(0, zeroRatio - 0.01), 'rgba(16, 185, 129, 0)'); 
        gradient.addColorStop(Math.min(1, zeroRatio + 0.01), 'rgba(244, 63, 94, 0)');
        gradient.addColorStop(1, 'rgba(244, 63, 94, 0.2)'); 
      }
      
      return gradient;
    },
    tension: 0.3,
    
    segment: {
      borderColor: (ctx: any) => {
        const dataIndex = ctx.p1DataIndex;
        const p1Data = ctx.p1.parsed.y;
        const color = p1Data >= 0 ? '#10b981' : '#f43f5e'; 
        
        if (props.isFutureMap && props.isFutureMap[dataIndex]) {
          return p1Data >= 0 ? 'rgba(16, 185, 129, 0.5)' : 'rgba(244, 63, 94, 0.5)';
        }
        
        return color;
      },
      borderDash: (ctx: any) => {
        const dataIndex = ctx.p1DataIndex;
        if (props.isFutureMap && props.isFutureMap[dataIndex]) {
          return [5, 5];
        }
        return undefined;
      }
    }
  }]
}));

const chartOptionsConfig = computed(() => ({
  responsive: true,
  maintainAspectRatio: false,
  interaction: { intersect: false, mode: 'index' as const },
  plugins: {
    legend: { display: false },
    tooltip: {
      backgroundColor: 'rgba(15, 23, 42, 0.9)',
      titleColor: '#94a3b8',
      bodyColor: '#fff',
      padding: 12,
      cornerRadius: 12,
      callbacks: {
        label: (context: any) => {
          return formatCurrency(context.raw, props.currency || 'CRC');
        }
      }
    }
  },
  scales: {
    x: { grid: { display: false }, ticks: { color: '#64748b', maxTicksLimit: 7 } },
    y: { display: false }
  }
}));
</script>

<template>
  <div class="w-full h-full relative">
    <Line :data="chartDataConfig" :options="chartOptionsConfig" />
  </div>
</template>