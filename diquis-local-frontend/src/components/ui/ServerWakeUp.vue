<script setup lang="ts">
import { Loader2, ServerCog, Coffee, RefreshCcw, WifiOff } from 'lucide-vue-next';

defineProps<{
  isWakingUp: boolean;
  message: string;
  showRetry?: boolean;
}>();

defineEmits(['retry']);
</script>

<template>
  <transition name="fade">
    <div v-if="isWakingUp" class="fixed inset-0 z-[999] flex flex-col items-center justify-center bg-slate-50/90 dark:bg-[#0a0a0a]/90 backdrop-blur-xl">
      
      <div class="flex flex-col items-center p-8 max-w-md text-center">
        <div class="relative w-24 h-24 mb-8 flex items-center justify-center">
          <div class="absolute inset-0 rounded-full blur-xl" :class="showRetry ? 'bg-red-500/20 dark:bg-red-500/10' : 'bg-emerald-500/20 dark:bg-emerald-500/10 animate-pulse'"></div>
          <div class="relative z-10 bg-white dark:bg-[#111] p-4 rounded-2xl shadow-2xl border border-slate-200/50 dark:border-white/5">
            <ServerCog v-if="!showRetry" class="w-10 h-10 text-slate-800 dark:text-white relative z-10" />
            <WifiOff v-else class="w-10 h-10 text-red-500 dark:text-red-400 relative z-10" />
            <Loader2 v-if="!showRetry" class="w-6 h-6 text-emerald-500 absolute -bottom-2 -right-2 animate-spin bg-white dark:bg-[#111] rounded-full" />
          </div>
        </div>

        <h2 class="text-2xl font-extrabold text-slate-900 dark:text-white tracking-tight mb-3">
          {{ showRetry ? 'Sin Conexión' : 'Despertando el Servidor' }}
        </h2>
        
        <p class="text-sm font-medium text-slate-500 dark:text-slate-400 mb-6">
          {{ message }}
        </p>

        <button 
          v-if="showRetry" 
          @click="$emit('retry')"
          class="flex items-center gap-2 px-6 py-3 bg-slate-900 dark:bg-white text-white dark:text-slate-900 font-bold rounded-xl shadow-lg hover:opacity-90 active:scale-95 transition-all mb-4"
        >
          <RefreshCcw class="w-4 h-4" />
          <span>Reintentar</span>
        </button>

        <div v-if="!showRetry" class="flex items-center gap-2 px-4 py-2 bg-amber-50 dark:bg-amber-500/10 border border-amber-200/50 dark:border-amber-500/20 rounded-xl text-amber-700 dark:text-amber-400 text-xs font-bold shadow-sm">
          <Coffee class="w-4 h-4" />
          <span>Toma un respiro, esto solo pasa la primera vez.</span>
        </div>
      </div>

    </div>
  </transition>
</template>

<style scoped>
.fade-enter-active, .fade-leave-active { transition: opacity 0.5s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>