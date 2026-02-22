<script setup>
// Main Chat Area Component - menampilkan chat bubbles atau empty state
import { ref, watch, nextTick, computed } from 'vue'
import { marked } from 'marked'
import { useChatbot } from '../composables/useChatbot'
import { useSearchMode } from '../composables/useSearchMode'

const { messages, isLoading, error, sendMessage } = useChatbot()
const { searchMode } = useSearchMode()

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
  <main ref="chatContainer" class="flex-1 overflow-y-auto relative flex flex-col thin-scrollbar">
    <!-- Empty State / Welcome -->
    <div
      v-if="messages.length === 0"
      class="flex-1 flex flex-col items-center justify-center px-4 sm:px-6 py-12 sm:py-16 text-center space-y-6 sm:space-y-8"
    >
      <!-- Animated Icon -->
      <div class="animate-fade-up" style="animation-delay: 0ms">
        <div
          class="w-20 h-20 sm:w-24 sm:h-24 bg-primary/10 rounded-3xl flex items-center justify-center shadow-md shadow-primary/10 border border-primary/10"
        >
          <span class="material-symbols-outlined text-4xl sm:text-5xl text-primary">school</span>
        </div>
      </div>

      <!-- Welcome Text -->
      <div class="animate-fade-up space-y-2 sm:space-y-3 max-w-md" style="animation-delay: 100ms">
        <h2 class="text-xl sm:text-2xl font-bold text-slate-900 dark:text-slate-100 leading-tight">
          Selamat datang
        </h2>
        <p class="text-slate-500 dark:text-slate-400 text-sm sm:text-base leading-relaxed">
          Temukan referensi penelitian tugas akhir mahasiswa Teknik Informatika dengan mudah
        </p>
      </div>

      <!-- Example Prompt Chips -->
      <div
        class="w-full max-w-md grid grid-cols-1 gap-2 sm:gap-3 animate-fade-up"
        style="animation-delay: 200ms"
      >
        <button
          @click="submitMessage('Implementasi Algoritma CNN pada deteksi penyakit daun')"
          class="text-left p-4 sm:p-5 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-2xl hover:border-primary/40 hover:shadow-md hover:shadow-primary/5 transition-all duration-300 active:scale-[0.98]"
        >
          <div class="flex items-start gap-2">
            <span class="material-symbols-outlined text-primary text-base flex-shrink-0 mt-0.5">
              search
            </span>
            <div class="min-w-0 text-left">
              <p class="text-xs font-bold text-primary mb-1">Contoh Pencarian</p>
              <p class="text-sm text-slate-600 dark:text-slate-300 leading-snug break-words">
                "Implementasi Algoritma CNN pada deteksi penyakit daun"
              </p>
            </div>
          </div>
        </button>

        <button
          @click="submitMessage('Analisis Sentimen Twitter menggunakan Naive Bayes')"
          class="text-left p-4 sm:p-5 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-2xl hover:border-primary/40 hover:shadow-md hover:shadow-primary/5 transition-all duration-300 active:scale-[0.98]"
        >
          <div class="flex items-start gap-2">
            <span class="material-symbols-outlined text-primary text-base flex-shrink-0 mt-0.5">
              trending_up
            </span>
            <div class="min-w-0 text-left">
              <p class="text-xs font-bold text-primary mb-1">Topik Populer</p>
              <p class="text-sm text-slate-600 dark:text-slate-300 leading-snug break-words">
                "Analisis Sentimen Twitter menggunakan Naive Bayes"
              </p>
            </div>
          </div>
        </button>
      </div>

      <!-- Tip -->
      <div
        class="animate-fade-up flex items-center gap-2 text-[10px] sm:text-xs text-slate-400 font-medium"
        style="animation-delay: 300ms"
      >
        <span class="material-symbols-outlined text-sm flex-shrink-0">lightbulb</span>
        <span>Ketik kata kunci atau tanyakan topik skripsi</span>
      </div>
    </div>

    <!-- Chat Messages (Dynamic) -->
    <div
      v-else
      class="flex flex-col gap-4 sm:gap-6 px-4 sm:px-6 py-6 sm:py-8 max-w-4xl mx-auto w-full"
    >
      <template v-for="(msg, index) in messages" :key="index">
        <!-- User Bubble (kanan) -->
        <div v-if="msg.role === 'user'" class="flex justify-end animate-fade-up">
          <div
            class="max-w-[80%] sm:max-w-[70%] bg-primary text-white rounded-2xl rounded-br-md px-4 py-3 sm:px-5 sm:py-3 break-words shadow-md shadow-primary/20"
          >
            <p class="text-sm sm:text-base leading-relaxed">{{ msg.content }}</p>
          </div>
        </div>

        <!-- Bot Bubble (kiri) — render markdown -->
        <div v-else class="flex justify-start animate-fade-up">
          <div class="flex items-start gap-2.5 max-w-[90%] sm:max-w-[80%]">
            <!-- Bot Avatar -->
            <div
              class="w-8 h-8 rounded-xl bg-gradient-to-br from-primary to-primary-dark flex items-center justify-center flex-shrink-0 shadow-sm mt-1"
            >
              <span class="material-symbols-outlined text-white text-sm">smart_toy</span>
            </div>

            <!-- Bot Message Content -->
            <div
              class="bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100 rounded-2xl rounded-tl-md px-4 py-4 sm:px-5 sm:py-4 shadow-sm border border-slate-200/60 dark:border-slate-700/60 min-w-0 overflow-hidden"
            >
              <div
                class="prose-chat text-sm sm:text-base leading-relaxed"
                v-html="renderMarkdown(msg.content)"
              ></div>
            </div>
          </div>
        </div>
      </template>

      <!-- Loading Indicator -->
      <div v-if="isLoading" class="flex justify-start animate-fade-up">
        <div class="flex items-start gap-2.5">
          <div
            class="w-8 h-8 rounded-xl bg-gradient-to-br from-primary to-primary-dark flex items-center justify-center flex-shrink-0 shadow-sm"
          >
            <span class="material-symbols-outlined text-white text-sm animate-pulse"
              >smart_toy</span
            >
          </div>
          <div
            class="bg-white dark:bg-slate-800 rounded-2xl rounded-tl-md px-5 py-4 shadow-sm border border-slate-200/60 dark:border-slate-700/60"
          >
            <div class="flex items-center gap-2">
              <div class="flex gap-1">
                <span
                  class="w-2 h-2 bg-primary/60 rounded-full animate-bounce"
                  style="animation-delay: 0ms"
                ></span>
                <span
                  class="w-2 h-2 bg-primary/60 rounded-full animate-bounce"
                  style="animation-delay: 150ms"
                ></span>
                <span
                  class="w-2 h-2 bg-primary/60 rounded-full animate-bounce"
                  style="animation-delay: 300ms"
                ></span>
              </div>
              <span class="text-xs text-slate-400 ml-1">Mencari...</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </main>
</template>

<style scoped>
/* Prose styling for rendered markdown in bot bubbles */
.prose-chat :deep(h1),
.prose-chat :deep(h2),
.prose-chat :deep(h3) {
  font-weight: 700;
  margin-top: 0.75rem;
  margin-bottom: 0.5rem;
  line-height: 1.3;
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
}
.prose-chat :deep(p:last-child) {
  margin-bottom: 0;
}

.prose-chat :deep(strong) {
  font-weight: 700;
  color: var(--color-primary, #6366f1);
}

.prose-chat :deep(em) {
  font-style: italic;
}

.prose-chat :deep(ul),
.prose-chat :deep(ol) {
  padding-left: 1.25rem;
  margin-bottom: 0.5rem;
}
.prose-chat :deep(li) {
  margin-bottom: 0.25rem;
  line-height: 1.5;
}
.prose-chat :deep(li::marker) {
  color: var(--color-primary, #6366f1);
}

/* Table styling — membuat tabel rapi di chat bubble */
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
  background: linear-gradient(135deg, var(--color-primary, #6366f1) 0%, #818cf8 100%);
  color: white;
}
.prose-chat :deep(th) {
  padding: 0.5rem 0.75rem;
  text-align: left;
  font-weight: 600;
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.03em;
  white-space: nowrap;
}
.prose-chat :deep(td) {
  padding: 0.5rem 0.75rem;
  border-bottom: 1px solid #e2e8f0;
  vertical-align: top;
}
.dark .prose-chat :deep(td) {
  border-bottom-color: #334155;
}
.prose-chat :deep(tbody tr:hover) {
  background: rgba(99, 102, 241, 0.04);
}
.dark .prose-chat :deep(tbody tr:hover) {
  background: rgba(99, 102, 241, 0.08);
}
.prose-chat :deep(tbody tr:nth-child(even)) {
  background: rgba(0, 0, 0, 0.015);
}
.dark .prose-chat :deep(tbody tr:nth-child(even)) {
  background: rgba(255, 255, 255, 0.02);
}

/* Horizontal rule */
.prose-chat :deep(hr) {
  border: none;
  border-top: 1px solid #e2e8f0;
  margin: 0.75rem 0;
}
.dark .prose-chat :deep(hr) {
  border-top-color: #334155;
}

/* Code */
.prose-chat :deep(code) {
  background: #f1f5f9;
  padding: 0.15rem 0.35rem;
  border-radius: 0.3rem;
  font-size: 0.85em;
  font-family: 'Fira Code', monospace;
}
.dark .prose-chat :deep(code) {
  background: #1e293b;
}

/* Links */
.prose-chat :deep(a) {
  color: var(--color-primary, #6366f1);
  text-decoration: underline;
  text-underline-offset: 2px;
}
.prose-chat :deep(a:hover) {
  opacity: 0.8;
}

/* Blockquote */
.prose-chat :deep(blockquote) {
  border-left: 3px solid var(--color-primary, #6366f1);
  padding-left: 0.75rem;
  margin: 0.5rem 0;
  color: #64748b;
  font-style: italic;
}
.dark .prose-chat :deep(blockquote) {
  color: #94a3b8;
}
</style>
