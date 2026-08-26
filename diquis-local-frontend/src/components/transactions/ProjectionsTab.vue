<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useScheduledStore } from '../../stores/scheduled';
import { CURRENCIES } from '../../constants/currencies';
import GlassCalendar from '../ui/GlassCalendar.vue';
import ScheduleDetailDrawer from '../forms/ScheduleDetailDrawer.vue';
import GlassCard from '../ui/GlassCard.vue';
import { 
  ChevronLeft, ChevronRight, 
  TrendingUp, TrendingDown, ArrowRightLeft, CalendarDays,
  FilterX
} from 'lucide-vue-next';

const props = defineProps({
  filterType: {
    type: String,
    default: 'all'
  }
});

const emit = defineEmits(['update:filterType']);

const scheduledStore = useScheduledStore();
const isDetailDrawerOpen = ref(false);
const selectedSchedule = ref<any>(null);

const selectedCalendarDate = ref<Date | undefined>(undefined);

const currentPage = ref(1);
const itemsPerPage = 7;

onMounted(() => {
  scheduledStore.refreshAll();
});

const handleRefresh = () => {
  scheduledStore.refreshAll();
};

const openDetailDrawer = (sched: any) => {
  selectedSchedule.value = sched;
  isDetailDrawerOpen.value = true;
};

const occursOnDate = (sched: any, tDate: Date) => {
    if (!sched.next_due_date) return false;
    const [sYear, sMonth, sDay] = sched.next_due_date.split('T')[0].split('-').map(Number);
    const sDate = new Date(sYear, sMonth - 1, sDay);
    const diffTime = tDate.getTime() - sDate.getTime();
    const diffDays = Math.round(diffTime / (1000 * 60 * 60 * 24));

    if (!sched.frequency || sched.frequency === 'once' || sched.frequency === 'one_time' || sched.frequency === 'none') {
        return tDate.getFullYear() === sYear && tDate.getMonth() === sMonth - 1 && tDate.getDate() === sDay;
    }

    switch (sched.frequency) {
        case 'daily': return true;
        case 'weekly': return diffDays % 7 === 0;
        case 'biweekly': return diffDays % 14 === 0;
        case 'monthly': {
            const tLastDay = new Date(tDate.getFullYear(), tDate.getMonth() + 1, 0).getDate();
            return tDate.getDate() === sDay || (sDay > tLastDay && tDate.getDate() === tLastDay);
        }
        case 'quarterly': {
            const tLastDayQ = new Date(tDate.getFullYear(), tDate.getMonth() + 1, 0).getDate();
            const isSameDayQ = tDate.getDate() === sDay || (sDay > tLastDayQ && tDate.getDate() === tLastDayQ);
            return isSameDayQ && (Math.abs(tDate.getMonth() - (sMonth - 1)) % 3 === 0);
        }
        case 'yearly': return tDate.getMonth() === (sMonth - 1) && tDate.getDate() === sDay;
        default: return tDate.getFullYear() === sYear && tDate.getMonth() === sMonth - 1 && tDate.getDate() === sDay;
    }
};

const filteredSchedules = computed(() => {
  let list = scheduledStore.activeSchedules;
  
  if (props.filterType !== 'all') {
    list = list.filter(sched => sched.type === props.filterType);
  }
  
  if (selectedCalendarDate.value) {
    list = list.filter(sched => occursOnDate(sched, selectedCalendarDate.value!));
  }
  
  return list;
});

const totalPages = computed(() => {
  return Math.max(1, Math.ceil(filteredSchedules.value.length / itemsPerPage));
});

const paginatedSchedules = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage;
  const end = start + itemsPerPage;
  return filteredSchedules.value.slice(start, end);
});

const nextPage = () => {
  if (currentPage.value < totalPages.value) currentPage.value++;
};

const prevPage = () => {
  if (currentPage.value > 1) currentPage.value--;
};

const clearFilter = () => {
  emit('update:filterType', 'all');
  selectedCalendarDate.value = undefined;
  currentPage.value = 1;
};

const formatCurrency = (val: number, currencyCode: string = 'CRC') => {
  const c = CURRENCIES.find(x => x.code === currencyCode);
  const symbol = c ? c.symbol : '$';
  const num = new Intl.NumberFormat('es-CR', { minimumFractionDigits: 2 }).format(Math.abs(val));
  return `${symbol}${num}`;
};

const formatDate = (dateStr: string) => {
  if (!dateStr) return '';
  const [year, month, day] = dateStr.split('T')[0].split('-').map(Number);
  const localDate = new Date(year, month - 1, day);
  return new Intl.DateTimeFormat('es-CR', { day: '2-digit', month: 'short', year: 'numeric' }).format(localDate);
};

const formatDateObj = (d: Date) => {
  return new Intl.DateTimeFormat('es-CR', { day: '2-digit', month: 'short', year: 'numeric' }).format(d);
};

const frequencyLabels: Record<string, string> = {
  daily: 'Diario', weekly: 'Semanal', biweekly: 'Quincenal',
  monthly: 'Mensual', quarterly: 'Trimestral', yearly: 'Anual',
  once: 'Una vez', none: 'Un solo pago'
};

const getTypeInfo = (type: string) => {
  if (type === 'income') return { icon: TrendingUp, color: 'text-emerald-500', prefix: '+' };
  if (type === 'expense') return { icon: TrendingDown, color: 'text-slate-400 dark:text-slate-500', prefix: '-' };
  return { icon: ArrowRightLeft, color: 'text-slate-400 dark:text-slate-500', prefix: '' };
};
</script>

<template>
  <div class="flex flex-col gap-8 w-full">
    
    <div class="w-full">
      <GlassCalendar :filter-type="props.filterType" v-model:selected-date="selectedCalendarDate" />
    </div>
    
    <GlassCard class="p-2 sm:p-4 flex flex-col flex-1 min-h-[400px]">
      
      <div class="px-3 sm:px-4 pt-3 sm:pt-4 pb-3 flex justify-between items-center" :class="{ 'border-b border-slate-200/50 dark:border-white/5': props.filterType === 'all' && !selectedCalendarDate }">
        <h4 class="text-sm font-extrabold text-slate-800 dark:text-white uppercase tracking-wider">Plantillas de Programación</h4>
        <span class="text-[10px] font-bold px-2 py-1 bg-slate-100 dark:bg-white/5 text-slate-500 dark:text-slate-400 rounded-md shrink-0 ml-2">
          {{ filteredSchedules.length }} Activas
        </span>
      </div>
      
      <div v-if="props.filterType !== 'all' || selectedCalendarDate" class="px-3 sm:px-4 pb-4 mb-2 border-b border-slate-200/50 dark:border-white/5 flex flex-col sm:flex-row sm:items-center justify-between gap-3 animate-in fade-in slide-in-from-top-2 duration-300">
        
        <div class="flex flex-wrap items-center gap-2">
          <span class="text-[10px] font-bold text-slate-400 dark:text-slate-500 uppercase tracking-widest mr-1">Filtros:</span>
          
          <span v-if="props.filterType !== 'all'" class="text-[10px] font-bold px-2.5 py-1 rounded-md border uppercase tracking-widest"
                :class="props.filterType === 'income' ? 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border-emerald-500/20' : 'bg-rose-500/10 text-rose-600 dark:text-rose-400 border-rose-500/20'">
            {{ props.filterType === 'income' ? 'Solo Ingresos' : 'Solo Gastos' }}
          </span>
          
          <span v-if="selectedCalendarDate" class="text-[10px] font-bold px-2.5 py-1 rounded-md border uppercase tracking-widest bg-indigo-500/10 text-indigo-600 dark:text-indigo-400 border-indigo-500/20">
            Día: {{ formatDateObj(selectedCalendarDate) }}
          </span>
        </div>

        <button @click="clearFilter" class="flex items-center justify-center gap-1.5 px-3 py-2 bg-slate-100 hover:bg-slate-200 dark:bg-white/5 dark:hover:bg-white/10 text-slate-600 dark:text-slate-300 rounded-lg transition-colors text-xs font-bold w-full sm:w-auto shrink-0">
          <FilterX class="w-3.5 h-3.5" />
          <span>Limpiar filtros</span>
        </button>
      </div>
      
      <div v-if="scheduledStore.activeSchedules.length === 0" class="flex-1 flex flex-col items-center justify-center py-12 text-center">
        <div class="w-12 h-12 rounded-full bg-slate-100 dark:bg-white/5 flex items-center justify-center mb-3 border border-slate-200/50 dark:border-white/5 shadow-inner">
          <CalendarDays class="w-5 h-5 text-slate-400" />
        </div>
        <p class="text-sm font-bold text-slate-700 dark:text-slate-300">No tienes programaciones activas.</p>
        <p class="text-xs text-slate-500 mt-1 max-w-xs mx-auto">Añade nuevos gastos fijos, suscripciones o ingresos regulares para que el calendario cobre vida.</p>
      </div>

      <div v-else-if="filteredSchedules.length === 0" class="flex-1 flex flex-col items-center justify-center py-12 text-center">
        <div class="w-12 h-12 rounded-full bg-slate-100 dark:bg-white/5 flex items-center justify-center mb-3 border border-slate-200/50 dark:border-white/5 shadow-inner">
          <FilterX class="w-5 h-5 text-slate-400" />
        </div>
        <p class="text-sm font-bold text-slate-700 dark:text-slate-300">No hay coincidencias.</p>
        <p class="text-xs text-slate-500 mt-1 max-w-xs mx-auto mb-4">
          No tienes programaciones activas {{ selectedCalendarDate ? 'para esta fecha' : 'en tu lista' }} {{ props.filterType !== 'all' ? 'con este filtro' : '' }}.
        </p>
        <button @click="clearFilter" class="text-xs font-bold text-slate-900 dark:text-white bg-slate-200/50 dark:bg-white/10 px-4 py-2 rounded-xl hover:bg-slate-300/50 dark:hover:bg-white/20 transition-colors">
          Mostrar todos
        </button>
      </div>

      <div v-else class="flex-1 flex flex-col gap-1">
        <div 
          v-for="sched in paginatedSchedules" 
          :key="sched.id"
          @click="openDetailDrawer(sched)"
          class="group flex flex-col sm:flex-row justify-between items-start sm:items-center p-3 sm:p-4 rounded-2xl hover:bg-slate-100/50 dark:hover:bg-white/[0.03] transition-all duration-300 cursor-pointer border border-transparent hover:border-slate-200/50 dark:hover:border-white/5"
        >
          
          <div class="flex items-center gap-4 overflow-hidden w-full sm:w-auto">
            
            <div class="w-16 h-11 shrink-0 rounded-xl flex flex-col items-center justify-center bg-slate-50/80 dark:bg-white/5 backdrop-blur-md border border-slate-200/50 dark:border-white/5 group-hover:bg-white dark:group-hover:bg-white/10 transition-colors duration-300">
               <span class="text-[8px] font-bold text-slate-400 uppercase tracking-widest leading-none mb-0.5">Próx</span>
               <span class="text-[10px] font-black text-slate-700 dark:text-slate-300 group-hover:text-slate-900 dark:group-hover:text-white uppercase tracking-wider leading-none">
                 {{ formatDate(sched.next_due_date).substring(0, 6) }}
               </span>
            </div>
            
            <div class="flex flex-col truncate">
              <div class="flex items-center gap-1.5 mb-0.5">
                 <component :is="getTypeInfo(sched.type).icon" class="w-3.5 h-3.5" :class="getTypeInfo(sched.type).color" />
                 <p class="font-bold text-sm text-slate-900 dark:text-white leading-tight truncate">
                   {{ sched.name }}
                 </p>
              </div>
              
              <div class="flex items-center gap-1.5 text-xs text-slate-500 dark:text-slate-400">
                <span class="font-medium">{{ frequencyLabels[sched.frequency] || 'Una vez' }}</span>
              </div>
            </div>
          </div>

          <div class="flex flex-col items-end shrink-0 pl-4 mt-2 sm:mt-0 w-full sm:w-auto">
            <p 
              class="font-extrabold text-base tracking-tight"
              :class="sched.type === 'income' ? 'text-emerald-600/90 dark:text-emerald-400/90' : (sched.type === 'expense' ? 'text-slate-900 dark:text-white' : 'text-slate-600 dark:text-slate-300')"
            >
              {{ getTypeInfo(sched.type).prefix }}{{ formatCurrency(sched.expected_amount, sched.currency) }}
            </p>
          </div>

        </div>
      </div>

      <div 
        v-if="filteredSchedules.length > 0" 
        class="mt-4 pt-4 border-t border-slate-200/50 dark:border-white/5 flex flex-col sm:flex-row items-center justify-between gap-4 px-2 sm:px-4"
      >
        <p class="text-xs font-semibold text-slate-500 dark:text-slate-400">
          Mostrando <span class="text-slate-800 dark:text-white font-bold">{{ (currentPage - 1) * itemsPerPage + 1 }}</span> al 
          <span class="text-slate-800 dark:text-white font-bold">{{ Math.min(currentPage * itemsPerPage, filteredSchedules.length) }}</span> de 
          <span class="text-slate-800 dark:text-white font-bold">{{ filteredSchedules.length }}</span>
        </p>

        <div class="flex items-center gap-2">
          <button 
            @click="prevPage"
            :disabled="currentPage === 1"
            class="p-2 rounded-xl border border-slate-200/50 dark:border-white/5 bg-white/50 dark:bg-white/5 text-slate-600 dark:text-slate-300 hover:bg-white dark:hover:bg-white/10 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
          >
            <ChevronLeft class="w-4 h-4" />
          </button>
          <span class="text-xs font-bold text-slate-700 dark:text-slate-300 px-3 py-1.5 bg-slate-100/50 dark:bg-white/5 rounded-lg border border-slate-200/50 dark:border-white/5">
            Pág {{ currentPage }} / {{ totalPages }}
          </span>
          <button 
            @click="nextPage"
            :disabled="currentPage === totalPages"
            class="p-2 rounded-xl border border-slate-200/50 dark:border-white/5 bg-white/50 dark:bg-white/5 text-slate-600 dark:text-slate-300 hover:bg-white dark:hover:bg-white/10 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
          >
            <ChevronRight class="w-4 h-4" />
          </button>
        </div>
      </div>

    </GlassCard>

    <ScheduleDetailDrawer 
      :is-open="isDetailDrawerOpen" 
      :schedule-id="selectedSchedule?.id || null"
      :schedule-data="selectedSchedule"
      @close="isDetailDrawerOpen = false"
      @updated="handleRefresh"
    />
  </div>
</template>