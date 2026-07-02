import {useState, useEffect} from 'react'
import IndexCard from './IndexCard'
import {AnimatePresence} from 'framer-motion'

export default function CatalogDrawer({resultsRag, resultsHyde, isSearching, error, onViewDetail}) {
  const [activeTab, setActiveTab] = useState('rag')
  const [isMobile, setIsMobile] = useState(false)

  useEffect(() => {
    const checkMobile = () => setIsMobile(window.innerWidth < 768)
    checkMobile()
    window.addEventListener('resize', checkMobile)
    return () => window.removeEventListener('resize', checkMobile)
  }, [])

  const hasResults = resultsRag.length > 0 || resultsHyde.length > 0

  // Render Skeleton for loading
  const renderSkeleton = () => {
    return Array.from({length: 3}).map((_, i) => (
      <div
        key={i}
        className="bg-[var(--color-card-surface)] rounded-[2px] border-l-[3px] border-[var(--color-rule)] border-y border-r p-4 sm:p-5 flex flex-col gap-3 h-[200px] animate-pulse"
      >
        <div className="w-16 h-3 bg-[var(--color-kraft-bg)] rounded" />
        <div className="w-full h-5 bg-[var(--color-kraft-bg)] rounded mt-2" />
        <div className="w-3/4 h-5 bg-[var(--color-kraft-bg)] rounded" />
        <div className="w-1/2 h-3 bg-[var(--color-kraft-bg)] rounded mt-2" />
        <div className="flex-1" />
        <div className="w-full border-t border-dashed border-[var(--color-rule)] my-1" />
        <div className="w-full h-3 bg-[var(--color-kraft-bg)] rounded" />
      </div>
    ))
  }

  // Render list of cards
  const renderList = (docs, method) => {
    if (isSearching) return renderSkeleton()
    if (docs.length === 0) return null

    // Find highest score for red stamp
    const getScore = (doc) =>
      Math.max(
        0,
        Math.min(
          100,
          Number(
            (doc.metadata && doc.metadata.similarity_score) ??
              doc.similarity_score ??
              doc.score ??
              0,
          ),
        ),
      )
    const maxScore = Math.max(...docs.map(getScore))

    return (
      <div className="flex flex-col gap-4">
        <AnimatePresence>
          {docs.map((doc, idx) => (
            <IndexCard
              key={idx}
              document={doc}
              method={method}
              rank={idx + 1}
              isHighestScore={getScore(doc) === maxScore && maxScore > 0}
              onViewDetail={onViewDetail}
            />
          ))}
        </AnimatePresence>
      </div>
    )
  }

  if (error) {
    return (
      <div className="w-full max-w-4xl mx-auto px-4 sm:px-8 py-8 flex justify-center">
        <div className="border border-[var(--color-stamp-red)] bg-[var(--color-stamp-red)]/10 text-[var(--color-stamp-red)] px-6 py-4 rounded-md font-body text-center">
          {error}
        </div>
      </div>
    )
  }

  if (!hasResults && !isSearching) {
    return (
      <div className="w-full h-[50vh] flex flex-col items-center justify-center text-[var(--color-ink-muted)] opacity-70">
        <div className="font-display text-4xl mb-4">🗄️</div>
        <p className="font-body text-sm text-center">
          Laci masih kosong — mulai ketik untuk mencari skripsi.
        </p>
      </div>
    )
  }

  return (
    <div className="w-full max-w-3xl mx-auto px-4 sm:px-8 pb-20">
      {/* Centered Single Column Layout */}
      <div className="relative">
        {resultsRag.length > 0 && (
          <div>
            <h2 className="font-display text-[13px] font-bold text-[var(--color-rag-tag)] mb-6 border-b border-[var(--color-rule)] pb-2 uppercase tracking-wide text-center">
              Laci — Standard RAG
            </h2>
            <div className="min-h-[300px]">{renderList(resultsRag, 'RAG')}</div>
          </div>
        )}

        {resultsHyde.length > 0 && (
          <div>
            <h2 className="font-display text-[13px] font-bold text-[var(--color-index-teal)] mb-6 border-b border-[var(--color-rule)] pb-2 uppercase tracking-wide text-center">
              Laci — HyDE
            </h2>
            <div className="min-h-[300px]">{renderList(resultsHyde, 'HyDE')}</div>
          </div>
        )}

        {/* Skeleton saat searching */}
        {isSearching && (
          <div>
            <h2 className="font-display text-[13px] font-bold text-[var(--color-ink-muted)] mb-6 border-b border-[var(--color-rule)] pb-2 uppercase tracking-wide text-center animate-pulse">
              Mengambil Arsip...
            </h2>
            <div className="min-h-[300px]">{renderList([], 'RAG')}</div>
          </div>
        )}
      </div>
    </div>
  )
}
