import React from 'react';
import { History, TrendingUp, TrendingDown, Clock, ArrowRight } from 'lucide-react';
import { Link } from 'react-router-dom';

interface Signal {
    id: number;
    timestamp: string;
    token: string;
    direction: string;
    entry: number;
    tp: number;
    sl: number;
    source: string;
    status: string;
    pnl: number | null;
}

interface DashboardHistoryProps {
    signals: Signal[];
}

export const DashboardHistory: React.FC<DashboardHistoryProps> = ({ signals }) => {
    return (
        <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden">
            <div className="p-4 border-b border-slate-800 flex justify-between items-center">
                <div className="flex items-center gap-2">
                    <History size={18} className="text-slate-400" />
                    <div>
                        <h2 className="text-lg font-bold text-white">Live Operations Feed</h2>
                        <p className="text-[10px] text-slate-500 uppercase tracking-wider">Real-time execution log</p>
                    </div>
                </div>
                <Link to="/logs" className="text-xs text-indigo-400 hover:text-indigo-300 font-medium flex items-center gap-1">
                    View System Logs <ArrowRight size={12} />
                </Link>
            </div>

            <div className="overflow-x-auto">
                <table className="w-full text-left border-collapse">
                    <thead>
                        <tr className="bg-slate-950/50 text-slate-400 text-xs uppercase tracking-wider">
                            <th className="p-4 font-semibold">Time</th>
                            <th className="p-4 font-semibold">Agent / Token</th>
                            <th className="p-4 font-semibold">Action</th>
                            <th className="p-4 font-semibold text-right">Entry</th>
                            <th className="p-4 font-semibold text-center">Status</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-800">
                        {signals.length === 0 ? (
                            <tr>
                                <td colSpan={5} className="p-8 text-center text-slate-500 italic">
                                    <div className="flex flex-col items-center gap-2">
                                        <div className="relative flex h-3 w-3">
                                            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                                            <span className="relative inline-flex rounded-full h-3 w-3 bg-emerald-500"></span>
                                        </div>
                                        <span>All systems nominal. Scanning markets for high-probability setups...</span>
                                    </div>
                                </td>
                            </tr>
                        ) : (
                            signals.map((sig) => (
                                <tr key={sig.id} className="hover:bg-slate-800/20 transition-colors group">
                                    <td className="p-4 text-slate-400 font-mono text-xs whitespace-nowrap">
                                        <div className="flex items-center gap-2">
                                            <Clock className="w-3 h-3 text-slate-600" />
                                            {new Date(sig.timestamp).toLocaleTimeString()}
                                            <span className="text-slate-600 hidden md:inline">
                                                {new Date(sig.timestamp).toLocaleDateString()}
                                            </span>
                                        </div>
                                    </td>
                                    <td className="p-4">
                                        <div className="flex items-center gap-3">
                                            <div className="w-8 h-8 rounded-full bg-slate-800 flex items-center justify-center text-xs font-bold text-slate-300 border border-slate-700">
                                                {sig.token.substring(0, 3)}
                                            </div>
                                            <div>
                                                <div className="text-sm font-bold text-white">{sig.token}</div>
                                                <div className="text-xs text-slate-500">{sig.source}</div>
                                            </div>
                                        </div>
                                    </td>
                                    <td className="p-4">
                                        <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs font-bold uppercase ${sig.direction.toLowerCase() === 'long'
                                            ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                                            : 'bg-rose-500/10 text-rose-400 border border-rose-500/20'
                                            }`}>
                                            {sig.direction === 'long' ? <TrendingUp size={12} /> : <TrendingDown size={12} />}
                                            {sig.direction}
                                        </span>
                                    </td>
                                    <td className="p-4 text-right font-mono text-slate-300 text-sm">
                                        {sig.entry}
                                    </td>
                                    <td className="p-4 text-center">
                                        {sig.status && sig.status !== 'OPEN' ? (
                                            <span className={`px-2 py-1 rounded text-xs font-bold ${['WIN', 'TP'].some(s => sig.status.includes(s)) || (sig.pnl && sig.pnl > 0)
                                                ? 'text-emerald-400 bg-emerald-500/10'
                                                : 'text-rose-400 bg-rose-500/10'
                                                }`}>
                                                {sig.status} {sig.pnl ? `(${sig.pnl > 0 ? '+' : ''}${sig.pnl}R)` : ''}
                                            </span>
                                        ) : (
                                            <span className="text-xs text-slate-500 bg-slate-800/50 px-2 py-1 rounded inline-flex items-center gap-1">
                                                <div className="w-1.5 h-1.5 rounded-full bg-indigo-500 animate-pulse" />
                                                Open
                                            </span>
                                        )}
                                    </td>
                                </tr>
                            ))
                        )}
                    </tbody>
                </table>
            </div>
        </div>
    );
};
