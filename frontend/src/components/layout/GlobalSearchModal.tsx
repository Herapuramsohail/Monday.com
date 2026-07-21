"use client";

import React, { useState, useEffect, useRef } from 'react';
import { Search, X, Briefcase, FileSpreadsheet, ArrowRight } from 'lucide-react';
import { globalSearch } from '@/lib/api';
import { DealItem, WorkOrderItem } from '@/lib/types';
import Link from 'next/link';

interface GlobalSearchModalProps {
  onClose: () => void;
}

export default function GlobalSearchModal({ onClose }: GlobalSearchModalProps) {
  const [query, setQuery] = useState('');
  const [deals, setDeals] = useState<DealItem[]>([]);
  const [workOrders, setWorkOrders] = useState<WorkOrderItem[]>([]);
  const [loading, setLoading] = useState(false);
  const modalRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [onClose]);

  useEffect(() => {
    if (!query.trim()) {
      setDeals([]);
      setWorkOrders([]);
      return;
    }
    const delayDebounce = setTimeout(async () => {
      setLoading(true);
      try {
        const res = await globalSearch(query);
        setDeals(res.deals || []);
        setWorkOrders(res.workOrders || []);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }, 300);

    return () => clearTimeout(delayDebounce);
  }, [query]);

  const handleOutsideClick = (e: React.MouseEvent) => {
    if (modalRef.current && !modalRef.current.contains(e.target as Node)) {
      onClose();
    }
  };

  return (
    <div 
      onClick={handleOutsideClick}
      className="fixed inset-0 bg-slate-950/65 backdrop-blur-sm z-50 flex items-start justify-center pt-24"
    >
      <div 
        ref={modalRef}
        className="bg-white dark:bg-slate-900 w-full max-w-2xl rounded-2xl border border-slate-200 dark:border-slate-800 shadow-2xl overflow-hidden transition-all transform duration-300"
      >
        <div className="p-4 border-b border-slate-200 dark:border-slate-800 flex items-center gap-3">
          <Search className="text-slate-400 dark:text-slate-500" size={20} />
          <input
            autoFocus
            type="text"
            placeholder="Type query to search across Deal Funnel & Work Orders..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            className="flex-1 bg-transparent border-0 outline-none text-slate-800 dark:text-slate-100 placeholder-slate-400 dark:placeholder-slate-500 text-sm font-medium"
          />
          <button onClick={onClose} className="p-1 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-400">
            <X size={18} />
          </button>
        </div>

        <div className="max-h-96 overflow-y-auto p-4 space-y-6">
          {loading && (
            <div className="flex items-center justify-center py-8">
              <div className="w-6 h-6 border-2 border-cyan-400 border-t-transparent rounded-full animate-spin"></div>
            </div>
          )}

          {!loading && !query && (
            <div className="text-center py-8 text-slate-400 text-xs font-medium">
              Start typing to search globally...
            </div>
          )}

          {!loading && query && deals.length === 0 && workOrders.length === 0 && (
            <div className="text-center py-8 text-slate-400 text-xs font-medium">
              No matching records found.
            </div>
          )}

          {deals.length > 0 && (
            <div>
              <h3 className="text-[10px] font-bold tracking-wider text-slate-400 dark:text-slate-500 uppercase mb-2">Deal Funnel Matches ({deals.length})</h3>
              <div className="space-y-1">
                {deals.map((deal, idx) => (
                  <Link 
                    key={idx} 
                    href="/deals" 
                    onClick={onClose}
                    className="flex items-center gap-3 p-2.5 rounded-xl hover:bg-slate-50 dark:hover:bg-slate-800/50 transition group"
                  >
                    <Briefcase size={16} className="text-cyan-500" />
                    <div>
                      <p className="text-xs font-semibold text-slate-800 dark:text-slate-200">{deal.dealName}</p>
                      <p className="text-[10px] text-slate-500 font-medium">{deal.sector} • Owner: {deal.ownerCode}</p>
                    </div>
                    <span className="ml-auto text-[10px] font-bold text-slate-500 group-hover:text-cyan-400 flex items-center gap-1 transition">
                      View <ArrowRight size={12} />
                    </span>
                  </Link>
                ))}
              </div>
            </div>
          )}

          {workOrders.length > 0 && (
            <div>
              <h3 className="text-[10px] font-bold tracking-wider text-slate-400 dark:text-slate-500 uppercase mb-2">Work Order Matches ({workOrders.length})</h3>
              <div className="space-y-1">
                {workOrders.map((wo, idx) => (
                  <Link 
                    key={idx} 
                    href="/work-orders" 
                    onClick={onClose}
                    className="flex items-center gap-3 p-2.5 rounded-xl hover:bg-slate-50 dark:hover:bg-slate-800/50 transition group"
                  >
                    <FileSpreadsheet size={16} className="text-rose-500" />
                    <div>
                      <p className="text-xs font-semibold text-slate-800 dark:text-slate-200">{wo.dealName} (`{wo.serialNo}`)</p>
                      <p className="text-[10px] text-slate-500 font-medium">{wo.natureOfWork} • Customer: {wo.customerNameCode} | Status: {wo.executionStatus}</p>
                    </div>
                    <span className="ml-auto text-[10px] font-bold text-slate-500 group-hover:text-rose-500 flex items-center gap-1 transition">
                      View <ArrowRight size={12} />
                    </span>
                  </Link>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
