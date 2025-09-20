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
        <div className="flex h-16 items-center px-4 sm:px-6">
          <div className="flex items-center space-x-2 sm:space-x-4 min-w-0 flex-shrink-0">
            <div className="flex items-center space-x-2 sm:space-x-3 min-w-0">
              <div className="h-8 w-8 sm:h-10 sm:w-10 rounded-xl bg-[#459B63] flex items-center justify-center shadow-sm flex-shrink-0">
                <span className="text-white font-bold text-sm sm:text-lg">FD</span>
              </div>
              <div className="hidden sm:block min-w-0">
                <h1 className="text-lg sm:text-xl font-bold text-gray-900 truncate">
                  Financial Dashboard
                </h1>
                <p className="text-xs sm:text-sm text-gray-600 truncate">
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
      <main className="flex-1 p-6">
        <div className="max-w-7xl mx-auto space-y-12">
          {children}
        </div>
      </main>
    </div>
  );
}