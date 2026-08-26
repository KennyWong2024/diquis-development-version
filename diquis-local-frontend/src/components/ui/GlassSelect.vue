<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue';
import { ChevronDown, Check } from 'lucide-vue-next';

const props = defineProps<{
  modelValue: string;
  options: { id: string; name: string; icon?: any }[];
  placeholder: string;
  icon?: any;
}>();

const emit = defineEmits(['update:modelValue']);

const isOpen = ref(false);
const selectRef = ref<HTMLElement | null>(null);
const dropdownRef = ref<HTMLElement | null>(null);

const dropdownStyle = ref({ 
  top: 'auto', 
  bottom: 'auto', 
  left: '0px', 
  width: '0px',
  transformOrigin: 'top center'
});

const selectedOption = computed(() => {
  return props.options.find(opt => opt.id === props.modelValue);
});

const updatePosition = () => {
  if (!selectRef.value || !isOpen.value) return;
  
  const rect = selectRef.value.getBoundingClientRect();
  const spaceBelow = window.innerHeight - rect.bottom;
  const spaceAbove = rect.top;
  const dropdownMaxHeight = 256; 
  
  const isDropUp = spaceBelow < dropdownMaxHeight && spaceAbove > spaceBelow;

  dropdownStyle.value = {
    left: `${rect.left}px`,
    width: `${rect.width}px`,
    top: isDropUp ? 'auto' : `${rect.bottom + 8}px`,
    bottom: isDropUp ? `${window.innerHeight - rect.top + 8}px` : 'auto',
    transformOrigin: isDropUp ? 'bottom center' : 'top center'
  };
};

const toggleDropdown = async () => {
  isOpen.value = !isOpen.value;
  if (isOpen.value) {
    await nextTick();
    updatePosition();
    window.addEventListener('scroll', updatePosition, true); 
    window.addEventListener('resize', updatePosition);
  } else {
    removeListeners();
  }
};

const closeDropdown = () => {
  isOpen.value = false;
  removeListeners();
};

const selectOption = (id: string) => {
  emit('update:modelValue', id);
  closeDropdown();
};

const removeListeners = () => {
  window.removeEventListener('scroll', updatePosition, true);
  window.removeEventListener('resize', updatePosition);
};

const handleClickOutside = (event: MouseEvent) => {
  const isInsideSelect = selectRef.value?.contains(event.target as Node);
  const isInsideDropdown = dropdownRef.value?.contains(event.target as Node);
  
  if (!isInsideSelect && !isInsideDropdown) {
    closeDropdown();
  }
};

onMounted(() => {
  document.addEventListener('click', handleClickOutside);
});

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside);
  removeListeners();
});
</script>

<template>
  <div ref="selectRef" class="relative group z-40">
    
    <button 
      @click="toggleDropdown" 
      type="button"
      class="w-full flex items-center gap-3.5 pl-4 pr-4 py-3.5 bg-white/50 dark:bg-black/20 border rounded-xl outline-none text-left transition-all duration-300 focus:bg-white/80 dark:focus:bg-black/40 focus:ring-2"
      :class="[
        isOpen ? 'border-slate-300 dark:border-white/10 ring-2 ring-slate-900/20 dark:ring-white/20' : 'border-slate-200/50 dark:border-white/5 hover:bg-white/60 dark:hover:bg-white/5',
        selectedOption ? 'text-slate-900 dark:text-white font-bold' : 'text-slate-400 dark:text-slate-500 font-medium'
      ]"
    >
      <component 
        v-if="icon" 
        :is="icon" 
        class="h-5 w-5 shrink-0 transition-colors" 
        :class="isOpen ? 'text-slate-800 dark:text-white' : 'text-slate-400 dark:text-slate-500'" 
      />
      
      <span class="flex-1 text-sm truncate" :class="{ 'pl-0': !icon }">
        {{ selectedOption ? selectedOption.name : placeholder }}
      </span>
      
      <ChevronDown 
        class="w-4 h-4 shrink-0 transition-transform duration-300" 
        :class="isOpen ? 'rotate-180 text-slate-800 dark:text-white' : 'text-slate-400'" 
      />
    </button>

    <Teleport to="body">
      <transition name="dropdown">
        <div 
          v-if="isOpen" 
          ref="dropdownRef"
          :style="dropdownStyle"
          class="fixed p-2 rounded-2xl bg-white/80 dark:bg-[#111111]/95 backdrop-blur-2xl border border-white/50 dark:border-white/10 shadow-[0_20px_40px_rgb(0,0,0,0.1)] dark:shadow-[0_20px_40px_rgb(0,0,0,0.5)] max-h-64 overflow-y-auto custom-scrollbar overscroll-contain z-[99999]"
        >
          
          <div class="absolute inset-x-0 top-0 h-px bg-white/80 dark:bg-white/10 pointer-events-none"></div>

          <div class="space-y-1 relative z-10">
            <button 
              v-for="option in options" 
              :key="option.id"
              @click="selectOption(option.id)"
              class="w-full flex items-center gap-3.5 px-3 py-2.5 rounded-xl text-left text-sm font-semibold transition-all duration-200 group"
              :class="modelValue === option.id ? 'bg-slate-900 dark:bg-white text-white dark:text-slate-950 shadow-md' : 'text-slate-700 dark:text-slate-300 hover:bg-slate-100/80 dark:hover:bg-white/10'"
            >
              <component 
                v-if="option.icon" 
                :is="option.icon" 
                class="w-4 h-4 shrink-0 transition-opacity" 
                :class="modelValue === option.id ? 'opacity-100' : 'opacity-60 group-hover:opacity-100'"
              />
              <span class="flex-1 truncate" :class="{ 'pl-0': !option.icon }">{{ option.name }}</span>
              <Check v-if="modelValue === option.id" class="w-4 h-4 shrink-0" :class="modelValue === option.id ? 'text-white dark:text-slate-950' : 'text-transparent'" />
            </button>
          </div>
        </div>
      </transition>
    </Teleport>
    
  </div>
</template>

<style scoped>
.dropdown-enter-active, .dropdown-leave-active { 
  transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1); 
}
.dropdown-enter-from, .dropdown-leave-to { 
  opacity: 0; 
  transform: scale(0.95); 
}

.custom-scrollbar::-webkit-scrollbar { 
  width: 5px; 
}
.custom-scrollbar::-webkit-scrollbar-track { 
  background: transparent; 
  margin: 8px 0; 
}
.custom-scrollbar::-webkit-scrollbar-thumb { 
  background: rgba(150, 150, 150, 0.3); 
  border-radius: 10px; 
}
.custom-scrollbar::-webkit-scrollbar-thumb:hover { 
  background: rgba(150, 150, 150, 0.5); 
}
:global(.dark) .custom-scrollbar::-webkit-scrollbar-thumb { 
  background: rgba(255, 255, 255, 0.15); 
}
:global(.dark) .custom-scrollbar::-webkit-scrollbar-thumb:hover { 
  background: rgba(255, 255, 255, 0.25); 
}
</style>