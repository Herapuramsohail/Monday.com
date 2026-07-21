"use client";

import React, { useState, useEffect } from 'react';
import { Search, Sun, Moon, Bell, ShieldCheck, Database } from 'lucide-react';

interface HeaderProps {
  toggleDarkMode: () => void;
  darkMode: boolean;
  openSearch: () => void;
}

export default function Header({ toggleDarkMode, darkMode, openSearch }: HeaderProps) {
  const [hasConnection, setHasConnection] = useState(false);

  useEffect(() => {
    // Check if settings exist
    const token = localStorage.getItem('mondayApiToken');
    setHasConnection(!!token);
  }, []);

  return (
    <header className="h-16 border-b border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-950 flex items-center justify-between px-6 transition-colors duration-200">
      <div className="flex items-center gap-4">
        {/* Search Bar Trigger */}
        <button 
          onClick={openSearch}
          className="flex items-center gap-3.5 bg-slate-100 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl px-4 py-2 text-slate-400 dark:text-slate-500 hover:border-slate-300 dark:hover:border-slate-700 transition-all w-80 text-left"
        >
          <Search size={16} />
          <span className="text-sm font-medium">Search company, deal, owner...</span>
          <kbd className="ml-auto text-xs bg-slate-200 dark:bg-slate-800 px-1.5 py-0.5 rounded font-mono border border-slate-300 dark:border-slate-700">Ctrl+K</kbd>
        </button>
      </div>

      <div className="flex items-center gap-4">
        {/* Connection status indicator */}
        <div className={`flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-semibold border ${
          hasConnection 
            ? 'bg-emerald-500/10 border-emerald-500/35 text-emerald-600 dark:text-emerald-400' 
            : 'bg-amber-500/10 border-amber-500/35 text-amber-600 dark:text-amber-400'
        }`}>
          {hasConnection ? <ShieldCheck size={14} /> : <Database size={14} />}
          <span>{hasConnection ? 'Monday.com Connected' : 'Using Fallback Datasets'}</span>
        </div>

        {/* Theme Toggle */}
        <button 
          onClick={toggleDarkMode}
          className="p-2.5 rounded-xl border border-slate-200 dark:border-slate-800 text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-900 transition-colors"
        >
          {darkMode ? <Sun size={18} /> : <Moon size={18} />}
        </button>

        {/* Notification bell */}
        <button className="p-2.5 rounded-xl border border-slate-200 dark:border-slate-800 text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-900 transition-colors relative">
          <Bell size={18} />
          <span className="absolute top-2 right-2 w-2 h-2 bg-rose-500 rounded-full"></span>
        </button>

        {/* User profile */}
        <div className="flex items-center gap-2 border-l border-slate-200 dark:border-slate-800 pl-4">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-cyan-400 to-blue-500 text-white flex items-center justify-center font-bold text-sm shadow-md">
            S
          </div>
          <div className="hidden md:block">
            <p className="text-xs font-semibold text-slate-800 dark:text-slate-200 leading-tight">Sohail</p>
            <p className="text-[10px] text-slate-500 font-medium leading-none">Founder & CEO</p>
          </div>
        </div>
      </div>
    </header>
  );
}
