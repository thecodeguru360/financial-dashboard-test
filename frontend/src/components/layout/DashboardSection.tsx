import React from 'react';
import { cn } from '../../lib/utils';

interface DashboardSectionProps {
  id: string;
  title: string;
  description?: string;
  children: React.ReactNode;
  className?: string;
}

export function DashboardSection({ 
  id, 
  title, 
  description, 
  children, 
  className 
}: DashboardSectionProps) {
  return (
    <section id={id} className={cn('space-y-6', className)}>
      <div className="space-y-2">
        <h2 className="text-3xl font-bold text-gray-900">{title}</h2>
        {description && (
          <p className="text-gray-600 text-lg">{description}</p>
        )}
      </div>
      <div className="grid gap-6">
        {children}
      </div>
    </section>
  );
}