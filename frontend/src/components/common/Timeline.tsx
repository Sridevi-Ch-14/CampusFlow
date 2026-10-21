import React from 'react';
import { StatusHistory } from '../../types';
import { StatusBadge } from './StatusBadge';
import { Clock, User } from 'lucide-react';

interface TimelineProps {
  history: StatusHistory[];
}

export const Timeline: React.FC<TimelineProps> = ({ history }) => {
  if (!history || history.length === 0) {
    return <p className="text-sm text-slate-500 italic">No history records found.</p>;
  }

  return (
    <div className="flow-root">
      <ul role="list" className="-mb-8">
        {history.map((item, idx) => (
          <li key={item.id}>
            <div className="relative pb-8">
              {idx !== history.length - 1 ? (
                <span
                  className="absolute left-4 top-4 -ml-px h-full w-0.5 bg-slate-200"
                  aria-hidden="true"
                />
              ) : null}
              <div className="relative flex space-x-3 items-start">
                <div>
                  <span className="h-8 w-8 rounded-full bg-slate-100 border border-slate-300 flex items-center justify-center ring-8 ring-white">
                    <Clock className="h-4 w-4 text-slate-600" />
                  </span>
                </div>
                <div className="flex min-w-0 flex-1 justify-between space-x-4 pt-1.5">
                  <div>
                    <div className="flex items-center space-x-2">
                      <StatusBadge status={item.new_status} size="sm" />
                      <span className="text-xs text-slate-500 flex items-center gap-1">
                        <User className="w-3 h-3" />
                        {item.changed_by.full_name} ({item.changed_by.role})
                      </span>
                    </div>
                    {item.comment && (
                      <p className="mt-1 text-sm text-slate-700 bg-slate-50 p-2.5 rounded border border-slate-200">
                        {item.comment}
                      </p>
                    )}
                  </div>
                  <div className="whitespace-nowrap text-right text-xs text-slate-400">
                    {new Date(item.created_at).toLocaleString()}
                  </div>
                </div>
              </div>
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
};
