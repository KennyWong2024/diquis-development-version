<script setup lang="ts">
import { useFinanceStore } from '../../stores/finance';
import { useCategoryStore } from '../../stores/category';
import type { Transaction } from '../../types/transaction';
import type { Category } from '../../types/category';
import { resolveIcon } from '../../utils/icons';
import { CURRENCIES } from '../../constants/currencies'; 
import {
  TrendingUp, TrendingDown, ArrowRightLeft,
  MoreHorizontal, Star, Wallet
} from 'lucide-vue-next';

const financeStore = useFinanceStore();
const categoryStore = useCategoryStore();

defineProps<{
  transactions: Transaction[];
  isLoading?: boolean;
}>();

const emit = defineEmits(['select']);

const formatCurrency = (val: number, currencyCode: string = 'CRC') => {
  const c = CURRENCIES.find(x => x.code === currencyCode);
  const symbol = c ? c.symbol : '$';
  const num = new Intl.NumberFormat('es-CR', { minimumFractionDigits: 2 }).format(Math.abs(val));
  return `${symbol}${num}`;
};

const formatDateTime = (isoString: string) => {
  if (!isoString) return '';
  const date = new Date(isoString);
  return new Intl.DateTimeFormat('es-CR', {
    day: '2-digit', month: 'short', hour: '2-digit', minute: '2-digit', hour12: false
  }).format(date);
};

const getTransactionDisplayInfo = (tx: Transaction) => {
  if (tx.type === 'transfer') {
    return { title: 'Ahorro / Transf.', icon: ArrowRightLeft };
  }

  const category = categoryStore.categories.find((c: Category) => c.id === tx.category_id);
  const title = category ? category.name : (tx.type === 'expense' ? 'Gasto' : 'Ingreso');

  const icon = category
    ? resolveIcon(category.icon)
    : (tx.type === 'expense' ? TrendingDown : TrendingUp);

  return { title, icon };
};

const getAccountInfo = (accountId: string) => {
  const acc = financeStore.accounts.find(a => a.id === accountId);
  return acc ? { name: acc.name, color: acc.theme_color || 'slate' } : { name: 'Cuenta', color: 'slate' };
};

const getColorClass = (themeColor: string) => {
  const map: Record<string, string> = {
    silver: 'bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-300 border-slate-200 dark:border-slate-700',
    gold: 'bg-amber-50 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400 border-amber-200 dark:border-amber-800',
    black: 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-300 border-gray-300 dark:border-gray-700',
    rose: 'bg-rose-50 text-rose-700 dark:bg-rose-900/30 dark:text-rose-400 border-rose-200 dark:border-rose-800',
    blue: 'bg-blue-50 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400 border-blue-200 dark:border-blue-800',
    green: 'bg-emerald-50 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400 border-emerald-200 dark:border-emerald-800',
  };
  return map[themeColor] || map['silver'];
};
</script>

<template>
  <div v-if="isLoading" class="py-12 flex justify-center items-center">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-slate-900 dark:border-white opacity-50"></div>
  </div>

  <div v-else-if="transactions.length === 0" class="py-16 text-center text-slate-400 dark:text-slate-500 border border-dashed border-slate-200/50 dark:border-white/5 rounded-[2rem] bg-white/30 dark:bg-[#111111]/30 backdrop-blur-sm">
    <div class="mx-auto w-12 h-12 bg-slate-100 dark:bg-white/5 rounded-2xl flex items-center justify-center mb-4 shadow-inner">
      <MoreHorizontal class="w-5 h-5 text-slate-400 dark:text-slate-500" />
    </div>
    <p class="font-bold text-slate-700 dark:text-slate-300">Sin movimientos</p>
    <p class="text-xs mt-1 font-medium">No hay datos en este período.</p>
  </div>

  <div v-else class="flex flex-col gap-1.5">
    <div 
      v-for="tx in transactions" 
      :key="tx.id"
      @click="emit('select', tx.id)"
      class="group flex justify-between items-center p-3 sm:p-4 rounded-2xl hover:bg-white/60 dark:hover:bg-white/5 transition-all duration-300 cursor-pointer border border-transparent hover:border-slate-200/50 dark:hover:border-white/5"
    >
      
      <div class="flex items-center gap-3 sm:gap-4 overflow-hidden flex-1 min-w-0">
        
        <div class="w-11 h-11 sm:w-12 sm:h-12 shrink-0 rounded-[14px] flex items-center justify-center text-slate-500 dark:text-slate-400 bg-slate-100/50 dark:bg-black/20 border border-slate-200/50 dark:border-white/5 group-hover:bg-slate-200/50 dark:group-hover:bg-white/10 group-hover:text-slate-900 dark:group-hover:text-white transition-all duration-300 shadow-sm group-hover:shadow">
            <component :is="getTransactionDisplayInfo(tx).icon" class="w-5 h-5" />
        </div>
        
        <div class="flex flex-col flex-1 min-w-0">
          <p class="font-extrabold text-sm text-slate-900 dark:text-white leading-tight truncate tracking-tight">
            {{ getTransactionDisplayInfo(tx).title }}
          </p>
          
          <div class="flex flex-col sm:flex-row sm:items-center gap-1.5 sm:gap-2 mt-1 sm:mt-0.5 min-w-0">
            
            <span v-if="tx.description" class="text-[11px] sm:text-xs text-slate-500 dark:text-slate-400 truncate font-medium">
              {{ tx.description }}
            </span>
            <span v-else class="text-[10px] sm:text-[11px] text-slate-400 dark:text-slate-500 italic font-medium opacity-70 truncate">
              Sin descripción
            </span>
            
            <div class="flex items-center gap-1.5 shrink-0 mt-0.5 sm:mt-0">
              <span class="inline-flex items-center gap-1 text-[9px] sm:text-[10px] uppercase font-bold tracking-widest px-1.5 sm:px-2 py-0.5 rounded shadow-sm border" :class="getColorClass(getAccountInfo(tx.account_id).color)">
                <Wallet class="w-2.5 h-2.5 sm:w-3 sm:h-3 opacity-70" /> 
                {{ getAccountInfo(tx.account_id).name }}
              </span>
              
              <span v-if="tx.is_essential" class="inline-flex items-center gap-1 text-[9px] sm:text-[10px] uppercase font-bold tracking-widest text-amber-600 dark:text-amber-400 bg-amber-50 dark:bg-amber-500/10 px-1.5 py-0.5 rounded border border-amber-200/50 dark:border-amber-500/20">
                <Star class="w-2.5 h-2.5 sm:w-3 sm:h-3 fill-amber-500/50" />
              </span>
            </div>

          </div>
        </div>
      </div>
      
      <div class="flex flex-col items-end shrink-0 pl-2 sm:pl-4">
        <p 
          class="font-extrabold text-sm sm:text-base tracking-tight whitespace-nowrap flex items-center gap-0.5"
          :class="{
            'text-slate-900 dark:text-white': tx.type === 'expense',     
            'text-emerald-600 dark:text-emerald-400': tx.type === 'income', 
            'text-slate-500 dark:text-slate-400': tx.type === 'transfer'    
          }"
        >
          <span v-if="tx.type === 'expense'" class="opacity-70 mr-0.5">-</span>
          <span v-else-if="tx.type === 'income'" class="opacity-70 mr-0.5">+</span>
          
          {{ formatCurrency(tx.amount, tx.currency) }}
        </p>
        
        <p class="text-[9px] sm:text-[10px] font-bold text-slate-400 dark:text-slate-500 mt-1 tracking-wider uppercase">
           {{ formatDateTime(tx.occurred_at) }}
        </p>
      </div>

    </div>
  </div>
</template>