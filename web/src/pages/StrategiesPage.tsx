import React, { useEffect, useState } from 'react';
import { StrategyCard } from '../components/dashboard/StrategyCard';
import { API_BASE_URL } from '../constants';
import { RefreshCw, Play, X, ArrowRight } from 'lucide-react';

interface StrategySignal {
    token: string;
    direction: string;
    entry: number;
    tp: number;
    sl: number;
    confidence: number;
}

export const StrategiesPage: React.FC = () => {
    const [strategies, setStrategies] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const [executingId, setExecutingId] = useState<string | null>(null);
    const [scanResults, setScanResults] = useState<{ strategy: string, signals: StrategySignal[] } | null>(null);

    const fetchStrategies = async () => {
        setLoading(true);
        try {
            // 1. Trigger evaluation to update stats first
            await fetch(`${API_BASE_URL}/analyze/evaluate`, { method: 'POST' });

            // 2. Fetch updated strategies
            const res = await fetch(`${API_BASE_URL}/strategies`);
            if (res.ok) {
                setStrategies(await res.json());
            }
        } catch (error) {
            console.error("Error fetching strategies:", error);
        } finally {
            setLoading(false);
        }
    };

    const handleRunStrategy = async (strategyId: string, timeframe: string) => {
        setExecutingId(strategyId);
        try {
            const res = await fetch(`${API_BASE_URL}/strategies/${strategyId}/execute`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    tokens: ["BTC", "ETH", "SOL"],
                    timeframe: timeframe || "1h",
                    context: {}
                })
            });
            const data = await res.json();

            if (res.ok) {
                setScanResults({
                    strategy: strategyId,
                    signals: data.signals || []
                });
            } else {
                alert(`Error: ${data.detail}`);
            }
        } catch (error) {
            console.error("Error running strategy:", error);
            alert("Failed to execute strategy command.");
        } finally {
            setExecutingId(null);
        }
    };

    useEffect(() => {
        fetchStrategies();
    }, []);

    return (
        <div className="space-y-6 relative">
            <div className="flex justify-between items-center">
                <div>
                    <h2 className="text-2xl font-bold text-slate-100">Strategy Portfolio</h2>
                    <p className="text-slate-400">Manage and monitor your automated trading strategies.</p>
                </div>
                <button
                    onClick={fetchStrategies}
                    className="p-2 rounded-lg bg-slate-800/50 text-slate-400 hover:text-white transition-colors"
                >
                    <RefreshCw className="w-5 h-5" />
                </button>
            </div>

            {loading ? (
                <div className="flex justify-center py-12">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-500"></div>
                </div>
            ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {strategies.map((strat, idx) => (
                        <div key={idx} className="relative group">
                            <StrategyCard
                                name={strat.name}
                                timeframe={strat.default_timeframe}
                                type={strat.mode === 'SCALPING' ? 'Scalping' : 'Trend'}
                                winRate={Math.round(strat.win_rate * 100)}
                                pnl={0}
                                status={strat.enabled ? 'active' : 'standby'}
                                description={strat.description}
                            />
                            {/* Overlay Actions */}
                            <div className="absolute top-4 right-4 opacity-0 group-hover:opacity-100 transition-opacity">
                                <button
                                    onClick={() => handleRunStrategy(strat.id, strat.default_timeframe)}
                                    disabled={!!executingId}
                                    className={`p-2 rounded-lg text-white shadow-lg transition-colors ${executingId === strat.id
                                        ? 'bg-slate-600 cursor-not-allowed'
                                        : 'bg-indigo-600 hover:bg-indigo-500'
                                        }`}
                                    title="Run Live Scan"
                                >
                                    {executingId === strat.id ? (
                                        <div className="animate-spin rounded-full h-4 w-4 border-2 border-white/30 border-t-white"></div>
                                    ) : (
                                        <Play className="w-4 h-4 fill-current" />
                                    )}
                                </button>
                            </div>
                        </div>
                    ))}
                </div>
            )}

            {/* Scan Results Modal */}
            {scanResults && (
                <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
                    <div className="bg-slate-900 border border-slate-700 rounded-xl shadow-2xl max-w-2xl w-full flex flex-col max-h-[80vh]">
                        <div className="p-4 border-b border-slate-800 flex justify-between items-center sticky top-0 bg-slate-900 rounded-t-xl z-10">
                            <div>
                                <h3 className="text-lg font-bold text-white flex items-center gap-2">
                                    <Play className="w-4 h-4 text-emerald-400" />
                                    Live Scan Results
                                </h3>
                                <p className="text-xs text-slate-400 uppercase tracking-wider font-mono mt-1">
                                    Strategy: <span className="text-indigo-400">{scanResults.strategy}</span>
                                </p>
                            </div>
                            <button
                                onClick={() => setScanResults(null)}
                                className="p-2 hover:bg-slate-800 rounded-lg text-slate-400 transition-colors"
                            >
                                <X className="w-5 h-5" />
                            </button>
                        </div>

                        <div className="p-6 overflow-y-auto space-y-4">
                            {scanResults.signals.length === 0 ? (
                                <div className="text-center py-8 text-slate-500">
                                    <p>No active signals found for ths strategy right now.</p>
                                    <p className="text-sm mt-2">Try checking a different timeframe or asset.</p>
                                </div>
                            ) : (
                                <div className="grid gap-4">
                                    {scanResults.signals.map((sig, i) => (
                                        <div key={i} className="bg-slate-800/50 rounded-lg p-4 border border-slate-700 hover:border-indigo-500/50 transition-colors">
                                            <div className="flex justify-between items-start mb-2">
                                                <div className="flex items-center gap-3">
                                                    <span className="font-bold text-xl text-white">{sig.token}</span>
                                                    <span className={`px-2 py-0.5 rounded text-xs font-bold uppercase tracking-wider ${sig.direction === 'long'
                                                        ? 'bg-emerald-500/20 text-emerald-400'
                                                        : 'bg-rose-500/20 text-rose-400'
                                                        }`}>
                                                        {sig.direction}
                                                    </span>
                                                </div>
                                                <div className="text-right">
                                                    <span className="text-xs text-slate-500 block">Entry Point</span>
                                                    <span className="font-mono text-white">{sig.entry}</span>
                                                </div>
                                            </div>

                                            <div className="flex items-center gap-4 text-sm text-slate-400 mt-3 font-mono">
                                                <div className="flex items-center gap-1">
                                                    <span className="text-xs text-slate-600">ATP</span>
                                                    <span className="text-emerald-400">{sig.tp}</span>
                                                </div>
                                                <div className="flex items-center gap-1">
                                                    <span className="text-xs text-slate-600">SL</span>
                                                    <span className="text-rose-400">{sig.sl}</span>
                                                </div>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            )}
                        </div>

                        <div className="p-4 border-t border-slate-800 bg-slate-900/50 rounded-b-xl flex justify-end">
                            <button
                                onClick={() => setScanResults(null)}
                                className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-sm font-medium transition-colors"
                            >
                                Done
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};
