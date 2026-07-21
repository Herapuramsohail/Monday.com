"use client";

import React, { useState, useRef, useEffect } from 'react';
import { sendChatMessage } from '@/lib/api';
import { MessageSquare, Send, Sparkles, AlertCircle, Bot, User, CornerDownLeft } from 'lucide-react';

interface ChatMessage {
  sender: 'user' | 'assistant';
  text: string;
  toolCalls?: any[];
}

const quickPrompts = [
  "How is our pipeline this quarter?",
  "Which sectors perform best?",
  "Which work orders are delayed?",
  "Compare Powerline and Mining sectors"
];

export default function AIAssistantPage() {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      sender: 'assistant',
      text: "Hello! I am your AI Business Intelligence Agent. I have full read access to your Deal Funnel and Work Order Tracker Monday boards. Ask me any strategic financial or delivery pipeline questions!"
    }
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const chatEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  const handleSend = async (textToSend: string) => {
    if (!textToSend.trim() || loading) return;
    
    const userMsg: ChatMessage = { sender: 'user', text: textToSend };
    setMessages(prev => [...prev, userMsg]);
    setInput("");
    setLoading(true);

    try {
      const res = await sendChatMessage(textToSend, {});
      const assistantMsg: ChatMessage = {
        sender: 'assistant',
        text: res.reply,
        toolCalls: res.toolCalls
      };
      setMessages(prev => [...prev, assistantMsg]);
    } catch (err) {
      setMessages(prev => [...prev, {
        sender: 'assistant',
        text: "⚠️ I encountered an error communicating with the BI analytics engine. Please ensure the backend server is running."
      }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-[82vh] bg-white dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-2xl overflow-hidden shadow-sm">
      {/* Top Info Bar */}
      <div className="p-4 border-b border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-900/40 flex items-center gap-3">
        <div className="p-2 bg-gradient-to-tr from-cyan-400 to-blue-500 rounded-xl text-white">
          <MessageSquare size={18} />
        </div>
        <div>
          <h3 className="text-xs font-bold text-slate-800 dark:text-slate-200">AI BI Strategy Assistant</h3>
          <p className="text-[10px] text-slate-500 font-semibold">Gemini 2.5 Pro Tool Calling Agent</p>
        </div>
        <div className="ml-auto flex items-center gap-1 text-[10px] font-bold text-emerald-500 bg-emerald-500/10 px-2.5 py-0.5 rounded-full border border-emerald-500/20">
          <Sparkles size={11} />
          <span>Analytical Sandbox Active</span>
        </div>
      </div>

      {/* Messages Stream */}
      <div className="flex-1 overflow-y-auto p-6 space-y-6">
        {messages.map((msg, idx) => (
          <div key={idx} className={`flex gap-4 ${msg.sender === 'user' ? 'justify-end' : ''}`}>
            {msg.sender === 'assistant' && (
              <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-cyan-400 to-blue-500 text-white flex items-center justify-center font-bold shadow-md shrink-0">
                <Bot size={16} />
              </div>
            )}
            
            <div className={`max-w-[75%] rounded-2xl px-4 py-3 text-xs leading-relaxed ${
              msg.sender === 'user'
                ? 'bg-slate-900 text-slate-100 dark:bg-slate-100 dark:text-slate-900 font-semibold shadow-sm'
                : 'bg-slate-50 dark:bg-slate-900/60 border border-slate-200 dark:border-slate-800 text-slate-700 dark:text-slate-300'
            }`}>
              {/* Tool Execution logs */}
              {msg.toolCalls && msg.toolCalls.map((tc, tIdx) => (
                <div key={tIdx} className="mb-2.5 bg-slate-200/50 dark:bg-slate-950/60 border border-slate-300 dark:border-slate-800 p-2 rounded-xl text-[10px] font-mono text-cyan-600 dark:text-cyan-400 flex items-center gap-2">
                  <span className="w-2 h-2 rounded-full bg-cyan-500 animate-pulse"></span>
                  <span>Executed tool: `{tc.tool}`</span>
                </div>
              ))}
              
              <div className="whitespace-pre-wrap">{msg.text}</div>
            </div>

            {msg.sender === 'user' && (
              <div className="w-8 h-8 rounded-lg bg-slate-200 dark:bg-slate-850 flex items-center justify-center text-slate-600 dark:text-slate-400 font-bold shrink-0">
                <User size={16} />
              </div>
            )}
          </div>
        ))}

        {loading && (
          <div className="flex gap-4">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-cyan-400 to-blue-500 text-white flex items-center justify-center font-bold shadow-md shrink-0">
              <Bot size={16} />
            </div>
            <div className="bg-slate-50 dark:bg-slate-900/60 border border-slate-200 dark:border-slate-800 rounded-2xl px-4 py-3 flex items-center gap-1.5">
              <span className="w-1.5 h-1.5 bg-slate-400 rounded-full animate-bounce"></span>
              <span className="w-1.5 h-1.5 bg-slate-400 rounded-full animate-bounce [animation-delay:0.2s]"></span>
              <span className="w-1.5 h-1.5 bg-slate-400 rounded-full animate-bounce [animation-delay:0.4s]"></span>
            </div>
          </div>
        )}
        <div ref={chatEndRef} />
      </div>

      {/* Quick Prompts Chips */}
      {messages.length === 1 && (
        <div className="px-6 py-2 border-t border-slate-100 dark:border-slate-800 flex flex-wrap gap-2">
          {quickPrompts.map((qp, idx) => (
            <button
              key={idx}
              onClick={() => handleSend(qp)}
              className="text-[10px] font-bold text-slate-500 hover:text-cyan-500 border border-slate-200 dark:border-slate-800 hover:border-cyan-500/30 px-3 py-1.5 rounded-full transition"
            >
              {qp}
            </button>
          ))}
        </div>
      )}

      {/* Input Tray */}
      <div className="p-4 border-t border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-900/20">
        <form 
          onSubmit={(e) => {
            e.preventDefault();
            handleSend(input);
          }}
          className="flex items-center gap-3 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-2.5 shadow-inner"
        >
          <input
            type="text"
            placeholder="Ask AI Assistant about pipeline, revenue, forecast, delayed work orders..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            disabled={loading}
            className="flex-1 bg-transparent border-0 outline-none text-xs text-slate-800 dark:text-slate-100 placeholder-slate-400 px-2"
          />
          <button 
            type="submit" 
            disabled={loading || !input.trim()}
            className="bg-slate-900 dark:bg-slate-100 hover:bg-slate-800 dark:hover:bg-slate-200 text-white dark:text-slate-950 p-2 rounded-lg transition disabled:opacity-50 flex items-center gap-1.5 text-xs font-semibold"
          >
            <Send size={14} />
            <span className="hidden sm:inline">Send</span>
          </button>
        </form>
      </div>
    </div>
  );
}
