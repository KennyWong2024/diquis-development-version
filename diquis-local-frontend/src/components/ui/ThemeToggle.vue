<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { Sun, Moon } from 'lucide-vue-next';

const isDark = ref(false);

onMounted(() => {
  if (localStorage.theme === 'dark' || (!('theme' in localStorage) && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
    isDark.value = true;
    document.documentElement.classList.add('dark');
  } else {
    isDark.value = false;
    document.documentElement.classList.remove('dark');
  }
});

const toggleTheme = () => {
  isDark.value = !isDark.value;
  if (isDark.value) {
    document.documentElement.classList.add('dark');
    localStorage.theme = 'dark';
  } else {
    document.documentElement.classList.remove('dark');
    localStorage.theme = 'light';
  }
};
</script>

<template>
  <button 
    @click="toggleTheme" 
    class="relative inline-flex h-7 w-12 items-center rounded-full bg-slate-200/50 dark:bg-white/10 backdrop-blur-md border border-slate-300/50 dark:border-white/5 cursor-pointer transition-colors duration-300 shadow-inner"
    aria-label="Alternar tema"
  >
    <div 
      class="inline-flex h-5 w-5 items-center justify-center rounded-full bg-white dark:bg-slate-800 shadow transform transition-transform duration-300 ease-in-out"
      :class="isDark ? 'translate-x-6' : 'translate-x-1'"
    >
      <Moon v-if="isDark" class="w-3 h-3 text-slate-300" />
      <Sun v-else class="w-3 h-3 text-amber-500" />
    </div>
  </button>
</template>