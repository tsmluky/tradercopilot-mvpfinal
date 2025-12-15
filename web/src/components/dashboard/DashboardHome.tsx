import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { StrategyCard } from './StrategyCard';
import { DashboardHistory } from './DashboardHistory';
import { Activity, DollarSign, Zap, RefreshCw, Target, Bot } from 'lucide-react';
import { api } from '../../services/api';
import { API_BASE_URL } from '../../constants';

export const DashboardHome: React.FC = () => {
    const [stats, setStats] = useState<any>(null);
    const [strategies, setStrategies] = useState<any[]>([]);
    const [recentSignals, setRecentSignals] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const [refreshing, setRefreshing] = useState(false);

    const fetchData = async () => {
        try {
            // 1. Fetch Stats
            const statsRes = await fetch(`${API_BASE_URL}/stats/summary`);
            if (statsRes.ok) {
                setStats(await statsRes.json());
            }

            // 2. Fetch Active Strategies (Personas from Marketplace)
            const stratRes = await fetch(`${API_BASE_URL}/strategies/marketplace`);
            if (stratRes.ok) {
                setStrategies(await stratRes.json());
            }

            // 3. Fetch Recent Signals (Now "Market Radar")
            const logsRes = await fetch(`${API_BASE_URL}/logs/recent?limit=20`);
            if (logsRes.ok) {
                setRecentSignals(await logsRes.json());
            }
        } catch (error) {
            console.error("Error fetching dashboard data:", error);
        } finally {
            setLoading(false);
            setRefreshing(false);
        }
    };

    useEffect(() => {
        fetchData();
        const interval = setInterval(fetchData, 30000);
        return () => clearInterval(interval);
    }, []);

    const handleRefresh = () => {
        setRefreshing(true);
        fetchData();
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center h-64">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-500"></div>
            </div>
        );
    }

    const activeStrategies = strategies.filter(s => s.is_active);
    const pnl7d = stats?.pnl_7d || 0;
    const winRate = stats?.win_rate_24h ? Math.round(stats.win_rate_24h * 100) : 0;

    return (
        <div className="space-y-8 pb-12">
            {/* 1. Header & Global Metrics */}
            <div className="flex flex-col xl:flex-row gap-6 xl:items-center justify-between">
                <div>
                    <h1 className="text-2xl font-bold text-white flex items-center gap-2">
                        <Zap className="text-amber-400 fill-current" size={24} />
                        Command Center
                    </h1>
                    <p className="text-slate-400 text-sm">Real-time trading operations overview.</p>
                </div>

                <div className="flex flex-wrap gap-4">
                    {/* Metric: PnL */}
                    <div className="bg-slate-900/80 border border-slate-800 p-3 px-5 rounded-xl flex items-center gap-4 min-w-[160px] backdrop-blur-md">
                        <div className={`p-2 rounded-full ${pnl7d >= 0 ? 'bg-emerald-500/10 text-emerald-400' : 'bg-rose-500/10 text-rose-400'}`}>
                            <DollarSign size={20} />
                        </div>
                        <div>
                            <div className="text-[10px] text-slate-500 uppercase font-bold tracking-wider">7d Net PnL</div>
                            <div className={`text-xl font-mono font-bold ${pnl7d >= 0 ? 'text-white' : 'text-rose-400'}`}>
                                {pnl7d > 0 ? '+' : ''}{pnl7d} R
                            </div>
                        </div>
                    </div>

                    {/* Metric: Active Agents */}
                    <div className="bg-slate-900/80 border border-slate-800 p-3 px-5 rounded-xl flex items-center gap-4 min-w-[160px] backdrop-blur-md">
                        <div className="p-2 rounded-full bg-indigo-500/10 text-indigo-400">
                            <Activity size={20} />
                        </div>
                        <div>
                            <div className="text-[10px] text-slate-500 uppercase font-bold tracking-wider">Active Fleet</div>
                            <div className="text-xl font-mono font-bold text-white">
                                {activeStrategies.length}
                            </div>
                        </div>
                    </div>

                    {/* Metric: Win Rate */}
                    <div className="bg-slate-900/80 border border-slate-800 p-3 px-5 rounded-xl flex items-center gap-4 min-w-[160px] backdrop-blur-md">
                        <div className={`p-2 rounded-full ${winRate >= 50 ? 'bg-emerald-500/10 text-emerald-400' : 'bg-amber-500/10 text-amber-400'}`}>
                            <Target size={20} />
                        </div>
                        <div>
                            <div className="text-[10px] text-slate-500 uppercase font-bold tracking-wider">Win Rate (24h)</div>
                            <div className="text-xl font-mono font-bold text-white">
                                {winRate}%
                            </div>
                        </div>
                    </div>

                    <button
                        onClick={handleRefresh}
                        className={`p-3 rounded-xl bg-slate-800 text-slate-400 hover:text-white hover:bg-slate-700 transition-all ${refreshing ? 'animate-spin' : ''}`}
                    >
                        <RefreshCw size={20} />
                    </button>
                </div>
            </div>

            {/* 2. My Active Agents (Hero Section) */}
            <div className="space-y-4">
                <div className="flex items-center justify-between">
                    <h2 className="text-lg font-bold text-slate-200 flex items-center gap-2">
                        <Activity className="text-indigo-400" size={18} />
                        Active Agents
                    </h2>
                </div>

                {activeStrategies.length === 0 ? (
                    <div className="p-8 border border-dashed border-slate-800 rounded-xl bg-slate-900/50 text-center">
                        <p className="text-slate-500 mb-4">No agents are currently running.</p>
                        <a href="/strategies" className="text-indigo-400 hover:text-indigo-300 font-bold text-sm">Deploy an Agent from Marketplace &rarr;</a>
                    </div>
                ) : (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
                        {activeStrategies.map((strat, idx) => (
                            <Link to={`/strategies/${strat.id}`} key={strat.id || idx} className="block group">
                                <StrategyCard
                                    name={strat.name}
                                    timeframe={strat.timeframe}
                                    type={strat.symbol}
                                    winRate={parseInt(strat.win_rate) || 0}
                                    pnl={0} // TODO: Add per-strategy PnL in future
                                    status={'active'}
                                    description={strat.description}
                                    isCustom={strat.is_custom}
                                />
                            </Link>
                        ))}
                    </div>
                )}
            </div>

            {/* 3. Global History (Fleet Activity) */}
            <DashboardHistory signals={recentSignals} />
        </div>
    );
};
