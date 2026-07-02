import React, { memo } from 'react';
import { m } from 'framer-motion';
import { ArrowRight } from 'lucide-react';

const IndexCard = memo(function IndexCard({ 
  document, 
  method, // 'RAG' or 'HyDE'
  rank, 
  latency, 
  isHighestScore, 
  onViewDetail 
}) {
  const getScore = (doc) => {
    const s = (doc.metadata && doc.metadata.similarity_score) ?? doc.similarity_score ?? doc.score ?? 0;
    return Math.max(0, Math.min(100, Number(s) || 0));
  };
  
  const getField = (key, fallback = '') => document[key] || (document.metadata && document.metadata[key]) || fallback;
  
  const score = getScore(document).toFixed(1);
  const title = getField('judul', 'Judul Tidak Tersedia');
  const author = getField('nama', 'Penulis Anonim');
  const year = getField('tahun', 'Tahun N/A');
  const content = getField('page_content', document.content || '');
  
  // Synthetic call number
  const hash = Math.abs(title.split('').reduce((a,b)=>{a=((a<<5)-a)+b.charCodeAt(0);return a&a},0)).toString().padStart(4, '0').slice(-4);
  const callNumber = `TI.${year}.${hash}`;

  const borderColor = method === 'RAG' ? 'border-[var(--color-rag-tag)]' : 'border-[var(--color-index-teal)]';
  const tagColor = method === 'RAG' ? 'text-[var(--color-rag-tag)]' : 'text-[var(--color-index-teal)]';

  return (
    <m.div 
      layout
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, scale: 0.95 }}
      transition={{ duration: 0.3 }}
      whileHover={{ y: -4, rotate: 0.5, boxShadow: '0 4px 12px rgba(27,36,50,0.08)' }}
      className={`relative bg-[var(--color-card-surface)] rounded-[2px] border-l-[3px] ${borderColor} border-y border-r border-[var(--color-rule)] p-4 sm:p-5 flex flex-col gap-3 interactive cursor-pointer`}
      onClick={() => onViewDetail(document, method)}
    >
      {/* Top right stamp */}
      <div 
        className={`absolute top-4 right-4 border px-2 py-0.5 rounded-full rotate-[-6deg] font-mono text-[11px] font-bold tracking-widest ${
          isHighestScore 
            ? 'border-[var(--color-stamp-red)] text-[var(--color-stamp-red)]' 
            : 'border-[var(--color-ink-muted)] text-[var(--color-ink-muted)] opacity-60'
        }`}
      >
        {score}
      </div>

      {/* Header: Label & Rank */}
      <div className={`font-mono text-[11px] font-bold ${tagColor}`}>
        {method} · #{rank}
      </div>

      {/* Title */}
      <h3 className="font-display font-semibold text-lg leading-snug text-[var(--color-ink)] line-clamp-2 pr-12">
        {title}
      </h3>

      {/* Metadata */}
      <div className="font-body text-[13px] text-[var(--color-ink-muted)]">
        {author} · {year} · Teknik Informatika
      </div>

      {/* Perforation Line */}
      <hr className="border-t border-dashed border-[var(--color-rule)] my-1" />

      {/* Abstract Snippet */}
      <p className="font-body text-[14px] leading-relaxed text-[var(--color-ink)] line-clamp-3">
        {content}
      </p>

      {/* Footer */}
      <div className="mt-2 flex items-center justify-between pt-2">
        <div className="font-mono text-[12px] text-[var(--color-ink-muted)]">
          ID: {callNumber}
        </div>
        <button 
          className="flex items-center gap-1 font-display font-medium text-[13px] text-[var(--color-ink)] hover:text-[var(--color-stamp-red)] transition-colors"
          onClick={(e) => {
            e.stopPropagation();
            onViewDetail(document, method);
          }}
        >
          Lihat detail <ArrowRight className="w-3.5 h-3.5" />
        </button>
      </div>
    </m.div>
  );
});

export default IndexCard;
