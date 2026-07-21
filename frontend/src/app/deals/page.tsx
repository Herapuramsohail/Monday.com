"use client";

import React, { useState, useEffect } from 'react';
import { fetchDeals } from '@/lib/api';
import { DealItem, FilterParams } from '@/lib/types';
import { Search, RefreshCw, AlertCircle, Sparkles, Filter } from 'lucide-react';

export default function DealsPage() {
  const [deals, setDeals] = useState<DealItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [filters, setFilters] = useState<FilterParams>({
    sector: 'all',
    dealStage: 'all',
  });
  
  // Available filter options
  const [sectors, setSectors] = useState<string[]>([]);
  const [stages, setStages] = useState<string[]>([]);

  const loadDeals = async () => {
    setLoading(true);
    try {
      const res = await fetchDeals(filters);
      setDeals(res.deals || []);

      // Extract filter values
      const uniqueSectors = Array.from(new Set((res.deals || []).map(d => d.sector))).filter(Boolean);
      const uniqueStages = Array.from(new Set((res.deals || []).map(d => d.dealStage))).filter(Boolean);
      setSectors(uniqueSectors);
      setStages(uniqueStages);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDeals();
  }, [filters]);

  const filteredDeals = deals.filter(d => {
    const text = `${d.dealName} ${d.clientCode} ${d.ownerCode} ${d.sector} ${d.productDeal}`.lower();
    return text.includes(search.toLowerCase());
  });

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'closed won':
      case 'closed':
        return 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border-emerald-500/20';
      case 'closed lost':
        return 'bg-rose-500/10 text-rose-600 dark:text-rose-400 border-rose-500/20';
      default:
        return 'bg-cyan-500/10 text-cyan-600 dark:text-cyan-400 border-cyan-500/20';
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold tracking-tight text-slate-800 dark:text-white">Deal Funnel Board</h2>
        <p className="text-xs text-slate-500 font-semibold">Granular view of active sales opportunities, values, and closure likelihoods</p>
      </div>

      {/* Control bar */}
      <div className="flex flex-col md:flex-row items-center justify-between gap-4 bg-white dark:bg-slate-950 p-4 border border-slate-200 dark:border-slate-800 rounded-2xl shadow-sm">
        {/* Search */}
        <div className="flex items-center gap-2 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl px-3.5 py-2 w-full md:w-80">
          <Search size={16} className="text-slate-400" />
          <input 
            type="text" 
            placeholder="Search deals, clients, owners..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="bg-transparent border-0 outline-none text-xs text-slate-800 dark:text-slate-100 placeholder-slate-400 w-full"
          />
        </div>

        {/* Filters */}
        <div className="flex flex-wrap items-center gap-3 w-full md:w-auto">
          <div className="flex items-center gap-2 text-xs font-bold text-slate-400">
            <Filter size={14} />
            <span>FILTER BY:</span>
          </div>

          <select 
            value={filters.sector}
            onChange={(e) => setFilters({...filters, sector: e.target.value})}
            className="bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl px-3 py-2 text-xs font-semibold text-slate-700 dark:text-slate-300 outline-none"
          >
            <option value="all">All Sectors</option>
            {sectors.map(s => <option key={s} value={s}>{s}</option>)}
          </select>

          <select 
            value={filters.dealStage}
            onChange={(e) => setFilters({...filters, dealStage: e.target.value})}
            className="bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl px-3 py-2 text-xs font-semibold text-slate-700 dark:text-slate-300 outline-none"
          >
            <option value="all">All Stages</option>
            {stages.map(s => <option key={s} value={s}>{s}</option>)}
          </select>

          <button 
            onClick={loadDeals}
            className="p-2 border border-slate-200 dark:border-slate-800 hover:bg-slate-50 dark:hover:bg-slate-900 rounded-xl text-slate-500"
          >
            <RefreshCw size={14} />
          </button>
        </div>
      </div>

      {/* Table grid */}
      <div className="bg-white dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-2xl shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-xs">
            <thead>
              <tr className="bg-slate-50 dark:bg-slate-900/60 border-b border-slate-200 dark:border-slate-800 text-slate-400 font-bold uppercase tracking-wider">
                <th className="py-4 px-5">Deal Name</th>
                <th className="py-4 px-5">Client Code</th>
                <th className="py-4 px-5">Value</th>
                <th className="py-4 px-5">Stage</th>
                <th className="py-4 px-5">Sector</th>
                <th className="py-4 px-5">Closure Probability</th>
                <th className="py-4 px-5">Status</th>
                <th className="py-4 px-5">Quality Flags</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 dark:divide-slate-850 font-medium">
              {loading ? (
                <tr>
                  <td colSpan={8} className="py-12 text-center text-slate-400">
                    <div className="w-6 h-6 border-2 border-cyan-400 border-t-transparent rounded-full animate-spin mx-auto mb-2"></div>
                    Loading deals list...
                  </td>
                </tr>
              ) : filteredDeals.length === 0 ? (
                <tr>
                  <td colSpan={8} className="py-8 text-center text-slate-400">No matching deals found.</td>
                </tr>
              ) : (
                filteredDeals.map((deal, idx) => (
                  <tr key={idx} className="hover:bg-slate-50/50 dark:hover:bg-slate-900/35 transition">
                    <td className="py-4 px-5 font-bold text-slate-800 dark:text-slate-200">{deal.dealName}</td>
                    <td className="py-4 px-5 font-mono text-[10px] text-slate-500">{deal.clientCode}</td>
                    <td className="py-4 px-5 font-bold text-slate-700 dark:text-slate-300">
                      ₹{deal.maskedDealValue.toLocaleString('en-IN')}
                    </td>
                    <td className="py-4 px-5">
                      <span className="bg-slate-100 dark:bg-slate-900 text-slate-600 dark:text-slate-400 px-2 py-1 rounded-md border border-slate-200 dark:border-slate-800/80">
                        {deal.dealStage}
                      </span>
                    </td>
                    <td className="py-4 px-5 text-slate-500">{deal.sector}</td>
                    <td className="py-4 px-5">
                      <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                        deal.closureProbability === 'High' ? 'bg-emerald-500/15 text-emerald-500' :
                        deal.closureProbability === 'Medium' ? 'bg-amber-500/15 text-amber-500' : 'bg-slate-500/15 text-slate-500'
                      }`}>
                        {deal.closureProbability}
                      </span>
                    </td>
                    <td className="py-4 px-5">
                      <span className={`px-2.5 py-1 rounded-full border text-[10px] font-bold ${getStatusColor(deal.dealStatus)}`}>
                        {deal.dealStatus}
                      </span>
                    </td>
                    <td className="py-4 px-5">
                      <div className="flex flex-wrap gap-1">
                        {deal.cleaningBadges && deal.cleaningBadges.map((badge, bIdx) => (
                          <span 
                            key={bIdx}
                            className="bg-amber-500/10 text-amber-600 border border-amber-500/20 text-[9px] font-bold px-1.5 py-0.5 rounded flex items-center gap-1"
                          >
                            <AlertCircle size={10} />
                            {badge}
                          </span>
                        ))}
                        {(!deal.cleaningBadges || deal.cleaningBadges.length === 0) && (
                          <span className="text-emerald-500 flex items-center gap-1 font-bold text-[10px]">
                            <Sparkles size={11} /> Clean
                          </span>
                        )}
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
