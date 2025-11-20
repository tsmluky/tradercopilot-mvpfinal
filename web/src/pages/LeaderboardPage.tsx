
import React, { useEffect, useState } from 'react';
import { Trophy, Medal, TrendingUp, Zap, Crown } from 'lucide-react';
import { api } from '../services/api';
import { LeaderboardEntry } from '../types';
import { Link } from 'react-router-dom';

export const LeaderboardPage: React.FC = () => {
  const [entries, setEntries] = useState<LeaderboardEntry[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetch = async () => {
      setLoading(true);
      try {
        const data = await api.fetchLeaderboard();
        setEntries(data);
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    };
    fetch();
  }, []);

  return (
    <div className="p-6 md:p-8 max-w-5xl mx-auto">
      <div className="mb-8 text-center">
        <h1 className="text-3xl font-bold text-white mb-2 flex items-center justify-center gap-3">
           <Trophy className="text-amber-400" size={32} /> Global Trader Ranking
        </h1>
        <p className="text-slate-400 max-w-lg mx-auto">
          Top performers tracked by Paper Trading PnL. <br/>
          Signals must be tracked within 30 seconds of generation to qualify.
        </p>
      </div>

      <div className="bg-slate-900 rounded-2xl border border-slate-800 shadow-2xl overflow-hidden mb-8">
         <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
               <thead className="bg-slate-950 border-b border-slate-800">
                  <tr>
                     <th className="p-6 text-xs font-bold text-slate-500 uppercase tracking-wider w-24 text-center">Rank</th>
                     <th className="p-6 text-xs font-bold text-slate-500 uppercase tracking-wider">Trader</th>
                     <th className="p-6 text-xs font-bold text-slate-500 uppercase tracking-wider text-right">Win Rate</th>
                     <th className="p-6 text-xs font-bold text-slate-500 uppercase tracking-wider text-right">Total PnL</th>
                     <th className="p-6 text-xs font-bold text-slate-500 uppercase tracking-wider text-right">Signals</th>
                  </tr>
               </thead>
               <tbody className="divide-y divide-slate-800 text-slate-300">
                  {loading ? (
                      [1,2,3,4,5].map(i => (
                          <tr key={i}>
                              <td colSpan={5} className="p-6"><div className="h-6 bg-slate-800 rounded animate-pulse"></div></td>
                          </tr>
                      ))
                  ) : (
                      entries.map((entry) => (
                          <tr key={entry.rank} className={`hover:bg-slate-800/50 transition-colors ${entry.is_current_user ? 'bg-emerald-900/10 border-l-2 border-l-emerald-500' : ''}`}>
                             <td className="p-6 text-center">
                                <div className="flex justify-center">
                                    {entry.rank === 1 ? <div className="w-8 h-8 bg-amber-400/20 text-amber-400 rounded-full flex items-center justify-center font-bold border border-amber-400/50"><Crown size={16} /></div> :
                                     entry.rank === 2 ? <div className="w-8 h-8 bg-slate-300/20 text-slate-300 rounded-full flex items-center justify-center font-bold border border-slate-300/50">2</div> :
                                     entry.rank === 3 ? <div className="w-8 h-8 bg-orange-700/20 text-orange-400 rounded-full flex items-center justify-center font-bold border border-orange-700/50">3</div> :
                                     <span className="font-mono font-bold text-slate-500">#{entry.rank}</span>}
                                </div>
                             </td>
                             <td className="p-6">
                                <div className="flex items-center gap-3">
                                   <img src={entry.avatar_url} className="w-10 h-10 rounded-full border border-slate-700" />
                                   <div>
                                      <div className={`font-bold ${entry.is_current_user ? 'text-emerald-400' : 'text-white'}`}>
                                          {entry.user_name} {entry.is_current_user && '(You)'}
                                      </div>
                                      {entry.rank <= 3 && <div className="text-[10px] text-amber-500 font-bold uppercase tracking-wide">Top Performer</div>}
                                   </div>
                                </div>
                             </td>
                             <td className="p-6 text-right">
                                <span className="font-mono font-bold text-white">{entry.win_rate}%</span>
                             </td>
                             <td className="p-6 text-right">
                                <span className={`font-mono font-bold ${entry.total_pnl > 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                                   {entry.total_pnl > 0 ? '+' : ''}{entry.total_pnl}R
                                </span>
                             </td>
                             <td className="p-6 text-right font-mono text-slate-400">
                                {entry.signals_tracked}
                             </td>
                          </tr>
                      ))
                  )}
               </tbody>
            </table>
         </div>
      </div>

      {/* Membership Upsell */}
      <div className="bg-gradient-to-r from-emerald-900/40 to-slate-900 rounded-xl border border-emerald-500/30 p-8 flex flex-col md:flex-row items-center justify-between gap-6">
         <div>
            <h2 className="text-xl font-bold text-white mb-2 flex items-center gap-2">
                <Zap className="text-amber-400" fill="currentColor" /> Climb the Ranks Faster
            </h2>
            <p className="text-slate-300 text-sm max-w-md">
                PRO members receive 5x more signals daily, giving you more opportunities to grow your PnL and top the leaderboard.
            </p>
         </div>
         <Link to="/membership" className="bg-emerald-500 hover:bg-emerald-600 text-white font-bold px-8 py-3 rounded-lg shadow-lg shadow-emerald-500/20 transition-all transform hover:scale-105 whitespace-nowrap">
            Upgrade to PRO
         </Link>
      </div>
    </div>
  );
};
