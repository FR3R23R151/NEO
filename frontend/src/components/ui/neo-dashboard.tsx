'use client'

import React from 'react'
import { motion } from 'framer-motion'
import {
  ChartBarIcon,
  ChatBubbleLeftRightIcon,
  CpuChipIcon,
  DocumentTextIcon,
  ClockIcon,
  TrendingUpIcon,
  TrendingDownIcon,
  SparklesIcon,
  RocketLaunchIcon,
  BoltIcon,
  UserGroupIcon,
  ServerIcon
} from '@heroicons/react/24/outline'
import { cn } from '@/lib/utils'

interface DashboardStats {
  totalChats: number
  activeAgents: number
  documentsProcessed: number
  uptime: string
  chatsTrend: number
  agentsTrend: number
  documentsTrend: number
}

interface RecentActivity {
  id: string
  type: 'chat' | 'agent' | 'document' | 'system'
  title: string
  description: string
  timestamp: Date
  status: 'success' | 'warning' | 'error' | 'info'
}

interface NEODashboardProps {
  stats: DashboardStats
  recentActivity: RecentActivity[]
  className?: string
}

const StatCard = ({ 
  title, 
  value, 
  trend, 
  icon: Icon, 
  color = 'blue' 
}: {
  title: string
  value: string | number
  trend?: number
  icon: React.ComponentType<{ className?: string }>
  color?: 'blue' | 'green' | 'purple' | 'amber'
}) => {
  const colorClasses = {
    blue: 'from-blue-500 to-cyan-500',
    green: 'from-green-500 to-emerald-500',
    purple: 'from-purple-500 to-indigo-500',
    amber: 'from-amber-500 to-orange-500'
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className="neo-glass-card p-6 hover:shadow-lg transition-all duration-200"
    >
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-gray-600 dark:text-gray-400">
            {title}
          </p>
          <p className="text-2xl font-bold text-gray-900 dark:text-white">
            {value}
          </p>
          {trend !== undefined && (
            <div className="flex items-center mt-2">
              {trend > 0 ? (
                <TrendingUpIcon className="h-4 w-4 text-green-500" />
              ) : (
                <TrendingDownIcon className="h-4 w-4 text-red-500" />
              )}
              <span className={cn(
                'text-sm font-medium ml-1',
                trend > 0 ? 'text-green-600' : 'text-red-600'
              )}>
                {Math.abs(trend)}%
              </span>
            </div>
          )}
        </div>
        <div className={cn(
          'p-3 rounded-xl bg-gradient-to-br',
          colorClasses[color]
        )}>
          <Icon className="h-6 w-6 text-white" />
        </div>
      </div>
    </motion.div>
  )
}

const ActivityItem = ({ activity }: { activity: RecentActivity }) => {
  const getIcon = () => {
    switch (activity.type) {
      case 'chat':
        return ChatBubbleLeftRightIcon
      case 'agent':
        return SparklesIcon
      case 'document':
        return DocumentTextIcon
      case 'system':
        return ServerIcon
      default:
        return BoltIcon
    }
  }

  const getStatusColor = () => {
    switch (activity.status) {
      case 'success':
        return 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400'
      case 'warning':
        return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400'
      case 'error':
        return 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400'
      default:
        return 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400'
    }
  }

  const Icon = getIcon()

  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      className="flex items-start gap-3 p-3 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors"
    >
      <div className={cn(
        'p-2 rounded-lg',
        getStatusColor()
      )}>
        <Icon className="h-4 w-4" />
      </div>
      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium text-gray-900 dark:text-white">
          {activity.title}
        </p>
        <p className="text-sm text-gray-500 dark:text-gray-400 truncate">
          {activity.description}
        </p>
        <p className="text-xs text-gray-400 dark:text-gray-500 mt-1">
          {activity.timestamp.toLocaleTimeString()}
        </p>
      </div>
    </motion.div>
  )
}

export function NEODashboard({ stats, recentActivity, className }: NEODashboardProps) {
  return (
    <div className={cn('space-y-6', className)}>
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            Dashboard
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">
            Welcome back! Here's what's happening with your NEO agents.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <div className="h-2 w-2 bg-green-500 rounded-full animate-pulse" />
          <span className="text-sm text-gray-600 dark:text-gray-400">
            System Online
          </span>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          title="Total Conversations"
          value={stats.totalChats.toLocaleString()}
          trend={stats.chatsTrend}
          icon={ChatBubbleLeftRightIcon}
          color="blue"
        />
        <StatCard
          title="Active Agents"
          value={stats.activeAgents}
          trend={stats.agentsTrend}
          icon={SparklesIcon}
          color="purple"
        />
        <StatCard
          title="Documents Processed"
          value={stats.documentsProcessed.toLocaleString()}
          trend={stats.documentsTrend}
          icon={DocumentTextIcon}
          color="green"
        />
        <StatCard
          title="System Uptime"
          value={stats.uptime}
          icon={ClockIcon}
          color="amber"
        />
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Quick Actions */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3, delay: 0.1 }}
          className="neo-glass-card p-6"
        >
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            Quick Actions
          </h2>
          <div className="space-y-3">
            <button className="w-full flex items-center gap-3 p-3 rounded-lg bg-gradient-to-r from-indigo-500 to-purple-600 text-white hover:from-indigo-600 hover:to-purple-700 transition-all duration-200">
              <ChatBubbleLeftRightIcon className="h-5 w-5" />
              <span>Start New Chat</span>
            </button>
            <button className="w-full flex items-center gap-3 p-3 rounded-lg border border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors">
              <RocketLaunchIcon className="h-5 w-5 text-gray-600 dark:text-gray-400" />
              <span className="text-gray-900 dark:text-white">Create Project</span>
            </button>
            <button className="w-full flex items-center gap-3 p-3 rounded-lg border border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors">
              <DocumentTextIcon className="h-5 w-5 text-gray-600 dark:text-gray-400" />
              <span className="text-gray-900 dark:text-white">Upload Document</span>
            </button>
          </div>
        </motion.div>

        {/* System Status */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3, delay: 0.2 }}
          className="neo-glass-card p-6"
        >
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            System Status
          </h2>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <div className="h-2 w-2 bg-green-500 rounded-full" />
                <span className="text-sm text-gray-600 dark:text-gray-400">Database</span>
              </div>
              <span className="text-sm font-medium text-green-600">Healthy</span>
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <div className="h-2 w-2 bg-green-500 rounded-full" />
                <span className="text-sm text-gray-600 dark:text-gray-400">API Server</span>
              </div>
              <span className="text-sm font-medium text-green-600">Online</span>
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <div className="h-2 w-2 bg-green-500 rounded-full" />
                <span className="text-sm text-gray-600 dark:text-gray-400">Isolator</span>
              </div>
              <span className="text-sm font-medium text-green-600">Running</span>
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <div className="h-2 w-2 bg-yellow-500 rounded-full" />
                <span className="text-sm text-gray-600 dark:text-gray-400">Storage</span>
              </div>
              <span className="text-sm font-medium text-yellow-600">85% Full</span>
            </div>
          </div>
        </motion.div>

        {/* Recent Activity */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3, delay: 0.3 }}
          className="neo-glass-card p-6"
        >
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            Recent Activity
          </h2>
          <div className="space-y-2 max-h-80 overflow-y-auto neo-scrollbar">
            {recentActivity.map((activity) => (
              <ActivityItem key={activity.id} activity={activity} />
            ))}
          </div>
        </motion.div>
      </div>

      {/* Performance Chart Placeholder */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3, delay: 0.4 }}
        className="neo-glass-card p-6"
      >
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
            Performance Overview
          </h2>
          <div className="flex items-center gap-2">
            <button className="px-3 py-1 text-sm rounded-lg bg-indigo-100 text-indigo-700 dark:bg-indigo-900/30 dark:text-indigo-400">
              7 days
            </button>
            <button className="px-3 py-1 text-sm rounded-lg text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800">
              30 days
            </button>
          </div>
        </div>
        
        {/* Chart placeholder */}
        <div className="h-64 bg-gradient-to-br from-indigo-50 to-purple-50 dark:from-indigo-900/20 dark:to-purple-900/20 rounded-lg flex items-center justify-center">
          <div className="text-center">
            <ChartBarIcon className="h-12 w-12 text-gray-400 mx-auto mb-2" />
            <p className="text-gray-500 dark:text-gray-400">
              Performance chart will be displayed here
            </p>
          </div>
        </div>
      </motion.div>
    </div>
  )
}