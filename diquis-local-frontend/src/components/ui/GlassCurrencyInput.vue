<script setup lang="ts">
import { ref, watch, nextTick, computed } from 'vue';

const props = defineProps<{
  modelValue: number | string;
  type?: 'expense' | 'income' | 'transfer';
  autoFocus?: boolean;
  readonly?: boolean;
  symbol?: string;
}>();

const emit = defineEmits(['update:modelValue']);

const inputRef = ref<HTMLInputElement | null>(null);
const displayValue = ref('');

const dynamicFontSize = computed(() => {
  const len = displayValue.value.length;
  if (len < 7) return 'text-6xl md:text-7xl';
  if (len < 10) return 'text-5xl md:text-6xl';
  if (len < 13) return 'text-4xl md:text-5xl';
  return 'text-3xl md:text-4xl';
});

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
  <div class="flex justify-center items-center gap-1 w-full px-2">
    <span class="font-extrabold text-slate-300 dark:text-slate-600 transition-all duration-200" 
          :class="dynamicFontSize.includes('6xl') ? 'text-3xl' : 'text-2xl'">
      {{ symbol || '₡' }}
    </span>
    
    <input 
      ref="inputRef"
      v-model="displayValue" 
      type="text" 
      inputmode="decimal"
      placeholder="0,00"
      @input="handleInput"
      :readonly="readonly" class="bg-transparent font-black w-full text-center outline-none placeholder:text-slate-300 dark:placeholder:text-slate-700 text-slate-900 dark:text-white transition-all duration-200 ease-out"
      :class="dynamicFontSize"
    >
  </div>
</template>

<style scoped>
input {
  caret-color: #64748b; 
}
</style>