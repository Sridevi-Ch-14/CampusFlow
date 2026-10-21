import React from 'react';
import { useAuth } from '../../context/AuthContext';
import { NotificationDropdown } from '../common/NotificationDropdown';
import { LogOut, User as UserIcon, ShieldCheck } from 'lucide-react';
import { Link } from 'react-router-dom';

export const Navbar: React.FC = () => {
  const { user, logout } = useAuth();

  const roleColors: Record<string, string> = {
    STUDENT: 'bg-blue-100 text-blue-800 border-blue-200',
    STAFF: 'bg-amber-100 text-amber-800 border-amber-200',
    ADMIN: 'bg-purple-100 text-purple-800 border-purple-200',
    SUPER_ADMIN: 'bg-rose-100 text-rose-800 border-rose-200',
  };

  return (
    <header className="sticky top-0 z-40 bg-white border-b border-slate-200 shadow-sm">
      <div className="flex items-center justify-between px-4 sm:px-6 py-3">
        <div className="flex items-center gap-3">
          <Link to="/" className="flex items-center gap-2">
            <div className="bg-sky-600 text-white font-black text-xl px-2.5 py-1 rounded-lg tracking-tight">
              CF
            </div>
            <div>
              <span className="text-lg font-extrabold text-slate-900 tracking-tight">Campus</span>
              <span className="text-lg font-extrabold text-sky-600 tracking-tight">Flow</span>
            </div>
          </Link>
          <span className="hidden md:inline-block text-xs text-slate-400 border-l border-slate-200 pl-3">
            Facility Complaint System
          </span>
        </div>

        {user && (
          <div className="flex items-center gap-3 sm:gap-4">
            <NotificationDropdown />

            <div className="h-6 w-px bg-slate-200 hidden sm:block" />

            <div className="flex items-center gap-2.5">
              <div className="w-8 h-8 rounded-full bg-slate-100 border border-slate-300 flex items-center justify-center text-slate-600 font-bold text-xs">
                {user.full_name.charAt(0).toUpperCase()}
              </div>
              <div className="hidden sm:block text-left">
                <p className="text-xs font-bold text-slate-800 leading-tight">{user.full_name}</p>
                <span
                  className={`inline-block px-1.5 py-0.2 text-[10px] font-bold rounded border ${
                    roleColors[user.role] || 'bg-slate-100 text-slate-700'
                  }`}
                >
                  {user.role}
                </span>
              </div>
            </div>

            <button
              onClick={logout}
              className="p-2 text-slate-500 hover:text-rose-600 hover:bg-rose-50 rounded-lg transition-colors"
              title="Logout"
            >
              <LogOut className="w-5 h-5" />
            </button>
          </div>
        )}
      </div>
    </header>
  );
};
