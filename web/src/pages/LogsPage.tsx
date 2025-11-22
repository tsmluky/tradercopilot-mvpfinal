import React, { useEffect, useState } from 'react';
import { FileText, Download, RefreshCw, AlertCircle } from 'lucide-react';
import { api } from '../services/api';
import { AnalysisMode, LogRow } from '../types';
import { TOKENS } from '../constants';

export const LogsPage: React.FC = () => {
  const [mode, setMode] = useState<string>(AnalysisMode.EVALUATED);
  const [token, setToken] = useState<string>('all');
  const [logs, setLogs] = useState<LogRow[]>([]);
  const [loading, setLoading] = useState(false);

  const fetchLogs = async () => {
    setLoading(true);
    try {
      let data: LogRow[] = [];

      if (token === 'all') {
        // Fetch logs for all tokens and merge
        const fetchPromises = TOKENS.map(t =>
          api.fetchLogs(mode, t.id).catch(err => {
            console.error(`Failed to fetch logs for ${t.id}`, err);
            return [];
          })
        );
        const results = await Promise.all(fetchPromises);
        data = results.flat();
      } else {
        // Fetch for specific token
        data = await api.fetchLogs(mode, token);
      }

      setLogs(data);
    } catch (e) {
      console.error('Failed to fetch logs', e);
      setLogs([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLogs();
  }, [mode, token]);

  const filteredLogs = logs
    .filter((log) => {
      if (token === 'all') return true;
      return log.token?.toString().toLowerCase() === token.toLowerCase();
    })
    .sort((a, b) => {
      const ta = new Date(
        (a.evaluated_at as string) || (a.timestamp as string) || 0
      ).getTime();
      const tb = new Date(
        (b.evaluated_at as string) || (b.timestamp as string) || 0
      ).getTime();
      return tb - ta;
    });

  const headers =
    filteredLogs.length > 0
      ? Object.keys(filteredLogs[0])
      : logs.length > 0
        ? Object.keys(logs[0])
        : [];

  return (
    <div className="p-6 md:p-8 max-w-7xl mx-auto h-full flex flex-col">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-8 gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center gap-2">
            <FileText className="text-emerald-400" /> System Logs
          </h1>
          <p className="text-slate-400 text-sm">
            Raw audit trails from backend CSV/JSON records.
          </p>
        </div>

        <div className="flex flex-wrap gap-3 items-center bg-slate-900 p-2 rounded-lg border border-slate-800">
          <select
            value={token}
            onChange={(e) => setToken(e.target.value)}
            className="bg-slate-800 text-white text-sm rounded px-3 py-1.5 border border-slate-700 focus:ring-2 focus:ring-emerald-500 outline-none font-mono uppercase"
          >
            <option value="all">ALL ASSETS</option>
            {TOKENS.map((t) => (
              <option key={t.id} value={t.id}>
                {t.symbol}
              </option>
            ))}
          </select>

          <span className="text-slate-600">/</span>

          <select
            value={mode}
            onChange={(e) => setMode(e.target.value)}
            className="bg-slate-800 text-white text-sm rounded px-3 py-1.5 border border-slate-700 focus:ring-2 focus:ring-emerald-500 outline-none font-mono uppercase"
          >
            {Object.values(AnalysisMode).map((m) => (
              <option key={m} value={m}>
                {m}
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

      <div className="flex-1 bg-slate-900 rounded-xl border border-slate-800 shadow-lg overflow-hidden flex flex-col">
        {loading ? (
          <div className="flex-1 flex items-center justify-center text-slate-500">
            <RefreshCw className="animate-spin mr-2" /> Loading logs...
          </div>
        ) : filteredLogs.length === 0 ? (
          <div className="flex-1 flex flex-col items-center justify-center text-slate-500 p-12">
            <AlertCircle size={48} className="mb-4 opacity-20" />
            <p>
              No logs found for {mode}/
              {token === 'all' ? 'ALL' : token.toUpperCase()}
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
                {filteredLogs.map((row, idx) => (
                  <tr
                    key={idx}
                    className="hover:bg-slate-800/30 transition-colors"
                  >
                    {headers.map((h) => {
                      const val = row[h];
                      const strVal = val != null ? String(val) : '';
                      let colorClass = 'text-slate-300';

                      if (h === 'result') {
                        if (strVal.includes('WIN') || strVal.includes('TP')) {
                          colorClass = 'text-emerald-400 font-bold';
                        } else if (
                          strVal.includes('LOSS') ||
                          strVal.includes('SL')
                        ) {
                          colorClass = 'text-rose-400 font-bold';
                        }
                      }

                      if (h === 'move_pct') {
                        if (strVal.startsWith('+'))
                          colorClass = 'text-emerald-400';
                        if (strVal.startsWith('-'))
                          colorClass = 'text-rose-400';
                      }

                      if (h === 'direction') {
                        if (strVal.toLowerCase() === 'long')
                          colorClass = 'text-emerald-400 uppercase';
                        if (strVal.toLowerCase() === 'short')
                          colorClass = 'text-rose-400 uppercase';
                      }

                      return (
                        <td key={h} className={`p-4 ${colorClass}`}>
                          {h === 'timestamp' || h === 'evaluated_at' || h === 'signal_ts' ? (
                            <div className="flex items-center gap-2 group cursor-help" title={new Date(strVal).toLocaleString()}>
                              <div className="flex flex-col">
                                <span className="text-slate-200 font-bold text-xs">
                                  {(() => {
                                    const date = new Date(strVal);
                                    const now = new Date();
                                    const diff = (now.getTime() - date.getTime()) / 1000;

                                    if (diff < 60) return 'Just now';
                                    if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
                                    if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
                                    return `${Math.floor(diff / 86400)}d ago`;
                                  })()}
                                </span>
                                <span className="text-[10px] text-slate-500 font-mono">
                                  {new Date(strVal).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                                </span>
                              </div>
                            </div>
                          ) : (
                            strVal
                          )}
                        </td>
                      );
                    })}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        <div className="p-4 border-t border-slate-800 bg-slate-900 flex justify-end">
          <button
            className="flex items-center gap-2 text-xs font-bold text-slate-500 hover:text-emerald-400 uppercase tracking-wider cursor-not-allowed"
            title="CSV download planned for next version"
            disabled
          >
            <Download size={14} /> Download CSV
          </button>
        </div>
      </div>
    </div>
  );
};
