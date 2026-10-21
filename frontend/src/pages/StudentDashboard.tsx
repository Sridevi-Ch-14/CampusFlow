import React, { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { StatCard } from '../components/common/StatCard';
import { ComplaintCard } from '../components/complaints/ComplaintCard';
import { ComplaintListItem } from '../types';
import api from '../services/api';
import { PlusCircle, FileText, Clock, CheckCircle2, AlertCircle } from 'lucide-react';
import { Link } from 'react-router-dom';

export const StudentDashboard: React.FC = () => {
  const { user } = useAuth();
  const [complaints, setComplaints] = useState<ComplaintListItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get<{ items: ComplaintListItem[] }>('/complaints?page_size=5')
      .then((res) => setComplaints(res.data.items))
      .catch((err) => console.error(err))
      .finally(() => setLoading(false));
  }, []);

  const totalCount = complaints.length;
  const openCount = complaints.filter((c) => c.status === 'OPEN').length;
  const inProgressCount = complaints.filter((c) => c.status === 'IN_PROGRESS' || c.status === 'ASSIGNED').length;
  const resolvedCount = complaints.filter((c) => c.status === 'RESOLVED' || c.status === 'CLOSED').length;

  return (
    <div className="space-y-6">
      {/* Header Banner */}
      <div className="bg-gradient-to-r from-sky-700 via-sky-800 to-slate-900 rounded-2xl p-6 sm:p-8 text-white shadow-lg flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <span className="text-xs font-bold uppercase tracking-wider text-sky-300">Student Service Desk</span>
          <h1 className="text-2xl sm:text-3xl font-extrabold mt-1">
            Welcome back, {user?.full_name.split(' ')[0]} 👋
          </h1>
          <p className="text-sm text-sky-100 mt-1 max-w-xl">
            Report facility issues across campus buildings, track maintenance status, and rate completed resolutions.
          </p>
        </div>
        <Link
          to="/create-complaint"
          className="inline-flex items-center justify-center gap-2 px-5 py-3 bg-white text-sky-800 font-extrabold text-sm rounded-xl hover:bg-sky-50 shadow-md transition-all shrink-0"
        >
          <PlusCircle className="w-5 h-5 text-sky-600" />
          Submit Complaint
        </Link>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard title="Total Submitted" value={totalCount} icon={FileText} color="blue" />
        <StatCard title="Pending Review" value={openCount} icon={AlertCircle} color="amber" />
        <StatCard title="Work In Progress" value={inProgressCount} icon={Clock} color="purple" />
        <StatCard title="Resolved Issues" value={resolvedCount} icon={CheckCircle2} color="emerald" />
      </div>

      {/* Recent Complaints Section */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-bold text-slate-900">Your Recent Service Requests</h2>
          <Link to="/complaints" className="text-xs font-bold text-sky-600 hover:text-sky-800">
            View All →
          </Link>
        </div>

        {loading ? (
          <div className="p-8 text-center text-sm text-slate-400">Loading complaints...</div>
        ) : complaints.length === 0 ? (
          <div className="bg-white rounded-2xl border border-slate-200 p-8 text-center space-y-3">
            <p className="text-sm font-semibold text-slate-600">No facility complaints reported yet.</p>
            <Link
              to="/create-complaint"
              className="inline-flex items-center gap-1.5 px-4 py-2 bg-sky-600 text-white font-bold text-xs rounded-xl"
            >
              Report First Problem
            </Link>
          </div>
        ) : (
          <div className="space-y-3">
            {complaints.map((c) => (
              <ComplaintCard key={c.id} complaint={c} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
