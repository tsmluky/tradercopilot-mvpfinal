import React, { useState } from 'react';
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
} from 'lucide-react';

export const SettingsPage: React.FC = () => {
  const [pingMsg, setPingMsg] = useState('');
  const [status, setStatus] = useState<'idle' | 'loading' | 'success' | 'error'>(
    'idle'
  );
  const { userProfile, logout } = useAuth();

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

  return (
    <div className="p-4 md:p-8 max-w-4xl mx-auto pb-24 md:pb-8">
      {/* Header */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-6 md:mb-8 gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white">System Settings</h1>
          <p className="text-slate-400 text-sm">
            Manage your account and preferences.
          </p>
        </div>
        <button
          onClick={logout}
          className="w-full md:w-auto flex items-center justify-center gap-2 text-rose-400 hover:text-rose-300 font-bold text-sm bg-rose-500/10 px-4 py-3 md:py-2 rounded-lg border border-rose-500/20 transition-colors active:scale-95"
        >
          <LogOut size={16} /> Sign Out
        </button>
      </div>

      {/* Profile Section */}
      {userProfile && (
        <div className="bg-slate-900 rounded-xl border border-slate-800 p-5 md:p-6 mb-6 shadow-lg">
          <h2 className="text-lg font-bold text-white mb-6 flex items-center gap-2">
            <User size={20} className="text-blue-400" /> Account Profile
          </h2>

          <div className="flex flex-col md:flex-row items-center md:items-start gap-6">
            <div className="flex-shrink-0">
              <img
                src={
                  userProfile.user.avatar_url ||
                  'https://api.dicebear.com/7.x/identicon/svg?seed=trader'
                }
                className="w-20 h-20 rounded-full border-4 border-slate-800 shadow-xl object-cover"
                alt="Profile"
              />
            </div>

            <div className="flex-1 w-full grid grid-cols-1 sm:grid-cols-2 gap-4 md:gap-6">
              <div className="bg-slate-950/50 p-3 rounded border border-slate-800/50">
                <label className="text-[10px] font-bold text-slate-500 uppercase block mb-1">
                  Full Name
                </label>
                <div className="text-white font-medium text-sm md:text-base truncate">
                  {userProfile.user.name}
                </div>
              </div>
              <div className="bg-slate-950/50 p-3 rounded border border-slate-800/50">
                <label className="text-[10px] font-bold text-slate-500 uppercase block mb-1">
                  Email Address
                </label>
                <div className="text-white font-medium text-sm md:text-base truncate">
                  {userProfile.user.email}
                </div>
              </div>
              <div className="bg-slate-950/50 p-3 rounded border border-slate-800/50">
                <label className="text-[10px] font-bold text-slate-500 uppercase block mb-1">
                  Role
                </label>
                <div className="text-white font-medium capitalize text-sm md:text-base">
                  {userProfile.user.role}
                </div>
              </div>
              <div className="bg-slate-950/50 p-3 rounded border border-slate-800/50">
                <label className="text-[10px] font-bold text-slate-500 uppercase block mb-1">
                  Subscription
                </label>
                <div className="flex items-center gap-2">
                  <div className="text-emerald-400 font-bold uppercase text-sm md:text-base flex items-center gap-1.5">
                    <CreditCard size={14} />{' '}
                    {userProfile.user.subscription_status}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
        {/* Legal & Compliance */}
        <div className="bg-slate-900 rounded-xl border border-slate-800 p-5 md:p-6">
          <h2 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
            <Shield size={20} className="text-slate-400" /> Legal & Compliance
          </h2>
          <div className="space-y-3">
            <button className="w-full flex items-center justify-between p-3 md:p-4 bg-slate-950 rounded-lg border border-slate-800 hover:border-slate-600 transition-colors text-sm text-slate-300 active:scale-[0.98]">
              <span className="flex items-center gap-2">
                <FileText size={16} /> Terms of Service
              </span>
              <span className="text-xs text-slate-500 font-mono">v1.2</span>
            </button>
            <button className="w-full flex items-center justify-between p-3 md:p-4 bg-slate-950 rounded-lg border border-slate-800 hover:border-slate-600 transition-colors text-sm text-slate-300 active:scale-[0.98]">
              <span className="flex items-center gap-2">
                <Shield size={16} /> Privacy Policy
              </span>
              <span className="text-xs text-emerald-500 font-bold">
                Updated
              </span>
            </button>
            <button className="w-full flex items-center justify-between p-3 md:p-4 bg-slate-950 rounded-lg border border-slate-800 hover:border-slate-600 transition-colors text-sm text-slate-300 active:scale-[0.98]">
              <span className="flex items-center gap-2">
                <AlertCircle size={16} /> Risk Disclaimer
              </span>
              <span className="text-xs text-amber-500 font-bold">
                Important
              </span>
            </button>
          </div>
        </div>

        {/* Support */}
        <div className="bg-slate-900 rounded-xl border border-slate-800 p-5 md:p-6 flex flex-col">
          <h2 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
            <HelpCircle size={20} className="text-slate-400" /> Support
          </h2>
          <p className="text-sm text-slate-400 mb-6 leading-relaxed">
            Having trouble with the terminal? Our team is available 24/7 for
            Pro members to assist with signal execution or technical issues.
          </p>
          <div className="mt-auto">
            <button className="w-full bg-slate-800 hover:bg-slate-700 text-white font-bold py-3.5 rounded-lg transition-all active:scale-[0.98] flex items-center justify-center gap-2 shadow-lg">
              <HelpCircle size={18} /> Contact Support
            </button>
          </div>
        </div>
      </div>

      {/* Telegram Integration */}
      <div className="bg-slate-900 rounded-xl border border-slate-800 p-5 md:p-6 mb-6">
        <h2 className="text-lg font-bold text-white mb-2">
          Telegram Integration
        </h2>
        <p className="text-slate-400 text-sm mb-6">
          Send a test message to the configured Telegram channel to verify
          connectivity.
        </p>

        <div className="flex flex-col md:flex-row gap-4">
          <input
            type="text"
            placeholder="Enter test message..."
            value={pingMsg}
            onChange={(e) => setPingMsg(e.target.value)}
            className="w-full bg-slate-950 border border-slate-800 text-white rounded-lg px-4 py-3.5 md:py-2.5 focus:ring-2 focus:ring-emerald-500 outline-none transition-all"
          />
          <button
            onClick={handlePing}
            disabled={status === 'loading'}
            className={`w-full md:w-auto px-6 py-3.5 md:py-2.5 rounded-lg font-bold flex items-center justify-center gap-2 transition-all active:scale-95 whitespace-nowrap ${
              status === 'success'
                ? 'bg-emerald-500 text-white shadow-[0_0_15px_rgba(16,185,129,0.4)]'
                : status === 'error'
                ? 'bg-rose-500 text-white'
                : 'bg-blue-600 hover:bg-blue-700 text-white shadow-lg shadow-blue-900/20'
            }`}
          >
            {status === 'loading' ? (
              <span className="animate-pulse">Sending...</span>
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
                <Send size={18} /> Test Ping
              </>
            )}
          </button>
        </div>
      </div>

      {/* API Connection */}
      <div className="bg-slate-900 rounded-xl border border-slate-800 p-5 md:p-6">
        <h2 className="text-lg font-bold text-white mb-4">API Connection</h2>
        <div className="space-y-0 divide-y divide-slate-800">
          <div className="flex items-center justify-between py-4">
            <span className="text-slate-400 text-sm">Endpoint</span>
            <code className="bg-slate-950 border border-slate-800 px-2 py-1 rounded text-emerald-400 font-mono text-xs md:text-sm">
              http://localhost:8010
            </code>
          </div>
          <div className="flex items-center justify-between py-4">
            <span className="text-slate-400 text-sm">Environment</span>
            <span className="text-white font-bold text-sm">v0.7 (Dev)</span>
          </div>
          <div className="flex items-center justify-between py-4">
            <span className="text-slate-400 text-sm">Trader Lab</span>
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 bg-rose-500 rounded-full" />
              <span className="text-slate-500 text-sm italic">
                Disconnected
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
