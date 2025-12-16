import React, { useState, useRef, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import { api } from '../services/api';
import { ChatMessage } from '../types';

interface AdvisorChatProps {
  currentToken?: string;
  currentTimeframe?: string;
  initialContext?: any; // New: For passing full signal context
  embedded?: boolean;   // New: Render without floating button
}

import { useAuth } from '../context/AuthContext';
import { Link } from 'react-router-dom';

export const AdvisorChat: React.FC<AdvisorChatProps> = ({ currentToken, currentTimeframe, initialContext, embedded = false }) => {
  const { userProfile } = useAuth();
  const plan = userProfile?.user.subscription_status || 'free';
  const isLocked = plan === 'free';

  // If embedded, default to open. Else default to closed.
  const [isOpen, setIsOpen] = useState(embedded);

  // Initial welcome message from assistant
  const [messages, setMessages] = useState<ChatMessage[]>([]);

  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Initialize Check
  const initializedRef = useRef(false);

  useEffect(() => {
    if (initializedRef.current) return;
    initializedRef.current = true;

    if (initialContext) {
      // Auto-trigger analysis
      handleSend(initialContext, true);
    } else {
      setMessages([{
        id: 'welcome',
        role: 'assistant',
        content: 'How can I assist you with risk assessment today?',
        type: 'text',
        timestamp: new Date().toISOString()
      }]);
    }
  }, [initialContext]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isOpen]);

  // Listen for 'open-advisor-chat' events only if NOT embedded
  useEffect(() => {
    if (embedded) return;
    const handleOpenEvent = (e: CustomEvent) => {
      setIsOpen(true);
    };

    window.addEventListener('open-advisor-chat', handleOpenEvent as EventListener);
    return () => window.removeEventListener('open-advisor-chat', handleOpenEvent as EventListener);
  }, [embedded]);

  const handleSend = async (overrideContext?: any, isInitialAutoSend: boolean = false) => {
    // Allow empty input if it's the initial auto-send (context-based)
    if (!isInitialAutoSend && (!input.trim() || isLoading)) return;

    let userMsg: ChatMessage;

    if (isInitialAutoSend) {
      // Generar prompt automático invisible para el usuario
      userMsg = {
        id: Date.now().toString(),
        role: 'user',
        content: `Analyze the following trade setup immediately and provide a risk assessment: Token ${overrideContext?.token}, Direction ${overrideContext?.direction}, Entry ${overrideContext?.entry}. Be concise.`,
        type: 'text',
        timestamp: new Date().toISOString(),
        // Optional: We could hide this from the UI if we supported a 'hidden' flag, 
        // but for now let's just not add it to 'messages' state if we want it hidden, 
        // OR better, let's add it so the user sees what was asked.
        // User asked for "automatic analysis", showing the prompt "System: Analyzing..." might be better.
        // Let's Just send it to backend but NOT add to UI state? 
        // No, let's make it look like a system trigger.
      };
      // Don't add to UI messages to keep it clean, OR add a "system" note.
      // Simplified: Just send it to API, don't setMessages(userMsg). 
      // The user will just see the "Agent" replying.
    } else {
      userMsg = {
        id: Date.now().toString(),
        role: 'user',
        content: input,
        type: 'text',
        timestamp: new Date().toISOString()
      };
      setMessages(prev => [...prev, userMsg]);
      setInput('');
    }

    setIsLoading(true);

    try {
      const context = overrideContext || {
        token: currentToken,
        timeframe: currentTimeframe
      };

      // Use the dedicated service method
      const responseMsg = await api.sendAdvisorChat(
        isInitialAutoSend ? [userMsg] : [...messages, userMsg],
        context
      );

      setMessages(prev => [...prev, responseMsg]);

    } catch (error) {
      console.error('Advisor chat error:', error);
      setMessages(prev => [...prev, {
        id: Date.now().toString(),
        role: 'assistant',
        content: '❌ Connection error. Please check system logs.',
        type: 'text',
        timestamp: new Date().toISOString()
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  // --- RENDER HELPERS ---

  // 1. Embedded Mode Render
  if (embedded) {
    return (
      <div className="flex flex-col h-full bg-[#0B1121]">
        {/* Messages Area */}
        <div className="flex-1 overflow-y-auto p-4 space-y-3 custom-scrollbar">
          {messages.map((msg, idx) => {
            const isUser = msg.role === 'user';
            return (
              <div
                key={msg.id || idx}
                className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[85%] rounded-lg p-3 text-sm shadow-md ${isUser
                    ? 'bg-blue-600 text-white rounded-tr-none'
                    : 'bg-gray-800 text-gray-200 rounded-tl-none border border-gray-700'
                    }`}
                >
                  {isUser ? (
                    <p className="whitespace-pre-wrap leading-relaxed">{msg.content}</p>
                  ) : (
                    <div className="prose prose-invert prose-sm max-w-none [&>ul]:list-disc [&>ul]:pl-4 [&>ol]:list-decimal [&>ol]:pl-4 [&>h3]:text-indigo-400 [&>h3]:font-bold [&>strong]:text-indigo-300">
                      {/* @ts-ignore */}
                      <ReactMarkdown>{msg.content}</ReactMarkdown>
                    </div>
                  )}
                </div>
              </div>
            );
          })}
          {isLoading && (
            <div className="flex justify-start">
              <div className="bg-gray-800 text-gray-400 rounded-lg p-3 text-sm border border-gray-700 animate-pulse">
                <span className="flex gap-1">
                  <span className="w-1.5 h-1.5 bg-gray-500 rounded-full animate-bounce delay-0"></span>
                  <span className="w-1.5 h-1.5 bg-gray-500 rounded-full animate-bounce delay-100"></span>
                  <span className="w-1.5 h-1.5 bg-gray-500 rounded-full animate-bounce delay-200"></span>
                </span>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
        {/* Input Area */}
        <div className="p-3 bg-gray-800/50 border-t border-gray-700 backdrop-blur-sm">
          <div className="flex gap-2">
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyPress}
              placeholder="Ask follow-up..."
              className="flex-1 bg-[#1E293B] text-white border border-gray-600 rounded-lg p-2 text-sm focus:outline-none focus:border-blue-500 resize-none h-10 py-2.5 scrollbar-none"
              rows={1}
            />
            <button
              onClick={() => handleSend()}
              disabled={isLoading || !input.trim()}
              className={`px-3 rounded-lg bg-blue-600 text-white font-medium hover:bg-blue-500 transition-colors shadow-lg ${(isLoading || !input.trim()) ? 'opacity-50 cursor-not-allowed' : ''
                }`}
            >
              ➤
            </button>
          </div>
        </div>
      </div>
    );
  }

  // 2. Floating Mode Render (Original)
  return (
    <div className="fixed bottom-6 right-6 z-[60] flex flex-col items-end pointer-events-none">
      {/* Chat Window - Enable pointer events for children */}
      {isOpen && (
        <div className="mb-4 w-80 md:w-96 h-[450px] bg-[#0B1121] border border-gray-700 rounded-xl shadow-2xl flex flex-col overflow-hidden animate-in slide-in-from-bottom-10 duration-300 pointer-events-auto">
          {/* Header */}
          <div className="bg-gray-800/80 p-3 border-b border-gray-700 flex justify-between items-center backdrop-blur-sm">
            <div className="flex items-center gap-2">
              <span className="text-xl">🛡️</span>
              <h3 className="font-bold text-gray-100">PRO Analyst AI</h3>
            </div>
            <button
              onClick={() => setIsOpen(false)}
              className="text-gray-400 hover:text-white hover:bg-red-500/20 transition-colors p-1.5 rounded-lg flex items-center justify-center w-8 h-8"
              title="Close Chat"
            >
              ✕
            </button>
          </div>

          {/* Messages Area */}
          <div className="flex-1 overflow-y-auto p-4 space-y-3 custom-scrollbar bg-slate-900/50">
            {messages.map((msg, idx) => {
              const isUser = msg.role === 'user';
              return (
                <div
                  key={msg.id || idx}
                  className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-[85%] rounded-lg p-3 text-sm shadow-md ${isUser
                      ? 'bg-blue-600 text-white rounded-tr-none'
                      : 'bg-gray-800 text-gray-200 rounded-tl-none border border-gray-700'
                      }`}
                  >
                    {isUser ? (
                      <p className="whitespace-pre-wrap leading-relaxed">{msg.content}</p>
                    ) : (
                      <div className="prose prose-invert prose-sm max-w-none [&>ul]:list-disc [&>ul]:pl-4 [&>ol]:list-decimal [&>ol]:pl-4 [&>h3]:text-indigo-400 [&>h3]:font-bold [&>strong]:text-indigo-300">
                        {/* @ts-ignore */}
                        <ReactMarkdown>{msg.content}</ReactMarkdown>
                      </div>
                    )}
                  </div>
                </div>
              );
            })}

            {isLoading && (
              <div className="flex justify-start">
                <div className="bg-gray-800 text-gray-400 rounded-lg p-3 text-sm border border-gray-700 animate-pulse">
                  <span className="flex gap-1">
                    <span className="w-1.5 h-1.5 bg-gray-500 rounded-full animate-bounce delay-0"></span>
                    <span className="w-1.5 h-1.5 bg-gray-500 rounded-full animate-bounce delay-100"></span>
                    <span className="w-1.5 h-1.5 bg-gray-500 rounded-full animate-bounce delay-200"></span>
                  </span>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Input Area */}
          <div className="p-3 bg-gray-800/80 border-t border-gray-700 backdrop-blur-sm">
            {isLocked ? (
              <div className="text-center py-2 h-full flex flex-col justify-center">
                <p className="text-sm text-slate-400 mb-2">Advisor Chat is available on Paid Plans.</p>
                <Link to="/membership" className="inline-block px-4 py-1.5 bg-gradient-to-r from-emerald-500 to-emerald-600 text-white text-xs font-bold rounded-full shadow-lg hover:scale-105 transition-transform">
                  Upgrade to Unlock
                </Link>
              </div>
            ) : (
              <div className="flex gap-2">
                <textarea
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyDown={handleKeyPress}
                  placeholder={currentToken ? `Ask about ${currentToken}...` : "Analyze risk profile..."}
                  className="flex-1 bg-[#1E293B] text-white border border-gray-600 rounded-lg p-2 text-sm focus:outline-none focus:border-blue-500 resize-none h-10 py-2.5 scrollbar-none"
                  rows={1}
                />
                <button
                  onClick={() => handleSend()}
                  disabled={isLoading || !input.trim()}
                  className={`px-3 rounded-lg bg-blue-600 text-white font-medium hover:bg-blue-500 transition-colors shadow-lg ${(isLoading || !input.trim()) ? 'opacity-50 cursor-not-allowed' : ''
                    }`}
                >
                  ➤
                </button>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Toggle Button - Only visible when closed */}
      {!isOpen && (
        <button
          onClick={() => setIsOpen(true)}
          className={`pointer-events-auto group flex items-center gap-2 px-4 py-3 rounded-full shadow-2xl transition-all duration-300 transform hover:scale-105 bg-gradient-to-r from-blue-600 to-indigo-600 text-white hover:shadow-blue-500/25`}
        >
          <span className="text-2xl group-hover:rotate-12 transition-transform">🛡️</span>
          <span className="font-bold">Advisor Chat</span>
        </button>
      )}
    </div>
  );
};
