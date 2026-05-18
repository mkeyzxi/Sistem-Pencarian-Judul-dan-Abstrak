<script setup>
import { ref } from 'vue'
import { useSearchMode } from '@/composables/useSearchMode'

defineProps({
  isOpen: Boolean,
})

const emit = defineEmits(['close'])

const { searchMode, setMode } = useSearchMode()

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
      class="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 lg:hidden"
      @click="$emit('close')"
    ></div>
  </Transition>

  <!-- Drawer Panel -->
  <Transition name="slide-left">
    <div
      v-if="isOpen"
      class="fixed inset-y-0 left-0 w-[85%] max-w-[320px] bg-bg-base shadow-spotify-heavy z-50 flex flex-col overflow-hidden lg:hidden"
    >
      <!-- Header -->
      <div class="flex items-center justify-between p-5 pb-4 shrink-0">
        <div class="flex items-center gap-3">
          <div
            class="w-10 h-10 bg-primary rounded-full flex items-center justify-center shadow-spotify-medium"
          >
            <span class="material-symbols-outlined text-black text-lg">school</span>
          </div>
          <div>
            <h2 class="text-base font-bold text-text-base leading-tight">
              Panel Kontrol
            </h2>
            <p class="text-[10px] text-text-subdued uppercase tracking-[0.2em] font-semibold">
              Chatbot Skripsi
            </p>
          </div>
        </div>
        <button
          @click="$emit('close')"
          class="p-2 rounded-full bg-bg-elevated hover:bg-bg-highlight transition-all duration-200 active:scale-95"
        >
          <span class="material-symbols-outlined text-text-subdued text-xl">close</span>
        </button>
      </div>

      <!-- Content -->
      <div class="flex-1 overflow-y-auto hide-scrollbar px-4 pb-4 space-y-5">
        <!-- New Chat -->
        <button
          @click="$emit('close')"
          class="w-full flex items-center justify-center gap-2 py-2.5 px-4 bg-primary/10 hover:bg-primary/15 text-primary rounded-full text-sm font-bold uppercase tracking-wider transition-all duration-200 border border-primary/20 hover:border-primary/30 active:scale-[0.98]"
        >
          <span class="material-symbols-outlined text-lg">add</span>
          <span>Obrolan Baru</span>
        </button>

        <!-- Mode Pencarian -->
        <section>
          <h3 class="text-[10px] font-bold text-text-subdued uppercase tracking-[0.15em] mb-3 px-1">
            Mode Pencarian
          </h3>
          <div class="space-y-2">
            <!-- RAG Mode -->
            <label
              class="relative flex items-center p-3.5 rounded-lg cursor-pointer transition-all duration-200 active:scale-[0.98]"
              :class="
                searchMode === 'rag'
                  ? 'bg-bg-highlight border border-primary/30 shadow-spotify-medium'
                  : 'bg-bg-elevated border border-transparent hover:bg-bg-highlight'
              "
            >
              <div class="flex-1">
                <p class="text-sm font-bold text-text-base">RAG Mode</p>
                <p class="text-[10px] text-text-subdued mt-0.5">Akurasi tinggi berdasarkan database</p>
              </div>
              <input v-model="searchMode" @click="setMode('rag')" type="radio" value="rag" class="sr-only" />
              <span
                class="material-symbols-outlined text-lg transition-colors"
                :class="
                  searchMode === 'rag' ? 'text-primary' : 'text-text-muted'
                "
                >{{
                  searchMode === 'rag' ? 'radio_button_checked' : 'radio_button_unchecked'
                }}</span
              >
            </label>

            <!-- HyDE Mode -->
            <label
              class="relative flex items-center p-3.5 rounded-lg cursor-pointer transition-all duration-200 active:scale-[0.98]"
              :class="
                searchMode === 'hyde'
                  ? 'bg-bg-highlight border border-primary/30 shadow-spotify-medium'
                  : 'bg-bg-elevated border border-transparent hover:bg-bg-highlight'
              "
            >
              <div class="flex-1">
                <p class="text-sm font-bold text-text-base">HyDE Mode</p>
                <p class="text-[10px] text-text-subdued mt-0.5">Pencarian semantik lebih luas</p>
              </div>
              <input v-model="searchMode" @click="setMode('hyde')" type="radio" value="hyde" class="sr-only" />
              <span
                class="material-symbols-outlined text-lg transition-colors"
                :class="
                  searchMode === 'hyde' ? 'text-primary' : 'text-text-muted'
                "
                >{{
                  searchMode === 'hyde' ? 'radio_button_checked' : 'radio_button_unchecked'
                }}</span
              >
            </label>
          </div>
        </section>

        <!-- Divider -->
        <div class="border-t border-border-subtle"></div>

        <!-- History Section -->
        <section>
          <h3 class="text-[10px] font-bold text-text-subdued uppercase tracking-[0.15em] mb-3 px-1">
            Riwayat Obrolan
          </h3>
          <div class="space-y-1">
            <button
              v-for="chat in chatHistory"
              :key="chat.id"
              class="w-full text-left px-3 py-2.5 rounded-lg hover:bg-bg-elevated flex items-center gap-2.5 group transition-all duration-200 active:scale-[0.98]"
            >
              <span
                class="material-symbols-outlined text-text-muted text-lg group-hover:text-primary transition-colors"
                >chat_bubble_outline</span
              >
              <div class="flex-1 min-w-0">
                <span
                  class="text-xs font-medium text-text-subdued truncate block group-hover:text-text-base transition-colors"
                  >{{ chat.title }}</span
                >
                <span class="text-[9px] text-text-muted">{{ chat.time }}</span>
              </div>
            </button>
          </div>
        </section>
      </div>

      <!-- Footer -->
      <div class="p-4 border-t border-border-subtle shrink-0">
        <div class="flex items-center gap-2">
          <div class="w-2 h-2 rounded-full bg-primary animate-pulse-glow"></div>
          <p class="text-[10px] text-text-subdued font-medium">v1.0.4 — Sistem aktif</p>
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
