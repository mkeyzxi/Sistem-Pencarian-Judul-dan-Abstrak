import { ref } from 'vue'

const searchMode = ref('rag'); // Default mode
export function useSearchMode() {
	const setMode = (mode) => {
		searchMode.value = mode; // Mode baru bisa berupa 'rag', 'hyde', atau 'hybrid'
	}
	return { searchMode, setMode }
}

