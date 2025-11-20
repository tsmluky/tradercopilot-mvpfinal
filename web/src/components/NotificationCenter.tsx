
import React, { useState } from 'react';
import { Bell, CheckCircle, AlertTriangle, Info, X } from 'lucide-react';
import { Notification } from '../types';

export const NotificationCenter: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [notifications, setNotifications] = useState<Notification[]>([
    { id: '1', title: 'Target Hit', message: 'ETH/USDT hit TP1 (+1.5R)', time: '2m ago', type: 'success', read: false },
    { id: '2', title: 'New Signal', message: 'BTC/USDT Long Setup Detected', time: '15m ago', type: 'info', read: false },
    { id: '3', title: 'Risk Alert', message: 'High volatility expected in 1h', time: '2h ago', type: 'alert', read: true },
  ]);

  const unreadCount = notifications.filter(n => !n.read).length;

  const markAllRead = () => {
    setNotifications(prev => prev.map(n => ({ ...n, read: true })));
  };

  return (
    <div className="relative z-50">
      <button 
        onClick={() => setIsOpen(!isOpen)}
        className="relative p-2 rounded-full hover:bg-slate-800 text-slate-400 hover:text-white transition-colors"
      >
        <Bell size={20} />
        {unreadCount > 0 && (
          <span className="absolute top-1 right-1 w-2.5 h-2.5 bg-rose-500 rounded-full border-2 border-slate-900"></span>
        )}
      </button>

      {isOpen && (
        <>
          <div className="fixed inset-0 z-40" onClick={() => setIsOpen(false)}></div>
          <div className="absolute right-0 mt-2 w-80 bg-slate-900 border border-slate-800 rounded-xl shadow-2xl z-50 overflow-hidden animate-in fade-in slide-in-from-top-2">
            <div className="p-3 border-b border-slate-800 flex justify-between items-center bg-slate-900/95 backdrop-blur">
              <h3 className="text-sm font-bold text-white">Notifications</h3>
              {unreadCount > 0 && (
                <button onClick={markAllRead} className="text-[10px] text-emerald-400 hover:text-emerald-300 font-bold uppercase">
                  Mark all read
                </button>
              )}
            </div>
            
            <div className="max-h-[300px] overflow-y-auto">
              {notifications.length === 0 ? (
                <div className="p-8 text-center text-slate-500 text-xs">No notifications</div>
              ) : (
                notifications.map(n => (
                  <div key={n.id} className={`p-4 border-b border-slate-800/50 hover:bg-slate-800/50 transition-colors ${n.read ? 'opacity-60' : 'opacity-100'}`}>
                    <div className="flex gap-3">
                      <div className="mt-0.5">
                        {n.type === 'success' && <CheckCircle size={14} className="text-emerald-400" />}
                        {n.type === 'alert' && <AlertTriangle size={14} className="text-amber-400" />}
                        {n.type === 'info' && <Info size={14} className="text-blue-400" />}
                      </div>
                      <div className="flex-1">
                        <div className="flex justify-between items-start">
                          <h4 className="text-sm font-bold text-slate-200">{n.title}</h4>
                          <span className="text-[10px] text-slate-500">{n.time}</span>
                        </div>
                        <p className="text-xs text-slate-400 mt-0.5">{n.message}</p>
                      </div>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </>
      )}
    </div>
  );
};
