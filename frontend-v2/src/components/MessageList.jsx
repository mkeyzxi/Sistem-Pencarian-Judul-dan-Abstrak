import {useState} from 'react'
import ReactMarkdown from 'react-markdown'
import {
  Copy,
  ThumbsUp,
  ThumbsDown,
  RotateCcw,
  ChevronDown,
  ChevronRight,
  FileText,
  BotMessageSquare,
} from 'lucide-react'

const getAbstractContent = (content) => {
  if (!content) return 'Konten tidak tersedia.'
  const abstrakMatch = content.match(/abstrak\s*:?\s*([\s\S]*)/i)
  if (abstrakMatch && abstrakMatch[1]) {
    return abstrakMatch[1].trim()
  }
  if (content.toLowerCase().startsWith('judul:')) {
    return content.split('\n').slice(1).join('\n').trim()
  }
  return content
}

function SourceCard({source, index}) {
  const [isExpanded, setIsExpanded] = useState(false)

  return (
    <div className="source-card mb-3">
      <div
        className="flex items-start justify-between cursor-pointer"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <div className="flex items-center gap-3">
          <div className="text-[var(--color-text-muted)] font-mono text-sm shrink-0">
            {String(index + 1).padStart(2, '0')}
          </div>
          <FileText className="w-5 h-5 text-[var(--color-primary)] shrink-0" />
          <div className="font-semibold text-[var(--color-navy)] text-sm">{source.title}</div>
        </div>
        <div className="flex items-center gap-2">
          {/* Relevansi dipindah ke dalam detail */}
          {isExpanded ? (
            <ChevronDown className="w-4 h-4 text-[var(--color-text-muted)]" />
          ) : (
            <ChevronRight className="w-4 h-4 text-[var(--color-text-muted)]" />
          )}
        </div>
      </div>

      {!isExpanded && <div className="source-excerpt">"{getAbstractContent(source.fullContent).substring(0, 180)}..."</div>}

      <div className={`source-details ${isExpanded ? 'open' : ''}`}>
        <div className="pt-4 mt-4 border-t border-[var(--color-border)] min-h-0">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4 text-sm bg-[var(--color-surface-soft)] p-3 rounded-lg border border-[var(--color-border)]">
            <div>
              <div className="text-[var(--color-text-muted)] text-xs mb-1">Penulis</div>
              <div className="text-[var(--color-text-primary)] font-semibold">
                {source.metadata?.author || '-'}
              </div>
            </div>
            <div>
              <div className="text-[var(--color-text-muted)] text-xs mb-1">NIM</div>
              <div className="text-[var(--color-text-primary)] font-semibold">
                {source.metadata?.nim || '-'}
              </div>
            </div>
            <div>
              <div className="text-[var(--color-text-muted)] text-xs mb-1">Tahun</div>
              <div className="text-[var(--color-text-primary)] font-semibold">
                {source.metadata?.year || '-'}
              </div>
            </div>
            <div>
              <div className="text-[var(--color-text-muted)] text-xs mb-1">Relevansi</div>
              <div className="text-[var(--color-primary)] font-semibold">
                {source.score ? source.score.toFixed(0) : 0}%
              </div>
            </div>
          </div>
          <div>
            <div className="text-[var(--color-text-primary)] text-sm leading-relaxed whitespace-pre-wrap pb-2">
              {getAbstractContent(source.fullContent)}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

function AssistantMessage({content, sources}) {
  return (
    <div className="message assistant mb-8">
      <div className="ai-avatar shrink-0 mt-1 overflow-hidden">
        {/* <img
          src="/81827305_1278039172384147_8186309804793266176_n (1).jpg"
          alt="AI"
          className="w-full h-full object-cover"
        /> */}
        <BotMessageSquare />
      </div>
      <div className="message-body">
        <div className="prose mb-6">
          <ReactMarkdown
            components={{
              code({inline, className, children, ...props}) {
                const match = /language-(\w+)/.exec(className || '')
                return !inline && match ? (
                  <div className="code-block">
                    <div className="code-block-header">
                      <span>{match[1]}</span>
                      <button className="text-[var(--color-text-muted)] hover:text-white transition-colors">
                        Copy
                      </button>
                    </div>
                    <pre className={className} {...props}>
                      <code>{children}</code>
                    </pre>
                  </div>
                ) : (
                  <code className={className} {...props}>
                    {children}
                  </code>
                )
              },
            }}
          >
            {content}
          </ReactMarkdown>
        </div>

        {sources && sources.length > 0 && (
          <div className="mt-6 border-t border-[var(--color-border)] pt-4">
            <h4 className="text-[var(--color-text-secondary)] text-sm font-semibold mb-3">
              Sources
            </h4>
            <div className="flex flex-col gap-1">
              {sources.map((source, idx) => (
                <SourceCard key={idx} source={source} index={idx} />
              ))}
            </div>
          </div>
        )}

        <div className="flex items-center gap-1 mt-4">
          <button className="message-action" title="Copy">
            <Copy className="w-4 h-4" />
          </button>
          <button className="message-action" title="Regenerate">
            <RotateCcw className="w-4 h-4" />
          </button>
          <button className="message-action" title="Good answer">
            <ThumbsUp className="w-4 h-4" />
          </button>
          <button className="message-action" title="Bad answer">
            <ThumbsDown className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  )
}

function UserMessage({content}) {
  return (
    <div className="message user mb-8">
      <div className="message-bubble">{content}</div>
    </div>
  )
}

export default function MessageList({messages}) {
  return (
    <div className="flex flex-col w-full">
      {messages.map((msg, index) =>
        msg.role === 'user' ? (
          <UserMessage key={index} content={msg.content} />
        ) : (
          <AssistantMessage key={index} content={msg.content} sources={msg.sources} />
        ),
      )}
    </div>
  )
}
