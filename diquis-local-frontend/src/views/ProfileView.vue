<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '../stores/auth';
import { useTheme } from '../composables/useTheme';
import { useScreen } from '../composables/useScreen';
import { authService } from '../services/authService';
import GlassCard from '../components/ui/GlassCard.vue';
import GlassCountrySelect from '../components/ui/GlassCountrySelect.vue';
import ChangePasswordModal from '../components/forms/ChangePasswordModal.vue';
import GlassDeleteAccountModal from '../components/forms/GlassDeleteAccountModal.vue';
import GlassAlert from '../components/ui/GlassAlert.vue'; 
import GlassTimezoneSelect from '../components/ui/GlassTimezoneSelect.vue';
import GlassSettingsGroup from '../components/ui/GlassSettingsGroup.vue';
import GlassSettingsRow from '../components/ui/GlassSettingsRow.vue';
import { 
  User, Mail, Globe, Shield, Edit2, CheckCircle2, RotateCcw,
  Key, LogOut, Smartphone, Monitor, Loader2, ChevronRight,
  AlertCircle, AlertOctagon, Trash2, Moon, Info, AlertTriangle,
  MapPin, Clock, Edit3
} from 'lucide-vue-next';

const router = useRouter();
const authStore = useAuthStore();
const { theme, toggleTheme } = useTheme();
const { isMobile } = useScreen();
const user = computed(() => authStore.user);
const isLoadingProfile = ref(true);
const isSavingProfile = ref(false);
const errorMessage = ref('');
const isEditingProfile = ref(false);
const isPasswordModalOpen = ref(false);
const showLogoutConfirm = ref(false);
const isDeleteModalOpen = ref(false);
const isDeletingAccount = ref(false);

const alertConfig = ref({
  show: false,
  message: '',
  type: 'success' as 'success' | 'error' | 'info' | 'warning',
  autoClose: 4000,
  isConfirm: false,
  confirmText: 'Confirmar',
  cancelText: 'Cancelar'
});

const pendingAction = ref<{ type: 'wipe' | 'logout', payload?: string } | null>(null);

const userInitials = computed(() => {
  if (!user.value?.full_name) return 'U';
  return user.value.full_name
    .split(' ')
    .map((n: string) => n[0])
    .join('')
    .substring(0, 2)
    .toUpperCase();
});

const getCleanData = () => ({
  full_name: user.value?.full_name || '',
  country_code: user.value?.country_code?.toLowerCase() || 'cr',
  default_currency: user.value?.default_currency || 'CRC',
  timezone: user.value?.timezone || 'America/Costa_Rica'
});

const formData = ref(getCleanData());

onMounted(async () => {
  try {
    isLoadingProfile.value = true;
    const userData = await authService.getCurrentUser();
    authStore.setUser(userData);
    formData.value = getCleanData();
  } catch (error) {
    console.error("Error cargando el perfil", error);
    errorMessage.value = "No se pudo cargar la información del perfil.";
  } finally {
    isLoadingProfile.value = false;
  }
});

const toggleEditMode = () => {
  if (isEditingProfile.value) {
    formData.value = getCleanData();
  }
  isEditingProfile.value = !isEditingProfile.value;
  errorMessage.value = '';
};

const defaultTimezones: Record<string, string> = {
  cr: 'America/Costa_Rica', pa: 'America/Panama', ni: 'America/Managua',
  hn: 'America/Honduras', sv: 'America/El_Salvador', gt: 'America/Guatemala',
  do: 'America/Santo_Domingo', us: 'America/New_York', mx: 'America/Mexico_City',
  ca: 'America/Toronto', co: 'America/Bogota', ar: 'America/Cordoba',
  cl: 'America/Santiago', pe: 'America/Lima', uy: 'America/Montevideo',
  br: 'America/Sao_Paulo', bo: 'America/La_Paz', py: 'America/Asuncion',
  ve: 'America/Caracas', es: 'Europe/Madrid', gb: 'Europe/London',
  ch: 'Europe/Zurich', se: 'Europe/Stockholm', no: 'Europe/Oslo',
  dk: 'Europe/Copenhagen', jp: 'Asia/Tokyo', cn: 'Asia/Shanghai',
  in: 'Asia/Kolkata', au: 'Australia/Sydney', nz: 'Pacific/Auckland',
  kr: 'Asia/Seoul', sg: 'Asia/Singapore', ae: 'Asia/Dubai',
  za: 'Africa/Johannesburg', il: 'Asia/Jerusalem'
};

watch(() => formData.value.country_code, (newCountry, oldCountry) => {
  if (isEditingProfile.value && newCountry && oldCountry && newCountry !== oldCountry) {
    const matchedTz = defaultTimezones[newCountry.toLowerCase()];
    if (matchedTz) {
      formData.value.timezone = matchedTz;
    }
  }
});

const triggerAlert = (message: string, type: 'success' | 'error' | 'warning' = 'success', autoClose = 4000) => {
  alertConfig.value = { ...alertConfig.value, show: true, message, type, autoClose, isConfirm: false };
};

const handleSavePreferences = async () => {
  if (!formData.value.full_name.trim()) {
      errorMessage.value = "El nombre completo no puede estar vacío.";
      return;
  }

  isSavingProfile.value = true;
  errorMessage.value = '';
  
  try {
    const payload = {
      ...formData.value,
      country_code: formData.value.country_code.toUpperCase()
    };
    
    const updatedUser = await authService.updateProfile(payload);
    authStore.setUser(updatedUser);
    
    isEditingProfile.value = false;
    triggerAlert('Tus preferencias se han guardado correctamente.');
  } catch (error: any) {
    errorMessage.value = error.response?.data?.detail || "Hubo un error al actualizar tus datos.";
  } finally {
    isSavingProfile.value = false;
  }
};

const handlePasswordSuccess = (msg: string) => {
  triggerAlert(msg, 'success');
};

const handleLogoutClick = async () => {
  if (!showLogoutConfirm.value) {
    showLogoutConfirm.value = true;
  } else {
    await authStore.logout();
    router.push('/auth/login');
  }
};

const handleNuclearDelete = async (password: string) => {
  isDeletingAccount.value = true;
  try {
    await authService.deleteAccount({ current_password: password });
    await authStore.logout();
    isDeleteModalOpen.value = false;
    router.push('/auth/login');
  } catch (error: any) {
    triggerAlert(error.response?.data?.detail || "No se pudo eliminar la cuenta.", "error");
  } finally {
    isDeletingAccount.value = false;
  }
};

// ── Mobile-specific handlers (estilo iOS Settings) ──

const handleEditNameMobile = async () => {
  const newName = prompt('Editar Nombre Completo', user.value?.full_name);
  if (newName && newName.trim() !== '' && newName !== user.value?.full_name) {
    try {
      const updatedUser = await authService.updateProfile({ 
        full_name: newName.trim(),
        country_code: user.value?.country_code || 'CR'
      });
      authStore.setUser(updatedUser);
      triggerAlert('Nombre actualizado correctamente.');
    } catch (error) {
      triggerAlert('Error al actualizar el nombre.', 'error');
    }
  }
};

const handleCountryChangeMobile = async (newCode: string) => {
  if (newCode === user.value?.country_code?.toLowerCase()) return;
  try {
    const updatedUser = await authService.updateProfile({ 
      country_code: newCode.toUpperCase(),
      full_name: user.value?.full_name || ''
    });
    authStore.setUser(updatedUser);
    triggerAlert('País actualizado correctamente.');
  } catch (error) {
    triggerAlert('Error al actualizar el país.', 'error');
  }
};

const handleTimezoneChangeMobile = async (newTz: string) => {
  if (newTz === user.value?.timezone) return;
  try {
    const updatedUser = await authService.updateProfile({ 
      timezone: newTz,
      full_name: user.value?.full_name || ''
    });
    authStore.setUser(updatedUser);
    triggerAlert('Zona horaria actualizada correctamente.');
  } catch (error) {
    triggerAlert('Error al actualizar la zona horaria.', 'error');
  }
};

const confirmDeleteMobile = () => {
  isDeleteModalOpen.value = true;
};

const confirmLogoutMobile = () => {
  pendingAction.value = { type: 'logout' };
  alertConfig.value = {
    show: true,
    type: 'warning',
    message: "Cerrarás sesión en este dispositivo. Tendrás que volver a ingresar tus credenciales. ¿Continuar?",
    isConfirm: true,
    confirmText: "Sí, Salir",
    cancelText: "Cancelar",
    autoClose: 0
  };
};

const handleAlertConfirm = async () => {
  const action = pendingAction.value;
  pendingAction.value = null;
  
  if (!action) return;

  if (action.type === 'logout') {
    await authStore.logout();
    router.push('/auth/login');
  }
};

const handleAlertCancel = () => {
  pendingAction.value = null;
};
</script>

<template>
  <div v-if="isLoadingProfile" class="flex justify-center items-center min-h-[60vh]">
    <Loader2 class="w-10 h-10 animate-spin text-slate-400" />
  </div>

  <!-- ═══════════ MOBILE: Estilo iOS Settings (como diquis-mobile) ═══════════ -->
  <div v-else-if="isMobile" class="max-w-3xl mx-auto space-y-8 pb-24 pt-6 px-4 sm:px-6">
    
    <!-- Avatar + Nombre -->
    <div class="flex flex-col items-center text-center space-y-4 mb-10">
      <div class="relative group">
        <div class="w-28 h-28 rounded-[2rem] bg-slate-100 dark:bg-[#1a1a1a] flex items-center justify-center shadow-xl border border-slate-200/50 dark:border-white/10 overflow-hidden relative z-10">
          <span class="text-4xl font-black text-slate-800 dark:text-white tracking-tighter">{{ userInitials }}</span>
        </div>
      </div>
      
      <div 
        @click="handleEditNameMobile"
        class="group flex items-center justify-center gap-2 cursor-pointer bg-slate-100 dark:bg-white/5 hover:bg-slate-200 dark:hover:bg-white/10 py-2 px-5 rounded-full transition-colors active:scale-95"
      >
        <span class="text-xl font-extrabold text-slate-800 dark:text-white tracking-tight">
          {{ user?.full_name || 'Usuario' }}
        </span>
        <Edit3 class="w-4 h-4 text-slate-400 group-hover:text-slate-600 dark:group-hover:text-white" />
      </div>

      <div class="inline-flex items-center justify-center gap-2 text-slate-500 dark:text-slate-400 font-medium text-sm px-3 py-1 bg-slate-100 dark:bg-white/5 rounded-full">
        <Mail class="w-4 h-4" /> {{ user?.email || 'correo@ejemplo.com' }}
      </div>
    </div>

    <!-- Preferencias Regionales -->
    <GlassSettingsGroup title="Preferencias Regionales" :icon="Globe" icon-color-class="text-indigo-500" icon-bg-class="bg-indigo-500/10">
      
      <GlassCountrySelect :model-value="user?.country_code?.toLowerCase() || 'cr'" @update:model-value="handleCountryChangeMobile">
        <GlassSettingsRow 
          title="País de Residencia" 
          :subtitle="user?.country_code || 'CR'" 
          :icon="MapPin" 
          clickable show-chevron 
        />
      </GlassCountrySelect>

      <GlassTimezoneSelect :model-value="user?.timezone || 'America/Costa_Rica'" @update:model-value="handleTimezoneChangeMobile">
        <GlassSettingsRow 
          title="Zona Horaria" 
          :subtitle="user?.timezone || 'America/Costa_Rica'" 
          :icon="Clock" 
          clickable show-chevron 
          is-last
        />
      </GlassTimezoneSelect>
      
    </GlassSettingsGroup>

    <!-- Interfaz e Información -->
    <GlassSettingsGroup title="Interfaz e Información" :icon="Monitor" icon-color-class="text-blue-500" icon-bg-class="bg-blue-500/10">
      <GlassSettingsRow 
        title="Modo Oscuro" 
        subtitle="Adaptar a la iluminación" 
        :icon="Moon" 
        clickable
        @click="toggleTheme" 
      >
        <template #action>
          <div 
            class="relative inline-flex h-7 w-12 items-center rounded-full transition-colors duration-300 pointer-events-none"
            :class="theme === 'dark' ? 'bg-emerald-500' : 'bg-slate-300 dark:bg-white/20'"
          >
            <span class="inline-block h-5 w-5 transform rounded-full bg-white transition duration-300 shadow-sm" :class="theme === 'dark' ? 'translate-x-6' : 'translate-x-1'" />
          </div>
        </template>
      </GlassSettingsRow>

      <GlassSettingsRow 
        title="Acerca de Diquis" 
        subtitle="Versión 1.0.0 (Cloud)" 
        :icon="Info" 
        is-last 
      >
        <template #action>
          <span class="text-xs font-bold text-slate-400 bg-slate-100 dark:bg-white/10 px-2 py-1 rounded-md">Cloud</span>
        </template>
      </GlassSettingsRow>
    </GlassSettingsGroup>

    <!-- Seguridad -->
    <GlassSettingsGroup title="Seguridad" :icon="Shield" icon-color-class="text-emerald-500" icon-bg-class="bg-emerald-500/10">
      <GlassSettingsRow 
        title="Cambiar Contraseña" 
        subtitle="Actualizar credenciales de acceso" 
        :icon="Key" 
        clickable 
        @click="isPasswordModalOpen = true"
      >
        <template #action>
          <ChevronRight class="w-4 h-4 text-slate-400" />
        </template>
      </GlassSettingsRow>

      <GlassSettingsRow 
        title="Cerrar Sesión" 
        subtitle="Desconectar este dispositivo" 
        :icon="LogOut" 
        clickable 
        is-last
        @click="confirmLogoutMobile"
      >
        <template #action>
          <ChevronRight class="w-4 h-4 text-amber-400" />
        </template>
      </GlassSettingsRow>
    </GlassSettingsGroup>

    <!-- Zona de Peligro -->
    <div class="pt-8">
      <GlassSettingsGroup title="Zona de Peligro" :icon="AlertTriangle" icon-color-class="text-red-500" icon-bg-class="bg-red-500/10">
        <GlassSettingsRow 
          title="Eliminar Cuenta y Datos" 
          subtitle="Borrar todo del servidor. Acción irreversible." 
          :icon="Trash2" 
          clickable is-last 
          @click="confirmDeleteMobile"
        >
          <template #action>
            <ChevronRight class="w-4 h-4 text-red-400" />
          </template>
        </GlassSettingsRow>
      </GlassSettingsGroup>
    </div>

    <ChangePasswordModal 
      :is-open="isPasswordModalOpen"
      @close="isPasswordModalOpen = false"
      @success="handlePasswordSuccess"
    />

    <GlassDeleteAccountModal 
      :is-open="isDeleteModalOpen"
      :is-loading="isDeletingAccount"
      @close="isDeleteModalOpen = false"
      @confirm="handleNuclearDelete"
    />

    <GlassAlert 
      v-model:show="alertConfig.show"
      :message="alertConfig.message"
      :type="alertConfig.type"
      :auto-close="alertConfig.autoClose"
      :is-confirm="alertConfig.isConfirm"
      :confirm-text="alertConfig.confirmText"
      :cancel-text="alertConfig.cancelText"
      @confirm="handleAlertConfirm"
      @cancel="handleAlertCancel"
    />

  </div>

  <!-- ═══════════ DESKTOP: Interfaz original con cards y formularios ═══════════ -->
  <div v-else class="max-w-4xl mx-auto space-y-6 sm:space-y-8 pb-20 px-4 sm:px-6">
    
    <div class="flex justify-between items-center relative z-20 mt-4 sm:mt-8 mb-4">
      <div>
        <h3 class="text-2xl sm:text-3xl font-extrabold text-slate-800 dark:text-white tracking-tight">Mi Perfil</h3>
        <p class="text-sm font-medium text-slate-500 dark:text-slate-400 mt-1">Configuración y seguridad de la cuenta</p>
      </div>
      
      <button 
        v-if="!isEditingProfile"
        @click="toggleEditMode"
        class="flex items-center gap-2 bg-slate-900 dark:bg-white text-white dark:text-slate-900 px-5 py-2.5 rounded-xl font-bold text-sm hover:opacity-90 transition-all shadow-md active:scale-95"
      >
        <Edit2 class="w-4 h-4" /> <span class="hidden sm:inline">Editar Perfil</span>
      </button>
      <button 
        v-else
        @click="toggleEditMode"
        class="flex items-center gap-2 bg-slate-200 dark:bg-white/10 text-slate-700 dark:text-slate-200 px-5 py-2.5 rounded-xl font-bold text-sm hover:bg-slate-300 dark:hover:bg-white/20 transition-all active:scale-95"
      >
        <RotateCcw class="w-4 h-4" /> <span class="hidden sm:inline">Cancelar Edición</span>
      </button>
    </div>

    <transition name="fade-slide">
      <div v-if="errorMessage" class="p-4 rounded-xl bg-rose-50 dark:bg-rose-500/10 border border-rose-200 dark:border-rose-500/20 text-rose-600 dark:text-rose-400 text-sm font-bold flex items-center gap-3 shadow-sm">
        <AlertCircle class="w-5 h-5 shrink-0" />
        <p>{{ errorMessage }}</p>
      </div>
    </transition>

    <GlassCard class="p-6 sm:p-8 flex flex-col sm:flex-row items-center sm:items-start gap-6 sm:gap-8 relative z-10 transition-all duration-300" :class="{ 'ring-2 ring-emerald-500/50 shadow-emerald-500/10': isEditingProfile }">
      <div class="relative shrink-0 group">
        <div class="w-28 h-28 sm:w-32 sm:h-32 rounded-full bg-gradient-to-br from-slate-800 to-slate-600 dark:from-slate-100 dark:to-slate-300 flex items-center justify-center shadow-xl ring-4 ring-white/50 dark:ring-black/20 transition-transform group-hover:scale-105">
          <span class="text-4xl sm:text-5xl font-black text-white dark:text-slate-900 tracking-tighter">{{ userInitials }}</span>
        </div>
        <div class="absolute bottom-1 right-1 w-7 h-7 bg-emerald-500 border-4 border-white dark:border-[#111] rounded-full shadow-md" title="Cuenta Activa"></div>
      </div>

      <div class="flex-1 w-full space-y-5 sm:mt-2">
        <div class="text-center sm:text-left space-y-1">
          <div class="inline-flex items-center justify-center sm:justify-start gap-2 text-slate-500 dark:text-slate-400 font-medium text-sm px-3 py-1 bg-slate-100 dark:bg-white/5 rounded-full mb-2">
            <Mail class="w-4 h-4" /> {{ user?.email || 'correo@ejemplo.com' }}
          </div>
        </div>

        <div class="relative group w-full max-w-md mx-auto sm:mx-0">
          <label class="text-[11px] font-bold text-slate-500 uppercase tracking-widest ml-1 mb-1 block" :class="{ 'text-emerald-600 dark:text-emerald-400': isEditingProfile }">
            Nombre Completo
          </label>
          <div class="relative">
            <User class="absolute left-4 top-3.5 h-5 w-5 transition-colors" :class="isEditingProfile ? 'text-emerald-500' : 'text-slate-300 dark:text-slate-600'" />
            <input 
              v-model="formData.full_name" 
              type="text" 
              placeholder="Tu nombre" 
              :readonly="!isEditingProfile"
              class="w-full pl-12 pr-4 py-3 bg-slate-50/50 dark:bg-black/20 rounded-xl outline-none text-slate-900 dark:text-white font-bold transition-all text-lg"
              :class="isEditingProfile ? 'border border-emerald-200 dark:border-emerald-500/30 focus:bg-white dark:focus:bg-black/40 focus:ring-4 focus:ring-emerald-500/10' : 'border border-transparent cursor-default opacity-80'"
            >
          </div>
        </div>
      </div>
    </GlassCard>

    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 sm:gap-8">
      
      <div class="space-y-6 sm:space-y-8">
        <GlassCard class="p-6 sm:p-8 relative z-50 transition-all duration-300" :class="{ 'ring-2 ring-emerald-500/50 shadow-emerald-500/10': isEditingProfile }">
          <div class="flex items-center gap-3 mb-8 pb-4 border-b border-slate-200/50 dark:border-white/5">
            <div class="p-2.5 bg-indigo-50 dark:bg-indigo-500/10 rounded-xl text-indigo-600 dark:text-indigo-400">
              <Globe class="w-5 h-5" />
            </div>
            <div>
              <h3 class="text-sm font-extrabold text-slate-800 dark:text-white uppercase tracking-wider">Región</h3>
              <p class="text-xs text-slate-500 mt-0.5">Ajustes locales y horarios</p>
            </div>
          </div>
          
          <div class="space-y-6">
            <div class="space-y-2 relative z-[60]" :class="{ 'pointer-events-none opacity-60 grayscale-[50%]': !isEditingProfile }">
              <label class="text-xs font-bold text-slate-500 uppercase tracking-widest ml-1" :class="{ 'text-emerald-600 dark:text-emerald-400': isEditingProfile }">País de Residencia</label>
              <GlassCountrySelect v-model="formData.country_code" placeholder="Seleccionar País..." />
            </div>

            <div class="space-y-2 relative z-[40]" :class="{ 'pointer-events-none opacity-60 grayscale-[50%]': !isEditingProfile }">
              <label class="text-xs font-bold text-slate-500 uppercase tracking-widest ml-1" :class="{ 'text-emerald-600 dark:text-emerald-400': isEditingProfile }">Zona Horaria</label>
              <GlassTimezoneSelect v-model="formData.timezone" placeholder="Seleccionar Zona Horaria..." />
            </div>

            <transition name="fade-slide">
              <div v-if="isEditingProfile" class="pt-6 mt-4 border-t border-slate-200/50 dark:border-white/5">
                <button 
                  @click="handleSavePreferences"
                  :disabled="isSavingProfile"
                  class="w-full flex items-center justify-center gap-2 py-3.5 bg-emerald-500 hover:bg-emerald-600 text-white font-bold rounded-xl transition-all shadow-lg shadow-emerald-500/20 active:scale-95 disabled:opacity-50"
                >
                  <Loader2 v-if="isSavingProfile" class="w-5 h-5 animate-spin" />
                  <CheckCircle2 v-else class="w-5 h-5" />
                  {{ isSavingProfile ? 'Guardando...' : 'Guardar Cambios' }}
                </button>
              </div>
            </transition>
          </div>
        </GlassCard>
      </div>

      <div class="space-y-6 sm:space-y-8 relative z-10 flex flex-col justify-between">
        
        <div class="space-y-6 sm:space-y-8">
          <GlassCard class="p-6 sm:p-8">
            <div class="flex items-center gap-3 mb-6 pb-4 border-b border-slate-200/50 dark:border-white/5">
              <div class="p-2.5 bg-amber-50 dark:bg-amber-500/10 rounded-xl text-amber-600 dark:text-amber-400">
                <Monitor class="w-5 h-5" />
              </div>
              <h3 class="text-sm font-extrabold text-slate-800 dark:text-white uppercase tracking-wider">Interfaz</h3>
            </div>
            
            <div class="flex items-center justify-between p-4 rounded-2xl bg-slate-50/50 dark:bg-white/5 border border-slate-200/50 dark:border-white/5 hover:bg-slate-100 dark:hover:bg-white/10 transition-colors">
              <div>
                <p class="font-bold text-slate-800 dark:text-white text-sm">Modo Oscuro</p>
                <p class="text-xs text-slate-500 mt-0.5">Adaptar al entorno visual</p>
              </div>
              <button 
                @click="toggleTheme" 
                class="relative inline-flex h-7 w-12 items-center rounded-full transition-colors duration-300 focus:outline-none focus:ring-2 focus:ring-emerald-500/50 focus:ring-offset-2 dark:focus:ring-offset-slate-900"
                :class="theme === 'dark' ? 'bg-emerald-500' : 'bg-slate-300 dark:bg-white/20'"
              >
                <span class="inline-block h-5 w-5 transform rounded-full bg-white transition duration-300 shadow-sm" :class="theme === 'dark' ? 'translate-x-6' : 'translate-x-1'" />
              </button>
            </div>
          </GlassCard>

          <GlassCard class="p-6 sm:p-8">
            <div class="flex items-center gap-3 mb-6 pb-4 border-b border-slate-200/50 dark:border-white/5">
              <div class="p-2.5 bg-blue-50 dark:bg-blue-500/10 rounded-xl text-blue-600 dark:text-blue-400">
                <Shield class="w-5 h-5" />
              </div>
              <h3 class="text-sm font-extrabold text-slate-800 dark:text-white uppercase tracking-wider">Seguridad</h3>
            </div>
            
            <button 
              @click="isPasswordModalOpen = true"
              class="w-full flex items-center justify-between p-4 rounded-2xl bg-slate-50/50 dark:bg-white/5 border border-slate-200/50 dark:border-white/5 hover:bg-white dark:hover:bg-white/10 transition-colors group"
            >
              <div class="flex items-center gap-3">
                <div class="p-2 rounded-lg bg-white dark:bg-black/30 text-slate-600 dark:text-slate-400 shadow-sm group-hover:scale-110 transition-transform">
                  <Key class="w-4 h-4" />
                </div>
                <div class="text-left">
                  <p class="font-bold text-slate-800 dark:text-white text-sm">Cambiar Contraseña</p>
                  <p class="text-xs text-slate-500 mt-0.5">Actualizar credenciales de acceso</p>
                </div>
              </div>
              <ChevronRight class="w-5 h-5 text-slate-400 group-hover:text-slate-600 dark:group-hover:text-white transition-colors" />
            </button>
          </GlassCard>
        </div>

        <GlassCard class="p-6 sm:p-8 border-slate-200/80 dark:border-white/10 bg-slate-50 dark:bg-white/5 mt-6 lg:mt-0">
          <transition name="fade-slide" mode="out-in">
            <div v-if="showLogoutConfirm" class="space-y-4">
              <div class="p-4 bg-amber-500/10 border border-amber-500/20 rounded-2xl flex items-start gap-3">
                <Smartphone class="w-5 h-5 text-amber-600 dark:text-amber-500 shrink-0 mt-0.5" />
                <div>
                  <p class="text-xs font-bold text-amber-700 dark:text-amber-400 uppercase tracking-wide">Desconectar Dispositivo</p>
                  <p class="text-[12px] font-medium text-amber-700/80 dark:text-amber-400/80 leading-relaxed mt-1">
                    Tendrás que volver a ingresar tu correo y contraseña la próxima vez que entres. ¿Continuar?
                  </p>
                </div>
              </div>
              <div class="flex gap-3">
                <button @click="showLogoutConfirm = false" class="flex-1 py-3 rounded-xl font-bold text-sm bg-slate-200 dark:bg-white/10 text-slate-700 dark:text-white hover:bg-slate-300 dark:hover:bg-white/20 transition-colors">
                  Cancelar
                </button>
                <button @click="handleLogoutClick" class="flex-1 py-3 rounded-xl font-bold text-sm bg-amber-600 hover:bg-amber-700 text-white shadow-lg shadow-amber-500/20 transition-all flex justify-center items-center gap-2">
                  <LogOut class="w-4 h-4" /> Sí, Salir
                </button>
              </div>
            </div>

            <button 
              v-else
              @click="showLogoutConfirm = true"
              class="w-full flex items-center justify-between p-4 rounded-2xl bg-white dark:bg-black/40 border border-slate-200/50 dark:border-white/5 hover:border-amber-300/50 dark:hover:border-amber-500/30 hover:bg-amber-50/50 dark:hover:bg-amber-500/5 transition-all group"
            >
              <div class="flex items-center gap-3">
                <div class="p-2 rounded-lg bg-slate-100 dark:bg-white/5 text-slate-500 group-hover:text-amber-600 dark:group-hover:text-amber-400 transition-colors">
                  <LogOut class="w-4 h-4" />
                </div>
                <div class="text-left">
                  <p class="font-bold text-slate-700 dark:text-slate-200 text-sm group-hover:text-amber-700 dark:group-hover:text-amber-400 transition-colors">Cerrar Sesión</p>
                  <p class="text-xs text-slate-500 mt-0.5">Desconectar este dispositivo</p>
                </div>
              </div>
              <ChevronRight class="w-5 h-5 text-slate-300 group-hover:text-amber-400 transition-colors" />
            </button>
          </transition>
        </GlassCard>

      </div>
    </div>

    <div class="w-full py-8 sm:py-12 flex items-center justify-center opacity-30">
      <div class="h-px bg-gradient-to-r from-transparent via-slate-400 dark:via-slate-500 to-transparent w-full max-w-xs"></div>
    </div>

    <GlassCard class="p-6 sm:p-8 border-rose-500/40 dark:border-rose-500/30 bg-gradient-to-br from-rose-50 to-white dark:from-rose-950/30 dark:to-black/40 shadow-xl shadow-rose-500/5">
      <div class="flex flex-col sm:flex-row items-center sm:items-start justify-between gap-6">
        <div class="text-center sm:text-left">
          <div class="flex items-center justify-center sm:justify-start gap-2 mb-2 text-rose-600 dark:text-rose-500">
            <AlertOctagon class="w-6 h-6 animate-pulse" />
            <h3 class="text-lg font-black uppercase tracking-wider">Zona de Peligro</h3>
          </div>
          <p class="text-sm font-medium text-slate-600 dark:text-slate-400 max-w-lg">
            Eliminar tu cuenta es una acción permanente. Borrará irremediablemente todos tus datos financieros, presupuestos, categorías personalizadas y configuraciones.
          </p>
        </div>
        
        <button 
          @click="isDeleteModalOpen = true"
          class="shrink-0 w-full sm:w-auto px-6 py-4 rounded-xl font-bold text-sm bg-white dark:bg-black/60 text-rose-600 dark:text-rose-400 border-2 border-rose-200 dark:border-rose-500/30 hover:bg-rose-600 hover:text-white hover:border-rose-600 dark:hover:bg-rose-600 dark:hover:text-white transition-all shadow-sm flex items-center justify-center gap-2 group"
        >
          <Trash2 class="w-5 h-5 group-hover:animate-bounce" /> Eliminar Cuenta
        </button>
      </div>
    </GlassCard>

    <ChangePasswordModal 
      :is-open="isPasswordModalOpen"
      @close="isPasswordModalOpen = false"
      @success="handlePasswordSuccess"
    />

    <GlassDeleteAccountModal 
      :is-open="isDeleteModalOpen"
      :is-loading="isDeletingAccount"
      @close="isDeleteModalOpen = false"
      @confirm="handleNuclearDelete"
    />

    <GlassAlert 
      v-model:show="alertConfig.show"
      :message="alertConfig.message"
      :type="alertConfig.type"
      :auto-close="alertConfig.autoClose"
      :is-confirm="alertConfig.isConfirm"
      :confirm-text="alertConfig.confirmText"
      :cancel-text="alertConfig.cancelText"
      @confirm="handleAlertConfirm"
      @cancel="handleAlertCancel"
    />

  </div>
</template>

<style scoped>
.fade-slide-enter-active, .fade-slide-leave-active { transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1); }
.fade-slide-enter-from, .fade-slide-leave-to { opacity: 0; transform: translateY(-10px); }
</style>