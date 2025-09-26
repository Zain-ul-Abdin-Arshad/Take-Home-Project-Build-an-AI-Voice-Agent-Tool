import ResultsTable from '../components/ResultsTable'

const CallResults = () => {
  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Call Results</h1>
        <p className="text-gray-600 mt-2">
          View detailed call logs with structured summaries and transcripts
        </p>
      </div>

      <ResultsTable />
    </div>
  )
}

export default CallResults
