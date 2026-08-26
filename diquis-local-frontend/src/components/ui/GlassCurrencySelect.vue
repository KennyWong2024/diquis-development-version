<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue';
import { ChevronDown, Coins, Search } from 'lucide-vue-next';
import { CURRENCIES } from '../../constants/currencies';

const props = defineProps<{
  modelValue: string;
  placeholder?: string;
}>();

const emit = defineEmits(['update:modelValue']);

const isOpen = ref(false);
const dropdownRef = ref<HTMLElement | null>(null);
const searchQuery = ref('');

const selectedCurrency = computed(() => {
  return CURRENCIES.find(c => c.code === props.modelValue) || null;
});

const filteredCurrencies = computed(() => {
  if (!searchQuery.value) return CURRENCIES;
  const query = searchQuery.value.toLowerCase();
  return CURRENCIES.filter(c => 
    c.name.toLowerCase().includes(query) || 
    c.code.toLowerCase().includes(query)
  );
});

const selectCurrency = (code: string) => {
  emit('update:modelValue', code);
  isOpen.value = false;
  searchQuery.value = '';
};

const toggleDropdown = () => {
  isOpen.value = !isOpen.value;
  if (isOpen.value) {
    searchQuery.value = '';
  }
};

const handleClickOutside = (e: MouseEvent) => {
  if (dropdownRef.value && !dropdownRef.value.contains(e.target as Node)) {
    isOpen.value = false;
  }
};

onMounted(() => document.addEventListener('click', handleClickOutside));
onUnmounted(() => document.removeEventListener('click', handleClickOutside));
</script>

<template>
  <div ref="dropdownRef" class="relative w-full">
    
    <button 
      type="button"
      @click="toggleDropdown"
      class="w-full flex items-center justify-between px-4 py-3.5 bg-white/50 dark:bg-black/20 border border-slate-200/50 dark:border-white/5 rounded-xl outline-none transition-all hover:bg-white/80 dark:hover:bg-black/40 focus:ring-2 focus:ring-slate-900/20 dark:focus:ring-white/20 group h-[52px]" 
    >
      <div class="flex items-center gap-3">
        <div v-if="!selectedCurrency" class="p-1.5 rounded-md bg-slate-200/50 dark:bg-white/10 text-slate-500 dark:text-slate-400 group-hover:text-slate-900 dark:group-hover:text-white transition-colors">
          <Coins class="w-4 h-4" />
        </div>
        
        <div v-else class="flex items-center gap-2">
          <img 
            :src="`https://flagcdn.com/${selectedCurrency.countryCode}.svg`" 
            :alt="selectedCurrency.code"
            class="w-[18px] h-[14px] object-cover rounded-[2px] shadow-sm"
          />
          <span class="text-sm font-semibold text-slate-900 dark:text-white leading-none">
            {{ selectedCurrency.code }}
          </span>
        </div>

        <span v-if="!selectedCurrency" class="text-sm text-slate-400 dark:text-slate-500 leading-none mt-[1px]">
          {{ placeholder || 'Moneda...' }}
        </span>
      </div>
      <ChevronDown class="w-4 h-4 text-slate-400 transition-transform duration-300" :class="{ 'rotate-180': isOpen }" />
    </button>

    <transition name="dropdown">
      <div v-if="isOpen" class="absolute z-50 w-full mt-2 p-2 rounded-2xl bg-white/95 dark:bg-[#111111]/95 backdrop-blur-2xl border border-white/50 dark:border-white/10 shadow-[0_20px_40px_rgb(0,0,0,0.15)] dark:shadow-[0_20px_40px_rgb(0,0,0,0.6)]">
        
        <div class="relative mb-2">
          <Search class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
          <input 
            v-model="searchQuery"
            type="text"
            placeholder="Buscar..."
            class="w-full pl-9 pr-3 py-2 bg-slate-100/50 dark:bg-white/5 border border-slate-200/50 dark:border-white/5 rounded-lg outline-none text-sm text-slate-900 dark:text-white focus:ring-2 focus:ring-slate-900/20 dark:focus:ring-white/20"
            @click.stop
          >
        </div>

        <div class="max-h-60 overflow-y-auto custom-scrollbar pr-1">
          <div v-if="filteredCurrencies.length === 0" class="py-4 text-center text-sm text-slate-500">
            Sin resultados.
          </div>
          
          <button
            v-for="currency in filteredCurrencies"
            :key="currency.code"
            type="button"
            @click="selectCurrency(currency.code)"
            class="w-full flex items-center justify-between px-3 py-2 rounded-xl text-left transition-colors hover:bg-slate-100/80 dark:hover:bg-white/10 mb-1"
            :class="{ 'bg-slate-100 dark:bg-white/10': modelValue === currency.code }"
          >
            <div class="flex items-center gap-3">
              <img 
                :src="`https://flagcdn.com/${currency.countryCode}.svg`" 
                :alt="currency.code"
                class="w-5 h-4 object-cover rounded-[2px] shadow-sm"
              />
              <div class="flex flex-col">
                <span class="text-sm font-bold text-slate-900 dark:text-white leading-none">{{ currency.code }}</span>
                <span class="text-[10px] text-slate-500 dark:text-slate-400 mt-0.5 truncate max-w-[100px]" :title="currency.name">{{ currency.name }}</span>
              </div>
            </div>
            <span class="text-xs font-bold text-slate-400 dark:text-slate-500 bg-slate-100 dark:bg-black/30 px-1.5 py-0.5 rounded-md">
              {{ currency.symbol }}
            </span>
          </button>
        </div>
      </div>
    </transition>
  </div>
</template>

<style scoped>
.dropdown-enter-active, .dropdown-leave-active { transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1); }
.dropdown-enter-from, .dropdown-leave-to { opacity: 0; transform: scale(0.95) translateY(-10px); }

.custom-scrollbar::-webkit-scrollbar { width: 4px; }
.custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
.custom-scrollbar::-webkit-scrollbar-thumb { background: rgba(156, 163, 175, 0.3); border-radius: 10px; }
.custom-scrollbar:hover::-webkit-scrollbar-thumb { background: rgba(156, 163, 175, 0.5); }
</style>