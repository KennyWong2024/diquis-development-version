<script setup lang="ts">
import { ref, watch, nextTick } from 'vue';

const props = defineProps<{
  modelValue: number | string;
  placeholder?: string;
  autoFocus?: boolean;
}>();

const emit = defineEmits(['update:modelValue']);

const inputRef = ref<HTMLInputElement | null>(null);
const displayValue = ref('');

const formatLive = (val: string) => {
  const formatter = new Intl.NumberFormat('es-CR');
  const parts = formatter.formatToParts(1000);
  const groupChar = parts.find(p => p.type === 'group')?.value;

  let cleaned = val;

  if (groupChar) {
    cleaned = cleaned.split(groupChar).join('');
  }
  cleaned = cleaned.replace(/[^\d.,]/g, '');
  
  cleaned = cleaned.replace(/\./g, ',');

  const splitParts = cleaned.split(',');
  let integerPart = splitParts[0];
  let decimalPart = splitParts.length > 1 ? splitParts[1] : null;

  if (integerPart !== '') {
    const intNumber = parseInt(integerPart, 10);
    integerPart = new Intl.NumberFormat('es-CR').format(intNumber);
  }

  let finalString = integerPart;
  if (decimalPart !== null) {
    finalString += ',' + decimalPart.substring(0, 2);
  } else if (cleaned.endsWith(',')) {
    finalString += ',';
  }

  return finalString;
};

const handleInput = (event: Event) => {
  const target = event.target as HTMLInputElement;
  
  const formatted = formatLive(target.value);
  displayValue.value = formatted;

  if (formatted === '') {
    emit('update:modelValue', '');
    return;
  }

  const rawNumberString = formatted.replace(/[^0-9,]/g, '').replace(',', '.');
  const numericValue = parseFloat(rawNumberString);
  
  emit('update:modelValue', isNaN(numericValue) ? '' : numericValue);
};

watch(() => props.modelValue, (newVal) => {
  if (document.activeElement !== inputRef.value) {
    if (newVal !== '' && newVal !== null && newVal !== undefined) {
      const strVal = newVal.toString().replace('.', ',');
      displayValue.value = formatLive(strVal);
    } else {
      displayValue.value = '';
    }
  }
}, { immediate: true });

watch(() => props.autoFocus, (val) => {
  if (val) {
    nextTick(() => inputRef.value?.focus());
  }
}, { immediate: true });
</script>

<template>
  <input 
    ref="inputRef"
    v-model="displayValue" 
    type="text" 
    inputmode="decimal"
    :placeholder="placeholder || 'Precio'"
    @input="handleInput"
    class="w-full min-w-[70px] bg-white/80 dark:bg-black/20 px-2 py-1.5 rounded-lg text-sm font-bold text-right outline-none text-slate-900 dark:text-white border border-slate-200/50 dark:border-white/5 transition-all focus:bg-white dark:focus:bg-black/40 focus:ring-2 focus:ring-slate-900/20 dark:focus:ring-white/20 placeholder:text-slate-400 dark:placeholder:text-slate-600"
  >
</template>

<style scoped>
input {
  caret-color: #64748b; 
}
</style>