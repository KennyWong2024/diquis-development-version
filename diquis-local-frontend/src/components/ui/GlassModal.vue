<script setup lang="ts">
import { X } from 'lucide-vue-next';
import { watch, onUnmounted } from 'vue';
import { registerBackHandler, unregisterBackHandler } from '../../composables/useBackButton';

const props = withDefaults(defineProps<{ 
  isOpen: boolean; 
  title: string;
  scrollable?: boolean;
  noPadding?: boolean;
}>(), {
  scrollable: true,
  noPadding: false
});

const emit = defineEmits(['close']);

// ID único por instancia de modal para soportar múltiples modales simultáneos
const handlerId = `modal-${Math.random().toString(36).substring(2, 9)}`;

watch(() => props.isOpen, (val) => {
  if (val) {
    document.body.style.overflow = 'hidden';
    registerBackHandler(handlerId, () => emit('close'), 100);
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
    <transition name="modal">
      <div v-if="isOpen" class="fixed inset-0 z-[100] flex items-center justify-center p-4 sm:p-6">
        
        <div 
          class="absolute inset-0 bg-slate-900/60 dark:bg-[#080808]/80 backdrop-blur-sm transition-opacity"
          @click="emit('close')"
        ></div>

        <div class="relative w-full max-w-lg rounded-[2rem] bg-white/70 dark:bg-[#111111]/80 backdrop-blur-2xl border border-white/50 dark:border-white/5 shadow-2xl flex flex-col max-h-[90vh] overflow-hidden transform transition-all">
          
          <div class="absolute inset-0 rounded-[inherit] border-t border-white/60 dark:border-white/10 pointer-events-none z-20"></div>

          <div class="flex items-center justify-between p-6 border-b border-slate-200/50 dark:border-white/5 shrink-0 z-30 relative">
            <h2 class="text-xl font-extrabold text-slate-900 dark:text-white tracking-tight">{{ title }}</h2>
            <button 
              @click="emit('close')" 
              class="p-2 rounded-full bg-white/50 dark:bg-white/5 hover:bg-slate-200/50 dark:hover:bg-white/10 text-slate-500 dark:text-slate-400 transition-colors"
            >
              <X class="w-5 h-5" />
            </button>
          </div>

          <div 
            class="flex-1 z-30 relative flex flex-col min-h-0"
            :class="[
              scrollable ? 'overflow-y-auto custom-scrollbar' : 'overflow-hidden',
              noPadding ? '' : 'p-6'
            ]"
          >
            <slot />
          </div>

        </div>
      </div>
    </transition>
  </Teleport>
</template>

<style scoped>
.modal-enter-active, .modal-leave-active { transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1); }
.modal-enter-from, .modal-leave-to { opacity: 0; transform: scale(0.95) translateY(10px); }

.custom-scrollbar::-webkit-scrollbar { width: 6px; }
.custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
.custom-scrollbar::-webkit-scrollbar-thumb { background: rgba(150, 150, 150, 0.3); border-radius: 10px; }
:global(.dark) .custom-scrollbar::-webkit-scrollbar-thumb { background: rgba(255, 255, 255, 0.1); }
</style>