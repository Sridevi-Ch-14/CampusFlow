import React, { useState } from 'react';
import { Upload, FileText, Image as ImageIcon, Download, Trash2, CheckCircle } from 'lucide-react';
import { Attachment } from '../../types';
import api from '../../services/api';

interface AttachmentUploaderProps {
  complaintId: string;
  attachments: Attachment[];
  onAttachmentUploaded: () => void;
  readOnly?: boolean;
}

export const AttachmentUploader: React.FC<AttachmentUploaderProps> = ({
  complaintId,
  attachments,
  onAttachmentUploaded,
  readOnly = false,
}) => {
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (!files || files.length === 0) return;

    const file = files[0];
    if (file.size > 10 * 1024 * 1024) {
      setError('File size must be less than 10MB');
      return;
    }

    const formData = new FormData();
    formData.append('file', file);

    setIsUploading(true);
    setError(null);
    try {
      await api.post(`/complaints/${complaintId}/attachments`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      onAttachmentUploaded();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to upload attachment');
    } finally {
      setIsUploading(false);
      e.target.value = '';
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  return (
    <div className="space-y-4">
      <h3 className="text-base font-bold text-slate-900 border-b border-slate-200 pb-2">
        Attachments & Evidence ({attachments.length})
      </h3>

      {!readOnly && (
        <div>
          <label className="flex flex-col items-center justify-center p-4 border-2 border-dashed border-slate-300 rounded-xl hover:border-sky-500 hover:bg-sky-50/50 cursor-pointer transition-all">
            <Upload className="w-6 h-6 text-slate-400 mb-1" />
            <span className="text-xs font-semibold text-slate-700">
              Click to upload photo or document
            </span>
            <span className="text-[11px] text-slate-400 mt-0.5">
              JPG, PNG, WEBP, PDF, DOCX (Max 10MB)
            </span>
            <input
              type="file"
              onChange={handleFileChange}
              disabled={isUploading}
              className="hidden"
            />
          </label>
          {isUploading && (
            <p className="text-xs text-sky-600 font-semibold mt-2 animate-pulse">Uploading file...</p>
          )}
          {error && <p className="text-xs text-rose-600 font-semibold mt-2">{error}</p>}
        </div>
      )}

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        {attachments.map((att) => (
          <div
            key={att.id}
            className="flex items-center justify-between p-3 bg-slate-50 border border-slate-200 rounded-xl text-xs"
          >
            <div className="flex items-center gap-2 min-w-0">
              {att.mime_type.startsWith('image/') ? (
                <ImageIcon className="w-4 h-4 text-sky-600 shrink-0" />
              ) : (
                <FileText className="w-4 h-4 text-amber-600 shrink-0" />
              )}
              <div className="truncate">
                <p className="font-semibold text-slate-800 truncate">{att.original_filename}</p>
                <p className="text-[10px] text-slate-400">{formatFileSize(att.file_size)}</p>
              </div>
            </div>
            <a
              href={`/api/v1/attachments/${att.storage_key}`}
              target="_blank"
              rel="noreferrer"
              className="p-1.5 text-slate-500 hover:text-sky-600 hover:bg-slate-200 rounded-lg transition-colors ml-2"
              title="Download File"
            >
              <Download className="w-4 h-4" />
            </a>
          </div>
        ))}
      </div>
    </div>
  );
};
