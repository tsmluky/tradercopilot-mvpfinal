import React, { useState, useEffect } from "react";
import { Loader2, BrainCircuit, LineChart, ShieldCheck, Newspaper } from "lucide-react";

const STEPS = [
    { text: "Scanning Market Structure...", icon: LineChart },
    { text: "Fetching OnChain Metrics...", icon: BrainCircuit },
    { text: "Analyzing Global Sentiment...", icon: Newspaper },
    { text: "Calculating Risk Adjustments...", icon: ShieldCheck },
    { text: "Drafting Institutional Report...", icon: BrainCircuit },
];

export const ThinkingOverlay: React.FC = () => {
    const [stepIndex, setStepIndex] = useState(0);

    useEffect(() => {
        const interval = setInterval(() => {
            setStepIndex((prev) => (prev + 1) % STEPS.length);
        }, 1200); // Change step every 1.2s

        return () => clearInterval(interval);
    }, []);

    const CurrentIcon = STEPS[stepIndex].icon;

    return (
        <div className="flex flex-col items-center justify-center p-12 space-y-4 animate-in fade-in duration-500">
            <div className="relative">
                <div className="absolute inset-0 bg-indigo-500/20 blur-xl rounded-full animate-pulse"></div>
                <div className="relative bg-slate-900 border border-slate-700/50 p-4 rounded-2xl shadow-2xl">
                    <Loader2 className="w-8 h-8 text-indigo-400 animate-spin" />
                </div>
            </div>

            <div className="text-center space-y-1">
                <h3 className="text-lg font-medium text-slate-200 flex items-center justify-center gap-2">
                    <CurrentIcon className="w-5 h-5 text-indigo-400 animate-bounce" />
                    {STEPS[stepIndex].text}
                </h3>
                <p className="text-xs text-slate-500 font-mono">
                    TraderCopilot AI Model v2.1
                </p>
            </div>

            {/* Progress Bar Simulation */}
            <div className="w-64 h-1 bg-slate-800 rounded-full overflow-hidden mt-4">
                <div className="h-full bg-indigo-500/50 animate-progress-indeterminate"></div>
            </div>
        </div>
    );
};
