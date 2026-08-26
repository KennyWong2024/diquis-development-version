<script setup lang="ts">
import GlassCard from './GlassCard.vue';
import type { Component } from 'vue';

defineProps<{
  title: string;
  icon?: Component;
  iconColorClass?: string;
  iconBgClass?: string;
}>();
</script>

<template>
  <div class="space-y-3">
    <div class="flex items-center gap-3 px-2">
      <div 
        v-if="icon" 
        class="p-2 rounded-xl flex items-center justify-center shadow-sm"
        :class="iconBgClass || 'bg-slate-100 dark:bg-white/5'"
      >
        <component 
          :is="icon" 
          class="w-4 h-4" 
          :class="iconColorClass || 'text-slate-600 dark:text-slate-400'" 
        />
      </div>
      <h3 class="text-xs font-black text-slate-800 dark:text-white uppercase tracking-widest opacity-90">
        {{ title }}
      </h3>
    </div>

    <GlassCard class="p-2 sm:p-3" clip>
      <div class="flex flex-col">
        <slot />
      </div>
    </GlassCard>
  </div>
</template>
