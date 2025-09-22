import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

// Safe number formatting utilities
export function formatCurrency(value: number | undefined | null, options?: Intl.NumberFormatOptions): string {
  const num = typeof value === 'number' ? value : 0;
  return num.toLocaleString('en-US', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
    ...options
  });
}

export function formatNumber(value: number | undefined | null, options?: Intl.NumberFormatOptions): string {
  const num = typeof value === 'number' ? value : 0;
  return num.toLocaleString('en-US', options);
}