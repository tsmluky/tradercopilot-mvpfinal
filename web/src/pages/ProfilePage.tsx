
import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { TOKENS } from '../constants';
import { User, CreditCard, Save, TrendingUp, Bookmark, Activity, LayoutDashboard, ChevronRight, Edit3, FileText, Trophy } from 'lucide-react';
import { Link } from 'react-router-dom';

export const ProfilePage: React.FC = () => {
  const { userProfile, updateProfile, updateSignalNote } = useAuth();
  const [isEditing, setIsEditing] = useState(false);
  
  // Profile Form state
  const [name, setName] = useState(userProfile?.user.name || '');
  const [favorites, setFavorites] = useState<string[]>(userProfile?.preferences.favorite_tokens || []);

  // Note Editing State
  const [editingNoteId, setEditingNoteId] = useState<string | null>(null);
  const [noteContent, setNoteContent] = useState('');

  if (!userProfile) return null;

  const handleSaveProfile = async () => {
    await updateProfile(name, favorites);
    setIsEditing(false);
  };

  const toggleFavorite = (tokenId: string) => {
    if (favorites.includes(tokenId)) {
      setFavorites(favorites.filter(id => id !== tokenId));
    } else {
      setFavorites([...favorites, tokenId]);
    }
  };

  const handleEditNote = (timestamp: string, token: string, currentNote: string) => {
      setEditingNoteId(`${timestamp}-${token}`);
      setNoteContent(currentNote || '');
  };

  const handleSaveNote = async (timestamp: string, token: string) => {
      await updateSignalNote(timestamp, token, noteContent);
      setEditingNoteId(null);
  };

  // Calculate Portfolio Stats
  const followed = userProfile.portfolio.followed_signals;
  const closedTrades = followed.filter(s => s.status === 'WIN' || s.status === 'LOSS');
  const wins = closedTrades.filter(s => s.status === 'WIN').length;
  const winRate = closedTrades.length > 0 ? Math.round((wins / closedTrades.length) * 100) : 0;
  const totalPnL = closedTrades.reduce((acc, curr) => acc + (curr.final_pnl || 0), 0);

  return (
    <div className="p-6 md:p-8 max-w-7xl mx-auto">
      <h1 className="text-2xl font-bold text-white mb-8 flex items-center gap-2">
        <User className="text-emerald-400" /> Trader Profile
      </h1>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left Col: User Details & Settings */}
        <div className="space-y-6">
            
            {/* User Info Card */}
            <div className="bg-slate-900 rounded-xl border border-slate-800 p-6 shadow-lg">
                <div className="flex flex-col items-center mb-6">
                    <img src={userProfile.user.avatar_url} className="w-24 h-24 rounded-full border-4 border-slate-800 mb-4" />
                    {!isEditing ? (
                        <>
                            <h2 className="text-xl font-bold text-white">{userProfile.user.name}</h2>
                            <p className="text-slate-400 text-sm">{userProfile.user.email}</p>
                            <button onClick={() => setIsEditing(true)} className="mt-4 text-xs font-bold text-emerald-400 hover:text-emerald-300 uppercase">Edit Profile</button>
                        </>
                    ) : (
                        <div className="w-full space-y-3">
                             <div>
                                <label className="text-xs font-bold text-slate-500 uppercase">Display Name</label>
                                <input 
                                    type="text" 
                                    value={name} 
                                    onChange={e => setName(e.target.value)} 
                                    className="w-full bg-slate-950 border border-slate-700 text-white rounded px-3 py-2 text-sm focus:ring-1 focus:ring-emerald-500 outline-none"
                                />
                             </div>
                             <button 
                                onClick={handleSaveProfile}
                                className="w-full bg-emerald-500 hover:bg-emerald-600 text-white text-xs font-bold py-2 rounded flex items-center justify-center gap-2"
                             >
                                <Save size={14} /> Save Changes
                             </button>
                        </div>
                    )}
                </div>
                
                <div className="border-t border-slate-800 pt-4">
                    <div className="flex justify-between items-center text-sm mb-2">
                        <span className="text-slate-500">Plan</span>
                        <Link to="/membership" className="font-bold text-white capitalize flex items-center gap-1 hover:text-emerald-400 transition-colors">
                            <CreditCard size={14} className="text-emerald-400" /> {userProfile.user.subscription_status} <ChevronRight size={14} />
                        </Link>
                    </div>
                    <div className="flex justify-between items-center text-sm">
                        <span className="text-slate-500">Role</span>
                        <span className="font-bold text-slate-400 capitalize">{userProfile.user.role}</span>
                    </div>
                </div>
            </div>

            {/* Rank / Gamification Card (New) */}
            <Link to="/leaderboard" className="block bg-gradient-to-br from-slate-900 to-indigo-950/30 rounded-xl border border-slate-800 hover:border-indigo-500/50 p-6 shadow-lg transition-colors group">
                <div className="flex justify-between items-start">
                    <div>
                         <h3 className="text-sm font-bold text-white uppercase tracking-wider mb-1 flex items-center gap-2">
                            <Trophy size={16} className="text-amber-400" /> Global Rank
                        </h3>
                        <p className="text-xs text-slate-400">Compete with top traders</p>
                    </div>
                    <div className="bg-slate-950 px-3 py-1 rounded border border-slate-800 group-hover:border-indigo-500/30 transition-colors">
                        <span className="text-lg font-bold text-white font-mono">#4</span>
                    </div>
                </div>
                <div className="mt-4 flex items-center gap-2 text-xs font-bold text-indigo-400 group-hover:text-indigo-300">
                    View Leaderboard <ChevronRight size={12} />
                </div>
            </Link>

            {/* Preferences Card */}
            <div className="bg-slate-900 rounded-xl border border-slate-800 p-6 shadow-lg">
                <h3 className="text-sm font-bold text-white uppercase tracking-wider mb-4 flex items-center gap-2">
                    <Activity size={16} /> Watchlist
                </h3>
                <div className="flex flex-wrap gap-2">
                    {TOKENS.map(t => {
                        const isActive = isEditing ? favorites.includes(t.id) : userProfile.preferences.favorite_tokens.includes(t.id);
                        return (
                            <button
                                key={t.id}
                                disabled={!isEditing}
                                onClick={() => toggleFavorite(t.id)}
                                className={`px-3 py-1.5 rounded text-xs font-bold border transition-all ${
                                    isActive 
                                    ? 'bg-emerald-500/10 border-emerald-500/50 text-emerald-400'
                                    : 'bg-slate-950 border-slate-800 text-slate-500'
                                } ${isEditing ? 'cursor-pointer hover:border-slate-600' : 'cursor-default'}`}
                            >
                                {t.symbol}
                            </button>
                        );
                    })}
                </div>
                {!isEditing && <p className="text-xs text-slate-600 mt-3 italic">Click "Edit Profile" to manage watchlist.</p>}
            </div>
        </div>

        {/* Right Col: Portfolio & History */}
        <div className="lg:col-span-2 space-y-6">
            
            {/* Personal Stats */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                 <div className="bg-indigo-900/20 border border-indigo-500/20 rounded-xl p-5">
                    <div className="text-indigo-400 mb-2"><TrendingUp size={20} /></div>
                    <div className="text-xs font-bold text-slate-500 uppercase">Personal Win Rate</div>
                    <div className="text-2xl font-bold text-white font-mono">{winRate}%</div>
                    <div className="text-xs text-slate-400 mt-1">{closedTrades.length} evaluated trades</div>
                 </div>
                 <div className="bg-emerald-900/20 border border-emerald-500/20 rounded-xl p-5">
                    <div className="text-emerald-400 mb-2"><Activity size={20} /></div>
                    <div className="text-xs font-bold text-slate-500 uppercase">Net PnL</div>
                    <div className={`text-2xl font-bold font-mono ${totalPnL >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                        {totalPnL > 0 ? '+' : ''}{totalPnL.toFixed(1)}R
                    </div>
                    <div className="text-xs text-slate-400 mt-1">Based on tracked signals</div>
                 </div>
                 <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
                    <div className="text-slate-400 mb-2"><Bookmark size={20} /></div>
                    <div className="text-xs font-bold text-slate-500 uppercase">Signals Tracked</div>
                    <div className="text-2xl font-bold text-white font-mono">{followed.length}</div>
                    <div className="text-xs text-slate-400 mt-1">Lifetime history</div>
                 </div>
            </div>

            {/* Followed Signals List with Journaling */}
            <div className="bg-slate-900 rounded-xl border border-slate-800 shadow-lg overflow-hidden flex flex-col h-[500px]">
                <div className="p-4 border-b border-slate-800 flex justify-between items-center bg-slate-800/50">
                    <h3 className="font-bold text-white flex items-center gap-2">
                        <LayoutDashboard size={18} className="text-indigo-400" /> Portfolio Journal
                    </h3>
                    <span className="text-xs text-slate-500">Last {followed.length} tracked signals</span>
                </div>
                
                <div className="overflow-y-auto flex-1 p-0">
                    {followed.length === 0 ? (
                        <div className="h-full flex flex-col items-center justify-center text-slate-500">
                            <Bookmark size={48} className="mb-4 opacity-20" />
                            <p>You haven't tracked any signals yet.</p>
                            <p className="text-xs mt-2">Click "Track" on any LITE signal to add it here.</p>
                        </div>
                    ) : (
                        <table className="w-full text-left border-collapse">
                            <thead className="bg-slate-950 text-xs uppercase text-slate-500 font-bold sticky top-0">
                                <tr>
                                    <th className="p-4">Date</th>
                                    <th className="p-4">Token</th>
                                    <th className="p-4">Entry</th>
                                    <th className="p-4">Result</th>
                                    <th className="p-4">Journal Notes</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-slate-800 text-sm text-slate-300">
                                {[...followed].reverse().map((sig, i) => {
                                    const uniqueId = `${sig.timestamp}-${sig.token}`;
                                    const isEditingNote = editingNoteId === uniqueId;

                                    return (
                                    <tr key={i} className="hover:bg-slate-800/50 transition-colors align-top">
                                        <td className="p-4 font-mono text-xs text-slate-500">
                                            {new Date(sig.timestamp).toLocaleDateString()} <br/>
                                            {new Date(sig.timestamp).toLocaleTimeString([], {hour:'2-digit', minute:'2-digit'})}
                                        </td>
                                        <td className="p-4">
                                            <div className="font-bold">{sig.token}</div>
                                            <div className={`text-xs uppercase font-bold ${sig.direction === 'long' ? 'text-emerald-400' : 'text-rose-400'}`}>{sig.direction}</div>
                                        </td>
                                        <td className="p-4 font-mono">{sig.entry}</td>
                                        <td className="p-4">
                                            <span className={`px-2 py-1 rounded text-[10px] font-bold uppercase ${
                                                sig.status === 'WIN' ? 'bg-emerald-500/10 text-emerald-400' : 
                                                sig.status === 'LOSS' ? 'bg-rose-500/10 text-rose-400' : 
                                                'bg-slate-700 text-slate-400'
                                            }`}>
                                                {sig.status || 'OPEN'}
                                            </span>
                                        </td>
                                        <td className="p-4">
                                            {isEditingNote ? (
                                                <div className="flex flex-col gap-2">
                                                    <textarea 
                                                        className="w-full bg-slate-950 border border-slate-700 rounded p-2 text-xs text-white focus:border-indigo-500 outline-none resize-none h-20"
                                                        value={noteContent}
                                                        onChange={(e) => setNoteContent(e.target.value)}
                                                        placeholder="Enter trade notes..."
                                                        autoFocus
                                                    />
                                                    <div className="flex gap-2">
                                                        <button onClick={() => handleSaveNote(sig.timestamp, sig.token)} className="px-3 py-1 bg-emerald-500 text-white text-xs font-bold rounded hover:bg-emerald-600">Save</button>
                                                        <button onClick={() => setEditingNoteId(null)} className="px-3 py-1 bg-slate-700 text-slate-300 text-xs font-bold rounded hover:bg-slate-600">Cancel</button>
                                                    </div>
                                                </div>
                                            ) : (
                                                <div className="group relative cursor-pointer" onClick={() => handleEditNote(sig.timestamp, sig.token, sig.notes || '')}>
                                                    {sig.notes ? (
                                                        <div className="text-xs text-slate-300 italic bg-slate-950/50 p-2 rounded border border-slate-800/50 hover:border-slate-700 min-w-[150px]">
                                                            "{sig.notes}"
                                                        </div>
                                                    ) : (
                                                        <div className="text-xs text-slate-600 flex items-center gap-1 hover:text-slate-400">
                                                            <Edit3 size={12} /> Add note
                                                        </div>
                                                    )}
                                                </div>
                                            )}
                                        </td>
                                    </tr>
                                )})}
                            </tbody>
                        </table>
                    )}
                </div>
            </div>

        </div>
      </div>
    </div>
  );
};
