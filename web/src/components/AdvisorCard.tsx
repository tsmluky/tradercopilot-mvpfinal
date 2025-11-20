import React from 'react';
import { AdvisorResponse } from '../types';
import { AlertCircle, ArrowRight } from 'lucide-react';

export const AdvisorCard: React.FC<{ data: AdvisorResponse }> = ({ data }) => {
  // Normalizamos dirección por si viene en MAYÚSCULAS o mezclado
  const direction = data.direction?.toLowerCase?.() ?? data.direction;
  const alternatives = data.alternatives ?? [];

  const riskColor =
    data.risk_score > 0.7
      ? 'text-rose-400'
      : data.risk_score > 0.4
      ? 'text-amber-400'
      : 'text-emerald-400';

  const directionColor =
    direction === 'long' ? 'text-emerald-400' : 'text-rose-400';

  return (
    <div className="bg-slate-800 rounded-xl border border-slate-700 overflow-hidden shadow-lg">
      {/* Header */}
      <div className="p-5 border-b border-slate-700 bg-slate-800/50">
        <div className="flex justify-between items-center">
          <div>
            <h3 className="text-lg font-bold text-white flex items-center gap-2">
              {data.token} Position Advisor
            </h3>
            <span className={`text-sm uppercase font-bold ${directionColor}`}>
              {direction} @ {data.entry}
            </span>
          </div>
          <div className="text-right">
            <div className="text-xs text-slate-400">Risk Score</div>
            <div className={`text-xl font-bold ${riskColor}`}>
              {data.risk_score.toFixed(2)}
            </div>
          </div>
        </div>
      </div>

      {/* Body */}
      <div className="p-5 grid grid-cols-2 gap-4">
        {/* Recommended Structure */}
        <div className="col-span-2">
          <h4 className="text-xs font-bold text-slate-500 uppercase mb-3">
            Recommended Structure
          </h4>
          <div className="grid grid-cols-3 gap-3">
            <div className="bg-slate-900 p-3 rounded border border-slate-700">
              <div className="text-xs text-slate-400">Size</div>
              <div className="font-mono font-bold">
                ${data.size_quote}
              </div>
            </div>
            <div className="bg-slate-900 p-3 rounded border border-slate-700">
              <div className="text-xs text-emerald-400">TP</div>
              <div className="font-mono font-bold text-emerald-400">
                {data.tp}
              </div>
            </div>
            <div className="bg-slate-900 p-3 rounded border border-slate-700">
              <div className="text-xs text-rose-400">SL</div>
              <div className="font-mono font-bold text-rose-400">
                {data.sl}
              </div>
            </div>
          </div>
        </div>

        {/* Scenario Management */}
        <div className="col-span-2 mt-2">
          <h4 className="text-xs font-bold text-slate-500 uppercase mb-3">
            Scenario Management
          </h4>

          {alternatives.length === 0 ? (
            <div className="text-xs text-slate-500 italic bg-slate-900/40 border border-dashed border-slate-700/60 rounded px-3 py-2">
              No scenario alternatives defined yet for this position.
            </div>
          ) : (
            <div className="space-y-2">
              {alternatives.map((alt, idx) => (
                <div
                  key={`${alt.if ?? 'scenario'}-${idx}`}
                  className="flex items-center gap-3 bg-slate-900/50 p-3 rounded border border-slate-700/50 text-sm"
                >
                  <div className="p-1.5 bg-indigo-500/10 rounded text-indigo-400">
                    <AlertCircle size={16} />
                  </div>
                  <div className="flex-1">
                    <div className="text-slate-300">
                      <span className="text-indigo-300 font-mono text-xs uppercase mr-2">
                        IF
                      </span>
                      {alt.if}
                    </div>
                    <div className="flex items-center gap-2 text-emerald-300 mt-0.5">
                      <ArrowRight size={12} />
                      <span className="font-semibold">
                        {alt.action}
                      </span>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-xs text-slate-500">New RR</div>
                    <div className="font-mono text-slate-200">
                      {alt.rr_target}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
