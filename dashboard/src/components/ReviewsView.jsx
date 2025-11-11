import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export default function ReviewsView() {
  const [reviews, setReviews] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetchReviews()
    const interval = setInterval(fetchReviews, 5000) // Refresh every 5 seconds
    return () => clearInterval(interval)
  }, [])

  const fetchReviews = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/reviews`)
      if (!response.ok) throw new Error('Failed to fetch reviews')
      const data = await response.json()
      setReviews(data)
      setLoading(false)
    } catch (err) {
      setError(err.message)
      setLoading(false)
    }
  }

  if (loading) {
    return <div className="text-center p-8">Loading reviews...</div>
  }

  if (error) {
    return <div className="text-center p-8 text-red-500">Error: {error}</div>
  }

  return (
    <div className="space-y-4">
      <h2 className="text-3xl font-bold tracking-tight">Reviews</h2>
      <div className="grid gap-4">
        {reviews.map((review) => (
          <Card key={review.id}>
            <CardHeader>
              <div className="flex items-start justify-between">
                <div>
                  <CardTitle className="text-lg">Review for Job {review.job_id}</CardTitle>
                  <CardDescription className="mt-1">
                    By {review.reviewer} • Score: {review.score}/5.0
                  </CardDescription>
                </div>
                <div className="text-right">
                  <div className="text-2xl font-bold text-blue-600">{review.score}</div>
                  <div className="text-xs text-gray-500">/ 5.0</div>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <p className="text-sm">{review.comments}</p>
                <div className="text-xs text-gray-500 mt-2">
                  {new Date(review.created_at).toLocaleString()}
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )
}
