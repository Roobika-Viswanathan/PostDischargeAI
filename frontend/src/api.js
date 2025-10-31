import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  timeout: 20000,
})

export async function health() {
  const { data } = await api.get('/health')
  return data
}

export async function lookupPatient(name) {
  const { data } = await api.get('/patients/lookup', { params: { name } })
  return data
}

export async function chatSession(payload) {
  const { data } = await api.post('/chat/session', payload)
  return data
}

export async function ragQuery(payload) {
  const { data } = await api.post('/rag/query', payload)
  return data
}

export async function fetchAgentLogs(download = false) {
  const url = `/logs/agent${download ? '?download=true' : ''}`
  const response = await api.get(url, { responseType: download ? 'blob' : 'text' })
  return response.data
}

export default api


