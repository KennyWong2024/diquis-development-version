<script setup lang="ts">
import { X } from 'lucide-vue-next';
import { watch, onUnmounted } from 'vue';
import { registerBackHandler, unregisterBackHandler } from '../../composables/useBackButton';

const props = defineProps<{ 
  isOpen: boolean; 
  title?: string;
}>();

const emit = defineEmits(['close']);

// ID único por instancia de drawer
const handlerId = `drawer-${Math.random().toString(36).substring(2, 9)}`;

watch(() => props.isOpen, (val) => {
  if (val) {
    document.body.style.overflow = 'hidden';
    // Prioridad 90: menor que modales (100) para que si un modal está sobre un drawer,
    // el back cierre primero el modal
    registerBackHandler(handlerId, () => emit('close'), 90);
  } else {
    document.body.style.overflow = 'auto';
    unregisterBackHandler(handlerId);
  }
});

onUnmounted(() => {
  unregisterBackHandler(handlerId);
});
</script>

<template>
  <Teleport to="body">
    <transition name="drawer-fade">
      <div v-if="isOpen" class="fixed inset-0 z-[200] flex justify-end">
        
        <div 
          class="absolute inset-0 bg-slate-900/40 dark:bg-[#080808]/60 backdrop-blur-[2px] transition-opacity"
          @click="emit('close')"
        ></div>

        <transition name="drawer-slide" appear>
          <div class="relative w-full max-w-md h-full bg-white/80 dark:bg-[#111111]/90 backdrop-blur-3xl border-l border-white/50 dark:border-white/5 shadow-2xl flex flex-col transform transition-all overflow-hidden z-10">
            
            <div class="absolute inset-y-0 left-0 w-px bg-white/60 dark:bg-white/10 pointer-events-none"></div>

            <div class="flex items-center justify-between p-6 border-b border-slate-200/50 dark:border-white/5 shrink-0 relative z-20 bg-white/30 dark:bg-black/10">
              <h2 v-if="title" class="text-lg font-extrabold text-slate-900 dark:text-white tracking-tight">{{ title }}</h2>
              <div v-else></div> <button 
                @click="emit('close')" 
                class="p-2 -mr-2 rounded-full bg-white/50 dark:bg-white/5 hover:bg-slate-200/50 dark:hover:bg-white/10 text-slate-500 dark:text-slate-400 transition-colors"
              >
                <X class="w-5 h-5" />
              </button>
            </div>

            <div class="flex-1 overflow-y-auto p-6 relative z-20 custom-scrollbar">
              <slot />
            </div>

          </div>
        </transition>

      </div>
    </transition>
  </Teleport>
</template>

<style scoped>
.drawer-fade-enter-active, .drawer-fade-leave-active { transition: opacity 0.3s ease; }
.drawer-fade-enter-from, .drawer-fade-leave-to { opacity: 0; }

.drawer-slide-enter-active, .drawer-slide-leave-active { transition: transform 0.4s cubic-bezier(0.16, 1, 0.3, 1); }
.drawer-slide-enter-from, .drawer-slide-leave-to { transform: translateX(100%); }

.custom-scrollbar::-webkit-scrollbar { width: 6px; }
.custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
.custom-scrollbar::-webkit-scrollbar-thumb { background: rgba(150, 150, 150, 0.3); border-radius: 10px; }
:global(.dark) .custom-scrollbar::-webkit-scrollbar-thumb { background: rgba(255, 255, 255, 0.1); }
</style>