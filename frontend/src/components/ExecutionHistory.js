import React, { useState } from 'react';
import { formatDate } from '../utils';

const ExecutionHistory = ({ executions, onRefresh }) => {
  const [selectedExecution, setSelectedExecution] = useState(null);
  const [filterStatus, setFilterStatus] = useState('all');

  console.log('ExecutionHistory received executions:', executions);

  const filteredExecutions = executions.filter(exec => {
    if (filterStatus === 'all') return true;
    return exec.status === filterStatus;
  });

  console.log('Filtered executions:', filteredExecutions);

  const getStatusBadge = (status) => {
    const badges = {
      scheduled: 'bg-blue-100 text-blue-800',
      in_progress: 'bg-yellow-100 text-yellow-800',
      completed: 'bg-green-100 text-green-800',
      cancelled: 'bg-gray-100 text-gray-800'
    };
    return badges[status] || 'bg-gray-100 text-gray-800';
  };

  const getStatusIcon = (status) => {
    const icons = {
      scheduled: '📅',
      in_progress: '⚙️',
      completed: '✅',
      cancelled: '❌'
    };
    return icons[status] || '•';
  };

  if (selectedExecution) {
    return (
      <div className="bg-white rounded-lg shadow">
        <div className="p-6 border-b border-gray-200">
          <button
            onClick={() => setSelectedExecution(null)}
            className="text-blue-600 hover:text-blue-800 mb-4"
          >
            ← Back to History
          </button>
          <h2 className="text-2xl font-bold text-gray-900">Execution Details</h2>
        </div>

        <div className="p-6 space-y-6">
          {/* Execution Info */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="text-sm font-medium text-gray-500">Protocol</label>
              <p className="text-gray-900">{selectedExecution.protocol?.name}</p>
            </div>
            <div>
              <label className="text-sm font-medium text-gray-500">Machine</label>
              <p className="text-gray-900">
                {selectedExecution.machine?.name || selectedExecution.machine?.model} ({selectedExecution.machine?.serial_number})
              </p>
            </div>
            <div>
              <label className="text-sm font-medium text-gray-500">Performed By</label>
              <p className="text-gray-900">{selectedExecution.performed_by?.name || selectedExecution.performed_by?.username || 'Unknown'}</p>
            </div>
            <div>
              <label className="text-sm font-medium text-gray-500">Date</label>
              <p className="text-gray-900">{formatDate(selectedExecution.performed_date || selectedExecution.created_at)}</p>
            </div>
            <div>
              <label className="text-sm font-medium text-gray-500">Status</label>
              <span className={`inline-flex px-2 py-1 rounded text-xs font-medium ${getStatusBadge(selectedExecution.status)}`}>
                {selectedExecution.status}
              </span>
            </div>
            {selectedExecution.machine_hours_at_service && (
              <div>
                <label className="text-sm font-medium text-gray-500">Machine Hours</label>
                <p className="text-gray-900">{selectedExecution.machine_hours_at_service} hours</p>
              </div>
            )}
          </div>

          {selectedExecution.notes && (
            <div>
              <label className="text-sm font-medium text-gray-500">Notes</label>
              <p className="text-gray-900 mt-1 bg-gray-50 p-3 rounded">{selectedExecution.notes}</p>
            </div>
          )}

          {/* Checklist Completions */}
          {selectedExecution.checklist_completions && selectedExecution.checklist_completions.length > 0 && (
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Checklist Items</h3>
              <div className="space-y-3">
                {selectedExecution.checklist_completions.map((completion, index) => (
                  <div key={completion.id} className="border border-gray-200 rounded-lg p-4">
                    <div className="flex items-start gap-3">
                      <div className="flex-shrink-0 w-6 h-6 bg-gray-100 rounded flex items-center justify-center text-sm text-gray-600">
                        {index + 1}
                      </div>
                      <div className="flex-1">
                        <div className="flex items-center justify-between mb-2">
                          <h4 className="font-medium text-gray-900">
                            {completion.checklist_item?.item_description}
                          </h4>
                          <span className={`px-2 py-0.5 rounded text-xs font-medium ${
                            completion.status === 'completed' 
                              ? 'bg-green-100 text-green-800' 
                              : 'bg-gray-100 text-gray-800'
                          }`}>
                            {completion.status}
                          </span>
                        </div>
                        {completion.actual_quantity_used && (
                          <p className="text-sm text-gray-600">
                            Quantity used: {completion.actual_quantity_used}
                          </p>
                        )}
                        {completion.notes && (
                          <p className="text-sm text-gray-600 mt-1 bg-gray-50 p-2 rounded">
                            {completion.notes}
                          </p>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow">
      <div className="p-6 border-b border-gray-200">
        <div className="flex justify-between items-center">
          <h2 className="text-xl font-semibold text-gray-900">Execution History</h2>
          <div className="flex items-center gap-4">
            <select
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="all">All Status</option>
              <option value="scheduled">Scheduled</option>
              <option value="in_progress">In Progress</option>
              <option value="completed">Completed</option>
              <option value="cancelled">Cancelled</option>
            </select>
            <button
              onClick={onRefresh}
              className="px-4 py-2 text-blue-600 hover:text-blue-800"
            >
              🔄 Refresh
            </button>
          </div>
        </div>
      </div>

      {filteredExecutions.length === 0 && (
        <div className="p-12 text-center text-gray-500">
          No executions found
        </div>
      )}

      <div className="divide-y divide-gray-200">
        {filteredExecutions.map((execution) => (
          <div
            key={execution.id}
            className="p-6 hover:bg-gray-50 cursor-pointer transition-colors"
            onClick={() => setSelectedExecution(execution)}
          >
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-center gap-3 mb-2">
                  <span className="text-xl">{getStatusIcon(execution.status)}</span>
                  <h3 className="font-medium text-gray-900">{execution.protocol?.name}</h3>
                  <span className={`px-2 py-0.5 rounded text-xs font-medium ${getStatusBadge(execution.status)}`}>
                    {execution.status}
                  </span>
                </div>
                <div className="flex items-center gap-4 text-sm text-gray-600">
                  <span>
                    Machine: {execution.machine?.name || execution.machine?.model} ({execution.machine?.serial_number})
                  </span>
                  <span>
                    By: {execution.performed_by?.name || execution.performed_by?.username || 'Unknown'}
                  </span>
                  <span>
                    Date: {formatDate(execution.performed_date || execution.created_at)}
                  </span>
                </div>
              </div>
              <button className="text-blue-600 hover:text-blue-800 text-sm">
                View Details →
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default ExecutionHistory;
