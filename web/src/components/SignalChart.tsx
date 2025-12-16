import React, { useEffect, useRef } from 'react';
import { createChart, ColorType, CrosshairMode } from 'lightweight-charts';

interface ChartProps {
    data: any[];
    entry?: number;
    tp?: number;
    sl?: number;
    direction?: "LONG" | "SHORT" | string;
}

export const SignalChart: React.FC<ChartProps> = ({ data, entry, tp, sl, direction }) => {
    const chartContainerRef = useRef<HTMLDivElement>(null);
    const chartRef = useRef<any>(null);

    useEffect(() => {
        if (!chartContainerRef.current || data.length === 0) return;

        const chart = createChart(chartContainerRef.current, {
            layout: {
                background: { type: ColorType.Solid, color: 'transparent' },
                textColor: '#94a3b8',
            },
            grid: {
                vertLines: { color: '#1e293b' },
                horzLines: { color: '#1e293b' },
            },
            width: chartContainerRef.current.clientWidth,
            height: 300,
            crosshair: {
                mode: CrosshairMode.Normal,
            },
            timeScale: {
                borderColor: '#334155',
                timeVisible: true,
            },
        });

        const candlestickSeries = chart.addCandlestickSeries({
            upColor: '#10b981',
            downColor: '#f43f5e',
            borderVisible: false,
            wickUpColor: '#10b981',
            wickDownColor: '#f43f5e',
        });

        candlestickSeries.setData(data);

        // Add Lines
        const isLong = direction?.toUpperCase() === "LONG";

        if (entry) {
            candlestickSeries.createPriceLine({
                price: entry,
                color: '#6366f1', // Indigo
                lineWidth: 2,
                lineStyle: 2, // Dashed
                axisLabelVisible: true,
                title: 'ENTRY',
            });
        }

        if (tp) {
            candlestickSeries.createPriceLine({
                price: tp,
                color: '#10b981', // Emerald
                lineWidth: 2,
                lineStyle: 0, // Solid
                axisLabelVisible: true,
                title: 'TP',
            });
        }

        if (sl) {
            candlestickSeries.createPriceLine({
                price: sl,
                color: '#f43f5e', // Rose
                lineWidth: 2,
                lineStyle: 0, // Solid
                axisLabelVisible: true,
                title: 'SL',
            });
        }

        chart.timeScale().fitContent();

        chartRef.current = chart;

        const handleResize = () => {
            chart.applyOptions({ width: chartContainerRef.current?.clientWidth || 400 });
        };

        window.addEventListener('resize', handleResize);

        return () => {
            window.removeEventListener('resize', handleResize);
            chart.remove();
        };
    }, [data, entry, tp, sl, direction]);

    return (
        <div className="w-full relative bg-slate-950/50 rounded-xl border border-slate-800 overflow-hidden shadow-inner">
            <div ref={chartContainerRef} className="w-full h-[300px]" />

            {/* Watermark / Logo Overlay */}
            <div className="absolute top-4 left-4 pointer-events-none opacity-30">
                <span className="text-xs font-bold text-slate-500 uppercase tracking-widest">Trader Copilot Chart</span>
            </div>
        </div>
    );
};
