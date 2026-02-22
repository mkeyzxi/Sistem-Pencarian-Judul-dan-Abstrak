<script setup>
defineEmits(['menuClick'])
</script>

<template>
  <header
    class="shrink-0 w-full glass bg-white/90 dark:bg-slate-900/90 border-b border-slate-200/60 dark:border-slate-800/60 px-4 sm:px-6 py-3"
  >
    <div class="flex items-center justify-between">
      <div class="flex items-center gap-3">
        <!-- Menu button (mobile only) -->
        <button
          @click="$emit('menuClick')"
          class="lg:hidden p-2 -ml-2 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-xl transition-all duration-200 active:scale-95"
        >
          <span class="material-symbols-outlined text-slate-500 dark:text-slate-400">menu</span>
        </button>

        <!-- Brand (mobile only — desktop has sidebar) -->
        <div class="lg:hidden flex items-center gap-2.5">
          <div
            class="w-8 h-8 bg-gradient-to-br from-primary to-primary-dark rounded-lg flex items-center justify-center shadow-sm"
          >
            <span class="material-symbols-outlined text-white text-base">school</span>
          </div>
          <div>
            <h1 class="text-sm font-bold leading-tight text-slate-900 dark:text-slate-100">
              Chatbot Skripsi TI
            </h1>
            <p class="text-[9px] font-medium text-slate-400 uppercase tracking-wider">
              UIN Alauddin Makassar
            </p>
          </div>
        </div>

        <!-- Title for desktop (sidebar already has brand) -->
        <div class="hidden lg:block">
          <h1 class="text-sm font-bold leading-tight text-slate-900 dark:text-slate-100">
            Chatbot Skripsi TI
          </h1>
          <p class="text-[9px] font-medium text-slate-400 uppercase tracking-wider">
            UIN Alauddin Makassar
          </p>
        </div>
      </div>

      <!-- Status Online -->
      <div
        class="flex items-center gap-2 px-3 py-1.5 bg-primary/8 rounded-full border border-primary/15"
      >
        <span class="relative flex h-2 w-2">
          <span
            class="animate-ping absolute inline-flex h-full w-full rounded-full bg-primary opacity-60"
          ></span>
          <span class="relative inline-flex rounded-full h-2 w-2 bg-primary"></span>
        </span>
        <span class="text-[10px] font-bold text-primary uppercase tracking-wide">Online</span>
      </div>
    </div>
  </header>
</template>
