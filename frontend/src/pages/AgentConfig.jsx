import { useState } from 'react'
import ConfigForm from '../components/ConfigForm'

const AgentConfig = () => {
  const [successMessage, setSuccessMessage] = useState('')

  const handleConfigSaved = (result) => {
    console.log('Config saved:', result)
    setSuccessMessage(`Config ${result.id ? 'updated' : 'created'} successfully!`)
    // Clear success message after 3 seconds
    setTimeout(() => setSuccessMessage(''), 3000)
  }

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Agent Configuration</h1>
        <p className="text-gray-600 mt-2">
          Create and manage AI agent configurations for driver calls
        </p>
      </div>

      {successMessage && (
        <div className="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-md">
          {successMessage}
        </div>
      )}

      <ConfigForm onSuccess={handleConfigSaved} />
    </div>
  )
}

export default AgentConfig
