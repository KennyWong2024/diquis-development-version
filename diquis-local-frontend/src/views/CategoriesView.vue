<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useFinanceStore } from '../stores/finance';
import { useCategoryStore } from '../stores/category';
import { categoryService } from '../services/categoryService';
import { resolveIcon } from '../utils/icons'; 
import { Plus, RefreshCcw } from 'lucide-vue-next';
import CategoryAnalyticsPanel from '../components/analytics/CategoryAnalyticsPanel.vue';
import CategoryFormModal from '../components/forms/CategoryFormModal.vue';

const financeStore = useFinanceStore();
const categoryStore = useCategoryStore();
const isFinanceLoading = computed(() => financeStore.isMonthlyLoading);
const isLoading = ref(false);

const isFormModalOpen = ref(false);
const isSaving = ref(false);
const isDeleting = ref(false);
const selectedCategory = ref<any>(null);

const handleRefresh = async () => {
  isLoading.value = true;
  await categoryStore.fetchCategories(true); 
  isLoading.value = false;
};

const openCreateModal = () => {
  selectedCategory.value = null;
  isFormModalOpen.value = true;
};

const openEditModal = (category: any) => {
  selectedCategory.value = category;
  isFormModalOpen.value = true;
};

const handleCreate = async (data: any) => {
  isSaving.value = true;
  try {
    await categoryService.createCategory(data);
    await categoryStore.fetchCategories(true);
    isFormModalOpen.value = false;
  } catch (error) {
    alert("Error al crear categoría");
  } finally {
    isSaving.value = false;
  }
};

const handleUpdate = async (data: any) => {
  if (!selectedCategory.value) return;
  isSaving.value = true;
  try {
    await categoryService.updateCategory(selectedCategory.value.id, data);
    await categoryStore.fetchCategories(true);
    isFormModalOpen.value = false;
  } catch (error) {
    alert("Error al actualizar");
  } finally {
    isSaving.value = false;
  }
};

const handleDelete = async (id: string) => {
  isDeleting.value = true;
  try {
    await categoryService.deleteCategory(id);
    await categoryStore.fetchCategories(true);
    isFormModalOpen.value = false;
  } catch (error) {
    alert("No se pudo eliminar la categoría.");
  } finally {
    isDeleting.value = false;
  }
};

onMounted(() => {
  if (categoryStore.categories.length === 0) handleRefresh();
});
</script>

<template>
  <div class="max-w-6xl mx-auto flex flex-col min-h-[calc(100vh-8rem)] relative">
    
    <div class="flex justify-between items-end mb-8 px-4 sm:px-0">
      <div>
        <h3 class="text-2xl font-extrabold text-slate-900 dark:text-white tracking-tight leading-none">Categorías</h3>
        <p class="text-xs font-semibold text-slate-500 dark:text-slate-400 mt-1.5">Personaliza tu forma de organizar el dinero.</p>
      </div>
      
      <div class="flex items-center gap-2 sm:gap-3">
        <button 
          @click="handleRefresh" 
          class="text-slate-400 hover:text-slate-800 dark:text-slate-500 dark:hover:text-white bg-slate-100 dark:bg-white/5 p-2.5 rounded-full transition-all duration-300"
        >
          <RefreshCcw class="w-4 h-4" :class="{ 'animate-spin text-slate-900 dark:text-white': isLoading || isFinanceLoading }" />
        </button>

        <button 
          @click="openCreateModal" 
          class="hidden lg:flex items-center gap-2 bg-slate-900 dark:bg-white text-white dark:text-slate-900 px-4 py-2.5 rounded-xl font-bold text-sm hover:opacity-90 transition-opacity shadow-sm"
        >
          <Plus class="w-4 h-4" />
          <span>Nueva Categoría</span>
        </button>
      </div>
    </div>

    <div class="flex-1 flex flex-col gap-8 pb-24">
        
        <CategoryAnalyticsPanel />

        <section>
            <h4 class="text-[10px] font-extrabold text-slate-400 dark:text-slate-500 mb-4 px-2 uppercase tracking-[0.15em]">Gestionar Catálogo</h4>
            
            <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-3 sm:gap-4 px-2 sm:px-0">
                <div 
                  v-for="category in categoryStore.categories" 
                  :key="category.id" 
                  @click="openEditModal(category)"
                  class="bg-white/60 dark:bg-white/5 border border-slate-200/50 dark:border-white/5 rounded-2xl p-4 flex flex-col items-center gap-3 cursor-pointer hover:bg-white dark:hover:bg-white/10 hover:-translate-y-1 transition-all shadow-sm group"
                >
                    <div class="w-12 h-12 rounded-xl bg-slate-100 dark:bg-black/20 flex items-center justify-center group-hover:bg-slate-200 dark:group-hover:bg-black/40 transition-colors">
                      <component :is="resolveIcon(category.icon)" class="w-5 h-5 text-slate-600 dark:text-slate-400 group-hover:text-slate-900 dark:group-hover:text-white" />
                    </div>
                    <div class="text-xs font-bold text-slate-700 dark:text-slate-300 text-center flex flex-col items-center">
                      {{ category.name }}
                      <span v-if="category.is_system" class="text-[8px] opacity-40 uppercase tracking-tighter mt-0.5">Sistema</span>
                    </div>
                </div>
            </div>
        </section>
    </div>

    <button 
      @click="openCreateModal"
      class="lg:hidden fixed bottom-24 right-5 z-40 w-14 h-14 bg-slate-900 dark:bg-white text-white dark:text-slate-900 rounded-full flex items-center justify-center shadow-[0_8px_24px_rgba(0,0,0,0.15)] dark:shadow-[0_8px_24px_rgba(255,255,255,0.25)] active:scale-95 transition-all duration-300"
    >
      <Plus class="w-6 h-6" />
    </button>

    <CategoryFormModal 
      :is-open="isFormModalOpen"
      :is-saving="isSaving"
      :is-deleting="isDeleting"
      :category="selectedCategory"
      @close="isFormModalOpen = false"
      @create="handleCreate"
      @update="handleUpdate"
      @delete="handleDelete"
    />

  </div>
</template>