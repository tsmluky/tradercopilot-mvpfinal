// constants.ts
// Config global de TraderCopilot Web (frontend Vite+React)

export const API_BASE_URL: string =
  (import.meta as any).env?.VITE_API_BASE_URL ??
  "http://127.0.0.1:8010";

// === Tokens soportados ===

export type Token = "eth" | "btc" | "sol" | "xau";

export interface TokenMeta {
  id: Token;
  symbol: string;
  name: string;
}

export const TOKENS: TokenMeta[] = [
  { id: "eth", symbol: "ETH", name: "Ethereum" },
  { id: "btc", symbol: "BTC", name: "Bitcoin" },
  { id: "sol", symbol: "SOL", name: "Solana" },
  { id: "xau", symbol: "XAU", name: "Gold (XAUUSD)" },
];

// Etiquetas opcionales por si las necesitas en otros sitios
export const TOKEN_LABELS: Record<Token, string> = {
  eth: "ETH · Ethereum",
  btc: "BTC · Bitcoin",
  sol: "SOL · Solana",
  xau: "XAU · Oro",
};

// === Timeframes ===

export const TIMEFRAMES: string[] = ["15m", "30m", "1h", "4h", "1d"];
