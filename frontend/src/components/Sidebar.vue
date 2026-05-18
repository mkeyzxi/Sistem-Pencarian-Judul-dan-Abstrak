<script setup>
import { ref } from 'vue'
import { useSearchMode } from '@/composables/useSearchMode'

const { searchMode, setMode } = useSearchMode()

const chatHistory = ref([
  { id: 1, title: 'Judul skripsi data mining', time: '2 jam lalu' },
  { id: 2, title: 'Rekomendasi topik AI', time: 'Kemarin' },
  { id: 3, title: 'Metode penelitian NLP', time: '3 hari lalu' },
])

console.log(searchMode)
</script>

<template>
  <aside
    class="hidden lg:flex flex-col w-[280px] h-screen sticky top-0 bg-bg-base border-r border-border-subtle overflow-y-auto hide-scrollbar shrink-0 !p-2"
  >
    <!-- Brand Header -->
    <div class="p-5 pb-4">
      <div class="flex items-center gap-3 mb-1">
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
            Chatbot Skripsi TI
          </p>
        </div>
      </div>
    </div>

    <div class="flex-1 !px-2 !space-y-5 overflow-y-auto hide-scrollbar !gap-4 !mt-10">
      <!-- Mode Pencarian -->
      <section>
        <h3
          class="text-[10px] font-bold text-text-subdued uppercase tracking-[0.15em] !mb-3 !px-1"
        >
          Mode Pencarian
        </h3>
        <div class="space-y-2">
          <label
            class="flex items-center gap-3 px-3.5 py-3 rounded-lg cursor-pointer transition-all duration-200"
            :class="
              searchMode === 'rag'
                ? 'bg-bg-highlight border border-primary/30'
                : 'bg-bg-elevated hover:bg-bg-highlight border border-transparent'
            "
          >
            <div
              class="w-4 h-4 rounded-full border-2 flex items-center justify-center transition-colors"
              :class="
                searchMode === 'rag' ? 'border-primary' : 'border-border-bright'
              "
            >
              <div v-if="searchMode === 'rag'" class="w-2 h-2 rounded-full bg-primary"></div>
            </div>
            <input
              v-model="searchMode"
              @click="setMode('rag')"
              type="radio"
              value="rag"
              class="sr-only"
            />
            <div class="flex-1 min-w-0">
              <span class="text-sm font-bold text-text-base">RAG Mode</span>
              <p class="text-[10px] text-text-subdued mt-0.5">Akurasi tinggi</p>
            </div>
            <span
              v-if="searchMode === 'rag'"
              class="material-symbols-outlined text-primary text-base"
              >check_circle</span
            >
          </label>

          <label
            class="flex items-center gap-3 px-3.5 py-3 rounded-lg cursor-pointer transition-all duration-200"
            :class="
              searchMode === 'hyde'
                ? 'bg-bg-highlight border border-primary/30'
                : 'bg-bg-elevated hover:bg-bg-highlight border border-transparent'
            "
          >
            <div
              class="w-4 h-4 rounded-full border-2 flex items-center justify-center transition-colors"
              :class="
                searchMode === 'hyde' ? 'border-primary' : 'border-border-bright'
              "
            >
              <div v-if="searchMode === 'hyde'" class="w-2 h-2 rounded-full bg-primary"></div>
            </div>
            <input
              v-model="searchMode"
              @click="setMode('hyde')"
              type="radio"
              value="hyde"
              class="sr-only"
            />
            <div class="flex-1 min-w-0">
              <span class="text-sm font-bold text-text-base"
                >HyDE Mode</span
              >
              <p class="text-[10px] text-text-subdued mt-0.5">Pencarian semantik</p>
            </div>
            <span
              v-if="searchMode === 'hyde'"
              class="material-symbols-outlined text-primary text-base"
              >check_circle</span
            >
          </label>
        </div>
      </section>

      <!-- Divider -->
      <div class="border-t border-border-subtle"></div>

      <!-- Obrolan Anda (commented out same as before) -->
      <!-- <section>
        <h3
          class="text-[10px] font-bold text-text-subdued uppercase tracking-[0.15em] mb-3 px-1"
        >
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
      </section> -->
    </div>

    <!-- Footer -->
    <div class="p-4 border-t border-border-subtle shrink-0">
      <div class="flex items-center gap-2">
        <div class="w-2 h-2 rounded-full bg-primary animate-pulse-glow"></div>
        <p class="text-[10px] text-text-subdued font-medium">v1.0.4 — Sistem aktif</p>
      </div>
    </div>
  </aside>
</template>
