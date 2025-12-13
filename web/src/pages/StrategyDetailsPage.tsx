
import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { api } from '../services/api';
import { ArrowLeft, Activity, Shield, Zap, TrendingUp, History, Hash } from 'lucide-react';

interface SignalHistory {
    id: string;
    timestamp: string;
    token: string;
    direction: string;
    entry: number;
    tp: number;
    sl: number;
    result: {
        result: string;
        pnl_r: number;
        exit_price: number;
        closed_at: string;
    } | null;
}

export const StrategyDetailsPage: React.FC = () => {
    const { id } = useParams<{ id: string }>();
    const navigate = useNavigate();

    const [persona, setPersona] = useState<any>(null);
    const [history, setHistory] = useState<SignalHistory[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        if (!id) return;
        loadData(id);
    }, [id]);

    const loadData = async (personaId: string) => {
        setLoading(true);
        try {
            // 1. Get Metadata from Marketplace list
            const marketData = await api.fetchMarketplace();
            const found = marketData.find((p: any) => p.id === personaId);
            setPersona(found);

            // 2. Get History
            const historyData = await api.fetchPersonaHistory(personaId);
            setHistory(historyData);
        } catch (error) {
            console.error(error);
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return (
            <div className="flex h-screen items-center justify-center">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-500"></div>
            </div>
        );
    }

    if (!persona) {
        return (
            <div className="p-8 text-center text-slate-500">
                Persona not found. <button onClick={() => navigate('/strategies')} className="text-indigo-400">Go Back</button>
            </div>
        );
    }

    const themeColor = persona.color || 'indigo';

    return (
        <div className="space-y-8 animate-fade-in pb-12">
            {/* Header / Nav */}
            <button
                onClick={() => navigate('/strategies')}
                className="flex items-center gap-2 text-slate-400 hover:text-white transition-colors"
            >
                <ArrowLeft className="w-4 h-4" /> Back to Marketplace
            </button>

            {/* HERO SECTION */}
            <div className={`relative overflow-hidden rounded-3xl border border-slate-800 bg-slate-900/50 p-8 md:p-12`}>
                <div className={`absolute -top-24 -right-24 h-64 w-64 rounded-full bg-${themeColor}-500/10 blur-3xl`} />

                <div className="relative z-10 flex flex-col md:flex-row gap-8 justify-between items-start">
                    <div>
                        <div className="flex items-center gap-3 mb-4">
                            <span className={`px-3 py-1 rounded-full text-xs font-bold bg-${themeColor}-500/10 text-${themeColor}-400 border border-${themeColor}-500/20`}>
                                {persona.id.toUpperCase()}
                            </span>
                            {persona.is_active && (
                                <span className="flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                                    <span className="relative flex h-2 w-2">
                                        <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                                        <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
                                    </span>
                                    ACTIVE
                                </span>
                            )}
                        </div>
                        <h1 className="text-4xl md:text-5xl font-black text-white tracking-tight mb-4">
                            {persona.name}
                        </h1>
                        <p className="text-xl text-slate-400 max-w-2xl leading-relaxed">
                            {persona.description}
                        </p>
                    </div>

                    <div className="grid grid-cols-2 gap-4 min-w-[300px]">
                        <div className="p-4 bg-slate-950/50 rounded-xl border border-slate-800">
                            <div className="flex items-center gap-2 text-slate-500 text-sm mb-2">
                                <TrendingUp className="w-4 h-4" /> Expected ROI
                            </div>
                            <div className={`text-2xl font-bold text-${themeColor}-400`}>{persona.expected_roi}</div>
                        </div>
                        <div className="p-4 bg-slate-950/50 rounded-xl border border-slate-800">
                            <div className="flex items-center gap-2 text-slate-500 text-sm mb-2">
                                <Activity className="w-4 h-4" /> Win Rate
                            </div>
                            <div className="text-2xl font-bold text-white">{persona.win_rate}</div>
                        </div>
                        <div className="p-4 bg-slate-950/50 rounded-xl border border-slate-800">
                            <div className="flex items-center gap-2 text-slate-500 text-sm mb-2">
                                <Zap className="w-4 h-4" /> Frequency
                            </div>
                            <div className="text-lg font-medium text-white">{persona.frequency}</div>
                        </div>
                        <div className="p-4 bg-slate-950/50 rounded-xl border border-slate-800">
                            <div className="flex items-center gap-2 text-slate-500 text-sm mb-2">
                                <Shield className="w-4 h-4" /> Risk Level
                            </div>
                            <div className="text-lg font-medium text-white">{persona.risk_level}</div>
                        </div>
                    </div>
                </div>
            </div>

            {/* SIGNAL HISTORY */}
            <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden">
                <div className="p-6 border-b border-slate-800 flex justify-between items-center bg-slate-900/50">
                    <h3 className="text-lg font-bold text-white flex items-center gap-2">
                        <History className="w-5 h-5 text-indigo-400" />
                        Signal History
                    </h3>
                    <span className="text-sm text-slate-500">Last 100 Signals</span>
                </div>

                <div className="overflow-x-auto">
                    <table className="w-full text-left border-collapse">
                        <thead>
                            <tr className="bg-slate-950/50 text-slate-400 text-xs uppercase tracking-wider">
                                <th className="p-4 font-semibold">Time</th>
                                <th className="p-4 font-semibold">Token</th>
                                <th className="p-4 font-semibold">Direction</th>
                                <th className="p-4 font-semibold text-right">Entry</th>
                                <th className="p-4 font-semibold text-right">TP / SL</th>
                                <th className="p-4 font-semibold text-center">Result</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-800">
                            {history.length === 0 ? (
                                <tr>
                                    <td colSpan={6} className="p-8 text-center text-slate-500 italic">
                                        No signals generated yet for this persona.
                                    </td>
                                </tr>
                            ) : (
                                history.map((sig) => (
                                    <tr key={sig.id} className="hover:bg-slate-800/20 transition-colors group">
                                        <td className="p-4 text-slate-400 font-mono text-xs whitespace-nowrap">
                                            {new Date(sig.timestamp).toLocaleString()}
                                        </td>
                                        <td className="p-4 text-white font-bold text-sm">
                                            {sig.token}
                                        </td>
                                        <td className="p-4">
                                            <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-bold uppercase ${sig.direction.toLowerCase() === 'long'
                                                    ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                                                    : 'bg-rose-500/10 text-rose-400 border border-rose-500/20'
                                                }`}>
                                                {sig.direction}
                                            </span>
                                        </td>
                                        <td className="p-4 text-right font-mono text-slate-300 text-sm">
                                            {sig.entry}
                                        </td>
                                        <td className="p-4 text-right font-mono text-slate-500 text-xs">
                                            <div className="text-emerald-500/80">TP: {sig.tp}</div>
                                            <div className="text-rose-500/80">SL: {sig.sl}</div>
                                        </td>
                                        <td className="p-4 text-center">
                                            {sig.result ? (
                                                <span className={`px-2 py-1 rounded text-xs font-bold ${sig.result.result.includes('tp') || sig.result.pnl_r > 0
                                                        ? 'text-emerald-400 bg-emerald-500/10'
                                                        : sig.result.result.includes('sl') || sig.result.pnl_r < 0
                                                            ? 'text-rose-400 bg-rose-500/10'
                                                            : 'text-slate-400 bg-slate-800'
                                                    }`}>
                                                    {sig.result.result.toUpperCase()} ({sig.result.pnl_r > 0 ? '+' : ''}{sig.result.pnl_r}R)
                                                </span>
                                            ) : (
                                                <span className="text-xs text-slate-600 italic">Pending</span>
                                            )}
                                        </td>
                                    </tr>
                                ))
                            )}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
};
