<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue';
import { useFinanceStore } from '../../stores/finance';
import { useCategoryStore } from '../../stores/category';
import type { Category } from '../../types/category';
import GlassMonthStepper from '../ui/GlassMonthStepper.vue';
import GlassDonutChart from '../ui/charts/GlassDonutChart.vue';
import GlassTopCategories from '../ui/GlassTopCategories.vue';
import { Loader2 } from 'lucide-vue-next';

const financeStore = useFinanceStore();
const categoryStore = useCategoryStore();
const selectedDate = ref(new Date());

const colorPalette = [
  '#6366f1', '#d946ef', '#14b8a6', '#f59e0b', '#8b5cf6', 
  '#0ea5e9', '#f43f5e', '#10b981', '#64748b', '#84cc16' 
];

const loadMonthlyData = async () => {
  const y = selectedDate.value.getFullYear();
  const m = selectedDate.value.getMonth();
  const startDate = new Date(y, m, 1).toISOString();
  const endDate = new Date(y, m + 1, 0, 23, 59, 59).toISOString();
  
  await financeStore.fetchMonthlyTransactions(startDate, endDate);
};

onMounted(() => {
  loadMonthlyData();
});

watch(selectedDate, () => {
  loadMonthlyData();
});

const analyticsData = computed(() => {
  if (!financeStore.monthlyTransactions) return { stats: [], total: 0 };

  const expenses = financeStore.monthlyTransactions.filter(tx => tx.type === 'expense' && !tx.is_deleted);
  
  const grouped: Record<string, number> = {};
  let totalExpenses = 0;

  expenses.forEach(tx => {
    const catId = tx.category_id || 'uncategorized';
    const effectiveAmount = Number(tx.amount_in_account_currency) || Number(tx.amount);
    grouped[catId] = (grouped[catId] || 0) + effectiveAmount;
    totalExpenses += effectiveAmount;
  });

  const sortedStats = Object.keys(grouped)
    .map((catId, index) => {
      const category = categoryStore.categories.find((c: Category) => c.id === catId);
      const amount = grouped[catId];
      return {
        id: catId,
        name: category ? category.name : 'Sin Categoría',
        iconName: category ? category.icon : null,
        amount: amount,
        percentage: totalExpenses > 0 ? (amount / totalExpenses) * 100 : 0,
        color: colorPalette[index % colorPalette.length] 
      };
    })
    .sort((a, b) => b.amount - a.amount);

  return { stats: sortedStats, total: totalExpenses };
});

const donutLabels = computed(() => analyticsData.value.stats.map(s => s.name));
const donutData = computed(() => analyticsData.value.stats.map(s => s.amount));
const donutColors = computed(() => analyticsData.value.stats.map(s => s.color));
</script>

<template>
  <div class="w-full flex flex-col gap-6">
    
    <div class="flex justify-center sm:justify-start">
      <GlassMonthStepper v-model="selectedDate" />
    </div>

    <div v-if="financeStore.isMonthlyLoading" class="w-full h-64 flex flex-col items-center justify-center gap-3">
      <Loader2 class="w-8 h-8 animate-spin text-slate-400" />
      <span class="text-xs font-bold text-slate-500 uppercase tracking-widest animate-pulse">Analizando gastos...</span>
    </div>

    <div v-else class="flex flex-col gap-6">
      
      <div class="w-full bg-white/50 dark:bg-[#111111]/40 border border-slate-200/50 dark:border-white/5 rounded-[2rem] p-6 sm:p-8 shadow-sm backdrop-blur-sm flex flex-col items-center">
        <h4 class="text-sm font-extrabold text-slate-800 dark:text-white mb-6 text-center">Distribución de Gastos</h4>
        <div class="w-full max-w-[320px] sm:max-w-[380px] h-[250px] sm:h-[300px]">
          <GlassDonutChart 
            :labels="donutLabels"
            :data="donutData"
            :colors="donutColors"
            :currency="financeStore.balance?.currency"
            title="Total Gastado"
          />
        </div>
      </div>

      <div class="w-full bg-white/50 dark:bg-[#111111]/40 border border-slate-200/50 dark:border-white/5 rounded-[2rem] p-6 sm:p-8 shadow-sm backdrop-blur-sm flex flex-col">
        <div class="flex items-center justify-between mb-6">
          <h4 class="text-sm font-extrabold text-slate-800 dark:text-white">Detalle por Categoría</h4>
          <span class="text-[10px] font-bold px-2 py-1 bg-slate-200 dark:bg-white/10 text-slate-600 dark:text-slate-300 rounded-lg uppercase tracking-wider">
            {{ analyticsData.stats.length }} Activas
          </span>
        </div>
        
        <GlassTopCategories :stats="analyticsData.stats" />
      </div>

    </div>
  </div>
</template>