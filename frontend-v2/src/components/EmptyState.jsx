export default function EmptyState({onSuggestionClick}) {
  const suggestions = [
    'Cari skripsi tentang implementasi algoritma Machine Learning',
    'Apa penelitian terbaru terkait pengembangan aplikasi mobile?',
    'Skripsi yang membahas tentang sistem keamanan jaringan',
  ]

  return (
    <div className="flex flex-col items-center justify-center h-full text-center px-4 pt-12 pb-8">
      <div className="w-24 h-24 bg-[var(--color-primary)] rounded-2xl flex items-center justify-center mb-6 shadow-md overflow-hidden">
        <img
          src="/81827305_1278039172384147_8186309804793266176_n (1).jpg"
          alt="Logo"
          className="w-full h-full object-cover"
        />
      </div>
      <p className="empty-state-description">
        Temukan referensi judul dan abstrak skripsi mahasiswa dengan mudah menggunakan pencarian alami. Sistem cerdas ini didukung oleh teknik Retrieval-Augmented Generation (RAG) untuk memberikan hasil pencarian dokumen skripsi yang paling relevan.
      </p>

      <div className="mt-10 flex flex-wrap justify-center gap-3 max-w-xl">
        {suggestions.map((suggestion, index) => (
          <button
            key={index}
            className="suggestion-chip"
            onClick={() => onSuggestionClick(suggestion)}
          >
            {suggestion}
          </button>
        ))}
      </div>
    </div>
  )
}
