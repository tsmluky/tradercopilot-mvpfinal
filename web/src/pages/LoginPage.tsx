
import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { Activity, Lock, Mail, ArrowRight, Loader2, TrendingUp, ShieldCheck } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export const LoginPage: React.FC = () => {
  const [email, setEmail] = useState('demo@tradercopilot.com');
  const [password, setPassword] = useState('demo');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await login(email, password);
      navigate('/');
    } catch (err) {
      setError('Invalid credentials. Try demo@tradercopilot.com / demo');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 flex items-center justify-center p-4 relative overflow-hidden">
      
      {/* Ambient Background Effects */}
      <div className="absolute inset-0 z-0 overflow-hidden pointer-events-none">
         {/* Top gradient */}
         <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full max-w-3xl h-[500px] bg-emerald-500/10 blur-[120px] rounded-full mix-blend-screen opacity-50"></div>
         {/* Bottom gradient */}
         <div className="absolute bottom-0 right-0 w-[500px] h-[500px] bg-indigo-500/10 blur-[100px] rounded-full mix-blend-screen opacity-30"></div>
         
         {/* Grid Texture */}
         <div className="absolute inset-0 bg-[linear-gradient(to_right,#80808012_1px,transparent_1px),linear-gradient(to_bottom,#80808012_1px,transparent_1px)] bg-[size:24px_24px]"></div>
      </div>

      <div className="max-w-md w-full bg-slate-900/60 backdrop-blur-2xl rounded-3xl border border-slate-800/50 shadow-2xl p-8 animate-fade-in relative z-10 ring-1 ring-white/5">
        <div className="text-center mb-8">
          <div className="relative inline-block group">
             <div className="absolute inset-0 bg-emerald-500 blur-xl opacity-20 group-hover:opacity-40 transition-opacity duration-500 rounded-full"></div>
             <div className="relative w-16 h-16 bg-slate-900 rounded-2xl flex items-center justify-center mx-auto border border-slate-700 shadow-xl mb-6">
                <Activity className="text-emerald-400 drop-shadow-[0_0_10px_rgba(52,211,153,0.5)]" size={32} />
             </div>
          </div>
          
          <h1 className="text-3xl font-bold text-white tracking-tight mb-2">Terminal Access</h1>
          <div className="flex items-center justify-center gap-2 text-slate-400 text-sm font-medium bg-slate-950/50 py-1 px-3 rounded-full w-fit mx-auto border border-slate-800/50">
             <ShieldCheck size={12} className="text-emerald-500" />
             <span>Secure Environment v0.7</span>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="space-y-5">
          <div>
            <label className="block text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-2 ml-1">Authorized Email</label>
            <div className="relative group">
              <Mail className="absolute left-3.5 top-3.5 text-slate-500 group-focus-within:text-emerald-400 transition-colors" size={18} />
              <input 
                type="email" 
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full bg-slate-950/50 border border-slate-800 text-white rounded-xl py-3 pl-11 pr-4 focus:ring-2 focus:ring-emerald-500/50 focus:border-emerald-500/50 outline-none transition-all placeholder:text-slate-600"
                placeholder="name@company.com"
              />
            </div>
          </div>

          <div>
            <label className="block text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-2 ml-1">Access Key</label>
            <div className="relative group">
              <Lock className="absolute left-3.5 top-3.5 text-slate-500 group-focus-within:text-emerald-400 transition-colors" size={18} />
              <input 
                type="password" 
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full bg-slate-950/50 border border-slate-800 text-white rounded-xl py-3 pl-11 pr-4 focus:ring-2 focus:ring-emerald-500/50 focus:border-emerald-500/50 outline-none transition-all placeholder:text-slate-600"
                placeholder="••••••••"
              />
            </div>
          </div>

          {error && (
            <div className="p-3 bg-rose-500/10 border border-rose-500/20 rounded-lg text-rose-400 text-sm text-center animate-in fade-in slide-in-from-top-1">
              {error}
            </div>
          )}

          <button 
            type="submit" 
            disabled={loading}
            className="w-full bg-emerald-500 hover:bg-emerald-400 text-slate-900 font-bold py-3.5 rounded-xl transition-all flex items-center justify-center gap-2 disabled:opacity-70 disabled:cursor-not-allowed shadow-lg shadow-emerald-900/20 active:scale-[0.98] mt-2"
          >
            {loading ? <Loader2 className="animate-spin" size={20} /> : <>Initialize Session <ArrowRight size={20} /></>}
          </button>
        </form>

        <div className="mt-8 pt-6 border-t border-slate-800/50 text-center">
           <p className="text-xs text-slate-500 leading-relaxed">
             Restricted access. Unauthorized use is prohibited.<br/>
             <span className="opacity-50">Use </span><code className="text-slate-400 font-mono bg-slate-950 px-1 py-0.5 rounded border border-slate-800">demo/demo</code><span className="opacity-50"> for evaluation.</span>
           </p>
        </div>
      </div>
      
      {/* Bottom Ticker Decoration */}
      <div className="absolute bottom-8 flex items-center gap-2 text-slate-700 text-xs font-mono opacity-50">
          <TrendingUp size={14} />
          <span>MARKET DATA FEED: ONLINE</span>
          <span className="w-1 h-1 bg-emerald-500 rounded-full animate-pulse ml-2"></span>
      </div>
    </div>
  );
};
