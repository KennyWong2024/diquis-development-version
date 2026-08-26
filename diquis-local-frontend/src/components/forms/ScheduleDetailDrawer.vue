<script setup lang="ts">
import { ref, watch, computed } from 'vue';
import { useFinanceStore } from '../../stores/finance';
import { useCategoryStore } from '../../stores/category'; 
import { scheduledService } from '../../services/scheduledService';
import type { ScheduledUpdate } from '../../types/scheduled';
import type { Category } from '../../types/category'; 
import { resolveIcon } from '../../utils/icons';
import { CURRENCIES } from '../../constants/currencies';
import GlassDrawer from '../ui/GlassDrawer.vue';
import ScheduleEditForm from './ScheduleEditForm.vue';
import GlassAlert from '../ui/GlassAlert.vue';
import { 
  Loader2, Trash2, Edit2, Calendar, Wallet, Type, ArrowRightLeft, TrendingDown, TrendingUp, Star
} from 'lucide-vue-next';

const props = defineProps<{ 
  isOpen: boolean;
  scheduleId?: string | null;
  scheduleData?: any | null; 
}>();

const emit = defineEmits(['close', 'updated']);
const financeStore = useFinanceStore();
const categoryStore = useCategoryStore(); 

const isEditing = ref(false);
const isSavingEdit = ref(false);
const isDeleting = ref(false);
const showDeleteConfirm = ref(false);
const localScheduleData = ref<any>(null);
const apiError = ref('');
const showErrorPopup = ref(false);

const frequencies = [
  { id: 'daily', name: 'Diario' }, { id: 'weekly', name: 'Semanal' }, { id: 'biweekly', name: 'Quincenal' },
  { id: 'monthly', name: 'Mensual' }, { id: 'quarterly', name: 'Trimestral' }, { id: 'yearly', name: 'Anual' }
];

const handleCloseError = () => {
  showErrorPopup.value = false;
  apiError.value = '';
};

const formatCurrency = (val: number, currencyCode?: string) => {
  const num = new Intl.NumberFormat('es-CR', { minimumFractionDigits: 2 }).format(val);
  if (currencyCode) {
    const c = CURRENCIES.find(x => x.code === currencyCode);
    return `${c ? c.symbol : '$'}${num}`;
  }
  return num;
};

const formatDate = (dateStr: string) => {
  if (!dateStr) return '';
  const [year, month, day] = dateStr.split('T')[0].split('-').map(Number);
  const localDate = new Date(year, month - 1, day);
  return new Intl.DateTimeFormat('es-CR', { day: '2-digit', month: 'short', year: 'numeric' }).format(localDate);
};

watch(() => props.isOpen, (isOpen) => {
  if (isOpen && props.scheduleData) {
    showDeleteConfirm.value = false;
    isEditing.value = false; 
    apiError.value = '';
    showErrorPopup.value = false;
    localScheduleData.value = { ...props.scheduleData };
  } else {
    localScheduleData.value = null;
    isEditing.value = false;
  }
});

const categoryName = computed(() => {
  if (!localScheduleData.value) return '';
  const cat = categoryStore.categories.find((c: Category) => c.id === localScheduleData.value.category_id); 
  return cat ? cat.name : 'General';
});

const accountName = computed(() => {
  if (!localScheduleData.value) return '';
  const acc = financeStore.accounts.find(a => a.id === localScheduleData.value.account_id);
  return acc ? acc.name : 'Cuenta Desconocida';
});

const headerIconInfo = computed(() => {
  if (!localScheduleData.value) return { icon: TrendingDown, color: 'text-slate-400' };
  const cat = categoryStore.categories.find((c: Category) => c.id === localScheduleData.value.category_id); 
  
  if (cat) {
      return { 
          icon: resolveIcon(cat.icon), 
          color: localScheduleData.value.type === 'income' ? 'text-emerald-500' : 'text-slate-700 dark:text-slate-300' 
      };
  }

  if (localScheduleData.value.type === 'income') return { icon: TrendingUp, color: 'text-emerald-500' };
  if (localScheduleData.value.type === 'expense') return { icon: TrendingDown, color: 'text-slate-700 dark:text-slate-300' };
  return { icon: ArrowRightLeft, color: 'text-slate-500' };
});

const handleUpdate = async (updateData: ScheduledUpdate) => {
  if (!props.scheduleId) return;
  
  isSavingEdit.value = true;
  apiError.value = '';
  showErrorPopup.value = false;

  try {
    await scheduledService.updateScheduled(props.scheduleId, updateData);
    
    // Si todo salió bien: Actualizamos la lista padre y cerramos el Drawer.
    emit('updated');
    emit('close'); 
    isEditing.value = false; // Reiniciar estado para la próxima vez
    
  } catch (error: any) {
    apiError.value = error.response?.data?.detail || "Error al actualizar la programación.";
    showErrorPopup.value = true;
  } finally {
    isSavingEdit.value = false;
  }
};

const handleDelete = async () => {
  if (!showDeleteConfirm.value) {
    showDeleteConfirm.value = true;
    return;
  }
  
  isDeleting.value = true;
  try {
    if (props.scheduleId) {
      await scheduledService.deleteScheduled(props.scheduleId);
      emit('updated');
      emit('close');
    }
  } catch (error: any) {
    apiError.value = error.response?.data?.detail || "Error al eliminar.";
    showErrorPopup.value = true;
    showDeleteConfirm.value = false;
  } finally {
    isDeleting.value = false;
  }
};
</script>

<template>
  <GlassDrawer :is-open="isOpen" :title="isEditing ? 'Editar Programación' : 'Detalle de Programación'" @close="emit('close')">
    
    <GlassAlert 
      :show="showErrorPopup" 
      :message="apiError" 
      :type="'error'" 
      @close="handleCloseError" 
    />

    <div v-if="!localScheduleData" class="flex justify-center py-10">
      <Loader2 class="w-8 h-8 animate-spin text-slate-400" />
    </div>

    <div v-else-if="isEditing" class="h-full">
      <ScheduleEditForm 
        :schedule="localScheduleData"
        :is-saving="isSavingEdit"
        :api-error="apiError"
        @save="handleUpdate"
        @cancel="isEditing = false; apiError = ''; showErrorPopup = false;"
        @clear-error="handleCloseError"
      />
    </div>

    <div v-else class="flex flex-col h-full animate-in fade-in slide-in-from-left-4 duration-300">
      
      <div class="flex flex-col items-center mb-8 mt-4 relative">
        <div v-if="localScheduleData.is_essential" class="absolute top-0 right-0 p-1.5 rounded-full bg-amber-50 dark:bg-amber-500/10 border border-amber-200 dark:border-amber-500/20" title="Gasto Indispensable">
          <Star class="w-5 h-5 fill-amber-500 text-amber-500" />
        </div>

        <div class="w-16 h-16 rounded-2xl flex items-center justify-center mb-4 bg-slate-100 dark:bg-white/5 border border-slate-200/50 dark:border-white/5 shadow-inner">
          <component :is="headerIconInfo.icon" class="w-8 h-8" :class="headerIconInfo.color" />
        </div>
        <h3 class="text-4xl font-black text-slate-900 dark:text-white tracking-tighter mb-1">
          {{ localScheduleData.type === 'expense' ? '-' : (localScheduleData.type === 'income' ? '+' : '') }}{{ formatCurrency(localScheduleData.expected_amount, localScheduleData.currency) }}
        </h3>
        <p class="text-sm font-bold text-slate-500 dark:text-slate-400 uppercase tracking-widest">{{ localScheduleData.name }}</p>
      </div>

      <div class="space-y-4 mb-8 bg-slate-50/50 dark:bg-black/20 p-5 rounded-2xl border border-slate-200/50 dark:border-white/5">
        <div class="flex items-start gap-3">
          <Calendar class="w-5 h-5 text-slate-400 mt-0.5 shrink-0" />
          <div>
            <p class="text-xs font-bold text-slate-500 uppercase tracking-wider mb-0.5">Próximo Pago</p>
            <p class="text-sm font-medium text-slate-900 dark:text-white">{{ formatDate(localScheduleData.next_due_date) }} <span class="text-slate-400">({{ frequencies.find(f => f.id === localScheduleData.frequency)?.name }})</span></p>
          </div>
        </div>
        <div class="w-full h-px bg-slate-200/50 dark:bg-white/5"></div>
        <div class="flex items-start gap-3">
          <Wallet class="w-5 h-5 text-slate-400 mt-0.5 shrink-0" />
          <div>
            <p class="text-xs font-bold text-slate-500 uppercase tracking-wider mb-0.5">Cuenta Asignada</p>
            <p class="text-sm font-medium text-slate-900 dark:text-white">{{ accountName }}</p>
          </div>
        </div>
        <div v-if="localScheduleData.type !== 'transfer'" class="w-full h-px bg-slate-200/50 dark:bg-white/5"></div>
        <div v-if="localScheduleData.type !== 'transfer'" class="flex items-start gap-3">
          <Type class="w-5 h-5 text-slate-400 mt-0.5 shrink-0" />
          <div>
            <p class="text-xs font-bold text-slate-500 uppercase tracking-wider mb-0.5">Categoría</p>
            <p class="text-sm font-medium text-slate-900 dark:text-white">{{ categoryName }}</p>
          </div>
        </div>
      </div>

      <div class="flex-1"></div>

      <div class="mt-8 flex gap-3">
        <button 
          @click="handleDelete" 
          :disabled="isDeleting"
          class="flex-1 py-3.5 rounded-xl font-bold text-sm transition-all duration-300 flex items-center justify-center gap-2 border"
          :class="showDeleteConfirm ? 'bg-red-600 text-white border-red-600 hover:bg-red-700' : 'bg-red-50 dark:bg-red-500/10 text-red-600 dark:text-red-400 border-red-200 dark:border-red-500/20 hover:bg-red-100 dark:hover:bg-red-500/20'"
        >
          <Loader2 v-if="isDeleting" class="w-4 h-4 animate-spin" />
          <Trash2 v-else class="w-4 h-4" />
          {{ showDeleteConfirm ? '¿Seguro? Confirmar' : 'Eliminar' }}
        </button>

        <button 
          v-if="!showDeleteConfirm" 
          @click="isEditing = true"
          class="flex-1 flex items-center justify-center gap-2 py-3.5 bg-slate-900 dark:bg-white text-white dark:text-slate-900 rounded-xl font-bold text-sm shadow-md hover:bg-slate-800 dark:hover:bg-slate-200 transition-all"
        >
          <Edit2 class="w-4 h-4" /> Editar
        </button>
      </div>

    </div>
  </GlassDrawer>
</template>