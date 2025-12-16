import React from 'react';
import { useLocation } from 'react-router-dom';
import { AdvisorChat } from '../components/AdvisorChat';
import { ShieldCheck } from 'lucide-react';

export const AdvisorPage: React.FC = () => {
    const location = useLocation();
    const context = location.state?.context;

    return (
        <div className="h-[calc(100vh-100px)] flex flex-col space-y-4">
            <div className="flex flex-col gap-2">
                <h1 className="text-2xl font-semibold text-slate-50 flex items-center gap-2">
                    <ShieldCheck className="w-6 h-6 text-indigo-400" />
                    Advisor Chat
                </h1>
                <p className="text-slate-400 text-sm">
                    Discuss signals, risk management, and market updates with your AI Copilot.
                </p>
            </div>

            <div className="flex-1 bg-slate-900 border border-slate-800 rounded-2xl overflow-hidden shadow-2xl">
                <AdvisorChat
                    embedded={true}
                    initialContext={context}
                    currentToken={context?.token}
                    currentTimeframe={context?.timeframe}
                />
            </div>
        </div>
    );
};
