import { ref, onMounted, onUnmounted } from 'vue';

export function useScreen() {
    const isMobile = ref(false);
    const BREAKPOINT = 1024;

    const update = () => {
        isMobile.value = window.innerWidth < BREAKPOINT;
    };

    onMounted(() => {
        update();
        window.addEventListener('resize', update);
    });

    onUnmounted(() => {
        window.removeEventListener('resize', update);
    });

    return { isMobile };
}