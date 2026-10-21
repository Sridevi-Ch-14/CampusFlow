import React, { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { StatCard } from '../components/common/StatCard';
import { ComplaintCard } from '../components/complaints/ComplaintCard';
import { ComplaintListItem } from '../types';
import api from '../services/api';
import { Wrench, Clock, AlertTriangle, CheckCircle2, Play } from 'lucide-react';
import { Link } from 'react-router-dom';

export const StaffDashboard: React.FC = () => {
  const { user } = useAuth();
  const [complaints, setComplaints] = useState<ComplaintListItem[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchStaffComplaints = () => {
    setLoading(true);
    api.get<{ items: ComplaintListItem[] }>('/complaints?page_size=20')
      .then((res) => setComplaints(res.data.items))
      .catch((err) => console.error(err))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchStaffComplaints();
  }, []);

  const assignedCount = complaints.filter((c) => c.status === 'ASSIGNED').length;
  const inProgressCount = complaints.filter((c) => c.status === 'IN_PROGRESS').length;
  const breachedCount = complaints.filter((c) => c.is_sla_breached).length;
  const resolvedCount = complaints.filter((c) => c.status === 'RESOLVED' || c.status === 'CLOSED').length;

  const handleStartWork = async (id: string, e: React.MouseEvent) => {
    e.preventDefault();
    try {
      await api.patch(`/complaints/${id}/status`, {
        target_status: 'IN_PROGRESS',
        comment: 'Staff started working on facility issue',
      });
      fetchStaffComplaints();
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-extrabold text-slate-900">Maintenance Staff Workbench</h1>
          <p className="text-xs text-slate-500 mt-1">
            Logged in as <strong className="text-slate-800">{user?.full_name}</strong> ({user?.department || 'Maintenance'})
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard title="Assigned To You" value={assignedCount} icon={Wrench} color="purple" />
        <StatCard title="In Progress" value={inProgressCount} icon={Clock} color="amber" />
        <StatCard title="SLA Overdue" value={breachedCount} icon={AlertTriangle} color="rose" />
        <StatCard title="Resolved" value={resolvedCount} icon={CheckCircle2} color="emerald" />
      </div>

      <div className="space-y-4">
        <h2 className="text-lg font-bold text-slate-900">Assigned Complaints</h2>

        {loading ? (
          <div className="p-8 text-center text-sm text-slate-400">Loading assignments...</div>
        ) : complaints.length === 0 ? (
          <div className="bg-white rounded-2xl border border-slate-200 p-8 text-center text-sm text-slate-500">
            No active maintenance tasks assigned to you right now.
          </div>
        ) : (
          <div className="space-y-3">
            {complaints.map((c) => (
              <div key={c.id} className="relative">
                <ComplaintCard complaint={c} />
                {c.status === 'ASSIGNED' && (
                  <div className="mt-2 flex justify-end">
                    <button
                      onClick={(e) => handleStartWork(c.id, e)}
                      className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-amber-500 hover:bg-amber-600 text-white font-bold text-xs rounded-lg transition-colors shadow-sm"
                    >
                      <Play className="w-3.5 h-3.5" />
                      Start Work
                    </button>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
