import React, { useState, useEffect } from "react";
import { analyzeLite, analyzePro, getOHLCV } from "../services/api";
import type { SignalLite, ProResponse } from "../types";
import { ProAnalysisViewer } from "../components/ProAnalysisViewer";
import { Copy, Check, Share2, Sparkles, BarChart2, MessageCircle } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { ThinkingOverlay } from "../components/ThinkingOverlay";
import { SignalChart } from "../components/SignalChart";
import { formatPrice } from "../utils/format";

type Mode = "LITE" | "PRO";

const TOKENS = ["BTC", "ETH", "SOL", "XRP", "BNB", "DOGE", "ADA", "AVAX", "DOT", "LINK", "LTC", "MATIC", "UNI", "ATOM", "NEAR"];
const TIMEFRAMES = ["1h", "4h", "1d"] as const;

export const AnalysisPage: React.FC = () => {
  const navigate = useNavigate();
  const { userProfile } = useAuth();
  const availableTokens = userProfile?.user.allowed_tokens && userProfile.user.allowed_tokens.length > 0
    ? userProfile.user.allowed_tokens
    : TOKENS;

  const [mode, setMode] = useState<Mode>("LITE");
  const [token, setToken] = useState<string>(availableTokens[0] || "ETH");
  const [timeframe, setTimeframe] = useState<string>("4h");

  // Reset token if list changes
  useEffect(() => {
    if (availableTokens.length > 0 && !availableTokens.includes(token)) {
      setToken(availableTokens[0]);
    }
  }, [availableTokens]);

  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [liteResult, setLiteResult] = useState<SignalLite | null>(null);

  // Pro Result & Streaming state
  const [proResult, setProResult] = useState<ProResponse | null>(null);
  const [streamedRaw, setStreamedRaw] = useState<string>("");
  const [isStreaming, setIsStreaming] = useState(false);

  // Chart Data
  const [chartData, setChartData] = useState<any[]>([]);

  const [liteCopied, setLiteCopied] = useState(false);

  // Streaming Effect Hook
  useEffect(() => {
    if (proResult && proResult.raw) {
      setStreamedRaw("");
      setIsStreaming(true);
      let i = 0;
      const fullText = proResult.raw;

      // Speed: 5ms per char = very fast typewriter
      const interval = setInterval(() => {
        setStreamedRaw((prev) => fullText.slice(0, i + 5)); // Batch 5 chars for performance
        i += 5;
        if (i >= fullText.length) {
          clearInterval(interval);
          setIsStreaming(false);
          setStreamedRaw(fullText);
        }
      }, 10);

      return () => clearInterval(interval);
    }
  }, [proResult]);

  async function handleGenerate() {
    setError(null);
    setIsLoading(true);
    setLiteResult(null);
    setProResult(null);
    setStreamedRaw("");
    setChartData([]);

    try {
      // 1. Fetch Chart Data in Parallel (for visualization)
      const dataPromise = getOHLCV(token, timeframe);

      if (mode === "LITE") {
        // QUICK mode uses standard loading
        const [signal, ohlcv] = await Promise.all([
          analyzeLite(token, timeframe),
          dataPromise
        ]);
        setLiteResult(signal);
        setChartData(ohlcv);

      } else {
        // PRO mode
        const [signal, ohlcv] = await Promise.all([
          analyzePro(token, timeframe, true),
          dataPromise
        ]);
        setProResult(signal);
        setChartData(ohlcv);
      }
    } catch (err: any) {
      console.error("Error generating analysis", err);
      setError(err?.message ?? "Error generating analysis");
    } finally {
      setIsLoading(false);
    }
  }

  const handleCopyLite = () => {
    if (!liteResult) return;
    const text = `⚡ *TRADER COPILOT LITE* ⚡\n` +
      `Asset: ${liteResult.token}\n` +
      `Signal: ${liteResult.direction} (Confidence: ${(liteResult.confidence * 100).toFixed(0)}%)\n` +
      `Entry: ${liteResult.entry}\n` +
      `TP: ${liteResult.tp}\n` +
      `SL: ${liteResult.sl}\n\n` +
      `Rationale: ${liteResult.rationale}`;

    navigator.clipboard.writeText(text);
    setLiteCopied(true);
    setTimeout(() => setLiteCopied(false), 2000);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col gap-2">
        <h1 className="text-2xl font-semibold text-slate-50 flex items-center gap-2">
          <Sparkles className="w-6 h-6 text-indigo-400" />
          AI Analysis Hub
        </h1>
        <p className="text-slate-400 text-sm">
          Select your asset and let our Multi-Agent AI analyze market structure, on-chain data, and global sentiment.
        </p>
      </div>

      {/* Config Card */}
      <div className="bg-slate-900/70 border border-slate-800 rounded-2xl p-5 flex flex-col gap-4 shadow-xl backdrop-blur-sm">
        {/* Mode toggle */}
        <div className="flex gap-3">
          {(["LITE", "PRO"] as Mode[]).map((m) => (
            <button
              key={m}
              type="button"
              onClick={() => setMode(m)}
              className={`px-4 py-2 rounded-full text-sm font-medium border transition-all duration-300
                ${mode === m
                  ? "bg-indigo-600 text-white border-indigo-500 shadow-lg shadow-indigo-500/20 scale-105"
                  : "bg-slate-950 text-slate-400 border-slate-800 hover:border-slate-600"
                }`}
            >
              {m === "LITE" ? "⚡ LITE Signal" : "🧠 PRO Deep Analysis"}
            </button>
          ))}
        </div>

        {/* Inputs */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <div className="flex flex-col gap-1">
            <label className="text-[10px] font-bold text-slate-500 uppercase tracking-wider">
              Asset
            </label>
            <select
              value={token}
              onChange={(e) => setToken(e.target.value)}
              className="bg-slate-950 border border-slate-800 rounded-xl px-4 py-3 text-sm text-slate-200 focus:outline-none focus:ring-2 focus:ring-indigo-500/50 appearance-none font-medium transition-shadow"
            >
              {availableTokens.map((t) => (
                <option key={t} value={t}>
                  {t}
                </option>
              ))}
            </select>
          </div>

          <div className="flex flex-col gap-1">
            <label className="text-[10px] font-bold text-slate-500 uppercase tracking-wider">
              Timeframe
            </label>
            <select
              value={timeframe}
              onChange={(e) => setTimeframe(e.target.value)}
              className="bg-slate-950 border border-slate-800 rounded-xl px-4 py-3 text-sm text-slate-200 focus:outline-none focus:ring-2 focus:ring-indigo-500/50 appearance-none font-medium transition-shadow"
            >
              {TIMEFRAMES.map((tf) => (
                <option key={tf} value={tf}>
                  {tf}
                </option>
              ))}
            </select>
          </div>

          <div className="flex items-end">
            <button
              type="button"
              onClick={handleGenerate}
              disabled={isLoading || isStreaming}
              className="w-full h-[46px] inline-flex items-center justify-center px-4 rounded-xl text-sm font-bold text-white uppercase tracking-wide
                bg-gradient-to-r from-indigo-600 to-indigo-500 hover:from-indigo-500 hover:to-indigo-400
                disabled:opacity-50 disabled:cursor-not-allowed
                transition-all shadow-lg hover:shadow-indigo-500/25 active:scale-95"
            >
              {isLoading
                ? "Connecting to Quant Brain..."
                : isStreaming
                  ? "Streaming Analysis..."
                  : "Start Analysis"}
            </button>
          </div>
        </div>

        {error && (
          <div className="text-sm text-rose-400 bg-rose-950/20 border border-rose-900/50 rounded-lg px-4 py-3 flex items-center gap-2 animate-in fade-in">
            <div className="w-2 h-2 bg-rose-500 rounded-full animate-pulse" />
            {error}
          </div>
        )}
      </div>

      {/* Thinking State */}
      {isLoading && <ThinkingOverlay />}

      {/* Result Card */}
      {!isLoading && (
        <div className="bg-slate-900/40 border border-slate-800/50 rounded-3xl p-6 min-h-[300px]">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-lg font-semibold text-slate-200 flex items-center gap-2">
              Analysis Result
              {isStreaming && <span className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse" />}
            </h2>
            {mode === "LITE" && liteResult && (
              <div className="flex gap-2">
                <button
                  onClick={() => navigate('/advisor', {
                    state: {
                      context: {
                        token: liteResult.token,
                        direction: liteResult.direction,
                        entry: liteResult.entry,
                        tp: liteResult.tp,
                        sl: liteResult.sl,
                        timeframe: liteResult.timeframe
                      }
                    }
                  })}
                  className="text-xs flex items-center gap-1.5 px-3 py-1.5 bg-indigo-600 hover:bg-indigo-500 rounded-lg text-white transition-colors shadow-lg shadow-indigo-500/20"
                >
                  <MessageCircle size={14} />
                  Discuss
                </button>
                <button
                  onClick={handleCopyLite}
                  className="text-xs flex items-center gap-1.5 px-3 py-1.5 bg-slate-800 hover:bg-slate-700 rounded-lg text-slate-300 transition-colors border border-slate-700"
                >
                  {liteCopied ? <Check size={14} className="text-emerald-400" /> : <Copy size={14} />}
                  {liteCopied ? "Copied" : "Copy"}
                </button>
              </div>
            )}
          </div>

          {!liteResult && !proResult && !error && (
            <div className="flex flex-col items-center justify-center py-20 text-slate-600 space-y-4">
              <div className="w-16 h-16 rounded-full bg-slate-900/50 flex items-center justify-center border border-slate-800">
                <Sparkles className="w-6 h-6 text-slate-700" />
              </div>
              <p className="text-sm font-medium">Ready to analyze the market.</p>
            </div>
          )}

          {mode === "LITE" && liteResult && (
            <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700">
              {/* Header / Meta */}
              <div className="flex items-center justify-between p-5 bg-gradient-to-br from-slate-800/50 to-slate-900/50 rounded-2xl border border-slate-700/50 backdrop-blur-md">
                <div className="flex items-center gap-4">
                  <div className="w-12 h-12 rounded-xl bg-indigo-500/10 flex items-center justify-center border border-indigo-500/20 shadow-inner">
                    <span className="font-bold text-lg text-indigo-400">{liteResult.token}</span>
                  </div>
                  <div>
                    <div className="flex items-center gap-2 mb-1">
                      <span className={`px-2.5 py-1 rounded-md text-[10px] font-bold uppercase tracking-wider border shadow-sm ${liteResult.direction.toLowerCase() === "long"
                        ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/30 shadow-emerald-900/20"
                        : "bg-rose-500/10 text-rose-400 border-rose-500/30 shadow-rose-900/20"
                        }`}>
                        {liteResult.direction}
                      </span>
                      <span className="text-xs text-slate-400 font-mono border border-slate-700/50 px-2 py-1 rounded-md">
                        {liteResult.timeframe}
                      </span>
                    </div>
                    <span className="text-xs text-slate-500 font-medium">
                      Generated {new Date(liteResult.timestamp).toLocaleTimeString()}
                    </span>
                  </div>
                </div>

                {/* Confidence Ring */}
                <div className="text-right">
                  <div className="text-[10px] text-slate-500 uppercase tracking-wider font-bold mb-1">Confidence Score</div>
                  <div className={`text-2xl font-black tracking-tight ${liteResult.confidence >= 0.8 ? 'text-emerald-400 drop-shadow-sm' :
                    liteResult.confidence >= 0.6 ? 'text-amber-400' : 'text-slate-400'
                    }`}>
                    {(liteResult.confidence * 100).toFixed(0)}%
                  </div>
                </div>
              </div>


              {/* Chart Block */}
              {chartData.length > 0 && (
                <div className="animate-in fade-in duration-700 delay-150">
                  <div className="flex items-center gap-2 mb-2 text-xs font-bold text-slate-500 uppercase tracking-widest">
                    <BarChart2 size={12} className="text-indigo-500" />
                    Live Market Context
                  </div>
                  <SignalChart
                    data={chartData}
                    entry={liteResult.entry}
                    tp={liteResult.tp}
                    sl={liteResult.sl}
                    direction={liteResult.direction}
                  />
                </div>
              )}

              {/* Execution Block */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {/* Entry */}
                <div className="p-5 bg-slate-950/40 rounded-2xl border border-slate-800/50 flex flex-col items-center justify-center text-center group hover:border-indigo-500/30 transition-all hover:bg-slate-900/60">
                  <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wider mb-2 group-hover:text-indigo-400 transition-colors">Entry Zone</span>
                  <span className="text-2xl font-mono text-slate-100 font-bold group-hover:scale-105 transition-transform">
                    {formatPrice(liteResult.entry)}
                  </span>
                </div>

                {/* Take Profit */}
                <div className="p-5 bg-emerald-950/10 rounded-2xl border border-emerald-900/30 flex flex-col items-center justify-center text-center group hover:border-emerald-500/30 transition-all hover:bg-emerald-950/20">
                  <span className="text-[10px] font-bold text-emerald-600/70 uppercase tracking-wider mb-2 group-hover:text-emerald-500 transition-colors">Take Profit</span>
                  <span className="text-2xl font-mono text-emerald-400 font-bold group-hover:scale-105 transition-transform">
                    {formatPrice(liteResult.tp)}
                  </span>
                </div>

                {/* Stop Loss */}
                <div className="p-5 bg-rose-950/10 rounded-2xl border border-rose-900/30 flex flex-col items-center justify-center text-center group hover:border-rose-500/30 transition-all hover:bg-rose-950/20">
                  <span className="text-[10px] font-bold text-rose-600/70 uppercase tracking-wider mb-2 group-hover:text-rose-500 transition-colors">Stop Loss</span>
                  <span className="text-2xl font-mono text-rose-400 font-bold group-hover:scale-105 transition-transform">
                    {formatPrice(liteResult.sl)}
                  </span>
                </div>
              </div>

              {/* Rationale Section */}
              <div className="p-6 bg-slate-950/30 rounded-2xl border border-slate-800 relative overflow-hidden">
                <div className="absolute top-0 left-0 w-1 h-full bg-gradient-to-b from-indigo-500 to-indigo-900"></div>
                <h3 className="text-xs font-bold text-indigo-400 uppercase tracking-wider mb-4 flex items-center gap-2">
                  <Sparkles size={14} className="text-indigo-500" />
                  AI Reasoning
                </h3>
                <p className="text-slate-300 text-sm leading-7 font-light tracking-wide">
                  {liteResult.rationale}
                </p>
              </div>
            </div>
          )}

          {mode === "PRO" && (
            <ProAnalysisViewer raw={streamedRaw} token={token} />
          )}
        </div>
      )}
    </div>
  );
};
