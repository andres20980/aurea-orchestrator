import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card'
import { Badge } from './ui/badge'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const statusVariants = {
  pending: 'secondary',
  running: 'warning',
  completed: 'success',
  failed: 'error',
}

export default function JobsView() {
  const [jobs, setJobs] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetchJobs()
    const interval = setInterval(fetchJobs, 5000) // Refresh every 5 seconds
    return () => clearInterval(interval)
  }, [])

  const fetchJobs = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/jobs`)
      if (!response.ok) throw new Error('Failed to fetch jobs')
      const data = await response.json()
      setJobs(data)
      setLoading(false)
    } catch (err) {
      setError(err.message)
      setLoading(false)
    }
  }

  if (loading) {
    return <div className="text-center p-8">Loading jobs...</div>
  }

  if (error) {
    return <div className="text-center p-8 text-red-500">Error: {error}</div>
  }

  return (
    <div className="space-y-4">
      <h2 className="text-3xl font-bold tracking-tight">Jobs</h2>
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {jobs.map((job) => (
          <Card key={job.id}>
            <CardHeader>
              <div className="flex items-start justify-between">
                <CardTitle className="text-lg">{job.name}</CardTitle>
                <Badge variant={statusVariants[job.status]}>
                  {job.status}
                </Badge>
              </div>
              <CardDescription className="text-xs">ID: {job.id}</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-500">Progress</span>
                  <span className="font-medium">{job.progress}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-blue-500 h-2 rounded-full transition-all"
                    style={{ width: `${job.progress}%` }}
                  />
                </div>
                {job.result && (
                  <div className="mt-3 pt-3 border-t">
                    <p className="text-sm text-gray-500">Result:</p>
                    <p className="text-sm font-medium">{job.result}</p>
                  </div>
                )}
                <div className="text-xs text-gray-500 mt-2">
                  Updated: {new Date(job.updated_at).toLocaleString()}
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )
}
