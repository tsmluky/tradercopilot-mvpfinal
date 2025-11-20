
import React, { useState, useEffect, useRef } from 'react';
import ReactMarkdown from 'react-markdown';
import { Send, Bot, User, Loader2, RefreshCw, XCircle } from 'lucide-react';
import { ChatMessage, AdvisorResponse } from '../types';
import { AdvisorCard } from './AdvisorCard';
import { api } from '../services/api';

interface Props {
  initialContext: {
    token: string;
    direction: string;
    entry: number;
    size_quote: number;
    tp: number; // calculated or 0
    sl: number; // calculated or 0
  };
  onReset: () => void;
}

export const AdvisorChat: React.FC<Props> = ({ initialContext, onReset }) => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping]);

  // Initialize chat with analysis
  useEffect(() => {
    const init = async () => {
      setIsTyping(true);
      try {
        const response = await api.sendAdvisorChat([], initialContext);
        setMessages([response]);
      } catch (e) {
        console.error(e);
      } finally {
        setIsTyping(false);
      }
    };
    init();
  }, []);

  const handleSend = async (e?: React.FormEvent) => {
    e?.preventDefault();
    if (!input.trim()) return;

    const userMsg: ChatMessage = {
      id: Date.now().toString(),
      role: 'user',
      content: input,
      type: 'text',
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setIsTyping(true);

    try {
      // Pass full history + current msg
      const response = await api.sendAdvisorChat([...messages, userMsg], initialContext);
      setMessages(prev => [...prev, response]);
    } catch (err) {
      console.error(err);
    } finally {
      setIsTyping(false);
    }
  };

  return (
    <div className="bg-slate-900 rounded-xl border border-slate-800 shadow-2xl flex flex-col h-[600px]">
      {/* Header */}
      <div className="p-4 border-b border-slate-800 bg-slate-900/80 backdrop-blur flex justify-between items-center">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-indigo-500/20 rounded-full flex items-center justify-center border border-indigo-500/50">
            <Bot className="text-indigo-400" size={20} />
          </div>
          <div>
            <h3 className="font-bold text-white">Risk Advisor AI</h3>
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse"></span>
              <span className="text-xs text-slate-400">Online • Context: {initialContext.token} {initialContext.direction.toUpperCase()}</span>
            </div>
          </div>
        </div>
        <button
          onClick={onReset}
          className="p-2 hover:bg-slate-800 rounded-full text-slate-400 hover:text-white transition-colors"
          title="End Session"
        >
          <XCircle size={20} />
        </button>
      </div>

      {/* Chat Area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-6 bg-slate-950/50">
        {messages.map((msg) => (
          <div key={msg.id} className={`flex gap-3 ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}>
            <div className={`w-8 h-8 rounded-full flex-shrink-0 flex items-center justify-center ${msg.role === 'user' ? 'bg-slate-700' : 'bg-indigo-500/20'}`}>
              {msg.role === 'user' ? <User size={14} /> : <Bot size={14} className="text-indigo-400" />}
            </div>

            <div className={`flex-1 max-w-[85%] space-y-2`}>
              {msg.content && (
                <div className={`p-3 rounded-lg text-sm leading-relaxed ${msg.role === 'user'
                  ? 'bg-slate-700 text-white rounded-tr-none'
                  : 'bg-slate-800 text-slate-200 rounded-tl-none border border-slate-700'
                  }`}>
                  <ReactMarkdown
                    components={{
                      strong: ({ node, ...props }) => <span className="font-bold text-indigo-300" {...props} />,
                      p: ({ node, ...props }) => <p className="mb-1 last:mb-0" {...props} />,
                      ul: ({ node, ...props }) => <ul className="list-disc ml-4 mb-2" {...props} />,
                      li: ({ node, ...props }) => <li className="mb-0.5" {...props} />,
                    }}
                  >
                    {msg.content}
                  </ReactMarkdown>
                </div>
              )}

              {msg.type === 'analysis' && msg.data && (
                <div className="mt-2">
                  <AdvisorCard data={msg.data} />
                </div>
              )}
            </div>
          </div>
        ))}

        {isTyping && (
          <div className="flex gap-3">
            <div className="w-8 h-8 rounded-full bg-indigo-500/20 flex-shrink-0 flex items-center justify-center">
              <Bot size={14} className="text-indigo-400" />
            </div>
            <div className="bg-slate-800 border border-slate-700 px-4 py-3 rounded-lg rounded-tl-none flex gap-1">
              <span className="w-2 h-2 bg-slate-500 rounded-full animate-bounce"></span>
              <span className="w-2 h-2 bg-slate-500 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></span>
              <span className="w-2 h-2 bg-slate-500 rounded-full animate-bounce" style={{ animationDelay: '0.4s' }}></span>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <form onSubmit={handleSend} className="p-4 bg-slate-900 border-t border-slate-800">
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask about risk, scenarios, or adjustments..."
            className="flex-1 bg-slate-950 border border-slate-800 text-white rounded-lg px-4 py-3 focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none"
          />
          <button
            type="submit"
            disabled={!input.trim() || isTyping}
            className="bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed text-white rounded-lg px-4 transition-colors"
          >
            <Send size={20} />
          </button>
        </div>
      </form>
    </div>
  );
};
