<script setup lang="ts">
withDefaults(defineProps<{
  clip?: boolean;
}>(), {
  clip: false
});
</script>

<template>
  <div 
    class="relative rounded-3xl transition-all duration-500
           bg-white/60 dark:bg-[#111111]/70 
           backdrop-blur-2xl 
           border border-white/50 dark:border-white/5 
           shadow-[0_8px_30px_rgb(0,0,0,0.04)] dark:shadow-[0_8px_30px_rgb(0,0,0,0.3)]
           hover:bg-white/70 dark:hover:bg-[#1a1a1a]/70 group"
    :class="clip ? 'overflow-hidden' : 'overflow-visible'"
  >
    
    <div class="absolute inset-0 rounded-[inherit] border-t border-white/60 dark:border-white/10 pointer-events-none z-20 transition-opacity duration-500 opacity-70 group-hover:opacity-100"></div>
    
    <div class="relative z-10 h-full w-full">
      <slot />
    </div>
  </div>
</template>