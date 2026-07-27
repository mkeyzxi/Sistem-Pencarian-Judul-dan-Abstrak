<script setup>
// Main Chat Area Component - menampilkan chat bubbles atau empty state
import { ref, watch, nextTick, computed } from 'vue'
import { marked } from 'marked'
import { useChatbot } from '../composables/useChatbot'
import { useSearchMode } from '../composables/useSearchMode'
import TableResults from './TableResults.vue'
const { messages, isLoading, error, sendMessage } = useChatbot()
const { searchMode } = useSearchMode()

// Mode check untuk rendering kondisional
const isChatbotMode = computed(() => searchMode.value === 'chatbot')

// Konfigurasi marked agar render tabel dan lain-lain
marked.setOptions({
  breaks: true,
  gfm: true,
})

// Render markdown ke HTML
const renderMarkdown = (text) => {
  if (!text) return ''
  if (typeof text !== 'string') return String(text)
  return marked.parse(text)
}

// Auto-scroll ke bawah saat pesan baru masuk
const chatContainer = ref(null)
const scrollToBottom = () => {
  nextTick(() => {
    if (chatContainer.value) {
      chatContainer.value.scrollTop = chatContainer.value.scrollHeight
    }
  })
}
watch(() => messages.value.length, scrollToBottom)
watch(isLoading, scrollToBottom)

const submitMessage = (message) => {
  sendMessage(message, searchMode.value)
}
</script>

<template>
  <main ref="chatContainer" class="flex-1 overflow-y-auto relative flex flex-col thin-scrollbar !p-4">
    <!-- Empty State / Welcome -->
    <div v-if="messages.length === 0"
      class="flex-1 flex flex-col items-center justify-center px-4 sm:px-6 py-12 sm:py-16 text-center space-y-6 sm:space-y-8">
      <!-- Animated Icon -->
      <div class="animate-fade-up" style="animation-delay: 0ms">
        <div
          class="w-20 h-20 sm:w-24 sm:h-24 !p-2 bg-bg-elevated rounded-2xl flex items-center justify-center shadow-spotify-medium border border-border-subtle">
          <img v-if="!isChatbotMode" src="/logo-pencarian.png" alt="Logo Pencarian">
          <span v-else class="material-symbols-outlined text-4xl sm:text-5xl text-primary">smart_toy</span>
        </div>
      </div>

      <!-- Welcome Text (Dinamis berdasarkan mode) -->
      <div class="animate-fade-up !space-y-2 !sm:space-y-3 max-w-md !mb-4" style="animation-delay: 100ms">
        <h2 class="text-xl sm:text-2xl font-bold text-text-base leading-tight !mt-5">
          {{ isChatbotMode ? 'Asisten Skripsi TI' : 'Selamat datang' }}
        </h2>
        <p class="text-text-subdued text-sm sm:text-base leading-relaxed">
          {{ isChatbotMode
            ? 'Konsultasikan ide skripsi Anda, minta rekomendasi judul baru, atau analisis research gap'
            : 'Temukan referensi penelitian tugas akhir mahasiswa Teknik Informatika dengan mudah'
          }}
        </p>
      </div>

      <!-- Example Prompt Chips — Mode Pencarian -->
      <div v-if="!isChatbotMode" class="w-full max-w-md grid grid-cols-1 gap-2.5 sm:gap-3 animate-fade-up" style="animation-delay: 200ms">
        <button @click="submitMessage('Implementasi Algoritma CNN pada deteksi penyakit daun')"
          class="text-left p-4 sm:p-5 bg-bg-surface border border-border-subtle rounded-lg hover:bg-bg-elevated hover:border-border-default transition-all duration-300 active:scale-[0.98] shadow-spotify-medium/0 hover:shadow-spotify-medium">
          <div class="flex items-start gap-3 !p-2">
            <span class="material-symbols-outlined text-primary text-base flex-shrink-0 mt-0.5">
              search
            </span>
            <div class="min-w-0 text-left">
              <p class="text-[11px] font-bold text-primary uppercase tracking-wider mb-1">
                Contoh Pencarian
              </p>
              <p class="text-sm text-text-subdued leading-snug break-words">
                "Implementasi Algoritma CNN pada deteksi penyakit daun"
              </p>
            </div>
          </div>
        </button>

        <button @click="submitMessage('Analisis Sentimen Twitter menggunakan Naive Bayes')"
          class="text-left p-4 sm:p-5 bg-bg-surface border border-border-subtle rounded-lg hover:bg-bg-elevated hover:border-border-default transition-all duration-300 active:scale-[0.98] shadow-spotify-medium/0 hover:shadow-spotify-medium">
          <div class="flex items-start gap-3 !p-2">
            <span class="material-symbols-outlined text-primary text-base flex-shrink-0 mt-0.5">
              trending_up
            </span>
            <div class="min-w-0 text-left">
              <p class="text-[11px] font-bold text-primary uppercase tracking-wider mb-1">
                Topik Populer
              </p>
              <p class="text-sm text-text-subdued leading-snug break-words">
                "Analisis Sentimen Twitter menggunakan Naive Bayes"
              </p>
            </div>
          </div>
        </button>
      </div>

      <!-- Example Prompt Chips — Mode Chatbot -->
      <div v-else class="w-full max-w-md grid grid-cols-1 gap-2.5 sm:gap-3 animate-fade-up" style="animation-delay: 200ms">
        <button @click="submitMessage('Rekomendasikan judul skripsi tentang machine learning untuk bidang kesehatan')"
          class="text-left p-4 sm:p-5 bg-bg-surface border border-border-subtle rounded-lg hover:bg-bg-elevated hover:border-border-default transition-all duration-300 active:scale-[0.98] shadow-spotify-medium/0 hover:shadow-spotify-medium">
          <div class="flex items-start gap-3 !p-2">
            <span class="material-symbols-outlined text-primary text-base flex-shrink-0 mt-0.5">
              auto_awesome
            </span>
            <div class="min-w-0 text-left">
              <p class="text-[11px] font-bold text-primary uppercase tracking-wider mb-1">
                Rekomendasi Judul
              </p>
              <p class="text-sm text-text-subdued leading-snug break-words">
                "Rekomendasikan judul skripsi tentang machine learning untuk bidang kesehatan"
              </p>
            </div>
          </div>
        </button>

        <button @click="submitMessage('Apa saja research gap di bidang NLP berdasarkan skripsi yang sudah ada?')"
          class="text-left p-4 sm:p-5 bg-bg-surface border border-border-subtle rounded-lg hover:bg-bg-elevated hover:border-border-default transition-all duration-300 active:scale-[0.98] shadow-spotify-medium/0 hover:shadow-spotify-medium">
          <div class="flex items-start gap-3 !p-2">
            <span class="material-symbols-outlined text-primary text-base flex-shrink-0 mt-0.5">
              psychology
            </span>
            <div class="min-w-0 text-left">
              <p class="text-[11px] font-bold text-primary uppercase tracking-wider mb-1">
                Analisis Research Gap
              </p>
              <p class="text-sm text-text-subdued leading-snug break-words">
                "Apa saja research gap di bidang NLP berdasarkan skripsi yang sudah ada?"
              </p>
            </div>
          </div>
        </button>

        <button @click="submitMessage('Bagaimana tahapan menyusun proposal skripsi yang baik?')"
          class="text-left p-4 sm:p-5 bg-bg-surface border border-border-subtle rounded-lg hover:bg-bg-elevated hover:border-border-default transition-all duration-300 active:scale-[0.98] shadow-spotify-medium/0 hover:shadow-spotify-medium">
          <div class="flex items-start gap-3 !p-2">
            <span class="material-symbols-outlined text-primary text-base flex-shrink-0 mt-0.5">
              school
            </span>
            <div class="min-w-0 text-left">
              <p class="text-[11px] font-bold text-primary uppercase tracking-wider mb-1">
                Panduan Skripsi
              </p>
              <p class="text-sm text-text-subdued leading-snug break-words">
                "Bagaimana tahapan menyusun proposal skripsi yang baik?"
              </p>
            </div>
          </div>
        </button>
      </div>

      <!-- Tip (Dinamis) -->
      <div class="animate-fade-up flex items-center gap-2 text-[10px] sm:text-xs text-text-muted font-medium !mt-5"
        style="animation-delay: 300ms">
        <span class="material-symbols-outlined text-sm flex-shrink-0 ">lightbulb</span>
        <span>{{ isChatbotMode ? 'Tanyakan apa saja seputar skripsi — saya siap membantu!' : 'Ketik kata kunci atau tanyakan topik skripsi' }}</span>
      </div>
    </div>

    <!-- Chat Messages (Dynamic) -->
    <div v-else class="flex flex-col gap-4 sm:gap-6 px-4 sm:px-6 py-6 sm:py-8 max-w-4xl mx-auto w-full">
      <template v-for="(msg, index) in messages" :key="index">
        <!-- User Bubble (kanan) -->
        <div v-if="msg.role === 'user'" class="flex justify-end animate-fade-up">
          <div
            class="max-w-[80%] sm:max-w-[70%] bg-primary text-black rounded-full rounded-br-lg px-5 py-3 sm:px-6 sm:py-3.5 break-words shadow-spotify-medium">
            <p class="text-sm sm:text-base font-medium leading-relaxed !p-2">{{ msg.content }}</p>
          </div>
        </div>

        <!-- Bot Bubble (kiri) — render markdown + table results -->
        <div v-else class="flex justify-start animate-fade-up">
          <div class="flex items-start gap-3 w-full max-w-4xl">
            <!-- Bot Avatar -->
            <div
              class="w-8 h-8 rounded-full bg-primary flex items-center justify-center flex-shrink-0 shadow-spotify-medium mt-1">
              <span class="material-symbols-outlined text-black text-sm">smart_toy</span>
            </div>

            <!-- Bot Message Content -->
            <div
              class="bg-bg-surface text-text-base rounded-2xl rounded-tl-md !px-4 !py-4 sm:px-5 sm:py-4 shadow-spotify-medium min-w-0 overflow-hidden flex-1">
              
              <!-- HyDE Hypothesis Document (jika ada) -->
              <details v-if="msg.hypothetical_document" class="hyde-hypothesis mb-3">
                <summary class="flex items-center gap-2 cursor-pointer select-none text-xs font-semibold text-primary hover:opacity-80 transition-opacity">
                  <span class="material-symbols-outlined text-sm">auto_awesome</span>
                  <span>Hipotesis Dokumen (HyDE)</span>
                  <span class="material-symbols-outlined text-xs hyde-chevron">expand_more</span>
                </summary>
                <div class="mt-2 p-3 bg-bg-elevated rounded-lg border border-border-subtle text-xs sm:text-sm text-text-subdued leading-relaxed">
                  {{ msg.hypothetical_document }}
                </div>
              </details>

              <!-- Chat message markdown text -->
              <div class="prose-chat text-sm sm:text-base leading-relaxed" v-html="renderMarkdown(msg.content)"></div>

              <!-- Interactive Table Results (jika ada documents) -->
              <!-- <----------- menambahkan table results untuk pencarian jika ingin melihat abstrak lengkapnya
                ->>>>>>>>>>>>>>>>>>>> -->
              <div v-if="msg.documents && msg.documents.length > 0" class="mt-6 pt-4 border-t border-border-subtle">
                <TableResults :documents="msg.documents" />
              </div>
            </div>
          </div>
        </div>
      </template>

      <!-- Loading Indicator -->
      <div v-if="isLoading" class="flex justify-start animate-fade-up">
        <div class="flex items-start gap-3">
          <div
            class="w-8 h-8 rounded-full bg-primary flex items-center justify-center flex-shrink-0 shadow-spotify-medium">
            <span class="material-symbols-outlined text-black text-sm animate-pulse">smart_toy</span>
          </div>
          <div class="bg-bg-surface rounded-2xl rounded-tl-md !px-5 !py-4 shadow-spotify-medium">
            <div class="flex items-center gap-2">
              <div class="flex gap-1.5">
                <span class="w-2 h-2 bg-primary/60 rounded-full animate-bounce" style="animation-delay: 0ms"></span>
                <span class="w-2 h-2 bg-primary/60 rounded-full animate-bounce" style="animation-delay: 150ms"></span>
                <span class="w-2 h-2 bg-primary/60 rounded-full animate-bounce" style="animation-delay: 300ms"></span>
              </div>
              <span class="text-xs text-text-subdued ml-1">{{ isChatbotMode ? 'Memproses...' : 'Mencari...' }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </main>
</template>

<style scoped>
/* Prose styling for rendered markdown in bot bubbles — Dynamic Theme */
.prose-chat :deep(h1),
.prose-chat :deep(h2),
.prose-chat :deep(h3) {
  font-weight: 700;
  margin-top: 0.75rem;
  margin-bottom: 0.5rem;
  line-height: 1.3;
  color: var(--app-text-bright);
}

.prose-chat :deep(h1) {
  font-size: 1.1rem;
}

.prose-chat :deep(h2) {
  font-size: 1rem;
}

.prose-chat :deep(h3) {
  font-size: 0.95rem;
}

.prose-chat :deep(p) {
  margin-bottom: 0.5rem;
  line-height: 1.65;
  color: var(--app-text-base);
}

.prose-chat :deep(p:last-child) {
  margin-bottom: 0;
}

.prose-chat :deep(strong) {
  font-weight: 700;
  color: var(--app-text-accent);
}

.prose-chat :deep(em) {
  font-style: italic;
  color: var(--app-text-subdued);
}

.prose-chat :deep(ul),
.prose-chat :deep(ol) {
  padding-left: 1.25rem;
  margin-bottom: 0.5rem;
  color: var(--app-text-base);
}

.prose-chat :deep(li) {
  margin-bottom: 0.25rem;
  line-height: 1.5;
}

.prose-chat :deep(li::marker) {
  color: var(--app-text-accent);
}

/* Table styling — Dynamic theme tables */
.prose-chat :deep(table) {
  width: 100%;
  border-collapse: collapse;
  margin: 0.75rem 0;
  font-size: 0.8rem;
  line-height: 1.4;
  display: block;
  overflow-x: auto;
}

.prose-chat :deep(thead) {
  background: var(--app-table-header-bg);
  color: var(--app-table-header-color);
}

.prose-chat :deep(th) {
  padding: 0.5rem 0.75rem;
  text-align: left;
  font-weight: 700;
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  white-space: nowrap;
}

.prose-chat :deep(td) {
  padding: 0.5rem 0.75rem;
  border-bottom: 1px solid var(--app-border-subtle);
  vertical-align: top;
  color: var(--app-text-base);
}

.prose-chat :deep(tbody tr:hover) {
  background: var(--app-bg-highlight);
}

.prose-chat :deep(tbody tr:nth-child(even)) {
  background: var(--app-bg-elevated);
}

/* Horizontal rule */
.prose-chat :deep(hr) {
  border: none;
  border-top: 1px solid var(--app-border-subtle);
  margin: 0.75rem 0;
}

/* Code */
.prose-chat :deep(code) {
  background: var(--app-bg-elevated);
  color: var(--app-text-accent);
  padding: 0.15rem 0.4rem;
  border-radius: 4px;
  font-size: 0.85em;
  font-family: 'Fira Code', 'Consolas', monospace;
  border: 1px solid var(--app-border-subtle);
}

/* Links */
.prose-chat :deep(a) {
  color: var(--app-text-accent);
  text-decoration: underline;
  text-underline-offset: 2px;
}

.prose-chat :deep(a:hover) {
  opacity: 0.8;
}

/* Blockquote */
.prose-chat :deep(blockquote) {
  border-left: 3px solid var(--app-text-accent);
  padding-left: 0.75rem;
  margin: 0.5rem 0;
  color: var(--app-text-subdued);
  font-style: italic;
}

/* HyDE Hypothesis collapsible */
.hyde-hypothesis summary {
  list-style: none;
}

.hyde-hypothesis summary::-webkit-details-marker {
  display: none;
}

.hyde-hypothesis .hyde-chevron {
  transition: transform 0.2s ease;
}

.hyde-hypothesis[open] .hyde-chevron {
  transform: rotate(180deg);
}
</style>
