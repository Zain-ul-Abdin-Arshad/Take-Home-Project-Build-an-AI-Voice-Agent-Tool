import axios from 'axios'

const API_BASE_URL = '/api'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Agent Config API
export const agentConfigAPI = {
  // Create or update agent config
  upsert: async (configData) => {
    const response = await api.post('/config', configData)
    return response.data
  },

  // Get agent config by ID
  get: async (id) => {
    const response = await api.get(`/config/${id}`)
    return response.data
  },

  // Get all agent configs
  getAll: async () => {
    const response = await api.get('/configs')
    return response.data
  },
}

// Call API
export const callAPI = {
  // Start a new call
  startCall: async (callData) => {
    const response = await api.post('/start-call', callData)
    return response.data
  },

  // Get call logs (we'll need to add this endpoint to backend)
  getCallLogs: async () => {
    const response = await api.get('/call-logs')
    return response.data
  },
}

// Health check
export const healthAPI = {
  check: async () => {
    const response = await api.get('/health')
    return response.data
  },
}

export default api
