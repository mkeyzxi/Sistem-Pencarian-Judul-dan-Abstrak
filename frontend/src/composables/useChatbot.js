import { ref } from 'vue'

// Shared state (singleton) — semua komponen yang memanggil useChatbot() berbagi data yang sama
const messages = ref([])
const isLoading = ref(false)
const error = ref(null)
const baseURL = 'http://127.0.0.1:8000'

export const useChatbot = () => {
  const sendMessage = async (message, mode) => {
    isLoading.value = true
    error.value = null

    // 1. Push pesan user ke messages agar langsung muncul di chat
    messages.value.push({
      role: 'user',
      content: message,
    })

    // 2. Bangun chat_history dari pesan-pesan sebelumnya (max 8 untuk chatbot, 10 untuk search)
    const historyLimit = mode === 'chatbot' ? 8 : 10
    const history = messages.value
      .slice(0, -1)
      .slice(-historyLimit)
      .map((msg) => ({
        role: msg.role === 'user' ? 'user' : 'bot',
        content: msg.content,
      }))

    try {
      // 3. Routing endpoint: chatbot → /api/chatbot, search → /api/chat
      const isChatbot = mode === 'chatbot'
      const endpoint = isChatbot ? '/api/chatbot' : '/api/chat'
      const payload = isChatbot
        ? { message: message, chat_history: history }
        : { message: message, mode: mode, chat_history: history }

      const response = await fetch(baseURL + endpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      })

      if (!response.ok) {
        throw new Error('Gagal mengirim pesan')
      }

      const data = await response.json()

      if (data.hypothetical_document) {
        console.log('HyDE Hypothesis Document:', data.hypothetical_document)
      }

      // 4. Tampilkan respons LLM dari backend
      const botText = data.message || 'Berikut hasil pencarian yang ditemukan:'

      messages.value.push({
        role: 'bot',
        content: botText,
        // documents hanya ada pada mode pencarian (rag/hyde/hybrid), tidak pada chatbot
        documents: data.documents || [],
        hypothetical_document: data.hypothetical_document || null,
      })
    } catch (err) {
      error.value = err
      // Push pesan error agar user tahu ada masalah
      messages.value.push({
        role: 'bot',
        content: 'Maaf, terjadi kesalahan. Silakan coba lagi.',
      })
    } finally {
      isLoading.value = false
    }
  }

  const clearMessages = () => {
    messages.value = []
    error.value = null
  }

  return {
    sendMessage,
    clearMessages,
    messages,
    isLoading,
    error,
  }
}
