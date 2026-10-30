import {useEffect} from 'react'
import {X, FileText, User, Calendar, BookOpen, GraduationCap} from 'lucide-react'

export default function DocumentModal({document: docData, onClose}) {
  // Prevent scrolling on body when modal is open
  useEffect(() => {
    document.body.style.overflow = 'hidden'
    return () => {
      document.body.style.overflow = 'auto'
    }
  }, [])

  if (!docData) return null

  const {title, fullContent, metadata, score} = docData

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="relative w-full max-w-3xl max-h-[85vh] bg-(--color-surface) rounded-2xl shadow-2xl flex flex-col overflow-hidden">
        {/* Header */}
        <div className="flex items-start justify-between p-6 border-b border-(--color-border) bg-(--color-background)">
          <div className="flex items-start gap-4 pr-8">
            <div className="w-12 h-12 bg-(--color-blue-soft) rounded-xl flex items-center justify-center shrink-0">
              <FileText className="w-6 h-6 text-(--color-primary)" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-(--color-navy) leading-tight mb-2">
                {title}
              </h2>
              <div className="relevance-badge mt-1">Relevance {score ? score.toFixed(0) : 0}%</div>
            </div>
          </div>
          <button
            onClick={onClose}
            className="absolute top-6 right-6 p-2 rounded-full hover:bg-(--color-border) text-(--color-text-muted) hover:text-(--color-navy) transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6">
          {/* Metadata Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8 bg-(--color-surface-soft) p-4 rounded-xl border border-(--color-border)">
            <div className="flex items-center gap-3 text-sm">
              <User className="w-4 h-4 text-(--color-text-muted)" />
              <div>
                <span className="text-(--color-text-muted) block text-xs">Penulis</span>
                <span className="font-semibold text-(--color-navy)">
                  {metadata?.author || '-'}
                </span>
              </div>
            </div>
            <div className="flex items-center gap-3 text-sm">
              <GraduationCap className="w-4 h-4 text-(--color-text-muted)" />
              <div>
                <span className="text-(--color-text-muted) block text-xs">NIM</span>
                <span className="font-semibold text-(--color-navy)">
                  {metadata?.nim || '-'}
                </span>
              </div>
            </div>
            <div className="flex items-center gap-3 text-sm">
              <BookOpen className="w-4 h-4 text-(--color-text-muted)" />
              <div>
                <span className="text-(--color-text-muted) block text-xs">Pembimbing</span>
                <span className="font-semibold text-(--color-navy)">
                  {metadata?.pembimbing || '-'}
                </span>
              </div>
            </div>
            <div className="flex items-center gap-3 text-sm">
              <Calendar className="w-4 h-4 text-(--color-text-muted)" />
              <div>
                <span className="text-(--color-text-muted) block text-xs">Tahun</span>
                <span className="font-semibold text-(--color-navy)">
                  {metadata?.year || '-'}
                </span>
              </div>
            </div>
          </div>

          {/* Full Abstract / Content */}
          <div>
            <h3 className="text-lg font-bold text-(--color-navy) mb-3">
              Abstrak / Konten Dokumen
            </h3>
            <div className="prose text-(--color-text-primary) text-sm leading-relaxed whitespace-pre-wrap">
              {fullContent || 'Tidak ada konten tambahan yang tersedia untuk dokumen ini.'}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
