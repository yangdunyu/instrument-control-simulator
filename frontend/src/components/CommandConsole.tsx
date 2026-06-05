import { useEffect, useRef, useState } from 'react'

interface HistoryEntry {
  command: string
  response: string
  timestamp: string
}

interface Props {
  onSend: (cmd: string) => Promise<string>
  disabled: boolean
}

export function CommandConsole({ onSend, disabled }: Props) {
  const [input, setInput] = useState('')
  const [history, setHistory] = useState<HistoryEntry[]>([])
  const [loading, setLoading] = useState(false)
  const historyRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (historyRef.current) {
      historyRef.current.scrollTop = historyRef.current.scrollHeight
    }
  }, [history])

  const submit = async () => {
    const cmd = input.trim()
    if (!cmd || loading) return
    setInput('')
    setLoading(true)
    try {
      const response = await onSend(cmd)
      setHistory((h) => [
        ...h,
        { command: cmd, response, timestamp: new Date().toLocaleTimeString() },
      ])
    } catch {
      setHistory((h) => [
        ...h,
        {
          command: cmd,
          response: 'ERROR:REQUEST_FAILED',
          timestamp: new Date().toLocaleTimeString(),
        },
      ])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="card">
      <div className="card-header">
        <span className="card-title">Command Console</span>
      </div>
      <div className="console-form">
        <input
          className="console-input"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && submit()}
          placeholder={disabled ? 'Connect an instrument to send commands' : 'Enter SCPI command (e.g. OUTP ON)'}
          disabled={disabled || loading}
        />
        <button
          className="btn btn-primary"
          onClick={submit}
          disabled={disabled || loading || !input.trim()}
        >
          {loading ? '…' : 'Send'}
        </button>
      </div>

      <div className="response-history" ref={historyRef}>
        {history.length === 0 ? (
          <span className="history-empty">No commands sent yet.</span>
        ) : (
          history.map((entry, i) => (
            <div key={i} className="history-entry">
              <div className="history-ts">{entry.timestamp}</div>
              <div className="history-cmd">{entry.command}</div>
              <div className={`history-res ${entry.response.startsWith('ERROR') ? 'error' : ''}`}>
                {entry.response}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  )
}
