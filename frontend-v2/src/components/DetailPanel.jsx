import { m, AnimatePresence } from 'framer-motion';
import { X } from 'lucide-react';

export default function DetailPanel({document, method, onClose}) {
  if (!document) return null

  const getField = (key, fallback = '') =>
    document[key] || (document.metadata && document.metadata[key]) || fallback
  const title = getField('judul', 'Judul Tidak Tersedia')
  const author = getField('nama', 'Penulis Anonim')
  const year = getField('tahun', 'Tahun N/A')
  const content = getField('page_content', document.content || '')
  const score = (
    (document.metadata && document.metadata.similarity_score) ??
    document.similarity_score ??
    document.score ??
    0
  ).toFixed(2)
  const nim = getField('nim', '-')
  const pembimbing = getField('pembimbing', '-')

  return (
    <AnimatePresence>
      <div className="fixed inset-0 z-50 flex justify-end">
        {/* Backdrop */}
        <m.div
          initial={{opacity: 0}}
          animate={{opacity: 1}}
          exit={{opacity: 0}}
          onClick={onClose}
          className="absolute inset-0 bg-[var(--color-ink)]/20 backdrop-blur-sm"
        />

        {/* Panel */}
        <m.div
          initial={{x: '100%'}}
          animate={{x: 0}}
          exit={{x: '100%'}}
          transition={{type: 'tween', duration: 0.22, ease: 'easeOut'}}
          className="relative w-full max-w-2xl bg-[var(--color-card-surface)] h-full shadow-2xl flex flex-col border-l border-[var(--color-rule)]"
        >
          {/* Header */}
          <div className="p-6 border-b border-[var(--color-rule)] flex items-center justify-between bg-[var(--color-kraft-bg)]/30">
            <div className="font-mono text-[13px] font-bold text-[var(--color-ink)]">
              DETAIL KARTU · {method}
            </div>
            <button
              onClick={onClose}
              aria-label="Tutup panel"
              className="p-1 text-[var(--color-ink-muted)] hover:text-[var(--color-stamp-red)] transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Body */}
          <div className="flex-1 overflow-y-auto p-6 hide-scrollbar">
            <h2 className="font-display font-bold text-2xl text-[var(--color-ink)] leading-tight mb-4">
              {title}
            </h2>

            <div className="grid grid-cols-2 gap-y-4 gap-x-2 mb-6 font-mono text-[13px]">
              <div>
                <div className="text-[var(--color-ink-muted)] mb-1 uppercase text-[10px]">
                  Penulis
                </div>
                <div className="text-[var(--color-ink)]">{author}</div>
              </div>
              <div>
                <div className="text-[var(--color-ink-muted)] mb-1 uppercase text-[10px]">NIM</div>
                <div className="text-[var(--color-ink)]">{nim}</div>
              </div>
              <div>
                <div className="text-[var(--color-ink-muted)] mb-1 uppercase text-[10px]">
                  Tahun
                </div>
                <div className="text-[var(--color-ink)]">{year}</div>
              </div>
              <div>
                <div className="text-[var(--color-ink-muted)] mb-1 uppercase text-[10px]">
                  Skor Relevansi
                </div>
                <div className="text-[var(--color-stamp-red)] font-bold">{score}</div>
              </div>
              <div className="col-span-2">
                <div className="text-[var(--color-ink-muted)] mb-1 uppercase text-[10px]">
                  Pembimbing
                </div>
                <div className="text-[var(--color-ink)]">{pembimbing}</div>
              </div>
            </div>

            <hr className="border-t border-dashed border-[var(--color-rule)] mb-6" />

            <div className="mb-2">
              <span className="font-display font-bold text-sm text-[var(--color-ink)] uppercase">
                Abstrak
              </span>
            </div>
            <p className="font-body text-[15px] leading-loose text-[var(--color-ink)] text-justify">
              {content}
            </p>
          </div>
        </m.div>
      </div>
    </AnimatePresence>
  )
}
