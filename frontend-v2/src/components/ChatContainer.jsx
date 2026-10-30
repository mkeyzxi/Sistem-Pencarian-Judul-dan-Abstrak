import {useState, useRef, useEffect} from 'react'
import EmptyState from './EmptyState'
import MessageList from './MessageList'
import MessageComposer from './MessageComposer'

export default function ChatContainer() {
  const [messages, setMessages] = useState([])
  const [isGenerating, setIsGenerating] = useState(false)
  const contentRef = useRef(null)

  const scrollToBottom = () => {
    if (contentRef.current) {
      contentRef.current.scrollTop = contentRef.current.scrollHeight
    }
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages, isGenerating])

  const handleSendMessage = async (text) => {
    // Add user message
    const newMessages = [...messages, {role: 'user', content: text}]
    setMessages(newMessages)
    setIsGenerating(true)

    try {
      const res = await fetch('http://127.0.0.1:8000/api/chat', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({message: text, mode: 'rag', chat_history: [], include_narrative: true}),
      })

      if (!res.ok) {
        throw new Error('Gagal menghubungi server pencarian.')
      }

      const data = await res.json()

      const assistantMsg = {
        role: 'assistant',
        content: data.narrative || data.message || 'Pencarian selesai.',
        narrative: data.narrative || null,
        narrativeFromCache: data.narrative_from_cache || false,
        latencyMs: data.latency_ms || null,
        fromCache: data.from_cache || false,
        sources: (data.documents || []).map((doc) => ({
          title: doc.metadata?.title || doc.metadata?.judul || 'Dokumen Tidak Berjudul',
          score: doc.similarity || doc.score || doc.metadata?.similarity_score || 0,
          excerpt: doc.content
            ? doc.content.substring(0, 180) + '...'
            : doc.page_content
              ? doc.page_content.substring(0, 180) + '...'
              : '',
          fullContent: doc.content || doc.page_content || '',
          metadata: {
            author:
              doc.metadata?.author || doc.metadata?.penulis || doc.metadata?.nama || 'Unknown',
            year: doc.metadata?.year || doc.metadata?.tahun || 'Unknown',
            nim: doc.metadata?.nim || '',
            pembimbing: doc.metadata?.pembimbing || '',
          },
        })),
      }

      setMessages([...newMessages, assistantMsg])
    } catch (error) {
      console.error('Error calling RAG service:', error)
      setMessages([
        ...newMessages,
        {
          role: 'assistant',
          content: 'Maaf, terjadi kesalahan saat menghubungi server: ' + error.message,
          sources: [],
        },
      ])
    } finally {
      setIsGenerating(false)
    }
  }

  return (
    <main className="chat-shell relative">
      <section className="chat-content" ref={contentRef}>
        <div className="chat-content-inner">
          {messages.length === 0 ? (
            <EmptyState onSuggestionClick={handleSendMessage} />
          ) : (
            <MessageList messages={messages} />
          )}

          {isGenerating && (
            <div className="message assistant mb-8 animate-pulse">
              <div className="ai-avatar shrink-0 mt-1 overflow-hidden">
                <img
                  src="/81827305_1278039172384147_8186309804793266176_n (1).jpg"
                  alt="AI"
                  className="w-full h-full object-cover"
                />
              </div>
              <div className="message-body flex items-center h-9">
                <div className="flex gap-1.5">
                  <div
                    className="w-2 h-2 rounded-full bg-(--color-text-muted) animate-bounce"
                    style={{animationDelay: '0ms'}}
                  ></div>
                  <div
                    className="w-2 h-2 rounded-full bg-(--color-text-muted) animate-bounce"
                    style={{animationDelay: '150ms'}}
                  ></div>
                  <div
                    className="w-2 h-2 rounded-full bg-(--color-text-muted) animate-bounce"
                    style={{animationDelay: '300ms'}}
                  ></div>
                </div>
                <span className="ml-2 text-sm text-(--color-text-muted)">
                  Menganalisis skripsi…
                </span>
              </div>
            </div>
          )}
        </div>
      </section>

      <MessageComposer onSendMessage={handleSendMessage} isGenerating={isGenerating} />
    </main>
  )
}
