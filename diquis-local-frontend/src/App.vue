<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { api } from './services/api';
import ServerWakeUp from './components/ui/ServerWakeUp.vue';

const isServerReady = ref(false);
const isServerChecking = ref(true);
const wakeUpMessage = ref('Iniciando conexión segura...');
const showRetryButton = ref(false);

const MAX_RETRIES = 5;
const RETRY_DELAY_MS = 10000;

const checkServerHealth = async (attempt: number = 1): Promise<boolean> => {
  try {
    const healthUrl = import.meta.env.VITE_API_URL 
      ? import.meta.env.VITE_API_URL.replace('/api/v1', '/health') 
      : 'http://localhost:8000/health';
      
    await api.get(healthUrl);
    return true;
  } catch (error) {
    if (attempt < MAX_RETRIES) {
      wakeUpMessage.value = `El servidor estaba en reposo. Reintentando conexión (${attempt}/${MAX_RETRIES})... 🚀`;
      await new Promise(resolve => setTimeout(resolve, RETRY_DELAY_MS));
      return checkServerHealth(attempt + 1);
    }
    return false;
  }
};

const startHealthCheck = async () => {
  isServerChecking.value = true;
  isServerReady.value = false;
  showRetryButton.value = false;
  wakeUpMessage.value = 'Iniciando conexión segura...';

  const slowLoadTimer = setTimeout(() => {
    if (!isServerReady.value) {
      wakeUpMessage.value = 'El servidor estaba en reposo. Levantando sistemas (puede tomar hasta 60 segundos)... 🚀';
    }
  }, 3000);

  const success = await checkServerHealth();
  clearTimeout(slowLoadTimer);

  if (success) {
    isServerReady.value = true;
    setTimeout(() => {
      isServerChecking.value = false;
    }, 400);
  } else {
    wakeUpMessage.value = 'No pudimos conectar con el servidor. Verifica tu conexión e intenta de nuevo.';
    showRetryButton.value = true;
  }
};

onMounted(() => {
  startHealthCheck();
});
</script>

<template>
  <router-view v-if="isServerReady"></router-view>

  <ServerWakeUp 
    :is-waking-up="isServerChecking" 
    :message="wakeUpMessage"
    :show-retry="showRetryButton"
    @retry="startHealthCheck"
  />
</template>