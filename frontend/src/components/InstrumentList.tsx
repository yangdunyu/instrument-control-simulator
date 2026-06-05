import { Instrument } from '../api/client'

interface Props {
  instruments: Instrument[]
  connected: boolean
  onConnect: () => void
  onDisconnect: () => void
}

export function InstrumentList({ instruments, connected, onConnect, onDisconnect }: Props) {
  return (
    <div className="card">
      <div className="card-header">
        <span className="card-title">Instruments</span>
      </div>
      {instruments.length === 0 && (
        <p style={{ color: '#94a3b8', fontSize: '0.875rem' }}>Scanning for instruments…</p>
      )}
      {instruments.map((inst) => (
        <div key={inst.id} className="instrument-row">
          <div>
            <div className="instrument-id">{inst.id}</div>
            <div className="instrument-meta">
              {inst.model} &middot; {inst.serial} &middot; v{inst.firmwareVersion}
            </div>
          </div>
          <div className="instrument-actions">
            <span className={`badge ${connected ? 'badge-green' : 'badge-gray'}`}>
              {connected ? 'connected' : 'available'}
            </span>
            {connected ? (
              <button className="btn btn-danger" onClick={onDisconnect}>
                Disconnect
              </button>
            ) : (
              <button className="btn btn-primary" onClick={onConnect}>
                Connect
              </button>
            )}
          </div>
        </div>
      ))}
    </div>
  )
}
