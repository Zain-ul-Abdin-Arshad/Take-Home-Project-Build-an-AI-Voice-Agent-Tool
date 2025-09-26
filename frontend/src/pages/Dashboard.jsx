import { useState } from 'react'
import CallTriggerForm from '../components/CallTriggerForm'
import ResultsTable from '../components/ResultsTable'
import ConfigForm from '../components/ConfigForm'

const Dashboard = () => {
  const [refreshResults, setRefreshResults] = useState(0)

  const handleCallStarted = (result) => {
    console.log('Call started:', result)
    // Trigger refresh of results table
    setRefreshResults(prev => prev + 1)
  }

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Admin Dashboard</h1>
        <p className="text-gray-600 mt-2">
          Configure the agent, trigger test calls, and review results
        </p>
      </div>

      <div className="bg-white rounded-lg shadow" id="config">
        <div className="border-b border-gray-200 px-6 py-3">
          <h2 className="text-xl font-semibold">Agent Configuration</h2>
        </div>
        <div className="p-6">
          <ConfigForm onSuccess={() => setRefreshResults(prev => prev + 1)} />
        </div>
      </div>

      <div className="bg-white rounded-lg shadow" id="trigger">
        <div className="border-b border-gray-200 px-6 py-3">
          <h2 className="text-xl font-semibold">Trigger Test Call</h2>
        </div>
        <div className="p-6">
          <CallTriggerForm onCallStarted={handleCallStarted} />
        </div>
      </div>

      <div className="bg-white rounded-lg shadow" key={refreshResults} id="results">
        <div className="border-b border-gray-200 px-6 py-3">
          <h2 className="text-xl font-semibold">Call History & Results</h2>
        </div>
        <div className="p-6">
          <ResultsTable />
        </div>
      </div>
    </div>
  )
}

export default Dashboard
