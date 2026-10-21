import React, { useState, useEffect } from 'react';
import { Modal } from '../common/Modal';
import { User } from '../../types';
import api from '../../services/api';
import { UserCheck } from 'lucide-react';

interface AssignStaffModalProps {
  isOpen: boolean;
  onClose: () => void;
  complaintId: string;
  currentStaffId?: string;
  onAssigned: () => void;
}

export const AssignStaffModal: React.FC<AssignStaffModalProps> = ({
  isOpen,
  onClose,
  complaintId,
  currentStaffId,
  onAssigned,
}) => {
  const [staffList, setStaffList] = useState<User[]>([]);
  const [selectedStaffId, setSelectedStaffId] = useState<string>(currentStaffId || '');
  const [notes, setNotes] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    if (isOpen) {
      api.get<User[]>('/users/staff').then((res) => {
        setStaffList(res.data);
        if (!selectedStaffId && res.data.length > 0) {
          setSelectedStaffId(res.data[0].id);
        }
      });
    }
  }, [isOpen]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedStaffId) return;

    setIsSubmitting(true);
    try {
      await api.post(`/complaints/${complaintId}/assign`, {
        staff_id: selectedStaffId,
        notes: notes.trim() || undefined,
      });
      onAssigned();
      onClose();
    } catch (err) {
      console.error('Assignment error', err);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Assign Maintenance Staff">
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-xs font-semibold text-slate-700 mb-1">
            Select Staff Member
          </label>
          <select
            value={selectedStaffId}
            onChange={(e) => setSelectedStaffId(e.target.value)}
            className="w-full text-sm border border-slate-300 rounded-lg p-2.5 focus:ring-2 focus:ring-sky-500 outline-none"
          >
            <option value="" disabled>-- Select Staff --</option>
            {staffList.map((staff) => (
              <option key={staff.id} value={staff.id}>
                {staff.full_name} ({staff.department || 'Maintenance'})
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-xs font-semibold text-slate-700 mb-1">
            Assignment Notes (Optional)
          </label>
          <textarea
            rows={3}
            placeholder="Special instructions or priority directions..."
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            className="w-full text-sm border border-slate-300 rounded-lg p-2.5 focus:ring-2 focus:ring-sky-500 outline-none resize-none"
          />
        </div>

        <div className="flex justify-end gap-2 pt-2">
          <button
            type="button"
            onClick={onClose}
            className="px-4 py-2 text-xs font-semibold text-slate-600 bg-slate-100 hover:bg-slate-200 rounded-lg transition-colors"
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={isSubmitting || !selectedStaffId}
            className="inline-flex items-center gap-1.5 px-4 py-2 text-xs font-semibold text-white bg-sky-600 hover:bg-sky-700 rounded-lg transition-colors disabled:opacity-50"
          >
            <UserCheck className="w-4 h-4" />
            {isSubmitting ? 'Assigning...' : 'Confirm Assignment'}
          </button>
        </div>
      </form>
    </Modal>
  );
};
