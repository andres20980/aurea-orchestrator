import { useState } from 'react'
import JobsView from './components/JobsView'
import MetricsView from './components/MetricsView'
import ReviewsView from './components/ReviewsView'

function App() {
  const [activeTab, setActiveTab] = useState('jobs')

  const tabs = [
    { id: 'jobs', label: 'Jobs' },
    { id: 'metrics', label: 'Metrics' },
    { id: 'reviews', label: 'Reviews' },
  ]

  return (
    <div className="min-h-screen bg-white">
      <header className="border-b">
        <div className="container mx-auto px-4 py-4">
          <h1 className="text-4xl font-bold">Aurea Orchestrator</h1>
          <p className="text-gray-500">Automated Unified Reasoning & Execution Agents</p>
        </div>
      </header>
      
      <nav className="border-b">
        <div className="container mx-auto px-4">
          <div className="flex space-x-8">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`py-4 px-2 border-b-2 font-medium text-sm transition-colors ${
                  activeTab === tab.id
                    ? 'border-blue-500 text-gray-900'
                    : 'border-transparent text-gray-500 hover:text-gray-900 hover:border-gray-300'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>
        </div>
      </nav>

      <main className="container mx-auto px-4 py-8">
        {activeTab === 'jobs' && <JobsView />}
        {activeTab === 'metrics' && <MetricsView />}
        {activeTab === 'reviews' && <ReviewsView />}
      </main>

      <footer className="border-t mt-auto">
        <div className="container mx-auto px-4 py-4 text-center text-sm text-gray-500">
          <p>Aurea Orchestrator Dashboard v1.0.0</p>
        </div>
      </footer>
    </div>
  )
}

export default App
