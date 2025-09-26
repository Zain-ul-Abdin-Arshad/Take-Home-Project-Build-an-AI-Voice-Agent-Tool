import { useState, useEffect } from 'react'
import { callAPI } from '../services/api'

const ResultsTable = () => {
  const [callLogs, setCallLogs] = useState([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    loadCallLogs()
  }, [])

  const loadCallLogs = async () => {
    try {
      setIsLoading(true)
      // Call the real API to get call logs
      const response = await callAPI.getCallLogs()
      setCallLogs(response.messages || [])
    } catch (err) {
      setError('Failed to load call logs')
      console.error('Error loading call logs:', err)
    } finally {
      setIsLoading(false)
    }
  }

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString()
  }

  const renderStructuredSummary = (summary) => {
    if (!summary) return <span className="text-gray-400">No summary</span>
    
    // Format key-value pairs for better readability
    const formatKey = (key) => {
      return key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
    }
    
    const formatValue = (value) => {
      if (value === null || value === undefined) return 'N/A'
      if (typeof value === 'boolean') return value ? 'Yes' : 'No'
      if (typeof value === 'object') return JSON.stringify(value, null, 2)
      return String(value)
    }
    
    return (
      <div className="space-y-2">
        {Object.entries(summary).map(([key, value]) => (
          <div key={key} className="text-sm border-b border-gray-100 pb-1">
            <div className="flex">
              <span className="font-semibold text-blue-700 min-w-[120px]">
                {formatKey(key)}:
              </span>
              <span className="text-gray-900 ml-2 flex-1">
                {typeof value === 'object' && value !== null ? (
                  <pre className="text-xs bg-gray-50 p-2 rounded border whitespace-pre-wrap">
                    {formatValue(value)}
                  </pre>
                ) : (
                  <span className="font-medium">{formatValue(value)}</span>
                )}
              </span>
            </div>
          </div>
        ))}
      </div>
    )
  }

  if (isLoading) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center justify-center h-32">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <div className="text-red-600 text-center">{error}</div>
      </div>
    )
  }

  return (
    <div className="bg-white rounded-lg shadow">
      <div className="px-6 py-4 border-b border-gray-200">
        <h2 className="text-2xl font-bold text-gray-900">Call Results</h2>
        <p className="text-gray-600 mt-1">View all call logs and their structured summaries</p>
      </div>
      
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Driver
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Load Number
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Structured Summary
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Transcript
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Created
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {callLogs.map((log) => (
              <tr key={log.id} className="hover:bg-gray-50">
                <td className="px-6 py-4 whitespace-nowrap">
                  <div>
                    <div className="text-sm font-medium text-gray-900">{log.driver_name}</div>
                    <div className="text-sm text-gray-500">{log.phone_number}</div>
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {log.load_number}
                </td>
                <td className="px-6 py-4">
                  <div className="max-w-xs">
                    {renderStructuredSummary(log.structured_summary)}
                  </div>
                </td>
                <td className="px-6 py-4">
                  <div className="max-w-xs">
                    <div className="text-sm text-gray-900 max-h-20 overflow-y-auto">
                      {log.transcript || <span className="text-gray-400">No transcript</span>}
                    </div>
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {formatDate(log.created_at)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      
      {callLogs.length === 0 && (
        <div className="text-center py-8 text-gray-500">
          No call logs found
        </div>
      )}
    </div>
  )
}

export default ResultsTable
