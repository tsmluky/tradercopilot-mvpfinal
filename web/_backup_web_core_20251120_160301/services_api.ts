// services/api.ts
// Cliente HTTP principal para el backend FastAPI de TraderCopilot
// Incluye fallback con mocks para entorno de desarrollo o sin conexión

import {
  API_BASE_URL,
  MOCK_LITE_SIGNAL,
  MOCK_PRO_RESPONSE,
  MOCK_ADVISOR_RESPONSE,
} from "../constants";
import {
  SignalLite,
  ProResponse,
  AdvisorResponse,
  SignalEvaluation,
  LogRow,
  LeaderboardEntry,
  ChatMessage,
} from "../types";

// ====================
// Tipos base
// ====================
export type LogMode = "LITE" | "PRO" | "ADVISOR" | "EVALUATED";

export interface LogsResponse<T = Record<string, any>> {
  count: number;
  logs: T[];
}

export type SignalEvaluationResult =
  | "hit-tp"
  | "hit-sl"
  | "open"
  | "neutral"
  | string;

export interface StatsSummary {
  win_rate_24h: number | null;
  signals_evaluated_24h: number;
  signals_total_evaluated: number;
  signals_lite_24h: number;
  open_signals: number;
}

// ====================
// Helper genérico con fallback
// ====================
async function fetchWithFallback<T>(
  url: string,
  options: RequestInit,
  mockData: T,
  timeoutMs = 3000
): Promise<T> {
  try {
    const controller = new AbortController();
    const id = setTimeout(() => controller.abort(), timeoutMs);

    const response = await fetch(url, {
      ...options,
      signal: controller.signal,
      headers: {
        "Content-Type": "application/json",
        ...options.headers,
      },
    });
    clearTimeout(id);

    if (!response.ok) throw new Error(`HTTP ${response.status}`);

    const contentType = response.headers.get("content-type");
    if (contentType?.includes("application/json")) {
      return (await response.json()) as T;
    }
    return (await response.text()) as unknown as T;
  } catch (err) {
    console.warn(`⚠️ [TraderCopilot API] Fallback -> ${url}`, err);
    await new Promise((r) => setTimeout(r, 800));
    return mockData;
  }
}

// ====================
// CSV Parser
// ====================
const parseCSV = (csvText: string): LogRow[] => {
  if (!csvText) return [];
  const lines = csvText.trim().split(/\r?\n/);
  if (lines.length < 2) return [];

  const headers = lines[0].split(",").map((h) => h.trim());
  return lines.slice(1).map((line) => {
    const cols = line.split(",");
    const obj: LogRow = {};
    headers.forEach((h, i) => {
      obj[h] = cols[i]?.trim() ?? "";
    });
    return obj;
  });
};

// ====================
// Mock Data
// ====================
const MOCK_CSV_EVALUATED = `signal_ts,evaluated_at,token,timeframe,entry,tp,sl,price_at_eval,result,move_pct
2024-11-16T10:00:00Z,2024-11-16T14:00:00Z,ETH,30m,3650.00,3700.00,3620.00,3705.00,WIN,+1.5%
2024-11-16T11:00:00Z,2024-11-16T15:00:00Z,BTC,1h,96000.00,98000.00,95000.00,94800.00,LOSS,-1.2%
2024-11-16T12:30:00Z,2024-11-16T16:30:00Z,SOL,15m,210.50,215.00,208.00,212.00,OPEN,+0.7%`;

const MOCK_CSV_LITE = `timestamp,token,timeframe,direction,entry,confidence
2024-11-16T10:00:00Z,ETH,30m,long,3650.00,0.75
2024-11-16T11:00:00Z,BTC,1h,long,96000.00,0.65`;

const MOCK_LEADERBOARD: LeaderboardEntry[] = [
  {
    rank: 1,
    user_name: "AlphaSeeker",
    avatar_url:
      "https://ui-avatars.com/api/?name=AS&background=10b981&color=fff",
    win_rate: 78,
    total_pnl: 45.2,
    signals_tracked: 124,
  },
  {
    rank: 2,
    user_name: "Pancho Trader",
    avatar_url:
      "https://ui-avatars.com/api/?name=PT&background=334155&color=fff",
    win_rate: 72,
    total_pnl: 39.8,
    signals_tracked: 98,
    is_current_user: true,
  },
];

// ====================
// API principal
// ====================
export const api = {
  // ---- Análisis ----
  async analyzeLite(token: string, timeframe: string): Promise<SignalLite> {
    const freshMock = {
      ...MOCK_LITE_SIGNAL,
      token: token.toUpperCase(),
      timeframe,
      timestamp: new Date().toISOString(),
    };

    return fetchWithFallback<SignalLite>(
      `${API_BASE_URL}/analyze/lite`,
      {
        method: "POST",
        body: JSON.stringify({ token, timeframe }),
      },
      freshMock
    );
  },

  async analyzePro(
    token: string,
    timeframe: string,
    rag: boolean
  ): Promise<ProResponse> {
    return fetchWithFallback<ProResponse>(
      `${API_BASE_URL}/analyze/pro`,
      {
        method: "POST",
        body: JSON.stringify({ token, timeframe, context: { rag } }),
      },
      { raw: MOCK_PRO_RESPONSE }
    );
  },

  async analyzeAdvisor(data: {
    token: string;
    direction: string;
    entry: number;
    tp: number;
    sl: number;
    size_quote: number;
  }): Promise<AdvisorResponse> {
    return fetchWithFallback<AdvisorResponse>(
      `${API_BASE_URL}/analyze/advisor`,
      {
        method: "POST",
        body: JSON.stringify(data),
      },
      {
        ...MOCK_ADVISOR_RESPONSE,
        token: data.token.toUpperCase(),
        direction: data.direction as "long" | "short",
        entry: data.entry,
      }
    );
  },

  // ---- Advisor Chat (simulado) ----
  async sendAdvisorChat(
    history: ChatMessage[],
    context: any
  ): Promise<ChatMessage> {
    await new Promise((r) => setTimeout(r, 1200));
    const last = history[history.length - 1];
    const text = last?.content?.toLowerCase() ?? "";
    let msg = "";

    if (text.includes("risk")) {
      msg = `To reduce risk on ${context.token}, consider reducing position by 30% or waiting for ${context.entry * 0.98}.`;
    } else if (text.includes("tp")) {
      msg = `TP near ${context.entry * 1.05} would optimize R/R ratio.`;
    } else if (text.includes("sl")) {
      msg = `Consider a wider SL near ${context.entry * 0.95} for reduced noise.`;
    } else {
      msg = `Understood. The ${context.token} structure looks stable. Do you want to recalc scenarios?`;
    }

    return {
      id: Date.now().toString(),
      role: "assistant",
      content: msg,
      type: "text",
      timestamp: new Date().toISOString(),
    };
  },

  // ---- Logs ----
  async fetchLogs(mode: string, token: string): Promise<LogRow[]> {
    const mock = mode === "EVALUATED" ? MOCK_CSV_EVALUATED : MOCK_CSV_LITE;
    const csv = await fetchWithFallback<string>(
      `${API_BASE_URL}/logs/${mode}/${token}`,
      { method: "GET" },
      mock
    );
    return parseCSV(csv);
  },

  // ---- Evaluación de señales ----
  async getSignalEvaluation(
    token: string,
    signalTimestamp: string
  ): Promise<SignalEvaluation | null> {
    const mock: SignalEvaluation = {
      signal_ts: signalTimestamp,
      evaluated_at: new Date().toISOString(),
      token,
      timeframe: "30m",
      entry: 3650,
      tp: 3700,
      sl: 3620,
      price_at_eval: 3705,
      result: Math.random() > 0.4 ? "hit-tp" : "hit-sl",
      move_pct: Math.random() > 0.4 ? 1.5 : -1.0,
      notes: "Simulated evaluation result",
    };
    return new Promise((r) => setTimeout(() => r(mock), 600));
  },

  // ---- Telegram ----
  async notifyTelegram(message: string): Promise<boolean> {
    return fetchWithFallback<boolean>(
      `${API_BASE_URL}/notify/telegram`,
      {
        method: "POST",
        body: JSON.stringify({ text: message }),
      },
      true
    );
  },

  // ---- Leaderboard ----
  async fetchLeaderboard(): Promise<LeaderboardEntry[]> {
    return new Promise((r) => setTimeout(() => r(MOCK_LEADERBOARD), 600));
  },

  // ---- Stats summary ----
  async fetchStatsSummary(): Promise<StatsSummary> {
    return fetchWithFallback<StatsSummary>(
      `${API_BASE_URL}/stats/summary`,
      { method: "GET" },
      {
        win_rate_24h: 0.67,
        signals_evaluated_24h: 12,
        signals_total_evaluated: 240,
        signals_lite_24h: 20,
        open_signals: 5,
      }
    );
  },
};
