<script setup lang="ts">
import { ref, computed, watch } from 'vue';
import { resolveIcon } from '../../utils/icons';
import { ChevronLeft, ChevronRight } from 'lucide-vue-next';

export interface CategoryStat {
  id: string;
  name: string;
  iconName: string | null;
  amount: number;
  percentage: number;
  color: string;
}

const props = defineProps<{
  stats: CategoryStat[];
}>();

const currentPage = ref(1);
const itemsPerPage = 15;

watch(() => props.stats, () => {
  currentPage.value = 1;
});

const totalPages = computed(() => Math.max(1, Math.ceil(props.stats.length / itemsPerPage)));

const paginatedStats = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage;
  return props.stats.slice(start, start + itemsPerPage);
});

const currentStart = computed(() => (currentPage.value - 1) * itemsPerPage + 1);
const currentEnd = computed(() => Math.min(currentPage.value * itemsPerPage, props.stats.length));

const nextPage = () => { if (currentPage.value < totalPages.value) currentPage.value++; };
const prevPage = () => { if (currentPage.value > 1) currentPage.value--; };

const formatCurrency = (val: number) => new Intl.NumberFormat('es-CR', { style: 'currency', currency: 'CRC', minimumFractionDigits: 0 }).format(val);
</script>

<template>
  <div class="w-full flex flex-col h-full">
    
    <div v-if="stats.length === 0" class="py-8 text-center text-xs font-medium text-slate-400 italic">
      No hay gastos registrados en este período.
    </div>

    <div v-else class="flex flex-col gap-3 transition-all duration-300">
      <div 
        v-for="stat in paginatedStats" 
        :key="stat.id"
        class="group flex items-center justify-between p-3 rounded-2xl bg-white/40 dark:bg-white/5 border border-white/50 dark:border-white/5 hover:bg-white/60 dark:hover:bg-white/10 transition-all duration-300"
      >
        <div class="flex items-center gap-3 w-full">
          <div 
            class="w-10 h-10 rounded-xl flex items-center justify-center shrink-0 shadow-sm transition-colors"
            :style="{ backgroundColor: `${stat.color}15`, color: stat.color }"
          >
            <component :is="resolveIcon(stat.iconName)" class="w-4 h-4" />
          </div>

          <div class="flex flex-col flex-1 min-w-0">
            <div class="flex justify-between items-end mb-1">
              <span class="text-xs font-extrabold text-slate-800 dark:text-slate-200 truncate pr-2">{{ stat.name }}</span>
              <span class="text-xs font-black text-slate-900 dark:text-white shrink-0">{{ formatCurrency(stat.amount) }}</span>
            </div>

            <div class="w-full h-1.5 bg-slate-200 dark:bg-black/40 rounded-full overflow-hidden flex relative">
              <div 
                class="h-full rounded-full transition-all duration-1000 ease-out"
                :style="{ width: `${stat.percentage}%`, backgroundColor: stat.color }"
              ></div>
            </div>
          </div>
          
          <span class="text-[10px] font-bold text-slate-500 dark:text-slate-400 w-8 text-right shrink-0">
            {{ Math.round(stat.percentage) }}%
          </span>
        </div>
      </div>

      <div v-if="totalPages > 1" class="mt-4 pt-4 border-t border-slate-200/50 dark:border-white/5 flex items-center justify-between px-1">
        <span class="text-[10px] sm:text-xs font-semibold text-slate-500 dark:text-slate-400">
          Mostrando <span class="text-slate-800 dark:text-slate-200 font-bold">{{ currentStart }}</span> - <span class="text-slate-800 dark:text-slate-200 font-bold">{{ currentEnd }}</span> de <span class="text-slate-800 dark:text-slate-200 font-bold">{{ stats.length }}</span>
        </span>
        
        <div class="flex items-center gap-2">
          <button 
            @click="prevPage" 
            :disabled="currentPage === 1"
            class="p-2 rounded-xl bg-white/50 dark:bg-white/5 border border-slate-200/50 dark:border-white/5 text-slate-600 dark:text-slate-300 hover:bg-white dark:hover:bg-white/10 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
          >
            <ChevronLeft class="w-4 h-4" />
          </button>
          <span class="text-xs font-bold text-slate-700 dark:text-slate-300 px-3 py-1.5 bg-slate-100/50 dark:bg-white/5 rounded-lg border border-slate-200/50 dark:border-white/5">
            Pág {{ currentPage }} / {{ totalPages }}
          </span>
          <button 
            @click="nextPage" 
            :disabled="currentPage === totalPages"
            class="p-2 rounded-xl bg-white/50 dark:bg-white/5 border border-slate-200/50 dark:border-white/5 text-slate-600 dark:text-slate-300 hover:bg-white dark:hover:bg-white/10 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
          >
            <ChevronRight class="w-4 h-4" />
          </button>
        </div>
      </div>

    </div>
  </div>
</template>