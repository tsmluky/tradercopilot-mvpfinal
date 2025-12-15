import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { StrategyCard } from './StrategyCard';
import { DashboardHistory } from './DashboardHistory';
import { Activity, DollarSign, Zap, RefreshCw, Target, Bot } from 'lucide-react';
import { api } from '../../services/api';
import { API_BASE_URL } from '../../constants';

import { MetricCard } from './MetricCard';

export const DashboardHome: React.FC = () => {
    const [globalStats, setStats] = useState<any>({
        win_rate: 0,
        win_rate_change: 0,
        pnl_7d: 0,
        pnl_7d_change: 0,
        active_fleet: 6
    });
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
                    <MetricCard
                        label="7d Net PnL"
                        value={`${globalStats?.pnl_7d > 0 ? '+' : ''}${globalStats?.pnl_7d || 0} R`}
                        trend={globalStats?.pnl_7d_change || 0}
                        icon={DollarSign}
                    />

                    {/* Metric: Active Agents */}
                    <MetricCard
                        label="Active Agents"
                        value={activeStrategies.length.toString()}
                        trend={0}
                        icon={Activity}
                    />

                    {/* Metric: Win Rate */}
                    <MetricCard
                        label="Win Rate (24h)"
                        value={`${globalStats?.win_rate || 0}%`}
                        trend={globalStats?.win_rate_change || 0}
                        icon={Target}
                    />

                    <button
                        onClick={handleRefresh}
                        className={`p-3 rounded-xl bg-slate-800 border border-slate-700 text-slate-400 hover:text-white hover:bg-slate-700 transition-colors ${refreshing ? 'animate-spin' : ''}`}
                    >
                        <RefreshCw size={20} />
                    </button>
                </div>
            </div>

            {/* Active Strategies Grid */}
            <div className="mb-8">
                <h2 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                    <Activity className="text-indigo-400" size={20} />
                    Active Agents
                </h2>
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
