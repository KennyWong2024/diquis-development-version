<script setup lang="ts">
import { useScreen } from '../composables/useScreen';
import DesktopLayout from './DesktopLayout.vue';
import MobileLayout from './MobileLayout.vue';

const { isMobile } = useScreen();
</script>

<template>
  <MobileLayout v-if="isMobile">
    <slot /> </MobileLayout>
  
  <DesktopLayout v-else>
    <slot />
  </DesktopLayout>
</template>