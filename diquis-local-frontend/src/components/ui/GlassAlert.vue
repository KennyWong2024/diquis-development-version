<script setup lang="ts">
import { computed, watch } from 'vue';
import { AlertCircle, CheckCircle2, Info, Loader2 } from 'lucide-vue-next';

const props = defineProps<{
  show: boolean;
  message: string;
  type?: 'error' | 'success' | 'warning' | 'info';
  autoClose?: number;
  isConfirm?: boolean;
  confirmText?: string;
  cancelText?: string;
  isLoading?: boolean;
}>();

const emit = defineEmits(['update:show', 'close', 'confirm', 'cancel']);

const closeAlert = () => {
  if (props.isLoading) return;
  emit('update:show', false);
  emit('close');
};

const handleConfirm = () => {
  if (props.isLoading) return;
  emit('confirm'); 
  if (!props.isLoading) {
    emit('update:show', false);
  }
};

const handleCancel = () => {
  if (props.isLoading) return;
  emit('update:show', false);
  emit('cancel');
};

watch(() => props.show, (newVal) => {
  if (newVal && props.autoClose && !props.isConfirm) {
    setTimeout(() => {
      closeAlert();
    }, props.autoClose);
  }
});

const themeClasses = computed(() => {
  switch (props.type) {
    case 'error': 
      return 'bg-rose-500/95 dark:bg-rose-600/95 border-rose-400/50 shadow-[0_0_40px_rgba(244,63,94,0.4)]';
    case 'success': 
      return 'bg-emerald-500/95 dark:bg-emerald-600/95 border-emerald-400/50 shadow-[0_0_40px_rgba(16,185,129,0.4)]';
    case 'warning': 
      return 'bg-amber-500/95 dark:bg-amber-600/95 border-amber-400/50 shadow-[0_0_40px_rgba(245,158,11,0.4)]';
    default: 
      return 'bg-slate-800/95 dark:bg-slate-700/95 border-slate-600/50 shadow-[0_0_40px_rgba(15,23,42,0.4)]';
  }
});

const buttonClasses = computed(() => {
  switch (props.type) {
    case 'error': return 'bg-rose-700 hover:bg-rose-800 text-white';
    case 'success': return 'bg-emerald-700 hover:bg-emerald-800 text-white';
    case 'warning': return 'bg-amber-700 hover:bg-amber-800 text-white';
    default: return 'bg-slate-900 hover:bg-black text-white';
  }
});

const Icon = computed(() => {
  switch (props.type) {
    case 'error': return AlertCircle;
    case 'success': return CheckCircle2;
    default: return Info;
  }
});
</script>

<template>
  <transition name="alert-pop">
    <div 
      v-if="show" 
      class="fixed inset-0 z-[99999] flex items-center justify-center p-4 sm:p-6 bg-slate-900/40 dark:bg-black/60 backdrop-blur-md"
    >
      <div 
        class="relative w-full max-w-sm p-6 sm:p-8 rounded-[2.5rem] border text-white flex flex-col items-center text-center backdrop-blur-2xl shadow-2xl" 
        :class="themeClasses"
      >
        <div class="w-16 h-16 sm:w-20 sm:h-20 rounded-full bg-white/20 flex items-center justify-center mb-5 sm:mb-6 shadow-inner border border-white/20"
             :class="{ 'animate-bounce': type === 'error' && isConfirm }">
          <component :is="Icon" class="w-8 h-8 sm:w-10 sm:h-10 drop-shadow-md" />
        </div>
        
        <h4 class="text-lg sm:text-xl font-black tracking-tight mb-2 uppercase drop-shadow-sm">
          {{ type === 'error' ? (isConfirm ? 'Advertencia' : 'Error') : type === 'success' ? 'Éxito' : 'Aviso' }}
        </h4>
        
        <p class="text-sm sm:text-base font-medium leading-relaxed opacity-95 mb-8 drop-shadow-sm">
          {{ message }}
        </p>

        <slot />

        <div v-if="isConfirm" class="w-full flex gap-3">
          <button 
            @click="handleCancel" 
            :disabled="isLoading"
            class="flex-1 py-3.5 sm:py-4 rounded-[1.25rem] font-bold tracking-wide transition-all shadow-sm active:scale-95 border border-white/30 bg-transparent hover:bg-white/10 text-white disabled:opacity-50"
          >
            {{ cancelText || 'Cancelar' }}
          </button>
          <button 
            @click="handleConfirm" 
            :disabled="isLoading"
            class="flex-1 flex items-center justify-center gap-2 py-3.5 sm:py-4 rounded-[1.25rem] font-bold tracking-wide transition-all shadow-lg active:scale-95 border border-white/10 disabled:opacity-80" 
            :class="buttonClasses"
          >
            <Loader2 v-if="isLoading" class="w-5 h-5 animate-spin" />
            <span v-else>{{ confirmText || 'Confirmar' }}</span>
          </button>
        </div>
        
        <button 
          v-else
          @click="closeAlert" 
          class="w-full py-3.5 sm:py-4 rounded-[1.25rem] font-bold tracking-wide transition-all shadow-lg active:scale-95 border border-white/10" 
          :class="buttonClasses"
        >
          Entendido
        </button>

      </div>
    </div>
  </transition>
</template>

<style scoped>
.alert-pop-enter-active, .alert-pop-leave-active { 
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1); 
}
.alert-pop-enter-from, .alert-pop-leave-to { 
  opacity: 0; 
  transform: scale(0.9) translateY(20px); 
}
</style>