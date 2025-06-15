'use client'

import React, { useState, useEffect } from 'react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  HomeIcon, 
  ChatBubbleLeftRightIcon, 
  CogIcon, 
  UserIcon,
  Bars3Icon,
  XMarkIcon,
  SparklesIcon,
  RocketLaunchIcon,
  CommandLineIcon,
  DocumentTextIcon,
  BoltIcon
} from '@heroicons/react/24/outline'
import { cn } from '@/lib/utils'

interface NavigationItem {
  name: string
  href: string
  icon: React.ComponentType<{ className?: string }>
  badge?: string
  description?: string
}

const navigationItems: NavigationItem[] = [
  {
    name: 'Dashboard',
    href: '/dashboard',
    icon: HomeIcon,
    description: 'Overview and analytics'
  },
  {
    name: 'Chat',
    href: '/chat',
    icon: ChatBubbleLeftRightIcon,
    description: 'AI conversations'
  },
  {
    name: 'Agents',
    href: '/agents',
    icon: SparklesIcon,
    badge: 'New',
    description: 'AI agent marketplace'
  },
  {
    name: 'Projects',
    href: '/projects',
    icon: RocketLaunchIcon,
    description: 'Your workspaces'
  },
  {
    name: 'Terminal',
    href: '/terminal',
    icon: CommandLineIcon,
    description: 'Code execution'
  },
  {
    name: 'Documents',
    href: '/documents',
    icon: DocumentTextIcon,
    description: 'File management'
  }
]

const bottomNavigationItems: NavigationItem[] = [
  {
    name: 'Settings',
    href: '/settings',
    icon: CogIcon,
    description: 'Preferences'
  },
  {
    name: 'Profile',
    href: '/profile',
    icon: UserIcon,
    description: 'Account settings'
  }
]

interface NEONavigationProps {
  className?: string
}

export function NEONavigation({ className }: NEONavigationProps) {
  const [isCollapsed, setIsCollapsed] = useState(false)
  const [isMobileOpen, setIsMobileOpen] = useState(false)
  const pathname = usePathname()

  // Auto-collapse on mobile
  useEffect(() => {
    const handleResize = () => {
      if (window.innerWidth < 768) {
        setIsCollapsed(true)
      }
    }

    handleResize()
    window.addEventListener('resize', handleResize)
    return () => window.removeEventListener('resize', handleResize)
  }, [])

  const NavigationLink = ({ item, isActive }: { item: NavigationItem; isActive: boolean }) => (
    <Link
      href={item.href}
      className={cn(
        'group relative flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition-all duration-200',
        'hover:bg-white/10 hover:backdrop-blur-sm',
        isActive 
          ? 'bg-white/20 text-white shadow-lg backdrop-blur-sm' 
          : 'text-white/70 hover:text-white'
      )}
      onClick={() => setIsMobileOpen(false)}
    >
      <div className={cn(
        'flex h-6 w-6 items-center justify-center transition-transform duration-200',
        'group-hover:scale-110'
      )}>
        <item.icon className="h-5 w-5" />
      </div>
      
      <AnimatePresence>
        {!isCollapsed && (
          <motion.div
            initial={{ opacity: 0, width: 0 }}
            animate={{ opacity: 1, width: 'auto' }}
            exit={{ opacity: 0, width: 0 }}
            transition={{ duration: 0.2 }}
            className="flex items-center gap-2 overflow-hidden"
          >
            <span className="whitespace-nowrap">{item.name}</span>
            {item.badge && (
              <span className="rounded-full bg-gradient-to-r from-amber-400 to-orange-500 px-2 py-0.5 text-xs font-semibold text-white">
                {item.badge}
              </span>
            )}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Tooltip for collapsed state */}
      {isCollapsed && (
        <div className="absolute left-full top-1/2 z-50 ml-2 hidden -translate-y-1/2 group-hover:block">
          <div className="rounded-lg bg-gray-900 px-3 py-2 text-sm text-white shadow-lg">
            <div className="font-medium">{item.name}</div>
            {item.description && (
              <div className="text-xs text-gray-300">{item.description}</div>
            )}
            {item.badge && (
              <div className="mt-1">
                <span className="rounded-full bg-gradient-to-r from-amber-400 to-orange-500 px-2 py-0.5 text-xs font-semibold text-white">
                  {item.badge}
                </span>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Active indicator */}
      {isActive && (
        <motion.div
          layoutId="activeIndicator"
          className="absolute inset-0 rounded-xl bg-gradient-to-r from-indigo-500/20 to-purple-500/20 backdrop-blur-sm"
          transition={{ type: "spring", bounce: 0.2, duration: 0.6 }}
        />
      )}
    </Link>
  )

  return (
    <>
      {/* Mobile Menu Button */}
      <button
        onClick={() => setIsMobileOpen(!isMobileOpen)}
        className="fixed top-4 left-4 z-50 flex h-10 w-10 items-center justify-center rounded-lg bg-gray-900/80 text-white backdrop-blur-sm md:hidden"
      >
        {isMobileOpen ? (
          <XMarkIcon className="h-5 w-5" />
        ) : (
          <Bars3Icon className="h-5 w-5" />
        )}
      </button>

      {/* Mobile Overlay */}
      <AnimatePresence>
        {isMobileOpen && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-40 bg-black/50 backdrop-blur-sm md:hidden"
            onClick={() => setIsMobileOpen(false)}
          />
        )}
      </AnimatePresence>

      {/* Navigation Sidebar */}
      <motion.nav
        initial={false}
        animate={{
          width: isCollapsed ? 80 : 280,
          x: isMobileOpen ? 0 : (window.innerWidth < 768 ? -280 : 0)
        }}
        transition={{ type: "spring", bounce: 0.1, duration: 0.4 }}
        className={cn(
          'fixed left-0 top-0 z-40 h-full',
          'bg-gradient-to-b from-slate-900 via-slate-800 to-slate-900',
          'border-r border-white/10 backdrop-blur-xl',
          'md:relative md:translate-x-0',
          className
        )}
      >
        {/* Header */}
        <div className="flex h-16 items-center justify-between px-4">
          <AnimatePresence>
            {!isCollapsed && (
              <motion.div
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.8 }}
                transition={{ duration: 0.2 }}
                className="flex items-center gap-3"
              >
                <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-indigo-500 to-purple-600">
                  <BoltIcon className="h-5 w-5 text-white" />
                </div>
                <div>
                  <h1 className="text-lg font-bold text-white">NEO</h1>
                  <p className="text-xs text-white/60">AI Agent Platform</p>
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Collapse Button */}
          <button
            onClick={() => setIsCollapsed(!isCollapsed)}
            className="hidden h-8 w-8 items-center justify-center rounded-lg text-white/60 transition-colors hover:bg-white/10 hover:text-white md:flex"
          >
            <motion.div
              animate={{ rotate: isCollapsed ? 180 : 0 }}
              transition={{ duration: 0.2 }}
            >
              <Bars3Icon className="h-4 w-4" />
            </motion.div>
          </button>
        </div>

        {/* Navigation Items */}
        <div className="flex flex-1 flex-col justify-between px-4 py-4">
          <div className="space-y-2">
            {navigationItems.map((item) => (
              <NavigationLink
                key={item.href}
                item={item}
                isActive={pathname === item.href}
              />
            ))}
          </div>

          {/* Bottom Navigation */}
          <div className="space-y-2 border-t border-white/10 pt-4">
            {bottomNavigationItems.map((item) => (
              <NavigationLink
                key={item.href}
                item={item}
                isActive={pathname === item.href}
              />
            ))}
          </div>
        </div>

        {/* Status Indicator */}
        <AnimatePresence>
          {!isCollapsed && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: 20 }}
              className="border-t border-white/10 p-4"
            >
              <div className="flex items-center gap-3 rounded-lg bg-white/5 p-3">
                <div className="h-2 w-2 rounded-full bg-green-500 animate-pulse" />
                <div className="flex-1">
                  <p className="text-sm font-medium text-white">System Online</p>
                  <p className="text-xs text-white/60">All services running</p>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </motion.nav>
    </>
  )
}