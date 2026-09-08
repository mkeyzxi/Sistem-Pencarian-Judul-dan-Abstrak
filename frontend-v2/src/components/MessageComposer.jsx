import {useState, useRef, useEffect} from 'react'
import {Send, Loader2} from 'lucide-react'

export default function MessageComposer({onSendMessage, isGenerating}) {
  const [message, setMessage] = useState('')
  const textareaRef = useRef(null)

  const adjustTextareaHeight = () => {
    const textarea = textareaRef.current
    if (textarea) {
      textarea.style.height = '42px' // Reset height
      textarea.style.height = `${Math.min(textarea.scrollHeight, 220)}px`
    }
  }

  useEffect(() => {
    adjustTextareaHeight()
  }, [message])

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const handleSend = () => {
    if (message.trim() && !isGenerating) {
      onSendMessage(message.trim())
      setMessage('')
    }
  }

  return (
    <footer className="composer-area">
      <div className="composer-wrapper">
        <div className="composer">
          <textarea
            ref={textareaRef}
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Cari dokumen skripsi..."
            disabled={isGenerating}
            rows={1}
          />
          <button
            className="send-button"
            onClick={handleSend}
            disabled={!message.trim() || isGenerating}
            aria-label="Send message"
          >
            {isGenerating ? (
              <Loader2 className="w-5 h-5 animate-spin" />
            ) : (
              <Send className="w-5 h-5" />
            )}
          </button>
        </div>
      </div>
    </footer>
  )
}
