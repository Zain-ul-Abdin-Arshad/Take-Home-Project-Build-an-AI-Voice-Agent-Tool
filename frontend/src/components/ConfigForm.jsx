import { useState } from 'react'
import { agentConfigAPI } from '../services/api'

const ConfigForm = ({ onSuccess, initialData = null }) => {
  const [formData, setFormData] = useState({
    name: initialData?.name || '',
    prompt: initialData?.prompt || '',
    settings: initialData?.settings ? JSON.stringify(initialData.settings, null, 2) : JSON.stringify({
      retell_agent_id: "",
      voice_settings: {
        voice_id: "default",
        speed: 1.0,
        backchanneling: true,
        filler_words: true,
        interruption_sensitivity: 0.5
      },
      conversation_flow: {
        max_retries: 3,
        emergency_keywords: ["accident", "breakdown", "emergency", "help"],
        status_keywords: ["driving", "arrived", "delayed", "stuck"]
      }
    }, null, 2),
  })
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

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
      // Parse settings JSON
      let parsedSettings = {}
      try {
        parsedSettings = JSON.parse(formData.settings)
      } catch (parseError) {
        throw new Error('Invalid JSON in settings field')
      }

      const configData = {
        ...(initialData?.id && { id: initialData.id }),
        name: formData.name,
        prompt: formData.prompt,
        settings: parsedSettings,
      }

      const result = await agentConfigAPI.upsert(configData)
      setSuccess(initialData ? 'Config updated successfully!' : 'Config created successfully!')
      
      if (onSuccess) {
        onSuccess(result)
      }
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'An error occurred')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-2xl font-bold text-gray-900 mb-6">
        {initialData ? 'Edit Agent Config' : 'Create Agent Config'}
      </h2>
      
      <form onSubmit={handleSubmit} className="space-y-6">
        <div>
          <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-2">
            Agent Name *
          </label>
          <input
            type="text"
            id="name"
            name="name"
            value={formData.name}
            onChange={handleChange}
            required
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder="Enter agent name"
          />
        </div>

        <div>
          <label htmlFor="prompt" className="block text-sm font-medium text-gray-700 mb-2">
            Prompt *
          </label>
          <textarea
            id="prompt"
            name="prompt"
            value={formData.prompt}
            onChange={handleChange}
            required
            rows={4}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder="Enter the agent prompt"
          />
        </div>

        <div>
          <label htmlFor="settings" className="block text-sm font-medium text-gray-700 mb-2">
            Advanced Settings (JSON)
          </label>
          <textarea
            id="settings"
            name="settings"
            value={formData.settings}
            onChange={handleChange}
            rows={12}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent font-mono text-sm"
            placeholder='{"retell_agent_id": "your_agent_id", "voice_settings": {...}}'
          />
          <div className="text-sm text-gray-500 mt-1">
            <p><strong>Required:</strong> Add your Retell AI agent ID</p>
            <p><strong>Voice Settings:</strong> Configure voice_id, speed, backchanneling, filler_words, interruption_sensitivity</p>
            <p><strong>Conversation Flow:</strong> Set max_retries, emergency_keywords, status_keywords</p>
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
            className="bg-blue-600 text-white px-6 py-2 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isLoading ? 'Saving...' : (initialData ? 'Update Config' : 'Create Config')}
          </button>
        </div>
      </form>
    </div>
  )
}

export default ConfigForm
