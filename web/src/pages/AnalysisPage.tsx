import React, { useState, useRef, useEffect } from 'react';
import { TOKENS, TIMEFRAMES } from '../constants';
import { api } from '../services/api';
import { notificationService } from '../services/notification';
import { SignalLite, ProResponse, AnalysisMode } from '../types';
import { SignalCard } from '../components/SignalCard';
import { ProAnalysisViewer } from '../components/ProAnalysisViewer';
import { AdvisorChat } from '../components/AdvisorChat';
import { PriceChart } from '../components/PriceChart';
import { Play, Zap, BookOpen, Briefcase, Loader2 } from 'lucide-react';

export const AnalysisPage: React.FC = () => {
  const [mode, setMode] = useState<AnalysisMode>(AnalysisMode.LITE);
  const [selectedToken, setSelectedToken] = useState('eth');
  const [selectedTimeframe, setSelectedTimeframe] = useState('30m');
  const [loading, setLoading] = useState(false);

  // State for responses
  const [liteSignal, setLiteSignal] = useState<SignalLite | null>(null);
  const [proResponse, setProResponse] = useState<ProResponse | null>(null);

  // State for Advisor
  const [advDirection, setAdvDirection] = useState('long');
  const [advEntry, setAdvEntry] = useState('3000');
  const [advQuote, setAdvQuote] = useState('1000');
  const [activeAdvisorSession, setActiveAdvisorSession] = useState<{
    token: string;
    direction: string;
    entry: number;
    size_quote: number;
    tp: number;
    sl: number;
  } | null>(null);

  // Ref for auto-scroll to results
  const resultsRef = useRef<HTMLDivElement | null>(null);

  // Reset resultados al cambiar de modo
  useEffect(() => {
    setLiteSignal(null);
    setProResponse(null);
    setActiveAdvisorSession(null);
    setLoading(false);
  }, [mode]);

  // Auto-scroll cuando llegan resultados
  useEffect(() => {
    if ((liteSignal || proResponse || activeAdvisorSession) && !loading) {
      setTimeout(() => {
        resultsRef.current?.scrollIntoView({
          behavior: 'smooth',
          block: 'start',
        });
      }, 100);
    }
  }, [liteSignal, proResponse, activeAdvisorSession, loading]);

  const handleRun = async () => {
    // Advisor → sólo abrimos sesión de chat con contexto inicial
    if (mode === AnalysisMode.ADVISOR) {
      setActiveAdvisorSession({
        token: selectedToken,
        direction: advDirection,
        entry: parseFloat(advEntry),
        size_quote: parseFloat(advQuote),
        tp: 0, // dejar que el backend/LLM calcule
        sl: 0,
      });
      return;
    }

    setLoading(true);
    // Limpieza ligera para refrescar visualmente
    setLiteSignal(null);
    setProResponse(null);

    try {
      if (mode === AnalysisMode.LITE) {
        const res = await api.analyzeLite(selectedToken, selectedTimeframe);
        setLiteSignal(res);
        notificationService.notify('Signal Generated', `LITE analysis for ${selectedToken.toUpperCase()} complete.`, 'success');
      } else if (mode === AnalysisMode.PRO) {
        const res = await api.analyzePro(selectedToken, selectedTimeframe, true);
        setProResponse(res);
        notificationService.notify('Analysis Complete', `PRO analysis for ${selectedToken.toUpperCase()} generated.`, 'success');
      }
    } catch (e) {
      console.error(e);
      notificationService.notify('Analysis Failed', 'Could not generate signal. Please try again.', 'error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-4 md:p-6 max-w-7xl mx-auto h-full flex flex-col pb-24 md:pb-6">
      <header className="mb-6 flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center gap-2">
            <TerminalIcon /> Trading Terminal
          </h1>
          <p className="text-slate-400 text-sm mt-1">
            Select mode and parameters to generate signals.
          </p>
        </div>

        {/* Mode Switcher */}
        <div className="w-full md:w-auto flex bg-slate-900 p-1 rounded-lg border border-slate-800 overflow-x-auto shrink-0">
          <ModeTab
            active={mode === AnalysisMode.LITE}
            onClick={() => setMode(AnalysisMode.LITE)}
            icon={<Zap size={16} />}
            label="LITE"
          />
          <ModeTab
            active={mode === AnalysisMode.PRO}
            onClick={() => setMode(AnalysisMode.PRO)}
            icon={<BookOpen size={16} />}
            label="PRO"
          />
          <ModeTab
            active={mode === AnalysisMode.ADVISOR}
            onClick={() => setMode(AnalysisMode.ADVISOR)}
            icon={<Briefcase size={16} />}
            label="ADVISOR"
          />
        </div>
      </header>

      {/* Controls Bar (se oculta cuando hay sesión de Advisor activa para ganar espacio) */}
      {!activeAdvisorSession && (
        <div className="bg-slate-900 p-4 rounded-xl border border-slate-800 shadow-sm mb-6 flex flex-wrap gap-4 items-end">
          <div className="flex-1 min-w-[120px]">
            <label className="block text-xs font-bold text-slate-500 uppercase mb-1.5">
              Asset
            </label>
            <select
              value={selectedToken}
              onChange={(e) => setSelectedToken(e.target.value)}
              className="w-full bg-slate-800 border border-slate-700 text-white rounded-lg px-3 py-2.5 focus:ring-2 focus:ring-emerald-500 focus:outline-none appearance-none font-mono text-base"
            >
              {TOKENS.map((t) => (
                <option key={t.id} value={t.id}>
                  {t.symbol} - {t.name}
                </option>
              ))}
            </select>
          </div>

          {mode !== AnalysisMode.ADVISOR && (
            <div className="w-32 flex-1 md:flex-none">
              <label className="block text-xs font-bold text-slate-500 uppercase mb-1.5">
                Timeframe
              </label>
              <select
                value={selectedTimeframe}
                onChange={(e) => setSelectedTimeframe(e.target.value)}
                className="w-full bg-slate-800 border border-slate-700 text-white rounded-lg px-3 py-2.5 focus:ring-2 focus:ring-emerald-500 focus:outline-none appearance-none font-mono text-base"
              >
                {TIMEFRAMES.map((t) => (
                  <option key={t} value={t}>
                    {t}
                  </option>
                ))}
              </select>
            </div>
          )}

          {mode === AnalysisMode.ADVISOR && (
            <>
              <div className="w-32 flex-1 md:flex-none">
                <label className="block text-xs font-bold text-slate-500 uppercase mb-1.5">
                  Direction
                </label>
                <select
                  value={advDirection}
                  onChange={(e) => setAdvDirection(e.target.value)}
                  className="w-full bg-slate-800 border border-slate-700 text-white rounded-lg px-3 py-2.5 font-mono text-base"
                >
                  <option value="long">LONG</option>
                  <option value="short">SHORT</option>
                </select>
              </div>
              <div className="w-32 flex-1 md:flex-none">
                <label className="block text-xs font-bold text-slate-500 uppercase mb-1.5">
                  Entry ($)
                </label>
                <input
                  type="number"
                  value={advEntry}
                  onChange={(e) => setAdvEntry(e.target.value)}
                  className="w-full bg-slate-800 border border-slate-700 text-white rounded-lg px-3 py-2.5 font-mono text-base"
                />
              </div>
              <div className="w-32 flex-1 md:flex-none">
                <label className="block text-xs font-bold text-slate-500 uppercase mb-1.5">
                  Size ($)
                </label>
                <input
                  type="number"
                  value={advQuote}
                  onChange={(e) => setAdvQuote(e.target.value)}
                  className="w-full bg-slate-800 border border-slate-700 text-white rounded-lg px-3 py-2.5 font-mono text-base"
                />
              </div>
            </>
          )}

          <button
            onClick={handleRun}
            disabled={loading}
            className="w-full md:w-auto flex items-center justify-center gap-2 bg-emerald-500 hover:bg-emerald-600 text-white font-bold px-6 py-2.5 rounded-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed ml-auto active:scale-95"
          >
            {loading ? (
              <Loader2 className="animate-spin" size={18} />
            ) : (
              <Play size={18} fill="currentColor" />
            )}
            {mode === AnalysisMode.ADVISOR ? 'START SESSION' : 'RUN'}
          </button>
        </div>
      )}

      {/* Main Layout - Vertical Stack */}
      <div className="space-y-6 flex-1">
        {/* Chart Section - Full Width on Top */}
        {!activeAdvisorSession && (
          <div className="w-full h-[350px] md:h-[400px]">
            <PriceChart
              token={selectedToken}
              signal={mode === AnalysisMode.LITE ? liteSignal : undefined}
              timeframe={selectedTimeframe}
            />
          </div>
        )}

        {/* Results Section - Full Width Below */}
        <div ref={resultsRef} className="w-full scroll-mt-20">
          {loading ? (
            <div className="h-64 flex flex-col items-center justify-center text-slate-500 animate-pulse bg-slate-900/30 rounded-xl border border-dashed border-slate-800">
              <div className="w-16 h-16 border-4 border-slate-700 border-t-emerald-500 rounded-full animate-spin mb-4"></div>
              <p className="font-mono text-sm">
                Processing market data & RAG context...
              </p>
            </div>
          ) : (
            <>
              {mode === AnalysisMode.LITE && liteSignal && (
                <SignalCard signal={liteSignal} />
              )}

              {mode === AnalysisMode.PRO && proResponse && (
                <ProAnalysisViewer
                  response={proResponse}
                  token={selectedToken}
                />
              )}

              {mode === AnalysisMode.ADVISOR && activeAdvisorSession && (
                <AdvisorChat
                  initialContext={activeAdvisorSession}
                  onReset={() => setActiveAdvisorSession(null)}
                />
              )}

              {!liteSignal && !proResponse && !activeAdvisorSession && (
                <div className="h-full flex flex-col items-center justify-center text-slate-600 border-2 border-dashed border-slate-800 rounded-xl p-12 min-h-[200px] bg-slate-900/20">
                  <TerminalIcon className="w-16 h-16 mb-4 opacity-20" />
                  <p>Ready to analyze. Set parameters and click RUN.</p>
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
};

const ModeTab = ({ active, onClick, icon, label }: any) => (
  <button
    onClick={onClick}
    className={`flex items-center gap-2 px-4 py-2 rounded-md text-sm font-bold transition-all active:scale-95 flex-1 justify-center md:flex-none whitespace-nowrap ${active
      ? 'bg-slate-700 text-white shadow'
      : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800'
      }`}
  >
    {icon} {label}
  </button>
);

const TerminalIcon = ({ className }: { className?: string }) => (
  <svg
    className={className}
    width="24"
    height="24"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
  >
    <polyline points="4 17 10 11 4 5"></polyline>
    <line x1="12" y1="19" x2="20" y2="19"></line>
  </svg>
);
