'use client'

import React, { useState } from 'react'
import { NEOLayout } from '@/components/layouts/neo-layout'
import { NEODashboard } from '@/components/ui/neo-dashboard'
import { NEOChat } from '@/components/ui/neo-chat'
import { NEOAuth } from '@/components/ui/neo-auth'

// Demo data
const demoStats = {
  totalChats: 1247,
  activeAgents: 8,
  documentsProcessed: 3456,
  uptime: '99.9%',
  chatsTrend: 12,
  agentsTrend: 5,
  documentsTrend: 8
}

const demoActivity = [
  {
    id: '1',
    type: 'chat' as const,
    title: 'New conversation started',
    description: 'User initiated chat with Data Analysis Agent',
    timestamp: new Date(),
    status: 'success' as const
  },
  {
    id: '2',
    type: 'agent' as const,
    title: 'Agent deployment completed',
    description: 'Code Review Agent successfully deployed',
    timestamp: new Date(Date.now() - 5 * 60 * 1000),
    status: 'success' as const
  },
  {
    id: '3',
    type: 'document' as const,
    title: 'Document processed',
    description: 'Financial report analysis completed',
    timestamp: new Date(Date.now() - 10 * 60 * 1000),
    status: 'info' as const
  },
  {
    id: '4',
    type: 'system' as const,
    title: 'System update',
    description: 'NEO platform updated to version 2.1.0',
    timestamp: new Date(Date.now() - 30 * 60 * 1000),
    status: 'warning' as const
  }
]

const demoMessages = [
  {
    id: '1',
    content: 'Hello! I need help analyzing some sales data. Can you help me create visualizations and insights?',
    role: 'user' as const,
    timestamp: new Date(Date.now() - 10 * 60 * 1000),
    status: 'sent' as const
  },
  {
    id: '2',
    content: 'Absolutely! I\'d be happy to help you analyze your sales data and create visualizations. I can help you with:\n\n• Data cleaning and preprocessing\n• Statistical analysis and trends\n• Interactive charts and graphs\n• Key insights and recommendations\n\nPlease upload your sales data file, and let me know what specific aspects you\'d like to focus on.',
    role: 'assistant' as const,
    timestamp: new Date(Date.now() - 9 * 60 * 1000)
  },
  {
    id: '3',
    content: 'Great! I have a CSV file with sales data from the last quarter. I\'m particularly interested in:\n\n1. Monthly sales trends\n2. Top performing products\n3. Regional performance comparison\n4. Customer segmentation insights',
    role: 'user' as const,
    timestamp: new Date(Date.now() - 8 * 60 * 1000),
    status: 'sent' as const,
    attachments: [
      {
        id: 'file1',
        name: 'Q4_sales_data.csv',
        type: 'text/csv',
        url: '#'
      }
    ]
  },
  {
    id: '4',
    content: 'Perfect! I\'ve received your Q4 sales data. Let me analyze this for you. I\'ll start by examining the data structure and then create the visualizations you requested.\n\n```python\nimport pandas as pd\nimport matplotlib.pyplot as plt\nimport seaborn as sns\n\n# Load and examine the data\ndf = pd.read_csv(\'Q4_sales_data.csv\')\nprint(df.head())\nprint(df.info())\n```\n\nI\'m processing your data now and will provide comprehensive insights shortly.',
    role: 'assistant' as const,
    timestamp: new Date(Date.now() - 5 * 60 * 1000)
  }
]

export default function NEODemoPage() {
  const [currentView, setCurrentView] = useState<'dashboard' | 'chat' | 'auth'>('dashboard')
  const [authMode, setAuthMode] = useState<'login' | 'register'>('login')
  const [isLoading, setIsLoading] = useState(false)

  const handleSendMessage = async (content: string, attachments?: File[]) => {
    console.log('Sending message:', content, attachments)
    // Demo implementation
  }

  const handleAuthSubmit = async (data: any) => {
    setIsLoading(true)
    // Demo implementation
    await new Promise(resolve => setTimeout(resolve, 2000))
    setIsLoading(false)
    console.log('Auth data:', data)
  }

  if (currentView === 'auth') {
    return (
      <div className="min-h-screen">
        <NEOAuth
          mode={authMode}
          onSubmit={handleAuthSubmit}
          onModeChange={setAuthMode}
          isLoading={isLoading}
        />
        <div className="fixed top-4 right-4 z-50">
          <button
            onClick={() => setCurrentView('dashboard')}
            className="px-4 py-2 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg shadow-lg hover:shadow-xl transition-all duration-200"
          >
            Back to Demo
          </button>
        </div>
      </div>
    )
  }

  return (
    <NEOLayout>
      {/* Demo Navigation */}
      <div className="mb-6 flex gap-4">
        <button
          onClick={() => setCurrentView('dashboard')}
          className={`px-4 py-2 rounded-lg font-medium transition-all duration-200 ${
            currentView === 'dashboard'
              ? 'bg-indigo-500 text-white shadow-lg'
              : 'bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 border border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700'
          }`}
        >
          Dashboard
        </button>
        <button
          onClick={() => setCurrentView('chat')}
          className={`px-4 py-2 rounded-lg font-medium transition-all duration-200 ${
            currentView === 'chat'
              ? 'bg-indigo-500 text-white shadow-lg'
              : 'bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 border border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700'
          }`}
        >
          Chat
        </button>
        <button
          onClick={() => setCurrentView('auth')}
          className="px-4 py-2 rounded-lg font-medium bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 border border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700 transition-all duration-200"
        >
          Auth Page
        </button>
      </div>

      {/* Content */}
      {currentView === 'dashboard' && (
        <NEODashboard
          stats={demoStats}
          recentActivity={demoActivity}
        />
      )}

      {currentView === 'chat' && (
        <div className="h-[calc(100vh-200px)] bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 overflow-hidden">
          <NEOChat
            messages={demoMessages}
            onSendMessage={handleSendMessage}
            isLoading={false}
          />
        </div>
      )}
    </NEOLayout>
  )
}