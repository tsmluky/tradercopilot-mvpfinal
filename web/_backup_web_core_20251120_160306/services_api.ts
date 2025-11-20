import { API_BASE_URL, MOCK_LITE_SIGNAL, MOCK_PRO_RESPONSE, MOCK_ADVISOR_RESPONSE } from '../constants';
import {
  SignalLite,
  ProResponse,
  AdvisorResponse,
  SignalEvaluation,
  LogRow,
  LeaderboardEntry,
  ChatMessage,
  AnalysisMode,
} from '../types';

// =========================
// Helpers HTTP básicos
// =========================

const DEFAULT_TIMEOUT_MS = 5000;

async function fetchWithTimeout(
  url: string,
  init: RequestInit = {},
  timeoutMs: number = DEFAULT_TIMEOUT_MS
): Promise<Response> {
  const controller = new AbortController();
  const id = setTimeout(() => controller.abort(), timeoutMs);

  try {
    const res = await fetch(url, { ...init, signal: controller.signal });
    return res;
  } finally {
    clearTimeout(id);
  }
}

function isJsonContent(res: Response): boolean {
  const ct = res.headers.get('content-type') || '';
  return ct.toLowerCase().includes('application/json');
}

// CSV -> LogRow[]
const parseCSV = (csvText: string): LogRow[] => {
  if (!csvText) return [];
  const lines = csvText.trim().split(/\r?\n/);
  if (lines.length < 2) return [];

  const headers = lines[0].split(',').map((h) => h.trim());
  const result: LogRow[] = [];

  for (let i = 1; i < lines.length; i++) {
    const line = lines[i].trim();
    if (!line) continue;
    const cols = line.split(',');
    const row: LogRow = {};
    for (let j = 0; j < headers.length; j++) {
      row[headers[j]] = (cols[j] ?? '').trim();
    }
    result.push(row);
  }
  return result;
};

// =========================
// Análisis LITE / PRO / ADVISOR
// =========================

async function analyzeLite(token: string, timeframe: string): Promise<SignalLite> {
  const body = { token, timeframe };

  try {
    const res = await fetchWithTimeout(`${API_BASE_URL}/analyze/lite`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });

    if (!res.ok) {
      throw new Error(`HTTP ${res.status} ${res.statusText}`);
    }

    return (await res.json()) as SignalLite;
  } catch (err) {
    console.warn('analyzeLite failed, using mock', err);
    // Garantizamos timestamp fresco para features tipo "30s expiry"
    const freshMock: SignalLite = {
      ...(MOCK_LITE_SIGNAL as SignalLite),
      token: token.toUpperCase(),
      timeframe,
      timestamp: new Date().toISOString(),
    };
    return freshMock;
  }
}

async function analyzePro(
  token: string,
  timeframe: string,
  rag: boolean
): Promise<ProResponse> {
  const body = { token, timeframe, context: { rag } };

  try {
    const res = await fetchWithTimeout(`${API_BASE_URL}/analyze/pro`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });

    if (!res.ok) {
      throw new Error(`HTTP ${res.status} ${res.statusText}`);
    }

    const data: any = isJsonContent(res) ? await res.json() : await res.text();
    const raw =
      typeof data === 'string'
        ? data
        : data.analysis ?? data.raw ?? JSON.stringify(data, null, 2);

    // ProResponse está pensado para tener al menos raw, el viewer se encarga del parse.
    return { raw } as ProResponse;
  } catch (err) {
    console.warn('analyzePro failed, using mock', err);
    return { raw: MOCK_PRO_RESPONSE } as ProResponse;
  }
}

type AdvisorPayload = {
  token: string;
  direction: 'long' | 'short';
  entry: number;
  tp: number;
  sl: number;
  size_quote: number;
};

async function analyzeAdvisor(payload: AdvisorPayload): Promise<AdvisorResponse> {
  try {
    const res = await fetchWithTimeout(`${API_BASE_URL}/analyze/advisor`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });

    if (!res.ok) {
      throw new Error(`HTTP ${res.status} ${res.statusText}`);
    }

    return (await res.json()) as AdvisorResponse;
  } catch (err) {
    console.warn('analyzeAdvisor failed, using mock', err);
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
// Devuelve siempre LogRow[] (independiente de JSON o CSV)
// =========================

async function fetchLogs(mode: string, token: string): Promise<LogRow[]> {
  const modeUp = mode.toUpperCase();
  const tokenLower = token.toLowerCase();
  const url = `${API_BASE_URL}/logs/${modeUp}/${tokenLower}`;

  try {
    const res = await fetchWithTimeout(url, { method: 'GET' });

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
    console.warn('fetchLogs failed, using mock CSV', err);
    // Fallback muy simple: unas pocas líneas mock (puedes ajustar o borrar si no quieres mocks aquí)
    const MOCK_CSV_EVALUATED = `signal_ts,evaluated_at,token,timeframe,entry,tp,sl,price_at_eval,result,move_pct
2023-11-16T10:00:00Z,2023-11-16T14:00:00Z,ETH,30m,3650.00,3700.00,3620.00,3705.00,WIN,+1.5%
2023-11-16T11:00:00Z,2023-11-16T15:00:00Z,BTC,1h,96000.00,98000.00,95000.00,94800.00,LOSS,-1.2%`;
    const MOCK_CSV_LITE = `timestamp,token,timeframe,direction,entry,confidence
2023-11-16T10:00:00Z,ETH,30m,long,3650.00,0.75
2023-11-16T11:00:00Z,BTC,1h,long,96000.00,0.65`;

    const csv = modeUp === 'EVALUATED' ? MOCK_CSV_EVALUATED : MOCK_CSV_LITE;
    return parseCSV(csv);
  }
}

// =========================
// getSignalEvaluation: busca una evaluación real para una señal concreta
// Usa /logs/EVALUATED/{token} y mapea a SignalEvaluation (UI)
// =========================

async function getSignalEvaluation(
  token: string,
  signalTimestamp: string
): Promise<SignalEvaluation | null> {
  const tokenLower = token.toLowerCase();
  const url = `${API_BASE_URL}/logs/EVALUATED/${tokenLower}`;

  try {
    const res = await fetchWithTimeout(url, { method: 'GET' });

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

    if (!rows.length) return null;

    const match = rows.find((r) => {
      const ts = (r.signal_ts as string) || (r.timestamp as string);
      return ts === signalTimestamp;
    });

    if (!match) return null;

    const rawResult = String(
      match.result ?? match.status ?? ''
    ).toUpperCase();

    let status: SignalEvaluation['status'] = 'BE';
    if (rawResult.includes('WIN') || rawResult.includes('TP')) status = 'WIN';
    else if (rawResult.includes('LOSS') || rawResult.includes('SL')) status = 'LOSS';

    const exitPriceStr =
      (match.exit_price as string) ||
      (match.price_at_eval as string) ||
      (match.tp as string) ||
      (match.sl as string) ||
      '';
    const exit_price = exitPriceStr ? Number(exitPriceStr) : NaN;

    const closed_at =
      (match.evaluated_at as string) ||
      (match.closed_at as string) ||
      (match.timestamp as string) ||
      new Date().toISOString();

    let pnl_r = 0;
    if (match.pnl_r != null) {
      pnl_r = Number(match.pnl_r);
    } else if (match.move_pct != null) {
      const mv = Number(match.move_pct);
      if (!Number.isNaN(mv)) pnl_r = mv / 100; // aproximación básica
    }

    return {
      status,
      pnl_r,
      exit_price,
      closed_at,
    };
  } catch (err) {
    console.error('getSignalEvaluation failed, returning null', err);
    return null;
  }
}

// =========================
// Telegram / Leaderboard / AdvisorChat (demo-friendly)
// =========================

async function notifyTelegram(message: string): Promise<boolean> {
  try {
    const res = await fetchWithTimeout(`${API_BASE_URL}/notify/telegram`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text: message }),
    });

    if (!res.ok) {
      throw new Error(`HTTP ${res.status} ${res.statusText}`);
    }

    return true;
  } catch (err) {
    console.warn('notifyTelegram failed', err);
    return false;
  }
}

// Demo leaderboards (mock por ahora)
const MOCK_LEADERBOARD: LeaderboardEntry[] = [
  {
    rank: 1,
    user_name: 'AlphaSeeker',
    avatar_url: 'https://ui-avatars.com/api/?name=AS&background=ffd700&color=000',
    win_rate: 78,
    total_pnl: 45.2,
    signals_tracked: 124,
  },
  {
    rank: 2,
    user_name: 'CryptoWhale',
    avatar_url: 'https://ui-avatars.com/api/?name=CW&background=c0c0c0&color=000',
    win_rate: 72,
    total_pnl: 38.5,
    signals_tracked: 98,
  },
  {
    rank: 3,
    user_name: 'SatoshiDisciple',
    avatar_url: 'https://ui-avatars.com/api/?name=SD&background=cd7f32&color=000',
    win_rate: 68,
    total_pnl: 32.1,
    signals_tracked: 156,
  },
  {
    rank: 4,
    user_name: 'Pancho Trader',
    avatar_url:
      'https://ui-avatars.com/api/?name=Pancho+Trader&background=10b981&color=fff',
    win_rate: 65,
    total_pnl: 28.4,
    signals_tracked: 42,
    is_current_user: true,
  },
  {
    rank: 5,
    user_name: 'MoonBoy23',
    avatar_url: 'https://ui-avatars.com/api/?name=MB&background=334155&color=fff',
    win_rate: 55,
    total_pnl: 12.8,
    signals_tracked: 210,
  },
];

async function fetchLeaderboard(): Promise<LeaderboardEntry[]> {
  // Por ahora es 100% mock, listo para conectar a backend cuando quieras.
  return new Promise((resolve) => setTimeout(() => resolve(MOCK_LEADERBOARD), 600));
}

// Chat del Advisor en modo demo (no toca backend, sólo usa analyzeAdvisor al inicio)
async function sendAdvisorChat(
  history: ChatMessage[],
  context: any
): Promise<ChatMessage> {
  await new Promise((resolve) => setTimeout(resolve, 600));

  const lastMsg = history[history.length - 1];

  if (!history.length) {
    // Mensaje inicial: genera análisis con analyzeAdvisor
    const analysis = await analyzeAdvisor(context);
    return {
      id: Date.now().toString(),
      role: 'assistant',
      content: `I've analyzed your proposed ${context.token} ${context.direction} position. Here is my risk assessment.`,
      type: 'analysis',
      data: analysis,
      timestamp: new Date().toISOString(),
    };
  }

  const text = (lastMsg.content || '').toLowerCase();
  let responseText = '';

  if (text.includes('risk') || text.includes('riesgo')) {
    responseText = `To reduce the risk on this ${context.token} trade, consider reducing your position size by 30% or waiting for a retest of ${
      context.entry * 0.98
    }. Current volatility is high.`;
  } else if (text.includes('stop') || text.includes('sl')) {
    responseText = `Your current SL is aggressive. A wider stop around ${
      context.entry * 0.95
    } would avoid noise, but requires smaller size to maintain risk limits.`;
  } else if (text.includes('tp') || text.includes('target')) {
    responseText = `The upside potential is limited by resistance at ${
      context.entry * 1.05
    }. I recommend taking partial profits at 1.5R.`;
  } else {
    responseText = `Understood. Based on the current market structure for ${context.token}, I advise patience. Do you want me to recalculate scenarios?`;
  }

  return {
    id: Date.now().toString(),
    role: 'assistant',
    content: responseText,
    type: 'text',
    timestamp: new Date().toISOString(),
  };
}

// =========================
// API pública
// =========================

export const api = {
  analyzeLite,
  analyzePro,
  analyzeAdvisor,
  fetchLogs,
  getSignalEvaluation,
  notifyTelegram,
  fetchLeaderboard,
  sendAdvisorChat,
};
