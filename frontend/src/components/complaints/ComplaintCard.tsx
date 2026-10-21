import React from 'react';
import { ComplaintListItem } from '../../types';
import { StatusBadge } from '../common/StatusBadge';
import { PriorityBadge } from '../common/PriorityBadge';
import { MapPin, Clock, AlertTriangle, ChevronRight } from 'lucide-react';
import { Link } from 'react-router-dom';

interface ComplaintCardProps {
  complaint: ComplaintListItem;
}

export const ComplaintCard: React.FC<ComplaintCardProps> = ({ complaint }) => {
  const isExpired = new Date(complaint.sla_deadline) < new Date() && complaint.status !== 'RESOLVED' && complaint.status !== 'CLOSED';

  return (
    <Link
      to={`/complaints/${complaint.id}`}
      className="block bg-white rounded-xl border border-slate-200 p-5 hover:border-sky-300 hover:shadow-md transition-all group"
    >
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div className="flex items-center gap-2">
          <span className="text-xs font-bold text-slate-500 bg-slate-100 px-2 py-0.5 rounded font-mono">
            {complaint.complaint_number}
          </span>
          <StatusBadge status={complaint.status} size="sm" />
          <PriorityBadge priority={complaint.priority} />
          {complaint.is_sla_breached && (
            <span className="inline-flex items-center gap-1 text-[11px] font-bold text-rose-600 bg-rose-50 px-2 py-0.5 rounded border border-rose-200">
              <AlertTriangle className="w-3 h-3" /> SLA Breached
            </span>
          )}
        </div>
        <span className="text-xs text-slate-400 font-medium">
          Created {new Date(complaint.created_at).toLocaleDateString()}
        </span>
      </div>

      <h3 className="text-base font-bold text-slate-900 mt-2 group-hover:text-sky-600 transition-colors flex items-center justify-between">
        {complaint.title}
        <ChevronRight className="w-4 h-4 text-slate-400 group-hover:translate-x-1 transition-transform" />
      </h3>

      <div className="mt-3 grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-2 text-xs text-slate-600">
        <div className="flex items-center gap-1.5 truncate">
          <span className="font-medium text-slate-500">Category:</span>
          <span className="font-semibold text-slate-700">{complaint.category.name}</span>
        </div>
        <div className="flex items-center gap-1.5 truncate">
          <MapPin className="w-3.5 h-3.5 text-slate-400 shrink-0" />
          <span className="truncate">
            {complaint.location.building_name || 'Building'}, Room {complaint.location.room_number}
          </span>
        </div>
        <div className="flex items-center gap-1.5 truncate">
          <Clock className={`w-3.5 h-3.5 shrink-0 ${isExpired ? 'text-rose-500' : 'text-slate-400'}`} />
          <span className={isExpired ? 'text-rose-600 font-bold' : ''}>
            SLA: {new Date(complaint.sla_deadline).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', month: 'short', day: 'numeric' })}
          </span>
        </div>
      </div>

      {complaint.assigned_staff && (
        <div className="mt-3 pt-3 border-t border-slate-100 flex items-center justify-between text-xs text-slate-500">
          <span>Assigned Staff: <strong className="text-slate-700">{complaint.assigned_staff.full_name}</strong></span>
          <span className="text-slate-400">Student: {complaint.creator.full_name}</span>
        </div>
      )}
    </Link>
  );
};
