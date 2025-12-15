import React, { useState } from "react";
import { analyzeLite, analyzePro } from "../services/api";
import type { SignalLite, ProResponse } from "../types";

type Mode = "LITE" | "PRO";

const TOKENS = ["ETH", "BTC", "SOL"] as const;
const TIMEFRAMES = ["1h", "4h", "1d"] as const;

export const AnalysisPage: React.FC = () => {
  const [mode, setMode] = useState<Mode>("LITE");
  const [token, setToken] = useState<string>("ETH");
  const [timeframe, setTimeframe] = useState<string>("4h");

  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [liteResult, setLiteResult] = useState<SignalLite | null>(null);
  const [proResult, setProResult] = useState<ProResponse | null>(null);

  async function handleGenerate() {
    setError(null);
    setIsLoading(true);

    try {
      if (mode === "LITE") {
        const data = await analyzeLite(token, timeframe);
        setLiteResult(data);
        setProResult(null);
      } else {
        const data = await analyzePro(token, timeframe, true);
        setProResult(data);
        setLiteResult(null);
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
        <h1 className="text-2xl font-semibold text-slate-50">Generate Signal</h1>
        <p className="text-slate-400 text-sm">
          Choose token, timeframe and mode. TraderCopilot will generate a LITE or PRO analysis
          based on your configuration.
        </p>
      </div>

      {/* Config Card */}
      <div className="bg-slate-900/70 border border-slate-800 rounded-2xl p-5 flex flex-col gap-4">
        {/* Mode toggle */}
        <div className="flex gap-3">
          {(["LITE", "PRO"] as Mode[]).map((m) => (
            <button
              key={m}
              type="button"
              onClick={() => setMode(m)}
              className={`px-4 py-2 rounded-full text-sm font-medium border transition
                ${mode === m
                  ? "bg-indigo-500 text-white border-indigo-400 shadow"
                  : "bg-slate-900 text-slate-300 border-slate-700 hover:border-slate-500"
                }`}
            >
              {m === "LITE" ? "LITE · Quick Signal" : "PRO · Full Analysis"}
            </button>
          ))}
        </div>

        {/* Inputs */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <div className="flex flex-col gap-1">
            <label className="text-xs font-medium text-slate-400 uppercase tracking-wide">
              Token
            </label>
            <select
              value={token}
              onChange={(e) => setToken(e.target.value)}
              className="bg-slate-950/80 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-100 focus:outline-none focus:ring-1 focus:ring-indigo-500"
            >
              {TOKENS.map((t) => (
                <option key={t} value={t}>
                  {t}
                </option>
              ))}
            </select>
          </div>

          <div className="flex flex-col gap-1">
            <label className="text-xs font-medium text-slate-400 uppercase tracking-wide">
              Timeframe
            </label>
            <select
              value={timeframe}
              onChange={(e) => setTimeframe(e.target.value)}
              className="bg-slate-950/80 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-100 focus:outline-none focus:ring-1 focus:ring-indigo-500"
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
              disabled={isLoading}
              className="w-full inline-flex items-center justify-center px-4 py-2 rounded-lg text-sm font-medium
                bg-indigo-500 text-white hover:bg-indigo-400 disabled:opacity-60 disabled:cursor-not-allowed
                transition shadow-sm"
            >
              {isLoading ? "Generating..." : "Generate analysis"}
            </button>
          </div>
        </div>

        {error && (
          <div className="text-sm text-red-400 bg-red-950/40 border border-red-900 rounded-lg px-3 py-2">
            {error}
          </div>
        )}
      </div>

      {/* Result Card */}
      <div className="bg-slate-900/70 border border-slate-800 rounded-2xl p-5">
        <h2 className="text-sm font-semibold text-slate-200 mb-3">Result</h2>

        {!liteResult && !proResult && (
          <p className="text-sm text-slate-500">
            No analysis generated yet. Configure your signal above and click{" "}
            <span className="text-slate-300 font-medium">Generate analysis</span>.
          </p>
        )}

        {mode === "LITE" && liteResult && (
          <div className="space-y-6 animate-in fade-in slide-in-from-bottom-2 duration-500">
            {/* Header / Meta */}
            <div className="flex items-center justify-between p-4 bg-slate-800/30 rounded-xl border border-slate-700/50">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-lg bg-indigo-500/10 flex items-center justify-center border border-indigo-500/20">
                  <span className="font-bold text-indigo-400">{liteResult.token}</span>
                </div>
                <div>
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-bold text-slate-100 uppercase tracking-tight">Signal Generated</span>
                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider ${liteResult.direction.toLowerCase() === "long"
                        ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20"
                        : "bg-rose-500/10 text-rose-400 border border-rose-500/20"
                      }`}>
                      {liteResult.direction}
                    </span>
                  </div>
                  <span className="text-xs text-slate-500 font-mono">
                    {liteResult.timeframe} • {new Date(liteResult.timestamp).toLocaleString()}
                  </span>
                </div>
              </div>

              {/* Confidence Ring */}
              <div className="text-right">
                <div className="text-xs text-slate-400 font-medium mb-1">Confidence</div>
                <div className={`text-xl font-bold ${liteResult.confidence >= 0.8 ? 'text-emerald-400' :
                    liteResult.confidence >= 0.6 ? 'text-amber-400' : 'text-slate-400'
                  }`}>
                  {(liteResult.confidence * 100).toFixed(0)}%
                </div>
              </div>
            </div>

            {/* Execution Block */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {/* Entry */}
              <div className="p-4 bg-slate-950/40 rounded-xl border border-slate-800/50 flex flex-col items-center justify-center text-center group hover:border-indigo-500/30 transition-colors">
                <span className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-2">Entry Zone</span>
                <span className="text-2xl font-mono text-slate-100 font-bold group-hover:scale-105 transition-transform">
                  {typeof liteResult.entry === 'number' ? liteResult.entry.toFixed(2) : liteResult.entry}
                </span>
              </div>

              {/* Take Profit */}
              <div className="p-4 bg-emerald-950/20 rounded-xl border border-emerald-900/40 flex flex-col items-center justify-center text-center group hover:border-emerald-500/30 transition-colors">
                <span className="text-xs font-bold text-emerald-600/80 uppercase tracking-wider mb-2">Take Profit</span>
                <span className="text-2xl font-mono text-emerald-400 font-bold group-hover:scale-105 transition-transform">
                  {typeof liteResult.tp === 'number' ? liteResult.tp.toFixed(2) : liteResult.tp}
                </span>
              </div>

              {/* Stop Loss */}
              <div className="p-4 bg-rose-950/20 rounded-xl border border-rose-900/40 flex flex-col items-center justify-center text-center group hover:border-rose-500/30 transition-colors">
                <span className="text-xs font-bold text-rose-600/80 uppercase tracking-wider mb-2">Stop Loss</span>
                <span className="text-2xl font-mono text-rose-400 font-bold group-hover:scale-105 transition-transform">
                  {typeof liteResult.sl === 'number' ? liteResult.sl.toFixed(2) : liteResult.sl}
                </span>
              </div>
            </div>

            {/* Rationale Section */}
            <div className="p-5 bg-slate-900/50 rounded-xl border border-slate-800 relative overflow-hidden">
              <div className="absolute top-0 left-0 w-1 h-full bg-gradient-to-b from-indigo-500 to-transparent"></div>
              <h3 className="text-sm font-bold text-slate-300 mb-3 flex items-center gap-2">
                <span className="w-1.5 h-1.5 rounded-full bg-indigo-500"></span>
                Analysis Rationale
              </h3>
              <p className="text-slate-400 text-sm leading-7 font-light">
                {liteResult.rationale}
              </p>
            </div>
          </div>
        )}

        {mode === "PRO" && proResult && (
          <div className="mt-2">
            <div className="text-xs font-semibold text-slate-400 mb-1 uppercase tracking-wide">
              PRO raw analysis
            </div>
            <pre className="mt-1 bg-slate-950/60 border border-slate-800 rounded-lg p-3 text-xs text-slate-100 max-h-[480px] overflow-auto whitespace-pre-wrap">
              {proResult.raw}
            </pre>
          </div>
        )}
      </div>
    </div>
  );
};
