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
    class="hidden lg:flex flex-col w-[280px] h-screen sticky top-0 bg-white dark:bg-slate-900 border-r border-slate-200/70 dark:border-slate-800/70 overflow-y-auto hide-scrollbar shrink-0"
  >
    <!-- Brand Header -->
    <div class="p-6 pb-4">
      <div class="flex items-center gap-3 mb-1">
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
            Chatbot Skripsi TI
          </p>
        </div>
      </div>
    </div>

    <div class="flex-1 px-4 space-y-6 overflow-y-auto hide-scrollbar">
      <!-- New Chat Button -->
      <!-- <button
        class="w-full flex items-center justify-center gap-2 py-2.5 px-4 bg-primary/10 hover:bg-primary/15 text-primary rounded-xl text-sm font-semibold transition-all duration-200 border border-primary/20 hover:border-primary/30 active:scale-[0.98]"
      >
        <span class="material-symbols-outlined text-lg">add</span>
        <span>Obrolan Baru</span>
      </button> -->

      <!-- Mode Pencarian -->
      <section>
        <h3
          class="text-[10px] font-bold text-slate-400 dark:text-slate-500 uppercase tracking-[0.15em] mb-3 px-1"
        >
          Mode Pencarian
        </h3>
        <div class="space-y-1.5">
          <label
            class="flex items-center gap-3 px-3 py-2.5 rounded-xl cursor-pointer transition-all duration-200"
            :class="
              searchMode === 'rag'
                ? 'bg-primary/8 border border-primary/20 shadow-sm'
                : 'hover:bg-slate-50 dark:hover:bg-slate-800/50 border border-transparent'
            "
          >
            <div
              class="w-4 h-4 rounded-full border-2 flex items-center justify-center transition-colors"
              :class="
                searchMode === 'rag' ? 'border-primary' : 'border-slate-300 dark:border-slate-600'
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
              <span class="text-sm font-semibold text-slate-800 dark:text-slate-200">RAG Mode</span>
              <p class="text-[10px] text-slate-400 mt-0.5">Akurasi tinggi</p>
            </div>
            <span
              v-if="searchMode === 'rag'"
              class="material-symbols-outlined text-primary text-base"
              >check_circle</span
            >
          </label>

          <label
            class="flex items-center gap-3 px-3 py-2.5 rounded-xl cursor-pointer transition-all duration-200"
            :class="
              searchMode === 'hyde'
                ? 'bg-primary/8 border border-primary/20 shadow-sm'
                : 'hover:bg-slate-50 dark:hover:bg-slate-800/50 border border-transparent'
            "
          >
            <div
              class="w-4 h-4 rounded-full border-2 flex items-center justify-center transition-colors"
              :class="
                searchMode === 'hyde' ? 'border-primary' : 'border-slate-300 dark:border-slate-600'
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
              <span class="text-sm font-semibold text-slate-800 dark:text-slate-200"
                >HyDE Mode</span
              >
              <p class="text-[10px] text-slate-400 mt-0.5">Pencarian semantik</p>
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
      <div class="border-t border-slate-100 dark:border-slate-800/60"></div>

      <!-- Obrolan Anda -->
      <!-- <section>
        <h3
          class="text-[10px] font-bold text-slate-400 dark:text-slate-500 uppercase tracking-[0.15em] mb-3 px-1"
        >
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
      </section> -->
    </div>

    <!-- Footer -->
    <div class="p-4 border-t border-slate-100 dark:border-slate-800/60 shrink-0">
      <div class="flex items-center gap-2">
        <div class="w-2 h-2 rounded-full bg-primary animate-pulse-subtle"></div>
        <p class="text-[10px] text-slate-400 font-medium">v1.0.4 — Sistem aktif</p>
      </div>
    </div>
  </aside>
</template>
