import React, { useEffect, useState } from 'react';
import { StrategyCard } from './StrategyCard';
import { ArrowUpRight, ArrowDownRight, Activity, DollarSign, Target, Zap, RefreshCw, Plus } from 'lucide-react';
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

            // 2. Fetch Strategies
            const stratRes = await fetch(`${API_BASE_URL}/strategies`);
            if (stratRes.ok) {
                setStrategies(await stratRes.json());
            }

            // 3. Fetch Recent Signals
            const logsRes = await fetch(`${API_BASE_URL}/logs/recent?limit=10`);
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
        const interval = setInterval(fetchData, 30000); // Auto-refresh every 30s
        return () => clearInterval(interval);
    }, []);

    const handleRefresh = () => {
        setRefreshing(true);
        fetchData();
    };

    const handleRequestSignal = async () => {
        // Simple implementation for now - could open a modal
        alert("To request a signal manually, go to the 'Live Signals' tab or use the CLI.");
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center h-64">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-500"></div>
            </div>
        );
    }

    return (
        <div className="space-y-8">
            {/* Header Actions */}
            <div className="flex justify-end gap-3">
                <button
                    onClick={handleRefresh}
                    className={`p-2 rounded-lg bg-slate-800/50 text-slate-400 hover:text-white hover:bg-slate-700/50 transition-all ${refreshing ? 'animate-spin' : ''}`}
                >
                    <RefreshCw className="w-4 h-4" />
                </button>
                <button
                    onClick={handleRequestSignal}
                    className="flex items-center gap-2 px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white font-medium text-sm transition-all shadow-lg shadow-indigo-500/20"
                >
                    <Plus className="w-4 h-4" />
                    Request Analysis
                </button>
            </div>

            {/* KPI Stats Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <KpiCard
                    title="Total PnL (24h)"
                    value={stats?.win_rate_24h ? `${(stats.win_rate_24h * 100).toFixed(1)}% WR` : "N/A"}
                    trend={`${stats?.signals_evaluated_24h || 0} evaluated`}
                    trendUp={true}
                    icon={DollarSign}
                    color="emerald"
                    trendLabel="in 24h"
                />
                <KpiCard
                    title="Total Signals"
                    value={stats?.signals_lite_24h || 0}
                    trend={`${stats?.open_signals || 0} open`}
                    trendUp={true}
                    icon={Activity}
                    color="blue"
                    trendLabel="waiting"
                />
                <KpiCard
                    title="Active Strategies"
                    value={strategies.filter(s => s.enabled).length}
                    trend="of 9 total"
                    trendUp={true}
                    icon={Target}
                    color="indigo"
                    trendLabel=""
                />
                <KpiCard
                    title="System Status"
                    value="Online"
                    trend="Scheduler Active"
                    trendUp={true}
                    icon={Zap}
                    color="amber"
                    trendLabel=""
                />
            </div>

            {/* Strategies Section */}
            <div>
                <div className="flex items-center justify-between mb-4">
                    <h2 className="text-xl font-bold text-slate-100">Active Strategies</h2>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                    {strategies.filter(s => s.enabled).map((strat, idx) => (
                        <StrategyCard
                            key={idx}
                            name={strat.name}
                            timeframe={strat.default_timeframe}
                            type={strat.mode === 'SCALPING' ? 'Scalping' : 'Trend'} // Simple mapping
                            winRate={Math.round(strat.win_rate * 100)}
                            pnl={0} // Backend doesn't send PnL per strategy yet in list
                            status={strat.enabled ? 'active' : 'standby'}
                            description={strat.description}
                        />
                    ))}
                </div>
            </div>

            {/* Recent Activity & Chart Section */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Live Signals Feed */}
                <div className="lg:col-span-3 bg-slate-900/50 border border-slate-800/50 rounded-xl p-6 backdrop-blur-sm">
                    <h3 className="text-lg font-bold text-slate-100 mb-4">Live Signals Feed</h3>
                    <div className="space-y-3">
                        {recentSignals.length === 0 ? (
                            <div className="text-center py-8 text-slate-500">No signals generated yet.</div>
                        ) : (
                            recentSignals.map((signal) => (
                                <div key={signal.id} className="flex items-center justify-between p-3 rounded-lg bg-slate-950/50 border border-slate-800/50 hover:border-slate-700 transition-colors">
                                    <div className="flex items-center gap-4">
                                        <div className={`w-10 h-10 rounded-lg flex items-center justify-center text-xs font-bold ${signal.token === 'BTC' ? 'bg-orange-500/10 text-orange-500' :
                                                signal.token === 'ETH' ? 'bg-purple-500/10 text-purple-500' :
                                                    'bg-cyan-500/10 text-cyan-500'
                                            }`}>
                                            {signal.token}
                                        </div>
                                        <div>
                                            <div className="flex items-center gap-2">
                                                <span className={`text-sm font-bold ${signal.direction === 'LONG' ? 'text-emerald-400' : 'text-rose-400'}`}>
                                                    {signal.direction}
                                                </span>
                                                <span className="text-slate-300 text-sm font-mono">@ {signal.entry}</span>
                                                <span className="text-xs text-slate-500 bg-slate-800 px-1.5 py-0.5 rounded">{signal.source}</span>
                                            </div>
                                            <div className="flex items-center gap-2 text-xs text-slate-500 mt-1">
                                                <span>{new Date(signal.timestamp).toLocaleTimeString()}</span>
                                                <span>•</span>
                                                <span>{signal.timeframe}</span>
                                            </div>
                                        </div>
                                    </div>
                                    <div className="text-right">
                                        <StatusBadge status={signal.status || 'OPEN'} />
                                        {signal.pnl !== null && (
                                            <div className={`text-xs font-mono mt-1 ${signal.pnl > 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                                                {signal.pnl > 0 ? '+' : ''}{(signal.pnl * 100).toFixed(2)}%
                                            </div>
                                        )}
                                    </div>
                                </div>
                            ))
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
};

// Helper Components (Same as before)
const KpiCard = ({ title, value, trend, trendUp, icon: Icon, color, trendLabel }: any) => {
    const colorMap: any = {
        emerald: "text-emerald-400 bg-emerald-500/10 border-emerald-500/20",
        indigo: "text-indigo-400 bg-indigo-500/10 border-indigo-500/20",
        amber: "text-amber-400 bg-amber-500/10 border-amber-500/20",
        blue: "text-blue-400 bg-blue-500/10 border-blue-500/20",
    };

    return (
        <div className="bg-slate-900/50 border border-slate-800/50 rounded-xl p-5 backdrop-blur-sm hover:border-slate-700 transition-all">
            <div className="flex justify-between items-start mb-2">
                <span className="text-slate-400 text-sm font-medium">{title}</span>
                <div className={`p-2 rounded-lg ${colorMap[color]}`}>
                    <Icon className="w-4 h-4" />
                </div>
            </div>
            <div className="text-2xl font-bold text-slate-100 mb-1">{value}</div>
            {trend && (
                <div className="flex items-center gap-1 text-xs">
                    <span className={`flex items-center font-medium ${trendUp ? 'text-emerald-400' : 'text-rose-400'}`}>
                        {trendUp ? <ArrowUpRight className="w-3 h-3 mr-0.5" /> : <ArrowDownRight className="w-3 h-3 mr-0.5" />}
                        {trend}
                    </span>
                    <span className="text-slate-600 ml-1">{trendLabel}</span>
                </div>
            )}
        </div>
    );
};

const StatusBadge = ({ status }: { status: string }) => {
    const styles: any = {
        OPEN: "bg-blue-500/10 text-blue-400 border-blue-500/20",
        WIN: "bg-emerald-500/10 text-emerald-400 border-emerald-500/20",
        LOSS: "bg-rose-500/10 text-rose-400 border-rose-500/20",
        BE: "bg-slate-500/10 text-slate-400 border-slate-500/20",
    };

    // Normalize status
    let normalized = status.toUpperCase();
    if (normalized.includes('HIT-TP')) normalized = 'WIN';
    if (normalized.includes('HIT-SL')) normalized = 'LOSS';

    return (
        <span className={`px-2 py-0.5 rounded text-[10px] font-bold border ${styles[normalized] || styles.OPEN}`}>
            {normalized}
        </span>
    );
};
