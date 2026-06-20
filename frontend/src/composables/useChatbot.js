import { ref } from 'vue'

// Shared state (singleton) — semua komponen yang memanggil useChatbot() berbagi data yang sama
const messages = ref([])
const isLoading = ref(false)
const error = ref(null)
const baseURL = "http://127.0.0.1:8000"

export const useChatbot = () => {

	const sendMessage = async (message, mode) => {
		isLoading.value = true
		error.value = null

		// 1. Push pesan user ke messages agar langsung muncul di chat
		messages.value.push({
			role: 'user',
			content: message
		})

		// 2. Bangun chat_history dari pesan-pesan sebelumnya (max 10 terakhir, tanpa pesan yang baru di-push)
		const history = messages.value.slice(0, -1).slice(-10).map(msg => ({
			role: msg.role === 'user' ? 'user' : 'bot',
			content: msg.content
		}))

		try {
			const response = await fetch(baseURL + '/api/chat', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json',
				},
				body: JSON.stringify({
					"message": message,
					"mode": mode,
					"chat_history": history
				}),
			})

			if (!response.ok) {
				throw new Error('Gagal mengirim pesan')
			}

			const data = await response.json()
			console.log(data.documents && data.documents[0])
			// Tampilkan respons LLM dari backend
			const botText = data.message || 'Berikut hasil pencarian yang ditemukan:'

			messages.value.push({
				role: 'bot',
				content: botText,
				documents: data.documents || [],
			})
			// console.log(data)
			console.log(messages.value)
			// console.log(messages.value)
			// console.log(messages.value[messages.value.length - 1].documents)

		} catch (err) {
			error.value = err
			// Push pesan error agar user tahu ada masalah
			messages.value.push({
				role: 'bot',
				content: 'Maaf, terjadi kesalahan. Silakan coba lagi.'
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