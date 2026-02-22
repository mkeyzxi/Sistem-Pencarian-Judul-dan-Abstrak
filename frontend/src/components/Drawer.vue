<script setup>
import { ref } from 'vue'

const props = defineProps({
  isOpen: Boolean
})

const emit = defineEmits(['close'])

const searchMode = ref('rag')
const selectedYear = ref('all')
const selectedInterest = ref('all')

const interests = [
  { value: 'all', label: 'Semua' },
  { value: 'ai', label: 'AI' },
  { value: 'web', label: 'Web' },
  { value: 'mobile', label: 'Mobile' },
  { value: 'iot', label: 'IoT' }
]

const chatHistory = [
  { id: 1, title: 'Pencarian AI 2023' },
  { id: 2, title: 'Deep Learning Skripsi' }
]
</script>

<template>
  <!-- Backdrop -->
  <Transition name="fade">
    <div v-if="isOpen" class="fixed inset-0 bg-slate-900/40 backdrop-blur-sm z-50" @click="$emit('close')"></div>

  </Transition>

  <!-- Drawer -->

  <Transition name="slide">
    <div v-if="isOpen"
      class="fixed right-0 top-0 h-full w-4/5 max-w-sm bg-white dark:bg-slate-900 shadow-2xl z-50 flex flex-col p-6 overflow-y-auto hide-scrollbar">
      <!-- Header -->

      <div class="flex items-center justify-between mb-8">
        <h2 class="text-lg font-bold">Pengaturan</h2>
        <button @click="$emit('close')" </button> <span class="material-symbols-outlined">close</span> class="p-2
          rounded-full hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors">

          <!-- Content -->
          <div class="space-y-8">
            <!-- Search Modes -->
            <section>
              <h3 class="text-xs font-bold text-slate-400 uppercase mb-4">Mode Pencarian</h3>
              <div class="space-y-3">
                <label class="relative flex items-center p-3 rounded-xl border-2 transition-all cursor-pointer"
                  :class="searchMode === 'rag' ? 'border-primary bg-primary/5' : 'border-slate-100 dark:border-slate-800'">
                  <div class="flex-1">
                    <p class="text-sm font-bold text-slate-900 dark:text-slate-100">RAG Mode</p>
                    <p class="text-[10px] text-slate-500">Akurasi tinggi berdasarkan database</p>
                  </div>
                  <input v-model="searchMode" type="radio" value="rag"
                    class="text-primary focus:ring-primary h-4 w-4" />
                </label>
                <label class="relative flex items-center p-3 rounded-xl border-2 transition-all cursor-pointer"
                  :class="searchMode === 'hyde' ? 'border-primary bg-primary/5' : 'border-slate-100 dark:border-slate-800'">
                  <div class="flex-1">
                    <p class="text-sm font-bold text-slate-900 dark:text-slate-100">HyDE Mode</p>
                    <p class="text-[10px] text-slate-500">Pencarian semantik lebih luas</p>
                  </div>
                  <input v-model="searchMode" type="radio" value="hyde"
                    class="text-primary focus:ring-primary h-4 w-4" />
                </label>
              </div>
            </section>

            <!-- Filters -->
            <section>
              <h3 class="text-xs font-bold text-slate-400 uppercase mb-4">Filter Skripsi</h3>
              <div class="space-y-4">
                <!-- Tahun Kelulusan -->
                <div>
                  <label class="text-xs font-medium text-slate-600 dark:text-slate-400 mb-2 block">Tahun
                    Kelulusan</label>
                  <select v-model="selectedYear"
                    class="w-full rounded-lg border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-slate-900 dark:text-slate-100 text-sm focus:ring-primary focus:border-primary py-2 px-3">
                    <option value="all">Semua Tahun</option>
                    <option value="2024">2024</option>
                    <option value="2023">2023</option>
                    <option value="2022">2022</option>
                    <option value="2021">2021</option>
                  </select>
                </div>

                <!-- Bidang Minat -->
                <div>
                  <label class="text-xs font-medium text-slate-600 dark:text-slate-400 mb-2 block">Bidang Minat</label>
                  <div class="flex flex-wrap gap-2">
                    <button v-for="interest in interests" :key="interest.value"
                      @click="selectedInterest = interest.value"
                      :class="selectedInterest === interest.value ? 'bg-primary text-white' : 'bg-slate-100 dark:bg-slate-800 text-slate-900 dark:text-slate-100'"
                      class="px-3 py-1.5 rounded-full text-[11px] font-bold transition-colors">
                      {{ interest.label }}
                    </button>
                  </div>
                </div>
              </div>
            </section>

            <!-- History -->
            <section>
              <h3 class="text-xs font-bold text-slate-400 uppercase mb-4">Obrolan Anda</h3>
              <div class="space-y-2">
                <button v-for="chat in chatHistory" :key="chat.id"
                  class="w-full text-left p-3 rounded-lg hover:bg-slate-50 dark:hover:bg-slate-800 flex items-center gap-3 transition-colors">
                  <span class="material-symbols-outlined text-slate-400 text-lg">history</span>
                  <span class="text-xs font-medium truncate">{{ chat.title }}</span>
                </button>
              </div>
            </section>
          </div>
      </div>
    </div>
  </Transition>
</template>

<style scoped>
.hide-scrollbar::-webkit-scrollbar {
  display: none;
}

.hide-scrollbar {
  -ms-overflow-style: none;
  scrollbar-width: none;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.slide-enter-active,
.slide-leave-active {
  transition: transform 0.3s ease;
}

.slide-enter-from,
.slide-leave-to {
  transform: translateX(100%);
}
</style>
