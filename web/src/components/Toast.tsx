
import React, { useEffect, useState } from 'react';
import { ToastAlert } from '../types';
import { notificationService } from '../services/notification';
import { CheckCircle, AlertTriangle, Info, XCircle, X } from 'lucide-react';

export const ToastContainer: React.FC = () => {
  const [toasts, setToasts] = useState<ToastAlert[]>([]);

  useEffect(() => {
    const remove = notificationService.subscribe((toast) => {
      setToasts((prev) => [...prev, toast]);
      // Auto dismiss logic is handled by the ToastItem component now or we can keep it here
      // Keeping it here for simplicity, but individual timers would be better for UX if hovering
    });
    return remove;
  }, []);

  const dismiss = (id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  };

  return (
    <div className="fixed top-6 right-6 z-[100] flex flex-col items-end gap-3 pointer-events-none">
      {toasts.map((toast) => (
        <ToastItem key={toast.id} toast={toast} onDismiss={dismiss} />
      ))}
    </div>
  );
};

const ToastItem: React.FC<{ toast: ToastAlert; onDismiss: (id: string) => void }> = ({ toast, onDismiss }) => {
  const [exiting, setExiting] = useState(false);

  useEffect(() => {
    const timer = setTimeout(() => {
      handleDismiss();
    }, 5000);
    return () => clearTimeout(timer);
  }, []);

  const handleDismiss = () => {
    setExiting(true);
    setTimeout(() => {
      onDismiss(toast.id);
    }, 300); // Wait for exit animation
  };

  const getIcon = () => {
    switch (toast.type) {
      case 'success': return <CheckCircle className="text-emerald-400" size={20} />;
      case 'error': return <XCircle className="text-rose-400" size={20} />;
      case 'warning': return <AlertTriangle className="text-amber-400" size={20} />;
      default: return <Info className="text-blue-400" size={20} />;
    }
  };

  const getBorderColor = () => {
    switch (toast.type) {
      case 'success': return 'border-emerald-500/30';
      case 'error': return 'border-rose-500/30';
      case 'warning': return 'border-amber-500/30';
      default: return 'border-blue-500/30';
    }
  };

  const getBgColor = () => {
    switch (toast.type) {
      case 'success': return 'bg-emerald-950/80';
      case 'error': return 'bg-rose-950/80';
      case 'warning': return 'bg-amber-950/80';
      default: return 'bg-slate-900/90';
    }
  };

  return (
    <div
      className={`
        pointer-events-auto w-80 
        ${getBgColor()} backdrop-blur-md 
        border ${getBorderColor()} 
        shadow-lg shadow-black/20 rounded-xl p-4 
        flex items-start gap-3 
        transition-all duration-300 ease-out
        ${exiting ? 'opacity-0 translate-x-10' : 'opacity-100 translate-x-0 animate-in slide-in-from-right-5 fade-in'}
      `}
    >
      <div className="mt-0.5 flex-shrink-0">
        {getIcon()}
      </div>
      <div className="flex-1">
        <h4 className="font-semibold text-white text-sm tracking-wide">{toast.title}</h4>
        <p className="text-xs text-slate-300 mt-1 leading-relaxed">{toast.message}</p>
      </div>
      <button
        onClick={handleDismiss}
        className="text-slate-500 hover:text-white transition-colors p-1 hover:bg-white/10 rounded-full"
      >
        <X size={14} />
      </button>
    </div>
  );
};
