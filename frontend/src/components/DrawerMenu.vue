<script setup>
import { ref } from 'vue'

defineProps({
  isOpen: Boolean,
})

const emit = defineEmits(['close'])

const searchMode = ref('rag')

const chatHistory = [
  { id: 1, title: 'Pencarian AI 2023', time: '2 jam lalu' },
  { id: 2, title: 'Deep Learning Skripsi', time: 'Kemarin' },
  { id: 3, title: 'Metode penelitian NLP', time: '3 hari lalu' },
]
</script>

<template>
  <!-- Backdrop -->
  <Transition name="fade">
    <div
      v-if="isOpen"
      class="fixed inset-0 bg-black/30 backdrop-blur-sm z-50 lg:hidden"
      @click="$emit('close')"
    ></div>
  </Transition>

  <!-- Drawer Panel -->
  <Transition name="slide-left">
    <div
      v-if="isOpen"
      class="fixed inset-y-0 left-0 w-[85%] max-w-[320px] bg-white dark:bg-slate-900 shadow-2xl z-50 flex flex-col overflow-hidden lg:hidden"
    >
      <!-- Header -->
      <div class="flex items-center justify-between p-5 pb-4 shrink-0">
        <div class="flex items-center gap-3">
          <div
            class="w-9 h-9 bg-gradient-to-br from-primary to-primary-dark rounded-xl flex items-center justify-center shadow-md"
          >
            <span class="material-symbols-outlined text-white text-lg">school</span>
          </div>
          <div>
            <h2 class="text-base font-bold text-slate-900 dark:text-white leading-tight">
              Panel Kontrol
            </h2>
            <p class="text-[10px] text-slate-400 uppercase tracking-[0.2em] font-semibold">
              Chatbot Skripsi
            </p>
          </div>
        </div>
        <button
          @click="$emit('close')"
          class="p-2 rounded-xl hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors active:scale-95"
        >
          <span class="material-symbols-outlined text-slate-400 text-xl">close</span>
        </button>
      </div>

      <!-- Content -->
      <div class="flex-1 overflow-y-auto hide-scrollbar px-4 pb-4 space-y-6">
        <!-- New Chat -->
        <button
          @click="$emit('close')"
          class="w-full flex items-center justify-center gap-2 py-2.5 px-4 bg-primary/10 hover:bg-primary/15 text-primary rounded-xl text-sm font-semibold transition-all duration-200 border border-primary/20 hover:border-primary/30 active:scale-[0.98]"
        >
          <span class="material-symbols-outlined text-lg">add</span>
          <span>Obrolan Baru</span>
        </button>

        <!-- Mode Pencarian -->
        <section>
          <h3 class="text-[10px] font-bold text-slate-400 uppercase tracking-[0.15em] mb-3 px-1">
            Mode Pencarian
          </h3>
          <div class="space-y-2">
            <!-- RAG Mode -->
            <label
              class="relative flex items-center p-3.5 rounded-xl border-2 cursor-pointer transition-all duration-200 active:scale-[0.98]"
              :class="
                searchMode === 'rag'
                  ? 'border-primary bg-primary/5 shadow-sm'
                  : 'border-slate-100 dark:border-slate-800 hover:border-slate-200 dark:hover:border-slate-700'
              "
            >
              <div class="flex-1">
                <p class="text-sm font-bold text-slate-900 dark:text-slate-100">RAG Mode</p>
                <p class="text-[10px] text-slate-400 mt-0.5">Akurasi tinggi berdasarkan database</p>
              </div>
              <input v-model="searchMode" type="radio" value="rag" class="sr-only" />
              <span
                class="material-symbols-outlined text-lg transition-colors"
                :class="
                  searchMode === 'rag' ? 'text-primary' : 'text-slate-300 dark:text-slate-600'
                "
                >{{
                  searchMode === 'rag' ? 'radio_button_checked' : 'radio_button_unchecked'
                }}</span
              >
            </label>

            <!-- HyDE Mode -->
            <label
              class="relative flex items-center p-3.5 rounded-xl border-2 cursor-pointer transition-all duration-200 active:scale-[0.98]"
              :class="
                searchMode === 'hyde'
                  ? 'border-primary bg-primary/5 shadow-sm'
                  : 'border-slate-100 dark:border-slate-800 hover:border-slate-200 dark:hover:border-slate-700'
              "
            >
              <div class="flex-1">
                <p class="text-sm font-bold text-slate-900 dark:text-slate-100">HyDE Mode</p>
                <p class="text-[10px] text-slate-400 mt-0.5">Pencarian semantik lebih luas</p>
              </div>
              <input v-model="searchMode" type="radio" value="hyde" class="sr-only" />
              <span
                class="material-symbols-outlined text-lg transition-colors"
                :class="
                  searchMode === 'hyde' ? 'text-primary' : 'text-slate-300 dark:text-slate-600'
                "
                >{{
                  searchMode === 'hyde' ? 'radio_button_checked' : 'radio_button_unchecked'
                }}</span
              >
            </label>
          </div>
        </section>

        <!-- Divider -->
        <div class="border-t border-slate-100 dark:border-slate-800/60"></div>

        <!-- History Section -->
        <section>
          <h3 class="text-[10px] font-bold text-slate-400 uppercase tracking-[0.15em] mb-3 px-1">
            Riwayat Obrolan
          </h3>
          <div class="space-y-1">
            <button
              v-for="chat in chatHistory"
              :key="chat.id"
              class="w-full text-left px-3 py-2.5 rounded-xl hover:bg-slate-50 dark:hover:bg-slate-800/50 flex items-center gap-2.5 group transition-all duration-200 active:scale-[0.98]"
            >
              <span
                class="material-symbols-outlined text-slate-300 dark:text-slate-600 text-lg group-hover:text-primary transition-colors"
                >chat_bubble_outline</span
              >
              <div class="flex-1 min-w-0">
                <span
                  class="text-xs font-medium text-slate-600 dark:text-slate-400 truncate block group-hover:text-slate-900 dark:group-hover:text-slate-200 transition-colors"
                  >{{ chat.title }}</span
                >
                <span class="text-[9px] text-slate-300 dark:text-slate-600">{{ chat.time }}</span>
              </div>
            </button>
          </div>
        </section>
      </div>

      <!-- Footer -->
      <div class="p-4 border-t border-slate-100 dark:border-slate-800/60 shrink-0">
        <div class="flex items-center gap-2">
          <div class="w-2 h-2 rounded-full bg-primary animate-pulse-subtle"></div>
          <p class="text-[10px] text-slate-400 font-medium">v1.0.4 — Sistem aktif</p>
        </div>
      </div>
    </div>
  </Transition>
</template>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.slide-left-enter-active,
.slide-left-leave-active {
  transition: transform 0.35s cubic-bezier(0.16, 1, 0.3, 1);
}

.slide-left-enter-from,
.slide-left-leave-to {
  transform: translateX(-100%);
}
</style>
