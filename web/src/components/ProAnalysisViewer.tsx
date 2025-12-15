import React, { useMemo, useState } from 'react';
import ReactMarkdown from 'react-markdown';
import { ProResponse } from '../types';
import { api } from '../services/api';
import {
  BookOpen,
  Search,
  Target,
  Lightbulb,
  Sliders,
  Copy,
  Send,
  Check,
  Heart,
  Link as LinkIcon,
  Activity,
} from 'lucide-react';

interface Props {
  response: ProResponse;
  token: string;
}

export const ProAnalysisViewer: React.FC<Props> = ({ response, token }) => {
  const [copied, setCopied] = useState(false);
  const [sendingTg, setSendingTg] = useState(false);
  const [sentTg, setSentTg] = useState(false);

  const sections = useMemo(() => {
    const raw = response.raw ?? '';
    const extract = (tag: string) => {
      const regex = new RegExp(`#${tag}#([\\s\\S]*?)(?=#|$)`, 'i');
      const match = raw.match(regex);
      return match ? match[1].trim() : null;
    };

    return {
      ctxt: extract('CTXT'),
      ta: extract('TA'),
      sentiment: extract('SENTIMENT'),
      onchain: extract('ONCHAIN'),
      plan: extract('PLAN'),
      insight: extract('INSIGHT'),
      params: extract('PARAMS'),
    };
  }, [response]);

  const handleCopy = () => {
    if (navigator?.clipboard?.writeText) {
      navigator.clipboard.writeText(response.raw ?? '').then(
        () => {
          setCopied(true);
          setTimeout(() => setCopied(false), 2000);
        },
        (err) => console.error('Clipboard error:', err)
      );
    }
  };

  const handleSendTg = async () => {
    setSendingTg(true);
    try {
      const summary =
        `🚀 **TRADER COPILOT PRO: ${token.toUpperCase()}**\\n\\n` +
        `🎯 **PLAN:**\\n${sections.plan || 'See full analysis.'}\\n\\n` +
        `🛠 **PARAMS:**\\n${sections.params || 'N/A'}\\n\\n` +
        `💡 **INSIGHT:**\\n${sections.insight || ''}`;
      await api.notifyTelegram(summary);
      setSentTg(true);
      setTimeout(() => setSentTg(false), 3000);
    } catch (e) {
      console.error(e);
    } finally {
      setSendingTg(false);
    }
  };

  if (!sections.ctxt && !sections.ta) {
    return (
      <div className="p-6 bg-slate-800 rounded-lg border border-slate-700 text-slate-400 font-mono whitespace-pre-wrap">
        {response.raw}
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-sky-900/20 to-slate-900 border border-sky-500/30 rounded-xl p-4 flex justify-between items-center">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-sky-500/20 rounded-lg flex items-center justify-center border border-sky-500/30">
            <BookOpen size={20} className="text-sky-400" />
          </div>
          <div>
            <h2 className="font-bold text-white text-lg">PRO Analysis</h2>
            <p className="text-xs text-slate-400">AI-Powered Deep Market Insights</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <button onClick={handleCopy} className="p-2 hover:bg-slate-800 rounded-lg text-slate-400 hover:text-white transition-colors" title="Copy">
            {copied ? <Check size={16} className="text-emerald-400" /> : <Copy size={16} />}
          </button>
          <button onClick={handleSendTg} disabled={sendingTg} className={`p-2 hover:bg-slate-800 rounded-lg transition-colors ${sentTg ? 'text-emerald-400' : 'text-slate-400 hover:text-white'}`} title="Send to Telegram">
            {sentTg ? <Check size={16} /> : sendingTg ? <span className="w-4 h-4 border-2 border-slate-500 border-t-white rounded-full animate-spin block" /> : <Send size={16} />}
          </button>
        </div>
      </div>

      {/* Main Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
        {/* Context */}
        {sections.ctxt && (
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
            <div className="flex items-center gap-2 mb-4">
              <Search size={16} className="text-emerald-400" />
              <h3 className="font-bold text-sm uppercase tracking-wider text-slate-300">Market Context</h3>
            </div>
            <div className="prose prose-invert prose-sm max-w-none text-slate-400 space-y-2">
              <ReactMarkdown>{sections.ctxt}</ReactMarkdown>
            </div>
          </div>
        )}

        {/* TA */}
        {sections.ta && (
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
            <div className="flex items-center gap-2 mb-4">
              <Activity size={16} className="text-sky-400" />
              <h3 className="font-bold text-sm uppercase tracking-wider text-slate-300">Technical Analysis</h3>
            </div>
            <div className="prose prose-invert prose-sm max-w-none text-slate-400 space-y-3">
              <ReactMarkdown>{sections.ta}</ReactMarkdown>
            </div>
          </div>
        )}

        {/* Sentiment */}
        {sections.sentiment && (
          <div className="bg-gradient-to-br from-purple-900/10 to-slate-900 border border-purple-500/20 rounded-xl p-6">
            <div className="flex items-center gap-2 mb-4">
              <Heart size={16} className="text-purple-400" />
              <h3 className="font-bold text-sm uppercase tracking-wider text-purple-300">Sentiment</h3>
            </div>
            <div className="prose prose-invert prose-sm max-w-none text-slate-300">
              <ReactMarkdown>{sections.sentiment}</ReactMarkdown>
            </div>
          </div>
        )}

        {/* OnChain */}
        {sections.onchain && (
          <div className="bg-gradient-to-br from-amber-900/10 to-slate-900 border border-amber-500/20 rounded-xl p-6">
            <div className="flex items-center gap-2 mb-4">
              <LinkIcon size={16} className="text-amber-400" />
              <h3 className="font-bold text-sm uppercase tracking-wider text-amber-300">On-Chain Data</h3>
            </div>
            <div className="prose prose-invert prose-sm max-w-none text-slate-300">
              <ReactMarkdown>{sections.onchain}</ReactMarkdown>
            </div>
          </div>
        )}
      </div>

      {/* Trading Plan - Full Width */}
      {sections.plan && (
        <div className="bg-gradient-to-r from-emerald-900/20 via-slate-900 to-emerald-900/20 border border-emerald-500/30 rounded-xl p-6">
          <div className="flex items-center gap-2 mb-4">
            <Target size={18} className="text-emerald-400" />
            <h3 className="font-bold text-base uppercase tracking-wider text-emerald-300">Trading Plan</h3>
          </div>
          <div className="prose prose-invert prose-sm max-w-none text-slate-200 space-y-3">
            <ReactMarkdown>{sections.plan}</ReactMarkdown>
          </div>
        </div>
      )}

      {/* Insight */}
      {sections.insight && (
        <div className="bg-slate-900 border-l-4 border-amber-500 rounded-lg p-6">
          <div className="flex items-center gap-2 mb-4">
            <Lightbulb size={16} className="text-amber-400" />
            <h3 className="font-bold text-sm uppercase tracking-wider text-amber-300">Key Insights</h3>
          </div>
          <div className="prose prose-invert prose-sm max-w-none text-amber-100 space-y-3">
            <ReactMarkdown>{sections.insight}</ReactMarkdown>
          </div>
        </div>
      )}

      {/* Parameters */}
      {sections.params && (
        <div className="bg-slate-950/50 rounded-xl border border-slate-800 overflow-hidden">
          <div className="bg-slate-900/50 px-5 py-3 border-b border-slate-800 flex items-center gap-2">
            <Sliders size={14} className="text-emerald-500" />
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400">Signal Parameters</h3>
          </div>
          <div className="p-5 grid grid-cols-2 md:grid-cols-3 gap-3 font-mono text-xs">
            {sections.params.split('\n').filter(l => l.trim()).map((line, i) => {
              const [key, ...valParts] = line.split(':');
              const val = valParts.join(':').trim();
              if (!key || !val) return null;
              const cleanKey = key.replace(/^-/, '').trim().replace(/_/g, ' ');
              return (
                <div key={i} className="bg-slate-900/50 rounded-lg p-3 border border-slate-800/50">
                  <div className="text-slate-500 text-[10px] uppercase mb-1">{cleanKey}</div>
                  <div className={`font-bold text-sm ${cleanKey.includes('direction') || cleanKey.includes('bias') ?
                    (val.toLowerCase().includes('long') || val.toLowerCase().includes('bull') ? 'text-emerald-400' : 'text-rose-400') :
                    cleanKey.includes('price') || cleanKey.includes('support') || cleanKey.includes('resistance') ? 'text-white' :
                      'text-emerald-300'
                    }`}>{val}</div>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
};
