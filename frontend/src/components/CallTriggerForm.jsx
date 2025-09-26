import { useState, useEffect } from 'react'
import { callAPI, agentConfigAPI } from '../services/api'

const CallTriggerForm = ({ onCallStarted }) => {
  const [formData, setFormData] = useState({
    driver_name: '',
    phone_number: '',
    load_number: '',
    config_id: '',
  })
  const [configs, setConfigs] = useState([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  // Load agent configs on component mount
  useEffect(() => {
    loadConfigs()
  }, [])

  const loadConfigs = async () => {
    try {
      // Call the real API to get agent configs
      const response = await agentConfigAPI.getAll()
      setConfigs(response || [])
    } catch (err) {
      console.error('Failed to load configs:', err)
      setError('Failed to load agent configurations')
    }
  }

  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: value
    }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setIsLoading(true)
    setError('')
    setSuccess('')

    try {
      const callData = {
        driver_name: formData.driver_name,
        phone_number: formData.phone_number,
        load_number: formData.load_number,
        config_id: parseInt(formData.config_id),
      }

      const result = await callAPI.startCall(callData)
      setSuccess(`Call started successfully! Call ID: ${result.call_id}`)
      
      // Reset form
      setFormData({
        driver_name: '',
        phone_number: '',
        load_number: '',
        config_id: '',
      })

      if (onCallStarted) {
        onCallStarted(result)
      }
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Failed to start call')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-2xl font-bold text-gray-900 mb-6">Trigger Test Call</h2>
      <p className="text-gray-600 mb-6">
        Enter driver details to trigger a voice agent call. The agent will check on the driver's status and collect structured information.
      </p>
      
      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label htmlFor="driver_name" className="block text-sm font-medium text-gray-700 mb-2">
              Driver Name *
            </label>
            <input
              type="text"
              id="driver_name"
              name="driver_name"
              value={formData.driver_name}
              onChange={handleChange}
              required
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Enter driver name"
            />
          </div>

          <div>
            <label htmlFor="phone_number" className="block text-sm font-medium text-gray-700 mb-2">
              Phone Number *
            </label>
            <input
              type="tel"
              id="phone_number"
              name="phone_number"
              value={formData.phone_number}
              onChange={handleChange}
              required
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="+1234567890"
            />
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label htmlFor="load_number" className="block text-sm font-medium text-gray-700 mb-2">
              Load Number *
            </label>
            <input
              type="text"
              id="load_number"
              name="load_number"
              value={formData.load_number}
              onChange={handleChange}
              required
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="e.g., 7891-B"
            />
          </div>

          <div>
            <label htmlFor="config_id" className="block text-sm font-medium text-gray-700 mb-2">
              Agent Config *
            </label>
            <select
              id="config_id"
              name="config_id"
              value={formData.config_id}
              onChange={handleChange}
              required
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">Select an agent config</option>
              {configs.map((config) => (
                <option key={config.id} value={config.id}>
                  {config.name}
                </option>
              ))}
            </select>
          </div>
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-md">
            {error}
          </div>
        )}

        {success && (
          <div className="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-md">
            {success}
          </div>
        )}

        <div className="flex justify-end">
            <button
              type="submit"
              disabled={isLoading}
              className="bg-green-600 text-white px-6 py-2 rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? 'Triggering Call...' : 'Start Test Call'}
            </button>
        </div>
      </form>
    </div>
  )
}

export default CallTriggerForm
