import React, { useEffect, useState } from 'react';
import { api } from '../services/api';
import { Shield, Users, EyeOff, Activity, Search, AlertTriangle, CheckCircle, XCircle } from 'lucide-react';
import { toast } from 'react-hot-toast';

interface AdminStats {
    total_users: number;
    active_plans: number;
    hidden_signals: number;
    total_signals: number;
}

interface UserData {
    id: number;
    email: string;
    role: string;
    plan: string;
    created_at: string;
}

interface SignalData {
    id: number;
    token: string;
    mode: string;
    timestamp: string;
    is_hidden: number;
}

export const AdminPage: React.FC = () => {
    const [stats, setStats] = useState<AdminStats | null>(null);
    const [activeTab, setActiveTab] = useState<'users' | 'signals' | 'audit'>('users');

    // Users State
    const [users, setUsers] = useState<UserData[]>([]);
    const [userPage, setUserPage] = useState(1);
    const [userSearch, setUserSearch] = useState('');

    // Signals State
    const [signals, setSignals] = useState<SignalData[]>([]);
    const [signalPage, setSignalPage] = useState(1);

    const [loading, setLoading] = useState(false);

    useEffect(() => {
        fetchStats();
        fetchUsers();
    }, []);

    const fetchStats = async () => {
        try {
            const data = await api.fetchAdminStats();
            setStats(data);
        } catch (error) {
            console.error(error);
            toast.error("Failed to load admin stats");
        }
    };

    const fetchUsers = async () => {
        setLoading(true);
        try {
            const data = await api.fetchAdminUsers(userPage, userSearch);
            setUsers(data.items);
        } catch (error) {
            console.error(error);
        } finally {
            setLoading(false);
        }
    };

    const fetchSignals = async () => {
        setLoading(true);
        try {
            const data = await api.fetchAdminSignals(signalPage);
            setSignals(data.items);
        } catch (error) {
            console.error(error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        if (activeTab === 'users') fetchUsers();
        if (activeTab === 'signals') fetchSignals();
    }, [activeTab, userPage, signalPage, userSearch]);

    const handleUpdatePlan = async (userId: number, newPlan: string) => {
        if (!confirm(`Change user ${userId} plan to ${newPlan}?`)) return;
        try {
            await api.updateUserPlan(userId, newPlan);
            toast.success("Plan updated");
            fetchUsers();
            fetchStats();
        } catch (error) {
            toast.error("Failed to update plan");
        }
    };

    const handleToggleSignal = async (signalId: number, currentHidden: number) => {
        const newState = currentHidden === 1 ? false : true;
        try {
            await api.toggleSignalVisibility(signalId, newState);
            toast.success(newState ? "Signal Hidden" : "Signal Visible");
            fetchSignals();
            fetchStats();
        } catch (error) {
            toast.error("Failed to toggle signal");
        }
    };

    return (
        <div className="space-y-8 animate-fade-in text-slate-200">
            {/* Header */}
            <div>
                <h1 className="text-4xl font-black text-white flex items-center gap-3">
                    <Shield className="w-10 h-10 text-red-500" />
                    Admin Control
                </h1>
                <p className="text-slate-400 mt-2">System Management & Audits</p>
            </div>

            {/* KPI Cards */}
            {stats && (
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl">
                        <div className="flex items-center gap-2 text-slate-400 mb-2">
                            <Users className="w-4 h-4" /> Total Users
                        </div>
                        <div className="text-2xl font-bold text-white">{stats.total_users}</div>
                    </div>
                    <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl">
                        <div className="flex items-center gap-2 text-emerald-400 mb-2">
                            <Activity className="w-4 h-4" /> Active Subscriptions
                        </div>
                        <div className="text-2xl font-bold text-emerald-400">{stats.active_plans}</div>
                    </div>
                    <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl">
                        <div className="flex items-center gap-2 text-slate-400 mb-2">
                            <Activity className="w-4 h-4" /> Total Signals
                        </div>
                        <div className="text-2xl font-bold text-white">{stats.total_signals}</div>
                    </div>
                    <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl">
                        <div className="flex items-center gap-2 text-amber-500 mb-2">
                            <EyeOff className="w-4 h-4" /> Hidden Signals
                        </div>
                        <div className="text-2xl font-bold text-amber-500">{stats.hidden_signals}</div>
                    </div>
                </div>
            )}

            {/* Tabs */}
            <div className="flex gap-4 border-b border-slate-800 pb-2">
                <button
                    onClick={() => setActiveTab('users')}
                    className={`px-4 py-2 font-bold transition-colors ${activeTab === 'users' ? 'text-white border-b-2 border-indigo-500' : 'text-slate-500 hover:text-slate-300'}`}
                >
                    Users
                </button>
                <button
                    onClick={() => setActiveTab('signals')}
                    className={`px-4 py-2 font-bold transition-colors ${activeTab === 'signals' ? 'text-white border-b-2 border-indigo-500' : 'text-slate-500 hover:text-slate-300'}`}
                >
                    Signals
                </button>
            </div>

            {/* Content */}
            <div className="bg-slate-900/50 border border-slate-800 rounded-xl p-6 overflow-hidden">
                {activeTab === 'users' && (
                    <div className="space-y-4">
                        <div className="flex gap-2 mb-4">
                            <div className="relative flex-1 max-w-sm">
                                <Search className="absolute left-3 top-3 w-4 h-4 text-slate-500" />
                                <input
                                    type="text"
                                    placeholder="Search by email..."
                                    className="w-full bg-slate-950 border border-slate-800 rounded-lg pl-10 pr-4 py-2 text-sm focus:border-indigo-500 outline-none"
                                    value={userSearch}
                                    onChange={(e) => setUserSearch(e.target.value)}
                                />
                            </div>
                        </div>

                        <table className="w-full text-left text-sm">
                            <thead className="text-slate-500 border-b border-slate-800">
                                <tr>
                                    <th className="pb-3 pl-2">ID</th>
                                    <th className="pb-3">Email</th>
                                    <th className="pb-3">Role</th>
                                    <th className="pb-3">Plan</th>
                                    <th className="pb-3">Actions</th>
                                </tr>
                            </thead>
                            <tbody className="text-slate-300">
                                {users.map(u => (
                                    <tr key={u.id} className="border-b border-slate-800/50 hover:bg-slate-800/20">
                                        <td className="py-3 pl-2 font-mono text-slate-500">#{u.id}</td>
                                        <td className="py-3">{u.email}</td>
                                        <td className="py-3">
                                            {u.role === 'admin' ?
                                                <span className="text-red-400 font-bold">OWNER</span> :
                                                <span className="text-slate-500">User</span>
                                            }
                                        </td>
                                        <td className="py-3">
                                            <span className={`px-2 py-1 round text-xs font-bold ${u.plan === 'PRO' ? 'bg-indigo-500/20 text-indigo-400' : u.plan === 'OWNER' ? 'bg-red-500/20 text-red-400' : 'bg-slate-700 text-slate-400'}`}>
                                                {u.plan}
                                            </span>
                                        </td>
                                        <td className="py-3 flex gap-2">
                                            {u.plan !== 'PRO' && u.role !== 'admin' && (
                                                <button onClick={() => handleUpdatePlan(u.id, 'PRO')} className="px-2 py-1 text-xs bg-indigo-600 hover:bg-indigo-700 rounded text-white">
                                                    Upgrade PRO
                                                </button>
                                            )}
                                            {u.plan === 'PRO' && (
                                                <button onClick={() => handleUpdatePlan(u.id, 'FREE')} className="px-2 py-1 text-xs bg-slate-700 hover:bg-slate-600 rounded text-white">
                                                    Downgrade
                                                </button>
                                            )}
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>

                        {/* Pagination Simple */}
                        <div className="flex justify-between items-center pt-4">
                            <span className="text-xs text-slate-500">Page {userPage}</span>
                            <div className="flex gap-2">
                                <button disabled={userPage === 1} onClick={() => setUserPage(p => p - 1)} className="px-3 py-1 bg-slate-800 rounded disabled:opacity-50">Prev</button>
                                <button onClick={() => setUserPage(p => p + 1)} className="px-3 py-1 bg-slate-800 rounded">Next</button>
                            </div>
                        </div>
                    </div>
                )}

                {activeTab === 'signals' && (
                    <div className="space-y-4">
                        <table className="w-full text-left text-sm">
                            <thead className="text-slate-500 border-b border-slate-800">
                                <tr>
                                    <th className="pb-3 pl-2">Time</th>
                                    <th className="pb-3">Token</th>
                                    <th className="pb-3">Mode</th>
                                    <th className="pb-3">Status</th>
                                    <th className="pb-3 text-right">Actions</th>
                                </tr>
                            </thead>
                            <tbody className="text-slate-300">
                                {signals.map(s => (
                                    <tr key={s.id} className={`border-b border-slate-800/50 hover:bg-slate-800/20 ${s.is_hidden ? 'opacity-50' : ''}`}>
                                        <td className="py-3 pl-2 text-slate-500">{new Date(s.timestamp).toLocaleString()}</td>
                                        <td className="py-3 font-bold">{s.token}</td>
                                        <td className="py-3">{s.mode}</td>
                                        <td className="py-3">
                                            {s.is_hidden ?
                                                <span className="flex items-center gap-1 text-amber-500 text-xs"><EyeOff className="w-3 h-3" /> Hidden</span> :
                                                <span className="flex items-center gap-1 text-emerald-500 text-xs"><CheckCircle className="w-3 h-3" /> Active</span>
                                            }
                                        </td>
                                        <td className="py-3 text-right">
                                            <button
                                                onClick={() => handleToggleSignal(s.id, s.is_hidden)}
                                                className={`px-3 py-1 text-xs rounded font-bold transition-colors ${s.is_hidden ? 'bg-emerald-500/20 text-emerald-400 hover:bg-emerald-500/30' : 'bg-amber-500/20 text-amber-500 hover:bg-amber-500/30'}`}
                                            >
                                                {s.is_hidden ? "UNHIDE" : "HIDE"}
                                            </button>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                        {/* Pagination Simple */}
                        <div className="flex justify-between items-center pt-4">
                            <span className="text-xs text-slate-500">Page {signalPage}</span>
                            <div className="flex gap-2">
                                <button disabled={signalPage === 1} onClick={() => setSignalPage(p => p - 1)} className="px-3 py-1 bg-slate-800 rounded disabled:opacity-50">Prev</button>
                                <button onClick={() => setSignalPage(p => p + 1)} className="px-3 py-1 bg-slate-800 rounded">Next</button>
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};
