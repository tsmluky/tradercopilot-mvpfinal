import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../services/api';
import { useAuth } from '../context/AuthContext';
import {
  Send,
  Check,
  AlertCircle,
  LogOut,
  User,
  CreditCard,
  Shield,
  HelpCircle,
  FileText,
  ChevronDown,
  ChevronUp,
  Server,
  Bell,
  Calendar,
  Zap,
} from 'lucide-react';

export const SettingsPage: React.FC = () => {
  const [pingMsg, setPingMsg] = useState('');
  const [status, setStatus] = useState<'idle' | 'loading' | 'success' | 'error'>(
    'idle'
  );
  const { userProfile, logout } = useAuth();
  const [showAdvanced, setShowAdvanced] = useState(false);

  const handlePing = async () => {
    setStatus('loading');
    try {
      await api.notifyTelegram(pingMsg || '🚀 TraderCopilot · Test Ping');
      setStatus('success');
      setTimeout(() => setStatus('idle'), 3000);
    } catch (e) {
      setStatus('error');
    }
  };

  if (!userProfile) return null;

  return (
    <div className="p-4 md:p-8 max-w-5xl mx-auto pb-24 md:pb-8 animate-fade-in">
      {/* Header / Hero */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-end mb-8 md:mb-10 gap-6">
        <div>
          <h1 className="text-3xl font-bold text-white mb-2">My Profile</h1>
          <p className="text-slate-400">
            Manage your account settings and preferences.
          </p>
        </div>
        <button
          onClick={logout}
          className="flex items-center gap-2 text-rose-400 hover:text-rose-300 font-semibold text-sm bg-rose-500/5 hover:bg-rose-500/10 px-4 py-2 rounded-lg border border-rose-500/20 transition-all active:scale-95"
        >
          <LogOut size={16} /> Sign Out
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 md:gap-8">

        {/* LEFT COLUMN: Main Profile Info */}
        <div className="lg:col-span-2 space-y-6">

          {/* Hero Card */}
          <div className="bg-gradient-to-br from-slate-900 to-slate-900/50 rounded-2xl border border-slate-800 p-6 md:p-8 relative overflow-hidden group">
            <div className="absolute top-0 right-0 p-6 opacity-10 group-hover:opacity-20 transition-opacity">
              <User size={120} />
            </div>

            <div className="flex flex-col md:flex-row items-center md:items-start gap-6 relative z-10">
              <div className="relative">
                <img
                  src={
                    userProfile.user.avatar_url ||
                    'https://api.dicebear.com/7.x/identicon/svg?seed=trader'
                  }
                  className="w-24 h-24 md:w-28 md:h-28 rounded-full border-4 border-slate-800 shadow-2xl object-cover"
                  alt="Profile"
                />
                <div className="absolute bottom-1 right-1 w-6 h-6 bg-emerald-500 border-4 border-slate-900 rounded-full" title="Active"></div>
              </div>

              <div className="flex-1 text-center md:text-left space-y-2">
                <div>
                  <h2 className="text-2xl font-bold text-white tracking-tight">{userProfile.user.name}</h2>
                  <p className="text-slate-400 font-medium">{userProfile.user.email}</p>
                </div>

                <div className="flex flex-wrap gap-2 justify-center md:justify-start pt-2">
                  <span className="px-3 py-1 rounded-full bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 text-xs font-bold uppercase tracking-wider">
                    {userProfile.user.role}
                  </span>
                  <span className="px-3 py-1 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 text-xs font-bold uppercase tracking-wider flex items-center gap-1.5">
                    <CreditCard size={12} /> {userProfile.user.subscription_status} Plan
                  </span>

                  {/* Upgrade CTA */}
                  {userProfile.user.subscription_status !== 'pro' && (
                    <a href="/membership" className="px-3 py-1 rounded-full bg-amber-500/10 text-amber-400 border border-amber-500/20 text-xs font-bold uppercase tracking-wider flex items-center gap-1.5 hover:bg-amber-500/20 transition-colors">
                      <Zap size={12} /> Upgrade
                    </a>
                  )}
                </div>
              </div>
            </div>
          </div>

          {/* Account Details */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="bg-slate-900/50 rounded-xl border border-slate-800 p-4">
              <div className="flex items-center gap-3 mb-1">
                <div className="p-2 bg-slate-800 rounded-lg text-slate-400">
                  <Calendar size={18} />
                </div>
                <div>
                  <label className="text-[10px] font-bold text-slate-500 uppercase">Member Since</label>
                  <div className="text-slate-200 font-medium text-sm">December 2025</div>
                </div>
              </div>
            </div>
            <div className="bg-slate-900/50 rounded-xl border border-slate-800 p-4">
              <div className="flex items-center gap-3 mb-1">
                <div className="p-2 bg-slate-800 rounded-lg text-slate-400">
                  <Shield size={18} />
                </div>
                <div>
                  <label className="text-[10px] font-bold text-slate-500 uppercase">Security Level</label>
                  <div className="text-emerald-400 font-medium text-sm">High (2FA Enabled)</div>
                </div>
              </div>
            </div>
          </div>

          {/* Notification Settings */}
          <div className="bg-slate-900 rounded-xl border border-slate-800 p-5 md:p-6">
            <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
              <Bell size={20} className="text-amber-400" /> Notifications
            </h3>
            <p className="text-slate-400 text-sm mb-6">
              Connect your Telegram account to verify you can receive real-time signals from your agents.
            </p>

            <div className="flex flex-col sm:flex-row gap-3">
              <input
                type="text"
                placeholder="Enter test message..."
                value={pingMsg}
                onChange={(e) => setPingMsg(e.target.value)}
                className="flex-1 bg-slate-950 border border-slate-800 text-white rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-emerald-500 outline-none transition-all placeholder:text-slate-600"
              />
              <button
                onClick={handlePing}
                disabled={status === 'loading'}
                className={`px-6 py-2.5 rounded-lg font-bold flex items-center justify-center gap-2 transition-all active:scale-95 whitespace-nowrap ${status === 'success'
                  ? 'bg-emerald-500 text-white shadow-[0_0_15px_rgba(16,185,129,0.4)]'
                  : status === 'error'
                    ? 'bg-rose-500 text-white'
                    : 'bg-indigo-600 hover:bg-indigo-500 text-white shadow-lg shadow-indigo-900/20'
                  }`}
              >
                {status === 'loading' ? (
                  <span className="animate-pulse">Testing...</span>
                ) : status === 'success' ? (
                  <>
                    <Check size={18} /> Sent
                  </>
                ) : status === 'error' ? (
                  <>
                    <AlertCircle size={18} /> Failed
                  </>
                ) : (
                  <>
                    <Send size={18} /> Test Telegram
                  </>
                )}
              </button>
            </div>
          </div>

        </div>

        {/* RIGHT COLUMN: Secondary Info */}
        <div className="space-y-6">

          {/* Support */}
          <div className="bg-slate-900 rounded-xl border border-slate-800 p-5 md:p-6">
            <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
              <HelpCircle size={20} className="text-blue-400" /> Help & Support
            </h3>
            <p className="text-sm text-slate-400 mb-6 leading-relaxed">
              Need assistance? Our specialized agent support team is available 24/7 for Pro plan members.
            </p>
            <button className="w-full bg-slate-800 hover:bg-slate-700 text-white font-medium py-3 rounded-lg transition-all active:scale-[0.98] flex items-center justify-center gap-2">
              Contact Support
            </button>
          </div>

          {/* Legal Links */}
          <div className="bg-slate-900 rounded-xl border border-slate-800 p-5 md:p-6 space-y-3">
            <button className="w-full flex items-center justify-between text-left text-sm text-slate-300 hover:text-white group">
              <span className="flex items-center gap-2"><FileText size={16} className="text-slate-500 group-hover:text-slate-300" /> Terms of Service</span>
              <span className="text-xs text-slate-600">v1.2</span>
            </button>
            <button className="w-full flex items-center justify-between text-left text-sm text-slate-300 hover:text-white group">
              <span className="flex items-center gap-2"><Shield size={16} className="text-slate-500 group-hover:text-slate-300" /> Privacy Policy</span>
            </button>
            <div className="pt-2 border-t border-slate-800/50">
              <div className="text-[10px] text-slate-500 text-center">
                TraderCopilot © 2025
              </div>
            </div>
          </div>

          {/* Advanced / System Toggle */}
          <div className="border-t border-slate-800 pt-6">
            <button
              onClick={() => setShowAdvanced(!showAdvanced)}
              className="flex items-center gap-2 text-xs font-bold text-slate-500 hover:text-slate-300 uppercase tracking-wider transition-colors"
            >
              {showAdvanced ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
              Advanced System Settings
            </button>

            {showAdvanced && (
              <div className="mt-4 bg-slate-950/50 rounded-xl border border-slate-800/50 p-4 animate-in slide-in-from-top-2 duration-200">
                <div className="flex items-center gap-2 mb-3 text-slate-400 text-xs font-mono">
                  <Server size={14} /> System Configuration
                </div>

                <div className="space-y-3">
                  <div className="flex justify-between items-center text-xs">
                    <span className="text-slate-500">API Endpoint</span>
                    <code className="bg-slate-900 px-2 py-1 rounded text-emerald-500">http://localhost:8010</code>
                  </div>
                  <div className="flex justify-between items-center text-xs">
                    <span className="text-slate-500">Version</span>
                    <span className="text-slate-300">v0.7.3-beta</span>
                  </div>
                  <div className="flex justify-between items-center text-xs">
                    <span className="text-slate-500">Environment</span>
                    <span className="text-amber-500">Development</span>
                  </div>
                  <div className="flex justify-between items-center text-xs">
                    <span className="text-slate-500">Timezone</span>
                    <span className="text-slate-300">{Intl.DateTimeFormat().resolvedOptions().timeZone}</span>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
