import {useState} from 'react'
import {Search} from 'lucide-react'
import {m} from 'framer-motion'

export default function SearchSlip({onSearch, activeQuery}) {
  const [inputValue, setInputValue] = useState('')
  const [searchMode, setSearchMode] = useState('rag')

  const handleSubmit = (e) => {
    e.preventDefault()
    if (inputValue.trim()) {
      onSearch(inputValue, searchMode)
    }
  }

  return (
    <div className="w-full max-w-4xl mx-auto px-4 sm:px-8 py-6 mb-4">
      {/* Search Slip */}
      <m.form
        onSubmit={handleSubmit}
        whileTap={{scale: 0.98}}
        transition={{duration: 0.1}}
        className="relative flex items-center bg-[var(--color-card-surface)] border-b-2 border-[var(--color-ink)]"
      >
        <input
          type="text"
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          placeholder="Cari judul, topik, atau kata kunci skripsi..."
          className="w-full bg-transparent border-none focus:outline-none focus:ring-0 text-[var(--color-ink)] font-body text-base px-2 py-4"
        />
        <button
          type="submit"
          className="p-3 text-[var(--color-ink)] hover:text-[var(--color-stamp-red)] transition-colors"
          aria-label="Cari Skripsi"
        >
          <Search className="w-6 h-6" />
        </button>
      </m.form>

      {/* Mode Selector */}
      <div className="mt-4 flex justify-center gap-8">
        <label className="flex items-center gap-2 cursor-pointer font-body text-sm text-[var(--color-ink)] hover:text-[var(--color-rag-tag)] transition-colors">
          <input 
            type="radio" 
            name="searchMode" 
            value="rag" 
            checked={searchMode === 'rag'} 
            onChange={() => setSearchMode('rag')} 
            className="w-4 h-4 accent-[var(--color-rag-tag)]"
          />
          <span className="font-display font-medium text-[13px] tracking-wide uppercase">Standard RAG</span>
        </label>
        
        <label className="flex items-center gap-2 cursor-pointer font-body text-sm text-[var(--color-ink)] hover:text-[var(--color-index-teal)] transition-colors">
          <input 
            type="radio" 
            name="searchMode" 
            value="hyde" 
            checked={searchMode === 'hyde'} 
            onChange={() => setSearchMode('hyde')} 
            className="w-4 h-4 accent-[var(--color-index-teal)]"
          />
          <span className="font-display font-medium text-[13px] tracking-wide uppercase">HyDE</span>
        </label>
      </div>

      {/* Active Query Label */}
      {activeQuery && (
        <div className="mt-6 flex items-center justify-center">
          <span className="font-display font-medium text-[11px] tracking-[0.06em] text-[var(--color-ink-muted)] uppercase bg-[var(--color-card-surface)] px-3 py-1 rounded-full border border-[var(--color-rule)]">
            HASIL UNTUK "{activeQuery}"
          </span>
        </div>
      )}
    </div>
  )
}
