import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Category, Campus, Building, Floor, Room, Priority } from '../types';
import api from '../services/api';
import { ArrowLeft, Send, Upload, MapPin, Tag, ShieldAlert } from 'lucide-react';

export const CreateComplaintPage: React.FC = () => {
  const navigate = useNavigate();

  const [categories, setCategories] = useState<Category[]>([]);
  const [campuses, setCampuses] = useState<Campus[]>([]);

  // Selection states
  const [selectedCategoryId, setSelectedCategoryId] = useState('');
  const [selectedBuildingId, setSelectedBuildingId] = useState('');
  const [selectedFloorId, setSelectedFloorId] = useState('');
  const [selectedRoomId, setSelectedRoomId] = useState('');
  const [specificDetails, setSpecificDetails] = useState('');
  const [priority, setPriority] = useState<Priority | ''>('');
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');

  // Attachment
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([
      api.get<Category[]>('/categories'),
      api.get<Campus[]>('/locations/hierarchy'),
    ])
      .then(([catRes, locRes]) => {
        setCategories(catRes.data);
        setCampuses(locRes.data);
        if (catRes.data.length > 0) setSelectedCategoryId(catRes.data[0].id);
      })
      .catch((err) => console.error(err));
  }, []);

  const availableBuildings = campuses.flatMap((c) => c.buildings);
  const selectedBuilding = availableBuildings.find((b) => b.id === selectedBuildingId);
  const availableFloors = selectedBuilding ? selectedBuilding.floors : [];
  const selectedFloor = availableFloors.find((f) => f.id === selectedFloorId);
  const availableRooms = selectedFloor ? selectedFloor.rooms : [];

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedCategoryId || !selectedRoomId || !title.trim() || !description.trim()) {
      setError('Please fill in all required fields including location room.');
      return;
    }

    setLoading(true);
    setError(null);
    try {
      const complaintRes = await api.post('/complaints', {
        title: title.trim(),
        description: description.trim(),
        category_id: selectedCategoryId,
        location_id: selectedRoomId,
        specific_location_details: specificDetails.trim() || undefined,
        priority: priority || undefined,
      });

      const complaintId = complaintRes.data.id;

      if (selectedFile) {
        const formData = new FormData();
        formData.append('file', selectedFile);
        await api.post(`/complaints/${complaintId}/attachments`, formData, {
          headers: { 'Content-Type': 'multipart/form-data' },
        });
      }

      navigate(`/complaints/${complaintId}`);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to submit complaint');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <button
        onClick={() => navigate(-1)}
        className="inline-flex items-center gap-1 text-xs font-bold text-slate-500 hover:text-slate-900 transition-colors"
      >
        <ArrowLeft className="w-4 h-4" /> Cancel & Return
      </button>

      <div className="bg-white rounded-2xl border border-slate-200 p-6 sm:p-8 shadow-sm space-y-6">
        <div>
          <h1 className="text-2xl font-extrabold text-slate-900">Submit Campus Service Request</h1>
          <p className="text-xs text-slate-500 mt-1">
            Provide details of the facility problem for university maintenance triage.
          </p>
        </div>

        {error && (
          <div className="bg-rose-50 border border-rose-200 text-rose-700 text-xs p-3 rounded-xl flex items-center gap-2">
            <ShieldAlert className="w-4 h-4 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-5">
          {/* Title */}
          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">
              Issue Title <span className="text-rose-500">*</span>
            </label>
            <input
              type="text"
              required
              placeholder="e.g. Air conditioner leaking water in CS Lab 201"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              className="w-full text-sm border border-slate-300 rounded-xl p-3 focus:ring-2 focus:ring-sky-500 outline-none"
            />
          </div>

          {/* Category & Priority */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                Problem Category <span className="text-rose-500">*</span>
              </label>
              <select
                value={selectedCategoryId}
                onChange={(e) => setSelectedCategoryId(e.target.value)}
                className="w-full text-sm border border-slate-300 rounded-xl p-3 focus:ring-2 focus:ring-sky-500 outline-none bg-white"
              >
                {categories.map((cat) => (
                  <option key={cat.id} value={cat.id}>
                    {cat.name}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                Priority Override (Optional)
              </label>
              <select
                value={priority}
                onChange={(e) => setPriority(e.target.value as Priority)}
                className="w-full text-sm border border-slate-300 rounded-xl p-3 focus:ring-2 focus:ring-sky-500 outline-none bg-white"
              >
                <option value="">Use Category Default</option>
                <option value="LOW">Low (72h SLA)</option>
                <option value="MEDIUM">Medium (48h SLA)</option>
                <option value="HIGH">High (24h SLA)</option>
                <option value="CRITICAL">Critical (4h SLA)</option>
              </select>
            </div>
          </div>

          {/* Structured Relational Location Picker */}
          <div className="space-y-3 p-4 bg-slate-50 border border-slate-200 rounded-xl">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-700 flex items-center gap-1.5">
              <MapPin className="w-4 h-4 text-sky-600" />
              Structured Campus Location <span className="text-rose-500">*</span>
            </h3>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
              <div>
                <label className="block text-[11px] font-semibold text-slate-500 mb-1">Building</label>
                <select
                  value={selectedBuildingId}
                  onChange={(e) => {
                    setSelectedBuildingId(e.target.value);
                    setSelectedFloorId('');
                    setSelectedRoomId('');
                  }}
                  className="w-full text-xs border border-slate-300 rounded-lg p-2.5 bg-white focus:ring-2 focus:ring-sky-500 outline-none"
                >
                  <option value="">Select Building</option>
                  {availableBuildings.map((b) => (
                    <option key={b.id} value={b.id}>
                      {b.name} ({b.code})
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-[11px] font-semibold text-slate-500 mb-1">Floor</label>
                <select
                  disabled={!selectedBuildingId}
                  value={selectedFloorId}
                  onChange={(e) => {
                    setSelectedFloorId(e.target.value);
                    setSelectedRoomId('');
                  }}
                  className="w-full text-xs border border-slate-300 rounded-lg p-2.5 bg-white focus:ring-2 focus:ring-sky-500 outline-none disabled:bg-slate-100"
                >
                  <option value="">Select Floor</option>
                  {availableFloors.map((f) => (
                    <option key={f.id} value={f.id}>
                      {f.name}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-[11px] font-semibold text-slate-500 mb-1">Room / Area</label>
                <select
                  disabled={!selectedFloorId}
                  value={selectedRoomId}
                  onChange={(e) => setSelectedRoomId(e.target.value)}
                  className="w-full text-xs border border-slate-300 rounded-lg p-2.5 bg-white focus:ring-2 focus:ring-sky-500 outline-none disabled:bg-slate-100"
                >
                  <option value="">Select Room</option>
                  {availableRooms.map((r) => (
                    <option key={r.id} value={r.id}>
                      Room {r.room_number} ({r.room_type})
                    </option>
                  ))}
                </select>
              </div>
            </div>

            <div>
              <label className="block text-[11px] font-semibold text-slate-500 mb-1">
                Specific Spot Details (e.g. Near window desk 4, North Wall)
              </label>
              <input
                type="text"
                placeholder="Near window desk 4"
                value={specificDetails}
                onChange={(e) => setSpecificDetails(e.target.value)}
                className="w-full text-xs border border-slate-300 rounded-lg p-2.5 bg-white focus:ring-2 focus:ring-sky-500 outline-none"
              />
            </div>
          </div>

          {/* Description */}
          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">
              Detailed Description <span className="text-rose-500">*</span>
            </label>
            <textarea
              rows={4}
              required
              placeholder="Describe the issue, observed symptoms, or hazard risks..."
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className="w-full text-sm border border-slate-300 rounded-xl p-3 focus:ring-2 focus:ring-sky-500 outline-none resize-none"
            />
          </div>

          {/* File Attachment */}
          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">Attach Photo or Document (Optional)</label>
            <input
              type="file"
              onChange={(e) => setSelectedFile(e.target.files ? e.target.files[0] : null)}
              className="block w-full text-xs text-slate-500 file:mr-4 file:py-2 file:px-4 file:rounded-xl file:border-0 file:text-xs file:font-semibold file:bg-sky-50 file:text-sky-700 hover:file:bg-sky-100 cursor-pointer"
            />
            {selectedFile && (
              <p className="text-xs text-emerald-600 font-semibold mt-1">
                Attached: {selectedFile.name} ({(selectedFile.size / 1024).toFixed(1)} KB)
              </p>
            )}
          </div>

          {/* Submit button */}
          <div className="flex justify-end pt-2">
            <button
              type="submit"
              disabled={loading}
              className="inline-flex items-center gap-2 px-6 py-3 bg-sky-600 hover:bg-sky-700 text-white font-extrabold text-sm rounded-xl shadow-md transition-colors disabled:opacity-50"
            >
              <Send className="w-4 h-4" />
              {loading ? 'Submitting Request...' : 'Submit Service Request'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
