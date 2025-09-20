import React from 'react';
import { HeaderFilterControls } from '../filters';
import { cn } from '../../lib/utils';

interface DashboardLayoutProps {
  children: React.ReactNode;
}

const navigationItems = [
  { id: 'revenue', label: 'Revenue Analytics', icon: '📊' },
  { id: 'maintenance', label: 'Maintenance Impact', icon: '🔧' },
  { id: 'reviews', label: 'Review Trends', icon: '⭐' },
  { id: 'leadtime', label: 'Lead Time Analysis', icon: '📅' },
];

export function DashboardLayout({ children }: DashboardLayoutProps) {
  const [activeSection, setActiveSection] = React.useState('revenue');
  const [isSidebarCollapsed, setIsSidebarCollapsed] = React.useState(false);

  // Track active section based on scroll position
  React.useEffect(() => {
    const handleScroll = () => {
      const sections = navigationItems.map(item => item.id);
      const scrollPosition = window.scrollY + 100; // Offset for header

      for (let i = sections.length - 1; i >= 0; i--) {
        const element = document.getElementById(sections[i]);
        if (element && element.offsetTop <= scrollPosition) {
          setActiveSection(sections[i]);
          break;
        }
      }
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  // Handle responsive sidebar collapse
  React.useEffect(() => {
    const handleResize = () => {
      if (window.innerWidth < 1024) {
        setIsSidebarCollapsed(true);
      } else {
        setIsSidebarCollapsed(false);
      }
    };

    handleResize(); // Check initial size
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  const scrollToSection = (sectionId: string) => {
    const element = document.getElementById(sectionId);
    if (element) {
      const headerHeight = 64; // 4rem = 64px
      const elementPosition = element.offsetTop - headerHeight - 20; // 20px extra padding
      window.scrollTo({
        top: elementPosition,
        behavior: 'smooth'
      });
    }
  };

  const sidebarWidth = isSidebarCollapsed ? 'w-16' : 'w-64';
  const mainMargin = isSidebarCollapsed ? 'ml-16' : 'ml-64';

  return (
    <div className="min-h-screen bg-[#FAFAFA]">
      {/* Header */}
      <header className="sticky top-0 z-40 border-b border-[#F1F1F1] bg-white shadow-sm">
        <div className="flex h-16 items-center px-6">
          <div className="flex items-center space-x-4">
            {/* Mobile sidebar toggle */}
            <button
              onClick={() => setIsSidebarCollapsed(!isSidebarCollapsed)}
              className="lg:hidden p-2 rounded-lg hover:bg-[#F5F5F5] transition-colors"
              aria-label="Toggle sidebar"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            </button>
            
            <div className="flex items-center space-x-3">
              <div className="h-10 w-10 rounded-xl bg-[#459B63] flex items-center justify-center shadow-sm">
                <span className="text-white font-bold text-lg">FD</span>
              </div>
              <div className="hidden sm:block">
                <h1 className="text-xl font-bold text-gray-900">
                  Financial Dashboard
                </h1>
                <p className="text-sm text-gray-600">
                  Short-term rental portfolio analytics
                </p>
              </div>
            </div>
          </div>
          
          {/* Compact Filter Controls in Header */}
          <div className="ml-auto">
            <HeaderFilterControls />
          </div>
        </div>
      </header>

      <div className="flex">
        {/* Sidebar Navigation - Fixed */}
        <aside className={cn(
          'fixed left-0 top-16 z-30 h-[calc(100vh-4rem)] border-r border-[#F1F1F1] bg-white overflow-y-auto transition-all duration-300 shadow-sm',
          sidebarWidth,
          isSidebarCollapsed && 'lg:w-64' // Always full width on desktop
        )}>
          <div className="p-4">
            <nav className="space-y-2">
              {navigationItems.map((item) => (
                <button
                  key={item.id}
                  onClick={() => scrollToSection(item.id)}
                  className={cn(
                    'w-full flex items-center space-x-3 px-4 py-3 text-sm font-medium rounded-xl transition-all duration-200 group',
                    activeSection === item.id
                      ? 'bg-[#459B63] text-white shadow-md'
                      : 'text-gray-600 hover:bg-[#F5F5F5] hover:text-gray-900'
                  )}
                  title={isSidebarCollapsed ? item.label : undefined}
                >
                  <span className="text-lg flex-shrink-0">{item.icon}</span>
                  <span className={cn(
                    'transition-opacity duration-200',
                    isSidebarCollapsed && 'lg:opacity-100 opacity-0 lg:block hidden'
                  )}>
                    {item.label}
                  </span>
                </button>
              ))}
            </nav>
          </div>
        </aside>

        {/* Main Content */}
        <main className={cn(
          'flex-1 p-6 transition-all duration-300',
          mainMargin,
          'lg:ml-64' // Always account for full sidebar on desktop
        )}>
          <div className="max-w-7xl mx-auto space-y-12">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
}