import React from 'react';
import { LucideIcon } from 'lucide-react';

interface MetricCardProps {
    label: string;
    value: string;
    trend: number;
    icon: LucideIcon;
}

export const MetricCard: React.FC<MetricCardProps> = ({ label, value, trend, icon: Icon }) => (
    <div className="bg-slate-900/80 border border-slate-800 p-3 px-5 rounded-xl flex items-center gap-4 min-w-[160px] backdrop-blur-md">
        <div className={`p-2 rounded-full ${trend >= 0 ? 'bg-emerald-500/10 text-emerald-400' : 'bg-rose-500/10 text-rose-400'}`}>
            <Icon size={20} />
        </div>
        <div>
            <div className="text-[10px] text-slate-500 uppercase font-bold tracking-wider">{label}</div>
            <div className="text-xl font-mono font-bold text-white">
                {value}
            </div>
            {trend !== 0 && (
                <div className={`text-[10px] font-bold ${trend > 0 ? 'text-emerald-500' : 'text-rose-500'}`}>
                    {trend > 0 ? '+' : ''}{trend}%
                </div>
            )}
        </div>
    </div>
);
