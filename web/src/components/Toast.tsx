
import React, { useEffect, useState } from 'react';
import { ToastAlert } from '../types';
import { notificationService } from '../services/notification';
import { CheckCircle, AlertTriangle, Info, XCircle, X } from 'lucide-react';

export const ToastContainer: React.FC = () => {
  const [toasts, setToasts] = useState<ToastAlert[]>([]);

  useEffect(() => {
    const remove = notificationService.subscribe((toast) => {
      setToasts((prev) => [...prev, toast]);
      // Auto dismiss
      setTimeout(() => {
        setToasts((prev) => prev.filter((t) => t.id !== toast.id));
      }, 5000);
    });
    return remove;
  }, []);

  const dismiss = (id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  };

  return (
    <div className="fixed top-4 left-0 right-0 z-[100] flex flex-col items-center gap-2 pointer-events-none px-4">
      {toasts.map((toast) => (
        <div
          key={toast.id}
          className="pointer-events-auto w-full max-w-sm bg-slate-900/95 backdrop-blur border border-slate-700 shadow-2xl rounded-lg p-4 flex items-start gap-3 animate-in slide-in-from-top-5 fade-in duration-300"
        >
          <div className="mt-0.5 flex-shrink-0">
            {toast.type === 'success' && <CheckCircle className="text-emerald-400" size={20} />}
            {toast.type === 'error' && <XCircle className="text-rose-400" size={20} />}
            {toast.type === 'warning' && <AlertTriangle className="text-amber-400" size={20} />}
            {toast.type === 'info' && <Info className="text-blue-400" size={20} />}
          </div>
          <div className="flex-1">
            <h4 className="font-bold text-white text-sm">{toast.title}</h4>
            <p className="text-sm text-slate-300 mt-0.5 leading-tight">{toast.message}</p>
          </div>
          <button onClick={() => dismiss(toast.id)} className="text-slate-500 hover:text-white">
            <X size={16} />
          </button>
        </div>
      ))}
    </div>
  );
};
