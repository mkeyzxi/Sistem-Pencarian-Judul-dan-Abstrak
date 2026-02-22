import { ref } from 'vue'

const searchMode = ref('rag');
export function useSearchMode() {
	const setMode = (mode) => {
		searchMode.value = mode;
	}
	return { searchMode, setMode }
}

