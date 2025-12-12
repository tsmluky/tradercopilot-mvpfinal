import React, { useEffect, useState } from 'react';
import { SignalLite, SignalEvaluation } from '../types';
import { api } from '../services/api';
import {
  TrendingUp,
  TrendingDown,
  Target,
  Shield,
  Clock,
  Activity,
  CheckCircle2,
  XCircle,
  Copy,
  Check,
  Bookmark,
  BookmarkCheck,
  AlertTriangle,
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';

interface SignalCardProps {
  signal: SignalLite;
}

export const SignalCard: React.FC<SignalCardProps> = ({ signal }) => {
  const [evaluation, setEvaluation] = useState<SignalEvaluation | null>(null);
  const [isLoadingEval, setIsLoadingEval] = useState(false);
  const [copied, setCopied] = useState(false);

  const { userProfile, toggleFollow } = useAuth();

  // Time Limit Logic (30s para seguir la señal)
  const [timeLeft, setTimeLeft] = useState<number>(30);
  const [isExpired, setIsExpired] = useState(false);

  const isLong = signal.direction === 'long';
  const directionColor = isLong ? 'text-emerald-400' : 'text-rose-400';
  const baseBg = isLong ? 'bg-emerald-500/5' : 'bg-rose-500/5';
  const borderColor = isLong ? 'border-emerald-500/20' : 'border-rose-500/20';

  // Check if followed (paper trading)
  const isFollowed =
    userProfile?.portfolio?.followed_signals?.some(
      (s) => s.timestamp === signal.timestamp && s.token === signal.token,
    ) ?? false;

  // Risk/Reward stats
  const risk = Math.abs(signal.entry - signal.sl);
  const reward = Math.abs(signal.tp - signal.entry);
  const rrRatio = risk === 0 ? 0 : Number((reward / risk).toFixed(2));

  // Spectrum bar positions
  const rangeMin = Math.min(signal.sl, signal.tp);
  const rangeMax = Math.max(signal.sl, signal.tp);
  const totalRange = rangeMax - rangeMin;

  const getPos = (val: number) => {
    if (totalRange === 0) return 50;
    return ((val - rangeMin) / totalRange) * 100;
  };

  // Fetch evaluación de la señal
  useEffect(() => {
    const fetchEval = async () => {
      setIsLoadingEval(true);
      try {
        const result = await api.getSignalEvaluation(signal.token, signal.timestamp);
        setEvaluation(result);
      } catch (e) {
        console.error('Failed to fetch evaluation', e);
      } finally {
        setIsLoadingEval(false);
      }
    };

    if (signal) {
      fetchEval();
    }
  }, [signal]);

  // Countdown Timer Logic (30s desde timestamp)
  useEffect(() => {
    if (isFollowed) return; // si ya está seguida, no contamos

    const createdTime = new Date(signal.timestamp).getTime();

    const update = () => {
      const now = Date.now();
      const secondsPassed = (now - createdTime) / 1000;
      const remaining = Math.max(0, 30 - secondsPassed);

      setTimeLeft(remaining);

      if (remaining <= 0) {
        setIsExpired(true);
        return true;
      }
      return false;
    };

    // Actualización inmediata para evitar 1s “en falso”
    if (update()) return;

    const interval = setInterval(() => {
      if (update()) {
        clearInterval(interval);
      }
    }, 1000);

    return () => clearInterval(interval);
  }, [signal.timestamp, isFollowed]);

  const handleCopy = () => {
    const text = `[LITE] ${signal.token} ${signal.timeframe
      } — ${signal.direction} | Entry ${signal.entry} | TP ${signal.tp} | SL ${signal.sl
      } | Conf ${(signal.confidence * 100).toFixed(0)}%`;

    if (navigator?.clipboard?.writeText) {
      navigator.clipboard.writeText(text);
    }

    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleToggleFollow = () => {
    if (isExpired && !isFollowed) return;
    toggleFollow(signal);
  };

  return (
    <div
      className={`rounded-xl border ${borderColor} ${baseBg} p-6 shadow-lg backdrop-blur-sm animate-fade-in relative overflow-hidden`}
    >
      {/* Header */}
      <div className="flex justify-between items-start mb-6">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="text-2xl font-bold text-white tracking-tight">
              {signal.token}
            </span>
            <span className="px-2 py-0.5 rounded text-xs font-bold bg-slate-800 text-slate-400 border border-slate-700">
              {signal.timeframe}
            </span>
          </div>
          <div
            className={`flex items-center gap-2 font-bold text-lg uppercase ${directionColor}`}
          >
            {isLong ? (
              <TrendingUp size={20} strokeWidth={2.5} />
            ) : (
              <TrendingDown size={20} strokeWidth={2.5} />
            )}
            {signal.direction}
          </div>
        </div>

        <div className="text-right flex flex-col items-end">
          {evaluation ? (
            <div
              className={`flex items-center gap-2 px-3 py-1 rounded-full border ${evaluation.status === 'WIN'
                ? 'bg-emerald-500/20 border-emerald-500 text-emerald-400'
                : 'bg-rose-500/20 border-rose-500 text-rose-400'
                } mb-1`}
            >
              {evaluation.status === 'WIN' ? (
                <CheckCircle2 size={16} />
              ) : (
                <XCircle size={16} />
              )}
              <span className="font-bold text-sm">
                {evaluation.status} (
                {evaluation.pnl_r > 0 ? '+' : ''}
                {evaluation.pnl_r}R)
              </span>
            </div>
          ) : (
            <div className="bg-slate-800/50 px-3 py-1 rounded-full border border-slate-700 flex items-center gap-2">
              <div className="w-2 h-2 rounded-full bg-blue-400 animate-pulse" />
              <span className="text-xs font-medium text-slate-400">
                {isLoadingEval ? 'CHECKING...' : 'ACTIVE'}
              </span>
            </div>
          )}

          <div className="mt-2 text-xs text-slate-500 font-mono">
            Conf:{' '}
            <span className="text-white font-bold">
              {(signal.confidence * 100).toFixed(0)}%
            </span>
          </div>
        </div>
      </div>

      {/* Numbers Grid - Clean & Integrated */}
      <div className="grid grid-cols-3 gap-px bg-slate-800/50 rounded-lg overflow-hidden border border-slate-800 mb-6">
        <div className="bg-slate-900/40 p-4 flex flex-col items-center justify-center hover:bg-slate-800/40 transition-colors group">
          <div className="text-[10px] uppercase tracking-wider text-slate-500 font-bold mb-1 group-hover:text-slate-400">Entry</div>
          <div className="font-mono text-lg font-bold text-white tracking-tight">{signal.entry}</div>
        </div>

        <div className="bg-slate-900/40 p-4 flex flex-col items-center justify-center hover:bg-emerald-900/10 transition-colors group relative">
          <div className="absolute inset-0 bg-emerald-500/5 opacity-0 group-hover:opacity-100 transition-opacity" />
          <div className="text-[10px] uppercase tracking-wider text-emerald-500/70 font-bold mb-1 group-hover:text-emerald-400">Target</div>
          <div className="font-mono text-lg font-bold text-emerald-400 tracking-tight">{signal.tp}</div>
        </div>

        <div className="bg-slate-900/40 p-4 flex flex-col items-center justify-center hover:bg-rose-900/10 transition-colors group relative">
          <div className="absolute inset-0 bg-rose-500/5 opacity-0 group-hover:opacity-100 transition-opacity" />
          <div className="text-[10px] uppercase tracking-wider text-rose-500/70 font-bold mb-1 group-hover:text-rose-400">Stop</div>
          <div className="font-mono text-lg font-bold text-rose-400 tracking-tight">{signal.sl}</div>
        </div>
      </div>

      {/* Minimalist RR Bar */}
      <div className="mb-6">
        <div className="flex justify-between text-[10px] font-bold text-slate-500 mb-1.5 uppercase tracking-wider">
          <span>Risk/Reward</span>
          <span className="text-slate-400">1:{rrRatio}</span>
        </div>
        <div className="h-1.5 w-full bg-slate-800 rounded-full overflow-hidden flex">
          <div style={{ width: '40%' }} className="h-full bg-rose-500/40" />
          <div style={{ width: '60%' }} className="h-full bg-emerald-500/40" />
        </div>
      </div>

      {/* Rationale */}
      <div className="bg-slate-900/60 rounded-lg p-4 border border-slate-700/50 mb-4">
        <div className="flex items-center gap-2 mb-2">
          <div className="w-1 h-4 bg-slate-500 rounded-full" />
          <div className="text-xs font-bold text-slate-500 uppercase tracking-wider">
            AI Rationale
          </div>
        </div>
        <p className="text-sm text-slate-300 leading-relaxed font-medium">
          {signal.rationale}
        </p>
      </div>

      {/* Footer Actions */}
      <div className="flex justify-between items-center pt-3 border-t border-slate-800/50">
        <div className="flex items-center gap-1.5 text-xs text-slate-500">
          <Clock size={12} />
          {new Date(signal.timestamp).toLocaleTimeString()} UTC
        </div>

        <div className="flex items-center gap-2">
          {/* Discuss */}
          <button
            onClick={() => {
              // Dispatch synthetic event or use a global context to open chat
              // Ideally parent should handle this, but for MVP we can use a custom event or props (if we refactor)
              // For now, let's assume we pass a prop or use a global store.
              // Simpler: Dispatch event to be caught by App.tsx or Layout
              window.dispatchEvent(new CustomEvent('open-advisor-chat', {
                detail: {
                  token: signal.token,
                  context: signal
                }
              }));
            }}
            className="flex items-center gap-2 px-3 py-2 rounded-lg text-xs font-bold bg-indigo-600 text-white hover:bg-indigo-500 transition-colors shadow-lg shadow-indigo-500/20 active:scale-95 duration-100"
          >
            <Shield size={14} />
            DISCUSS
          </button>

          {/* Track button con expiry */}
          <button
            onClick={handleToggleFollow}
            disabled={isExpired && !isFollowed}
            className={`flex items-center gap-2 px-3 py-2 rounded-lg text-xs font-bold transition-all border active:scale-95 duration-100 ${isFollowed
              ? 'bg-indigo-500/10 text-indigo-400 border-indigo-500/30 hover:bg-indigo-500/20'
              : isExpired
                ? 'bg-slate-800 text-slate-600 border-slate-800 cursor-not-allowed'
                : 'bg-slate-800 text-slate-300 border-slate-700 hover:bg-slate-700 hover:text-white hover:border-slate-500'
              }`}
          >
            {isFollowed ? (
              <BookmarkCheck size={14} />
            ) : isExpired ? (
              <AlertTriangle size={14} />
            ) : (
              <Bookmark size={14} />
            )}

            {isFollowed
              ? 'TRACKING'
              : isExpired
                ? 'EXPIRED'
                : `TRACK (${timeLeft.toFixed(0)}s)`}
          </button>

          {/* Copy */}
          <button
            onClick={handleCopy}
            className={`flex items-center gap-2 px-3 py-2 rounded-lg text-xs font-bold transition-all active:scale-95 duration-100 ${copied
              ? 'bg-emerald-500 text-white'
              : 'bg-slate-800 text-slate-400 hover:bg-slate-700 hover:text-white'
              }`}
          >
            {copied ? <Check size={14} /> : <Copy size={14} />}
            {copied ? 'COPIED' : 'COPY'}
          </button>
        </div>
      </div>
    </div>
  );
};
