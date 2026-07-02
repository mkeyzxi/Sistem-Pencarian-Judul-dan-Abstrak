export default function MetricStrip({metricsRag, metricsHyde, isSearching}) {
  if (isSearching) {
    return (
      <div className="fixed bottom-0 left-0 right-0 bg-[var(--color-ink)] text-[var(--color-card-surface)] border-t border-[var(--color-rule)] py-2 px-4 shadow-[0_-4px_12px_rgba(0,0,0,0.1)] z-40">
        <div className="w-full max-w-5xl mx-auto flex items-center justify-center font-mono text-[11px] animate-pulse">
          Mencari di katalog...
        </div>
      </div>
    )
  }

  if (!metricsRag && !metricsHyde) return null

  const latRag = metricsRag?.latency ? `${metricsRag.latency.toFixed(0)}ms` : '-'
  const latHyde = metricsHyde?.latency ? `${metricsHyde.latency.toFixed(0)}ms` : '-'

  // Highlight the faster one
  const isRagFaster =
    metricsRag?.latency && metricsHyde?.latency && metricsRag.latency < metricsHyde.latency
  const isHydeFaster =
    metricsRag?.latency && metricsHyde?.latency && metricsHyde.latency < metricsRag.latency

  return (
    <div className="fixed bottom-0 left-0 right-0 bg-[var(--color-card-surface)] border-t border-[var(--color-rule)] py-2.5 px-4 shadow-[0_-4px_12px_rgba(0,0,0,0.05)] z-40">
      <div className="w-full max-w-5xl mx-auto flex flex-wrap items-center justify-between gap-4 font-mono text-[11px] md:text-[12px] text-[var(--color-ink)]">
        {/* Latency Metric */}
        <div className="flex items-center gap-4">
          <span className="text-[var(--color-ink-muted)]">Latency avg</span>
          <span className="flex items-center gap-3">
            <span
              className={isRagFaster ? 'border-b-2 border-[var(--color-stamp-red)] font-bold' : ''}
            >
              RAG {latRag}
            </span>
            <span className="text-[var(--color-rule)]">·</span>
            <span
              className={isHydeFaster ? 'border-b-2 border-[var(--color-stamp-red)] font-bold' : ''}
            >
              HyDE {latHyde}
            </span>
          </span>
        </div>

        {/* Future expansion: Hit@5, MRR */}
        <div className="hidden md:flex items-center gap-4 opacity-50">
          <span className="text-[var(--color-ink-muted)]">Hit@5</span>
          <span>RAG - · HyDE -</span>
        </div>
      </div>
    </div>
  )
}
