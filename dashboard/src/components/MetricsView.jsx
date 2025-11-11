import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export default function MetricsView() {
  const [metrics, setMetrics] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetchMetrics()
    const interval = setInterval(fetchMetrics, 5000) // Refresh every 5 seconds
    return () => clearInterval(interval)
  }, [])

  const fetchMetrics = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/metrics`)
      if (!response.ok) throw new Error('Failed to fetch metrics')
      const data = await response.json()
      setMetrics(data)
      setLoading(false)
    } catch (err) {
      setError(err.message)
      setLoading(false)
    }
  }

  if (loading) {
    return <div className="text-center p-8">Loading metrics...</div>
  }

  if (error) {
    return <div className="text-center p-8 text-red-500">Error: {error}</div>
  }

  return (
    <div className="space-y-4">
      <h2 className="text-3xl font-bold tracking-tight">Metrics</h2>
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {metrics.map((metric, index) => (
          <Card key={index}>
            <CardHeader className="pb-2">
              <CardDescription>{metric.name}</CardDescription>
              <CardTitle className="text-4xl">{metric.value}</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-xs text-gray-500">
                {metric.unit}
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )
}
