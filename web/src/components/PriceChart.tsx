import React, { useMemo, useEffect, useState } from 'react';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
} from 'recharts';
import { SignalLite } from '../types';
import { Maximize2 } from 'lucide-react';

interface PriceChartProps {
  token: string;
  signal?: SignalLite | null;
  timeframe: string;
  compact?: boolean;
}

export const PriceChart: React.FC<PriceChartProps> = ({
  token,
  signal,
  timeframe,
  compact = false,
}) => {
  const [chartData, setChartData] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const response = await fetch(
          `http://127.0.0.1:8010/market/ohlcv/${token}?timeframe=${timeframe}&limit=50`
        );

        if (!response.ok) throw new Error('Failed to fetch');

        const result = await response.json();
        const formatted = result.data.map((candle: any) => ({
          time: candle.time,
          price: candle.close,
          vol: candle.volume,
        }));

        setChartData(formatted);
      } catch (error) {
        console.error('Error fetching chart data:', error);
        // Fallback to mock data
        setChartData(generateMockData(signal?.entry || 3600));
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [token, timeframe, signal]);

  const domain = useMemo(() => {
    if (!signal || chartData.length === 0) return ['auto', 'auto'] as const;
    const values = [signal.entry, signal.tp, signal.sl, ...chartData.map((d) => d.price)];
    const min = Math.min(...values);
    const max = Math.max(...values);
    const padding = (max - min) * 0.1;
    return [min - padding, max + padding] as [number, number];
  }, [signal, chartData]);

  const currentPrice = chartData.length > 0 ? chartData[chartData.length - 1]?.price : null;

  return (
    <div
      className={
        compact
          ? 'h-full w-full'
          : 'bg-slate-900 rounded-xl border border-slate-800 shadow-lg p-4 h-full flex flex-col'
      }
    >
      {!compact && (
        <div className="flex justify-between items-center mb-4 px-2">
          <div>
            <h3 className="text-sm font-bold text-slate-400 uppercase tracking-wider flex items-center gap-2">
              <span className="text-emerald-400">{token.toUpperCase()}</span>
              <span className="text-slate-600">/</span>
              <span className="text-slate-500">USDT</span>
              <span className="text-xs bg-slate-800 px-1.5 py-0.5 rounded text-slate-500">
                {timeframe}
              </span>
            </h3>
            {currentPrice && (
              <p className="text-xs text-slate-500 mt-1">
                Current: <span className="text-white font-mono font-bold">${currentPrice.toFixed(2)}</span>
              </p>
            )}
          </div>
          <Maximize2
            size={14}
            className="text-slate-600 cursor-pointer hover:text-slate-400"
          />
        </div>
      )}

      <div
        className="w-full relative"
        style={{ height: compact ? 100 : 250, minWidth: 100 }}
      >
        {loading && (
          <div className="absolute inset-0 flex items-center justify-center bg-slate-950/50 z-10">
            <div className="w-8 h-8 border-2 border-slate-700 border-t-emerald-500 rounded-full animate-spin"></div>
          </div>
        )}

        <ResponsiveContainer width="100%" height="100%" minWidth={100} minHeight={100}>
          <AreaChart
            data={chartData}
            margin={
              compact
                ? { top: 5, right: 0, left: 0, bottom: 0 }
                : { top: 10, right: 30, left: 0, bottom: 0 }
            }
          >
            <defs>
              <linearGradient id="colorPrice" x1="0" y1="0" x2="0" y2="1">
                <stop
                  offset="5%"
                  stopColor="#3b82f6"
                  stopOpacity={compact ? 0.2 : 0.3}
                />
                <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
              </linearGradient>
            </defs>

            {!compact && (
              <CartesianGrid
                strokeDasharray="3 3"
                stroke="#1e293b"
                vertical={false}
              />
            )}

            {!compact && (
              <XAxis
                dataKey="time"
                stroke="#475569"
                tick={{ fontSize: 10 }}
                minTickGap={30}
              />
            )}

            {!compact && (
              <YAxis
                domain={domain}
                stroke="#475569"
                tick={{ fontSize: 11 }}
                tickFormatter={(val: number) => val.toFixed(1)}
                width={60}
                orientation="right"
              />
            )}

            {compact && <YAxis domain={domain} hide={true} />}

            {!compact && (
              <Tooltip
                contentStyle={{
                  backgroundColor: '#0f172a',
                  borderColor: '#334155',
                  fontSize: '12px',
                }}
                itemStyle={{ color: '#e2e8f0' }}
                formatter={(value: number) => [value.toFixed(2), 'Price']}
              />
            )}

            <Area
              type="monotone"
              dataKey="price"
              stroke="#3b82f6"
              strokeWidth={compact ? 1.5 : 2}
              fillOpacity={1}
              fill="url(#colorPrice)"
            />

            {signal && (
              <>
                <ReferenceLine
                  y={signal.entry}
                  stroke="#60a5fa"
                  strokeDasharray="3 3"
                  label={
                    compact
                      ? undefined
                      : {
                        position: 'insideLeft',
                        value: 'ENTRY',
                        fill: '#60a5fa',
                        fontSize: 10,
                      }
                  }
                />
                <ReferenceLine
                  y={signal.tp}
                  stroke="#10b981"
                  label={
                    compact
                      ? undefined
                      : {
                        position: 'insideLeft',
                        value: 'TP',
                        fill: '#10b981',
                        fontSize: 10,
                      }
                  }
                />
                <ReferenceLine
                  y={signal.sl}
                  stroke="#f43f5e"
                  label={
                    compact
                      ? undefined
                      : {
                        position: 'insideLeft',
                        value: 'SL',
                        fill: '#f43f5e',
                        fontSize: 10,
                      }
                  }
                />
              </>
            )}
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

// Helper to generate mock data
const generateMockData = (basePrice: number, points: number = 50) => {
  const data: { time: string; price: number; vol: number }[] = [];
  let currentPrice = basePrice * 0.98;
  const volatility = basePrice * 0.002;

  for (let i = 0; i < points; i++) {
    const change = (Math.random() - 0.45) * volatility * 5;
    currentPrice += change;

    if (i > points - 5) {
      currentPrice = basePrice + (Math.random() - 0.5) * volatility;
    }

    const date = new Date();
    date.setMinutes(date.getMinutes() - (points - i) * 15);

    data.push({
      time: date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      price: currentPrice,
      vol: Math.floor(Math.random() * 1000) + 500,
    });
  }
  return data;
};
