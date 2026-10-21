import React from 'react';
import { NavLink } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import {
  LayoutDashboard,
  PlusCircle,
  FileText,
  ClipboardList,
  BarChart3,
  Users,
  Layers,
  MapPin,
} from 'lucide-react';

export const Sidebar: React.FC = () => {
  const { user } = useAuth();
  if (!user) return null;

  const isStudent = user.role === 'STUDENT';
  const isStaff = user.role === 'STAFF';
  const isAdmin = user.role === 'ADMIN' || user.role === 'SUPER_ADMIN';

  const linkClass = ({ isActive }: { isActive: boolean }) =>
    `flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-xs font-semibold transition-all ${
      isActive
        ? 'bg-sky-600 text-white shadow-sm'
        : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
    }`;

  return (
    <aside className="w-64 bg-white border-r border-slate-200 hidden md:flex flex-col min-h-[calc(100vh-61px)] p-4 space-y-6">
      <div>
        <p className="px-3 text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-2">
          Dashboard View
        </p>
        <nav className="space-y-1">
          {isStudent && (
            <NavLink to="/" end className={linkClass}>
              <LayoutDashboard className="w-4 h-4" />
              Student Portal
            </NavLink>
          )}

          {isStaff && (
            <NavLink to="/" end className={linkClass}>
              <LayoutDashboard className="w-4 h-4" />
              Staff Workbench
            </NavLink>
          )}

          {isAdmin && (
            <NavLink to="/" end className={linkClass}>
              <BarChart3 className="w-4 h-4" />
              Admin Command Center
            </NavLink>
          )}
        </nav>
      </div>

      <div>
        <p className="px-3 text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-2">
          Complaints
        </p>
        <nav className="space-y-1">
          {isStudent && (
            <NavLink to="/create-complaint" className={linkClass}>
              <PlusCircle className="w-4 h-4" />
              Submit Complaint
            </NavLink>
          )}

          <NavLink to="/complaints" className={linkClass}>
            <FileText className="w-4 h-4" />
            {isStudent ? 'My Complaints' : 'All Complaints'}
          </NavLink>
        </nav>
      </div>

      {isAdmin && (
        <div>
          <p className="px-3 text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-2">
            System Admin
          </p>
          <nav className="space-y-1">
            <NavLink to="/admin/users" className={linkClass}>
              <Users className="w-4 h-4" />
              Manage Users
            </NavLink>
          </nav>
        </div>
      )}

      <div className="mt-auto pt-4 border-t border-slate-100">
        <div className="bg-slate-50 p-3 rounded-xl border border-slate-200">
          <p className="text-[11px] font-bold text-slate-700">CampusFlow Support</p>
          <p className="text-[10px] text-slate-500 mt-0.5">SLA response guaranteed within configured hours.</p>
        </div>
      </div>
    </aside>
  );
};
