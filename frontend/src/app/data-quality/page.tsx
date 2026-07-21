"use client";

import React, { useState, useEffect } from 'react';
import { fetchDataQualityReport } from '@/lib/api';
import { DataQualityReportResponse } from '@/lib/types';
import { ShieldCheck, AlertTriangle, RefreshCw, FileText, Settings, HelpCircle, HardDrive } from 'lucide-react';

export default function DataQualityPage() {
  const [data, setData] = useState<DataQualityReportResponse | null>(null);
  const [loading, setLoading] = useState(true);

  const loadReport = async () => {
    setLoading(true);
    try {
      const res = await fetchDataQualityReport();
      setData(res);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadReport();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-[80vh]">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-cyan-400 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-slate-500 font-semibold text-sm">Auditing data cleanliness and compliance rules...</p>
        </div>
      </div>
    );
  }

  const getScoreColor = (score: number) => {
    if (score >= 90) return 'text-emerald-500 border-emerald-500/20 bg-emerald-500/5';
    if (score >= 75) return 'text-amber-500 border-amber-500/20 bg-amber-500/5';
    return 'text-rose-500 border-rose-500/20 bg-rose-500/5';
  };

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold tracking-tight text-slate-800 dark:text-white">Data Quality Auditor</h2>
          <p className="text-xs text-slate-500 font-semibold">Integrity audit logs, deduplication, missing data imputation, and sanitization summary</p>
        </div>
        <button 
          onClick={loadReport}
          className="flex items-center gap-2 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 px-4 py-2 rounded-xl text-xs font-semibold text-slate-700 dark:text-slate-300 hover:bg-slate-50 transition"
        >
          <RefreshCw size={14} />
          <span>Rerun Audit</span>
        </button>
      </div>

      {data && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left panel: Score and Stats */}
          <div className="lg:col-span-1 space-y-6">
            <div className={`p-6 rounded-3xl border text-center ${getScoreColor(data.confidenceScore)}`}>
              <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">Data Confidence Score</span>
              <p className="text-5xl font-black mt-2">{data.confidenceScore}%</p>
              <div className="mt-4 flex items-center justify-center gap-2 text-xs font-semibold">
                <ShieldCheck size={16} />
                <span>{data.confidenceScore >= 80 ? 'Robust Data Health' : 'Needs Optimization'}</span>
              </div>
            </div>

            <div className="bg-white dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-3xl p-5 space-y-4">
              <h3 className="text-xs font-bold uppercase text-slate-400 tracking-wider">Audit Metrics</h3>
              
              <div className="flex items-center justify-between text-xs py-1.5 border-b border-slate-100 dark:border-slate-850">
                <span className="text-slate-500">Missing Values Handled</span>
                <span className="font-bold text-slate-700 dark:text-slate-200">{data.missingValuesCount}</span>
              </div>

              <div className="flex items-center justify-between text-xs py-1.5 border-b border-slate-100 dark:border-slate-850">
                <span className="text-slate-500">Duplicate Companies Merged</span>
                <span className="font-bold text-slate-700 dark:text-slate-200">{data.duplicateRecordsCount}</span>
              </div>

              <div className="flex items-center justify-between text-xs py-1.5 border-b border-slate-100 dark:border-slate-850">
                <span className="text-slate-500">Date Formats Corrected</span>
                <span className="font-bold text-slate-700 dark:text-slate-200">{data.invalidDatesFixed}</span>
              </div>

              <div className="flex items-center justify-between text-xs py-1.5 border-b border-slate-100 dark:border-slate-850">
                <span className="text-slate-500">Empty Sectors Reclassified</span>
                <span className="font-bold text-slate-700 dark:text-slate-200">{data.emptySectorsHandled}</span>
              </div>

              <div className="flex items-center justify-between text-xs py-1.5">
                <span className="text-slate-500">Incomplete Work Orders</span>
                <span className="font-bold text-slate-700 dark:text-slate-200">{data.incompleteWorkOrders}</span>
              </div>
            </div>

            <div className="bg-white dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-3xl p-5 space-y-2">
              <h3 className="text-xs font-bold uppercase text-slate-400 tracking-wider mb-2">Record Volumes</h3>
              <div className="flex items-center gap-3">
                <HardDrive className="text-slate-400" size={18} />
                <div className="text-xs">
                  <p className="font-bold text-slate-700 dark:text-slate-200">{data.totalCleanedDeals} Deals Cleaned</p>
                  <p className="text-slate-400 font-semibold">{data.totalCleanedWorkOrders} Work Orders Cleaned</p>
                </div>
              </div>
            </div>
          </div>

          {/* Right Panel: Operations log */}
          <div className="lg:col-span-2 bg-white dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-3xl p-6 flex flex-col h-[70vh]">
            <h3 className="text-xs font-bold uppercase text-slate-400 tracking-wider mb-4">Cleaner Operations Log</h3>
            <div className="flex-1 overflow-y-auto space-y-4 pr-2">
              {data.logs && data.logs.length === 0 ? (
                <div className="text-center py-12 text-slate-400 text-xs">No cleaning operations logged yet.</div>
              ) : (
                data.logs.map((log, idx) => (
                  <div 
                    key={idx} 
                    className="p-4 bg-slate-50 dark:bg-slate-900/40 rounded-2xl border border-slate-200/80 dark:border-slate-850 flex gap-4 items-start hover:border-slate-300 dark:hover:border-slate-800 transition"
                  >
                    <div className="p-2 bg-cyan-500/10 text-cyan-500 rounded-xl mt-0.5 shrink-0">
                      <Settings size={16} className="animate-spin [animation-duration:12s]" />
                    </div>
                    <div className="space-y-1">
                      <div className="flex items-center gap-2">
                        <h4 className="font-bold text-slate-850 dark:text-slate-100 text-xs">{log.operation}</h4>
                        <span className="text-[9px] font-bold text-cyan-500 bg-cyan-500/10 px-2 py-0.5 rounded-full border border-cyan-500/10">Field: {log.field}</span>
                      </div>
                      <p className="text-slate-500 text-[11px] font-semibold">{log.details}</p>
                      <div className="flex items-center gap-2.5 pt-1 text-[10px] text-slate-400 font-semibold">
                        <span>Affected Count: <strong className="text-slate-600 dark:text-slate-300">{log.affectedCount}</strong></span>
                        <span>•</span>
                        <span>{log.timestamp}</span>
                      </div>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
