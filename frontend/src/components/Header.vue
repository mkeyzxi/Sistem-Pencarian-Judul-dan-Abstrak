<script setup>
import ThemeToggle from './ThemeToggle.vue'
defineEmits(['toggleDrawer'])
</script>

<template>
  <header
    class="sticky top-0 z-40 w-full bg-white dark:bg-slate-900 border-b border-slate-200/50 dark:border-slate-800/50 px-4 py-2.5 shadow-sm">
    <div class="flex items-center justify-between max-w-7xl mx-auto h-12">
      <!-- Left Section: Menu + Title -->
      <div class="flex items-center gap-2 min-w-0">
        <!-- Menu Button (Mobile Only) -->
        <button @click="$emit('toggleDrawer')"
          class="lg:hidden p-1.5 -ml-1.5 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-lg transition-colors flex-shrink-0">
          <span class="material-symbols-outlined text-slate-600 dark:text-slate-400 text-xl">
            menu
          </span>
        </button>
        <!-- Title -->
        <div class="min-w-0">
          <h1 class="text-xs font-bold leading-tight text-slate-900 dark:text-slate-100 truncate">
            Chatbot Skripsi TI
          </h1>
          <p class="text-[9px] font-medium text-slate-400 dark:text-slate-500 uppercase tracking-wide truncate">
            UIN Alauddin Makassar
          </p>
        </div>
      </div>

      <!-- Right Section: Theme toggle + Status -->
      <div class="flex items-center gap-2">
        <ThemeToggle />
        <div class="flex items-center gap-2">
          <span class="relative flex h-2 w-2">
            <span
              class="animate-pulse absolute inline-flex h-full w-full rounded-full bg-emerald-500 opacity-75"></span>
            <span class="relative inline-flex rounded-full h-2 w-2 bg-emerald-600"></span>
          </span>
          <span class="text-[11px] font-medium text-slate-600 dark:text-slate-300 tracking-wide">
            Siap Konsultasi
          </span>
        </div>
      </div>
    </div>
  </header>
</template>
