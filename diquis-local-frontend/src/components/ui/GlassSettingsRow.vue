<script setup lang="ts">
import { ChevronRight } from 'lucide-vue-next';
import type { Component } from 'vue';

defineProps<{
  title: string;
  subtitle?: string;
  icon?: Component;
  isLast?: boolean;
  clickable?: boolean;
  showChevron?: boolean;
}>();

defineEmits(['click']);
</script>

<template>
  <div 
    @click="clickable ? $emit('click') : null"
    class="flex items-center justify-between p-3 rounded-2xl transition-all duration-300"
    :class="[
      !isLast ? 'border-b border-slate-200/50 dark:border-white/5 pb-4 mb-1' : '',
      clickable ? 'cursor-pointer hover:bg-slate-50/50 dark:hover:bg-white/5 active:scale-[0.98]' : ''
    ]"
  >
    <div class="flex items-center gap-4">
      <div v-if="icon" class="text-slate-400 dark:text-slate-500">
        <component :is="icon" class="w-5 h-5" />
      </div>

      <div class="flex flex-col justify-center">
        <span class="text-sm font-bold text-slate-800 dark:text-white">{{ title }}</span>
        <span v-if="subtitle" class="text-xs text-slate-500 dark:text-slate-400 mt-0.5 font-medium leading-tight">
          {{ subtitle }}
        </span>
      </div>
    </div>

    <div class="flex items-center gap-2 text-slate-400">
      <slot name="action">
        <ChevronRight v-if="showChevron" class="w-4 h-4" />
      </slot>
    </div>
  </div>
</template>
