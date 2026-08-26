<script setup lang="ts">
import { computed } from 'vue';
import { MoreVertical, Nfc, CreditCard, Wallet, PiggyBank, Smartphone } from 'lucide-vue-next';
import { CURRENCIES } from '../../constants/currencies';

const props = defineProps<{
  account: {
    id: string;
    name: string;
    current_balance: number;
    currency: string;
    account_type: string;
  };
  colorTheme?: string;
}>();

const emit = defineEmits(['edit', 'navigate']);

const colorPalettes: Record<string, string> = {
  blue: 'from-blue-500/40 via-blue-400/20 to-blue-600/40 dark:from-blue-600/50 dark:to-cyan-700/50',
  red: 'from-red-500/40 via-red-400/20 to-rose-600/40 dark:from-red-600/50 dark:to-rose-800/50',
  green: 'from-emerald-500/40 via-emerald-400/20 to-teal-600/40 dark:from-emerald-600/50 dark:to-teal-800/50',
  gold: 'from-amber-300/50 via-yellow-200/30 to-amber-500/50 dark:from-amber-400/60 dark:to-amber-700/60',
  silver: 'from-slate-300/50 via-gray-200/30 to-slate-400/50 dark:from-slate-400/40 dark:to-slate-600/40',
  black: 'from-gray-800/60 via-gray-600/40 to-black/70 dark:from-gray-800/80 dark:to-black/90'
};

const activeTheme = computed(() => {
  return props.colorTheme && colorPalettes[props.colorTheme] 
    ? colorPalettes[props.colorTheme] 
    : colorPalettes['silver'];
});

const typeIcon = computed(() => {
  switch (props.account.account_type) {
    case 'checking': return CreditCard;
    case 'saving': return PiggyBank;
    case 'cash': return Wallet;
    case 'digital': return Smartphone;
    default: return Wallet;
  }
});

const currencySymbol = computed(() => {
  const c = CURRENCIES.find(x => x.code === props.account.currency);
  return c ? c.symbol : '$';
});

const formatNumber = (val: number) => {
  return new Intl.NumberFormat('es-CR', { minimumFractionDigits: 2 }).format(val);
};

const textClass = computed(() => {
  return props.colorTheme === 'black' ? 'text-white drop-shadow-md' : 'text-slate-900 dark:text-white';
});
</script>

<template>
  <div 
    @click="emit('navigate')"
    class="relative w-full aspect-[1.58/1] rounded-3xl overflow-hidden group shadow-[0_10px_40px_rgba(0,0,0,0.08)] dark:shadow-[0_10px_40px_rgba(0,0,0,0.3)] transition-transform duration-500 hover:-translate-y-2 cursor-pointer"
  >
    
    <div class="absolute inset-0 bg-gradient-to-br opacity-100 z-0 transition-colors duration-700" :class="activeTheme"></div>
    <div class="absolute inset-0 bg-white/40 dark:bg-[#111111]/40 backdrop-blur-xl z-0"></div>
    <div class="absolute inset-0 bg-gradient-to-tr from-white/60 via-white/10 to-transparent dark:from-white/20 dark:via-white/0 dark:to-transparent opacity-70 transform -skew-x-12 translate-x-1/3 z-0 pointer-events-none"></div>

    <div class="relative z-10 h-full p-5 sm:p-6 flex flex-col justify-between" :class="textClass">
      
      <div class="flex justify-between items-start">
        <div class="flex flex-col gap-3">
          <svg class="w-10 sm:w-11 h-8 sm:h-9 opacity-90 drop-shadow-sm" viewBox="0 0 40 32" fill="none" xmlns="http://www.w3.org/2000/svg">
            <rect width="40" height="32" rx="6" fill="#FCD34D" fill-opacity="0.8" stroke="#D97706" stroke-width="0.5"/>
            <path d="M12 0v32 M28 0v32 M0 12h12 M28 12h40 M0 20h12 M28 20h40" stroke="#D97706" stroke-width="0.5" stroke-opacity="0.7"/>
            <rect x="12" y="8" width="16" height="16" rx="2" stroke="#D97706" stroke-width="0.5" stroke-opacity="0.7"/>
          </svg>
          
          <div class="flex items-center gap-2 opacity-80">
            <component :is="typeIcon" class="w-3.5 h-3.5 sm:w-4 sm:h-4" />
            <span class="text-[9px] sm:text-[10px] uppercase font-bold tracking-widest">{{ account.account_type }}</span>
          </div>
        </div>

        <button 
          @click.stop="emit('edit')" 
          class="p-1.5 rounded-full hover:bg-black/10 dark:hover:bg-white/10 transition-colors backdrop-blur-md relative z-50"
        >
          <MoreVertical class="w-4 h-4 sm:w-5 sm:h-5" />
        </button>
      </div>

      <div class="flex justify-between items-end">
        <div class="flex flex-col max-w-[80%]">
          <p class="text-[10px] sm:text-xs font-semibold opacity-70 uppercase tracking-widest mb-1 drop-shadow-sm truncate">{{ account.name }}</p>
          
          <h3 class="text-2xl sm:text-4xl font-black tracking-tighter drop-shadow-sm flex items-baseline gap-1 truncate">
            <span class="text-base sm:text-2xl opacity-80 font-extrabold">{{ currencySymbol }}</span>
            <span class="truncate">{{ formatNumber(account.current_balance) }}</span>
          </h3>
        </div>
        <Nfc class="w-6 h-6 sm:w-8 sm:h-8 opacity-50 drop-shadow-sm rotate-90 shrink-0" />
      </div>
    </div>

    <div class="absolute inset-0 rounded-3xl border-2 border-white/50 dark:border-white/10 pointer-events-none z-20 mix-blend-overlay"></div>
  </div>
</template>