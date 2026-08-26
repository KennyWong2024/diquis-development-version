<script setup lang="ts">
import GlassCard from '../ui/GlassCard.vue';

defineProps<{
  title: string;
  amount: string;
  subtitle?: string;
  icon?: any;
  trend?: 'up' | 'down' | 'neutral';
}>();
</script>

<template>
  <GlassCard class="p-4 sm:p-6 lg:p-7 flex flex-col h-full justify-between">
    <div class="flex justify-between items-start mb-4">
      <p class="text-[11px] sm:text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-widest">{{ title }}</p>
      
      <div v-if="icon"
           class="p-2 rounded-xl backdrop-blur-md border shadow-sm transition-colors"
           :class="{
             'bg-emerald-50/50 dark:bg-emerald-500/10 border-emerald-200/50 dark:border-emerald-500/10 text-emerald-600/80 dark:text-emerald-400/80': trend === 'up',
             'bg-slate-100/50 dark:bg-white/5 border-slate-200/50 dark:border-white/5 text-slate-500/80 dark:text-slate-400/80': trend === 'down',
             'bg-blue-50/50 dark:bg-blue-500/10 border-blue-200/50 dark:border-blue-500/10 text-slate-600/80 dark:text-slate-300/80': trend === 'neutral'
           }">
        <component :is="icon" class="w-4 h-4" />
      </div>
    </div>

    <div>
      <h3 class="text-xl sm:text-2xl lg:text-3xl font-extrabold text-slate-900 dark:text-white truncate tracking-tight">
        {{ amount }}
      </h3>
      <p v-if="subtitle" class="text-[10px] font-bold text-slate-400 dark:text-slate-500 mt-1.5 sm:mt-2 uppercase tracking-wider">
        {{ subtitle }}
      </p>
    </div>
  </GlassCard>
</template>