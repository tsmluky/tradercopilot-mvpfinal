import React, { useRef } from 'react';
import { NavLink, Link, useLocation } from 'react-router-dom';
import {
  LayoutDashboard,
  Terminal,
  FileText,
  Settings,
  Activity,
  Trophy,
  Zap,
  User,
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { MarketTicker } from './MarketTicker';
import { NotificationCenter } from './NotificationCenter';

interface LayoutProps {
  children: React.ReactNode;
}

export const Layout: React.FC<LayoutProps> = ({ children }) => {
  const { userProfile } = useAuth();
  const location = useLocation();
  const scrollRef = useRef<HTMLDivElement>(null);

  // Premium feel: si clicas en la pestaña ya activa, hace scroll suave al top
  const handleNavClick = (e: React.MouseEvent, path: string) => {
    if (location.pathname === path) {
      e.preventDefault();
      scrollRef.current?.scrollTo({ top: 0, behavior: 'smooth' });
    }
  };

  return (
    <div className="flex flex-col h-[100dvh] w-full bg-slate-950 text-slate-200 overflow-hidden">
      {/* Top Market Ticker (Fixed) */}
      <div className="flex-shrink-0 z-20">
        <MarketTicker />
      </div>

      <div className="flex flex-1 overflow-hidden relative">
        {/* DESKTOP SIDEBAR (Hidden on Mobile) */}
        <div className="hidden md:flex w-64 flex-shrink-0 bg-slate-900 border-r border-slate-800 flex-col z-20">
          {/* Brand */}
          <Link to="/" className="h-16 flex items-center px-6 border-b border-slate-800 hover:bg-slate-800/50 transition-colors">
            <div className="w-8 h-8 bg-emerald-500 rounded-lg flex items-center justify-center flex-shrink-0 shadow-lg shadow-emerald-500/20">
              <Activity className="text-white" size={20} />
            </div>
            <span className="ml-3 font-bold text-lg tracking-tight text-white">
              Trader<span className="text-emerald-400">Copilot</span>
            </span>
          </Link>

          {/* Navigation */}
          <nav className="flex-1 p-4 space-y-2 overflow-y-auto no-scrollbar">
            <NavItem
              to="/"
              icon={<LayoutDashboard size={20} />}
              label="Dashboard"
              onClick={(e) => handleNavClick(e, '/')}
            />
            <NavItem
              to="/analysis"
              icon={<Terminal size={20} />}
              label="Terminal"
              onClick={(e) => handleNavClick(e, '/analysis')}
            />
            {/* Opcional: Leaderboard (paper trading / ranking) */}
            <NavItem
              to="/leaderboard"
              icon={<Trophy size={20} />}
              label="Leaderboard"
              onClick={(e) => handleNavClick(e, '/leaderboard')}
            />
            <NavItem
              to="/logs"
              icon={<FileText size={20} />}
              label="Logs"
              onClick={(e) => handleNavClick(e, '/logs')}
            />

            <div className="pt-4 mt-4 border-t border-slate-800">
              <NavItem
                to="/membership"
                icon={<Zap size={20} className="text-amber-400" />}
                label="Upgrade Plan"
                onClick={(e) => handleNavClick(e, '/membership')}
              />
              <NavItem
                to="/settings"
                icon={<Settings size={20} />}
                label="Settings"
                onClick={(e) => handleNavClick(e, '/settings')}
              />
            </div>
          </nav>

          {/* Desktop Footer: Perfil + System Status */}
          <div className="p-4 border-t border-slate-800 space-y-3">
            {userProfile ? (
              <Link
                to="/profile"
                className="flex items-center gap-3 p-2 -mx-2 rounded hover:bg-slate-800 transition-colors group"
              >
                <img
                  src={userProfile.user.avatar_url}
                  alt="Avatar"
                  className="w-8 h-8 rounded-full border border-slate-700 group-hover:border-emerald-500 transition-colors"
                />
                <div className="overflow-hidden">
                  <div className="text-sm font-bold text-white truncate">
                    {userProfile.user.name}
                  </div>
                  <div className="text-xs text-slate-500 truncate">
                    {userProfile.user.email}
                  </div>
                </div>
              </Link>
            ) : null}

            {/* System Status heredado del layout original */}
            <div className="bg-slate-800 rounded p-3">
              <div className="text-xs font-bold text-slate-500 uppercase">
                System Status
              </div>
              <div className="flex items-center gap-2 mt-1">
                <span className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse" />
                <span className="text-xs text-emerald-400 font-mono">
                  v0.7.3 ONLINE
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Main Content Area */}
        <main className="flex-1 flex flex-col overflow-hidden bg-slate-950 relative w-full">
          {/* Header: Solid Background on Mobile */}
          <div className="h-16 border-b border-slate-800 flex justify-between items-center px-4 md:px-6 flex-shrink-0 bg-slate-950 z-30 sticky top-0 shadow-md">
            {/* Mobile logo/avatar */}
            <div className="md:hidden flex items-center gap-3">
              {userProfile && (
                <Link
                  to="/profile"
                  className="active:scale-95 transition-transform"
                >
                  <img
                    src={userProfile.user.avatar_url}
                    className="w-8 h-8 rounded-full border border-slate-700"
                  />
                </Link>
              )}
              <span className="font-bold text-white">
                Trader<span className="text-emerald-400">Copilot</span>
              </span>
            </div>

            {/* Desktop placeholder para centrar NotificationCenter */}
            <div className="hidden md:block" />

            <NotificationCenter />
          </div>

          {/* Scrollable Content Container */}
          <div
            className="flex-1 overflow-y-auto overflow-x-hidden pb-[calc(4rem+env(safe-area-inset-bottom))] md:pb-0 scroll-smooth bg-slate-950"
            id="main-scroll"
            ref={scrollRef}
          >
            <div className="animate-fade-in">{children}</div>
          </div>
        </main>

        {/* MOBILE BOTTOM NAVIGATION BAR */}
        <div className="md:hidden fixed bottom-0 left-0 right-0 h-[calc(3.5rem+env(safe-area-inset-bottom))] bg-slate-950 border-t border-slate-800 flex justify-around items-start pt-3 z-50 pb-safe shadow-[0_-5px_20px_rgba(0,0,0,0.8)]">
          <MobileNavItem
            to="/"
            icon={<LayoutDashboard size={26} />}
            active={location.pathname === '/'}
            onClick={(e) => handleNavClick(e, '/')}
          />
          <MobileNavItem
            to="/analysis"
            icon={<Terminal size={26} />}
            active={location.pathname === '/analysis'}
            onClick={(e) => handleNavClick(e, '/analysis')}
          />
          <MobileNavItem
            to="/logs"
            icon={<FileText size={26} />}
            active={location.pathname === '/logs'}
            onClick={(e) => handleNavClick(e, '/logs')}
          />
          <MobileNavItem
            to="/profile"
            icon={<User size={26} />}
            active={location.pathname === '/profile'}
            onClick={(e) => handleNavClick(e, '/profile')}
          />
        </div>
      </div>
    </div>
  );
};

interface NavItemProps {
  to: string;
  icon: React.ReactNode;
  label: string;
  onClick: (e: React.MouseEvent) => void;
}

const NavItem: React.FC<NavItemProps> = ({ to, icon, label, onClick }) => (
  <NavLink
    to={to}
    onClick={onClick}
    className={({ isActive }) =>
      `flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all duration-200 group active:scale-95 ${isActive
        ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
        : 'text-slate-400 hover:bg-slate-800 hover:text-slate-200'
      }`
    }
  >
    <span className="group-hover:scale-110 transition-transform duration-200">
      {icon}
    </span>
    <span className="font-medium">{label}</span>
  </NavLink>
);

interface MobileNavItemProps {
  to: string;
  icon: React.ReactNode;
  active: boolean;
  onClick: (e: React.MouseEvent) => void;
}

const MobileNavItem: React.FC<MobileNavItemProps> = ({
  to,
  icon,
  active,
  onClick,
}) => (
  <Link
    to={to}
    onClick={onClick}
    className={`flex items-center justify-center w-14 h-10 active:scale-90 transition-transform duration-150 rounded-xl ${active ? 'text-emerald-400 bg-emerald-500/10' : 'text-slate-500'
      }`}
  >
    {icon}
  </Link>
);
