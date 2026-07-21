"use client";

import React, { useState, useEffect } from 'react';
import { fetchExecutiveSummary } from '@/lib/api';
import { ExecutiveSummaryResponse } from '@/lib/types';
import { FileText, Download, Share2, Printer, ShieldAlert, CheckCircle2, ChevronRight, Award } from 'lucide-react';

export default function ExecutiveSummaryPage() {
  const [summary, setSummary] = useState<ExecutiveSummaryResponse | null>(null);
  const [loading, setLoading] = useState(true);

  const loadSummary = async () => {
    setLoading(true);
    try {
      const res = await fetchExecutiveSummary();
      setSummary(res);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadSummary();
  }, []);

  const handlePrint = () => {
    window.print();
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-[80vh]">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-cyan-400 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-slate-500 font-semibold text-sm">Synthesizing leadership summary report...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6 max-w-4xl mx-auto print:bg-white print:p-8">
      {/* Control bar */}
      <div className="flex items-center justify-between print:hidden">
        <div>
          <h2 className="text-2xl font-bold tracking-tight text-slate-800 dark:text-white">Executive BI Summary</h2>
          <p className="text-xs text-slate-500 font-semibold">Leadership summary compiled across operational indicators</p>
        </div>
        <div className="flex items-center gap-3">
          <button 
            onClick={handlePrint}
            className="flex items-center gap-2 bg-slate-900 hover:bg-slate-800 text-white dark:bg-white dark:text-slate-950 dark:hover:bg-slate-100 px-4 py-2.5 rounded-xl text-xs font-bold transition shadow-sm"
          >
            <Printer size={14} />
            <span>Export to PDF / Print</span>
          </button>
        </div>
      </div>

      {summary && (
        <div className="bg-white dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-3xl p-8 shadow-sm print:border-none print:shadow-none space-y-8">
          {/* Header section */}
          <div className="border-b border-slate-200 dark:border-slate-850 pb-6 flex items-center justify-between">
            <div>
              <span className="bg-gradient-to-r from-cyan-500 to-blue-500 text-white text-[9px] font-bold uppercase tracking-wider px-2.5 py-1 rounded-full mb-2 inline-block">Confidential</span>
              <h1 className="text-3xl font-extrabold text-slate-900 dark:text-white tracking-tight">{summary.title}</h1>
              <p className="text-xs text-slate-500 font-medium mt-1">Generated: {summary.generatedAt} IST</p>
            </div>
            <div className="text-right hidden sm:block">
              <h4 className="font-bold text-sm text-slate-800 dark:text-slate-200">Monday.com BI Platform</h4>
              <p className="text-[10px] text-slate-500">Corporate Strategy Division</p>
            </div>
          </div>

          {/* Quick Metrics Grid */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-6 bg-slate-50 dark:bg-slate-900/40 p-6 rounded-2xl border border-slate-200 dark:border-slate-800">
            <div className="space-y-1">
              <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wide">Total Sales Pipeline</span>
              <p className="text-xl font-black text-cyan-600 dark:text-cyan-400">{summary.totalPipelineFormatted}</p>
            </div>
            <div className="space-y-1 border-l-0 sm:border-l border-slate-200 dark:border-slate-850 sm:pl-6">
              <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wide">Active Opportunities</span>
              <p className="text-xl font-black text-indigo-600 dark:text-indigo-400">{summary.activeDealsCount} Deals</p>
            </div>
            <div className="space-y-1 border-l-0 sm:border-l border-slate-200 dark:border-slate-850 sm:pl-6">
              <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wide">Expected Closures (Qtr)</span>
              <p className="text-xl font-black text-emerald-600 dark:text-emerald-400">{summary.expectedRevenueQuarterFormatted}</p>
            </div>
          </div>

          {/* Performance sector insights */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
            <div className="bg-slate-50/50 dark:bg-slate-900/20 border border-slate-200 dark:border-slate-800/80 p-5 rounded-2xl flex items-start gap-4">
              <div className="p-2.5 bg-emerald-500/10 text-emerald-500 rounded-xl"><Award size={20} /></div>
              <div>
                <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wide">Best Performing Sector</span>
                <h4 className="font-bold text-slate-850 dark:text-slate-100 text-sm mt-1">{summary.bestPerformingSector}</h4>
              </div>
            </div>

            <div className="bg-slate-50/50 dark:bg-slate-900/20 border border-slate-200 dark:border-slate-800/80 p-5 rounded-2xl flex items-start gap-4">
              <div className="p-2.5 bg-rose-500/10 text-rose-500 rounded-xl"><ShieldAlert size={20} /></div>
              <div>
                <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wide">Under-performing / Low sector</span>
                <h4 className="font-bold text-slate-850 dark:text-slate-100 text-sm mt-1">{summary.worstPerformingSector}</h4>
              </div>
            </div>
          </div>

          {/* Business Risks */}
          <div className="space-y-4">
            <h3 className="text-xs font-extrabold uppercase tracking-wider text-slate-400 flex items-center gap-2">
              <ShieldAlert size={14} className="text-rose-500" />
              <span>Major Business & Delivery Risks</span>
            </h3>
            <div className="space-y-3">
              {summary.majorBusinessRisks.map((risk, idx) => (
                <div key={idx} className="flex gap-3 items-start bg-rose-500/5 dark:bg-rose-500/10 border border-rose-500/10 p-3.5 rounded-xl text-xs text-slate-700 dark:text-slate-300">
                  <span className="w-1.5 h-1.5 rounded-full bg-rose-500 mt-1.5 shrink-0"></span>
                  <span>{risk}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Strategic Actions */}
          <div className="space-y-4">
            <h3 className="text-xs font-extrabold uppercase tracking-wider text-slate-400 flex items-center gap-2">
              <CheckCircle2 size={14} className="text-emerald-500" />
              <span>Recommended Executive Actions</span>
            </h3>
            <div className="space-y-3">
              {summary.recommendedActions.map((act, idx) => (
                <div key={idx} className="flex gap-3 items-start bg-slate-50 dark:bg-slate-900/40 p-4 rounded-xl text-xs text-slate-700 dark:text-slate-300 border border-slate-200/80 dark:border-slate-800">
                  <ChevronRight size={14} className="text-cyan-500 mt-0.5 shrink-0" />
                  <span>{act}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
