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
                ${
                  mode === m
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
          <div className="space-y-3">
            <div className="flex flex-wrap items-center gap-2 text-sm">
              <span className="px-2 py-1 rounded-full text-xs font-semibold bg-slate-800 text-slate-100">
                {liteResult.token} · {liteResult.timeframe}
              </span>
              <span
                className={`px-2 py-1 rounded-full text-xs font-semibold ${
                  liteResult.direction.toLowerCase() === "long"
                    ? "bg-emerald-500/10 text-emerald-300 border border-emerald-500/40"
                    : "bg-rose-500/10 text-rose-300 border border-rose-500/40"
                }`}
              >
                {liteResult.direction.toUpperCase()}
              </span>
              <span className="text-xs text-slate-500">
                {new Date(liteResult.timestamp).toLocaleString()}
              </span>
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-sm">
              <div className="bg-slate-950/60 border border-slate-800 rounded-lg p-3">
                <div className="text-xs text-slate-400">Entry</div>
                <div className="text-slate-50 font-semibold">
                  {liteResult.entry?.toFixed?.(2) ?? liteResult.entry}
                </div>
              </div>
              <div className="bg-slate-950/60 border border-slate-800 rounded-lg p-3">
                <div className="text-xs text-slate-400">Take Profit</div>
                <div className="text-emerald-300 font-semibold">
                  {liteResult.tp?.toFixed?.(2) ?? liteResult.tp}
                </div>
              </div>
              <div className="bg-slate-950/60 border border-slate-800 rounded-lg p-3">
                <div className="text-xs text-slate-400">Stop Loss</div>
                <div className="text-rose-300 font-semibold">
                  {liteResult.sl?.toFixed?.(2) ?? liteResult.sl}
                </div>
              </div>
              <div className="bg-slate-950/60 border border-slate-800 rounded-lg p-3">
                <div className="text-xs text-slate-400">Confidence</div>
                <div className="text-slate-50 font-semibold">
                  {(liteResult.confidence * 100).toFixed(0)}%
                </div>
              </div>
            </div>

            <div className="mt-2">
              <div className="text-xs font-semibold text-slate-400 mb-1 uppercase tracking-wide">
                Rationale
              </div>
              <p className="text-sm text-slate-200 leading-relaxed whitespace-pre-wrap">
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
