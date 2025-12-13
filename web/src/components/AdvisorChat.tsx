import React, { useState, useRef, useEffect } from 'react';
import { api } from '../services/api';
import { ChatMessage } from '../types';

interface AdvisorChatProps {
  currentToken?: string;
  currentTimeframe?: string;
}

export const AdvisorChat: React.FC<AdvisorChatProps> = ({ currentToken, currentTimeframe }) => {
  const [isOpen, setIsOpen] = useState(false);

  // Initial welcome message from assistant
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: 'welcome',
      role: 'assistant',
      content: '¿En qué puedo ayudarte a evaluar riesgos hoy?',
      type: 'text',
      timestamp: new Date().toISOString()
    }
  ]);

  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isOpen]);

  // Listen for 'open-advisor-chat' events from other components
  useEffect(() => {
    const handleOpenEvent = (e: CustomEvent) => {
      setIsOpen(true);
    };

    window.addEventListener('open-advisor-chat', handleOpenEvent as EventListener);
    return () => window.removeEventListener('open-advisor-chat', handleOpenEvent as EventListener);
  }, []);

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    const userMsg: ChatMessage = {
      id: Date.now().toString(),
      role: 'user',
      content: input,
      type: 'text',
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setIsLoading(true);

    try {
      const context = {
        token: currentToken,
        timeframe: currentTimeframe
      };

      // Use the dedicated service method
      // api.sendAdvisorChat handles the /chat endpoint logic
      const responseMsg = await api.sendAdvisorChat(
        [...messages, userMsg],
        context
      );

      setMessages(prev => [...prev, responseMsg]);

    } catch (error) {
      console.error('Advisor chat error:', error);
      setMessages(prev => [...prev, {
        id: Date.now().toString(),
        role: 'assistant',
        content: '❌ Error al conectar con el Asesor. Revisa los logs.',
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

  return (
    <div className="fixed bottom-6 right-6 z-[60] flex flex-col items-end">
      {/* Chat Window */}
      {isOpen && (
        <div className="mb-4 w-80 md:w-96 h-96 bg-[#0B1121] border border-gray-700 rounded-xl shadow-2xl flex flex-col overflow-hidden animate-in slide-in-from-bottom-10 duration-300">
          {/* Header */}
          <div className="bg-gray-800/50 p-3 border-b border-gray-700 flex justify-between items-center backdrop-blur-sm">
            <div className="flex items-center gap-2">
              <span className="text-xl">🛡️</span>
              <h3 className="font-bold text-gray-100">Risk Advisor AI</h3>
            </div>
            <button
              onClick={() => setIsOpen(false)}
              className="text-gray-400 hover:text-white transition-colors p-1 rounded hover:bg-white/10"
            >
              ✕
            </button>
          </div>

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
                    <p className="whitespace-pre-wrap leading-relaxed">{msg.content}</p>
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
                placeholder={currentToken ? `Pregunta sobre ${currentToken}...` : "Analizar riesgo..."}
                className="flex-1 bg-[#1E293B] text-white border border-gray-600 rounded-lg p-2 text-sm focus:outline-none focus:border-blue-500 resize-none h-10 py-2.5 scrollbar-none"
                rows={1}
              />
              <button
                onClick={handleSend}
                disabled={isLoading || !input.trim()}
                className={`px-3 rounded-lg bg-blue-600 text-white font-medium hover:bg-blue-500 transition-colors shadow-lg ${(isLoading || !input.trim()) ? 'opacity-50 cursor-not-allowed' : ''
                  }`}
              >
                ➤
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Toggle Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className={`group flex items-center gap-2 px-4 py-3 rounded-full shadow-2xl transition-all duration-300 transform hover:scale-105 ${isOpen
            ? 'bg-gray-700 text-gray-300 hover:bg-gray-600'
            : 'bg-gradient-to-r from-blue-600 to-indigo-600 text-white hover:shadow-blue-500/25'
          }`}
      >
        <span className="text-2xl group-hover:rotate-12 transition-transform">🛡️</span>
        {!isOpen && <span className="font-bold">Advisor Chat</span>}
      </button>
    </div>
  );
};
