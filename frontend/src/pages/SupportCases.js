import React, { useState, useEffect, useCallback } from 'react';
import { useAuth } from '../AuthContext';
import { useTranslation } from '../hooks/useTranslation';
import {
  listSupportCases,
  createSupportCase,
  updateSupportCase,
  resolveSupportCase,
  getSupportCase,
  addComment,
  getSupportCaseStats,
} from '../services/supportCasesService';

const STATUS_OPTIONS = [
  { value: 'open', label: 'Open', color: 'bg-blue-100 text-blue-800' },
  { value: 'investigating', label: 'Investigating', color: 'bg-yellow-100 text-yellow-800' },
  { value: 'waiting_on_customer', label: 'Waiting on Customer', color: 'bg-purple-100 text-purple-800' },
  { value: 'resolved', label: 'Resolved', color: 'bg-green-100 text-green-800' },
  { value: 'closed', label: 'Closed', color: 'bg-gray-100 text-gray-800' },
];

const PRIORITY_OPTIONS = [
  { value: 'low', label: 'Low', color: 'bg-gray-100 text-gray-800' },
  { value: 'medium', label: 'Medium', color: 'bg-blue-100 text-blue-800' },
  { value: 'high', label: 'High', color: 'bg-orange-100 text-orange-800' },
  { value: 'critical', label: 'Critical', color: 'bg-red-100 text-red-800' },
];

const MACHINE_MODELS = ['V4.0', 'V3.1B', 'V3.0', 'V2.0'];

const StatusBadge = ({ status }) => {
  const opt = STATUS_OPTIONS.find(o => o.value === status) || STATUS_OPTIONS[0];
  return (
    <span className={`px-2 py-1 rounded-full text-xs font-medium ${opt.color}`}>
      {opt.label}
    </span>
  );
};

const PriorityBadge = ({ priority }) => {
  const opt = PRIORITY_OPTIONS.find(o => o.value === priority) || PRIORITY_OPTIONS[1];
  return (
    <span className={`px-2 py-1 rounded-full text-xs font-medium ${opt.color}`}>
      {opt.label}
    </span>
  );
};

// ===== CREATE/EDIT FORM MODAL =====
const CaseFormModal = ({ isOpen, onClose, onSave, editCase }) => {
  const [formData, setFormData] = useState({
    title: '', description: '', machine_model: '', symptoms: '',
    priority: 'medium', tags: '', assigned_to: '',
  });

  useEffect(() => {
    if (editCase) {
      setFormData({
        title: editCase.title || '',
        description: editCase.description || '',
        machine_model: editCase.machine_model || '',
        symptoms: editCase.symptoms || '',
        root_cause: editCase.root_cause || '',
        resolution: editCase.resolution || '',
        priority: editCase.priority || 'medium',
        customer: editCase.organization_id || '',
        tags: (editCase.tags || []).join(', '),
        assigned_to: editCase.assigned_to || '',
      });
    } else {
      setFormData({ title: '', description: '', machine_model: '', symptoms: '', root_cause: '', resolution: '', priority: 'medium', customer: '', tags: '', assigned_to: '' });
    }
  }, [editCase, isOpen]);

  const handleSubmit = (e) => {
    e.preventDefault();
    const payload = {
      ...formData,
      organization_id: formData.customer || undefined,
      tags: formData.tags ? formData.tags.split(',').map(t => t.trim()).filter(Boolean) : [],
    };
    delete payload.customer;
    if (!payload.machine_model) delete payload.machine_model;
    if (!payload.assigned_to) delete payload.assigned_to;
    if (!payload.root_cause) delete payload.root_cause;
    if (!payload.resolution) delete payload.resolution;
    if (!payload.organization_id) delete payload.organization_id;
    onSave(payload);
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-lg max-h-[90vh] overflow-y-auto p-6">
        <h2 className="text-lg font-semibold mb-4">{editCase ? 'Edit Case' : 'New Support Case'}</h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700">Title *</label>
            <input type="text" required value={formData.title}
              onChange={e => setFormData(f => ({ ...f, title: e.target.value }))}
              className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 text-sm" />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Description *</label>
            <textarea required rows={3} value={formData.description}
              onChange={e => setFormData(f => ({ ...f, description: e.target.value }))}
              className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 text-sm" />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Customer / Company</label>
            <input type="text" value={formData.customer}
              onChange={e => setFormData(f => ({ ...f, customer: e.target.value }))}
              className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 text-sm"
              placeholder="Which company reported this issue?" />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700">Machine Model</label>
              <select value={formData.machine_model}
                onChange={e => setFormData(f => ({ ...f, machine_model: e.target.value }))}
                className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 text-sm">
                <option value="">-- Select --</option>
                {MACHINE_MODELS.map(m => <option key={m} value={m}>{m}</option>)}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Priority</label>
              <select value={formData.priority}
                onChange={e => setFormData(f => ({ ...f, priority: e.target.value }))}
                className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 text-sm">
                {PRIORITY_OPTIONS.map(p => <option key={p.value} value={p.value}>{p.label}</option>)}
              </select>
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Symptoms</label>
            <textarea rows={2} value={formData.symptoms}
              onChange={e => setFormData(f => ({ ...f, symptoms: e.target.value }))}
              className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 text-sm"
              placeholder="What symptoms were observed?" />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Diagnostics / Possible Causes</label>
            <textarea rows={3} value={formData.root_cause}
              onChange={e => setFormData(f => ({ ...f, root_cause: e.target.value }))}
              className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 text-sm"
              placeholder="What could be causing this? Diagnostic steps taken, possible root causes..." />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Resolution</label>
            <textarea rows={3} value={formData.resolution}
              onChange={e => setFormData(f => ({ ...f, resolution: e.target.value }))}
              className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 text-sm"
              placeholder="How was the problem resolved? Steps taken to fix it..." />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Tags (comma-separated)</label>
            <input type="text" value={formData.tags}
              onChange={e => setFormData(f => ({ ...f, tags: e.target.value }))}
              className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 text-sm"
              placeholder="e.g. hydraulic, pump, V4.0" />
          </div>
          <div className="flex justify-end space-x-3 pt-2">
            <button type="button" onClick={onClose}
              className="px-4 py-2 text-sm text-gray-700 border border-gray-300 rounded-md hover:bg-gray-50">Cancel</button>
            <button type="submit"
              className="px-4 py-2 text-sm text-white bg-blue-600 rounded-md hover:bg-blue-700">
              {editCase ? 'Update' : 'Create Case'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

// ===== RESOLVE MODAL =====
const ResolveModal = ({ isOpen, onClose, onResolve }) => {
  const [rootCause, setRootCause] = useState('');
  const [resolution, setResolution] = useState('');
  const [publishToKB, setPublishToKB] = useState(true);

  const handleSubmit = (e) => {
    e.preventDefault();
    onResolve({ root_cause: rootCause, resolution, publish_to_knowledge_base: publishToKB });
    setRootCause('');
    setResolution('');
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-lg p-6">
        <h2 className="text-lg font-semibold mb-4">Resolve Support Case</h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700">Root Cause *</label>
            <textarea required rows={3} value={rootCause} onChange={e => setRootCause(e.target.value)}
              className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 text-sm"
              placeholder="What was the root cause of the issue?" />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Resolution *</label>
            <textarea required rows={3} value={resolution} onChange={e => setResolution(e.target.value)}
              className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 text-sm"
              placeholder="How was the issue resolved?" />
          </div>
          <div className="flex items-center">
            <input type="checkbox" id="publishKB" checked={publishToKB}
              onChange={e => setPublishToKB(e.target.checked)}
              className="h-4 w-4 text-blue-600 border-gray-300 rounded" />
            <label htmlFor="publishKB" className="ml-2 text-sm text-gray-700">
              Publish to AI Knowledge Base (makes this resolution searchable by the AI assistant)
            </label>
          </div>
          <div className="flex justify-end space-x-3 pt-2">
            <button type="button" onClick={onClose}
              className="px-4 py-2 text-sm text-gray-700 border border-gray-300 rounded-md hover:bg-gray-50">Cancel</button>
            <button type="submit"
              className="px-4 py-2 text-sm text-white bg-green-600 rounded-md hover:bg-green-700">Resolve Case</button>
          </div>
        </form>
      </div>
    </div>
  );
};

// ===== CASE DETAIL VIEW =====
const CaseDetail = ({ caseData, onBack, onStatusChange, onResolve, onAddComment, onRefresh }) => {
  const [comment, setComment] = useState('');
  const [isInternal, setIsInternal] = useState(false);

  const handleAddComment = async (e) => {
    e.preventDefault();
    if (!comment.trim()) return;
    await onAddComment(caseData.id, { content: comment, is_internal: isInternal });
    setComment('');
    onRefresh();
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <button onClick={onBack} className="text-blue-600 hover:text-blue-800 text-sm flex items-center">
          &larr; Back to Cases
        </button>
        <div className="flex items-center space-x-2">
          <StatusBadge status={caseData.status} />
          <PriorityBadge priority={caseData.priority} />
        </div>
      </div>

      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex justify-between items-start">
          <div>
            <p className="text-xs text-gray-500 font-mono">{caseData.case_number}</p>
            <h2 className="text-xl font-semibold mt-1">{caseData.title}</h2>
          </div>
          <div className="flex space-x-2">
            {caseData.status !== 'resolved' && caseData.status !== 'closed' && (
              <button onClick={() => onResolve(caseData)}
                className="px-3 py-1.5 text-sm bg-green-600 text-white rounded hover:bg-green-700">
                Resolve
              </button>
            )}
            {caseData.status === 'resolved' && (
              <button onClick={() => onStatusChange(caseData.id, 'closed')}
                className="px-3 py-1.5 text-sm bg-gray-600 text-white rounded hover:bg-gray-700">
                Close
              </button>
            )}
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-6">
          <div>
            <h3 className="text-sm font-medium text-gray-500">Description</h3>
            <p className="mt-1 text-sm text-gray-900 whitespace-pre-wrap">{caseData.description}</p>
          </div>
          <div className="space-y-3">
            {caseData.machine_model && (
              <div><span className="text-sm font-medium text-gray-500">Machine Model:</span>
                <span className="ml-2 text-sm">AutoBoss {caseData.machine_model}</span></div>
            )}
            {caseData.symptoms && (
              <div><span className="text-sm font-medium text-gray-500">Symptoms:</span>
                <p className="mt-1 text-sm text-gray-900 whitespace-pre-wrap">{caseData.symptoms}</p></div>
            )}
            {caseData.tags && caseData.tags.length > 0 && (
              <div><span className="text-sm font-medium text-gray-500">Tags:</span>
                <div className="mt-1 flex flex-wrap gap-1">
                  {caseData.tags.map(tag => (
                    <span key={tag} className="px-2 py-0.5 bg-gray-100 text-gray-700 text-xs rounded">{tag}</span>
                  ))}
                </div>
              </div>
            )}
            <div><span className="text-sm font-medium text-gray-500">Created:</span>
              <span className="ml-2 text-sm">{new Date(caseData.created_at).toLocaleString()}</span></div>
          </div>
        </div>

        {(caseData.root_cause || caseData.resolution) && (
          <div className="mt-6 p-4 bg-green-50 rounded-lg border border-green-200">
            <h3 className="text-sm font-semibold text-green-800 mb-2">Resolution</h3>
            {caseData.root_cause && (
              <div className="mb-2"><span className="text-sm font-medium text-green-700">Root Cause:</span>
                <p className="text-sm text-green-900 mt-1 whitespace-pre-wrap">{caseData.root_cause}</p></div>
            )}
            {caseData.resolution && (
              <div><span className="text-sm font-medium text-green-700">Resolution:</span>
                <p className="text-sm text-green-900 mt-1 whitespace-pre-wrap">{caseData.resolution}</p></div>
            )}
            {caseData.knowledge_doc_id && (
              <p className="text-xs text-green-600 mt-2">Published to AI Knowledge Base</p>
            )}
          </div>
        )}
      </div>

      {/* Comments Section */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-md font-semibold mb-4">Comments & Updates</h3>
        {caseData.comments && caseData.comments.length > 0 ? (
          <div className="space-y-3 mb-4">
            {caseData.comments.map(c => (
              <div key={c.id} className={`p-3 rounded-lg text-sm ${c.is_internal ? 'bg-yellow-50 border border-yellow-200' : 'bg-gray-50 border border-gray-200'}`}>
                <div className="flex justify-between items-center mb-1">
                  <span className="font-medium text-gray-700">{c.author_id}</span>
                  <div className="flex items-center space-x-2">
                    {c.is_internal && <span className="text-xs text-yellow-600 font-medium">Internal</span>}
                    <span className="text-xs text-gray-500">{new Date(c.created_at).toLocaleString()}</span>
                  </div>
                </div>
                <p className="text-gray-800 whitespace-pre-wrap">{c.content}</p>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-sm text-gray-500 mb-4">No comments yet.</p>
        )}

        <form onSubmit={handleAddComment} className="space-y-2">
          <textarea rows={2} value={comment} onChange={e => setComment(e.target.value)}
            className="block w-full border border-gray-300 rounded-md px-3 py-2 text-sm"
            placeholder="Add a comment..." />
          <div className="flex justify-between items-center">
            <label className="flex items-center text-sm text-gray-600">
              <input type="checkbox" checked={isInternal} onChange={e => setIsInternal(e.target.checked)}
                className="h-4 w-4 text-yellow-600 border-gray-300 rounded mr-2" />
              Internal note
            </label>
            <button type="submit" disabled={!comment.trim()}
              className="px-4 py-1.5 text-sm bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50">
              Add Comment
            </button>
          </div>
        </form>
      </div>

      {/* Status Actions */}
      {caseData.status !== 'closed' && (
        <div className="bg-white rounded-lg shadow p-4">
          <h3 className="text-sm font-medium text-gray-700 mb-2">Change Status</h3>
          <div className="flex flex-wrap gap-2">
            {STATUS_OPTIONS.filter(s => s.value !== caseData.status && s.value !== 'closed')
              .map(s => (
                <button key={s.value} onClick={() => onStatusChange(caseData.id, s.value)}
                  className={`px-3 py-1.5 text-xs rounded border hover:opacity-80 ${s.color}`}>
                  {s.label}
                </button>
              ))}
          </div>
        </div>
      )}
    </div>
  );
};

// ===== MAIN PAGE COMPONENT =====
const SupportCases = () => {
  const { user } = useAuth();
  const [cases, setCases] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedCase, setSelectedCase] = useState(null);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [editCase, setEditCase] = useState(null);
  const [showResolveModal, setShowResolveModal] = useState(false);
  const [resolveTarget, setResolveTarget] = useState(null);
  const [filters, setFilters] = useState({ status: '', priority: '', machine_model: '', search: '' });
  const [total, setTotal] = useState(0);

  const fetchCases = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const activeFilters = {};
      Object.entries(filters).forEach(([key, value]) => {
        if (value) activeFilters[key] = value;
      });
      const data = await listSupportCases(activeFilters);
      setCases(data.cases || []);
      setTotal(data.total || 0);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [filters]);

  const fetchStats = useCallback(async () => {
    try {
      const data = await getSupportCaseStats();
      setStats(data);
    } catch (err) {
      console.error('Failed to fetch stats:', err);
    }
  }, []);

  useEffect(() => { fetchCases(); }, [fetchCases]);
  useEffect(() => { fetchStats(); }, [fetchStats]);

  const handleCreate = async (data) => {
    try {
      await createSupportCase(data);
      setShowCreateModal(false);
      fetchCases();
      fetchStats();
    } catch (err) {
      alert('Failed to create case: ' + err.message);
    }
  };

  const handleUpdate = async (data) => {
    try {
      await updateSupportCase(editCase.id, data);
      setEditCase(null);
      fetchCases();
      if (selectedCase && selectedCase.id === editCase.id) {
        const updated = await getSupportCase(editCase.id);
        setSelectedCase(updated);
      }
    } catch (err) {
      alert('Failed to update case: ' + err.message);
    }
  };

  const handleStatusChange = async (caseId, newStatus) => {
    try {
      await updateSupportCase(caseId, { status: newStatus });
      fetchCases();
      fetchStats();
      if (selectedCase && selectedCase.id === caseId) {
        const updated = await getSupportCase(caseId);
        setSelectedCase(updated);
      }
    } catch (err) {
      alert('Failed to update status: ' + err.message);
    }
  };

  const handleResolve = async (resolutionData) => {
    try {
      await resolveSupportCase(resolveTarget.id, resolutionData);
      setShowResolveModal(false);
      setResolveTarget(null);
      fetchCases();
      fetchStats();
      if (selectedCase && selectedCase.id === resolveTarget.id) {
        const updated = await getSupportCase(resolveTarget.id);
        setSelectedCase(updated);
      }
    } catch (err) {
      alert('Failed to resolve case: ' + err.message);
    }
  };

  const handleAddComment = async (caseId, commentData) => {
    try {
      await addComment(caseId, commentData);
    } catch (err) {
      alert('Failed to add comment: ' + err.message);
    }
  };

  const handleViewCase = async (caseItem) => {
    try {
      const full = await getSupportCase(caseItem.id);
      setSelectedCase(full);
    } catch (err) {
      alert('Failed to load case: ' + err.message);
    }
  };

  const handleRefreshDetail = async () => {
    if (selectedCase) {
      const updated = await getSupportCase(selectedCase.id);
      setSelectedCase(updated);
    }
  };

  // If viewing a specific case
  if (selectedCase) {
    return (
      <div className="p-6 max-w-5xl mx-auto">
        <CaseDetail
          caseData={selectedCase}
          onBack={() => setSelectedCase(null)}
          onStatusChange={handleStatusChange}
          onResolve={(c) => { setResolveTarget(c); setShowResolveModal(true); }}
          onAddComment={handleAddComment}
          onRefresh={handleRefreshDetail}
        />
        <ResolveModal
          isOpen={showResolveModal}
          onClose={() => { setShowResolveModal(false); setResolveTarget(null); }}
          onResolve={handleResolve}
        />
      </div>
    );
  }

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Support Cases</h1>
          <p className="text-sm text-gray-500 mt-1">Record and track customer issues for AI knowledge building</p>
        </div>
        <button onClick={() => setShowCreateModal(true)}
          className="px-4 py-2 bg-blue-600 text-white text-sm rounded-md hover:bg-blue-700">
          + New Case
        </button>
      </div>

      {/* Stats Summary */}
      {stats && (
        <div className="grid grid-cols-2 md:grid-cols-5 gap-3 mb-6">
          <div className="bg-blue-50 rounded-lg p-3 text-center">
            <p className="text-2xl font-bold text-blue-700">{stats.open_cases}</p>
            <p className="text-xs text-blue-600">Open</p>
          </div>
          <div className="bg-yellow-50 rounded-lg p-3 text-center">
            <p className="text-2xl font-bold text-yellow-700">{stats.investigating_cases}</p>
            <p className="text-xs text-yellow-600">Investigating</p>
          </div>
          <div className="bg-purple-50 rounded-lg p-3 text-center">
            <p className="text-2xl font-bold text-purple-700">{stats.waiting_cases}</p>
            <p className="text-xs text-purple-600">Waiting</p>
          </div>
          <div className="bg-green-50 rounded-lg p-3 text-center">
            <p className="text-2xl font-bold text-green-700">{stats.resolved_cases}</p>
            <p className="text-xs text-green-600">Resolved</p>
          </div>
          <div className="bg-gray-50 rounded-lg p-3 text-center">
            <p className="text-2xl font-bold text-gray-700">{stats.total_cases}</p>
            <p className="text-xs text-gray-600">Total</p>
          </div>
        </div>
      )}

      {/* Filters */}
      <div className="bg-white rounded-lg shadow p-4 mb-4">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
          <input type="text" placeholder="Search title, description, symptoms..."
            value={filters.search} onChange={e => setFilters(f => ({ ...f, search: e.target.value }))}
            className="border border-gray-300 rounded-md px-3 py-2 text-sm" />
          <select value={filters.status} onChange={e => setFilters(f => ({ ...f, status: e.target.value }))}
            className="border border-gray-300 rounded-md px-3 py-2 text-sm">
            <option value="">All Statuses</option>
            {STATUS_OPTIONS.map(s => <option key={s.value} value={s.value}>{s.label}</option>)}
          </select>
          <select value={filters.priority} onChange={e => setFilters(f => ({ ...f, priority: e.target.value }))}
            className="border border-gray-300 rounded-md px-3 py-2 text-sm">
            <option value="">All Priorities</option>
            {PRIORITY_OPTIONS.map(p => <option key={p.value} value={p.value}>{p.label}</option>)}
          </select>
          <select value={filters.machine_model} onChange={e => setFilters(f => ({ ...f, machine_model: e.target.value }))}
            className="border border-gray-300 rounded-md px-3 py-2 text-sm">
            <option value="">All Models</option>
            {MACHINE_MODELS.map(m => <option key={m} value={m}>{m}</option>)}
          </select>
        </div>
      </div>

      {/* Cases List */}
      {loading ? (
        <div className="text-center py-8 text-gray-500">Loading cases...</div>
      ) : error ? (
        <div className="text-center py-8 text-red-600">Error: {error}</div>
      ) : cases.length === 0 ? (
        <div className="text-center py-12 bg-white rounded-lg shadow">
          <p className="text-gray-500 text-lg">No support cases found</p>
          <p className="text-gray-400 text-sm mt-1">Create your first case to start building the AI knowledge base</p>
        </div>
      ) : (
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Case</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Priority</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Model</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Created</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {cases.map(c => (
                <tr key={c.id} className="hover:bg-gray-50 cursor-pointer" onClick={() => handleViewCase(c)}>
                  <td className="px-4 py-3">
                    <p className="text-sm font-medium text-gray-900 truncate max-w-xs">{c.title}</p>
                    <p className="text-xs text-gray-500 font-mono">{c.case_number}</p>
                  </td>
                  <td className="px-4 py-3"><StatusBadge status={c.status} /></td>
                  <td className="px-4 py-3"><PriorityBadge priority={c.priority} /></td>
                  <td className="px-4 py-3 text-sm text-gray-600">{c.machine_model || '-'}</td>
                  <td className="px-4 py-3 text-sm text-gray-500">{new Date(c.created_at).toLocaleDateString()}</td>
                  <td className="px-4 py-3">
                    <button onClick={(e) => { e.stopPropagation(); setEditCase(c); }}
                      className="text-xs text-blue-600 hover:text-blue-800 mr-2">Edit</button>
                    {c.status !== 'resolved' && c.status !== 'closed' && (
                      <button onClick={(e) => { e.stopPropagation(); setResolveTarget(c); setShowResolveModal(true); }}
                        className="text-xs text-green-600 hover:text-green-800">Resolve</button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {total > cases.length && (
            <div className="px-4 py-3 bg-gray-50 text-sm text-gray-500 text-center">
              Showing {cases.length} of {total} cases
            </div>
          )}
        </div>
      )}

      {/* Modals */}
      <CaseFormModal
        isOpen={showCreateModal || !!editCase}
        onClose={() => { setShowCreateModal(false); setEditCase(null); }}
        onSave={editCase ? handleUpdate : handleCreate}
        editCase={editCase}
      />
      <ResolveModal
        isOpen={showResolveModal}
        onClose={() => { setShowResolveModal(false); setResolveTarget(null); }}
        onResolve={handleResolve}
      />
    </div>
  );
};

export default SupportCases;
