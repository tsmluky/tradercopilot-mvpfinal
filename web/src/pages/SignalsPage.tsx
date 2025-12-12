import React, { useEffect, useState } from 'react';
import { API_BASE_URL } from '../constants';
import { RefreshCw } from 'lucide-react';
import { SignalCard } from '../components/SignalCard';

export const SignalsPage: React.FC = () => {
    const [signals, setSignals] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const [filter, setFilter] = useState('ALL'); // ALL, WIN, LOSS, OPEN

    const fetchSignals = async () => {
        setLoading(true);
        try {
            const res = await fetch(`${API_BASE_URL}/logs/recent?limit=50`);
            if (res.ok) {
                setSignals(await res.json());
            }
        } catch (error) {
            console.error("Error fetching signals:", error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchSignals();
        const interval = setInterval(fetchSignals, 15000);
        return () => clearInterval(interval);
    }, []);

    const filteredSignals = signals.filter(s => {
        if (filter === 'ALL') return true;
        if (filter === 'OPEN') return s.status === 'OPEN';
        if (filter === 'WIN') return s.status === 'WIN' || s.status === 'HIT-TP';
        if (filter === 'LOSS') return s.status === 'LOSS' || s.status === 'HIT-SL';
        return true;
    });

    return (
        <div className="space-y-6">
            <div className="flex justify-between items-center">
                <div>
                    <h2 className="text-2xl font-bold text-slate-100">Live Signals Feed</h2>
                    <p className="text-slate-400">Real-time stream of generated trading signals.</p>
                </div>
                <button
                    onClick={fetchSignals}
                    className="p-2 rounded-lg bg-slate-800/50 text-slate-400 hover:text-white transition-colors"
                >
                    <RefreshCw className="w-5 h-5" />
                </button>
            </div>

            {/* Filters */}
            <div className="flex gap-2 overflow-x-auto pb-2">
                {['ALL', 'OPEN', 'WIN', 'LOSS'].map(f => (
                    <button
                        key={f}
                        onClick={() => setFilter(f)}
                        className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${filter === f
                            ? 'bg-indigo-500/20 text-indigo-400 border border-indigo-500/30'
                            : 'bg-slate-900/50 text-slate-400 border border-slate-800/50 hover:bg-slate-800'
                            }`}
                    >
                        {f}
                    </button>
                ))}
            </div>

            {/* Signals Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
                {loading && signals.length === 0 ? (
                    <div className="col-span-full h-64 flex items-center justify-center text-slate-500">
                        Loading signals...
                    </div>
                ) : filteredSignals.length === 0 ? (
                    <div className="col-span-full h-64 flex items-center justify-center text-slate-500">
                        No signals found matching filter.
                    </div>
                ) : (
                    filteredSignals.map((signal) => (
                        <SignalCard key={signal.id} signal={signal} />
                    ))
                )}
            </div>
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

    let normalized = status.toUpperCase();
    if (normalized.includes('HIT-TP')) normalized = 'WIN';
    if (normalized.includes('HIT-SL')) normalized = 'LOSS';

    return (
        <span className={`px-2 py-1 rounded text-xs font-bold border ${styles[normalized] || styles.OPEN}`}>
            {normalized}
        </span>
    );
};
