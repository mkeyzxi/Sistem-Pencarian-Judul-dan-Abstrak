<script setup>
import { ref, onMounted } from 'vue'
import { Icon } from '@iconify/vue'

const isDark = ref(false)

function setTheme(dark) {
  const el = document.documentElement
  if (dark) el.classList.add('dark')
  else el.classList.remove('dark')
  localStorage.setItem('theme', dark ? 'dark' : 'light')
  isDark.value = dark
}

onMounted(() => {
  const stored = localStorage.getItem('theme')
  if (stored === 'dark') setTheme(true)
  else if (stored === 'light') setTheme(false)
  else {
    const prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches
    setTheme(prefersDark)
  }
})

const toggle = () => setTheme(!isDark.value)
</script>

<template>
  <button @click="toggle" aria-label="Toggle theme" class="w-9 h-9 border  rounded-full flex items-center justify-center
           transition-all duration-200
           hover:scale-105
           hover:bg-green-100
           dark:hover:bg-green-900/30">
    <Icon :icon="isDark ? 'mdi:weather-night' : 'mdi:weather-sunny'"
      class="w-5 h-5 text-green-500 dark:text-green-400" />
  </button>
</template>
