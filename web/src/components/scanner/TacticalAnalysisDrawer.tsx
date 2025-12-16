import { X, Bot, Shield, Target } from 'lucide-react';
import { AdvisorChat } from '../AdvisorChat';
import { formatPrice, formatRelativeTime } from '../../utils/format';

interface TacticalAnalysisDrawerProps {
    isOpen: boolean;
    onClose: () => void;
    signal: any;
}

export const TacticalAnalysisDrawer: React.FC<TacticalAnalysisDrawerProps> = ({ isOpen, onClose, signal }) => {
    if (!isOpen || !signal) return null;

    // Prep context for the advisor
    const analysisContext = {
        token: signal.token,
        direction: signal.direction.toLowerCase(),
        entry: signal.entry,
        tp: signal.tp || 0,
        sl: signal.sl || 0,
        timeframe: signal.timeframe,
        rogue_mode: true // Enable fun mode
    };

    return (
        <div className="fixed inset-x-0 bottom-0 top-16 z-40 flex justify-end pointer-events-none">
            {/* Backdrop - only clickable part is pointer-events-auto */}
            <div
                className="absolute inset-0 bg-black/60 backdrop-blur-sm transition-opacity pointer-events-auto"
                onClick={onClose}
            />

            {/* Slide-over Panel */}
            <div className="relative w-full max-w-md bg-slate-900 border-l border-slate-800 h-full shadow-2xl shadow-indigo-500/20 animate-slide-in-right flex flex-col pointer-events-auto">

                {/* Header */}
                <div className="flex items-center justify-between p-6 border-b border-slate-800 bg-slate-950/50">
                    <div>
                        <h2 className="text-lg font-bold text-white flex items-center gap-2">
                            <Bot className="text-indigo-400" size={20} />
                            Tactical Analysis
                        </h2>
                        <p className="text-xs text-slate-400 mt-1">
                            Use AI to validate this {signal.token} opportunity.
                        </p>
                    </div>
                    <button
                        onClick={onClose}
                        className="p-2 rounded-lg hover:bg-slate-800 text-slate-400 hover:text-white transition-colors"
                    >
                        <X size={20} />
                    </button>
                </div>

                {/* Signal Context Summary */}
                <div className="p-4 bg-slate-800/30 border-b border-slate-800 flex flex-col gap-3 text-xs">
                    {/* Key Levels Row */}
                    <div className="flex items-center justify-between text-slate-300 bg-slate-900/40 p-2 rounded-lg border border-slate-800/50">
                        <div className="flex flex-col items-center">
                            <span className="text-[10px] uppercase text-slate-500 font-bold">Entry</span>
                            <span className="font-mono font-bold text-white">{formatPrice(signal.entry)}</span>
                        </div>
                        <div className="w-px h-6 bg-slate-800"></div>
                        <div className="flex flex-col items-center">
                            <span className="text-[10px] uppercase text-emerald-500 font-bold">TP</span>
                            <span className="font-mono font-bold text-emerald-400">{formatPrice(signal.tp)}</span>
                        </div>
                        <div className="w-px h-6 bg-slate-800"></div>
                        <div className="flex flex-col items-center">
                            <span className="text-[10px] uppercase text-rose-500 font-bold">SL</span>
                            <span className="font-mono font-bold text-rose-400">{formatPrice(signal.sl)}</span>
                        </div>
                    </div>

                    {/* Rationale Snippet */}
                    {signal.rationale && (
                        <div className="text-slate-400 italic leading-relaxed px-1 text-[11px] border-l-2 border-indigo-500/30 pl-2">
                            "{signal.rationale}"
                        </div>
                    )}

                    {/* Meta Info */}
                    <div className="flex items-center justify-between text-[10px] text-slate-500 px-1">
                        <span>TF: {signal.timeframe}</span>
                        <span>{formatRelativeTime(signal.timestamp)}</span>
                    </div>
                </div>

                {/* Chat Area */}
                <div className="flex-1 overflow-hidden relative">
                    <AdvisorChat
                        initialContext={analysisContext}
                        embedded={true}
                    />
                </div>
            </div>
        </div>
    );
};
