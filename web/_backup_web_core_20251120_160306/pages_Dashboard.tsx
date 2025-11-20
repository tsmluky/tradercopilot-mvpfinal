import React, { useEffect, useState } from 'react';
import {
  Activity,
  TrendingUp,
  BarChart2,
  FileText,
  ArrowRight,
  Terminal,
  Zap,
} from 'lucide-react';
import { api } from '../services/api';
import { LogRow, AnalysisMode } from '../types';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export const Dashboard: React.FC = () => {
  const { userProfile, completeOnboarding } = useAuth();
  const [logs, setLogs] = useState<LogRow[]>([]);
  const [loading, setLoading] = useState(true);

  const [winRate, setWinRate] = useState(0);
  const [activeSignals, setActiveSignals] = useState(0);
  const [evaluatedCount, setEvaluatedCount] = useState(0);
  const [estPnL, setEstPnL] = useState(0);

  const [chartData, setChartData] = useState<any[]>([]);

  const showWelcome = userProfile?.user.onboarding_completed === false;

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [ethLogs, btcLogs, solLogs] = await Promise.all([
          api.fetchLogs(AnalysisMode.EVALUATED, 'eth'),
          api.fetchLogs(AnalysisMode.EVALUATED, 'btc'),
          api.fetchLogs(AnalysisMode.EVALUATED, 'sol'),
        ]);

        const allLogs = [...ethLogs, ...btcLogs, ...solLogs];
        allLogs.sort((a, b) => {
          const ta = new Date((a.evaluated_at as string) || (a.timestamp as string) || 0).getTime();
          const tb = new Date((b.evaluated_at as string) || (b.timestamp as string) || 0).getTime();
          return tb - ta;
        });

        setLogs(allLogs);

        const now = new Date();
        const oneDayAgo = new Date(now.getTime() - 24 * 60 * 60 * 1000);
        const sevenDaysAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);

        const last24hLogs = allLogs.filter(
          (l) => new Date((l.evaluated_at as string) || 0) > oneDayAgo
        );

        const wins24h = last24hLogs.filter(
          (l) => String(l.result || '').toUpperCase().includes('WIN') || String(l.result || '').toUpperCase().includes('TP')
        ).length;
        const losses24h = last24hLogs.filter(
          (l) => String(l.result || '').toUpperCase().includes('LOSS') || String(l.result || '').toUpperCase().includes('SL')
        ).length;
        const totalClosed24h = wins24h + losses24h;

        setWinRate(totalClosed24h > 0 ? Math.round((wins24h / totalClosed24h) * 100) : 0);

        setActiveSignals(
          allLogs.filter(
            (l) =>
              String(l.result || '').toUpperCase() === 'OPEN' ||
              String(l.result || '').toUpperCase() === 'PENDING'
          ).length
        );

        const last7dLogs = allLogs.filter(
          (l) => new Date((l.evaluated_at as string) || 0) > sevenDaysAgo
        );
        setEvaluatedCount(last7dLogs.length);

        let pnl = 0;
        last7dLogs.forEach((l) => {
          const res = String(l.result || '').toUpperCase();
          if (res.includes('WIN') || res.includes('TP')) pnl += 1.5;
          else if (res.includes('LOSS') || res.includes('SL')) pnl -= 1.0;
        });
        setEstPnL(parseFloat(pnl.toFixed(1)));

        const dailyStats: Record<
          string,
          { date: string; wins: number; losses: number }
        > = {};

        for (let i = 6; i >= 0; i--) {
          const d = new Date(now.getTime() - i * 24 * 60 * 60 * 1000);
          const key = d.toLocaleDateString('en-GB', {
            day: '2-digit',
            month: '2-digit',
          });
          dailyStats[key] = { date: key, wins: 0, losses: 0 };
        }

        last7dLogs.forEach((l) => {
          const d = new Date((l.evaluated_at as string) || 0);
          const key = d.toLocaleDateString('en-GB', {
            day: '2-digit',
            month: '2-digit',
          });
          if (!dailyStats[key]) return;
          const res = String(l.result || '').toUpperCase();
          if (res.includes('WIN') || res.includes('TP')) dailyStats[key].wins++;
          else if (res.includes('LOSS') || res.includes('SL'))
            dailyStats[key].losses++;
        });

        setChartData(Object.values(dailyStats));
      } catch (e) {
        console.error('Dashboard data load failed', e);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const KPICard = ({ title, value, sub, icon, color }: any) => (
    <div className="bg-slate-900 p-5 md:p-6 rounded-xl border border-slate-800 shadow-lg relative overflow-hidden">
      <div className={`absolute top-0 right-0 p-4 opacity-10 ${color}`}>{icon}</div>
      <h3 className="text-slate-400 text-xs font-bold uppercase tracking-wider mb-2">
        {title}
      </h3>
      {loading ? (
        <div className="h-8 w-24 bg-slate-800 rounded animate-pulse"></div>
      ) : (
        <div className="text-3xl font-mono font-bold text-white">{value}</div>
      )}
      <div className="text-xs text-slate-500 mt-1">{sub}</div>
    </div>
  );

  return (
    <div className="p-4 md:p-8 max-w-7xl mx-auto pb-20 md:pb-8">
      {showWelcome && (
        <div className="mb-8 bg-gradient-to-r from-indigo-900/40 to-slate-900 rounded-2xl border border-indigo-500/30 p-6 md:p-8 shadow-xl relative overflow-hidden">
          <div className="relative z-10">
            <div className="flex items-center gap-3 mb-3">
              <div className="bg-indigo-500 text-white p-2 rounded-lg">
                <Zap size={20} fill="currentColor" />
              </div>
              <h2 className="text-xl md:text-2xl font-bold text-white">
                Welcome, Commander.
              </h2>
            </div>
            <p className="text-slate-300 max-w-xl mb-6">
              Your terminal is ready. The AI is online and scanning the markets.
              Initialize your first scan to start building your portfolio.
            </p>
            <div className="flex flex-wrap gap-3">
              <Link
                to="/analysis"
                onClick={completeOnboarding}
                className="bg-indigo-500 hover:bg-indigo-600 text-white font-bold px-6 py-3 rounded-lg transition-all flex items-center gap-2 shadow-lg shadow-indigo-500/20 active:scale-95"
              >
                <Terminal size={18} /> Initialize Terminal
              </Link>
              <Link
                to="/settings"
                onClick={completeOnboarding}
                className="bg-slate-800 hover:bg-slate-700 text-slate-300 font-bold px-6 py-3 rounded-lg transition-all flex items-center gap-2 active:scale-95"
              >
                Configure Alerts
              </Link>
            </div>
          </div>
          <div className="absolute right-0 top-0 bottom-0 w-1/2 bg-gradient-to-l from-indigo-500/10 to-transparent pointer-events-none" />
        </div>
      )}

      <h1 className="text-2xl font-bold text-white mb-6 md:mb-8 flex items-center gap-2">
        <Activity className="text-emerald-400" /> Performance Dashboard
      </h1>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 md:gap-6 mb-6 md:mb-8">
        <KPICard
          title="Win Rate"
          value={`${winRate}%`}
          sub="Last 24h"
          icon={<TrendingUp size={40} />}
          color="text-emerald-400"
        />
        <KPICard
          title="Active"
          value={activeSignals}
          sub="Open Signals"
          icon={<Activity size={40} />}
          color="text-blue-400"
        />
        <KPICard
          title="Evaluated"
          value={evaluatedCount}
          sub="Last 7 Days"
          icon={<FileText size={40} />}
          color="text-slate-400"
        />
        <KPICard
          title="PnL (7d)"
          value={`${estPnL > 0 ? '+' : ''}${estPnL}R`}
          sub="Est. Return"
          icon={<BarChart2 size={40} />}
          color={estPnL >= 0 ? 'text-emerald-400' : 'text-rose-400'}
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 md:gap-8">
        <div className="lg:col-span-2 bg-slate-900 p-5 rounded-xl border border-slate-800 shadow-lg">
          <h3 className="text-lg font-bold text-white mb-6">
            Signal Performance (Last 7 Days)
          </h3>
          <div className="h-56 md:h-64 w-full">
            {loading ? (
              <div className="w-full h-full flex items-center justify-center bg-slate-800/30 rounded-lg animate-pulse">
                <span className="text-slate-600 font-mono">Loading chart data...</span>
              </div>
            ) : chartData.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={chartData}>
                  <XAxis
                    dataKey="date"
                    stroke="#64748b"
                    fontSize={12}
                    tickLine={false}
                    axisLine={false}
                  />
                  <YAxis
                    stroke="#64748b"
                    fontSize={12}
                    tickLine={false}
                    axisLine={false}
                    allowDecimals={false}
                  />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: '#0f172a',
                      borderColor: '#334155',
                      color: '#f8fafc',
                    }}
                    cursor={{ fill: '#1e293b', opacity: 0.3 }}
                  />
                  <Bar dataKey="wins" name="Wins" stackId="a" radius={[4, 4, 0, 0]} />
                  <Bar
                    dataKey="losses"
                    name="Losses"
                    stackId="a"
                    radius={[0, 0, 4, 4]}
                  />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="w-full h-full flex items-center justify-center text-slate-500 border border-dashed border-slate-800 rounded-lg">
                No data for this period
              </div>
            )}
          </div>
        </div>

        <div className="bg-slate-900 p-5 rounded-xl border border-slate-800 shadow-lg flex flex-col">
          <div className="flex justify-between items-center mb-6">
            <h3 className="text-lg font-bold text-white">Live Feed</h3>
            <Link
              to="/logs"
              className="text-xs text-emerald-400 hover:text-emerald-300 font-bold uppercase active:scale-95 transition-transform"
            >
              View All
            </Link>
          </div>

          <div className="flex-1 overflow-y-auto pr-2 space-y-4 max-h-[300px]">
            {loading ? (
              <div className="space-y-3">
                {[1, 2, 3].map((i) => (
                  <div key={i} className="h-16 bg-slate-800 rounded animate-pulse" />
                ))}
              </div>
            ) : logs.length > 0 ? (
              logs.slice(0, 10).map((log, idx) => {
                const token = (log.token || 'ETH').toString().toUpperCase();
                const ts =
                  (log.evaluated_at as string) ||
                  (log.timestamp as string) ||
                  new Date().toISOString();
                const time = new Date(ts).toLocaleTimeString([], {
                  hour: '2-digit',
                  minute: '2-digit',
                });

                const result = String(log.result || '').toUpperCase();
                const badgeClass =
                  result.includes('WIN') || result.includes('TP')
                    ? 'bg-emerald-500/10 text-emerald-400'
                    : result.includes('LOSS') || result.includes('SL')
                    ? 'bg-rose-500/10 text-rose-400'
                    : 'bg-blue-500/10 text-blue-400';

                const move = log.move_pct || log.timeframe;

                return (
                  <div
                    key={idx}
                    className="border-b border-slate-800 pb-3 last:border-0 last:pb-0"
                  >
                    <div className="flex justify-between items-center mb-1">
                      <span className="font-bold text-white text-sm">{token}</span>
                      <span className="text-[10px] text-slate-500 font-mono">{time}</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span
                        className={`text-xs font-bold px-1.5 py-0.5 rounded ${badgeClass}`}
                      >
                        {result || 'SIGNAL'}
                      </span>
                      <span className="text-xs font-mono text-slate-400">{move}</span>
                    </div>
                  </div>
                );
              })
            ) : (
              <div className="text-center text-slate-500 py-8 text-sm">
                No recent activity
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
