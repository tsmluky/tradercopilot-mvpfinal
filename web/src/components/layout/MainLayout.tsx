import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import {
    LayoutDashboard,
    LineChart,
    Zap,
    Settings,
    Menu,
    Activity,
    Terminal,
    LogOut,
    FlaskConical
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { NotificationCenter } from '../NotificationCenter';

interface MainLayoutProps {
    children: React.ReactNode;
}

export const MainLayout: React.FC<MainLayoutProps> = ({ children }) => {
    const [isSidebarOpen, setIsSidebarOpen] = useState(false);
    const navigate = useNavigate();
    const location = useLocation();
    const { logout, user } = useAuth();

    const navItems = [
        { id: '/', label: 'Dashboard', icon: LayoutDashboard },
        { id: '/analysis', label: 'Generate Signal', icon: Zap },
        { id: '/signals', label: 'Live Signals', icon: Activity },
        { id: '/strategies', label: 'Strategies', icon: LineChart },
        { id: '/backtest', label: 'Backtest', icon: FlaskConical },
        { id: '/logs', label: 'System Logs', icon: Terminal },
        { id: '/settings', label: 'Settings', icon: Settings },
    ];

    const activeItem = navItems.find(item => location.pathname === item.id) || navItems[0];

    return (
        <div className="flex h-screen bg-[#020617] text-slate-200 overflow-hidden font-sans">
            {/* Mobile Sidebar Overlay */}
            {isSidebarOpen && (
                <div
                    className="fixed inset-0 bg-black/50 z-40 lg:hidden backdrop-blur-sm"
                    onClick={() => setIsSidebarOpen(false)}
                />
            )}

            {/* Sidebar */}
            <aside className={`
        fixed lg:static inset-y-0 left-0 z-50 w-64 bg-[#020617] border-r border-slate-800/50
        transform transition-transform duration-300 ease-in-out
        ${isSidebarOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}
      `}>
                <div className="h-full flex flex-col">
                    {/* Logo Area */}
                    <div className="h-16 flex items-center px-6 border-b border-slate-800/50">
                        <div className="flex items-center gap-3">
                            <div className="w-8 h-8 rounded-lg bg-indigo-500/10 flex items-center justify-center border border-indigo-500/20">
                                <Activity className="w-5 h-5 text-indigo-400" />
                            </div>
                            <span className="font-bold text-lg tracking-tight text-slate-100">
                                Trader<span className="text-indigo-400">Copilot</span>
                            </span>
                        </div>
                    </div>

                    {/* Navigation */}
                    <nav className="flex-1 px-3 py-6 space-y-1">
                        {navItems.map((item) => {
                            const Icon = item.icon;
                            const isActive = location.pathname === item.id;

                            return (
                                <button
                                    key={item.id}
                                    onClick={() => {
                                        navigate(item.id);
                                        setIsSidebarOpen(false);
                                    }}
                                    className={`
                    w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-200
                    ${isActive
                                            ? 'bg-indigo-500/10 text-indigo-400 border border-indigo-500/10'
                                            : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50 border border-transparent'}
                  `}
                                >
                                    <Icon className={`w-5 h-5 ${isActive ? 'text-indigo-400' : 'text-slate-500'}`} />
                                    {item.label}
                                </button>
                            );
                        })}
                    </nav>

                    {/* User Footer */}
                    <div className="p-4 border-t border-slate-800/50">
                        <div className="flex items-center justify-between px-3 py-2 rounded-lg bg-slate-900/50 border border-slate-800/50 mb-3">
                            <div className="flex items-center gap-3">
                                <div className="w-8 h-8 rounded-full bg-indigo-500/20 flex items-center justify-center text-indigo-400 font-bold text-xs border border-indigo-500/30">
                                    {user?.username?.substring(0, 2).toUpperCase() || 'ME'}
                                </div>
                                <div className="flex flex-col">
                                    <span className="text-xs font-medium text-slate-300">{user?.username || 'Trader'}</span>
                                    <span className="text-[10px] text-slate-500">Pro Plan</span>
                                </div>
                            </div>
                            <button onClick={logout} className="text-slate-500 hover:text-rose-400 transition-colors">
                                <LogOut className="w-4 h-4" />
                            </button>
                        </div>

                        <div className="flex items-center gap-2 justify-center">
                            <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></div>
                            <span className="text-[10px] text-slate-500 font-mono">SYSTEM ONLINE</span>
                        </div>
                    </div>
                </div>
            </aside>

            {/* Main Content Area */}
            <div className="flex-1 flex flex-col min-w-0 overflow-hidden relative">
                {/* Background Gradient Mesh */}
                <div className="absolute top-0 left-0 w-full h-96 bg-gradient-to-b from-indigo-900/10 to-transparent pointer-events-none" />

                {/* Header */}
                <header className="h-16 flex items-center justify-between px-6 border-b border-slate-800/50 bg-[#020617]/80 backdrop-blur-md z-30 sticky top-0">
                    <div className="flex items-center gap-4">
                        <button
                            onClick={() => setIsSidebarOpen(true)}
                            className="lg:hidden p-2 -ml-2 text-slate-400 hover:text-slate-200"
                        >
                            <Menu className="w-6 h-6" />
                        </button>

                        <h1 className="text-lg font-semibold text-slate-100 flex items-center gap-2">
                            {activeItem.label}
                        </h1>
                    </div>

                    {/* Top Bar Stats */}
                    <div className="flex items-center gap-4">
                        <div className="hidden md:flex items-center gap-6 text-sm bg-slate-900/50 px-4 py-1.5 rounded-full border border-slate-800/50">
                            <div className="flex items-center gap-2">
                                <span className="text-slate-500 font-medium">BTC</span>
                                <span className="font-mono text-emerald-400">$90,728</span>
                            </div>
                            <div className="w-px h-3 bg-slate-700"></div>
                            <div className="flex items-center gap-2">
                                <span className="text-slate-500 font-medium">ETH</span>
                                <span className="font-mono text-emerald-400">$3,010</span>
                            </div>
                        </div>

                        {/* Notification Center */}
                        <div className="pl-4 border-l border-slate-800/50">
                            <NotificationCenter />
                        </div>
                    </div>
                </header>

                {/* Scrollable Content */}
                <main className="flex-1 overflow-y-auto overflow-x-hidden p-6 relative z-10 custom-scrollbar">
                    <div className="max-w-7xl mx-auto">
                        {children}
                    </div>
                </main>
            </div>
        </div>
    );
};
