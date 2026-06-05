import axios from 'axios'

const BASE = '/api'

export interface Instrument {
  id: string
  model: string
  serial: string
  firmwareVersion: string
  status: string
}

export interface InstrumentStatus {
  connected: boolean
  outputEnabled: boolean
  powerDbm: number
  temperature: number
  firmwareVersion: string
  lastError: string
}

export interface FirmwareStatus {
  state: string
  progress: number
  firmwareVersion: string
}

export interface CommandResponse {
  command: string
  response: string
}

export interface PowerResponse {
  powerDbm: number
  response?: string
}

export interface OutputResponse {
  outputEnabled: boolean
  response: string
}

export const listInstruments = (): Promise<Instrument[]> =>
  axios.get(`${BASE}/instruments`).then((r) => r.data)

export const connectInstrument = (id: string): Promise<{ status: string; identity: string }> =>
  axios.post(`${BASE}/instruments/${id}/connect`).then((r) => r.data)

export const disconnectInstrument = (id: string): Promise<{ status: string }> =>
  axios.post(`${BASE}/instruments/${id}/disconnect`).then((r) => r.data)

export const getStatus = (id: string): Promise<InstrumentStatus> =>
  axios.get(`${BASE}/instruments/${id}/status`).then((r) => r.data)

export const sendCommand = (id: string, command: string): Promise<CommandResponse> =>
  axios.post(`${BASE}/instruments/${id}/command`, { command }).then((r) => r.data)

export const setOutput = (id: string, enabled: boolean): Promise<OutputResponse> =>
  axios.post(`${BASE}/instruments/${id}/output`, { enabled }).then((r) => r.data)

export const setPower = (id: string, dbm: number): Promise<PowerResponse> =>
  axios.post(`${BASE}/instruments/${id}/power`, { dbm }).then((r) => r.data)

export const readPower = (id: string): Promise<PowerResponse> =>
  axios.get(`${BASE}/instruments/${id}/power`).then((r) => r.data)

export const startFirmwareUpgrade = (id: string): Promise<{ status: string }> =>
  axios.post(`${BASE}/instruments/${id}/firmware/upgrade`).then((r) => r.data)

export const getFirmwareStatus = (id: string): Promise<FirmwareStatus> =>
  axios.get(`${BASE}/instruments/${id}/firmware/status`).then((r) => r.data)
