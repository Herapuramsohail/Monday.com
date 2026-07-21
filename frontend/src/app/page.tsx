"use client";

import React, { useState, useEffect } from 'react';
import { fetchDashboard } from '@/lib/api';
import { DashboardResponse, FilterParams } from '@/lib/types';
import { 
  Briefcase, 
  Layers, 
  CheckSquare, 
  DollarSign, 
  TrendingUp, 
  Activity, 
  Calendar, 
  RefreshCw, 
  Percent,
  AlertTriangle
} from 'lucide-react';
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, 
  PieChart, Pie, Cell, LineChart, Line, AreaChart, Area 
} from 'recharts';

export default function Dashboard() {
  const [data, setData] = useState<DashboardResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  
  // Filters State
  const [filters, setFilters] = useState<FilterParams>({
    sector: 'all',
    dealStage: 'all',
    salesperson: 'all',
    workOrderStatus: 'all',
  });

  const loadData = async () => {
    setLoading(true);
    try {
      const res = await fetchDashboard(filters);
      setData(res);
    } catch (err: any) {
      setError(err.message || "Failed to load dashboard data");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [filters]);

  const formatCurrency = (val: number) => {
    if (val >= 10000000) {
      return `₹${(val / 10000000).toFixed(2)} Cr`;
    }
    return `₹${val.toLocaleString('en-IN', { maximumFractionDigits: 0 })}`;
  };

  if (loading && !data) {
    return (
      <div className="flex items-center justify-center h-[80vh]">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-cyan-400 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-slate-500 font-semibold text-sm">Parsing & cleaning Monday board datasets...</p>
        </div>
      </div>
    );
  }

  const kpis = data?.kpis;
  const charts = data?.charts;
  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#a855f7', '#ec4899', '#3b82f6'];

  return (
    <div className="space-y-6">
      {/* Upper header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold tracking-tight text-slate-800 dark:text-white">Executive BI Dashboard</h2>
          <p className="text-xs text-slate-500 font-semibold">Live business metrics consolidated from Monday boards</p>
        </div>
        <button 
          onClick={loadData}
          className="flex items-center gap-2 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 px-4 py-2 rounded-xl text-xs font-semibold text-slate-700 dark:text-slate-300 hover:bg-slate-50 transition"
        >
          <RefreshCw size={14} />
          <span>Refresh Live</span>
        </button>
      </div>

      {/* Filter Bar */}
      <div className="bg-white dark:bg-slate-950 border border-slate-200 dark:border-slate-800 p-4 rounded-2xl flex flex-wrap gap-4 shadow-sm">
        <div className="flex flex-col gap-1.5 flex-1 min-w-[150px]">
          <label className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Sector</label>
          <select 
            value={filters.sector}
            onChange={(e) => setFilters({...filters, sector: e.target.value})}
            className="bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl px-3 py-2 text-xs font-semibold text-slate-700 dark:text-slate-300 outline-none"
          >
            <option value="all">All Sectors</option>
            {data?.sectors.map(s => <option key={s} value={s}>{s}</option>)}
          </select>
        </div>

        <div className="flex flex-col gap-1.5 flex-1 min-w-[150px]">
          <label className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Deal Stage</label>
          <select 
            value={filters.dealStage}
            onChange={(e) => setFilters({...filters, dealStage: e.target.value})}
            className="bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl px-3 py-2 text-xs font-semibold text-slate-700 dark:text-slate-300 outline-none"
          >
            <option value="all">All Stages</option>
            {data?.dealStages.map(s => <option key={s} value={s}>{s}</option>)}
          </select>
        </div>

        <div className="flex flex-col gap-1.5 flex-1 min-w-[150px]">
          <label className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Salesperson</label>
          <select 
            value={filters.salesperson}
            onChange={(e) => setFilters({...filters, salesperson: e.target.value})}
            className="bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl px-3 py-2 text-xs font-semibold text-slate-700 dark:text-slate-300 outline-none"
          >
            <option value="all">All Owners</option>
            {data?.salespersons.map(s => <option key={s} value={s}>{s}</option>)}
          </select>
        </div>

        <div className="flex flex-col gap-1.5 flex-1 min-w-[150px]">
          <label className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Work Order Status</label>
          <select 
            value={filters.workOrderStatus}
            onChange={(e) => setFilters({...filters, workOrderStatus: e.target.value})}
            className="bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl px-3 py-2 text-xs font-semibold text-slate-700 dark:text-slate-300 outline-none"
          >
            <option value="all">All statuses</option>
            {data?.workOrderStatuses.map(s => <option key={s} value={s}>{s}</option>)}
          </select>
        </div>
      </div>

      {/* KPI Cards */}
      {kpis && (
        <div className="grid grid-cols-2 lg:grid-cols-5 gap-4">
          <div className="bg-white dark:bg-slate-950 border border-slate-200 dark:border-slate-800 p-5 rounded-2xl shadow-sm hover:shadow-md transition">
            <div className="flex items-center justify-between mb-2">
              <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Total Funnel Deals</span>
              <div className="p-2 bg-cyan-500/10 text-cyan-500 rounded-xl"><Briefcase size={16} /></div>
            </div>
            <p className="text-2xl font-bold">{kpis.totalDeals}</p>
            <p className="text-[10px] text-slate-500 font-semibold mt-1">{kpis.openDeals} Active | {kpis.closedDeals} Closed</p>
          </div>

          <div className="bg-white dark:bg-slate-950 border border-slate-200 dark:border-slate-800 p-5 rounded-2xl shadow-sm hover:shadow-md transition">
            <div className="flex items-center justify-between mb-2">
              <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Pipeline Value</span>
              <div className="p-2 bg-emerald-500/10 text-emerald-500 rounded-xl"><DollarSign size={16} /></div>
            </div>
            <p className="text-2xl font-bold">{formatCurrency(kpis.totalPipelineValue)}</p>
            <p className="text-[10px] text-slate-500 font-semibold mt-1">Avg Deal: {formatCurrency(kpis.averageDealSize)}</p>
          </div>

          <div className="bg-white dark:bg-slate-950 border border-slate-200 dark:border-slate-800 p-5 rounded-2xl shadow-sm hover:shadow-md transition">
            <div className="flex items-center justify-between mb-2">
              <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Expected Revenue</span>
              <div className="p-2 bg-indigo-500/10 text-indigo-500 rounded-xl"><TrendingUp size={16} /></div>
            </div>
            <p className="text-2xl font-bold">{formatCurrency(kpis.expectedRevenue)}</p>
            <p className="text-[10px] text-slate-500 font-semibold mt-1">Weighted conversion: {kpis.conversionRate}%</p>
          </div>

          <div className="bg-white dark:bg-slate-950 border border-slate-200 dark:border-slate-800 p-5 rounded-2xl shadow-sm hover:shadow-md transition">
            <div className="flex items-center justify-between mb-2">
              <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Active Work Orders</span>
              <div className="p-2 bg-blue-500/10 text-blue-500 rounded-xl"><Activity size={16} /></div>
            </div>
            <p className="text-2xl font-bold">{kpis.activeWorkOrders}</p>
            <p className="text-[10px] text-slate-500 font-semibold mt-1">{kpis.completedWorkOrders} Delivered</p>
          </div>

          <div className="bg-white dark:bg-slate-950 border border-slate-200 dark:border-slate-800 p-5 rounded-2xl shadow-sm hover:shadow-md transition">
            <div className="flex items-center justify-between mb-2">
              <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Delayed Projects</span>
              <div className="p-2 bg-rose-500/10 text-rose-500 rounded-xl"><AlertTriangle size={16} /></div>
            </div>
            <p className="text-2xl font-bold text-rose-500">{kpis.delayedWorkOrders}</p>
            <p className="text-[10px] text-slate-500 font-semibold mt-1">Requiring action</p>
          </div>
        </div>
      )}

      {/* Main Charts Row */}
      {charts && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Revenue by Sector Chart */}
          <div className="bg-white dark:bg-slate-950 border border-slate-200 dark:border-slate-800 p-5 rounded-2xl shadow-sm">
            <h3 className="text-sm font-bold text-slate-700 dark:text-slate-200 mb-4 uppercase tracking-wide">Revenue Pipeline by Sector</h3>
            <div className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={charts.revenueBySector}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#33415520" />
                  <XAxis dataKey="name" stroke="#64748b" fontSize={11} tickLine={false} />
                  <YAxis stroke="#64748b" fontSize={11} tickLine={false} tickFormatter={(v) => `₹${(v/10000000).toFixed(0)}Cr`} />
                  <Tooltip formatter={(value: any) => [formatCurrency(value), "Pipeline"]} contentStyle={{ borderRadius: '12px' }} />
                  <Bar dataKey="value" fill="#00c6ff" radius={[8, 8, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Deals by Month Trend */}
          <div className="bg-white dark:bg-slate-950 border border-slate-200 dark:border-slate-800 p-5 rounded-2xl shadow-sm">
            <h3 className="text-sm font-bold text-slate-700 dark:text-slate-200 mb-4 uppercase tracking-wide">Deal Intake Trend (Monthly)</h3>
            <div className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={charts.dealsByMonth}>
                  <defs>
                    <linearGradient id="colorValue" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#0072ff" stopOpacity={0.3}/>
                      <stop offset="95%" stopColor="#0072ff" stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#33415520" />
                  <XAxis dataKey="name" stroke="#64748b" fontSize={11} tickLine={false} />
                  <YAxis stroke="#64748b" fontSize={11} tickLine={false} tickFormatter={(v) => `₹${(v/10000000).toFixed(0)}Cr`} />
                  <Tooltip formatter={(value: any) => [formatCurrency(value), "Total Value"]} />
                  <Area type="monotone" dataKey="value" stroke="#0072ff" strokeWidth={2.5} fillOpacity={1} fill="url(#colorValue)" />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Pipeline Stages Breakdown */}
          <div className="bg-white dark:bg-slate-950 border border-slate-200 dark:border-slate-800 p-5 rounded-2xl shadow-sm">
            <h3 className="text-sm font-bold text-slate-700 dark:text-slate-200 mb-4 uppercase tracking-wide">Deals Pipeline by Funnel Stage</h3>
            <div className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart layout="vertical" data={charts.pipelineByStage.slice(0, 5)}>
                  <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#33415520" />
                  <XAxis type="number" stroke="#64748b" fontSize={11} tickLine={false} tickFormatter={(v) => `₹${(v/10000000).toFixed(0)}Cr`} />
                  <YAxis dataKey="name" type="category" stroke="#64748b" fontSize={10} width={120} tickLine={false} />
                  <Tooltip formatter={(value: any) => [formatCurrency(value), "Value"]} />
                  <Bar dataKey="value" fill="#ec4899" radius={[0, 8, 8, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Project Statuses */}
          <div className="bg-white dark:bg-slate-950 border border-slate-200 dark:border-slate-800 p-5 rounded-2xl shadow-sm flex flex-col justify-between">
            <h3 className="text-sm font-bold text-slate-700 dark:text-slate-200 mb-4 uppercase tracking-wide">Work Orders Execution Status</h3>
            <div className="flex-1 h-64 flex items-center justify-center">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={charts.workOrdersByStatus}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={90}
                    paddingAngle={3}
                    dataKey="value"
                  >
                    {charts.workOrdersByStatus.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip formatter={(value: any) => [value, "Work Orders"]} />
                </PieChart>
              </ResponsiveContainer>
            </div>
            <div className="grid grid-cols-3 gap-2 text-center text-xs font-semibold mt-4">
              {charts.workOrdersByStatus.slice(0, 6).map((item, index) => (
                <div key={item.name} className="flex flex-col items-center">
                  <div className="flex items-center gap-1.5">
                    <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: COLORS[index % COLORS.length] }}></span>
                    <span className="text-[10px] text-slate-500 truncate max-w-[80px]">{item.name}</span>
                  </div>
                  <span className="font-bold text-slate-700 dark:text-slate-200 mt-0.5">{item.value}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
