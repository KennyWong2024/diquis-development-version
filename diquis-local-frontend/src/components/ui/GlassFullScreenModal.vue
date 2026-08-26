<script setup lang="ts">
import { X } from 'lucide-vue-next';

defineProps<{
  isOpen: boolean;
  title: string;
}>();

defineEmits(['close']);
</script>

<template>
  <Teleport to="body">
    <transition name="slide-up-full">
      <div 
        v-if="isOpen" 
        class="fixed inset-0 z-[9999] flex flex-col bg-[#fbfbfb]/98 dark:bg-[#050505]/98 backdrop-blur-3xl overflow-hidden"
      >
        <header class="flex-none pt-safe px-4 h-[72px] flex items-center justify-between border-b border-slate-200/50 dark:border-white/5 bg-white/50 dark:bg-black/20 backdrop-blur-md relative z-20">
          <button 
            @click="$emit('close')" 
            class="p-2 -ml-2 rounded-full active:scale-90 transition-transform text-slate-500 dark:text-slate-400 hover:bg-slate-200/50 dark:hover:bg-white/10"
          >
             <X class="w-6 h-6" />
          </button>
          
          <h2 class="text-lg font-black text-slate-900 dark:text-white tracking-tight truncate px-4">
            {{ title }}
          </h2>
          
          <div class="w-10"></div> </header>

        <main class="flex-1 overflow-y-auto custom-scrollbar relative z-10">
          <div class="p-5 pb-32"> <slot />
          </div>
        </main>

        <div class="fixed bottom-0 inset-x-0 pb-safe p-5 bg-gradient-to-t from-[#fbfbfb] via-[#fbfbfb]/95 to-transparent dark:from-[#050505] dark:via-[#050505]/95 z-20 pointer-events-none">
           <div class="pointer-events-auto">
              <slot name="footer" />
           </div>
        </div>

      </div>
    </transition>
  </Teleport>
</template>

<style scoped>
.slide-up-full-enter-active, .slide-up-full-leave-active {
  transition: transform 0.35s cubic-bezier(0.16, 1, 0.3, 1), opacity 0.35s ease;
}
.slide-up-full-enter-from, .slide-up-full-leave-to {
  transform: translateY(100%);
  opacity: 0.5;
}
.pt-safe { padding-top: env(safe-area-inset-top); }
.pb-safe { padding-bottom: env(safe-area-inset-bottom, 1rem); }
.custom-scrollbar::-webkit-scrollbar { width: 0px; background: transparent; }
</style>
