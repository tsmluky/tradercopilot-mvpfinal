
export enum AnalysisMode {
  LITE = 'LITE',
  PRO = 'PRO',
  ADVISOR = 'ADVISOR',
  EVALUATED = 'EVALUATED'
}

export interface SignalLite {
  timestamp: string;
  token: string;
  timeframe: string;
  direction: 'long' | 'short';
  entry: number;
  tp: number;
  sl: number;
  confidence: number;
  rationale: string;
  source: string;
}

export interface SignalEvaluation {
  status: 'WIN' | 'LOSS' | 'BE'; // Break Even
  pnl_r: number; // Realized R-multiple (e.g. 1.5 or -1.0)
  exit_price: number;
  closed_at: string;
}

export interface ProContext {
  rag: boolean;
}

export interface ProResponse {
  raw: string; // The full markdown content
  sections?: {
    ctxt?: string;
    ta?: string;
    plan?: string;
    insight?: string;
    params?: string;
  };
}

export interface AdvisorAlternative {
  if: string;
  action: string;
  rr_target: number;
}

export interface AdvisorResponse {
  token: string;
  direction: 'long' | 'short';
  entry: number;
  size_quote: number;
  tp: number;
  sl: number;
  alternatives: AdvisorAlternative[];
  risk_score: number;
  confidence: number;
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  type: 'text' | 'analysis';
  data?: AdvisorResponse; // For embedding the card
  timestamp: string;
}

export interface LogEntry {
  timestamp: string;
  mode: string;
  token: string;
  details: string; // JSON string or summary
}

export interface LogRow {
  [key: string]: string;
}

export interface MarketRate {
  token: string;
  price: number;
  change24h: number;
}

export interface ChartDataPoint {
  time: string;
  price: number;
  vol: number;
}

export interface User {
  id: string;
  email: string;
  name: string;
  role: 'admin' | 'user';
  avatar_url?: string;
  subscription_status: 'active' | 'inactive' | 'trial' | 'free' | 'trader' | 'pro';
  plan?: string; // Backend plan (FREE/PRO/OWNER)
  plan_status?: string;
  onboarding_completed?: boolean;
  allowed_tokens?: string[];
}

export interface FollowedSignal extends SignalLite {
  followed_at: string;
  status?: 'OPEN' | 'WIN' | 'LOSS'; // Personal tracking status
  final_pnl?: number;
  notes?: string; // Journaling notes
}

export interface NotificationPreferences {
  trade_updates: boolean;
  market_volatility: boolean;
  system_status: boolean;
}

export interface UserProfile {
  user: User;
  preferences: {
    favorite_tokens: string[];
    default_timeframe: string;
    notifications: NotificationPreferences;
  };
  portfolio: {
    followed_signals: FollowedSignal[];
  };
}

export interface Notification {
  id: string;
  title: string;
  message: string;
  time: string;
  type: 'info' | 'alert' | 'success';
  read: boolean;
}

export interface ToastAlert {
  id: string;
  title: string;
  message: string;
  type: 'success' | 'error' | 'info' | 'warning';
}
