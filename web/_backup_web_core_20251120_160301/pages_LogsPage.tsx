// pages/LogsPage.tsx
// Logs & History conectado a /logs/{mode}/{token} con opción ALL ASSETS (agregado cliente)

import React, { useEffect, useState } from 'react';
import { FileText, Download, RefreshCw, AlertCircle } from 'lucide-react';
import { TOKENS } from '../constants';
import { api, LogsResponse } from '../services/api';
import { AnalysisMode, LogRow } from '../types';

type LogModeValue =
  | AnalysisMode.LITE
  | AnalysisMode.PRO
  | AnalysisMode.ADVISOR
  | AnalysisMode.EVALUATED;

const LOG_MODE_OPTIONS: { value: LogModeValue; label: string }[] = [
  { value: AnalysisMode.LITE,      label: 'LITE · Signals' },
  { value: AnalysisMode.PRO,       label: 'PRO · Analyses' },
  { value: AnalysisMode.ADVISOR,   label: 'ADVISOR · Requests' },
  { value: AnalysisMode.EVALUATED, label: 'EVALUATED · Results' },
];

export const LogsPage: React.FC = () => {
  // Por defecto mostramos lo prioritario ahora: resultados evaluados
  const [mode, setMode] = useState<LogModeValue>(AnalysisMode.EVALUATED);
  const [token, setToken] = useState<string>('eth');
  const [logs, setLogs] = useState<LogRow[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const currentModeLabel =
    LOG_MODE_OPTIONS.find((m) => m.value === mode)?.label ?? mode;

  const fetchLogs = async () => {
    setLoading(true);
    setError(null);
    try {
      // Si seleccionas ALL ASSETS, agregamos desde todos los tokens definidos en TOKENS
      if (token === 'all') {
        const responses = await Promise.all(
          TOKENS.map((t) =>
            api.fetchLogs(mode, t.id) as Promise<LogsResponse>
          )
        );
        const merged = responses.flatMap((r) => r.logs ?? []);
        // Orden descendente por evaluated_at / timestamp
        merged.sort(
          (a, b) =>
            new Date(b.evaluated_at || b.timestamp || 0).getTime() -
            new Date(a.evaluated_at || a.timestamp || 0).getTime()
        );
        setLogs(merged);
      } else {
        const data = (await api.fetchLogs(mode, token)) as LogsResponse;
        const rows = data?.logs ?? [];
        setLogs(rows);
      }
    } catch (e: any) {
      console.error('Failed to fetch logs', e);
      setError(e?.message ?? 'Failed to fetch logs');
      setLogs([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLogs();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [mode, token]);

  // Encabezados dinámicos a partir de la primera fila
  const headers = logs.length > 0 ? Object.keys(logs[0]) : [];

  return (
    <div className="p-6 md:p-8 max-w-7xl mx-auto h-full flex flex-col">
      {/* Header */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-8 gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center gap-2">
            <FileText className="text-emerald-400" /> Logs &amp; History
          </h1>
          <p className="text-slate-400 text-sm">
            Inspect recorded signals, analyses and evaluations from backend CSV logs.
          </p>
          <p className="text-[11px] text-slate-500 mt-1 font-mono">
            {currentModeLabel} ·{' '}
            {token === 'all' ? 'ALL ASSETS' : token.toUpperCase()}
          </p>
        </div>

        {/* Filtros: token / mode / refresh */}
        <div className="flex flex-wrap gap-3 items-center bg-slate-900 p-2 rounded-lg border border-slate-800">
          {/* Token Selector */}
          <select
            value={token}
            onChange={(e) => setToken(e.target.value)}
            className="bg-slate-800 text-white text-sm rounded px-3 py-1.5 border border-slate-700 focus:ring-2 focus:ring-emerald-500 outline-none font-mono uppercase"
          >
            <option value="all">ALL</option>
            {TOKENS.map((t) => (
              <option key={t.id} value={t.id}>
                {t.symbol}
              </option>
            ))}
          </select>

          <span className="text-slate-600">/</span>

          {/* Mode Selector */}
          <select
            value={mode}
            onChange={(e) => setMode(e.target.value as LogModeValue)}
            className="bg-slate-800 text-white text-sm rounded px-3 py-1.5 border border-slate-700 focus:ring-2 focus:ring-emerald-500 outline-none font-mono uppercase"
          >
            {LOG_MODE_OPTIONS.map((m) => (
              <option key={m.value} value={m.value}>
                {m.label}
              </option>
            ))}
          </select>

          <button
            onClick={fetchLogs}
            className="ml-2 p-2 hover:bg-slate-700 rounded-full text-slate-400 hover:text-white transition-colors"
            title="Refresh"
          >
            <RefreshCw size={16} className={loading ? 'animate-spin' : ''} />
          </button>
        </div>
      </div>

      {/* Contenedor principal */}
      <div className="flex-1 bg-slate-900 rounded-xl border border-slate-800 shadow-lg overflow-hidden flex flex-col">
        {/* Estados: loading / error / vacío / tabla */}
        {loading ? (
          <div className="flex-1 flex items-center justify-center text-slate-500 text-sm">
            <RefreshCw className="animate-spin mr-2" /> Loading logs...
          </div>
        ) : error ? (
          <div className="flex-1 flex flex-col items-center justify-center text-red-400 text-sm p-12">
            <AlertCircle size={40} className="mb-3 opacity-60" />
            <p className="font-mono">Error: {error}</p>
          </div>
        ) : logs.length === 0 ? (
          <div className="flex-1 flex flex-col items-center justify-center text-slate-500 p-12">
            <AlertCircle size={48} className="mb-4 opacity-20" />
            <p className="text-sm">
              No logs found for{' '}
              <span className="font-mono">{mode}</span> /{' '}
              <span className="font-mono">
                {token === 'all' ? 'ALL' : token.toUpperCase()}
              </span>
              .
            </p>
          </div>
        ) : (
          <div className="overflow-x-auto flex-1">
            <table className="w-full text-left border-collapse whitespace-nowrap">
              <thead>
                <tr className="bg-slate-800 text-slate-400 text-xs uppercase tracking-wider border-b border-slate-700">
                  {headers.map((h) => (
                    <th key={h} className="p-4 font-mono font-bold">
                      {h.replace(/_/g, ' ')}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/50 text-sm font-mono text-slate-300">
                {logs.map((row, idx) => (
                  <tr
                    key={idx}
                    className="hover:bg-slate-800/30 transition-colors"
                  >
                    {headers.map((h) => {
                      const rawVal = (row as any)?.[h];
                      const val =
                        rawVal === null || rawVal === undefined ? '' : rawVal;

                      let colorClass = 'text-slate-300';

                      // Estilos según columna / contenido
                      if (h === 'direction') {
                        const v = String(val).toLowerCase();
                        if (v === 'long')
                          colorClass = 'text-emerald-400 uppercase';
                        if (v === 'short')
                          colorClass = 'text-rose-400 uppercase';
                      }

                      if (h === 'result') {
                        const v = String(val).toUpperCase();
                        if (v.includes('TP') || v.includes('WIN')) {
                          colorClass = 'text-emerald-400 font-bold';
                        } else if (v.includes('SL') || v.includes('LOSS')) {
                          colorClass = 'text-rose-400 font-bold';
                        }
                      }

                      if (h === 'move_pct') {
                        const vStr = String(val);
                        if (vStr.startsWith('+'))
                          colorClass = 'text-emerald-400';
                        if (vStr.startsWith('-'))
                          colorClass = 'text-rose-400';
                      }

                      if (h === 'confidence') {
                        const num =
                          typeof val === 'number'
                            ? val
                            : parseFloat(String(val).replace(',', '.'));
                        if (!isNaN(num)) {
                          if (num >= 0.7) colorClass = 'text-emerald-400';
                          else if (num <= 0.4)
                            colorClass = 'text-amber-400';
                        }
                      }

                      return (
                        <td key={h} className={`p-4 ${colorClass}`}>
                          {typeof val === 'number' ? val.toString() : val}
                        </td>
                      );
                    })}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* Footer / Download (placeholder) */}
        <div className="p-4 border-t border-slate-800 bg-slate-900 flex justify-end">
          <button
            className="flex items-center gap-2 text-xs font-bold text-slate-500 hover:text-emerald-400 uppercase tracking-wider cursor-not-allowed"
            title="CSV download planned for v0.8"
            disabled
          >
            <Download size={14} /> Download CSV
          </button>
        </div>
      </div>
    </div>
  );
};
