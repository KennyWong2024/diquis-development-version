<script setup lang="ts">
import { computed } from 'vue';
import { CURRENCIES } from '../../constants/currencies';

const props = defineProps<{
  account: {
    id: string;
    name: string;
    current_balance: number;
    currency: string;
    account_type: string;
    theme_color?: string; 
  };
  isSelected: boolean;
}>();

const colorPalettes: Record<string, string> = {
  blue: 'from-blue-500/40 via-blue-400/20 to-blue-600/40 dark:from-blue-600/50 dark:to-cyan-700/50',
  red: 'from-red-500/40 via-red-400/20 to-rose-600/40 dark:from-red-600/50 dark:to-rose-800/50',
  green: 'from-emerald-500/40 via-emerald-400/20 to-teal-600/40 dark:from-emerald-600/50 dark:to-teal-800/50',
  gold: 'from-amber-300/50 via-yellow-200/30 to-amber-500/50 dark:from-amber-400/60 dark:to-amber-700/60',
  silver: 'from-slate-300/50 via-gray-200/30 to-slate-400/50 dark:from-slate-400/40 dark:to-slate-600/40',
  black: 'from-gray-800/60 via-gray-600/40 to-black/70 dark:from-gray-800/80 dark:to-black/90'
};

const activeTheme = computed(() => {
  const theme = props.account.theme_color || 'silver';
  return colorPalettes[theme] || colorPalettes['silver'];
});

const currencySymbol = computed(() => {
  const c = CURRENCIES.find(x => x.code === props.account.currency);
  return c ? c.symbol : '$';
});

const formatNumber = (val: number) => {
  return new Intl.NumberFormat('es-CR', { minimumFractionDigits: 2 }).format(val);
};

const textClass = computed(() => {
  const theme = props.account.theme_color || 'silver';
  return theme === 'black' ? 'text-white drop-shadow-md' : 'text-slate-900 dark:text-white';
});
</script>

<template>
  <div
    class="relative cursor-pointer rounded-2xl flex flex-col justify-between transition-all duration-300 ease-out overflow-hidden group shrink-0"
    :class="[
      isSelected 
        ? 'w-[160px] sm:w-[180px] h-[100px] sm:h-[110px] shadow-[0_8px_20px_rgba(0,0,0,0.08)] dark:shadow-[0_8px_20px_rgba(0,0,0,0.3)] scale-100 grayscale-0 opacity-100' 
        : 'w-[140px] sm:w-[160px] h-[85px] sm:h-[95px] bg-white/30 dark:bg-white/5 border border-white/20 dark:border-white/5 opacity-60 hover:opacity-80 grayscale hover:grayscale-[50%] scale-95 shadow-sm'
    ]"
  >
    <div v-if="isSelected" class="absolute inset-0 bg-gradient-to-br opacity-100 z-0 transition-colors duration-700" :class="activeTheme"></div>
    <div v-if="isSelected" class="absolute inset-0 bg-white/40 dark:bg-[#111111]/40 backdrop-blur-xl z-0"></div>
    <div v-if="isSelected" class="absolute inset-0 bg-gradient-to-tr from-white/60 via-white/10 to-transparent dark:from-white/20 dark:via-white/0 dark:to-transparent opacity-70 transform -skew-x-12 translate-x-1/3 z-0 pointer-events-none"></div>

    <div class="relative z-10 h-full p-3 sm:p-4 flex flex-col justify-between" :class="isSelected ? textClass : 'text-slate-600 dark:text-slate-300'">
      
      <div class="flex justify-between items-start gap-2">
        <svg class="w-[18px] sm:w-[22px] h-[14px] sm:h-[18px] opacity-80 drop-shadow-sm shrink-0" viewBox="0 0 40 32" fill="none" xmlns="http://www.w3.org/2000/svg" :class="!isSelected ? 'grayscale opacity-50' : ''">
          <rect width="40" height="32" rx="6" fill="#FCD34D" fill-opacity="0.8" stroke="#D97706" stroke-width="0.5"/>
          <path d="M12 0v32 M28 0v32 M0 12h12 M28 12h40 M0 20h12 M28 20h40" stroke="#D97706" stroke-width="0.5" stroke-opacity="0.7"/>
          <rect x="12" y="8" width="16" height="16" rx="2" stroke="#D97706" stroke-width="0.5" stroke-opacity="0.7"/>
        </svg>

        <p class="text-[8px] sm:text-[9px] font-bold tracking-widest uppercase truncate text-right mt-0.5 opacity-80 drop-shadow-sm">
          {{ account.name }}
        </p>
      </div>

      <div class="flex flex-col">
        <p class="text-[8px] sm:text-[9px] uppercase tracking-wider mb-0.5 opacity-60 font-bold" v-if="isSelected">Balance</p>
        
        <h3 class="text-sm sm:text-base font-black tracking-tight drop-shadow-sm flex items-baseline gap-0.5 truncate">
          <span class="text-[10px] sm:text-xs opacity-80 font-extrabold">{{ currencySymbol }}</span>
          <span class="truncate">{{ formatNumber(account.current_balance) }}</span>
        </h3>
      </div>
    </div>

    <div v-if="isSelected" class="absolute inset-0 rounded-2xl border-2 border-white/50 dark:border-white/10 pointer-events-none z-20 mix-blend-overlay"></div>
  </div>
</template>