import React from 'react';
import { TrendingUp, TrendingDown, Clock, Activity, Crosshair, Lock } from 'lucide-react';
import { Link } from 'react-router-dom';
import { formatPrice } from '../../utils/format';

interface ScannerSignalCardProps {
    signal: any;
    onAnalyze: (signal: any) => void;
}

export const ScannerSignalCard: React.FC<ScannerSignalCardProps> = ({ signal, onAnalyze }) => {
    // ... existing logic ...
    const isLong = signal.direction.toUpperCase() === 'LONG';
    const isWin = signal.status?.includes('WIN') || signal.status?.includes('TP');
    const isLoss = signal.status?.includes('LOSS') || signal.status?.includes('SL');
    const isOpen = signal.status === 'OPEN';

    // Fix Timezone: Ensure timestamp is treated as UTC
    const safeTimestamp = signal.timestamp.endsWith('Z') ? signal.timestamp : `${signal.timestamp}Z`;

    const timeAgo = (dateStr: string) => {
        if (!dateStr) return '';
        const diff = Date.now() - new Date(dateStr).getTime();

        // Handle "Future" times or slight clock skews
        if (diff < 0) return 'Just now';

        const mins = Math.floor(diff / 60000);
        if (mins < 1) return 'Just now';

        if (mins < 60) return `${mins}m ago`;
        const hours = Math.floor(mins / 60);
        if (hours < 24) return `${hours}h ago`;
        return `${Math.floor(hours / 24)}d ago`;
    };

    return (
        <div className="group relative bg-slate-900 border border-slate-800 rounded-xl overflow-hidden hover:border-indigo-500/50 transition-all duration-300 hover:shadow-lg hover:shadow-indigo-500/10">

            {/* Locked Overlay */}
            {signal.locked && (
                <div className="absolute inset-0 z-20 bg-slate-900/60 backdrop-blur-[6px] flex flex-col items-center justify-center p-6 text-center animate-in fade-in duration-500">
                    <div className="w-12 h-12 rounded-full bg-slate-800 flex items-center justify-center mb-3 shadow-xl border border-slate-700">
                        <Lock size={24} className="text-amber-400" />
                    </div>
                    <h3 className="text-white font-bold mb-1">Signal Locked</h3>
                    <p className="text-xs text-slate-400 mb-4 px-2">
                        Upgrade your plan to see {signal.timeframe} opportunities like this.
                    </p>
                    <Link to="/membership" className="px-5 py-2 rounded-lg bg-amber-500 hover:bg-amber-400 text-slate-900 font-bold text-xs transition-colors shadow-lg shadow-amber-500/20">
                        Unlock Now
                    </Link>
                </div>
            )}

            {/* Header */}
            <div className="p-4 border-b border-slate-800/50 flex justify-between items-start bg-slate-800/20">
                <div className="flex items-center gap-3">
                    <div className="p-2 bg-slate-800 rounded-lg">
                        <span className="font-bold text-slate-200">{signal.token}</span>
                    </div>
                    <div>
                        <div className="flex items-center gap-2">
                            <span className="text-xs font-bold text-slate-400">{signal.token}USDT</span>
                            <span className="text-[10px] px-1.5 py-0.5 rounded bg-slate-800 text-slate-500 border border-slate-700">
                                {timeAgo(safeTimestamp)}
                            </span>
                        </div>
                        <span className="text-xs text-slate-500 flex items-center gap-2">
                            {signal.timeframe}
                            <span className={`text-[9px] font-bold px-1.5 rounded border ${['1m', '5m', '15m', '30m'].includes(signal.timeframe) ? 'border-amber-500/30 text-amber-500 bg-amber-500/10' :
                                ['1h', '4h'].includes(signal.timeframe) ? 'border-blue-500/30 text-blue-500 bg-blue-500/10' :
                                    'border-purple-500/30 text-purple-500 bg-purple-500/10'
                                }`}>
                                {['1m', '5m', '15m', '30m'].includes(signal.timeframe) ? 'SCALP' :
                                    ['1h', '4h'].includes(signal.timeframe) ? 'SWING' : 'MACRO'}
                            </span>
                            • {new Date(safeTimestamp).toLocaleTimeString()}
                        </span>
                    </div>
                </div>
            </div>

            <div className={`p-5 space-y-4 ${signal.locked ? 'opacity-20 blur-sm select-none' : ''}`}>
                {/* Context & Confidence */}
                <div className="grid grid-cols-3 gap-2 py-3 border-t border-b border-slate-800/50 bg-slate-800/20 rounded-lg">
                    <div className="text-center border-r border-slate-800/50 px-2">
                        <div className="text-[10px] text-slate-500 uppercase tracking-wider mb-1">Entry</div>
                        <div className="font-mono text-white font-bold text-sm">
                            {formatPrice(signal.entry)}
                        </div>
                    </div>
                    <div className="text-center border-r border-slate-800/50 px-2">
                        <div className="text-[10px] text-slate-500 uppercase tracking-wider mb-1">TP</div>
                        <div className="font-mono text-emerald-400 font-bold text-sm">
                            {formatPrice(signal.tp)}
                        </div>
                    </div>
                    <div className="text-center px-2">
                        <div className="text-[10px] text-slate-500 uppercase tracking-wider mb-1">SL</div>
                        <div className="font-mono text-rose-400 font-bold text-sm">
                            {formatPrice(signal.sl)}
                        </div>
                    </div>
                </div>

                {/* Main signal info (reduced to just direction header) */}
                <div className="flex items-center gap-2 pb-2">
                    {isLong ? <TrendingUp size={20} className="text-emerald-400" /> : <TrendingDown size={20} className="text-rose-400" />}
                    <span className={`text-xl font-black ${isLong ? 'text-emerald-400' : 'text-rose-400'} tracking-tight`}>
                        {signal.direction.toUpperCase()}
                    </span>
                </div>

                {/* Rationale / Context */}
                {/* Context & Confidence */}
                <div className="space-y-2">
                    <div className="flex justify-between items-center text-xs">
                        <span className="text-slate-500 font-medium">AI Confidence</span>
                        <span className={`font-bold ${(signal.confidence || 0) >= 0.8 ? 'text-emerald-400' :
                            (signal.confidence || 0) >= 0.5 ? 'text-yellow-400' : 'text-slate-400'
                            }`}>
                            {Math.round((signal.confidence || 0) * 100)}%
                        </span>
                    </div>

                    {/* Progress Bar */}
                    <div className="w-full h-1.5 bg-slate-800 rounded-full overflow-hidden">
                        <div
                            className={`h-full rounded-full transition-all duration-500 ${(signal.confidence || 0) >= 0.8 ? 'bg-emerald-500' :
                                (signal.confidence || 0) >= 0.5 ? 'bg-yellow-500' : 'bg-slate-600'
                                }`}
                            style={{ width: `${Math.round((signal.confidence || 0) * 100)}%` }}
                        />
                    </div>

                    <p className="text-[11px] text-slate-400 line-clamp-2 leading-relaxed pt-1 border-t border-slate-800/50 mt-2">
                        {signal.rationale || "Technical signal detected based on active strategy parameters and market conditions."}
                    </p>
                </div>

                {/* Footer Actions */}
                <div className="pt-2 flex items-center justify-between">
                    {/* Status Pill */}
                    <div>
                        {isOpen ? (
                            <span className="inline-flex items-center gap-1.5 px-2 py-1 rounded text-[10px] font-bold bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
                                <Activity size={10} />
                                ACTIVE
                            </span>
                        ) : (
                            <span className={`inline-flex items-center px-2 py-1 rounded text-[10px] font-bold border ${isWin ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' :
                                isLoss ? 'bg-rose-500/10 text-rose-400 border-rose-500/20' :
                                    'bg-slate-500/10 text-slate-400 border-slate-500/20'
                                }`}>
                                {signal.status}
                            </span>
                        )}
                    </div>

                    {/* Analyze Button */}
                    <button
                        onClick={() => onAnalyze(signal)}
                        className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-bold transition-all border border-slate-700 hover:border-slate-600"
                    >
                        <Crosshair size={14} className="text-indigo-400" />
                        Analyze Risk (PRO)
                    </button>
                </div>
            </div>
        </div>
    );
};
