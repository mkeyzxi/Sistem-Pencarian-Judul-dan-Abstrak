import { ref } from 'vue'

const searchMode = ref('rag'); // Default mode
export function useSearchMode() {
	const setMode = (mode) => {
		searchMode.value = mode; // Mode: 'rag', 'hyde', 'hybrid', atau 'chatbot'
	}
	return { searchMode, setMode }
}

