'use client'

import React, { useState, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  PaperAirplaneIcon,
  MicrophoneIcon,
  PaperClipIcon,
  StopIcon,
  SparklesIcon,
  UserIcon,
  ComputerDesktopIcon,
  ClockIcon,
  CheckIcon,
  ExclamationTriangleIcon
} from '@heroicons/react/24/outline'
import { cn } from '@/lib/utils'

interface Message {
  id: string
  content: string
  role: 'user' | 'assistant' | 'system'
  timestamp: Date
  status?: 'sending' | 'sent' | 'error'
  attachments?: Array<{
    id: string
    name: string
    type: string
    url: string
  }>
}

interface NEOChatProps {
  messages: Message[]
  onSendMessage: (content: string, attachments?: File[]) => void
  isLoading?: boolean
  className?: string
}

export function NEOChat({ messages, onSendMessage, isLoading = false, className }: NEOChatProps) {
  const [inputValue, setInputValue] = useState('')
  const [isRecording, setIsRecording] = useState(false)
  const [attachments, setAttachments] = useState<File[]>([])
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLTextAreaElement>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  // Auto-resize textarea
  useEffect(() => {
    if (inputRef.current) {
      inputRef.current.style.height = 'auto'
      inputRef.current.style.height = `${inputRef.current.scrollHeight}px`
    }
  }, [inputValue])

  const handleSend = () => {
    if (inputValue.trim() || attachments.length > 0) {
      onSendMessage(inputValue.trim(), attachments)
      setInputValue('')
      setAttachments([])
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || [])
    setAttachments(prev => [...prev, ...files])
  }

  const removeAttachment = (index: number) => {
    setAttachments(prev => prev.filter((_, i) => i !== index))
  }

  const MessageBubble = ({ message }: { message: Message }) => {
    const isUser = message.role === 'user'
    const isSystem = message.role === 'system'

    return (
      <motion.div
        initial={{ opacity: 0, y: 20, scale: 0.95 }}
        animate={{ opacity: 1, y: 0, scale: 1 }}
        transition={{ duration: 0.3, ease: "easeOut" }}
        className={cn(
          'flex gap-3 group',
          isUser ? 'justify-end' : 'justify-start'
        )}
      >
        {/* Avatar */}
        {!isUser && (
          <div className={cn(
            'flex h-8 w-8 items-center justify-center rounded-full shrink-0',
            isSystem 
              ? 'bg-amber-100 text-amber-600 dark:bg-amber-900/30 dark:text-amber-400'
              : 'bg-gradient-to-br from-indigo-500 to-purple-600 text-white'
          )}>
            {isSystem ? (
              <ComputerDesktopIcon className="h-4 w-4" />
            ) : (
              <SparklesIcon className="h-4 w-4" />
            )}
          </div>
        )}

        {/* Message Content */}
        <div className={cn(
          'flex flex-col gap-1 max-w-[80%]',
          isUser && 'items-end'
        )}>
          {/* Message Bubble */}
          <div className={cn(
            'relative rounded-2xl px-4 py-3 shadow-sm',
            'transition-all duration-200 group-hover:shadow-md',
            isUser 
              ? 'bg-gradient-to-br from-indigo-500 to-purple-600 text-white'
              : isSystem
                ? 'bg-amber-50 text-amber-800 border border-amber-200 dark:bg-amber-900/20 dark:text-amber-200 dark:border-amber-800/30'
                : 'bg-white text-gray-900 border border-gray-200 dark:bg-gray-800 dark:text-gray-100 dark:border-gray-700'
          )}>
            {/* Message Text */}
            <div className="prose prose-sm max-w-none">
              <p className="m-0 whitespace-pre-wrap break-words">
                {message.content}
              </p>
            </div>

            {/* Attachments */}
            {message.attachments && message.attachments.length > 0 && (
              <div className="mt-3 space-y-2">
                {message.attachments.map((attachment) => (
                  <div
                    key={attachment.id}
                    className="flex items-center gap-2 rounded-lg bg-black/10 p-2"
                  >
                    <PaperClipIcon className="h-4 w-4" />
                    <span className="text-sm">{attachment.name}</span>
                  </div>
                ))}
              </div>
            )}

            {/* Status Indicator for User Messages */}
            {isUser && (
              <div className="absolute -bottom-1 -right-1">
                {message.status === 'sending' && (
                  <div className="h-4 w-4 rounded-full bg-gray-300 animate-pulse" />
                )}
                {message.status === 'sent' && (
                  <div className="h-4 w-4 rounded-full bg-green-500 flex items-center justify-center">
                    <CheckIcon className="h-2.5 w-2.5 text-white" />
                  </div>
                )}
                {message.status === 'error' && (
                  <div className="h-4 w-4 rounded-full bg-red-500 flex items-center justify-center">
                    <ExclamationTriangleIcon className="h-2.5 w-2.5 text-white" />
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Timestamp */}
          <div className={cn(
            'flex items-center gap-1 text-xs text-gray-500 dark:text-gray-400',
            isUser && 'flex-row-reverse'
          )}>
            <ClockIcon className="h-3 w-3" />
            <span>
              {message.timestamp.toLocaleTimeString([], { 
                hour: '2-digit', 
                minute: '2-digit' 
              })}
            </span>
          </div>
        </div>

        {/* User Avatar */}
        {isUser && (
          <div className="flex h-8 w-8 items-center justify-center rounded-full bg-gray-200 text-gray-600 shrink-0 dark:bg-gray-700 dark:text-gray-300">
            <UserIcon className="h-4 w-4" />
          </div>
        )}
      </motion.div>
    )
  }

  const TypingIndicator = () => (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className="flex gap-3"
    >
      <div className="flex h-8 w-8 items-center justify-center rounded-full bg-gradient-to-br from-indigo-500 to-purple-600 text-white">
        <SparklesIcon className="h-4 w-4" />
      </div>
      <div className="flex items-center gap-1 rounded-2xl bg-white px-4 py-3 shadow-sm border border-gray-200 dark:bg-gray-800 dark:border-gray-700">
        <div className="flex gap-1">
          {[0, 1, 2].map((i) => (
            <motion.div
              key={i}
              className="h-2 w-2 rounded-full bg-gray-400"
              animate={{ scale: [1, 1.2, 1] }}
              transition={{
                duration: 1,
                repeat: Infinity,
                delay: i * 0.2
              }}
            />
          ))}
        </div>
        <span className="ml-2 text-sm text-gray-500">NEO is thinking...</span>
      </div>
    </motion.div>
  )

  return (
    <div className={cn('flex flex-col h-full bg-gray-50 dark:bg-gray-900', className)}>
      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 neo-scrollbar">
        <AnimatePresence>
          {messages.map((message) => (
            <MessageBubble key={message.id} message={message} />
          ))}
          {isLoading && <TypingIndicator />}
        </AnimatePresence>
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="border-t border-gray-200 bg-white p-4 dark:border-gray-700 dark:bg-gray-800">
        {/* Attachments Preview */}
        <AnimatePresence>
          {attachments.length > 0 && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className="mb-3 flex flex-wrap gap-2"
            >
              {attachments.map((file, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, scale: 0.8 }}
                  animate={{ opacity: 1, scale: 1 }}
                  className="flex items-center gap-2 rounded-lg bg-gray-100 px-3 py-2 text-sm dark:bg-gray-700"
                >
                  <PaperClipIcon className="h-4 w-4" />
                  <span className="max-w-32 truncate">{file.name}</span>
                  <button
                    onClick={() => removeAttachment(index)}
                    className="text-gray-500 hover:text-red-500"
                  >
                    ×
                  </button>
                </motion.div>
              ))}
            </motion.div>
          )}
        </AnimatePresence>

        {/* Input Row */}
        <div className="flex items-end gap-3">
          {/* File Upload */}
          <button
            onClick={() => fileInputRef.current?.click()}
            className="flex h-10 w-10 items-center justify-center rounded-full text-gray-500 transition-colors hover:bg-gray-100 hover:text-gray-700 dark:hover:bg-gray-700 dark:hover:text-gray-300"
          >
            <PaperClipIcon className="h-5 w-5" />
          </button>
          <input
            ref={fileInputRef}
            type="file"
            multiple
            className="hidden"
            onChange={handleFileSelect}
          />

          {/* Text Input */}
          <div className="flex-1 relative">
            <textarea
              ref={inputRef}
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Type your message..."
              className="w-full resize-none rounded-2xl border border-gray-300 bg-white px-4 py-3 pr-12 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500 dark:border-gray-600 dark:bg-gray-700 dark:text-white dark:focus:border-indigo-400"
              rows={1}
              style={{ maxHeight: '120px' }}
            />
          </div>

          {/* Voice Recording */}
          <button
            onClick={() => setIsRecording(!isRecording)}
            className={cn(
              'flex h-10 w-10 items-center justify-center rounded-full transition-all duration-200',
              isRecording
                ? 'bg-red-500 text-white animate-pulse'
                : 'text-gray-500 hover:bg-gray-100 hover:text-gray-700 dark:hover:bg-gray-700 dark:hover:text-gray-300'
            )}
          >
            {isRecording ? (
              <StopIcon className="h-5 w-5" />
            ) : (
              <MicrophoneIcon className="h-5 w-5" />
            )}
          </button>

          {/* Send Button */}
          <button
            onClick={handleSend}
            disabled={!inputValue.trim() && attachments.length === 0}
            className={cn(
              'flex h-10 w-10 items-center justify-center rounded-full transition-all duration-200',
              inputValue.trim() || attachments.length > 0
                ? 'bg-gradient-to-r from-indigo-500 to-purple-600 text-white shadow-lg hover:shadow-xl hover:scale-105'
                : 'bg-gray-200 text-gray-400 cursor-not-allowed dark:bg-gray-700 dark:text-gray-500'
            )}
          >
            <PaperAirplaneIcon className="h-5 w-5" />
          </button>
        </div>

        {/* Quick Actions */}
        <div className="mt-3 flex gap-2">
          <button className="rounded-full bg-gray-100 px-3 py-1 text-xs text-gray-600 transition-colors hover:bg-gray-200 dark:bg-gray-700 dark:text-gray-300 dark:hover:bg-gray-600">
            💡 Suggest ideas
          </button>
          <button className="rounded-full bg-gray-100 px-3 py-1 text-xs text-gray-600 transition-colors hover:bg-gray-200 dark:bg-gray-700 dark:text-gray-300 dark:hover:bg-gray-600">
            🔍 Analyze data
          </button>
          <button className="rounded-full bg-gray-100 px-3 py-1 text-xs text-gray-600 transition-colors hover:bg-gray-200 dark:bg-gray-700 dark:text-gray-300 dark:hover:bg-gray-600">
            📝 Write code
          </button>
        </div>
      </div>
    </div>
  )
}