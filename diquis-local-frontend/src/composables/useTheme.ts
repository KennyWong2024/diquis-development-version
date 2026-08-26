import { ref, onMounted } from 'vue';

const theme = ref<'light' | 'dark'>('light');

export function useTheme() {
    const toggleTheme = () => {
        theme.value = theme.value === 'light' ? 'dark' : 'light';
        console.log("Cambiando tema a:", theme.value);

        if (theme.value === 'dark') {
            document.documentElement.classList.add('dark');
            localStorage.setItem('theme', 'dark');
        } else {
            document.documentElement.classList.remove('dark');
            localStorage.setItem('theme', 'light');
        }
    };

    onMounted(() => {
        const savedTheme = localStorage.getItem('theme');
        const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;

        if (savedTheme === 'dark' || (!savedTheme && prefersDark)) {
            theme.value = 'dark';
            document.documentElement.classList.add('dark');
        } else {
            theme.value = 'light';
            document.documentElement.classList.remove('dark');
        }
        console.log("Tema inicial cargado:", theme.value);
    });

    return { theme, toggleTheme };
}