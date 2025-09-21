import React from 'react';
import { HeaderFilterControls } from '../filters';

interface DashboardLayoutProps {
  children: React.ReactNode;
}

export function DashboardLayout({ children }: DashboardLayoutProps) {
  return (
    <div className="min-h-screen bg-[#FAFAFA]">
      {/* Header */}
      <header className="sticky top-0 z-40 border-b border-[#F1F1F1] bg-white shadow-sm">
        <div className="flex h-14 items-center max-w-8xl mx-auto px-2 sm:px-4 lg:px-16">
          <div className="flex items-center space-x-2 min-w-0 flex-shrink-0">
            <div className="flex items-center space-x-2 min-w-0">
              <div className="h-7 w-7 sm:h-8 sm:w-8 rounded-lg bg-[#459B63] flex items-center justify-center shadow-sm flex-shrink-0">
                <svg className="w-4 h-4 sm:w-5 sm:h-5 text-white" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M2 11a1 1 0 011-1h2a1 1 0 011 1v5a1 1 0 01-1 1H3a1 1 0 01-1-1v-5zM8 7a1 1 0 011-1h2a1 1 0 011 1v9a1 1 0 01-1 1H9a1 1 0 01-1-1V7zM14 4a1 1 0 011-1h2a1 1 0 011 1v12a1 1 0 01-1 1h-2a1 1 0 01-1-1V4z" />
                </svg>
              </div>
              <div className="hidden sm:block min-w-0">
                <h1 className="text-sm sm:text-base font-bold text-gray-900 truncate">
                  Financial Dashboard
                </h1>
                <p className="text-xs text-gray-600 truncate">
                  Short-term rental portfolio analytics
                </p>
              </div>
            </div>
          </div>

          {/* Filter Controls in Header */}
          <div className="ml-auto min-w-0 flex-shrink-0">
            <HeaderFilterControls />
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 p-3 sm:p-4">
        <div className="max-w-8xl mx-auto space-y-6 px-2 sm:px-4 lg:px-12">
          <div className="flex justify-between text-xl font-bold  mt-2">
            <div className='text-gray-900'>
              Welcome Back, Laeeq{" "} 👋
            </div>
            <div className='text-gray-700 text-lg'>{new Date().toDateString()}</div>
          </div>
          {children}
        </div>
      </main>
    </div>
  );
}