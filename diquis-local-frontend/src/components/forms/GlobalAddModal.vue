<script setup lang="ts">
import GlassModal from '../ui/GlassModal.vue';
import { ArrowRightLeft, CalendarDays, CalendarClock } from 'lucide-vue-next';

const props = defineProps<{
  isOpen: boolean;
  context?: 'all' | 'history' | 'planning';
  initialTab?: 'expense' | 'income' | 'transfer';
}>();

const emit = defineEmits(['close', 'select-transaction', 'select-schedule']);

const handleSelect = (actionType: 'transaction' | 'once' | 'recurring') => {
  if (actionType === 'transaction') {
    emit('select-transaction', props.initialTab || 'expense');
  } else if (actionType === 'once') {
    emit('select-schedule', 'once', props.initialTab); 
  } else if (actionType === 'recurring') {
    emit('select-schedule', 'monthly', props.initialTab); 
  }
  emit('close');
};
</script>

<template>
  <GlassModal :is-open="isOpen" title="¿Qué deseas registrar?" @close="emit('close')">
    
    <div class="space-y-3 w-full py-4">
      
      <button 
        v-if="!context || context === 'all' || context === 'history'"
        @click="handleSelect('transaction')" 
        class="w-full flex items-center gap-4 p-4 bg-white/60 dark:bg-white/5 border border-slate-200/50 dark:border-white/5 rounded-2xl hover:bg-white dark:hover:bg-white/10 transition-all group shadow-sm hover:shadow-md"
      >
        <div class="w-10 h-10 rounded-xl bg-slate-100 dark:bg-white/10 text-slate-600 dark:text-slate-400 flex items-center justify-center shrink-0">
          <ArrowRightLeft class="w-5 h-5" />
        </div>
        <div class="text-left flex-1">
          <p class="text-sm font-bold text-slate-800 dark:text-slate-200 transition-colors group-hover:text-slate-900 dark:group-hover:text-white">
            {{ initialTab === 'income' ? 'Ingreso de Hoy' : (initialTab === 'transfer' ? 'Transferencia de Hoy' : 'Ingreso o Gasto Inmediato') }}
          </p>
          <p class="text-[10px] font-medium text-slate-500 dark:text-slate-400 mt-0.5">Registro puntual de hoy o del pasado</p>
        </div>
      </button>

      <button 
        v-if="!context || context === 'all' || context === 'planning'"
        @click="handleSelect('once')" 
        class="w-full flex items-center gap-4 p-4 bg-white/60 dark:bg-white/5 border border-slate-200/50 dark:border-white/5 rounded-2xl hover:bg-white dark:hover:bg-white/10 transition-all group shadow-sm hover:shadow-md"
      >
        <div class="w-10 h-10 rounded-xl bg-slate-100 dark:bg-white/10 text-slate-600 dark:text-slate-400 flex items-center justify-center shrink-0">
          <CalendarDays class="w-5 h-5" />
        </div>
        <div class="text-left flex-1">
          <p class="text-sm font-bold text-slate-800 dark:text-slate-200 transition-colors group-hover:text-slate-900 dark:group-hover:text-white">Evento Futuro (Único)</p>
          <p class="text-[10px] font-medium text-slate-500 dark:text-slate-400 mt-0.5">Agendar cita médica, matrícula, pago único que aun no ha ocurrido</p>
        </div>
      </button>

      <button 
        v-if="!context || context === 'all' || context === 'planning'"
        @click="handleSelect('recurring')" 
        class="w-full flex items-center gap-4 p-4 bg-white/60 dark:bg-white/5 border border-slate-200/50 dark:border-white/5 rounded-2xl hover:bg-white dark:hover:bg-white/10 transition-all group shadow-sm hover:shadow-md"
      >
        <div class="w-10 h-10 rounded-xl bg-slate-100 dark:bg-white/10 text-slate-600 dark:text-slate-400 flex items-center justify-center shrink-0">
          <CalendarClock class="w-5 h-5" />
        </div>
        <div class="text-left flex-1">
          <p class="text-sm font-bold text-slate-800 dark:text-slate-200 transition-colors group-hover:text-slate-900 dark:group-hover:text-white">Registro Recurrente</p>
          <p class="text-[10px] font-medium text-slate-500 dark:text-slate-400 mt-0.5">Salario, suscripciones, recibos o gastos fijos</p>
        </div>
      </button>

    </div>
  </GlassModal>
</template>