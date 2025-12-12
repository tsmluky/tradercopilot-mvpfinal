
import React, { useState } from 'react';
import { Play, TrendingUp, TrendingDown, Clock, Download, Info } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Legend } from 'recharts';

export const BacktestPage: React.FC = () => {
    const [loading, setLoading] = useState(false);
    const [params, setParams] = useState({
        token: 'SOL',
        timeframe: '1h',
        days: 30,
        strategy: 'rsi_divergence',
        capital: 1000
    });

    const [results, setResults] = useState<any>(null);
    const [error, setError] = useState('');

    const runBacktest = async () => {
        setLoading(true);
        setError('');
        setResults(null);

        try {
            const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

            const res = await fetch(`${API_URL}/backtest/run`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    strategy_id: params.strategy,
                    token: params.token,
                    timeframe: params.timeframe,
                    days: Number(params.days),
                    initial_capital: Number(params.capital)
                })
            });

            if (!res.ok) {
                throw new Error(`Error ${res.status}: ${await res.text()}`);
            }

            const data = await res.json();
            setResults(data);
        } catch (err: any) {
            setError(err.message || "Error desconocido al ejecutar backtest");
        } finally {
            setLoading(false);
        }
    };

    // Preparar datos para el gráfico
    // El backend ahora devuelve "curve" que tiene la historia día a día
    const chartData = results?.curve || [];

    // Custom Tooltip
    const CustomTooltip = ({ active, payload, label }: any) => {
        if (active && payload && payload.length) {
            return (
                <div className="bg-[#1e293b] border border-slate-700 p-3 rounded shadow-xl">
                    <p className="text-slate-400 text-xs mb-1">{label}</p>
                    {payload.map((p: any, idx: number) => (
                        <p key={idx} style={{ color: p.color }} className="text-sm font-mono">
                            {p.name}: ${Number(p.value).toFixed(2)}
                        </p>
                    ))}
                    {payload[0].payload.price && (
                        <p className="text-xs text-slate-500 mt-1 border-t border-slate-700 pt-1">
                            Price: ${Number(payload[0].payload.price).toFixed(2)}
                        </p>
                    )}
                </div>
            );
        }
        return null;
    };

    return (
        <div className="p-6 space-y-8 min-h-screen bg-[#020617] text-slate-100">

            {/* Header */}
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div>
                    <h1 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-indigo-400 to-cyan-400">
                        Backtesting & Validación
                    </h1>
                    <p className="text-slate-400 mt-2">
                        Simula tus estrategias con datos históricos reales vs Buy & Hold.
                    </p>
                </div>
            </div>

            {/* Controls */}
            <div className="bg-[#0f172a] p-6 rounded-xl border border-slate-800 shadow-lg">
                <div className="grid grid-cols-1 md:grid-cols-5 gap-4 items-end">
                    <div>
                        <label className="block text-sm text-slate-400 mb-1">Estrategia</label>
                        <select
                            className="w-full bg-[#1e293b] border border-slate-700 rounded-lg px-3 py-2 focus:ring-2 focus:ring-indigo-500 outline-none"
                            value={params.strategy}
                            onChange={(e) => setParams({ ...params, strategy: e.target.value })}
                        >
                            <option value="rsi_divergence">RSI Divergence</option>
                            <option value="ma_cross">MA Cross</option>
                            <option value="bb_mean_reversion">Bollinger Mean Rev</option>
                            <option value="donchian">Donchian Breakout</option>
                        </select>
                    </div>

                    <div>
                        <label className="block text-sm text-slate-400 mb-1">Token</label>
                        <select
                            className="w-full bg-[#1e293b] border border-slate-700 rounded-lg px-3 py-2 focus:ring-2 focus:ring-indigo-500 outline-none"
                            value={params.token}
                            onChange={(e) => setParams({ ...params, token: e.target.value })}
                        >
                            <option value="BTC">Bitcoin (BTC)</option>
                            <option value="ETH">Ethereum (ETH)</option>
                            <option value="SOL">Solana (SOL)</option>
                        </select>
                    </div>

                    <div>
                        <label className="block text-sm text-slate-400 mb-1">Timeframe</label>
                        <select
                            className="w-full bg-[#1e293b] border border-slate-700 rounded-lg px-3 py-2 focus:ring-2 focus:ring-indigo-500 outline-none"
                            value={params.timeframe}
                            onChange={(e) => setParams({ ...params, timeframe: e.target.value })}
                        >
                            <option value="15m">15 Minutos</option>
                            <option value="1h">1 Hora</option>
                            <option value="4h">4 Horas</option>
                        </select>
                    </div>

                    <div>
                        <label className="block text-sm text-slate-400 mb-1">Histórico (Días)</label>
                        <select
                            className="w-full bg-[#1e293b] border border-slate-700 rounded-lg px-3 py-2 focus:ring-2 focus:ring-indigo-500 outline-none"
                            value={params.days}
                            onChange={(e) => setParams({ ...params, days: Number(e.target.value) })}
                        >
                            <option value={7}>7 Días (Rápido)</option>
                            <option value={30}>30 Días (Mes)</option>
                            <option value={90}>90 Días (Trimestre)</option>
                        </select>
                    </div>

                    <button
                        onClick={runBacktest}
                        disabled={loading}
                        className="w-full bg-indigo-600 hover:bg-indigo-500 text-white font-semibold py-2 px-4 rounded-lg transition-all flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        {loading ? (
                            <Clock className="animate-spin h-5 w-5" />
                        ) : (
                            <Play className="h-5 w-5" />
                        )}
                        {loading ? 'Simulando...' : 'Ejecutar'}
                    </button>
                </div>
                {error && <p className="text-red-400 mt-4 text-sm bg-red-900/20 p-2 rounded border border-red-900">{error}</p>}
            </div>

            {/* Results View */}
            {results && (
                <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">

                    {/* Metrics Grid */}
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                        <div className="bg-[#0f172a] p-4 rounded-xl border border-slate-800 relative overflow-hidden">
                            <div className="relative z-10">
                                <p className="text-slate-400 text-sm">Strategy PnL</p>
                                <p className={`text-2xl font-bold ${results.metrics.total_pnl >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                                    {results.metrics.total_pnl >= 0 ? '+' : ''}{results.metrics.total_pnl} USDT
                                </p>
                                <p className="text-xs text-slate-500 mt-1 flex items-center gap-1">
                                    <Info size={12} /> Vs Buy & Hold:
                                    <span className={results.metrics.buy_hold_pnl > results.metrics.total_pnl ? 'text-red-400' : 'text-green-400'}>
                                        ${results.metrics.buy_hold_pnl}
                                    </span>
                                </p>
                            </div>
                            {/* Background decoration */}
                            <div className={`absolute -right-4 -bottom-4 w-24 h-24 rounded-full opacity-10 ${results.metrics.total_pnl >= 0 ? 'bg-green-500' : 'bg-red-500'}`}></div>
                        </div>

                        <div className="bg-[#0f172a] p-4 rounded-xl border border-slate-800">
                            <p className="text-slate-400 text-sm">Win Rate</p>
                            <p className="text-2xl font-bold text-indigo-400">{results.metrics.win_rate}%</p>
                            <p className="text-xs text-slate-500 mt-1">
                                {results.metrics.total_trades} Trades
                            </p>
                        </div>
                        <div className="bg-[#0f172a] p-4 rounded-xl border border-slate-800">
                            <p className="text-slate-400 text-sm">Best Trade</p>
                            <p className="text-2xl font-bold text-green-400">+{results.metrics.best_trade}</p>
                        </div>
                        <div className="bg-[#0f172a] p-4 rounded-xl border border-slate-800">
                            <p className="text-slate-400 text-sm">Worst Trade</p>
                            <p className="text-2xl font-bold text-red-400">{results.metrics.worst_trade}</p>
                        </div>
                    </div>

                    {/* Chart */}
                    <div className="bg-[#0f172a] p-6 rounded-xl border border-slate-800 h-[450px]">
                        <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                            <TrendingUp className="h-5 w-5 text-indigo-400" /> Benchmark (Buy & Hold) vs Strategy
                        </h3>
                        <ResponsiveContainer width="100%" height="100%">
                            <LineChart data={chartData} margin={{ top: 5, right: 20, left: 10, bottom: 5 }}>
                                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                                <XAxis
                                    dataKey="time"
                                    stroke="#64748b"
                                    tick={{ fontSize: 12 }}
                                    minTickGap={50}
                                />
                                <YAxis stroke="#64748b" domain={['auto', 'auto']} />
                                <Tooltip content={<CustomTooltip />} />
                                <Legend />
                                <Line
                                    name="Strategy Equity"
                                    type="monotone"
                                    dataKey="strategy_equity"
                                    stroke="#818cf8"
                                    strokeWidth={3}
                                    dot={false}
                                />
                                <Line
                                    name="Buy & Hold"
                                    type="monotone"
                                    dataKey="buy_hold_equity"
                                    stroke="#64748b"
                                    strokeWidth={2}
                                    strokeDasharray="5 5"
                                    dot={false}
                                />
                            </LineChart>
                        </ResponsiveContainer>
                    </div>

                    {/* Trades Table */}
                    <div className="bg-[#0f172a] rounded-xl border border-slate-800 overflow-hidden">
                        <div className="p-4 border-b border-slate-800 flex justify-between items-center">
                            <h3 className="text-lg font-semibold">Historial de Trades</h3>
                            <span className="text-xs text-slate-500 bg-slate-900 px-2 py-1 rounded">Last 50</span>
                        </div>
                        <div className="overflow-x-auto">
                            <table className="w-full text-left text-sm text-slate-400">
                                <thead className="bg-[#1e293b] text-slate-200">
                                    <tr>
                                        <th className="p-3 w-16">#</th>
                                        <th className="p-3">In</th>
                                        <th className="p-3">Out</th>
                                        <th className="p-3">Type</th>
                                        <th className="p-3">Entry</th>
                                        <th className="p-3">Exit</th>
                                        <th className="p-3">Reason</th>
                                        <th className="p-3 text-right">PnL</th>
                                    </tr>
                                </thead>
                                <tbody className="divide-y divide-slate-800">
                                    {[...results.trades].reverse().map((t: any) => (
                                        <tr key={t.id} className="hover:bg-[#1e293b]/50 transition-colors">
                                            <td className="p-3">#{t.id}</td>
                                            <td className="p-3 text-slate-300 font-mono text-xs">{t.entry_time}</td>
                                            <td className="p-3 text-slate-300 font-mono text-xs">{t.exit_time}</td>
                                            <td className="p-3">
                                                <span className={`px-2 py-0.5 rounded text-xs font-bold uppercase ${t.type === 'LONG' ? 'bg-green-900/30 text-green-400 border border-green-900/50' : 'bg-red-900/30 text-red-400 border border-red-900/50'
                                                    }`}>
                                                    {t.type}
                                                </span>
                                            </td>
                                            <td className="p-3">${t.entry}</td>
                                            <td className="p-3">${t.exit}</td>
                                            <td className="p-3">
                                                <span className="text-xs bg-slate-800 px-1.5 py-0.5 rounded text-slate-400">
                                                    {t.reason}
                                                </span>
                                            </td>
                                            <td className={`p-3 text-right font-mono font-bold ${t.pnl >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                                                {t.pnl >= 0 ? '+' : ''}{t.pnl}
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};
