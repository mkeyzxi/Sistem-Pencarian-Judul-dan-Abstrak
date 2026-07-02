import { useState, useCallback } from 'react';

const baseURL = "http://127.0.0.1:8000";

export const useSearch = () => {
  const [state, setState] = useState({
    query: '',
    isSearching: false,
    resultsRag: [],
    resultsHyde: [],
    metricsRag: null,
    metricsHyde: null,
    error: null,
  });

  const performSearch = useCallback(async (query, mode = 'rag') => {
    if (!query.trim()) return;

    setState((prev) => ({
      ...prev,
      query,
      activeMode: mode,
      isSearching: true,
      error: null,
      resultsRag: [],
      resultsHyde: [],
      metricsRag: null,
      metricsHyde: null,
    }));

    try {
      const startTime = performance.now();
      
      // Mengirimkan 'HyDE' (dengan huruf besar) agar mengembalikan fallback backend lama
      const payloadMode = mode === 'hyde' ? 'HyDE' : 'rag';

      const res = await fetch(baseURL + '/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: query, mode: payloadMode, chat_history: [] }),
      });

      if (!res.ok) {
        throw new Error(`Pencarian ${mode.toUpperCase()} gagal diproses.`);
      }

      const data = await res.json();
      const latency = performance.now() - startTime;

      setState((prev) => ({
        ...prev,
        isSearching: false,
        resultsRag: mode === 'rag' ? data.documents || [] : [],
        resultsHyde: mode === 'hyde' ? data.documents || [] : [],
        metricsRag: mode === 'rag' ? { latency } : null,
        metricsHyde: mode === 'hyde' ? { latency } : null,
      }));

    } catch (err) {
      console.error(err);
      setState((prev) => ({
        ...prev,
        isSearching: false,
        error: err.message || 'Terjadi kesalahan saat mencari.',
      }));
    }
  }, []);

  const clearSearch = useCallback(() => {
    setState({
      query: '',
      isSearching: false,
      resultsRag: [],
      resultsHyde: [],
      metricsRag: null,
      metricsHyde: null,
      error: null,
    });
  }, []);

  return {
    ...state,
    performSearch,
    clearSearch,
  };
};
