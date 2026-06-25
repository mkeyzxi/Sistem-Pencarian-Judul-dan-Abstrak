<script setup>
import { ref } from 'vue'
import { useSearchMode } from '@/composables/useSearchMode'

const props = defineProps({
  isOpen: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['close'])

const { searchMode, setMode } = useSearchMode()

const chatHistory = ref([
  { id: 1, title: 'Judul skripsi data mining', time: '2 jam lalu' },
  { id: 2, title: 'Rekomendasi topik AI', time: 'Kemarin' },
  { id: 3, title: 'Metode penelitian NLP', time: '3 hari lalu' },
])

console.log(searchMode)
</script>

<template>
  <!-- Mobile Backdrop Overlay -->
  <div 
    v-if="isOpen" 
    class="fixed inset-0 bg-black/50 z-40 lg:hidden transition-opacity"
    @click="emit('close')"
  ></div>

  <aside
    class="fixed lg:sticky top-0 left-0 z-50 flex flex-col w-[280px] h-screen bg-bg-base border-r border-border-subtle overflow-y-auto hide-scrollbar shrink-0 !p-2 transition-transform duration-300 ease-in-out lg:translate-x-0"
    :class="isOpen ? 'translate-x-0' : '-translate-x-full'"
  >
    <!-- Brand Header -->
    <div class="p-5 pb-4 flex justify-between items-center">
      <div class="flex items-center gap-3">
        <div class="w-10 h-10 rounded-full flex items-center justify-center shadow-spotify-medium shrink-0">
          <!-- <span class="material-symbols-outlined text-black text-lg">school</span> -->
          <img src="/logo-pencarian.png" alt="Logo Pencarian" class="w-full h-full object-contain">
        </div>
        <div>
          <h2 class="text-base font-bold text-text-base leading-tight">
            Panel Kontrol
          </h2>
          <p class="text-[10px] text-text-subdued uppercase tracking-[0.2em] font-semibold">
            Pencarian Skripsi TI
          </p>
        </div>
      </div>
      <!-- Mobile Close Button -->
      <button 
        class="lg:hidden p-2 text-text-subdued hover:text-text-base rounded-full hover:bg-bg-elevated transition-colors" 
        @click="emit('close')"
      >
        <span class="material-symbols-outlined text-lg">close</span>
      </button>
    </div>

    <div class="flex-1 !px-2 !space-y-5 overflow-y-auto hide-scrollbar !gap-4 !mt-10">
      <!-- Mode Pencarian -->
      <section>
        <h3 class="text-[10px] font-bold text-text-subdued uppercase tracking-[0.15em] !mb-3 !px-1">
          Mode Pencarian
        </h3>
        <div class="space-y-2 flex flex-col gap-2 ">
          <label class="flex items-center gap-3 px-3.5 py-3 rounded-lg cursor-pointer transition-all duration-200 !px-2"
            :class="searchMode === 'rag'
              ? 'bg-bg-highlight border border-primary/30'
              : 'bg-bg-elevated hover:bg-bg-highlight border border-transparent'
              ">
            <div class="w-4 h-4 rounded-full border-2 flex items-center justify-center transition-colors " :class="searchMode === 'rag' ? 'border-primary' : 'border-border-bright'
              ">
              <div v-if="searchMode === 'rag'" class="w-2 h-2 rounded-full bg-primary"></div>
            </div>
            <input v-model="searchMode" @click="setMode('rag')" type="radio" value="rag" class="sr-only" />
            <div class="flex-1 min-w-0">
              <span class="text-sm font-bold text-text-base">RAG Mode</span>
              <p class="text-[10px] text-text-subdued mt-0.5">Akurasi tinggi</p>
            </div>
            <span v-if="searchMode === 'rag'"
              class="material-symbols-outlined text-primary text-base">check_circle</span>
          </label>

          <label class="flex items-center gap-3 px-3.5 py-3 rounded-lg cursor-pointer transition-all duration-200 !px-2"
            :class="searchMode === 'hyde'
              ? 'bg-bg-highlight border border-primary/30'
              : 'bg-bg-elevated hover:bg-bg-highlight border border-transparent'
              ">
            <div class="w-4 h-4 rounded-full border-2 flex items-center justify-center transition-colors" :class="searchMode === 'hyde' ? 'border-primary' : 'border-border-bright'
              ">
              <div v-if="searchMode === 'hyde'" class="w-2 h-2 rounded-full bg-primary"></div>
            </div>
            <input v-model="searchMode" @click="setMode('hyde')" type="radio" value="hyde" class="sr-only " />
            <div class="flex-1 min-w-0 ">
              <span class="text-sm font-bold text-text-base">HyDE Mode</span>
              <p class="text-[10px] text-text-subdued mt-0.5">Pencarian semantik</p>
            </div>
            <span v-if="searchMode === 'hyde'"
              class="material-symbols-outlined text-primary text-base">check_circle</span>
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
        <p class="text-[10px] text-text-subdued font-medium">v1.0.4 - Sistem aktif</p>
      </div>
    </div>
  </aside>
</template>
