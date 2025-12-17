import React, { useState, useEffect, useRef } from 'react';
import { Search, ChevronDown, Check, Lock } from 'lucide-react';

interface TokenSelectorProps {
    value: string;
    onChange: (token: string) => void;
    availableTokens: string[];
    isProUser: boolean;
}

export const TokenSelector: React.FC<TokenSelectorProps> = ({ value, onChange, availableTokens = [], isProUser }) => {
    const [isOpen, setIsOpen] = useState(false);
    const [search, setSearch] = useState("");
    const wrapperRef = useRef<HTMLDivElement>(null);

    // Initial value safety
    useEffect(() => {
        if (value && !search) {
            // Don't auto-set search to value to keep it clean, or maybe we should?
            // Usually combobox shows value. 
        }
    }, [value]);

    useEffect(() => {
        function handleClickOutside(event: MouseEvent) {
            if (wrapperRef.current && !wrapperRef.current.contains(event.target as Node)) {
                setIsOpen(false);
            }
        }
        document.addEventListener("mousedown", handleClickOutside);
        return () => document.removeEventListener("mousedown", handleClickOutside);
    }, [wrapperRef]);

    const filtered = availableTokens.filter(t =>
        t.toUpperCase().includes(search.toUpperCase())
    );

    // Group for display? Nah, simple list for now.

    return (
        <div className="relative" ref={wrapperRef}>
            <div
                className="flex items-center justify-between w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-3 text-sm text-slate-200 cursor-pointer hover:border-slate-700 transition-colors"
                onClick={() => setIsOpen(!isOpen)}
            >
                <div className="flex items-center gap-3">
                    {value && (
                        <div className="w-6 h-6 rounded-full bg-indigo-500/20 text-indigo-400 flex items-center justify-center text-[10px] font-bold border border-indigo-500/30">
                            {value.substring(0, 1)}
                        </div>
                    )}
                    <span className="font-bold tracking-wide">{value || "Select Asset"}</span>
                </div>
                <ChevronDown size={16} className={`text-slate-500 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
            </div>

            {isOpen && (
                <div className="absolute top-full left-0 right-0 mt-2 bg-[#0b1121] border border-slate-700 rounded-xl shadow-2xl z-50 overflow-hidden animate-in fade-in zoom-in-95 duration-200">

                    {/* Search Bar */}
                    <div className="p-2 border-b border-slate-800 sticky top-0 bg-[#0b1121] z-10">
                        <div className="relative">
                            <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
                            <input
                                type="text"
                                placeholder="Search token..."
                                className="w-full bg-slate-900 border border-slate-800 rounded-lg pl-9 pr-3 py-2 text-xs text-white placeholder-slate-600 focus:outline-none focus:border-indigo-500 transition-colors"
                                autoFocus
                                value={search}
                                onChange={(e) => setSearch(e.target.value)}
                            />
                        </div>
                    </div>

                    {/* List */}
                    <div className="max-h-60 overflow-y-auto custom-scrollbar p-1">
                        {filtered.length > 0 ? (
                            filtered.map(token => {
                                const isSelected = token === value;
                                return (
                                    <div
                                        key={token}
                                        onClick={() => {
                                            onChange(token);
                                            setIsOpen(false);
                                            setSearch("");
                                        }}
                                        className={`flex items-center justify-between px-3 py-2.5 rounded-lg cursor-pointer transition-colors ${isSelected
                                                ? 'bg-indigo-600/10 text-indigo-400'
                                                : 'text-slate-300 hover:bg-slate-800'
                                            }`}
                                    >
                                        <div className="flex items-center gap-3">
                                            <span className="font-bold text-sm">{token}</span>
                                            {/* Maybe add full name here later if we have a map */}
                                        </div>
                                        {isSelected && <Check size={14} />}
                                    </div>
                                );
                            })
                        ) : (
                            <div className="px-4 py-8 text-center text-slate-500 text-xs">
                                No tokens found.
                                {!isProUser && (
                                    <div className="mt-2 text-indigo-400 flex items-center justify-center gap-1">
                                        <Lock size={12} />
                                        <span>Upgrade to PRO for more</span>
                                    </div>
                                )}
                            </div>
                        )}

                        {!isProUser && filtered.length > 0 && (
                            <div className="px-3 py-2 border-t border-slate-800 text-[10px] text-center text-slate-500 bg-slate-900/30">
                                🔒 +100 tokens locked (PRO Plan)
                            </div>
                        )}
                    </div>
                </div>
            )}
        </div>
    );
};
