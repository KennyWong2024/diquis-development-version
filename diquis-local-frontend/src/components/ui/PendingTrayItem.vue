<script setup lang="ts">
import { computed } from 'vue';
import { ChevronRight, TrendingUp, TrendingDown, ArrowRightLeft, Info } from 'lucide-vue-next';
import { CURRENCIES } from '../../constants/currencies';

const props = defineProps<{ sched: any }>();
const emit = defineEmits(['manage']);

const formatCurrency = (val: number, currencyCode: string = 'CRC') => {
  const c = CURRENCIES.find(x => x.code === currencyCode);
  const symbol = c ? c.symbol : '$';
  const num = new Intl.NumberFormat('es-CR', { minimumFractionDigits: 2 }).format(Math.abs(val));
  return `${symbol}${num}`;
};

const dateStatus = computed(() => {
    if (!props.sched.next_due_date) return { text: '---', overdue: false };
    
    const parts = props.sched.next_due_date.split('-');
    const target = new Date(Number(parts[0]), Number(parts[1]) - 1, Number(parts[2]));
    
    const today = new Date();
    today.setHours(0, 0, 0, 0);

    if (target.getTime() === today.getTime()) return { text: 'HOY', overdue: false };
    
    const tomorrow = new Date(today);
    tomorrow.setDate(tomorrow.getDate() + 1);
    if (target.getTime() === tomorrow.getTime()) return { text: 'MAÑANA', overdue: false };

    if (target < today) return { text: 'ATRASADO', overdue: true };

    const formatted = new Intl.DateTimeFormat('es-CR', { day: '2-digit', month: 'short' }).format(target);
    return { text: formatted.toUpperCase(), overdue: false };
});

const frequencyLabels: Record<string, string> = {
    once: 'Única vez',
    daily: 'Diario', weekly: 'Semanal', biweekly: 'Quincenal',
    monthly: 'Mensual', quarterly: 'Trimestral', yearly: 'Anual'
};

const typeInfo = computed(() => {
    if (props.sched.type === 'income') return { icon: TrendingUp, iconColor: 'text-emerald-500', prefix: '+' };
    if (props.sched.type === 'expense') return { icon: TrendingDown, iconColor: 'text-slate-400 dark:text-slate-500', prefix: '-' };
    return { icon: ArrowRightLeft, iconColor: 'text-slate-400 dark:text-slate-500', prefix: '' };
});
</script>

<template>
  <div 
    class="group flex flex-row justify-between items-center p-3 sm:p-4 rounded-2xl hover:bg-slate-100/50 dark:hover:bg-white/[0.03] transition-all duration-300 cursor-pointer border border-transparent hover:border-slate-200/50 dark:hover:border-white/5 gap-3" 
    @click="emit('manage', sched)"
  >
    
    <div class="flex items-center gap-3 sm:gap-4 overflow-hidden flex-1 min-w-0">
      
      <div class="w-14 h-11 sm:w-16 shrink-0 rounded-xl flex items-center justify-center bg-slate-50/80 dark:bg-white/5 backdrop-blur-md border border-slate-200/50 dark:border-white/5 group-hover:bg-white dark:group-hover:bg-white/10 transition-colors duration-300 relative overflow-hidden"
           :class="{'border-rose-200 bg-rose-50 dark:border-rose-500/30 dark:bg-rose-500/10': dateStatus.overdue}">
         <span class="text-[8px] sm:text-[9px] font-black uppercase tracking-wider relative z-10 transition-colors" :class="dateStatus.overdue ? 'text-rose-600/90 dark:text-rose-400/90' : 'text-slate-500 dark:text-slate-400 group-hover:text-slate-900 dark:group-hover:text-white'">
            {{ dateStatus.text }}
         </span>
         <div v-if="dateStatus.overdue" class="absolute inset-0 bg-rose-500/10 dark:bg-rose-500/20 blur-md pointer-events-none"></div>
      </div>
      
      <div class="flex flex-col flex-1 min-w-0">
        <div class="flex items-center gap-1.5 mb-0.5">
           <component :is="typeInfo.icon" class="w-3.5 h-3.5 shrink-0" :class="typeInfo.iconColor" />
           <p class="font-bold text-sm text-slate-900 dark:text-white leading-tight truncate">
             {{ sched.name }}
           </p>
        </div>
        
        <div class="flex items-center gap-1.5 text-xs text-slate-500 dark:text-slate-400 truncate">
          <span class="font-medium truncate">{{ frequencyLabels[sched.frequency] || 'No definido' }}</span>
          <span v-if="sched.is_estimated" class="shrink-0 flex items-center gap-1 text-[9px] uppercase font-bold tracking-wider text-slate-400/80 dark:text-slate-500/80 ml-1 bg-slate-200/50 dark:bg-white/5 px-1.5 py-0.5 rounded-md">
            <Info class="w-3 h-3" /> <span class="hidden sm:inline">Aprox.</span>
          </span>
        </div>
      </div>
    </div>

    <div class="flex items-center gap-2 sm:gap-4 shrink-0 pl-1">
       
       <p class="font-extrabold text-sm sm:text-base tracking-tight"
          :class="sched.type === 'income' ? 'text-emerald-600/90 dark:text-emerald-400/90' : (sched.type === 'expense' ? 'text-slate-900 dark:text-white' : 'text-slate-600 dark:text-slate-300')">
         {{ typeInfo.prefix }}{{ formatCurrency(sched.expected_amount, sched.currency) }}
       </p>
       
       <button 
          class="sm:p-2 sm:px-3 sm:bg-slate-900 sm:dark:bg-white text-slate-400 group-hover:text-slate-900 sm:text-white sm:dark:text-slate-950 sm:dark:hover:text-slate-950 font-bold text-xs rounded-xl transition-all flex items-center justify-center sm:shadow-md sm:hover:bg-slate-800 sm:dark:hover:bg-slate-200 border border-transparent"
       >
          <span class="hidden sm:inline mr-1">Resolver</span>
          <ChevronRight class="w-4 h-4 sm:w-3.5 sm:h-3.5" />
       </button>
    </div>

  </div>
</template>