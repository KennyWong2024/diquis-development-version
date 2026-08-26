<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue';
import { Plus, ArrowRightLeft, CalendarClock, CalendarDays } from 'lucide-vue-next';

const emit = defineEmits(['select-transaction', 'select-schedule']);
const isOpen = ref(false);
const dropdownRef = ref<HTMLElement | null>(null);

const toggleDropdown = () => isOpen.value = !isOpen.value;

const handleSelect = (type: 'transaction' | 'schedule' | 'schedule-once') => {
  if (type === 'transaction') {
      emit('select-transaction');
  } else if (type === 'schedule') {
      emit('select-schedule', 'monthly'); 
  } else if (type === 'schedule-once') {
      emit('select-schedule', 'once'); 
  }
  isOpen.value = false;
};

const handleClickOutside = (e: MouseEvent) => {
  if (dropdownRef.value && !dropdownRef.value.contains(e.target as Node)) {
    isOpen.value = false;
  }
};

onMounted(() => document.addEventListener('click', handleClickOutside));
onUnmounted(() => document.removeEventListener('click', handleClickOutside));
</script>

<template>
  <div ref="dropdownRef" class="relative z-[100]">
    
    <button 
      @click="toggleDropdown"
      class="text-sm font-bold flex items-center gap-2 text-white dark:text-slate-950 bg-slate-900 dark:bg-white hover:bg-slate-800 dark:hover:bg-slate-100 px-5 py-2.5 rounded-xl shadow-[0_8px_16px_rgb(0,0,0,0.1)] dark:shadow-[0_8px_24px_rgb(255,255,255,0.15)] transition-all duration-300"
    >
      <Plus class="w-4 h-4 transition-transform duration-300" :class="{ 'rotate-45': isOpen }" /> Agregar
    </button>

    <transition name="dropdown">
      <div v-if="isOpen" class="absolute right-0 top-[calc(100%+12px)] w-72 p-2 rounded-2xl bg-white/80 dark:bg-[#111111]/95 backdrop-blur-2xl border border-white/50 dark:border-white/10 shadow-[0_20px_40px_rgb(0,0,0,0.15)] dark:shadow-[0_20px_40px_rgb(0,0,0,0.5)] transform transition-all overflow-hidden origin-top-right">
        
        <div class="absolute inset-x-0 top-0 h-px bg-white/60 dark:bg-white/10 pointer-events-none"></div>

        <div class="flex flex-col gap-1">
          
          <button 
            @click="handleSelect('transaction')"
            class="w-full flex items-start gap-3 p-3 rounded-xl text-left transition-colors hover:bg-slate-100/80 dark:hover:bg-white/5 group"
          >
            <div class="p-2 rounded-lg bg-slate-200/50 dark:bg-white/5 text-slate-600 dark:text-slate-400 group-hover:bg-slate-900 group-hover:text-white dark:group-hover:bg-white dark:group-hover:text-slate-900 transition-colors shadow-sm">
              <ArrowRightLeft class="w-4 h-4" />
            </div>
            <div>
              <h4 class="text-sm font-extrabold text-slate-900 dark:text-white leading-none mb-1">Movimiento de Hoy</h4>
              <p class="text-[10px] font-medium text-slate-500 dark:text-slate-400 leading-tight">
                Gasto o ingreso puntual de hoy o del pasado.
              </p>
            </div>
          </button>

          <button 
            @click="handleSelect('schedule-once')"
            class="w-full flex items-start gap-3 p-3 rounded-xl text-left transition-colors hover:bg-slate-100/80 dark:hover:bg-white/5 group mt-1"
          >
            <div class="p-2 rounded-lg bg-slate-200/50 dark:bg-white/5 text-slate-600 dark:text-slate-400 group-hover:bg-slate-900 group-hover:text-white dark:group-hover:bg-white dark:group-hover:text-slate-900 transition-colors shadow-sm">
              <CalendarDays class="w-4 h-4" />
            </div>
            <div>
              <h4 class="text-sm font-extrabold text-slate-900 dark:text-white leading-none mb-1">Evento Futuro (Único)</h4>
              <p class="text-[10px] font-medium text-slate-500 dark:text-slate-400 leading-tight">
                Agendar cita médica, matricula, pago pendiente, etc.
              </p>
            </div>
          </button>

          <button 
            @click="handleSelect('schedule')"
            class="w-full flex items-start gap-3 p-3 rounded-xl text-left transition-colors hover:bg-slate-100/80 dark:hover:bg-white/5 group mt-1"
          >
            <div class="p-2 rounded-lg bg-slate-200/50 dark:bg-white/5 text-slate-600 dark:text-slate-400 group-hover:bg-slate-900 group-hover:text-white dark:group-hover:bg-white dark:group-hover:text-slate-900 transition-colors shadow-sm">
              <CalendarClock class="w-4 h-4" />
            </div>
            <div>
              <h4 class="text-sm font-extrabold text-slate-900 dark:text-white leading-none mb-1">Pago Recurrente</h4>
              <p class="text-[10px] font-medium text-slate-500 dark:text-slate-400 leading-tight">
                Suscripciones, recibos o gastos fijos periódicos.
              </p>
            </div>
          </button>

        </div>
      </div>
    </transition>

  </div>
</template>

<style scoped>
.dropdown-enter-active, .dropdown-leave-active { transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1); }
.dropdown-enter-from, .dropdown-leave-to { opacity: 0; transform: scale(0.95) translateY(-10px); }
</style>