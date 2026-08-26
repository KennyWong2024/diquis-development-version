<script setup lang="ts">
import { ref, computed, watch } from 'vue';
import GlassModal from '../ui/GlassModal.vue';
import GlassSelect from '../ui/GlassSelect.vue';
import { getAvailableIconNames, resolveIcon } from '../../utils/icons';
import type { Category } from '../../types/category';
import { 
  Loader2, Type, Shapes, Smile, Briefcase, PiggyBank, 
  ShoppingCart, Home, Activity, Gamepad2, Package, Trash2, 
  Save, Zap, Utensils, Car, BookOpen, ShoppingBag, Users 
} from 'lucide-vue-next';

const props = defineProps<{
  isOpen: boolean;
  isSaving: boolean;
  isDeleting?: boolean;
  category?: Category | null; 
}>();

const emit = defineEmits(['close', 'create', 'update', 'delete']);

const name = ref('');
const domain = ref('');
const selectedIcon = ref('Package');
const showDeleteConfirm = ref(false); 

const isEditing = computed(() => !!props.category);
const isSystem = computed(() => props.category?.is_system || false);

const domainOptions = [
  { id: 'income', name: 'Ingresos / Salarios', icon: Briefcase },
  { id: 'savings', name: 'Ahorros / Inversiones', icon: PiggyBank },
  { id: 'home', name: 'Hogar / Alquiler', icon: Home },
  { id: 'utilities', name: 'Servicios / Suscripciones', icon: Zap },
  { id: 'grocery', name: 'Supermercado / Despensa', icon: ShoppingCart },
  { id: 'food_out', name: 'Restaurantes / Comida Fuera', icon: Utensils },
  { id: 'transport', name: 'Transporte / Vehículos', icon: Car },
  { id: 'health', name: 'Salud / Bienestar', icon: Activity },
  { id: 'personal_care', name: 'Cuidado Personal', icon: Smile }, 
  { id: 'education', name: 'Educación / Cursos', icon: BookOpen },
  { id: 'entertainment', name: 'Entretenimiento / Ocio', icon: Gamepad2 },
  { id: 'shopping', name: 'Compras / Tiendas', icon: ShoppingBag },
  { id: 'family', name: 'Familia / Mascotas', icon: Users },
  { id: 'other', name: 'Otros Gastos (General)', icon: Package },
];

const availableIcons = getAvailableIconNames();

const currentDomainIcon = computed(() => {
  const d = domainOptions.find(opt => opt.id === domain.value);
  return d ? d.icon : Shapes;
});

watch(() => props.isOpen, (newVal) => {
  if (newVal) {
    showDeleteConfirm.value = false; 
    if (props.category) {
      name.value = props.category.name;
      domain.value = props.category.domain;
      selectedIcon.value = props.category.icon || 'Package';
    } else {
      name.value = '';
      domain.value = 'other'; 
      selectedIcon.value = 'Package';
    }
  }
});

const isValid = computed(() => {
  return name.value.trim() !== '' && domain.value !== '' && selectedIcon.value !== '';
});

const handleSubmit = () => {
  if (!isValid.value) return;
  if (isEditing.value) {
    emit('update', { name: name.value.trim(), icon: selectedIcon.value });
  } else {
    emit('create', { name: name.value.trim(), domain: domain.value, icon: selectedIcon.value });
  }
};

const handleDeleteClick = () => {
  if (!showDeleteConfirm.value) {
    showDeleteConfirm.value = true; 
  } else {
    emit('delete', props.category?.id); 
  }
};
</script>

<template>
  <GlassModal :is-open="isOpen" :title="isEditing ? 'Configurar Categoría' : 'Nueva Categoría'" @close="emit('close')">
    
    <div class="relative overflow-hidden">
      
      <transition name="fade-blur">
        <div v-if="showDeleteConfirm" class="absolute inset-0 z-50 flex flex-col items-center justify-center p-6 text-center backdrop-blur-md bg-white/20 dark:bg-black/30 rounded-3xl border border-red-500/20 shadow-2xl">
          <div class="w-16 h-16 rounded-full bg-red-500/20 flex items-center justify-center mb-4 animate-bounce">
            <Trash2 class="w-8 h-8 text-red-500" />
          </div>
          <h4 class="text-lg font-black text-slate-900 dark:text-white mb-2">¿Eliminar categoría?</h4>
          <p class="text-xs font-medium text-slate-600 dark:text-slate-300 mb-8 max-w-[240px]">
            Esta acción no se puede deshacer y las transacciones asociadas perderán su clasificación.
          </p>
          
          <div class="flex gap-3 w-full max-w-[280px]">
            <button @click="showDeleteConfirm = false" class="flex-1 py-3.5 rounded-xl font-bold text-xs bg-slate-200/50 dark:bg-white/5 text-slate-600 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-white/10 transition-all border border-slate-300/50 dark:border-white/10">
              Cancelar
            </button>
            <button @click="handleDeleteClick" :disabled="isDeleting" class="flex-1 py-3.5 rounded-xl font-bold text-xs bg-red-600 text-white shadow-lg shadow-red-600/20 hover:bg-red-700 transition-all flex items-center justify-center gap-2">
              <Loader2 v-if="isDeleting" class="w-3.5 h-3.5 animate-spin" />
              Confirmar
            </button>
          </div>
        </div>
      </transition>

      <div :class="{ 'opacity-20 blur-[2px] pointer-events-none scale-[0.98]': showDeleteConfirm }" class="space-y-6 transition-all duration-300 ease-out p-1">
        
        <div class="mb-6 flex flex-col items-center justify-center">
          <p class="text-[10px] font-bold text-slate-400 dark:text-slate-500 uppercase tracking-widest mb-4">Vista Previa</p>
          <div class="w-20 h-20 rounded-3xl bg-slate-100 dark:bg-white/5 border border-slate-200/50 dark:border-white/10 flex items-center justify-center shadow-inner transition-all duration-300">
            <component 
              :is="resolveIcon(selectedIcon)" 
              class="w-10 h-10 text-slate-700 dark:text-slate-300 transition-all duration-300"
            />
          </div>
          <p class="mt-4 font-black text-slate-800 dark:text-white text-lg tracking-tight h-7">
            {{ name || 'Nombre...' }}
          </p>
          <span v-if="isSystem" class="mt-1 text-[9px] font-bold bg-slate-200 dark:bg-white/10 text-slate-500 px-2 py-0.5 rounded-full uppercase tracking-tighter shadow-sm border border-slate-300/50 dark:border-white/10">
            Sistema
          </span>
        </div>

        <div class="space-y-6">
          <div>
            <label class="flex items-center gap-2 text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-widest mb-2 ml-1">
              <Type class="w-4 h-4" /> Nombre
            </label>
            <input 
              v-model="name" 
              type="text" 
              :disabled="isSystem"
              placeholder="Ej. Suscripciones..."
              class="w-full px-4 py-3.5 bg-white/50 dark:bg-black/20 border border-slate-200/50 dark:border-white/5 rounded-xl outline-none text-slate-900 dark:text-white transition-all focus:bg-white/80 dark:focus:bg-black/40 focus:ring-2 focus:ring-slate-900/20 dark:focus:ring-white/20 disabled:opacity-50 disabled:cursor-not-allowed"
            >
          </div>

          <div class="relative z-20" :class="{ 'opacity-50 pointer-events-none': isEditing }">
            <label class="flex items-center gap-2 text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-widest mb-2 ml-1">
              <Shapes class="w-4 h-4" /> Grupo / Naturaleza
            </label>
            <GlassSelect v-model="domain" :options="domainOptions" placeholder="Seleccionar grupo..." :icon="currentDomainIcon" />
          </div>

          <div class="relative z-10">
            <label class="flex items-center gap-2 text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-widest mb-3 ml-1">
              <Smile class="w-4 h-4" /> Elegir Ícono
            </label>
            
            <div class="grid grid-cols-6 sm:grid-cols-7 gap-2 p-3 bg-white/40 dark:bg-black/20 border border-slate-200/50 dark:border-white/5 rounded-2xl max-h-48 overflow-y-auto custom-scrollbar shadow-inner">
              <button 
                v-for="iconName in availableIcons" 
                :key="iconName"
                @click="selectedIcon = iconName"
                type="button"
                class="aspect-square flex items-center justify-center rounded-xl transition-all duration-200 group"
                :class="selectedIcon === iconName ? 'bg-slate-900 dark:bg-white text-white dark:text-slate-900 shadow-md scale-105' : 'text-slate-500 dark:text-slate-400 hover:bg-white/60 dark:hover:bg-white/10 hover:text-slate-800 dark:hover:text-slate-200'"
                :title="iconName"
              >
                <component :is="resolveIcon(iconName)" class="w-5 h-5 transition-transform group-hover:scale-110" />
              </button>
            </div>
          </div>
        </div>

      </div>
    </div>

    <div v-if="!showDeleteConfirm" class="flex gap-3 mt-8 animate-in fade-in duration-300">
      
      <button 
        v-if="isEditing && !isSystem"
        @click="handleDeleteClick" 
        :disabled="isSaving || isDeleting"
        class="flex-1 py-4 bg-red-50 dark:bg-red-500/10 text-red-600 dark:text-red-400 border border-red-200 dark:border-red-500/20 font-bold rounded-xl transition-all hover:bg-red-100 dark:hover:bg-red-500/20 flex items-center justify-center gap-2 disabled:opacity-50"
      >
        <Trash2 class="h-5 w-5" />
        <span class="hidden sm:inline">Eliminar</span>
      </button>

      <button 
        @click="handleSubmit" 
        :disabled="isSaving || isDeleting || !isValid"
        class="flex-[2] py-4 bg-slate-900 dark:bg-white hover:bg-slate-800 dark:hover:bg-slate-200 text-white dark:text-slate-900 font-bold rounded-xl transition-all shadow-lg hover:shadow-xl flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        <Loader2 v-if="isSaving" class="animate-spin h-5 w-5" />
        <template v-else>
          <Save v-if="isEditing" class="h-5 w-5" />
          <span>{{ isEditing ? 'Guardar Cambios' : 'Crear Categoría' }}</span>
        </template>
      </button>

    </div>

  </GlassModal>
</template>

<style scoped>
.custom-scrollbar::-webkit-scrollbar {
  width: 4px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
  margin: 8px;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background-color: rgba(156, 163, 175, 0.4); 
  border-radius: 20px;
}
:global(.dark) .custom-scrollbar::-webkit-scrollbar-thumb {
  background-color: rgba(255, 255, 255, 0.15); 
}

.fade-blur-enter-active,
.fade-blur-leave-active {
  transition: all 0.3s ease;
}
.fade-blur-enter-from,
.fade-blur-leave-to {
  opacity: 0;
  backdrop-filter: blur(0px);
}
</style>