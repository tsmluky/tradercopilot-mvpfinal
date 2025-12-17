import React, { useState, useEffect } from "react";
import { analyzeLite, analyzePro, getOHLCV } from "../services/api";
import type { SignalLite, ProResponse } from "../types";
import { ProAnalysisViewer } from "../components/ProAnalysisViewer";
import { Sparkles } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { ThinkingOverlay } from "../components/ThinkingOverlay";
import { SignalCard } from "../components/SignalCard";
import { TokenSelector } from "../components/TokenSelector";
import { SignalChart } from "../components/SignalChart"; // Still needed? SignalCard doesn't have chart built-in? 
// Wait, SignalCard DOES NOT have chart built-in in the code I viewed. It has RR bar.
// I need to check SignalCard again.
// Viewed SignalCard.tsx: It does NOT have the chart. 
// However, the AnalysisPage has a "LIVE MARKET CONTEXT" chart.
// The user request was "Tracking button". `SignalCard` has it.
// I should render `SignalChart` AND `SignalCard` (for the metrics/tracking).
// The `SignalCard` in `AnalysisPage` will replace the "Execution Block" and "Rationale Section".

type Mode = "LITE" | "PRO";

const DEFAULT_TOKENS = ["BTC", "ETH", "SOL"];
const TIMEFRAMES = ["1h", "4h", "1d"] as const;

export const AnalysisPage: React.FC = () => {
  const navigate = useNavigate();
  const { userProfile } = useAuth();

  // Clean tokens list
  const availableTokens = userProfile?.user.allowed_tokens && userProfile.user.allowed_tokens.length > 0
    ? userProfile.user.allowed_tokens
    : DEFAULT_TOKENS;

  const [mode, setMode] = useState<Mode>("LITE");
  const [token, setToken] = useState<string>(availableTokens[0] || "ETH");
  const [timeframe, setTimeframe] = useState<string>("4h");

  // Reset token if list changes and current not in list (safety)
  useEffect(() => {
    if (availableTokens.length > 0 && !availableTokens.includes(token)) {
      // If current token is invalid for new list, reset.
      // But if I want to allow searching ANY token maybe I shouldn't restrict strict equality?
      // For now, strict is safer for entitlements.
      setToken(availableTokens[0]);
    }
  }, [availableTokens, userProfile]); // Check dependency

  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [liteResult, setLiteResult] = useState<SignalLite | null>(null);

  // Pro Result & Streaming state
  const [proResult, setProResult] = useState<ProResponse | null>(null);
  const [streamedRaw, setStreamedRaw] = useState<string>("");
  const [isStreaming, setIsStreaming] = useState(false);

  // Chart Data
  const [chartData, setChartData] = useState<any[]>([]);

  // Streaming Effect Hook
  useEffect(() => {
    if (proResult && proResult.raw) {
      setStreamedRaw("");
      setIsStreaming(true);
      let i = 0;
      const fullText = proResult.raw;

      const interval = setInterval(() => {
        setStreamedRaw((prev) => fullText.slice(0, i + 5));
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
      const dataPromise = getOHLCV(token, timeframe);

      if (mode === "LITE") {
        const [signal, ohlcv] = await Promise.all([
          analyzeLite(token, timeframe),
          dataPromise
        ]);
        setLiteResult(signal);
        setChartData(ohlcv);

      } else {
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
          <div className="flex flex-col gap-1 relative z-20">
            <label className="text-[10px] font-bold text-slate-500 uppercase tracking-wider">
              Asset
            </label>
            <TokenSelector
              value={token}
              onChange={setToken}
              availableTokens={availableTokens}
              isProUser={mode === "PRO" || userProfile?.user.subscription_status !== 'free'}
            />
          </div>

          <div className="flex flex-col gap-1 z-10">
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

          <div className="flex items-end z-10">
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
            <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-700">

              {/* 1. Chart (Context) - Kept separate as SignalCard doesn't have it */}
              {chartData.length > 0 && (
                <div className="p-4 bg-slate-950/30 rounded-2xl border border-slate-800">
                  <SignalChart
                    data={chartData}
                    entry={liteResult.entry}
                    tp={liteResult.tp}
                    sl={liteResult.sl}
                    direction={liteResult.direction}
                  />
                </div>
              )}

              {/* 2. Signal Card (Replaces the custom table/grid) - contains Track, Metrics, Rationale */}
              <SignalCard signal={liteResult} />

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
