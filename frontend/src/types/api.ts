// Property types
export interface Property {
  property_id: number;
  property_name: string;
  reviews_count: number;
  average_review_score: number;
}

// Revenue types
export interface RevenuePoint {
  date: string;
  revenue: number;
  property_id?: number;
}

export interface RevenueTimeline {
  data: Array<{
    date: string;
    total_revenue: number;
    property_breakdown?: Record<number, number>;
  }>;
}

export interface PropertyRevenue {
  data: Array<{
    property_id: number;
    property_name: string;
    total_revenue: number;
  }>;
}

// Maintenance types
export interface LostIncomeData {
  data: Array<{
    property_id: number;
    property_name: string;
    lost_income: number;
    blocked_days: number;
  }>;
}

// Review types
export interface ReviewTrend {
  month: string;
  avg_rating: number;
  review_count: number;
}

export interface ReviewTrendsData {
  data: ReviewTrend[];
}

// Lead time types
export interface LeadTimeStats {
  median_days: number;
  p90_days: number;
  distribution: number[]; // histogram bins
}

export interface LeadTimeData {
  stats: LeadTimeStats;
  data: Array<{
    lead_time_days: number;
    count: number;
  }>;
}

// Filter types
export interface DateRange {
  start_date?: string;
  end_date?: string;
}

export interface ApiFilters extends DateRange {
  property_ids?: number[];
}

// API Error types
export interface ApiError {
  detail: string;
  status_code: number;
}