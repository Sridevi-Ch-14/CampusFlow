import React, { useState } from 'react';
import { Comment } from '../../types';
import { Send, User as UserIcon, ShieldAlert } from 'lucide-react';
import api from '../../services/api';

interface CommentSectionProps {
  complaintId: string;
  comments: Comment[];
  onCommentAdded: () => void;
}

export const CommentSection: React.FC<CommentSectionProps> = ({
  complaintId,
  comments,
  onCommentAdded,
}) => {
  const [content, setContent] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!content.trim()) return;

    setIsSubmitting(true);
    try {
      await api.post(`/complaints/${complaintId}/comments`, {
        content: content.trim(),
        is_internal: false,
      });
      setContent('');
      onCommentAdded();
    } catch (err) {
      console.error('Failed to post comment', err);
    } finally {
      setIsSubmitting(false);
    }
  };

  const roleBadges: Record<string, string> = {
    STUDENT: 'bg-blue-100 text-blue-700',
    STAFF: 'bg-amber-100 text-amber-800',
    ADMIN: 'bg-purple-100 text-purple-700',
    SUPER_ADMIN: 'bg-rose-100 text-rose-700',
  };

  return (
    <div className="space-y-6">
      <h3 className="text-base font-bold text-slate-900 border-b border-slate-200 pb-2">
        Discussion Thread ({comments.length})
      </h3>

      <div className="space-y-4 max-h-96 overflow-y-auto pr-1">
        {comments.length === 0 ? (
          <p className="text-sm text-slate-400 italic">No comments yet. Start a discussion below.</p>
        ) : (
          comments.map((comment) => (
            <div
              key={comment.id}
              className="bg-slate-50 rounded-xl p-4 border border-slate-200 text-sm space-y-2"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className="font-semibold text-slate-800 flex items-center gap-1">
                    <UserIcon className="w-3.5 h-3.5 text-slate-400" />
                    {comment.author.full_name}
                  </span>
                  <span
                    className={`px-2 py-0.5 text-[10px] font-bold uppercase rounded ${
                      roleBadges[comment.author.role] || 'bg-slate-100 text-slate-700'
                    }`}
                  >
                    {comment.author.role}
                  </span>
                </div>
                <span className="text-xs text-slate-400">
                  {new Date(comment.created_at).toLocaleString()}
                </span>
              </div>
              <p className="text-slate-700 whitespace-pre-line leading-relaxed">{comment.content}</p>
            </div>
          ))
        )}
      </div>

      <form onSubmit={handleSubmit} className="flex flex-col gap-2">
        <textarea
          rows={3}
          placeholder="Add a comment or update note..."
          value={content}
          onChange={(e) => setContent(e.target.value)}
          className="w-full p-3 text-sm border border-slate-300 rounded-xl focus:ring-2 focus:ring-sky-500 outline-none resize-none"
        />
        <div className="flex justify-end">
          <button
            type="submit"
            disabled={isSubmitting || !content.trim()}
            className="inline-flex items-center gap-2 px-4 py-2 bg-sky-600 hover:bg-sky-700 text-white font-semibold text-xs rounded-lg transition-colors disabled:opacity-50"
          >
            <Send className="w-3.5 h-3.5" />
            {isSubmitting ? 'Posting...' : 'Post Comment'}
          </button>
        </div>
      </form>
    </div>
  );
};
