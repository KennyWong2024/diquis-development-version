<script setup lang="ts">
import { computed, ref, watch } from 'vue';
import { Calendar } from 'lucide-vue-next';

const props = defineProps<{
  modelValue: Date;
}>();

const emit = defineEmits(['update:modelValue', 'toggle']);

const nativeInputRef = ref<HTMLInputElement | null>(null);

const formatToInput = (date: Date): string => {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  const hours = String(date.getHours()).padStart(2, '0');
  const minutes = String(date.getMinutes()).padStart(2, '0');
  return `${year}-${month}-${day}T${hours}:${minutes}`;
};

const localDateString = ref(formatToInput(props.modelValue));

watch(() => props.modelValue, (newVal) => {
  localDateString.value = formatToInput(newVal);
});

const handleInput = (event: Event) => {
  const target = event.target as HTMLInputElement;
  if (!target.value) return;
  
  const newDate = new Date(target.value);
  emit('update:modelValue', newDate);
};

const triggerPicker = () => {
  emit('toggle', true);
  
  if (nativeInputRef.value && typeof nativeInputRef.value.showPicker === 'function') {
    try {
      nativeInputRef.value.showPicker();
    } catch (err) {
      console.warn("Navegador utiliza comportamiento nativo por defecto.");
    }
  }
};

const displayValue = computed(() => {
  return new Intl.DateTimeFormat('es-CR', { 
    day: '2-digit', 
    month: 'short', 
    year: 'numeric', 
    hour: '2-digit', 
    minute: '2-digit' 
  }).format(props.modelValue);
});
</script>

<template>
  <div class="relative group w-full">
    
    <div 
      class="w-full flex items-center pl-12 pr-4 py-3.5 bg-white/50 dark:bg-black/20 border border-slate-200/50 dark:border-white/5 rounded-xl text-left transition-all duration-300 group-focus-within:bg-white/80 dark:group-focus-within:bg-black/40 group-focus-within:ring-2 group-focus-within:ring-slate-900/20 dark:group-focus-within:ring-white/20"
    >
      <Calendar class="absolute left-4 h-5 w-5 text-slate-400 dark:text-slate-500 group-hover:text-slate-600 dark:group-hover:text-slate-300 transition-colors" />
      <span class="flex-1 text-sm font-semibold text-slate-900 dark:text-white truncate tracking-wide capitalize">
        {{ displayValue }}
      </span>
    </div>

    <input 
      ref="nativeInputRef"
      type="datetime-local"
      v-model="localDateString"
      @input="handleInput"
      @click="triggerPicker"
      class="date-overlay-input absolute inset-0 w-full h-full opacity-0 cursor-pointer z-10"
    />
    
  </div>
</template>

<style scoped>
.date-overlay-input::-webkit-calendar-picker-indicator {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  margin: 0;
  padding: 0;
  cursor: pointer;
}
</style>