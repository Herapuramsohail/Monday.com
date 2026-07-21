"use client";

import React, { useState, useEffect } from 'react';
import { fetchWorkOrders } from '@/lib/api';
import { WorkOrderItem, FilterParams } from '@/lib/types';
import { Search, RefreshCw, AlertTriangle, Sparkles, Filter, Calendar } from 'lucide-react';

export default function WorkOrdersPage() {
  const [workOrders, setWorkOrders] = useState<WorkOrderItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [filters, setFilters] = useState<FilterParams>({
    sector: 'all',
    workOrderStatus: 'all',
    customer: 'all',
  });

  const [sectors, setSectors] = useState<string[]>([]);
  const [statuses, setStatuses] = useState<string[]>([]);
  const [customers, setCustomers] = useState<string[]>([]);

  const loadWorkOrders = async () => {
    setLoading(true);
    try {
      const res = await fetchWorkOrders(filters);
      setWorkOrders(res.workOrders || []);

      const uniqueSectors = Array.from(new Set((res.workOrders || []).map(w => w.sector))).filter(Boolean);
      const uniqueStatuses = Array.from(new Set((res.workOrders || []).map(w => w.executionStatus))).filter(Boolean);
      const uniqueCustomers = Array.from(new Set((res.workOrders || []).map(w => w.customerNameCode))).filter(Boolean);

      setSectors(uniqueSectors);
      setStatuses(uniqueStatuses);
      setCustomers(uniqueCustomers);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadWorkOrders();
  }, [filters]);

  const filteredOrders = workOrders.filter(w => {
    const text = `${w.dealName} ${w.customerNameCode} ${w.serialNo} ${w.bdPersonnelCode} ${w.sector} ${w.natureOfWork}`.lower();
    return text.includes(search.toLowerCase());
  });

  const getStatusStyle = (status: string, isDelayed: boolean) => {
    if (isDelayed) {
      return 'bg-rose-500/10 text-rose-600 dark:text-rose-400 border-rose-500/20';
    }
    switch (status.toLowerCase()) {
      case 'completed':
      case 'executed':
      case 'closed':
        return 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border-emerald-500/20';
      case 'ongoing':
      case 'in progress':
      case 'executed until current month':
        return 'bg-blue-500/10 text-blue-600 dark:text-blue-400 border-blue-500/20';
      default:
        return 'bg-slate-500/10 text-slate-600 dark:text-slate-400 border-slate-500/20';
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold tracking-tight text-slate-800 dark:text-white">Work Order Tracker</h2>
        <p className="text-xs text-slate-500 font-semibold">Real-time status of client project delivery pipelines, deliverables, PO dates, and deadlines</p>
      </div>

      {/* Control bar */}
      <div className="flex flex-col lg:flex-row items-center justify-between gap-4 bg-white dark:bg-slate-950 p-4 border border-slate-200 dark:border-slate-800 rounded-2xl shadow-sm">
        <div className="flex items-center gap-2 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl px-3.5 py-2 w-full lg:w-80">
          <Search size={16} className="text-slate-400" />
          <input 
            type="text" 
            placeholder="Search serial #, client, deal name..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="bg-transparent border-0 outline-none text-xs text-slate-800 dark:text-slate-100 placeholder-slate-400 w-full"
          />
        </div>

        <div className="flex flex-wrap items-center gap-3 w-full lg:w-auto">
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
            value={filters.workOrderStatus}
            onChange={(e) => setFilters({...filters, workOrderStatus: e.target.value})}
            className="bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl px-3 py-2 text-xs font-semibold text-slate-700 dark:text-slate-300 outline-none"
          >
            <option value="all">All Statuses</option>
            {statuses.map(s => <option key={s} value={s}>{s}</option>)}
          </select>

          <select 
            value={filters.customer}
            onChange={(e) => setFilters({...filters, customer: e.target.value})}
            className="bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl px-3 py-2 text-xs font-semibold text-slate-700 dark:text-slate-300 outline-none"
          >
            <option value="all">All Customers</option>
            {customers.map(c => <option key={c} value={c}>{c}</option>)}
          </select>

          <button onClick={loadWorkOrders} className="p-2 border border-slate-200 dark:border-slate-800 hover:bg-slate-50 dark:hover:bg-slate-900 rounded-xl text-slate-500">
            <RefreshCw size={14} />
          </button>
        </div>
      </div>

      {/* Grid Table */}
      <div className="bg-white dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-2xl shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-xs">
            <thead>
              <tr className="bg-slate-50 dark:bg-slate-900/60 border-b border-slate-200 dark:border-slate-800 text-slate-400 font-bold uppercase tracking-wider">
                <th className="py-4 px-5">Serial # / Deal</th>
                <th className="py-4 px-5">Customer Code</th>
                <th className="py-4 px-5">Nature of Work</th>
                <th className="py-4 px-5">Status</th>
                <th className="py-4 px-5">Delivery Target</th>
                <th className="py-4 px-5">Total Value (Masked)</th>
                <th className="py-4 px-5">Collected (Masked)</th>
                <th className="py-4 px-5">Receivables</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 dark:divide-slate-850 font-medium">
              {loading ? (
                <tr>
                  <td colSpan={8} className="py-12 text-center text-slate-400">
                    <div className="w-6 h-6 border-2 border-cyan-400 border-t-transparent rounded-full animate-spin mx-auto mb-2"></div>
                    Loading tracker entries...
                  </td>
                </tr>
              ) : filteredOrders.length === 0 ? (
                <tr>
                  <td colSpan={8} className="py-8 text-center text-slate-400">No matching work orders.</td>
                </tr>
              ) : (
                filteredOrders.map((wo, idx) => (
                  <tr key={idx} className="hover:bg-slate-50/50 dark:hover:bg-slate-900/35 transition">
                    <td className="py-4 px-5">
                      <div>
                        <span className="font-mono text-[9px] font-bold bg-slate-100 dark:bg-slate-900 px-1.5 py-0.5 rounded text-slate-500 mb-0.5 inline-block">{wo.serialNo}</span>
                        <p className="font-bold text-slate-800 dark:text-slate-200">{wo.dealName}</p>
                      </div>
                    </td>
                    <td className="py-4 px-5 font-mono text-[10px] text-slate-500">{wo.customerNameCode}</td>
                    <td className="py-4 px-5 text-slate-600 dark:text-slate-400">
                      <p className="truncate max-w-[150px]">{wo.natureOfWork}</p>
                      <span className="text-[10px] text-slate-400">{wo.typeOfWork} • {wo.sector}</span>
                    </td>
                    <td className="py-4 px-5">
                      <span className={`px-2.5 py-1 rounded-full border text-[10px] font-bold flex items-center gap-1.5 w-fit ${getStatusStyle(wo.executionStatus, wo.isDelayed)}`}>
                        {wo.isDelayed && <AlertTriangle size={10} />}
                        <span>{wo.executionStatus}{wo.isDelayed ? ' (Delayed)' : ''}</span>
                      </span>
                    </td>
                    <td className="py-4 px-5 text-slate-500">
                      <div className="flex items-center gap-1">
                        <Calendar size={12} />
                        <span>{wo.probableEndDate || 'N/A'}</span>
                      </div>
                    </td>
                    <td className="py-4 px-5 font-bold text-slate-700 dark:text-slate-300">
                      ₹{wo.amountRupeesInclGST.toLocaleString('en-IN')}
                    </td>
                    <td className="py-4 px-5 text-emerald-500">
                      ₹{wo.collectedAmountInclGST.toLocaleString('en-IN')}
                    </td>
                    <td className="py-4 px-5 text-rose-500 font-bold">
                      ₹{wo.amountReceivable.toLocaleString('en-IN')}
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
