import { FirmwareStatus, InstrumentStatus } from '../api/client'

interface Props {
  fwStatus: FirmwareStatus | null
  instrumentStatus: InstrumentStatus | null
  onUpgrade: () => void
  disabled: boolean
}

const BADGE_CLASS: Record<string, string> = {
  idle: 'badge-gray',
  uploading: 'badge-yellow',
  validating: 'badge-yellow',
  applying: 'badge-yellow',
  completed: 'badge-green',
  failed: 'badge-red',
}

const FILL_CLASS: Record<string, string> = {
  uploading: 'running',
  validating: 'running',
  applying: 'running',
  completed: 'completed',
  failed: 'failed',
}

export function FirmwarePanel({ fwStatus, instrumentStatus, onUpgrade, disabled }: Props) {
  const state = fwStatus?.state ?? 'idle'
  const progress = fwStatus?.progress ?? 0
  const version = instrumentStatus?.firmwareVersion ?? fwStatus?.firmwareVersion ?? '—'
  const inProgress = ['uploading', 'validating', 'applying'].includes(state)

  return (
    <div className="card">
      <div className="card-header">
        <span className="card-title">Firmware</span>
        <button
          className="btn btn-secondary"
          onClick={onUpgrade}
          disabled={disabled || inProgress}
        >
          Upgrade Firmware
        </button>
      </div>

      <div className="fw-row">
        <span className="fw-label">Version</span>
        <span className="fw-version">{version}</span>
      </div>
      <div className="fw-row">
        <span className="fw-label">State</span>
        <span className={`badge ${BADGE_CLASS[state] ?? 'badge-gray'}`}>{state}</span>
      </div>

      {state !== 'idle' && (
        <>
          <div className="progress-track">
            <div
              className={`progress-fill ${FILL_CLASS[state] ?? 'running'}`}
              style={{ width: `${progress}%` }}
            />
          </div>
          <div className="progress-pct">{progress}%</div>
        </>
      )}
    </div>
  )
}
