"use client";

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { 
  LayoutDashboard, 
  Briefcase, 
  FileSpreadsheet, 
  MessageSquare, 
  TrendingUp, 
  FileText, 
  ShieldAlert, 
  Settings, 
  BarChart3
} from 'lucide-react';

const navItems = [
  { name: 'Dashboard', path: '/', icon: LayoutDashboard },
  { name: 'Deals Funnel', path: '/deals', icon: Briefcase },
  { name: 'Work Orders', path: '/work-orders', icon: FileSpreadsheet },
  { name: 'AI Assistant', path: '/ai-assistant', icon: MessageSquare },
  { name: 'Executive Summary', path: '/executive-summary', icon: FileText },
  { name: 'Data Quality', path: '/data-quality', icon: ShieldAlert },
  { name: 'Settings', path: '/settings', icon: Settings },
];

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-64 bg-slate-900 text-slate-300 flex flex-col border-r border-slate-800 h-screen transition-all duration-300">
      <div className="p-6 border-b border-slate-800 flex items-center gap-3">
        <div className="bg-gradient-to-tr from-cyan-400 to-blue-600 p-2 rounded-xl text-white shadow-lg shadow-cyan-500/20">
          <BarChart3 size={22} />
        </div>
        <div>
          <h1 className="font-bold text-white tracking-wide text-lg">Monday.com BI</h1>
          <p className="text-xs text-slate-500 font-medium">AI Intelligence Agent</p>
        </div>
      </div>

      <nav className="flex-1 px-4 py-6 space-y-1.5 overflow-y-auto">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = pathname === item.path;

          return (
            <Link
              key={item.name}
              href={item.path}
              className={`flex items-center gap-3.5 px-4 py-3 rounded-xl text-sm font-semibold transition-all duration-200 ${
                isActive
                  ? 'bg-gradient-to-r from-cyan-500/25 to-blue-500/10 text-cyan-400 border-l-4 border-cyan-400 pl-3'
                  : 'hover:bg-slate-800/60 hover:text-white text-slate-400'
              }`}
            >
              <Icon size={18} className={isActive ? 'text-cyan-400' : 'text-slate-400'} />
              <span>{item.name}</span>
            </Link>
          );
        })}
      </nav>

      <div className="p-4 border-t border-slate-800 bg-slate-950/40 text-center">
        <p className="text-xs text-slate-600">v1.0.0 Stable Build</p>
      </div>
    </aside>
  );
}
