<script setup>
import { ref } from 'vue'
import { useChatbot } from '@/composables/useChatbot'

const { sendMessage } = useChatbot()

const message = ref('')
const textareaRef = ref(null)
defineProps({
  mode: String,
})

const handleInput = () => {
  // Auto-resize textarea
  if (textareaRef.value) {
    textareaRef.value.style.height = 'auto'
    textareaRef.value.style.height = Math.min(textareaRef.value.scrollHeight, 128) + 'px'
  }
}

const submitMessage = () => {
  if (message.value.trim()) {
    console.log('Message sent:', message.value)
    sendMessage({ payload: message.value, mode: mode.value })
    message.value = ''
    // Reset textarea height
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
    class="fixed bottom-0 left-0 right-0 bg-white/80 dark:bg-slate-900/80 backdrop-blur-md border-t border-slate-200 dark:border-slate-800 p-4 pb-8 z-40"
  >
    <div
      class="max-w-2xl mx-auto flex items-end gap-2 bg-slate-100 dark:bg-slate-800 rounded-2xl p-2 border border-slate-200 dark:border-slate-700"
    >
      <!-- Textarea Input -->
      <form @submit.prevent="submitMessage">
        <textarea
          ref="textareaRef"
          v-model="message"
          @input="handleInput"
          @keydown="handleKeydown"
          placeholder="Ketik judul, topik, atau kata kunci skripsi..."
          rows="1"
          class="flex-1 w-100 p-5 bg-transparent border-none focus:ring-0 text-sm py-2 px-3 resize-none max-h-32 hide-scrollbar font-display"
        ></textarea>

        <!-- Send Button -->
        <button
          @click="submitMessage"
          class="h-10 w-10 bg-primary text-white rounded-xl flex items-center justify-center shadow-lg hover:opacity-90 transition-opacity flex-shrink-0"
        >
          <span class="material-symbols-outlined text-xl">send</span>
        </button>
      </form>
    </div>

    <!-- Footer Text -->
    <p class="text-[10px] text-center text-slate-400 mt-3 font-medium">
      Powered by Teknik Informatika UIN Alauddin
    </p>
  </div>
</template>

<style scoped>
.hide-scrollbar::-webkit-scrollbar {
  display: none;
}

.hide-scrollbar {
  -ms-overflow-style: none;
  scrollbar-width: none;
}
</style>
