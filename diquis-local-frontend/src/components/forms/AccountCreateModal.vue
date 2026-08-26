<script setup lang="ts">
import { ref, computed, watch } from 'vue';
import GlassModal from '../ui/GlassModal.vue';
import GlassSelect from '../ui/GlassSelect.vue';
import GlassCurrencySelect from '../ui/GlassCurrencySelect.vue';
import { 
  Loader2, Palette, Type, CreditCard, Wallet, 
  PiggyBank, Smartphone, Coins, TrendingDown 
} from 'lucide-vue-next';
import type { AccountCreatePayload } from '../../types/account';

const props = defineProps<{
  isOpen: boolean;
  isSaving: boolean;
}>();

const emit = defineEmits<{
  (e: 'close'): void;
  (e: 'create', payload: AccountCreatePayload): void;
}>();

const name = ref('');
const accountType = ref<'checking' | 'saving' | 'cash' | 'digital' | ''>('');
const themeColor = ref('blue');
const currency = ref('');
const allowNegative = ref(false);

const colors = [
  { id: 'blue', name: 'Azul Zafiro', hex: 'bg-blue-500', border: 'border-blue-400' },
  { id: 'red', name: 'Rojo Rubí', hex: 'bg-red-500', border: 'border-red-400' },
  { id: 'green', name: 'Verde Esmeralda', hex: 'bg-emerald-500', border: 'border-emerald-400' },
  { id: 'gold', name: 'Oro Premium', hex: 'bg-amber-400', border: 'border-amber-300' },
  { id: 'silver', name: 'Plata Clásica', hex: 'bg-slate-300', border: 'border-slate-400' },
  { id: 'black', name: 'Negro Élite', hex: 'bg-gray-900', border: 'border-gray-700' }
];

const accountTypes = [
  { id: 'checking', name: 'Cuenta Bancaria', icon: CreditCard },
  { id: 'saving', name: 'Cuenta de Ahorros', icon: PiggyBank },
  { id: 'cash', name: 'Efectivo', icon: Wallet },
  { id: 'digital', name: 'Billetera Digital', icon: Smartphone }
];

const selectedTypeIcon = computed(() => {
  const type = accountTypes.find(t => t.id === accountType.value);
  return type ? type.icon : Wallet;
});

watch(() => props.isOpen, (newVal) => {
  if (newVal) {
    name.value = '';
    accountType.value = '';
    themeColor.value = 'blue';
    currency.value = '';
    allowNegative.value = false;
  }
});

const isValid = computed(() => {
  return name.value.trim() !== '' && accountType.value !== '' && currency.value !== '';
});

const handleCreate = () => {
  if (!isValid.value) return;
  
  emit('create', {
    name: name.value.trim(),
    account_type: accountType.value as 'checking' | 'saving' | 'cash' | 'digital',
    currency: currency.value, 
    initial_balance: 0, 
    theme_color: themeColor.value,
    allow_negative_balance: allowNegative.value
  });
};
</script>

<template>
  <GlassModal :is-open="isOpen" title="Añadir Nueva Cuenta" @close="emit('close')">
    
    <div class="space-y-6">
      
      <div class="pt-2">
        <label class="flex items-center gap-2 text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-widest mb-2 ml-1">
          <Type class="w-4 h-4" /> Nombre de la Cuenta
        </label>
        <input 
          v-model="name" 
          type="text" 
          placeholder="Ej. Tarjetas de Débito, Ahorros, etc..."
          class="w-full px-4 py-3.5 bg-white/50 dark:bg-black/20 border border-slate-200/50 dark:border-white/5 rounded-xl outline-none text-slate-900 dark:text-white transition-all focus:bg-white/80 dark:focus:bg-black/40 focus:ring-2 focus:ring-slate-900/20 dark:focus:ring-white/20"
        >
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-4 relative z-40">
        <div class="relative z-30">
          <label class="flex items-center gap-2 text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-widest mb-2 ml-1">
            <Wallet class="w-4 h-4" /> Tipo
          </label>
          <GlassSelect 
            v-model="accountType" 
            :options="accountTypes" 
            placeholder="Tipo..." 
            :icon="selectedTypeIcon"
          />
        </div>

        <div class="relative z-20">
          <label class="flex items-center gap-2 text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-widest mb-2 ml-1">
            <Coins class="w-4 h-4" /> Divisa
          </label>
          <GlassCurrencySelect 
            v-model="currency"
            placeholder="Moneda..."
          />
        </div>
      </div>

      <div class="relative z-15">
        <div class="flex items-center justify-between p-4 rounded-xl bg-slate-50/80 dark:bg-black/20 border border-slate-200/50 dark:border-white/5 hover:bg-slate-100 dark:hover:bg-white/5 transition-colors">
          <div class="flex items-center gap-3">
            <div class="p-2 rounded-lg" :class="allowNegative ? 'bg-rose-100 dark:bg-rose-500/20 text-rose-600 dark:text-rose-400' : 'bg-slate-200 dark:bg-white/10 text-slate-500'">
              <TrendingDown class="w-4 h-4" />
            </div>
            <div>
              <p class="text-sm font-bold text-slate-800 dark:text-white">Admitir saldos negativos</p>
              <p class="text-[10px] sm:text-xs text-slate-500 dark:text-slate-400 mt-0.5">Permite que el balance caiga por debajo de cero</p>
            </div>
          </div>
          <button 
            @click="allowNegative = !allowNegative" 
            class="relative inline-flex h-6 w-11 items-center rounded-full transition-colors duration-300 focus:outline-none focus:ring-2 focus:ring-emerald-500/50 shrink-0"
            :class="allowNegative ? 'bg-emerald-500' : 'bg-slate-300 dark:bg-white/20'"
          >
            <span class="inline-block h-4 w-4 transform rounded-full bg-white shadow-sm transition duration-300" :class="allowNegative ? 'translate-x-6' : 'translate-x-1'" />
          </button>
        </div>
      </div>

      <div class="relative z-10">
        <label class="flex items-center gap-2 text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-widest mb-3 ml-1">
          <Palette class="w-4 h-4" /> Diseño de la Tarjeta
        </label>
        
        <div class="grid grid-cols-3 gap-3">
          <button 
            v-for="color in colors" 
            :key="color.id"
            @click="themeColor = color.id"
            class="relative flex flex-col items-center justify-center p-3 rounded-2xl border-2 transition-all duration-300 group overflow-hidden"
            :class="themeColor === color.id ? 'border-slate-800 dark:border-white bg-white/60 dark:bg-white/10 shadow-md scale-[1.02]' : 'border-transparent bg-white/30 dark:bg-black/20 hover:bg-white/50 dark:hover:bg-white/5'"
          >
            <div class="w-6 h-6 rounded-full mb-1.5 shadow-inner border transition-transform duration-300 group-hover:scale-110" :class="[color.hex, color.border]"></div>
            <span class="text-[9px] font-bold text-slate-700 dark:text-slate-300 uppercase tracking-wider text-center leading-tight">{{ color.name }}</span>
          </button>
        </div>
      </div>

    </div>

    <button 
      @click="handleCreate" 
      :disabled="isSaving || !isValid"
      class="w-full mt-8 py-4 bg-slate-900 dark:bg-white hover:bg-slate-800 dark:hover:bg-slate-200 text-white dark:text-slate-900 font-bold rounded-xl transition-all shadow-lg hover:shadow-xl flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
    >
      <Loader2 v-if="isSaving" class="animate-spin h-5 w-5" />
      <span v-else>Crear Cuenta</span>
    </button>

  </GlassModal>
</template>