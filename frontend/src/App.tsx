import { useEffect, useState } from 'react'
import * as api from './api/client'
import type { FirmwareStatus, Instrument, InstrumentStatus } from './api/client'
import { CommandConsole } from './components/CommandConsole'
import { ControlPanel } from './components/ControlPanel'
import { FirmwarePanel } from './components/FirmwarePanel'
import { InstrumentList } from './components/InstrumentList'

const INSTRUMENT_ID = 'laser-001'

export default function App() {
  const [instruments, setInstruments] = useState<Instrument[]>([])
  const [status, setStatus] = useState<InstrumentStatus | null>(null)
  const [fwStatus, setFwStatus] = useState<FirmwareStatus | null>(null)
  const [connected, setConnected] = useState(false)

  // Fetch instrument list once on mount
  useEffect(() => {
    api.listInstruments().then(setInstruments).catch(console.error)
  }, [])

  // Poll instrument status every 2 s
  useEffect(() => {
    const poll = () => {
      api
        .getStatus(INSTRUMENT_ID)
        .then((s) => {
          setStatus(s)
          setConnected(s.connected)
        })
        .catch(() => {})
    }
    poll()
    const t = setInterval(poll, 2000)
    return () => clearInterval(t)
  }, [])

  // Poll firmware status while an upgrade is in progress
  useEffect(() => {
    if (!fwStatus) return
    if (['idle', 'completed', 'failed'].includes(fwStatus.state)) return
    const t = setInterval(() => {
      api.getFirmwareStatus(INSTRUMENT_ID).then(setFwStatus).catch(() => {})
    }, 1000)
    return () => clearInterval(t)
  }, [fwStatus?.state])

  const handleConnect = async () => {
    await api.connectInstrument(INSTRUMENT_ID)
    const s = await api.getStatus(INSTRUMENT_ID)
    setStatus(s)
    setConnected(true)
    setInstruments((prev) =>
      prev.map((i) => (i.id === INSTRUMENT_ID ? { ...i, status: 'connected' } : i)),
    )
  }

  const handleDisconnect = async () => {
    await api.disconnectInstrument(INSTRUMENT_ID)
    setConnected(false)
    setStatus(null)
    setInstruments((prev) =>
      prev.map((i) => (i.id === INSTRUMENT_ID ? { ...i, status: 'available' } : i)),
    )
  }

  const handleSendCommand = async (cmd: string): Promise<string> => {
    const result = await api.sendCommand(INSTRUMENT_ID, cmd)
    return result.response
  }

  const refreshStatus = async () => {
    const s = await api.getStatus(INSTRUMENT_ID)
    setStatus(s)
    setConnected(s.connected)
  }

  const handleSetOutput = async (enabled: boolean) => {
    await api.setOutput(INSTRUMENT_ID, enabled)
    await refreshStatus()
  }

  const handleSetPower = async (dbm: number) => {
    await api.setPower(INSTRUMENT_ID, dbm)
    await refreshStatus()
  }

  const handleReadPower = async (): Promise<number> => {
    const result = await api.readPower(INSTRUMENT_ID)
    return result.powerDbm
  }

  const handleUpgrade = async () => {
    await api.startFirmwareUpgrade(INSTRUMENT_ID)
    const s = await api.getFirmwareStatus(INSTRUMENT_ID)
    setFwStatus(s)
  }

  return (
    <div className="app">
      {/* Header */}
      <div className="header">
        <svg
          width="20"
          height="20"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          viewBox="0 0 24 24"
        >
          <rect x="2" y="3" width="20" height="14" rx="2" />
          <path d="M8 21h8M12 17v4" />
          <circle cx="12" cy="10" r="3" />
        </svg>
        <h1>Instrument Control Simulator</h1>
      </div>

      {/* Discovery */}
      <InstrumentList
        instruments={instruments}
        connected={connected}
        onConnect={handleConnect}
        onDisconnect={handleDisconnect}
      />

      {/* Status + Firmware (side by side when connected) */}
      {status && (
        <div className="grid-2">
          <div className="card">
            <div className="card-header">
              <span className="card-title">Instrument Status</span>
            </div>
            <div className="status-grid">
              <div className="status-item">
                <span className="status-label">Connected</span>
                <span className={`badge ${status.connected ? 'badge-green' : 'badge-gray'}`}>
                  {status.connected ? 'yes' : 'no'}
                </span>
              </div>
              <div className="status-item">
                <span className="status-label">Output</span>
                <span className={`badge ${status.outputEnabled ? 'badge-green' : 'badge-gray'}`}>
                  {status.outputEnabled ? 'ON' : 'OFF'}
                </span>
              </div>
              <div className="status-item">
                <span className="status-label">Power</span>
                <span className="status-value">{status.powerDbm.toFixed(2)} dBm</span>
              </div>
              <div className="status-item">
                <span className="status-label">Temperature</span>
                <span className="status-value">{status.temperature.toFixed(1)} °C</span>
              </div>
              <div className="status-item">
                <span className="status-label">Firmware</span>
                <span className="status-value">{status.firmwareVersion}</span>
              </div>
              <div className="status-item">
                <span className="status-label">Last Error</span>
                <span
                  className={`status-value ${
                    status.lastError === 'No error' ? 'ok' : 'err'
                  }`}
                >
                  {status.lastError}
                </span>
              </div>
            </div>
          </div>

          <FirmwarePanel
            fwStatus={fwStatus}
            instrumentStatus={status}
            onUpgrade={handleUpgrade}
            disabled={!connected}
          />
        </div>
      )}

      {status && (
        <ControlPanel
          status={status}
          disabled={!connected}
          onSetOutput={handleSetOutput}
          onSetPower={handleSetPower}
          onReadPower={handleReadPower}
        />
      )}

      {/* SCPI Command Console */}
      <CommandConsole onSend={handleSendCommand} disabled={!connected} />
    </div>
  )
}
