<script setup lang="ts">
</script>

<template>
  <div class="fixed inset-0 w-screen h-screen flex items-center justify-center overflow-hidden bg-[#fbfbfb] dark:bg-[#050505] transition-colors duration-700">
    
    <div class="relative z-10 w-full h-full flex items-center justify-center">
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </div>
  </div>
</template>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease, transform 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translateY(10px);
}
</style>