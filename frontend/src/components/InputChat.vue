<script setup>
import { ref } from 'vue'
import { useChatbot } from '@/composables/useChatbot'
import { useSearchMode } from '@/composables/useSearchMode'
const { searchMode } = useSearchMode()
const { sendMessage } = useChatbot()
const message = ref('')
const textareaRef = ref(null)
const isFocused = ref(false)

const handleInput = () => {
  if (textareaRef.value) {
    textareaRef.value.style.height = 'auto'
    textareaRef.value.style.height = Math.min(textareaRef.value.scrollHeight, 120) + 'px'
  }
}

const submitMessage = () => {
  if (message.value.trim()) {
    sendMessage(message.value, searchMode.value)
    message.value = ''
    if (textareaRef.value) {
      textareaRef.value.style.height = 'auto'
    }
  }
}

const handleKeydown = (event) => {
  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault()
    submitMessage()
  }
}
</script>

<template>
  <div
    class="shrink-0 bg-white/60 dark:bg-slate-900/60 backdrop-blur-md border-t border-slate-200/50 dark:border-slate-800/50 px-4 sm:px-6 py-3 sm:py-4 pb-[max(env(safe-area-inset-bottom),1rem)]"
  >
    <div
      class="w-full max-w-6xl mx-auto flex items-end gap-2 rounded-2xl p-2 sm:p-3 border transition-all duration-300"
      :class="
        isFocused
          ? 'bg-white dark:bg-slate-800 border-primary/30 shadow-lg shadow-primary/5'
          : 'bg-slate-100 dark:bg-slate-800/80 border-slate-200/80 dark:border-slate-700/50'
      "
    >
      <textarea
        ref="textareaRef"
        v-model="message"
        @input="handleInput"
        @keydown="handleKeydown"
        @focus="isFocused = true"
        @blur="isFocused = false"
        placeholder="Ketik judul, topik, atau kata kunci skripsi..."
        rows="1"
        class="flex-1 bg-transparent border-none focus:ring-0 focus:outline-none text-sm py-2.5 sm:py-3 px-3 resize-none max-h-[120px] hide-scrollbar font-display text-slate-800 dark:text-slate-200 placeholder-slate-400/70"
      ></textarea>
      <button
        @click="submitMessage"
        :disabled="!message.trim()"
        class="h-10 w-10 sm:h-11 sm:w-11 rounded-xl flex items-center justify-center flex-shrink-0 transition-all duration-200 active:scale-90"
        :class="
          message.trim()
            ? 'bg-primary text-white hover:bg-primary shadow-md shadow-primary/30 hover:shadow-lg hover:shadow-primary/40'
            : 'bg-slate-200 dark:bg-slate-700 text-slate-400 dark:text-slate-500 cursor-not-allowed'
        "
      >
        <span class="material-symbols-outlined text-lg sm:text-xl">send</span>
      </button>
    </div>

    <!-- Footer Info -->
    <p
      class="text-[9px] sm:text-[10px] text-center text-slate-400/60 mt-2.5 font-medium max-w-6xl mx-auto"
    >
      Powered by Teknik Informatika UIN Alauddin • Enter untuk kirim, Shift+Enter untuk baris baru
    </p>
  </div>
</template>
