<script setup lang="ts">
import { ref, computed } from 'vue';
import { useScheduledStore } from '../../stores/scheduled';
import { ChevronLeft, ChevronRight } from 'lucide-vue-next';

const props = defineProps({
  filterType: {
    type: String,
    default: 'all'
  },
  selectedDate: {
    type: Date,
    default: undefined
  }
});

const emit = defineEmits(['update:selectedDate']);

const scheduledStore = useScheduledStore();
const currentDate = ref(new Date());

const daysOfWeek = ['Dom', 'Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb'];

const nextMonth = () => {
    currentDate.value = new Date(currentDate.value.getFullYear(), currentDate.value.getMonth() + 1, 1);
};

const prevMonth = () => {
    currentDate.value = new Date(currentDate.value.getFullYear(), currentDate.value.getMonth() - 1, 1);
};

const monthName = computed(() => {
    return new Intl.DateTimeFormat('es-CR', { month: 'long', year: 'numeric' }).format(currentDate.value);
});

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
        case 'daily':
            return true;
        case 'weekly':
            return diffDays % 7 === 0;
        case 'biweekly':
            return diffDays % 14 === 0;
        case 'monthly': {
            const tLastDay = new Date(tDate.getFullYear(), tDate.getMonth() + 1, 0).getDate();
            return tDate.getDate() === sDay || (sDay > tLastDay && tDate.getDate() === tLastDay);
        }
        case 'quarterly': {
            const tLastDayQ = new Date(tDate.getFullYear(), tDate.getMonth() + 1, 0).getDate();
            const isSameDayQ = tDate.getDate() === sDay || (sDay > tLastDayQ && tDate.getDate() === tLastDayQ);
            return isSameDayQ && (Math.abs(tDate.getMonth() - (sMonth - 1)) % 3 === 0);
        }
        case 'yearly':
            return tDate.getMonth() === (sMonth - 1) && tDate.getDate() === sDay;
        default:
            return tDate.getFullYear() === sYear && tDate.getMonth() === sMonth - 1 && tDate.getDate() === sDay;
    }
};

const calendarDays = computed(() => {
    const year = currentDate.value.getFullYear();
    const month = currentDate.value.getMonth();
    const firstDayIndex = new Date(year, month, 1).getDay();
    const daysInMonth = new Date(year, month + 1, 0).getDate();
    const days = [];
    
    for (let i = 0; i < firstDayIndex; i++) {
        days.push({ empty: true });
    }
    
    const today = new Date();
    today.setHours(0, 0, 0, 0); 

    for (let d = 1; d <= daysInMonth; d++) {
        const iterDate = new Date(year, month, d);
        const isToday = d === today.getDate() && month === today.getMonth() && year === today.getFullYear();
        
        const isSelected = props.selectedDate && d === props.selectedDate.getDate() && month === props.selectedDate.getMonth() && year === props.selectedDate.getFullYear();
        
        let hasIncome = false;
        let hasExpense = false;
        let hasTransfer = false;
        
        if (scheduledStore.activeSchedules && scheduledStore.activeSchedules.length > 0) {
            scheduledStore.activeSchedules.forEach(sched => {
                
                if (props.filterType === 'income' && sched.type !== 'income') return;
                if (props.filterType === 'expense' && sched.type !== 'expense') return;

                if (occursOnDate(sched, iterDate)) {
                    if (sched.type === 'income') hasIncome = true;
                    else if (sched.type === 'expense') hasExpense = true;
                    else if (sched.type === 'transfer') hasTransfer = true;
                }
            });
        }
        
        days.push({ day: d, isToday, isSelected, hasIncome, hasExpense, hasTransfer, empty: false });
    }
    return days;
});

const handleDayClick = (day: any) => {
    if (day.empty) return;
    const clickedDate = new Date(currentDate.value.getFullYear(), currentDate.value.getMonth(), day.day);
    
    if (props.selectedDate && clickedDate.getTime() === props.selectedDate.getTime()) {
        emit('update:selectedDate', undefined);
    } else {
        emit('update:selectedDate', clickedDate);
    }
};
</script>

<template>
  <div class="w-full bg-white/40 dark:bg-[#111111]/30 backdrop-blur-xl border border-slate-200/50 dark:border-white/5 rounded-3xl p-6 sm:p-8 shadow-[0_8px_30px_rgb(0,0,0,0.04)] dark:shadow-[0_8px_30px_rgb(0,0,0,0.2)]">
    
    <div class="flex items-center justify-between mb-8">
      <button @click="prevMonth" class="p-2 sm:p-3 rounded-2xl bg-white/50 dark:bg-white/5 hover:bg-slate-200/50 dark:hover:bg-white/10 transition-colors text-slate-500 dark:text-slate-400 shadow-sm border border-slate-200/50 dark:border-white/5">
        <ChevronLeft class="w-5 h-5" />
      </button>
      
      <h4 class="text-xl sm:text-2xl font-extrabold text-slate-800 dark:text-white capitalize tracking-tight">{{ monthName }}</h4>
      
      <button @click="nextMonth" class="p-2 sm:p-3 rounded-2xl bg-white/50 dark:bg-white/5 hover:bg-slate-200/50 dark:hover:bg-white/10 transition-colors text-slate-500 dark:text-slate-400 shadow-sm border border-slate-200/50 dark:border-white/5">
        <ChevronRight class="w-5 h-5" />
      </button>
    </div>
    
    <div class="grid grid-cols-7 gap-2 sm:gap-4 text-center mb-4">
      <span v-for="d in daysOfWeek" :key="d" class="text-[11px] sm:text-xs font-black uppercase tracking-widest text-slate-400 dark:text-slate-500">{{ d }}</span>
    </div>
    
    <div class="grid grid-cols-7 gap-2 sm:gap-4">
      <div 
        v-for="(day, idx) in calendarDays" 
        :key="idx" 
        @click="handleDayClick(day)"
        class="aspect-[4/3] sm:aspect-[2/1] flex flex-col items-center justify-center rounded-2xl relative transition-all duration-300"
        :class="[
          day.empty ? 'opacity-0 pointer-events-none' : 'cursor-pointer border border-transparent hover:border-slate-200/50 dark:hover:border-white/10 hover:bg-slate-50/50 dark:hover:bg-white/5',
          day.isToday ? 'bg-slate-900 dark:bg-white text-white dark:text-slate-900 shadow-lg scale-105 border-slate-900 dark:border-white z-10' : 'text-slate-700 dark:text-slate-300',
          day.isSelected && !day.isToday ? 'ring-2 ring-slate-800 dark:ring-white bg-slate-100 dark:bg-white/10 scale-105' : '',
          day.isSelected && day.isToday ? 'ring-4 ring-slate-300 dark:ring-slate-600' : ''
        ]"
      >
        <span v-if="!day.empty" class="text-sm sm:text-lg font-bold" :class="day.isToday ? 'font-black' : ''">{{ day.day }}</span>
        
        <div v-if="!day.empty && (day.hasIncome || day.hasExpense || day.hasTransfer)" class="absolute bottom-2 flex gap-1">
            <div v-if="day.hasExpense" class="w-2 h-2 rounded-full bg-rose-500 shadow-[0_0_8px_rgba(244,63,94,0.6)] transition-transform" :class="day.isToday ? 'border-2 border-slate-900 dark:border-white w-2.5 h-2.5' : ''"></div>
            <div v-if="day.hasTransfer" class="w-2 h-2 rounded-full bg-amber-400 shadow-[0_0_8px_rgba(251,191,36,0.6)] transition-transform" :class="day.isToday ? 'border-2 border-slate-900 dark:border-white w-2.5 h-2.5' : ''"></div>
            <div v-if="day.hasIncome" class="w-2 h-2 rounded-full bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.6)] transition-transform" :class="day.isToday ? 'border-2 border-slate-900 dark:border-white w-2.5 h-2.5' : ''"></div>
        </div>
      </div>
    </div>

  </div>
</template>