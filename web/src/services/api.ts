import { API_BASE_URL, MOCK_LITE_SIGNAL, MOCK_PRO_RESPONSE, MOCK_ADVISOR_RESPONSE } from "../constants";
import {
  SignalLite,
  ProResponse,
  AdvisorResponse,
  SignalEvaluation,
  LogRow,
  LeaderboardEntry,
  ChatMessage,
  AnalysisMode,
  UserProfile,
} from "../types";

// =========================
// Helpers HTTP básicos
// =========================

const DEFAULT_TIMEOUT_MS = 15000;


async function fetchWithTimeout(
  url: string,
  init: RequestInit = {},
  timeoutMs: number = DEFAULT_TIMEOUT_MS
): Promise<Response> {
  const controller = new AbortController();
  const id = setTimeout(() => controller.abort(), timeoutMs);

  // Inject Token if available
  const token = localStorage.getItem('auth_token');
  const headers = { ...init.headers } as Record<string, string>;

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  try {
    const res = await fetch(url, { ...init, headers, signal: controller.signal });
    return res;
  } finally {
    clearTimeout(id);
  }
}

// ... existing isJsonContent ...

function isJsonContent(res: Response): boolean {
  const ct = res.headers.get("content-type") || "";
  return ct.toLowerCase().includes("application/json");
}

// CSV -> LogRow[]
const parseCSV = (csvText: string): LogRow[] => {
  if (!csvText) return [];
  const lines = csvText.trim().split(/\r?\n/);
  if (lines.length < 2) return [];

  const headers = lines[0].split(",").map((h) => h.trim());
  const result: LogRow[] = [];

  for (let i = 1; i < lines.length; i++) {
    const line = lines[i].trim();
    if (!line) continue;
    const cols = line.split(",");
    const row: LogRow = {};
    for (let j = 0; j < headers.length; j++) {
      row[headers[j]] = (cols[j] ?? "").trim();
    }
    result.push(row);
  }
  return result;
};

// =========================
// Health (para DevPanel y checks)
// =========================

export async function getHealth(): Promise<any> {
  const res = await fetchWithTimeout(`${API_BASE_URL}/health`, { method: "GET" });
  if (!res.ok) throw new Error(`HTTP ${res.status} ${res.statusText}`);
  return res.json();
}

// =========================
// Análisis LITE / PRO / ADVISOR
// =========================

export async function analyzeLite(token: string, timeframe: string): Promise<SignalLite> {
  const body = { token, timeframe };

  try {
    const res = await fetchWithTimeout(`${API_BASE_URL}/analyze/lite`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });

    if (!res.ok) {
      throw new Error(`HTTP ${res.status} ${res.statusText}`);
    }

    return (await res.json()) as SignalLite;
  } catch (err) {
    console.warn("analyzeLite failed, using mock", err);
    const freshMock: SignalLite = {
      ...(MOCK_LITE_SIGNAL as SignalLite),
      token: token.toUpperCase(),
      timeframe,
      timestamp: new Date().toISOString(),
    };
    return freshMock;
  }
}

export async function analyzePro(
  token: string,
  timeframe: string,
  rag: boolean
): Promise<ProResponse> {
  const body = { token, timeframe, context: { rag } };

  try {
    const res = await fetchWithTimeout(`${API_BASE_URL}/analyze/pro`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });

    if (!res.ok) {
      throw new Error(`HTTP ${res.status} ${res.statusText}`);
    }

    const data: any = isJsonContent(res) ? await res.json() : await res.text();
    const raw =
      typeof data === "string"
        ? data
        : data.analysis ?? data.raw ?? JSON.stringify(data, null, 2);

    return { raw } as ProResponse;
  } catch (err) {
    console.warn("analyzePro failed, using mock", err);
    return { raw: MOCK_PRO_RESPONSE } as ProResponse;
  }
}

type AdvisorPayload = {
  token: string;
  direction: "long" | "short";
  entry: number;
  tp: number;
  sl: number;
  size_quote: number;
};

export async function analyzeAdvisor(payload: AdvisorPayload): Promise<AdvisorResponse> {
  try {
    const res = await fetchWithTimeout(`${API_BASE_URL}/analyze/advisor`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    if (!res.ok) {
      throw new Error(`HTTP ${res.status} ${res.statusText}`);
    }

    return (await res.json()) as AdvisorResponse;
  } catch (err) {
    console.warn("analyzeAdvisor failed, using mock", err);
    return {
      ...(MOCK_ADVISOR_RESPONSE as AdvisorResponse),
      token: payload.token.toUpperCase(),
      direction: payload.direction,
      entry: payload.entry,
    };
  }
}

// =========================
// Logs genéricos /logs/{mode}/{token}
// Devuelve siempre LogRow[]
// =========================

export async function fetchLogs(mode: string, token: string): Promise<LogRow[]> {
  const modeUp = mode.toUpperCase();
  const tokenLower = token.toLowerCase();
  const url = `${API_BASE_URL}/logs/${modeUp}/${tokenLower}`;

  try {
    const res = await fetchWithTimeout(url, { method: "GET" });

    if (!res.ok) {
      throw new Error(`HTTP ${res.status} ${res.statusText}`);
    }

    if (isJsonContent(res)) {
      const data: any = await res.json();
      if (Array.isArray(data)) return data as LogRow[];
      if (Array.isArray(data.logs)) return data.logs as LogRow[];
      return [];
    } else {
      const text = await res.text();
      return parseCSV(text);
    }
  } catch (err) {
    console.error("fetchLogs failed, returning []", err);
    return [];
  }
}

// =========================
// getSignalEvaluation: /logs/EVALUATED/{token}
// =========================

export async function getSignalEvaluation(
  token: string,
  signalTimestamp: string
): Promise<SignalEvaluation | null> {
  const tokenLower = token.toLowerCase();
  const url = `${API_BASE_URL}/logs/EVALUATED/${tokenLower}`;

  try {
    const res = await fetchWithTimeout(url, { method: "GET" });

    if (!res.ok) {
      throw new Error(`HTTP ${res.status} ${res.statusText}`);
    }

    let rows: LogRow[] = [];
    if (isJsonContent(res)) {
      const data: any = await res.json();
      if (Array.isArray(data)) rows = data as LogRow[];
      else if (Array.isArray(data.logs)) rows = data.logs as LogRow[];
    } else {
      const text = await res.text();
      rows = parseCSV(text);
    }

    const match = rows.find((r) => {
      const ts = (r["signal_ts"] as string) || (r["timestamp"] as string);
      return ts === signalTimestamp;
    });

    if (!match) return null;

    const rawResult = String(match["result"] ?? match["status"] ?? "").toUpperCase();

    let status: SignalEvaluation["status"] = "BE";
    if (rawResult.includes("WIN") || rawResult.includes("TP")) status = "WIN";
    else if (rawResult.includes("LOSS") || rawResult.includes("SL")) status = "LOSS";

    const exitPriceStr =
      (match["exit_price"] as string) ||
      (match["price_at_eval"] as string) ||
      (match["tp"] as string) ||
      (match["sl"] as string) ||
      "";
    const exit_price = exitPriceStr ? Number(exitPriceStr) : NaN;

    const closed_at =
      (match["evaluated_at"] as string) ||
      (match["closed_at"] as string) ||
      (match["timestamp"] as string) ||
      new Date().toISOString();

    let pnl_r = 0;
    if (match["pnl_r"] != null) {
      pnl_r = Number(match["pnl_r"]);
    } else if (match["move_pct"] != null) {
      const mv = Number(match["move_pct"]);
      if (!Number.isNaN(mv)) pnl_r = mv / 100;
    }

    return {
      status,
      pnl_r,
      exit_price,
      closed_at,
    };
  } catch (err) {
    console.error("getSignalEvaluation failed, returning null", err);
    return null;
  }
}

// =========================
// Telegram / Leaderboard / AdvisorChat
// =========================

export async function notifyTelegram(message: string): Promise<boolean> {
  try {
    const res = await fetchWithTimeout(`${API_BASE_URL}/notify/telegram`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text: message }),
    });

    if (!res.ok) {
      throw new Error(`HTTP ${res.status} ${res.statusText}`);
    }

    return true;
  } catch (err) {
    console.warn("notifyTelegram failed", err);
    return false;
  }
}

const MOCK_LEADERBOARD: LeaderboardEntry[] = [
  {
    rank: 1,
    user_name: "AlphaSeeker",
    avatar_url: "https://ui-avatars.com/api/?name=AS&background=ffd700&color=000",
    win_rate: 78,
    total_pnl: 45.2,
    signals_tracked: 124,
  },
  {
    rank: 2,
    user_name: "CryptoWhale",
    avatar_url: "https://ui-avatars.com/api/?name=CW&background=c0c0c0&color=000",
    win_rate: 72,
    total_pnl: 38.5,
    signals_tracked: 98,
  },
  {
    rank: 3,
    user_name: "SatoshiDisciple",
    avatar_url: "https://ui-avatars.com/api/?name=SD&background=cd7f32&color=000",
    win_rate: 68,
    total_pnl: 32.1,
    signals_tracked: 156,
  },
  {
    rank: 4,
    user_name: "Pancho Trader",
    avatar_url:
      "https://ui-avatars.com/api/?name=Pancho+Trader&background=10b981&color=fff",
    win_rate: 65,
    total_pnl: 28.4,
    signals_tracked: 42,
    is_current_user: true,
  },
  {
    rank: 5,
    user_name: "MoonBoy23",
    avatar_url: "https://ui-avatars.com/api/?name=MB&background=334155&color=fff",
    win_rate: 55,
    total_pnl: 12.8,
    signals_tracked: 210,
  },
];

export async function fetchLeaderboard(): Promise<LeaderboardEntry[]> {
  // De momento 100 % mock; listo para conectar a backend cuando quieras.
  return new Promise((resolve) => setTimeout(() => resolve(MOCK_LEADERBOARD), 600));
}

// Chat del Advisor (demo-friendly)
// - Primer mensaje: usa analyzeAdvisor y devuelve un ChatMessage tipo "analysis"
// - Mensajes siguientes: llama a /analyze/advisor/chat
export async function sendAdvisorChat(
  history: ChatMessage[],
  context: any
): Promise<ChatMessage> {
  // Mensaje inicial: hacemos un análisis completo
  if (!history.length) {
    const analysis = await analyzeAdvisor(context);
    return {
      id: Date.now().toString(),
      role: "assistant",
      content: `I've analyzed your proposed ${context.token} ${context.direction} position. Here is my risk assessment.`,
      type: "analysis",
      data: analysis,
      timestamp: new Date().toISOString(),
    };
  }

  // Mensajes siguientes: endpoint de chat real
  try {
    const body = {
      history: history.map((m) => ({ role: m.role, content: m.content })),
      context,
    };

    const res = await fetchWithTimeout(
      `${API_BASE_URL}/analyze/advisor/chat`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      },
      60000
    );

    if (!res.ok) {
      throw new Error(`HTTP ${res.status} ${res.statusText}`);
    }

    const data: any = isJsonContent(res) ? await res.json() : await res.text();
    const content =
      typeof data === "string"
        ? data
        : data.message ?? data.reply ?? "Advisor reply received.";

    return {
      id: Date.now().toString(),
      role: "assistant",
      content,
      type: "text",
      timestamp: new Date().toISOString(),
    };
  } catch (err) {
    console.error("sendAdvisorChat failed", err);
    return {
      id: Date.now().toString(),
      role: "assistant",
      content:
        "I'm having trouble reaching the advisor backend right now. Please try again later.",
      type: "text",
      timestamp: new Date().toISOString(),
    };
  }
}

// =========================
// Auth API
// =========================

export async function login(email: string, password: string): Promise<any> {
  const formData = new URLSearchParams();
  formData.append('username', email);
  formData.append('password', password);

  const res = await fetchWithTimeout(`${API_BASE_URL}/auth/token`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
    body: formData.toString(),
  });

  if (!res.ok) {
    throw new Error(`Login failed: ${res.statusText}`);
  }

  return res.json();
}

export async function register(email: string, password: string, name?: string): Promise<any> {
  const res = await fetchWithTimeout(`${API_BASE_URL}/auth/register?email=${encodeURIComponent(email)}&password=${encodeURIComponent(password)}&name=${encodeURIComponent(name || 'Trader')}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' }
  });

  if (!res.ok) throw new Error('Registration failed');
  return res.json();
}

export async function getMe(): Promise<UserProfile['user']> {
  const res = await fetchWithTimeout(`${API_BASE_URL}/auth/users/me`, {
    method: 'GET'
  });

  if (!res.ok) throw new Error('Failed to fetch user profile');
  return res.json();
}


// =========================
// API pública agrupada
// =========================

export async function fetchMarketplace(): Promise<any[]> {
  try {
    const res = await fetchWithTimeout(`${API_BASE_URL}/strategies/marketplace`, {
      method: 'GET'
    });
    if (!res.ok) throw new Error('Failed to fetch marketplace');
    return res.json();
  } catch (err) {
    console.warn("fetchMarketplace failed", err);
    return [];
  }
}

export const api = {
  analyzeLite,
  analyzePro,
  analyzeAdvisor,
  fetchLogs,
  getSignalEvaluation,
  notifyTelegram,
  fetchLeaderboard,
  sendAdvisorChat,
  login,
  register,
  getMe,
  fetchMarketplace
};
