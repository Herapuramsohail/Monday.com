"use client";

import React, { useState, useEffect } from 'react';
import { verifyConnection } from '@/lib/api';
import { ShieldCheck, Database, Key, Settings, RefreshCw, CheckCircle2, AlertTriangle } from 'lucide-react';

export default function SettingsPage() {
  const [token, setToken] = useState("");
  const [dealId, setDealId] = useState("");
  const [workId, setWorkId] = useState("");
  
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState<{ success?: boolean; message: string } | null>(null);

  useEffect(() => {
    setToken(localStorage.getItem('mondayApiToken') || "");
    setDealId(localStorage.getItem('mondayDealBoardId') || "");
    setWorkId(localStorage.getItem('mondayWorkBoardId') || "");
  }, []);

  const handleSave = () => {
    localStorage.setItem('mondayApiToken', token);
    localStorage.setItem('mondayDealBoardId', dealId);
    localStorage.setItem('mondayWorkBoardId', workId);
    setStatus({ success: true, message: "Settings saved successfully! Board queries will reload." });
  };

  const handleTest = async () => {
    if (!token || !dealId || !workId) {
      setStatus({ success: false, message: "Please fill out all token and board ID configuration fields." });
      return;
    }
    setLoading(true);
    setStatus(null);
    try {
      const res = await verifyConnection(token, dealId, workId);
      if (res.success) {
        setStatus({
          success: true,
          message: `Connected successfully! Found boards: '${res.dealBoardName}' (${res.dealItemsCount} rows) and '${res.workBoardName}' (${res.workItemsCount} rows).`
        });
        // Save automatically
        localStorage.setItem('mondayApiToken', token);
        localStorage.setItem('mondayDealBoardId', dealId);
        localStorage.setItem('mondayWorkBoardId', workId);
      } else {
        setStatus({ success: false, message: res.message });
      }
    } catch (err: any) {
      setStatus({ success: false, message: err.message || "Failed to reach Monday.com API. Verify token credentials." });
    } finally {
      setLoading(false);
    }
  };

  const handleClear = () => {
    localStorage.removeItem('mondayApiToken');
    localStorage.removeItem('mondayDealBoardId');
    localStorage.removeItem('mondayWorkBoardId');
    setToken("");
    setDealId("");
    setWorkId("");
    setStatus({ success: true, message: "Credentials cleared. Reverted back to high-fidelity offline datasets." });
  };

  return (
    <div className="space-y-6 max-w-2xl mx-auto">
      <div>
        <h2 className="text-2xl font-bold tracking-tight text-slate-800 dark:text-white">Credentials & settings</h2>
        <p className="text-xs text-slate-500 font-semibold">Verify Monday.com API Token and connect boards dynamically</p>
      </div>

      <div className="bg-white dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-3xl p-6 space-y-6 shadow-sm">
        {/* API Token */}
        <div className="space-y-2">
          <label className="text-xs font-bold text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
            <Key size={14} />
            <span>Monday.com Personal API Token</span>
          </label>
          <input
            type="password"
            placeholder="Paste your Monday v2 token here..."
            value={token}
            onChange={(e) => setToken(e.target.value)}
            className="w-full bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl px-4 py-3 text-xs font-semibold text-slate-700 dark:text-slate-200 outline-none"
          />
        </div>

        {/* Board IDs */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div className="space-y-2">
            <label className="text-xs font-bold text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
              <Database size={14} />
              <span>Deal Funnel Board ID</span>
            </label>
            <input
              type="text"
              placeholder="e.g. 1049497920"
              value={dealId}
              onChange={(e) => setDealId(e.target.value)}
              className="w-full bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl px-4 py-3 text-xs font-semibold text-slate-700 dark:text-slate-200 outline-none"
            />
          </div>

          <div className="space-y-2">
            <label className="text-xs font-bold text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
              <Database size={14} />
              <span>Work Order Tracker Board ID</span>
            </label>
            <input
              type="text"
              placeholder="e.g. 1049497921"
              value={workId}
              onChange={(e) => setWorkId(e.target.value)}
              className="w-full bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl px-4 py-3 text-xs font-semibold text-slate-700 dark:text-slate-200 outline-none"
            />
          </div>
        </div>

        {/* Status display */}
        {status && (
          <div className={`p-4 rounded-2xl border text-xs font-semibold flex gap-3 ${
            status.success 
              ? 'bg-emerald-500/10 border-emerald-500/20 text-emerald-600 dark:text-emerald-400' 
              : 'bg-rose-500/10 border-rose-500/20 text-rose-600 dark:text-rose-400'
          }`}>
            {status.success ? <CheckCircle2 size={16} className="shrink-0" /> : <AlertTriangle size={16} className="shrink-0" />}
            <span>{status.message}</span>
          </div>
        )}

        {/* Buttons tray */}
        <div className="flex items-center gap-3 pt-4 border-t border-slate-100 dark:border-slate-900">
          <button
            onClick={handleTest}
            disabled={loading}
            className="flex items-center gap-2 bg-slate-900 hover:bg-slate-800 text-white dark:bg-slate-100 dark:text-slate-950 dark:hover:bg-slate-200 px-4 py-2.5 rounded-xl text-xs font-bold transition disabled:opacity-50"
          >
            {loading ? <RefreshCw size={14} className="animate-spin" /> : <ShieldCheck size={14} />}
            <span>Test Monday Connection</span>
          </button>

          <button
            onClick={handleSave}
            className="bg-cyan-500 hover:bg-cyan-600 text-white px-4 py-2.5 rounded-xl text-xs font-bold transition"
          >
            Save Credentials
          </button>

          <button
            onClick={handleClear}
            className="ml-auto text-xs font-bold text-rose-500 hover:bg-rose-500/10 border border-transparent hover:border-rose-500/20 px-4 py-2.5 rounded-xl transition"
          >
            Clear Fields
          </button>
        </div>
      </div>
    </div>
  );
}
