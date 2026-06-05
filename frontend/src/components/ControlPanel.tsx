import { useEffect, useState } from 'react'
import type { InstrumentStatus } from '../api/client'

interface Props {
  status: InstrumentStatus | null
  disabled: boolean
  onSetOutput: (enabled: boolean) => Promise<void>
  onSetPower: (dbm: number) => Promise<void>
  onReadPower: () => Promise<number>
}

export function ControlPanel({
  status,
  disabled,
  onSetOutput,
  onSetPower,
  onReadPower,
}: Props) {
  const [power, setPower] = useState(0)
  const [measuredPower, setMeasuredPower] = useState<number | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)

  useEffect(() => {
    if (status) setPower(status.powerDbm)
  }, [status?.powerDbm])

  const run = async (action: () => Promise<void>) => {
    setBusy(true)
    setError(null)
    try {
      await action()
    } catch (err) {
      setError('Structured API call failed')
    } finally {
      setBusy(false)
    }
  }

  const handleRead = () =>
    run(async () => {
      const value = await onReadPower()
      setMeasuredPower(value)
    })

  return (
    <div className="card">
      <div className="card-header">
        <span className="card-title">Structured Controls</span>
      </div>

      <div className="control-section">
        <div>
          <div className="status-label">Output</div>
          <div className="control-hint">Calls semantic API, backend maps to OUTP ON/OFF.</div>
        </div>
        <button
          className={`btn ${status?.outputEnabled ? 'btn-danger' : 'btn-primary'}`}
          disabled={disabled || busy}
          onClick={() => run(() => onSetOutput(!status?.outputEnabled))}
        >
          {status?.outputEnabled ? 'Disable Output' : 'Enable Output'}
        </button>
      </div>

      <div className="control-section vertical">
        <div className="range-row">
          <div>
            <div className="status-label">Power Setpoint</div>
            <div className="control-hint">Range: -60 to +10 dBm. Maps to SOUR:POW.</div>
          </div>
          <span className="range-value">{power.toFixed(1)} dBm</span>
        </div>
        <input
          className="power-range"
          type="range"
          min="-60"
          max="10"
          step="0.5"
          value={power}
          disabled={disabled || busy}
          onChange={(e) => setPower(Number(e.target.value))}
        />
        <button
          className="btn btn-secondary"
          disabled={disabled || busy}
          onClick={() => run(() => onSetPower(power))}
        >
          Set Power
        </button>
      </div>

      <div className="control-section">
        <div>
          <div className="status-label">Measured Power</div>
          <div className="status-value">
            {measuredPower === null ? 'not measured' : `${measuredPower.toFixed(2)} dBm`}
          </div>
        </div>
        <button className="btn btn-secondary" disabled={disabled || busy} onClick={handleRead}>
          Read Power
        </button>
      </div>

      {error && <div className="control-error">{error}</div>}
    </div>
  )
}
