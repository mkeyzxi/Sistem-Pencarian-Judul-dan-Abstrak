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
    class="shrink-0 bg-bg-base/80 glass border-t border-border-subtle !px-4 !py-3 !sm:py-4 !pb-[max(env(safe-area-inset-bottom),1rem)]"
  >
    <div
      class="w-full max-w-6xl mx-auto flex items-end gap-2.5 rounded-pill p-2 sm:p-3 transition-all duration-300"
      :class="
        isFocused
          ? 'bg-bg-elevated shadow-spotify-inset ring-1 ring-primary/20'
          : 'bg-bg-elevated shadow-spotify-inset'
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
        class="flex-1 bg-transparent border-none focus:ring-0 focus:outline-none text-sm !py-2.5 !sm:py-3 !px-3 resize-none !max-h-[120px] hide-scrollbar font-display text-text-base placeholder-text-subdued/50"
      ></textarea>
      <button
        @click="submitMessage"
        :disabled="!message.trim()"
        class="h-10 w-10 sm:h-11 sm:w-11 rounded-full flex items-center justify-center flex-shrink-0 transition-all duration-200 active:scale-90"
        :class="
          message.trim()
            ? 'bg-primary text-black hover:bg-primary-light shadow-spotify-medium glow-primary'
            : 'bg-bg-highlight text-text-muted cursor-not-allowed'
        "
      >
        <span class="material-symbols-outlined text-lg sm:text-xl">send</span>
      </button>
    </div>

    <!-- Footer Info -->
    <p
      class="text-[9px] sm:text-[10px] text-center text-text-muted mt-2.5 font-medium tracking-wide max-w-6xl mx-auto"
    >
      Powered by Teknik Informatika UIN Alauddin • Enter untuk kirim, Shift+Enter untuk baris baru
    </p>
  </div>
</template>
