import React, { useEffect, useState } from 'react';
import { StatCard } from '../components/common/StatCard';
import { AnalyticsDashboardData } from '../types';
import api from '../services/api';
import {
  BarChart3,
  CheckCircle2,
  Clock,
  AlertTriangle,
  FileText,
  Users,
  Building,
  RefreshCw,
} from 'lucide-react';
import { Link } from 'react-router-dom';

export const AdminDashboard: React.FC = () => {
  const [data, setData] = useState<AnalyticsDashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [isScanningSla, setIsScanningSla] = useState(false);

  const fetchAnalytics = () => {
    setLoading(true);
    api.get<AnalyticsDashboardData>('/analytics/dashboard')
      .then((res) => setData(res.data))
      .catch((err) => console.error(err))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchAnalytics();
  }, []);

  const handleTriggerSlaScan = async () => {
    setIsScanningSla(true);
    try {
      await api.post('/sla/trigger-check');
      fetchAnalytics();
    } catch (err) {
      console.error(err);
    } finally {
      setIsScanningSla(false);
    }
  };

  if (loading || !data) {
    return <div className="p-8 text-center text-sm text-slate-400">Loading analytics engine...</div>;
  }

  const { kpi } = data;

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-extrabold text-slate-900">Admin Analytics & Operations Center</h1>
          <p className="text-xs text-slate-500 mt-1">
            Real-time university facility request metrics, staff load distribution, and SLA monitoring.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={handleTriggerSlaScan}
            disabled={isScanningSla}
            className="inline-flex items-center gap-1.5 px-3 py-2 text-xs font-bold text-slate-700 bg-white border border-slate-300 hover:bg-slate-50 rounded-xl transition-colors shadow-sm disabled:opacity-50"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isScanningSla ? 'animate-spin' : ''}`} />
            Scan SLA Breaches
          </button>
          <Link
            to="/complaints"
            className="inline-flex items-center gap-1.5 px-4 py-2 text-xs font-bold text-white bg-sky-600 hover:bg-sky-700 rounded-xl transition-colors shadow-sm"
          >
            Manage Complaints
          </Link>
        </div>
      </div>

      {/* KPI Overview Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard title="Total Complaints" value={kpi.total_complaints} icon={FileText} color="blue" />
        <StatCard title="Open / Unassigned" value={kpi.open_complaints} icon={Clock} color="amber" />
        <StatCard title="SLA Breached" value={kpi.sla_breached_complaints} icon={AlertTriangle} color="rose" />
        <StatCard
          title="Resolution Rate"
          value={`${kpi.resolution_rate_percent}%`}
          subtitle={`Avg ${kpi.avg_resolution_time_hours} hrs`}
          icon={CheckCircle2}
          color="emerald"
        />
      </div>

      {/* Breakdown Charts & Tables */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Category Breakdown */}
        <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm space-y-4">
          <h3 className="text-sm font-bold text-slate-800 flex items-center gap-2">
            <BarChart3 className="w-4 h-4 text-sky-600" />
            Complaints by Category
          </h3>
          <div className="space-y-2.5">
            {data.by_category.map((item) => (
              <div key={item.category_name} className="space-y-1">
                <div className="flex justify-between text-xs font-semibold">
                  <span className="text-slate-700">{item.category_name}</span>
                  <span className="text-slate-500">{item.count}</span>
                </div>
                <div className="w-full bg-slate-100 rounded-full h-2 overflow-hidden">
                  <div
                    className="bg-sky-500 h-2 rounded-full transition-all"
                    style={{
                      width: `${kpi.total_complaints > 0 ? (item.count / kpi.total_complaints) * 100 : 0}%`,
                    }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Location Breakdown */}
        <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm space-y-4">
          <h3 className="text-sm font-bold text-slate-800 flex items-center gap-2">
            <Building className="w-4 h-4 text-purple-600" />
            Complaints by Building
          </h3>
          <div className="space-y-2.5">
            {data.by_location.map((item) => (
              <div key={item.building_name} className="space-y-1">
                <div className="flex justify-between text-xs font-semibold">
                  <span className="text-slate-700">{item.building_name}</span>
                  <span className="text-slate-500">{item.count}</span>
                </div>
                <div className="w-full bg-slate-100 rounded-full h-2 overflow-hidden">
                  <div
                    className="bg-purple-500 h-2 rounded-full transition-all"
                    style={{
                      width: `${kpi.total_complaints > 0 ? (item.count / kpi.total_complaints) * 100 : 0}%`,
                    }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Priority Breakdown */}
        <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm space-y-4">
          <h3 className="text-sm font-bold text-slate-800 flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 text-amber-600" />
            Complaints by Priority
          </h3>
          <div className="space-y-2.5">
            {data.by_priority.map((item) => (
              <div key={item.priority} className="space-y-1">
                <div className="flex justify-between text-xs font-semibold">
                  <span className="text-slate-700">{item.priority}</span>
                  <span className="text-slate-500">{item.count}</span>
                </div>
                <div className="w-full bg-slate-100 rounded-full h-2 overflow-hidden">
                  <div
                    className={`h-2 rounded-full transition-all ${
                      item.priority === 'CRITICAL'
                        ? 'bg-rose-500'
                        : item.priority === 'HIGH'
                        ? 'bg-amber-500'
                        : 'bg-blue-500'
                    }`}
                    style={{
                      width: `${kpi.total_complaints > 0 ? (item.count / kpi.total_complaints) * 100 : 0}%`,
                    }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Staff Workload Table */}
      <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm space-y-4">
        <h3 className="text-sm font-bold text-slate-800 flex items-center gap-2">
          <Users className="w-4 h-4 text-emerald-600" />
          Maintenance Staff Workload & Performance
        </h3>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50 border-b border-slate-200 text-slate-500 uppercase font-semibold">
              <tr>
                <th className="p-3">Staff Member</th>
                <th className="p-3">Pending Assigned</th>
                <th className="p-3">In Progress</th>
                <th className="p-3">Completed</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 text-slate-700 font-medium">
              {data.staff_workload.map((staff) => (
                <tr key={staff.staff_id} className="hover:bg-slate-50">
                  <td className="p-3 font-semibold text-slate-900">{staff.staff_name}</td>
                  <td className="p-3">
                    <span className="px-2 py-0.5 bg-purple-50 text-purple-700 font-bold rounded">
                      {staff.assigned_count}
                    </span>
                  </td>
                  <td className="p-3">
                    <span className="px-2 py-0.5 bg-amber-50 text-amber-700 font-bold rounded">
                      {staff.in_progress_count}
                    </span>
                  </td>
                  <td className="p-3">
                    <span className="px-2 py-0.5 bg-emerald-50 text-emerald-700 font-bold rounded">
                      {staff.resolved_count}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
