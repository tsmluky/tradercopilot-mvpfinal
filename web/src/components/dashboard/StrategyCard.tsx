import React from 'react';
import { Activity, TrendingUp, TrendingDown, Clock, BarChart2 } from 'lucide-react';

interface StrategyCardProps {
    name: string;
    timeframe: string;
    type: string;
    winRate: number;
    pnl: number;
    status: 'active' | 'standby';
    description: string;
    isCustom?: boolean;
}

export const StrategyCard: React.FC<StrategyCardProps> = ({
    name,
    timeframe,
    type,
    winRate,
    pnl,
    status,
    description,
    isCustom
}) => {
    const isProfitable = pnl > 0;
    const statusColor = status === 'active' ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' : 'bg-slate-700/30 text-slate-400 border-slate-700';

    return (
        <div className={`bg-slate-800/50 backdrop-blur-sm border rounded-xl p-5 transition-all duration-300 group relative ${isCustom ? 'border-indigo-500/30 shadow-lg shadow-indigo-500/10' : 'border-slate-700/50 hover:border-indigo-500/30'}`}>
            {/* Custom Badge */}
            {isCustom && (
                <div className="absolute top-0 right-0 -mt-2 -mr-2 px-2 py-0.5 bg-indigo-500 text-white text-[10px] font-bold uppercase tracking-wider rounded-md shadow-md border border-indigo-400">
                    Custom
                </div>
            )}

            <div className="flex justify-between items-start mb-4">
                <div>
                    <div className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${statusColor} mb-2`}>
                        <span className={`w-1.5 h-1.5 rounded-full mr-1.5 ${status === 'active' ? 'bg-emerald-400 animate-pulse' : 'bg-slate-400'}`}></span>
                        {status.toUpperCase()}
                    </div>
                    <h3 className="text-lg font-bold text-slate-100 group-hover:text-indigo-400 transition-colors">{name}</h3>
                    <div className="flex items-center text-slate-400 text-sm mt-1">
                        <Clock className="w-3.5 h-3.5 mr-1" />
                        <span>{timeframe}</span>
                        <span className="mx-2">•</span>
                        <span>{type}</span>
                    </div>
                </div>
                <div className="bg-slate-900/50 p-2 rounded-lg border border-slate-700/50">
                    {type === 'Trend' ? <TrendingUp className="w-5 h-5 text-indigo-400" /> : <Activity className="w-5 h-5 text-purple-400" />}
                </div>
            </div>

            <p className="text-slate-400 text-sm mb-5 line-clamp-2 h-10">
                {description}
            </p>

            <div className="grid grid-cols-2 gap-3">
                <div className="bg-slate-900/40 rounded-lg p-3 border border-slate-700/30">
                    <div className="text-slate-500 text-xs font-medium mb-1">Win Rate</div>
                    <div className="text-xl font-bold text-slate-200">
                        {winRate}%
                    </div>
                </div>
                <div className="bg-slate-900/40 rounded-lg p-3 border border-slate-700/30">
                    <div className="text-slate-500 text-xs font-medium mb-1">Total PnL</div>
                    <div className={`text-xl font-bold ${isProfitable ? 'text-emerald-400' : 'text-rose-400'}`}>
                        {pnl > 0 ? '+' : ''}{pnl}R
                    </div>
                </div>
            </div>
        </div>
    );
};
