<script setup>
defineEmits(['menuClick'])
</script>

<template>
  <header
    class="shrink-0 w-full bg-bg-surface/95 glass border-b border-border-subtle px-4 sm:px-6 py-3 !p-4"
  >
    <div class="flex items-center justify-between">
      <div class="flex items-center gap-3">
        <!-- Menu button (mobile only) -->
        <button
          @click="$emit('menuClick')"
          class="lg:hidden p-2 -ml-2 bg-bg-elevated hover:bg-bg-highlight rounded-full transition-all duration-200 active:scale-95"
        >
          <span class="material-symbols-outlined text-text-subdued">menu</span>
        </button>

        <!-- Brand (mobile only — desktop has sidebar) -->
        <div class="lg:hidden flex items-center gap-2.5">
          <div
            class="w-8 h-8 bg-primary rounded-full flex items-center justify-center shadow-spotify-medium"
          >
            <span class="material-symbols-outlined text-black text-base">school</span>
          </div>
          <div>
            <h1 class="text-sm font-bold leading-tight text-text-base">
              Chatbot Skripsi TI
            </h1>
            <p class="text-[9px] font-semibold text-text-subdued uppercase tracking-[0.15em]">
              UIN Alauddin Makassar
            </p>
          </div>
        </div>

        <!-- Title for desktop (sidebar already has brand) -->
        <div class="hidden lg:block">
          <h1 class="text-sm font-bold leading-tight text-text-base">
            Chatbot Skripsi TI
          </h1>
          <p class="text-[9px] font-semibold text-text-subdued uppercase tracking-[0.15em]">
            UIN Alauddin Makassar
          </p>
        </div>
      </div>

      <!-- Status Online — Pill Shape -->
      <div
        class="flex items-center gap-2 px-3.5 py-1.5 bg-primary/10 rounded-full border border-primary/20"
      >
        <span class="relative flex h-2 w-2">
          <span
            class="animate-ping absolute inline-flex h-full w-full rounded-full bg-primary opacity-60"
          ></span>
          <span class="relative inline-flex rounded-full h-2 w-2 bg-primary"></span>
        </span>
        <span class="text-[10px] font-bold text-primary uppercase tracking-wider">Online</span>
      </div>
    </div>
  </header>
</template>
