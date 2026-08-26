<script setup lang="ts">
import { onMounted, ref, computed } from 'vue';
import { useRouter } from 'vue-router'; 
import { useFinanceStore } from '../stores/finance';
import { accountService } from '../services/accountService';
import GlassBankCard from '../components/ui/GlassBankCard.vue';
import AccountEditModal from '../components/forms/AccountEditModal.vue';
import AccountCreateModal from '../components/forms/AccountCreateModal.vue';
import { Plus } from 'lucide-vue-next';
import type { Account, AccountCreatePayload, AccountUpdatePayload } from '../types/account';

const router = useRouter(); 
const financeStore = useFinanceStore();

const isEditModalOpen = ref(false);
const isCreateModalOpen = ref(false);
const selectedAccount = ref<Account | null>(null);
const isSaving = ref(false);

const modalError = ref('');

const sortedAccounts = computed(() => {
  return [...financeStore.accounts].sort((a, b) => {
    const getPriority = (type: string) => {
      if (type === 'checking') return 1;
      if (type === 'saving') return 2;
      return 3;
    };
    return getPriority(a.account_type) - getPriority(b.account_type);
  });
});

onMounted(() => {
  if (financeStore.accounts.length === 0) {
    financeStore.fetchAccounts();
  }
});

const openEditModal = (account: Account) => {
  selectedAccount.value = account;
  modalError.value = ''; 
  isEditModalOpen.value = true;
};

const createSecureSlug = (account: Account) => {
  if (!account || !account.name || !account.id) return '';
  const nameSlug = account.name
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLowerCase()
    .trim()
    .replace(/[^a-z0-9 ]/g, "")
    .replace(/\s+/g, "-");
  
  const shortId = account.id.split('-')[0]; 
  return `${nameSlug}-${shortId}`;
};

const goToHistory = (account: Account) => {
  const slug = createSecureSlug(account);
  router.push({ path: '/historial', query: { cuenta: slug } });
};

const handleSaveAccount = async (updatedData: AccountUpdatePayload & { id: string }) => {
  isSaving.value = true;
  modalError.value = ''; 
  
  try {
    const { id, ...payload } = updatedData;

    const acc = financeStore.accounts.find(a => a.id === id);
    if (acc) {
      if (payload.name) acc.name = payload.name;
      if (payload.theme_color) acc.theme_color = payload.theme_color;
      if (payload.allow_negative_balance !== undefined) acc.allow_negative_balance = payload.allow_negative_balance;
    }
    
    await accountService.updateAccount(id, payload);
    
    isEditModalOpen.value = false;
  } catch (error: any) {
    console.error("Error actualizando cuenta:", error);
    modalError.value = error.response?.data?.detail || "Hubo un error al actualizar la cuenta.";
    financeStore.fetchAccounts(true);
  } finally {
    isSaving.value = false;
  }
};

const handleCreateAccount = async (newData: AccountCreatePayload) => {
  isSaving.value = true;
  try {
    await accountService.createAccount(newData);
    await financeStore.refreshAllData();
    isCreateModalOpen.value = false;
  } catch (error: any) {
    console.error("Error creando cuenta:", error);
    alert(error.response?.data?.detail || "Hubo un error al crear la cuenta.");
  } finally {
    isSaving.value = false;
  }
};

const handleDeleteAccount = async (accountId: string) => {
  isSaving.value = true;
  modalError.value = ''; 
  
  try {
    await accountService.deleteAccount(accountId);
    await financeStore.refreshAllData();
    isEditModalOpen.value = false; 
  } catch (error: any) {
    console.error("Error eliminando cuenta:", error);
    modalError.value = error.response?.data?.detail || "Hubo un error al eliminar la cuenta. Es posible que tenga transacciones ligadas o saldo pendiente.";
  } finally {
    isSaving.value = false;
  }
};
</script>

<template>
  <div class="max-w-4xl mx-auto space-y-8">
    
    <div class="relative z-20 mb-8">
      <h3 class="text-xl font-extrabold text-slate-800 dark:text-white tracking-tight">Mis Cuentas</h3>
      <p class="text-xs font-semibold text-slate-500 dark:text-slate-400 mt-1">Gestiona tu patrimonio y billeteras</p>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 gap-6 lg:gap-8">
      
      <GlassBankCard 
        v-for="account in sortedAccounts" 
        :key="account.id"
        :account="account"
        :color-theme="account.theme_color || 'silver'"
        :is-default="account.is_system" 
        @edit="openEditModal(account)"
        @navigate="goToHistory(account)" 
      />
      
      <button 
        @click="isCreateModalOpen = true"
        class="relative w-full aspect-[1.58/1] rounded-3xl overflow-hidden flex flex-col items-center justify-center p-6 transition-all duration-300 group border-2 border-dashed border-slate-300/70 dark:border-slate-700/70 hover:border-slate-800 dark:hover:border-white hover:bg-slate-100/50 dark:hover:bg-white/5"
      >
        <div class="w-16 h-16 rounded-full bg-slate-200/50 dark:bg-white/5 group-hover:bg-slate-800 dark:group-hover:bg-white flex items-center justify-center transition-colors duration-300 mb-4 shadow-sm group-hover:scale-110">
          <Plus class="w-8 h-8 text-slate-500 dark:text-slate-400 group-hover:text-white dark:group-hover:text-slate-900 transition-colors" />
        </div>
        <p class="font-extrabold text-slate-500 dark:text-slate-400 group-hover:text-slate-900 dark:group-hover:text-white transition-colors tracking-tight text-lg">
          Añadir Cuenta
        </p>
      </button>

    </div>

    <AccountEditModal 
      :is-open="isEditModalOpen"
      :account="selectedAccount"
      :is-saving="isSaving"
      :error-msg="modalError" 
      @close="isEditModalOpen = false"
      @save="handleSaveAccount"
      @delete="handleDeleteAccount"
      @clearError="modalError = ''" 
    />

    <AccountCreateModal 
      :is-open="isCreateModalOpen"
      :is-saving="isSaving"
      @close="isCreateModalOpen = false"
      @create="handleCreateAccount"
    />

  </div>
</template>