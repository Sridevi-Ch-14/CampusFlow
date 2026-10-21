import React, { useState, useEffect } from 'react';
import { ComplaintListItem, Category, ComplaintListResponse } from '../types';
import api from '../services/api';
import { ComplaintFilters } from '../components/complaints/ComplaintFilters';
import { ComplaintCard } from '../components/complaints/ComplaintCard';
import { ChevronLeft, ChevronRight, PlusCircle } from 'lucide-react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export const MyComplaintsPage: React.FC = () => {
  const { user } = useAuth();
  const [complaints, setComplaints] = useState<ComplaintListItem[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [loading, setLoading] = useState(true);

  // Pagination & Filter state
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalItems, setTotalItems] = useState(0);

  const [search, setSearch] = useState('');
  const [status, setStatus] = useState('');
  const [priority, setPriority] = useState('');
  const [categoryId, setCategoryId] = useState('');
  const [isSlaBreached, setIsSlaBreached] = useState(false);

  useEffect(() => {
    api.get<Category[]>('/categories')
      .then((res) => setCategories(res.data))
      .catch((err) => console.error(err));
  }, []);

  const fetchComplaints = () => {
    setLoading(true);
    const params = new URLSearchParams();
    params.append('page', page.toString());
    params.append('page_size', '10');
    if (search) params.append('search', search);
    if (status) params.append('status', status);
    if (priority) params.append('priority', priority);
    if (categoryId) params.append('category_id', categoryId);
    if (isSlaBreached) params.append('is_sla_breached', 'true');

    api.get<ComplaintListResponse>(`/complaints?${params.toString()}`)
      .then((res) => {
        setComplaints(res.data.items);
        setTotalPages(res.data.total_pages);
        setTotalItems(res.data.total);
      })
      .catch((err) => console.error(err))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchComplaints();
  }, [page, search, status, priority, categoryId, isSlaBreached]);

  const handleReset = () => {
    setSearch('');
    setStatus('');
    setPriority('');
    setCategoryId('');
    setIsSlaBreached(false);
    setPage(1);
  };

  const isStudent = user?.role === 'STUDENT';

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-extrabold text-slate-900">
            {isStudent ? 'My Service Complaints' : 'Campus Complaint Directory'}
          </h1>
          <p className="text-xs text-slate-500 mt-1">
            Showing {totalItems} total facility complaints with backend-driven search and filtering.
          </p>
        </div>
        {isStudent && (
          <Link
            to="/create-complaint"
            className="inline-flex items-center justify-center gap-1.5 px-4 py-2.5 bg-sky-600 hover:bg-sky-700 text-white font-bold text-xs rounded-xl shadow-sm transition-colors shrink-0"
          >
            <PlusCircle className="w-4 h-4" />
            Submit Complaint
          </Link>
        )}
      </div>

      {/* Filter Controls */}
      <ComplaintFilters
        search={search}
        onSearchChange={(val) => { setSearch(val); setPage(1); }}
        status={status}
        onStatusChange={(val) => { setStatus(val); setPage(1); }}
        priority={priority}
        onPriorityChange={(val) => { setPriority(val); setPage(1); }}
        categoryId={categoryId}
        onCategoryChange={(val) => { setCategoryId(val); setPage(1); }}
        isSlaBreached={isSlaBreached}
        onSlaBreachedChange={(val) => { setIsSlaBreached(val); setPage(1); }}
        categories={categories}
        onReset={handleReset}
      />

      {/* Complaint Cards List */}
      {loading ? (
        <div className="p-8 text-center text-sm text-slate-400">Searching complaints database...</div>
      ) : complaints.length === 0 ? (
        <div className="bg-white rounded-2xl border border-slate-200 p-8 text-center text-sm text-slate-500">
          No complaints match the specified search filters.
        </div>
      ) : (
        <div className="space-y-3">
          {complaints.map((c) => (
            <ComplaintCard key={c.id} complaint={c} />
          ))}
        </div>
      )}

      {/* Pagination Footer */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between bg-white px-4 py-3 border border-slate-200 rounded-xl">
          <span className="text-xs text-slate-500">
            Page <strong className="text-slate-800">{page}</strong> of <strong className="text-slate-800">{totalPages}</strong>
          </span>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              disabled={page === 1}
              className="p-1.5 border border-slate-300 rounded-lg hover:bg-slate-50 disabled:opacity-40 text-slate-600"
            >
              <ChevronLeft className="w-4 h-4" />
            </button>
            <button
              onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
              disabled={page === totalPages}
              className="p-1.5 border border-slate-300 rounded-lg hover:bg-slate-50 disabled:opacity-40 text-slate-600"
            >
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
