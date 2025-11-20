
import React, { useEffect, useState } from 'react';
import { TrendingUp, TrendingDown } from 'lucide-react';

interface TickerItem {
  symbol: string;
  price: number;
  change: number;
}

export const MarketTicker: React.FC = () => {
  // Initial mock state
  const [items, setItems] = useState<TickerItem[]>([
    { symbol: 'BTC/USDT', price: 96420.50, change: 2.4 },
    { symbol: 'ETH/USDT', price: 3675.80, change: -0.8 },
    { symbol: 'SOL/USDT', price: 212.15, change: 5.2 },
    { symbol: 'XAU/USD', price: 2340.10, change: 0.1 },
    { symbol: 'BTC.D', price: 58.2, change: 0.3 },
    { symbol: 'TOTAL3', price: 780.5, change: 1.2 },
    { symbol: 'FEAR&GREED', price: 78, change: 0 },
  ]);

  // Simulate live updates
  useEffect(() => {
    const interval = setInterval(() => {
      setItems(prev => prev.map(item => ({
        ...item,
        price: item.symbol === 'FEAR&GREED' ? item.price : item.price * (1 + (Math.random() - 0.5) * 0.0005),
      })));
    }, 2000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="h-8 bg-slate-950 border-b border-slate-900 flex items-center overflow-hidden relative">
      <div className="flex items-center gap-8 animate-marquee whitespace-nowrap px-4">
        {/* Duplicate list for seamless loop effect */}
        {[...items, ...items, ...items].map((item, idx) => (
          <div key={idx} className="flex items-center gap-2 text-xs font-mono">
            <span className="font-bold text-slate-400">{item.symbol}</span>
            <span className="text-slate-200">{item.price.toFixed(item.symbol === 'FEAR&GREED' ? 0 : 2)}</span>
            <span className={`flex items-center ${item.change >= 0 ? 'text-emerald-500' : 'text-rose-500'}`}>
              {item.change >= 0 ? <TrendingUp size={10} className="mr-0.5" /> : <TrendingDown size={10} className="mr-0.5" />}
              {Math.abs(item.change)}%
            </span>
          </div>
        ))}
      </div>
      
      {/* Gradient Masks for fade effect */}
      <div className="absolute left-0 top-0 bottom-0 w-8 bg-gradient-to-r from-slate-950 to-transparent pointer-events-none"></div>
      <div className="absolute right-0 top-0 bottom-0 w-8 bg-gradient-to-l from-slate-950 to-transparent pointer-events-none"></div>
      
      <style>{`
        @keyframes marquee {
          0% { transform: translateX(0); }
          100% { transform: translateX(-33.33%); }
        }
        .animate-marquee {
          animation: marquee 20s linear infinite;
        }
        .animate-marquee:hover {
          animation-play-state: paused;
        }
      `}</style>
    </div>
  );
};
