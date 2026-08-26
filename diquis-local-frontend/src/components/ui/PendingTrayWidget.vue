<script setup lang="ts">
import { computed } from 'vue';
import { useScheduledStore } from '../../stores/scheduled';
import { BellRing, CheckCircle, ChevronRight } from 'lucide-vue-next';
import PendingTrayItem from './PendingTrayItem.vue';
import GlassCard from './GlassCard.vue';

const scheduledStore = useScheduledStore();
const emit = defineEmits(['execute']); 

const pendings = computed(() => scheduledStore.pendingSchedules.slice(0, 5));
const hiddenCount = computed(() => Math.max(0, scheduledStore.pendingSchedules.length - 5));
</script>

<template>
  <GlassCard class="p-4 sm:p-7 flex flex-col h-full relative group">
    
    <div class="flex items-center justify-between mb-4 sm:mb-6 relative z-10">
      <div class="flex items-center gap-2 sm:gap-3">
        <div class="w-8 h-8 rounded-full bg-slate-200/50 dark:bg-white/5 flex items-center justify-center border border-slate-300/50 dark:border-white/5 shadow-inner">
            <BellRing class="w-4 h-4 text-slate-700 dark:text-slate-300" />
        </div>
        <h3 class="text-sm font-bold text-slate-800 dark:text-white uppercase tracking-wider">Atención Requerida</h3>
      </div>
      <span v-if="scheduledStore.pendingSchedules.length > 0" class="text-[10px] font-extrabold px-2 py-1 bg-amber-50 dark:bg-amber-500/10 text-amber-600 dark:text-amber-400 border border-amber-200/50 dark:border-amber-500/20 rounded-lg uppercase tracking-widest shadow-sm">
        {{ scheduledStore.pendingSchedules.length }} <span class="hidden sm:inline">esperando</span>
      </span>
    </div>

    <div v-if="scheduledStore.pendingSchedules.length === 0" class="flex-1 flex flex-col items-center justify-center py-8 sm:py-12 text-center border border-dashed border-slate-200 dark:border-white/10 rounded-2xl bg-slate-50/50 dark:bg-white/[0.02]">
        <div class="mx-auto w-12 h-12 bg-emerald-50 dark:bg-emerald-500/10 rounded-full flex items-center justify-center mb-3">
          <CheckCircle class="w-5 h-5 text-emerald-500" />
        </div>
        <p class="font-medium text-slate-700 dark:text-slate-300">¡Todo bajo control!</p>
        <p class="text-xs mt-1 opacity-70 max-w-[200px] mx-auto">No hay pagos ni ingresos programados para hoy</p>
    </div>

    <div v-else class="space-y-1 flex-1 relative z-10 flex flex-col justify-between">
        <div class="space-y-1">
            <PendingTrayItem 
                v-for="sched in pendings" 
                :key="sched.id"
                :sched="sched"
                @manage="emit('execute', $event)" 
            />
        </div>
        
        <router-link 
            v-if="hiddenCount > 0" 
            to="/proyecciones" 
            class="mt-4 pt-4 border-t border-slate-200/50 dark:border-white/5 flex items-center justify-center gap-1 w-full text-center text-[10px] sm:text-[11px] font-bold uppercase tracking-widest text-slate-500 hover:text-slate-900 dark:text-slate-400 dark:hover:text-white transition-colors group/link"
        >
            Ver {{ hiddenCount }} compromisos más <span class="hidden sm:inline">en proyecciones</span>
            <ChevronRight class="w-3 h-3 group-hover/link:translate-x-0.5 transition-transform" />
        </router-link>
    </div>
  </GlassCard>
</template>