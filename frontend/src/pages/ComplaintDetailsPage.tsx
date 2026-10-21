import React, { useEffect, useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Complaint } from '../types';
import api from '../services/api';
import { StatusBadge } from '../components/common/StatusBadge';
import { PriorityBadge } from '../components/common/PriorityBadge';
import { Timeline } from '../components/common/Timeline';
import { CommentSection } from '../components/complaints/CommentSection';
import { AttachmentUploader } from '../components/complaints/AttachmentUploader';
import { AssignStaffModal } from '../components/admin/AssignStaffModal';
import { Modal } from '../components/common/Modal';
import {
  ArrowLeft,
  MapPin,
  Clock,
  UserCheck,
  CheckCircle2,
  XCircle,
  RotateCcw,
  Star,
  Play,
  FileCheck,
  AlertTriangle,
} from 'lucide-react';

export const ComplaintDetailsPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { user } = useAuth();
  const [complaint, setComplaint] = useState<Complaint | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Modals
  const [isAssignModalOpen, setIsAssignModalOpen] = useState(false);
  const [isResolveModalOpen, setIsResolveModalOpen] = useState(false);
  const [isRatingModalOpen, setIsRatingModalOpen] = useState(false);
  const [isReopenModalOpen, setIsReopenModalOpen] = useState(false);

  // Form states
  const [resolutionNotes, setResolutionNotes] = useState('');
  const [reopenReason, setReopenReason] = useState('');
  const [ratingScore, setRatingScore] = useState(5);
  const [ratingFeedback, setRatingFeedback] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const fetchComplaintDetails = () => {
    if (!id) return;
    setLoading(true);
    api.get<Complaint>(`/complaints/${id}`)
      .then((res) => setComplaint(res.data))
      .catch((err: any) => setError(err.response?.data?.detail || 'Failed to load complaint details'))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchComplaintDetails();
  }, [id]);

  if (loading) {
    return <div className="p-8 text-center text-sm text-slate-400">Loading complaint details...</div>;
  }

  if (error || !complaint) {
    return (
      <div className="bg-white rounded-2xl border border-slate-200 p-8 text-center space-y-4">
        <p className="text-sm font-semibold text-rose-600">{error || 'Complaint not found'}</p>
        <Link to="/complaints" className="inline-flex items-center gap-1 text-xs font-bold text-sky-600">
          <ArrowLeft className="w-3.5 h-3.5" /> Back to Complaints
        </Link>
      </div>
    );
  }

  const isStudent = user?.role === 'STUDENT';
  const isStaff = user?.role === 'STAFF';
  const isAdmin = user?.role === 'ADMIN' || user?.role === 'SUPER_ADMIN';

  const isCreator = user?.id === complaint.creator.id;
  const isAssignedStaff = user?.id === complaint.assigned_staff?.id;

  // Status transitions handlers
  const handleStartWork = async () => {
    try {
      await api.patch(`/complaints/${complaint.id}/status`, {
        target_status: 'IN_PROGRESS',
        comment: 'Staff started working on issue',
      });
      fetchComplaintDetails();
    } catch (err) {
      console.error(err);
    }
  };

  const handleResolveSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!resolutionNotes.trim()) return;

    setIsSubmitting(true);
    try {
      await api.patch(`/complaints/${complaint.id}/status`, {
        target_status: 'RESOLVED',
        resolution_notes: resolutionNotes.trim(),
        comment: resolutionNotes.trim(),
      });
      setIsResolveModalOpen(false);
      setResolutionNotes('');
      fetchComplaintDetails();
    } catch (err) {
      console.error(err);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleCloseComplaint = async () => {
    try {
      await api.patch(`/complaints/${complaint.id}/status`, {
        target_status: 'CLOSED',
        comment: 'Student confirmed resolution and closed complaint',
      });
      fetchComplaintDetails();
    } catch (err) {
      console.error(err);
    }
  };

  const handleReopenSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!reopenReason.trim()) return;

    setIsSubmitting(true);
    try {
      await api.patch(`/complaints/${complaint.id}/status`, {
        target_status: 'REOPENED',
        comment: `Complaint reopened by student: ${reopenReason.trim()}`,
      });
      setIsReopenModalOpen(false);
      setReopenReason('');
      fetchComplaintDetails();
    } catch (err) {
      console.error(err);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleRatingSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    try {
      await api.post(`/complaints/${complaint.id}/rating`, {
        score: ratingScore,
        feedback: ratingFeedback.trim() || undefined,
      });
      setIsRatingModalOpen(false);
      fetchComplaintDetails();
    } catch (err) {
      console.error(err);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Top Bar Navigation */}
      <div className="flex items-center justify-between">
        <button
          onClick={() => navigate(-1)}
          className="inline-flex items-center gap-1 text-xs font-bold text-slate-500 hover:text-slate-900 transition-colors"
        >
          <ArrowLeft className="w-4 h-4" /> Back
        </button>

        {/* Action Toolbar */}
        <div className="flex flex-wrap items-center gap-2">
          {isAdmin && (
            <button
              onClick={() => setIsAssignModalOpen(true)}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-purple-600 hover:bg-purple-700 text-white font-bold text-xs rounded-lg transition-colors shadow-sm"
            >
              <UserCheck className="w-3.5 h-3.5" />
              {complaint.assigned_staff ? 'Reassign Staff' : 'Assign Staff'}
            </button>
          )}

          {(isStaff || isAdmin) && complaint.status === 'ASSIGNED' && (
            <button
              onClick={handleStartWork}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-amber-500 hover:bg-amber-600 text-white font-bold text-xs rounded-lg transition-colors shadow-sm"
            >
              <Play className="w-3.5 h-3.5" /> Start Work
            </button>
          )}

          {(isStaff || isAdmin) && (complaint.status === 'IN_PROGRESS' || complaint.status === 'ASSIGNED') && (
            <button
              onClick={() => setIsResolveModalOpen(true)}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-xs rounded-lg transition-colors shadow-sm"
            >
              <CheckCircle2 className="w-3.5 h-3.5" /> Mark Resolved
            </button>
          )}

          {(isCreator || isAdmin) && complaint.status === 'RESOLVED' && (
            <>
              <button
                onClick={handleCloseComplaint}
                className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-slate-700 hover:bg-slate-800 text-white font-bold text-xs rounded-lg transition-colors shadow-sm"
              >
                <FileCheck className="w-3.5 h-3.5" /> Confirm & Close
              </button>

              <button
                onClick={() => setIsReopenModalOpen(true)}
                className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-orange-600 hover:bg-orange-700 text-white font-bold text-xs rounded-lg transition-colors shadow-sm"
              >
                <RotateCcw className="w-3.5 h-3.5" /> Reopen Complaint
              </button>
            </>
          )}

          {isCreator && (complaint.status === 'RESOLVED' || complaint.status === 'CLOSED') && !complaint.rating && (
            <button
              onClick={() => setIsRatingModalOpen(true)}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-amber-500 hover:bg-amber-600 text-white font-bold text-xs rounded-lg transition-colors shadow-sm"
            >
              <Star className="w-3.5 h-3.5 fill-white" /> Rate Service
            </button>
          )}
        </div>
      </div>

      {/* Main Header Card */}
      <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm space-y-4">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div className="flex items-center gap-2">
            <span className="font-mono font-bold text-sm bg-slate-100 text-slate-700 px-2.5 py-1 rounded">
              {complaint.complaint_number}
            </span>
            <StatusBadge status={complaint.status} size="lg" />
            <PriorityBadge priority={complaint.priority} />
            {complaint.is_sla_breached && (
              <span className="inline-flex items-center gap-1 text-xs font-bold text-rose-600 bg-rose-50 px-2.5 py-1 rounded border border-rose-200">
                <AlertTriangle className="w-3.5 h-3.5" /> SLA Breached
              </span>
            )}
          </div>
          <span className="text-xs text-slate-400 font-medium">
            Submitted {new Date(complaint.created_at).toLocaleString()}
          </span>
        </div>

        <h1 className="text-xl sm:text-2xl font-extrabold text-slate-900">{complaint.title}</h1>
        <p className="text-sm text-slate-700 whitespace-pre-line leading-relaxed bg-slate-50 p-4 rounded-xl border border-slate-100">
          {complaint.description}
        </p>

        {/* Location & Metadata Details */}
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4 text-xs pt-2">
          <div className="space-y-0.5">
            <span className="text-slate-400 font-medium">Category</span>
            <p className="font-bold text-slate-800">{complaint.category.name}</p>
          </div>

          <div className="space-y-0.5">
            <span className="text-slate-400 font-medium">Location</span>
            <p className="font-bold text-slate-800 flex items-center gap-1">
              <MapPin className="w-3.5 h-3.5 text-slate-500 shrink-0" />
              Room {complaint.location.room_number} ({complaint.location.room_type})
            </p>
            {complaint.specific_location_details && (
              <p className="text-[11px] text-slate-500 italic">{complaint.specific_location_details}</p>
            )}
          </div>

          <div className="space-y-0.5">
            <span className="text-slate-400 font-medium">Assigned Technician</span>
            <p className="font-bold text-slate-800">
              {complaint.assigned_staff ? complaint.assigned_staff.full_name : 'Unassigned'}
            </p>
          </div>

          <div className="space-y-0.5">
            <span className="text-slate-400 font-medium">SLA Deadline</span>
            <p className="font-bold text-slate-800 flex items-center gap-1">
              <Clock className="w-3.5 h-3.5 text-slate-500 shrink-0" />
              {new Date(complaint.sla_deadline).toLocaleString()}
            </p>
          </div>
        </div>

        {/* Resolution Notes section if present */}
        {complaint.resolution_notes && (
          <div className="mt-4 p-4 bg-emerald-50 border border-emerald-200 rounded-xl space-y-1">
            <span className="text-xs font-bold uppercase tracking-wider text-emerald-800 flex items-center gap-1">
              <CheckCircle2 className="w-4 h-4" /> Resolution Notes
            </span>
            <p className="text-sm text-emerald-900 font-medium">{complaint.resolution_notes}</p>
          </div>
        )}

        {/* Service Rating Display */}
        {complaint.rating && (
          <div className="p-4 bg-amber-50 border border-amber-200 rounded-xl space-y-1">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold uppercase tracking-wider text-amber-800">
                Student Satisfaction Rating
              </span>
              <div className="flex items-center gap-1 text-amber-500">
                {[1, 2, 3, 4, 5].map((star) => (
                  <Star
                    key={star}
                    className={`w-4 h-4 ${star <= complaint.rating!.score ? 'fill-amber-400' : 'text-slate-300'}`}
                  />
                ))}
              </div>
            </div>
            {complaint.rating.feedback && (
              <p className="text-xs text-amber-900 italic">"{complaint.rating.feedback}"</p>
            )}
          </div>
        )}
      </div>

      {/* Grid containing Attachments, Comments, and Timeline */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm">
            <AttachmentUploader
              complaintId={complaint.id}
              attachments={complaint.attachments || []}
              onAttachmentUploaded={fetchComplaintDetails}
              readOnly={complaint.status === 'CLOSED'}
            />
          </div>

          <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm">
            <CommentSection
              complaintId={complaint.id}
              comments={complaint.comments || []}
              onCommentAdded={fetchComplaintDetails}
            />
          </div>
        </div>

        <div>
          <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm space-y-4">
            <h3 className="text-base font-bold text-slate-900 border-b border-slate-200 pb-2">
              Status & Audit History
            </h3>
            <Timeline history={complaint.status_history || []} />
          </div>
        </div>
      </div>

      {/* Assign Staff Modal */}
      <AssignStaffModal
        isOpen={isAssignModalOpen}
        onClose={() => setIsAssignModalOpen(false)}
        complaintId={complaint.id}
        currentStaffId={complaint.assigned_staff?.id}
        onAssigned={fetchComplaintDetails}
      />

      {/* Resolve Modal */}
      <Modal isOpen={isResolveModalOpen} onClose={() => setIsResolveModalOpen(false)} title="Mark Complaint Resolved">
        <form onSubmit={handleResolveSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">
              Resolution Notes (Required)
            </label>
            <textarea
              rows={4}
              required
              placeholder="Describe work completed, components replaced, or troubleshooting results..."
              value={resolutionNotes}
              onChange={(e) => setResolutionNotes(e.target.value)}
              className="w-full text-sm border border-slate-300 rounded-lg p-2.5 focus:ring-2 focus:ring-sky-500 outline-none resize-none"
            />
          </div>
          <div className="flex justify-end gap-2">
            <button
              type="button"
              onClick={() => setIsResolveModalOpen(false)}
              className="px-4 py-2 text-xs font-semibold text-slate-600 bg-slate-100 hover:bg-slate-200 rounded-lg"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSubmitting || !resolutionNotes.trim()}
              className="px-4 py-2 text-xs font-semibold text-white bg-emerald-600 hover:bg-emerald-700 rounded-lg disabled:opacity-50"
            >
              {isSubmitting ? 'Resolving...' : 'Confirm Resolution'}
            </button>
          </div>
        </form>
      </Modal>

      {/* Reopen Modal */}
      <Modal isOpen={isReopenModalOpen} onClose={() => setIsReopenModalOpen(false)} title="Reopen Complaint">
        <form onSubmit={handleReopenSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">
              Reason for Reopening (Required)
            </label>
            <textarea
              rows={3}
              required
              placeholder="Explain why the resolution was unsatisfactory or problem persisted..."
              value={reopenReason}
              onChange={(e) => setReopenReason(e.target.value)}
              className="w-full text-sm border border-slate-300 rounded-lg p-2.5 focus:ring-2 focus:ring-sky-500 outline-none resize-none"
            />
          </div>
          <div className="flex justify-end gap-2">
            <button
              type="button"
              onClick={() => setIsReopenModalOpen(false)}
              className="px-4 py-2 text-xs font-semibold text-slate-600 bg-slate-100 hover:bg-slate-200 rounded-lg"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSubmitting || !reopenReason.trim()}
              className="px-4 py-2 text-xs font-semibold text-white bg-orange-600 hover:bg-orange-700 rounded-lg disabled:opacity-50"
            >
              {isSubmitting ? 'Reopening...' : 'Confirm Reopen'}
            </button>
          </div>
        </form>
      </Modal>

      {/* Rating Modal */}
      <Modal isOpen={isRatingModalOpen} onClose={() => setIsRatingModalOpen(false)} title="Rate Service Quality">
        <form onSubmit={handleRatingSubmit} className="space-y-4 text-center">
          <p className="text-xs text-slate-500">How satisfied are you with the maintenance resolution?</p>
          <div className="flex justify-center gap-2">
            {[1, 2, 3, 4, 5].map((star) => (
              <button
                key={star}
                type="button"
                onClick={() => setRatingScore(star)}
                className="p-1 text-amber-400 hover:scale-110 transition-transform"
              >
                <Star className={`w-7 h-7 ${star <= ratingScore ? 'fill-amber-400' : 'text-slate-300'}`} />
              </button>
            ))}
          </div>

          <textarea
            rows={3}
            placeholder="Optional feedback..."
            value={ratingFeedback}
            onChange={(e) => setRatingFeedback(e.target.value)}
            className="w-full text-sm border border-slate-300 rounded-lg p-2.5 focus:ring-2 focus:ring-sky-500 outline-none resize-none text-left"
          />

          <div className="flex justify-end gap-2 pt-2">
            <button
              type="button"
              onClick={() => setIsRatingModalOpen(false)}
              className="px-4 py-2 text-xs font-semibold text-slate-600 bg-slate-100 hover:bg-slate-200 rounded-lg"
            >
              Skip
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className="px-4 py-2 text-xs font-semibold text-white bg-sky-600 hover:bg-sky-700 rounded-lg disabled:opacity-50"
            >
              Submit Rating
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
};
