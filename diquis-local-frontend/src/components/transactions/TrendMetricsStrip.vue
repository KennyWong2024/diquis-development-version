<script setup lang="ts">
import { computed } from 'vue';
import { useAnalyticsStore } from '../../stores/analytics';
import { TrendingUp, TrendingDown, Target } from 'lucide-vue-next';
import { CURRENCIES } from '../../constants/currencies';

const analyticsStore = useAnalyticsStore();

const metrics = computed(() => {
  if (!analyticsStore.cashflowReport) return null;

  let rIncome = 0, rExpense = 0, pIncome = 0, pExpense = 0;
  
  analyticsStore.cashflowReport.timeline.forEach(day => {
    rIncome += day.real_income;
    rExpense += day.real_expense;
    pIncome += day.projected_income;
    pExpense += day.projected_expense;
  });

  const totalIncome = rIncome + pIncome;
  const totalExpense = rExpense + pExpense;

  return {
    income: totalIncome,
    expense: totalExpense,
    isEstimated: pIncome > rIncome || pExpense > rExpense
  };
});

const currency = computed(() => analyticsStore.cashflowReport?.currency || 'CRC');

const formatCurrency = (val: number, currencyCode: string = 'CRC') => {
  const c = CURRENCIES.find(x => x.code === currencyCode);
  const symbol = c ? c.symbol : '$';
  const isNegative = val < 0;
  const num = new Intl.NumberFormat('es-CR', { minimumFractionDigits: 0, maximumFractionDigits: 0 }).format(Math.abs(val));
  return isNegative ? `-${symbol}${num}` : `${symbol}${num}`;
};
</script>

<template>
  <div v-if="metrics" class="grid grid-cols-1 sm:grid-cols-3 gap-4">
    
    <div class="bg-white/50 dark:bg-white/5 backdrop-blur-xl border border-slate-200/50 dark:border-white/5 p-4 rounded-2xl shadow-sm">
      <div class="flex justify-between items-start mb-2">
        <p class="text-[10px] font-bold uppercase tracking-wider text-slate-500">Ingresos</p>
        <TrendingUp class="w-4 h-4 text-emerald-500" />
      </div>
      <h4 class="text-xl font-black text-slate-800 dark:text-white">{{ formatCurrency(metrics.income, currency) }}</h4>
      <p class="text-[9px] text-slate-400 mt-1 uppercase">{{ metrics.isEstimated ? 'Incluye Proyecciones' : 'Total Real' }}</p>
    </div>

    <div class="bg-white/50 dark:bg-white/5 backdrop-blur-xl border border-slate-200/50 dark:border-white/5 p-4 rounded-2xl shadow-sm">
      <div class="flex justify-between items-start mb-2">
        <p class="text-[10px] font-bold uppercase tracking-wider text-slate-500">Gastos</p>
        <TrendingDown class="w-4 h-4 text-rose-500" />
      </div>
      <h4 class="text-xl font-black text-slate-800 dark:text-white">{{ formatCurrency(metrics.expense, currency) }}</h4>
      <p class="text-[9px] text-slate-400 mt-1 uppercase">{{ metrics.isEstimated ? 'Incluye Proyecciones' : 'Total Real' }}</p>
    </div>

    <div class="relative overflow-hidden bg-white/50 dark:bg-white/5 backdrop-blur-xl border border-slate-200/50 dark:border-white/5 p-4 rounded-2xl shadow-sm">
      
      <div class="absolute inset-0 bg-gradient-to-tr from-slate-100 to-transparent dark:from-white/5 dark:to-transparent opacity-40 pointer-events-none"></div>
      
      <div class="relative z-10 flex justify-between items-start mb-2">
        <p class="text-[10px] font-bold uppercase tracking-wider text-slate-500">Cierre Proyectado</p>
        <Target class="w-4 h-4 text-slate-400 dark:text-slate-500" />
      </div>
      
      <h4 class="relative z-10 text-xl font-black" :class="(analyticsStore.cashflowReport?.ending_balance ?? 0) >= 0 ? 'text-slate-800 dark:text-white' : 'text-rose-600 dark:text-rose-400'">
        {{ formatCurrency(analyticsStore.cashflowReport?.ending_balance ?? 0, currency) }}
      </h4>
      
      <p class="relative z-10 text-[9px] text-slate-400 mt-1 uppercase">Balance a fin de mes</p>
    </div>

  </div>
</template>