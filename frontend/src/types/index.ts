export interface User {
  id: string;
  email: string;
  name?: string;
  plan: 'basic' | 'pro' | 'premium' | 'bot' | 'enterprise';
  status: string;
  created_at: string;
}

export interface TradingSignal {
  id: string;
  symbol: string;
  action: 'BUY' | 'SELL';
  confidence: number;
  entry_price: number;
  stop_loss?: number;
  take_profit?: number;
  risk_reward?: number;
  timeframe: string;
  reason: string;
  created_at: string;
}

export interface Subscription {
  id: string;
  plan: string;
  monthly_fee: number;
  currency: string;
  status: string;
  next_billing_date: string;
  created_at: string;
}

export interface AnalysisRequest {
  symbols: string[];
  timeframe: string;
  max_signals?: number;
}

export interface AnalysisResponse {
  symbols_analyzed: number;
  signals_generated: number;
  signals: TradingSignal[];
  timestamp: string;
}

export interface AuthTokens {
  access_token: string;
  token_type: string;
  expires_in: number;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface SignupData {
  email: string;
  name?: string;
  phone?: string;
  plan?: string;
  password: string;
}

export interface PlanInfo {
  name: string;
  price: number;
  features: string[];
  signalsPerDay: string;
  popular?: boolean;
}
