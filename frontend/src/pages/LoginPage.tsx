import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate, Link } from 'react-router-dom';
import { LogIn, Lock, Mail, ShieldAlert } from 'lucide-react';

export const LoginPage: React.FC = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const { login, isLoading } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    try {
      await login(email, password);
      navigate('/');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Invalid email or password');
    }
  };

  const handleDemoLogin = async (demoEmail: string) => {
    setEmail(demoEmail);
    setPassword('Password123!');
    try {
      await login(demoEmail, 'Password123!');
      navigate('/');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Demo login failed');
    }
  };

  return (
    <div className="min-h-screen bg-slate-100 flex items-center justify-center p-4">
      <div className="w-full max-w-md bg-white rounded-2xl shadow-xl border border-slate-200 p-8 space-y-6">
        <div className="text-center space-y-2">
          <div className="inline-flex bg-sky-600 text-white font-black text-2xl px-3 py-1 rounded-xl tracking-tight mb-2">
            CF
          </div>
          <h1 className="text-2xl font-extrabold text-slate-900">Sign in to CampusFlow</h1>
          <p className="text-xs text-slate-500">
            University Facility Service Request & Management Platform
          </p>
        </div>

        {error && (
          <div className="bg-rose-50 border border-rose-200 text-rose-700 text-xs p-3 rounded-xl flex items-center gap-2">
            <ShieldAlert className="w-4 h-4 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">Email Address</label>
            <div className="relative">
              <Mail className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="user@campusflow.edu"
                className="w-full pl-9 pr-4 py-2.5 text-sm border border-slate-300 rounded-xl focus:ring-2 focus:ring-sky-500 outline-none"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">Password</label>
            <div className="relative">
              <Lock className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className="w-full pl-9 pr-4 py-2.5 text-sm border border-slate-300 rounded-xl focus:ring-2 focus:ring-sky-500 outline-none"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="w-full py-3 bg-sky-600 hover:bg-sky-700 text-white font-bold text-sm rounded-xl transition-colors shadow-sm disabled:opacity-50"
          >
            {isLoading ? 'Signing in...' : 'Sign In'}
          </button>
        </form>

        <div className="pt-4 border-t border-slate-100 space-y-3">
          <p className="text-[11px] font-bold text-slate-400 uppercase tracking-wider text-center">
            One-Click Demo Roles
          </p>
          <div className="grid grid-cols-2 gap-2 text-xs">
            <button
              onClick={() => handleDemoLogin('student@campusflow.edu')}
              className="p-2 border border-slate-200 rounded-lg hover:bg-blue-50 hover:border-blue-300 text-slate-700 font-semibold text-center transition-colors"
            >
              🎓 Student
            </button>
            <button
              onClick={() => handleDemoLogin('staff.electrical@campusflow.edu')}
              className="p-2 border border-slate-200 rounded-lg hover:bg-amber-50 hover:border-amber-300 text-slate-700 font-semibold text-center transition-colors"
            >
              🔧 Staff
            </button>
            <button
              onClick={() => handleDemoLogin('admin@campusflow.edu')}
              className="p-2 border border-slate-200 rounded-lg hover:bg-purple-50 hover:border-purple-300 text-slate-700 font-semibold text-center transition-colors"
            >
              📊 Admin
            </button>
            <button
              onClick={() => handleDemoLogin('superadmin@campusflow.edu')}
              className="p-2 border border-slate-200 rounded-lg hover:bg-rose-50 hover:border-rose-300 text-slate-700 font-semibold text-center transition-colors"
            >
              👑 Super Admin
            </button>
          </div>
        </div>

        <p className="text-center text-xs text-slate-500">
          Don't have an account?{' '}
          <Link to="/register" className="font-bold text-sky-600 hover:underline">
            Register here
          </Link>
        </p>
      </div>
    </div>
  );
};
