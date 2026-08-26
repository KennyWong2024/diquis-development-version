<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue';
import { ChevronLeft, ChevronRight, CalendarDays, ChevronDown, CalendarHeart } from 'lucide-vue-next';

const props = defineProps<{
  modelValue: Date;
}>();

const emit = defineEmits(['update:modelValue', 'change']);

const isOpen = ref(false);
const stepperRef = ref<HTMLElement | null>(null);
const pickerYear = ref(props.modelValue.getFullYear());

const months = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'];

const currentMonthName = computed(() => {
  return new Intl.DateTimeFormat('es-CR', { month: 'long', year: 'numeric' }).format(props.modelValue);
});

const prevMonth = () => {
  const newDate = new Date(props.modelValue);
  newDate.setMonth(newDate.getMonth() - 1);
  emit('update:modelValue', newDate);
  emit('change', newDate);
};

const nextMonth = () => {
  const newDate = new Date(props.modelValue);
  newDate.setMonth(newDate.getMonth() + 1);
  emit('update:modelValue', newDate);
  emit('change', newDate);
};

const togglePicker = () => {
  isOpen.value = !isOpen.value;
  if (isOpen.value) {
    pickerYear.value = props.modelValue.getFullYear();
  }
};

const selectMonth = (monthIndex: number) => {
  const newDate = new Date(pickerYear.value, monthIndex, 1);
  emit('update:modelValue', newDate);
  emit('change', newDate);
  isOpen.value = false;
};

const goToCurrentMonth = () => {
  const now = new Date();
  pickerYear.value = now.getFullYear();
  emit('update:modelValue', now);
  emit('change', now);
  isOpen.value = false;
};

const handleClickOutside = (event: MouseEvent) => {
  if (stepperRef.value && !stepperRef.value.contains(event.target as Node)) {
    isOpen.value = false;
  }
};

onMounted(() => document.addEventListener('click', handleClickOutside));
onUnmounted(() => document.removeEventListener('click', handleClickOutside));

const isCurrentMonth = computed(() => {
  const now = new Date();
  return props.modelValue.getMonth() === now.getMonth() && props.modelValue.getFullYear() === now.getFullYear();
});

const isSelectedMonth = (index: number) => {
  return props.modelValue.getMonth() === index && props.modelValue.getFullYear() === props.modelValue.getFullYear();
};
</script>

<template>
  <div ref="stepperRef" class="relative z-[100]">
    
    <div class="inline-flex items-center p-1.5 bg-white/30 dark:bg-white/[0.03] border border-white/40 dark:border-white/5 rounded-2xl backdrop-blur-xl shadow-[0_8px_32px_0_rgba(31,38,135,0.07)] dark:shadow-[0_8px_32px_0_rgba(0,0,0,0.3)] transition-all duration-300 hover:shadow-lg hover:border-white/60 dark:hover:border-white/10 relative overflow-hidden group">
      
      <div class="absolute inset-x-0 top-0 h-px bg-white/40 dark:bg-white/10 pointer-events-none"></div>

      <button 
        @click="prevMonth"
        class="p-2.5 rounded-xl text-slate-600 hover:text-slate-950 hover:bg-white dark:text-slate-400 dark:hover:text-white dark:hover:bg-white/10 transition-all duration-300 relative z-10"
      >
        <ChevronLeft class="w-5 h-5" />
      </button>

      <button 
        @click="togglePicker"
        class="flex items-center justify-center gap-2.5 px-5 py-2 w-48 rounded-xl hover:bg-white/60 dark:hover:bg-white/5 transition-colors group relative z-10"
      >
        <CalendarDays class="w-4 h-4 text-slate-500 dark:text-slate-500 group-hover:text-slate-800 dark:group-hover:text-slate-200 transition-colors" />
        <span class="text-sm font-bold text-slate-900 dark:text-white capitalize truncate tracking-wide">
          {{ currentMonthName }}
        </span>
        <ChevronDown class="w-3.5 h-3.5 text-slate-500 transition-transform duration-300" :class="{ 'rotate-180': isOpen }" />
      </button>

      <button 
        @click="nextMonth"
        :disabled="isCurrentMonth"
        class="p-2.5 rounded-xl transition-all duration-300 relative z-10"
        :class="isCurrentMonth ? 'text-slate-300 dark:text-slate-700 cursor-not-allowed' : 'text-slate-600 hover:text-slate-950 hover:bg-white dark:text-slate-400 dark:hover:text-white dark:hover:bg-white/10'"
      >
        <ChevronRight class="w-5 h-5" />
      </button>
    </div>

    <transition name="dropdown">
      <div v-if="isOpen" class="absolute top-[calc(100%+12px)] left-1/2 -translate-x-1/2 w-72 p-5 rounded-[2.5rem] bg-white/50 dark:bg-[#111111]/95 backdrop-blur-2xl border border-white/50 dark:border-white/5 shadow-[0_20px_40px_rgb(0,0,0,0.1)] dark:shadow-[0_20px_40px_rgb(0,0,0,0.4)] transform transition-all z-[150] overflow-hidden">
        
        <div class="absolute inset-x-0 top-0 h-px bg-white/60 dark:bg-white/10 pointer-events-none"></div>

        <div class="flex items-center justify-between mb-5 px-3 relative z-10">
          <button @click="pickerYear--" class="p-2 rounded-lg hover:bg-slate-200/50 dark:hover:bg-white/10 text-slate-500 transition-colors">
            <ChevronLeft class="w-4 h-4" />
          </button>
          <span class="text-sm font-black text-slate-900 dark:text-white tracking-widest">{{ pickerYear }}</span>
          <button @click="pickerYear++" class="p-2 rounded-lg hover:bg-slate-200/50 dark:hover:bg-white/10 text-slate-500 transition-colors">
            <ChevronRight class="w-4 h-4" />
          </button>
        </div>

        <div class="grid grid-cols-3 gap-2.5 relative z-10">
          <button 
            v-for="(month, index) in months" 
            :key="index"
            @click="selectMonth(index)"
            class="py-3 rounded-xl text-xs font-bold transition-all duration-300 border border-transparent backdrop-blur-sm"
            :class="[
              isSelectedMonth(index) && pickerYear === props.modelValue.getFullYear()
                ? 'bg-slate-900 dark:bg-white text-white dark:text-slate-900 shadow-md scale-105 border-slate-900 dark:border-white' 
                : 'text-slate-700 dark:text-slate-400 bg-white/40 dark:bg-white/5 hover:bg-white dark:hover:bg-white/10 hover:text-slate-950 dark:hover:text-white border-white/40 dark:border-white/5'
            ]"
          >
            {{ month }}
          </button>
        </div>

        <div class="mt-5 pt-4 border-t border-slate-200/50 dark:border-white/10 relative z-10 flex justify-center">
           <button 
             @click="goToCurrentMonth" 
             class="flex items-center gap-2 text-xs font-bold text-slate-600 hover:text-slate-900 dark:text-slate-400 dark:hover:text-white transition-all bg-white/50 dark:bg-white/5 hover:bg-white dark:hover:bg-white/10 px-5 py-2.5 rounded-xl border border-white/50 dark:border-white/5 shadow-sm w-full justify-center"
           >
             <CalendarHeart class="w-3.5 h-3.5" />
             Ir al mes actual
           </button>
        </div>

      </div>
    </transition>

  </div>
</template>

<style scoped>
.dropdown-enter-active, .dropdown-leave-active { transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1); }
.dropdown-enter-from, .dropdown-leave-to { opacity: 0; transform: translate(-50%, -10px) scale(0.95); }
</style>